"""
gen_00c_synthetic_marketscan.py -- SYNTHETIC MarketScan stand-in generator.

WHY THIS EXISTS
---------------
The MarketScan (NBER) claims extracts are the one restricted source that cannot be
transferred to the JPE Data Editor (NBER's agreement requires NBER affiliation;
verification is provider-/enclave-run). The three other restricted sources
(Dimensions, WRDS/CRSP-Compustat, Nexis) have confidential temporary-access routes,
so the Data Editor can run their code on the real (confidential) files.

To satisfy the JPE Data Editor's requirement that confidential data be accompanied by
"a synthetic/simulated dataset allowing the code to run and produce all outputs," this
script generates schema-faithful, fully SYNTHETIC replacements for the three restricted
MarketScan derived files. With these in place, the MarketScan-dependent code runs
end-to-end and produces price/utilization exhibits of the correct shape (with synthetic
numbers; the real estimates are verified in the NBER environment).

WHAT IS REAL VS SYNTHETIC
-------------------------
- REAL (public, not sensitive): the schema; the procedure-code keys (taken from the
  PUBLIC GPT price-link crosswalks so the synthetic claims merge correctly); the
  1996-2013 year span; the product-code / reclassification design.
- SYNTHETIC (randomly generated, seeded): every dollar and quantity value
  (coins, copay, netpay, qty, pay, proc_count, enrolid_count, BilledAmt, PaidAmt).
No real MarketScan claim values are read or reproduced.

OUTPUT
------
Writes into  confidential-data-not-for-publication/synthetic_marketscan/ :
  outpatient_combined_censored.csv   (schema: proc1,year,coins,copay,netpay,qty,pay,proc_count,enrolid_count)
  constrained_adv_event_new_sept25.csv, constrained_adv_event_new_sept25_3_2.csv  (PC-year grids)
To run the MarketScan steps synthetically, copy these over the same-named files in
data/derived/ (in a throwaway working copy). See the confidential-data README.

USAGE
-----
    python3 code/00_generate_data/gen_00c_synthetic_marketscan.py
Deterministic: fixed RNG seed, so re-running reproduces byte-identical output.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
from synthetic_seed import seed

# --- paths (relative to package root) -------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gen_00b_pc_effects as pcmod   # shared PC-level design/theta (PUBLIC product-code universe)
import synthetic_paths
# Single source of truth for column KIND classification -- the SAME `_kind()` function
# certification/validate_payload_contract.py uses to cross-check the shipped payload against
# the committed contract. Importing it (rather than re-deriving the mapping) guarantees the
# generator's own kind-fidelity coercion below can never silently drift from the validator.
_CERT_DIR = os.path.join(ROOT, "certification")
if _CERT_DIR not in sys.path:
    sys.path.insert(0, _CERT_DIR)
from generate_simulation_schema_contract import _kind as _contract_kind

INTERNAL = str(synthetic_paths.internal_dir())
OUT_DIR = os.path.join(INTERNAL, "synthetic_marketscan")
SCHEMA_CONTRACT = os.path.join(INTERNAL, "simulation_schema_contract.json")
# SYNTHETIC price-link crosswalks are GENERATED (not the shipped real ones) and flow through the standard
# synthetic-publish channel: written to _synthetic_source_internal/synthetic_price_links/ -> gen_00g's
# blanket `synthetic_*` glob publishes them to simulated_data/synthetic_price_links/ -> materialize routes
# them to data/raw/ (OVERRIDING the real crosswalk) on the simulated routes (like the synthetic KPST/KPSS).
# gen_00c never writes data/raw itself, so the DEPOSITED data/raw/*_GPT_Price_Links.csv stay REAL for the
# restricted-data reproduction; only the synthetic runs (which run materialize) see the synthetic crosswalk.
PRICE_XWALK_DIR = os.path.join(INTERNAL, "synthetic_price_links")
XWALK_FILES = {
    "2_1": os.path.join(PRICE_XWALK_DIR, "2_1_GPT_Price_Links.csv"),
    "3_2": os.path.join(PRICE_XWALK_DIR, "3_2_GPT_Price_Links.csv"),
}
# Fake-keyed twin of the PUBLIC human-expert device-to-procedure concordance. It travels the same
# synthetic-publish channel as the price-link twins, and materialize routes it OVER the shipped
# public data/raw/FDA_HCPCS_Xwalk_Moazzam.csv on the synthetic routes only. The real file is public
# and keeps shipping, untouched, for the restricted-data reproduction.
EXPERT_XWALK_FILE = os.path.join(PRICE_XWALK_DIR, "FDA_HCPCS_Xwalk_Moazzam.csv")

# --- synthetic procedure-code domain --------------------------------------
# Single source of truth for the domain the simulated MarketScan claims, the synthetic GPT
# price-link twins and the synthetic expert-concordance twin all share: one letter + four digits,
# with a leading "Y". Change this one constant to move the whole domain.
#
# WHY A LETTER PREFIX AT ALL, AND WHY "Y":
#
# (1) The domain must be DISJOINT from every real procedure-code space, because the synthetic files
#     are compared to the real ones value-by-value and a shared value in a sensitive column is a
#     disclosure finding (zero allowed).
#       * HCPCS Level II = one letter + four digits, and the letters in use are A B C D E G H J K L
#         M P Q R S T U V. "Y" is not among them.
#       * CPT Category I = five digits with no letter. CPT Category II = four digits + "F", Category
#         III = four digits + "T", and the Proprietary Laboratory Analyses codes = four digits + "U"
#         -- all LETTER-SUFFIX forms, so a LEADING letter cannot collide with any of them either.
#       * The letters HCPCS and CPT never use are I, N, O, W, X, Y and Z. "I" and "O" are excluded
#         because they read as the digits 1 and 0 in a code column, and "X" because it has been
#         floated for temporary Medicare codes.
#     The predecessor domain used "S", which IS a live HCPCS Level II letter: the synthetic codes
#     then coincided with the real S-codes carried by the public expert crosswalk
#     (data/raw/FDA_HCPCS_Xwalk_Moazzam.csv), and the disclosure audit flagged the overlap.
#
# (2) Among the remaining letters (N, W, Y, Z) the domain must also avoid COINCIDING, in the
#     disclosure audit's canonical form (lowercase, non-alphanumerics stripped), with any value in
#     the real inputs the audit pools -- which include free-form identifier and address fields that
#     happen to take a letter-plus-four-digit shape. Measured over every real input the audit scans,
#     N, W and Z each have at least one such coincidence in the range this generator uses and "Y"
#     has none, so "Y" is the only letter that clears both tests. Re-measure after any change to
#     the real inputs; a coincidence would surface as a finding from
#     synthetic_pipeline/audit_simulated_data.py, which is run before the package is built.
#
# (3) A letter prefix also keeps the domain clear of the pure-digit code corrections wired into
#     05_price_analysis.py (85002/84155/80197/83010/52352/52336), and keeps the shipped proc1 column
#     NON-numeric: a synthetic code column of pure-digit strings (the original "90000".."99999"
#     scheme) round-trips through CSV as int64 on read, which flips proc1 from the committed
#     "string" kind to "integer" (a payload/contract type mismatch).
#
# Disjointness from the three shipped public procedure-code files is checkable directly:
#     grep -cE '(^|,|")Y[0-9]{4}' data/raw/FDA_HCPCS_Xwalk_Moazzam.csv \
#         data/raw/2_1_GPT_Price_Links.csv data/raw/3_2_GPT_Price_Links.csv
# which returns 0 for each.
SYNTHETIC_CODE_PREFIX = "Y"
SYNTHETIC_CODE_DOMAIN_DESC = f"{SYNTHETIC_CODE_PREFIX}0000-{SYNTHETIC_CODE_PREFIX}9998"

# Synthetic claim-year span. The real MarketScan extracts are 1996-2013, but the PUBLIC device
# reclassification years the price/utilization DiD keys on span ~1986-2015 (II->I: 1996/1998; III->II:
# 1986..2015). A synthetic claim window of only 1996-2013 leaves any treated code reclassified BEFORE
# 1996 (all-post) or AFTER 2013 (all-pre) with NO within-unit `posttreat` variation -> feols voids with
# "'posttreat' is collinear with the fixed effects" (05_price_analysis run_static_estimation via
# conley_taber_stacked; also the 04 utilization DiD, which reads the same YEARS-spanned skeleton).
# We therefore widen the SYNTHETIC span to straddle EVERY public reclassification year, so every treated
# code has both pre- and post-reclassification claim rows and the DiD is identified. Calendar years are
# PUBLIC, so this discloses nothing; it only makes the synthetic panel non-degenerate.
YEARS = list(range(1984, 2021))          # 1984-2020: straddles all public reclassification years
SEED = seed(12345)
MIN_CELL = 11                            # <11-enrollee small-cell suppression floor
# The utilization path (04_event_studies.py) also consumes these two MarketScan files:
SKELETON_FILES = [
    "constrained_adv_event_new_sept25.csv",
    "constrained_adv_event_new_sept25_3_2.csv",
]
# Seed offsets per skeleton file. These values are load-bearing: they fix the two grids
# byte-for-byte, so they must not be renumbered (the sequence deliberately starts at 11).
SKELETON_SEED_OFFSET = {
    "constrained_adv_event_new_sept25.csv": 11,
    "constrained_adv_event_new_sept25_3_2.csv": 12,
}


def _needed_procedure_codes():
    """Union of HCPCS/CPT codes referenced by the SYNTHETIC price-link crosswalks (written by
    _write_synthetic_price_crosswalks to the staging dir just above), plus the code corrections applied
    in 05_price_analysis.py. These are exactly the proc1 keys the price analysis merges against -- reading
    the SAME synthetic crosswalk the analysis will see (via materialize) keeps claims and crosswalk HCPCS
    consistent on both simulated routes."""
    codes = set()
    for path in XWALK_FILES.values():
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        for col in ("hcpcs_cpt", "hcpcs_level_2"):
            if col in df.columns:
                for cell in df[col].dropna():
                    for c in str(cell).split(","):
                        c = c.strip()
                        if c and c.lower() != "nan":
                            codes.add(c)
    # corrections / successors used in load_hcpcs_crosswalk + load_claims_data
    codes.update({"85002", "84155", "80197", "83010", "52352", "52336"})
    return sorted(codes)


# Real GPT price-link crosswalk schema. Only productcode / hcpcs_cpt / hcpcs_level_2 /
# procedure_desc are read downstream (this file's _needed_procedure_codes + 05_price's
# load_hcpcs_crosswalk); the remaining columns are schema padding so the synthetic file
# parses identically to the shipped public one.
_XWALK_COLS = ["row_index", "productcode", "devicename", "regulationnumber",
               "description_of_regnum", "subpart_description", "status", "decision",
               "mapping_quality", "hcpcs_cpt", "hcpcs_level_2", "procedure_desc",
               "rationale", "alternates", "confidence"]


def _write_synthetic_price_crosswalks(theta):
    """Generate SYNTHETIC GPT price-link crosswalks over the PUBLIC product-code universe.

    Why this exists (price 'Matched' panel): the shipped 2_1/3_2_GPT_Price_Links.csv are a FROZEN real
    artifact -- 12b_gpt_price_links_generation.py built them by querying GPT for the HCPCS of the
    REAL price matched sample (its 130 treated + 171 control 2->1 codes; 12 + 24 for 3->2). In the
    simulated-data route 02_match_samples regenerates the matched sample from the synthetic
    universe, so its treated/control codes no longer coincide with that frozen crosswalk. The price
    'Matched' panel keeps only codes in (crosswalk ∩ matched_sample): every matched CONTROL drops
    out (the synthetic matching selects controls the real crosswalk never covered), leaving a
    treated-only panel on which `feols(BilledAmt ~ posttreat | factorized^FE + year^FE)` reports
    "posttreat is collinear with the fixed effects" and 05_price fails. (The 'All CPTs' panel
    survives -- it synthesizes controls from all claims codes -- which is why only the crosswalk-
    dependent 'Matched' panel breaks.)

    'Generate, don't map' fix: build the crosswalk from the PUBLIC universe (theta) instead of
    reusing the frozen real one, covering EVERY code that can enter a price matched sample -- all
    reclassified (2_1 / 3_2) codes AND all control codes -- each mapped to a UNIQUE synthetic HCPCS.
    gen_00c then generates claims for every one of those HCPCS (via _needed_procedure_codes, below),
    so whatever treated/control codes the synthetic matching selects have price data and both price
    panels are well posed. Product codes are public (FDA + Federal Register); the HCPCS are synthetic.
    Written to the synthetic-publish STAGING dir (PRICE_XWALK_DIR); gen_00g publishes it to
    simulated_data/synthetic_price_links/ and materialize routes it to data/raw/ (overriding the real
    crosswalk) on both simulated routes -- so the claims below (read from the SAME staging crosswalk) and
    05_price's crosswalk stay HCPCS-consistent for the derived inputs too. gen_00c never writes data/raw, so
    the DEPOSITED data/raw/*_GPT_Price_Links.csv stay REAL for restricted-data reproduction. (The shipped
    crosswalk's codes are really a derived artifact of the RESTRICTED matched sample, not truly public, so
    regenerating them synthetically for the simulated routes also corrects that misclassification.)
    """
    t = theta.copy()
    t["PRODUCTCODE"] = t["PRODUCTCODE"].astype(str)
    is_c = t["is_control"].astype(bool) if "is_control" in t.columns \
        else pd.Series(False, index=t.index)
    events = [("2_1", "is_reclass_2_1", XWALK_FILES["2_1"]),
              ("3_2", "is_reclass_3_2", XWALK_FILES["3_2"])]
    # Three stable, unique synthetic procedure codes per product code across BOTH crosswalks (a
    # control shared by the 2_1 and 3_2 lists keeps the same codes). Multiple procedures per product
    # code provide enough distinct code-year cells to match the disclosure-reviewed approximate
    # dimensions. The codes are drawn from SYNTHETIC_CODE_DOMAIN_DESC (see the constants above
    # SYNTHETIC_CODE_PREFIX): "Y0000".."Y9998", provably disjoint from every real procedure-code
    # space. Rationale for the shape, in order:
    # The full rationale for the letter and the shape is at SYNTHETIC_CODE_PREFIX, above.
    eligible = set()
    for _ev, flag, _p in events:
        f = t[flag].astype(bool) if flag in t.columns else pd.Series(False, index=t.index)
        eligible |= set(t.loc[f | is_c, "PRODUCTCODE"])
    ordered = sorted(eligible)
    if len(ordered) * 3 > 9999:
        raise SystemExit(f"gen_00c: {len(ordered)} price-eligible codes exceed the three-code-per-"
                         f"product-code {SYNTHETIC_CODE_DOMAIN_DESC} range -- widen the range.")
    hcpcs_of = {
        pc: [f"{SYNTHETIC_CODE_PREFIX}{3*i + j:04d}" for j in range(3)]
        for i, pc in enumerate(ordered)
    }
    os.makedirs(PRICE_XWALK_DIR, exist_ok=True)
    for _ev, flag, path in events:
        f = t[flag].astype(bool) if flag in t.columns else pd.Series(False, index=t.index)
        pcs = sorted(set(t.loc[f | is_c, "PRODUCTCODE"]))
        rows = [{
            "row_index": i, "productcode": pc, "devicename": f"SYN_DEVICE_{pc}",
            "regulationnumber": "", "description_of_regnum": "", "subpart_description": "",
            "status": "", "decision": "", "mapping_quality": "synthetic",
            "hcpcs_cpt": ",".join(hcpcs_of[pc]), "hcpcs_level_2": "",
            "procedure_desc": f"SYN_PROC_{pc}", "rationale": "synthetic",
            "alternates": "", "confidence": "synthetic",
        } for i, pc in enumerate(pcs)]
        pd.DataFrame(rows, columns=_XWALK_COLS).to_csv(path, index=False)
        print(f"  wrote synthetic {os.path.basename(path)}  ({len(pcs)} public codes "
              f"[reclass_{_ev} + controls] -> three unique synthetic HCPCS each)")
    return hcpcs_of


# The human-expert concordance's schema, read from the real file's header line only.
# 05_price_analysis.load_expert_hcpcs_crosswalk reads PRODUCTCODE and 'HCCPS Category Code'
# (sic -- the real file's spelling); the other two columns are schema padding so the synthetic
# file parses identically to the public one.
_EXPERT_XWALK_COLS = ["PRODUCTCODE", "HCPCS Level 1 (CPT Code)", "HCPCS Level 2",
                      "HCCPS Category Code"]
# Coverage shape of the real file, so the twin exercises the same code paths: 7,953 rows over
# 5,541 product codes (mean 1.435 rows per code) with the category code populated on 6,125 of
# them (77.0%). Reproduced as probabilities, not as a copy of the real row-per-code pattern.
_EXPERT_ROWS_PER_CODE_P = (0.72, 0.16, 0.12)     # 1, 2 or 3 rows -> mean 1.40
_EXPERT_CATEGORY_FILL_P = 0.77


def _write_synthetic_expert_crosswalk(theta, hcpcs_of):
    """Generate a fake-keyed twin of the HUMAN-EXPERT device-to-procedure concordance.

    `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv` is PUBLIC and ships, so it is not restricted --
    but it carries REAL HCPCS/CPT codes, while the simulated MarketScan claims live entirely
    in the synthetic Y#### procedure-code domain written above (see SYNTHETIC_CODE_PREFIX), which
    is disjoint from every real code space by construction. Without this twin the real concordance
    and the synthetic claims share no procedure code at all: 05_price_analysis's Expert sample
    collapses to a handful of treated codes and its four registered in-text scalars come out
    non-finite, which fails the strict in-text gate. This is exactly the problem the GPT price-link
    twins above solve for the baseline concordance, so it is solved the same way and in the same
    place. (The predecessor domain used an "S" prefix, a live HCPCS Level II letter, so a few links
    survived by namespace collision -- at the price of shipping synthetic codes that coincided with
    real ones, which the disclosure audit correctly flagged. Real links now come from this twin.)

    Construction: PUBLIC product codes (theta's universe -- FDA product codes are public), and
    synthetic procedure codes drawn from the SAME Y#### domain the claims are generated for, so every
    link the analysis follows has claims behind it. A price-eligible code draws only from its
    OWN three synthetic codes, so no control code can inherit a treated code's procedure code
    (load_expert_hcpcs_crosswalk drops overlapping control links); the remaining public codes
    draw from the shared pool, reproducing the real file's many-codes-to-one-procedure shape,
    and are dropped by the matched-sample merge in any case.

    The twin is a DIFFERENT concordance from the GPT twin (1-3 single-code rows per product
    code over the whole public universe, versus all three codes for every price-eligible code),
    so the Expert robustness sample remains a genuinely distinct sample rather than a copy of
    the baseline. Written to the same synthetic-publish staging directory; materialize routes it
    over data/raw/FDA_HCPCS_Xwalk_Moazzam.csv on the simulated route only, so the restricted-data
    reproduction keeps the real public concordance.
    """
    rng = np.random.default_rng(SEED + 77)
    pool = sorted({code for codes in hcpcs_of.values() for code in codes})
    if not pool:
        raise SystemExit("gen_00c: no synthetic HCPCS pool -- price crosswalks must be written first.")
    codes_all = sorted(set(theta["PRODUCTCODE"].astype(str)))
    rows = []
    for pc in codes_all:
        n_rows = int(rng.choice([1, 2, 3], p=_EXPERT_ROWS_PER_CODE_P))
        own = hcpcs_of.get(pc)
        for _ in range(n_rows):
            if rng.random() < _EXPERT_CATEGORY_FILL_P:
                category = str(rng.choice(own)) if own else str(rng.choice(pool))
            else:
                category = ""
            rows.append({
                "PRODUCTCODE": pc,
                "HCPCS Level 1 (CPT Code)": f"SYN_L1_{pc}",
                "HCPCS Level 2": f"SYN_L2_{pc}",
                "HCCPS Category Code": category,
            })
    df = pd.DataFrame(rows, columns=_EXPERT_XWALK_COLS)
    os.makedirs(PRICE_XWALK_DIR, exist_ok=True)
    df.to_csv(EXPERT_XWALK_FILE, index=False)
    filled = int((df["HCCPS Category Code"] != "").sum())
    print(f"  wrote synthetic {os.path.basename(EXPERT_XWALK_FILE)}  ({len(df)} rows over "
          f"{len(codes_all)} public product codes; {filled} carry a synthetic procedure code)")


def _synth_claims(codes, rng):
    """One synthetic (proc1, year) claims row per code-year with plausible, random
    dollar/quantity values. proc_count >= enrolid_count >= MIN_CELL."""
    rows = []
    for code in codes:
        for year in YEARS:
            enrolid_count = int(rng.integers(MIN_CELL, 4000))
            proc_count = enrolid_count + int(rng.integers(0, 2000))
            price_per = float(rng.uniform(50, 3000))
            pay = round(proc_count * price_per, 1)
            netpay = round(pay * float(rng.uniform(0.70, 0.90)), 1)
            copay = round(pay * float(rng.uniform(0.02, 0.10)), 1)
            coins = round(pay * float(rng.uniform(0.00, 0.05)), 1)
            qty = round(proc_count * float(rng.uniform(1.0, 3.0)), 1)
            rows.append((code, year, coins, copay, netpay, qty, pay,
                         proc_count, float(enrolid_count)))
    return pd.DataFrame(rows, columns=[
        "proc1", "year", "coins", "copay", "netpay", "qty", "pay",
        "proc_count", "enrolid_count"])


def _load_market_contract():
    if not os.path.isfile(SCHEMA_CONTRACT):
        raise SystemExit(f"gen_00c: public schema contract missing: {SCHEMA_CONTRACT}")
    with open(SCHEMA_CONTRACT) as f:
        contract = json.load(f)
    specs = contract.get("marketscan_files", {})
    expected = set(SKELETON_FILES) | {"outpatient_combined_censored.csv"}
    missing = sorted(expected - set(specs))
    extra = sorted(set(specs) - expected)
    if missing or extra:
        raise SystemExit(f"gen_00c: MarketScan contract drift; missing={missing}, extra={extra}")
    for name, spec in specs.items():
        if int(spec.get("rows", 0)) <= 0:
            raise SystemExit(f"gen_00c: invalid contract row count for {name}")
        if spec.get("format") != "csv":
            raise SystemExit(f"gen_00c: expected CSV contract for {name}")
    return specs


def _resize_claims(frame, target, preferred_codes, seed):
    """Select exactly target unique proc-year cells while retaining support."""
    if target > len(frame):
        raise SystemExit(f"gen_00c: target {target:,} exceeds {len(frame):,} available claim cells")
    preferred = frame[
        frame["proc1"].isin(preferred_codes) & frame["year"].isin((1984, 1997, 2020))
    ]
    preferred = preferred.drop_duplicates(["proc1", "year"])
    if len(preferred) > target:
        raise SystemExit("gen_00c: claims target too small for required support cells")
    remaining = frame.merge(
        preferred[["proc1", "year"]], on=["proc1", "year"], how="left", indicator=True
    )
    remaining = remaining[remaining["_merge"].eq("left_only")].drop(columns="_merge")
    remaining = remaining.sample(frac=1, random_state=seed)
    out = pd.concat([preferred, remaining.head(target - len(preferred))], ignore_index=True)
    return out.sort_values(["proc1", "year"], kind="mergesort").reset_index(drop=True)


def _coerce_to_contract_kinds(frame, kinds):
    """Final safety-net pass: force every column present in `kinds` (the committed schema
    contract's column_kinds) to actually carry that STRUCTURAL kind -- integer/number/date/
    string, per `_contract_kind()` (== certification/generate_simulation_schema_contract.py's
    `_kind()`, the same classifier certification/validate_payload_contract.py cross-checks the
    shipped payload against) -- regardless of how the column was built upstream. Only the DTYPE
    changes; every value stays synthetic. A column absent from `kinds` or from `frame` is left
    untouched, so this is safe to call with the full per-file column_kinds dict on any frame.
    """
    for col, kind in kinds.items():
        if col not in frame.columns:
            continue
        try:
            if kind == "string":
                frame[col] = frame[col].astype("string")
            elif kind == "integer":
                frame[col] = pd.to_numeric(frame[col], errors="raise").astype("Int64")
            elif kind == "number":
                frame[col] = pd.to_numeric(frame[col], errors="raise").astype(float)
            elif kind == "date":
                frame[col] = pd.to_datetime(frame[col])
            else:
                raise ValueError(f"unrecognized contract kind {kind!r}")
        except (ValueError, TypeError) as exc:
            raise SystemExit(
                f"_coerce_to_contract_kinds: cannot coerce column {col!r} to contract kind "
                f"{kind!r}: {exc}"
            ) from exc
        shipped = _contract_kind(frame[col].dtype)
        # Tolerate the same integer<->number CSV-NaN carve-out validate_payload_contract.py does
        # (a whole-number column round-trips as float64 the instant one cell is NaN); every other
        # disagreement means the coercion above did not actually reach the target kind.
        if shipped != kind and not ({shipped, kind} <= {"integer", "number"}):
            raise SystemExit(
                f"_coerce_to_contract_kinds: column {col!r} still kind {shipped!r} (dtype="
                f"{frame[col].dtype}) after coercing to contract kind {kind!r}"
            )
    return frame


def _validate_contract_frame(frame, spec, name):
    cols = spec.get("columns", [])
    kinds = spec.get("column_kinds", {})
    if list(frame.columns) != cols:
        raise SystemExit(f"gen_00c: schema/order mismatch for {name}")
    if len(frame) != int(spec["rows"]):
        raise SystemExit(f"gen_00c: row-count mismatch for {name}: {len(frame)} != {spec['rows']}")
    for col, kind in kinds.items():
        if kind == "integer" and not pd.api.types.is_integer_dtype(frame[col]):
            raise SystemExit(f"gen_00c: integer type mismatch for {name}:{col} ({frame[col].dtype})")
        if kind == "number" and not pd.api.types.is_numeric_dtype(frame[col]):
            raise SystemExit(f"gen_00c: numeric type mismatch for {name}:{col} ({frame[col].dtype})")


def _select_pc_years(theta, name, target, seed):
    event = "3_2" if "3_2" in name else "2_1"
    flag = f"is_reclass_{event}"
    year_col = f"year_reclassified_{event}"
    if "constrained_adv_event" in name:
        treated = theta.loc[theta[flag].astype(bool), "PRODUCTCODE"].astype(str).tolist()
        controls = theta.loc[theta["is_control"].astype(bool), "PRODUCTCODE"].astype(str).tolist()
        # Equal-sized deterministic control support is sufficient for the matched estimator.
        pcs = treated + controls[:max(len(treated), 1)]
    else:
        pcs = theta["PRODUCTCODE"].astype(str).tolist()
        treated = theta.loc[theta[flag].astype(bool), "PRODUCTCODE"].astype(str).tolist()
        controls = theta.loc[theta["is_control"].astype(bool), "PRODUCTCODE"].astype(str).tolist()
    pcs = list(dict.fromkeys(pcs))
    lookup = theta.set_index(theta["PRODUCTCODE"].astype(str))
    required = []
    for pc in treated:
        y = lookup.loc[pc, year_col]
        if pd.notna(y):
            for yy in (max(YEARS[0], int(y)-1), int(y), min(YEARS[-1], int(y)+1)):
                required.append((pc, yy))
    for pc in controls[:max(len(treated), 1)]:
        required.extend((pc, yy) for yy in (1997, 2005))
    if "utilization" in name:
        required.extend((pc, 1997) for pc in pcs)
    required = list(dict.fromkeys(required))
    universe = [(pc, y) for pc in pcs for y in YEARS]
    if target > len(universe) or len(required) > target:
        raise SystemExit(
            f"gen_00c: {name} target={target:,}, available={len(universe):,}, required={len(required):,}"
        )
    required_set = set(required)
    rest = [pair for pair in universe if pair not in required_set]
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(rest))
    selected = required + [rest[i] for i in order[:target-len(required)]]
    return pd.DataFrame(selected, columns=["PRODUCTCODE", "year"])


def _synth_grid(name, seed, theta, spec):
    """Build a fully synthetic PC-year grid from the committed public schema contract.

    No file under ``data/raw`` or ``data/derived`` is read. The contract contains only
    disclosure-reviewed structural metadata; all values and row membership are generated
    here from public design data.
    """
    cols = spec.get("columns", [])
    kinds = spec.get("column_kinds", {})
    if not cols or set(cols) != set(kinds):
        raise SystemExit(f"gen_00c: invalid schema contract for {name}")
    rng = np.random.default_rng(seed)
    grid = _select_pc_years(theta, name, int(spec["rows"]), seed)
    n = len(grid)
    theta_idx = theta.copy()
    theta_idx["PRODUCTCODE"] = theta_idx["PRODUCTCODE"].astype(str)
    theta_idx = theta_idx.drop_duplicates("PRODUCTCODE").set_index("PRODUCTCODE")
    event = "3_2" if "3_2" in name else "2_1"
    flag = f"is_reclass_{event}"
    year_col = f"year_reclassified_{event}"
    is_treated = grid["PRODUCTCODE"].map(theta_idx[flag]).fillna(False).astype(bool)
    event_year = pd.to_numeric(grid["PRODUCTCODE"].map(theta_idx[year_col]), errors="coerce")
    factor = pd.Categorical(grid["PRODUCTCODE"], categories=sorted(grid["PRODUCTCODE"].unique())).codes
    for c in cols:
        if c in ("PRODUCTCODE", "year"):
            continue
        cl = c.lower()
        if cl == "index":
            grid[c] = np.arange(n, dtype=np.int64)
        elif cl in ("2_1", "3_2"):
            grid[c] = grid["PRODUCTCODE"].map(theta_idx[f"is_reclass_{cl}"]).fillna(False).astype(int)
        elif cl in ("year_reclassified_2_1", "year_reclassified_3_2"):
            suffix = cl.rsplit("_", 2)[-2] + "_" + cl.rsplit("_", 1)[-1]
            grid[c] = pd.to_numeric(grid["PRODUCTCODE"].map(theta_idx[f"year_reclassified_{suffix}"]), errors="coerce")
        elif cl == "year_reclassified":
            grid[c] = event_year
        elif cl == "treatment":
            grid[c] = is_treated.astype(int)
        elif cl == "event_time":
            grid[c] = np.where(is_treated, grid["year"] - event_year, np.nan)
        elif cl == "posttreat":
            grid[c] = (is_treated & (grid["year"] >= event_year)).astype(int)
        elif cl in ("fe", "factorized", "class_by_episode"):
            grid[c] = factor.astype(np.int64)
        elif cl == "fda_own_accord":
            grid[c] = grid["PRODUCTCODE"].map(theta_idx["is_reclass_3_2"]).fillna(False).astype(int)
        elif cl == "proc_count":
            grid[c] = rng.integers(MIN_CELL, 5000, size=n).astype(float)     # strictly > 0 (denominator)
        elif cl in ("pay", "netpay"):
            grid[c] = np.round(rng.uniform(500, 3_000_000, size=n), 1)
        elif cl in ("billedamt", "paidamt"):
            grid[c] = np.round(rng.uniform(1, 500, size=n), 4)
        elif kinds[c] in ("integer", "number"):
            grid[c] = np.round(rng.uniform(0, 1000, size=n), 3)
        else:
            grid[c] = [f"SYN_{cl}_{v}" for v in rng.integers(0, 999999, size=n)]
    missing_cols = [c for c in cols if c not in grid.columns]
    if missing_cols:
        raise SystemExit(f"gen_00c: failed to generate {name} columns: {missing_cols}")
    grid = grid[cols]
    # Fully-populated-support sanity check (kept from the prior per-kind loop): every
    # "integer"-kind column in these synthetic grids is meant to have complete support.
    for c, kind in kinds.items():
        if kind == "integer" and grid[c].isna().any():
            raise SystemExit(f"gen_00c: integer contract column contains NaN: {name}:{c}")
    grid = _coerce_to_contract_kinds(grid, kinds)
    _validate_contract_frame(grid, spec, name)
    grid.to_csv(os.path.join(OUT_DIR, name), index=False)
    print(f"  wrote {name}  ({n:,} independently selected synthetic PC-year rows; "
          f"rounded contract dimension; no real skeleton/sentinels)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    market_specs = _load_market_contract()
    theta = pcmod.load_theta()
    # Build the SYNTHETIC price-link crosswalks FIRST (from the public universe), so the claims
    # below cover every code that can enter a price matched sample and 05_price reads the same map.
    hcpcs_of = _write_synthetic_price_crosswalks(theta)
    # The human-expert concordance twin uses the SAME synthetic procedure-code domain, so the
    # Expert robustness sample in 05_price_analysis has claims behind every link it follows.
    _write_synthetic_expert_crosswalk(theta, hcpcs_of)
    codes = _needed_procedure_codes()
    if not codes:
        raise SystemExit("No procedure codes found in the GPT price-link crosswalks "
                         "-- cannot build synthetic MarketScan claims.")
    print(f"Synthetic MarketScan: {len(codes)} procedure codes x {len(YEARS)} years")
    rng = np.random.default_rng(SEED)
    all_out = _synth_claims(codes, rng)
    # First-of-triplet ("Y{3i}") codes from hcpcs_of, above -- the real correction codes (all pure-digit)
    # never match the SYNTHETIC_CODE_PREFIX test, so this selects exactly the same code set as before
    # the letter-prefix change.
    preferred = [c for c in codes
                 if c.startswith(SYNTHETIC_CODE_PREFIX) and c[1:].isdigit() and int(c[1:]) % 3 == 0]
    out = _resize_claims(all_out, int(market_specs["outpatient_combined_censored.csv"]["rows"]),
                         preferred, SEED + 100)
    out = _coerce_to_contract_kinds(
        out, market_specs["outpatient_combined_censored.csv"]["column_kinds"])
    _validate_contract_frame(out, market_specs["outpatient_combined_censored.csv"],
                             "outpatient_combined_censored.csv")
    out.to_csv(os.path.join(OUT_DIR, "outpatient_combined_censored.csv"), index=False)
    print(f"  wrote outpatient_combined_censored.csv  ({len(out):,} rows)")
    # constrained-adverse-event MarketScan files: FULLY SYNTHETIC grid (F3 -- no real
    # skeleton/sentinels), over the PUBLIC product-code universe from theta (loaded above).
    for name in SKELETON_FILES:
        _synth_grid(name, SEED + SKELETON_SEED_OFFSET[name], theta, market_specs[name])
    print(f"  -> {OUT_DIR}")


if __name__ == "__main__":
    main()
