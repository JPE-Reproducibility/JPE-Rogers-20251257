"""
Table formatting utilities for LaTeX output.

Handles SE computation from asymmetric CIs, significance stars,
row/panel assembly for booktabs-style tables.

Provides two output modes:
  1. assemble_table()       — full \begin{table}...\\end{table} LaTeX
  2. assemble_row_fragment() — bare rows only, for \\input{} inside a
                               table environment defined in the paper .tex

Inputs: Estimate DataFrames
Outputs: LaTeX table strings (full or fragment)
"""

import numpy as np
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config


def compute_se(estimate, lower_ci, upper_ci):
    """
    Compute standard error from estimate and confidence interval bounds.

    Handles asymmetric CIs by using the appropriate bound:
    - If estimate > 0, SE = (estimate - lower_CI) / 1.96
    - If estimate < 0, SE = |estimate - upper_CI| / 1.96
    - If estimate == 0, SE = (upper_CI - lower_CI) / (2 * 1.96)
    """
    if estimate > 0:
        se = (estimate - lower_ci) / 1.96
        if se < 0:
            se = estimate * 1.96 * 2
    elif estimate < 0:
        se = np.abs(estimate - upper_ci) / 1.96
    else:
        se = (upper_ci - lower_ci) / (2 * 1.96)
    return max(se, 0)


def compute_se_series(df):
    """
    Vectorized SE computation for a DataFrame with Estimate, lower_CI, upper_CI columns.

    Returns a Series of SEs.
    """
    se = pd.Series(0.0, index=df.index)
    pos = df["Estimate"] > 0
    neg = df["Estimate"] < 0
    zero = df["Estimate"] == 0

    se.loc[pos] = (df.loc[pos, "Estimate"] - df.loc[pos, "lower_CI"]) / 1.96
    # Fix negative SEs
    bad = se < 0
    se.loc[pos & bad] = df.loc[pos & bad, "Estimate"] * 1.96 * 2

    se.loc[neg] = np.abs(df.loc[neg, "Estimate"] - df.loc[neg, "upper_CI"]) / 1.96
    se.loc[zero] = (df.loc[zero, "upper_CI"] - df.loc[zero, "lower_CI"]) / (2 * 1.96)

    return se.clip(lower=0)


def significance_stars(estimate, se):
    """
    Return significance stars based on z-statistic.

    Convention: + (10%), * (5%), ** (1%), *** (0.1%).
    """
    if se <= 0:
        return ""
    z = np.abs(estimate / se)
    if z >= 3.2905:
        return "***"
    elif z >= 2.576:
        return "**"
    elif z >= 1.96:
        return "*"
    elif z >= 1.645:
        return "+"
    return ""


def format_estimate_cell(estimate, se, decimal_places=2):
    """Format a single estimate+SE cell for LaTeX."""
    if np.isnan(estimate) or np.isnan(se):
        return "", ""
    stars = significance_stars(estimate, se)
    est_str = f"{estimate:.{decimal_places}f}{stars}"
    se_str = f"({se:.{decimal_places}f})"
    return est_str, se_str


def format_table_row(outcome_label, estimates_by_sample, ses_by_sample,
                     pre_mean=None, pre_std=None, sample_sizes=None,
                     decimal_places=2):
    """
    Format one outcome row across multiple samples for LaTeX.

    Returns two strings: the estimate row and the SE row.
    """
    cells_est = [outcome_label]
    cells_se = [""]

    if pre_mean is not None:
        cells_est.append(f"{pre_mean:.{decimal_places}f}")
        cells_se.append(f"({pre_std:.{decimal_places}f})" if pre_std is not None else "")

    for est, se in zip(estimates_by_sample, ses_by_sample):
        est_str, se_str = format_estimate_cell(est, se, decimal_places)
        cells_est.append(est_str)
        cells_se.append(se_str)

    if sample_sizes is not None:
        cells_est.append(str(sample_sizes[0]) if sample_sizes else "")
        cells_se.append("")

    est_row = " & ".join(cells_est) + " \\\\ "
    se_row = " & ".join(cells_se) + " \\\\ "
    return est_row, se_row


def assemble_row_fragment(rows, sample_sizes=None, has_price_column=False):
    """
    Assemble a row-fragment .tex file: just the body rows for \\input{}.

    No \\begin{table}, no \\toprule/\\bottomrule. Only outcome rows,
    a blank separator row, and the sample-size row.

    Parameters:
        rows: list of (est_row, se_row) tuples
        sample_sizes: dict mapping sample label -> size, or list of sizes
                      in column order. If None, omit sample size row.
        has_price_column: if True, insert "- &" placeholder for price column
                          in the estimate rows and sample size row.
    """
    lines = []
    for est_row, se_row in rows:
        lines.append(est_row)
        lines.append(se_row)

    # Sample size row — match original format string patterns
    sizes = None
    if sample_sizes is not None:
        if isinstance(sample_sizes, dict):
            sizes = list(sample_sizes.values())
        else:
            sizes = list(sample_sizes)

    # Blank separator row. Most regression fragments have five columns and use
    # four ampersands. Matched-only spillover fragments are inserted into a
    # three-column table, so they need two ampersands to avoid an extra alignment
    # tab if the formatter is rerun.
    if rows:
        if sizes is not None and len(sizes) == 1 and not has_price_column:
            blank = "&& \\\\ "
        else:
            blank = "&&&& \\\\ "
        lines.append(blank)

    if sizes is not None:

        sizes_int = [str(int(s)) for s in sizes]

        if len(sizes) == 3:
            # "Both" mode: {N1}&{N2} compressed (no spaces around middle &)
            if has_price_column:
                size_line = f"\\hspace{{6mm}}Sample Size & & -& {sizes_int[0]}&{sizes_int[1]} & {sizes_int[2]} \\\\ "
            else:
                size_line = f"\\hspace{{6mm}}Sample Size & & {sizes_int[0]}&{sizes_int[1]} & {sizes_int[2]} \\\\ "
        elif len(sizes) == 1:
            # "MatchedOnly" mode (spillovers)
            size_line = f"\\hspace{{6mm}}Sample Size & & {sizes_int[0]} \\\\ "
        else:
            # Fallback
            size_cells = ["\\hspace{6mm}Sample Size", ""]
            if has_price_column:
                size_cells.append("-")
            size_cells.extend(sizes_int)
            size_line = " & ".join(size_cells) + " \\\\ "

        lines.append(size_line)

    return "\n".join(lines) + "\n"


def assemble_table(rows, panel_header=None, caption=None, label=None,
                   column_headers=None, notes=None):
    """
    Assemble a complete booktabs-style LaTeX table.

    Parameters:
        rows: list of (est_row, se_row) tuples from format_table_row
        panel_header: optional panel header string
        caption: table caption
        label: LaTeX label
        column_headers: list of column header strings
        notes: table notes string
    """
    lines = []
    ncols = rows[0][0].count("&") + 1 if rows else 5

    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    if caption:
        lines.append(f"\\caption{{{caption}}}")
    if label:
        lines.append(f"\\label{{{label}}}")

    col_spec = "l" + "c" * (ncols - 1)
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\toprule")

    if column_headers:
        lines.append(" & ".join(column_headers) + " \\\\")
        lines.append("\\midrule")

    if panel_header:
        lines.append(f"\\multicolumn{{{ncols}}}{{l}}{{\\textit{{{panel_header}}}}} \\\\")
        lines.append("\\addlinespace")

    for est_row, se_row in rows:
        lines.append(est_row)
        lines.append(se_row)
        lines.append("\\addlinespace")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")

    if notes:
        lines.append(f"\\begin{{tablenotes}}\\small")
        lines.append(f"\\item {notes}")
        lines.append(f"\\end{{tablenotes}}")

    lines.append("\\end{table}")
    return "\n".join(lines)
