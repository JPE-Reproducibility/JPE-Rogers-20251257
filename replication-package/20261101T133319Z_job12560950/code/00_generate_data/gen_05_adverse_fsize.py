"""
gen_05_adverse_fsize.py — Build adverse event panel with firm size

The full pipeline requires interactive fuzzy matching of manufacturer names
to CRSP/Compustat identifiers via pandas_dedupe. The manufacturer→permno
mapping must be provided pre-built.

Reads:
    data/raw/MAUDE/device_data/*.csv         (MAUDE device-level event files)
    data/raw/MAUDE/masterevent.txt
    data/raw/MAUDE/patient.txt
    data/raw/MAUDE/deviceproblems.txt
    data/raw/MAUDE/problemcodedesc.txt
    data/derived/all_adv_events_w_permno5.csv  (pre-built manufacturer→permno mapping)
    data/raw/compustat_firm_data.csv           (Compustat total assets)
    data/raw/CPI_deflator.csv                  (CPI deflator for real dollars)

Writes:
    data/derived/Adverse_fsize_ready_all4_oct22_24.csv

Source logic: Dedupe_Manuf_firm_size_adverse_events.py lines 1505-1682
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

DERIVED = config.DERIVED_DATA_DIR
RAW = config.RAW_DATA_DIR

MAUDE_DIR = RAW / "MAUDE"
OUTCOME_CODES = ["L", "H", "S", "C", "R", "O", "U", "I", "A", "D"]


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
        OUT = DERIVED / "_generated"
        OUT.mkdir(parents=True, exist_ok=True)
        print(f"STAGING MODE: writing to {OUT}")
    else:
        OUT = DERIVED
    # Safety: abort if any output path is a symlink
    _check_no_symlinks([
        OUT / "Adverse_fsize_ready_all4_oct22_24.csv",
    ])
    device_data_dir = MAUDE_DIR / "device_data"
    if not device_data_dir.exists():
        # Fails closed: the contracted output Adverse_fsize_ready_all4_oct22_24.csv cannot be
        # built without this directory.
        raise RuntimeError(
            f"MAUDE device_data directory not found: {device_data_dir}. It is required to build "
            "the contracted output Adverse_fsize_ready_all4_oct22_24.csv. Provide the public FDA "
            "MAUDE extract (see DATA_INPUTS.md) or, on the simulated route, run "
            "`python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` first."
        )

    # ------------------------------------------------------------------
    # Step 1: Load MAUDE reference tables
    # ------------------------------------------------------------------
    print("  Loading MAUDE reference tables...")
    master_event = pd.read_csv(
        MAUDE_DIR / "masterevent.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        usecols=['MDR_REPORT_KEY', 'DATE_RECEIVED'])
    patients = pd.read_csv(
        MAUDE_DIR / "patient.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        usecols=['MDR_REPORT_KEY', 'PATIENT_SEQUENCE_NUMBER', 'SEQUENCE_NUMBER_OUTCOME'])
    device_problems = pd.read_csv(
        MAUDE_DIR / "deviceproblems.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        header=None, names=['MDR_REPORT_KEY', 'DEVICE_PROBLEM_CODE'],
        usecols=[0, 1])
    problem_codes = pd.read_csv(
        MAUDE_DIR / "problemcodedesc.txt",
        encoding='latin-1', on_bad_lines='skip', sep="|",
        names=['DEVICE_PROBLEM_CODE', 'PROBLEM_DESCRIPTION'])

    # ------------------------------------------------------------------
    # Step 2: Load manufacturer→permno and firm-size lookups once
    # ------------------------------------------------------------------
    print("  Merging manufacturer permno mapping...")
    permno_cols = ['MDR_REPORT_KEY', 'clean_name', 'permno', 'stock_name',
                   'manually_encoded', 'manual_stock']
    all_adv_events_w_permno = pd.read_csv(
        DERIVED / "all_adv_events_w_permno5.csv",
        usecols=lambda c: c in permno_cols,
    )
    all_adv_events_w_permno = all_adv_events_w_permno.drop_duplicates("MDR_REPORT_KEY")

    print("  Merging Compustat firm size...")
    firm_data = pd.read_csv(RAW / "compustat_firm_data.csv")
    firm_data['firm_size'] = firm_data['at']
    firm_data['permno'] = firm_data['LPERMNO']
    firm_data = firm_data[~firm_data.fyear.isnull()]
    firm_data['year'] = firm_data['fyear'].astype(int)

    CPI = pd.read_csv(RAW / "CPI_deflator.csv")
    firm_data = pd.merge(firm_data, CPI, on="year", how='left')
    firm_data['firm_size'] *= firm_data['CPI']
    firm_grouped = firm_data[['permno', 'firm_size']].groupby('permno').mean().reset_index()

    keep_cols = [
        'DEVICE_PROBLEM_CODE', 'PROBLEM_DESCRIPTION',
        'L', 'H', 'S', 'C', 'R', 'O', 'U', 'I', 'A', 'D',
        'year', 'PRODUCTCODE', 'event_count', 'file_year',
        'clean_name', 'permno', 'stock_name',
        'manually_encoded', 'manual_stock', 'firm_size',
    ]

    # ------------------------------------------------------------------
    # Step 3: Process one device file at a time and append output
    # ------------------------------------------------------------------
    out_path = OUT / "Adverse_fsize_ready_all4_oct22_24.csv"
    tmp_path = OUT / (out_path.name + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    print("  Processing MAUDE device files...")
    onlyfiles = sorted([f for f in listdir(device_data_dir)
                        if isfile(join(device_data_dir, f)) and f != ".DS_Store"])

    total_rows = 0
    wrote_header = False
    for file in onlyfiles:
        print(f"    {file}")
        df = pd.read_csv(
            device_data_dir / file,
            encoding='latin-1', on_bad_lines='skip', sep="|",
            usecols=['MDR_REPORT_KEY', 'DEVICE_REPORT_PRODUCT_CODE', 'DATE_RECEIVED'])

        merged = pd.merge(master_event, df, on="MDR_REPORT_KEY", how="inner")
        merged = merged.dropna(subset=['DATE_RECEIVED_y'])
        merged = pd.merge(merged, patients, on="MDR_REPORT_KEY", how="left")
        merged = pd.merge(merged, device_problems, on="MDR_REPORT_KEY", how="left")
        merged = pd.merge(merged, problem_codes, on="DEVICE_PROBLEM_CODE", how="left")
        merged.SEQUENCE_NUMBER_OUTCOME = merged.SEQUENCE_NUMBER_OUTCOME.fillna("None")

        for code in OUTCOME_CODES:
            merged[code] = merged.SEQUENCE_NUMBER_OUTCOME.str.contains(code).astype(int)

        merged['year'] = pd.DatetimeIndex(merged['DATE_RECEIVED_x']).year
        merged['PRODUCTCODE'] = merged['DEVICE_REPORT_PRODUCT_CODE']
        merged['event_count'] = 1
        merged['file_year'] = file

        merged = pd.merge(
            merged, all_adv_events_w_permno, on="MDR_REPORT_KEY", how='left')
        merged = pd.merge(
            merged, firm_grouped[['permno', 'firm_size']],
            on='permno', how='left')
        merged = merged[keep_cols]

        merged.to_csv(
            tmp_path, index=False, mode="a",
            header=not wrote_header,
        )
        wrote_header = True
        total_rows += len(merged)

        del df, merged
        gc.collect()

    tmp_path.replace(out_path)
    print(f"  Wrote {out_path.name}: {total_rows} rows")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting reference")
    args = parser.parse_args()
    print("=== gen_05_adverse_fsize.py ===")
    run(staging=args.staging)
    print("gen_05_adverse_fsize.py complete.")
