#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
05_price_analysis.py -- Price and utilization analysis (MarketScan claims data).

Reads censored outpatient and inpatient claims data, constructs price and
utilization panels by product code, then estimates:
  - Static DiD for price (BilledAmt) and utilization (proc_count)
  - Conley-Taber event study for price (Figure 3c)

The price event study uses Conley-Taber stacked DiD. Utilization estimates
are reported in a compact appendix table (tab:Utilization) rather than as
event study figures.

IMPORTANT: The underlying MarketScan data are proprietary. If the input files
are not present, this script logs a warning and exits gracefully so that the
rest of the replication pipeline continues without error.

Source: Price_data_and_analysis.py (2409 lines).

Inputs:
    data/derived/outpatient_combined_censored.csv
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_3_2_onepat.csv
    data/derived/matched_sample_2_1_onepat_innovation.csv
    data/derived/matched_sample_3_2_onepat_innovation.csv

Outputs:
    output/figures/3_2_nolog_Price_solo_CTs_sept20_25.png
    output/figures/2_1_nolog_Price_solo_CTs_sept20_25.png
    output/tables/price_utilization_estimates.csv
    output/tables/price_sample_construction.csv
    output/tables/Formatted/RegTable_Prices_3_2_sep25.tex
    output/tables/Formatted/RegTable_Prices_2_1_sep25.tex
    output/tables/Formatted/DIDimpute_RegTable_Prices_3_2_sep25.tex
    output/tables/Formatted/DIDimpute_RegTable_Prices_2_1_sep25.tex
    output/tables/Formatted/RegTable_Utilization_3_2_sep25.tex
    output/tables/Formatted/RegTable_Utilization_2_1_sep25.tex
    output/tables/Formatted/DIDimpute_RegTable_Utilization_3_2_sep25.tex
    output/tables/Formatted/DIDimpute_RegTable_Utilization_2_1_sep25.tex
"""

import sys
import logging
import time
import os
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked, conley_taber_stacked_es
import conley_taber as _conley_taber_module
from estimation import run_did_imputation, run_feols_es_2to1, source_r_scripts
from plotting import (
    create_figure, plot_event_study, save_figure, setup_event_study_axes,
)
from table_format import compute_se, significance_stars

np.random.seed(config.RANDOM_SEED)

# Conley-Taber event-study periods that failed. The per-period loop in
# run_price_event_study_ct() records a failed period here; a dropped period would leave a
# hole in the event-time grid of Figure 3c and ES_coefs_price_<reclass>.csv, so the
# end-of-step guard (_verify_price_exhibits) refuses to report success while any is recorded.
_CT_ES_FAILURES = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "05_price_analysis.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# File paths for proprietary MarketScan data
# ============================================================================
# Outpatient claims only: the price and utilization analysis uses outpatient claims, so the
# outpatient extract is the single MarketScan input.
OUTPATIENT_FILE = config.DERIVED_DATA_DIR / "outpatient_combined_censored.csv"

# GPT price links (PRODUCTCODE -> HCPCS crosswalk)
GPT_LINKS_2_1 = config.RAW_DATA_DIR / "2_1_GPT_Price_Links.csv"
GPT_LINKS_3_2 = config.RAW_DATA_DIR / "3_2_GPT_Price_Links.csv"

# Human-expert device-type-to-procedure concordance (two AAPC-certified coders
# with third-coder reconciliation). This is the alternative concordance the price
# footnote reports robustness to; see load_expert_hcpcs_crosswalk().
EXPERT_LINKS = config.RAW_DATA_DIR / "FDA_HCPCS_Xwalk_Moazzam.csv"

# ============================================================================
# Price / utilization outcome columns
# BilledAmt is the primary price outcome (average billed amount per procedure).
# The original analysis uses BilledAmt throughout; PaidAmt is constructed
# identically in the source data but BilledAmt is the reported outcome.
# ============================================================================
PRICE_OUTCOME = "BilledAmt"
UTILIZATION_OUTCOME = "q"
LOG_UTILIZATION_OUTCOME = "log_q"

OUTCOME_LABELS = {
    "BilledAmt": "Average Price",
    "q": "Procedure Count (Utilization)",
    "log_q": "Log Procedure Count (Utilization)",
}

# ============================================================================
# Event study window sizes — match the original analysis exactly.
#
# Price event study (BJS imputation):
#   III->II: symmetric [-10, +10]
#   II->I:   asymmetric [-2, +15]  (note: wider than utilization)
#
# Utilization event study (Conley-Taber stacked):
#   III->II: symmetric [-10, +10]
#   II->I:   asymmetric [-2, +10]
# ============================================================================
PRICE_WINDOWS = {
    "3_2": {"low": 10, "high": 10},
    "2_1": {"low": 2, "high": 10},
}
UTILIZATION_WINDOWS = {
    "3_2": {"low": 10, "high": 10},
    "2_1": {"low": 2, "high": 10},
}


# Opt-out for a replicator who runs neither official route and therefore has no claims
# extract at all. It is the same switch 09_summary_stats.py uses for Table 1 Panel III,
# so one variable covers every MarketScan-dependent step.
SKIP_MARKETSCAN_ENV = "FDA_SKIP_MARKETSCAN_PANEL"


def _missing_claims_inputs():
    """Return the claims-extract inputs that are absent (empty list when the extract is present)."""
    return [p for p in (OUTPATIENT_FILE,) if not p.exists()]


def load_claims_data():
    """
    Load outpatient claims data and prepare it.

    Following the original Price_data_and_analysis.py, the analysis uses outpatient only
    (the inpatient merge was overridden with `merged_df = outpatient_claims_extract.copy()`).

    Returns a claims DataFrame with proc1/HCPCS, year, pay, proc_count, BilledAmt.
    """
    logging.info("Loading outpatient claims data...")
    df = pd.read_csv(OUTPATIENT_FILE)
    logging.info(f"  Outpatient: {len(df):,} rows")

    # Compute BilledAmt (average price per procedure)
    df["BilledAmt"] = df["pay"] / df["proc_count"]
    df["PaidAmt"] = df["BilledAmt"]
    df["ProcCode"] = df["proc1"].astype(str).str.strip()
    df["HCPCS"] = df["ProcCode"]

    # CPT code update for retired procedure code.
    # CPT 52336 (cystourethroscopy with ureteroscopy) was retired and replaced
    # by CPT 52352 prior to 2001. Remap pre-2001 claims to the successor code
    # and drop all 52336 entries (post-2001 claims under 52336 are erroneous).
    mask_rename = (df["proc1"].astype(str).str.strip() == "52336") & (df["year"] < 2001)
    update = df[mask_rename].copy()
    update["proc1"] = "52352"
    update["ProcCode"] = "52352"
    update["HCPCS"] = "52352"
    # Remove ALL 52336 rows (both year<2001 and year>=2001)
    df = df[df["proc1"].astype(str).str.strip() != "52336"]
    df = pd.concat([df, update], ignore_index=True)

    # MLM's 1996 cell (carry-back). The extract has no 1996 row for CPT 80197 -- the
    # procedure the concordance maps to product code MLM -- because that code's claims
    # begin in 1997; 742 of the extract's procedure codes likewise start in 1997 and
    # 9,279 start later still, so a missing first year is ordinary. MLM is carried back so
    # that its claims enter the procedure-level price matching and the sample-construction
    # counts from 1996, like the other six codes in the III->II price panel. The value
    # carried back is MLM's earliest observed year, 1997, the same value the panel's own
    # backfill rule would use for the cell -- but the carried-back row also enters the
    # matching and aggregation that precede the panel, so the two are not equivalent. MLM
    # was reclassified in 2002, so the cell sits at event time -6, in the pre-period. The
    # row matters: MLM is one of three treated product codes in the III->II price panel,
    # and without it the III->II price sample and estimates change (see README, "Two
    # hand-coded adjustments to the MarketScan claims extract"). The II->I results do not
    # use MLM.
    #
    # The source row is selected by minimum year, not by position in the input file.
    if "80197" in df["proc1"].astype(str).str.strip().values:
        first_80197 = (df[df["proc1"].astype(str).str.strip() == "80197"]
                       .sort_values("year", kind="stable").iloc[[0]].copy())
        first_80197["year"] = 1996
        df = pd.concat([first_80197, df], ignore_index=True)

    df["q"] = df["proc_count"]

    logging.info(f"  Prepared claims: {len(df):,} rows")
    return df


def load_hcpcs_crosswalk(matched_sample_21, matched_sample_32):
    """
    Load GPT price links and build the PRODUCTCODE -> HCPCS crosswalk.

    Returns two DataFrames: hcpcs_2_1 and hcpcs_3_2, each with columns
    [PRODUCTCODE, HCPCS, procedure_desc] plus treatment assignment columns
    from the matched samples.
    """
    logging.info("Loading HCPCS crosswalk from GPT price links...")

    # Load 3_2 links
    tidy2 = pd.read_csv(GPT_LINKS_3_2)
    tidy2["hcpcs_cpt"] = tidy2["hcpcs_cpt"].apply(
        lambda x: str(x).split(",") if pd.notna(x) else []
    )
    tidy2["hcpcs_level_2"] = tidy2["hcpcs_level_2"].apply(
        lambda x: str(x).split(",") if pd.notna(x) else []
    )
    tidy2["HCPCS"] = tidy2["hcpcs_cpt"] + tidy2["hcpcs_level_2"]
    tidy2_exploded = tidy2.explode("HCPCS").reset_index(drop=True)
    tidy2_exploded["PRODUCTCODE"] = tidy2_exploded["productcode"]

    # Load 2_1 links
    tidy = pd.read_csv(GPT_LINKS_2_1)
    tidy["hcpcs_cpt"] = tidy["hcpcs_cpt"].apply(
        lambda x: str(x).split(",") if pd.notna(x) else []
    )
    tidy["hcpcs_level_2"] = tidy["hcpcs_level_2"].apply(
        lambda x: str(x).split(",") if pd.notna(x) else []
    )
    tidy["HCPCS"] = tidy["hcpcs_cpt"] + tidy["hcpcs_level_2"]
    tidy_exploded = tidy.explode("HCPCS").reset_index(drop=True)
    tidy_exploded["PRODUCTCODE"] = tidy_exploded["productcode"]

    # Combine
    fda_to_hcpcs = pd.concat([
        tidy2_exploded[["PRODUCTCODE", "HCPCS", "procedure_desc"]],
        tidy_exploded[["PRODUCTCODE", "HCPCS", "procedure_desc"]],
    ], ignore_index=True)
    fda_to_hcpcs = fda_to_hcpcs[fda_to_hcpcs.HCPCS.notnull()]
    fda_to_hcpcs["HCPCS"] = fda_to_hcpcs["HCPCS"].astype(str).str.strip()

    # HCPCS/CPT code corrections for retired and replaced procedure codes.
    # The GPT-generated crosswalk occasionally maps product codes to outdated or
    # incorrect CPT codes. The corrections below update these to the current (or
    # period-appropriate) CPT codes that appear in the Medicare claims data:
    #   JCA (Bleeding Time Devices): 85730 retired -> 85002 (bleeding time test)
    #   JGP (Total Protein Reagents): 84156 retired -> 84155 (total protein, serum)
    #   MLM (Tacrolimus Assay Reagents): 80162 retired -> 80197 (tacrolimus assay)
    #   DAD (Haptoglobin Reagents): 84295 retired -> 83010 (haptoglobin)
    fda_to_hcpcs.loc[fda_to_hcpcs.PRODUCTCODE == "JCA", "HCPCS"] = "85002"
    fda_to_hcpcs.loc[fda_to_hcpcs.PRODUCTCODE == "JGP", "HCPCS"] = "84155"
    fda_to_hcpcs.loc[fda_to_hcpcs.PRODUCTCODE == "MLM", "HCPCS"] = "80197"
    fda_to_hcpcs.loc[fda_to_hcpcs.PRODUCTCODE == "DAD", "HCPCS"] = "83010"

    return _attach_treatment_to_crosswalk(
        fda_to_hcpcs, matched_sample_21, matched_sample_32, label="GPT"
    )


def emit_price_sample_construction_counts(df_claims, matched_21,
                                          expert_panels, gpt_panels,
                                          expert_estimating_panels,
                                          gpt_estimating_panels):
    """
    Emit the price-data sample-construction counts stated in the data section
    (JPE Policy 2.2 in-text numbers) to output/tables/price_sample_construction.csv.

    Rows (each carries the manuscript-stated value so any divergence is visible):
      devices_reclassified_1998_2_1  -- treated Class II->I device types whose
          reclassification year is after 1996, i.e. the 1998 cohort, counted on the
          same matched sample the price crosswalk is built from. Manuscript: 56.
      analytic_procedure_codes       -- distinct procedure codes in the prepared
          MarketScan analytic claims panel. Manuscript: approximately 17,400.
      analytic_proc_code_year_obs    -- procedure-code-by-year observations in the
          same panel. Manuscript: approximately 181,700.
      expert_treated_device_types    -- treated device types actually present in
          the human-expert estimating panels, pooled across both pathways. This is
          the like-for-like analogue of the baseline concordance's "15 deregulated
          + 3 of the 12 down-regulated" coverage counts in d1_price_coverage.csv.
          Manuscript: 48.
      gpt_treated_device_types       -- the same count for the baseline LLM
          concordance, for comparison (manuscript: 15 + 3 = 18).
      *_linked_device_types          -- the same counts BEFORE the claims-coverage
          restriction (device types the concordance links at all), recorded so the
          two definitions can be told apart.
    """
    rows = []

    n_1998 = int(matched_21.loc[
        (matched_21["treatment"] == 1) & (matched_21["year_reclassified"] > 1996),
        "PRODUCTCODE"].nunique())
    rows.append({"metric": "devices_reclassified_1998_2_1",
                 "description": "Treated Class II to I device types reclassified after 1996 "
                                "(the 1998 cohort) in the matched sample",
                 "computed": n_1998, "manuscript_value": 56})

    proc_col = "proc1" if "proc1" in df_claims.columns else "HCPCS"
    n_codes = int(df_claims[proc_col].astype(str).str.strip().nunique())
    n_obs = int(len(df_claims.drop_duplicates([proc_col, "year"])))
    rows.append({"metric": "analytic_procedure_codes",
                 "description": f"Distinct procedure codes ({proc_col}) in the prepared "
                                "MarketScan analytic claims panel",
                 "computed": n_codes, "manuscript_value": 17400})
    rows.append({"metric": "analytic_proc_code_year_obs",
                 "description": f"Procedure-code-by-year observations ({proc_col} x year) in "
                                "the prepared MarketScan analytic claims panel",
                 "computed": n_obs, "manuscript_value": 181700})

    for label, panels, metric, stated in (
            ("Expert", expert_estimating_panels, "expert_treated_device_types", 48),
            ("GPT", gpt_estimating_panels, "gpt_treated_device_types", 18)):
        pcs = set()
        for pan in panels:
            pcs |= set(pan.loc[pan["treatment"] == 1, "PRODUCTCODE"].astype(str))
        rows.append({"metric": metric,
                     "description": f"Treated device types in the {label}-concordance price "
                                    "estimating panels, pooled across both pathways",
                     "computed": len(pcs), "manuscript_value": stated})

    for label, panels, metric in (
            ("Expert", expert_panels, "expert_linked_device_types"),
            ("GPT", gpt_panels, "gpt_linked_device_types")):
        pcs = set()
        for xw in panels:
            pcs |= set(xw.loc[xw["treatment"] == 1, "PRODUCTCODE"].astype(str))
        rows.append({"metric": metric,
                     "description": f"Treated device types the {label} concordance links to any "
                                    "procedure code, before the claims-coverage restriction",
                     "computed": len(pcs), "manuscript_value": ""})

    out_path = config.TABLES_DIR / "price_sample_construction.csv"
    pd.DataFrame(rows, columns=["metric", "description", "computed",
                                "manuscript_value"]).to_csv(out_path, index=False)
    for r in rows:
        logging.info(f"  [price sample] {r['metric']}: computed={r['computed']} "
                     f"(manuscript={r['manuscript_value']})")
    logging.info(f"Saved price sample-construction counts: {out_path}")


def _attach_treatment_to_crosswalk(fda_to_hcpcs, matched_sample_21,
                                   matched_sample_32, label=""):
    """Attach matched-sample treatment assignment to a PRODUCTCODE->HCPCS
    concordance and return (hcpcs_2_1, hcpcs_3_2).

    Shared by the baseline LLM concordance (load_hcpcs_crosswalk) and the
    human-expert concordance (load_expert_hcpcs_crosswalk) so the two samples
    differ ONLY in the concordance they start from, never in how treatment is
    assigned or how overlapping control procedures are dropped.
    """
    # Merge with matched sample treatment info for 3_2
    treat_32 = matched_sample_32[
        ["PRODUCTCODE", "FDA_own_accord", "treatment", "year_reclassified", "factorized", "FE"]
    ].drop_duplicates()
    hcpcs_3_2 = pd.merge(fda_to_hcpcs, treat_32, on="PRODUCTCODE", how="left")
    hcpcs_3_2 = hcpcs_3_2[hcpcs_3_2.treatment.notnull()]

    # Merge with matched sample treatment info for 2_1
    treat_21 = matched_sample_21[
        ["PRODUCTCODE", "treatment", "year_reclassified", "factorized", "FE"]
    ].drop_duplicates()
    hcpcs_2_1 = pd.merge(fda_to_hcpcs, treat_21, on="PRODUCTCODE", how="left")
    hcpcs_2_1 = hcpcs_2_1[hcpcs_2_1.treatment.notnull()]

    # Remove control HCPCS that overlap with treated HCPCS (for 2_1)
    treated_hcpcs = set(hcpcs_2_1[hcpcs_2_1.treatment == 1]["HCPCS"])
    hcpcs_2_1 = hcpcs_2_1[
        (hcpcs_2_1.treatment == 1) | ~(hcpcs_2_1.HCPCS.isin(treated_hcpcs))
    ]

    logging.info(
        f"  {label} HCPCS crosswalk: {len(hcpcs_3_2)} rows (3_2), "
        f"{len(hcpcs_2_1)} rows (2_1); treated device types: "
        f"{hcpcs_3_2.loc[hcpcs_3_2.treatment == 1, 'PRODUCTCODE'].nunique()} (3_2), "
        f"{hcpcs_2_1.loc[hcpcs_2_1.treatment == 1, 'PRODUCTCODE'].nunique()} (2_1)"
    )
    return hcpcs_2_1, hcpcs_3_2


def load_expert_hcpcs_crosswalk(matched_sample_21, matched_sample_32):
    """
    Load the HUMAN-EXPERT device-type-to-procedure concordance and build the
    PRODUCTCODE -> HCPCS crosswalk from it.

    This is the concordance produced independently by two AAPC-certified medical
    coders with third-coder reconciliation (data/raw/FDA_HCPCS_Xwalk_Moazzam.csv,
    documented in README "Data inputs"). The manuscript adopts the LLM concordance
    at baseline and reports the price estimates from this one as robustness; the
    estimates it produces are written to output/tables/price_utilization_estimates.csv
    with sample="Expert".

    Construction follows the author's own reading of the file: the concordance's
    'HCCPS Category Code' column, stripped, is the HCPCS/CPT code, and the
    concordance is restricted to product codes in the matched samples. Unlike the
    LLM crosswalk, NO retired-code corrections are applied: those corrections were
    made to the LLM's proposed links, and applying them here would silently edit
    the human coders' encoding, which is the object being compared.

    Returns two DataFrames: hcpcs_2_1 and hcpcs_3_2, with the same columns as
    load_hcpcs_crosswalk().
    """
    logging.info("Loading HCPCS crosswalk from the human-expert concordance...")
    xw = pd.read_csv(EXPERT_LINKS, dtype=str)
    if "HCCPS Category Code" not in xw.columns:
        raise KeyError(
            f"{EXPERT_LINKS.name} is missing the 'HCCPS Category Code' column "
            f"(found {list(xw.columns)})")
    xw["HCPCS"] = xw["HCCPS Category Code"].astype(str).str.strip()
    xw["PRODUCTCODE"] = xw["PRODUCTCODE"].astype(str).str.strip()
    xw = xw[xw["HCPCS"].notnull() & ~xw["HCPCS"].isin(["", "nan", "NaN", "None"])]
    fda_to_hcpcs = xw[["PRODUCTCODE", "HCPCS"]].drop_duplicates().copy()
    # The expert file carries no procedure description; the column is retained so
    # the two crosswalks are schema-identical downstream.
    fda_to_hcpcs["procedure_desc"] = ""
    logging.info(f"  Expert concordance: {len(xw)} rows, "
                 f"{fda_to_hcpcs.PRODUCTCODE.nunique()} product codes, "
                 f"{fda_to_hcpcs.HCPCS.nunique()} distinct HCPCS codes")

    return _attach_treatment_to_crosswalk(
        fda_to_hcpcs, matched_sample_21, matched_sample_32, label="Expert"
    )


def _build_price_matched_panel(
    df,
    proc_col="proc1",
    year_col="year",
    price_col="BilledAmt",
    treat_col="treatment",
    reclass_col="year_reclassified",
    productcode_col="PRODUCTCODE",
    min_overlap_years=2,
    use_log=False,
    n_controls=1,
    without_replacement=True,
    random_state=42,
    require_control_cover_treated_years=True,
    drop_extra_control_years=True,
):
    """
    Nearest-neighbor matching on pre-treatment prices for the "All CPTs" sample.

    Matches each treated procedure (proc1) to n_controls control procedures based
    on RMSE of pre-treatment prices. Returns only the matched pairs, with each
    control assigned a synthetic PRODUCTCODE = treated_PRODUCTCODE + match_rank.

    This replicates build_matched_panel from Price_data_and_analysis.py (lines 1042-1270).
    """
    rng = np.random.default_rng(random_state)
    base = df.copy()

    # Average price per procedure × year
    by_py = base.groupby([proc_col, year_col], as_index=False)[price_col].mean()
    if use_log:
        by_py["_price_for_dist_"] = np.log(by_py[price_col].astype(float) + 1e-9)
    else:
        by_py["_price_for_dist_"] = by_py[price_col].astype(float)

    proc_treat_flag = base.groupby(proc_col, as_index=True)[treat_col].max()
    treated_procs = proc_treat_flag[proc_treat_flag == 1].index.tolist()
    control_procs = proc_treat_flag[proc_treat_flag == 0].index.tolist()

    yreclass = (
        base.loc[base[proc_col].isin(treated_procs), [proc_col, reclass_col]]
        .dropna(subset=[reclass_col])
        .drop_duplicates(subset=[proc_col])
        .set_index(proc_col)[reclass_col]
    )
    treat_with_cutoff = [p for p in treated_procs if p in yreclass.index]

    proc_to_productcode = {}
    if productcode_col in base.columns:
        proc_to_productcode = (
            base[[proc_col, productcode_col]]
            .dropna(subset=[productcode_col])
            .drop_duplicates(subset=[proc_col])
            .set_index(proc_col)[productcode_col]
            .to_dict()
        )

    # Fast lookups for price series
    proc_series = {}
    proc_years = {}
    for p, sub in by_py.groupby(proc_col):
        years = sub[year_col].astype(int).tolist()
        proc_years[p] = set(years)
        proc_series[p] = dict(zip(years, sub["_price_for_dist_"]))

    def distance_for_pair(t_proc, c_proc, pre_years):
        t_map = proc_series.get(t_proc, {})
        c_map = proc_series.get(c_proc, {})
        common = [y for y in pre_years if (y in t_map and y in c_map)]
        if len(common) >= min_overlap_years:
            diffs = [t_map[y] - c_map[y] for y in common]
            return float(np.sqrt(np.mean(np.square(diffs)))), len(common)
        t_vals = [t_map[y] for y in pre_years if y in t_map]
        c_vals = [c_map[y] for y in pre_years if y in c_map]
        if len(t_vals) and len(c_vals):
            return float(abs(np.mean(t_vals) - np.mean(c_vals))), min(len(t_vals), len(c_vals))
        return float("inf"), 0

    controls_by_year = {}
    ctrl_df = by_py[by_py[proc_col].isin(control_procs)]
    for y, sub in ctrl_df.groupby(year_col):
        controls_by_year[int(y)] = set(sub[proc_col].unique())

    chosen_controls_global = set()
    matches = []

    for t in treat_with_cutoff:
        cutoff = int(yreclass.loc[t])
        t_years_all_sorted = sorted(proc_series.get(t, {}).keys())
        t_years_all_set = set(t_years_all_sorted)
        pre_years = [y for y in t_years_all_sorted if y < cutoff]
        if len(pre_years) == 0:
            pre_years = sorted([y for y in t_years_all_sorted if y <= cutoff])
            pre_years = pre_years[:max(min_overlap_years, min(3, len(pre_years)))]

        # Candidates: controls observed in any pre year
        cand = set()
        if pre_years:
            for y in pre_years:
                cand |= controls_by_year.get(y, set())
        else:
            cand = set(control_procs)

        # Year coverage filter: require control to cover all treated years
        if require_control_cover_treated_years:
            cand_full = [c for c in cand if t_years_all_set.issubset(proc_years.get(c, set()))]
            if len(cand_full) == 0:
                cand_full = list(cand)
            cand = cand_full
        else:
            cand = list(cand)

        if without_replacement:
            cand = [c for c in cand if c not in chosen_controls_global]

        if not cand:
            pool = [c for c in control_procs if c not in chosen_controls_global] if without_replacement else list(control_procs)
            if require_control_cover_treated_years:
                cand = [c for c in pool if t_years_all_set.issubset(proc_years.get(c, set()))]
                if not cand:
                    cand = pool
            else:
                cand = pool

        rows = []
        for c in cand:
            d, overlap = distance_for_pair(t, c, pre_years)
            rows.append((c, d, overlap))
        cand_df = (
            pd.DataFrame(rows, columns=["control_proc1", "distance", "overlap_years"])
            .sort_values(["distance", "overlap_years", "control_proc1"], ascending=[True, False, True])
        )

        if len(cand_df):
            finite_df = cand_df[np.isfinite(cand_df["distance"])]
            pick_df = finite_df if len(finite_df) >= n_controls else cand_df
            pick_df = pick_df.head(n_controls)
        else:
            pick_df = pd.DataFrame(columns=["control_proc1", "distance", "overlap_years"])

        for rank, (_, r) in enumerate(pick_df.iterrows(), start=1):
            c_best = r["control_proc1"]
            if without_replacement:
                chosen_controls_global.add(c_best)
            matches.append({
                "treated_proc1": t,
                "treated_PRODUCTCODE": proc_to_productcode.get(t, np.nan),
                "control_proc1": c_best,
                "match_rank": rank,
                "cutoff_year": cutoff,
            })

    match_map = pd.DataFrame(matches).reset_index(drop=True)

    # Build matched panel: one block per matched pair
    blocks = []
    for _, m in match_map.iterrows():
        t = m["treated_proc1"]
        c = m["control_proc1"]

        sub_t = base[base[proc_col] == t].copy()
        sub_c = base[base[proc_col] == c].copy()

        if drop_extra_control_years:
            t_years = set(sub_t[year_col].astype(int))
            sub_c = sub_c[sub_c[year_col].astype(int).isin(t_years)].copy()

        for sub, is_control in [(sub_t, False), (sub_c, True)]:
            sub["treated_proc1"] = t
            sub["treated_PRODUCTCODE"] = m["treated_PRODUCTCODE"]
            sub["match_rank"] = m["match_rank"]
            sub["is_control"] = 1 if is_control else 0
            blocks.append(sub)

    if blocks:
        matched_panel = pd.concat(blocks, axis=0, ignore_index=True)
    else:
        matched_panel = base.iloc[0:0].copy()

    logging.info(
        f"  Price matching: {len(treat_with_cutoff)} treated procs, "
        f"{len(match_map)} matched pairs ({n_controls} controls each)"
    )
    return matched_panel, match_map


def build_price_panel(df_claims, hcpcs_xwalk, reclass_type, match_type="Matched",
                      match_on="BilledAmt"):
    """
    Merge claims data with HCPCS crosswalk (which contains treatment assignments),
    aggregate to PRODUCTCODE x year, balance the panel, and construct the
    stacked DiD structure.

    Following the original Price_data_and_analysis.py logic exactly:
    - "Matched": keep only treatment.notnull() (PCs in the device-outcome matched sample)
    - "All CPTs": match treated to controls via nearest-neighbor on pre-treatment
      values of match_on (default: BilledAmt for prices, proc_count for utilization),
      assign synthetic PRODUCTCODEs to controls

    Parameters:
        df_claims: Claims DataFrame with HCPCS, year, pay, proc_count
        hcpcs_xwalk: HCPCS crosswalk with PRODUCTCODE, HCPCS, treatment, year_reclassified
        reclass_type: '2_1' or '3_2'
        match_type: 'All CPTs' or 'Matched'
        match_on: Column to match on for All CPTs ('BilledAmt' or 'proc_count')

    Returns:
        DataFrame ready for estimation (both BJS and Conley-Taber)
    """
    logging.info(f"Building price panel for {reclass_type} ({match_type})...")

    # Merge claims with HCPCS crosswalk
    claims = pd.merge(df_claims, hcpcs_xwalk, how="left", on="HCPCS")

    if reclass_type == "2_1":
        # Exclude 1996 reclassifications (too early for price data)
        claims = claims[claims.year_reclassified != 1996]

    if match_type == "Matched":
        # Keep only product codes in the matched sample
        claims = claims[claims.treatment.notnull()]
    else:
        # "All CPTs" — match treated to controls on pre-treatment values
        # of match_on (prices or utilization)
        claims.loc[claims.treatment.isnull(), "treatment"] = 0
        n_controls = 10 if reclass_type == "3_2" else 4
        use_log = (match_on == "proc_count")  # log for utilization (right-skewed)
        claims, _match_table = _build_price_matched_panel(
            claims, use_log=use_log, n_controls=n_controls,
            price_col=match_on,
        )
        # Assign synthetic PRODUCTCODE to controls: treated_PRODUCTCODE + match_rank
        claims.loc[claims.year_reclassified.isnull(), "PRODUCTCODE"] = (
            claims.loc[claims.year_reclassified.isnull(), "treated_PRODUCTCODE"]
            + claims.loc[claims.year_reclassified.isnull(), "match_rank"].astype(str)
        )

    claims["proc_count"] = claims["proc_count"].astype(float)

    # Aggregate to PRODUCTCODE x year
    agg_dict = {"pay": "sum", "proc_count": "sum", "coins": "sum", "year_reclassified": "mean"}
    if "FDA_own_accord" in claims.columns:
        agg_dict["FDA_own_accord"] = "mean"
    claims = claims.groupby(["year", "PRODUCTCODE"]).agg(agg_dict).reset_index()

    # Recompute BilledAmt at the aggregated level
    claims["BilledAmt"] = claims["pay"] / claims["proc_count"]
    claims["PaidAmt"] = claims["BilledAmt"]

    # Balance the panel via unstack/stack
    FILL_VAL = -99999999999999.0
    full = (
        claims.set_index(["PRODUCTCODE", "year"])
        .unstack(fill_value=FILL_VAL)
        .stack()
        .sort_index(level=1)
        .reset_index()
    )

    # Forward/backward fill the sentinel values. FDA_own_accord is a per-product-code constant;
    # it is filled too, because the III->II filter below keeps a treated row only when
    # FDA_own_accord == 1, and a treated product code with no claims in some year would
    # otherwise lose that year's (filled) row and leave its cluster unbalanced.
    for col in ["BilledAmt", "proc_count", "year_reclassified", "FDA_own_accord"]:
        if col in full.columns:
            full.loc[full[col] == FILL_VAL, col] = np.nan
            full[col] = full.groupby("PRODUCTCODE")[col].transform(lambda v: v.ffill())
            full[col] = full.groupby("PRODUCTCODE")[col].transform(lambda v: v.bfill())

    # Set treatment based on year_reclassified
    full["treatment"] = 0
    full.loc[full.year_reclassified.notnull(), "treatment"] = 1

    # Build stacked FE structure (matching original logic)
    subset_t1 = full[full["treatment"] == 1].copy()
    subset_t0 = full[full["treatment"] == 0].copy()
    subset_t1["FE"] = subset_t1["PRODUCTCODE"].astype("category").cat.codes

    # Duplicate controls for each treated FE
    dups = []
    for fe_val in set(subset_t1["FE"]):
        temp = subset_t0.copy()
        temp["FE"] = fe_val
        dups.append(temp)
    combined_t0 = pd.concat(dups, ignore_index=True) if dups else subset_t0
    combined_t0["treatment"] = 0
    combined_t0["year_reclassified"] = 0

    stacked = pd.concat([subset_t1, combined_t0], ignore_index=True)

    # For III->II, apply FDA_own_accord filter
    if reclass_type == "3_2" and "FDA_own_accord" in stacked.columns:
        stacked = stacked[(stacked.treatment == 0) | (stacked.FDA_own_accord == 1)]

    # Compute derived columns
    stacked["event_time"] = stacked["year"] - stacked["year_reclassified"]
    stacked["posttreat"] = 0
    stacked.loc[
        (stacked.year >= stacked.year_reclassified) & (stacked.treatment == 1),
        "posttreat",
    ] = 1
    stacked["factorized"] = stacked.PRODUCTCODE.astype("category").cat.codes
    stacked["class_by_episode"] = (
        stacked["PRODUCTCODE"].astype(str) + "[SEP]" + stacked["FE"].astype(str)
    )
    stacked["class_by_episode"] = stacked.class_by_episode.astype("category").cat.codes
    stacked = stacked.sort_values(
        by=["treatment", "class_by_episode", "year"]
    ).reset_index(drop=True)

    # Use log(BilledAmt) — original uses logged=True for price
    stacked["BilledAmt"] = np.log(stacked["BilledAmt"])

    stacked["q"] = stacked["proc_count"]
    # Log utilization — same treatment as log(BilledAmt) for prices
    stacked["log_q"] = np.log(stacked["proc_count"])
    # Compute ET using max(year_reclassified) within each FE group, matching
    # the original Price_data_and_analysis.py (line 2058-2061).  Controls have
    # year_reclassified=0, so transform(max) gives them the treated unit's
    # reclassification year within the same cohort (FE group).
    stacked["year_reclass_ET"] = stacked.groupby("FE")[
        "year_reclassified"
    ].transform("max")
    stacked["ET"] = stacked["year"] - stacked["year_reclass_ET"]

    n_treated = stacked[stacked.treatment == 1]["PRODUCTCODE"].nunique()
    n_control = stacked[stacked.treatment == 0]["PRODUCTCODE"].nunique()
    logging.info(
        f"  Price panel ({reclass_type}, {match_type}): "
        f"{n_treated} treated, {n_control} control PCs"
    )

    return stacked


def run_static_estimation(df_panel, outcome, reclass_type, use_bjs=False):
    """
    Run static DiD estimation for a single price/utilization outcome.

    When use_bjs=True, uses BJS imputation (did_imputation via rpy2).
    Otherwise uses Conley-Taber stacked DiD.

    Returns:
        (estimate, alpha025, alpha975, ci_method) or (None, None, None, None) if too few PCs.
        ci_method names the inference behind the interval and is written to the ci_method
        column of price_utilization_estimates.csv:
          "permutation (Conley-Taber)"                                   -- the stacked permutation CI;
          "clustered-SE normal approximation (feols; permutation CI undefined)"
                                                                         -- conley_taber_stacked could not
                                                                            lay out the balanced grid (feols
                                                                            removed observations) and reports
                                                                            the feols estimate with a
                                                                            clustered-SE interval, recorded in
                                                                            output/logs/inference_method_fallbacks.csv;
          "clustered-SE normal approximation (did_imputation)"           -- the BJS rows' conf.low/conf.high.
    """
    df = df_panel[df_panel[outcome].notnull()].copy().reset_index(drop=True)

    if df["PRODUCTCODE"].nunique() < 5:
        logging.warning(f"  {outcome}: fewer than 5 PCs, skipping")
        return None, None, None, None

    if use_bjs:
        # BJS imputation via R did_imputation package
        source_r_scripts()
        bjs_cols = [outcome, "year_reclassified", "treatment", "factorized", "year"]
        df_bjs = df[bjs_cols].copy()
        estimate, alpha025, alpha975 = run_did_imputation(df_bjs, outcome)
        ci_method = "clustered-SE normal approximation (did_imputation)"
    else:
        # Conley-Taber stacked DiD
        cols = [
            outcome, "posttreat", "treatment", "class_by_episode",
            "year", "factorized", "FE", "PRODUCTCODE",
        ]
        n_fallbacks_before = len(_conley_taber_module.INFERENCE_FALLBACKS)
        estimate, alpha025, alpha975 = conley_taber_stacked(
            df[cols], outcome, "posttreat", "treatment",
            "class_by_episode", "year", seed=config.RANDOM_SEED,
        )
        if len(_conley_taber_module.INFERENCE_FALLBACKS) > n_fallbacks_before:
            ci_method = "clustered-SE normal approximation (feols; permutation CI undefined)"
        else:
            ci_method = "permutation (Conley-Taber)"

    se = compute_se(estimate, alpha025, alpha975)
    stars = significance_stars(estimate, se)
    N = len(df.drop_duplicates(["PRODUCTCODE", "year"]))
    logging.info(
        f"  {outcome} ({'BJS' if use_bjs else 'CT'}): est={estimate:.4f}{stars}, "
        f"CI=[{alpha025:.4f}, {alpha975:.4f}], N={N}"
    )

    return estimate, alpha025, alpha975, ci_method


def run_price_event_study_bjs(df_panel, outcome, reclass_type):
    """
    Run BJS imputation event study for a price outcome.

    Uses filter_country_ES_2_1 from preprocess.R, which runs:
        feols(outcome ~ i(ET, treatment, ref = -1) | factorized^FE + year^FE,
              cluster = 'class_by_episode')

    The R function returns coefficients and SEs for each event time.
    We then trim to the appropriate window and insert zero at t=-1.

    Returns:
        (event_times, estimates, lower_cis, upper_cis) arrays
    """
    source_r_scripts()

    window = PRICE_WINDOWS[reclass_type]
    window_low = window["low"]
    window_high = window["high"]

    df = df_panel[df_panel[outcome].notnull()].copy()

    # Prepare data for R event study
    es_cols = [
        outcome, "year_reclassified", "treatment", "factorized",
        "year", "FE", "ET", "class_by_episode",
    ]
    df_es = df[es_cols].copy()

    logging.info(
        f"  Price ES ({reclass_type}): "
        f"{df_es[df_es.treatment == 1]['factorized'].nunique()} treated units, "
        f"window=[-{window_low}, +{window_high}]"
    )

    # Run BJS event study via R
    coefs, ses = run_feols_es_2to1(df_es, outcome)

    # The R function returns coefficients for all event times except ref=-1.
    # Trim to the plotted window and insert the zero at t=-1.
    et_min = int(df["ET"].min())

    # Index into the full coefficient array for the plotted window
    index_int_low = int(-et_min - window_low)
    index_int_high = int(-et_min + window_high)

    coefs_trimmed = coefs[index_int_low:index_int_high]
    ses_trimmed = ses[index_int_low:index_int_high]

    # Build event time grid and insert reference period (t=-1 -> 0)
    event_times = np.arange(-window_low, window_high + 1, 1)
    # Insert 0 at the position corresponding to t=-1 (index = window_low - 1)
    # because the R function omits the reference period
    coefs_full = np.insert(coefs_trimmed, window_low - 1, 0.0)
    ses_full = np.insert(ses_trimmed, window_low - 1, 0.0)

    # Compute CIs
    lower_cis = coefs_full - 1.96 * ses_full
    upper_cis = coefs_full + 1.96 * ses_full

    return event_times, coefs_full, lower_cis, upper_cis


def _getNewPostTreat(df, i):
    """
    Create posttreat_new indicator = 1 at exactly event-time i for treated units.

    Applied per product code group. Mirrors getNewPostTreat in 04_event_studies.py.

    The indicator is selected on the ET column: the one treated row of the group whose
    ET equals i is marked, a control group (no posttreat == 1 row) gets an all-zero
    indicator, a target outside the group's observed window marks nothing, and a group
    with two rows at the same event time is an error rather than an arbitrary choice.
    """
    df = df.copy()
    df["posttreat_new"] = 0
    if "ET" not in df.columns or "posttreat" not in df.columns:
        raise KeyError(
            f"_getNewPostTreat requires 'ET' and 'posttreat' columns; got {list(df.columns)}")

    if not (df["posttreat"] > 0).any():
        # Control group: it has no event of its own, so no event-time period to mark.
        return df

    hit = df["ET"] == i
    n_hit = int(hit.sum())
    if n_hit == 0:
        # Target event time outside this group's observed window (the original script's
        # i > ET.max() / i < ET.min() branch, and its "target_idx not in index" branch).
        return df
    if n_hit > 1:
        pc = df["PRODUCTCODE"].iloc[0] if "PRODUCTCODE" in df.columns else "?"
        raise ValueError(
            f"_getNewPostTreat: {n_hit} rows at ET={i} for group {pc}; the event-time "
            "indicator must mark exactly one row per group")
    df.loc[hit, "posttreat_new"] = 1
    return df


def run_price_event_study_ct(df_panel, outcome, reclass_type):
    """
    Run Conley-Taber event study for price using full-panel estimation.

    Matches the original manuscript approach: for each event time, calls
    conley_taber_stacked_es which runs R feols with i(ET, treatment, ref=-1)
    on the full panel, then applies CT permutation inference to the
    coefficient at the target event time.
    """
    window = PRICE_WINDOWS[reclass_type]
    window_low = window["low"]
    window_high = window["high"]

    logging.info(
        f"  Price ES CT ({reclass_type}): window=[-{window_low}, +{window_high}]"
    )

    cols = [
        outcome, "posttreat", "treatment", "factorized",
        "year", "FE", "ET", "class_by_episode", "PRODUCTCODE",
    ]

    event_times, estimates, lower_cis, upper_cis = [], [], [], []

    for num in range(-window_low, window_high + 1):
        if num == -1:
            event_times.append(num)
            estimates.append(0.0)
            lower_cis.append(0.0)
            upper_cis.append(0.0)
            continue

        # Create posttreat_new marking only event-time num for treated units
        df_new = df_panel.groupby("PRODUCTCODE", group_keys=False).apply(
            _getNewPostTreat, num
        )

        # Compute index for the target coefficient in the feols output
        # i(ET, treatment, ref=-1) creates coefficients for all ET != -1
        index_int = int(-df_new["ET"].min() + num)
        if num > -1:
            index_int -= 1

        logging.info(f"  CT-ES period {num}: index_int={index_int}")

        try:
            est, lo, hi = conley_taber_stacked_es(
                df_new[cols + ["posttreat_new"]].reset_index(drop=True),
                outcome,
                "posttreat_new",
                "treatment",
                "class_by_episode",
                "year",
                index_int,
                seed=config.RANDOM_SEED,
            )
            event_times.append(num)
            estimates.append(est)
            lower_cis.append(lo)
            upper_cis.append(hi)
            logging.info(f"  CT-ES period {num}: est={est}, CI=[{lo}, {hi}]")
        except Exception as e:
            # Recorded, not swallowed: a dropped period leaves a hole in the event-time
            # grid of a manuscript exhibit, and main()'s guard fails the step on it.
            _CT_ES_FAILURES.append(
                {"reclass_type": reclass_type, "outcome": outcome,
                 "event_time": int(num), "error": f"{type(e).__name__}: {e}"})
            logging.error(
                "  CT-ES period %s FAILED for %s/%s: %s -- this event time will be "
                "ABSENT from the figure and from ES_coefs_price_%s.csv; the step will fail.",
                num, reclass_type, outcome, e, reclass_type, exc_info=True)

    return (
        np.array(event_times),
        np.array(estimates),
        np.array(lower_cis),
        np.array(upper_cis),
    )


def save_price_event_study_coefficients(df_panel, et, est, lo, hi, reclass_type):
    """Write the Figure 3c event-study coefficients to output/tables/event_study_coefficients/.

    Written so the figure's coefficients are on disk and comparable with the manuscript's panels.
    (The DiD estimates the text cites are separate; they go to
    price_utilization_estimates.csv.)

    Columns deviate from the other ES_coefs_* files on purpose: Conley-Taber inference returns CI bounds
    rather than a standard error, so no SE column is reported; the CI bounds are the inference
    object. Event time -1 is the
    reference period, held at exactly 0 by construction, and is flagged rather than presented as an
    estimate."""
    out_dir = config.TABLES_DIR / "event_study_coefficients"
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    if df_panel is not None and "ET" in df_panel.columns and "treatment" in df_panel.columns:
        grouped = df_panel.groupby(["ET", "treatment"]).size()
        for (event_time, treated), n in grouped.items():
            counts.setdefault(int(event_time), {})[int(treated)] = int(n)
    rows = []
    for i, event_time in enumerate(et):
        n = counts.get(int(event_time), {})
        rows.append({
            "ET": int(event_time),
            "Effect": float(est[i]),
            "lower_CI": float(lo[i]),
            "upper_CI": float(hi[i]),
            "n_treated": n.get(1, ""),
            "n_control": n.get(0, ""),
            "is_reference": int(int(event_time) == -1),
            "method": "Conley_Taber_stacked_ES",
        })
    outpath = out_dir / f"ES_coefs_price_{reclass_type}.csv"
    pd.DataFrame(rows).to_csv(outpath, index=False)
    logging.info(f"Saved price event-study coefficients: {outpath} ({len(rows)} event times)")
    return outpath


def produce_figures(df_panel_21, df_panel_32):
    """
    Produce Figure 3c: Conley-Taber event study for BilledAmt.

    Saved as two separate PNGs matching the manuscript's \\includegraphics filenames:
        3_2_nolog_Price_solo_CTs_sept20_25.png
        2_1_nolog_Price_solo_CTs_sept20_25.png
    """
    # --- Figure 3c: Price event study (Conley-Taber) — one PNG per direction ---
    logging.info("Producing Figure 3c (price event study via Conley-Taber)...")

    PRICE_FIGURE_FILENAMES = {
        "3_2": "3_2_nolog_Price_solo_CTs_sept20_25.png",
        "2_1": "2_1_nolog_Price_solo_CTs_sept20_25.png",
    }
    force_figures = os.environ.get("FDA_FORCE_PRICE_FIGURES") == "1"

    for reclass_type, df_panel, label in [
        ("3_2", df_panel_32, "III to II"),
        ("2_1", df_panel_21, "II to I"),
    ]:
        figure_path = config.FIGURES_DIR / PRICE_FIGURE_FILENAMES[reclass_type]
        reuse_figure = figure_path.exists() and not force_figures

        # Both use Conley-Taber stacked event study (matching original
        # Price_data_and_analysis.py which calls ConleyTaberStackedES
        # period-by-period for both 3_2 and 2_1).
        #
        # The coefficients are computed and written on EVERY run, including when the included figure is
        # reused, so the panels' numbers are always on disk.
        et, est, lo, hi = run_price_event_study_ct(
            df_panel, PRICE_OUTCOME, reclass_type
        )
        if len(et) > 0:
            save_price_event_study_coefficients(df_panel, et, est, lo, hi, reclass_type)
        if reuse_figure:
            logging.info(
                "  Using included price event-study figure: %s "
                "(set FDA_FORCE_PRICE_FIGURES=1 to regenerate); coefficients emitted regardless",
                figure_path.name,
            )
            continue
        if len(et) > 0:
            fig, ax = create_figure(nrows=1, ncols=1, figsize=(12, 8))
            plot_event_study(
                ax, et, est, lo, hi,
                reclass_type, outcome_label=f"Average Price ({label})",
            )
            save_figure(fig, PRICE_FIGURE_FILENAMES[reclass_type])

    # Utilization event study figures removed — utilization result is reported
    # as a null finding in a compact appendix table (tab:Utilization) rather
    # than as event study figures.


def compute_pre_treatment_price_stats(df_panel, outcome):
    """
    Compute pre-treatment mean and std of the price outcome for treated units
    at event_time == -1.

    Returns level (un-logged) statistics, matching original script which
    computed baseline BEFORE log transformation.

    Returns (pre_mean, pre_std).
    """
    mask = (
        (df_panel["treatment"] == 1)
        & (df_panel["ET"] == -1)
        & df_panel[outcome].notnull()
    )
    # The panel has already been log-transformed, so exponentiate back
    pre_df = np.exp(df_panel.loc[mask, outcome])
    if len(pre_df) == 0:
        return np.nan, np.nan
    return pre_df.mean(), pre_df.std()


def compute_pre_treatment_utilization_stats(df_panel, outcome):
    """
    Compute pre-treatment mean and std of utilization for treated units
    at event_time == -1.

    Unlike price, utilization is in levels (not log-transformed),
    so no exponentiation needed.

    Returns (pre_mean, pre_std).
    """
    mask = (
        (df_panel["treatment"] == 1)
        & (df_panel["ET"] == -1)
        & df_panel[outcome].notnull()
    )
    pre_df = df_panel.loc[mask, outcome]
    if len(pre_df) == 0:
        return np.nan, np.nan
    return pre_df.mean(), pre_df.std()


def _format_signed(value, decimals=2):
    """
    Format a float to `decimals` places using the manuscript's LaTeX math-minus
    ($-$) for negative values instead of a plain hyphen (cosmetic only -- the
    rounding is identical to f"{value:.{decimals}f}"; only the sign glyph
    differs so the emitted fragment is byte-identical to the hand-typeset
    manuscript rows).
    """
    magnitude_str = f"{abs(value):.{decimals}f}"
    return f"$-${magnitude_str}" if value < 0 else magnitude_str


def write_price_tex_files(price_results, df_panel_32, df_panel_21):
    """
    Write the 4 .tex row-fragment files expected by the manuscript for price:
        RegTable_Prices_3_2_sep25.tex       (Conley-Taber, III->II)
        RegTable_Prices_2_1_sep25.tex       (Conley-Taber, II->I)
        DIDimpute_RegTable_Prices_3_2_sep25.tex  (BJS imputation, III->II)
        DIDimpute_RegTable_Prices_2_1_sep25.tex  (BJS imputation, II->I)

    Each file is 4 lines:
        Row 1: estimate row with pre-mean, All CPTs est, Matched est, 2 dash placeholders
        Row 2: SE row with pre-std, All CPTs SE, Matched SE, 2 dash placeholders
        Row 3: blank separator row
        Row 4: sample size row

    The two estimate columns correspond to table columns (2) and (3):
        (2) "All CPTs" — matched on baseline prices across all procedure codes
        (3) "Matched" — matched on device outcomes

    Parameters:
        price_results: list of dicts with keys:
            reclass_type, method, sample, Estimate, lower_CI, upper_CI, Sample Size
        df_panel_32: All CPTs panel for III->II (for pre-treatment stats)
        df_panel_21: All CPTs panel for II->I (for pre-treatment stats)
    """
    formatted_dir = config.TABLES_DIR / "Formatted"
    formatted_dir.mkdir(parents=True, exist_ok=True)

    panels = {"3_2": df_panel_32, "2_1": df_panel_21}

    # D.1 provenance (JPE 2.2, output-only): number of TREATED device types actually covered by the
    # price/utilization estimating sample -- i.e., treated device types whose linked procedures are
    # observed in the MarketScan claims. These are the ``3'' (III->II) and ``15'' (II->I) cells in
    # Table D.1, Panel B (Price and utilization row). Counts treatment==1 unique PRODUCTCODEs in each
    # All-CPTs panel (synthetic controls carry treatment==0, so they are excluded). This is a COUNT
    # of the estimating sample, not an estimate; it does not touch any regression. Read by
    # 10c_generate_appendix_tables.generate_d1().
    cov_rows = []
    for rtype, df_panel in panels.items():
        if "treatment" in df_panel.columns and "PRODUCTCODE" in df_panel.columns:
            n_cov = int(df_panel.loc[df_panel["treatment"] == 1, "PRODUCTCODE"].nunique())
        else:
            n_cov = None
        cov_rows.append({"reclass_type": rtype, "n_covered": n_cov})
    pd.DataFrame(cov_rows).to_csv(config.TABLES_DIR / "d1_price_coverage.csv", index=False)
    logging.info("D.1 provenance: price/utilization coverage counts %s -> d1_price_coverage.csv"
                 % {r["reclass_type"]: r["n_covered"] for r in cov_rows})

    # Compute pre-treatment stats for each reclassification type
    pre_stats = {}
    for rtype, df_panel in panels.items():
        pre_mean, pre_std = compute_pre_treatment_price_stats(
            df_panel, PRICE_OUTCOME
        )
        pre_stats[rtype] = (pre_mean, pre_std)

    # Map: (method, reclass_type) -> filename
    TEX_FILENAMES = {
        ("Conley_Taber", "3_2"): "RegTable_Prices_3_2_sep25.tex",
        ("Conley_Taber", "2_1"): "RegTable_Prices_2_1_sep25.tex",
        ("BJS_imputation", "3_2"): "DIDimpute_RegTable_Prices_3_2_sep25.tex",
        ("BJS_imputation", "2_1"): "DIDimpute_RegTable_Prices_2_1_sep25.tex",
    }

    # Build lookup: (method, reclass_type, sample) -> result dict
    result_lookup = {}
    for r in price_results:
        key = (r["method"], r["reclass_type"], r["sample"])
        result_lookup[key] = r

    for (method, rtype), filename in TEX_FILENAMES.items():
        pre_mean, pre_std = pre_stats[rtype]

        # Column (2): "All CPTs" — matched on baseline prices across all CPTs
        allcpt_r = result_lookup.get((method, rtype, "All CPTs"))
        # Column (3): "Matched" — matched on device outcomes
        matched_r = result_lookup.get((method, rtype, "Matched"))

        # Format estimate and SE for All CPTs sample (column 2)
        if allcpt_r is not None:
            ac_est = allcpt_r["Estimate"]
            ac_se = compute_se(ac_est, allcpt_r["lower_CI"], allcpt_r["upper_CI"])
            ac_stars = significance_stars(ac_est, ac_se)
            ac_N = int(allcpt_r["Sample Size"])
            # Price table (Table D.10) uses a PLAIN hyphen for negatives (verified against the shipped
            # RegTable_Prices_*.tex fragments); do NOT use $-$ here (that is the Utilization/D.11 convention).
            ac_est_str = f"{ac_est:.2f}{ac_stars}"
            ac_se_str = f"({ac_se:.2f})"
        else:
            ac_est_str = ""
            ac_se_str = ""
            ac_N = 0

        # Format estimate and SE for Matched sample (column 3)
        if matched_r is not None:
            m_est = matched_r["Estimate"]
            m_se = compute_se(m_est, matched_r["lower_CI"], matched_r["upper_CI"])
            m_stars = significance_stars(m_est, m_se)
            m_N = int(matched_r["Sample Size"])
            m_est_str = f"{m_est:.2f}{m_stars}"
            m_se_str = f"({m_se:.2f})"
        else:
            m_est_str = ""
            m_se_str = ""
            m_N = 0

        # Format pre-mean with dagger
        pre_mean_str = f"{pre_mean:.2f}" if not np.isnan(pre_mean) else ""
        pre_std_str = f"({pre_std:.2f})" if not np.isnan(pre_std) else ""

        # Assemble 4 rows matching the exact manuscript format
        lines = []
        # Row 1: estimate row
        lines.append(
            f"\\hspace{{6mm}}Procedure Price & {pre_mean_str}\u2020 "
            f"&{ac_est_str}&  {m_est_str} & - & -  \\\\ "
        )
        # Row 2: SE row
        lines.append(
            f" &{pre_std_str} & {ac_se_str} & {m_se_str} & - & - \\\\ "
        )
        # Row 3: blank separator
        lines.append("&&&& \\\\ ")
        # Row 4: sample size
        lines.append(
            f"\\hspace{{6mm}}Sample Size &  & {ac_N} & {m_N} & - & - \\\\ "
        )

        tex_str = "\n".join(lines) + "\n"

        outpath = formatted_dir / filename
        with open(outpath, "w") as f:
            f.write(tex_str)
        logging.info(f"  Saved price .tex fragment: {outpath.name}")


def write_utilization_tex_files(utilization_results, pre_stats):
    """
    Write the 4 .tex row-fragment files Table D.11 (tab:Utilization) needs for log procedure
    utilization:
        RegTable_Utilization_3_2_sep25.tex            (Conley-Taber, III->II)
        RegTable_Utilization_2_1_sep25.tex            (Conley-Taber, II->I)
        DIDimpute_RegTable_Utilization_3_2_sep25.tex  (BJS imputation, III->II)
        DIDimpute_RegTable_Utilization_2_1_sep25.tex  (BJS imputation, II->I)

    Each file is 2 lines (estimate row + SE row), matching the format
    code/10c_generate_appendix_tables.py's _extract_method_row() reads (it locates the row by its
    "Conley--Taber" / "BJS Imputation" marker and takes that line plus the next). Row layout
    mirrors write_price_tex_files() exactly: label, pre-mean, All-CPTs estimate, Matched estimate,
    2 dash placeholder columns (trimmed away downstream to fit Table D.11's 4-column layout).

    Parameters:
        utilization_results: list of dicts (outcome == "log_q") with keys reclass_type, method
            ("Conley_Taber" / "BJS_imputation"), sample ("All CPTs" / "Matched"), Estimate,
            lower_CI, upper_CI.
        pre_stats: {reclass_type: (pre_mean, pre_std)} for log utilization -- shared by both
            method rows and both estimate columns (see main()).
    """
    formatted_dir = config.TABLES_DIR / "Formatted"
    formatted_dir.mkdir(parents=True, exist_ok=True)

    result_lookup = {}
    for r in utilization_results:
        key = (r["method"], r["reclass_type"], r["sample"])
        result_lookup[key] = r

    # Map: (method, reclass_type) -> (filename, row-label marker)
    TEX_FILENAMES = {
        ("Conley_Taber", "3_2"): ("RegTable_Utilization_3_2_sep25.tex", "Conley--Taber"),
        ("Conley_Taber", "2_1"): ("RegTable_Utilization_2_1_sep25.tex", "Conley--Taber"),
        ("BJS_imputation", "3_2"): ("DIDimpute_RegTable_Utilization_3_2_sep25.tex", "BJS Imputation"),
        ("BJS_imputation", "2_1"): ("DIDimpute_RegTable_Utilization_2_1_sep25.tex", "BJS Imputation"),
    }

    for (method, rtype), (filename, label) in TEX_FILENAMES.items():
        pre_mean, pre_std = pre_stats[rtype]
        pre_mean_str = _format_signed(pre_mean) if not np.isnan(pre_mean) else ""
        pre_std_str = f"({pre_std:.2f})" if not np.isnan(pre_std) else ""

        allcpt_r = result_lookup.get((method, rtype, "All CPTs"))
        matched_r = result_lookup.get((method, rtype, "Matched"))

        if allcpt_r is not None:
            ac_est = allcpt_r["Estimate"]
            ac_se = compute_se(ac_est, allcpt_r["lower_CI"], allcpt_r["upper_CI"])
            ac_stars = significance_stars(ac_est, ac_se)
            ac_est_str = f"{_format_signed(ac_est)}{ac_stars}"
            ac_se_str = f"({ac_se:.2f})"
        else:
            ac_est_str = ""
            ac_se_str = ""

        if matched_r is not None:
            m_est = matched_r["Estimate"]
            m_se = compute_se(m_est, matched_r["lower_CI"], matched_r["upper_CI"])
            m_stars = significance_stars(m_est, m_se)
            m_est_str = f"{_format_signed(m_est)}{m_stars}"
            m_se_str = f"({m_se:.2f})"
        else:
            m_est_str = ""
            m_se_str = ""

        lines = [
            f"\\hspace{{6mm}}{label} & {pre_mean_str}† "
            f"&{ac_est_str}&  {m_est_str} & - & -  \\\\",
            f" &{pre_std_str} & {ac_se_str} & {m_se_str} & - & - \\\\",
        ]
        tex_str = "\n".join(lines) + "\n"

        outpath = formatted_dir / filename
        with open(outpath, "w") as f:
            f.write(tex_str)
        logging.info(f"  Saved utilization .tex fragment: {outpath.name}")


def _verify_price_exhibits(run_started):
    """Return a list of reasons the price exhibits are not a complete product of THIS run.

    Split out of main() so it can be exercised directly: see
    certification/test_price_exhibit_guard.py, which checks that each clause binds by
    corrupting a complete set of outputs one way at a time.

    Existence of the output files is not enough: the two included price panels are
    committed and reused by design, an event-study period can be dropped without the
    file disappearing, and a table left by an earlier run exists just as well as a fresh
    one. Each clause below covers one way a manuscript exhibit could be missing a
    horizon, stale, or non-finite while the files are all present.
    """
    failures = []

    # (a) No Conley-Taber event-study period may have been dropped: a missing period is a
    #     hole in the grid of a manuscript figure.
    for f in _CT_ES_FAILURES:
        logging.error(
            "Price CT event study FAILED: %s / %s at event time %+d -- %s",
            f["reclass_type"], f["outcome"], f["event_time"], f["error"])
    if _CT_ES_FAILURES:
        failures.append(f"{len(_CT_ES_FAILURES)} Conley-Taber event-study period(s) failed")

    # (b) Per-horizon completeness of the event-study coefficient files. These are the
    #     exhibits' own numbers and they are rewritten on every run (including when the
    #     included figure is reused), so each must carry its FULL requested event-time
    #     grid -- the existence of the file says nothing about whether a period is missing.
    for reclass_type, window in PRICE_WINDOWS.items():
        expected = set(range(-window["low"], window["high"] + 1))
        path = (config.TABLES_DIR / "event_study_coefficients"
                / f"ES_coefs_price_{reclass_type}.csv")
        if not path.exists():
            failures.append(f"{path.name} absent")
            continue
        try:
            got = pd.read_csv(path)
        except Exception as e:
            failures.append(f"{path.name} unreadable: {e}")
            continue
        have = set(int(x) for x in got["ET"]) if "ET" in got.columns else set()
        if have != expected:
            logging.error(
                "%s is incomplete: expected event times %s, missing %s, unexpected %s",
                path.name, sorted(expected), sorted(expected - have), sorted(have - expected))
            failures.append(f"{path.name} incomplete")
        nonfinite = [c for c in ("Effect", "lower_CI", "upper_CI")
                     if c in got.columns and not np.isfinite(got[c].to_numpy(dtype=float)).all()]
        if nonfinite:
            logging.error("%s has non-finite values in %s", path.name, nonfinite)
            failures.append(f"{path.name} non-finite in {','.join(nonfinite)}")

    # (c) The estimate table must have been written BY THIS RUN, not merely be present.
    est_path = config.TABLES_DIR / "price_utilization_estimates.csv"
    if not est_path.exists():
        failures.append(f"{est_path.name} absent")
    elif est_path.stat().st_mtime < run_started:
        logging.error(
            "%s was not written by this run (mtime %.0f < run start %.0f): it is a stale "
            "copy from an earlier run.",
            est_path.name, est_path.stat().st_mtime, run_started)
        failures.append(f"{est_path.name} stale")

    # (d) The two included price panels. They are committed and deliberately reused
    #     unless FDA_FORCE_PRICE_FIGURES=1 (see produce_figures), so their presence is
    #     all that can be asserted when they are reused; when a regeneration was asked
    #     for, require that this run actually wrote them.
    for name in ("3_2_nolog_Price_solo_CTs_sept20_25.png",
                 "2_1_nolog_Price_solo_CTs_sept20_25.png"):
        p = config.FIGURES_DIR / name
        if not p.exists():
            failures.append(f"{name} absent")
        elif (os.environ.get("FDA_FORCE_PRICE_FIGURES") == "1"
              and p.stat().st_mtime < run_started):
            failures.append(f"{name} not regenerated despite FDA_FORCE_PRICE_FIGURES=1")
    return failures


def main():
    # Wall-clock start, used by the end-of-step guard to tell an exhibit this run wrote
    # from a stale copy an earlier run left behind.
    _run_started = time.time()

    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # ================================================================
    # Required inputs (fail closed)
    #
    # Both official routes supply the censored claims extract -- the
    # restricted route from the licensed extract, the simulated-data route
    # from the simulator -- so their absence means the run is not one of the
    # two supported routes, not that this step is optional. Every price and
    # utilization exhibit (Figures 4-5, Tables D.10-D.11) comes from here, so
    # a missing input aborts the step rather than leaving those exhibits
    # missing or stale.
    # ================================================================
    missing = _missing_claims_inputs()
    if missing:
        names = ", ".join(str(p) for p in missing)
        if os.environ.get(SKIP_MARKETSCAN_ENV) == "1":
            # Printed as well as logged: this banner is the ONLY thing that distinguishes an
            # exit 0 with no price exhibits from a successful reproduction, so it must reach
            # the console whatever the logging configuration. run_all.py scrubs this variable
            # from every step it launches, so reaching here means the script was invoked
            # directly with the opt-out set.
            banner = (
                "=" * 70 + "\n"
                f"{SKIP_MARKETSCAN_ENV}=1: skipping the whole price and utilization "
                f"analysis because {names} is absent.\n"
                "The run will NOT regenerate the price/utilization figures and tables "
                "(Figure 3c, Tables D.10-D.11), and its output is NOT a complete "
                "reproduction.\n" + "=" * 70
            )
            print(banner, flush=True)
            logging.warning(banner)
            return 0
        logging.error(
            f"Required claims extract not found: {names}. The price and utilization "
            "analysis cannot run. Supply the licensed MarketScan extract (restricted "
            "route) or materialize the simulated payload (simulated-data route); to "
            f"proceed deliberately without it, set {SKIP_MARKETSCAN_ENV}=1, which "
            "produces an incomplete reproduction."
        )
        return 1

    # ================================================================
    # Load data
    # ================================================================
    df_claims = load_claims_data()

    # Load matched samples for HCPCS crosswalk construction
    matched_21 = pd.read_csv(
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"]
    )
    matched_32 = pd.read_csv(
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat"]
    )

    # Build HCPCS crosswalk from GPT price links
    hcpcs_2_1, hcpcs_3_2 = load_hcpcs_crosswalk(matched_21, matched_32)

    # Human-expert concordance (robustness sample reported in the price footnote)
    hcpcs_2_1_exp, hcpcs_3_2_exp = load_expert_hcpcs_crosswalk(matched_21, matched_32)

    # ================================================================
    # Build panels — two per reclassification type
    #
    # "All CPTs" panels: used for column (2) in the manuscript table
    # "Matched" panels: used for column (3) in the manuscript table
    # ================================================================
    logging.info("Building All CPTs panels...")
    df_panel_21_allcpt = build_price_panel(df_claims, hcpcs_2_1, "2_1", "All CPTs")
    df_panel_32_allcpt = build_price_panel(df_claims, hcpcs_3_2, "3_2", "All CPTs")

    logging.info("Building Matched panels...")
    df_panel_21_matched = build_price_panel(df_claims, hcpcs_2_1, "2_1", "Matched")
    df_panel_32_matched = build_price_panel(df_claims, hcpcs_3_2, "3_2", "Matched")

    # Utilization-matched "All CPTs" panels: match on pre-treatment proc_count
    # (not prices). Utilization is right-skewed so matching uses log.
    logging.info("Building All CPTs panels (utilization-matched)...")
    df_panel_21_allcpt_util = build_price_panel(
        df_claims, hcpcs_2_1, "2_1", "All CPTs", match_on="proc_count"
    )
    df_panel_32_allcpt_util = build_price_panel(
        df_claims, hcpcs_3_2, "3_2", "All CPTs", match_on="proc_count"
    )

    # Human-expert concordance panels. Same estimating procedure as the preferred
    # "All CPTs" specification (treated procedures matched to controls drawn from
    # the full CPT universe on pre-event mean prices); only the device-type ->
    # procedure concordance differs.
    logging.info("Building Expert-concordance panels...")
    df_panel_21_expert = build_price_panel(df_claims, hcpcs_2_1_exp, "2_1", "All CPTs")
    df_panel_32_expert = build_price_panel(df_claims, hcpcs_3_2_exp, "3_2", "All CPTs")
    # ...and the device-type-matched control construction, the second control set
    # the data section describes, so the footnote's robustness claim can be read
    # against both control constructions rather than only the preferred one.
    df_panel_21_expert_m = build_price_panel(df_claims, hcpcs_2_1_exp, "2_1", "Matched")
    df_panel_32_expert_m = build_price_panel(df_claims, hcpcs_3_2_exp, "3_2", "Matched")

    # In-text sample-construction counts stated in the data section (JPE 2.2)
    emit_price_sample_construction_counts(
        df_claims, matched_21,
        expert_panels=(hcpcs_2_1_exp, hcpcs_3_2_exp),
        gpt_panels=(hcpcs_2_1, hcpcs_3_2),
        expert_estimating_panels=(df_panel_21_expert, df_panel_32_expert),
        gpt_estimating_panels=(df_panel_21_allcpt, df_panel_32_allcpt),
    )

    # ================================================================
    # Static DiD estimates (table rows)
    #
    # Price (BilledAmt): both BJS imputation and Conley-Taber, for
    #   each of two control samples (All CPTs and Matched).
    # Utilization (log_q): BJS + CT, using utilization-matched panels.
    # ================================================================
    logging.info("=" * 60)
    logging.info("Running static DiD estimates...")

    results = []
    price_results = []

    # Panels indexed by (reclass_type, sample_label)
    price_panels = [
        ("3_2", "All CPTs", df_panel_32_allcpt),
        ("3_2", "Matched", df_panel_32_matched),
        ("2_1", "All CPTs", df_panel_21_allcpt),
        ("2_1", "Matched", df_panel_21_matched),
        # Human-expert concordance robustness sample (price footnote).
        # "Expert" mirrors the preferred "All CPTs" control construction;
        # "Expert Matched" mirrors the device-type-matched control construction.
        ("3_2", "Expert", df_panel_32_expert),
        ("2_1", "Expert", df_panel_21_expert),
        ("3_2", "Expert Matched", df_panel_32_expert_m),
        ("2_1", "Expert Matched", df_panel_21_expert_m),
    ]

    for reclass_type, sample_label, df_panel in price_panels:
        N = len(df_panel.drop_duplicates(["PRODUCTCODE", "year"]))

        # Price — BJS imputation (for DIDimpute_ .tex files)
        est, lo, hi, ci_m = run_static_estimation(
            df_panel, PRICE_OUTCOME, reclass_type, use_bjs=True
        )
        if est is not None:
            rec = {
                "reclass_type": reclass_type,
                "outcome": PRICE_OUTCOME,
                "formal_name": OUTCOME_LABELS[PRICE_OUTCOME],
                "method": "BJS_imputation",
                "sample": sample_label,
                "Estimate": est,
                "lower_CI": lo,
                "upper_CI": hi,
                "ci_method": ci_m,
                "Sample Size": N,
            }
            results.append(rec)
            price_results.append(rec)

        # Price — Conley-Taber (for RegTable_ .tex files)
        est, lo, hi, ci_m = run_static_estimation(
            df_panel, PRICE_OUTCOME, reclass_type, use_bjs=False
        )
        if est is not None:
            rec = {
                "reclass_type": reclass_type,
                "outcome": PRICE_OUTCOME,
                "formal_name": OUTCOME_LABELS[PRICE_OUTCOME],
                "method": "Conley_Taber",
                "sample": sample_label,
                "Estimate": est,
                "lower_CI": lo,
                "upper_CI": hi,
                "ci_method": ci_m,
                "Sample Size": N,
            }
            results.append(rec)
            price_results.append(rec)

    # Utilization — Conley-Taber AND BJS imputation, for BOTH the utilization-matched "All CPTs"
    # panel and the device-outcome "Matched" panel (columns (2)/(3) of Table D.11, tab:Utilization).
    #
    # Both estimators are run on both panels so that all four (method x sample) cells Table D.11
    # needs -- Conley-Taber/All-CPTs, BJS/All-CPTs, Conley-Taber/Matched, BJS/Matched -- are
    # computed and written here, through the same run_static_estimation() call and use_bjs toggle
    # as the price loop above. The "Matched" utilization panels are the device-outcome-matched
    # panels already built for price (df_panel_32_matched / df_panel_21_matched); q/log_q are
    # computed for every panel.
    utilization_panels = {
        "3_2": {"All CPTs": df_panel_32_allcpt_util, "Matched": df_panel_32_matched},
        "2_1": {"All CPTs": df_panel_21_allcpt_util, "Matched": df_panel_21_matched},
    }
    utilization_results = []
    util_pre_stats = {}
    for reclass_type, samples in utilization_panels.items():
        allcpt_panel = samples["All CPTs"]

        # Pre-treatment means (unlogged and logged) are computed once from the All-CPTs-matched
        # utilization panel. The treated units -- and hence their pre-period means -- are the same
        # regardless of which control sample (All CPTs vs Matched) is used for the DiD estimate,
        # and Table D.11 shows a single Pre-mean column shared by both method rows and both
        # estimate columns.
        util_pre_mean, util_pre_std = compute_pre_treatment_utilization_stats(
            allcpt_panel, UTILIZATION_OUTCOME
        )
        log_pre_mean, log_pre_std = compute_pre_treatment_utilization_stats(
            allcpt_panel, LOG_UTILIZATION_OUTCOME
        )
        util_pre_stats[reclass_type] = (log_pre_mean, log_pre_std)
        logging.info(
            f"  Utilization pre-event mean ({reclass_type}): "
            f"{util_pre_mean:,.1f} (SD={util_pre_std:,.1f})"
        )
        logging.info(
            f"  Log utilization pre-event mean ({reclass_type}): "
            f"{log_pre_mean:.3f} (SD={log_pre_std:.3f})"
        )

        for sample_label, df_panel in samples.items():
            N = len(df_panel.drop_duplicates(["PRODUCTCODE", "year"]))

            for method, use_bjs in (("Conley_Taber", False), ("BJS_imputation", True)):
                # Level utilization (q): retained All-CPTs/Conley-Taber only, matching prior
                # behavior -- Table D.11 reports LOG utilization, so level utilization does not
                # need the full 4-combo coverage; kept here only for CSV documentation continuity.
                if sample_label == "All CPTs" and method == "Conley_Taber":
                    est, lo, hi, ci_m = run_static_estimation(
                        df_panel, UTILIZATION_OUTCOME, reclass_type, use_bjs=use_bjs
                    )
                    if est is not None:
                        results.append({
                            "reclass_type": reclass_type,
                            "outcome": UTILIZATION_OUTCOME,
                            "formal_name": OUTCOME_LABELS[UTILIZATION_OUTCOME],
                            "method": method,
                            "sample": sample_label,
                            "Estimate": est,
                            "lower_CI": lo,
                            "upper_CI": hi,
                            "ci_method": ci_m,
                            "Sample Size": N,
                            "pre_mean": util_pre_mean,
                            "pre_std": util_pre_std,
                        })

                # Log utilization (log_q): ALL FOUR method x sample combos -- feeds Table D.11
                # columns (2) All CPTs / (3) Matched, both the Conley-Taber and BJS Imputation rows.
                est, lo, hi, ci_m = run_static_estimation(
                    df_panel, LOG_UTILIZATION_OUTCOME, reclass_type, use_bjs=use_bjs
                )
                if est is not None:
                    rec = {
                        "reclass_type": reclass_type,
                        "outcome": LOG_UTILIZATION_OUTCOME,
                        "formal_name": OUTCOME_LABELS[LOG_UTILIZATION_OUTCOME],
                        "method": method,
                        "sample": sample_label,
                        "Estimate": est,
                        "lower_CI": lo,
                        "upper_CI": hi,
                        "ci_method": ci_m,
                        "Sample Size": N,
                        "pre_mean": log_pre_mean,
                        "pre_std": log_pre_std,
                    }
                    results.append(rec)
                    utilization_results.append(rec)

    if results:
        df_results = pd.DataFrame(results)
        outpath = config.TABLES_DIR / "price_utilization_estimates.csv"
        df_results.to_csv(outpath, index=False)
        logging.info(f"Saved estimate table: {outpath}")

    # ================================================================
    # Write .tex row-fragment files for the manuscript price tables
    # ================================================================
    logging.info("=" * 60)
    logging.info("Writing price .tex row-fragment files...")
    write_price_tex_files(
        price_results, df_panel_32_allcpt, df_panel_21_allcpt
    )

    logging.info("Writing utilization .tex row-fragment files...")
    write_utilization_tex_files(utilization_results, util_pre_stats)

    # ================================================================
    # Event study figures (use All CPTs panels for the main figures)
    # ================================================================
    logging.info("=" * 60)
    logging.info("Producing event study figures...")
    produce_figures(df_panel_21_allcpt, df_panel_32_allcpt)

    # ================================================================
    # Fail closed on the exhibits themselves.
    #
    # Returning 0 here is a claim that this step produced the price and utilization
    # exhibits. The ONLY circumstance in which this step may exit 0 without them is the
    # documented opt-out above, which prints a banner and returns 0 there -- it never
    # reaches this point. Anything missing here is therefore a silent failure, and the
    # step must fail rather than let the run report success without Figure 3c.
    # ================================================================
    failures = _verify_price_exhibits(_run_started)
    if failures:
        logging.error(
            "Price analysis is INCOMPLETE: %s. This step may exit 0 without the price "
            "exhibits ONLY under the documented %s=1 opt-out, which returns earlier and prints "
            "a banner. Failing rather than reporting a successful run with missing, stale or "
            "incomplete exhibits.",
            "; ".join(failures), SKIP_MARKETSCAN_ENV)
        return 1

    logging.info("Price analysis complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
