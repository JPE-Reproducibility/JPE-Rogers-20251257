"""
gen_03b_lbd_clusters.py -- Generate LBD cluster ID CSVs via pandas_dedupe

Produces:
    data/derived/AD_data_applicant_df_oct22_24.csv   (device-level clusters)
    data/derived/AD_data_applicant_df2_oct22_24.csv  (applicant-level clusters)

These pre-computed cluster IDs are used by gen_03_lbd.py to build the LBD
approval-time panel.

Pipeline:
    1. Load Applicant_Device_data.csv and merge DECISIONDATE from raw FDA data.
    2. Sort by (DEVICENAME, APPLICANT, year) and drop exact (APPLICANT, DEVICENAME)
       duplicates to build the dedupe input.
    3. Run pandas_dedupe.dedupe_dataframe() on ['APPLICANT', 'DEVICENAME'] with
       pre-trained settings → device-level clusters.
    4. Further deduplicate to unique APPLICANTs.
    5. Run pandas_dedupe.dedupe_dataframe() on ['APPLICANT'] with same settings
       → applicant-level clusters.
    6. Save both output CSVs.

The dedupe settings files (dedupe_dataframe_learned_settings, _training.json)
were produced by interactive labelling in the original Fuzzy_matching_lbd_vars
notebook. The pre-trained StaticDedupe model uses normalizedAffineGapDistance
on APPLICANT and DEVICENAME fields with a cophenetic threshold of 0.4.

Reads:
    data/derived/Applicant_Device_data.csv
    data/raw/501k_all.csv
    data/raw/all_pma_approvals.txt
    data/derived/dedupe_settings/dedupe_dataframe_learned_settings
    data/derived/dedupe_settings/dedupe_dataframe_training.json

Writes:
    data/derived/AD_data_applicant_df_oct22_24.csv
    data/derived/AD_data_applicant_df2_oct22_24.csv

Source logic: Fuzzy_matching_lbd_vars.ipynb (cells 2-5, 7, 12, 15, 23-24)
"""

import os
import sys
import shutil
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

SYNTHETIC_MODE = os.environ.get("FDA_SYNTHETIC_MODE") == "1"
if not SYNTHETIC_MODE:
    import pandas_dedupe

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR))
import config

DERIVED = config.DERIVED_DATA_DIR
RAW = config.RAW_DATA_DIR

OUTPUT_AD1 = DERIVED / "AD_data_applicant_df_oct22_24.csv"
OUTPUT_AD2 = DERIVED / "AD_data_applicant_df2_oct22_24.csv"

# Source directory for dedupe settings
DEDUPE_SETTINGS_DIR = DERIVED / "dedupe_settings"


def _dedupe_config_name(settings_dir, prefix="dedupe_dataframe"):
    """Return a config_name path safe for pandas_dedupe.

    pandas_dedupe replaces spaces with underscores in config_name, which
    breaks paths containing spaces. Work around this by
    copying settings to a temp directory when the path has spaces.
    """
    src = str(settings_dir / prefix)
    if " " not in src:
        return src
    tmp = tempfile.mkdtemp(prefix="dedupe_settings_")
    for suffix in ("_learned_settings", "_training.json"):
        src_file = str(settings_dir / (prefix + suffix))
        if os.path.exists(src_file):
            shutil.copy2(src_file, os.path.join(tmp, prefix + suffix))
    return os.path.join(tmp, prefix)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate(out_ad1, out_ad2):
    """Run pandas_dedupe entity resolution to produce cluster ID CSVs."""

    synthetic_mode = SYNTHETIC_MODE
    dedupe_config = None if synthetic_mode else _dedupe_config_name(DEDUPE_SETTINGS_DIR)

    # ------------------------------------------------------------------
    # Phase 1: Load data and merge decision dates
    # ------------------------------------------------------------------
    print("  Phase 1: Loading data and merging decision dates...")
    ad_df = pd.read_csv(DERIVED / "Applicant_Device_data.csv")
    n_raw = len(ad_df)

    k501s = pd.read_csv(RAW / "501k_all.csv", encoding='latin-1', low_memory=False)
    k501s['year'] = pd.DatetimeIndex(k501s['DATERECEIVED']).year

    pmas = pd.read_csv(RAW / "all_pma_approvals.txt",
                       encoding='latin-1', on_bad_lines='skip', sep="|")
    pmas['year'] = pd.DatetimeIndex(pmas['DATERECEIVED']).year
    pmas['DEVICENAME'] = pmas['TRADENAME']

    ad_df = pd.merge(
        ad_df,
        pmas[['PMANUMBER', 'DATERECEIVED', 'DECISIONDATE', 'DEVICENAME', 'PRODUCTCODE']],
        how='left', on=['PMANUMBER', 'DATERECEIVED', 'DEVICENAME', 'PRODUCTCODE'])
    ad_df = pd.merge(
        ad_df,
        k501s[['KNUMBER', 'DATERECEIVED', 'DECISIONDATE']],
        how='left', on=['KNUMBER', 'DATERECEIVED'])
    ad_df = ad_df.drop_duplicates(
        ['PMANUMBER', 'DATERECEIVED', 'DEVICENAME', 'PRODUCTCODE'])
    print(f"    Raw: {n_raw} rows, post-merge: {len(ad_df)} rows")

    # ------------------------------------------------------------------
    # Phase 2: Sort and prepare dedupe input
    # ------------------------------------------------------------------
    print("  Phase 2: Sorting and preparing dedupe input...")
    # Sort by (DEVICENAME, APPLICANT, year) -- matches notebook cell 7
    ad_sorted = ad_df.sort_values(by=["DEVICENAME", "APPLICANT", "year"])

    # Drop exact (APPLICANT, DEVICENAME) duplicates -- keeps earliest year
    dedupe_input = ad_sorted.drop_duplicates(subset=['APPLICANT', 'DEVICENAME'])
    print(f"    Dedupe input (device-level): {len(dedupe_input)} unique "
          f"(APPLICANT, DEVICENAME) pairs")

    # ------------------------------------------------------------------
    # Phase 3: Device-level dedupe
    # ------------------------------------------------------------------
    print("  Phase 3: Running device-level dedupe (APPLICANT + DEVICENAME)...")
    if synthetic_mode:
        ad_data1 = dedupe_input.copy()
        keys = (ad_data1["APPLICANT"].fillna("").astype(str) + "\x1f" +
                ad_data1["DEVICENAME"].fillna("").astype(str))
        ad_data1["cluster id"] = pd.factorize(keys, sort=True)[0]
        ad_data1["confidence"] = 1.0
        print("    Synthetic mode: deterministic exact normalized-pair clustering")
    else:
        print(f"    Using settings: {dedupe_config}_learned_settings")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ad_data1 = pandas_dedupe.dedupe_dataframe(
                dedupe_input,
                ['APPLICANT', 'DEVICENAME'],
                config_name=dedupe_config,
            )
    n_clusters1 = ad_data1['cluster id'].nunique()
    print(f"    Output: {len(ad_data1)} rows, {n_clusters1} device clusters")

    # ------------------------------------------------------------------
    # Phase 4: Applicant-level dedupe
    # ------------------------------------------------------------------
    print("  Phase 4: Running applicant-level dedupe (APPLICANT)...")
    dedupe_input2 = dedupe_input.drop_duplicates('APPLICANT')
    print(f"    Dedupe input (applicant-level): {len(dedupe_input2)} unique APPLICANTs")

    if synthetic_mode:
        ad_data2 = dedupe_input2.copy()
        ad_data2["cluster id"] = pd.factorize(
            ad_data2["APPLICANT"].fillna("").astype(str), sort=True
        )[0]
        ad_data2["confidence"] = 1.0
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ad_data2 = pandas_dedupe.dedupe_dataframe(
                dedupe_input2,
                ['APPLICANT'],
                config_name=dedupe_config,
            )
    n_clusters2 = ad_data2['cluster id'].nunique()
    print(f"    Output: {len(ad_data2)} rows, {n_clusters2} applicant clusters")

    # ------------------------------------------------------------------
    # Phase 5: Save outputs
    # ------------------------------------------------------------------
    print("  Phase 5: Saving outputs...")
    ad_data1.to_csv(out_ad1)
    ad_data2.to_csv(out_ad2)

    print(f"\n  AD_data1: {out_ad1.name}")
    print(f"    Rows: {len(ad_data1):,}")
    print(f"    Device clusters: {n_clusters1:,}")
    print(f"  AD_data2: {out_ad2.name}")
    print(f"    Rows: {len(ad_data2):,}")
    print(f"    Applicant clusters: {n_clusters2:,}")

    return ad_data1, ad_data2


def run(staging=False):
    if staging:
        out_dir = DERIVED / "_generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_ad1 = out_dir / "AD_data_applicant_df_oct22_24.csv"
        out_ad2 = out_dir / "AD_data_applicant_df2_oct22_24.csv"
        print(f"STAGING MODE: writing to {out_dir}")
    else:
        out_ad1 = OUTPUT_AD1
        out_ad2 = OUTPUT_AD2
    generate(out_ad1, out_ad2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting main files")
    args = parser.parse_args()
    print("=== gen_03b_lbd_clusters.py ===")
    run(staging=args.staging)
    print("gen_03b_lbd_clusters.py complete.")
