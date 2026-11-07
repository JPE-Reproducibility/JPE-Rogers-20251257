"""
12_invention_year_generation.py
===============================
The default command validates the acquired invention-year inputs and makes no
network calls. The three API generation functions below are retained solely for
provenance and are guarded: each refuses to run unless RUN_GPT_INVENTION_YEARS=1
and an OPENAI_API_KEY is present.

This script documents how the invention-year CSVs in data/raw/ were generated.
The outputs are checked into the replication package as static data files because:
  1. They depend on OpenAI GPT-4o API calls whose responses may vary across runs.
  2. Both II->I and III->II invention years were generated/validated via GPT-4o.
  3. Re-running would require an OpenAI API key and would incur costs.

These invention years are DATA-DERIVED (GPT-4o extracted them from the device /
patent records), then frozen because the external LLM extraction is not
deterministically re-runnable inside the package. Freezing an external,
non-deterministic derivation is standard practice
(JPE Data Policy 2.2). See the REPRODUCIBILITY POLICY block in run_all.py.

The original code lived in a Jupyter notebook outside this package:
  <project>/hcpcs_and_cpt_codes/OpenAI_Upwork.ipynb

------------------------------------------------------------------------------
GENERATION RECORD (JPE Data Policy 2.1a / 4.3)
------------------------------------------------------------------------------
  Provider / model : OpenAI, `gpt-4o` (all three parts below). The *price-link*
                     concordance is a different model -- see
                     12b_gpt_price_links_generation.py, which uses `gpt-5-mini`.
  Sampling settings: temperature=0, one request per product code, rate-limited to
                     60 requests per minute.
  Prompts          : reproduced verbatim below -- instructions_3_2 (Part 1, three
                     few-shot examples) and instructions (Parts 2 and 3, four
                     few-shot examples).
  Date of the run  : 2024-09-09 for the III->II and II->I files, 2024-12-03 for
                     innovation_year_all_other_FDA_project.csv. Evidence is the
                     pre-staging originals I hold outside the package; the
                     shipped CSVs' modification times (2026-02-18 to 2026-02-20)
                     are re-staging dates and do not evidence the run. See
                     README, "Why four artifacts are frozen rather than
                     regenerated", for the mechanism.
  Raw responses    : PARTLY archived. The 25 III->II raw replies ship in
                     data/raw/innovation_year_FDA_project.csv (column `response`),
                     alongside the exact query sent (`query`). The 293 II->I and
                     2,784 all-other raw replies were not retained; only the parsed
                     year (and, for the all-other file, the parsed `source` string)
                     ship.
  Regeneration     : none. No route -- synthetic, from-raw, or provider -- calls
                     this script; the four CSVs are fixed inputs.

Outputs produced (now in data/raw/):
  - innovation_year_2_1_FDA_project.csv        (293 product codes, cols: PRODUCTCODE, years)
  - innovation_year_3_2_FDA_project.csv        (25 product codes,  cols: PRODUCTCODE, years,
                                                 year_reclassified, FDA_own_accord)
  - innovation_year_all_other_FDA_project.csv  (2784 product codes, cols: PRODUCTCODE, years, source)

These files are consumed by:
  - code/11d_reg_design.py  (calculates experience years = year_reclassified - invention year;
    the "all_other" file provides device-age distributions for ALL PMA and 510(K) PCs)
"""

# =============================================================================
# Part 1: III -> II invention years (innovation_year_3_2_FDA_project.csv)
# =============================================================================
#
# Source (project-root input, outside the replication package):
#   <project>/3_2_begin_final_revisions.csv
#
# The source CSV contained hand-coded invention/commercial-availability years
# (column: yr_invent_or_comm_avail). After filtering invalid rows, the remaining
# ~25 product codes were split into:
#   - ranndom_subset: 5 PCs (indices [13, 30, 14, 26, 23]) used as held-out validation
#   - queryit: the remaining ~20 PCs, sent to GPT-4o for independent year estimates
#
# GPT-4o was queried using a separate prompt with 3 few-shot examples (Lens/Contact,
# Soft Contact Lens, Vascular Graft). The GPT-returned years were then compared
# against the hand-coded years via correlation analysis to validate accuracy.
#
# The final "years" column in the output CSV comes from GPT-4o responses (parsed
# via "Year: YYYY" regex), not from the original hand-coded column.
#
# WHERE THE 0.76 VALIDATION + RAW GPT RESPONSES LIVE (read before trusting file names):
#   * data/raw/innovation_year_FDA_project.csv  -- the ORIGINAL 25-row output of this step. It preserves
#     BOTH the raw GPT-4o strings (column `response`, e.g. "['Year: 1978', 'source: ...']"), the GPT year
#     parsed from them (column `years`), AND the hand-coded years (`yr_invent_or_comm_avail`). The
#     manuscript's r=0.76 validation (footnote L500; body L1795; caption L2508) IS
#     corr(yr_invent_or_comm_avail, years) on THIS file = 0.7574 (p=1.2e-05, n=25) -- reproduced + gated by
#     code/15_intext_derived_numbers.py::derived_invention_year_validation.
#   * data/raw/innovation_year_3_2_FDA_project.csv  -- the DOWNSTREAM age-calculation artifact (read by
#     11d_reg_design.py). Its `years` column was REPLACED with the hand-coded values and merged with
#     PRODUCTCODE/year_reclassified/FDA_own_accord, so corr(its years, hand) = 1.0. Do NOT use this file to
#     reproduce the 0.76 -- use the sibling above.
#
# The year_reclassified and FDA_own_accord columns were merged from reclassification
# metadata before export.

import os
import re
import sys
import time
import json
import pandas as pd
try:
    import openai
except ImportError:  # validation does not require the optional API client
    openai = None

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# Run guard for the three API generation functions, as README "Externally generated
# inputs" documents it. The default command (this module's __main__) VALIDATES the
# acquired invention-year inputs and makes no network call; the generation functions
# below refuse to run unless the guard variable is set AND an API key is present.
# Without this the README named a mechanism that did not exist, and a caller who
# imported one of the generation functions would have started billing API calls with
# no confirmation step.
RUN_GUARD_ENV = "RUN_GPT_INVENTION_YEARS"


def _require_generation_guard(what):
    """Refuse to make OpenAI calls unless the replicator has asked for them explicitly."""
    if os.environ.get(RUN_GUARD_ENV) != "1":
        raise SystemExit(
            f"{what} makes OpenAI GPT-4o API calls and is provenance documentation, not part of "
            f"either reproduction route. The authoritative inputs are the invention-year CSVs "
            f"bundled in data/raw/, and an LLM re-run cannot reproduce them exactly. "
            f"Set {RUN_GUARD_ENV}=1 to exercise the call path against the current model."
        )
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            f"{RUN_GUARD_ENV}=1 but OPENAI_API_KEY is not set: {what} cannot run.")
    if openai is None:
        raise SystemExit(
            f"{RUN_GUARD_ENV}=1 but the optional `openai` package is not installed: "
            f"{what} cannot run.")
    print(f"[{RUN_GUARD_ENV}=1] {what}: making live OpenAI API calls. The result will NOT "
          f"reproduce the deposited CSVs exactly (LLM non-determinism).", file=sys.stderr)


def _acquired_input(env_var, filename):
    """Resolve a generation input to a PACKAGE-RELATIVE path under data/raw/.

    Two of the three inputs ship in data/raw/; the third does not, and this says so
    by name.
    """
    path = os.environ.get(env_var) or os.path.join(DATA_DIR, filename)
    if not os.path.isfile(path):
        raise SystemExit(
            f"generation input not found: {path}\n"
            f"  Expected data/raw/{filename}. If it is not in the deposit (some generation "
            f"inputs are author-side working files, not deposited data), point {env_var} at "
            f"your own copy.")
    return path

def generate_3_2_invention_years():
    """
    Query GPT-4o for invention years of III->II reclassified product codes,
    cross-validated against hand-coded years from 3_2_begin_final_revisions.csv.

    WARNING: This function makes OpenAI API calls and should NOT be re-run.
    """
    _require_generation_guard("generate_3_2_invention_years()")
    # --- Load source data (package-relative; override with the env var if needed) ---
    df_3_2 = pd.read_csv(
        _acquired_input("BEGIN_FINAL_REVISIONS_3_2_CSV", "3_2_begin_final_revisions.csv")
    )

    subset = df_3_2[
        df_3_2.yr_invent_or_comm_avail != "Too early for adverse events"
    ][["DEVICENAME", "DESCRIPTION_OF_REGNUM", "yr_invent_or_comm_avail", "source"]]

    subset = subset[subset.yr_invent_or_comm_avail != "0"]
    subset["yr_invent_or_comm_avail"] = subset["yr_invent_or_comm_avail"].astype(int)

    # 5 randomly selected PCs held out for validation
    # indices = array([13, 30, 14, 26, 23])
    ranndom_subset = subset.sample(5)
    queryit = subset[~subset.index.isin([13, 30, 14, 26, 23])]
    queryit["query"] = queryit["DEVICENAME"] + queryit["DESCRIPTION_OF_REGNUM"]

    # --- GPT-4o query (separate prompt from II->I) ---
    instructions_3_2 = (
        "You are an expert in medical devices and have knowledge of when the first "
        "device of a given type was introduced. This could be through the earliest "
        "academic study that presented the device or the first patent filed by its "
        "inventor, whichever came first. I will provide you with a specific medical "
        "device, and I would like you to report back the year it was introduced, "
        "along with the relevant source.\n\n"
        "Here are a few examples:\n\n"
        "User: 'Lens, Contact (Other Material) - DailyRigid gas permeable contact "
        "lens.\\n' Response: ['Year: 1979', 'source: first patent filed by Norman "
        "Gaylord for rigid gas permeable (RGP) contact lenses.'] \n"
        "User: 'Lenses, Soft Contact, Daily WearSoft (hydrophilic) contact lens.'"
        "\\n Response: ['Year: 1960', 'source: first academic study by Otto "
        "Wichterle and Drahoslav Lim, who developed the first soft (hydrophilic) "
        "contact lenses.'] \n"
        "User: 'Graft, Vascular, Synthetic/Biologic CompositeVascular graft "
        "prosthesis.'\\n Response: ['Year: 1952', 'source: Voorhees, A. B., "
        "Jaretzki, A., & Blakemore, A. H. (1952). The use of tubes constructed "
        "from vinyon N cloth in bridging arterial defects. Annals of Surgery, "
        "135(3), 332-336.'] \n"
    )

    queries_per_minute = 60
    time_between_queries = 60 / queries_per_minute
    last_query_time = time.time() - time_between_queries
    response_list = []

    for i, text_example in enumerate(queryit["query"].values):
        send_to_gpt = [
            {"role": "system", "content": instructions_3_2},
            {"role": "user", "content": text_example},
        ]

        while time.time() - last_query_time < time_between_queries:
            time.sleep(0.1)
        last_query_time = time.time()

        for attempt in range(200):
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=send_to_gpt,
                    temperature=0,
                )
                response_content = response.choices[0].message.content
                response_list.append(response_content)
                break
            except Exception:
                print(f"An error occurred on query {i}. Retrying...")
                time.sleep(3600)

    # --- Parse responses and combine ---
    queryit["response"] = response_list
    combined_answers = pd.concat([ranndom_subset, queryit])
    combined_answers["years"] = [
        re.search(r"Year:\s*(\d{4})", entry).group(1)
        for entry in combined_answers["response"]
    ]
    combined_answers["years"] = combined_answers["years"].astype(int)

    # --- Validation: correlate GPT years vs hand-coded years ---
    # correlation = combined_answers['yr_invent_or_comm_avail'].corr(combined_answers['years'])

    # --- Export ---
    # The final CSV also includes year_reclassified and FDA_own_accord columns,
    # which were merged from reclassification metadata before export.
    # Output: innovation_year_3_2_FDA_project.csv
    # Columns: PRODUCTCODE, years, year_reclassified, FDA_own_accord
    # 25 product codes


# =============================================================================
# Part 2: II -> I invention years (innovation_year_2_1_FDA_project.csv)
# =============================================================================
#
# Source (project-root input, outside the replication package):
#   <project>/DPM2_1_1997/for_gpt_2_1_invention_dates.csv
#         (and additional batches from for_gpt_2_1_2017_invention_dates.csv, etc.)
#
# Each product code's device name + regulatory description was sent to GPT-4o
# with expert instructions asking for the year the first device of that type
# was introduced (earliest academic study or first patent filed).
#
# GPT responses were parsed with regex to extract "Year: YYYY" and "source: ...".

def generate_2_1_invention_years():
    """
    Query GPT-4o for invention years of II->I reclassified product codes.

    WARNING: This function makes ~293 OpenAI API calls and should NOT be re-run.
    """
    _require_generation_guard("generate_2_1_invention_years()")
    # --- Load source data ---
    # The 1996/1998 reclassification batch:
    df_2_1 = pd.read_csv(
        _acquired_input("GPT_2_1_INVENTION_DATES_CSV", "for_gpt_2_1_invention_dates.csv")
    )
    df_2_1["query"] = df_2_1["DEVICENAME"] + df_2_1["DESCRIPTION_OF_REGNUM"]

    # The 2017 reclassification batch (run separately, then combined):
    # df_2_1_2017 = pd.read_csv(
    #     _acquired_input("GPT_2_1_2017_INVENTION_DATES_CSV",
    #                     "for_gpt_2_1_2017_invention_dates.csv")
    # )
    # df_2_1_2017["query"] = df_2_1_2017["DEVICENAME"] + " " + df_2_1_2017["DESCRIPTION_OF_REGNUM"]

    # --- GPT-4o query ---
    instructions = (
        "You are an expert in medical devices and have knowledge of when the first "
        "device of a given type was introduced. This could be through the earliest "
        "academic study that presented the device or the first patent filed by its "
        "inventor, whichever came first. I will provide you with a specific medical "
        "device, and I would like you to report back the year it was introduced, "
        "along with the relevant source.\n\n"
        "Here are a few examples:\n\n"
        "User: 'Sterilizer, Soft-Lens, Thermal, Ac-Powered, Soft (hydrophilic) "
        "contact lens care products.\\n' Response: ['Year: 1974', 'source: first "
        "patent filed by Cybron Corp. likely used some time before.'] \n"
        "User: 'Stimulator, Salivary System, Electrical salivary stimulatory "
        "system.'\\n Response: ['Year: 1986', 'source: first submitted PMA. Weiss "
        "1986. subsequent study in 1988 by steller M.'] \n"
        "User: 'Device, Vascular, For Promoting Embolization, Vascular embolization "
        "device.'\\n Response: ['Year: 1975', 'Wooly tail embolization coil invented "
        "by Cesare Gianturco.'] \n"
        "User: 'Intervertebral Fusion Device With Bone Graft, Lumbar, "
        "Intervertebral body fusion device.' \\n Response: ['Year: 1953', 'source: "
        "The Treatment of Ruptured Lumbar Intervertebral Discs by Vertebral Body "
        "Fusion: I. Indications, Operative Technique, After Care.'] \n"
    )

    queries_per_minute = 60
    time_between_queries = 60 / queries_per_minute
    last_query_time = time.time() - time_between_queries
    response_list = []

    for i, text_example in enumerate(df_2_1["query"].values):
        send_to_gpt = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": text_example},
        ]

        while time.time() - last_query_time < time_between_queries:
            time.sleep(0.1)
        last_query_time = time.time()

        for attempt in range(200):
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=send_to_gpt,
                    temperature=0,
                )
                response_content = response.choices[0].message.content
                response_list.append(response_content)
                break
            except Exception:
                print(f"An error occurred on query {i}. Retrying...")
                time.sleep(3600)  # original wait was 1 hour for rate-limit resets

    # --- Parse responses ---
    df_2_1["response"] = response_list
    df_2_1["years"] = df_2_1["response"].str.extract(r"Year:\s*(\d{4})")[0]
    df_2_1["years"] = pd.to_numeric(df_2_1["years"], errors="coerce")
    df_2_1["source"] = df_2_1["response"].str.extract(r"source:\s*(.*?)(?:\.|$)")[0]

    # --- Export ---
    out_path = os.path.join(DATA_DIR, "innovation_year_2_1_FDA_project.csv")
    df_2_1[["PRODUCTCODE", "years"]].to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    # Output: innovation_year_2_1_FDA_project.csv
    # Columns: PRODUCTCODE, years
    # 293 product codes


# =============================================================================
# Part 3: All-other invention years (innovation_year_all_other_FDA_project.csv)
# =============================================================================
#
# Source: RegNum_Factorized_Synth.csv (all FDA product codes with regulatory metadata)
#
# This file covers ALL 510(K) and PMA product codes -- not just those in the
# II->I or III->II reclassification cohorts. It is used by 11d_reg_design.py
# to produce Figures D.11a/b (distribution of device experience years for all
# Class III PMA devices and all Class II 510(K) devices).
#
# Generation process (OpenAI_Upwork.ipynb, cells 21-25):
#   1. Load RegNum_Factorized_Synth.csv, deduplicate by PRODUCTCODE_x
#   2. Filter to SUBMISSION_TYPE_ID in ('510(K)', 'PMA') -- 2784 product codes
#   3. Concatenate DEVICENAME + DESCRIPTION_OF_REGNUM as query text
#   4. Send each query to GPT-4o with the same prompt/instructions as Part 2
#      (expert in medical devices, report year of first introduction + source)
#   5. Parse responses: extract "Year: YYYY" and "source: ..." via regex
#   6. Export PRODUCTCODE, years, source to CSV
#
# The exported file includes the 'source' column (free-text provenance from GPT)
# which is not present in the 2_1 or 3_2 files.

def generate_all_other_invention_years():
    """
    Query GPT-4o for invention years of ALL 510(K) and PMA product codes.

    WARNING: This function makes ~2784 OpenAI API calls and should NOT be re-run.
    """
    _require_generation_guard("generate_all_other_invention_years()")
    synth_number = pd.read_csv(
        _acquired_input("REGNUM_FACTORIZED_SYNTH_CSV", "RegNum_Factorized_Synth.csv"),
        dtype={"REGULATIONNUMBER": str},
    )
    synth_number = synth_number.drop_duplicates("PRODUCTCODE_x")
    synth_number["PRODUCTCODE"] = synth_number["PRODUCTCODE_x"]

    df = synth_number.copy()
    df["DEVICENAME"] = df["DEVICENAME"].fillna("")
    df["DESCRIPTION_OF_REGNUM"] = df["DESCRIPTION_OF_REGNUM"].fillna("")
    df["query"] = df["DEVICENAME"] + " " + df["DESCRIPTION_OF_REGNUM"]
    df = df[df.SUBMISSION_TYPE_ID.isin(["510(K)", "PMA"])]

    # --- GPT-4o query (same instructions as Part 2) ---
    instructions = (
        "You are an expert in medical devices and have knowledge of when the first "
        "device of a given type was introduced. This could be through the earliest "
        "academic study that presented the device or the first patent filed by its "
        "inventor, whichever came first. I will provide you with a specific medical "
        "device, and I would like you to report back the year it was introduced, "
        "along with the relevant source.\n\n"
        "Here are a few examples:\n\n"
        "User: 'Sterilizer, Soft-Lens, Thermal, Ac-Powered, Soft (hydrophilic) "
        "contact lens care products.\\n' Response: ['Year: 1974', 'source: first "
        "patent filed by Cybron Corp. likely used some time before.'] \n"
        "User: 'Stimulator, Salivary System, Electrical salivary stimulatory "
        "system.'\\n Response: ['Year: 1986', 'source: first submitted PMA. Weiss "
        "1986. subsequent study in 1988 by steller M.'] \n"
        "User: 'Device, Vascular, For Promoting Embolization, Vascular embolization "
        "device.'\\n Response: ['Year: 1975', 'Wooly tail embolization coil invented "
        "by Cesare Gianturco.'] \n"
        "User: 'Intervertebral Fusion Device With Bone Graft, Lumbar, "
        "Intervertebral body fusion device.' \\n Response: ['Year: 1953', 'source: "
        "The Treatment of Ruptured Lumbar Intervertebral Discs by Vertebral Body "
        "Fusion: I. Indications, Operative Technique, After Care.'] \n"
    )

    queries_per_minute = 60
    time_between_queries = 60 / queries_per_minute
    last_query_time = time.time() - time_between_queries
    response_list = []

    for i, text_example in enumerate(df["query"].values):
        send_to_gpt = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": text_example},
        ]

        while time.time() - last_query_time < time_between_queries:
            time.sleep(0.1)
        last_query_time = time.time()

        for attempt in range(200):
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=send_to_gpt,
                    temperature=0,
                )
                response_content = response.choices[0].message.content
                response_list.append(response_content)
                break
            except Exception:
                print(f"An error occurred on query {i}. Retrying...")
                time.sleep(3600)

    # --- Parse responses ---
    df["response"] = response_list
    df["years"] = df["response"].str.extract(r"Year:\s*(\d{4})")[0]
    df["years"] = pd.to_numeric(df["years"], errors="coerce")
    df["source"] = df["response"].str.extract(r"source:\s*(.*?)(?:\.|$)")[0]

    # --- Export ---
    out_path = os.path.join(DATA_DIR, "innovation_year_all_other_FDA_project.csv")
    df[["PRODUCTCODE", "years", "source"]].to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    # Output: innovation_year_all_other_FDA_project.csv
    # Columns: PRODUCTCODE, years, source
# 2784 product codes


def validate_acquired_invention_year_inputs():
    """Fail-closed validation for the author-curated external-API input files.

    The GPT calls are source acquisition, not a deterministic transformation.
    The public synthetic route executes this validation instead of contacting an
    external API. Downstream transformations then consume the validated files.
    """
    specs = {
        "innovation_year_2_1_FDA_project.csv": {"PRODUCTCODE", "years"},
        "innovation_year_3_2_FDA_project.csv": {"PRODUCTCODE", "years"},
        "innovation_year_all_other_FDA_project.csv": {"PRODUCTCODE", "years"},
    }
    for name, required in specs.items():
        path = os.path.join(DATA_DIR, name)
        if not os.path.isfile(path):
            raise RuntimeError(f"required acquired invention-year input missing: {path}")
        df = pd.read_csv(path)
        missing = required - set(df.columns)
        if missing:
            raise RuntimeError(f"{name} lacks required columns: {sorted(missing)}")
        if df.empty or df["PRODUCTCODE"].isna().any() or df["PRODUCTCODE"].duplicated().any():
            raise RuntimeError(f"{name} must contain unique, nonmissing PRODUCTCODE rows")
        years = pd.to_numeric(df["years"], errors="coerce")
        # Some device families have genuinely early antecedents (the curated
        # file includes dates before 1800), so validate a broad historical
        # support rather than imposing a modern-device cutoff.
        if years.isna().any() or not years.between(1000, 2026).all():
            raise RuntimeError(f"{name} has missing or out-of-range invention years")
        print(f"Validated acquired input {name}: {len(df):,} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_acquired_invention_year_inputs())
