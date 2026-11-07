"""
Shared matplotlib boilerplate for event study and other figures.

Centralizes color palette, axis formatting, and save conventions.
Replaces 15+ scattered copies of the same setup code.

Inputs: matplotlib axes, estimate DataFrames
Outputs: Formatted figures saved to output/figures/
"""

import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.ticker as ticker
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

# ============================================================================
# Global style — match original's style.use('seaborn-poster')
# ============================================================================
try:
    style.use('seaborn-v0_8-poster')
except OSError:
    try:
        style.use('seaborn-poster')
    except OSError:
        pass  # fall back to matplotlib defaults if neither available

# ============================================================================
# Color palette
# ============================================================================
COLORS = config.COLORS


def get_colors(reclass_type):
    """Return (line_color, dot_color, error_color) for a reclassification type."""
    if reclass_type == "3_2":
        return COLORS["downreg_line"], COLORS["downreg_dot"], COLORS["error"]
    else:
        return COLORS["dereg_line"], COLORS["dereg_dot"], COLORS["error"]


# ============================================================================
# Axis setup
# ============================================================================

def setup_event_study_axes(ax, reclass_type=None, xlabel=None,
                           ylabel="Change in Outcome", title=None):
    """Standard event-study axis formatting.

    If xlabel is not provided, it defaults based on reclass_type:
      '3_2' -> "Years Since Down-Regulation"
      else  -> "Years Since Deregulation"
    """
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    if xlabel is None:
        if reclass_type == "3_2":
            xlabel = "Years Since Down-Regulation"
        else:
            xlabel = "Years Since Deregulation"
    ax.set_xlabel(xlabel, fontsize=24)
    ax.set_ylabel(ylabel, fontsize=24)
    if title:
        ax.set_title(title, fontsize=30, pad=30)
    plt.rc('xtick', labelsize=16)
    plt.rc('ytick', labelsize=16)


def setup_standard_axes(ax, xlabel=None, ylabel=None, title=None,
                        fontsize_label=18, fontsize_title=24):
    """Standard non-event-study axis formatting."""
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=fontsize_label)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=fontsize_label)
    if title:
        ax.set_title(title, fontsize=fontsize_title, pad=20)
    ax.grid(False)


# ============================================================================
# Event study plotting
# ============================================================================

def plot_event_study(ax, event_times, estimates, lower_cis, upper_cis,
                     reclass_type, outcome_label=None, add_trend_lines=True,
                     ref_period=-1):
    """
    Plot event-study coefficients with error bars and optional trend lines.
    Matches original styling: separate scatter + errorbar, dashed error bars,
    dashed trend lines for both pre and post.

    Parameters:
        ax: matplotlib Axes
        event_times: array of event-time integers
        estimates: array of point estimates
        lower_cis: array of CI lower bounds
        upper_cis: array of CI upper bounds
        reclass_type: '2_1' or '3_2'
        outcome_label: title string
        add_trend_lines: whether to fit pre/post linear trends
        ref_period: reference period (normalized to zero)
    """
    line_c, dot_c, error_c = get_colors(reclass_type)

    # Derive symmetric SE from CI bounds (matching original convention):
    #   positive estimate → SE = (estimate - lower_CI) / 1.96
    #   negative estimate → SE = |estimate - upper_CI| / 1.96
    #   zero estimate     → SE = (upper_CI - lower_CI) / (2 * 1.96)
    # Then plot symmetric bands: estimate ± 1.96 * SE
    estimates = np.asarray(estimates, dtype=float)
    lower_cis = np.asarray(lower_cis, dtype=float)
    upper_cis = np.asarray(upper_cis, dtype=float)

    se = np.where(
        estimates > 0,
        (estimates - lower_cis) / 1.96,
        np.where(
            estimates < 0,
            np.abs(estimates - upper_cis) / 1.96,
            (upper_cis - lower_cis) / (2 * 1.96),
        ),
    )
    se = np.maximum(se, 0)  # guard against negative SE
    yerr = 1.96 * se

    # Linear trend lines (pre: ET < 0, post: ET >= 0, matching original)
    if add_trend_lines:
        pre_mask = event_times < 0
        post_mask = event_times >= 0
        if np.sum(pre_mask) > 1:
            m, b = np.polyfit(event_times[pre_mask], estimates[pre_mask], 1)
            ax.plot(event_times[pre_mask], m * event_times[pre_mask] + b,
                    '--', color=line_c)
        if np.sum(post_mask) > 1:
            m2, b2 = np.polyfit(event_times[post_mask], estimates[post_mask], 1)
            ax.plot(event_times[post_mask], m2 * event_times[post_mask] + b2,
                    '--', color=line_c)

    # Error bars with dashed line style (matching original: symmetric bands)
    eb = ax.errorbar(
        event_times, estimates,
        yerr=yerr,
        ls='none',
        elinewidth=1, ecolor='grey',
    )
    eb[-1][0].set_linestyle('--')

    # Hollow scatter markers (matching original: s=80, linewidth=3)
    ax.scatter(
        event_times, estimates,
        facecolors='none', edgecolors=dot_c,
        s=80, linewidth=3,
    )

    # Reference lines (matching original: no alpha)
    ax.axhline(y=0, ls="--", lw=1, color="black")
    ax.axvline(x=-0.5, ls="--", lw=1, color="black")

    # X-tick spacing of 2
    ax.set_xticks(np.arange(min(event_times), max(event_times) + 1, 2.0))

    setup_event_study_axes(ax, reclass_type, title=outcome_label)


def plot_no_data_panel(ax, reclass_type, outcome_label, message=None):
    """Plot a placeholder panel for outcomes without data (e.g., dev_count for 2->1)."""
    if message is None:
        message = "The FDA does not gather comparable data for Class I devices."
    ax.axis([-10, 10, -2, 2])
    ax.text(-8, 0.04, message, fontsize=18, color=COLORS["dereg_dot"])
    ax.set_xticks([])
    ax.set_yticks([])
    setup_event_study_axes(ax, reclass_type, title=outcome_label)


# ============================================================================
# Save helper
# ============================================================================

def save_figure(fig, filename, output_dir=None, dpi=300):
    """Save figure with standardized settings."""
    if output_dir is None:
        output_dir = config.FIGURES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    fig.savefig(filepath, bbox_inches="tight", dpi=dpi)
    print(f"Saved: {filepath}")
    plt.close(fig)


def create_figure(nrows=1, ncols=1, figsize=(12, 8)):
    """Create a figure with standard sizing."""
    return plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
