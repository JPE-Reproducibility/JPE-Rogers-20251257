#!/usr/bin/env python
"""
11d_reg_design.py -- Regulation design analysis (Figures D.11-D.12, Tables D.11-D.12).

Examines the institutional details of FDA reclassification design:
  - Relates pre-reclassification device characteristics (market age, adverse
    event severity, FDA-initiation status) to post-reclassification outcomes
  - Compares petitioned vs. FDA-initiated reclassifications (III->II)
  - Produces covariate-adjusted scatter plots of treatment effect vs. market age

Methodology:
  1. For III->II (and II->I), construct a matched sample by pairing each
     treated product code to a within-subpart control on pre-period adverse
     event severity rates.
  2. Run per-product-code Conley-Taber to obtain individual treatment effects
     on serious-event rates and patenting.
  3. Regress those per-PC treatment effects on market age at reclassification,
     pre-period adverse event severity, FDA-initiation status (III->II only),
     and product-area fixed effects.
  4. Produce covariate-adjusted scatter plots (holding non-age covariates at
     sample means) to show how market age relates to treatment effects.

Inputs:
    data/derived/Full_sample.csv
    data/derived/matched_sample_3_2_onepat.csv
    data/derived/matched_sample_3_2_onepat_innovation_petitioned.csv
    data/raw/RegNum_Factorized_Synth.csv

Outputs:
    output/figures/exp_vs_impact_v_serious_est_3_2.png
    output/figures/exp_vs_impact_patent_est_3_2.png
    output/figures/exp_vs_impact_v_serious_est_2_1.png
    output/figures/exp_vs_impact_patent_est_2_1.png
    output/figures/Distribution_of_3_over_years.png
    output/figures/Distribution_of_2_over_years.png
    output/tables/Table_D11_reg_design.tex
    output/tables/Table_D12_petitioned_vs_fda.tex
    output/tables/model_{v_serious,patent}_est_{2_1,3_2}.csv
        (the fitted coefficient tables Table D.11a/D.11b are typeset from, in plain CSV)
"""

import sys
import re
import logging
import time
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_simple
from plotting import create_figure, save_figure, setup_standard_axes
from table_format import assemble_table, format_table_row, compute_se, significance_stars

np.random.seed(config.RANDOM_SEED)

# Conley-Taber inference in this module draws from the GLOBAL NumPy stream seeded on the
# line above: the five Conley-Taber calls in 11a/11d pass no `seed=` of their own, unlike
# the sixteen calls in the other analysis steps. Measured on the real data (the probes are in
# the author-side change record, not in the package):
#   * the POINT ESTIMATE is draw-invariant -- it is OLS on the residualized data, and it
#     was identical to 10 decimal places across six different streams and six stream
#     offsets. So every estimate this module reports, including the Section 6 footnote
#     maturity-gradient slopes and their OLS standard errors (which are computed from the
#     per-product-code point estimates, not from the permutation CIs), does not depend on
#     the draw at all;
#   * the PERMUTATION CI does depend on the draw: about 1.3e-2 of spread on a bound of
#     0.72 at the shipped CT_NUMBSIM=5000.
# The consequence is that these CIs are reproducible only while the sequence of draws is
# reproducible, which means while the NUMBER and ORDER of Conley-Taber calls in this
# process is unchanged. A caught-and-skipped failure inside the loops below is therefore
# not a local event: it shifts the stream for every later call. That is why those handlers
# log at ERROR with this consequence spelled out rather than at WARNING.
# Adding `seed=config.RANDOM_SEED` at the call sites would make each call's draw
# independent of the ones before it, which is the better design -- but it would also
# change the permutation CIs this package has already deposited, so it is not a
# like-for-like fix and is not applied here.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "11d_reg_design.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


# ============================================================================
# Part description consolidation
# ============================================================================
# The original code collapses rare part descriptions into broader categories
# to avoid singularity in OLS with part-area dummies.

PART_DESC_MAP_3_2 = {
    "CLINICAL CHEMISTRY AND CLINICAL TOXICOLOGY DEVICES": "OTHER DEVICES",
    "OPHTHALMIC DEVICES": "OTHER DEVICES",
    "PHYSICAL MEDICINE DEVICES": "OTHER DEVICES",
    "OBSTETRICAL AND GYNECOLOGICAL DEVICES": "OTHER DEVICES",
    "IMMUNOLOGY AND MICROBIOLOGY DEVICES": "OTHER DEVICES",
    "DENTAL DEVICES": "OTHER DEVICES",
    "RADIOLOGY DEVICES": "OTHER DEVICES",
    "CLINICAL CHEMISTRY AND CLINICAL TOXICOLOGY DEVICES\n": "OTHER DEVICES",
    "NEUROLOGICAL DEVICES": "OTHER DEVICES",
    "HEMATOLOGY AND PATHOLOGY DEVICES\n": "OTHER DEVICES",
    "ANESTHESIOLOGY DEVICES": "OTHER DEVICES",
    "GASTROENTEROLOGY-UROLOGY DEVICES": "PLASTIC SURGERY, GASTROENTEROLOGY-UROLOGY DEVICES",
    "GENERAL AND PLASTIC SURGERY DEVICES": "PLASTIC SURGERY, GASTROENTEROLOGY-UROLOGY DEVICES",
}

# II->I has many more PCs per part so fewer collapses needed
PART_DESC_MAP_2_1 = {
    # Original has all part description consolidation commented out for II->I
    # ("Don't need to reduce dimensionality because of many obs per part")
}


# ============================================================================
# Helper: nearest-neighbor matching on a scalar (squared distance)
# ============================================================================

def _get_similar(pos_pscore, neg_pscore):
    """Return (squared_distances_array, argmin_index) for scalar matching."""
    diff = pos_pscore - neg_pscore
    diff = diff * diff
    return diff, np.argmin(diff)


# ============================================================================
# Helper: annotation placement without overlap
# ============================================================================

def _place_annotation(ax, text, x, y, box=0.28):
    """Place boxed annotation in whichever corner has fewest data points."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    xf = (np.asarray(x) - x0) / (x1 - x0 + 1e-12)
    yf = (np.asarray(y) - y0) / (y1 - y0 + 1e-12)

    corners = [
        (0.98, 0.98, "right", "top"),
        (0.02, 0.98, "left", "top"),
        (0.02, 0.02, "left", "bottom"),
        (0.98, 0.02, "right", "bottom"),
    ]
    best = None
    best_score = 1e18
    for cx, cy, ha, va in corners:
        xmin = cx - (box if ha == "right" else 0.0)
        xmax = cx + (0.0 if ha == "right" else box)
        ymin = cy - (box if va == "top" else 0.0)
        ymax = cy + (0.0 if va == "top" else box)
        n = ((xf >= xmin) & (xf <= xmax) & (yf >= ymin) & (yf <= ymax)).sum()
        if n < best_score:
            best_score = n
            best = (cx, cy, ha, va)

    cx, cy, ha, va = best
    ax.text(
        cx, cy, text,
        transform=ax.transAxes, ha=ha, va=va, fontsize=14,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  alpha=0.9, edgecolor="none"),
    )


# ============================================================================
# Helper: construct and run per-PC Conley-Taber estimates
# ============================================================================

def _run_per_pc_ct(synth_df, outcomes, treated_pcs, year_min=1991,
                   use_window=True):
    """
    For each treated PC and each outcome, run Conley-Taber on the pair
    (treated PC + its matched control).  Return lists of estimates, SEs,
    and the DPM/experience score vector.

    Parameters:
        synth_df: DataFrame with treatment, posttreat, factorized, FE, year
        outcomes: list of outcome variable names
        treated_pcs: set of treated product codes
        year_min: earliest year to include in estimation
        use_window: if True, restrict to [yr_reclass-5, yr_reclass+15].
                    Original uses window for III->II but not for II->I.

    Returns:
        T_est, T_std: flat lists (len = len(outcomes) * len(treated_pcs))
        DPM_score: list of auxiliary scores per treated PC (len = len(treated_pcs))
    """
    T_est = []
    T_std = []
    DPM_score = []

    for j in outcomes:
        for i in treated_pcs:
            # Select the matched pair using FE
            keep_treats = synth_df[synth_df.PRODUCTCODE == i]["PRODUCTCODE"]
            fes = synth_df[synth_df.PRODUCTCODE.isin(keep_treats)]["FE"]
            test_main = synth_df[synth_df.FE.isin(fes)]
            yr_reclass = test_main[test_main.treatment == 1]["year_reclassified"].values[0]
            test_main = test_main[test_main.year > year_min]
            # Window: 5 years before to 15 years after (III->II only)
            if use_window:
                test_main = test_main[
                    (test_main.year > yr_reclass - 6) & (test_main.year < yr_reclass + 16)
                ]

            test_main_use = test_main.copy()
            # Log-transform event_count only (not patents -- original uses levels)
            if j == "event_count":
                test_main_use[j] = np.log(test_main_use[j] + 1)

            test_main_use = test_main_use.reset_index(drop=True)
            try:
                estimate, alpha025, alpha975 = conley_taber_simple(
                    test_main_use, j, "posttreat", "treatment", "factorized", "year"
                )
            except Exception as e:
                # Not local: the per-product-code point estimate becomes NaN (dropped from
                # the cross-sectional OLS below) and the permutation draws for every later
                # product code shift, because the CT call takes the global stream.
                logging.error(
                    "CT FAILED for %s / %s: %s -- this product code drops out of the "
                    "gradient regression and the draws of every later one shift.",
                    j, i, e, exc_info=True)
                estimate, alpha025, alpha975 = np.nan, np.nan, np.nan

            # SE from CI
            if np.isnan(estimate):
                SE = np.nan
            elif estimate < 0:
                SE = np.abs(estimate - alpha975)
            else:
                SE = estimate - alpha025

            T_est.append(estimate)
            T_std.append(SE)

            # Record experience years for first outcome only
            if j == outcomes[0]:
                score_vals = synth_df[synth_df.PRODUCTCODE == i]["years_exp"]
                DPM_score.append(score_vals.values[0] if len(score_vals) > 0 else np.nan)

    return T_est, T_std, DPM_score


# ============================================================================
# PART 1: III -> II burden analysis
# ============================================================================

def build_3_2_burden_sample():
    """
    Build the III->II matched burden-analysis sample.

    Matches each downregulated product code to a same-subpart Class III control
    on pre-period serious-event rate.  Returns:
        synth_df:  panel DataFrame with treatment, posttreat, factorized, FE
        matched_pairs: DataFrame mapping treated -> control PCs
    """
    logging.info("Building III->II burden-analysis matched sample...")

    # Load the full sample and reclassification event data
    full = pd.read_csv(config.DERIVED_DATA_DIR / config.FULL_SAMPLE)
    full.loc[:, ["event_count", "L", "H", "S", "R", "D"]] = (
        full[["event_count", "L", "H", "S", "R", "D"]].fillna(0)
    )

    # Load regulation-number crosswalk for PART/SUBPART descriptions
    synth_number = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["synth_number"],
        dtype={"REGULATIONNUMBER": str},
    )
    synth_number.REGULATIONNUMBER = synth_number.REGULATIONNUMBER.str.pad(
        width=8, side="right", fillchar="0"
    )
    synth_number = synth_number.drop_duplicates("PRODUCTCODE_x")
    synth_number["PRODUCTCODE"] = synth_number["PRODUCTCODE_x"]

    # Merge part description onto full sample (drop existing PART_DESCRIPTION if present)
    if "PART_DESCRIPTION" in full.columns:
        full = full.drop(columns=["PART_DESCRIPTION"])
    full = pd.merge(
        full,
        synth_number[["PRODUCTCODE", "PART_DESCRIPTION"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )

    # Build 3->2 event data
    # Load reclassification + invention year data from the canonical source file.
    # Full_sample's year_reclassified_3_2 is missing 2 PCs (LTT, HRC) that the
    # original analysis includes, so year_reclassified comes from the invention
    # year file instead (matches the original's merge from 3_2_begin_final_revisions.csv).
    inv_path = config.RAW_DATA_DIR / config.INVENTION_YEAR_FILES["3_2"]
    inv_years = pd.read_csv(inv_path)
    inv_years = inv_years.rename(columns={"years": "yr_invent"})

    # Drop existing FDA_own_accord to avoid collision (matches original line 218)
    if "FDA_own_accord" in full.columns:
        full = full.drop(columns=["FDA_own_accord"])

    # Merge year_reclassified, yr_invent, FDA_own_accord from invention year file
    full = pd.merge(
        full,
        inv_years[["PRODUCTCODE", "yr_invent", "year_reclassified", "FDA_own_accord"]]
            .drop_duplicates("PRODUCTCODE"),
        on="PRODUCTCODE", how="left",
    )
    full["years_exp"] = full["year_reclassified"] - full["yr_invent"]

    # Treatment = 1 for PCs with valid invention year data (25 PCs)
    full["treatment"] = 0
    full.loc[full.years_exp.notnull(), "treatment"] = 1
    n_treated = full[full.treatment == 1]["PRODUCTCODE"].nunique()
    logging.info(f"Loaded invention years for III->II from {inv_path} "
                 f"({len(inv_years)} PCs, {n_treated} treated after filtering)")

    # Construct derived adverse event variables
    full["serious_event"] = full["L"] + full["S"]
    full["less_serious_event"] = full["R"] + full["H"]
    full["DPM"] = (0.38 * full["D"] + 0.3 * full["serious_event"]
                   + 0.12 * full["less_serious_event"])
    full["v_serious_event"] = full["L"] + full["S"] + full["H"] + full["D"]

    # Severity rates
    full["v_serious_rate"] = 0.0
    mask = full.event_count > 0
    full.loc[mask, "v_serious_rate"] = (
        full.loc[mask, "v_serious_event"] / full.loc[mask, "event_count"]
    )
    full["H_rate"] = 0.0
    full.loc[mask, "H_rate"] = full.loc[mask, "H"] / full.loc[mask, "event_count"]
    full["D_rate"] = 0.0
    full.loc[mask, "D_rate"] = full.loc[mask, "D"] / full.loc[mask, "event_count"]
    full["L_rate"] = 0.0
    full.loc[mask, "L_rate"] = full.loc[mask, "L"] / full.loc[mask, "event_count"]

    # Merge SUBPART for matching (drop existing to avoid _x/_y suffixes)
    if "SUBPART_DESCRIPTION" in full.columns:
        full = full.drop(columns=["SUBPART_DESCRIPTION"])
    full = pd.merge(
        full,
        synth_number[["PRODUCTCODE", "SUBPART_DESCRIPTION"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )

    # ---- Matching within subpart on v_serious_rate ----
    treated_list = []
    matched_list = []
    similarity = []
    year_reclass_list = []
    baseline_devs = []
    baseline_devsctrl = []

    treated_pcs = np.unique(full[full.treatment == 1]["PRODUCTCODE"])
    for code in treated_pcs:
        treated = full[full.PRODUCTCODE == code]
        part_desc = treated["PART_DESCRIPTION"].values[0]
        subpart_desc = treated["SUBPART_DESCRIPTION"].values[0]
        yr_reclass = treated.year_reclassified.values[0]

        # Pre-period means
        treated_pre = treated[
            (treated.year < yr_reclass) & (treated.year > yr_reclass - 6)
        ].mean(numeric_only=True)

        # Control pool: untreated, same subpart+part, not already matched
        control = full[full.treatment == 0].copy()
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control[
            (control.SUBPART_DESCRIPTION == subpart_desc)
            & (control.PART_DESCRIPTION == part_desc)
            & (control.SUBMISSION_TYPE_ID != "510(K) Exempt")
        ]
        if len(control) == 0:
            logging.warning(f"No controls for {code} in subpart {subpart_desc}; skipping.")
            continue

        control_pre = control[
            (control.year < yr_reclass) & (control.year > yr_reclass - 6)
        ].groupby("PRODUCTCODE").mean(numeric_only=True).reset_index()

        if len(control_pre) == 0:
            logging.warning(f"No pre-period control data for {code}; skipping.")
            continue

        # Match on v_serious_rate
        sim_distances, sim_idx = _get_similar(
            treated_pre["v_serious_rate"], control_pre["v_serious_rate"].values
        )

        treated_list.append(code)
        matched_list.append(control_pre.iloc[sim_idx]["PRODUCTCODE"])
        similarity.append(sim_distances[sim_idx])
        year_reclass_list.append(yr_reclass)
        baseline_devs.append(treated_pre["DPM"])
        baseline_devsctrl.append(control_pre.iloc[sim_idx]["DPM"])

    # Assemble matched pairs
    matched_pairs = pd.DataFrame({
        "PRODUCTCODE": treated_list,
        "treated": treated_list,
        "match": matched_list,
        "SSE": similarity,
        "FE": range(len(treated_list)),
        "year_reclassified_controls": year_reclass_list,
        "baseline_treat": baseline_devs,
        "baseline_ctrl": baseline_devsctrl,
    })
    logging.info(f"III->II burden sample: {len(matched_pairs)} matched pairs.")

    # Build panel
    synth = pd.concat([
        full[full.PRODUCTCODE.isin(matched_pairs["match"])],
        full[full.PRODUCTCODE.isin(matched_pairs.treated)],
    ])
    synth["posttreat"] = 0
    synth.loc[synth.year >= synth.year_reclassified, "posttreat"] = 1
    synth["factorized"] = synth.PRODUCTCODE.astype("category").cat.codes

    # Assign FE and year_reclassified for controls
    synth = pd.merge(
        synth,
        matched_pairs[["PRODUCTCODE", "match", "SSE", "FE", "year_reclassified_controls"]],
        on="PRODUCTCODE", how="left",
    )
    for matched in matched_list:
        row = matched_pairs[matched_pairs["match"] == matched]
        if len(row) == 0:
            continue
        synth.loc[synth.PRODUCTCODE == matched, "FE"] = row["FE"].values[0]
        ctrl_yr = synth[synth["match"] == matched]["year_reclassified_controls"]
        if len(ctrl_yr) > 0:
            synth.loc[synth.PRODUCTCODE == matched, "year_reclassified"] = ctrl_yr.values[0]

    return synth, matched_pairs


def emit_dpm_decile_ratio(dpm_scores):
    """
    Emit the proxy-DPM decile statistics stated in the regulation-design appendix
    to output/tables/dpm_decile_ratio.csv.

    `dpm_scores` is one row per device type, carrying the pre-period mean proxy
    DPM (0.38 x deaths + 0.30 x serious injuries + 0.12 x less-serious injuries)
    over the 1996/1998 Class II universe -- the same score the burden analysis
    matches on.

    The reported ratio (`dpm_top_decile_ratio`) compares the TYPICAL top-decile
    device type -- the median score among device types at or above the 90th
    percentile -- with the device type at the 89th percentile, which is what the
    sentence compares. The mean-based ratio, the 90th-over-89th ratio and the
    top-decile-over-rest ratio are emitted alongside it, because the proxy's right
    tail is extreme (its mean is two orders of magnitude above the rest of the
    distribution) and the choice of statistic changes the answer by a factor of
    fifty. The percentile values themselves are emitted too, so any alternative
    reading of "four times" can be checked without rerunning the estimation.
    """
    s = pd.to_numeric(dpm_scores["mean_DPM"], errors="coerce").dropna()
    n = int(len(s))
    p89 = float(s.quantile(0.89))
    p90 = float(s.quantile(0.90))
    top_decile_mean = float(s[s >= p90].mean()) if n else float("nan")
    top_decile_median = float(s[s >= p90].median()) if n else float("nan")
    ratio = (top_decile_median / p89) if p89 else float("nan")
    rows = [
        {"metric": "dpm_device_types", "description": "Device types with a pre-period proxy-DPM score",
         "computed": n, "manuscript_value": ""},
        {"metric": "dpm_p89", "description": "Proxy DPM at the 89th percentile",
         "computed": round(p89, 6), "manuscript_value": ""},
        {"metric": "dpm_p90", "description": "Proxy DPM at the 90th percentile",
         "computed": round(p90, 6), "manuscript_value": ""},
        {"metric": "dpm_top_decile_mean",
         "description": "Mean proxy DPM among device types at or above the 90th percentile",
         "computed": round(top_decile_mean, 6), "manuscript_value": ""},
        {"metric": "dpm_top_decile_median",
         "description": "Median proxy DPM among device types at or above the 90th percentile",
         "computed": round(top_decile_median, 6), "manuscript_value": ""},
        {"metric": "dpm_top_decile_ratio",
         "description": "Median top-decile proxy DPM divided by the 89th-percentile proxy DPM "
                        "(the typical top-decile device type vs the 89th-percentile type)",
         "computed": round(ratio, 4), "manuscript_value": 4.0},
        # Alternative readings of "four times", recorded so the comparison the
        # sentence makes can be checked without re-running the estimation. None of
        # them is registered as the manuscript scalar; the row above is.
        {"metric": "dpm_top_decile_mean_over_p89",
         "description": "MEAN proxy DPM among top-decile device types divided by the "
                        "89th-percentile proxy DPM (tail-sensitive alternative)",
         "computed": round(top_decile_mean / p89, 4) if p89 else float("nan"),
         "manuscript_value": ""},
        {"metric": "dpm_p90_over_p89",
         "description": "90th-percentile proxy DPM divided by the 89th-percentile proxy DPM",
         "computed": round(p90 / p89, 4) if p89 else float("nan"),
         "manuscript_value": ""},
        {"metric": "dpm_top_decile_mean_over_rest_mean",
         "description": "Mean proxy DPM among top-decile device types divided by the mean "
                        "among the remaining device types",
         "computed": round(top_decile_mean / float(s[s < p90].mean()), 4)
                     if n and float(s[s < p90].mean()) else float("nan"),
         "manuscript_value": ""},
    ]
    out_path = config.TABLES_DIR / "dpm_decile_ratio.csv"
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["metric", "description", "computed",
                                "manuscript_value"]).to_csv(out_path, index=False)
    for r in rows:
        logging.info(f"  [DPM decile] {r['metric']}: {r['computed']}")
    logging.info(f"Saved proxy-DPM decile statistics: {out_path}")


def build_2_1_burden_sample():
    """
    Build the II->I matched burden-analysis sample.

    Uses the 63 FR 59 and 61 FR 111/112 reclassifications as treated units,
    matches on pre-period mean DPM score, then estimates per-PC Conley-Taber.
    """
    logging.info("Building II->I burden-analysis matched sample...")

    full = pd.read_csv(config.DERIVED_DATA_DIR / config.FULL_SAMPLE)
    full.loc[:, ["event_count", "L", "H", "S", "R", "D"]] = (
        full[["event_count", "L", "H", "S", "R", "D"]].fillna(0)
    )

    # Synth number for regulation details
    synth_number = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["synth_number"],
        dtype={"REGULATIONNUMBER": str},
    )
    synth_number.REGULATIONNUMBER = synth_number.REGULATIONNUMBER.str.pad(
        width=8, side="right", fillchar="0"
    )
    synth_number = synth_number.drop_duplicates("PRODUCTCODE_x")
    synth_number["PRODUCTCODE"] = synth_number["PRODUCTCODE_x"]

    # Identify II->I treated units (63 FR 59 = 1998, 61 FR 111/112 = 1996)
    synth_2_1_true = full[
        (full.Reg_Change_List.str.contains("63 FR 59", na=False))
        & (full.SUBMISSION_TYPE_ID == "510(K) Exempt")
    ].copy()
    synth_2_1_true = synth_2_1_true[synth_2_1_true.PRODUCTCODE != "PUN"]

    synth_2_1_true2 = full[
        ((full.Reg_Change_List.str.contains("61 FR 111", na=False))
         | (full.Reg_Change_List.str.contains("61 FR 112", na=False)))
        & ((full.DEVICECLASS == "1") | (full.DEVICECLASS == 1))
        & (full.SUBMISSION_TYPE_ID == "510(K) Exempt")
    ].copy()

    # Remove overlap
    synth_2_1_true = synth_2_1_true[
        ~synth_2_1_true.PRODUCTCODE.isin(synth_2_1_true2.PRODUCTCODE)
    ]
    synth_2_1_true["year_reclassified"] = 1998
    synth_2_1_true2["year_reclassified"] = 1996

    synth_2_1 = pd.concat([synth_2_1_true, synth_2_1_true2])
    synth_2_1["treatment"] = 1

    # Construct DPM
    for df in [synth_2_1]:
        df["serious_event"] = df["L"] + df["S"]
        df["less_serious_event"] = df["R"] + df["H"]
        df["DPM"] = 0.38 * df["D"] + 0.3 * df["serious_event"] + 0.12 * df["less_serious_event"]
        df["v_serious_event"] = df["L"] + df["S"] + df["H"] + df["D"]

    # Control pool: Class I/II devices not reclassified
    def _get_reclass_years(s):
        try:
            found = re.findall(r"\,+\ +[0-9]{1,4}", s)
            found = [x.replace(", ", "") for x in found]
            return [int(x) for x in found] if found else "None"
        except Exception:
            return "Null"

    synth_number["reclass_years"] = synth_number.apply(
        lambda row: _get_reclass_years(str(row.get("Reg_Change_Text", ""))), axis=1
    )
    synth_no_reclass = synth_number[synth_number.reclass_years == "None"]["PRODUCTCODE"]

    synth_2_1_control = full[
        (full.PRODUCTCODE.isin(synth_no_reclass))
        | (((full.DEVICECLASS == "1") | (full.DEVICECLASS == 1))
           & ~(full.PRODUCTCODE.isin(synth_2_1.PRODUCTCODE)))
    ].copy()
    synth_2_1_control["treatment"] = 0

    # Merge PART_DESCRIPTION / SUBPART_DESCRIPTION onto treated + control
    # (needed for 1996 matching which filters on part description)
    sn_desc = synth_number[
        ["PRODUCTCODE", "PART_DESCRIPTION", "SUBPART_DESCRIPTION"]
    ].drop_duplicates("PRODUCTCODE")
    for df in [synth_2_1_true, synth_2_1_true2, synth_2_1_control]:
        for col in ["PART_DESCRIPTION", "SUBPART_DESCRIPTION"]:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
        df_merged = pd.merge(df, sn_desc, on="PRODUCTCODE", how="left")
        for col in sn_desc.columns:
            if col != "PRODUCTCODE":
                df[col] = df_merged[col].values

    # Combine treated + control (DPM on full panel for later use)
    synth_2_1_combined = pd.concat([synth_2_1_control, synth_2_1])
    for df in [synth_2_1_combined]:
        df["serious_event"] = df["L"] + df["S"]
        df["less_serious_event"] = df["R"] + df["H"]
        df["DPM"] = 0.38 * df["D"] + 0.3 * df["serious_event"] + 0.12 * df["less_serious_event"]

    # Create pre-period filtered datasets (original computes mean_DPM
    # ONLY on pre-period data for each cohort)
    synth_2_1_1998_treat = synth_2_1_true[
        (synth_2_1_true.year < synth_2_1_true.year_reclassified)
        & (synth_2_1_true.year > 1991)
    ].copy()
    synth_2_1_1998_control = synth_2_1_control[
        (synth_2_1_control.year < 1998) & (synth_2_1_control.year > 1991)
    ].copy()
    synth_2_1_1996_treat = synth_2_1_true2[
        (synth_2_1_true2.year < synth_2_1_true2.year_reclassified)
        & (synth_2_1_true2.year > 1991)
    ].copy()
    synth_2_1_1996_control = synth_2_1_control[
        (synth_2_1_control.year < 1996) & (synth_2_1_control.year > 1991)
    ].copy()

    # Compute DPM and mean_DPM on each pre-period dataset
    for pre_df in [synth_2_1_1998_treat, synth_2_1_1998_control,
                   synth_2_1_1996_treat, synth_2_1_1996_control]:
        pre_df["serious_event"] = pre_df["L"] + pre_df["S"]
        pre_df["less_serious_event"] = pre_df["R"] + pre_df["H"]
        pre_df["DPM"] = (0.38 * pre_df["D"]
                         + 0.3 * pre_df["serious_event"]
                         + 0.12 * pre_df["less_serious_event"])
        pre_df["mean_DPM"] = pre_df.groupby(
            "PRODUCTCODE"
        )["DPM"].transform("mean")

    # Match 1998 treated PCs (DPM-only matching, using pre-period mean_DPM)
    treated_list = []
    matched_list = []
    similarity = []
    year_reclass_list = []

    # part_desc / subpart_desc are captured in 1998 loop but only used
    # (accidentally) in the 1996 loop -- replicating original quirk
    part_desc = ""
    subpart_desc = ""

    for code in np.unique(synth_2_1_1998_treat["PRODUCTCODE"]):
        treated = synth_2_1_1998_treat[synth_2_1_1998_treat.PRODUCTCODE == code]
        treated = treated.drop_duplicates(subset="PRODUCTCODE")
        yr_reclass = treated.year_reclassified.values[0]
        if "PART_DESCRIPTION" in treated.columns:
            part_desc = treated["PART_DESCRIPTION"].values[0]
        if "SUBPART_DESCRIPTION" in treated.columns:
            subpart_desc = treated["SUBPART_DESCRIPTION"].values[0]
        control = synth_2_1_1998_control.copy()
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control.drop_duplicates(subset="PRODUCTCODE")
        if len(control) == 0:
            continue
        sim_d, sim_i = _get_similar(
            treated["mean_DPM"].values[0], control["mean_DPM"].values
        )
        matched_list.append(control.iloc[sim_i]["PRODUCTCODE"])
        treated_list.append(code)
        similarity.append(sim_d[sim_i])
        year_reclass_list.append(yr_reclass)

    # Match 1996 treated PCs (with part-description filtering using the
    # LAST 1998 treated PC's part_desc/subpart_desc -- an original-code quirk)
    for code in np.unique(synth_2_1_1996_treat["PRODUCTCODE"]):
        treated = synth_2_1_1996_treat[synth_2_1_1996_treat.PRODUCTCODE == code]
        treated = treated.drop_duplicates(subset="PRODUCTCODE")
        yr_reclass = treated.year_reclassified.values[0]
        control = synth_2_1_1996_control.copy()
        control = control[~control.PRODUCTCODE.isin(matched_list)]
        control = control.drop_duplicates(subset="PRODUCTCODE")
        if len(control) == 0:
            continue
        # Original tries subpart+part filtering first, then part-only, then all
        control2 = control
        if "SUBPART_DESCRIPTION" in control.columns:
            control2 = control[
                (control.SUBPART_DESCRIPTION == subpart_desc)
                & (control.PART_DESCRIPTION == part_desc)
            ]
            if len(control2) == 0:
                control2 = control[control.PART_DESCRIPTION == part_desc]
                if len(control2) == 0:
                    control2 = control
        sim_d, sim_i = _get_similar(
            treated["mean_DPM"].values[0], control2["mean_DPM"].values
        )
        matched_list.append(control2.iloc[sim_i]["PRODUCTCODE"])
        treated_list.append(code)
        similarity.append(sim_d[sim_i])
        year_reclass_list.append(yr_reclass)

    matched_pairs = pd.DataFrame({
        "PRODUCTCODE": treated_list,
        "treated": treated_list,
        "match": matched_list,
        "SSE": similarity,
        "FE": range(len(treated_list)),
        "year_reclassified_controls": year_reclass_list,
    })
    logging.info(f"II->I burden sample: {len(matched_pairs)} matched pairs.")

    # Build panel
    synth = pd.concat([
        synth_2_1_control[synth_2_1_control.PRODUCTCODE.isin(matched_pairs["match"])],
        synth_2_1[synth_2_1.PRODUCTCODE.isin(matched_pairs.treated)],
    ])
    synth["posttreat"] = 0
    synth.loc[synth.year >= synth.year_reclassified, "posttreat"] = 1
    synth["factorized"] = synth.PRODUCTCODE.astype("category").cat.codes
    synth["v_serious_event"] = synth["L"] + synth["S"] + synth["H"] + synth["D"]
    synth["v_serious_rate"] = 0.0
    mask = synth.event_count > 0
    synth.loc[mask, "v_serious_rate"] = (
        synth.loc[mask, "v_serious_event"] / synth.loc[mask, "event_count"]
    )

    # Merge pre-period mean_DPM from all four filtered datasets (original
    # approach: concat 1996_ctrl, 1998_ctrl, 1998_treat, 1996_treat, then
    # drop_duplicates keeps the first occurrence for each PC)
    dpm_scores = pd.concat([
        synth_2_1_1996_control[["mean_DPM", "PRODUCTCODE"]].drop_duplicates(),
        synth_2_1_1998_control[["mean_DPM", "PRODUCTCODE"]].drop_duplicates(),
        synth_2_1_1998_treat[["mean_DPM", "PRODUCTCODE"]].drop_duplicates(),
        synth_2_1_1996_treat[["mean_DPM", "PRODUCTCODE"]].drop_duplicates(),
    ]).drop_duplicates(subset="PRODUCTCODE")

    # In-text provenance (JPE 2.2): the DPM-proxy paragraph states that "top-decile
    # device types have roughly four times the proxy score of the 89th-percentile
    # type". No quantile of the proxy was computed anywhere, so the claim had no
    # producing output. It is emitted here from `dpm_scores`, the device-type-level
    # pre-period mean proxy DPM this analysis itself matches on.
    emit_dpm_decile_ratio(dpm_scores)

    synth = pd.merge(synth, dpm_scores, on="PRODUCTCODE", how="left")

    # Assign FE and year_reclassified for controls
    synth = pd.merge(
        synth,
        matched_pairs[["PRODUCTCODE", "match", "SSE", "FE", "year_reclassified_controls"]],
        on="PRODUCTCODE", how="left",
    )
    for matched in matched_list:
        row = matched_pairs[matched_pairs["match"] == matched]
        if len(row) == 0:
            continue
        synth.loc[synth.PRODUCTCODE == matched, "FE"] = row["FE"].values[0]
        ctrl_yr = synth[synth["match"] == matched]["year_reclassified_controls"]
        if len(ctrl_yr) > 0:
            synth.loc[synth.PRODUCTCODE == matched, "year_reclassified"] = ctrl_yr.values[0]

    # Merge part description (drop existing if present to avoid suffixes)
    if "PART_DESCRIPTION" in synth.columns:
        synth = synth.drop(columns=["PART_DESCRIPTION"])
    synth = pd.merge(
        synth,
        synth_number[["PRODUCTCODE", "PART_DESCRIPTION"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )

    # Experience years from manually researched invention/commercial availability dates
    inv_path = config.RAW_DATA_DIR / config.INVENTION_YEAR_FILES["2_1"]
    if inv_path.exists():
        inv_years = pd.read_csv(inv_path)
        inv_years = inv_years.rename(columns={"years": "yr_invent"})
        synth = pd.merge(synth, inv_years[["PRODUCTCODE", "yr_invent"]].drop_duplicates("PRODUCTCODE"),
                         on="PRODUCTCODE", how="left")
        synth["years_exp"] = synth["year_reclassified"] - synth["yr_invent"]
        logging.info(f"Loaded invention years for II->I from {inv_path} ({len(inv_years)} PCs)")
    else:
        logging.warning(f"Invention year file not found: {inv_path}. years_exp will be NaN.")

    return synth, matched_pairs


# ============================================================================
# OLS burden regression and adjusted scatter plot
# ============================================================================

def _consolidate_part_desc(df, part_map):
    """Apply part-description consolidation to reduce dummies."""
    for old, new in part_map.items():
        df.loc[df.PART_DESCRIPTION == old, "PART_DESCRIPTION"] = new
    return df


# In-text provenance (JPE 2.2): accumulates the fitted zero-crossing market ages (the age at which
# the post-reclassification effect crosses zero) so 15_intext can reproduce the manuscript's ~30-year
# (III->II) / ~63-year (II->I) statements. Populated in run_burden_ols_and_plot, written by main().
_EXP_CROSSINGS: list = []


def write_model_coefficient_csv(model, out_path):
    """Write one fitted model's coefficient table as plain CSV (JPE 1.4: no proprietary format).

    Columns: term, coef, std_err, pvalue -- one row per parameter, in the model's own parameter
    order -- followed by a `# nobs,<N>` trailing line so the file is self-contained. This is the
    file Tables D.11a/D.11b are typeset from; it is written here, by the step that fits the model,
    so that no later step depends on a Python pickle.
    """
    params = model.params
    bse = getattr(model, "bse", None)
    pvals = getattr(model, "pvalues", None)
    rows = [{
        "term": name,
        "coef": float(params[name]),
        "std_err": float(bse[name]) if bse is not None and name in bse.index else "",
        "pvalue": float(pvals[name]) if pvals is not None and name in pvals.index else "",
    } for name in params.index]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nobs = getattr(model, "nobs", None)
    with open(out_path, "w", newline="") as fh:
        pd.DataFrame(rows, columns=["term", "coef", "std_err", "pvalue"]).to_csv(fh, index=False)
        if nobs is None:
            raise AssertionError(
                f"{out_path.name}: the fitted model carries no .nobs, so the table's sample size "
                "could not be recorded")
        fh.write(f"# nobs,{int(round(float(nobs)))}\n")
    logging.info("Saved model coefficients: %s", out_path.name)


def run_burden_ols_and_plot(df_done, estimate_name, reclass_label,
                            has_fda_own_accord=True, has_dpm=False):
    """
    Run OLS of per-PC treatment effects on market age + covariates.
    Produce covariate-adjusted scatter plot.

    Parameters:
        df_done: DataFrame with per-PC estimates and characteristics
        estimate_name: column name ('v_serious_est' or 'patent_est')
        reclass_label: '3_2' or '2_1' for filenames and color
        has_fda_own_accord: whether to include FDA_own_accord regressor
        has_dpm: whether to include DPM as regressor

    Returns:
        model: fitted OLS model
        latex_df: tidy regression table DataFrame
    """
    df_done["constant"] = 1.0
    part_map = PART_DESC_MAP_3_2 if reclass_label == "3_2" else PART_DESC_MAP_2_1
    df_done = _consolidate_part_desc(df_done, part_map)
    part_dummies = pd.get_dummies(df_done["PART_DESCRIPTION"], drop_first=True)

    # Build regressors
    if estimate_name == "patent_est":
        base_cols = ["constant", "exp_years", "v_serious_event", "patents_allpats"]
        y_label = "Patent Effect"
        line_color = "#2a9d8f"
    else:
        base_cols = ["constant", "exp_years", "v_serious_event"]
        y_label = "Serious-Event Effect"
        line_color = "#A51C30"

    if has_fda_own_accord and "FDA_own_accord" in df_done.columns:
        base_cols.append("FDA_own_accord")
    if has_dpm and "DPM" in df_done.columns:
        base_cols.append("DPM")

    # Ensure columns exist
    base_cols = [c for c in base_cols if c in df_done.columns]
    X = pd.concat([df_done[base_cols], part_dummies], axis=1)
    y = df_done[estimate_name]

    # Drop NaN rows
    valid = y.notna() & X.notna().all(axis=1)
    X = X[valid].astype(float)
    y = y[valid].astype(float)
    df_plot = df_done[valid].copy()

    if len(y) < 5:
        logging.warning(f"Too few observations ({len(y)}) for OLS: {estimate_name} {reclass_label}")
        return None, None, None

    model = sm.OLS(y, X).fit()
    logging.info(f"OLS {estimate_name} ({reclass_label}): N={len(y)}, "
                 f"R2={model.rsquared:.3f}")
    logging.info(f"\n{model.summary()}")

    # Save the coefficient table in a NON-PROPRIETARY form (JPE 1.4). This .csv is what step 31 (10b_format_remaining_tables.py) reads to typeset Tables
    # D.11a/D.11b. A pickle is a Python- and library-version-specific format, so the .csv is
    # written here, by the step that fits the model, and no later step has to unpickle anything.
    write_model_coefficient_csv(
        model, config.TABLES_DIR / f"model_{estimate_name}_{reclass_label}.csv")

    # ---- Tidy table ----
    summary = model.summary2().tables[1].rename(
        columns={"Coef.": "Coefficient", "Std.Err.": "Std. Error", "P>|t|": "P>|t|"}
    )
    latex_df = summary[["Coefficient", "Std. Error", "P>|t|"]].copy()

    def _sig(p):
        return "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ("+" if p < 0.10 else "")))

    latex_df["Significance"] = summary["P>|t|"].apply(_sig)
    latex_df = latex_df.round({"Coefficient": 4, "Std. Error": 3, "P>|t|": 3})
    latex_df = latex_df.reset_index().rename(
        columns={"index": "Variable", "P>|t|": "p-value"}
    )

    # ---- Covariate-adjusted scatter ----
    beta = model.params
    non_age_cols = [c for c in X.columns if c not in ("constant", "exp_years")]
    rep_vals = X.mean().copy()
    rep_vals["constant"] = 1.0
    contrib_non_age = (X[non_age_cols] - rep_vals[non_age_cols]) @ beta[non_age_cols]
    y_adj = y - contrib_non_age

    x_min = float(df_plot["exp_years"].min())
    x_max = float(df_plot["exp_years"].max())
    exp_grid = np.linspace(x_min, x_max, 200)
    X_grid = pd.DataFrame(0.0, index=np.arange(len(exp_grid)), columns=X.columns)
    X_grid["constant"] = 1.0
    X_grid["exp_years"] = exp_grid
    for c in non_age_cols:
        X_grid[c] = rep_vals[c]

    pred = model.get_prediction(X_grid).summary_frame(alpha=0.05)
    y_fit = pred["mean"].values

    # Zero crossing
    intercept_adj = float(beta["constant"] + (rep_vals[non_age_cols] @ beta[non_age_cols]))
    slope = float(beta.get("exp_years", np.nan))
    zero_cross = None
    if np.isfinite(slope) and abs(slope) > 1e-12:
        zero_cross = -intercept_adj / slope
        # Output-only in-text provenance (does not affect the plot/estimate).
        _EXP_CROSSINGS.append({"reclass_type": reclass_label, "outcome": estimate_name,
                               "zero_crossing_years": round(float(zero_cross), 1)})

    p_age = float(model.pvalues.get("exp_years", np.nan))

    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(df_plot["exp_years"], y_adj, s=40, color="#264653", alpha=0.85)
    ax.plot(exp_grid, y_fit, color=line_color, linewidth=2.0, label="Conditional OLS fit")

    if zero_cross is not None and (x_min <= zero_cross <= x_max):
        ax.axvline(zero_cross, linestyle="--", color="grey", linewidth=1.5)

    ax.axhline(0, linestyle="dotted", color="black", linewidth=1.0)
    ax.set_xlabel("Market Age at Reclassification (Years)", fontsize=20)
    ax.set_ylabel(y_label + " (Covariate-Adjusted)", fontsize=20)
    ax.tick_params(axis="both", labelsize=16)

    annot_lines = []
    if np.isfinite(slope):
        annot_lines.append(f"Slope(Age) = {slope:.4f} (p={p_age:.2f})")
    if zero_cross is not None:
        annot_lines.append(f"Zero Crossing \u2248 {zero_cross:.0f} Years")

    if annot_lines:
        _place_annotation(
            ax, "\n".join(annot_lines),
            x=df_plot["exp_years"].values,
            y=y_adj.values if hasattr(y_adj, "values") else y_adj,
        )

    return model, latex_df, fig


# ============================================================================
# PART 2: Petitioned vs FDA-initiated comparison (Table D.12)
# ============================================================================

def petitioned_vs_fda_analysis():
    """
    Compare outcomes for petitioned vs. FDA-initiated III->II reclassifications.

    Uses the pre-built matched samples:
      - matched_sample_3_2_onepat_innovation (FDA-initiated, baseline)
      - matched_sample_3_2_onepat_innovation_petitioned (petitioned)

    Runs Conley-Taber on each and formats a comparison table.
    """
    logging.info("Running petitioned vs FDA-initiated comparison...")

    # Load the two matched samples
    fda_path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat_innovation"]
    pet_path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat_innovation_petitioned"]

    if not fda_path.exists() or not pet_path.exists():
        logging.warning(
            f"Matched sample files not found: {fda_path} or {pet_path}. "
            "Run 02_match_samples.py first. Skipping petitioned analysis."
        )
        return None

    df_fda = pd.read_csv(fda_path)
    df_pet = pd.read_csv(pet_path)

    logging.info(
        f"FDA-initiated sample: {df_fda[df_fda.treatment == 1]['PRODUCTCODE'].nunique()} "
        f"treated PCs, {len(df_fda)} rows."
    )
    logging.info(
        f"Petitioned sample: {df_pet[df_pet.treatment == 1]['PRODUCTCODE'].nunique()} "
        f"treated PCs, {len(df_pet)} rows."
    )

    # Outcome variables to compare
    outcome_vars = ["real_pats", "dev_count", "times_cited", "xi_real_2019"]
    outcome_labels = {
        "real_pats": "Patenting Rate",
        "dev_count": "Device Approval Rate",
        "times_cited": "Citations-Per-Patent",
        "xi_real_2019": "Average Patent Value",
    }

    # Ensure derived columns exist
    for df in [df_fda, df_pet]:
        if "real_pats" not in df.columns and "patents_allpats" in df.columns:
            df["real_pats"] = df["patents_allpats"]
        if "xi_real_2019" not in df.columns and "xi_real" in df.columns:
            df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019
        for col in ["dev_count", "times_cited", "xi_real", "real_pats"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        if "xi_real_2019" in df.columns:
            df["xi_real_2019"] = df["xi_real_2019"].fillna(0)

    results = []
    for outcome in outcome_vars:
        row = {"Outcome": outcome_labels.get(outcome, outcome)}

        for label, df in [("FDA-Initiated", df_fda), ("Petitioned", df_pet)]:
            if outcome not in df.columns:
                row[f"{label}_est"] = np.nan
                row[f"{label}_lo"] = np.nan
                row[f"{label}_hi"] = np.nan
                continue

            # Need posttreat, treatment, factorized, year columns
            required = {"posttreat", "treatment", "factorized", "year"}
            if not required.issubset(df.columns):
                logging.warning(f"Missing required columns for CT in {label}: {required - set(df.columns)}")
                row[f"{label}_est"] = np.nan
                row[f"{label}_lo"] = np.nan
                row[f"{label}_hi"] = np.nan
                continue

            df_use = df.copy().reset_index(drop=True)
            try:
                est, lo, hi = conley_taber_simple(
                    df_use, outcome, "posttreat", "treatment", "factorized", "year"
                )
                row[f"{label}_est"] = est
                row[f"{label}_lo"] = lo
                row[f"{label}_hi"] = hi
            except Exception as e:
                # This cell becomes NaN in Table_D12_petitioned_vs_fda.tex (printed as a
                # blank), and the draws of every later cell shift.
                logging.error(
                    "CT FAILED for %s (%s): %s -- the table cell will be empty and the "
                    "draws of every later cell shift.", outcome, label, e, exc_info=True)
                row[f"{label}_est"] = np.nan
                row[f"{label}_lo"] = np.nan
                row[f"{label}_hi"] = np.nan

        results.append(row)

    results_df = pd.DataFrame(results)
    return results_df


def format_petitioned_table(results_df):
    """Format the petitioned vs FDA-initiated comparison as LaTeX."""
    if results_df is None or len(results_df) == 0:
        return ""

    rows = []
    for _, row in results_df.iterrows():
        estimates = []
        ses = []
        for label in ["FDA-Initiated", "Petitioned"]:
            est = row.get(f"{label}_est", np.nan)
            lo = row.get(f"{label}_lo", np.nan)
            hi = row.get(f"{label}_hi", np.nan)
            if np.isnan(est):
                estimates.append(np.nan)
                ses.append(np.nan)
            else:
                se = compute_se(est, lo, hi)
                estimates.append(est)
                ses.append(se)

        est_row, se_row = format_table_row(
            row["Outcome"], estimates, ses, decimal_places=3
        )
        rows.append((est_row, se_row))

    table = assemble_table(
        rows,
        caption="Petitioned vs.\\ FDA-Initiated Reclassifications (III$\\to$II)",
        label="tab:petitioned_vs_fda",
        column_headers=["Outcome", "FDA-Initiated", "Petitioned"],
        notes="Conley-Taber 95\\% confidence intervals. "
              "Standard errors in parentheses.",
    )
    return table


# ============================================================================
# PART 3: Format Table D.11 (regulation design OLS)
# ============================================================================

def format_reg_design_table(keep_stats_3_2, keep_stats_2_1):
    """
    Format the regulation design OLS results into a LaTeX table (Table D.11).

    Combines III->II and II->I OLS results into a single table with
    two panels.
    """
    lines = []
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering")
    lines.append("\\caption{Determinants of Treatment Effect Heterogeneity}")
    lines.append("\\label{tab:reg_design}")
    lines.append("\\begin{tabular}{lcccc}")
    lines.append("\\toprule")
    lines.append("& \\multicolumn{2}{c}{III$\\to$II} & \\multicolumn{2}{c}{II$\\to$I} \\\\")
    lines.append("\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}")
    lines.append("Variable & Serious Events & Patents & Serious Events & Patents \\\\")
    lines.append("\\midrule")

    # Merge results
    panels = [
        ("III$\\to$II", keep_stats_3_2),
        ("II$\\to$I", keep_stats_2_1),
    ]

    # Collect unique variables from the first (broadest) table
    all_vars = []
    for _, stats_list in panels:
        if stats_list is not None:
            for df in stats_list:
                if df is not None:
                    all_vars.extend(df["Variable"].tolist())
    # Keep key variables only
    key_vars = ["constant", "exp_years", "v_serious_event", "FDA_own_accord",
                "DPM", "patents_allpats"]

    for var in key_vars:
        cells = [var.replace("_", "\\_")]
        for _, stats_list in panels:
            if stats_list is None:
                cells.extend(["", ""])
                continue
            for df in stats_list:
                if df is None:
                    cells.append("")
                    continue
                match = df[df.Variable == var]
                if len(match) == 0:
                    cells.append("")
                else:
                    coef = match["Coefficient"].values[0]
                    sig = match["Significance"].values[0]
                    se = match["Std. Error"].values[0]
                    cells.append(f"{coef:.4f}{sig}")

        lines.append(" & ".join(cells) + " \\\\")

        # SE row
        se_cells = [""]
        for _, stats_list in panels:
            if stats_list is None:
                se_cells.extend(["", ""])
                continue
            for df in stats_list:
                if df is None:
                    se_cells.append("")
                    continue
                match = df[df.Variable == var]
                if len(match) == 0:
                    se_cells.append("")
                else:
                    se = match["Std. Error"].values[0]
                    se_cells.append(f"({se:.3f})")
        lines.append(" & ".join(se_cells) + " \\\\")
        lines.append("\\addlinespace")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\begin{tablenotes}\\small")
    lines.append("\\item OLS regressions of per-product-code treatment effects on pre-reclassification "
                 "device characteristics. Product-area fixed effects included but not reported.")
    lines.append("\\end{tablenotes}")
    lines.append("\\end{table}")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("=" * 70)
    logging.info("Starting regulation design analysis (Figures D.11-D.12, Tables D.11-D.12)...")
    t_start = time.time()

    # ------------------------------------------------------------------
    # 1. III->II burden analysis
    # ------------------------------------------------------------------
    keep_stats_3_2_list = []
    figs_3_2 = []
    try:
        synth_3_2, mp_3_2 = build_3_2_burden_sample()

        # Per-PC Conley-Taber for serious events and patents
        outcomes_3_2 = ["v_serious_rate", "patents_allpats"]
        treated_3_2 = set(synth_3_2[synth_3_2.treatment == 1]["PRODUCTCODE"])
        logging.info(f"Running per-PC Conley-Taber for {len(treated_3_2)} III->II treated PCs...")

        T_est, T_std, DPM_score = _run_per_pc_ct(
            synth_3_2, outcomes_3_2, treated_3_2
        )

        len_treats = len(treated_3_2)
        df_done_3_2 = pd.DataFrame()
        df_done_3_2["exp_years"] = DPM_score
        df_done_3_2["v_serious_est"] = T_est[:len_treats]
        df_done_3_2["patent_est"] = T_est[len_treats:]
        df_done_3_2["PC"] = list(treated_3_2)

        # Merge characteristics from year before reclassification
        pre_chars = synth_3_2[
            synth_3_2.year == synth_3_2.year_reclassified - 1
        ][["PRODUCTCODE", "FDA_own_accord", "v_serious_event", "L", "H", "D",
           "DPM", "event_count", "patents_allpats", "PART_DESCRIPTION"]].copy()
        pre_chars = pre_chars.drop_duplicates("PRODUCTCODE")

        df_done_3_2 = pd.merge(
            df_done_3_2, pre_chars, how="left", left_on="PC", right_on="PRODUCTCODE"
        )

        # OLS for each outcome
        for est_name in ["v_serious_est", "patent_est"]:
            df_sub = df_done_3_2.dropna(subset=[est_name, "exp_years"]).copy()
            if len(df_sub) < 5:
                logging.warning(f"Insufficient data for {est_name} (3_2). Skipping OLS.")
                keep_stats_3_2_list.append(None)
                continue

            result = run_burden_ols_and_plot(
                df_sub, est_name, "3_2",
                has_fda_own_accord=True, has_dpm=False,
            )
            if result[0] is not None:
                model, latex_df, fig = result
                keep_stats_3_2_list.append(latex_df)
                figs_3_2.append((fig, est_name))
            else:
                keep_stats_3_2_list.append(None)

    except FileNotFoundError as e:
        # FAIL-CLOSED: this block fits the D.11 regressions and writes their coefficient
        # exports and scatter figures. Swallowing the error left step 31 to format Table
        # D.11 from whatever was on disk before, with this step still exiting 0.
        raise RuntimeError(
            f"III->II device-experience analysis: required input not found ({e}). "
            "Run the estimation steps (11-12) and step 9 before this step.") from e
    except Exception as e:
        raise RuntimeError(
            f"III->II device-experience analysis failed: {e}") from e

    # ------------------------------------------------------------------
    # 2. II->I burden analysis
    # ------------------------------------------------------------------
    keep_stats_2_1_list = []
    figs_2_1 = []
    try:
        synth_2_1, mp_2_1 = build_2_1_burden_sample()

        # For II->I, use v_serious_rate and patents_allpats
        outcomes_2_1 = ["v_serious_rate", "patents_allpats"]
        treated_2_1 = set(synth_2_1[synth_2_1.treatment == 1]["PRODUCTCODE"])
        logging.info(f"Running per-PC Conley-Taber for {len(treated_2_1)} II->I treated PCs...")

        # Verify exp_years available from invention year data (fail closed: the experience
        # scatter is a required figure input)
        if "years_exp" not in synth_2_1.columns:
            raise RuntimeError("years_exp missing on the II->I panel; the experience scatter cannot be drawn")

        T_est, T_std, DPM_score = _run_per_pc_ct(
            synth_2_1, outcomes_2_1, treated_2_1,
            use_window=False,  # Original II->I has no time window (just year > 1991)
        )

        len_treats = len(treated_2_1)
        df_done_2_1 = pd.DataFrame()
        df_done_2_1["v_serious_est"] = T_est[:len_treats]
        df_done_2_1["patent_est"] = T_est[len_treats:]
        df_done_2_1["PC"] = list(treated_2_1)

        # Use pre-period mean_DPM from the panel (merged during sample construction
        # from the concatenation of pre-period filtered datasets)
        mean_dpm = (
            synth_2_1[synth_2_1.treatment == 1][["PRODUCTCODE", "mean_DPM"]]
            .drop_duplicates("PRODUCTCODE")
        )
        df_done_2_1 = pd.merge(
            df_done_2_1, mean_dpm, how="left", left_on="PC", right_on="PRODUCTCODE"
        )
        df_done_2_1["DPM"] = df_done_2_1["mean_DPM"]
        df_done_2_1 = df_done_2_1.drop(columns=["mean_DPM", "PRODUCTCODE"])

        # Merge pre-reclassification characteristics
        pre_chars = synth_2_1[
            synth_2_1.year == synth_2_1.year_reclassified - 1
        ][["PRODUCTCODE", "v_serious_event", "L", "H", "D",
           "event_count", "patents_allpats", "PART_DESCRIPTION"]].copy()
        pre_chars = pre_chars.drop_duplicates("PRODUCTCODE")

        df_done_2_1 = pd.merge(
            df_done_2_1, pre_chars, how="left", left_on="PC", right_on="PRODUCTCODE"
        )

        # Experience years from invention year data (already on the panel as years_exp)
        exp_df = synth_2_1[synth_2_1.treatment == 1][
            ["PRODUCTCODE", "years_exp"]
        ].drop_duplicates("PRODUCTCODE").rename(columns={"years_exp": "exp_years"})
        df_done_2_1 = pd.merge(
            df_done_2_1, exp_df[["PRODUCTCODE", "exp_years"]], on="PRODUCTCODE", how="left"
        )

        for est_name in ["v_serious_est", "patent_est"]:
            df_sub = df_done_2_1.dropna(subset=[est_name, "exp_years"]).copy()
            if len(df_sub) < 5:
                logging.warning(f"Insufficient data for {est_name} (2_1). Skipping OLS.")
                keep_stats_2_1_list.append(None)
                continue

            result = run_burden_ols_and_plot(
                df_sub, est_name, "2_1",
                has_fda_own_accord=False, has_dpm=True,
            )
            if result[0] is not None:
                model, latex_df, fig = result
                keep_stats_2_1_list.append(latex_df)
                figs_2_1.append((fig, est_name))
            else:
                keep_stats_2_1_list.append(None)

    except FileNotFoundError as e:
        # FAIL-CLOSED: this block fits the D.11 regressions and writes their coefficient
        # exports and scatter figures. Swallowing the error left step 31 to format Table
        # D.11 from whatever was on disk before, with this step still exiting 0.
        raise RuntimeError(
            f"II->I device-experience analysis: required input not found ({e}). "
            "Run the estimation steps (11-12) and step 9 before this step.") from e
    except Exception as e:
        raise RuntimeError(
            f"II->I device-experience analysis failed: {e}") from e

    # ------------------------------------------------------------------
    # 3. Save individual scatter plot figures
    # ------------------------------------------------------------------
    # III->II scatter plots: save each individually as PNG
    for fig_single, est_name in figs_3_2:
        out_name = f"exp_vs_impact_{est_name}_3_2.png"
        save_figure(fig_single, out_name)
    if not figs_3_2:
        logging.info("No III->II burden figures produced.")

    # II->I scatter plots: save each individually as PNG
    for fig_single, est_name in figs_2_1:
        out_name = f"exp_vs_impact_{est_name}_2_1.png"
        save_figure(fig_single, out_name)
    if not figs_2_1:
        logging.info("No II->I burden figures produced.")

    # ------------------------------------------------------------------
    # 3b. Distribution of experience years figures
    #
    # These figures show the distribution of device age (2019 - invention year)
    # for ALL PMA devices (Class III) and ALL 510(K) devices (Class II) that
    # have invention year data -- not just the matched/treated sample.
    # Original: Implications_for_reg_design.py lines 1306-1456 (III) and 2678-2839 (II).
    # ------------------------------------------------------------------

    # Load the broad invention-year file (all product codes) and synth_number
    inv_all_path = config.RAW_DATA_DIR / config.INVENTION_YEAR_FILES["all_other"]
    inv_all = pd.read_csv(inv_all_path)
    logging.info(f"Loaded broad invention years: {len(inv_all)} PCs from {inv_all_path}")

    synth_number = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["synth_number"],
        dtype={"REGULATIONNUMBER": str},
    )
    synth_number.REGULATIONNUMBER = synth_number.REGULATIONNUMBER.str.pad(
        width=8, side="right", fillchar="0"
    )
    synth_number = synth_number.drop_duplicates("PRODUCTCODE_x")
    synth_number["PRODUCTCODE"] = synth_number["PRODUCTCODE_x"]

    full_sample = pd.read_csv(config.DERIVED_DATA_DIR / config.FULL_SAMPLE)

    # --- Distribution_of_3_over_years: ALL PMA (Class III) PCs ---
    try:
        inv_pma = pd.merge(inv_all, synth_number[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]],
                           on="PRODUCTCODE", how="left")
        inv_pma = inv_pma[inv_pma.SUBMISSION_TYPE_ID == "PMA"]
        others_sub_3 = full_sample[full_sample.PRODUCTCODE.isin(inv_pma["PRODUCTCODE"])]
        others_sub_3 = pd.merge(others_sub_3, inv_pma[["PRODUCTCODE", "years"]], how="left")
        others_sub_3["exp_years"] = 2019 - others_sub_3["years"]
        # Post-2015 cross-section, one row per PC
        df_dist3 = (
            others_sub_3[others_sub_3.year > 2015.0]
            .groupby(["PRODUCTCODE", "exp_years"])
            .mean(numeric_only=True)
            .reset_index()
        )
        logging.info(f"Distribution III: {df_dist3.PRODUCTCODE.nunique()} PMA PCs")

        threetwo = (
            df_dist3.drop_duplicates("PRODUCTCODE")
            .groupby("exp_years")
            .count()["PRODUCTCODE"]
            .reset_index()
        )
        threetwo["count"] = threetwo["PRODUCTCODE"]
        threetwo["exp_years"] = threetwo["exp_years"].astype(int)
        threetwo = threetwo.set_index("exp_years")["count"]
        all_years = range(0, threetwo.index.max() + 5, 1)
        threetwo = threetwo.reindex(all_years, fill_value=0)

        ax_dist3 = threetwo.plot(kind="bar", figsize=(12, 8),
                                 color="#984c2a", edgecolor="black", width=1)
        ax_dist3.set_xlabel("Years of Experience With Device", fontsize=18)
        ax_dist3.set_ylabel("Count", fontsize=18)
        ax_dist3.set_title("Count of Class III Devices by Years of Device Experience",
                           fontsize=24, weight="bold", pad=20)
        plt.tight_layout()
        n = 5
        ticks_to_show = list(range(0, len(threetwo.index), n))
        ax_dist3.set_xticks(ticks_to_show)
        ax_dist3.set_xticklabels([threetwo.index[i] for i in ticks_to_show],
                                 rotation=0, fontsize=14)
        ax_dist3.tick_params(axis="y", labelsize=14)
        fig_dist3 = ax_dist3.get_figure()
        save_figure(fig_dist3, "Distribution_of_3_over_years.png")
    except Exception as e:
        logging.warning(f"Could not produce Distribution_of_3_over_years.png: {e}")

    # --- Distribution_of_2_over_years: ALL 510(K) (Class II) PCs ---
    try:
        inv_510k = pd.merge(inv_all, synth_number[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]],
                            on="PRODUCTCODE", how="left")
        inv_510k = inv_510k[inv_510k.SUBMISSION_TYPE_ID == "510(K)"]
        others_sub_2 = full_sample[full_sample.PRODUCTCODE.isin(inv_510k["PRODUCTCODE"])]
        others_sub_2 = pd.merge(others_sub_2, inv_510k[["PRODUCTCODE", "years"]], how="left")
        others_sub_2["exp_years"] = 2019 - others_sub_2["years"]
        # Post-2015 cross-section, one row per PC
        df_dist2 = (
            others_sub_2[others_sub_2.year > 2015.0]
            .groupby(["PRODUCTCODE", "exp_years"])
            .mean(numeric_only=True)
            .reset_index()
        )
        logging.info(f"Distribution II: {df_dist2.PRODUCTCODE.nunique()} 510(K) PCs")

        threetwo = (
            df_dist2.drop_duplicates("PRODUCTCODE")
            .groupby("exp_years")
            .count()["PRODUCTCODE"]
            .reset_index()
        )
        threetwo["count"] = threetwo["PRODUCTCODE"]
        threetwo["exp_years"] = threetwo["exp_years"].astype(int)
        threetwo = threetwo.set_index("exp_years")["count"]
        all_years = range(0, threetwo.index.max() + 1, 1)
        threetwo = threetwo.reindex(all_years, fill_value=0)

        ax_dist2 = threetwo.plot(kind="bar", figsize=(12, 8),
                                 color="#2a9d8f", edgecolor="black", width=1)
        ax_dist2.set_xlabel("Years of Experience With Device", fontsize=18)
        ax_dist2.set_ylabel("Count", fontsize=18)
        ax_dist2.set_title("Count of Class II Devices by Years of Device Experience",
                           fontsize=24, weight="bold", pad=20)
        plt.tight_layout()
        n = 25
        ticks_to_show = list(range(0, len(threetwo.index), n))
        ax_dist2.set_xticks(ticks_to_show)
        ax_dist2.set_xticklabels([threetwo.index[i] for i in ticks_to_show],
                                 rotation=0, fontsize=14)
        ax_dist2.tick_params(axis="y", labelsize=14)
        fig_dist2 = ax_dist2.get_figure()
        save_figure(fig_dist2, "Distribution_of_2_over_years.png")
    except Exception as e:
        logging.warning(f"Could not produce Distribution_of_2_over_years.png: {e}")

    # ------------------------------------------------------------------
    # 4. Table D.11: Regulation design OLS
    # ------------------------------------------------------------------
    table_d11 = format_reg_design_table(
        keep_stats_3_2_list if keep_stats_3_2_list else None,
        keep_stats_2_1_list if keep_stats_2_1_list else None,
    )
    table_d11_path = config.TABLES_DIR / "Table_D11_reg_design.tex"
    with open(table_d11_path, "w") as f:
        f.write(table_d11)
    logging.info(f"Saved Table D.11: {table_d11_path}")

    # ------------------------------------------------------------------
    # 5. Table D.12: Petitioned vs FDA-initiated
    # ------------------------------------------------------------------
    results_pet = petitioned_vs_fda_analysis()
    table_d12 = format_petitioned_table(results_pet)
    table_d12_path = config.TABLES_DIR / "Table_D12_petitioned_vs_fda.tex"
    with open(table_d12_path, "w") as f:
        f.write(table_d12)
    logging.info(f"Saved Table D.12: {table_d12_path}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    # In-text provenance (JPE 2.2): write the fitted zero-crossing market ages used in Section 6.
    if _EXP_CROSSINGS:
        pd.DataFrame(_EXP_CROSSINGS).to_csv(
            config.TABLES_DIR / "exp_impact_zero_crossings.csv", index=False)
        logging.info(f"  In-text: wrote {len(_EXP_CROSSINGS)} zero-crossing(s) -> "
                     f"exp_impact_zero_crossings.csv")

    elapsed = time.time() - t_start
    logging.info(f"Regulation design analysis complete in {elapsed:.1f}s.")
    logging.info("Outputs:")
    logging.info(f"  Figures: exp_vs_impact_*_3_2.png, exp_vs_impact_*_2_1.png")
    logging.info(f"  Tables:  Table_D11_reg_design.tex, Table_D12_petitioned_vs_fda.tex")


# ============================================================================
# ROBUSTNESS: log(serious+1) and log(patents+1) for manuscript footnote
# ============================================================================
# The manuscript footnote (Section 6) reports maturity-gradient regressions
# using log(v_serious_event + 1) and log(patents_allpats + 1) instead of the
# main specification's severity share and patent levels.  This section
# replicates those estimates.

def _run_per_pc_ct_logged(synth_df, outcomes_logged, treated_pcs,
                          year_min=1991, use_window=True):
    """
    Like _run_per_pc_ct, but log-transforms ALL outcomes via log(y + 1).

    Parameters:
        synth_df: panel DataFrame with treatment, posttreat, factorized, FE, year
        outcomes_logged: list of outcome variable names to log-transform
        treated_pcs: set of treated product codes
        year_min: earliest year to include
        use_window: if True, restrict to [yr_reclass-5, yr_reclass+15]

    Returns:
        T_est, T_std: flat lists (len = len(outcomes_logged) * len(treated_pcs))
        DPM_score: experience years per treated PC
    """
    T_est = []
    T_std = []
    DPM_score = []

    for j in outcomes_logged:
        for i in treated_pcs:
            keep_treats = synth_df[synth_df.PRODUCTCODE == i]["PRODUCTCODE"]
            fes = synth_df[synth_df.PRODUCTCODE.isin(keep_treats)]["FE"]
            test_main = synth_df[synth_df.FE.isin(fes)]
            yr_reclass = test_main[test_main.treatment == 1]["year_reclassified"].values[0]
            test_main = test_main[test_main.year > year_min]
            if use_window:
                test_main = test_main[
                    (test_main.year > yr_reclass - 6) & (test_main.year < yr_reclass + 16)
                ]

            test_main_use = test_main.copy()
            # Log-transform the outcome
            test_main_use[j] = np.log(test_main_use[j] + 1)

            test_main_use = test_main_use.reset_index(drop=True)
            try:
                estimate, alpha025, alpha975 = conley_taber_simple(
                    test_main_use, j, "posttreat", "treatment", "factorized", "year"
                )
            except Exception as e:
                # See the note at the top of this module: the estimate becomes NaN and the
                # draws of every later product code shift.
                logging.error(
                    "CT (logged) FAILED for %s / %s: %s -- this product code drops out of "
                    "the gradient regression and the draws of every later one shift.",
                    j, i, e, exc_info=True)
                estimate, alpha025, alpha975 = np.nan, np.nan, np.nan

            if np.isnan(estimate):
                SE = np.nan
            elif estimate < 0:
                SE = np.abs(estimate - alpha975)
            else:
                SE = estimate - alpha025

            T_est.append(estimate)
            T_std.append(SE)

            if j == outcomes_logged[0]:
                score_vals = synth_df[synth_df.PRODUCTCODE == i]["years_exp"]
                DPM_score.append(score_vals.values[0] if len(score_vals) > 0 else np.nan)

    return T_est, T_std, DPM_score


def _run_log_robustness_ols(df_done, estimate_name, reclass_label,
                            has_fda_own_accord=True, has_dpm=False):
    """
    Run the same cross-sectional OLS as run_burden_ols_and_plot, but only
    print coefficients (no figures).  Used for the log(y+1) robustness check.

    Returns:
        dict with keys: slope, se, pvalue, n
    """
    df_done = df_done.copy()
    df_done["constant"] = 1.0
    part_map = PART_DESC_MAP_3_2 if reclass_label == "3_2" else PART_DESC_MAP_2_1
    df_done = _consolidate_part_desc(df_done, part_map)
    part_dummies = pd.get_dummies(df_done["PART_DESCRIPTION"], drop_first=True)

    if estimate_name == "patent_est":
        base_cols = ["constant", "exp_years", "v_serious_event", "patents_allpats"]
    else:
        base_cols = ["constant", "exp_years", "v_serious_event"]

    if has_fda_own_accord and "FDA_own_accord" in df_done.columns:
        base_cols.append("FDA_own_accord")
    if has_dpm and "DPM" in df_done.columns:
        base_cols.append("DPM")

    base_cols = [c for c in base_cols if c in df_done.columns]
    X = pd.concat([df_done[base_cols], part_dummies], axis=1)
    y = df_done[estimate_name]

    valid = y.notna() & X.notna().all(axis=1)
    X = X[valid].astype(float)
    y = y[valid].astype(float)

    if len(y) < 5:
        logging.warning(f"Too few obs for log-robustness OLS: {estimate_name} {reclass_label}")
        return {"slope": np.nan, "se": np.nan, "pvalue": np.nan, "n": len(y)}

    model = sm.OLS(y, X).fit()
    slope = float(model.params.get("exp_years", np.nan))
    se = float(model.bse.get("exp_years", np.nan))
    pval = float(model.pvalues.get("exp_years", np.nan))

    return {"slope": slope, "se": se, "pvalue": pval, "n": len(y)}


def run_log_robustness():
    """
    Reproduce the manuscript footnote estimates using log(v_serious_event+1)
    and log(patents_allpats+1).  Reproduces the Section 6 footnote values (verified
    against the real-data run 2026-07-15; these ARE what the code produces):
      III->II safety:  β_age = -0.0170, s.e. 0.008, p=0.060
      II->I  safety:  β_age = -0.0015, s.e. 0.001, p=0.218
      III->II innov:   β_age = -0.0396, s.e. 0.013, p=0.008
      II->I  innov:   β_age =  0.0002, s.e. 0.001, p=0.876
    """
    logging.info("=" * 70)
    logging.info("ROBUSTNESS: log(serious+1) and log(patents+1) maturity gradient")
    logging.info("=" * 70)

    # Outcomes to log-transform
    outcomes_logged = ["v_serious_event", "patents_allpats"]

    results = {}

    # --- III->II ---
    try:
        synth_3_2, mp_3_2 = build_3_2_burden_sample()
        treated_3_2 = set(synth_3_2[synth_3_2.treatment == 1]["PRODUCTCODE"])
        logging.info(f"Log robustness: {len(treated_3_2)} III->II treated PCs")

        T_est, T_std, DPM_score = _run_per_pc_ct_logged(
            synth_3_2, outcomes_logged, treated_3_2, use_window=True
        )

        len_treats = len(treated_3_2)
        df_done = pd.DataFrame()
        df_done["exp_years"] = DPM_score
        df_done["v_serious_est"] = T_est[:len_treats]
        df_done["patent_est"] = T_est[len_treats:]
        df_done["PC"] = list(treated_3_2)

        pre_chars = synth_3_2[
            synth_3_2.year == synth_3_2.year_reclassified - 1
        ][["PRODUCTCODE", "FDA_own_accord", "v_serious_event", "L", "H", "D",
           "DPM", "event_count", "patents_allpats", "PART_DESCRIPTION"]].copy()
        pre_chars = pre_chars.drop_duplicates("PRODUCTCODE")
        df_done = pd.merge(df_done, pre_chars, how="left", left_on="PC", right_on="PRODUCTCODE")

        for est_name in ["v_serious_est", "patent_est"]:
            df_sub = df_done.dropna(subset=[est_name, "exp_years"]).copy()
            res = _run_log_robustness_ols(
                df_sub, est_name, "3_2",
                has_fda_own_accord=True, has_dpm=False,
            )
            results[f"3_2_{est_name}"] = res
    except Exception as e:
        logging.error(f"Log robustness III->II failed: {e}", exc_info=True)

    # --- II->I ---
    try:
        synth_2_1, mp_2_1 = build_2_1_burden_sample()
        treated_2_1 = set(synth_2_1[synth_2_1.treatment == 1]["PRODUCTCODE"])
        logging.info(f"Log robustness: {len(treated_2_1)} II->I treated PCs")

        T_est, T_std, DPM_score = _run_per_pc_ct_logged(
            synth_2_1, outcomes_logged, treated_2_1,
            use_window=False,
        )

        len_treats = len(treated_2_1)
        df_done = pd.DataFrame()
        df_done["v_serious_est"] = T_est[:len_treats]
        df_done["patent_est"] = T_est[len_treats:]
        df_done["PC"] = list(treated_2_1)

        mean_dpm = (
            synth_2_1[synth_2_1.treatment == 1][["PRODUCTCODE", "mean_DPM"]]
            .drop_duplicates("PRODUCTCODE")
        )
        df_done = pd.merge(df_done, mean_dpm, how="left", left_on="PC", right_on="PRODUCTCODE")
        df_done["DPM"] = df_done["mean_DPM"]
        df_done = df_done.drop(columns=["mean_DPM", "PRODUCTCODE"])

        pre_chars = synth_2_1[
            synth_2_1.year == synth_2_1.year_reclassified - 1
        ][["PRODUCTCODE", "v_serious_event", "L", "H", "D",
           "event_count", "patents_allpats", "PART_DESCRIPTION"]].copy()
        pre_chars = pre_chars.drop_duplicates("PRODUCTCODE")
        df_done = pd.merge(df_done, pre_chars, how="left", left_on="PC", right_on="PRODUCTCODE")

        exp_df = synth_2_1[synth_2_1.treatment == 1][
            ["PRODUCTCODE", "years_exp"]
        ].drop_duplicates("PRODUCTCODE").rename(columns={"years_exp": "exp_years"})
        df_done = pd.merge(
            df_done, exp_df[["PRODUCTCODE", "exp_years"]], on="PRODUCTCODE", how="left"
        )

        for est_name in ["v_serious_est", "patent_est"]:
            df_sub = df_done.dropna(subset=[est_name, "exp_years"]).copy()
            res = _run_log_robustness_ols(
                df_sub, est_name, "2_1",
                has_fda_own_accord=False, has_dpm=True,
            )
            results[f"2_1_{est_name}"] = res
    except Exception as e:
        logging.error(f"Log robustness II->I failed: {e}", exc_info=True)

    # --- Print comparison ---
    logging.info("=" * 70)
    logging.info("LOG ROBUSTNESS: Comparison with manuscript footnote")
    logging.info("=" * 70)

    # Manuscript Section 6 footnote values (verified on the real-data run 2026-07-15).
    ms_vals = {
        "3_2_v_serious_est": {"slope": -0.0170, "se": 0.008, "pvalue": 0.060},
        "3_2_patent_est":    {"slope": -0.0396, "se": 0.013, "pvalue": 0.008},
        "2_1_v_serious_est": {"slope": -0.0015, "se": 0.001, "pvalue": 0.218},
        "2_1_patent_est":    {"slope":  0.0002, "se": 0.001, "pvalue": 0.876},
    }

    labels = {
        "3_2_v_serious_est": "III->II safety (log serious+1)",
        "3_2_patent_est":    "III->II innovation (log patents+1)",
        "2_1_v_serious_est": "II->I  safety (log serious+1)",
        "2_1_patent_est":    "II->I  innovation (log patents+1)",
    }

    for key in ms_vals:
        ms = ms_vals[key]
        got = results.get(key, {"slope": np.nan, "se": np.nan, "pvalue": np.nan, "n": 0})
        match_slope = abs(got["slope"] - ms["slope"]) < 0.005 if np.isfinite(got["slope"]) else False
        match_se = abs(got["se"] - ms["se"]) < 0.005 if np.isfinite(got["se"]) else False
        status = "MATCH" if (match_slope and match_se) else "MISMATCH"

        logging.info(
            f"  {labels[key]}:\n"
            f"    Manuscript:  β={ms['slope']:.4f}, SE={ms['se']:.3f}, p={ms['pvalue']:.3f}\n"
            f"    Replication: β={got['slope']:.4f}, SE={got['se']:.3f}, p={got['pvalue']:.3f}, N={got['n']}\n"
            f"    --> {status}"
        )

    # In-text provenance (JPE 2.2): emit the Section 6 footnote maturity-gradient slopes so
    # 15_intext can reproduce them. Keys are "<reclass>_<outcome>" with reclass = first 3 chars.
    _rows = [{"reclass_type": k[:3], "outcome": k[4:], "slope": v["slope"], "se": v["se"],
              "pvalue": v["pvalue"], "n": v["n"]} for k, v in results.items()]
    if _rows:
        pd.DataFrame(_rows).to_csv(config.TABLES_DIR / "maturity_gradient_slopes.csv", index=False)
        logging.info(f"  In-text: wrote {len(_rows)} maturity-gradient slope(s) -> "
                     f"maturity_gradient_slopes.csv")

    return results


if __name__ == "__main__":
    rc = main() or 0

    # Run the log-robustness check after the main analysis
    logging.info("\n\nRunning log(y+1) robustness check for manuscript footnote...")
    run_log_robustness()
    sys.exit(rc)
