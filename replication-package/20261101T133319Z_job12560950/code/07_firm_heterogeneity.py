#!/usr/bin/env python
"""
07_firm_heterogeneity.py -- Firm-size tercile heterogeneity analysis.

Splits samples by firm-size terciles using patent-level firm assets, runs
Conley-Taber stacked DiD within each tercile, and saves estimated treatment
effects for downstream use in 08_lbd_simulation.py.

Three analyses, each split by firm-size tercile:
  (A) Safety emphasis heterogeneity (II->I only)
  (B) Adverse event heterogeneity   (II->I only)
  (C) Innovation heterogeneity      (II->I and III->II)

Tercile splitting methodology:
  - Patent-level firm assets are used, NOT PC-level averages.
  - For safety: percentiles conditioned on treated pre-period safety patents.
  - For adverse events and innovation: percentiles of all non-null firm_size
    patents.
  - Observations (patent- or PC-year-firm level) are assigned to a tercile
    based on whether their firm_size falls within the tercile boundaries.

Safety and adverse event analyses re-run nearest-neighbor matching within
each tercile. Innovation analyses re-filter patent counts by firm-size
boundaries within each tercile and merge onto the existing matched sample.

Source: Replication_analysis.py lines 5454-6290.

Inputs:
    data/derived/safety_vars_allpats.csv
    data/derived/all_patents_w_xi_oct22_24.csv
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_2_1_onepat_innovation.csv
    data/derived/matched_sample_3_2_onepat_innovation.csv
    data/derived/Adverse_fsize_ready_all4_oct22_24.csv

Outputs:
    output/figures/3_2_smallvlarge.png              (III->II innovation)
    output/figures/2_1_smallvlarge.png              (II->I innovation)
    output/figures/2_1_Safety_Top_Decile_Present_oct22_24.png
    output/figures/2_1_Deaths_Top_Decile_oct22_24.png
    output/tables/firm_heterogeneity_k_est.csv
    output/tables/firm_heterogeneity_k_pct.csv
"""

import sys
import logging
import time
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked
from match_mahal import get_similar, MatchInputError
from plotting import save_figure

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "07_firm_heterogeneity.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

TERCILE_LABELS = ["First", "Second", "Third"]
NUM_TERCILES = 3


# ============================================================================
# Utility: standard bar chart for tercile heterogeneity
# ============================================================================

def _bar_chart(values, errors, ylabel, title, filename,
               bar_colors=None, ylim=None, pct_scale=False,
               clean_style=True):
    """
    Plot a bar chart of tercile estimates with error bars.

    clean_style=True (default): reset rcParams, hide all spines, tick length=0.
      Used for safety/adverse event figures (D.7a-b).
    clean_style=False: use seaborn-poster styling (visible spines), tick labelsize=20.
      Used for innovation bar charts (Figures 5a-b).
    """
    if bar_colors is None:
        bar_colors = ["#264653", "#2a9d8f", "#f4a261"]

    # Scale to percent if requested
    plot_vals = np.array(values) * 100 if pct_scale else np.array(values)
    plot_errs = np.array(errors) * 100 if pct_scale else np.array(errors)

    if clean_style:
        mpl.rcParams.update(mpl.rcParamsDefault)
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
        for spine in ["right", "bottom", "left", "top"]:
            ax.spines[spine].set_visible(False)
        ax.tick_params(axis="both", which="both", length=0)
    else:
        # seaborn-poster style (set at module load via plotting.py import)
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

    ax.bar(
        TERCILE_LABELS, plot_vals, yerr=plot_errs,
        align="center", color=bar_colors[:len(values)],
        ecolor="black", alpha=0.9,
    )
    ax.axhline(0, color="black", linestyle="dashed")
    ax.set_xlabel("Total Asset Terciles", fontsize=24)
    ax.set_ylabel(ylabel, fontsize=24)
    if title:
        ax.set_title(title, fontsize=30, pad=30)

    tick_size = 16 if clean_style else 20
    ax.tick_params(axis="x", labelsize=tick_size)
    ax.tick_params(axis="y", labelsize=tick_size)

    if ylim is not None:
        ax.set_ylim(ylim)

    fig.subplots_adjust(left=0.15)
    save_figure(fig, filename)


# ============================================================================
# Utility: compute percentile boundaries for a given tercile index
# ============================================================================

def _tercile_bounds(firm_sizes, tercile_idx, n_terciles=NUM_TERCILES):
    """
    Compute the lower and upper percentile boundaries for a given tercile.

    Parameters:
        firm_sizes: 1-D array of firm asset values
        tercile_idx: 0, 1, or 2
        n_terciles: total number of quantile bins (default 3)

    Returns:
        (lower_bound, upper_bound) percentile values
    """
    pct_lo = 100 / n_terciles * tercile_idx
    pct_hi = 100 / n_terciles * tercile_idx + 100 / n_terciles
    lower = np.percentile(firm_sizes, pct_lo)
    upper = np.percentile(firm_sizes, pct_hi)
    return lower, upper


# ============================================================================
# Utility: NN matching on a pre-event variable
# ============================================================================

def _nn_match(df_orig, match_var, pre_window=(-3, 0)):
    """
    Nearest-neighbor matching on a single variable within a pre-event window.

    For each treated PC, find the closest unmatched control PC by `match_var`
    averaged over event_time in (pre_window[0], pre_window[1]).

    Falls back to all controls if no unmatched controls remain.

    Parameters:
        df_orig: DataFrame with PRODUCTCODE, year, treatment_final,
                 year_reclassified, and the match variable.
        match_var: column name to match on
        pre_window: (lower_exclusive, upper_exclusive) event-time bounds

    Returns:
        Matched DataFrame with treated + 1:1 matched controls, FE assigned.
    """
    temp_parts = []
    control_list = []
    skipped = []
    treated_pcs = np.unique(df_orig[df_orig.treatment_final == 1]["PRODUCTCODE"])

    for i, PC in enumerate(treated_pcs):
        treated = df_orig[df_orig.PRODUCTCODE == PC].copy()
        yr_reclass = treated["year_reclassified"].values[0]
        treated["event_time"] = treated["year"] - int(float(yr_reclass))

        # Try excluding already-matched controls; fall back if none remain
        control = df_orig[
            (df_orig.treatment_final == 0) & ~(df_orig.PRODUCTCODE.isin(control_list))
        ].copy()
        if len(control) == 0:
            control = df_orig[df_orig.treatment_final == 0].copy()

        control["event_time"] = control["year"] - int(float(yr_reclass))

        lo, hi = pre_window
        control_meaned = (
            control[(control.event_time > lo) & (control.event_time < hi)]
            .groupby("PRODUCTCODE")
            .mean(numeric_only=True)
            .reset_index()
        )
        treated_meaned = treated[
            (treated.event_time > lo) & (treated.event_time < hi)
        ].mean(numeric_only=True)

        if len(control_meaned) == 0:
            logging.warning(f"No controls available for {PC} in NN matching. Skipping.")
            continue

        try:
            sim_distances, sim_indices = get_similar(
                treated_meaned[[match_var]].values,
                control_meaned[[match_var]].values,
                topn=1,
            )
        except MatchInputError as exc:
            # A skipped treated unit is a CHANGED ESTIMATION SAMPLE for this tercile, not a
            # cosmetic gap, so it is counted and surfaced after the loop rather than left as one
            # warning line among thousands. The former handler was a bare `except Exception` with a
            # warning and `continue`: a treated product code could silently leave the tercile --
            # most plausibly when controls are consumed without replacement until only one remains,
            # which this match cannot use.
            skipped.append((str(PC), str(exc)))
            logging.warning("NN matching skipped treated %s: %s", PC, exc)
            continue

        PC_CONTROL = control_meaned.iloc[sim_indices]["PRODUCTCODE"].values[0]
        control_list.append(PC_CONTROL)

        control_keep = df_orig[df_orig.PRODUCTCODE == PC_CONTROL].copy()
        control_keep["FE"] = i
        treated["FE"] = i

        temp_parts.append(control_keep)
        temp_parts.append(treated)

    if skipped:
        # FATAL (2026-10-13, author-approved after a zero-skip real-data run): a treated product code
        # that leaves the sample changes the tercile estimate, so the step fails rather than
        # reporting a quietly smaller sample. Every skip is collected first, so the message names
        # all of them instead of only the first. Verified on the real data: all three analyses
        # matched every treated unit (92/92, 88/88, 104/104 and 130/130 x3), so this raises only if
        # something that does not happen today starts happening.
        detail = "; ".join(f"{pc} ({why})" for pc, why in skipped)
        logging.error(
            "NN matching dropped %d of %d treated product code(s) from this sample on '%s': %s.",
            len(skipped), len(treated_pcs), match_var, detail,
        )
        raise RuntimeError(
            f"nearest-neighbour matching on '{match_var}' dropped {len(skipped)} of "
            f"{len(treated_pcs)} treated product code(s): {detail}. The tercile estimates would be "
            f"computed on a smaller treated sample than the one documented; failing instead."
        )

    if len(temp_parts) == 0:
        return pd.DataFrame()

    temp = pd.concat(temp_parts, ignore_index=True)
    temp = temp.drop_duplicates(subset=["year", "PRODUCTCODE", "FE"])
    return temp


# ============================================================================
# (A) Safety emphasis heterogeneity by firm size (II->I)
# ============================================================================

def run_safety_heterogeneity():
    """
    Tercile heterogeneity of safety emphasis for II->I.

    Tercile boundaries are conditioned on treated pre-period safety patents
    (safety==1 & treatment==1 & year < 1998) at the patent level.

    Within each tercile, re-filter patents, aggregate to PC-year, balance panel,
    merge treatment, re-run NN matching on safety_prop, run Conley-Taber.

    Returns:
        k_est: list of percentage-change estimates by tercile
        k_pct: list of estimate/baseline ratios by tercile
        k_std: list of scaled SEs by tercile
    """
    logging.info("=" * 60)
    logging.info("(A) Safety emphasis heterogeneity by firm size (II->I)")

    # Load patent-level data with safety flag and firm_size
    df_safety_raw = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["safety_vars"]
    )
    df_safety_raw["patents"] = 1
    all_pats = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"]
    )

    # Build df_safety_keep_w_permno: patent-level safety data with firm_size
    # Keep patents where firm_size is non-null (via all_pats)
    df_safety_keep = df_safety_raw[
        df_safety_raw.id.isin(all_pats[all_pats.firm_size.notnull()]["id"])
    ]
    df_safety_keep = pd.merge(
        df_safety_keep,
        all_pats[["id", "firm_size", "permno", "PRODUCTCODE", "year"]],
        how="left", on="id",
    )

    # Keep patents from firms in adverse event data (ensures same firm universe)
    w_fsize = pd.read_csv(
        config.DERIVED_DATA_DIR / "Adverse_fsize_ready_all4_oct22_24.csv"
    )
    df_safety_keep_w_permno = df_safety_keep[
        df_safety_keep.permno.isin(w_fsize.permno)
    ]

    # Load matched sample for treatment status
    matched_21 = pd.read_csv(
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"]
    )
    test_main21 = matched_21.copy()

    # Merge treatment status
    df_safety_keep_w_permno = pd.merge(
        df_safety_keep_w_permno,
        test_main21[["PRODUCTCODE", "treatment"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )
    # Keep PCs in matched sample or controls not in matched sample
    df_safety_keep_w_permno = df_safety_keep_w_permno[
        (df_safety_keep_w_permno.PRODUCTCODE.isin(test_main21.PRODUCTCODE.values))
        | df_safety_keep_w_permno.treatment.isnull()
    ]

    logging.info(
        f"  Patent-level safety data: {len(df_safety_keep_w_permno)} rows, "
        f"{df_safety_keep_w_permno.PRODUCTCODE.nunique()} PCs"
    )

    k_est = []
    k_pct = []
    k_std = []

    for tercile_idx in range(NUM_TERCILES):
        logging.info(f"  Tercile {tercile_idx + 1} ({TERCILE_LABELS[tercile_idx]})")

        # Filter to non-null firm_size patents
        notnull = df_safety_keep_w_permno[
            df_safety_keep_w_permno.firm_size.notnull()
        ]

        # Percentile boundaries: conditioned on treated pre-period SAFETY patents
        cond_mask = (
            (notnull.safety == 1)
            & (notnull.treatment == 1)
            & (notnull.year < 1998)
        )
        conditioning_sizes = notnull.loc[cond_mask, "firm_size"].values
        if len(conditioning_sizes) == 0:
            logging.warning("  No treated pre-period safety patents. Skipping tercile.")
            k_est.append(np.nan)
            k_pct.append(np.nan)
            k_std.append(np.nan)
            continue

        lower, upper = _tercile_bounds(conditioning_sizes, tercile_idx)
        logging.info(f"    Firm size bounds: ({lower:.2f}, {upper:.2f})")

        # Filter patents within these firm-size bounds
        temp = notnull[(notnull.firm_size > lower) & (notnull.firm_size < upper)]

        # Keep only IDs from this subset in the full safety data
        df_safety_dd = df_safety_keep_w_permno[
            df_safety_keep_w_permno.id.isin(temp.id)
        ]
        df_safety_dd = df_safety_dd[df_safety_dd.year >= 1976]

        # Aggregate to PC-year level
        df_safety_dd = (
            df_safety_dd[["PRODUCTCODE", "year", "patents", "safety"]]
            .groupby(["PRODUCTCODE", "year"])
            .sum()
            .reset_index()
        )

        # Balance panel
        df_safety_dd = (
            df_safety_dd.set_index(["PRODUCTCODE", "year"])
            .unstack(fill_value=0)
            .stack()
            .sort_index(level=1)
            .reset_index()
        )

        # Merge treatment info
        df_safety_dd = pd.merge(
            df_safety_dd,
            test_main21[["PRODUCTCODE", "treatment", "year_reclassified"]].drop_duplicates(),
            on="PRODUCTCODE", how="left",
        )
        df_safety_dd.loc[df_safety_dd.treatment.isnull(), "treatment"] = 0
        df_safety_dd = df_safety_dd.reset_index(drop=True)

        # Consolidate treatment
        df_safety_dd["year_reclassfinal"] = df_safety_dd.groupby("PRODUCTCODE")[
            "year_reclassified"
        ].transform(pd.Series.max)
        df_safety_dd["treatment_final"] = df_safety_dd.groupby("PRODUCTCODE")[
            "treatment"
        ].transform(pd.Series.max)
        df_safety_dd["treatment"] = df_safety_dd["treatment_final"]
        df_safety_dd["year_reclassified"] = df_safety_dd["year_reclassfinal"]

        # Safety proportion and binarize
        df_safety_dd["FE"] = np.nan
        df_safety_dd.loc[df_safety_dd.treatment == 0, "FE"] = 0
        df_safety_dd["safety_prop"] = df_safety_dd["safety"] / df_safety_dd["patents"]
        df_safety_dd["safety_prop"] = df_safety_dd["safety_prop"].fillna(0)

        df_safety_orig = df_safety_dd.copy()

        # --- Re-run NN matching within this tercile (on safety_prop) ---
        df_safety_dd = _nn_match(df_safety_orig, "safety_prop", pre_window=(-3, 0))
        if len(df_safety_dd) == 0:
            logging.warning("  NN matching returned empty DataFrame. Skipping.")
            k_est.append(np.nan)
            k_pct.append(np.nan)
            k_std.append(np.nan)
            continue

        n_treat = len(set(df_safety_dd[df_safety_dd.treatment_final == 1]["PRODUCTCODE"]))
        n_ctrl = len(set(df_safety_dd[df_safety_dd.treatment_final == 0]["PRODUCTCODE"]))
        logging.info(f"    After NN matching: {n_treat} treated, {n_ctrl} control PCs")

        # Post-matching setup
        df_safety_dd.loc[df_safety_dd.treatment == 0, "year_reclassified"] = np.nan
        df_safety_dd["year_reclass_ET"] = df_safety_dd.groupby(["FE"])[
            "year_reclassified"
        ].transform(pd.Series.max)
        df_safety_dd["factorized"] = df_safety_dd.PRODUCTCODE.astype("category").cat.codes
        df_safety_dd["class_by_episode"] = (
            df_safety_dd["FE"].astype(int).astype(str)
            + "[SEP]"
            + df_safety_dd["factorized"].astype(str)
        )
        df_safety_dd["class_by_episode"] = (
            df_safety_dd.class_by_episode.astype("category").cat.codes
        )

        # Posttreat with 1-year anticipation
        df_safety_dd["posttreat"] = 0
        df_safety_dd.loc[
            (df_safety_dd.treatment == 1)
            & (df_safety_dd.year >= df_safety_dd.year_reclassified - 1),
            "posttreat",
        ] = 1
        df_safety_dd["ET"] = df_safety_dd["year"] - df_safety_dd["year_reclass_ET"] + 1

        # Binarize safety_prop
        df_safety_dd.loc[df_safety_dd["safety_prop"] > 0, "safety_prop"] = 1
        df_safety_dd["baseline_event_count"] = df_safety_dd.groupby("PRODUCTCODE")[
            "safety_prop"
        ].transform(pd.Series.max)
        df_safety_dd = df_safety_dd.sort_values(
            by=["PRODUCTCODE", "year"]
        ).reset_index(drop=True)

        # Baseline stats
        baseline = df_safety_dd[
            (df_safety_dd.treatment_final == 1)
            & (df_safety_dd.year - df_safety_dd.year_reclassfinal < -1)
            & (df_safety_dd.year - df_safety_dd.year_reclassfinal > -4)
        ]["safety_prop"].mean()

        baseline_c = df_safety_dd[
            (df_safety_dd.treatment_final == 0)
            & (df_safety_dd.year < 1996) & (df_safety_dd.year > 1990)
        ]["safety_prop"].mean()

        after_c = df_safety_dd[
            (df_safety_dd.treatment_final == 0) & (df_safety_dd.year > 1996)
        ]["safety_prop"].mean()

        # Run Conley-Taber
        df_safety_dd = df_safety_dd.sort_values(
            by=["class_by_episode", "year"]
        ).reset_index(drop=True)

        cols = [
            "safety_prop", "posttreat", "treatment", "class_by_episode",
            "year", "factorized", "FE", "PRODUCTCODE",
        ]
        estimate, alpha025, alpha975 = conley_taber_stacked(
            df_safety_dd[cols], "safety_prop", "posttreat", "treatment",
            "class_by_episode", "year", seed=config.RANDOM_SEED,
        )
        logging.info(
            f"    Estimate: {estimate:.4f}, CI: [{alpha025:.4f}, {alpha975:.4f}]"
        )
        logging.info(f"    Baseline treated: {baseline:.4f}")

        # SE = CI half-width / 1.96
        if estimate < 0:
            SE = np.abs(estimate - alpha975) / 1.96
        else:
            SE = (estimate - alpha025) / 1.96

        # k_est stores percentage change: estimate / (baseline + after_c - baseline_c) * 100
        denom = baseline + after_c - baseline_c
        if denom != 0 and not np.isnan(denom):
            k_est.append(estimate / denom * 100)
            k_std.append(SE / denom * 100)
        else:
            k_est.append(np.nan)
            k_std.append(np.nan)

        # k_pct stores estimate/baseline
        if baseline != 0 and not np.isnan(baseline):
            k_pct.append(estimate / baseline)
        else:
            k_pct.append(np.nan)

        logging.info(
            f"    % change: {k_est[-1]:.2f}, ratio: {k_pct[-1]:.4f}"
        )

    return k_est, k_pct, k_std


# ============================================================================
# (B) Adverse event heterogeneity by firm size (II->I)
# ============================================================================

def run_adverse_event_heterogeneity():
    """
    Tercile heterogeneity of adverse events (v_serious) for II->I.

    Tercile boundaries use all non-null firm_size rows in w_fsize_in_treated21.

    Within each tercile, re-filter adverse event counts, merge onto the matched
    sample, re-run NN matching on v_serious, run Conley-Taber.

    Returns:
        k_est: list of raw estimates by tercile
        k_pct: list of estimate / (|estimate| + after_t) ratios by tercile
        k_std: list of scaled SEs by tercile
    """
    logging.info("=" * 60)
    logging.info("(B) Adverse event heterogeneity by firm size (II->I)")

    # Load adverse event data with firm sizes
    w_fsize = pd.read_csv(
        config.DERIVED_DATA_DIR / "Adverse_fsize_ready_all4_oct22_24.csv"
    )

    # Load matched sample for treatment status and structure
    matched_21 = pd.read_csv(
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"]
    )
    test_main21 = matched_21.copy()
    test_main21_dropped = test_main21.drop(
        columns=[c for c in ["L", "H", "S", "D"] if c in test_main21.columns]
    )

    # Restrict to PCs in matched sample
    w_fsize_in_treated21 = w_fsize[
        w_fsize.PRODUCTCODE.isin(test_main21_dropped.PRODUCTCODE.values)
    ]

    logging.info(
        f"  Adverse event data: {len(w_fsize_in_treated21)} rows, "
        f"{w_fsize_in_treated21.PRODUCTCODE.nunique()} PCs"
    )

    k_est = []
    k_pct = []
    k_std = []

    for tercile_idx in range(NUM_TERCILES):
        logging.info(f"  Tercile {tercile_idx + 1} ({TERCILE_LABELS[tercile_idx]})")

        notnull = w_fsize_in_treated21[w_fsize_in_treated21.firm_size.notnull()]

        # Percentile boundaries: all non-null firm_size rows
        lower, upper = _tercile_bounds(notnull.firm_size.values, tercile_idx)
        logging.info(f"    Firm size bounds: ({lower:.2f}, {upper:.2f})")

        # Filter adverse event rows within firm-size bounds
        temp = notnull[(notnull.firm_size > lower) & (notnull.firm_size < upper)]

        # Aggregate to PC-year level
        temp_agg = (
            temp[["PRODUCTCODE", "year", "L", "H", "S", "D"]]
            .groupby(["PRODUCTCODE", "year"])
            .sum()
            .reset_index()
        )
        # Balance panel
        temp_agg = (
            temp_agg.set_index(["PRODUCTCODE", "year"])
            .unstack(fill_value=0)
            .stack()
            .sort_index(level=1)
            .reset_index()
        )

        # Merge onto matched sample structure
        df_safety_dda = test_main21_dropped.copy()
        df_safety_dda = df_safety_dda[df_safety_dda.year >= 1992]
        df_safety_dda = pd.merge(
            df_safety_dda, temp_agg,
            on=["PRODUCTCODE", "year"], how="left",
        )
        df_safety_dda[["L", "H", "S", "D"]] = (
            df_safety_dda[["L", "H", "S", "D"]].fillna(0)
        )
        df_safety_dda = df_safety_dda.reset_index(drop=True)

        # Consolidate treatment
        df_safety_dda["year_reclassfinal"] = df_safety_dda.groupby("PRODUCTCODE")[
            "year_reclassified"
        ].transform(pd.Series.max)
        df_safety_dda["treatment_final"] = df_safety_dda.groupby("PRODUCTCODE")[
            "treatment"
        ].transform(pd.Series.max)
        df_safety_dda["treatment"] = df_safety_dda["treatment_final"]
        df_safety_dda["year_reclassified"] = df_safety_dda["year_reclassfinal"]

        df_safety_dda["factorized"] = (
            df_safety_dda.PRODUCTCODE.astype("category").cat.codes
        )
        df_safety_dda["v_serious"] = (
            df_safety_dda["L"] + df_safety_dda["H"]
            + df_safety_dda["D"] + df_safety_dda["S"]
        )
        df_safety_dda["baseline_event_count"] = df_safety_dda.groupby("PRODUCTCODE")[
            "v_serious"
        ].transform(pd.Series.max)

        n_treat = len(set(df_safety_dda[df_safety_dda.treatment_final == 1]["PRODUCTCODE"]))
        n_ctrl = len(set(df_safety_dda[df_safety_dda.treatment_final == 0]["PRODUCTCODE"]))
        logging.info(f"    Before NN: {n_treat} treated, {n_ctrl} control PCs")

        # Baseline stats (before matching, used for percent calc)
        baseline = df_safety_dda[
            (df_safety_dda.treatment_final == 1)
            & (df_safety_dda.year - df_safety_dda.year_reclassfinal < 0)
            & (df_safety_dda.year - df_safety_dda.year_reclassfinal > -5)
        ]["v_serious"].mean()

        after_t = df_safety_dda[
            (df_safety_dda.treatment_final == 1)
            & (df_safety_dda.year - df_safety_dda.year_reclassfinal > 0)
        ]["v_serious"].mean()

        # --- Re-run NN matching within tercile (on v_serious) ---
        df_diff = df_safety_dda.copy()
        df_diff["FE"] = np.nan
        df_diff_orig = df_diff.copy()

        temp_parts = []
        control_list = []
        treated_pcs = np.unique(
            df_diff_orig[df_diff_orig.treatment_final == 1]["PRODUCTCODE"]
        )
        skipped_ae = []

        for i, PC in enumerate(treated_pcs):
            treated = df_diff_orig[df_diff_orig.PRODUCTCODE == PC].copy()
            yr_reclass = treated["year_reclassified"].values[0]
            treated["event_time"] = treated["year"] - int(float(yr_reclass))

            # Try excluding already-matched; fall back to all
            control = df_diff_orig[
                (df_diff_orig.treatment_final == 0)
                & ~(df_diff_orig.PRODUCTCODE.isin(control_list))
            ].copy()
            if len(control) == 0:
                control = df_diff_orig[df_diff_orig.treatment_final == 0].copy()

            control["event_time"] = control["year"] - int(float(yr_reclass))

            # Pre-window: (-2, 0) for adverse events
            control_meaned = (
                control[(control.event_time < 0) & (control.event_time > -2)]
                .groupby("PRODUCTCODE")
                .mean(numeric_only=True)
                .reset_index()
            )
            treated_meaned = treated[
                (treated.event_time < 0) & (treated.event_time > -2)
            ].mean(numeric_only=True)

            if len(control_meaned) == 0:
                continue

            try:
                sim_distances, sim_indices = get_similar(
                    treated_meaned[["v_serious"]].values,
                    control_meaned[["v_serious"]].values,
                    topn=1,
                )
            except MatchInputError as exc:
                # Was `except Exception: continue` with NO log line at all: a treated product code
                # could leave this tercile's sample without leaving a trace anywhere. Its pre-window
                # here is a single year (event_time == -1), so an empty one is entirely possible.
                skipped_ae.append((str(PC), str(exc)))
                logging.warning("NN matching skipped treated %s: %s", PC, exc)
                continue

            PC_CONTROL = control_meaned.iloc[sim_indices]["PRODUCTCODE"].values[0]
            control_list.append(PC_CONTROL)

            control_keep = df_diff_orig[df_diff_orig.PRODUCTCODE == PC_CONTROL].copy()
            control_keep["FE"] = i
            treated["FE"] = i

            temp_parts.append(control_keep)
            temp_parts.append(treated)

        if skipped_ae:
            # FATAL, same rule as _nn_match above (author-approved 2026-10-13). This loop's
            # pre-window is a single year (event_time == -1), so an empty one is the likelier
            # trigger here; the real-data run skipped nothing.
            detail_ae = "; ".join(f"{pc} ({why})" for pc, why in skipped_ae)
            logging.error(
                "  NN matching dropped %d of %d treated product code(s) from this tercile's "
                "adverse-event sample: %s.",
                len(skipped_ae), len(treated_pcs), detail_ae,
            )
            raise RuntimeError(
                f"nearest-neighbour matching dropped {len(skipped_ae)} of {len(treated_pcs)} "
                f"treated product code(s) from the adverse-event tercile sample: {detail_ae}."
            )

        if len(temp_parts) == 0:
            logging.warning("  NN matching returned no matches. Skipping.")
            k_est.append(np.nan)
            k_pct.append(np.nan)
            k_std.append(np.nan)
            continue

        df_diff = pd.concat(temp_parts, ignore_index=True)
        df_diff = df_diff.drop_duplicates(subset=["year", "PRODUCTCODE", "FE"])

        n_treat = len(set(df_diff[df_diff.treatment_final == 1]["PRODUCTCODE"]))
        n_ctrl = len(set(df_diff[df_diff.treatment_final == 0]["PRODUCTCODE"]))
        logging.info(f"    After NN matching: {n_treat} treated, {n_ctrl} control PCs")

        # Post-matching setup
        df_diff["factorized"] = df_diff.PRODUCTCODE.astype("category").cat.codes
        df_diff["posttreat"] = 0
        df_diff.loc[
            (df_diff.treatment == 1) & (df_diff.year >= df_diff.year_reclassified),
            "posttreat",
        ] = 1
        df_diff["class_by_episode"] = (
            df_diff["FE"].astype(int).astype(str)
            + "[SEP]"
            + df_diff["factorized"].astype(str)
        )
        df_diff["class_by_episode"] = (
            df_diff.class_by_episode.astype("category").cat.codes
        )
        df_diff = df_diff.sort_values(
            by=["treatment_final", "class_by_episode", "year"]
        ).reset_index(drop=True)

        df_safety_dda = df_diff.copy()
        df_safety_dda.loc[df_safety_dda.treatment == 0, "year_reclassified"] = np.nan
        df_safety_dda["year_reclass_ET"] = df_safety_dda.groupby(["FE"])[
            "year_reclassified"
        ].transform(pd.Series.max)
        df_safety_dda["ET"] = df_safety_dda["year"] - df_safety_dda["year_reclass_ET"]

        # Binarize v_serious
        df_safety_dda.loc[df_safety_dda.v_serious > 0, "v_serious"] = 1

        df_safety_dda = df_safety_dda.sort_values(
            by=["class_by_episode", "year"]
        ).reset_index(drop=True)

        # Run Conley-Taber
        cols = [
            "v_serious", "posttreat", "treatment", "year",
            "factorized", "FE", "ET", "class_by_episode", "PRODUCTCODE",
        ]
        estimate, alpha025, alpha975 = conley_taber_stacked(
            df_safety_dda[cols], "v_serious", "posttreat", "treatment",
            "class_by_episode", "year", seed=config.RANDOM_SEED,
        )
        logging.info(
            f"    Estimate: {estimate:.4f}, CI: [{alpha025:.4f}, {alpha975:.4f}]"
        )
        logging.info(f"    Treat baseline: {baseline:.4f}, after: {after_t:.4f}")

        # SE = CI half-width / 1.96
        if estimate < 0:
            SE = np.abs(estimate - alpha975) / 1.96
        else:
            SE = (estimate - alpha025) / 1.96

        # k_est stores raw estimate; k_pct stores estimate/(|estimate|+after_t)
        k_est.append(estimate)
        denom_pct = np.abs(estimate) + after_t
        if denom_pct != 0 and not np.isnan(denom_pct):
            k_std.append(SE / denom_pct)
            k_pct.append(estimate / denom_pct)
        else:
            k_std.append(np.nan)
            k_pct.append(np.nan)

        logging.info(
            f"    % of outcome: {k_pct[-1] * 100 if not np.isnan(k_pct[-1]) else 'NaN'}"
        )

    return k_est, k_pct, k_std


# ============================================================================
# (C) Innovation heterogeneity by firm size (II->I and III->II)
# ============================================================================

def run_innovation_heterogeneity(reclass_type):
    """
    Tercile heterogeneity of innovation for a given reclassification type.

    Tercile boundaries use all non-null firm_size patents in
    all_patents_w_xi_oct22_24.csv.

    Within each tercile, re-filter patents by firm-size boundaries,
    aggregate to PC-year, merge onto the existing matched sample,
    and run Conley-Taber.

    Parameters:
        reclass_type: "2_1" or "3_2"

    Returns:
        k_est: list of raw estimates by tercile
        k_pct: list of estimate/baseline ratios by tercile
        k_std: list of SEs by tercile
    """
    logging.info("=" * 60)
    logging.info(f"(C) Innovation heterogeneity by firm size ({reclass_type})")

    # Load all patents with firm_size
    all_pats = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"]
    )

    # Matched sample key
    sample_key = f"{reclass_type}_onepat_innovation"
    matched_path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[sample_key]

    logging.info(f"  All patents: {len(all_pats)} rows")
    logging.info(f"  Matched sample: {matched_path}")

    k_est = []
    k_pct = []
    k_std = []

    for tercile_idx in range(NUM_TERCILES):
        logging.info(f"  Tercile {tercile_idx + 1} ({TERCILE_LABELS[tercile_idx]})")

        # Percentile boundaries on all non-null firm_size patents
        notnull = all_pats[all_pats.firm_size.notnull()]
        lower, upper = _tercile_bounds(notnull.firm_size.values, tercile_idx)
        logging.info(f"    Firm size bounds: ({lower:.2f}, {upper:.2f})")

        # Filter patents within these firm-size bounds
        temp = notnull[
            (notnull.firm_size > lower) & (notnull.firm_size < upper)
        ]
        temp = temp[["PRODUCTCODE", "year", "patents"]]
        temp = temp.groupby(["PRODUCTCODE", "year"]).sum().reset_index()
        temp["PRODUCTCODE"] = temp["PRODUCTCODE"].astype(str)

        # Balance panel
        temp = (
            temp.set_index(["PRODUCTCODE", "year"])
            .unstack(fill_value=0)
            .stack()
            .sort_index(level=1)
            .reset_index()
        )

        # Load matched sample and merge in the re-filtered patent counts
        test_main = pd.read_csv(matched_path)
        # Drop the existing 'patents' column and replace with tercile-filtered counts
        if "patents" in test_main.columns:
            test_main = test_main.drop(columns=["patents"])
        test_main = pd.merge(
            test_main, temp, on=["PRODUCTCODE", "year"], how="left"
        )
        test_main = test_main[test_main.year > 1975]
        test_main["patents"] = test_main["patents"].fillna(0)

        # Standard stacking variables
        test_main.loc[test_main.treatment == 0, "year_reclassified"] = np.nan
        test_main["year_reclass_ET"] = test_main.groupby(["FE"])[
            "year_reclassified"
        ].transform(pd.Series.max)
        test_main["class_by_episode"] = (
            test_main["FE"].astype(str) + "[SEP]" + test_main["factorized"].astype(str)
        )
        test_main["class_by_episode"] = (
            test_main.class_by_episode.astype("category").cat.codes
        )

        # Posttreat with anticipation
        anticipation = config.ANTICIPATION.get(reclass_type, 0)
        test_main["posttreat"] = 0
        test_main.loc[
            (test_main.treatment == 1)
            & (test_main.year >= test_main.year_reclassified - anticipation),
            "posttreat",
        ] = 1
        test_main["ET"] = test_main["year"] - test_main["year_reclass_ET"] + 1

        # Baseline mean
        baseline = test_main[
            (test_main.treatment == 1)
            & (test_main.ET < 0)
            & (test_main.ET >= -5)
        ]["patents"].mean()
        logging.info(f"    Baseline mean patents: {baseline:.4f}")

        # Sort for estimation
        test_main_use = test_main.sort_values(
            by=["treatment", "class_by_episode", "year"]
        ).reset_index(drop=True)

        if len(np.unique(test_main_use["PRODUCTCODE"].values)) < 5:
            logging.warning("    Too few PCs for estimation. Skipping.")
            k_est.append(np.nan)
            k_pct.append(np.nan)
            k_std.append(np.nan)
            continue

        # Run Conley-Taber
        cols = [
            "patents", "posttreat", "treatment", "class_by_episode",
            "year", "factorized", "FE", "PRODUCTCODE",
        ]
        estimate, alpha025, alpha975 = conley_taber_stacked(
            test_main_use[cols], "patents", "posttreat", "treatment",
            "class_by_episode", "year", seed=config.RANDOM_SEED,
        )
        logging.info(
            f"    Estimate: {estimate:.4f}, CI: [{alpha025:.4f}, {alpha975:.4f}]"
        )
        logging.info(
            f"    Baseline: {baseline:.4f}, ratio: {estimate / baseline if baseline != 0 else 'NaN'}"
        )

        # SE = CI half-width / 1.96
        if estimate < 0:
            SE = np.abs(estimate - alpha975) / 1.96
        else:
            SE = (estimate - alpha025) / 1.96

        k_est.append(estimate)
        k_std.append(SE)
        # k_pct stores estimate/baseline
        if baseline != 0 and not np.isnan(baseline):
            k_pct.append(estimate / baseline)
        else:
            k_pct.append(np.nan)

    return k_est, k_pct, k_std


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    t_start = time.time()

    # Storage for k_est and k_pct to pass to 08_lbd_simulation.py
    all_k_est = {}
    all_k_pct = {}

    # ================================================================
    # (A) Safety emphasis heterogeneity (II->I) -- Figure D.7a
    # ================================================================
    safety_k_est, safety_k_pct, safety_k_std = run_safety_heterogeneity()

    all_k_est["2_1_safety"] = safety_k_est
    all_k_pct["2_1_safety"] = safety_k_pct

    _bar_chart(
        safety_k_est, safety_k_std,
        ylabel="% Change in Pr(Safety Mention > 0)",
        title="Change in Safety Effort by Firm Assets",
        filename="2_1_Safety_Top_Decile_Present_oct22_24.png",
    )

    # ================================================================
    # (B) Adverse event heterogeneity (II->I) -- Figure D.7b
    # ================================================================
    adv_k_est, adv_k_pct, adv_k_std = run_adverse_event_heterogeneity()

    all_k_est["2_1_adverse"] = adv_k_est
    all_k_pct["2_1_adverse"] = adv_k_pct

    _bar_chart(
        adv_k_pct, adv_k_std,
        ylabel="% Change in Pr(Serious Event > 0)",
        title="Change in Serious Events by Firm Assets",
        filename="2_1_Deaths_Top_Decile_oct22_24.png",
        pct_scale=True,
        ylim=(-100, None),
    )

    # ================================================================
    # (C) Innovation heterogeneity -- II->I (Figure 5b)
    # ================================================================
    innov_21_k_est, innov_21_k_pct, innov_21_k_std = run_innovation_heterogeneity("2_1")

    all_k_est["2_1_innovation"] = innov_21_k_est
    all_k_pct["2_1_innovation"] = innov_21_k_pct

    _bar_chart(
        innov_21_k_est, innov_21_k_std,
        ylabel="Change in Patenting Rates",
        title="",
        filename="2_1_smallvlarge.png",
        ylim=(-0.5, 2.95),
        clean_style=True,
    )

    # ================================================================
    # (C) Innovation heterogeneity -- III->II (Figure 5a)
    # ================================================================
    innov_32_k_est, innov_32_k_pct, innov_32_k_std = run_innovation_heterogeneity("3_2")

    all_k_est["3_2_innovation"] = innov_32_k_est
    all_k_pct["3_2_innovation"] = innov_32_k_pct

    _bar_chart(
        innov_32_k_est, innov_32_k_std,
        ylabel="Change in Patenting Rates",
        title="",
        filename="3_2_smallvlarge.png",
        clean_style=True,
    )

    # ================================================================
    # Save k_est and k_pct arrays for 08_lbd_simulation.py
    # ================================================================
    logging.info("=" * 60)
    logging.info("Saving k_est and k_pct arrays...")

    rows_est = []
    for key, arr in all_k_est.items():
        for idx, label in enumerate(TERCILE_LABELS):
            rows_est.append({
                "specification": key,
                "tercile": label,
                "estimate": arr[idx] if idx < len(arr) else np.nan,
            })
    df_k_est = pd.DataFrame(rows_est)
    est_path = config.TABLES_DIR / "firm_heterogeneity_k_est.csv"
    df_k_est.to_csv(est_path, index=False)
    logging.info(f"Saved: {est_path}")

    rows_pct = []
    for key, arr in all_k_pct.items():
        for idx, label in enumerate(TERCILE_LABELS):
            rows_pct.append({
                "specification": key,
                "tercile": label,
                "ratio": arr[idx] if idx < len(arr) else np.nan,
            })
    df_k_pct = pd.DataFrame(rows_pct)
    pct_path = config.TABLES_DIR / "firm_heterogeneity_k_pct.csv"
    df_k_pct.to_csv(pct_path, index=False)
    logging.info(f"Saved: {pct_path}")

    elapsed = time.time() - t_start
    logging.info(f"Firm heterogeneity analysis complete in {elapsed:.1f}s.")


if __name__ == "__main__":
    sys.exit(main())
