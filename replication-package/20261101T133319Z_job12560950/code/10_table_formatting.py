#!/usr/bin/env python3
"""
10_table_formatting.py — Format LaTeX row-fragment .tex files from estimate CSVs.

Reads estimate CSVs produced by 03a, 03b, 05, 06a, and 07, computes
pre-treatment means/SDs from the matched sample data, and assembles
row-fragment .tex files that the paper's LaTeX source \\input{}s inside
its own table environments.

Each output file contains only the body rows — no \begin{table},
no \toprule/\bottomrule. The paper's .tex wraps them with its own
headers, column specs, and notes.

Source: Replication_analysis.py formatting blocks (lines 2740-3600).

Inputs:
    output/tables/Paper*_Estimates_*.csv  (all estimate CSVs)
    data/derived/ (matched sample CSVs for pre-treatment means)

Outputs:
    output/tables/Formatted/
        PaperRegTable{reclass}_{panel}_{logged}[_suffix]_oct22_24.tex
        (and DIDimpute_ prefixed variants, spillover variants, etc.)

Filename convention matches the paper's \\input{} references exactly:
    Table 2 (innovation):
        PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex
        PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex
    Table 3 (adverse events):
        PaperRegTable3_2_AdverseEvent_NoLog_oct22_24.tex
        PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex
    Table 4 (market composition):
        PaperRegTable3_2_MarketComposition_NoLog_oct22_24.tex
        PaperRegTable2_1_MarketComposition_NoLog_oct22_24.tex
    Robustness (nozero):
        PaperRegTable3_2_Main_Panel_NoLog_No0_oct22_24.tex  etc.
    Robustness (BJS imputation):
        DIDimpute_PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex  etc.
    Robustness (poisson):
        PaperRegTable3_2_Main_Panel_NoLog_poisson_oct22_24.tex  etc.
    Robustness (log):
        PaperRegTable3_2_Main_Panel_Log_oct22_24.tex  etc.
    Spillovers:
        PaperRegTableSpillovers_3_2_Spillovers_NoLog.tex
        PaperRegTableSpillovers_2_1_Spillovers_NoLog.tex
"""

import sys
import logging
import time
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from table_format import (
    compute_se, compute_se_series, significance_stars,
    format_estimate_cell, format_table_row, assemble_row_fragment,
)

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "10_table_formatting.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Output directory for formatted .tex fragments
# ============================================================================
FORMATTED_DIR = config.TABLES_DIR / "Formatted"

# ============================================================================
# Panel description mapping: outcome_type -> panel_desc used in filenames
# ============================================================================
PANEL_DESC = {
    "MainPanel": "Main_Panel",
    "AdverseEvent": "AdverseEvent",
    "MarketComposition": "MarketComposition",
    "Spillovers": "Spillovers",
}

# ============================================================================
# Table specifications to generate
# ============================================================================
# Each entry: (outcome_type, spec_name, reclass_types, sample_mode)
#   sample_mode: "Both"       = columns for Matched/Intuitive/Later
#                "MatchedOnly" = single Matched column (spillovers)

TABLE_SPECS = []

# --- Main tables (Tables 2-4): baseline spec, all three outcome types ---
for otype in ["MainPanel", "AdverseEvent", "MarketComposition"]:
    TABLE_SPECS.append({
        "outcome_type": otype,
        "spec_name": "baseline",
        "reclass_types": ["3_2", "2_1"],
        "sample_mode": "Both",
    })

# --- Robustness: nozero (Table D.7) ---
for otype in ["MainPanel", "AdverseEvent", "MarketComposition"]:
    TABLE_SPECS.append({
        "outcome_type": otype,
        "spec_name": "nozero",
        "reclass_types": ["3_2", "2_1"],
        "sample_mode": "Both",
    })

# --- Robustness: BJS imputation (Table D.3) ---
for otype in ["MainPanel", "AdverseEvent", "MarketComposition"]:
    TABLE_SPECS.append({
        "outcome_type": otype,
        "spec_name": "did_impute",
        "reclass_types": ["3_2", "2_1"],
        "sample_mode": "Both",
    })

# --- Robustness: poisson (Table D.4) ---
for otype in ["MainPanel", "AdverseEvent", "MarketComposition"]:
    TABLE_SPECS.append({
        "outcome_type": otype,
        "spec_name": "poisson",
        "reclass_types": ["3_2", "2_1"],
        "sample_mode": "Both",
    })

# --- Robustness: log (Table D.2) ---
for otype in ["MainPanel", "AdverseEvent", "MarketComposition"]:
    TABLE_SPECS.append({
        "outcome_type": otype,
        "spec_name": "log",
        "reclass_types": ["3_2", "2_1"],
        "sample_mode": "Both",
    })

# --- Spillovers (Table 5): baseline, matched only ---
TABLE_SPECS.append({
    "outcome_type": "Spillovers",
    "spec_name": "baseline",
    "reclass_types": ["3_2", "2_1"],
    "sample_mode": "MatchedOnly",
})


# ============================================================================
# Helpers
# ============================================================================

def find_spec_by_name(spec_name):
    """Find the spec variant dict from config by name."""
    for spec in config.SPEC_VARIANTS:
        if spec["name"] == spec_name:
            return spec
    raise ValueError(f"Spec '{spec_name}' not found in config.SPEC_VARIANTS")


def load_estimate_csv(outcome_type, reclass_type, spec, sample_name):
    """
    Load an estimate CSV for a specific sample.
    Returns DataFrame or None if file not found.
    """
    path = config.estimate_csv_path(
        outcome_type, reclass_type, spec["logged"], sample_name,
        nozero=spec["nozero"],
        df_imput=spec["df_imput"],
        nodrugs_A61=spec["nodrugs_A61"],
        poisson=spec["poisson"],
    )
    if path.exists():
        return pd.read_csv(path)
    logging.warning(f"  Estimate CSV not found: {path}")
    return None


def _derive_variables(df):
    """
    Compute derived variables that the estimation scripts create from raw data.

    These are needed for computing pre-treatment means on columns that
    don't exist in the raw CSVs but are derived during estimation.
    """
    # real_pats = patents_allpats
    if "real_pats" not in df.columns and "patents_allpats" in df.columns:
        df["real_pats"] = df["patents_allpats"]
    # unique_firms = patents_newfirm
    if "unique_firms" not in df.columns and "patents_newfirm" in df.columns:
        df["unique_firms"] = df["patents_newfirm"]
    # unique_firmsPC = patents_newfirmPC
    if "unique_firmsPC" not in df.columns and "patents_newfirmPC" in df.columns:
        df["unique_firmsPC"] = df["patents_newfirmPC"]
    # xi_real_2019 = xi_real / CPI deflator
    if "xi_real_2019" not in df.columns and "xi_real" in df.columns:
        df["xi_real"] = df["xi_real"].fillna(0)
        df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019
    # firm_expansion = firm_count - absnew_firm_count
    if "firm_expansion" not in df.columns:
        if "firm_count" in df.columns and "absnew_firm_count" in df.columns:
            df["firm_count"] = df["firm_count"].fillna(0)
            df["absnew_firm_count"] = df["absnew_firm_count"].fillna(0)
            df["firm_expansion"] = df["firm_count"] - df["absnew_firm_count"]
    # firm_expansion_patents = unique_firmsPC - unique_firms
    if "firm_expansion_patents" not in df.columns:
        if "unique_firmsPC" in df.columns and "unique_firms" in df.columns:
            df["firm_expansion_patents"] = df["unique_firmsPC"] - df["unique_firms"]
    # dev_count fillna
    if "dev_count" in df.columns:
        df["dev_count"] = df["dev_count"].fillna(0)
    # times_cited fillna
    if "times_cited" in df.columns:
        df["times_cited"] = df["times_cited"].fillna(0)

    return df


def load_sample_data(reclass_type, outcome_type):
    """
    Load the matched sample data for computing pre-treatment means.

    For MainPanel/MarketComposition: use the _onepat_innovation matched sample.
    For AdverseEvent: use the _onepat matched sample.
    For Spillovers: use the spillovers source file.

    Returns a DataFrame with derived variables, or None.
    """
    if outcome_type == "Spillovers":
        # Spillovers use the spillover source data for pre-treatment means
        if reclass_type == "3_2":
            key = "intuitive_spillovers_3_2"
        else:
            key = "spillovers_2_1"
        path = config.DERIVED_DATA_DIR / config.SOURCE_FILES.get(key, "")
        if not path.exists():
            raise FileNotFoundError(
                f"Spillover sample not found: {path}. Without it the pre-treatment means "
                "of the spillover tables would be blank. Run the estimation steps first.")
        return _derive_variables(pd.read_csv(path))

    if reclass_type == "3_2":
        if outcome_type in ("MainPanel", "MarketComposition"):
            key = "3_2_onepat_innovation"
        else:
            key = "3_2_onepat"
    else:
        if outcome_type in ("MainPanel", "MarketComposition"):
            key = "2_1_onepat_innovation"
        else:
            key = "2_1_onepat"

    path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[key]
    if not path.exists():
        # Fails closed: without the matched sample the pre-treatment statistics cannot be
        # computed and the formatted table would carry blank pre-mean rows.
        raise FileNotFoundError(
            f"Matched sample not found: {path}. Run step 9 (02_match_samples.py) first.")
    return _derive_variables(pd.read_csv(path))


def compute_pre_treatment_stats(sample_df, outcome_vars, reclass_type=None):
    """
    Compute pre-treatment mean and std for treated units in event-time [-5, -1].

    Follows the original code:
        firms[(treatment == 1) & (event_time < 0) & (event_time > -6)]

    Returns dict: outcome_var -> (mean, std)
    """
    if sample_df is None:
        return {}

    df = sample_df.copy()

    # Derive treatment column if absent
    if "treatment" not in df.columns:
        yr_col = None
        if "year_reclassified" in df.columns:
            yr_col = "year_reclassified"
        elif reclass_type and f"year_reclassified_{reclass_type}" in df.columns:
            yr_col = f"year_reclassified_{reclass_type}"
        elif "year_reclassified_3_2" in df.columns:
            yr_col = "year_reclassified_3_2"
        elif "year_reclassified_2_1" in df.columns:
            yr_col = "year_reclassified_2_1"
        if yr_col is not None:
            df["treatment"] = 0
            df.loc[df[yr_col].notnull(), "treatment"] = 1
        else:
            return {}

    # Compute event_time
    if "event_time" not in df.columns:
        if "year_reclassified" in df.columns:
            df["event_time"] = df["year"] - df["year_reclassified"]
        elif reclass_type and f"year_reclassified_{reclass_type}" in df.columns:
            df["event_time"] = df["year"] - df[f"year_reclassified_{reclass_type}"]
        elif "year_reclassified_3_2" in df.columns:
            df["event_time"] = df["year"] - df["year_reclassified_3_2"]
        elif "year_reclassified_2_1" in df.columns:
            df["event_time"] = df["year"] - df["year_reclassified_2_1"]
        else:
            return {}

    # Filter to treated units in pre-treatment window [-5, -1]
    mask = (df["treatment"] == 1) & (df["event_time"] < 0) & (df["event_time"] > -6)
    pre_df = df.loc[mask]

    stats = {}
    for var in outcome_vars:
        if var in pre_df.columns:
            stats[var] = (pre_df[var].mean(), pre_df[var].std())
        else:
            stats[var] = (np.nan, np.nan)

    return stats


def build_output_filename(outcome_type, reclass_type, spec):
    """
    Build the output .tex filename matching the paper's \\input{} references.

    Pattern (from the original Replication_analysis.py):
        [DIDimpute_]PaperRegTable[Spillovers_]{reclass}_{panel_desc}_{logged}[_suffix]_oct22_24.tex

    Spillovers use a different pattern:
        PaperRegTableSpillovers_{reclass}_Spillovers_NoLog.tex
        (no _oct22_24 suffix)
    """
    panel_desc = PANEL_DESC[outcome_type]
    logged_type = spec["logged"]

    prefix = ""
    if spec["df_imput"]:
        prefix = "DIDimpute_"

    # Spillovers have a different naming convention
    if outcome_type == "Spillovers":
        return f"{prefix}PaperRegTableSpillovers_{reclass_type}_{panel_desc}_{logged_type}.tex"

    suffix = ""
    if spec["nozero"]:
        suffix = "_No0"
    elif spec["nodrugs_A61"]:
        suffix = "_NoDrugs_A61"
    elif spec["poisson"]:
        suffix = "_poisson"
    # logged is already part of logged_type ("Log" vs "NoLog")

    return f"{prefix}PaperRegTable{reclass_type}_{panel_desc}_{logged_type}{suffix}_oct22_24.tex"


def format_one_fragment(outcome_type, reclass_type, spec, sample_mode):
    """
    Format a single row-fragment .tex file.

    For sample_mode == "Both": columns are [Pre-mean, Matched, Intuitive, Later]
    For sample_mode == "MatchedOnly": columns are [Pre-mean, Matched]

    For MarketComposition: an extra "- &" column is inserted for the price column
    that appears in the paper but is produced by a separate script.

    Returns (tex_string, filename) or (None, filename) if no data.
    """
    rename_dict = config.get_outcome_dict(
        outcome_type, reclass_type, nodrugs_A61=spec["nodrugs_A61"]
    )
    outcome_vars = list(rename_dict.keys())

    is_market_comp = outcome_type == "MarketComposition"

    # Determine which samples to include
    if sample_mode == "Both":
        sample_list = ["Matched", "Intuitive", "Later"]
    else:
        sample_list = ["Matched"]

    # Load estimate CSVs for each sample
    estimate_dfs = {}
    for sample_name in sample_list:
        df_est = load_estimate_csv(outcome_type, reclass_type, spec, sample_name)
        if df_est is not None:
            # Compute SE
            df_est["SE"] = 0.0
            pos = df_est["Estimate"] > 0
            neg = df_est["Estimate"] < 0
            df_est.loc[pos, "SE"] = (
                df_est.loc[pos, "Estimate"] - df_est.loc[pos, "lower_CI"]
            ) / 1.96
            # Fix negative SE
            bad_se = df_est["SE"] < 0
            df_est.loc[bad_se, "SE"] = df_est.loc[bad_se, "Estimate"] * 1.96 * 2
            df_est.loc[neg, "SE"] = np.abs(
                df_est.loc[neg, "Estimate"] - df_est.loc[neg, "upper_CI"]
            ) / 1.96
            # Stars
            df_est["tstat"] = np.abs(df_est["Estimate"] / df_est["SE"].replace(0, np.nan))
            df_est["stars"] = ""
            df_est.loc[df_est["tstat"] > 1.6449, "stars"] = "+"
            df_est.loc[df_est["tstat"] > 1.9600, "stars"] = "*"
            df_est.loc[df_est["tstat"] > 2.5758, "stars"] = "**"
            df_est.loc[df_est["tstat"] > 3.2905, "stars"] = "***"

            estimate_dfs[sample_name] = df_est

    if not estimate_dfs:
        return None, build_output_filename(outcome_type, reclass_type, spec)

    # Load sample data for pre-treatment stats (from Matched sample)
    sample_df = load_sample_data(reclass_type, outcome_type)
    pre_stats = compute_pre_treatment_stats(sample_df, outcome_vars, reclass_type=reclass_type)

    # Get sample sizes from estimate CSVs (minimum N across outcomes)
    sample_sizes = []
    for sample_name in sample_list:
        if sample_name in estimate_dfs:
            df_est = estimate_dfs[sample_name]
            if "Sample Size" in df_est.columns:
                sample_sizes.append(int(df_est["Sample Size"].min()))
            else:
                sample_sizes.append(0)
        else:
            sample_sizes.append(0)

    # Build rows
    rows = []
    for var in outcome_vars:
        label = rename_dict[var]
        pre_mean, pre_std = pre_stats.get(var, (np.nan, np.nan))

        estimates = []
        ses = []

        if is_market_comp:
            # Insert placeholder "- &" for the price column (All CPTs)
            estimates.append("-")
            ses.append("-")

        for sample_name in sample_list:
            if sample_name in estimate_dfs:
                df_est = estimate_dfs[sample_name]
                row_data = df_est[df_est.outcome == var]
                if len(row_data) > 0:
                    est_val = row_data.iloc[0]["Estimate"]
                    se_val = row_data.iloc[0]["SE"]
                    stars_val = row_data.iloc[0]["stars"]
                    estimates.append((est_val, stars_val))
                    ses.append(se_val)
                else:
                    estimates.append(None)
                    ses.append(None)
            else:
                estimates.append(None)
                ses.append(None)

        # Build the estimate row string
        est_cells = [f"\\hspace{{6mm}}{label}"]
        se_cells = [""]

        # Pre-mean
        if not np.isnan(pre_mean):
            est_cells.append(f"{round(pre_mean, 2):.2f}")
        else:
            est_cells.append("")
        # Pre-std
        if not np.isnan(pre_std):
            se_cells.append(f"({round(pre_std, 2):.2f})")
        else:
            se_cells.append("")

        for est_item, se_item in zip(estimates, ses):
            if est_item == "-":
                est_cells.append("-")
                se_cells.append("-")
            elif est_item is not None:
                est_val, stars_val = est_item
                est_cells.append(f"{round(est_val, 2):.2f}{stars_val}")
                se_cells.append(f"({round(se_item, 2):.2f})")
            else:
                est_cells.append("")
                se_cells.append("")

        est_row = " & ".join(est_cells) + " \\\\ "
        se_row = " & ".join(se_cells) + " \\\\ "

        # Match original code formatting (Replication_analysis.py L3086-3162):
        # 1. After dash placeholder: no space between & and next value
        est_row = est_row.replace("- & ", "- &")
        se_row = se_row.replace("- & ", "- &")
        # 2. SE row pre-treatment std: no space between & and (
        se_row = se_row.replace(" & (", " &(", 1)

        rows.append((est_row, se_row))

    # Build fragment
    tex_str = assemble_row_fragment(
        rows,
        sample_sizes=sample_sizes,
        has_price_column=is_market_comp,
    )

    filename = build_output_filename(outcome_type, reclass_type, spec)
    return tex_str, filename


def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FORMATTED_DIR.mkdir(parents=True, exist_ok=True)

    t_start = time.time()

    n_formatted = 0
    skipped = []

    for table_spec in TABLE_SPECS:
        outcome_type = table_spec["outcome_type"]
        spec_name = table_spec["spec_name"]
        sample_mode = table_spec["sample_mode"]
        spec = find_spec_by_name(spec_name)

        for reclass_type in table_spec["reclass_types"]:
            tex_str, filename = format_one_fragment(
                outcome_type, reclass_type, spec, sample_mode
            )

            if tex_str is not None:
                outpath = FORMATTED_DIR / filename
                with open(outpath, "w") as f:
                    f.write(tex_str)
                logging.info(f"  Saved: {outpath.name}")
                n_formatted += 1
            else:
                logging.error(
                    f"  No estimates found for {filename}: the table was NOT written"
                )
                skipped.append(filename)

    elapsed = time.time() - t_start
    logging.info(
        f"Table formatting complete: {n_formatted} files written, "
        f"{len(skipped)} skipped, in {elapsed:.1f}s."
    )
    # FAIL-CLOSED: every entry of TABLE_SPECS is a manuscript table. A skipped one means
    # its estimate CSVs are missing, i.e. an earlier estimation step did not produce what
    # this step formats -- the run must not report success with the exhibit missing.
    if skipped:
        logging.error(
            "FATAL: %d manuscript table(s) not formatted (missing estimate CSVs from the "
            "estimation steps): %s", len(skipped), ", ".join(skipped))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
