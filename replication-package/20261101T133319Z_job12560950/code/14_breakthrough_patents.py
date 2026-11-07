#!/usr/bin/env python
"""
14_breakthrough_patents.py -- Table D.16: Breakthrough patents analysis.

Estimates the effect of reclassification on breakthrough patent counts
(KPST bk_p90_alqsim05 indicator). Merges KPST breakthrough data with
matched quality samples, then runs three estimation specifications:
  (1) Quasi-Poisson (via R fixest)
  (2) OLS (linear, Conley-Taber)
  (3) Log (log(y+1), Conley-Taber)

Each specification is run for both III->II and II->I reclassifications.

Source: Replication_analysis.py lines 3848-4047.

Inputs:
    data/derived/matched_sample_{reclass}_onepat_innovation_quality.csv
    data/derived/all_patents_w_xi_oct22_24.csv
    data/raw/KPST_Breakthrough.csv

Outputs:
    output/tables/BreakthroughPatents_estimates.csv
    output/tables/Formatted/TableD16_BreakthroughPatents.tex
"""

import sys
import logging
import time
import re
from pathlib import Path

import pandas as pd
import numpy as np
import scipy.stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked
from estimation import source_r_scripts, run_quasipoisson
from table_format import compute_se, significance_stars

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "14_breakthrough_patents.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Data file paths
# ============================================================================

# KPST Breakthrough data: expected in data/raw/
KPST_BREAKTHROUGH_PATH = config.RAW_DATA_DIR / "KPST_Breakthrough.csv"

# Outcome variable
OUTCOME = "bk_p90_alqsim05"
OUTCOME_LABEL = "Breakthrough Patents"

# Model specifications to run
MODEL_SPECS = ["poisson", "linear", "logged"]


# ============================================================================
# Data preparation
# ============================================================================

def load_and_merge_breakthrough(reclass_type):
    """
    Load matched quality sample and merge KPST breakthrough patent counts.

    Steps:
      1. Load matched_sample_{reclass}_onepat_innovation_quality.csv
      2. Load all_patents_w_xi_oct22_24.csv
      3. Load KPST_Breakthrough.csv
      4. Filter all_patents to those with breakthrough scores
      5. Merge breakthrough counts per (PRODUCTCODE, year)
      6. Fill missing with 0

    Returns DataFrame with bk_p90_alqsim05 column.
    """
    # Load matched quality sample
    sample_key = f"{reclass_type}_onepat_innovation_quality"
    sample_path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[sample_key]
    logging.info(f"  Loading quality sample: {sample_path}")
    firms = pd.read_csv(sample_path)

    # Load all patents
    all_pats_path = config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"]
    logging.info(f"  Loading all patents: {all_pats_path}")
    all_pats = pd.read_csv(all_pats_path)

    # Extract numeric patent_id from the 'id' column
    all_pats["patent_id"] = (
        all_pats["id"].astype(str).str.split("-").str[1]
        .apply(lambda s: re.sub(r"\D", "", s))
        .astype(str)
    )

    # Load KPST breakthrough data
    logging.info(f"  Loading KPST breakthrough: {KPST_BREAKTHROUGH_PATH}")
    breakthrough = pd.read_csv(KPST_BREAKTHROUGH_PATH)
    breakthrough["patent_id"] = breakthrough["patent_num"].astype(str)

    # Filter all_pats to those with non-null breakthrough scores
    bt_with_score = breakthrough[breakthrough[OUTCOME].notnull()]["patent_id"]
    all_pats = all_pats[all_pats.patent_id.isin(bt_with_score)]

    # Merge breakthrough score onto all_pats
    all_pats = pd.merge(
        all_pats,
        breakthrough[["patent_id", OUTCOME]],
        how="left",
        on="patent_id",
    )

    # Aggregate breakthrough count per (PRODUCTCODE, year)
    bt_by_pc_year = (
        all_pats.groupby(["PRODUCTCODE", "year"])[OUTCOME]
        .sum()
        .reset_index()
    )

    # Merge onto matched sample
    firms = pd.merge(firms, bt_by_pc_year, on=["year", "PRODUCTCODE"], how="left")
    firms[OUTCOME] = firms[OUTCOME].fillna(0)

    logging.info(
        f"  Merged sample: {len(firms)} obs, "
        f"{firms['PRODUCTCODE'].nunique()} PCs, "
        f"mean {OUTCOME}={firms[OUTCOME].mean():.3f}"
    )
    return firms


# ============================================================================
# Estimation
# ============================================================================

def run_single_estimation(firms, model, reclass_type):
    """
    Run one estimation specification (poisson/linear/logged).

    Returns dict with estimate, CIs, N, baseline stats, or None on failure.
    """
    outcome = OUTCOME
    firms_temp = firms.copy().reset_index(drop=True)

    if firms_temp["PRODUCTCODE"].nunique() < 5:
        logging.warning(f"  {outcome} [{model}]: fewer than 5 PCs, skipping")
        return None

    # class_by_episode fixed effect
    firms_temp["class_by_episode"] = (
        firms_temp["FE"].astype(str) + "[SEP]" + firms_temp["factorized"].astype(str)
    )
    firms_temp["class_by_episode"] = (
        firms_temp["class_by_episode"].astype("category").cat.codes
    )
    firms_temp = firms_temp.sort_values(
        by=["class_by_episode", "year"]
    ).reset_index(drop=True)

    # Posttreat with anticipation
    anticipation = config.ANTICIPATION[reclass_type]
    firms_temp["posttreat"] = 0
    firms_temp.loc[
        (firms_temp.treatment == 1)
        & (firms_temp.year >= firms_temp.year_reclassified - anticipation),
        "posttreat",
    ] = 1
    firms_temp = firms_temp.reset_index(drop=True)

    # Columns needed for estimation
    cols = [
        outcome, "posttreat", "treatment", "factorized",
        "year", "FE", "class_by_episode", "PRODUCTCODE",
    ]

    try:
        if model == "poisson":
            firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0
            estimate, alpha025, alpha975 = run_quasipoisson(
                firms_temp[cols], outcome
            )
        elif model == "logged":
            firms_temp[outcome] = np.log(firms_temp[outcome] + 1)
            estimate, alpha025, alpha975 = conley_taber_stacked(
                firms_temp[cols],
                outcome, "posttreat", "treatment", "class_by_episode", "year",
                seed=config.RANDOM_SEED,
            )
        else:  # linear
            estimate, alpha025, alpha975 = conley_taber_stacked(
                firms_temp[cols],
                outcome, "posttreat", "treatment", "class_by_episode", "year",
                seed=config.RANDOM_SEED,
            )
    except Exception as e:
        logging.warning(f"  {outcome} [{model}]: estimation failed ({e})")
        return None

    N = len(firms_temp.drop_duplicates(["PRODUCTCODE", "year"]))

    # Pre-treatment baseline mean (event_time in [-5, -1])
    # For logged model, compute baseline on the original (un-logged) scale
    # by reloading the original data
    if model == "logged":
        firms_orig = firms.copy().reset_index(drop=True)
        firms_orig["event_time"] = firms_orig["year"] - firms_orig["year_reclassified"]
        pre_mask = (
            (firms_orig.treatment == 1)
            & (firms_orig.event_time < 0)
            & (firms_orig.event_time > -6)
        )
        baseline_mean = firms_orig.loc[pre_mask, outcome].mean()
        baseline_sd = firms_orig.loc[pre_mask, outcome].std()
    else:
        firms_temp["event_time"] = firms_temp["year"] - firms_temp["year_reclassified"]
        pre_mask = (
            (firms_temp.treatment == 1)
            & (firms_temp.event_time < 0)
            & (firms_temp.event_time > -6)
        )
        baseline_mean = firms_temp.loc[pre_mask, outcome].mean()
        baseline_sd = firms_temp.loc[pre_mask, outcome].std()

    # Fallback for zero baseline
    if baseline_mean == 0:
        pre_mask2 = (
            (firms_temp.treatment == 1)
            & (firms_temp.event_time < 0)
            & (firms_temp.event_time > -10)
        )
        baseline_mean = firms_temp.loc[pre_mask2, outcome].mean()
    if baseline_mean == 0:
        pre_mask3 = (firms_temp.treatment == 1) & (firms_temp.event_time < 0)
        baseline_mean = firms_temp.loc[pre_mask3, outcome].mean()

    logging.info(
        f"  {outcome} [{model}, {reclass_type}]: est={estimate}, "
        f"CI=[{alpha025}, {alpha975}], N={N}, "
        f"pre-mean={baseline_mean:.2f}"
    )

    return {
        "estimate": estimate,
        "lower_CI": alpha025,
        "upper_CI": alpha975,
        "N": N,
        "baseline_mean": baseline_mean,
        "baseline_sd": baseline_sd,
    }


# ============================================================================
# LaTeX formatting
# ============================================================================

def format_latex_table(df_results):
    """
    Format Table D.16 as a LaTeX row-fragment .tex file.

    Structure: two panels (A. Class III to II, B. Class II to I).
    Each panel has one row: Breakthrough Patents.
    Columns: Outcome | Pre-mean | Q-Poisson | OLS | Log.
    """
    lines = []

    panel_labels = {
        "3_2": "A. Class III to II",
        "2_1": "B. Class II to I",
    }

    for reclass_type in ["3_2", "2_1"]:
        panel = df_results[df_results.reclass_type == reclass_type]

        lines.append(
            f"\\textbf{{{panel_labels[reclass_type]}}} & & & & \\\\"
        )
        lines.append("\\addlinespace")

        # Get results for each model spec
        poisson_row = panel[panel.Model == "poisson"]
        linear_row = panel[panel.Model == "linear"]
        logged_row = panel[panel.Model == "logged"]

        # Pre-mean (use linear model's baseline, same data before transformation)
        if not linear_row.empty:
            pre_mean = linear_row.iloc[0]["baseline"]
        elif not poisson_row.empty:
            pre_mean = poisson_row.iloc[0]["baseline"]
        else:
            pre_mean = 0.0

        # Build estimate cells for each specification
        cells_est = [f"\\hspace{{3mm}}{OUTCOME_LABEL}", f"{pre_mean:.2f}"]
        cells_se = ["", ""]

        for model_name, model_df in [
            ("poisson", poisson_row),
            ("linear", linear_row),
            ("logged", logged_row),
        ]:
            if model_df.empty:
                cells_est.append("")
                cells_se.append("")
            else:
                row = model_df.iloc[0]
                est = row["Estimate"]
                se = row["SE"]
                stars = significance_stars(est, se)
                cells_est.append(f"{est:.2f}{stars}")
                cells_se.append(f"({se:.2f})")

        lines.append(" & ".join(cells_est) + " \\\\")
        lines.append(" & ".join(cells_se) + " \\\\")
        lines.append("\\addlinespace")

    return "\n".join(lines) + "\n"


# ============================================================================
# Additive emitter: breakthrough device-type-year panel distribution
# ============================================================================
# The manuscript characterizes the breakthrough outcome (bk_p90_alqsim05) in the
# "device-type-year panel" with a single distribution summary. This emitter
# recomputes the distribution for each estimation panel this script actually
# builds and writes them to a NEW CSV, alongside the manuscript-stated reference
# for comparison. It is READ-ONLY: it reuses load_and_merge_breakthrough (no side
# effects) and never alters any existing output value or file.

def _panel_distribution(series):
    s = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    n = len(s)
    return {
        "n_obs": n,
        "pct_zero": round(100.0 * (s == 0).mean(), 2) if n else np.nan,
        "max": s.max() if n else np.nan,
        "mean": round(s.mean(), 4) if n else np.nan,
        "sd": round(s.std(), 4) if n else np.nan,
    }


def emit_breakthrough_panel_distribution():
    """
    Additive emitter (read-only): summarize the breakthrough outcome distribution
    in the device-type-year panels this script builds (each reclassification and
    pooled), and write them to a NEW CSV. Records the manuscript-stated reference
    and a `reproduces` flag for the panel the manuscript describes.
    """
    # Manuscript-stated reference for the Class III->II (3_2) breakthrough-count
    # device-type-year panel (breakthrough-patents subsection): 1,584 obs
    # (36 down-regulated device types x 44 years), ~81% zeros, max 51, mean 0.66,
    # s.d. 3.20. Authoritative source of these manuscript numbers:
    # the manuscript-number ledger and
    # code/15_intext_derived_numbers.py:derived_breakthrough_distribution() (kept in
    # sync). The reproduces flag below applies ONLY to the III->II panel this describes.
    ms = {"n_obs": 1584, "pct_zero": 81.0, "max": 51.0, "mean": 0.66, "sd": 3.20}

    rows = []
    panels = {}
    for rc in ["3_2", "2_1"]:
        try:
            firms = load_and_merge_breakthrough(rc)
        except Exception as e:
            logging.warning(f"  [bt-dist] panel {rc} unavailable ({e})")
            continue
        # device-type-year panel = unique (PRODUCTCODE, year)
        panel = firms.drop_duplicates(["PRODUCTCODE", "year"])
        panels[rc] = panel[OUTCOME]
        label = "Class III to II" if rc == "3_2" else "Class II to I"
        d = _panel_distribution(panel[OUTCOME])
        d["panel"] = f"{rc} ({label})"
        rows.append(d)

    if panels:
        d = _panel_distribution(pd.concat(list(panels.values())))
        d["panel"] = "pooled (3_2 + 2_1 unique PC-year)"
        rows.append(d)

    # Attach the manuscript reference + reproduce flag ONLY to the panel the
    # manuscript number describes (Class III->II, the 3_2 panel). The 2_1 and
    # pooled panels carry no manuscript reference, so no reproduces flag is
    # attached to them.
    for d in rows:
        is_ms_panel = d["panel"].startswith("3_2")
        if is_ms_panel:
            d["ms_n_obs"] = ms["n_obs"]
            d["ms_pct_zero"] = ms["pct_zero"]
            d["ms_max"] = ms["max"]
            d["ms_mean"] = ms["mean"]
            d["ms_sd"] = ms["sd"]
            d["reproduces"] = bool(
                d["n_obs"] == ms["n_obs"]
                and (not pd.isna(d["mean"])) and abs(d["mean"] - ms["mean"]) < 0.05
                and (not pd.isna(d["sd"])) and abs(d["sd"] - ms["sd"]) < 0.05
                and (not pd.isna(d["max"])) and d["max"] == ms["max"]
            )
        else:
            d["ms_n_obs"] = d["ms_pct_zero"] = d["ms_max"] = d["ms_mean"] = d["ms_sd"] = ""
            d["reproduces"] = "n/a (no manuscript reference for this panel)"
        logging.info(f"  [bt-dist] {d['panel']}: n={d['n_obs']} "
                     f"pct_zero={d['pct_zero']} max={d['max']} mean={d['mean']} "
                     f"sd={d['sd']} reproduces={d['reproduces']}")

    cols = ["panel", "n_obs", "pct_zero", "max", "mean", "sd",
            "ms_n_obs", "ms_pct_zero", "ms_max", "ms_mean", "ms_sd", "reproduces"]
    out_path = config.TABLES_DIR / "BreakthroughPanel_distribution.csv"
    pd.DataFrame(rows, columns=cols).to_csv(out_path, index=False)
    logging.info(f"Saved breakthrough panel distribution: {out_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    t0 = time.time()
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    (config.TABLES_DIR / "Formatted").mkdir(parents=True, exist_ok=True)

    source_r_scripts()

    logging.info("=" * 60)
    logging.info("14_breakthrough_patents.py — Table D.16")
    logging.info("=" * 60)

    # Check for KPST data
    if not KPST_BREAKTHROUGH_PATH.exists():
        logging.error(
            f"KPST Breakthrough data not found at {KPST_BREAKTHROUGH_PATH}. "
            f"Please copy KPST_Breakthrough.csv to {config.RAW_DATA_DIR}/"
        )
        sys.exit(1)

    # Collect results
    results = []

    for model in MODEL_SPECS:
        for reclass_type in ["3_2", "2_1"]:
            logging.info(f"\n--- Model={model}, Reclass={reclass_type} ---")

            # Load and merge breakthrough data
            firms = load_and_merge_breakthrough(reclass_type)

            # Run estimation
            result = run_single_estimation(firms, model, reclass_type)

            if result is not None:
                se = compute_se(
                    result["estimate"], result["lower_CI"], result["upper_CI"]
                )
                results.append({
                    "outcome": OUTCOME,
                    "formal_name": OUTCOME_LABEL,
                    "reclass_type": reclass_type,
                    "Model": model,
                    "Estimate": result["estimate"],
                    "lower_CI": result["lower_CI"],
                    "upper_CI": result["upper_CI"],
                    "SE": se,
                    "baseline": result["baseline_mean"],
                    "baseline_sd": result["baseline_sd"],
                    "Sample Size": result["N"],
                })

    # Build results DataFrame
    df_results = pd.DataFrame(results)

    # Compute t-stats and stars
    df_results["tstat"] = np.abs(df_results["Estimate"] / df_results["SE"])
    ninety = scipy.stats.norm.ppf(0.95)
    ninety5 = scipy.stats.norm.ppf(0.975)
    ninety9 = scipy.stats.norm.ppf(0.995)
    ninety9point9 = scipy.stats.norm.ppf(0.9995)
    df_results["stars"] = ""
    df_results.loc[df_results["tstat"] > ninety, "stars"] = "+"
    df_results.loc[df_results["tstat"] > ninety5, "stars"] = "*"
    df_results.loc[df_results["tstat"] > ninety9, "stars"] = "**"
    df_results.loc[df_results["tstat"] > ninety9point9, "stars"] = "***"

    # Log summary
    logging.info("\n" + "=" * 60)
    logging.info("RESULTS SUMMARY — Table D.16 (Breakthrough Patents)")
    logging.info("=" * 60)
    for _, row in df_results.iterrows():
        logging.info(
            f"  {row['reclass_type']} | {row['Model']:8s} | "
            f"pre-mean={row['baseline']:.2f} | "
            f"est={row['Estimate']:.2f}{row['stars']} ({row['SE']:.2f}) | "
            f"N={int(row['Sample Size'])}"
        )

    # Verification against manuscript targets
    logging.info("\n--- Manuscript target comparison ---")
    targets = {
        ("3_2", "poisson"): {"pre_mean": 0.98, "est": 0.54, "se": 0.44},
        ("3_2", "linear"):  {"pre_mean": 0.98, "est": 0.68, "se": 0.21},
        ("3_2", "logged"):  {"pre_mean": 0.98, "est": 0.10, "se": 0.03},
        ("2_1", "poisson"): {"pre_mean": 2.98, "est": 0.19, "se": 0.26},
        ("2_1", "linear"):  {"pre_mean": 2.98, "est": 0.66, "se": 0.00},
        ("2_1", "logged"):  {"pre_mean": 2.98, "est": 0.05, "se": 0.00},
    }
    for _, row in df_results.iterrows():
        key = (row["reclass_type"], row["Model"])
        if key in targets:
            t = targets[key]
            logging.info(
                f"  {key}: target est={t['est']:.2f} SE=({t['se']:.2f}) | "
                f"actual est={row['Estimate']:.2f} SE=({row['SE']:.2f})"
            )

    # Save raw estimates CSV
    csv_path = config.TABLES_DIR / "BreakthroughPatents_estimates.csv"
    df_results.to_csv(csv_path, index=False)
    logging.info(f"\nSaved estimates CSV: {csv_path}")

    # Save formatted LaTeX
    tex_content = format_latex_table(df_results)
    tex_path = config.TABLES_DIR / "Formatted" / "TableD16_BreakthroughPatents.tex"
    with open(tex_path, "w") as f:
        f.write(tex_content)
    logging.info(f"Saved LaTeX fragment: {tex_path}")

    # Additive emitter (read-only, new CSV only): breakthrough panel distribution.
    # Guarded so it can never break the pipeline.
    try:
        emit_breakthrough_panel_distribution()
    except Exception as e:
        logging.warning(f"emit_breakthrough_panel_distribution skipped: {e}")

    elapsed = time.time() - t0
    logging.info(f"\nTotal runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    sys.exit(main())
