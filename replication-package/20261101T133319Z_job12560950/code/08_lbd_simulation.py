#!/usr/bin/env python
"""
08_lbd_simulation.py -- Learning-by-doing experience tercile estimation.

Loads firm-level cumulative experience data (from Fuzzy_matching_lbd_vars.py
output), splits firms into experience terciles, runs Conley-Taber stacked
DiD for each tercile to estimate the treatment effect on device approvals
by experience level, and produces the LBD estimation bar chart.

Source: Replication_analysis.py lines 6290-7330.

Inputs:
    data/derived/LBD_ApprovalTime_Both_oct22_24.csv
    data/derived/matched_sample_3_2_onepat_innovation.csv

Outputs:
    output/figures/LBDEstimation.png
    output/figures/LBDEstimation_ProductCount.png  (robustness: product count measure)
    output/tables/lbd_tercile_estimation.csv
    output/tables/lbd_tercile_estimation_product_count.csv
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
from conley_taber import conley_taber_stacked
import matplotlib.pyplot as plt
from plotting import create_figure, save_figure, setup_standard_axes

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "08_lbd_simulation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Number of experience terciles (matches firm-size heterogeneity binning)
N_TERCILES = 3
TERCILE_LABELS = ["First", "Second", "Third"]


# ============================================================================
# Data loading
# ============================================================================

def load_lbd_experience():
    """
    Load the LBD cumulative experience data.
    This is the output of Fuzzy_matching_lbd_vars.py (both PMA and 510k combined).
    """
    lbd_path = config.DERIVED_DATA_DIR / "LBD_ApprovalTime_Both_oct22_24.csv"
    if not lbd_path.exists():
        # Required on both official routes (step 4 writes it on the restricted route; the
        # simulated payload materializes it).
        raise FileNotFoundError(
            f"LBD experience file not found: {lbd_path}. Run step 4 "
            "(00_generate_data/gen_03_lbd.py) or materialize the simulated payload first.")

    df = pd.read_csv(lbd_path)
    df["dev_count_lbd"] = 1
    df["PRODUCTCODE"] = df["PRODUCTCODE"].str.upper()
    df = df[df.cumsum_time_t1.notnull()]

    # Construct alternative proficiency measure: cumulative product count
    # (number of prior device approvals by same firm, ordered by cluster id)
    df = df.sort_values(["cluster id app", "cluster id"])
    df["cum_product_count_t1"] = df.groupby("cluster id app").cumcount() + 1

    logging.info(f"Loaded LBD experience data: {len(df)} rows, "
                 f"{df.PRODUCTCODE.nunique()} product codes")
    return df


def load_matched_sample_32():
    """Load the III->II matched sample for innovation outcomes."""
    path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat_innovation"]
    if not path.exists():
        raise FileNotFoundError(
            f"Matched sample not found: {path}. Run step 9 (02_match_samples.py) first.")
    df = pd.read_csv(path)
    # Keep only FDA-initiated reclassifications
    if "FDA_own_accord" in df.columns:
        df = df[df.FDA_own_accord == 1]
    logging.info(f"Loaded 3->2 matched sample: {len(df)} rows")
    return df


# ============================================================================
# LBD tercile estimation
# ============================================================================

def run_lbd_tercile_estimation(Cumsumtime_df, test_main_base,
                                experience_col="cumsum_time_t1"):
    """
    Split LBD experience data into terciles, merge with the matched sample,
    and run Conley-Taber stacked DiD for each tercile.

    For each experience tercile, filter the LBD data to firms in that tercile,
    aggregate device counts at (PRODUCTCODE, year), merge with the matched
    sample, and estimate the treatment effect on dev_count_lbd.

    Percentile boundaries are computed on the filtered (experience > 1)
    distribution to match the data actually used in estimation.

    Parameters:
        Cumsumtime_df: LBD experience DataFrame
        test_main_base: base matched sample (3->2 innovation, FDA own accord)
        experience_col: column to use for tercile splits (default: cumsum_time_t1)

    Returns:
        k_est: list of point estimates by tercile (normalized by baseline)
        k_std: list of SEs by tercile (normalized by baseline)
        k_pct: list of percent changes by tercile
        baseline_listdev: list of baseline means by tercile
    """
    k_est = []
    k_std = []
    k_pct = []
    baseline_listdev = []

    logging.info(f"  Experience measure: {experience_col}")

    # Compute percentile boundaries on the filtered distribution
    # (experience > 1) to match the data used in estimation.
    filtered_exp = Cumsumtime_df[Cumsumtime_df[experience_col] > 1][experience_col]

    for i in range(N_TERCILES):
        temp = Cumsumtime_df.copy()
        # Only intensive margin (experience > 1) to avoid
        # bias from latent variable at extensive margin
        temp = temp[temp[experience_col] > 1]

        lo_pctile = np.percentile(filtered_exp,
                                   100 / N_TERCILES * i)
        hi_pctile = np.percentile(filtered_exp,
                                   100 / N_TERCILES * i + 100 / N_TERCILES)
        if experience_col == "cum_product_count_t1":
            # Discrete measure: use <= for upper bound to avoid empty bins
            temp = temp[
                (temp[experience_col] > lo_pctile) &
                (temp[experience_col] <= hi_pctile)
            ]
        else:
            temp = temp[
                (temp[experience_col] > lo_pctile) &
                (temp[experience_col] < hi_pctile)
            ]
        temp = temp[["PRODUCTCODE", "year", "dev_count_lbd"]]
        temp = temp.groupby(["PRODUCTCODE", "year"]).sum().reset_index()

        # Balanced panel: fill missing (PRODUCTCODE, year) with 0
        temp["PRODUCTCODE"] = temp["PRODUCTCODE"].astype(str)
        temp = (
            temp.set_index(["PRODUCTCODE", "year"])
            .unstack(fill_value=0)
            .stack()
            .sort_index(level=1)
            .reset_index()
        )

        # Merge with matched sample
        test_main = test_main_base.copy()
        test_main["class_by_episode"] = (
            test_main["FE"].astype(str) + "[SEP]"
            + test_main["factorized"].astype(str)
        )
        test_main["class_by_episode"] = (
            test_main.class_by_episode.astype("category").cat.codes
        )
        test_main = test_main.sort_values(
            by=["treatment", "class_by_episode", "year"]
        ).reset_index(drop=True)
        test_main = pd.merge(test_main, temp,
                              on=["PRODUCTCODE", "year"], how="left")

        n_treat = len(set(test_main[test_main.treatment == 1]["PRODUCTCODE"]))
        n_ctrl = len(set(test_main[test_main.treatment == 0]["PRODUCTCODE"]))
        logging.info(f"  T{i+1}: {n_treat} treated PCs, {n_ctrl} control PCs")

        test_main = test_main[test_main.year > 1975]
        test_main.dev_count_lbd = test_main.dev_count_lbd.fillna(0)
        test_main["event_time"] = test_main["year"] - test_main["year_reclassified"]

        # Pre-treatment baseline mean (5-year window before reclassification)
        baseline = test_main[
            (test_main.treatment == 1) &
            (test_main.event_time < 0) &
            (test_main.event_time >= -5)
        ]["dev_count_lbd"].mean()

        if baseline == 0:
            baseline = test_main[
                (test_main.treatment == 1) & (test_main.event_time < 0)
            ]["dev_count_lbd"].mean()

        test_main_use = test_main.copy()

        if len(np.unique(test_main_use["PRODUCTCODE"].values)) < 5:
            logging.warning(f"  T{i+1}: too few product codes, skipping")
            k_est.append(np.nan)
            k_std.append(np.nan)
            k_pct.append(np.nan)
            baseline_listdev.append(baseline)
            continue

        cols_needed = [
            "dev_count_lbd", "posttreat", "treatment",
            "class_by_episode", "year", "FE", "factorized", "PRODUCTCODE",
        ]
        available_cols = [c for c in cols_needed if c in test_main_use.columns]

        try:
            estimate, alpha025, alpha975 = conley_taber_stacked(
                test_main_use[available_cols],
                "dev_count_lbd", "posttreat", "treatment",
                "class_by_episode", "year",
                seed=config.RANDOM_SEED,
            )
            logging.info(
                f"  T{i+1}: est={estimate:.4f}, "
                f"CI=[{alpha025:.4f}, {alpha975:.4f}]"
            )
            logging.info(
                f"  T{i+1}: pct_change={estimate/baseline*100:.2f}%, "
                f"baseline={baseline:.4f}"
            )

            # SE = CI half-width / 1.96
            if estimate < 0:
                SE = np.abs(estimate - alpha975) / 1.96
            else:
                SE = (estimate - alpha025) / 1.96

            k_est.append(estimate / baseline)
            k_std.append(SE / baseline)
            k_pct.append((estimate / baseline) * 100)
            baseline_listdev.append(baseline)

        except Exception as e:
            logging.error(f"  T{i+1} estimation failed: {e}")
            k_est.append(np.nan)
            k_std.append(np.nan)
            k_pct.append(np.nan)
            baseline_listdev.append(baseline)

    return k_est, k_std, k_pct, baseline_listdev


# ============================================================================
# Figures
# ============================================================================

def produce_lbd_estimation_figure(k_est, k_std,
                                   filename="LBDEstimation.png",
                                   xlabel="Cumulative Experience Terciles"):
    """
    Produce the LBD estimation bar chart.
    Shows percent change in new devices by experience tercile.
    """
    logging.info(f"Producing LBD estimation figure: {filename}...")

    fig, ax = create_figure(nrows=1, ncols=1, figsize=(12, 8))

    colors = ["#264653", "#2a9d8f", "#f4a261"]
    ax.bar(
        TERCILE_LABELS,
        np.array(k_est) * 100,
        yerr=np.array(k_std) * 100,
        align="center",
        color=colors,
        alpha=0.9,
        error_kw=dict(lw=1),
    )

    ax.set_ylabel("Percent Change", fontsize=24)
    ax.set_xlabel(xlabel, fontsize=24)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.tick_params(axis="both", which="both", length=0)
    ax.tick_params(axis="x", labelsize=16)
    ax.tick_params(axis="y", labelsize=16)

    # Save with bbox_inches='tight' at default DPI to match original output
    outpath = config.FIGURES_DIR / filename
    fig.savefig(outpath, bbox_inches="tight")
    print(f"Saved: {outpath}")
    plt.close(fig)


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    t_start = time.time()

    # ================================================================
    # Step 1: Load LBD experience data
    # ================================================================
    logging.info("=" * 60)
    logging.info("Step 1: Loading data...")

    # Both loaders raise on a missing required input (see above): this step cannot
    # produce its exhibits without them, so it must not exit 0.
    Cumsumtime_df = load_lbd_experience()
    test_main_base = load_matched_sample_32()

    # Ensure factorized column exists
    if "factorized" not in test_main_base.columns:
        test_main_base["factorized"] = (
            test_main_base["PRODUCTCODE"].astype("category").cat.codes
        )

    # ================================================================
    # Step 2: LBD tercile estimation (Conley-Taber by experience tercile)
    # ================================================================
    logging.info("=" * 60)
    logging.info("Step 2: Running LBD tercile estimation (cumulative time)...")

    k_est, k_std, k_pct, baseline_listdev = run_lbd_tercile_estimation(
        Cumsumtime_df, test_main_base, experience_col="cumsum_time_t1"
    )

    # Save tercile estimation results
    df_terc_est = pd.DataFrame({
        "tercile": TERCILE_LABELS,
        "k_est": k_est,
        "k_std": k_std,
        "k_pct": k_pct,
        "baseline_dev": baseline_listdev,
    })
    terc_path = config.TABLES_DIR / "lbd_tercile_estimation.csv"
    df_terc_est.to_csv(terc_path, index=False)
    logging.info(f"Saved: {terc_path}")

    # ================================================================
    # Step 3: Produce LBD estimation bar chart (main)
    # ================================================================
    logging.info("=" * 60)
    logging.info("Step 3: Producing LBD estimation figure (cumulative time)...")
    produce_lbd_estimation_figure(k_est, k_std)

    # ================================================================
    # Step 4: Robustness — product count proficiency measure
    # ================================================================
    logging.info("=" * 60)
    logging.info("Step 4: Running LBD tercile estimation (product count)...")

    k_est_pc, k_std_pc, k_pct_pc, baseline_pc = run_lbd_tercile_estimation(
        Cumsumtime_df, test_main_base, experience_col="cum_product_count_t1"
    )

    df_terc_pc = pd.DataFrame({
        "tercile": TERCILE_LABELS,
        "k_est": k_est_pc,
        "k_std": k_std_pc,
        "k_pct": k_pct_pc,
        "baseline_dev": baseline_pc,
    })
    terc_pc_path = config.TABLES_DIR / "lbd_tercile_estimation_product_count.csv"
    df_terc_pc.to_csv(terc_pc_path, index=False)
    logging.info(f"Saved: {terc_pc_path}")

    # ================================================================
    # Step 5: Produce robustness figure (product count)
    # ================================================================
    logging.info("=" * 60)
    logging.info("Step 5: Producing LBD estimation figure (product count)...")
    produce_lbd_estimation_figure(
        k_est_pc, k_std_pc,
        filename="LBDEstimation_ProductCount.png",
        xlabel="Cumulative Product Count Terciles",
    )

    elapsed = time.time() - t_start
    logging.info("=" * 60)
    logging.info(f"LBD simulation complete in {elapsed:.1f}s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
