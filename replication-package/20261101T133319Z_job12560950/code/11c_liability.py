#!/usr/bin/env python
"""
11c_liability.py -- Liability analysis (Figures D.10a-b).

Combines two original analyses:
  1) Liability_graphs.py: plots tort litigation trends (medical device
     preemption cases, all device tort cases, pharmaceutical preemption
     cases) around Medtronic v. Lohr (1996).
  2) Response_doc_bankruptcy_data_analysis.py: plots the ratio of
     bankruptcy cases to tort claims for medical device firms.

Inputs:
    data/raw/Liability/Results list for_medical device tort preempt.xlsx
    data/raw/Liability/Results list for_medical device tort preempt 2006-2007.xlsx
    data/raw/Liability/Results list for_medical device tort 1985-1995.xlsx
    data/raw/Liability/Results list for_medical device tort 1996-2000.xlsx
    data/raw/Liability/Results list for_medical device tort 2001-2004.xlsx
    data/raw/Liability/Results list for_medical device tort 2005-2007.xlsx
    data/raw/Liability/Results list for_pharmaceutical tort preempt 1985-1998.xlsx
    data/raw/Liability/Results list for_pharmaceutical tort preempt 1999-2004.xlsx
    data/raw/Liability/Results list for_pharmaceutical tort preempt 2005-2007.xlsx
    data/raw/Liability/medtech/ (bankruptcy Excel files)

Outputs:
    output/figures/cases_preemption.png
    output/figures/Bankruptcy_1996_raw_trend.png
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
from plotting import setup_standard_axes

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "11c_liability.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


# ============================================================================
# Figure D.10a: Tort litigation trends
# ============================================================================

def figure_D10a(base_path, output_path):
    """
    Plot tort litigation counts: device preemption cases, all device cases,
    and pharmaceutical preemption cases. Vertical line at Medtronic v. Lohr (1996).
    """
    logging.info("Producing Figure D.10a: tort litigation trends.")
    rolling_param = 1

    # Device cases specifically related to preemption
    tort = pd.read_excel(base_path / "Results list for_medical device tort preempt.xlsx")
    tort2 = pd.read_excel(base_path / "Results list for_medical device tort preempt 2006-2007.xlsx")
    tort_comb = pd.concat([tort, tort2])
    tortgroup = tort_comb.groupby("YEAR").count()["CITE"].rolling(rolling_param).mean().reset_index()
    dict_input = {"YEAR": 1985, "CITE": 0}
    tortgroup = pd.concat([pd.DataFrame([dict_input]), tortgroup]).reset_index(drop=True)

    # All medical device tort cases
    tort_all = pd.concat([
        pd.read_excel(base_path / "Results list for_medical device tort 1985-1995.xlsx"),
        pd.read_excel(base_path / "Results list for_medical device tort 1996-2000.xlsx"),
        pd.read_excel(base_path / "Results list for_medical device tort 2001-2004.xlsx"),
        pd.read_excel(base_path / "Results list for_medical device tort 2005-2007.xlsx"),
    ])
    tortgroup2 = tort_all.groupby("YEAR").count()["CITE"].rolling(rolling_param).mean().reset_index()

    # Pharmaceutical preemption cases
    drug_comb = pd.concat([
        pd.read_excel(base_path / "Results list for_pharmaceutical tort preempt 1985-1998.xlsx"),
        pd.read_excel(base_path / "Results list for_pharmaceutical tort preempt 1999-2004.xlsx"),
        pd.read_excel(base_path / "Results list for_pharmaceutical tort preempt 2005-2007.xlsx"),
    ])
    druggroup = drug_comb.groupby("YEAR").count()["CITE"].rolling(rolling_param).mean().reset_index()

    # ---- Plot ----
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

    plt.plot(tortgroup2["YEAR"], tortgroup2["CITE"], c="lightblue", label="Medical Device Cases")
    ax.scatter(tortgroup2["YEAR"], tortgroup2["CITE"],
               facecolors="none", edgecolors="lightblue", s=40, linewidth=3)

    plt.plot(tortgroup["YEAR"], tortgroup["CITE"], c="#2a9d8f", label="Medical Device Cases Preempted")
    ax.scatter(tortgroup["YEAR"], tortgroup["CITE"],
               facecolors="none", edgecolors="#2a9d8f", s=40, linewidth=3)

    plt.plot(druggroup["YEAR"], druggroup["CITE"], c="#e76f51", label="Pharmaceutical Cases Preempted")
    ax.scatter(druggroup["YEAR"], druggroup["CITE"],
               facecolors="none", edgecolors="#e76f51", s=40, linewidth=3)

    ax.axvline(1996.5, linestyle="--", linewidth=2, color="black")
    ax.text(1995.6, 250, "Medtronic, inc. v. Lohr", rotation=90, va="center", fontsize=14)

    plt.xlabel("Year", fontsize=20)
    plt.ylabel("Number of Cases", fontsize=20)
    plt.rc("xtick", labelsize=14)
    plt.rc("ytick", labelsize=14)
    plt.xticks(np.arange(min(druggroup["YEAR"]), max(druggroup["YEAR"]) + 1, 2.0))
    plt.legend(fontsize="large")

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close(fig)


# ============================================================================
# Figure D.10b: Bankruptcy-to-tort ratio
# ============================================================================

def figure_D10b(base_path, output_path):
    """
    Plot the ratio of medical-device bankruptcy mentions (from Nexis Uni)
    to the total number of medical device tort claims over time.
    """
    logging.info("Producing Figure D.10b: bankruptcy-to-tort ratio.")

    medtech_dir = base_path / "medtech"

    # ---- Load medical device bankruptcy data ----
    range1 = np.arange(1989, 2003, 1)
    range2 = np.arange(1991, 2005, 1)

    gather = pd.DataFrame()
    for i in range(14):
        fname = (
            f"Results list for__medical device_ AND _Chapter 11_ AND bankruptcy "
            f"AND date _{range1[i]} AND date _ {range2[i]}.xlsx"
        )
        fpath = medtech_dir / fname
        if not fpath.exists():
            # All 14 windows ship (restricted route: the author's export; simulated route:
            # the materialized payload); a missing window would drop a year from Figure D.10b,
            # so the step fails instead.
            raise FileNotFoundError(
                f"Bankruptcy search export missing: {fpath}. Figure D.10b needs all 14 "
                "year windows; supply the liability exports or materialize the simulated "
                "payload before running this step.")
        excelsheet = pd.read_excel(fpath)
        excelsheet["year"] = range1[i] + 1
        excelsheet["count"] = 1
        gather = pd.concat([gather, excelsheet])

    gather = gather.sort_values(by="year").drop_duplicates("Company")

    # ---- Load tort data for normalization ----
    tort_comb = pd.concat([
        pd.read_excel(base_path / "Results list for_medical device tort 1985-1995.xlsx"),
        pd.read_excel(base_path / "Results list for_medical device tort 1996-2000.xlsx"),
        pd.read_excel(base_path / "Results list for_medical device tort 2001-2004.xlsx"),
        pd.read_excel(base_path / "Results list for_medical device tort 2005-2007.xlsx"),
    ])
    tort_comb["year"] = tort_comb["YEAR"]
    grouped_tort_o = tort_comb[tort_comb.year < 2004].groupby("year").count()["CITE"]

    # ---- Compute ratio ----
    agg = gather.groupby("year").sum(numeric_only=True)["count"].reset_index()
    # Normalize by number of tort cases (years > 1989)
    tort_denominator = grouped_tort_o[grouped_tort_o.index > 1989].reset_index()["CITE"]
    if len(agg) == len(tort_denominator):
        agg["count"] = agg["count"].values / tort_denominator.values
    else:
        logging.warning(
            f"Length mismatch: bankruptcy agg ({len(agg)}) vs tort ({len(tort_denominator)}). "
            "Aligning on available years."
        )
        # Align on overlapping years
        tort_series = grouped_tort_o[grouped_tort_o.index > 1989]
        agg = agg[agg.year.isin(tort_series.index)]
        agg["count"] = agg["count"].values / tort_series.loc[agg.year.values].values

    # ---- Plot ----
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
    plt.plot(agg["year"], agg["count"], c="#2a9d8f")
    ax.scatter(agg["year"], agg["count"],
               facecolors="none", edgecolors="#2a9d8f", s=40, linewidth=3)

    plt.title("Ratio of Bankruptcy Cases to Tort Claims for Medical Devices",
              fontsize=26, pad=40)
    plt.xlabel("Year", fontsize=20)
    plt.ylabel("Ratio", fontsize=20)
    plt.rc("xtick", labelsize=14)
    plt.rc("ytick", labelsize=14)
    plt.xticks(np.arange(min(agg["year"]), max(agg["year"]) + 1, 2.0))
    plt.axvline(x=1995.5, ls="--", lw=1, color="black")

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close(fig)


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting liability analysis (Figures D.10a-b)...")

    base_path = config.RAW_DATA_DIR / "Liability"

    figure_D10a(base_path, config.FIGURES_DIR / "cases_preemption.png")
    figure_D10b(base_path, config.FIGURES_DIR / "Bankruptcy_1996_raw_trend.png")

    logging.info("Liability analysis complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
