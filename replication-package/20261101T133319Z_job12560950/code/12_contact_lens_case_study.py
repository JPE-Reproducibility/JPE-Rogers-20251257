#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
12_contact_lens_case_study.py -- Contact lens descriptive case study figure.

Plots raw time series of patent filings, device submissions, and new-firm
entry for daily-wear soft contact lenses (product code LPL, reclassified
from Class III to II in 1994) against extended-wear soft contact lenses
(product code LPM, remained Class III) as a visual control.

Inputs:
    data/derived/Full_sample.csv

Outputs:
    output/figures/ContactLens_CaseStudy.png
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from plotting import create_figure, save_figure, setup_standard_axes

import matplotlib.pyplot as plt
from matplotlib import style

try:
    style.use('seaborn-v0_8-poster')
except OSError:
    try:
        style.use('seaborn-poster')
    except OSError:
        pass

# ============================================================================
# Parameters
# ============================================================================
TREATED_PC = "LPL"       # Daily-wear soft contact lens (reclassified 1994)
CONTROL_PC = "LPM"       # Extended-wear soft contact lens (remained Class III)
RECLASS_YEAR = 1994
PRE_WINDOW = 10           # Years before reclassification to show

OUTCOMES = [
    ("patents_allpats", "Annual Patent Filings"),
    ("dev_count", "Device Submissions"),
    ("firm_count", "New Firms"),
]


def main():
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load panel data
    df = pd.read_csv(config.DERIVED_DATA_DIR / "Full_sample.csv", low_memory=False)

    treated = (
        df[df["PRODUCTCODE"] == TREATED_PC][["year"] + [o[0] for o in OUTCOMES]]
        .sort_values("year")
        .reset_index(drop=True)
    )
    control = (
        df[df["PRODUCTCODE"] == CONTROL_PC][["year"] + [o[0] for o in OUTCOMES]]
        .sort_values("year")
        .reset_index(drop=True)
    )

    # Restrict to 10 years before reclassification through 2017
    year_min = RECLASS_YEAR - PRE_WINDOW
    treated = treated[(treated["year"] >= year_min) & (treated["year"] <= 2017)]
    control = control[(control["year"] >= year_min) & (control["year"] <= 2017)]

    # ── Figure: 2 rows x 1 column (top: patents; bottom: device submissions) ──
    # Third outcome (new firms) included as secondary axis or separate;
    # for a clean 2x1, combine device submissions and new firms on bottom panel
    # Actually: 3 panels stacked vertically in a 2-row layout doesn't work.
    # Use a 3x1 vertical stack to match the "2x1" manuscript feel.
    # Or: top row = patents, bottom row = two panels side by side.
    # Manuscript 2x1 figures are typically 2 rows, 1 column.
    # Let's do 3 rows x 1 column for the three outcomes.

    line_c_treated = config.COLORS["dereg_line"]    # Teal (matches recall raw trends)
    line_c_control = "#e76f51"                        # Salmon (matches recall raw trends)

    # Black-and-white legibility: the two series are distinguished by LINE STYLE
    # (treated solid, control dashed) and MARKER SHAPE (treated filled circle,
    # control open square), so the figure reads correctly in grayscale as well as
    # color (addresses Reviewer 1 comment on B&W printing of Figure 1).

    panel_filenames = [
        "ContactLens_patents.png",
        "ContactLens_submissions.png",
        "ContactLens_firms.png",
    ]

    # Save individual panel figures for subfloat layout in manuscript
    for (col, title), fname in zip(OUTCOMES, panel_filenames):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(
            treated["year"], treated[col],
            color=line_c_treated, linewidth=2, linestyle="-",
        )
        ax.scatter(
            treated["year"], treated[col],
            marker="o", facecolors=line_c_treated, edgecolors=line_c_treated,
            s=45, linewidth=1.5, label="Daily-Wear Soft (Reclassified)",
        )
        ax.plot(
            control["year"], control[col],
            color=line_c_control, linewidth=2, linestyle="--",
        )
        ax.scatter(
            control["year"], control[col],
            marker="s", facecolors="none", edgecolors=line_c_control,
            s=45, linewidth=2.5, label="Extended-Wear Soft (Remained Class III)",
        )
        is_first_panel = (fname == panel_filenames[0])

        ax.axvline(x=RECLASS_YEAR, color="black", linestyle="--", linewidth=1, zorder=1)

        setup_standard_axes(ax, ylabel=title, fontsize_label=20, fontsize_title=24)
        ax.tick_params(axis="both", labelsize=14)
        ax.grid(False)
        ax.set_xlabel("Year", fontsize=20)

        # Legend and reclassification annotation only on panel (a)
        if is_first_panel:
            leg = ax.legend(fontsize=14, loc="upper left", frameon=True,
                           facecolor="white", edgecolor="none", framealpha=1)
            leg.set_zorder(5)
            ax.annotate(
                "Reclassification\n(1994)",
                xy=(RECLASS_YEAR, ax.get_ylim()[1] * 0.55),
                xytext=(RECLASS_YEAR + 5, ax.get_ylim()[1] * 0.65),
                fontsize=12, color="black", va="bottom", ha="left",
                arrowprops=dict(arrowstyle="->", color="black", lw=1),
            )

        plt.tight_layout()
        save_figure(fig, fname)

    # Also save combined 3-panel version for backward compatibility
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 14), sharex=True)

    for ax, (col, title) in zip(axes, OUTCOMES):
        ax.plot(
            treated["year"], treated[col],
            color=line_c_treated, linewidth=2,
        )
        ax.scatter(
            treated["year"], treated[col],
            facecolors="none", edgecolors=line_c_treated,
            s=40, linewidth=3, label="Daily-Wear Soft (Reclassified)",
        )
        ax.plot(
            control["year"], control[col],
            color=line_c_control, linewidth=2,
        )
        ax.scatter(
            control["year"], control[col],
            facecolors="none", edgecolors=line_c_control,
            s=40, linewidth=3, label="Extended-Wear Soft (Remained Class III)",
        )
        ax.axvline(x=RECLASS_YEAR, color="black", linestyle="--", linewidth=1)

        setup_standard_axes(ax, ylabel=title, fontsize_label=20, fontsize_title=24)
        ax.tick_params(axis="both", labelsize=14)
        ax.grid(False)

    axes[-1].set_xlabel("Year", fontsize=20)
    axes[0].legend(fontsize=14, loc="upper left", frameon=False)
    axes[0].annotate(
        "Reclassification\n(1994)",
        xy=(RECLASS_YEAR, axes[0].get_ylim()[1] * 0.55),
        xytext=(RECLASS_YEAR + 5, axes[0].get_ylim()[1] * 0.65),
        fontsize=12, color="black", va="bottom", ha="left",
        arrowprops=dict(arrowstyle="->", color="black", lw=1),
    )

    plt.tight_layout()
    save_figure(fig, "ContactLens_CaseStudy.png")

    # ── Additive emitter: write the intro case-study pre/post ratios ──
    # (reads the already-built `treated` series; no side effects on figures)
    write_case_study_ratios(treated)


def write_case_study_ratios(treated):
    """Emit the intro case-study pre/post ratios (JPE_submission_v8.tex:203).

    Purely additive: consumes the SAME `treated` LPL series that the plotting
    code above already built (product code LPL, restricted to the plot window
    RECLASS_YEAR - PRE_WINDOW = 1984 through 2017) and writes a NEW CSV with the
    pre-1994 vs post-1994 means and their ratio for each plotted outcome. It does
    not read new data, does not alter `treated`, and does not touch any existing
    output. The pre window is the plotted years before reclassification
    (year < RECLASS_YEAR); the post window is the reclassification year onward
    (year >= RECLASS_YEAR), matching the figure's vertical reclassification line.
    """
    pre = treated[treated["year"] < RECLASS_YEAR]
    post = treated[treated["year"] >= RECLASS_YEAR]

    rows = []
    for col, _label in OUTCOMES:
        pre_mean = pre[col].mean()
        post_mean = post[col].mean()
        ratio = post_mean / pre_mean if pre_mean else float("nan")
        rows.append(
            {
                "measure": col,
                "pre_mean": pre_mean,
                "post_mean": post_mean,
                "ratio": ratio,
            }
        )

    out = pd.DataFrame(rows, columns=["measure", "pre_mean", "post_mean", "ratio"])
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(config.TABLES_DIR / "contact_lens_case_study_ratios.csv", index=False)


if __name__ == "__main__":
    sys.exit(main())
