"""
gen_04_parquets.py — Build pre-computed parquet files for 2→1 estimation

Loads the 2→1 CSV panels, adds derived columns, then performs FE stacking
(duplicating the control group for each treated product code) and saves
the stacked panels as parquet files.

Reads:
    data/derived/Full_sample.csv
    data/derived/later_treated_2_1_oct22_24.csv
    data/derived/intuitive_2_1_oct22_24.csv
    data/derived/spillovers_2_1_oct22_24.csv

Writes:
    data/derived/data_2_1_full.parquet
    data/derived/data_2_1_latertreat.parquet
    data/derived/data_2_1_intuitive.parquet
    data/derived/data_2_1_spillovers.parquet

Source logic: Replication_analysis.py lines 426-895
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths — resolve relative to replication_package root
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent          # replication_package/
sys.path.insert(0, str(ROOT_DIR))
import config

DERIVED = config.DERIVED_DATA_DIR


def _check_no_symlinks(paths):
    """Abort if any output path is a symlink (prevents overwriting originals)."""
    bad = [str(p) for p in paths if p.is_symlink()]
    if bad:
        raise RuntimeError(
            "SAFETY CHECK FAILED: Output paths are symlinks. "
            "Replace them with copies before running.\n  " +
            "\n  ".join(bad))


def _stack_FE(df):
    """Duplicate control rows for each treated PC, assigning FE index.

    For each treated product code (enumerated via np.unique), all control
    rows are duplicated with FE = i. The first treated PC (i=0) reuses the
    original control rows (FE=0). This matches the original code at
    Replication_analysis.py lines 768-820.
    """
    df = df.copy()
    treated_PCs = np.unique(df.loc[df.treatment == 1, 'PRODUCTCODE'])
    fe_map = {pc: i for i, pc in enumerate(treated_PCs)}

    df['FE'] = df['PRODUCTCODE'].map(fe_map)
    df.loc[df.treatment == 0, 'FE'] = 0

    if len(treated_PCs) <= 1:
        return df

    controls = df.loc[df.treatment == 0].copy()
    control_blocks = []
    for i in range(1, len(treated_PCs)):
        block = controls.copy()
        block['FE'] = i
        control_blocks.append(block)

    return pd.concat([df] + control_blocks, axis=0)


def run(staging=False):
    if staging:
        OUT = DERIVED / "_generated"
        OUT.mkdir(parents=True, exist_ok=True)
        print(f"STAGING MODE: writing to {OUT}")
    else:
        OUT = DERIVED

    # Safety: abort if any output path is a symlink
    _check_no_symlinks([
        OUT / config.PARQUET_FILES["data_2_1_full"],
        OUT / config.PARQUET_FILES["data_2_1_latertreat"],
        OUT / config.PARQUET_FILES["data_2_1_intuitive"],
        OUT / config.PARQUET_FILES["data_2_1_spillovers"],
    ])

    # ------------------------------------------------------------------
    # Step 1: Load source CSVs (produced by gen_01_main_panels.py)
    # ------------------------------------------------------------------
    print("  Loading source CSVs...")

    df_2_1_spillovers = pd.read_csv(
        DERIVED / config.SOURCE_FILES["spillovers_2_1"])

    df_2_1_later_treated = pd.read_csv(
        DERIVED / config.SOURCE_FILES["later_treated_2_1"])

    df_2_1_intuitive = pd.read_csv(
        DERIVED / config.SOURCE_FILES["intuitive_2_1"])

    # Full sample: filter to treated + controls with patents
    df_2_1 = pd.read_csv(DERIVED / config.FULL_SAMPLE)
    if 'index' not in df_2_1.columns:
        df_2_1['index'] = df_2_1.index
    df_2_1['year_reclassified'] = df_2_1['year_reclassified_2_1']
    df_2_1['treatment'] = 0
    df_2_1.loc[df_2_1.year_reclassified.notnull(), 'treatment'] = 1
    df_2_1 = df_2_1[(df_2_1.treatment == 1) | (df_2_1.controls == 1)]
    df_2_1 = df_2_1[df_2_1.total_pat_sum > 0].reset_index(drop=True)
    df_2_1 = df_2_1[(df_2_1.controls == 1) | (df_2_1.patent_sum_2_1 > 0)]

    # ------------------------------------------------------------------
    # Step 2: Filter out year == 0 rows
    # ------------------------------------------------------------------
    df_2_1 = df_2_1[df_2_1.year != 0]
    df_2_1_spillovers = df_2_1_spillovers[df_2_1_spillovers.year != 0]
    df_2_1_intuitive = df_2_1_intuitive[df_2_1_intuitive.year != 0]

    # ------------------------------------------------------------------
    # Step 3: Create derived columns
    # ------------------------------------------------------------------
    print("  Creating derived columns...")
    for df in [df_2_1, df_2_1_intuitive, df_2_1_later_treated]:
        df['real_pats'] = df['patents_allpats']
        df['unique_firms'] = df['patents_newfirm']
        df['unique_firmsPC'] = df['patents_newfirmPC']

    df_2_1_spillovers['real_pats'] = df_2_1_spillovers['patents_allpats']

    # Fill NAs for times_cited, xi_real; compute xi_real_2019
    for df in [df_2_1, df_2_1_intuitive, df_2_1_later_treated]:
        df['times_cited'] = df['times_cited'].fillna(0)
        df['xi_real'] = df['xi_real'].fillna(0)
        df['xi_real_2019'] = df['xi_real'] / config.CPI_DEFLATOR_2019

    df_2_1_spillovers['times_cited'] = df_2_1_spillovers['times_cited'].fillna(0)

    # Compute firm_expansion_patents
    for df in [df_2_1, df_2_1_intuitive, df_2_1_later_treated]:
        df['firm_expansion_patents'] = df['unique_firmsPC'] - df['unique_firms']

    # ------------------------------------------------------------------
    # Step 4: FE stacking — duplicate controls for each treated PC
    # ------------------------------------------------------------------
    print("  FE stacking df_2_1_full...")
    df_2_1 = _stack_FE(df_2_1)
    print(f"    {len(df_2_1)} rows")

    print("  FE stacking df_2_1_later_treated...")
    df_2_1_later_treated = _stack_FE(df_2_1_later_treated)
    print(f"    {len(df_2_1_later_treated)} rows")

    print("  FE stacking df_2_1_intuitive...")
    df_2_1_intuitive = _stack_FE(df_2_1_intuitive)
    print(f"    {len(df_2_1_intuitive)} rows")

    print("  FE stacking df_2_1_spillovers...")
    df_2_1_spillovers = _stack_FE(df_2_1_spillovers)
    print(f"    {len(df_2_1_spillovers)} rows")

    # ------------------------------------------------------------------
    # Step 5: Column selection (matches commented-out code lines 827-885)
    # ------------------------------------------------------------------
    # Common outcome + patent columns shared by all parquets
    _outcome_cols = [
        'L_U', 'L_D', 'L_P', 'L_M', 'H_U', 'H_D', 'H_P', 'H_M',
        'S_U', 'S_D', 'S_P', 'S_M', 'C_U', 'C_D', 'C_P', 'C_M',
        'R_U', 'R_D', 'R_P', 'R_M', 'O_U', 'O_D', 'O_P', 'O_M',
        'U_U', 'U_D', 'U_P', 'U_M', 'I_U', 'I_D', 'I_P', 'I_M',
        'A_U', 'A_D', 'A_P', 'A_M', 'D_U', 'D_D', 'D_P', 'D_M',
        'D', 'H', 'L', 'S', 'R',
    ]

    # Per-parquet column lists (from commented-out code lines 827-885)
    cols_full = (['PRODUCTCODE', 'year', 'patents_allpats', 'patents_newfirm',
                  'patents_pats_nodrugs', 'times_cited', 'times_cited_outside_ind',
                  'xi_real', 'firm_size'] + _outcome_cols +
                 ['index', 'year_reclassified_2_1', 'year_reclassified', 'treatment',
                  'real_pats', 'unique_firms', 'unique_firmsPC',
                  'firm_expansion_patents', 'xi_real_2019', 'FE'])

    cols_intuitive = (['PRODUCTCODE', 'year', 'patents_allpats', 'patents_newfirm',
                       'patents_pats_nodrugs', 'times_cited', 'times_cited_outside_ind',
                       'xi_real', 'firm_size'] + _outcome_cols +
                      ['year_reclassified_2_1', 'year_reclassified', 'treatment',
                       'real_pats', 'unique_firms', 'unique_firmsPC',
                       'firm_expansion_patents', 'xi_real_2019', 'FE'])

    cols_spillovers = (['PRODUCTCODE', 'year', 'patents_allpats', 'patents_newfirm',
                        'patents_pats_nodrugs', 'times_cited', 'times_cited_outside_ind',
                        'xi_real', 'firm_size'] + _outcome_cols +
                       ['year_reclassified_2_1', 'year_reclassified', 'treatment',
                        'real_pats', 'FE', 'factorized', 'posttreat'])

    cols_latertreat = (['PRODUCTCODE', 'year', 'patents_allpats', 'patents_newfirm',
                        'patents_pats_nodrugs', 'times_cited', 'times_cited_outside_ind',
                        'xi_real', 'firm_size'] + _outcome_cols +
                       ['year_reclassified_2_1', 'treatment', 'real_pats',
                        'unique_firms', 'unique_firmsPC',
                        'firm_expansion_patents', 'xi_real_2019', 'FE'])

    # Select only columns that exist in each DataFrame
    df_2_1 = df_2_1[[c for c in cols_full if c in df_2_1.columns]]
    df_2_1_intuitive = df_2_1_intuitive[[c for c in cols_intuitive if c in df_2_1_intuitive.columns]]
    df_2_1_spillovers = df_2_1_spillovers[[c for c in cols_spillovers if c in df_2_1_spillovers.columns]]
    df_2_1_later_treated = df_2_1_later_treated[[c for c in cols_latertreat if c in df_2_1_later_treated.columns]]

    # ------------------------------------------------------------------
    # Step 6: Save as parquet with snappy compression
    # ------------------------------------------------------------------
    output_files = {
        "data_2_1_full": df_2_1,
        "data_2_1_latertreat": df_2_1_later_treated,
        "data_2_1_intuitive": df_2_1_intuitive,
        "data_2_1_spillovers": df_2_1_spillovers,
    }

    for name, df in output_files.items():
        out_path = OUT / config.PARQUET_FILES[name]
        df.to_parquet(out_path, compression='snappy')
        print(f"  Wrote {out_path.name}: {len(df)} rows, {len(df.columns)} cols")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting reference")
    args = parser.parse_args()
    print("=== gen_04_parquets.py ===")
    run(staging=args.staging)
    print("gen_04_parquets.py complete.")
