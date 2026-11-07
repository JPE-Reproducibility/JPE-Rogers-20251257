#!/usr/bin/env python
"""
11b_recall_analysis.py -- Recall analysis (Figures D.14-D.15).

Analyzes FDA device recall data around the 2015/2017 deregulation (II->I)
and the staggered 1990s-2000s reclassifications (II->I matched sample).

Figure D.14: Event study of recall counts for the 2015 Class II exemptions,
             matched to unaffected Class II devices, estimated via R fixest.
Figure D.15: Event study of recall counts for the 1996-era II->I events
             using the matched sample and DID-imputation via R.

Also produces adverse-event event studies for the 2015 deregulations (D, L, H,
v_serious) as supplementary panels.

Inputs:
    data/raw/device-recall-0001-of-0001-2.json
    data/raw/Class2_Exemptions_2017_Grennan.csv
    data/derived/Full_sample.csv
    data/derived/Adv_Event_2020_2022.csv
    data/derived/RegNum_Factorized_Synth.csv
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/intuitive_2_1_oct22_24.csv
    r_scripts/preprocess.R
    r_scripts/did_imputation_topython.R

Outputs:
    output/figures/Recalls_2017.png
    output/figures/Recalls_2017_raw_trends.png
    output/figures/2_1_no_logv_serious_2016_oct22_24.png
    output/figures/2_1_no_log_recalls_1996.png
    output/figures/Recalls_1996_raw_trend.png
    output/figures/Recalls_1996_raw_trend_intuitive.png
    output/tables/recall_event_study_1996.csv       (in-text: the recall decline)
    output/tables/recall_in_text_numbers.csv        (in-text: decline, % of control
                                                     mean, 2015 cohort size)
"""

import sys
import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style

from rpy2 import robjects
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from plotting import save_figure
from match_mahal import get_similar

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "11b_recall_analysis.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Colors
# ============================================================================
REG_LINE_C = config.COLORS["dereg_line"]
DOT_C = config.COLORS["dereg_dot"]
ERROR_C = config.COLORS["error"]
CONTROL_C = "#e76f51"  # salmon for control group in raw-trend plots


# ============================================================================
# Helper: raw-trend plot (treated vs control means by year)
# ============================================================================

def plot_raw_trends(df, year_col, treatment_col, outcome_col, output_name,
                    treated_label="Deregulated Devices",
                    control_label="Unaffected",
                    title="Average Device Recall Counts by Treatment Status",
                    ylabel="Recall Counts",
                    max_year=2019):
    """Plot mean outcome by year for treated vs control groups.

    Matches original notebook style: open-circle markers via separate
    plt.plot() + ax.scatter() calls, default legend placement.

    Parameters:
        max_year: truncate data after this year (default 2019; recall reporting
                  lags make post-2019 data unreliable).
    """
    df = df[df[year_col] <= max_year].copy()
    means = df.groupby([treatment_col, year_col]).mean(numeric_only=True).reset_index()

    treated = means[means[treatment_col] == 1].sort_values(year_col)
    control = means[means[treatment_col] == 0].sort_values(year_col)

    style.use("seaborn-v0_8-poster")
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

    plt.plot(treated[year_col], treated[outcome_col], c=REG_LINE_C, label=treated_label)
    ax.scatter(treated[year_col], treated[outcome_col], facecolors="none",
               edgecolors=REG_LINE_C, s=40, linewidth=3)
    plt.plot(control[year_col], control[outcome_col], c=CONTROL_C, label=control_label)
    ax.scatter(control[year_col], control[outcome_col], facecolors="none",
               edgecolors=CONTROL_C, s=40, linewidth=3)

    plt.title(title, fontsize=26, pad=40)
    plt.xlabel("Year", fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.rc("xtick", labelsize=14)
    plt.rc("ytick", labelsize=14)
    plt.xticks(np.arange(min(treated[year_col]), max(treated[year_col]) + 1, 2.0))
    plt.legend()

    save_figure(fig, output_name)


# ============================================================================
# Helper: build recall panel from JSON
# ============================================================================

def load_recall_data():
    """Load device recall JSON and build a PRODUCTCODE x year panel."""
    json_path = config.RAW_DATA_DIR / "device-recall-0001-of-0001-2.json"
    logging.info(f"Loading recall JSON from {json_path}")
    with open(json_path, "r") as f:
        data = json.load(f)

    # Extract dates and product codes from the JSON results
    results = list(data.values())[1] if isinstance(list(data.values())[1], list) else list(data.items())[1][1]
    dates, pcs = [], []
    for d in results:
        dates.append(d.get("event_date_initiated", "None"))
        pcs.append(d.get("product_code", "None"))

    df = pd.DataFrame({"PRODUCTCODE": pcs, "dates": pd.to_datetime(dates, errors="coerce")})
    df["year"] = pd.DatetimeIndex(df["dates"]).year
    df["PRODUCTCODE"] = df["PRODUCTCODE"].str.upper()

    # Build balanced PC x year panel
    grouped = df.groupby(["PRODUCTCODE", "year"]).count().reset_index()
    grouped = (
        grouped.set_index(["PRODUCTCODE", "year"])
        .unstack(fill_value=0)
        .stack()
        .sort_index(level=1)
        .reset_index()
    )
    grouped = grouped[grouped.year > 1999]
    logging.info(f"Recall panel: {len(grouped)} rows, {grouped.PRODUCTCODE.nunique()} PCs.")
    return grouped


# ============================================================================
# Helper: nearest-neighbor matching for recalls
# ============================================================================

def match_recalls(dfgrouped, treatment_col, outcome, cutoff, topn=1):
    """One-to-one matching of treated to control PCs on pre-event outcome."""
    product_codes_iter = np.unique(
        dfgrouped[dfgrouped[treatment_col] == 1]["PRODUCTCODE"].drop_duplicates().sample(frac=1)
    )
    matched_list = []
    matched_pairs = pd.DataFrame()

    for i, number in enumerate(product_codes_iter):
        temp = pd.DataFrame()
        control = dfgrouped[~dfgrouped.PRODUCTCODE.isin(product_codes_iter)]
        control = control[~control.PRODUCTCODE.isin(list(matched_list))]
        control = control[control[outcome].notnull()]

        treated = dfgrouped[dfgrouped.PRODUCTCODE == number]
        yr_reclass = treated["year_reclassified"].values[0]
        treated = treated.copy()
        treated["event_time"] = treated["year"] - int(float(yr_reclass))
        control = control.copy()
        control["event_time"] = control["year"] - int(float(yr_reclass))

        control_meaned = (
            control[(control.event_time < 0) & (control.event_time > cutoff)]
            .groupby("PRODUCTCODE").mean(numeric_only=True).reset_index()
        )
        treated_meaned = treated[(treated.event_time < 0) & (treated.event_time > cutoff)].mean(numeric_only=True)

        if control_meaned.empty:
            continue

        sim_distances, sim_indices = get_similar(
            treated_meaned[[outcome]].values,
            control_meaned[[outcome]].values,
            topn=topn,
        )

        temp["PRODUCTCODE"] = [number]
        temp["treated"] = [number]
        temp["match"] = [control_meaned.iloc[sim_indices]["PRODUCTCODE"].values]
        for j in range(topn):
            matches = control_meaned.iloc[sim_indices]["PRODUCTCODE"].values
            if j < len(matches):
                temp[f"match_{j}"] = matches[j]
        temp["SSE"] = [np.round(sim_distances[sim_indices], 2)]
        temp["FE"] = i
        temp["year_reclassified_controls"] = yr_reclass
        matched_pairs = pd.concat([matched_pairs, temp], ignore_index=True)
        matched_list += list(control_meaned.iloc[sim_indices]["PRODUCTCODE"].values)

    matched_pairs = matched_pairs[matched_pairs["match_0"] != "None"]
    return matched_pairs


def assemble_matched_panel(dfgrouped, matched_pairs, topn=1):
    """Merge matched pairs back to full panel with FE assignments."""
    final = dfgrouped[
        dfgrouped.PRODUCTCODE.isin(matched_pairs.treated)
        | dfgrouped.PRODUCTCODE.isin(np.concatenate(list(matched_pairs["match"].values)))
    ]
    for i in range(topn):
        temp = matched_pairs[[f"match_{i}", "FE"]].copy()
        temp["PRODUCTCODE"] = temp[f"match_{i}"]
        if i == 0:
            stacked_fes = pd.concat([matched_pairs[["PRODUCTCODE", "FE"]], temp[["PRODUCTCODE", "FE"]]])
        else:
            stacked_fes = pd.concat([stacked_fes, temp])
    final = pd.merge(final, stacked_fes[["PRODUCTCODE", "FE"]], on="PRODUCTCODE", how="left")
    return final


# ============================================================================
# Helper: event-study plot using R fixest
# ============================================================================

def plot_es_with_R(final, outcome, title, output_path, window_low=10, window_high=8):
    """Run recalls_ES via R and produce event-study figure."""
    r = robjects.r
    r["source"](str(config.R_SCRIPTS_DIR / "preprocess.R"))
    recalls_ES = robjects.globalenv["recalls_ES"]

    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(final)
    r("gc()")  # reclaim before estimating on rpy2-converted data (see estimation._to_r); no effect on results
    df_result_r = recalls_ES(df_r, outcome)

    with localconverter(ro.default_converter + pandas2ri.converter):
        static = ro.conversion.rpy2py(df_result_r[0])
        ses = ro.conversion.rpy2py(df_result_r[1])

    index_int_low = int(-final["ET"].min() - window_low)
    index_int_high = int(-final["ET"].min() + window_high)
    static = static[index_int_low:index_int_high]
    ses = ses[index_int_low:index_int_high]

    # The R function may return fewer coefficients than the full window
    # (e.g., if data doesn't span the full range). Adjust window_high accordingly.
    actual_n = len(static)  # should be window_low + window_high (before insert)
    expected_n = window_low + window_high
    if actual_n < expected_n:
        window_high = actual_n - window_low

    estimates_df = pd.DataFrame()
    estimates_df["ET"] = np.arange(-window_low, window_high + 1, 1)
    # Insert 0 for the omitted period (t=-1)
    static = np.insert(static, window_low - 1, 0)
    ses = np.insert(ses, window_low - 1, 0)
    estimates_df["Effect"] = static
    estimates_df["SE"] = ses.astype(float)

    # Pre/post trend lines
    m, b = np.polyfit(
        estimates_df[estimates_df.ET < 0]["ET"],
        estimates_df[estimates_df.ET < 0]["Effect"], 1,
    )
    m2, b2 = np.polyfit(
        estimates_df[estimates_df.ET >= 0]["ET"],
        estimates_df[estimates_df.ET >= 0]["Effect"], 1,
    )

    style.use("seaborn-v0_8-poster")
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

    pre = estimates_df[estimates_df.ET < 0]
    post = estimates_df[estimates_df.ET >= 0]
    ax.plot(pre["ET"], m * pre["ET"] + b, "--", color=REG_LINE_C)
    ax.plot(post["ET"], m2 * post["ET"] + b2, "--", color=REG_LINE_C)

    eb = ax.errorbar(
        estimates_df["ET"], estimates_df["Effect"],
        yerr=1.96 * estimates_df["SE"], ls="none", elinewidth=1, ecolor="grey",
    )
    eb[-1][0].set_linestyle("--")
    ax.scatter(
        estimates_df["ET"], estimates_df["Effect"],
        facecolors="none", edgecolors=DOT_C, s=80, linewidth=3,
    )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.xlabel("Years Since Deregulation", fontsize=24)
    plt.ylabel("Change in Outcome", fontsize=24)
    ax.set_title(title, fontsize=30, pad=30)
    plt.axvline(x=-0.5, ls="--", lw=1, color="black")
    plt.axhline(y=0, ls="--", lw=1, color="black")
    plt.xticks(np.arange(estimates_df["ET"].min(), estimates_df["ET"].max() + 1, 2.0))
    plt.rc("xtick", labelsize=16)
    plt.rc("ytick", labelsize=16)

    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close(fig)


# ============================================================================
# In-text number emission (JPE Policy 2.2)
# ============================================================================

# Event time at which the recall decline is read. The manuscript describes "no
# divergence at event times 4-6 when data exist, and a significant decline
# beginning around year 7 that grows thereafter", and then quotes "the decline of
# about 0.5 recalls per device-type-year" -- i.e. the decline where it begins, at
# event time 7, not the later (larger) effects it grows into. The mean effect over
# the whole post-divergence window is emitted alongside it, unregistered, so the
# alternative reading is visible in the same file.
RECALL_DECLINE_ONSET_ET = 7


def emit_recall_in_text_numbers(estimates_df, panel, fda_deregs):
    """Write the recall event-study coefficients and the two in-text magnitudes.

    output/tables/recall_event_study_1996.csv -- the per-event-time effects and
        standard errors plotted in the 1996-era recall event study.
    output/tables/recall_in_text_numbers.csv -- the derived magnitudes:
        recall_decline_per_device_type_year  = mean effect over the post-divergence
            window (manuscript: about 0.5 recalls per device-type-year)
        recall_decline_pct_of_control_mean   = |that decline| / the control group's
            mean recalls per device-type-year (manuscript: roughly 50 percent)
        control_mean_recalls_per_device_type_year -- the denominator, so the ratio
            can be checked without rerunning the estimation
        class2_device_types_2015 -- rows of the 2015 Class II exemption list
            (manuscript: "more than 200 Class II device types")
    """
    tables_dir = config.TABLES_DIR
    tables_dir.mkdir(parents=True, exist_ok=True)

    es_path = tables_dir / "recall_event_study_1996.csv"
    estimates_df[["ET", "Effect", "SE"]].to_csv(es_path, index=False)
    logging.info(f"Saved recall event-study coefficients: {es_path}")

    lo = RECALL_DECLINE_ONSET_ET
    onset = estimates_df[estimates_df.ET == lo]
    decline = float(onset["Effect"].iloc[0]) if len(onset) else float("nan")
    post = estimates_df[estimates_df.ET >= lo]
    decline_window_mean = float(post["Effect"].mean()) if len(post) else float("nan")

    # Control mean recalls per device-type-year on the estimating panel.
    ctrl = panel[panel.treatment == 0]
    control_mean = float(pd.to_numeric(ctrl["dates"], errors="coerce").mean())
    pct = (abs(decline) / control_mean * 100.0) if control_mean else float("nan")
    pct_window = ((abs(decline_window_mean) / control_mean * 100.0)
                  if control_mean else float("nan"))

    n_class2_2015 = int(len(fda_deregs))

    rows = [
        {"metric": "recall_decline_per_device_type_year",
         "description": f"Recall event-study effect at event time {lo}, where the "
                        "significant decline begins",
         "computed": round(decline, 4), "manuscript_value": -0.5},
        {"metric": "recall_decline_window_mean",
         "description": f"Mean recall event-study effect over event times >= {lo} "
                        "(the whole post-divergence window; alternative reading)",
         "computed": round(decline_window_mean, 4), "manuscript_value": ""},
        {"metric": "recall_decline_window_pct_of_control_mean",
         "description": "|window mean| / control mean, in percent (alternative reading)",
         "computed": round(pct_window, 2), "manuscript_value": ""},
        {"metric": "control_mean_recalls_per_device_type_year",
         "description": "Mean recalls per device-type-year among control device types "
                        "in the 1996-era recall estimating panel",
         "computed": round(control_mean, 4), "manuscript_value": ""},
        {"metric": "recall_decline_pct_of_control_mean",
         "description": "|decline| / control mean, in percent",
         "computed": round(pct, 2), "manuscript_value": 50.0},
        {"metric": "class2_device_types_2015",
         "description": "Class II device types on the 2015 exemption list "
                        "(data/raw/Class2_Exemptions_2017_Grennan.csv)",
         "computed": n_class2_2015, "manuscript_value": ">200"},
    ]
    out_path = tables_dir / "recall_in_text_numbers.csv"
    pd.DataFrame(rows, columns=["metric", "description", "computed",
                                "manuscript_value"]).to_csv(out_path, index=False)
    for r in rows:
        logging.info(f"  [recall in-text] {r['metric']}: computed={r['computed']} "
                     f"(manuscript={r['manuscript_value']})")
    logging.info(f"Saved recall in-text numbers: {out_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting recall analysis (Figures D.14, D.15)...")

    # ---- Load 2015 deregulation list ----
    fda_deregs = pd.read_csv(config.RAW_DATA_DIR / "Class2_Exemptions_2017_Grennan.csv")

    # ---- Load and prepare recall panel ----
    dfgrouped_filled = load_recall_data()

    # ================================================================
    # Figure D.14: 2015 Deregulation -- Recall Event Study
    # ================================================================
    logging.info("--- Figure D.14: 2015 recall event study ---")
    fda_deregs["treated"] = 1
    dfgrouped_merged = pd.merge(
        dfgrouped_filled, fda_deregs[["treated", "PRODUCTCODE"]], how="left", on="PRODUCTCODE",
    )
    dfgrouped_merged.loc[dfgrouped_merged.treated != 1, "treated"] = 0
    dfgrouped_merged["factorized"] = dfgrouped_merged.PRODUCTCODE.astype("category").cat.codes
    dfgrouped_merged["treatment"] = dfgrouped_merged["treated"]
    dfgrouped_merged["year_reclassified"] = 2015

    # Match recalls
    matched_pairs = match_recalls(dfgrouped_merged, "treatment", "dates", cutoff=-5, topn=1)
    final = assemble_matched_panel(dfgrouped_merged, matched_pairs, topn=1)

    final["year_treated"] = 2016
    final["post"] = 0
    final.loc[final.year >= final.year_treated, "post"] = 1
    final["posttreat"] = final["treatment"] * final["post"]
    final["dates"] = final["dates"].clip(
        lower=final["dates"].quantile(0.01), upper=final["dates"].quantile(0.99),
    )
    final["ET"] = final["year"] - final["year_reclassified"]
    final.loc[final.treatment == 0, "ET"] = 0

    plot_es_with_R(
        final, "dates", "Device Recalls",
        config.FIGURES_DIR / "Recalls_2017.png",
        window_low=10, window_high=8,
    )

    # Raw trend: 2017 deregulation recalls
    plot_raw_trends(
        final, "year", "treatment", "dates", "Recalls_2017_raw_trends.png",
        treated_label="Down-Classified Devices",
    )

    # ---- Adverse event analysis for 2015 deregulations ----
    logging.info("--- Figure D.14: 2015 adverse event event studies ---")
    adv_2015 = pd.read_csv(config.DERIVED_DATA_DIR / config.FULL_SAMPLE)
    adv_2015 = adv_2015[adv_2015.year != 0]

    # Narrow to needed columns before unstack (matching original script)
    adv_2015 = adv_2015[["PRODUCTCODE", "year", "L", "H", "S", "D"]]

    # Append 2020-2022 adverse event data if available
    adv_ext_path = config.DERIVED_DATA_DIR / "Adv_Event_2020_2022.csv"
    if adv_ext_path.exists():
        df_ext = pd.read_csv(adv_ext_path)
        df_ext = df_ext[df_ext.PRODUCTCODE.isin(adv_2015["PRODUCTCODE"].values)]
        adv_2015 = pd.concat([
            adv_2015,
            df_ext[df_ext.PRODUCTCODE.isin(set(adv_2015.PRODUCTCODE))][
                ["PRODUCTCODE", "year", "L", "H", "S", "D"]
            ],
        ])

    adv_2015 = (
        adv_2015.set_index(["PRODUCTCODE", "year"])
        .unstack(fill_value=0).stack().sort_index(level=1).reset_index()
    )
    adv_2015["treatment"] = 0
    adv_2015.loc[adv_2015.PRODUCTCODE.isin(set(fda_deregs["PRODUCTCODE"].values)), "treatment"] = 1
    adv_2015["year_reclassified"] = 2016

    # Merge SUBMISSION_TYPE_ID from synth_number (matching original script)
    synth_number = pd.read_csv(
        config.DERIVED_DATA_DIR / config.SOURCE_FILES["synth_number"],
        dtype={"REGULATIONNUMBER": str},
    )
    synth_number.REGULATIONNUMBER = synth_number.REGULATIONNUMBER.str.pad(width=8, side="right", fillchar="0")
    synth_number = synth_number.drop_duplicates("PRODUCTCODE_x")
    synth_number["PRODUCTCODE"] = synth_number["PRODUCTCODE_x"]
    adv_2015 = pd.merge(
        adv_2015, synth_number[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]],
        on="PRODUCTCODE", how="left",
    )
    adv_2015["factorized"] = adv_2015.PRODUCTCODE.astype("category").cat.codes
    adv_2015 = adv_2015[adv_2015.year > 1991]
    adv_2015["v_serious"] = adv_2015["D"] + adv_2015["L"] + adv_2015["H"] + adv_2015["S"]
    adv_2015 = adv_2015[adv_2015.year > 2005]

    rename_dict = {
        "L": "Life-Threatening Events",
        "H": "Hospitalization Events",
        "D": "Mortality Events",
        "v_serious": "Serious Adverse Events",
    }

    for name, full_name in rename_dict.items():
        logging.info(f"  Estimating 2015 adverse events: {name}")
        # Match on pre-event outcome
        adv_temp = adv_2015.copy()
        product_codes_iter = np.unique(
            adv_temp[adv_temp.treatment == 1]["PRODUCTCODE"].drop_duplicates().sample(frac=1)
        )
        matched_list = []
        matched_pairs = pd.DataFrame()

        for i, number in enumerate(product_codes_iter):
            temp = pd.DataFrame()
            control = adv_temp[~adv_temp.PRODUCTCODE.isin(product_codes_iter)]
            control = control[~control.PRODUCTCODE.isin(list(matched_list))]
            control = control[
                (control.SUBMISSION_TYPE_ID == "510(K)") | (control.SUBMISSION_TYPE_ID == "510(K) Exempt")
            ]
            control = control[control[name].notnull()]

            treated = adv_temp[adv_temp.PRODUCTCODE == number].copy()
            yr_reclass = treated["year_reclassified"].values[0]
            treated["event_time"] = treated["year"] - int(float(yr_reclass))
            control = control.copy()
            control["event_time"] = control["year"] - int(float(yr_reclass))

            control_meaned = (
                control[(control.event_time < 0) & (control.event_time > -15)]
                .groupby("PRODUCTCODE").mean(numeric_only=True).reset_index()
            )
            treated_meaned = treated[(treated.event_time < 0) & (treated.event_time > -15)].mean(numeric_only=True)

            if control_meaned.empty:
                continue

            sim_distances, sim_indices = get_similar(
                treated_meaned[[name]].values,
                control_meaned[[name]].values,
                topn=1,
            )
            temp["PRODUCTCODE"] = [number]
            temp["treated"] = [number]
            temp["match"] = [control_meaned.iloc[sim_indices]["PRODUCTCODE"].values]
            matches = control_meaned.iloc[sim_indices]["PRODUCTCODE"].values
            temp["match_0"] = matches[0] if len(matches) > 0 else "None"
            temp["SSE"] = [np.round(sim_distances[sim_indices], 2)]
            temp["FE"] = i
            temp["year_reclassified_controls"] = yr_reclass
            matched_pairs = pd.concat([matched_pairs, temp], ignore_index=True)
            matched_list += list(matches)

        if matched_pairs.empty:
            logging.warning(f"  No matched pairs for {name}. Skipping.")
            continue

        matched_pairs = matched_pairs[matched_pairs["match_0"] != "None"]
        final_adv = assemble_matched_panel(adv_temp, matched_pairs, topn=1)

        final_adv["year_treated"] = 2016
        final_adv["post"] = 0
        final_adv.loc[final_adv.year >= final_adv.year_treated, "post"] = 1
        final_adv["posttreat"] = final_adv["treatment"] * final_adv["post"]
        final_adv[name] = final_adv[name].clip(
            lower=final_adv[name].quantile(0.01), upper=final_adv[name].quantile(0.99),
        )
        final_adv["ET"] = final_adv["year"] - final_adv["year_reclassified"]
        final_adv.loc[final_adv.treatment == 0, "ET"] = 0
        final_adv = final_adv[final_adv.year > 1991]

        plot_es_with_R(
            final_adv, name, full_name,
            config.FIGURES_DIR / f"2_1_no_logv_serious_2016_oct22_24.png" if name == "v_serious" else config.FIGURES_DIR / f"Figure_D14_recall_2015_{name}.png",
            window_low=10, window_high=6,
        )

    # ================================================================
    # Figure D.15: 1996-era recalls using matched sample
    # ================================================================
    logging.info("--- Figure D.15: 1996-era recall event study ---")
    df_2_1_matched = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"])
    df_2_1_matched["treated"] = df_2_1_matched["treatment"]

    dfgrouped_merged2 = pd.merge(
        dfgrouped_filled[dfgrouped_filled.PRODUCTCODE.isin(df_2_1_matched["PRODUCTCODE"])],
        df_2_1_matched[["treated", "PRODUCTCODE", "year_reclassified"]].drop_duplicates("PRODUCTCODE"),
        how="left", on="PRODUCTCODE",
    )
    dfgrouped_merged2["factorized"] = dfgrouped_merged2.PRODUCTCODE.astype("category").cat.codes

    # Raw trend: 1996-era recalls (matched controls, pre-extension panel)
    plot_raw_trends(dfgrouped_merged2, "year", "treated", "dates",
                    "Recalls_1996_raw_trend.png")

    # Extend panel back to 1993
    df_addon = pd.DataFrame({
        "year": list(range(1993, 2001)),
        "PRODUCTCODE": ["EXTEND"] * 8,
        "dates": [0] * 8,
        "treated": [0] * 8,
        "factorized": [-1111] * 8,
    })
    dfgrouped_merged3 = pd.concat([dfgrouped_merged2, df_addon])
    dfgrouped_merged3 = (
        dfgrouped_merged3.set_index(["PRODUCTCODE", "year"])
        .unstack(fill_value=0).stack().sort_index(level=1).reset_index()
    )
    dfgrouped_merged3 = dfgrouped_merged3[dfgrouped_merged3.PRODUCTCODE != "EXTEND"]
    dfgrouped_merged3["factorized"] = dfgrouped_merged3.PRODUCTCODE.astype("category").cat.codes

    # Propagate treated and year_reclassified per PC
    grouped = dfgrouped_merged3.groupby("PRODUCTCODE")["treated"].max()
    dfgrouped_merged3["treated"] = dfgrouped_merged3["PRODUCTCODE"].map(grouped)
    grouped = dfgrouped_merged3.groupby("PRODUCTCODE")["year_reclassified"].max()
    dfgrouped_merged3["year_reclassified"] = dfgrouped_merged3["PRODUCTCODE"].map(grouped)
    dfgrouped_merged3.loc[dfgrouped_merged3.treated == 0, "year_reclassified"] = 0

    dfgrouped_merged3["year_treated"] = dfgrouped_merged3["year_reclassified"]
    dfgrouped_merged3["treatment"] = dfgrouped_merged3["treated"]
    dfgrouped_merged3["dates"] = dfgrouped_merged3["dates"].clip(
        lower=dfgrouped_merged3["dates"].quantile(0.01),
        upper=dfgrouped_merged3["dates"].quantile(0.99),
    )
    dfgrouped_merged3["ET"] = dfgrouped_merged3["year"] - dfgrouped_merged3["year_reclassified"]
    dfgrouped_merged3.loc[dfgrouped_merged3.treatment == 0, "ET"] = 0

    # Build stacked FEs (duplicate controls for each treated episode)
    dfgrouped_merged3["FE"] = np.nan
    dfgrouped_merged3.loc[dfgrouped_merged3.treatment == 0, "FE"] = 0
    dfgrouped_merged3_orig = dfgrouped_merged3.copy()
    treated_pcs = np.unique(dfgrouped_merged3_orig[dfgrouped_merged3_orig.treatment == 1]["PRODUCTCODE"])

    for i, PC in enumerate(treated_pcs):
        if i > 0:
            controls = dfgrouped_merged3_orig[dfgrouped_merged3_orig.treatment == 0].copy()
            controls["FE"] = i
            dfgrouped_merged3 = pd.concat([dfgrouped_merged3, controls], ignore_index=True)
        dfgrouped_merged3.loc[dfgrouped_merged3.PRODUCTCODE == PC, "FE"] = i

    dfgrouped_merged3["class_by_episode"] = (
        dfgrouped_merged3["FE"].astype(int).astype(str) + "[SEP]"
        + dfgrouped_merged3["factorized"].astype(str)
    )
    dfgrouped_merged3["class_by_episode"] = (
        dfgrouped_merged3.class_by_episode.astype("category").cat.codes
    )

    # Run standard event study via R (filter_country_ES_2_1 from preprocess.R)
    # Original notebook uses this function, NOT did_imputation_to_python.
    # filter_country_ES_2_1 fits: dates ~ i(ET, treatment, ref=-1) | factorized^FE + year^FE
    # with clustering on class_by_episode.
    r = robjects.r
    r["source"](str(config.R_SCRIPTS_DIR / "preprocess.R"))
    filter_country_ES_2_1 = robjects.globalenv["filter_country_ES_2_1"]

    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(dfgrouped_merged3)
    r("gc()")  # reclaim before estimating on rpy2-converted data (see estimation._to_r); no effect on results
    df_result_r = filter_country_ES_2_1(df_r, "dates")

    with localconverter(ro.default_converter + pandas2ri.converter):
        static = ro.conversion.rpy2py(df_result_r[0])
        ses = ro.conversion.rpy2py(df_result_r[1])

    window_low = 2
    window_high = 20

    index_int_low = int(-dfgrouped_merged3["ET"].min() - window_low)
    index_int_high = int(-dfgrouped_merged3["ET"].min() + window_high)

    static = static[index_int_low:index_int_high]
    ses = ses[index_int_low:index_int_high]

    estimates_df = pd.DataFrame()
    estimates_df["ET"] = np.arange(-window_low, window_high + 1, 1)
    static = np.insert(static, window_low - 1, 0)
    ses = np.insert(ses, window_low - 1, 0)
    estimates_df["Effect"] = static
    estimates_df["SE"] = ses.astype(float)

    df_didmultiple = estimates_df.copy()
    df_didmultiple.SE = df_didmultiple.SE.astype(float)

    # ----------------------------------------------------------------
    # In-text provenance (JPE 2.2): the recall paragraph states "The decline of
    # about 0.5 recalls per device-type-year represents roughly a 50 percent
    # reduction relative to the control mean." Neither the coefficients nor the
    # control mean were written anywhere, so the claim had no producing output.
    # Both are emitted here from exactly the estimating sample this figure uses.
    # ----------------------------------------------------------------
    emit_recall_in_text_numbers(df_didmultiple, dfgrouped_merged3, fda_deregs)

    # Pre and post trend lines (original has both, unlike DID imputation version)
    m, b = np.polyfit(
        df_didmultiple[df_didmultiple.ET < 0]["ET"],
        df_didmultiple[df_didmultiple.ET < 0]["Effect"], 1,
    )
    m2, b2 = np.polyfit(
        df_didmultiple[df_didmultiple.ET >= 0]["ET"],
        df_didmultiple[df_didmultiple.ET >= 0]["Effect"], 1,
    )

    style.use("seaborn-v0_8-poster")
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

    pre = df_didmultiple[df_didmultiple.ET < 0]
    post = df_didmultiple[df_didmultiple.ET >= 0]
    ax.plot(pre["ET"], m * pre["ET"] + b, "--", color=REG_LINE_C)
    ax.plot(post["ET"], m2 * post["ET"] + b2, "--", color=REG_LINE_C)

    eb = ax.errorbar(
        df_didmultiple["ET"], df_didmultiple["Effect"],
        yerr=1.96 * df_didmultiple["SE"], ls="none", elinewidth=1, ecolor="grey",
    )
    eb[-1][0].set_linestyle("--")
    ax.scatter(
        df_didmultiple["ET"], df_didmultiple["Effect"],
        facecolors="none", edgecolors=DOT_C, s=80, linewidth=3,
    )

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    plt.xlabel("Years Since Deregulation", fontsize=24)
    plt.ylabel("Change in Outcome", fontsize=24)
    ax.set_title("Device Recalls", fontsize=30, pad=30)
    plt.axvline(x=-0.5, ls="--", lw=1, color="black")
    plt.axhline(y=0, ls="--", lw=1, color="black")
    plt.xticks(np.arange(min(df_didmultiple["ET"]), max(df_didmultiple["ET"]) + 1, 2.0))
    plt.rc("xtick", labelsize=16)
    plt.rc("ytick", labelsize=16)

    output_path = config.FIGURES_DIR / "2_1_no_log_recalls_1996.png"
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close(fig)

    # ================================================================
    # Raw trend: 1996-era recalls (intuitive controls)
    # ================================================================
    logging.info("--- Recalls_1996_raw_trend_intuitive.png ---")
    df_intuitive = pd.read_csv(
        config.DERIVED_DATA_DIR / "intuitive_2_1_oct22_24.csv"
    )
    df_intuitive = df_intuitive[df_intuitive.year != 0]
    df_intuitive["treated"] = df_intuitive["treatment"]
    dfgrouped_intuitive = pd.merge(
        dfgrouped_filled[dfgrouped_filled.PRODUCTCODE.isin(df_intuitive["PRODUCTCODE"])],
        df_intuitive[["treated", "PRODUCTCODE", "year_reclassified"]].drop_duplicates("PRODUCTCODE"),
        how="left", on="PRODUCTCODE",
    )
    dfgrouped_intuitive["factorized"] = dfgrouped_intuitive.PRODUCTCODE.astype("category").cat.codes
    plot_raw_trends(dfgrouped_intuitive, "year", "treated", "dates",
                    "Recalls_1996_raw_trend_intuitive.png")

    logging.info("Recall analysis complete.")


if __name__ == "__main__":
    sys.exit(main())
