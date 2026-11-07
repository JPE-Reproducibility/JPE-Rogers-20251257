# -*- coding: utf-8 -*-
"""
gen_01_main_panels.py -- Master data generation script

Adapted from Replication_Gather_and_Compile_Data.py (~2700 lines). Produces 13
derived datasets from raw inputs; patent data is provided as pre-scraped CSVs, so
no Dimensions API calls are made.

Produces:
    data/derived/Full_sample.csv
    data/derived/all_patents_w_xi_oct22_24.csv
    data/derived/safety_vars_allpats.csv
    data/derived/intuitive_2_1_oct22_24.csv
    data/derived/later_treated_2_1_oct22_24.csv
    data/derived/intuitive_3_2_oct22_24_similarity.csv
    data/derived/later_treated_3_2_oct22_24.csv
    data/derived/intuitive_spillovers_3_2_oct22_24.csv
    data/derived/spillovers_2_1_oct22_24.csv
    data/derived/adverse_event_panel_by_PC_full.csv
    data/raw/unique_devices_thr_75.csv
    data/raw/unique_firms_in_PC_thr_75.csv
    data/raw/unique_firms_thr_75.csv

Source: my_paper/analysis/code/Replication_Gather_and_Compile_Data.py
"""

import argparse
import gc
import os
import re
import string
import sys
import warnings
from ast import literal_eval
from os import listdir
from os.path import isfile, join
from pathlib import Path

import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from rapidfuzz import fuzz
from joblib import Parallel, delayed

try:
    from flashtext import KeywordProcessor
except ImportError:
    KeywordProcessor = None

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR))
import config

warnings.filterwarnings("ignore", category=FutureWarning)

RAW = config.RAW_DATA_DIR
DERIVED = config.DERIVED_DATA_DIR

# Staging output directories (set by --staging flag)
OUT_RAW = RAW
OUT_DERIVED = DERIVED


def _check_no_symlinks(paths):
    """Abort if any output path is a symlink (prevents overwriting originals)."""
    bad = [str(p) for p in paths if p.is_symlink()]
    if bad:
        raise RuntimeError(
            "SAFETY CHECK FAILED: Output paths are symlinks. "
            "Replace them with copies before running.\n  " +
            "\n  ".join(bad))


# ============================================================================
# Utility functions
# ============================================================================

def deduplicate_fuzzy_parallel(df, key_column, group_column=None,
                               threshold=90, n_jobs=-1):
    """Fuzzy-deduplicate entries using rapidfuzz token_sort_ratio."""
    if group_column:
        grouped = df.groupby(group_column)
    else:
        grouped = [('global', df)]

    def process_group(name, group):
        seen = []
        deduped = []
        for _, row in group.iterrows():
            key = row[key_column]
            if not any(fuzz.token_sort_ratio(key, s) >= threshold for s in seen):
                deduped.append(row)
                seen.append(key)
        return deduped

    results = Parallel(n_jobs=n_jobs)(
        delayed(process_group)(name, group) for name, group in grouped
    )
    deduped_rows = [row for sublist in results for row in sublist]
    return pd.DataFrame(deduped_rows)


def get_similar(pos_pscore, neg_pscore, topn=1):
    """Euclidean distance matching — returns (distances, best_index)."""
    diff = pos_pscore - neg_pscore
    diff = diff * diff
    return diff, np.argmin(diff)


def _extract_grid_id(assignees_str):
    """Extract first GRID ID from original_assignees JSON string (scalar)."""
    try:
        parsed = literal_eval(assignees_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed[0].get('id', np.nan)
    except Exception:
        pass
    return np.nan


def _extract_assignee_name(assignee_names_str):
    """Extract first assignee name from original_assignee_names string (scalar)."""
    try:
        name = str(assignee_names_str).replace("'", "").strip('[]').split(',')[0]
        return name.strip()
    except Exception:
        return np.nan


def remove_punctuation(text):
    """Strip all punctuation from text."""
    return text.translate(str.maketrans('', '', string.punctuation))


def clean_text(text):
    """Clean patent text for keyword extraction."""
    if pd.isnull(text) or not text:
        return ''
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def unstack_stack_panel(df, index_cols=None):
    """Create complete (PRODUCTCODE, year) panel via unstack/stack."""
    if index_cols is None:
        index_cols = ['PRODUCTCODE', 'year']
    return (df.set_index(index_cols)
              .unstack(fill_value=0)
              .stack()
              .sort_index(level=1)
              .reset_index())


# Product code remapping (same REGULATIONNUMBER, merged into one PC)
PC_REMAPS = {
    'NAJ': 'KRD', 'MAB': 'MAL', 'MUW': 'HQD',
    'MVN': 'LPL', 'MZD': 'LPL', 'NCZ': 'LPL',
}


# ============================================================================
# PHASE 1: Load synth_number (no API scraping)
# ============================================================================
def phase_01_load_synth():
    """Load the master product-code regulatory data."""
    print("  Phase 1: Loading synth_number...")
    synth_number = pd.read_csv(
        DERIVED / config.SOURCE_FILES["synth_number"],
        dtype={'REGULATIONNUMBER': str})
    synth_number.REGULATIONNUMBER = synth_number.REGULATIONNUMBER.str.pad(
        width=8, side='right', fillchar="0")
    synth_number = synth_number.drop_duplicates('PRODUCTCODE_x')
    synth_number['PRODUCTCODE'] = synth_number['PRODUCTCODE_x']
    synth_number = synth_number[[
        'FDA_own_accord', 'PRODUCTCODE', 'Reg_Change_List', 'use_case',
        'REGULATIONNUMBER', 'DEVICECLASS', 'SUBMISSION_TYPE_ID', 'DEVICENAME',
        'DESCRIPTION_OF_REGNUM', 'SUBPART_DESCRIPTION']]
    print(f"    {len(synth_number)} rows, "
          f"{len(set(synth_number.PRODUCTCODE))} unique PCs")
    return synth_number


# ============================================================================
# PHASE 2a: Compile the 510(k) + PMA submission table
# ============================================================================
# Columns and their order in data/derived/Applicant_Device_data.csv, exactly as the deposited
# file carries them (alphabetical, a subset of the two raw sources' columns).
APPLICANT_DEVICE_COLS = ["APPLICANT", "DATERECEIVED", "DEVICENAME", "KNUMBER",
                         "PMANUMBER", "PRODUCTCODE", "year"]
# The deposited file is ordered by (PRODUCTCODE, APPLICANT, DEVICENAME, year) with a stable sort.
APPLICANT_DEVICE_SORT = ["PRODUCTCODE", "APPLICANT", "DEVICENAME", "year"]


def phase_02a_applicant_device_data():
    """Write data/derived/Applicant_Device_data.csv: every 510(k) submission plus every PMA
    approval, as raw text, keyed to a product code.

    `gen_03_lbd.py` and `gen_03b_lbd_clusters.py` read this file, and JPE policy 2.1 requires
    the program that builds each analysis dataset to ship. The content is derived entirely from
    the two PUBLIC FDA registries.

    Two details differ from the `concatenated` frame that phase 2 builds below, and both are
    deliberate -- they are what the deposited file actually contains, and changing either would
    change gen_03's learning-by-doing panel:
      * PMA rows are NOT filtered to original approvals + Panel Track supplements. This file
        carries all 41,645 PMA records; phase 2's own fuzzy-dedup frame applies that filter.
      * APPLICANT / DEVICENAME are the raw registry strings. The text cleaning (lowercasing,
        punctuation and stop-word removal) that phase 2 applies to its own frame is applied by
        the READER instead (`gen_03_lbd._clean_text_field`), so it must not be applied here.
    """
    print("  Phase 2a: Compiling Applicant_Device_data.csv (510(k) + PMA submissions)...")
    out_path = OUT_DERIVED / "Applicant_Device_data.csv"
    _check_no_symlinks([out_path])

    k501s = pd.read_csv(RAW / config.GEN_RAW_FILES["501k_all"], encoding='latin-1',
                        low_memory=False)
    k501s['year'] = pd.DatetimeIndex(k501s['DATERECEIVED']).year

    pmas = pd.read_csv(RAW / config.GEN_RAW_FILES["all_pma_approvals"], encoding='latin-1',
                       on_bad_lines='skip', sep="|", low_memory=False)
    pmas['year'] = pd.DatetimeIndex(pmas['DATERECEIVED']).year
    pmas['DEVICENAME'] = pmas['TRADENAME']

    combined = pd.concat(
        [k501s.reindex(columns=APPLICANT_DEVICE_COLS),
         pmas.reindex(columns=APPLICANT_DEVICE_COLS)],
        ignore_index=True,
    )
    combined = (combined.sort_values(APPLICANT_DEVICE_SORT, kind='stable')
                        .reset_index(drop=True))
    combined.to_csv(out_path, index=False)
    print(f"    {len(combined):,} rows "
          f"({int(k501s.shape[0]):,} 510(k) + {int(pmas.shape[0]):,} PMA) -> {out_path}")


# ============================================================================
# PHASE 2: Fuzzy deduplication of firms/devices
# ============================================================================
def phase_02_fuzzy_dedup():
    """Fuzzy-deduplicate 510(k) and PMA submissions."""
    print("  Phase 2: Fuzzy deduplication of firms/devices...")
    synthetic_mode = os.environ.get("FDA_SYNTHETIC_MODE") == "1"

    # Skip if output files already exist (fuzzy dedup is very slow)
    out1 = OUT_RAW / "unique_firms_thr_75.csv"
    out2 = OUT_RAW / "unique_firms_in_PC_thr_75.csv"
    out3 = OUT_RAW / "unique_devices_thr_75.csv"
    if out1.exists() and out2.exists() and out3.exists():
        if synthetic_mode:
            raise RuntimeError(
                "Synthetic from-raw route found pre-existing fuzzy-dedup outputs; "
                "refusing to bypass phase 2. Materialize with --for-gen-run first."
            )
        # All three of these files SHIP in data/raw (see RESTRICTED_FILE_INVENTORY.csv, disposition
        # "ships"), and in a non-staging run OUT_RAW IS data/raw, so on a from-raw real run this
        # branch is always reached; synthetic_pipeline/fromraw_contract.py lists these same three
        # paths as step-1 TRANSFORMATION OUTPUTS that a from-raw run is supposed to produce. The
        # dedup is a greedy first-wins pass over a single-key, non-stable sort_values('DATERECEIVED')
        # with many date ties, and on the real-data path it runs multi-process (dedup_jobs = -1
        # below), so its result can depend on row order and on process scheduling, and a
        # regeneration may not reproduce the shipped copies byte for byte. Reusing the shipped copies is therefore a
        # deliberate, recorded choice (FDA_REUSE_FROZEN_DEDUP=1) rather than a default.
        if os.environ.get("FDA_REUSE_FROZEN_DEDUP") == "1":
            print("    FDA_REUSE_FROZEN_DEDUP=1: reusing the three SHIPPED fuzzy-dedup artifacts in "
                  f"{OUT_RAW} instead of regenerating them. This run is NOT from raw for "
                  "unique_firms_thr_75 / unique_firms_in_PC_thr_75 / unique_devices_thr_75; the "
                  "firm- and device-count outcomes derive from the deposited artifacts.")
            return
        raise RuntimeError(
            "phase 2 (fuzzy dedup) found all three of its outputs already present in "
            f"{OUT_RAW}:\n"
            f"  {out1.name}\n  {out2.name}\n  {out3.name}\n"
            "These files SHIP in data/raw, and fromraw_contract.py classifies them as step-1 "
            "transformation outputs, i.e. things a from-raw run must produce, so they are not reused "
            "by default. Either delete them to regenerate (hours; the pass is greedy and first-wins "
            "over a sort with many date ties and runs multi-process on this path, so its result can "
            "depend on row order and process scheduling and may not "
            "reproduce the shipped copies byte for byte), or set FDA_REUSE_FROZEN_DEDUP=1 to reuse "
            "them deliberately, which this run will then say in its log."
        )

    # In staging mode, copy from RAW if available (avoids hours-long re-dedup)
    src1 = RAW / "unique_firms_thr_75.csv"
    src2 = RAW / "unique_firms_in_PC_thr_75.csv"
    src3 = RAW / "unique_devices_thr_75.csv"
    if (not synthetic_mode and OUT_RAW != RAW
            and src1.exists() and src2.exists() and src3.exists()):
        import shutil
        for src, dst in [(src1, out1), (src2, out2), (src3, out3)]:
            shutil.copy2(str(src), str(dst))
        print("    Copied 3 dedup files from reference dir (staging mode). "
              "Delete _generated/ copies to force re-dedup.")
        return

    # Load 510(k) data
    k501s = pd.read_csv(RAW / config.GEN_RAW_FILES["501k_all"],
                         encoding='latin-1')
    k501s['year'] = pd.DatetimeIndex(k501s['DATERECEIVED']).year
    k501s = k501s[['KNUMBER', 'PRODUCTCODE', 'APPLICANT', 'DEVICENAME',
                    'COUNTRY_CODE', 'year', 'DATERECEIVED', 'DECISIONDATE']]

    # Load PMA data
    pmas = pd.read_csv(RAW / config.GEN_RAW_FILES["all_pma_approvals"],
                        encoding='latin-1', on_bad_lines='skip', sep="|")
    pmas['year'] = pd.DatetimeIndex(pmas['DATERECEIVED']).year
    pmas['COUNTRY_CODE'] = 'Not US'
    pmas.loc[pmas.STATE.notnull(), 'COUNTRY_CODE'] = 'US'
    pmas = pmas[(pmas.SUPPLEMENTTYPE == "Panel Track") |
                (pmas.SUPPLEMENTREASON.isnull()) |
                (pmas.SUPPLEMENTREASON ==
                 'Change Design/Components/Specifications/Material')]
    pmas = pmas[['PMANUMBER', 'PRODUCTCODE', 'APPLICANT', 'TRADENAME',
                  'COUNTRY_CODE', 'year', 'DATERECEIVED', 'DECISIONDATE']]
    pmas['DEVICENAME'] = pmas['TRADENAME']

    concatenated = pd.concat([k501s, pmas])

    # Clean text
    stop = stopwords.words('english')
    for col in ['APPLICANT', 'DEVICENAME']:
        concatenated[col] = concatenated[col].astype(str)
        concatenated[col] = concatenated[col].str.lower()
        concatenated[col] = concatenated[col].str.replace('/', ' ', regex=False)
        concatenated[col] = concatenated[col].str.replace(r'\d+', ' ', regex=True)
        concatenated[col] = concatenated[col].str.replace(
            '[{}]'.format(re.escape(string.punctuation)), ' ', regex=True)
        concatenated[col] = concatenated[col].str.strip()
        concatenated[col] = concatenated[col].str.split()
        concatenated[col] = concatenated[col].apply(
            lambda x: [item for item in x if item not in stop])
        concatenated[col] = concatenated[col].str.join(" ")

    # Product code remapping
    for old, new in PC_REMAPS.items():
        concatenated.loc[concatenated.PRODUCTCODE == old, 'PRODUCTCODE'] = new

    # Sort by date and clean punctuation
    Applicant_Device_data_df = concatenated.copy()
    Applicant_Device_data_df['DATERECEIVED'] = pd.to_datetime(
        Applicant_Device_data_df['DATERECEIVED'], errors='coerce')
    Applicant_Device_data_df_sorted = Applicant_Device_data_df.sort_values(
        by='DATERECEIVED').reset_index(drop=True)

    Applicant_Device_data_df_sorted['APPLICANT'] = \
        Applicant_Device_data_df_sorted['APPLICANT'].apply(remove_punctuation)
    Applicant_Device_data_df_sorted['DEVICENAME'] = \
        Applicant_Device_data_df_sorted['DEVICENAME'].apply(remove_punctuation)
    Applicant_Device_data_df_sorted['APPLICANT'] = \
        Applicant_Device_data_df_sorted['APPLICANT'].fillna('')
    Applicant_Device_data_df_sorted['DEVICENAME'] = \
        Applicant_Device_data_df_sorted['DEVICENAME'].fillna('')

    # Single-process execution fixes group ordering for the certification route.
    # The default real-data path retains the historical parallel setting.
    dedup_jobs = 1 if synthetic_mode else -1

    # 3 fuzzy dedup passes
    print("    Dedup 1/3: global APPLICANT...")
    unique_applicant_df = deduplicate_fuzzy_parallel(
        df=Applicant_Device_data_df_sorted,
        key_column='APPLICANT', group_column=None,
        threshold=75, n_jobs=dedup_jobs).reset_index(drop=True)

    print("    Dedup 2/3: within-PC APPLICANT...")
    unique_applicant_product_df = deduplicate_fuzzy_parallel(
        df=Applicant_Device_data_df_sorted,
        key_column='APPLICANT', group_column='PRODUCTCODE',
        threshold=75, n_jobs=dedup_jobs).reset_index(drop=True)

    print("    Dedup 3/3: within-PC DEVICENAME...")
    unique_devicename_product_df = deduplicate_fuzzy_parallel(
        df=Applicant_Device_data_df_sorted,
        key_column='DEVICENAME', group_column='PRODUCTCODE',
        threshold=75, n_jobs=dedup_jobs).reset_index(drop=True)

    # Write outputs
    unique_applicant_df.to_csv(OUT_RAW / "unique_firms_thr_75.csv", index=False)
    unique_applicant_product_df.to_csv(
        OUT_RAW / "unique_firms_in_PC_thr_75.csv", index=False)
    unique_devicename_product_df.to_csv(
        OUT_RAW / "unique_devices_thr_75.csv", index=False)

    print(f"    Wrote 3 dedup files: "
          f"{len(unique_applicant_df)} firms, "
          f"{len(unique_applicant_product_df)} firm-PCs, "
          f"{len(unique_devicename_product_df)} device-PCs")


# ============================================================================
# PHASE 3: Build main_outcomes skeleton
# ============================================================================
def phase_03_main_outcomes_skeleton(synth_number):
    """Build the (PRODUCTCODE, year) panel from device/firm counts."""
    print("  Phase 3: Building main_outcomes skeleton...")

    # Read from OUT_RAW (staging) if available, else fall back to RAW
    _raw_src = OUT_RAW if (OUT_RAW / "unique_devices_thr_75.csv").exists() else RAW
    unique_dev = pd.read_csv(_raw_src / "unique_devices_thr_75.csv")
    firm_entrant = pd.read_csv(_raw_src / "unique_firms_in_PC_thr_75.csv")
    total_firm_entrant = pd.read_csv(_raw_src / "unique_firms_thr_75.csv")

    unique_dev['dev_count'] = 1
    firm_entrant['firm_count'] = 1
    total_firm_entrant['absnew_firm_count'] = 1

    unique_dev = unique_dev[['PRODUCTCODE', 'year', 'dev_count']]
    firm_entrant = firm_entrant[['PRODUCTCODE', 'year', 'firm_count']]
    total_firm_entrant = total_firm_entrant[
        ['PRODUCTCODE', 'year', 'absnew_firm_count']]

    unique_dev = unique_dev.groupby(['PRODUCTCODE', 'year']).sum().reset_index()
    firm_entrant = firm_entrant.groupby(
        ['PRODUCTCODE', 'year']).sum().reset_index()
    total_firm_entrant = total_firm_entrant.groupby(
        ['PRODUCTCODE', 'year']).sum().reset_index()

    unique_dev = unstack_stack_panel(unique_dev)
    firm_entrant = unstack_stack_panel(firm_entrant)
    total_firm_entrant = unstack_stack_panel(total_firm_entrant)

    unique_dev = unique_dev[unique_dev.year > 1975]
    firm_entrant = firm_entrant[firm_entrant.year > 1975]
    total_firm_entrant = total_firm_entrant[total_firm_entrant.year > 1975]

    main_outcomes = pd.merge(synth_number, unique_dev,
                             on='PRODUCTCODE', how='left')
    main_outcomes = pd.merge(main_outcomes, firm_entrant,
                             on=['PRODUCTCODE', 'year'], how='left')
    main_outcomes = pd.merge(main_outcomes, total_firm_entrant,
                             on=['PRODUCTCODE', 'year'], how='left')

    main_outcomes['dev_count'] = main_outcomes['dev_count'].fillna(0)
    main_outcomes['firm_count'] = main_outcomes['firm_count'].fillna(0)
    main_outcomes['absnew_firm_count'] = main_outcomes[
        'absnew_firm_count'].fillna(0)

    print(f"    main_outcomes: {main_outcomes.shape}")
    return main_outcomes


# ============================================================================
# PHASE 4: Patent processing + GRID firm IDs
# ============================================================================
def phase_04_patents(main_outcomes):
    """Process patent data: concatenate sources, extract firm IDs, aggregate."""
    print("  Phase 4: Patent processing...")

    np.random.seed(42)

    # Load firm names
    firm_names = pd.read_csv(RAW / config.GEN_RAW_FILES["fda_patents_text"].replace(
        "FDA_patents_text.csv", "FDA_pats_original_firmname.csv"))

    # Load 4 patent sources
    expanded_pats = pd.read_csv(RAW / "expanded_3_2_pats.csv")
    expanded_pats = expanded_pats[expanded_pats.filing_status == "Grant"]

    missed_pats = pd.read_csv(RAW / "missed_2_1_pats.csv")
    missed_pats = missed_pats[missed_pats.filing_status == "Grant"]

    honed_pats = pd.read_csv(RAW / "expanded_2_1_pats.csv")
    honed_pats = honed_pats[honed_pats.filing_status == "Grant"]

    all_pats = pd.read_csv(RAW / "all_PC_pats.csv")
    all_pats = all_pats[all_pats.filing_status == "Grant"]
    # Remove PCs and IDs that appear in augmented sources
    all_pats = all_pats[~((all_pats.PRODUCTCODE.isin(missed_pats.PRODUCTCODE)) |
                          (all_pats.PRODUCTCODE.isin(honed_pats.PRODUCTCODE)) |
                          (all_pats.PRODUCTCODE.isin(expanded_pats.PRODUCTCODE)))]
    all_pats = all_pats[~((all_pats.id.isin(honed_pats.id)) |
                          (all_pats.id.isin(missed_pats.id)) |
                          (all_pats.id.isin(expanded_pats.id)))]

    # Concatenate, randomize, dedup
    all_pats = pd.concat([all_pats, missed_pats, honed_pats, expanded_pats])
    idx = np.random.permutation(np.arange(len(all_pats)))
    all_pats = all_pats.iloc[idx].drop_duplicates('id')
    all_pats = all_pats[all_pats.filing_status == "Grant"]
    all_pats = all_pats[['id', 'year', 'PRODUCTCODE']]
    all_pats = all_pats.drop(
        columns=['original_assignee_names', 'original_assignees',
                 'inventor_names'],
        errors='ignore')
    all_pats = pd.merge(all_pats, firm_names, on='id', how='left')
    all_pats['patents'] = 1

    # Merge CPC codes
    all_pats_wGRID_MERGED = pd.read_csv(
        RAW / "all_pats_wtitlesCPC.csv", usecols=['id', 'cpc'])
    all_pats = pd.merge(all_pats, all_pats_wGRID_MERGED, on='id', how='left')

    # Non-drug A61 patents
    all_pats_nnan = all_pats[all_pats.cpc.notnull()].copy()
    all_pats_nnan = all_pats_nnan[~all_pats_nnan.cpc.str.contains("A61P")]
    all_pats_nnan = all_pats_nnan[all_pats_nnan.cpc.str.contains("A61")]

    # Extract USID
    all_pats['USID'] = all_pats.id.str.split("-").str[1]

    # Extract GRID IDs (vectorized)
    print("    Extracting GRID IDs...")
    all_pats['GRID'] = all_pats['original_assignees'].apply(_extract_grid_id)
    all_pats_wGRID = all_pats

    # Merge with GRID types
    grid_path = RAW / "GRID" / "types.csv"
    if grid_path.exists():
        GRID = pd.read_csv(grid_path)
        GRID['GRID'] = GRID['grid_id']
        all_pats_wGRID = pd.merge(all_pats_wGRID, GRID[['GRID', 'type']],
                                   on="GRID", how='left')
    else:
        print("    WARNING: GRID/types.csv not found, skipping type merge")
        all_pats_wGRID['type'] = np.nan

    all_pats_wGRID = all_pats_wGRID[[
        'PRODUCTCODE', 'GRID', 'original_assignee_names',
        'original_assignees', 'id', 'inventor_names', 'patents', 'year',
        'type']]

    # Extract solo assignee name (vectorized)
    all_pats_wGRID['orig_assignee_solo'] = \
        all_pats_wGRID['original_assignee_names'].apply(_extract_assignee_name)
    all_pats_wGRID = all_pats_wGRID[[
        'PRODUCTCODE', 'GRID', 'orig_assignee_solo',
        'original_assignee_names', 'original_assignees', 'id',
        'inventor_names', 'patents', 'year', 'type']]

    # Add one-hot dummies for org type
    all_pats_wGRID = pd.concat(
        [all_pats_wGRID, pd.get_dummies(all_pats_wGRID.type)], axis=1)

    # Product code remapping
    for old, new in PC_REMAPS.items():
        all_pats_wGRID.loc[
            all_pats_wGRID.PRODUCTCODE == old, 'PRODUCTCODE'] = new

    # --- Firm entry tracking ---
    # Unique firm-PC entry (first time a firm appears in a PC)
    all_pats_wGRID_unique_firmsPC = all_pats_wGRID.sort_values(
        by=['year', 'PRODUCTCODE', 'GRID'])
    all_pats_wGRID_unique_firmsPC = all_pats_wGRID_unique_firmsPC[
        (~all_pats_wGRID_unique_firmsPC.duplicated(
            subset=['PRODUCTCODE', 'GRID'])) |
        (all_pats_wGRID_unique_firmsPC['GRID'].isnull())]

    all_pats_wGRID_unique_firmsPC.orig_assignee_solo = \
        all_pats_wGRID_unique_firmsPC.orig_assignee_solo.str.lower().str.strip()
    all_pats_wGRID_unique_firmsPC = all_pats_wGRID_unique_firmsPC.sort_values(
        by=['year', 'PRODUCTCODE', 'orig_assignee_solo'])
    all_pats_wGRID_unique_firmsPC = all_pats_wGRID_unique_firmsPC[
        (~all_pats_wGRID_unique_firmsPC.duplicated(
            subset=['PRODUCTCODE', 'orig_assignee_solo'])) |
        (all_pats_wGRID_unique_firmsPC['GRID'].isnull())]

    # Unique firm entry (global — first time ever)
    all_pats_wGRID_unique_firms = all_pats_wGRID.sort_values(
        by=['year', 'GRID'])
    all_pats_wGRID_unique_firms = all_pats_wGRID_unique_firms[
        (~all_pats_wGRID_unique_firms.duplicated(subset=['GRID'])) |
        (all_pats_wGRID_unique_firms['GRID'].isnull())]

    all_pats_wGRID_unique_firms.orig_assignee_solo = \
        all_pats_wGRID_unique_firms.orig_assignee_solo.str.lower().str.strip()
    all_pats_wGRID_unique_firms = all_pats_wGRID_unique_firms.sort_values(
        by=['year', 'orig_assignee_solo'])
    all_pats_wGRID_unique_firms = all_pats_wGRID_unique_firms[
        (~all_pats_wGRID_unique_firms.duplicated(
            subset=['orig_assignee_solo'])) |
        (all_pats_wGRID_unique_firms['GRID'].isnull())]

    # --- Aggregate by PC×year ---
    all_pats_grouped = all_pats_wGRID.groupby(
        ['PRODUCTCODE', 'year']).sum(numeric_only=True)
    all_pats_grouped = all_pats_grouped.add_suffix('_allpats').reset_index()
    all_pats_grouped['PRODUCTCODE'] = all_pats_grouped['PRODUCTCODE'].astype(str)
    all_pats_grouped = unstack_stack_panel(all_pats_grouped)

    all_pats_grouped_cpc = all_pats_nnan.groupby(
        ['PRODUCTCODE', 'year']).sum(numeric_only=True)
    all_pats_grouped_cpc = all_pats_grouped_cpc.add_suffix(
        '_pats_nodrugs').reset_index()
    all_pats_grouped_cpc['PRODUCTCODE'] = \
        all_pats_grouped_cpc['PRODUCTCODE'].astype(str)
    all_pats_grouped_cpc = unstack_stack_panel(all_pats_grouped_cpc)
    all_pats_grouped_cpc = all_pats_grouped_cpc[
        all_pats_grouped_cpc.year > 1975]

    pat_counts_newfirm_PC = all_pats_wGRID_unique_firmsPC.groupby(
        ['PRODUCTCODE', 'year']).sum(numeric_only=True)
    pat_counts_newfirm_PC = pat_counts_newfirm_PC.add_suffix(
        '_newfirmPC').reset_index()
    pat_counts_newfirm_PC['PRODUCTCODE'] = \
        pat_counts_newfirm_PC['PRODUCTCODE'].astype(str)
    pat_counts_newfirm_PC = unstack_stack_panel(pat_counts_newfirm_PC)

    pat_counts_newfirm = all_pats_wGRID_unique_firms.groupby(
        ['PRODUCTCODE', 'year']).sum(numeric_only=True)
    pat_counts_newfirm = pat_counts_newfirm.add_suffix(
        '_newfirm').reset_index()
    pat_counts_newfirm['PRODUCTCODE'] = \
        pat_counts_newfirm['PRODUCTCODE'].astype(str)
    pat_counts_newfirm = unstack_stack_panel(pat_counts_newfirm)

    # Merge all into main_outcomes
    main_outcomes = pd.merge(main_outcomes, all_pats_grouped,
                             on=['PRODUCTCODE', 'year'], how='left')
    main_outcomes = pd.merge(main_outcomes, pat_counts_newfirm_PC,
                             on=['PRODUCTCODE', 'year'], how='left')
    main_outcomes = pd.merge(main_outcomes, pat_counts_newfirm,
                             on=['PRODUCTCODE', 'year'], how='left')
    main_outcomes = pd.merge(main_outcomes, all_pats_grouped_cpc,
                             on=['PRODUCTCODE', 'year'], how='left')

    main_outcomes.loc[main_outcomes.FDA_own_accord.isnull(),
                      'FDA_own_accord'] = -1
    main_outcomes = main_outcomes.fillna(0)

    print(f"    Patents processed: {len(all_pats_wGRID)} total patents")
    return main_outcomes, all_pats_wGRID


# ============================================================================
# PHASE 5: Citations
# ============================================================================
def phase_05_citations(main_outcomes):
    """Merge citation data by PC×year."""
    print("  Phase 5: Citations...")

    applicantonlycites = pd.read_csv(
        RAW / "PC_by_year_cites_ApplicantOnly.csv")
    applicantonlycites['PRODUCTCODE'] = \
        applicantonlycites['PRODUCTCODE'].astype(str)

    applicantonlycites_outside = pd.read_csv(
        RAW / "PC_by_year_diff_ind_appl_only.csv")
    applicantonlycites_outside['times_cited_outside_ind'] = \
        applicantonlycites_outside['times_cited']
    applicantonlycites_outside = applicantonlycites_outside[
        ['PRODUCTCODE', 'year', 'times_cited_outside_ind']]
    applicantonlycites_outside['PRODUCTCODE'] = \
        applicantonlycites_outside['PRODUCTCODE'].astype(str)

    main_outcomes = pd.merge(main_outcomes, applicantonlycites,
                             on=['PRODUCTCODE', 'year'], how='left')
    main_outcomes = pd.merge(main_outcomes, applicantonlycites_outside,
                             on=['PRODUCTCODE', 'year'], how='left')
    return main_outcomes


# ============================================================================
# PHASE 6: Patent values (xi) + firm size
# ============================================================================
def phase_06_patent_values(main_outcomes, all_pats_wGRID):
    """Merge KPSS patent values and Compustat firm size."""
    print("  Phase 6: Patent values (xi) + firm size...")

    patents_xi = pd.read_csv(RAW / config.GEN_RAW_FILES["kpss_2019"])
    patents_xi['patnum'] = patents_xi['patent_num']
    patents_xi['year'] = patents_xi.filing_date.str.split("/").str[2]
    patents_xi.loc[patents_xi.year.isnull(), 'year'] = \
        patents_xi.loc[patents_xi.year.isnull(), 'issue_date'].str.split(
            "/").str[2]
    patents_xi['year'] = patents_xi.year.astype(int)
    patents_xi['CPI'] = patents_xi['xi_real'] / patents_xi['xi_nominal']
    patents_xi = patents_xi.sort_values(
        by=['patnum', 'xi_real']).drop_duplicates(['patnum'])

    # Load Compustat
    firm_innovaton = pd.read_csv(
        RAW / config.GEN_RAW_FILES["compustat_firm_data"])
    firm_innovaton['firm_size'] = firm_innovaton['at']
    firm_innovaton['permno'] = firm_innovaton['LPERMNO']
    firm_innovaton = firm_innovaton[~firm_innovaton.fyear.isnull()]
    firm_innovaton['year'] = firm_innovaton['fyear'].astype(int)

    # Extract patnum from patent ID and merge
    all_pats_wGRID_forxi = all_pats_wGRID.copy()
    all_pats_wGRID_forxi['patnum'] = \
        all_pats_wGRID_forxi['id'].str.split('-').str[1]

    # Separate numeric vs non-numeric patnums
    all_pats_wGRID_append = all_pats_wGRID_forxi[
        all_pats_wGRID_forxi.patnum.str.isupper()]
    all_pats_wGRID_forxi = all_pats_wGRID_forxi[
        ~all_pats_wGRID_forxi.patnum.str.isupper()]
    all_pats_wGRID_forxi['patnum'] = \
        all_pats_wGRID_forxi['patnum'].astype(int)

    # Merge with KPSS
    all_pats_wGRID_forxi = pd.merge(
        all_pats_wGRID_forxi,
        patents_xi[['patnum', 'permno', 'xi_real', 'xi_nominal', 'cites',
                     'CPI']],
        on='patnum', how='left')
    all_pats_wGRID_forxi['CPI'] = (all_pats_wGRID_forxi['xi_real'] /
                                    all_pats_wGRID_forxi['xi_nominal'])

    # Recombine
    all_pats_wGRID_forxi = pd.concat(
        [all_pats_wGRID_forxi, all_pats_wGRID_append])
    all_pats_wGRID_forxi['PRODUCTCODE'] = \
        all_pats_wGRID_forxi['PRODUCTCODE'].astype(str)
    all_pats_wGRID_forxi['year'] = \
        all_pats_wGRID_forxi['year'].astype(int)

    # Merge with Compustat firm size
    firm_innovaton = firm_innovaton[
        firm_innovaton.permno.isin(all_pats_wGRID_forxi.permno)]
    all_pats_wGRID_forxi_test = pd.merge(
        all_pats_wGRID_forxi,
        firm_innovaton[['permno', 'firm_size', 'year']],
        on=['permno', 'year'], how='left')
    all_pats_wGRID_forxi_test['firm_size'] *= \
        all_pats_wGRID_forxi_test['CPI']

    # Write patent-level data
    all_pats_wGRID_forxi_test.to_csv(
        OUT_DERIVED / "all_patents_w_xi_oct22_24.csv", index=False)
    print(f"    Wrote all_patents_w_xi_oct22_24.csv: "
          f"{len(all_pats_wGRID_forxi_test)} rows")

    # Aggregate to PC×year
    all_pats_wGRID_grouped = all_pats_wGRID_forxi_test[
        ['PRODUCTCODE', 'year', 'xi_real', 'firm_size']
    ].groupby(['PRODUCTCODE', 'year']).mean().reset_index()

    main_outcomes = pd.merge(main_outcomes, all_pats_wGRID_grouped,
                             on=['PRODUCTCODE', 'year'], how='left')
    return main_outcomes


# ============================================================================
# PHASE 7: Adverse events
# ============================================================================
def phase_07_adverse_events(main_outcomes):
    """Process MAUDE adverse event data."""
    print("  Phase 7: Adverse events...")

    maude_path = RAW / "MAUDE"
    device_path = maude_path / "device_data"

    if not maude_path.exists():
        # Fails closed: MAUDE is a public FDA extract required on both routes, and every
        # adverse-event exhibit downstream depends on the columns and the
        # adverse_event_panel_by_PC_full.csv built here.
        raise RuntimeError(
            f"MAUDE directory not found: {maude_path}. gen_01 phase 7 builds every adverse-event "
            "outcome in the master panel from it, so it is required on both the restricted and "
            "the simulated route. Supply the public FDA MAUDE extract (see DATA_INPUTS.md) or, on "
            "the simulated route, run "
            "`python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` first."
        )

    # Load only columns needed for manuscript-facing adverse-event counts.  The
    # earlier implementation loaded and retained the full MAUDE event detail
    # across all device files, which can exceed container memory.
    master_event = pd.read_csv(
        maude_path / "masterevent.txt", encoding='latin-1',
        on_bad_lines='skip', sep="|",
        usecols=['MDR_REPORT_KEY', 'REPORT_SOURCE_CODE', 'DATE_RECEIVED'])
    patients = pd.read_csv(
        maude_path / "patient.txt", encoding='latin-1',
        on_bad_lines='skip', sep="|",
        usecols=['MDR_REPORT_KEY', 'PATIENT_SEQUENCE_NUMBER',
                 'SEQUENCE_NUMBER_OUTCOME'])
    # Keep one row per event problem so the aggregation preserves the row
    # multiplicity of the original merge without carrying unused descriptions.
    device_problems = pd.read_csv(
        maude_path / "deviceproblems.txt", encoding='latin-1',
        on_bad_lines='skip', sep="|", header=None,
        names=['MDR_REPORT_KEY', 'DEVICE_PROBLEM_CODE'],
        usecols=[0])

    onlyfiles = [f for f in listdir(str(device_path))
                 if isfile(join(str(device_path), f))]
    onlyfiles.sort()

    outcome_codes = ["L", "H", "S", "C", "R", "O", "U", "I", "A", "D"]
    reporter_codes = ["U", "D", "P", "M"]
    grouped_parts = []

    for file in onlyfiles:
        if file == ".DS_Store":
            continue
        print(f"    Processing {file}...")
        df = pd.read_csv(
            device_path / file, encoding='latin-1',
            on_bad_lines='skip', sep="|")

        cols_to_keep = [c for c in [
            'MDR_REPORT_KEY', 'DEVICE_EVENT_KEY', 'IMPLANT_FLAG',
            'DATE_REMOVED_FLAG', 'DEVICE_SEQUENCE_NO', 'DATE_RECEIVED',
            'BRAND_NAME', 'GENERIC_NAME', 'MANUFACTURER_D_NAME',
            'MANUFACTURER_D_ADDRESS_1', 'MANUFACTURER_D_CITY',
            'EXPIRATION_DATE_OF_DEVICE', 'MODEL_NUMBER', 'CATALOG_NUMBER',
            'LOT_NUMBER', 'OTHER_ID_NUMBER', 'DEVICE_OPERATOR',
            'DEVICE_AVAILABILITY', 'DATE_RETURNED_TO_MANUFACTURER',
            'DEVICE_REPORT_PRODUCT_CODE', 'DEVICE_AGE_TEXT',
            'DEVICE_EVALUATED_BY_MANUFACTUR'] if c in df.columns]
        df = df[cols_to_keep]

        # NO FNL filter — process all product codes
        temp = master_event[
            master_event.MDR_REPORT_KEY.isin(df['MDR_REPORT_KEY'].values)]
        merged_master = pd.merge(temp, df, on="MDR_REPORT_KEY", how="left")
        merged_master = merged_master.dropna(subset=['DATE_RECEIVED_y'])
        merged_master = pd.merge(merged_master, patients,
                                  on="MDR_REPORT_KEY", how="left")
        merged_master = pd.merge(merged_master, device_problems,
                                  on="MDR_REPORT_KEY", how="left")
        merged_master.SEQUENCE_NUMBER_OUTCOME = \
            merged_master.SEQUENCE_NUMBER_OUTCOME.fillna("None")

        # Outcome flags
        for code in outcome_codes:
            merged_master[code] = 0
            merged_master.loc[
                merged_master.SEQUENCE_NUMBER_OUTCOME.str.contains(code),
                code] = 1

        merged_master['year'] = pd.DatetimeIndex(
            merged_master['DATE_RECEIVED_x']).year
        merged_master['PRODUCTCODE'] = \
            merged_master['DEVICE_REPORT_PRODUCT_CODE']
        merged_master['event_count'] = 1

        # Reporter-specific flags
        for col in outcome_codes:
            for reporter in reporter_codes:
                new_col_name = f'{col}_{reporter}'
                merged_master[new_col_name] = np.where(
                    merged_master['REPORT_SOURCE_CODE'].eq(reporter),
                    merged_master[col],
                    0)

        keep_cols = (
            ['PRODUCTCODE', 'year', 'event_count'] +
            outcome_codes +
            [f'{code}_{reporter}' for code in outcome_codes
             for reporter in reporter_codes])
        grouped_parts.append(
            merged_master[keep_cols]
            .groupby(['PRODUCTCODE', 'year'])
            .sum(numeric_only=True)
            .reset_index())
        del df, temp, merged_master
        gc.collect()

    if len(grouped_parts) == 0:
        print("    WARNING: No adverse event data processed")
        return main_outcomes

    # Aggregate by PC×year
    df_combined_grouped = pd.concat(grouped_parts, ignore_index=True).groupby(
        ['PRODUCTCODE', 'year']).sum(numeric_only=True).reset_index()

    # Recalculate aggregate flags from reporter-specific, matching the original
    # code's U/D/P/M reporter convention, and guarantee expected columns exist.
    for code in ['D', 'H', 'L', 'S', 'R']:
        reporter_cols = [f'{code}_{r}' for r in reporter_codes]
        for reporter_col in reporter_cols:
            if reporter_col not in df_combined_grouped.columns:
                df_combined_grouped[reporter_col] = 0
        df_combined_grouped[code] = df_combined_grouped[reporter_cols].sum(axis=1)

    df_combined_grouped = unstack_stack_panel(df_combined_grouped)
    expected_cols = (
        ['event_count', 'L', 'H', 'S', 'R', 'D'] +
        [f'{code}_{reporter}' for code in outcome_codes
         for reporter in reporter_codes])
    for col in expected_cols:
        if col not in df_combined_grouped.columns:
            df_combined_grouped[col] = 0

    # Write
    df_combined_grouped.to_csv(
        OUT_DERIVED / "adverse_event_panel_by_PC_full.csv", index=False)
    print(f"    Wrote adverse_event_panel_by_PC_full.csv: "
          f"{len(df_combined_grouped)} rows")

    # Merge into main_outcomes — keep only outcome columns (drop junk
    # numeric aggregations like summed zip codes, event keys, etc.)
    _adv_keep_cols = (
        ['PRODUCTCODE', 'year', 'event_count'] +
        ['L', 'H', 'S', 'R', 'D'] +
        [f'{code}_{r}' for code in ['L', 'H', 'S', 'C', 'R', 'O', 'U', 'I', 'A', 'D']
         for r in ['U', 'D', 'P', 'M']
         if f'{code}_{r}' in df_combined_grouped.columns])
    main_outcomes = pd.merge(
        main_outcomes, df_combined_grouped[_adv_keep_cols],
        on=['PRODUCTCODE', 'year'], how='left')

    # Fill post-1991 NaN with 0 (MAUDE reliable after 1992)
    columns_to_replace = [
        'L_U', 'L_D', 'L_P', 'L_M', 'H_U', 'H_D', 'H_P', 'H_M',
        'S_U', 'S_D', 'S_P', 'S_M', 'C_U', 'C_D', 'C_P', 'C_M',
        'R_U', 'R_D', 'R_P', 'R_M', 'O_U', 'O_D', 'O_P', 'O_M',
        'U_U', 'U_D', 'U_P', 'U_M', 'I_U', 'I_D', 'I_P', 'I_M',
        'A_U', 'A_D', 'A_P', 'A_M', 'D_U', 'D_D', 'D_P', 'D_M',
        'D', 'H', 'L', 'S', 'R']
    cols_present = [c for c in columns_to_replace if c in main_outcomes.columns]
    main_outcomes.loc[main_outcomes['year'] > 1991, cols_present] = (
        main_outcomes.loc[main_outcomes['year'] > 1991, cols_present].fillna(0))

    return main_outcomes


# ============================================================================
# PHASE 8: Safety keywords
# ============================================================================
def phase_08_safety_keywords():
    """Extract safety/cost/quality keyword flags from patent text."""
    print("  Phase 8: Safety keywords...")

    if KeywordProcessor is None:
        print("    WARNING: flashtext not installed, skipping safety keywords")
        return

    title_abstract = pd.read_csv(RAW / config.GEN_RAW_FILES["fda_patents_text"])
    title_abstract['clean_input'] = title_abstract['input'].apply(clean_text)

    safety_processor = KeywordProcessor(case_sensitive=False)
    cost_processor = KeywordProcessor(case_sensitive=False)
    quality_processor = KeywordProcessor(case_sensitive=False)

    safety_keywords = [
        'safety', 'safe', 'safer', 'endangering', 'precautions', 'unsafe',
        'hazardous', 'failsafe', 'safely', 'dangerous', 'hazard', 'danger',
        'harming', 'injuring', 'injury', 'jeopardizing', 'risking', 'risk',
        'complication', 'life-threatening']
    cost_keywords = [
        'cost', 'price', 'economic', 'costs', 'revenue', 'savings',
        'discount', 'premiums', 'pricing', 'budget', 'expense',
        'expensive', 'costly', 'prices', 'complexity']
    quality_keywords = [
        'performance', 'reliability', 'performances', 'quality',
        'durability', 'accuracy', 'robustness', 'reproducibility',
        'transferability', 'effectiveness', 'sensitivity']

    safety_processor.add_keywords_from_list(safety_keywords)
    cost_processor.add_keywords_from_list(cost_keywords)
    quality_processor.add_keywords_from_list(quality_keywords)

    def set_flag(processor, text):
        return 1 if processor.extract_keywords(text) else 0

    title_abstract['safety'] = title_abstract['clean_input'].apply(
        lambda x: set_flag(safety_processor, x))
    title_abstract['cost'] = title_abstract['clean_input'].apply(
        lambda x: set_flag(cost_processor, x))
    title_abstract['quality'] = title_abstract['clean_input'].apply(
        lambda x: set_flag(quality_processor, x))

    title_abstract[['id', 'safety', 'cost', 'quality']].to_csv(
        OUT_DERIVED / "safety_vars_allpats.csv", index=False)
    print(f"    Wrote safety_vars_allpats.csv: {len(title_abstract)} rows")


# ============================================================================
# PHASE 9: Treatment indicators + Full_sample
# ============================================================================
def phase_09_treatment_indicators(main_outcomes):
    """Add reclassification treatment indicators and write Full_sample."""
    print("  Phase 9: Treatment indicators...")

    # --- 3 to 2 reclassification ---
    df_3_2 = pd.read_csv(
        RAW / config.GEN_RAW_FILES["3_2_begin_final_revisions"])
    df_3_2['PRODUCTCODE'] = df_3_2['PRODUCTCODE_x']
    df_3_2 = df_3_2[['DESCRIPTION_OF_REGNUM', 'year_reclassified',
                       'FDA_own_accord', 'PART_DESCRIPTION', 'PRODUCTCODE',
                       'Petition_DeNovo_Filing_Date', 'REGULATIONNUMBER',
                       'date_proposed', 'SUBMISSION_TYPE_ID',
                       'SUBPART_DESCRIPTION']]
    right_suffix = '_3_2'
    rename_dict = {col: f"{col}{right_suffix}" for col in [
        'DESCRIPTION_OF_REGNUM', 'year_reclassified', 'FDA_own_accord',
        'PART_DESCRIPTION', 'Petition_DeNovo_Filing_Date',
        'REGULATIONNUMBER', 'date_proposed', 'SUBMISSION_TYPE_ID',
        'SUBPART_DESCRIPTION']}
    df_3_2 = df_3_2.rename(columns=rename_dict)
    df_3_2 = df_3_2[df_3_2.PRODUCTCODE != 'LTT']
    df_3_2 = df_3_2[df_3_2.PRODUCTCODE != 'HRD']
    main_outcomes = pd.merge(main_outcomes, df_3_2,
                             on='PRODUCTCODE', how='left')

    # --- 2 to 1 reclassification ---
    synth_2_1_true = main_outcomes[
        (main_outcomes.Reg_Change_List.str.contains("63 FR 59", na=False)) &
        (main_outcomes.SUBMISSION_TYPE_ID == '510(K) Exempt')].copy()
    synth_2_1_true = synth_2_1_true[
        synth_2_1_true.PRODUCTCODE != 'PUN'].copy()

    synth_2_1_true2 = main_outcomes[
        ((main_outcomes.Reg_Change_List.str.contains("61 FR 111", na=False)) |
         (main_outcomes.Reg_Change_List.str.contains("61 FR 112", na=False))) &
        ((main_outcomes.DEVICECLASS == '1') |
         (main_outcomes.DEVICECLASS == 1)) &
        (main_outcomes.SUBMISSION_TYPE_ID == '510(K) Exempt')]

    synth_2_1_true = synth_2_1_true[
        ~synth_2_1_true.PRODUCTCODE.isin(synth_2_1_true2.PRODUCTCODE)]
    synth_2_1_true['year_reclassified'] = 1998
    synth_2_1_true2['year_reclassified'] = 1996

    synth_2_1 = pd.concat([synth_2_1_true, synth_2_1_true2])
    synth_2_1 = synth_2_1[['PRODUCTCODE', 'year_reclassified']].drop_duplicates()
    synth_2_1 = synth_2_1.rename(columns={'year_reclassified':
                                            'year_reclassified_2_1'})
    main_outcomes = pd.merge(main_outcomes, synth_2_1,
                             on='PRODUCTCODE', how='left')

    # PRODUCTCODE_COUNT: rows per product code (used for validation)
    main_outcomes['PRODUCTCODE_COUNT'] = main_outcomes.groupby(
        'PRODUCTCODE')['PRODUCTCODE'].transform('count')

    # --- Treatment/control indicators ---
    synth_number2 = pd.read_csv(
        DERIVED / config.SOURCE_FILES["synth_number"],
        dtype={'REGULATIONNUMBER': str})
    synth_number2.REGULATIONNUMBER = synth_number2.REGULATIONNUMBER.str.pad(
        width=8, side='right', fillchar="0")
    synth_number2 = synth_number2.drop_duplicates('PRODUCTCODE_x')
    synth_number2['PRODUCTCODE'] = synth_number2['PRODUCTCODE_x']
    synth_number2 = synth_number2[['PRODUCTCODE', 'Reg_Change_Text']]

    def get_years(data):
        s = data.Reg_Change_Text
        try:
            list_str = re.findall(r"\,+\ +[0-9]{1,4}", s)
            list_str = [s.replace(', ', "") for s in list_str]
            list_int = [int(s) for s in list_str]
            return "None" if len(list_str) == 0 else list_int
        except Exception:
            return "Null"

    synth_number2['reclass_years'] = synth_number2.apply(get_years, axis=1)
    synth_no_reclass_PCs = synth_number2[
        synth_number2.reclass_years == 'None']['PRODUCTCODE']

    main_outcomes['controls'] = 0
    main_outcomes.loc[
        ((main_outcomes.year_reclassified_2_1.isnull()) &
         (main_outcomes.year_reclassified_3_2.isnull())) &
        (main_outcomes.PRODUCTCODE.isin(synth_no_reclass_PCs)),
        'controls'] = 1

    # Pre-period patent sums for 2→1
    main_outcomes['patent_sum_2_1'] = main_outcomes[
        (main_outcomes.year < main_outcomes.year_reclassified_2_1) &
        (main_outcomes.year_reclassified_2_1.notnull())
    ].groupby('PRODUCTCODE')['patents_allpats'].transform(pd.Series.sum)
    main_outcomes['patent_sum_2_1'] = main_outcomes.groupby('PRODUCTCODE')[
        'patent_sum_2_1'].transform(lambda v: v.ffill())

    main_outcomes['use_2_1_treat'] = 0
    main_outcomes.loc[(main_outcomes.controls == 1) |
                      (main_outcomes.patent_sum_2_1 > 0),
                      'use_2_1_treat'] = 1

    # Total patent sum
    main_outcomes['total_pat_sum'] = main_outcomes.groupby('PRODUCTCODE')[
        'patents_allpats'].transform(pd.Series.sum)
    main_outcomes['one_pat_atleast'] = 0
    main_outcomes.loc[main_outcomes.total_pat_sum > 0,
                      'one_pat_atleast'] = 1

    # Pre-period patent sums for 3→2
    main_outcomes['patent_sum_3_2'] = main_outcomes[
        (main_outcomes.year < main_outcomes.year_reclassified_3_2) &
        (main_outcomes.year_reclassified_3_2.notnull())
    ].groupby('PRODUCTCODE')['patents_allpats'].transform(pd.Series.sum)
    main_outcomes['patent_sum_3_2'] = main_outcomes.groupby('PRODUCTCODE')[
        'patent_sum_3_2'].transform(lambda v: v.ffill())

    main_outcomes['use_3_2_treat'] = 0
    main_outcomes.loc[(main_outcomes.controls == 1) |
                      (main_outcomes.patent_sum_3_2 > 0),
                      'use_3_2_treat'] = 1

    # Recompute total_pat_sum and one_pat_atleast (matches source)
    main_outcomes['total_pat_sum'] = main_outcomes.groupby('PRODUCTCODE')[
        'patents_allpats'].transform(pd.Series.sum)
    main_outcomes['one_pat_atleast'] = 0
    main_outcomes.loc[main_outcomes.total_pat_sum > 0,
                      'one_pat_atleast'] = 1

    # Write Full_sample
    main_outcomes.to_csv(OUT_DERIVED / "Full_sample.csv", index=False)
    n_treated_21 = len(set(main_outcomes[
        main_outcomes.year_reclassified_2_1.notnull()]['PRODUCTCODE']))
    n_treated_32 = len(set(main_outcomes[
        main_outcomes.year_reclassified_3_2.notnull()]['PRODUCTCODE']))
    print(f"    Wrote Full_sample.csv: {len(main_outcomes)} rows "
          f"({n_treated_21} treated 2→1, {n_treated_32} treated 3→2)")

    return main_outcomes, synth_no_reclass_PCs


# ============================================================================
# PHASE 10: Intuitive matching
# ============================================================================
def phase_10_intuitive_matching(main_outcomes):
    """Intuitive matched-pair construction for 2→1 and 3→2."""
    print("  Phase 10: Intuitive matching...")

    # Reload Full_sample (matches source behavior) — from staging if available
    _fs_src = OUT_DERIVED if (OUT_DERIVED / "Full_sample.csv").exists() else DERIVED
    main_outcomes = pd.read_csv(_fs_src / "Full_sample.csv")

    # Add PART_DESCRIPTION from synth_number
    synth_number = pd.read_csv(
        DERIVED / config.SOURCE_FILES["synth_number"],
        dtype={'REGULATIONNUMBER': str})
    synth_number.REGULATIONNUMBER = synth_number.REGULATIONNUMBER.str.pad(
        width=8, side='right', fillchar="0")
    synth_number = synth_number.drop_duplicates('PRODUCTCODE_x')
    synth_number['PRODUCTCODE'] = synth_number['PRODUCTCODE_x']
    synth_number = synth_number[['PRODUCTCODE', 'PART_DESCRIPTION']]
    main_outcomes = pd.merge(main_outcomes, synth_number, how='left')

    # Load FOI class
    foi = pd.read_csv(RAW / config.GEN_RAW_FILES["foiclass"],
                       encoding='latin-1', on_bad_lines='skip', sep="|")
    foi['implant'] = 0
    foi.loc[foi.Implant_Flag == 'Y', 'implant'] = 1
    foi['life_sustaining'] = 0
    foi.loc[foi.Life_Sustain_support_flag == 'Y', 'life_sustaining'] = 1

    # ---- 2→1 Intuitive Matching ----
    print("    2→1 intuitive matching...")
    treated_list = []
    matched_list = []
    similarity = []
    baseline_devs = []
    year_reclass_list = []

    main_outcomes['v_serious'] = (main_outcomes['D'] + main_outcomes['L'] +
                                   main_outcomes['H'] + main_outcomes['S'])

    pcs_implant = foi[foi.implant == 1]['PRODUCTCODE']
    main_outcomes['REGULATIONNUMBER'] = \
        main_outcomes['REGULATIONNUMBER'].astype(float)

    active_main_outcomes = main_outcomes[
        (main_outcomes.patent_sum_2_1 > 0) |
        (main_outcomes.controls == 1)]
    active_main_outcomes = active_main_outcomes[
        active_main_outcomes.one_pat_atleast > 0]

    product_codes_iter = active_main_outcomes[
        active_main_outcomes.year_reclassified_2_1.notnull()
    ]['PRODUCTCODE'].sample(frac=1)

    for number in np.unique(product_codes_iter):
        PART_DESC = active_main_outcomes[
            active_main_outcomes.PRODUCTCODE == number][
            'PART_DESCRIPTION'].values[0]
        yr_reclass = active_main_outcomes[
            active_main_outcomes.PRODUCTCODE == number][
            'year_reclassified_2_1'].values[0]

        control = active_main_outcomes[
            (active_main_outcomes['year_reclassified_3_2'].isnull()) &
            (active_main_outcomes['year_reclassified_2_1'].isnull()) &
            (active_main_outcomes.PART_DESCRIPTION == PART_DESC)]
        control = control[~control.PRODUCTCODE.isin(product_codes_iter)]
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control[~control.PRODUCTCODE.isin(
            foi[foi['life_sustaining'] == 1]['PRODUCTCODE'])]
        implant_t = foi[foi.PRODUCTCODE == number]['implant'].values[0]
        if implant_t == 1:
            control = control[control.PRODUCTCODE.isin(pcs_implant)]
        else:
            control = control[~control.PRODUCTCODE.isin(pcs_implant)]

        treated = active_main_outcomes[
            active_main_outcomes.PRODUCTCODE == number]
        treated = treated.copy()
        treated['event_time'] = treated['year'] - int(float(yr_reclass))
        control = control.copy()
        control['event_time'] = control['year'] - int(float(yr_reclass))

        treated['baseline_sum'] = treated[
            (treated.event_time < 0) &
            (treated.event_time > -6)]['v_serious'].sum()
        baseline_devs.append(treated['baseline_sum'].values[0])

        control = control.groupby(
            ['PRODUCTCODE', 'event_time']).mean(numeric_only=True).reset_index()
        control_meaned = control[control.event_time < 0].groupby(
            'PRODUCTCODE').mean(numeric_only=True).reset_index()

        treated_meaned = treated[treated.event_time < 0].mean(numeric_only=True)
        try:
            sim_distances, sim_indices = get_similar(
                treated_meaned[['REGULATIONNUMBER']].values,
                control_meaned[['REGULATIONNUMBER']].values, topn=1)
            treated_list.append(number)
            matched_list.append(
                control_meaned.iloc[sim_indices]['PRODUCTCODE'])
            similarity.append(sim_distances[sim_indices])
            year_reclass_list.append(yr_reclass)
        except Exception:
            treated_list.append(number)
            matched_list.append("None")
            similarity.append(0)
            year_reclass_list.append(yr_reclass)

    matched_pairs = pd.DataFrame()
    matched_pairs['PRODUCTCODE'] = treated_list
    matched_pairs['treated'] = treated_list
    matched_pairs['match'] = matched_list
    matched_pairs['SSE'] = similarity
    matched_pairs['baseline_serious'] = baseline_devs
    matched_pairs['FE'] = matched_pairs.index
    matched_pairs['year_reclassified_controls'] = year_reclass_list
    matched_pairs = matched_pairs[matched_pairs['match'] != "None"]

    final = active_main_outcomes[
        (active_main_outcomes.PRODUCTCODE.isin(matched_pairs.treated)) |
        (active_main_outcomes.PRODUCTCODE.isin(matched_pairs.match))]
    final = final.copy()
    final['treatment'] = 0
    final.loc[final.PRODUCTCODE.isin(matched_pairs.treated), 'treatment'] = 1
    matched_pairs['year_reclassified'] = \
        matched_pairs['year_reclassified_controls']
    final = pd.merge(final, matched_pairs[['PRODUCTCODE', 'year_reclassified']],
                     on='PRODUCTCODE', how='left')
    final['factorized'] = final.PRODUCTCODE.astype('category').cat.codes
    final['posttreat'] = 0
    final.loc[(final.treatment == 1) &
              (final.year >= final.year_reclassified), 'posttreat'] = 1

    matched_pairs.to_csv(OUT_DERIVED / "matched_pairs_intuitive_2_1.csv",
                          index=False)
    final.to_csv(OUT_DERIVED / "intuitive_2_1_oct22_24.csv", index=False)
    print(f"    Wrote intuitive_2_1_oct22_24.csv: {len(final)} rows "
          f"({len(matched_pairs)} matched pairs)")

    # ---- 3→2 Intuitive Matching ----
    print("    3→2 intuitive matching...")
    # Note: do NOT drop FDA_own_accord — it's needed in downstream spillover
    # files. The 3→2 matching uses FDA_own_accord_3_2 (suffixed) instead.

    hand_coded_intuitive = pd.read_csv(
        RAW / config.GEN_RAW_FILES["hand_coded_intuitive_3_2"])
    df_treated = main_outcomes[
        (main_outcomes.year_reclassified_3_2.notnull()) &
        (main_outcomes.FDA_own_accord_3_2 == 1)]

    final_3_2_matched = main_outcomes[
        (main_outcomes.PRODUCTCODE.isin(set(df_treated['PRODUCTCODE']))) |
        (main_outcomes.PRODUCTCODE.isin(
            set(hand_coded_intuitive['PRODUCTCODE'])))]
    final_3_2_matched = final_3_2_matched.copy()

    final_3_2_matched['treatment'] = 0
    final_3_2_matched.loc[
        final_3_2_matched.PRODUCTCODE.isin(
            set(df_treated['PRODUCTCODE'])), 'treatment'] = 1

    get_groups = final_3_2_matched.sort_values(
        by=['PART_DESCRIPTION', 'SUBPART_DESCRIPTION',
            'DESCRIPTION_OF_REGNUM', 'DEVICENAME']
    ).drop_duplicates('PRODUCTCODE')[
        ['PART_DESCRIPTION', 'SUBPART_DESCRIPTION',
         'DESCRIPTION_OF_REGNUM', 'DEVICENAME', 'PRODUCTCODE']]

    get_groups['Group'] = np.repeat(np.arange(1, 13, 1), 2)
    final_3_2_matched = pd.merge(
        final_3_2_matched, get_groups[['PRODUCTCODE', 'Group']],
        on='PRODUCTCODE', how='left')
    final_3_2_matched['year_reclassified'] = \
        final_3_2_matched['year_reclassified_3_2']
    final_3_2_matched['factorized'] = \
        final_3_2_matched.PRODUCTCODE.astype('category').cat.codes
    final_3_2_matched['posttreat'] = 0
    final_3_2_matched.loc[
        (final_3_2_matched.treatment == 1) &
        (final_3_2_matched.year >= final_3_2_matched.year_reclassified),
        'posttreat'] = 1

    final_3_2_matched = final_3_2_matched.drop(
        columns=['FDA_own_accord'], errors='ignore')
    final_3_2_matched.to_csv(
        OUT_DERIVED / "intuitive_3_2_oct22_24_similarity.csv")
    print(f"    Wrote intuitive_3_2_oct22_24_similarity.csv: "
          f"{len(final_3_2_matched)} rows")

    return main_outcomes, foi, df_treated


# ============================================================================
# PHASE 11: Later-treated + Spillovers
# ============================================================================
def phase_11_later_treated_spillovers(main_outcomes, foi, df_treated):
    """Build later-treated control and spillover samples."""
    print("  Phase 11: Later-treated + Spillovers...")

    # ---- Later-treated 2→1 ----
    print("    Later-treated 2→1...")
    synth_number2 = pd.read_csv(
        DERIVED / config.SOURCE_FILES["synth_number"],
        dtype={'REGULATIONNUMBER': str})
    synth_number2.REGULATIONNUMBER = synth_number2.REGULATIONNUMBER.str.pad(
        width=8, side='right', fillchar="0")
    synth_number2 = synth_number2.drop_duplicates('PRODUCTCODE_x')
    synth_number2['PRODUCTCODE'] = synth_number2['PRODUCTCODE_x']

    def get_years(data):
        s = data.Reg_Change_Text
        try:
            list_str = re.findall(r"\,+\ +[0-9]{1,4}", s)
            list_str = [s.replace(', ', "") for s in list_str]
            list_int = [int(s) for s in list_str]
            return "None" if len(list_str) == 0 else list_int
        except Exception:
            return "Null"

    synth_number2['reclass_years'] = synth_number2.apply(get_years, axis=1)
    synth_no_reclass_PCs = synth_number2[
        synth_number2.reclass_years == 'None']['PRODUCTCODE']

    # Parse good controls from text file
    good_controls_path = RAW / config.GEN_RAW_FILES["good_2_1_controls"]
    with open(good_controls_path, "r") as f:
        list_strings = f.read().split("§")
    keep = []
    for s in list_strings:
        s = s.strip()
        if re.search(r"\d\d\d+\.+\d", s):
            if re.search(r"\d\d\d+\.+9", s):
                pass
            else:
                keep.append(s[:8])
    controls_good = set(keep)

    synth_number2['good_controls'] = 0
    synth_number2.loc[
        synth_number2.REGULATIONNUMBER.isin(controls_good),
        'good_controls'] = 1

    # Build sample
    synth_2_1_control = main_outcomes[
        (main_outcomes.PRODUCTCODE.isin(synth_no_reclass_PCs)) |
        (((main_outcomes.DEVICECLASS == '1') |
          (main_outcomes.DEVICECLASS == 1)) &
         ~(main_outcomes.PRODUCTCODE.isin(
             main_outcomes[main_outcomes.year_reclassified_2_1.notnull()][
                 'PRODUCTCODE'].values)))]

    synth_2_1_combined_1996 = pd.concat([
        synth_2_1_control[synth_2_1_control.PRODUCTCODE.isin(
            synth_number2[synth_number2.good_controls == 1]['PRODUCTCODE'])],
        main_outcomes[main_outcomes.year_reclassified_2_1.notnull()]])

    synth_2_1_combined_1996 = synth_2_1_combined_1996[
        synth_2_1_combined_1996.year > 1975]
    synth_2_1_combined_1996['treatment'] = 0
    synth_2_1_combined_1996.loc[
        synth_2_1_combined_1996.year_reclassified_2_1.notnull(),
        'treatment'] = 1
    synth_2_1_combined_1996['posttreat'] = 0
    synth_2_1_combined_1996.loc[
        synth_2_1_combined_1996.year >=
        synth_2_1_combined_1996.year_reclassified_2_1,
        'posttreat'] = 1
    synth_2_1_combined_1996['factorized'] = \
        synth_2_1_combined_1996.PRODUCTCODE.astype('category').cat.codes

    synth_2_1_combined_1996_regress = synth_2_1_combined_1996.copy()
    synth_2_1_combined_1996_regress = synth_2_1_combined_1996_regress[
        (synth_2_1_combined_1996_regress.patent_sum_2_1 > 0) |
        (synth_2_1_combined_1996_regress.controls == 1)]
    synth_2_1_combined_1996_regress = synth_2_1_combined_1996_regress[
        synth_2_1_combined_1996_regress.one_pat_atleast > 0]

    # Matching within placebo window
    synth_2_1_later = synth_2_1_combined_1996_regress[
        (synth_2_1_combined_1996_regress.year <= 1996) &
        (synth_2_1_combined_1996_regress.year > 1991)]
    synth_2_1_later = synth_2_1_later[
        (synth_2_1_later.patent_sum_2_1 > 0) |
        (synth_2_1_later.controls == 1)]
    synth_2_1_later = synth_2_1_later[synth_2_1_later.one_pat_atleast > 0]

    synth_2_1_later = synth_2_1_later.copy()
    synth_2_1_later['serious_event'] = \
        synth_2_1_later['L'] + synth_2_1_later['S']
    synth_2_1_later['less_serious_event'] = \
        synth_2_1_later['R'] + synth_2_1_later['H']
    synth_2_1_later['DPM'] = (0.38 * synth_2_1_later['D'] +
                               0.3 * synth_2_1_later['serious_event'] +
                               0.12 * synth_2_1_later['less_serious_event'])
    synth_2_1_later['mean_DPM'] = synth_2_1_later.groupby('PRODUCTCODE')[
        'DPM'].transform(pd.Series.mean)

    treated_list = []
    matched_list = []
    similarity = []
    year_reclass_list = []

    for code in np.unique(
            synth_2_1_later[synth_2_1_later.treatment == 1]['PRODUCTCODE']):
        treated = synth_2_1_later[synth_2_1_later.PRODUCTCODE == code]
        treated = treated.drop_duplicates(subset="PRODUCTCODE")
        control = synth_2_1_later[synth_2_1_later.treatment == 0]
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control.drop_duplicates(subset="PRODUCTCODE")
        yr_reclass = treated.year_reclassified_2_1.values[0]

        sim_distances, sim_indices = get_similar(
            treated['mean_DPM'].values[0],
            control['mean_DPM'].values, topn=1)
        treated_list.append(code)
        matched_list.append(control.iloc[sim_indices]['PRODUCTCODE'])
        similarity.append(sim_distances[sim_indices])
        year_reclass_list.append(yr_reclass)

    matched_pairs_lt = pd.DataFrame({
        'PRODUCTCODE': treated_list, 'treated': treated_list,
        'match': matched_list, 'SSE': similarity,
        'FE': range(len(treated_list)),
        'year_reclassified_controls': year_reclass_list})

    synth_2_1_combined_later_matched = pd.concat([
        synth_2_1_combined_1996_regress[
            synth_2_1_combined_1996_regress.PRODUCTCODE.isin(
                matched_pairs_lt.match)],
        synth_2_1_combined_1996_regress[
            synth_2_1_combined_1996_regress.PRODUCTCODE.isin(
                matched_pairs_lt.treated)]])

    # Note: original code applied times_cited fillna to matched subset only
    # (which wasn't written), so the output retains NaN for times_cited.
    # Only xi_real fillna was applied to the written DataFrame.
    synth_2_1_combined_later_matched['times_cited'] = \
        synth_2_1_combined_later_matched['times_cited'].fillna(0)
    synth_2_1_combined_1996_regress['xi_real'] = \
        synth_2_1_combined_1996_regress['xi_real'].fillna(0)

    synth_2_1_combined_1996_regress = synth_2_1_combined_1996_regress.drop(
        columns=['v_serious', 'FDA_own_accord', 'PART_DESCRIPTION'],
        errors='ignore')
    synth_2_1_combined_1996_regress.to_csv(
        OUT_DERIVED / "later_treated_2_1_oct22_24.csv", index=False)
    print(f"    Wrote later_treated_2_1_oct22_24.csv: "
          f"{len(synth_2_1_combined_1996_regress)} rows")

    # ---- Later-treated 3→2 ----
    print("    Later-treated 3→2...")
    # The control list is reproduced exactly as used for the published estimates. The two
    # adjacent string literals below ('888.307' '880.621') are concatenated by Python into a
    # single entry, so regulation numbers 888.307 and 880.621 are not in the list; the list is
    # kept as is because changing it would change the published sample.
    control_regnums = [
        '870.52', '870.521', '870.41', '870.36', '870.3605', '890.5525',
        '888.307' '880.621', '884.534', '882.594', '882.58', '892.207']

    df_control = main_outcomes[
        (main_outcomes.REGULATIONNUMBER.astype(str).isin(control_regnums)) &
        (main_outcomes.PRODUCTCODE != "DTB")]
    df_control = df_control[df_control.year > 1975]
    df_control = df_control[[
        'FDA_own_accord_3_2', 'PRODUCTCODE', 'year', 'patents_allpats',
        'patents_newfirm', 'patents_newfirmPC', 'times_cited',
        'patents_pats_nodrugs', 'times_cited_outside_ind', 'firm_size',
        'year_reclassified_3_2', 'L', 'H', 'S', 'D', 'xi_real',
        'dev_count', 'firm_count', 'absnew_firm_count']]
    total = pd.concat([df_treated, df_control])
    total['factorized'] = total.PRODUCTCODE.astype('category').cat.codes
    total = total.drop(
        columns=['v_serious', 'FDA_own_accord', 'PART_DESCRIPTION'],
        errors='ignore')
    total.to_csv(OUT_DERIVED / "later_treated_3_2_oct22_24.csv")
    print(f"    Wrote later_treated_3_2_oct22_24.csv: {len(total)} rows")

    # ---- Spillovers 3→2 ----
    print("    Spillovers 3→2...")
    _i32_src = OUT_DERIVED if (OUT_DERIVED / "intuitive_3_2_oct22_24_similarity.csv").exists() else DERIVED
    total_3_2 = pd.read_csv(
        _i32_src / "intuitive_3_2_oct22_24_similarity.csv")
    total_3_2['year_reclassified_controls'] = total_3_2.groupby('Group')[
        'year_reclassified'].transform('max')

    total_spillovers = total_3_2.copy()
    total_spillovers['treatment'] = 0
    total_spillovers.loc[
        total_spillovers.year_reclassified.isnull(), 'treatment'] = 1
    total_spillovers['year_reclassified'] = \
        total_spillovers['year_reclassified_controls']
    total_spillovers = total_spillovers[total_spillovers.treatment == 1]

    pcs_implant = foi[foi.implant == 1]['PRODUCTCODE']
    main_outcomes['v_serious'] = (main_outcomes['D'] + main_outcomes['L'] +
                                   main_outcomes['H'] + main_outcomes['S'])
    total_spillovers['v_serious'] = (total_spillovers['D'] +
                                      total_spillovers['L'] +
                                      total_spillovers['H'] +
                                      total_spillovers['S'])

    treated_list = []
    matched_list = []
    similarity = []
    baseline_devs = []
    year_reclass_list = []
    product_codes_iter = total_spillovers['PRODUCTCODE'].sample(frac=1)

    for number in np.unique(product_codes_iter):
        yr_reclass = total_spillovers[
            total_spillovers.PRODUCTCODE == number]['year_reclassified'].values[0]
        control = main_outcomes.copy()
        control = control[~control.PRODUCTCODE.isin(product_codes_iter)]
        control = control[
            (control.year_reclassified_2_1.isnull()) &
            (control.year_reclassified_3_2.isnull())]
        control = control[~control.PRODUCTCODE.isin(
            total_spillovers[total_spillovers.treatment == 1]['PRODUCTCODE'])]
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control[~control.PRODUCTCODE.isin(
            foi[foi['life_sustaining'] == 1]['PRODUCTCODE'])]
        implant_t = foi[foi.PRODUCTCODE == number]['implant'].values[0]
        if implant_t == 1:
            control = control[control.PRODUCTCODE.isin(pcs_implant)]
        else:
            control = control[~control.PRODUCTCODE.isin(pcs_implant)]

        treated = total_spillovers[total_spillovers.PRODUCTCODE == number].copy()
        treated['event_time'] = treated['year'] - int(float(yr_reclass))
        control = control.copy()
        control['event_time'] = control['year'] - int(float(yr_reclass))

        treated['baseline_sum'] = treated[
            (treated.event_time < 0) &
            (treated.event_time > -6)]['v_serious'].sum()
        baseline_devs.append(treated['baseline_sum'].values[0])

        control = control.groupby(
            ['PRODUCTCODE', 'event_time']).mean(numeric_only=True).reset_index()
        control_meaned = control[
            (control.event_time < 0) &
            (control.event_time > -6)].groupby(
            'PRODUCTCODE').mean(numeric_only=True).reset_index()

        # The treated pre-period mean below is computed with the mask `control.event_time > -6`,
        # which pandas aligns on the index of `treated`; this is the selection the published
        # estimates use and it is kept as is because changing it would change the matched sample.
        treated_meaned = treated[
            (treated.event_time < 0) &
            (control.event_time > -6)].mean(numeric_only=True)
        sim_distances, sim_indices = get_similar(
            treated_meaned[['dev_count']].values,
            control_meaned[['dev_count']].values, topn=1)
        treated_list.append(number)
        matched_list.append(control_meaned.iloc[sim_indices]['PRODUCTCODE'])
        similarity.append(sim_distances[sim_indices])
        year_reclass_list.append(yr_reclass)

    matched_pairs_sp32 = pd.DataFrame({
        'PRODUCTCODE': treated_list, 'treated': treated_list,
        'match': matched_list, 'SSE': similarity,
        'baseline_serious': baseline_devs,
        'FE': range(len(treated_list)),
        'year_reclassified_controls': year_reclass_list})
    matched_pairs_sp32 = matched_pairs_sp32[
        matched_pairs_sp32['match'] != "None"]

    final_spillovers = main_outcomes[
        (main_outcomes.PRODUCTCODE.isin(matched_pairs_sp32.treated)) |
        (main_outcomes.PRODUCTCODE.isin(matched_pairs_sp32.match))]
    final_spillovers = final_spillovers.copy()
    final_spillovers['treatment'] = 0
    final_spillovers.loc[
        final_spillovers.PRODUCTCODE.isin(
            matched_pairs_sp32.treated), 'treatment'] = 1
    matched_pairs_sp32['year_reclassified'] = \
        matched_pairs_sp32['year_reclassified_controls']
    final_spillovers = pd.merge(
        final_spillovers,
        matched_pairs_sp32[['PRODUCTCODE', 'year_reclassified']],
        on='PRODUCTCODE', how='left')
    final_spillovers['factorized'] = \
        final_spillovers.PRODUCTCODE.astype('category').cat.codes
    final_spillovers['posttreat'] = 0
    final_spillovers.loc[
        (final_spillovers.treatment == 1) &
        (final_spillovers.year >= final_spillovers.year_reclassified),
        'posttreat'] = 1

    final_spillovers = final_spillovers.drop(
        columns=['PRODUCTCODE_COUNT'], errors='ignore')
    final_spillovers.to_csv(
        OUT_DERIVED / "intuitive_spillovers_3_2_oct22_24.csv", index=False)
    print(f"    Wrote intuitive_spillovers_3_2_oct22_24.csv: "
          f"{len(final_spillovers)} rows")

    # ---- Spillovers 2→1 ----
    print("    Spillovers 2→1...")
    _i21_src = OUT_DERIVED if (OUT_DERIVED / "intuitive_2_1_oct22_24.csv").exists() else DERIVED
    final_intuitive = pd.read_csv(
        _i21_src / "intuitive_2_1_oct22_24.csv")
    matched_pairs_21 = pd.read_csv(
        _i21_src / "matched_pairs_intuitive_2_1.csv")
    matched_pairs_21['PRODUCTCODE'] = matched_pairs_21['match']
    matched_pairs_21['year_reclassified_2_1'] = \
        matched_pairs_21['year_reclassified']

    spillover_treated = final_intuitive[
        final_intuitive.treatment == 0].copy()
    spillover_treated.drop(columns='year_reclassified_2_1',
                           inplace=True, errors='ignore')
    spillover_treated['treatment'] = 1
    spillover_treated = pd.merge(
        spillover_treated,
        matched_pairs_21[['PRODUCTCODE', 'year_reclassified_2_1']],
        on='PRODUCTCODE', how='left')

    # Reload FOI
    foi = pd.read_csv(RAW / config.GEN_RAW_FILES["foiclass"],
                       encoding='latin-1', on_bad_lines='skip', sep="|")
    foi['implant'] = 0
    foi.loc[foi.Implant_Flag == 'Y', 'implant'] = 1
    foi['life_sustaining'] = 0
    foi.loc[foi.Life_Sustain_support_flag == 'Y', 'life_sustaining'] = 1
    pcs_implant = foi[foi.implant == 1]['PRODUCTCODE']

    treated_list = []
    matched_list = []
    similarity = []
    baseline_devs = []
    year_reclass_list = []

    product_codes_iter = spillover_treated.drop_duplicates("PRODUCTCODE")[
        'PRODUCTCODE'].sample(frac=1)
    latest_3_2_all_select = main_outcomes.copy()
    latest_3_2_all_select['v_serious'] = (
        latest_3_2_all_select['D'] + latest_3_2_all_select['L'] +
        latest_3_2_all_select['H'] + latest_3_2_all_select['S'])
    spillover_treated['v_serious'] = (
        spillover_treated['D'] + spillover_treated['L'] +
        spillover_treated['H'] + spillover_treated['S'])
    latest_3_2_all_select['REGULATIONNUMBER'] = \
        latest_3_2_all_select['REGULATIONNUMBER'].astype(float)
    spillover_treated['REGULATIONNUMBER'] = \
        spillover_treated['REGULATIONNUMBER'].astype(float)

    for number in np.unique(product_codes_iter):
        PART_DESC = spillover_treated[
            spillover_treated.PRODUCTCODE == number][
            'PART_DESCRIPTION'].values[0]
        yr_reclass = spillover_treated[
            spillover_treated.PRODUCTCODE == number][
            'year_reclassified_2_1'].values[0]

        control = latest_3_2_all_select[
            (latest_3_2_all_select.year_reclassified_2_1.isnull()) &
            (latest_3_2_all_select.year_reclassified_3_2.isnull())]
        control = control[~control.PRODUCTCODE.isin(product_codes_iter)]
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control[~control.PRODUCTCODE.isin(
            foi[foi['life_sustaining'] == 1]['PRODUCTCODE'])]
        implant_t = foi[foi.PRODUCTCODE == number]['implant'].values[0]
        if implant_t == 1:
            control = control[control.PRODUCTCODE.isin(pcs_implant)]
        else:
            control = control[~control.PRODUCTCODE.isin(pcs_implant)]

        treated = spillover_treated[
            spillover_treated.PRODUCTCODE == number].copy()
        treated['event_time'] = treated['year'] - int(float(yr_reclass))
        control = control.copy()
        control['event_time'] = control['year'] - int(float(yr_reclass))

        treated['baseline_sum'] = treated[
            (treated.event_time < 0) &
            (treated.event_time > -6)]['v_serious'].sum()
        baseline_devs.append(treated['baseline_sum'].values[0])

        control = control.groupby(
            ['PRODUCTCODE', 'event_time']).mean(
            numeric_only=True).reset_index()
        control_meaned = control[control.event_time < 0].groupby(
            'PRODUCTCODE').mean(numeric_only=True).reset_index()

        treated_meaned = treated[
            treated.event_time < 0].mean(numeric_only=True)
        try:
            sim_distances, sim_indices = get_similar(
                treated_meaned[['patents_allpats']].values,
                control_meaned[['patents_allpats']].values, topn=1)
            treated_list.append(number)
            matched_list.append(
                control_meaned.iloc[sim_indices]['PRODUCTCODE'])
            similarity.append(sim_distances[sim_indices])
            year_reclass_list.append(yr_reclass)
        except Exception:
            treated_list.append(number)
            matched_list.append("None")
            similarity.append(0)
            year_reclass_list.append(yr_reclass)

    matched_pairs_sp21 = pd.DataFrame({
        'PRODUCTCODE': treated_list, 'treated': treated_list,
        'match': matched_list, 'SSE': similarity,
        'baseline_serious': baseline_devs,
        'FE': range(len(treated_list)),
        'year_reclassified_controls': year_reclass_list})
    matched_pairs_sp21 = matched_pairs_sp21[
        matched_pairs_sp21['match'] != "None"]

    final = latest_3_2_all_select[
        (latest_3_2_all_select.PRODUCTCODE.isin(
            matched_pairs_sp21.treated)) |
        (latest_3_2_all_select.PRODUCTCODE.isin(
            matched_pairs_sp21.match))]
    final = final.copy()
    final['treatment'] = 0
    final.loc[final.PRODUCTCODE.isin(
        matched_pairs_sp21.treated), 'treatment'] = 1
    matched_pairs_sp21['year_reclassified'] = \
        matched_pairs_sp21['year_reclassified_controls']
    final = pd.merge(
        final,
        matched_pairs_sp21[['PRODUCTCODE', 'year_reclassified']],
        on='PRODUCTCODE', how='left')
    final['factorized'] = final.PRODUCTCODE.astype('category').cat.codes
    final['posttreat'] = 0
    final.loc[(final.treatment == 1) &
              (final.year >= final.year_reclassified), 'posttreat'] = 1

    final = final.drop(columns=['PRODUCTCODE_COUNT'], errors='ignore')
    final.to_csv(OUT_DERIVED / "spillovers_2_1_oct22_24.csv", index=False)
    print(f"    Wrote spillovers_2_1_oct22_24.csv: {len(final)} rows")


# ============================================================================
# Main entry point
# ============================================================================
def run(staging=False):
    global OUT_RAW, OUT_DERIVED

    if staging:
        OUT_RAW = RAW / "_generated"
        OUT_DERIVED = DERIVED / "_generated"
        OUT_RAW.mkdir(parents=True, exist_ok=True)
        OUT_DERIVED.mkdir(parents=True, exist_ok=True)
        print("STAGING MODE: writing to _generated/ subdirectories")
        print(f"  OUT_RAW:     {OUT_RAW}")
        print(f"  OUT_DERIVED: {OUT_DERIVED}")
    else:
        OUT_RAW = RAW
        OUT_DERIVED = DERIVED

    print("=" * 70)
    print("gen_01_main_panels.py")
    print("=" * 70)
    print()

    # Safety: abort if any output path is a symlink
    _check_no_symlinks([
        OUT_DERIVED / "Applicant_Device_data.csv",
        OUT_DERIVED / "Full_sample.csv",
        OUT_DERIVED / "all_patents_w_xi_oct22_24.csv",
        OUT_DERIVED / "safety_vars_allpats.csv",
        OUT_DERIVED / "adverse_event_panel_by_PC_full.csv",
        OUT_DERIVED / "intuitive_2_1_oct22_24.csv",
        OUT_DERIVED / "intuitive_3_2_oct22_24_similarity.csv",
        OUT_DERIVED / "later_treated_2_1_oct22_24.csv",
        OUT_DERIVED / "later_treated_3_2_oct22_24.csv",
        OUT_DERIVED / "intuitive_spillovers_3_2_oct22_24.csv",
        OUT_DERIVED / "spillovers_2_1_oct22_24.csv",
        OUT_RAW / "unique_firms_thr_75.csv",
        OUT_RAW / "unique_firms_in_PC_thr_75.csv",
        OUT_RAW / "unique_devices_thr_75.csv",
    ])

    # Phase 1: Load synth_number
    synth_number = phase_01_load_synth()

    # Phase 2a: compile the 510(k)+PMA submission table gen_03/gen_03b read.
    # Runs before phase 2's skip-if-exists branch, so it is produced on every route.
    phase_02a_applicant_device_data()

    # Phase 2: Fuzzy dedup
    phase_02_fuzzy_dedup()

    # Phase 3: Main outcomes skeleton
    main_outcomes = phase_03_main_outcomes_skeleton(synth_number)

    # Phase 4: Patent processing
    main_outcomes, all_pats_wGRID = phase_04_patents(main_outcomes)

    # Phase 5: Citations
    main_outcomes = phase_05_citations(main_outcomes)

    # Phase 6: Patent values
    main_outcomes = phase_06_patent_values(main_outcomes, all_pats_wGRID)

    # Phase 7: Adverse events
    main_outcomes = phase_07_adverse_events(main_outcomes)

    # Phase 8: Safety keywords
    phase_08_safety_keywords()

    # Phase 9: Treatment indicators + Full_sample
    main_outcomes, synth_no_reclass_PCs = phase_09_treatment_indicators(
        main_outcomes)

    # Phase 10: Intuitive matching
    main_outcomes, foi, df_treated = phase_10_intuitive_matching(
        main_outcomes)

    # Phase 11: Later-treated + Spillovers
    phase_11_later_treated_spillovers(main_outcomes, foi, df_treated)

    print()
    print("gen_01_main_panels.py complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate main panel datasets")
    parser.add_argument("--staging", action="store_true",
                        help="Write outputs to _generated/ subdirectories "
                             "instead of overwriting reference files")
    args = parser.parse_args()
    run(staging=args.staging)
