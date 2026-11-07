#!/usr/bin/env python
"""
06a_safety_analysis.py — Safety patent emphasis DiD analysis.

Constructs safety_prop (share of patents emphasizing safety), does
nearest-neighbor matching on pre-event safety_prop, runs Conley-Taber
stacked DiD for both II→I and III→II.

MUST run before 04_event_studies.py (produces safety_did_analysis.csv).

Inputs:
    data/derived/safety_vars_allpats.csv
    data/derived/all_patents_w_xi_oct22_24.csv
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_3_2_onepat.csv
    data/derived/Adverse_fsize_ready_all4_oct22_24.csv
Outputs:
    data/derived/safety_did_analysis.csv
    data/derived/safety_did_analysis_3_2.csv
    output/tables/ (safety table rows)
"""

import sys
import logging
import time
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked
from match_mahal import get_similar
from plotting import save_figure
from table_format import significance_stars

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "06a_safety_analysis.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def _nn_match_safety(df_orig, reclass_type):
    """
    Nearest-neighbor matching on pre-event safety_prop.

    For each treated PC, find the closest control PC by safety_prop
    in the 2 years before reclassification.
    """
    temp_parts = []
    control_list = []
    treated_pcs = np.unique(df_orig[df_orig.treatment_final == 1]["PRODUCTCODE"])

    for i, PC in enumerate(treated_pcs):
        treated = df_orig[df_orig.PRODUCTCODE == PC].copy()
        yr_reclass = treated["year_reclassified"].values[0]
        treated["event_time"] = treated["year"] - int(float(yr_reclass))

        # First try: exclude already-matched controls
        control = df_orig[
            (df_orig.treatment_final == 0) & ~(df_orig.PRODUCTCODE.isin(control_list))
        ].copy()

        if len(control) == 0:
            # Fallback: use all controls
            control = df_orig[df_orig.treatment_final == 0].copy()

        control["event_time"] = control["year"] - int(float(yr_reclass))

        control_meaned = (
            control[(control.event_time < 0) & (control.event_time > -3)]
            .groupby("PRODUCTCODE")
            .mean(numeric_only=True)
            .reset_index()
        )
        treated_meaned = treated[
            (treated.event_time < 0) & (treated.event_time > -3)
        ].mean(numeric_only=True)

        if len(control_meaned) == 0:
            logging.warning(f"No controls for {PC}. Skipping.")
            continue

        sim_distances, sim_indices = get_similar(
            treated_meaned[["safety_prop"]].values,
            control_meaned[["safety_prop"]].values,
            topn=1,
        )
        PC_CONTROL = control_meaned.iloc[sim_indices]["PRODUCTCODE"].values[0]
        control_list.append(PC_CONTROL)

        control_keep = df_orig[df_orig.PRODUCTCODE == PC_CONTROL].copy()
        control_keep["FE"] = i
        treated["FE"] = i

        temp_parts.append(control_keep)
        temp_parts.append(treated)

    temp = pd.concat(temp_parts, ignore_index=True)
    temp = temp.drop_duplicates(subset=["year", "PRODUCTCODE", "FE"])
    return temp


def _build_safety_panel(df_safety_raw, all_pats, matched_sample, reclass_type):
    """
    Build the safety DiD panel: aggregate patents and safety counts by PC-year,
    merge treatment status, then run nearest-neighbor matching.
    """
    # Merge patent-level data
    if reclass_type == "2_1":
        df_safety_keep = df_safety_raw[
            df_safety_raw.id.isin(all_pats[all_pats.firm_size.notnull()]["id"])
        ]
        df_safety_keep = pd.merge(
            df_safety_keep,
            all_pats[["id", "firm_size", "permno", "PRODUCTCODE", "year"]],
            how="left", on="id",
        )
        # Keep patents from firms in adverse event data
        w_fsize = pd.read_csv(
            config.DERIVED_DATA_DIR / "Adverse_fsize_ready_all4_oct22_24.csv"
        )
        df_safety_keep_w_permno = df_safety_keep[
            df_safety_keep.permno.isin(w_fsize.permno)
        ]
    else:
        # For III→II: use all patents (no firm size filter)
        df_safety_keep_vars = pd.merge(
            df_safety_raw,
            all_pats[["id", "PRODUCTCODE", "year"]],
            how="left", on="id",
        )
        df_safety_keep_w_permno = df_safety_keep_vars.copy()

    # Merge treatment status from matched sample
    df_safety_keep_w_permno = pd.merge(
        df_safety_keep_w_permno,
        matched_sample[["PRODUCTCODE", "treatment"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )

    # Keep PCs in matched sample or controls not in matched sample
    df_safety_keep_w_permno = df_safety_keep_w_permno[
        (df_safety_keep_w_permno.PRODUCTCODE.isin(matched_sample.PRODUCTCODE.values))
        | df_safety_keep_w_permno.treatment.isnull()
    ]

    # Aggregate to PC-year level
    df_dd = df_safety_keep_w_permno.copy()
    df_dd = df_dd[df_dd.year >= 1976]
    df_dd = (
        df_dd[["PRODUCTCODE", "year", "patents", "safety"]]
        .groupby(["PRODUCTCODE", "year"])
        .sum()
        .reset_index()
    )

    # Balance panel
    df_dd = (
        df_dd.set_index(["PRODUCTCODE", "year"])
        .unstack(fill_value=0)
        .stack()
        .sort_index(level=1)
        .reset_index()
    )

    # Merge treatment info
    df_dd = pd.merge(
        df_dd,
        matched_sample[["PRODUCTCODE", "treatment", "year_reclassified"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )
    df_dd.loc[df_dd.treatment.isnull(), "treatment"] = 0
    df_dd = df_dd.reset_index(drop=True)

    # Consolidate treatment across PC
    df_dd["year_reclassfinal"] = df_dd.groupby("PRODUCTCODE")[
        "year_reclassified"
    ].transform(pd.Series.max)
    df_dd["treatment_final"] = df_dd.groupby("PRODUCTCODE")[
        "treatment"
    ].transform(pd.Series.max)
    df_dd["treatment"] = df_dd["treatment_final"]
    df_dd["year_reclassified"] = df_dd["year_reclassfinal"]

    # Safety proportion
    df_dd["FE"] = np.nan
    df_dd.loc[df_dd.treatment == 0, "FE"] = 0
    df_dd["safety_prop"] = df_dd["safety"] / df_dd["patents"]
    df_dd["safety_prop"] = df_dd["safety_prop"].fillna(0)

    # Nearest-neighbor matching
    df_dd = _nn_match_safety(df_dd, reclass_type)

    # Post-matching setup
    df_dd.loc[df_dd.treatment == 0, "year_reclassified"] = np.nan
    df_dd["year_reclass_ET"] = df_dd.groupby(["FE"])["year_reclassified"].transform(
        pd.Series.max
    )
    df_dd["factorized"] = df_dd.PRODUCTCODE.astype("category").cat.codes
    df_dd["class_by_episode"] = (
        df_dd["FE"].astype(int).astype(str) + "[SEP]" + df_dd["factorized"].astype(str)
    )
    df_dd["class_by_episode"] = df_dd.class_by_episode.astype("category").cat.codes

    # Posttreat with 1-year anticipation
    df_dd["posttreat"] = 0
    df_dd.loc[
        (df_dd.treatment == 1) & (df_dd.year >= df_dd.year_reclassified - 1),
        "posttreat",
    ] = 1
    df_dd["ET"] = df_dd["year"] - df_dd["year_reclass_ET"] + 1

    # Binarize safety_prop
    df_dd.loc[df_dd["safety_prop"] > 0, "safety_prop"] = 1
    df_dd["baseline_event_count"] = df_dd.groupby("PRODUCTCODE")[
        "safety_prop"
    ].transform(pd.Series.max)
    df_dd = df_dd.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)

    n_treated = len(set(df_dd[df_dd.treatment_final == 1]["PRODUCTCODE"]))
    n_control = len(set(df_dd[df_dd.treatment_final == 0]["PRODUCTCODE"]))
    logging.info(
        f"Safety panel ({reclass_type}): {n_treated} treated PCs, {n_control} control PCs"
    )

    return df_dd


def _fmt(val):
    """Format a float to 2 decimal places (matches 10_table_formatting.py)."""
    return f"{val:.2f}"


def _run_safety_did(df_dd, reclass_type):
    """Run Conley-Taber stacked DiD on the safety panel.

    Returns (estimate, alpha025, alpha975, baseline_mean, baseline_std, table_row).
    """
    # Baseline stats
    mask = (
        (df_dd.treatment_final == 1)
        & (df_dd.year - df_dd.year_reclassfinal < -1)
        & (df_dd.year - df_dd.year_reclassfinal > -4)
    )
    baseline_mean = df_dd.loc[mask, "safety_prop"].mean()
    baseline_std = df_dd.loc[mask, "safety_prop"].std()

    logging.info(f"Baseline safety_prop ({reclass_type}): mean={baseline_mean:.4f}, std={baseline_std:.4f}")

    cols = [
        "safety_prop", "posttreat", "treatment", "class_by_episode",
        "year", "factorized", "FE", "PRODUCTCODE",
    ]
    estimate, alpha025, alpha975 = conley_taber_stacked(
        df_dd[cols], "safety_prop", "posttreat", "treatment",
        "class_by_episode", "year", seed=config.RANDOM_SEED,
    )

    se = (estimate - alpha025) / 1.96
    logging.info(
        f"Safety DiD ({reclass_type}): est={estimate:.3f}, "
        f"CI=[{alpha025:.3f}, {alpha975:.3f}], SE={se:.3f}"
    )

    # Format table row (matches original .tex row-fragment style)
    mean_s = _fmt(baseline_mean)
    est_s = _fmt(estimate)
    std_s = _fmt(baseline_std)
    se_s = _fmt(se)

    stars = significance_stars(estimate, se)
    table_row = (
        f"\\hspace{{6mm}} Emphasis on Safety & {mean_s} & "
        f"{est_s}{stars}&- & - \\\\ \n"
        f"  & ({std_s}) & ({se_s}) & - & - \\\\"
    )
    print(table_row)

    return estimate, alpha025, alpha975, baseline_mean, baseline_std, table_row


def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.DERIVED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    formatted_dir = config.TABLES_DIR / "Formatted"
    formatted_dir.mkdir(parents=True, exist_ok=True)

    # Load shared data
    df_safety = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["safety_vars"])
    df_safety["patents"] = 1
    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])

    # ================================================================
    # II→I Safety Analysis
    # ================================================================
    logging.info("=" * 60)
    logging.info("Starting II→I safety analysis")
    t0 = time.time()

    matched_21 = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"])
    df_safety_21 = _build_safety_panel(df_safety, all_pats, matched_21, "2_1")

    # Raw trend: safety emphasis by treatment status (binarized: any safety patent)
    raw_safety = df_safety_21.drop_duplicates(subset=["PRODUCTCODE", "year"]).copy()
    means = raw_safety.groupby(["year", "treatment_final"])["safety_prop"].mean().reset_index()
    treated_m = means[means.treatment_final == 1].sort_values("year")
    control_m = means[means.treatment_final == 0].sort_values("year")

    median_yr = raw_safety.loc[
        raw_safety.treatment_final == 1, "year_reclassified"
    ].dropna().median()

    style.use("seaborn-v0_8-poster")
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(treated_m["year"], treated_m["safety_prop"], "-o",
            color=config.COLORS["dereg_line"], label="Treated Device Types",
            linewidth=2, markersize=6)
    ax.plot(control_m["year"], control_m["safety_prop"], "-o",
            color="#e76f51", label="Control Device Types",
            linewidth=2, markersize=6)
    ax.axvline(x=median_yr, ls="--", lw=1.5, color="black")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_xlabel("Year", fontsize=22)
    ax.set_ylabel("Pr of Safety Mention", fontsize=22)
    ax.set_title("Probability of Safety Mention by Treatment Status",
                 fontsize=26, pad=20)
    ax.legend(fontsize=16, frameon=True)
    ax.tick_params(labelsize=14)
    save_figure(fig, "Safety_emphasis_raw_trends.png")

    # Save for event studies
    outpath_21 = config.DERIVED_DATA_DIR / config.SAFETY_FILES["safety_did_2_1"]
    df_safety_21.to_csv(outpath_21, index=False)
    logging.info(f"Saved: {outpath_21}")

    est_21 = _run_safety_did(df_safety_21, "2_1")
    tex_path_21 = formatted_dir / "PaperRegTableSafety_IItoI_NoLog.tex"
    tex_path_21.write_text(est_21[-1])
    logging.info(f"Wrote table row: {tex_path_21}")
    logging.info(f"II→I safety completed in {time.time() - t0:.1f}s")

    # ================================================================
    # III→II Safety Analysis
    # ================================================================
    logging.info("=" * 60)
    logging.info("Starting III→II safety analysis")
    t0 = time.time()

    matched_32 = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat"])
    df_safety_32 = _build_safety_panel(df_safety, all_pats, matched_32, "3_2")

    # Save for event studies
    outpath_32 = config.DERIVED_DATA_DIR / config.SAFETY_FILES["safety_did_3_2"]
    df_safety_32.to_csv(outpath_32, index=False)
    logging.info(f"Saved: {outpath_32}")

    est_32 = _run_safety_did(df_safety_32, "3_2")
    tex_path_32 = formatted_dir / "PaperRegTableSafety_IIItoII_NoLog.tex"
    tex_path_32.write_text(est_32[-1])
    logging.info(f"Wrote table row: {tex_path_32}")
    logging.info(f"III→II safety completed in {time.time() - t0:.1f}s")

    logging.info("Safety analysis complete.")


if __name__ == "__main__":
    sys.exit(main())
