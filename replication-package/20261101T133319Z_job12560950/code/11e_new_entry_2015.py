#!/usr/bin/env python
"""
11e_new_entry_2015.py -- New entry analysis for the 2015 Cures Act (Figure D.16).

Examines new-firm patenting entry around the 2016 Cures Act deregulation
(Class II -> I). Constructs a panel of new-firm entry counts per product code,
matches treated PCs to controls using nearest-neighbor on pre-event firm-count
levels and trends, then estimates an event study via R (fixest).

Inputs:
    data/derived/Full_sample.csv
    data/derived/later_treated_2_1_oct22_24.csv
    data/raw/501k_all.csv
    r_scripts/did_ES.R

Outputs:
    output/figures/NewFirmsPatenting_2017.png
    output/tables/new_entry_2015_event_study.csv   (in-text: 2015 new-entry effects)
    output/tables/new_entry_2015_in_text.csv       (in-text: base 11.9, ~5 firms/yr, ~39%)
"""

import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors

from rpy2 import robjects
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from plotting import save_figure, setup_event_study_axes

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "11e_new_entry_2015.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Product code lists (from original New_Entry_2015.py)
# ============================================================================

PRODUCT_CODES_2_1 = [
    'CJN', 'CJR', 'CJX', 'CKB', 'CKE', 'CKH', 'JFH', 'KQN', 'CIF', 'CIQ',
    'CIS', 'CIT', 'JIS', 'JIT', 'JIW', 'JIX', 'MRV', 'PJT', 'CEX', 'CFE',
    'JGF', 'LPT', 'CEE', 'CDX', 'KLI', 'PFF', 'NSU', 'OOI', 'OTA', 'OUE',
    'OVA', 'PCA', 'PQQ', 'DKB', 'DLJ', 'DNN', 'GIE', 'JBT', 'GGC', 'GGN',
    'GIZ', 'OSL', 'JBZ', 'JBO', 'JBN', 'GFX', 'GIL', 'GII', 'JMH', 'KQF',
    'JCM', 'GHQ', 'GGF', 'GGQ', 'JPF', 'KRX', 'KRZ', 'KRY', 'KSA', 'GFS',
    'GGL', 'GGM', 'GJP', 'GJR', 'GLK', 'GLQ', 'JCN', 'JPK', 'NRF', 'NRS',
    'KSK', 'OUC', 'CHN', 'DCT', 'DCY', 'DDB', 'JFQ', 'JFR', 'DAM', 'DDT',
    'DDY', 'DEB', 'JZG', 'NZB', 'BSI', 'LLK', 'KLK', 'LPP', 'JAX', 'CCO',
    'BTI', 'DRC', 'OCR', 'DRZ', 'KRJ', 'DTL', 'DTW', 'DTS', 'DWD', 'EAT',
    'PME', 'EBE', 'EHR', 'EHS', 'EBP', 'ELM', 'EKO', 'ELS', 'KKO', 'EJI',
    'ETS', 'KLX', 'ETW', 'EPF', 'LZI', 'KHL', 'ETC', 'MCK', 'FCQ', 'FCR',
    'FCW', 'FGS', 'GCT', 'GCW', 'NTN', 'OCY', 'FCS', 'EZP', 'FHN', 'MND',
    'LQC', 'EZO', 'EXF', 'PIA', 'EZM', 'FAT', 'KNQ', 'KOE', 'NIH', 'FKI',
    'EXD', 'FGD', 'PLI', 'ERY', 'EYX', 'EYY', 'FNW', 'HMT', 'HMW', 'KGW',
    'FQP', 'FSQ', 'FSS', 'FSW', 'FSX', 'FSY', 'FSZ', 'FTA', 'FTD', 'FTG',
    'GBC', 'FZG', 'FZH', 'FZI', 'BWJ', 'MQX', 'DWL', 'GZM', 'GZO', 'HCJ',
    'GYE', 'OVP', 'NHM', 'HFL', 'HDA', 'HFW', 'HIB', 'HIC', 'NBZ', 'HDD',
    'HHP', 'KNC', 'OOA', 'HGZ', 'HHA', 'KND', 'HHE', 'HHL', 'MQJ', 'MMF',
    'PJZ', 'HMK', 'HLI', 'HLJ', 'MSG', 'HKL', 'HJM', 'MSR', 'HRO', 'FCT',
    'FSR', 'HPQ', 'HPM', 'HPO', 'HOZ', 'OJK', 'LBB', 'JDX', 'LZV', 'IKO',
    'ILJ', 'ILM', 'IMC', 'IMB', 'ISD', 'ILY', 'IRN', 'OIM', 'OIJ', 'IZS',
    'IZT', 'IZW', 'IZX', 'KPW', 'OII', 'OIK', 'IXL', 'OIO', 'OIP', 'OIL',
    'HBK', 'IXA', 'KPX', 'IZP', 'EGT', 'EGW', 'EGY', 'IXW', 'IXX', 'LMA',
    'NFH', 'LMC', 'NFI', 'OIN',
]

PARTIALLY_EXEMPT_CODES = [
    'PUX', 'PUY', 'PUZ', 'PVA', 'PVB', 'PVC', 'PVD', 'PVE', 'PVF', 'PVG',
    'PVH', 'PVI', 'PVJ', 'PVK', 'PUW', 'PUG', 'PTL', 'PTM', 'PUH', 'PTN',
    'PTO', 'PTP', 'PTQ', 'PTR', 'PTS', 'PTT', 'PTU', 'PTV', 'PTW', 'PUI',
    'PTX', 'PTY', 'PTZ', 'PUA', 'PUB', 'PUC', 'PUD', 'PUE', 'PUF',
]

CLASS_I_CODES = [
    'CFM', 'JIY', 'JIZ', 'JJA', 'JMO', 'JQD', 'JQE', 'JQF', 'JQG', 'CEO', 'JJR',
    'JJS', 'JJT', 'JJW', 'JJX', 'JJY', 'LCH', 'MJX', 'MJY', 'MJZ', 'MKA',
    'CDH', 'CDO', 'JHA', 'JHC', 'LFQ', 'DJZ', 'JKS', 'JKT', 'MKU', 'DIG',
    'DIH', 'DLI', 'DMR', 'DOH', 'DIE', 'DIF', 'DJK', 'DKC', 'DMP', 'LAS',
    'LAW', 'LAX', 'LAY', 'LAZ', 'LBA', 'JWR', 'KHF', 'LKS', 'EGI', 'EIB',
    'MNG', 'OVR', 'PRN', 'LZB', 'KZF', 'PEQ', 'KMJ', 'BRT', 'FMQ', 'OYS',
    'GWW', 'HCD', 'GYK', 'NUQ', 'NUR', 'HLD', 'HOG', 'HRF', 'HRG', 'HQS',
]

NON_EXEMPT_CODES = [
    'DKZ', 'DJP', 'DIT', 'DOD', 'DNI', 'DJL', 'DIS', 'DKN', 'DKX', 'DJN',
    'DLX', 'DMF', 'KZY', 'JXM', 'LAA', 'NFV', 'KZZ', 'LAB', 'DIO', 'KLN',
    'JXO', 'DLN', 'DMN', 'DIR', 'DIN', 'DOM', 'LAC', 'LAE', 'DLD', 'LAD',
    'DLB', 'DOL', 'LAF', 'DJC', 'LAG', 'NGG', 'DJR', 'DIW', 'DMB', 'DKR',
    'DNT', 'DPP', 'KXS', 'DNK', 'DOE', 'DJJ', 'DPK', 'DMY', 'DLR', 'DOK',
    'DIQ', 'DNA', 'DJG', 'DJF', 'DLT', 'LAI', 'DKT', 'LAH', 'JXN', 'DPN',
    'LAJ', 'LAK', 'LDJ', 'DKE', 'LAT', 'LFI', 'LFH', 'MLK', 'DHB', 'MRQ',
    'DQX', 'MAV', 'MNW', 'DTN', 'ETY', 'NAS', 'FCC', 'KGD', 'OCZ', 'GCA',
    'FJS', 'FKO', 'FKX', 'KKX', 'GAQ', 'PKQ', 'HEX', 'HDC', 'MQG', 'MQH',
    'MQK', 'HJO', 'MQU',
]


# ============================================================================
# In-text number emission (JPE Policy 2.2)
# ============================================================================

def emit_new_entry_in_text_numbers(estimates_df, baseline_mean, yr_treated):
    """Write the 2015-event new-entry event study and its two in-text magnitudes.

    output/tables/new_entry_2015_event_study.csv -- the per-year effects and
        standard errors plotted in the figure.
    output/tables/new_entry_2015_in_text.csv -- the derived magnitudes:
        new_entry_2015_baseline_firms_per_yr -- treated mean new-firm count in the
            event year's pre-period year (manuscript: base 11.9 entrants/yr)
        new_entry_2015_effect_2yr -- the event-study effect two years after the
            event year (manuscript footnote: "about five new firms per year")
        new_entry_2015_pct_2yr -- that effect as a percentage of the baseline
            (manuscript: "roughly 39% within two years")
    """
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    es_path = config.TABLES_DIR / "new_entry_2015_event_study.csv"
    estimates_df[["ET", "Effect", "SE"]].to_csv(es_path, index=False)
    logging.info(f"Saved 2015 new-entry event study: {es_path}")

    target_year = yr_treated + 2
    row = estimates_df[estimates_df.ET == target_year]
    eff = float(row["Effect"].iloc[0]) if len(row) else float("nan")
    se = float(row["SE"].iloc[0]) if len(row) else float("nan")
    pct = (eff / baseline_mean * 100.0) if baseline_mean else float("nan")

    rows = [
        {"metric": "new_entry_2015_baseline_firms_per_yr",
         "description": f"Treated mean new-firm count in {yr_treated - 1}, the pre-event year",
         "computed": round(float(baseline_mean), 4), "manuscript_value": 11.9},
        {"metric": "new_entry_2015_effect_2yr",
         "description": f"Event-study effect in {target_year} (two years after the event year)",
         "computed": round(eff, 4), "manuscript_value": 5.0},
        {"metric": "new_entry_2015_effect_2yr_se",
         "description": f"Standard error of the {target_year} effect",
         "computed": round(se, 4), "manuscript_value": ""},
        {"metric": "new_entry_2015_pct_2yr",
         "description": "Two-year effect as a percentage of the pre-event baseline",
         "computed": round(pct, 2), "manuscript_value": 39.0},
    ]
    out_path = config.TABLES_DIR / "new_entry_2015_in_text.csv"
    pd.DataFrame(rows, columns=["metric", "description", "computed",
                                "manuscript_value"]).to_csv(out_path, index=False)
    for r in rows:
        logging.info(f"  [2015 new entry] {r['metric']}: computed={r['computed']} "
                     f"(manuscript={r['manuscript_value']})")
    logging.info(f"Saved 2015 new-entry in-text numbers: {out_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting new entry 2015 analysis (Figure D.16)...")

    yr_treated = 2016

    # ---- Build control sample from later_treated_2_1 ----
    df_2_1_lt = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["later_treated_2_1"])
    df_2_1_lt["year_reclassified"] = 2016

    # Add partially exempt codes as controls
    df_temp = pd.DataFrame({
        "PRODUCTCODE": PARTIALLY_EXEMPT_CODES,
        "year_reclassified": 2016,
        "treatment": 0,
    })
    df_2_1_lt = pd.concat([df_2_1_lt, df_temp])
    df_2_1_lt = (
        df_2_1_lt[df_2_1_lt.treatment == 0]
        .drop_duplicates("PRODUCTCODE")[["PRODUCTCODE", "year_reclassified"]]
    )

    # Merge 510(k) submission counts
    k501s = pd.read_csv(config.RAW_DATA_DIR / "501k_all.csv", encoding="ISO-8859-1")
    k501s["year"] = pd.DatetimeIndex(k501s["DATERECEIVED"]).year
    k501s = k501s[["KNUMBER", "PRODUCTCODE", "APPLICANT", "DEVICENAME", "COUNTRY_CODE", "year"]]

    # Pre-event 10yr submissions
    pre_event = k501s[(k501s.year < 2016) & (k501s.year >= 2006)]
    pre_event["pre_event_10yr_submission_count"] = 1
    pre_event_group = pre_event.groupby("PRODUCTCODE").sum(numeric_only=True).reset_index()
    df_2_1_lt = df_2_1_lt.merge(
        pre_event_group[["PRODUCTCODE", "pre_event_10yr_submission_count"]], how="left",
    )

    # Pre-event any submissions
    pre_event_any = k501s[k501s.year < 2016]
    pre_event_any["pre_event_any_submission_count"] = 1
    pre_event_any_group = pre_event_any.groupby("PRODUCTCODE").sum(numeric_only=True).reset_index()
    df_2_1_lt = df_2_1_lt.merge(
        pre_event_any_group[["PRODUCTCODE", "pre_event_any_submission_count"]], how="left",
    )

    df_2_1_lt["pre_event_10yr_submission_count"] = df_2_1_lt["pre_event_10yr_submission_count"].fillna(0)
    df_2_1_lt["pre_event_any_submission_count"] = df_2_1_lt["pre_event_any_submission_count"].fillna(0)

    # Tag categories
    df_2_1_lt["two_to_one"] = df_2_1_lt.PRODUCTCODE.isin(PRODUCT_CODES_2_1).astype(int)
    df_2_1_lt["exempted_preone"] = df_2_1_lt.PRODUCTCODE.isin(CLASS_I_CODES).astype(int)
    df_2_1_lt["two_to_one_partial"] = df_2_1_lt.PRODUCTCODE.isin(PARTIALLY_EXEMPT_CODES).astype(int)
    df_2_1_lt["actually_non_exempt"] = df_2_1_lt.PRODUCTCODE.isin(NON_EXEMPT_CODES).astype(int)

    # Remove erroneously included PCs
    df_2_1_lt["erroneously_included"] = 0
    df_2_1_lt.loc[
        (df_2_1_lt.exempted_preone != 1)
        & (df_2_1_lt.actually_non_exempt != 1)
        & (df_2_1_lt.two_to_one_partial != 1)
        & (df_2_1_lt.two_to_one != 1),
        "erroneously_included",
    ] = 1
    df_2_1_lt = df_2_1_lt[df_2_1_lt.erroneously_included != 1]

    fda_deregs = df_2_1_lt.copy()
    logging.info(f"Control sample: {len(fda_deregs)} product codes.")

    # ---- Load full sample and tag treatment ----
    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.FULL_SAMPLE)
    all_pats["treated"] = 0
    all_pats.loc[all_pats.PRODUCTCODE.isin(fda_deregs.PRODUCTCODE), "treated"] = 1
    all_pats = all_pats[all_pats.year > 1975]

    from_stata = all_pats.copy()
    from_stata["firm_count"] = from_stata["patents_newfirmPC"]
    from_stata["factorized"] = pd.Categorical(from_stata["PRODUCTCODE"]).codes
    from_stata["treated_final"] = from_stata.groupby("factorized")["treated"].transform("max")
    from_stata["eventyear"] = from_stata["year"] - yr_treated

    logging.info(f"Full sample: {len(from_stata)} rows, "
                 f"{from_stata[from_stata.treated_final == 1].PRODUCTCODE.nunique()} treated PCs.")

    # ---- Nearest-neighbor matching on pre-event firm counts + slope ----
    df_filtered = from_stata[from_stata["year"].isin([2010, 2011, 2012, 2013, 2014])]

    slopes = {}
    for product_code in df_filtered["PRODUCTCODE"].unique():
        product_data = df_filtered[df_filtered["PRODUCTCODE"] == product_code]
        if len(product_data) == 5:
            X = product_data["year"].values.reshape(-1, 1)
            y = product_data["firm_count"].values
            reg = LinearRegression().fit(X, y)
            slopes[product_code] = reg.coef_[0]
        else:
            slopes[product_code] = np.nan

    df_filtered = df_filtered.copy()
    df_filtered["slope"] = df_filtered["PRODUCTCODE"].map(slopes)
    df_filtered = df_filtered.dropna(subset=["slope"])

    pivoted_df = df_filtered.pivot(index="PRODUCTCODE", columns="year", values="firm_count").reset_index()
    pivoted_df.columns = [str(c) for c in pivoted_df.columns]
    pivoted_df["slope"] = pivoted_df["PRODUCTCODE"].map(slopes)

    treated_pivoted = pivoted_df[
        pivoted_df["PRODUCTCODE"].isin(df_filtered[df_filtered["treated_final"] == 1]["PRODUCTCODE"])
    ]
    control_pivoted = pivoted_df[
        pivoted_df["PRODUCTCODE"].isin(df_filtered[df_filtered["treated_final"] == 0]["PRODUCTCODE"])
    ]

    matching_features = [col for col in treated_pivoted.columns if col not in ["PRODUCTCODE"]]
    nbrs = NearestNeighbors(n_neighbors=1, algorithm="ball_tree").fit(control_pivoted[matching_features])
    distances, indices = nbrs.kneighbors(treated_pivoted[matching_features])

    matched_control_indices = indices.flatten()
    matched_controls = control_pivoted.iloc[matched_control_indices]
    matched_productcodes = treated_pivoted["PRODUCTCODE"].tolist() + matched_controls["PRODUCTCODE"].tolist()
    from_stata = from_stata[from_stata["PRODUCTCODE"].isin(matched_productcodes)]

    logging.info(f"After matching: {len(from_stata)} rows, "
                 f"{from_stata[from_stata.treated_final == 1].PRODUCTCODE.nunique()} treated PCs.")

    # ---- Run event study via R ----
    r = robjects.r
    r["source"](str(config.R_SCRIPTS_DIR / "did_ES.R"))

    baseline_mean = from_stata[
        (from_stata.treated_final == 1) & (from_stata.year == 2015)
    ]["firm_count"].mean()
    logging.info(f"Baseline mean firm_count (treated, 2015): {baseline_mean:.3f}")

    didimputation_r = robjects.globalenv["event_study"]
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(
            from_stata[["firm_count", "treated_final", "factorized", "year", "eventyear"]]
        )
    r("gc()")  # reclaim before estimating on rpy2-converted data (see estimation._to_r); no effect on results
    df_result_r = didimputation_r(df_r, "firm_count")

    with localconverter(ro.default_converter + pandas2ri.converter):
        static = ro.conversion.rpy2py(df_result_r[0])
        ses = ro.conversion.rpy2py(df_result_r[1])
    logging.info(f"R event study returned {len(static)} estimates.")

    # ---- Build event-study DataFrame ----
    df_didmultiple = pd.DataFrame()
    df_didmultiple["Effect"] = np.concatenate([
        static[:yr_treated - 1977], np.array([0]), static[yr_treated - 1977:]
    ])
    df_didmultiple["SE"] = np.concatenate([
        ses[:yr_treated - 1977], np.array([0]), ses[yr_treated - 1977:]
    ])
    yrs_after = 2019 - yr_treated + 1
    df_didmultiple["ET"] = np.concatenate([
        np.arange(-1 * (yr_treated - 1976), -1, 1),
        np.array([-1]),
        np.arange(0, yrs_after, 1),
    ]) + yr_treated
    df_didmultiple = df_didmultiple[df_didmultiple.ET > 2011]

    # ---- In-text provenance (JPE 2.2) ----
    # The 2015-event paragraph states that new-entrant patenting "rises by roughly
    # 39% within two years (base 11.9 entrants/yr)", and its footnote that "the
    # 2015 event adds about five new firms per year relative to pre-event means".
    # Both magnitudes are emitted here, from exactly the estimates plotted, so each
    # is machine-readable.
    emit_new_entry_in_text_numbers(df_didmultiple, baseline_mean, yr_treated)

    # ---- Plot ----
    DOT_C = config.COLORS["dereg_dot"]

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))
    df_didmultiple.SE = df_didmultiple.SE.astype(float)

    eb = ax.errorbar(
        df_didmultiple["ET"], df_didmultiple["Effect"],
        yerr=1.96 * df_didmultiple["SE"], ls="none", elinewidth=1, ecolor="grey",
    )
    eb[-1][0].set_linestyle("--")
    ax.scatter(
        df_didmultiple["ET"], df_didmultiple["Effect"],
        facecolors="none", edgecolors=DOT_C, s=80, linewidth=3,
    )

    plt.xlabel("Year", fontsize=20)
    plt.ylabel("New Firms Patenting", fontsize=20)
    plt.axhline(y=0, ls="--", lw=1, color="black")
    plt.axvline(x=yr_treated - 0.5, ls="--", lw=2, color=DOT_C)
    plt.text(yr_treated - 0.75, 0.9, "Year Cures Act Passed", fontsize=12, rotation=90)

    plt.rc("xtick", labelsize=16)
    plt.rc("ytick", labelsize=16)

    output_path = config.FIGURES_DIR / "NewFirmsPatenting_2017.png"
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close(fig)

    logging.info("New entry 2015 analysis complete.")


if __name__ == "__main__":
    sys.exit(main())
