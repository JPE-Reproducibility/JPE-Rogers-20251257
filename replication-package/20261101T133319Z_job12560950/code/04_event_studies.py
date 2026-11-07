#!/usr/bin/env python
"""
04_event_studies.py -- Event study figures for all panels x reclassification types.

Produces event-study coefficient plots for innovation, adverse events, safety,
and utilization outcomes, for both II->I and III->II reclassification events.

For II->I:  Uses R-based estimation (fixest::feols with clustered SEs) via
            run_feols_es_2to1 / run_feols_es_2to1_utilization.
For III->II: Uses ConleyTaberStackedES per event-time period, iterating over
            the event window and calling conley_taber_stacked_es for each.

Inputs:
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_2_1_onepat_innovation.csv
    data/derived/matched_sample_3_2_onepat.csv
    data/derived/matched_sample_3_2_onepat_innovation.csv
    data/derived/matched_sample_3_2_onepat_innovation_quality.csv
    data/derived/safety_did_analysis.csv            (from 06a_safety_analysis.py)
    data/derived/safety_did_analysis_3_2.csv        (from 06a_safety_analysis.py)
    data/derived/constrained_adv_event_new_sept25.csv
    data/derived/constrained_adv_event_new_sept25_3_2.csv
Outputs:
    output/figures/<reclass_type>_nolog_<outcome>_oct22_24.png
    output/figures/<reclass_type>_nolog_<outcome>_restrict_oct22_24.png
    output/figures/unreported/<reclass_type>_nolog_<outcome>_{intuitive,later}_oct22_24.png
        (the "not shown" alternative-control-group event studies)
    output/tables/event_study_coefficients/ES_coefs_<reclass_type>_<outcome>[_<suffix>].csv
    output/tables/event_study_base_rates.csv
        (the treated pre-event base rates printed as \\put overlays on the
         manuscript's event-study figures; see MANUSCRIPT_BASE_RATE_FIGURES)
"""

import os
import sys
import logging
import time
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked_es
from estimation import (
    run_feols_es_2to1,
    run_feols_es_2to1_utilization,
    source_r_scripts,
)
from plotting import (
    create_figure,
    plot_event_study,
    plot_no_data_panel,
    save_figure,
)

np.random.seed(config.RANDOM_SEED)
warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "04_event_studies.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Figure specifications — replaces manual flag toggling in the notebook
# ============================================================================
# Each dict defines one event-study figure. Fields:
#   outcome       — variable name in the DataFrame
#   label         — human-readable axis / title label
#   panel         — which panel type ('Innovation', 'Adverse_Events', 'Safety',
#                   'Utilization')
#   reclass_type  — '2_1' or '3_2'
#   window_low    — number of pre-event periods to display
#   window_high   — number of post-event periods to display
#   matched_file  — which matched sample CSV to load (key into config.MATCHED_SAMPLES)
#   restrict_utilization — whether to restrict to utilization-available PCs
# ============================================================================

FIGURE_SPECS = [
    # ========================================================================
    # Innovation panel — II->I
    # ========================================================================
    {"outcome": "real_pats",     "label": "Patenting Rate",
     "panel": "Innovation", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "matched_file": "2_1_onepat_innovation"},
    {"outcome": "dev_count",     "label": "Device Submission Rate",
     "panel": "Innovation", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "matched_file": "2_1_onepat_innovation",
     "no_data": True,
     "filename_override": "2_1_nolog_dev_count_solo.png"},   # FDA does not gather comparable data for Class I

    # ========================================================================
    # Innovation panel — III->II
    # ========================================================================
    {"outcome": "real_pats",     "label": "Patenting Rate",
     "panel": "Innovation", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation"},
    {"outcome": "dev_count",     "label": "Device Submission Rate",
     "panel": "Innovation", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation"},

    # ========================================================================
    # Market Composition panel — II->I
    # ========================================================================
    {"outcome": "unique_firms",  "label": "New Entry (pat.)",
     "panel": "MarketComposition", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "matched_file": "2_1_onepat_innovation"},
    {"outcome": "firm_expansion_patents",  "label": "Incumb. Entry (pat.)",
     "panel": "MarketComposition", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "matched_file": "2_1_onepat_innovation"},

    # ========================================================================
    # Market Composition panel — III->II
    # ========================================================================
    {"outcome": "unique_firms",  "label": "New Entry (pat.)",
     "panel": "MarketComposition", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation",
     "filename_override": "3_2_nolog_unique_firms_solo_CTs.png"},
    {"outcome": "absnew_firm_count",  "label": "New Entry (dev.)",
     "panel": "MarketComposition", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation"},
    {"outcome": "firm_expansion",  "label": "Incumb. Entry (dev.)",
     "panel": "MarketComposition", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation"},
    {"outcome": "firm_expansion_patents",  "label": "Incumb. Entry (pat.)",
     "panel": "MarketComposition", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation"},

    # ========================================================================
    # Nodrugs restricted sample — III->II
    # ========================================================================
    {"outcome": "patents_pats_nodrugs",  "label": "Patenting Rate (No Drugs/A61)",
     "panel": "Innovation", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation"},

    # ========================================================================
    # Adverse Events panel — II->I
    # ========================================================================
    {"outcome": "v_serious",  "label": "Serious Event Rate",
     "panel": "Adverse_Events", "reclass_type": "2_1",
     "window_low": 4, "window_high": 15,
     "matched_file": "2_1_onepat"},

    # ========================================================================
    # Adverse Events panel — III->II
    # ========================================================================
    {"outcome": "v_serious",  "label": "Serious Event Rate",
     "panel": "Adverse_Events", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat"},

    # ========================================================================
    # Adverse Events subtypes: Hospitalizations (H) and Deaths (D)
    # These per-subtype event studies mirror the combined
    # v_serious Adverse_Events specs above (same panel/reclass/window/matched_file, outcome column only
    # differs; the matched-sample df already carries L/H/D/S columns -- see load_matched_sample /
    # v_serious construction). They are "not shown" in the paper (Results footnote) but their ES_coefs
    # (treated/control means by event time) feed 15_intext_derived_numbers.py's counterfactual
    # hospitalization/death % reductions and the H=-1.77/yr, D=-0.43/yr level estimates. They are
    # required: step 35 reads their ES_coefs.
    # ========================================================================
    {"outcome": "H",  "label": "Hospitalizations",
     "panel": "Adverse_Events", "reclass_type": "2_1",
     "window_low": 4, "window_high": 15,
     "matched_file": "2_1_onepat"},
    {"outcome": "D",  "label": "Deaths",
     "panel": "Adverse_Events", "reclass_type": "2_1",
     "window_low": 4, "window_high": 15,
     "matched_file": "2_1_onepat"},
    {"outcome": "H",  "label": "Hospitalizations",
     "panel": "Adverse_Events", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat"},
    {"outcome": "D",  "label": "Deaths",
     "panel": "Adverse_Events", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat"},

    # ========================================================================
    # Safety panel — II->I and III->II
    # ========================================================================
    {"outcome": "safety_prop", "label": "Safety Emphasis",
     "panel": "Safety", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "safety_file": "safety_did_2_1"},

    # ========================================================================
    # Utilization panel — II->I (restrict_utilization=True)
    # ========================================================================
    {"outcome": "v_serious",  "label": "Serious Event Rate",
     "panel": "Utilization", "reclass_type": "2_1",
     "window_low": 2, "window_high": 10,
     "matched_file": "2_1_onepat",
     "restrict_utilization": True},

    # ========================================================================
    # Petitioned subsample — III->II (Fig D.3)
    # ========================================================================
    {"outcome": "real_pats",  "label": "Patenting Rate",
     "panel": "Innovation", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "matched_file": "3_2_onepat_innovation_petitioned",
     "filename_suffix": "petitioned"},

    # ========================================================================
    # Normalizable subset — II->I (Fig D.9a)
    # ========================================================================
    {"outcome": "v_serious",  "label": "Serious Event Rate",
     "panel": "Adverse_Events", "reclass_type": "2_1",
     "window_low": 2, "window_high": 10,
     "matched_file": "2_1_onepat",
     "restrict_utilization": True,
     "normalizable": True,
     "filename_suffix": "normalizable"},

    # ========================================================================
    # Voluntary reporters — II->I (Fig D.17a)
    # ========================================================================
    {"outcome": "v_serious",  "label": "Serious Event Rate (Voluntary)",
     "panel": "Adverse_Events", "reclass_type": "2_1",
     "window_low": 4, "window_high": 15,
     "matched_file": "2_1_onepat",
     "reporter_filter": "voluntary",
     "filename_suffix": "voluntary"},

    # ========================================================================
    # Manufacturer reporters — II->I (Fig D.17b)
    # ========================================================================
    {"outcome": "v_serious",  "label": "Serious Event Rate (Manufacturer)",
     "panel": "Adverse_Events", "reclass_type": "2_1",
     "window_low": 4, "window_high": 15,
     "matched_file": "2_1_onepat",
     "reporter_filter": "manufacturer",
     "filename_suffix": "manuf"},

    # ========================================================================
    # Alternative control groups — "not shown" in the paper.
    #
    # The parallel-trends footnote states: "Event study coefficients are similar
    # to those estimated using the intuitive and later-treated controls (not
    # shown)." These four specs are the producing program for that claim: they
    # estimate the same event study on the intuitive and later-treated control
    # pools (the pooled DiD on those pools is in 03a_estimation_3to2.py /
    # 03b_estimation_2to1.py), writing coefficients to
    # output/tables/event_study_coefficients/ES_coefs_*_{intuitive,later}.csv and
    # figures to output/figures/unreported/ (they are not manuscript exhibits).
    # The outcome is the patenting rate — the outcome of the figure the footnote
    # attaches to (Figure "Effect of Reclassification on Innovation").
    # ========================================================================
    {"outcome": "real_pats", "label": "Patenting Rate (Intuitive Controls)",
     "panel": "Innovation", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "control_group": "intuitive",
     "filename_suffix": "intuitive",
     "figure_subdir": "unreported"},
    {"outcome": "real_pats", "label": "Patenting Rate (Later-Treated Controls)",
     "panel": "Innovation", "reclass_type": "3_2",
     "window_low": 10, "window_high": 10,
     "control_group": "later",
     "filename_suffix": "later",
     "figure_subdir": "unreported"},
    {"outcome": "real_pats", "label": "Patenting Rate (Intuitive Controls)",
     "panel": "Innovation", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "control_group": "intuitive",
     "filename_suffix": "intuitive",
     "figure_subdir": "unreported"},
    {"outcome": "real_pats", "label": "Patenting Rate (Later-Treated Controls)",
     "panel": "Innovation", "reclass_type": "2_1",
     "window_low": 10, "window_high": 10,
     "control_group": "later",
     "filename_suffix": "later",
     "figure_subdir": "unreported"},
]


# ============================================================================
# Helpers
# ============================================================================

def _is_adverse_or_nonanticipation(outcome):
    """Return True if this outcome uses no-anticipation timing."""
    return outcome in config.ANTICIPATION["no_anticipation"]


def _get_anticipation(outcome, reclass_type):
    """Return anticipation window (years) for a given outcome."""
    if _is_adverse_or_nonanticipation(outcome):
        return 0
    return config.ANTICIPATION[reclass_type]


def getNewPostTreat(df, i):
    """
    Create a posttreat_new indicator that equals 1 at exactly event-time i.

    Applied per product code group to identify a single event-time period
    for the Conley-Taber event-study loop.

    The indicator is selected on the ET column: the one treated row of the group whose
    ET equals i is marked, a control group (no posttreat == 1 row) gets an all-zero
    indicator, a target outside the group's observed window marks nothing, and a group
    with two rows at the same event time is an error rather than an arbitrary choice.
    """
    df = df.copy()
    df["posttreat_new"] = 0
    if "ET" not in df.columns or "posttreat" not in df.columns:
        raise KeyError(
            f"getNewPostTreat requires 'ET' and 'posttreat' columns; got {list(df.columns)}")

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
            f"getNewPostTreat: {n_hit} rows at ET={i} for group {pc}; the event-time "
            "indicator must mark exactly one row per group")
    df.loc[hit, "posttreat_new"] = 1
    return df


# ============================================================================
# Data loading
# ============================================================================

def _stack_control_group(df):
    """Build the stacked (episode x unit) FE structure for an alternative control
    pool, exactly as 03a_estimation_3to2.load_samples() does for the intuitive and
    later-treated samples: every treated product code gets its own episode index,
    and the full control pool is duplicated once per episode."""
    df = df.copy()
    df["FE"] = np.nan
    df.loc[df.treatment == 0, "FE"] = 0
    df_orig = df.copy()
    parts = []
    for i, PC in enumerate(np.unique(df_orig[df_orig.treatment == 1]["PRODUCTCODE"])):
        if i > 0:
            controls = df_orig[df_orig.treatment == 0].copy()
            controls["FE"] = i
            parts.append(controls)
        df.loc[df.PRODUCTCODE == PC, "FE"] = i
    if parts:
        df = pd.concat([df] + parts, ignore_index=True)
    return df


def load_control_group_sample(spec):
    """Load an ALTERNATIVE-control-group panel (intuitive or later-treated).

    These are the same pools 03a/03b use for their pooled DiD columns; here they
    are prepared for the event-study estimators. The preparation mirrors
    03a_estimation_3to2.load_samples() (III->II, CSV inputs) and
    03b_estimation_2to1.load_samples() (II->I, parquet inputs with stacked FEs
    already built) so the event study runs on exactly the pooled-DiD sample.
    """
    reclass_type = spec["reclass_type"]
    group = spec["control_group"]           # "intuitive" or "later"
    if reclass_type == "3_2":
        key = "intuitive_3_2" if group == "intuitive" else "later_treated_3_2"
        df = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES[key],
                         low_memory=False)
        df["year_reclassified"] = df["year_reclassified_3_2"]
        df["treatment"] = 0
        df.loc[df.year_reclassified.notnull(), "treatment"] = 1
        if "FDA_own_accord_3_2" in df.columns:
            df["FDA_own_accord"] = df["FDA_own_accord_3_2"]
        df = _stack_control_group(df)
    else:
        key = "data_2_1_intuitive" if group == "intuitive" else "data_2_1_latertreat"
        df = pd.read_parquet(config.DERIVED_DATA_DIR / config.PARQUET_FILES[key])
        df["year_reclassified"] = df["year_reclassified_2_1"]
        df["treatment"] = 0
        df.loc[df.year_reclassified.notnull(), "treatment"] = 1
        # The 2_1 parquets already carry the stacked FE column built in 02/03b.
        if "FE" not in df.columns:
            df = _stack_control_group(df)

    df = df[df.year != 0].reset_index(drop=True)
    # `factorized` (unit id within episode) is required by prepare_class_by_episode.
    if "factorized" not in df.columns or df["factorized"].isna().any():
        df["factorized"] = df["PRODUCTCODE"].astype("category").cat.codes
    return df


def load_matched_sample(spec):
    """Load and prepare the matched sample DataFrame for a figure spec."""
    reclass_type = spec["reclass_type"]

    # Safety panel reads from pre-built safety DiD file
    if spec["panel"] == "Safety":
        safety_key = spec["safety_file"]
        df = pd.read_csv(config.DERIVED_DATA_DIR / config.SAFETY_FILES[safety_key])
        return df

    # Alternative control pools (intuitive / later-treated); "not shown" specs.
    if spec.get("control_group"):
        df = load_control_group_sample(spec)
    else:
        # Standard matched sample
        matched_key = spec["matched_file"]
        df = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[matched_key])

    # Ensure derived columns exist
    if "patents_allpats" in df.columns:
        df["real_pats"] = df["patents_allpats"]
    if "patents_newfirm" in df.columns:
        df["unique_firms"] = df["patents_newfirm"]
    if "patents_newfirmPC" in df.columns:
        df["unique_firmsPC"] = df["patents_newfirmPC"]
    if "times_cited" in df.columns:
        df["times_cited"] = df["times_cited"].fillna(0)
    if "xi_real" in df.columns:
        df["xi_real"] = df["xi_real"].fillna(0)
        df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019
    if "unique_firmsPC" in df.columns and "unique_firms" in df.columns:
        df["firm_expansion_patents"] = df["unique_firmsPC"] - df["unique_firms"]
    if "dev_count" in df.columns:
        df["dev_count"] = df["dev_count"].fillna(0)
    if "firm_count" in df.columns:
        df["firm_count"] = df["firm_count"].fillna(0)
    if "absnew_firm_count" in df.columns:
        df["absnew_firm_count"] = df["absnew_firm_count"].fillna(0)
    if "firm_count" in df.columns and "absnew_firm_count" in df.columns:
        df["firm_expansion"] = df["firm_count"] - df["absnew_firm_count"]

    # Construct v_serious if adverse event columns present
    for col in ["L", "H", "D", "S"]:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    if all(c in df.columns for c in ["L", "H", "D", "S"]):
        df["v_serious"] = df["L"] + df["H"] + df["D"] + df["S"]

    return df


def prepare_event_time(df, spec):
    """
    Prepare event-time indicators (ET, posttreat) on the DataFrame.

    For II->I:
        innovation outcomes: ET = year - year_reclass_ET + 1 (anticipation offset)
        adverse/utilization: ET = year - year_reclass_ET
    For III->II:
        innovation outcomes: ET = year - year_reclass_ET + 2
        adverse/utilization: ET = year - year_reclass_ET
    """
    outcome = spec["outcome"]
    reclass_type = spec["reclass_type"]
    panel = spec["panel"]

    # Ensure controls have no year_reclassified
    df.loc[df.treatment == 0, "year_reclassified"] = np.nan

    # Compute cohort-level reclassification year
    df["year_reclass_ET"] = df.groupby(["FE"])["year_reclassified"].transform(
        pd.Series.max
    )

    # Adverse events / utilization / no-anticipation outcomes: no offset
    anticipation = _get_anticipation(outcome, reclass_type)
    if _is_adverse_or_nonanticipation(outcome):
        df["ET"] = df["year"] - df["year_reclass_ET"]
    else:
        # Innovation outcomes get anticipation offset
        if reclass_type == "2_1":
            df["ET"] = df["year"] - df["year_reclass_ET"] + 1
        else:  # 3_2
            df["ET"] = df["year"] - df["year_reclass_ET"] + 2

    # Controls get ET = 0
    df.loc[df.treatment == 0, "ET"] = 0

    # Set posttreat with anticipation window
    if _is_adverse_or_nonanticipation(outcome):
        # Posttreat already set from matched sample; ensure it exists
        if "posttreat" not in df.columns:
            df["posttreat"] = 0
            df.loc[
                (df.treatment == 1) & (df.year >= df.year_reclassified),
                "posttreat",
            ] = 1
    else:
        df["posttreat"] = 0
        df.loc[
            (df.treatment == 1)
            & (df.year >= df.year_reclassified - anticipation),
            "posttreat",
        ] = 1

    return df


def prepare_class_by_episode(df):
    """Build the class_by_episode grouping variable and sort."""
    df["class_by_episode"] = (
        df["FE"].astype(str) + "[SEP]" + df["factorized"].astype(str)
    )
    df["class_by_episode"] = df.class_by_episode.astype("category").cat.codes
    df = df.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)
    return df


def apply_utilization_restriction_2_1(df, outcome, normalizable=False):
    """
    Apply utilization restriction for II->I: merge proc_count, normalize
    outcome by procedure count, restrict year range, and match controls.

    If normalizable=True, skip year restriction and normalization but still
    filter to PCs with utilization data and perform nearest-neighbor matching.
    """
    # proc_count comes from the constrained price panel that gen_02_price_matching.py
    # builds from the outpatient claims extract.
    util_devs_all = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["constrained_adv_event"]
    ).drop_duplicates(subset=["PRODUCTCODE", "year"])
    util_devs_all["year"] = util_devs_all["year"].astype(float)

    # Merge procedure count
    df = pd.merge(
        df,
        util_devs_all[["PRODUCTCODE", "proc_count", "year"]],
        on=["year", "PRODUCTCODE"],
        how="left",
    )

    # Restrict year range and normalize (skip if normalizable)
    if not normalizable:
        df = df[(df.year > 1995) & (df.year < 2014)]
        df[outcome] = df[outcome] / df["proc_count"]

    # Keep only PCs with utilization data
    df = df[df.PRODUCTCODE.isin(util_devs_all["PRODUCTCODE"].values)]

    # Nearest-neighbor matching on outcome at baseline (1997)
    group_means = (
        df[df["year"] == 1997]
        .groupby(["PRODUCTCODE"])
        .mean(numeric_only=True)
        .reset_index()
    )
    treated_groups = (
        group_means.loc[
            group_means["treatment"] == 1, ["PRODUCTCODE", outcome]
        ]
        .rename(columns={outcome: "metric"})
        .dropna(subset=["metric"])
        .reset_index(drop=True)
    )
    control_groups = (
        group_means.loc[
            group_means["treatment"] == 0, ["PRODUCTCODE", outcome]
        ]
        .rename(columns={outcome: "metric"})
        .dropna(subset=["metric"])
        .reset_index(drop=True)
    )

    # Greedy matching without replacement: each control used at most once
    pairs_nr = []
    available = set(control_groups.index)
    for t_pc, t_val in zip(
        treated_groups["PRODUCTCODE"], treated_groups["metric"]
    ):
        if len(available) == 0:
            break
        d = (control_groups.loc[list(available), "metric"] - t_val).abs()
        choose = d.nsmallest(min(3, len(d))).index.tolist()
        for idx in choose:
            pairs_nr.append((t_pc, control_groups.loc[idx, "PRODUCTCODE"]))
        available.difference_update(choose)

    chosen = pd.DataFrame(pairs_nr, columns=["TREATED_PC", "CONTROL_PC"])
    chosen_controls = set(chosen["CONTROL_PC"].unique())
    df = df[
        (df["treatment"] == 1) | (df["PRODUCTCODE"].isin(chosen_controls))
    ]

    return df


def apply_utilization_restriction_3_2(df, outcome):
    """
    Apply utilization restriction for III->II: merge proc_count, normalize
    outcome by procedure count, restrict year range.
    """
    util_devs_all = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["constrained_adv_event_3_2"]
    )
    util_devs_all["year"] = util_devs_all["year"].astype(float)

    # Merge procedure count
    df = pd.merge(
        df,
        util_devs_all[["PRODUCTCODE", "proc_count", "year"]],
        on=["year", "PRODUCTCODE"],
        how="left",
    )

    # Restrict year range and normalize
    df = df[(df.year > 1995) & (df.year < 2014)]
    df[outcome] = df[outcome] / df["proc_count"]

    # Keep only PCs with utilization data
    df = df[df.PRODUCTCODE.isin(util_devs_all["PRODUCTCODE"].values)]

    return df


def apply_normalizable_filter(df, reclass_type):
    """
    Filter the matched sample to only include product codes present in the
    constrained adverse event data (i.e., product codes for which utilization
    data exists), but do NOT normalize by procedure count.

    This produces the "normalizable" subset used in robustness checks.
    """
    if reclass_type == "2_1":
        adv_key = "constrained_adv_event"
    else:
        adv_key = "constrained_adv_event_3_2"

    util_devs_all = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES[adv_key]
    )
    df = df[df.PRODUCTCODE.isin(util_devs_all["PRODUCTCODE"].values)]
    return df.reset_index(drop=True)


def apply_reporter_filter(df, reporter_filter):
    """
    Recompute v_serious from reporter-type-specific adverse event columns.

    reporter_filter='manufacturer':
        v_serious = D_M + S_M + H_M + L_M
    reporter_filter='voluntary':
        v_serious = (D_U + S_U + H_U + L_U)      (user)
                  + (D_P + S_P + H_P + L_P)      (voluntary/patient)
                  + (D_D + S_D + H_D + L_D)      (distributor)
    """
    if reporter_filter == "manufacturer":
        for col in ["D_M", "S_M", "H_M", "L_M"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        df["v_serious"] = df["D_M"] + df["S_M"] + df["H_M"] + df["L_M"]
    elif reporter_filter == "voluntary":
        for col in ["D_U", "S_U", "H_U", "L_U",
                     "D_P", "S_P", "H_P", "L_P",
                     "D_D", "S_D", "H_D", "L_D"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        df["v_serious_user"] = df["D_U"] + df["S_U"] + df["H_U"] + df["L_U"]
        df["v_serious_voluntary"] = df["D_P"] + df["S_P"] + df["H_P"] + df["L_P"]
        df["v_serious_distributor"] = df["D_D"] + df["S_D"] + df["H_D"] + df["L_D"]
        df["v_serious"] = (
            df["v_serious_user"]
            + df["v_serious_voluntary"]
            + df["v_serious_distributor"]
        )
    else:
        raise ValueError(f"Unknown reporter_filter: {reporter_filter}")

    df.loc[df.v_serious.isnull(), "v_serious"] = 0
    return df


# ============================================================================
# Estimation routines
# ============================================================================

def estimate_event_study_2to1(df, spec):
    """
    Estimate event study for II->I using R-based fixest::feols.

    Returns a DataFrame with columns: ET, Effect, SE.
    """
    outcome = spec["outcome"]
    window_low = spec["window_low"]
    window_high = spec["window_high"]
    restrict_util = spec.get("restrict_utilization", False)

    # Select R estimation function
    if restrict_util:
        r_func = run_feols_es_2to1_utilization
    else:
        r_func = run_feols_es_2to1

    # Columns needed by R
    cols = [
        outcome, "year_reclassified", "treatment", "factorized",
        "year", "FE", "ET", "class_by_episode",
    ]
    static, ses = r_func(df[cols], outcome)

    # Compute index slicing based on ET range
    index_int_low = int(-df["ET"].min() - window_low)
    index_int_high = int(-df["ET"].min() + window_high)

    static = static[index_int_low:index_int_high]
    ses = ses[index_int_low:index_int_high]

    # Build results DataFrame
    estimates_df = pd.DataFrame()
    estimates_df["ET"] = np.arange(-window_low, window_high + 1, 1)

    # Insert zero at the reference period (-1)
    static = np.insert(static, window_low - 1, 0)
    ses = np.insert(ses, window_low - 1, 0)

    estimates_df["Effect"] = static
    estimates_df["SE"] = ses

    return estimates_df


def estimate_event_study_3to2(df, spec):
    """
    Estimate event study for III->II using Conley-Taber permutation inference.

    Iterates over each event-time period in the window, calling
    conley_taber_stacked_es for each.

    Returns a DataFrame with columns: ET, Effect, lower_cb, upper_cb, SE.
    """
    outcome = spec["outcome"]
    window_low = spec["window_low"]
    window_high = spec["window_high"]

    n_periods = window_low + window_high + 1
    estimates = np.zeros(n_periods)
    lower_cb = np.zeros(n_periods)
    upper_cb = np.zeros(n_periods)

    cols = [
        outcome, "posttreat_new", "treatment", "factorized",
        "year", "FE", "ET", "class_by_episode", "PRODUCTCODE",
    ]

    for i, num in enumerate(np.arange(-window_low, window_high + 1, 1)):
        if num == -1:
            # Reference period: zero by construction
            estimates[i], lower_cb[i], upper_cb[i] = 0, 0, 0
        else:
            # Apply getNewPostTreat per product code group
            df_new = df.groupby("PRODUCTCODE", group_keys=False).apply(
                getNewPostTreat, num
            )

            # Compute index for event-time coefficient
            index_int = int(-df_new["ET"].min() + num)
            if num > -1:
                index_int -= 1

            logging.info(
                f"  CT-ES period {num}: index_int={index_int}"
            )

            est, low, high = conley_taber_stacked_es(
                df_new[cols].reset_index(drop=True),
                outcome,
                "posttreat_new",
                "treatment",
                "class_by_episode",
                "year",
                index_int,
                seed=config.RANDOM_SEED,
            )
            estimates[i] = est
            lower_cb[i] = low
            upper_cb[i] = high

            logging.info(
                f"  CT-ES period {num}: est={est}, CI=[{low}, {high}]"
            )

    # Build results DataFrame
    estimates_df = pd.DataFrame()
    estimates_df["ET"] = np.arange(-window_low, window_high + 1, 1)
    estimates_df["Effect"] = estimates
    estimates_df["lower_cb"] = lower_cb
    estimates_df["upper_cb"] = upper_cb

    # Derive SE from CIs
    estimates_df["SE"] = 0.0
    for idx, row in estimates_df.iterrows():
        if row["Effect"] < 0:
            estimates_df.loc[idx, "SE"] = (row["upper_cb"] - row["Effect"]) / 1.96
        else:
            estimates_df.loc[idx, "SE"] = (row["Effect"] - row["lower_cb"]) / 1.96

    return estimates_df


# ============================================================================
# Plotting
# ============================================================================

def plot_and_save(estimates_df, spec):
    """Create event-study figure and save to disk."""
    outcome = spec["outcome"]
    reclass_type = spec["reclass_type"]
    label = spec["label"]
    restrict_util = spec.get("restrict_utilization", False)

    fig, ax = create_figure(nrows=1, ncols=1, figsize=(12, 8))

    event_times = estimates_df["ET"].values
    effects = estimates_df["Effect"].values.astype(float)
    ses = estimates_df["SE"].values.astype(float)

    # Always pass CI bounds (regression-based or Conley-Taber).
    # plot_event_study() derives symmetric SEs from these bounds
    # so estimates are always centered within the displayed bands.
    if reclass_type == "3_2" and "lower_cb" in estimates_df.columns:
        lower_cis = estimates_df["lower_cb"].values.astype(float)
        upper_cis = estimates_df["upper_cb"].values.astype(float)
    else:
        lower_cis = effects - 1.96 * ses
        upper_cis = effects + 1.96 * ses

    plot_event_study(
        ax, event_times, effects, lower_cis, upper_cis,
        reclass_type, outcome_label=label,
        ref_period=-1,
    )

    # Set x-ticks at intervals of 2
    ax.set_xticks(
        np.arange(
            min(event_times),
            max(event_times) + 1,
            2.0,
        )
    )

    # Build output filename (suffix takes priority over restrict_util flag)
    suffix = spec.get("filename_suffix", "")
    if suffix:
        filename = f"{reclass_type}_nolog_{outcome}_{suffix}_oct22_24.png"
    elif restrict_util:
        filename = f"{reclass_type}_nolog_{outcome}_restrict_oct22_24.png"
    else:
        filename = f"{reclass_type}_nolog_{outcome}_oct22_24.png"

    # filename_override takes absolute priority
    filename = spec.get("filename_override", filename)

    # Specs that are not manuscript exhibits ("not shown" robustness panels) are
    # written to a clearly-labelled subdirectory so they cannot be mistaken for
    # one of the figures the paper prints.
    out_dir = config.FIGURES_DIR
    subdir = spec.get("figure_subdir")
    if subdir:
        out_dir = out_dir / subdir
        out_dir.mkdir(parents=True, exist_ok=True)

    save_figure(fig, filename, output_dir=out_dir)
    logging.info(f"  Saved figure: {filename}")


# ============================================================================
# Additive side-output: persist per-event-time coefficients + group level
# trajectories. This does NOT alter any figure or existing output; it only
# writes extra CSVs to output/tables/event_study_coefficients/ so that derived
# in-text magnitudes (e.g. the counterfactual-based % reductions cited in the
# Results section) are reproducible by code rather than hand-computed. It is
# wrapped so any failure here can never disrupt figure generation.
# ============================================================================

def save_event_study_coefficients(df, estimates_df, spec):
    """Write per-ET DiD effects plus treated/control mean level trajectories.

    Columns: ET, Effect, SE, treated_mean, control_mean, n_treated, n_control.
    The treated/control means are the raw outcome means by event time, from
    which a counterfactual level (treated pre-level projected by the control
    slope) can be reconstructed for the % reductions in the manuscript.
    """
    try:
        outcome = spec["outcome"]
        if outcome not in df.columns or "ET" not in df.columns:
            return
        out_dir = config.TABLES_DIR / "event_study_coefficients"
        out_dir.mkdir(parents=True, exist_ok=True)

        # raw level means by group x event time
        g = (
            df.groupby(["treatment", "ET"])[outcome]
            .agg(["mean", "count"])
            .reset_index()
        )
        treated = (g[g.treatment == 1].rename(
            columns={"mean": "treated_mean", "count": "n_treated"})
            [["ET", "treated_mean", "n_treated"]])
        control = (g[g.treatment == 0].rename(
            columns={"mean": "control_mean", "count": "n_control"})
            [["ET", "control_mean", "n_control"]])

        merged = estimates_df.merge(treated, on="ET", how="left").merge(
            control, on="ET", how="left")

        reclass_type = spec["reclass_type"]
        # Distinct ES_coefs filenames: the raw Adverse_Events v_serious 2_1 spec and the
        # utilization-restricted v_serious 2_1 spec share (reclass_type, outcome), so they need
        # distinct stems. Use filename_suffix when the spec has one; otherwise tag
        # restrict_utilization variants with "restrict" so the RAW spec keeps the canonical stem and
        # the restricted variant gets its own file. Figures are unaffected (this is a side-output only).
        suffix = spec.get("filename_suffix", "")
        if not suffix and spec.get("restrict_utilization"):
            suffix = "restrict"
        stem = f"{reclass_type}_{outcome}" + (f"_{suffix}" if suffix else "")
        out_path = out_dir / f"ES_coefs_{stem}.csv"
        merged.to_csv(out_path, index=False)
        logging.info(f"  Saved ES coefficients: {out_path.name}")
    except Exception as e:
        # FAIL-CLOSED: the ES-coefficient CSV is a REQUIRED output -- it feeds the manuscript
        # event-study exhibits, the in-text half-distance magnitudes computed by
        # 15_intext_derived_numbers.py, and the numeric comparator inventory
        # (certification/COMPARATOR_INVENTORY.txt). A failed export ABORTS the step.
        raise RuntimeError(
            f"ES-coefficient export FAILED for spec {spec.get('reclass_type')}/{outcome}: {e}") from e


# ============================================================================
# Additive side-output #2: event-study figure pre-event BASE RATES.
#
# Several event-study figures in the manuscript print a \put overlay of the
# treated group's pre-event base rate (e.g. "Base rate: 6.3 patents/yr",
# "0.6 events/yr"; see paper/JPE_submission_v8.tex, the InnovationES /
# MarketStructure / ESProductSafety sidewaysfigures). Those printed values are
# computed here from each figure's own estimation sample, written to
# output/tables/event_study_base_rates.csv, and checked by step 35 against the
# printed values (JPE §2.2).
#
# This block computes each figure's overlay value FROM THE SAME estimation sample
# and event-time window the figure itself uses -- i.e. the fully-prepared `df`
# that is handed to the estimator in process_figure(), AFTER every filter
# (FDA_own_accord, adverse-event year cut, utilization/normalizable restriction,
# reporter-type recomputation, cohort event-time construction incl. the
# anticipation offset). The base rate is the mean of the figure's outcome over
# TREATED rows in event-time [-5, -1] (the 5-year pre-event window; the same
# pre-event convention used for the Table-1 pre-means in 10_table_formatting.py).
#
# It is PURELY ADDITIVE with respect to the figures and estimates: it only READS
# already-built columns on `df`, accumulates rows in a module-level list, and
# writes ONE new CSV (output/tables/event_study_base_rates.csv) once at the end
# of main(). It never touches any figure, any estimate, or any existing output.
#
# It is, however, REQUIRED: the twelve values it recomputes are printed in the
# manuscript, so JPE Policy 2.2 makes this CSV a governed output exactly like the
# ES-coefficient export above. A failure to record any of the twelve overlay
# figures, or to write the CSV, therefore ABORTS the step.
# ============================================================================

# 5-year pre-event window (matches 10_table_formatting.compute_pre_treatment_stats:
# treated units, event_time in [-5, -1]).
_BASE_RATE_PRE_WINDOW = (-5, -1)

# Accumulator: one row per processed figure, written once by
# write_event_study_base_rates() at the end of main().
_BASE_RATE_ROWS = []

# The manuscript figures that print a "Base rate: X/yr" \put overlay
# (paper/JPE_submission_v8.tex, lines 678, 682, 688, 745, 749, 814, 819, 1902,
# 2046, 2050, 2056, 2060), plus the utilization-normalized panel whose caption
# states "0.002 serious events per procedure" (tex:830). Every one of these must
# receive a base-rate row on a complete run, otherwise a printed number has no
# producing program and write_event_study_base_rates() raises.
MANUSCRIPT_BASE_RATE_FIGURES = {
    "3_2_nolog_real_pats_oct22_24.png",              # tex:678  6.3 patents/yr
    "3_2_nolog_dev_count_oct22_24.png",              # tex:682  0.9 dev/yr
    "2_1_nolog_real_pats_oct22_24.png",              # tex:688  14.8 patents/yr
    "3_2_nolog_unique_firms_solo_CTs.png",           # tex:745  3.0 firms/yr
    "2_1_nolog_unique_firms_oct22_24.png",           # tex:749  6.8 firms/yr
    "3_2_nolog_v_serious_oct22_24.png",              # tex:814  0.6 events/yr
    "2_1_nolog_v_serious_oct22_24.png",              # tex:819  0.5 events/yr
    "3_2_nolog_real_pats_petitioned_oct22_24.png",   # tex:1902 3.9 patents/yr
    "3_2_nolog_absnew_firm_count_oct22_24.png",      # tex:2046 0.1 firms/yr
    "3_2_nolog_firm_expansion_oct22_24.png",         # tex:2050 0.3 firms/yr
    "2_1_nolog_firm_expansion_patents_oct22_24.png",  # tex:2056 2.2 firms/yr
    "3_2_nolog_firm_expansion_patents_oct22_24.png",  # tex:2060 1.5 firms/yr
    "2_1_nolog_v_serious_restrict_oct22_24.png",     # tex:830  0.002 events/procedure
}


def _es_figure_filename(spec):
    """Return the output PNG filename this spec produces (read-only helper).

    Mirrors the filename logic in plot_and_save() so each base-rate row maps to
    the exact figure carrying the overlay. No side effects.
    """
    reclass_type = spec["reclass_type"]
    outcome = spec["outcome"]
    restrict_util = spec.get("restrict_utilization", False)
    suffix = spec.get("filename_suffix", "")
    if suffix:
        filename = f"{reclass_type}_nolog_{outcome}_{suffix}_oct22_24.png"
    elif restrict_util:
        filename = f"{reclass_type}_nolog_{outcome}_restrict_oct22_24.png"
    else:
        filename = f"{reclass_type}_nolog_{outcome}_oct22_24.png"
    return spec.get("filename_override", filename)


def record_event_study_base_rate(df, spec):
    """Record the treated pre-event base rate for this figure's overlay.

    Computes mean(outcome) over treated rows with ET in [-5, -1] on the SAME
    prepared estimation-sample DataFrame the figure uses, and appends a row to
    the module-level accumulator.

    NOT guarded: for the figures listed in MANUSCRIPT_BASE_RATE_FIGURES the value
    is printed in the paper, so a missing column, a missing event-time variable or
    an empty pre-event window means a manuscript number has no producing program
    and must fail the step rather than be logged and skipped.
    """
    outcome = spec["outcome"]
    figure_file = _es_figure_filename(spec)
    required = figure_file in MANUSCRIPT_BASE_RATE_FIGURES

    missing = [c for c in (outcome, "ET", "treatment") if c not in df.columns]
    if missing:
        if required:
            raise RuntimeError(
                f"base-rate record FAILED for {spec.get('reclass_type')}/{outcome} "
                f"({figure_file}): missing column(s) {missing}; this figure carries a "
                f"manuscript base-rate overlay")
        logging.info(f"  base-rate not applicable for {figure_file} "
                     f"(missing {missing}; no manuscript overlay)")
        return

    lo, hi = _BASE_RATE_PRE_WINDOW
    treated_pre = df[
        (df["treatment"] == 1) & (df["ET"] >= lo) & (df["ET"] <= hi)
    ]
    vals = pd.to_numeric(treated_pre[outcome], errors="coerce").dropna()
    if len(vals) == 0:
        if required:
            raise RuntimeError(
                f"base-rate record FAILED for {spec.get('reclass_type')}/{outcome} "
                f"({figure_file}): no treated observations in the pre-event window "
                f"[{lo},{hi}]; this figure carries a manuscript base-rate overlay")
        logging.info(f"  base-rate empty for {figure_file}; no manuscript overlay")
        return

    _BASE_RATE_ROWS.append({
        "figure_panel": f"{spec['panel']}/{spec['reclass_type']}",
        "outcome": outcome,
        "reclass_type": spec["reclass_type"],
        "figure_file": figure_file,
        "pre_window": f"[{lo},{hi}]",
        "n_treated_obs": int(len(vals)),
        "base_rate": round(float(vals.mean()), 6),
    })


def write_event_study_base_rates():
    """Write the accumulated pre-event base rates to a single new CSV.

    output/tables/event_study_base_rates.csv with columns
    {figure_panel, outcome, reclass_type, figure_file, pre_window,
     n_treated_obs, base_rate}.

    FAIL-CLOSED: the CSV is a governed output (it backs the twelve printed
    "Base rate: X/yr" overlays and the normalized-panel caption value), so an
    empty accumulator, a missing overlay figure, or a write failure RAISES.
    """
    out_dir = config.TABLES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    cols = ["figure_panel", "outcome", "reclass_type", "figure_file",
            "pre_window", "n_treated_obs", "base_rate"]
    if not _BASE_RATE_ROWS:
        raise RuntimeError(
            "event-study base-rate export FAILED: no base rates were recorded, so "
            "the manuscript's printed overlay values have no producing output")
    df_out = pd.DataFrame(_BASE_RATE_ROWS)[cols]
    recorded = set(df_out["figure_file"])
    absent = sorted(MANUSCRIPT_BASE_RATE_FIGURES - recorded)
    if absent:
        raise RuntimeError(
            "event-study base-rate export FAILED: no base rate was recorded for the "
            f"manuscript overlay figure(s) {absent}")
    out_path = out_dir / "event_study_base_rates.csv"
    df_out.to_csv(out_path, index=False)
    logging.info(
        f"  Saved event-study base rates: {out_path.name} "
        f"({len(df_out)} rows; all {len(MANUSCRIPT_BASE_RATE_FIGURES)} manuscript "
        f"overlay figures present)"
    )


# ============================================================================
# Main loop
# ============================================================================

def process_figure(spec):
    """Process a single figure specification end-to-end."""
    outcome = spec["outcome"]
    reclass_type = spec["reclass_type"]
    panel = spec["panel"]
    restrict_util = spec.get("restrict_utilization", False)

    logging.info(
        f"Processing: {panel} / {outcome} / {reclass_type}"
        + (" (utilization-restricted)" if restrict_util else "")
    )

    # Handle no-data placeholder (dev_count for 2->1)
    if spec.get("no_data", False):
        fig, ax = create_figure(nrows=1, ncols=1, figsize=(12, 8))
        plot_no_data_panel(ax, reclass_type, spec["label"])
        filename = f"{reclass_type}_nolog_{outcome}_oct22_24.png"
        filename = spec.get("filename_override", filename)
        save_figure(fig, filename, output_dir=config.FIGURES_DIR)
        logging.info(f"  Saved no-data placeholder: {filename}")
        return

    # Load data
    df = load_matched_sample(spec)

    # Adverse events: filter year > 1991 (II->I only; III->II uses full panel)
    if panel == "Adverse_Events" and reclass_type == "2_1":
        df = df[df.year > config.ADVERSE_EVENT_MIN_YEAR].reset_index(drop=True)

    # For III->II non-safety: apply FDA_own_accord filter
    # Petitioned subsample: keep petition-initiated (== 0); all others: keep FDA-initiated (== 1)
    if reclass_type == "3_2" and panel != "Safety":
        if "FDA_own_accord_3_2" in df.columns:
            is_petitioned = "petitioned" in spec.get("matched_file", "")
            accord_val = 0 if is_petitioned else 1
            df = df[
                (df.FDA_own_accord_3_2 == accord_val) | (df.treatment == 0)
            ].reset_index(drop=True)

    # Ensure class_by_episode exists
    if "class_by_episode" not in df.columns or panel != "Safety":
        df = prepare_class_by_episode(df)

    # Prepare event-time indicators
    df = prepare_event_time(df, spec)

    # Apply utilization restriction if needed
    is_normalizable = spec.get("normalizable", False)
    if restrict_util or is_normalizable:
        if reclass_type == "2_1":
            df = apply_utilization_restriction_2_1(
                df, outcome, normalizable=is_normalizable
            )
        else:
            df = apply_utilization_restriction_3_2(df, outcome)
        # Rebuild class_by_episode after filtering
        df = prepare_class_by_episode(df)

    # Apply reporter-type filter: recompute v_serious from reporter-specific
    # adverse event columns
    reporter_filter = spec.get("reporter_filter")
    if reporter_filter:
        df = apply_reporter_filter(df, reporter_filter)

    n_treated = len(set(df[df.treatment == 1]["PRODUCTCODE"]))
    n_control = len(set(df[df.treatment == 0]["PRODUCTCODE"]))
    logging.info(f"  N treated PCs: {n_treated}, N control PCs: {n_control}")

    # Estimate
    if reclass_type == "2_1":
        estimates_df = estimate_event_study_2to1(df, spec)
    else:
        estimates_df = estimate_event_study_3to2(df, spec)

    # Plot and save
    plot_and_save(estimates_df, spec)

    # Additive side-output (does not affect the figure above)
    save_event_study_coefficients(df, estimates_df, spec)

    # Additive side-output #2: record this figure's pre-event base-rate overlay
    # value (guarded; accumulated and written once in main()).
    record_event_study_base_rate(df, spec)


def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    source_r_scripts()

    t_total = time.time()
    logging.info("=" * 60)
    logging.info("Starting event study figure generation")
    logging.info(f"Total figure specs: {len(FIGURE_SPECS)}")

    # FAIL-CLOSED: save_event_study_coefficients() RAISES on a required ES-coefficient export
    # failure. Per-spec failures are collected rather than discarded, and after the loop, if ANY spec
    # failed, the SCRIPT exits nonzero. A clean all-pass run exits 0. FDA_STRICT_ES=1 (opt-in,
    # strict-certification mode) additionally aborts immediately on the FIRST failure rather than
    # continuing through the remaining specs, so no later spec can produce a governed output after a
    # required failure; without the flag, the loop still runs to completion (so a single dev run
    # reports every failure at once) but the final exit code is nonzero exactly as it is in strict mode.
    fail_fast = os.environ.get("FDA_STRICT_ES") == "1"
    failures = []

    for i, spec in enumerate(FIGURE_SPECS):
        t0 = time.time()
        logging.info(f"--- Figure {i + 1}/{len(FIGURE_SPECS)} ---")
        try:
            process_figure(spec)
        except Exception as e:
            spec_id = f"{spec['panel']}/{spec['outcome']}/{spec['reclass_type']}"
            logging.error(f"  FAILED: {spec_id}: {e}", exc_info=True)
            failures.append(spec_id)
            if fail_fast:
                remaining = len(FIGURE_SPECS) - (i + 1)
                logging.error(
                    f"STRICT (FDA_STRICT_ES=1): aborting immediately after failure on {spec_id}; "
                    f"{remaining} remaining spec(s) NOT attempted."
                )
                break
        elapsed = time.time() - t0
        logging.info(f"  Elapsed: {elapsed:.1f}s")

    logging.info(
        f"Event study generation complete. Total time: {time.time() - t_total:.1f}s"
    )

    # Side-output #2: write the pre-event base-rate table. This is a GOVERNED
    # output (it backs the manuscript's printed overlay values), so a failure is
    # recorded as a step failure rather than logged and ignored. It is attempted
    # even when some figure specs failed, so the run reports every problem at once.
    try:
        write_event_study_base_rates()
    except Exception as e:
        logging.error(f"  {e}", exc_info=True)
        failures.append("event_study_base_rates")

    if failures:
        logging.error(
            f"FAILED: {len(failures)} of {len(FIGURE_SPECS)} figure spec(s) did not complete: "
            f"{failures}"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
