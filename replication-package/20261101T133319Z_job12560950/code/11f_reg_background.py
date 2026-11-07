#!/usr/bin/env python
"""
11f_reg_background.py -- Regulatory background figure (Figure D.1).

Plots bar charts showing the count of reclassification events by year,
separately for II->I (deregulation) and III->II (down-regulation) events.

Inputs:
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_3_2_onepat.csv

Outputs:
    output/figures/Distribution_of_2_1_over_years.png
    output/figures/Distribution_of_3_2_over_years.png
"""

import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "11f_reg_background.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


# ============================================================================
# Figure D.1a: Distribution of II->I deregulation events over years
# ============================================================================

def figure_D1a(df_2_1, output_path):
    """
    Bar chart: count of unique product codes reclassified from Class II to
    Class I, by year_reclassified.
    """
    logging.info("Producing Figure D.1a: distribution of II->I events by year.")

    # Filter to treated PCs, deduplicate by product code, group by year
    threetwo = (
        df_2_1[df_2_1.treatment == 1]
        .drop_duplicates("PRODUCTCODE")
        .groupby("year_reclassified")
        .count()["year"]
        .reset_index()
    )
    threetwo["count"] = threetwo["year"]
    threetwo["year_reclassified"] = threetwo["year_reclassified"].astype(int)
    threetwo = threetwo.set_index("year_reclassified")["count"]

    # Complete year range (1988-2015 as in original)
    all_years = range(1988, 2015 + 1)
    threetwo = threetwo.reindex(all_years, fill_value=0)

    logging.info(
        f"II->I events: {threetwo.sum()} total across {(threetwo > 0).sum()} years."
    )

    # Plot
    ax = threetwo.plot(
        kind="bar",
        figsize=(12, 8),
        color="#2a9d8f",
        edgecolor="black",
    )
    ax.set_xlabel("Year", fontsize=18)
    ax.set_ylabel("Count", fontsize=18)
    ax.set_title(
        "Count of Deregulation Events By Year",
        fontsize=24,
        weight="bold",
        pad=20,
    )
    ax.grid(True, which="major", linestyle="--", linewidth=0.5)

    plt.tight_layout()

    # Show every other year on x-axis
    n = 2
    ticks_to_show = list(range(0, len(threetwo.index), n))
    ax.set_xticks(ticks_to_show)
    ax.set_xticklabels(
        [threetwo.index[i] for i in ticks_to_show], ha="center", rotation=0, fontsize=14
    )
    ax.tick_params(axis="y", labelsize=14)

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close()


# ============================================================================
# Figure D.1b: Distribution of III->II down-regulation events over years
# ============================================================================

def figure_D1b(df_3_2, output_path):
    """
    Bar chart: count of unique product codes reclassified from Class III to
    Class II, by year_reclassified.
    """
    logging.info("Producing Figure D.1b: distribution of III->II events by year.")

    # Filter to treated PCs, deduplicate by product code, group by year
    threetwo = (
        df_3_2[df_3_2.treatment == 1]
        .drop_duplicates("PRODUCTCODE")
        .groupby("year_reclassified")
        .count()["year"]
        .reset_index()
    )
    threetwo["count"] = threetwo["year"]
    threetwo["year_reclassified"] = threetwo["year_reclassified"].astype(int)
    threetwo = threetwo.set_index("year_reclassified")["count"]

    # Complete year range from data bounds
    start_year = threetwo.index.min()
    end_year = threetwo.index.max()
    all_years = range(start_year, end_year + 1)
    threetwo = threetwo.reindex(all_years, fill_value=0)

    logging.info(
        f"III->II events: {threetwo.sum()} total across {(threetwo > 0).sum()} years."
    )

    # Plot
    ax = threetwo.plot(
        kind="bar",
        figsize=(12, 8),
        color="#984c2a",
        edgecolor="black",
    )
    ax.set_xlabel("Year", fontsize=18)
    ax.set_ylabel("Count", fontsize=18)
    ax.set_title(
        "Count of Down-Regulation Events By Year",
        fontsize=24,
        weight="bold",
        pad=20,
    )
    ax.grid(True, which="major", linestyle="--", linewidth=0.5)

    plt.tight_layout()

    # Show every other year on x-axis
    n = 2
    ticks_to_show = list(range(0, len(threetwo.index), n))
    ax.set_xticks(ticks_to_show)
    ax.set_xticklabels(
        [threetwo.index[i] for i in ticks_to_show], ha="center", rotation=0, fontsize=14
    )
    ax.tick_params(axis="y", labelsize=14)

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close()


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting regulatory background figure (Figure D.1)...")

    # Load matched samples
    df_2_1 = pd.read_csv(
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"]
    )
    logging.info(f"Loaded II->I matched sample: {len(df_2_1)} rows.")

    df_3_2 = pd.read_csv(
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat"]
    )
    # Original filters 3->2 to FDA_own_accord == 1
    df_3_2 = df_3_2[df_3_2.FDA_own_accord == 1]
    logging.info(
        f"Loaded III->II matched sample (FDA_own_accord=1): {len(df_3_2)} rows."
    )

    figure_D1a(df_2_1, config.FIGURES_DIR / "Distribution_of_2_1_over_years.png")
    figure_D1b(df_3_2, config.FIGURES_DIR / "Distribution_of_3_2_over_years.png")

    logging.info("Regulatory background figure complete.")


if __name__ == "__main__":
    sys.exit(main())
