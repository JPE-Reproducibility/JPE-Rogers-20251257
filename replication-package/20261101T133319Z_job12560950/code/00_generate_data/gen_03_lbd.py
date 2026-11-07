"""
gen_03_lbd.py -- Generate learning-by-doing approval time panel

Produces LBD_ApprovalTime_Both_oct22_24.csv, a firm-level panel of cumulative
FDA approval experience used by downstream scripts (08_lbd_simulation,
09_summary_stats).

FROZEN ARTIFACT (regenerable with --regenerate-lbd; pinned by SHA-256 because the
firm clustering step uses `pandas_dedupe`, an active-learning entity-resolution
library that is not deterministic across environments): this script builds the
panel FROM the raw approval records; run_all freezes the deposited output so the
published numbers are stable and re-runs this generator only under
--regenerate-lbd. Freezing a non-deterministic step is the accepted way to keep it
reproducible (JPE Data Policy 2.2). See the REPRODUCIBILITY POLICY block in
run_all.py.

Pipeline:
    1. Load compiled 510(k)/PMA submissions and merge decision dates from
       raw FDA data.
    2. Clean text fields (applicant names, device names).
    3. Load pre-computed cluster IDs from pandas_dedupe entity resolution:
       - AD_data1: device-level clusters (170,929 rows)
       - AD_data2: applicant-level clusters (32,709 rows)
    4. Assign applicant-level cluster IDs via APPLICANT name matching
       and forward-fill.
    5. Compute per-device approval time (Days_take_approve) and cumulative
       experience within firm clusters (cumsum_time_t1).

The cluster ID CSVs were produced by Fuzzy_matching_lbd_vars.ipynb using
pandas_dedupe with pre-trained settings files included in the replication
package.

Reads:
    data/derived/Applicant_Device_data.csv                 (compiled 510k+PMA submissions)
    data/derived/AD_data_applicant_df_oct22_24.csv         (device-level clusters)
    data/derived/AD_data_applicant_df2_oct22_24.csv        (applicant-level clusters)
    data/raw/501k_all.csv                                  (FDA 510(k) submissions)
    data/raw/all_pma_approvals.txt                         (FDA PMA approvals)

Writes:
    data/derived/LBD_ApprovalTime_Both_oct22_24.csv

Source logic: Fuzzy_matching_lbd_vars.ipynb
"""

import sys
import string
import warnings
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

OUTPUT_FILE = DERIVED / "LBD_ApprovalTime_Both_oct22_24.csv"
EXPECTED_COLS = ['cluster id app', 'cluster id', 'PRODUCTCODE', 'year',
                 'Days_take_approve', 'cumsum_time_t1']


def _clean_text_field(series, remove_stopwords=False):
    """Clean a text column: lowercase, remove punctuation, normalize whitespace.

    Matches Fuzzy_matching_lbd_vars.ipynb text-cleaning cells.
    """
    s = series.str.lower()
    s = s.str.replace('[{}]'.format(string.punctuation), ' ', regex=True)
    s = s.str.strip()
    s = s.str.split()
    if remove_stopwords:
        from nltk.corpus import stopwords
        stop = stopwords.words('english')
        s = s.apply(lambda x: [item for item in x if item not in stop]
                    if isinstance(x, list) else x)
    s = s.str.join(" ")
    s = s.str.replace('/', ' ', regex=False)
    s = s.str.strip()
    s = s.str.split().str.join(" ")
    return s


def cumsum_df(row):
    """Compute cumulative approval time within firm cluster."""
    row['cumsum_time_t1'] = row.Days_take_approve.cumsum() - row.Days_take_approve
    row['head'] = 1
    row.loc[row['cluster id'].duplicated(), 'head'] = 0
    return row


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate(out_path):
    """Generate LBD panel from pre-computed cluster IDs and raw data.

    Assigns applicant-level cluster IDs ('cluster id app') by matching on
    APPLICANT name against the pre-computed applicant-level clusters in
    AD_data2, then forward-fills within sorted (APPLICANT, year) groups.
    """

    # ------------------------------------------------------------------
    # Phase 1: Load raw data and merge decision dates
    # ------------------------------------------------------------------
    print("  Phase 1: Loading data and merging decision dates...")
    Applicant_Device_data_df = pd.read_csv(DERIVED / "Applicant_Device_data.csv")
    n_raw = len(Applicant_Device_data_df)
    # Preserve original CSV row indices for DECISIONDATE lookup
    Applicant_Device_data_df['original_idx'] = np.arange(n_raw)

    k501s = pd.read_csv(RAW / "501k_all.csv", encoding='latin-1', low_memory=False)
    k501s['year'] = pd.DatetimeIndex(k501s['DATERECEIVED']).year

    pmas = pd.read_csv(RAW / "all_pma_approvals.txt",
                        encoding='latin-1', on_bad_lines='skip', sep="|")
    pmas['year'] = pd.DatetimeIndex(pmas['DATERECEIVED']).year
    pmas['DEVICENAME'] = pmas['TRADENAME']

    Applicant_Device_data_df = pd.merge(
        Applicant_Device_data_df,
        pmas[['PMANUMBER', 'DATERECEIVED', 'DECISIONDATE', 'DEVICENAME', 'PRODUCTCODE']],
        how='left', on=['PMANUMBER', 'DATERECEIVED', 'DEVICENAME', 'PRODUCTCODE'])
    Applicant_Device_data_df = pd.merge(
        Applicant_Device_data_df,
        k501s[['KNUMBER', 'DATERECEIVED', 'DECISIONDATE']],
        how='left', on=['KNUMBER', 'DATERECEIVED'])
    Applicant_Device_data_df = Applicant_Device_data_df.drop_duplicates(
        ['PMANUMBER', 'DATERECEIVED', 'DEVICENAME', 'PRODUCTCODE'])
    Applicant_Device_data_df = Applicant_Device_data_df.reset_index(drop=True)
    print(f"    Raw: {n_raw} rows, post-merge: {len(Applicant_Device_data_df)} rows")

    # ------------------------------------------------------------------
    # Phase 2: Text clean
    # ------------------------------------------------------------------
    print("  Phase 2: Text cleaning...")
    Applicant_Device_data_df['APPLICANT'] = _clean_text_field(
        Applicant_Device_data_df['APPLICANT'], remove_stopwords=True)
    Applicant_Device_data_df['DEVICENAME'] = _clean_text_field(
        Applicant_Device_data_df['DEVICENAME'], remove_stopwords=False)

    # ------------------------------------------------------------------
    # Phase 3: Load pre-saved cluster IDs
    # ------------------------------------------------------------------
    print("  Phase 3: Loading pre-computed cluster IDs...")
    AD_data1 = pd.read_csv(DERIVED / "AD_data_applicant_df_oct22_24.csv")
    if 'Unnamed: 0' in AD_data1.columns:
        AD_data1['orig_csv_idx'] = AD_data1['Unnamed: 0']
        AD_data1 = AD_data1.drop(columns=['Unnamed: 0'])
    print(f"    AD_data1: {len(AD_data1)} rows, "
          f"{AD_data1['cluster id'].nunique()} device clusters")

    # Merge DECISIONDATE into AD_data1 if not already present
    has_dec = ('DECISIONDATE_x' in AD_data1.columns or
               'DECISIONDATE_y' in AD_data1.columns)
    if has_dec:
        n_dec = AD_data1[['DECISIONDATE_x', 'DECISIONDATE_y']].notna().any(axis=1).sum()
        print(f"    DECISIONDATE already in AD_data1: {n_dec} / {len(AD_data1)} rows")
    elif 'orig_csv_idx' in AD_data1.columns:
        ad1_pre = len(AD_data1)
        dec_lookup = (Applicant_Device_data_df[['original_idx', 'DECISIONDATE_x', 'DECISIONDATE_y']]
                      .drop_duplicates('original_idx'))
        AD_data1 = pd.merge(AD_data1, dec_lookup,
                             left_on='orig_csv_idx', right_on='original_idx', how='left')
        AD_data1 = AD_data1.drop(columns=['original_idx'])
        assert len(AD_data1) == ad1_pre, \
            f"DECISIONDATE merge changed row count: {ad1_pre} -> {len(AD_data1)}"
        n_dec = AD_data1[['DECISIONDATE_x', 'DECISIONDATE_y']].notna().any(axis=1).sum()
        print(f"    DECISIONDATE merged via orig_csv_idx: {n_dec} / {len(AD_data1)} rows")
    else:
        print("    WARNING: No DECISIONDATE columns and no orig_csv_idx for merge")

    AD_data2 = pd.read_csv(DERIVED / "AD_data_applicant_df2_oct22_24.csv")
    AD_data2 = AD_data2.drop(columns=['Unnamed: 0'])
    print(f"    AD_data2: {len(AD_data2)} rows, "
          f"{AD_data2['cluster id'].nunique()} applicant clusters")

    # ------------------------------------------------------------------
    # Phase 4: Reconstruct panel with cluster IDs
    # ------------------------------------------------------------------
    print("  Phase 4: Reconstructing panel...")
    AD_data1 = AD_data1.sort_values(by=['cluster id', 'year'])
    AD_data1_dropped = AD_data1.copy()

    AD_data2.loc[AD_data2.confidence < .4, "cluster id"] = np.nan
    AD_data2['cluster id app'] = AD_data2['cluster id']

    # Concat AD_data1 rows + non-overlapping rows from Applicant_Device_data_df
    # Use orig_csv_idx for content-based matching (index-based is unreliable
    # after reset_index on both DataFrames).
    if 'orig_csv_idx' in AD_data1_dropped.columns:
        ad1_indices = set(AD_data1_dropped['orig_csv_idx'].dropna().astype(int))
        extra_rows = Applicant_Device_data_df[
            ~Applicant_Device_data_df['original_idx'].isin(ad1_indices)]
    else:
        extra_rows = Applicant_Device_data_df[
            ~Applicant_Device_data_df.index.isin(AD_data1_dropped.index)]
    new_df = pd.concat([AD_data1_dropped, extra_rows])
    print(f"    After concat: {len(new_df)} rows")

    # Assign applicant-level cluster IDs via APPLICANT name matching.
    ad2_lookup = (AD_data2[['APPLICANT', 'cluster id app']]
                  .dropna(subset=['cluster id app'])
                  .drop_duplicates('APPLICANT'))
    new_df = pd.merge(new_df, ad2_lookup, on='APPLICANT', how='left',
                       suffixes=('', '_from_ad2'))
    if 'cluster id app_from_ad2' in new_df.columns:
        mask = new_df['cluster id app'].isna() & new_df['cluster id app_from_ad2'].notna()
        new_df.loc[mask, 'cluster id app'] = new_df.loc[mask, 'cluster id app_from_ad2']
        new_df['cluster id app'] = new_df['cluster id app'].fillna(
            new_df['cluster id app_from_ad2'])
        new_df = new_df.drop(columns=['cluster id app_from_ad2'])
    n_mapped = new_df['cluster id app'].notna().sum()
    print(f"    cluster id app assigned: {n_mapped} / {len(new_df)} "
          f"({n_mapped/len(new_df)*100:.1f}%)")

    # Sort and forward-fill cluster IDs within groups (not globally,
    # which would leak one firm's cluster ID into the next firm's rows).
    new_df.year = new_df.year.astype(int)
    new_df = new_df.sort_values(by=["APPLICANT", "year"])
    new_df['cluster id app'] = new_df.groupby('APPLICANT')['cluster id app'].ffill()
    new_df.loc[new_df.APPLICANT == '', 'APPLICANT'] = np.nan
    new_df = new_df[(new_df.APPLICANT.notnull()) & (new_df.DEVICENAME.notnull())]
    new_df = new_df.sort_values(by=["APPLICANT", 'DEVICENAME', "year"])
    new_df['cluster id'] = new_df.groupby(['APPLICANT', 'DEVICENAME'])['cluster id'].ffill()
    print(f"    After filters: {len(new_df)} rows, "
          f"{new_df['cluster id app'].nunique()} applicant clusters")

    # ------------------------------------------------------------------
    # Phase 5: Compute approval times and cumulative sums
    # ------------------------------------------------------------------
    print("  Phase 5: Computing approval times and cumulative experience...")
    onlyPMAfirms = new_df.sort_values(by=['cluster id app', 'year'])

    onlyPMAfirms['Rec_Date_dt'] = pd.DatetimeIndex(onlyPMAfirms['DATERECEIVED'])
    onlyPMAfirms['Dec_Date_dt_510k'] = pd.DatetimeIndex(onlyPMAfirms['DECISIONDATE_y'])
    onlyPMAfirms['Dec_Date_dt_pma'] = pd.DatetimeIndex(onlyPMAfirms['DECISIONDATE_x'])

    onlyPMAfirms['Days_take_approve_pma'] = (
        onlyPMAfirms['Dec_Date_dt_pma'] - onlyPMAfirms['Rec_Date_dt']).dt.days
    onlyPMAfirms['Days_take_approve_510k'] = (
        onlyPMAfirms['Dec_Date_dt_510k'] - onlyPMAfirms['Rec_Date_dt']).dt.days

    onlyPMAfirms['Days_take_approve'] = 0
    onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_pma.isnull(), 'Days_take_approve'] = \
        onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_pma.isnull(), 'Days_take_approve_510k']
    onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_510k.isnull(), 'Days_take_approve'] = \
        onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_510k.isnull(), 'Days_take_approve_pma']

    onlyPMAfirms_andpmas = onlyPMAfirms.copy()
    onlyPMAfirms_andpmas['DATERECEIVED'] = pd.to_datetime(onlyPMAfirms_andpmas['DATERECEIVED'])
    onlyPMAfirms_andpmas = onlyPMAfirms_andpmas.sort_values(by=['cluster id', 'DATERECEIVED'])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        onlyPMAfirms_cumsum = onlyPMAfirms_andpmas.groupby(
            'cluster id app', group_keys=False).apply(cumsum_df)
    onlyPMAfirms_cumsum = onlyPMAfirms_cumsum.reset_index(drop=True)

    onlyPMAfirms_cumsum.loc[onlyPMAfirms_cumsum['cumsum_time_t1'] == 0, 'cumsum_time_t1'] = 1
    onlyPMAfirms_cumsum = onlyPMAfirms_cumsum[onlyPMAfirms_cumsum.PRODUCTCODE.notnull()]
    onlyPMAfirms_cumsum.PRODUCTCODE = onlyPMAfirms_cumsum.PRODUCTCODE.str.lower()

    # Output: head observations with known submission IDs
    output = onlyPMAfirms_cumsum[
        (onlyPMAfirms_cumsum['head'] == 1) &
        ((onlyPMAfirms_cumsum.KNUMBER.notnull()) |
         (onlyPMAfirms_cumsum.PMANUMBER.notnull()))
    ][EXPECTED_COLS].copy()

    output.to_csv(out_path, index=False)

    # Summary
    prof = (output['cumsum_time_t1'].dropna() / 365).mean()
    print(f"\n  Output: {out_path.name}")
    print(f"    Rows:              {len(output):,}")
    print(f"    Unique cluster id app: {output['cluster id app'].nunique():,}")
    print(f"    Unique cluster id:     {output['cluster id'].nunique():,}")
    print(f"    Year range:        {output['year'].min()}-{output['year'].max()}")
    print(f"    Proficiency (yrs): {prof:.2f}")
    print(f"    Days_take_approve: mean={output['Days_take_approve'].mean():.1f}, "
          f"median={output['Days_take_approve'].median():.1f}")

    return output


def run(staging=False):
    if staging:
        out_dir = DERIVED / "_generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "LBD_ApprovalTime_Both_oct22_24.csv"
        print(f"STAGING MODE: writing to {out_dir}")
    else:
        out_path = OUTPUT_FILE
    generate(out_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting main file")
    args = parser.parse_args()
    print("=== gen_03_lbd.py ===")
    run(staging=args.staging)
    print("gen_03_lbd.py complete.")
