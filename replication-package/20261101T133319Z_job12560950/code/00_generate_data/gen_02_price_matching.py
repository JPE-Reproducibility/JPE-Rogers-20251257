"""
gen_02_price_matching.py — Build constrained adverse event panels from price matching

This script recreates the matched price panel used as an input to the event
study analysis (04_event_studies.py). It requires PROPRIETARY MarketScan data.
If MarketScan files are not available, the pre-built constrained_adv_event
CSVs must be provided directly.

The GPT Price Links CSVs are also non-deterministic (OpenAI API output) and
must be provided as static files.

Reads:
    data/derived/outpatient_combined_censored.csv     (PROPRIETARY MarketScan)
    data/raw/2_1_GPT_Price_Links.csv                  (GPT-generated)
    data/raw/3_2_GPT_Price_Links.csv                  (GPT-generated)
    data/derived/matched_sample_3_2_onepat.csv        (from 02_match_samples)
    data/derived/matched_sample_2_1_onepat.csv        (from 02_match_samples)

Writes:
    data/derived/constrained_adv_event_new_sept25.csv
    data/derived/constrained_adv_event_new_sept25_3_2.csv

Source logic: Price_data_and_analysis.py lines 740-1932
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR))
import config

DERIVED = config.DERIVED_DATA_DIR
RAW = config.RAW_DATA_DIR


def _check_no_symlinks(paths):
    """Abort if any output path is a symlink (prevents overwriting originals)."""
    bad = [str(p) for p in paths if p.is_symlink()]
    if bad:
        raise RuntimeError(
            "SAFETY CHECK FAILED: Output paths are symlinks. "
            "Replace them with copies before running.\n  " +
            "\n  ".join(bad))


# HCPCS corrections from original code (lines 854-899)
HCPCS_CORRECTIONS = {
    'JCA': {'HCPCS': '85002', 'procedure_desc': 'Bleeding time test'},
    'JGP': {'HCPCS': '84155', 'procedure_desc': 'Measurement of total protein concentration in blood'},
    'MLM': {'HCPCS': '80197', 'procedure_desc': 'therapeutic drug assay of Tacrolimus (FK506) in blood'},
    'DAD': {'HCPCS': '83010'},
}


def _load_gpt_links(filepath, df_matched, reclass_col):
    """Load a GPT Price Links CSV, explode HCPCS codes, and tag treatment."""
    tidy = pd.read_csv(filepath)
    tidy["hcpcs_cpt"] = tidy["hcpcs_cpt"].apply(
        lambda x: str(x).split(",") if pd.notna(x) else [])
    tidy["hcpcs_level_2"] = tidy["hcpcs_level_2"].apply(
        lambda x: str(x).split(",") if pd.notna(x) else [])
    tidy["HCPCS"] = tidy["hcpcs_cpt"] + tidy["hcpcs_level_2"]
    exploded = tidy.explode("HCPCS").reset_index(drop=True)

    exploded['PRODUCTCODE'] = exploded['productcode']
    exploded['HCPCS Level 1 (CPT Code)'] = exploded['hcpcs_cpt']
    exploded['HCPCS Level 2'] = exploded['hcpcs_level_2']
    exploded['HCCPS Category Code'] = exploded['HCPCS']
    exploded['2_1'] = 0
    exploded['3_2'] = 0

    treated_pcs = set(df_matched[df_matched.treatment == 1]['PRODUCTCODE'])
    exploded.loc[exploded.PRODUCTCODE.isin(treated_pcs), reclass_col] = 1

    return exploded[['PRODUCTCODE', 'HCPCS Level 1 (CPT Code)',
                      'HCPCS Level 2', 'HCCPS Category Code',
                      '2_1', '3_2', 'HCPCS', 'procedure_desc']]


def _apply_hcpcs_corrections(fda_to_hcpcs):
    """Apply manual HCPCS code corrections from original code lines 854-899."""
    for pc, corrections in HCPCS_CORRECTIONS.items():
        mask = fda_to_hcpcs.PRODUCTCODE == pc
        if 'HCPCS' in corrections:
            # Assign the corrected code as a SCALAR (broadcast), not a length-1 list. On the real GPT
            # crosswalk each corrected product code maps to exactly one HCPCS row, so `[scalar]` and a
            # scalar are identical. The synthetic crosswalk (gen_00c) maps each product code to THREE
            # unique synthetic HCPCS, so the mask selects 0 or 3 rows; a length-1 list then raises
            # "Must have equal len keys and value". Scalar broadcast is a no-op on the real data (1 row)
            # and fixes the synthetic case (sets every matched row to the manually-verified code).
            fda_to_hcpcs.loc[mask, 'HCPCS Level 1 (CPT Code)'] = corrections['HCPCS']
            fda_to_hcpcs.loc[mask, 'HCCPS Category Code'] = corrections['HCPCS']
            fda_to_hcpcs.loc[mask, 'HCPCS'] = corrections['HCPCS']
        if 'procedure_desc' in corrections:
            fda_to_hcpcs.loc[mask, 'procedure_desc'] = corrections['procedure_desc']
    return fda_to_hcpcs


def _process_claims(rogers_claims_extract):
    """Apply CPT code updates and prepare claims data."""
    # Remove 52336 entirely and remap pre-2001 to 52352
    cpt_update = rogers_claims_extract[
        (rogers_claims_extract.proc1 == '52336') &
        (rogers_claims_extract.year < 2001)].copy()
    cpt_update['proc1'] = '52352'
    cpt_update['ProcCode'] = '52352'
    cpt_update['HCPCS'] = '52352'

    rogers_claims_extract = rogers_claims_extract[
        rogers_claims_extract.proc1 != '52336']
    rogers_claims_extract = pd.concat([rogers_claims_extract, cpt_update])

    # MLM's 1996 cell (carry-back). The claims extract has no 1996 row for CPT 80197, the
    # procedure the expert concordance maps to product code MLM: its claims begin in 1997.
    # Its 1996 cell is carried back from its earliest observed year, 1997, here, so that MLM's
    # claims enter the procedure-level matching and the (product code, year) aggregation in
    # _build_panel_and_export() from 1996 like the other six codes in the III->II panel. The
    # value is the same one the panel's own backfill rule (bfill within product code) would use
    # for the cell, but the carried-back row also enters the matching and aggregation that
    # precede the panel, so the two are not equivalent and the exported grid differs without it.
    # MLM was reclassified in 2002, so the carried-back cell sits at event time -6, in the
    # pre-period.
    # The source row is selected by minimum year, not by file position.
    first_row = (rogers_claims_extract.loc[rogers_claims_extract['proc1'] == '80197']
                 .sort_values('year', kind='stable').iloc[[0]].copy())
    first_row['year'] = 1996
    rogers_claims_extract = pd.concat([first_row, rogers_claims_extract], ignore_index=True)

    return rogers_claims_extract


def _build_panel_and_export(rogers_claims_extract, fda_to_hcpcs_mapping,
                            df_matched, reclass_type, logged=True,
                            FDA_own_accord=True, outcome='BilledAmt',
                            out_dir=None):
    """Build the matched price panel for one reclassification type and export."""

    # Merge claims with HCPCS mapping
    claims = pd.merge(rogers_claims_extract, fda_to_hcpcs_mapping,
                       how='left', on='HCPCS')

    if reclass_type == "2_1":
        claims = claims[claims.year_reclassified != 1996]

    # Filter to previously matched (treatment is not null)
    claims = claims[claims.treatment.notnull()]

    claims['proc_count'] = claims['proc_count'].astype(float)

    # Aggregate by year and product code
    agg_dict = {'pay': 'sum', 'proc_count': 'sum',
                'coins': 'sum', 'year_reclassified': 'mean'}
    if reclass_type == "3_2":
        agg_dict['FDA_own_accord'] = 'mean'

    claims = claims.groupby(['year', 'PRODUCTCODE']).agg(agg_dict).reset_index()
    claims['BilledAmt'] = claims['pay'] / claims['proc_count']
    claims['PaidAmt'] = claims['pay'] / claims['proc_count']

    # Create balanced panel
    full = (claims.set_index(['PRODUCTCODE', 'year'])
            .unstack(fill_value=-99999999999999.0)
            .stack().sort_index(level=1).reset_index())

    # Forward/backward fill
    for col in ['BilledAmt', 'proc_count', 'year_reclassified', 'FDA_own_accord']:
        if col not in full.columns:
            continue
        full.loc[full[col] == -99999999999999.0, col] = np.nan
        full[col] = full.groupby('PRODUCTCODE')[col].transform(lambda v: v.ffill())
        full[col] = full.groupby('PRODUCTCODE')[col].transform(lambda v: v.bfill())

    full['treatment'] = 0
    full.loc[full.year_reclassified.notnull(), 'treatment'] = 1

    # Create stacked panel (duplicate controls for each treated FE)
    subset_t1 = full[full['treatment'] == 1].copy()
    subset_t0 = full[full['treatment'] == 0].copy()
    subset_t1['FE'] = subset_t1['PRODUCTCODE'].astype('category').cat.codes

    duplicated = []
    for i in set(subset_t1['FE']):
        temp = subset_t0.copy()
        temp['FE'] = i
        duplicated.append(temp)

    combined_t0 = pd.concat(duplicated)
    combined_t0['treatment'] = 0
    combined_t0['year_reclassified'] = 0
    stacked = pd.concat([subset_t1, combined_t0])

    new = stacked.copy()
    if reclass_type == "3_2" and FDA_own_accord:
        new = new[(new.treatment == 0) | (new.FDA_own_accord == 1)]

    if outcome == "MarketSize":
        new[outcome] = new['proc_count'] * new['BilledAmt']

    new['event_time'] = new['year'] - new['year_reclassified']

    etpcfull = new[new.treatment.notnull()].copy()
    etpcfull['posttreat'] = 0
    etpcfull.loc[(etpcfull.year >= etpcfull.year_reclassified) &
                 (etpcfull.treatment == 1), 'posttreat'] = 1

    etpcfull['factorized'] = etpcfull.PRODUCTCODE.astype('category').cat.codes
    etpcfull['class_by_episode'] = (etpcfull['PRODUCTCODE'].astype(str) +
                                     "[SEP]" + etpcfull['FE'].astype(str))
    etpcfull['class_by_episode'] = etpcfull.class_by_episode.astype('category').cat.codes
    etpcfull = etpcfull.sort_values(
        by=['treatment', 'class_by_episode', 'year']).reset_index(drop=True)

    if logged:
        etpcfull[outcome] = np.log(etpcfull[outcome])

    # Export
    export = etpcfull.copy()
    if reclass_type == "2_1":
        export['2_1'] = 1
        export['year_reclassified_2_1'] = export['year_reclassified']
        out_name = "constrained_adv_event_new_sept25.csv"
    else:
        export['3_2'] = 1
        export['year_reclassified_3_2'] = export['year_reclassified']
        out_name = "constrained_adv_event_new_sept25_3_2.csv"

    _out = out_dir if out_dir is not None else DERIVED
    out_path = _out / out_name
    export.to_csv(out_path, index=False)
    n_treated = len(set(export[export.treatment == 1]['PRODUCTCODE']))
    n_control = len(set(export[export.treatment == 0]['PRODUCTCODE']))
    print(f"  Wrote {out_name}: {len(export)} rows "
          f"({n_treated} treated PCs, {n_control} control PCs)")


def run(staging=False):
    if staging:
        OUT = DERIVED / "_generated"
        OUT.mkdir(parents=True, exist_ok=True)
        print(f"STAGING MODE: writing to {OUT}")
    else:
        OUT = DERIVED
    # Safety: abort if any output path is a symlink
    _check_no_symlinks([
        OUT / "constrained_adv_event_new_sept25.csv",
        OUT / "constrained_adv_event_new_sept25_3_2.csv",
    ])

    # ------------------------------------------------------------------
    # Check for PROPRIETARY MarketScan data
    # ------------------------------------------------------------------
    outpatient_path = DERIVED / "outpatient_combined_censored.csv"
    if not outpatient_path.exists():
        # Fails closed: the contracted outputs constrained_adv_event_new_sept25{,_3_2}.csv cannot
        # be built without this file, and step 4's utilization-normalized adverse-event exhibits
        # read them. Both official routes supply it (the restricted route from the provider
        # extract, the simulated route from the simulator).
        raise RuntimeError(
            f"MarketScan outpatient claims not found: {outpatient_path}. gen_02 cannot build the "
            "contracted constrained_adv_event_new_sept25{,_3_2}.csv without it. On the restricted "
            "route supply the provider-produced aggregate extract; on the simulated route run "
            "`python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` first."
        )

    # ------------------------------------------------------------------
    # Step 1: Load matched samples
    # ------------------------------------------------------------------
    print("  Loading matched samples...")
    df_3_2_matched = pd.read_csv(
        DERIVED / config.MATCHED_SAMPLES["3_2_onepat"])
    df_2_1_matched = pd.read_csv(
        DERIVED / config.MATCHED_SAMPLES["2_1_onepat"])

    # ------------------------------------------------------------------
    # Step 2: Load and process GPT Price Links
    # ------------------------------------------------------------------
    print("  Loading GPT Price Links...")
    tidy_3_2 = _load_gpt_links(
        RAW / "3_2_GPT_Price_Links.csv", df_3_2_matched, '3_2')
    tidy_2_1 = _load_gpt_links(
        RAW / "2_1_GPT_Price_Links.csv", df_2_1_matched, '2_1')

    fda_to_hcpcs = pd.concat([tidy_3_2, tidy_2_1])
    fda_to_hcpcs = _apply_hcpcs_corrections(fda_to_hcpcs)
    fda_to_hcpcs = fda_to_hcpcs[fda_to_hcpcs.HCPCS.notnull()]

    # ------------------------------------------------------------------
    # Step 3: Create per-reclassification-type HCPCS mappings
    # ------------------------------------------------------------------
    print("  Creating HCPCS mappings per reclassification type...")
    merge_cols = ['PRODUCTCODE', 'FDA_own_accord', 'treatment',
                  'year_reclassified', 'factorized', 'FE']

    fda_3_2 = pd.merge(
        fda_to_hcpcs,
        df_3_2_matched[[c for c in merge_cols if c in df_3_2_matched.columns]].drop_duplicates(),
        on='PRODUCTCODE', how='left')
    fda_3_2 = fda_3_2[fda_3_2.treatment.notnull()]

    fda_2_1 = pd.merge(
        fda_to_hcpcs,
        df_2_1_matched[[c for c in merge_cols if c in df_2_1_matched.columns]].drop_duplicates(),
        on='PRODUCTCODE', how='left')
    fda_2_1 = fda_2_1[fda_2_1.treatment.notnull()]

    # For 2_1: remove control HCPCS codes that overlap with treated
    treated_hcpcs = set(fda_2_1[fda_2_1.treatment == 1]['HCPCS'])
    fda_2_1 = fda_2_1[(fda_2_1.treatment == 1) |
                        ~(fda_2_1.HCPCS.isin(treated_hcpcs))]

    # ------------------------------------------------------------------
    # Step 4: Load and process MarketScan claims
    # ------------------------------------------------------------------
    print("  Loading MarketScan outpatient claims...")
    # Read the procedure code as a string: real HCPCS carry alpha characters so pandas already infers
    # object/string, but the synthetic MarketScan uses all-numeric synthetic HCPCS (90000+), which pandas
    # would otherwise infer as int64 and break the .str accessor below (and the string match to the
    # crosswalk HCPCS). dtype={'proc1': str} is a no-op for the real data and fixes the synthetic case.
    rogers_claims_extract = pd.read_csv(outpatient_path, dtype={"proc1": str})
    rogers_claims_extract['proc1'] = rogers_claims_extract['proc1'].str.strip()
    rogers_claims_extract['BilledAmt'] = (
        rogers_claims_extract['pay'] / rogers_claims_extract['proc_count'])
    rogers_claims_extract['PaidAmt'] = rogers_claims_extract['BilledAmt']
    rogers_claims_extract['ProcCode'] = rogers_claims_extract['proc1']
    rogers_claims_extract['HCPCS'] = rogers_claims_extract['ProcCode']
    rogers_claims_extract = _process_claims(rogers_claims_extract)

    # ------------------------------------------------------------------
    # Step 5: Build and export for each reclassification type
    # ------------------------------------------------------------------
    for rtype, mapping, matched in [("3_2", fda_3_2, df_3_2_matched),
                                     ("2_1", fda_2_1, df_2_1_matched)]:
        print(f"  Building {rtype} matched panel...")
        _build_panel_and_export(
            rogers_claims_extract, mapping, matched,
            reclass_type=rtype, logged=True, FDA_own_accord=True,
            outcome='BilledAmt', out_dir=OUT)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting reference")
    args = parser.parse_args()
    print("=== gen_02_price_matching.py ===")
    run(staging=args.staging)
    print("gen_02_price_matching.py complete.")
