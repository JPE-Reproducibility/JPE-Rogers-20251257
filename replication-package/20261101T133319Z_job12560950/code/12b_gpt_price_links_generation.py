"""
12b_gpt_price_links_generation.py
=================================
PROVENANCE ONLY -- DO NOT RUN AS PART OF THE DEFAULT PIPELINE.

This script documents how the GPT-generated FDA-product-code -> HCPCS/CPT
mappings were created. The outputs are checked into the replication package as
static data files because:
  1. They depend on OpenAI Chat Completions calls (model `gpt-5-mini`) whose
     responses are non-deterministic and vary across runs.
  2. OpenAI does not provide a way to replay a prior call against a frozen
     model snapshot, so an exact re-extraction of the identical mappings is not
     possible.
  3. Both II->I and III->II mappings were generated/validated via GPT.
  4. Re-running would require an OpenAI API key and would incur per-call costs.

The original notebook lives in the project root:
    Query_Prices_GPT_New_Price_Analysis_9_25_25.ipynb (cells 0-6, 15)

------------------------------------------------------------------------------
GENERATION RECORD (JPE Data Policy 2.1a / 4.3)
------------------------------------------------------------------------------
  Provider / model : OpenAI, `gpt-5-mini` (MODEL, below). NOT GPT-4o -- the
                     invention-year files (12_invention_year_generation.py) are
                     the GPT-4o ones.
  Sampling settings: the API defaults. run_extraction() calls
                     chat(model=MODEL, messages=[...]) and sets no temperature,
                     top_p or seed.
  Prompt           : reproduced verbatim below as INSTRUCTIONS (the system
                     message); the user message is built by _build_user_message().
  Date of the run  : 2025-09-22, from the pre-staging originals I hold outside
                     the package. The source notebook above is named for
                     2025-09-25, which is when I saved it rather than when the
                     queries ran, and the shipped CSVs' modification times
                     (2026-02-24) are re-staging dates. See README, "Why four
                     artifacts are frozen rather than regenerated", for the
                     mechanism.
  Raw responses    : NOT archived in the deposit. run_extraction() writes every
                     raw reply to a JSONL beside the tidy CSV, but that JSONL is
                     not a package member; only the parsed 15-column CSVs ship.
  Regeneration     : none. No route -- synthetic, from-raw, or provider -- calls
                     this script; the two CSVs are fixed inputs.

Outputs produced (now bundled in data/raw/):
  - 2_1_GPT_Price_Links.csv   FDA II->I product codes -> outpatient HCPCS/CPT
  - 3_2_GPT_Price_Links.csv   FDA III->II product codes -> outpatient HCPCS/CPT

These files are consumed by:
  - code/00_generate_data/gen_02_price_matching.py (whose docstring notes the
    files are "non-deterministic (OpenAI API output) and must be provided as
    static files")
  - code/05_price_analysis.py (manual HCPCS corrections at lines 854-899)

This mirrors the precedent set by `12_invention_year_generation.py` (also
GPT-generated, also DO-NOT-RUN). The method is documented here in full;
byte-identical reproduction is NOT possible. The static CSVs ship in the
package as the authoritative inputs.

------------------------------------------------------------------------------
SECURITY: NO API KEY IS STORED HERE
------------------------------------------------------------------------------
This provenance script reads the key only from the `OPENAI_API_KEY`
environment variable or a one-line local `pw_openai.txt`. No key is stored in
this file.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


# --- guard: do not run by default ---------------------------------------------
if __name__ == "__main__" and os.environ.get("RUN_GPT_PRICE_LINKS") != "1":
    sys.exit(
        "12b_gpt_price_links_generation.py is provenance documentation and is "
        "not run by default. It requires the OpenAI Python SDK + an API key + "
        "GPT calls (gpt-5-mini), and CANNOT reproduce the exact paper extract "
        "(LLM non-determinism). The authoritative inputs are the bundled "
        "data/raw/{2_1,3_2}_GPT_Price_Links.csv. Set RUN_GPT_PRICE_LINKS=1 to "
        "exercise the call path against the current model."
    )


# Model used in the paper. Per the source notebook: "you can swap to
# gpt-5-thinking for higher quality". The exact 2026-script run used gpt-5-mini.
MODEL = "gpt-5-mini"


# ---------------------------------------------------------------------------
# System prompt -- verbatim from the source notebook (Query_Prices_GPT_*.ipynb
# cell 3 INSTRUCTIONS, identical to cell 5 INSTRUCTIONS for the III->II pass).
# ---------------------------------------------------------------------------
INSTRUCTIONS = """
You are an expert on FDA medical devices and outpatient HCPCS/CPT procedures.

TASK: Given a specific device description (or FDA product code), return the single best outpatient procedure mapping IF AND ONLY IF the device is a nontrivial driver of the outpatient episode (e.g., the core implant/kit that defines the surgery, or the assay/test system in a lab test), not a trivial supply. If no suitable outpatient procedure exists—or the device is only a trivial component—return a structured 'no_link' result.

Scope & priority:
1) Scope = Outpatient claims (HOPD/ASC and outpatient professional/supplier). Return CPT (HCPCS Level I) for procedures. Include HCPCS Level II **when it is clearly device-specific** (e.g., implants, orthotics/prosthetics, defined DMEPOS items, device pass-through C-codes) and plausibly appears in outpatient episodes.
2) Materiality test:
   - LINK if the device/implant/test system is the defining component or drives a nontrivial share of payment (e.g., IOL in cataract surgery; a specific in vitro diagnostic assay kit; an ambulatory infusion pump).
   - NO LINK if the item is a generic tool/consumable, if mapping is diffuse (many-to-many across unrelated procedures), or if the code is primarily an evaluation/visit/collection/handling/service code.
3) Specificity:
   - Choose the **most specific, commonly used outpatient code(s)** that match the device.
   - For CPT vs G-codes covering the same service, **prefer current CPT**; put legacy/alternative G-codes under "alternates".
4) HCPCS Level II inclusion rules:
   - **Include** E-/L-/A-/C-code families if the code descriptor matches the device (e.g., E0730/E0731 TENS, E0781/E0784 infusion pumps, E0603 breast pump, L-codes for prosthetics/orthotics, truly device-specific C-codes).
   - **Exclude** “misc/unlisted” Level II such as A4649, E1399, L8699, J3490, J3590, C9399, Q9999 unless the device itself is billed *only* under that unlisted code and you can justify it with strong sources.
   - Do **not** return HCPCS J-codes for **drugs/agents** unless the device **is** the agent (e.g., diagnostic radiopharmaceutical) rather than the equipment.
5) Lab/test linking guardrails:
   - **Link** to lab CPT (80xxx) when the device is the assay/test system or kit targeting that analyte/panel (e.g., troponin immunoassay kit → CPT 84484).
   - **NO LINK** when the device is a **general analyzer platform** used across many unrelated tests (diffuse mapping).
   - **Exclude** specimen handling/collection and general services: 36415, P9603, P9604, G2023, G2024, G0463, and similar.
6) Hard bans (DO NOT LINK):
   - E/M and general services (e.g., 992xx, 993xx, 994xx, 990xx), clinic visit G-codes (e.g., G0463), specimen collection/handling (e.g., 36415, P9603, P9604, G2023, G2024), and generic supply/unlisted HCPCS (e.g., A4649, E1399, L8699, J3490, J3590, C9399, Q9999) unless explicitly justified as the **only** correct code with strong sources (rare).
7) One-shot answer per query:
   - Return the **single best** code(s). If several are equally strong variants, put the top choice(s) in the main fields and place others in "alternates".
8) Sources: Provide ≥1 high-quality source (FDA Product Classification page, CMS/AMA descriptor, relevant specialty society guidance, or manufacturer IFU/clinical overview). If a reliable source can’t be identified, respond with no_link.

Validation checklist (apply before answering):
- CPT must be 5 digits and appropriate to the service class (e.g., 70xxx radiology, 80xxx lab).
- HCPCS Level II must match pattern A–V + 4 digits and be **device-specific** per rule 4.
- Reject mappings that rely solely on visit/collection/handling/service or unlisted codes (rule 6).

Output format: Return ONLY one JSON object with these keys:
{
  "decision": "link" | "no_link",
  "mapping_quality": "strong" | "weak" | "diffuse",
  "hcpcs_cpt": ["<CPT code(s)>"],
  "hcpcs_level_2": ["<HCPCS Level II codes>"],
  "procedure_desc": "<short plain-English description>",
  "rationale": "<why this is (not) a good outpatient mapping, focusing on materiality (short)>",
  "alternates": ["<other plausible CPT/HCPCS>"],
  "sources": [{"title":"<source name>","url":"<https://...>"}],
  "confidence": 0.0-1.0
}

Few-shot examples (follow precisely):

# GOOD (device defines the procedure)
User: "'Device candidate:
- FDA product code: HQL
- Device name: intraocular lens
- Regulation: 886.3600; intraocular lens.
- Subpart: Prosthetic Devices
Return ONLY the JSON object described in the system message.'"
Assistant:
{
  "decision": "link",
  "mapping_quality": "strong",
  "hcpcs_cpt": ["66984","66982"],
  "hcpcs_level_2": [],
  "procedure_desc": "Cataract extraction with intraocular lens (standard and complex variants).",
  "rationale": "The IOL is the defining implant and a major driver of the outpatient cataract episode.",
  "alternates": [],
  "sources": [
    {"title": "Cataract surgery with IOL (CPT descriptors/society guidance)", "url": "<authoritative_source>"}
  ],
  "confidence": 0.92
}

# GOOD (device-specific HCPCS Level II)
User: "'Device candidate:
- FDA product code: NUH
- Device name: STIMULATOR, NERVE, TRANSCUTANEOUS, OVER-THE-COUNTER
- Regulation: 882.5890; Transcutaneous electrical nerve stimulator for pain relief.
- Subpart: Neurological Therapeutic Devices
Return ONLY the JSON object described in the system message.'"
Assistant:
{
  "decision": "link",
  "mapping_quality": "strong",
  "hcpcs_cpt": [],
  "hcpcs_level_2": ["E0730","E0731"],
  "procedure_desc": "TENS device (2-lead or 4-lead) furnished for outpatient/home use.",
  "rationale": "HCPCS Level II E-codes are device-specific for TENS; they directly describe the item being provided.",
  "alternates": [],
  "sources": [
    {"title": "HCPCS E0730/E0731 descriptors", "url": "<authoritative_source>"}
  ],
  "confidence": 0.90
}

# GOOD (lab assay kit → analyte-specific CPT)
User: "'Device candidate:
- FDA product code: MMI
- Device name: Immunoassay Method, Troponin Subunit
- Regulation: 862.1215; Creatine phosphokinase/creatine kinase or isoenzymes test system. 
- Subpart: Clinical Chemistry Test Systems
Return ONLY the JSON object described in the system message.'"
Assistant:
{
  "decision": "link",
  "mapping_quality": "strong",
  "hcpcs_cpt": ["84484"],
  "hcpcs_level_2": [],
  "procedure_desc": "Quantitative troponin assay.",
  "rationale": "The device is the specific assay/test system for troponin; CPT 84484 directly describes the analyte-specific test.",
  "alternates": [],
  "sources": [
    {"title": "CPT 84484 descriptor (troponin)", "url": "<authoritative_source>"}
  ],
  "confidence": 0.88
}

# NO LINK (generic analyzer platform → diffuse)
User: "'Device candidate:
- FDA product code: OHQ
- Device name: Multi-Analyte Controls Unassayed
- Regulation: 862.1660; Quality control material (assayed and unassayed).
- Subpart: Clinical Chemistry Test Systems 
Return ONLY the JSON object described in the system message.'"
Assistant:
{
  "decision": "no_link",
  "mapping_quality": "diffuse",
  "hcpcs_cpt": [],
  "hcpcs_level_2": [],
  "procedure_desc": "",
  "rationale": "General analyzers run many unrelated assays; no single outpatient lab CPT is uniquely driven by this device.",
  "alternates": [],
  "sources": [
    {"title": "Manufacturer overview showing multi-assay platform use", "url": "<authoritative_source>"}
  ],
  "confidence": 0.76
}

# BAD (tool; trivial component — do not link)
User: "'Device candidate:
- FDA product code: HNN
- Device name: Knife, ophthalmic
- Regulation: 886.4350; Manual ophthalmic surgical instrument.
- Subpart: Surgical Devices
Return ONLY the JSON object described in the system message.'"
Assistant:
{
  "decision": "no_link",
  "mapping_quality": "weak",
  "hcpcs_cpt": [],
  "hcpcs_level_2": [],
  "procedure_desc": "",
  "rationale": "Manual instrument used across many procedures; not a price driver of any specific outpatient episode.",
  "alternates": [],
  "sources": [
    {"title": "FDA Product Classification: HNN", "url": "<FDA_classification_URL_for_HNN>"}
  ],
  "confidence": 0.70
}

Now handle the next query. Return ONLY the JSON object—no prose.
"""


# ---------------------------------------------------------------------------
# Manual HCPCS corrections applied AFTER the GPT pass (source notebook cell
# 15). These override the GPT mapping for product codes where the analyst
# verified a more accurate HCPCS/CPT than the model returned. Same set the
# downstream `05_price_analysis.py` re-applies (lines 854-899).
# ---------------------------------------------------------------------------
MANUAL_HCPCS_CORRECTIONS = {
    "JCA": {"hcpcs": "85002", "procedure_desc": "Bleeding time test"},
    "JGP": {"hcpcs": "84155",
            "procedure_desc": "Measurement of total protein concentration in blood "
                              "(serum, plasma, or whole blood)"},
    "MLM": {"hcpcs": "80197",
            "procedure_desc": "Therapeutic drug assay of Tacrolimus (FK506) in blood"},
    "DAD": {"hcpcs": "83010", "procedure_desc": None},
    # Description-only edits (no HCPCS override):
    "MAX": {"procedure_desc": "Anterior lumbar interbody fusion (ALIF)"},
    "FNL": {"procedure_desc":
            "Hospital bed, semi-electric (head & foot adjustment), with any "
            "type side rails, with mattress."},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _load_api_key() -> str:
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key.strip()
    for candidate in ("pw_openai.txt", os.path.expanduser("~/pw_openai.txt")):
        p = Path(candidate)
        if p.exists():
            return p.read_text(encoding="utf-8").splitlines()[0].strip()
    raise SystemExit(
        "No OpenAI API key found. Set OPENAI_API_KEY or place a one-line "
        "pw_openai.txt in the working directory. Never hard-code the key."
    )


def _chat_create():
    """Return a (callable, sdk_name) tuple supporting both new and legacy SDK."""
    api_key = _load_api_key()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        return (lambda **kw: client.chat.completions.create(**kw)), "openai>=1"
    except Exception:
        import openai
        openai.api_key = api_key
        return (lambda **kw: openai.chat.completions.create(**kw)), "openai (legacy)"


def _build_user_message(row) -> str:
    """Mirrors the source notebook's per-row user prompt."""
    return (
        "Device candidate:\n"
        f"- FDA product code: {row.get('PRODUCTCODE')}\n"
        f"- Device name: {row.get('DEVICENAME')}\n"
        f"- Regulation: {row.get('REGULATIONNUMBER')}; "
        f"{row.get('DESCRIPTION_OF_REGNUM')}\n"
        f"- Subpart: {row.get('SUBPART_DESCRIPTION')}\n"
        "Return ONLY the JSON object described in the system message."
    )


def _extract_json_obj(text: str):
    """Pull the first JSON object out of a model response. Source: notebook helper."""
    if not text:
        return None
    try:
        # fast path
        return json.loads(text)
    except Exception:
        pass
    # find the first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


def _save_jsonl(path: str, record: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _flatten(rec: dict) -> dict:
    base = {k: rec.get(k) for k in [
        "row_index", "productcode", "devicename", "regulationnumber",
        "description_of_regnum", "subpart_description", "status",
    ]}
    p = rec.get("parsed") or {}
    base.update({
        "decision": p.get("decision"),
        "mapping_quality": p.get("mapping_quality"),
        "hcpcs_cpt": ",".join(p.get("hcpcs_cpt", []) or []),
        "hcpcs_level_2": ",".join(p.get("hcpcs_level_2", []) or []),
        "procedure_desc": p.get("procedure_desc"),
        "rationale": p.get("rationale"),
        "alternates": ",".join(p.get("alternates", []) or []),
        "confidence": p.get("confidence"),
    })
    return base


# ---------------------------------------------------------------------------
# Per-direction extraction (II->I or III->II)
# ---------------------------------------------------------------------------
def run_extraction(
    matched_sample_csv: str,
    jsonl_path: str,
    output_csv: str,
) -> None:
    import pandas as pd

    df = pd.read_csv(matched_sample_csv).drop_duplicates(subset="PRODUCTCODE")
    chat, sdk = _chat_create()
    print(f"[{sdk}] iterating {len(df)} unique product codes -> {jsonl_path}")

    system_msg = {"role": "system", "content": INSTRUCTIONS}
    results = []
    for i, row in df.iterrows():
        user_msg = {"role": "user", "content": _build_user_message(row)}
        try:
            resp = chat(model=MODEL, messages=[system_msg, user_msg])
            response_text = resp.choices[0].message.content
        except Exception as e:
            response_text = None
            print(f"  row {i} ({row.get('PRODUCTCODE')}): error {e}")
            time.sleep(1)

        record = {
            "row_index": i,
            "productcode": row.get("PRODUCTCODE"),
            "devicename": row.get("DEVICENAME"),
            "regulationnumber": row.get("REGULATIONNUMBER"),
            "description_of_regnum": row.get("DESCRIPTION_OF_REGNUM"),
            "subpart_description": row.get("SUBPART_DESCRIPTION"),
            "raw_response": response_text,
        }
        parsed = _extract_json_obj(response_text) if response_text else None
        record["parsed"] = parsed
        record["status"] = "ok" if parsed else "error_no_or_bad_response"
        _save_jsonl(jsonl_path, record)
        results.append(record)

    tidy = pd.DataFrame([_flatten(r) for r in results if r.get("parsed")])
    tidy.to_csv(output_csv, index=False)
    print(f"Wrote {output_csv}: {len(tidy)} parsed rows.")


def apply_manual_corrections(price_links_csv: str) -> None:
    """Apply MANUAL_HCPCS_CORRECTIONS to a tidy GPT_Price_Links CSV in place."""
    import pandas as pd
    df = pd.read_csv(price_links_csv)
    for pc, edits in MANUAL_HCPCS_CORRECTIONS.items():
        mask = df["productcode"] == pc
        if not mask.any():
            continue
        if "hcpcs" in edits:
            df.loc[mask, "hcpcs_cpt"] = edits["hcpcs"]
        if edits.get("procedure_desc"):
            df.loc[mask, "procedure_desc"] = edits["procedure_desc"]
    df.to_csv(price_links_csv, index=False)
    print(f"Applied {len(MANUAL_HCPCS_CORRECTIONS)} manual corrections to {price_links_csv}.")


def main() -> None:
    # II->I direction (matched_sample_2_1_onepat.csv -> 2_1_GPT_Price_Links.csv)
    run_extraction(
        matched_sample_csv="data/derived/matched_sample_2_1_onepat.csv",
        jsonl_path="hcpcs_link_results.jsonl",
        output_csv="data/raw/2_1_GPT_Price_Links.csv",
    )
    apply_manual_corrections("data/raw/2_1_GPT_Price_Links.csv")

    # III->II direction (matched_sample_3_2_onepat.csv -> 3_2_GPT_Price_Links.csv)
    run_extraction(
        matched_sample_csv="data/derived/matched_sample_3_2_onepat.csv",
        jsonl_path="hcpcs_link_results_2.jsonl",
        output_csv="data/raw/3_2_GPT_Price_Links.csv",
    )
    apply_manual_corrections("data/raw/3_2_GPT_Price_Links.csv")


if __name__ == "__main__":
    sys.exit(main())
