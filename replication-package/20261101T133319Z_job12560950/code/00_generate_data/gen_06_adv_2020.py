"""
gen_06_adv_2020.py — Aggregate MAUDE adverse events for 2020-2022

Reads:
    data/raw/MAUDE_2020/device_data/*.txt   (device-level event files)
    data/raw/MAUDE_2020/masterevent.txt
    data/raw/MAUDE_2020/patient.txt
    data/raw/MAUDE_2020/deviceproblems.txt
    data/raw/MAUDE_2020/problemcodedesc.txt

Writes:
    data/derived/Adv_Event_2020_2022.csv

Source logic: Recall_Analysis_2017_1998_appendix.py lines 1165-1265
"""

import sys
import gc
from pathlib import Path
from os.path import isfile, join
from os import listdir

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR))
import config

# MAUDE 2020-2022 data directory
MAUDE_2020_DIR = config.RAW_DATA_DIR / "MAUDE_2020"

OUTCOME_CODES = ["L", "H", "S", "C", "R", "O", "U", "I", "A", "D"]

DEVICE_COLS = [
    'MDR_REPORT_KEY', 'DEVICE_EVENT_KEY', 'IMPLANT_FLAG', 'DATE_REMOVED_FLAG',
    'DEVICE_SEQUENCE_NO', 'DATE_RECEIVED', 'BRAND_NAME', 'GENERIC_NAME',
    'MANUFACTURER_D_NAME', 'MANUFACTURER_D_ADDRESS_1', 'MANUFACTURER_D_CITY',
    'EXPIRATION_DATE_OF_DEVICE', 'MODEL_NUMBER', 'CATALOG_NUMBER', 'LOT_NUMBER',
    'OTHER_ID_NUMBER', 'DEVICE_OPERATOR', 'DEVICE_AVAILABILITY',
    'DATE_RETURNED_TO_MANUFACTURER', 'DEVICE_REPORT_PRODUCT_CODE',
    'DEVICE_AGE_TEXT', 'DEVICE_EVALUATED_BY_MANUFACTUR',
]


def _check_no_symlinks(paths):
    """Abort if any output path is a symlink (prevents overwriting originals)."""
    bad = [str(p) for p in paths if p.is_symlink()]
    if bad:
        raise RuntimeError(
            "SAFETY CHECK FAILED: Output paths are symlinks. "
            "Replace them with copies before running.\n  " +
            "\n  ".join(bad))


def run(staging=False):
    if staging:
        OUT = config.DERIVED_DATA_DIR / "_generated"
        OUT.mkdir(parents=True, exist_ok=True)
        print(f"STAGING MODE: writing to {OUT}")
    else:
        OUT = config.DERIVED_DATA_DIR

    # Safety: abort if any output path is a symlink
    _check_no_symlinks([
        OUT / "Adv_Event_2020_2022.csv",
    ])

    device_data_dir = MAUDE_2020_DIR / "device_data"
    if not device_data_dir.exists():
        # Fails closed: the contracted output Adv_Event_2020_2022.csv cannot be built without
        # this directory.
        raise RuntimeError(
            f"MAUDE 2020-2022 device_data directory not found: {device_data_dir}. It is required "
            "to build the contracted output Adv_Event_2020_2022.csv. Provide the public FDA MAUDE "
            "2020-2022 extract (see DATA_INPUTS.md) or, on the simulated route, run "
            "`python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` first."
        )

    # Load reference tables
    master_event = pd.read_csv(
        MAUDE_2020_DIR / "masterevent.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        usecols=['MDR_REPORT_KEY', 'DATE_RECEIVED'])
    patients = pd.read_csv(
        MAUDE_2020_DIR / "patient.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        usecols=['MDR_REPORT_KEY', 'PATIENT_SEQUENCE_NUMBER', 'SEQUENCE_NUMBER_OUTCOME'])
    device_problems = pd.read_csv(
        MAUDE_2020_DIR / "deviceproblems.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        header=None, names=['MDR_REPORT_KEY', 'DEVICE_PROBLEM_CODE'],
        usecols=[0, 1])
    problem_codes = pd.read_csv(
        MAUDE_2020_DIR / "problemcodedesc.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        names=['DEVICE_PROBLEM_CODE', 'PROBLEM_DESCRIPTION'])

    # Process each device file
    onlyfiles = sorted([f for f in listdir(device_data_dir)
                        if isfile(join(device_data_dir, f)) and f != ".DS_Store"])

    grouped_parts = []

    for file in onlyfiles:
        print(f"  Processing {file}...")
        # Read the full FDA file before selecting columns so pandas applies
        # the same bad-line handling as the original full-schema pipeline.
        df = pd.read_csv(
            device_data_dir / file,
            encoding='latin-1', on_bad_lines='skip', sep="|")
        df = df[[c for c in ['MDR_REPORT_KEY', 'DATE_RECEIVED', 'DEVICE_REPORT_PRODUCT_CODE']
                 if c in df.columns]]

        # Merge with master event, patients, device problems
        merged = pd.merge(master_event, df, on="MDR_REPORT_KEY", how="inner")
        merged = merged.dropna(subset=['DATE_RECEIVED_y'])
        merged = pd.merge(merged, patients, on="MDR_REPORT_KEY", how="left")
        merged = pd.merge(merged, device_problems, on="MDR_REPORT_KEY", how="left")
        merged = pd.merge(merged, problem_codes, on="DEVICE_PROBLEM_CODE", how="left")
        merged.SEQUENCE_NUMBER_OUTCOME = merged.SEQUENCE_NUMBER_OUTCOME.fillna("None")

        # Create binary outcome indicators
        for code in OUTCOME_CODES:
            merged[code] = merged.SEQUENCE_NUMBER_OUTCOME.str.contains(code).astype(int)

        merged['year'] = pd.DatetimeIndex(merged['DATE_RECEIVED_x']).year
        merged['PRODUCTCODE'] = merged['DEVICE_REPORT_PRODUCT_CODE']
        merged['event_count'] = 1

        grouped = (
            merged.groupby(['PRODUCTCODE', 'year'])[OUTCOME_CODES + ['event_count']]
            .sum()
            .reset_index()
        )
        grouped_parts.append(grouped)

        del df, merged, grouped
        gc.collect()

    # Aggregate by product code and year
    df_combined_grouped = (
        pd.concat(grouped_parts, ignore_index=True)
        .groupby(['PRODUCTCODE', 'year'])[OUTCOME_CODES + ['event_count']]
        .sum()
        .reset_index()
    )
    df_combined_grouped = (df_combined_grouped.set_index(['PRODUCTCODE', 'year'])
                  .unstack(fill_value=0)
                  .stack()
                  .sort_index(level=1)
                  .reset_index())

    out_path = OUT / "Adv_Event_2020_2022.csv"
    df_combined_grouped.to_csv(out_path, index=False)
    print(f"  Wrote {out_path.name}: {len(df_combined_grouped)} rows")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting reference")
    args = parser.parse_args()
    print("=== gen_06_adv_2020.py ===")
    run(staging=args.staging)
    print("gen_06_adv_2020.py complete.")
