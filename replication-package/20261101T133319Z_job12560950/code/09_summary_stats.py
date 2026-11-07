#!/usr/bin/env python
"""
09_summary_stats.py -- Summary statistics tables.

Computes summary statistics for the full sample and matched samples,
then formats them as LaTeX tables. Reproduces:

  - Table 1 (Summary Statistics): aggregate statistics across all device
    classes, organized by data source (FDA admin data, patents, adverse
    events, claims).  Structure matches the paper's Table 1.

  - Table D.14 (Summary Statistics by FDA Class): the same statistics
    broken out by Class I, II, and III.  Structure matches the paper's
    Appendix Table D.14 (label: SummaryStatistics_AllClasses_Reorg).

Source: SummaryStats.py (original analysis notebook, 1518 lines).

Inputs:
    data/derived/Full_sample.csv
    data/derived/RegNum_Factorized_Synth.csv          (product-code-to-class crosswalk)
    data/derived/all_patents_w_xi_oct22_24.csv         (patent-level data with xi values)
    data/derived/adverse_event_panel_by_PC_full.csv    (adverse events by product code)
    data/derived/LBD_ApprovalTime_Both_oct22_24.csv    (firm regulatory proficiency)
    data/raw/501k_all.csv                              (510(k) submissions)
    data/raw/all_pma_approvals.txt                     (PMA submissions)
    data/raw/unique_devices_thr_75.csv                 (unique device count)
    data/raw/unique_firms_in_PC_thr_75.csv             (firms per product code)
    data/raw/unique_firms_thr_75.csv                   (unique entrant firms)
    data/raw/Adverse_fsize_ready_all4_oct22_24.csv     (adverse-event firm sizes)
    data/raw/KPSS_2019_public.csv                      (patent value data)
    data/raw/compustat_firm_data.csv                   (firm total assets from Compustat)
    data/raw/Applicant_Cites_Only.csv                  (forward citations per patent)
    data/derived/outpatient_combined_censored.csv       (MarketScan outpatient claims, proprietary)

Every input above is REQUIRED on both the restricted route and the simulated route: if any is
absent this module logs which ones, writes nothing, and exits non-zero. The single exception is
the MarketScan claims file behind Table 1 Panel III, which a replicator running neither official
route may omit deliberately by setting FDA_SKIP_MARKETSCAN_PANEL=1; the resulting Table 1 is then
knowingly incomplete and says so in the log.

Outputs:
    output/tables/Table_1_summary_stats.csv
    output/tables/Table_1_summary_stats.tex
    output/tables/Table_D14_summary_stats_by_class.csv
    output/tables/Table_D14_summary_stats_by_class.tex
"""

import os
import sys
import logging
import time
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "09_summary_stats.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Required-input contract (FAIL CLOSED)
# ============================================================================
# Every input below is required on BOTH routes -- the restricted real-data route and the
# simulated route (the simulator produces a counterpart for each of them, and
# synthetic_pipeline/materialize_simulation.py places it at the path this module reads).
# Missing required inputs are collected during the load phase and abort the module with a
# non-zero exit code BEFORE any table is written, so a degraded table cannot be produced or shipped.
#
# The one deliberately optional panel is Table 1 Panel III (MarketScan claims). It is required by
# default; a replicator who has no MarketScan licence and is running neither official route can
# set FDA_SKIP_MARKETSCAN_PANEL=1 to omit Panel III explicitly. That is logged loudly and is never
# the silent default.
SKIP_MARKETSCAN_ENV = "FDA_SKIP_MARKETSCAN_PANEL"

_MISSING_REQUIRED = []


def require_input(path, what):
    """Return True if a REQUIRED input exists; otherwise record it and return False.

    Recording (rather than raising on the first miss) lets the load phase report every missing
    input in one message instead of one per run.
    """
    if Path(path).exists():
        return True
    _MISSING_REQUIRED.append(f"{what} -- expected at: {path}")
    logging.error(f"  REQUIRED INPUT MISSING -- {what}: {path}")
    return False


def marketscan_panel_skipped():
    """True only when the replicator explicitly opted out of Table 1 Panel III."""
    return os.environ.get(SKIP_MARKETSCAN_ENV) == "1"


# ============================================================================
# Helper: describe a variable, returning mean, std, min, max, count
# ============================================================================

def describe_var(series):
    """Return dict with count, mean, std, min, max for a numeric Series."""
    s = series.dropna()
    return {
        "count": len(s),
        "mean": s.mean() if len(s) > 0 else np.nan,
        "std": s.std() if len(s) > 0 else np.nan,
        "min": s.min() if len(s) > 0 else np.nan,
        "max": s.max() if len(s) > 0 else np.nan,
    }


def describe_var_by_class(series_by_class):
    """
    Given a dict {class_label: Series}, return dict-of-dicts with stats per class.
    """
    result = {}
    for cls_label, series in series_by_class.items():
        result[cls_label] = describe_var(series)
    return result


# ============================================================================
# Data loaders
# ============================================================================

def load_synth_number():
    """Load and clean the product-code-to-class crosswalk."""
    synth_path = config.DERIVED_DATA_DIR / config.SOURCE_FILES["synth_number"]
    if not require_input(synth_path, "product-code-to-class crosswalk (every panel of "
                                     "Table 1 and Table D.14 is keyed on it)"):
        return None
    logging.info(f"  Loading synth_number from {synth_path}")
    synth_number = pd.read_csv(synth_path, dtype={"REGULATIONNUMBER": str})
    synth_number["REGULATIONNUMBER"] = (
        synth_number["REGULATIONNUMBER"].str.pad(width=8, side="right", fillchar="0")
    )
    synth_number = synth_number.drop_duplicates("PRODUCTCODE_x")
    synth_number["PRODUCTCODE"] = synth_number["PRODUCTCODE_x"]
    synth_number = synth_number[
        ["FDA_own_accord", "PRODUCTCODE", "Reg_Change_List",
         "use_case", "REGULATIONNUMBER", "DEVICECLASS", "SUBMISSION_TYPE_ID"]
    ]
    logging.info(f"    synth_number: {len(synth_number):,} product codes")
    return synth_number


def load_fda_submissions():
    """Load 510(k) and PMA submission data."""
    k501_path = config.RAW_DATA_DIR / "501k_all.csv"
    pma_path = config.RAW_DATA_DIR / "all_pma_approvals.txt"

    ok = require_input(k501_path, "510(k) submissions (Table 1 / D.14 Panel I)")
    ok = require_input(pma_path, "PMA approvals (Table 1 / D.14 Panel I)") and ok
    if not ok:
        return None

    logging.info(f"  Loading 510(k) data from {k501_path}")
    k501s = pd.read_csv(k501_path, encoding="ISO-8859-1")
    k501s["year"] = pd.DatetimeIndex(k501s["DATERECEIVED"]).year
    k501s = k501s[["KNUMBER", "PRODUCTCODE", "APPLICANT", "DEVICENAME", "year"]]
    logging.info(f"    510(k) submissions: {len(k501s):,}")

    logging.info(f"  Loading PMA data from {pma_path}")
    pmas = pd.read_csv(pma_path, encoding="ISO-8859-1", on_bad_lines="skip", sep="|")
    pmas["year"] = pd.DatetimeIndex(pmas["DATERECEIVED"]).year
    # Keep original PMAs and Panel Track supplements only
    pmas = pmas[
        (pmas.SUPPLEMENTTYPE == "Panel Track")
        | (pmas.SUPPLEMENTREASON.isnull())
        | (pmas.SUPPLEMENTREASON == "Change Design/Components/Specifications/Material")
    ]
    pmas = pmas[["PMANUMBER", "PRODUCTCODE", "APPLICANT", "TRADENAME", "year"]]
    pmas["DEVICENAME"] = pmas["TRADENAME"]
    logging.info(f"    PMA submissions (filtered): {len(pmas):,}")

    concatenated = pd.concat([k501s, pmas], ignore_index=True)
    logging.info(f"    Combined submissions: {len(concatenated):,}")
    return concatenated


def load_patent_data(synth_number):
    """
    Load patent-level data with citations and patent values (xi),
    mirroring the original SummaryStats.py pipeline.
    """
    # Patent-to-device-type mapping with GRID dummies
    all_pats_path = config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"]
    if not require_input(all_pats_path, "patent panel with market values "
                                        "(Table 1 / D.14 Panel II)"):
        return None, None, None
    logging.info(f"  Loading patent data from {all_pats_path}")
    all_pats = pd.read_csv(all_pats_path)
    all_pats = pd.merge(
        all_pats, synth_number[["PRODUCTCODE", "DEVICECLASS"]], how="left"
    )
    logging.info(f"    Patents loaded: {len(all_pats):,}")

    # Extract patent numbers for merging with xi data
    all_pats["USID"] = all_pats["id"].str.split("-").str[1].astype(str)

    # Forward citations
    cites_path = config.RAW_DATA_DIR / "Applicant_Cites_Only.csv"
    if require_input(cites_path, "forward citations per patent (Table 1 / D.14 "
                                 "'Citations per Patent')"):
        logging.info(f"  Loading citations from {cites_path}")
        applicant_cites = pd.read_csv(cites_path)
        applicant_cites["USID"] = applicant_cites["USID"].astype(str)
        applicant_cites = applicant_cites.drop_duplicates("USID")
        all_pats_cites = pd.merge(
            all_pats, applicant_cites[["USID", "times_cited"]],
            on="USID", how="left"
        )
        logging.info(f"    Patents with citations: {all_pats_cites['times_cited'].notna().sum():,}")
    else:
        all_pats_cites = all_pats.copy()
        all_pats_cites["times_cited"] = np.nan

    # Patent values (xi_real) and firm size (firm_size) are already pre-merged
    # in all_patents_w_xi_oct22_24.csv from the original analysis pipeline.
    # Use these directly rather than re-merging from raw KPSS/Compustat,
    # which causes column collisions (xi_real_x/xi_real_y).
    all_pats_forxi = all_pats.copy()
    if "xi_real" not in all_pats_forxi.columns:
        all_pats_forxi["xi_real"] = np.nan
    if "firm_size" not in all_pats_forxi.columns:
        all_pats_forxi["firm_size"] = np.nan
    logging.info(f"    Patents with xi values: {all_pats_forxi['xi_real'].notna().sum():,}")
    logging.info(f"    Patents with firm size: {all_pats_forxi['firm_size'].notna().sum():,}")

    return all_pats, all_pats_cites, all_pats_forxi


def load_adverse_event_data(synth_number):
    """Load adverse event panel data."""
    ae_path = config.DERIVED_DATA_DIR / "adverse_event_panel_by_PC_full.csv"
    if not ae_path.exists():
        # Try raw data dir
        ae_path = config.RAW_DATA_DIR / "adverse_event_panel_by_PC_full.csv"
    if not require_input(ae_path, "adverse-event panel by product code "
                                  "(Table 1 / D.14 Panel 'Adverse Events')"):
        return None

    logging.info(f"  Loading adverse event data from {ae_path}")
    df_ae = pd.read_csv(ae_path)
    df_ae["v_serious"] = df_ae["L"] + df_ae["H"] + df_ae["D"] + df_ae["S"]
    logging.info(f"    Adverse event records: {len(df_ae):,}")
    return df_ae


def load_device_market_data():
    """Load unique devices, firms per PC, and total entrant firms."""
    unique_dev_path = config.RAW_DATA_DIR / "unique_devices_thr_75.csv"
    firm_entrant_path = config.RAW_DATA_DIR / "unique_firms_in_PC_thr_75.csv"
    total_firm_path = config.RAW_DATA_DIR / "unique_firms_thr_75.csv"

    results = {}
    if require_input(unique_dev_path, "unique devices per product code "
                                      "(Table 1 / D.14 'Devices per Product Code')"):
        logging.info(f"  Loading unique devices from {unique_dev_path}")
        unique_dev = pd.read_csv(unique_dev_path)
        unique_dev["dev_count"] = 1
        unique_dev = unique_dev[["PRODUCTCODE", "year", "dev_count"]]
        results["unique_dev"] = unique_dev
    else:
        results["unique_dev"] = None

    if require_input(firm_entrant_path, "unique firms per product code "
                                        "(Table 1 / D.14 'Firms per Product Code')"):
        logging.info(f"  Loading firm entrants from {firm_entrant_path}")
        firm_entrant = pd.read_csv(firm_entrant_path)
        firm_entrant["firm_count"] = 1
        firm_entrant = firm_entrant[["PRODUCTCODE", "year", "firm_count"]]
        results["firm_entrant"] = firm_entrant
    else:
        results["firm_entrant"] = None

    if require_input(total_firm_path, "total entrant firms "
                                      "(Table 1 / D.14 'Entrant Firms')"):
        logging.info(f"  Loading total entrant firms from {total_firm_path}")
        total_firm = pd.read_csv(total_firm_path)
        total_firm["absnew_firm_count"] = 1
        total_firm = total_firm[["PRODUCTCODE", "year", "absnew_firm_count"]]
        results["total_firm_entrant"] = total_firm
    else:
        results["total_firm_entrant"] = None

    return results


def load_regulatory_proficiency(synth_number):
    """Load firm regulatory proficiency (learning-by-doing) data."""
    lbd_path = config.DERIVED_DATA_DIR / "LBD_ApprovalTime_Both_oct22_24.csv"
    if not lbd_path.exists():
        lbd_path = config.RAW_DATA_DIR / "LBD_ApprovalTime_Both_oct22_24.csv"

    if require_input(lbd_path, "firm regulatory proficiency / learning-by-doing panel "
                               "(Table 1 / D.14 'Regulatory Proficiency')"):
        logging.info(f"  Loading regulatory proficiency data from {lbd_path}")
        lbd = pd.read_csv(lbd_path)
        lbd["dev_count_lbd"] = 1
        lbd["PRODUCTCODE"] = lbd["PRODUCTCODE"].str.upper()
        lbd = lbd[lbd.cumsum_time_t1.notnull()]
        lbd = pd.merge(
            lbd, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )
        logging.info(f"    LBD records: {len(lbd):,}")
        return lbd
    return None


def load_adverse_firm_sizes(synth_number):
    """Load adverse event firm size data."""
    fsize_path = config.RAW_DATA_DIR / "Adverse_fsize_ready_all4_oct22_24.csv"
    if not fsize_path.exists():
        fsize_path = config.DERIVED_DATA_DIR / "Adverse_fsize_ready_all4_oct22_24.csv"

    if require_input(fsize_path, "adverse-event firm sizes "
                                 "(Table 1 / D.14 'Firm Size | Adverse Event')"):
        logging.info(f"  Loading adverse-event firm sizes from {fsize_path}")
        w_fsize = pd.read_csv(fsize_path)
        w_fsize = pd.merge(
            w_fsize, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )
        logging.info(f"    Adverse firm size records: {len(w_fsize):,}")
        return w_fsize
    return None


def load_claims_data():
    """
    Load MarketScan outpatient claims data for Panel III summary statistics.

    Uses only the outpatient file, consistent with the price analysis
    (05_price_analysis.py) where the inpatient merge was overridden.

    The underlying MarketScan data are proprietary, but BOTH official routes supply this file:
    the restricted route uses the provider-produced aggregate extract, and the simulated route
    materializes the simulator's counterpart. It is therefore REQUIRED by default. A replicator
    running neither official route, and who therefore cannot produce Panel III at all, must opt
    out explicitly with FDA_SKIP_MARKETSCAN_PANEL=1; that omission is logged, and Table 1 is then
    knowingly produced without Panel III. There is no silent skip.
    """
    outpatient_path = config.DERIVED_DATA_DIR / "outpatient_combined_censored.csv"
    if marketscan_panel_skipped():
        # Printed as well as logged: this banner is the only thing that distinguishes an
        # exit 0 with an incomplete Table 1 from a complete reproduction. run_all.py scrubs
        # this variable from every step it launches, so reaching here means the script was
        # invoked directly with the opt-out set.
        banner = (
            "=" * 70 + "\n"
            f"{SKIP_MARKETSCAN_ENV}=1 -- OMITTING Table 1 Panel III (MarketScan claims) at the "
            "replicator's explicit request.\nThe resulting Table 1 is incomplete and does not "
            "match the deposited reference table.\n" + "=" * 70
        )
        print(banner, flush=True)
        logging.warning(banner)
        return None
    if not require_input(outpatient_path, "MarketScan outpatient claims aggregate "
                                          "(Table 1 Panel III). Set "
                                          f"{SKIP_MARKETSCAN_ENV}=1 to omit Panel III on purpose"):
        return None

    logging.info(f"  Loading MarketScan outpatient data from {outpatient_path}")
    df = pd.read_csv(outpatient_path)
    # BilledAmt = average billed amount per procedure in each proc-year cell
    df["BilledAmt"] = df["pay"] / df["proc_count"]
    logging.info(f"    Outpatient rows: {len(df):,}")
    logging.info(f"    Total procedures: {df['proc_count'].sum():,.0f}")
    logging.info(f"    Unique procedure codes: {df['proc1'].nunique():,}")
    return df


# ============================================================================
# Table 1: Aggregate summary statistics
# ============================================================================

def compute_table1(submissions, synth_number, all_pats, all_pats_cites,
                   all_pats_forxi, df_ae, market_data, lbd_df, w_fsize,
                   claims_df=None):
    """
    Compute Table 1 aggregate summary statistics.

    Returns a list of dicts, each representing a row in the table.
    """
    rows = []

    # --- Panel I: FDA Administrative Data ---
    # A. PMA/510(k) Submissions
    concat_merge = pd.merge(
        submissions, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
        on="PRODUCTCODE", how="left"
    )
    total_submissions = len(submissions)
    n_device_types_sub = submissions["PRODUCTCODE"].nunique()

    # Submissions per device type
    temp_fda = submissions.groupby("PRODUCTCODE").size().reset_index(name="sub_count")
    sub_per_dt = describe_var(temp_fda["sub_count"])

    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "A. PMA/510(k) Submissions",
        "variable": "Total Submissions",
        "N": total_submissions,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })
    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "A. PMA/510(k) Submissions",
        "variable": "Number of Device Types",
        "N": n_device_types_sub,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })
    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "A. PMA/510(k) Submissions",
        "variable": "Submissions per Device Type",
        "N": np.nan,
        "mean": sub_per_dt["mean"],
        "std": sub_per_dt["std"],
        "min": sub_per_dt["min"],
        "max": sub_per_dt["max"],
    })

    # Total submitting firms
    if market_data.get("total_firm_entrant") is not None:
        total_firms = int(market_data["total_firm_entrant"]["absnew_firm_count"].sum())
    else:
        total_firms = np.nan

    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "A. PMA/510(k) Submissions",
        "variable": "Total Submitting Firms",
        "N": total_firms,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })

    # Firms per device type
    if market_data.get("firm_entrant") is not None:
        firms_per_dt = (
            market_data["firm_entrant"]
            .groupby("PRODUCTCODE")["firm_count"]
            .sum()
            .reset_index()
        )
        fpdt = describe_var(firms_per_dt["firm_count"])
        rows.append({
            "panel": "I. FDA Administrative Data",
            "subpanel": "A. PMA/510(k) Submissions",
            "variable": "Firms per Device Type",
            "N": fpdt["count"],
            "mean": fpdt["mean"], "std": fpdt["std"],
            "min": fpdt["min"], "max": fpdt["max"],
        })

    # Firm regulatory proficiency
    if lbd_df is not None:
        lbd_stats = describe_var(lbd_df["cumsum_time_t1"] / 365.0)
        n_pc_lbd = lbd_df.groupby("PRODUCTCODE").size().reset_index()
        rows.append({
            "panel": "I. FDA Administrative Data",
            "subpanel": "A. PMA/510(k) Submissions",
            "variable": "Firm Regulatory Proficiency (years)",
            "N": lbd_stats["count"],
            "mean": lbd_stats["mean"], "std": lbd_stats["std"],
            "min": lbd_stats["min"], "max": lbd_stats["max"],
        })

    # B. Adverse Event Reports
    ae_total = int(df_ae["event_count"].sum()) if "event_count" in df_ae.columns else len(df_ae)
    n_dt_ae = df_ae["PRODUCTCODE"].nunique()
    temp_ae = df_ae.groupby("PRODUCTCODE")["event_count"].sum().reset_index()
    ae_per_dt = describe_var(temp_ae["event_count"])

    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "B. Adverse Event Reports",
        "variable": "Total Adverse Event Reports",
        "N": ae_total,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })
    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "B. Adverse Event Reports",
        "variable": "Number of Device Types Reporting",
        "N": n_dt_ae,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })
    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "B. Adverse Event Reports",
        "variable": "Adverse Events per Device Type",
        "N": np.nan,
        "mean": ae_per_dt["mean"], "std": ae_per_dt["std"],
        "min": ae_per_dt["min"], "max": ae_per_dt["max"],
    })

    # Serious events per device type
    temp_ae_serious = (
        df_ae[df_ae.v_serious > 0]
        .groupby("PRODUCTCODE")["v_serious"]
        .sum()
        .reset_index()
    )
    serious_per_dt = describe_var(temp_ae_serious["v_serious"])
    rows.append({
        "panel": "I. FDA Administrative Data",
        "subpanel": "B. Adverse Event Reports",
        "variable": "Serious Events per Device Type",
        "N": serious_per_dt["count"],
        "mean": serious_per_dt["mean"], "std": serious_per_dt["std"],
        "min": serious_per_dt["min"], "max": serious_per_dt["max"],
    })

    # Assets of offending firms
    if w_fsize is not None:
        fsize_stats = describe_var(w_fsize["firm_size"])
        rows.append({
            "panel": "I. FDA Administrative Data",
            "subpanel": "B. Adverse Event Reports",
            "variable": "Assets of Offending Firms",
            "N": fsize_stats["count"],
            "mean": fsize_stats["mean"], "std": fsize_stats["std"],
            "min": fsize_stats["min"], "max": fsize_stats["max"],
        })

    # --- Panel II: Dimensions Device Patents ---
    n_total_pats = len(all_pats)
    n_dt_pats = all_pats["PRODUCTCODE"].nunique()

    # Patents per device type
    pats_per_dt = (
        all_pats.groupby("PRODUCTCODE").size().reset_index(name="pat_count")
    )
    ppdt = describe_var(pats_per_dt["pat_count"])

    rows.append({
        "panel": "II. Dimensions Device Patents",
        "subpanel": "",
        "variable": "Total Patents",
        "N": n_total_pats,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })
    rows.append({
        "panel": "II. Dimensions Device Patents",
        "subpanel": "",
        "variable": "Number of Device Types",
        "N": n_dt_pats,
        "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
    })
    rows.append({
        "panel": "II. Dimensions Device Patents",
        "subpanel": "",
        "variable": "Patents per Device Type",
        "N": np.nan,
        "mean": ppdt["mean"], "std": ppdt["std"],
        "min": ppdt["min"], "max": ppdt["max"],
    })

    # Citations per patent
    cite_stats = describe_var(all_pats_cites["times_cited"])
    rows.append({
        "panel": "II. Dimensions Device Patents",
        "subpanel": "",
        "variable": "Citations per Patent",
        "N": cite_stats["count"],
        "mean": cite_stats["mean"], "std": cite_stats["std"],
        "min": cite_stats["min"], "max": cite_stats["max"],
    })

    # Patent market valuation (xi_real)
    xi_stats = describe_var(all_pats_forxi["xi_real"])
    rows.append({
        "panel": "II. Dimensions Device Patents",
        "subpanel": "",
        "variable": "Patent Market Valuation",
        "N": xi_stats["count"],
        "mean": xi_stats["mean"], "std": xi_stats["std"],
        "min": xi_stats["min"], "max": xi_stats["max"],
    })

    # Applicant assets (firm_size)
    fsize_pat_stats = describe_var(all_pats_forxi["firm_size"])
    rows.append({
        "panel": "II. Dimensions Device Patents",
        "subpanel": "",
        "variable": "Applicant Assets",
        "N": fsize_pat_stats["count"],
        "mean": fsize_pat_stats["mean"], "std": fsize_pat_stats["std"],
        "min": fsize_pat_stats["min"], "max": fsize_pat_stats["max"],
    })

    # --- Panel III: MarketScan Claims Data ---
    if claims_df is not None:
        total_procedures = int(claims_df["proc_count"].sum())

        # Number of procedure codes
        n_proc_codes = claims_df["proc1"].nunique()

        # Procedures per code: total proc_count summed across years for each code
        procs_per_code = claims_df.groupby("proc1")["proc_count"].sum()
        ppc_stats = describe_var(procs_per_code)

        # Price per procedure-year: BilledAmt = pay / proc_count, filtered to > 0
        price_data = claims_df[claims_df["BilledAmt"] > 0].copy()
        price_stats = describe_var(price_data["BilledAmt"])

        panel_header = f"III. MarketScan Claims Data (N = {total_procedures / 1e9:.1f}B procedures)"
        rows.append({
            "panel": panel_header,
            "subpanel": "",
            "variable": "Number of Procedure Codes",
            "N": n_proc_codes,
            "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
        })
        rows.append({
            "panel": panel_header,
            "subpanel": "",
            "variable": "Procedures per Code",
            "N": np.nan,
            "mean": ppc_stats["mean"], "std": ppc_stats["std"],
            "min": ppc_stats["min"], "max": ppc_stats["max"],
        })
        rows.append({
            "panel": panel_header,
            "subpanel": "",
            "variable": "Price per Procedure-Year",
            "N": price_stats["count"],
            "mean": price_stats["mean"], "std": price_stats["std"],
            "min": price_stats["min"], "max": price_stats["max"],
        })
    else:
        logging.info("  Skipping Panel III (MarketScan claims data not available).")

    return pd.DataFrame(rows)


# ============================================================================
# Table D.14: Summary statistics by FDA class
# ============================================================================

def compute_table_d14(submissions, synth_number, all_pats, all_pats_cites,
                      all_pats_forxi, df_ae, market_data, lbd_df, w_fsize):
    """
    Compute Table D.14 (Summary Statistics by FDA Class).

    Returns a DataFrame with statistics broken out by Class I, II, III.
    """
    classes = ["1", "2", "3"]
    class_labels = {"1": "Class I", "2": "Class II", "3": "Class III"}
    rows = []

    # Merge submissions with class info
    concat_merge = pd.merge(
        submissions, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
        on="PRODUCTCODE", how="left"
    )

    # --- Panel A: FDA Administrative Data ---

    # Device submissions by class
    for cls in classes:
        cls_sub = concat_merge[concat_merge.DEVICECLASS == cls]
        total_n = len(cls_sub)
        n_dt = cls_sub["PRODUCTCODE"].nunique()

        # Submissions per device type
        temp = cls_sub.groupby("PRODUCTCODE").size().reset_index(name="sub_count")
        sub_stats = describe_var(temp["sub_count"])

        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Device submissions",
            "variable": "Total submissions (N)",
            "class": class_labels[cls],
            "value": total_n,
            "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
        })
        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Device submissions",
            "variable": "Number of device types (N)",
            "class": class_labels[cls],
            "value": n_dt,
            "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
        })
        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Device submissions",
            "variable": "Submissions per device type",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": sub_stats["mean"], "std": sub_stats["std"],
            "min": sub_stats["min"], "max": sub_stats["max"],
        })

    # Total submitting firms by class
    if market_data.get("total_firm_entrant") is not None:
        fe_copy = market_data["total_firm_entrant"].copy()
        fe_copy["PRODUCTCODE"] = fe_copy["PRODUCTCODE"].str.upper()
        fe_w_class = pd.merge(
            fe_copy, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )
        for cls in classes:
            total_firms_cls = int(
                fe_w_class[fe_w_class.DEVICECLASS == cls]["absnew_firm_count"].sum()
            )
            rows.append({
                "panel": "A. FDA Administrative Data",
                "section": "Device submissions",
                "variable": "Total submitting firms (N)",
                "class": class_labels[cls],
                "value": total_firms_cls,
                "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
            })

    # Firms per device type by class
    if market_data.get("firm_entrant") is not None:
        fe_dt = market_data["firm_entrant"].groupby("PRODUCTCODE")["firm_count"].sum().reset_index()
        fe_dt["PRODUCTCODE"] = fe_dt["PRODUCTCODE"].str.upper()
        fe_dt = pd.merge(
            fe_dt, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )
        for cls in classes:
            temp = fe_dt[fe_dt.DEVICECLASS == cls]
            fpdt_stats = describe_var(temp["firm_count"])
            rows.append({
                "panel": "A. FDA Administrative Data",
                "section": "Device submissions",
                "variable": "Firms per device type",
                "class": class_labels[cls],
                "value": np.nan,
                "mean": fpdt_stats["mean"], "std": fpdt_stats["std"],
                "min": fpdt_stats["min"], "max": fpdt_stats["max"],
            })

    # Firm regulatory proficiency by class
    if lbd_df is not None:
        for cls in classes:
            temp = lbd_df[lbd_df.DEVICECLASS == cls]
            lbd_stats = describe_var(temp["cumsum_time_t1"] / 365.0)
            rows.append({
                "panel": "A. FDA Administrative Data",
                "section": "Device submissions",
                "variable": "Firm regulatory proficiency (years)",
                "class": class_labels[cls],
                "value": np.nan,
                "mean": lbd_stats["mean"], "std": lbd_stats["std"],
                "min": lbd_stats["min"], "max": lbd_stats["max"],
            })

    # Adverse event reports by class
    ae_merge = pd.merge(
        df_ae, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
        on="PRODUCTCODE", how="left"
    )
    for cls in classes:
        cls_ae = ae_merge[ae_merge.DEVICECLASS == cls]
        total_ae = int(cls_ae["event_count"].sum()) if "event_count" in cls_ae.columns else len(cls_ae)
        n_dt_ae = cls_ae["PRODUCTCODE"].nunique()

        # AERs per device type
        temp = cls_ae.groupby("PRODUCTCODE")["event_count"].sum().reset_index()
        ae_stats = describe_var(temp["event_count"])

        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Adverse event reports",
            "variable": "Total AERs (N)",
            "class": class_labels[cls],
            "value": total_ae,
            "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
        })
        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Adverse event reports",
            "variable": "Device types reporting (N)",
            "class": class_labels[cls],
            "value": n_dt_ae,
            "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
        })
        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Adverse event reports",
            "variable": "Adverse events per device type",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": ae_stats["mean"], "std": ae_stats["std"],
            "min": ae_stats["min"], "max": ae_stats["max"],
        })

        # Serious events per device type
        temp_serious = (
            cls_ae[cls_ae.v_serious > 0]
            .groupby("PRODUCTCODE")["v_serious"]
            .sum()
            .reset_index()
        )
        serious_stats = describe_var(temp_serious["v_serious"])
        rows.append({
            "panel": "A. FDA Administrative Data",
            "section": "Adverse event reports",
            "variable": "Serious events per device type",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": serious_stats["mean"], "std": serious_stats["std"],
            "min": serious_stats["min"], "max": serious_stats["max"],
        })

    # AERs with matched firm assets by class
    if w_fsize is not None:
        for cls in classes:
            cls_fsize = w_fsize[w_fsize.DEVICECLASS == cls]
            n_matched = len(cls_fsize)
            fsize_stats = describe_var(cls_fsize["firm_size"])
            rows.append({
                "panel": "A. FDA Administrative Data",
                "section": "Adverse event reports",
                "variable": "AERs with matched firm assets (N)",
                "class": class_labels[cls],
                "value": n_matched,
                "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
            })
            rows.append({
                "panel": "A. FDA Administrative Data",
                "section": "Adverse event reports",
                "variable": "Assets of offending firms",
                "class": class_labels[cls],
                "value": np.nan,
                "mean": fsize_stats["mean"], "std": fsize_stats["std"],
                "min": fsize_stats["min"], "max": fsize_stats["max"],
            })

    # --- Panel B: Dimensions Device Patents ---
    # Group patents by class
    pats_w_class = all_pats.copy()
    if "DEVICECLASS" not in pats_w_class.columns:
        pats_w_class = pd.merge(
            pats_w_class, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )

    pats_cites_w_class = all_pats_cites.copy()
    if "DEVICECLASS" not in pats_cites_w_class.columns:
        pats_cites_w_class = pd.merge(
            pats_cites_w_class, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )

    pats_xi_w_class = all_pats_forxi.copy()
    if "DEVICECLASS" not in pats_xi_w_class.columns:
        pats_xi_w_class = pd.merge(
            pats_xi_w_class, synth_number[["PRODUCTCODE", "DEVICECLASS"]],
            on="PRODUCTCODE", how="left"
        )

    for cls in classes:
        cls_pats = pats_w_class[pats_w_class.DEVICECLASS == cls]
        n_pats = len(cls_pats)

        # Patents per device type
        pats_per_dt = cls_pats.groupby("PRODUCTCODE").size().reset_index(name="count")
        ppdt_stats = describe_var(pats_per_dt["count"])

        rows.append({
            "panel": "B. Dimensions Device Patents",
            "section": "",
            "variable": "Total patents (N)",
            "class": class_labels[cls],
            "value": n_pats,
            "mean": np.nan, "std": np.nan, "min": np.nan, "max": np.nan,
        })
        rows.append({
            "panel": "B. Dimensions Device Patents",
            "section": "",
            "variable": "Patents per device type",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": ppdt_stats["mean"], "std": ppdt_stats["std"],
            "min": ppdt_stats["min"], "max": ppdt_stats["max"],
        })

        # Citations per patent
        cls_cites = pats_cites_w_class[pats_cites_w_class.DEVICECLASS == cls]
        cite_stats = describe_var(cls_cites["times_cited"])
        rows.append({
            "panel": "B. Dimensions Device Patents",
            "section": "",
            "variable": "Citations per patent",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": cite_stats["mean"], "std": cite_stats["std"],
            "min": cite_stats["min"], "max": cite_stats["max"],
        })

        # Patent market valuation
        cls_xi = pats_xi_w_class[pats_xi_w_class.DEVICECLASS == cls]
        cls_xi_nn = cls_xi[cls_xi.xi_real.notnull()]
        xi_stats = describe_var(cls_xi_nn["xi_real"])
        rows.append({
            "panel": "B. Dimensions Device Patents",
            "section": "",
            "variable": "Patent market valuation",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": xi_stats["mean"], "std": xi_stats["std"],
            "min": xi_stats["min"], "max": xi_stats["max"],
        })

        # Applicant assets
        cls_fsize = cls_xi[cls_xi.firm_size.notnull()]
        fsize_stats = describe_var(cls_fsize["firm_size"])
        rows.append({
            "panel": "B. Dimensions Device Patents",
            "section": "",
            "variable": "Applicant assets",
            "class": class_labels[cls],
            "value": np.nan,
            "mean": fsize_stats["mean"], "std": fsize_stats["std"],
            "min": fsize_stats["min"], "max": fsize_stats["max"],
        })

    return pd.DataFrame(rows)


# ============================================================================
# LaTeX formatters
# ============================================================================

def fmt_number(x, prefix="", suffix="", decimals=1, large_number=False):
    """Format a number for the LaTeX table with optional prefix/suffix."""
    if pd.isna(x):
        return "-"
    if large_number:
        return f"{prefix}{x:,.0f}{suffix}"
    return f"{prefix}{x:,.{decimals}f}{suffix}"


def _fmt_int(x):
    """Format as integer with commas, or '-' if NaN."""
    if pd.isna(x):
        return "-"
    return f"{x:,.0f}"


def _fmt_dollars(x):
    """Format dollar amount in millions with human-readable magnitude suffix.

    Input is in MILLIONS for Assets/Valuation rows.
    Uses adaptive decimal places to match manuscript conventions:
      < $1K     → $NN  (plain dollars)
      $1K-$1M   → $NNK  (no decimals)
      $1M-$1B   → $NN.NM  (1 decimal)
      $1B-$1T   → $N.NNB or $NN.NB  (2 dec if <10B, else 1 dec)
      $1T+      → $N.NT  (1 decimal)
    """
    if pd.isna(x):
        return "-"
    # x is in millions
    abs_x = abs(x)
    sign = "-" if x < 0 else ""
    if abs_x < 0.001:
        # sub-thousand: show as plain dollars
        val = abs_x * 1e6
        return f"\\${sign}{val:,.0f}" if val >= 1 else f"\\${sign}{val:.1f}"
    if abs_x < 1:
        # thousands
        val = abs_x * 1000
        return f"\\${sign}{val:,.0f}K"
    if abs_x < 1000:
        # millions
        return f"\\${sign}{abs_x:,.1f}M"
    if abs_x < 1_000_000:
        # billions — 2 decimals for <10B, 1 decimal for >=10B
        val = abs_x / 1000
        dec = 1 if val >= 10 else 2
        return f"\\${sign}{val:,.{dec}f}B"
    # trillions
    val = abs_x / 1_000_000
    return f"\\${sign}{val:,.1f}T"


def _fmt_magnitude(x, decimals=1):
    """Format a large count with M/B suffix (no dollar sign)."""
    if pd.isna(x):
        return "-"
    abs_x = abs(x)
    if abs_x >= 1e9:
        return f"{x / 1e9:,.{decimals}f}B"
    if abs_x >= 1e6:
        return f"{x / 1e6:,.{decimals}f}M"
    return f"{x:,.{decimals}f}"


def public_patent_share(df_stats):
    """Percent of patents filed by publicly traded firms: patents carrying a Kogan et al. (2017) market value
    over all patents, from Table 1's own counts (JPE §2.2: computed, not typed). Both the Table 1 and the
    Table D.14 notes print it, so the two notes cannot disagree."""
    rows_plain = {r["variable"]: r for _, r in df_stats.iterrows()}
    return 100.0 * float(rows_plain["Patent Market Valuation"]["N"]) / float(rows_plain["Total Patents"]["N"])


def format_table1_latex(df_stats):
    """
    Format Table 1 as a LaTeX string.

    Matches the paper's Table 1 structure exactly: section headers with
    inline totals, dollar-formatted monetary values with magnitude suffixes,
    'yrs' on regulatory proficiency, and proper spacing.
    """
    # Build lookup from (panel, variable) → row  (handles duplicate var names)
    rows = {(r["panel"], r["variable"]): r for _, r in df_stats.iterrows()}
    # Also keep a plain variable→row dict for unique names (convenience)
    rows_plain = {r["variable"]: r for _, r in df_stats.iterrows()}

    def _r(var, panel=None):
        if panel is not None:
            return rows[(panel, var)]
        return rows_plain[var]

    def _plain_row(var, n=None, mean=None, sd=None, rng=None):
        """Build a standard \\hspace row from preformatted strings."""
        n_s = n if n is not None else "-"
        m_s = mean if mean is not None else "-"
        sd_s = sd if sd is not None else "-"
        rng_s = rng if rng is not None else "-"
        return f"\\hspace{{4mm}}{var} & {n_s} & {m_s} & {sd_s} & {rng_s} \\\\"

    # Helpers for specific variable types
    def _count_row(var_label, csv_var, panel=None):
        """Row with only an N count (no mean/sd/range)."""
        r = _r(csv_var, panel=panel)
        return _plain_row(var_label, n=_fmt_int(r["N"]))

    def _dist_row(var_label, csv_var, decimals=1, panel=None):
        """Row with mean, sd, range as plain numbers (integer ranges)."""
        r = _r(csv_var, panel=panel)
        n_s = _fmt_int(r["N"]) if not pd.isna(r["N"]) else "-"
        m_s = fmt_number(r["mean"], decimals=decimals) if not pd.isna(r["mean"]) else "-"
        sd_s = fmt_number(r["std"], decimals=decimals) if not pd.isna(r["std"]) else "-"
        mn = int(r["min"]) if not pd.isna(r["min"]) and r["min"] == int(r["min"]) else r["min"]
        mx = int(r["max"]) if not pd.isna(r["max"]) and r["max"] == int(r["max"]) else r["max"]
        rng_s = f"[{_fmt_int(mn) if isinstance(mn, int) else fmt_number(mn)}, " \
                f"{_fmt_int(mx) if isinstance(mx, int) else fmt_number(mx)}]"
        return _plain_row(var_label, n=n_s, mean=m_s, sd=sd_s, rng=rng_s)

    lines = []
    lines.append("\\begin{table}[h!]")
    lines.append("\\begin{center}")
    lines.append("\\caption{\\textbf{Summary Statistics}}")
    lines.append("\\begin{tabular}{lcccc}")
    lines.append("\\hline \\hline ")
    lines.append("\\addlinespace")
    lines.append("\\textbf{Variable} & \\textbf{N} & \\textbf{Mean}  "
                 "& \\textbf{SD} & \\textbf{Range} \\\\")
    lines.append("\\hline")
    lines.append("\\addlinespace")
    lines.append("")

    # ── Panel I: FDA Administrative Data ──
    lines.append("\\multicolumn{5}{l}{\\textbf{I. FDA Administrative Data}} \\\\")
    lines.append("")
    lines.append("\\addlinespace")

    # Subpanel A header with inline total (force M suffix like manuscript)
    r_sub = _r("Total Submissions")
    sub_total = f"{r_sub['N'] / 1e6:.3f}M"
    lines.append(
        f"\\textit{{A. PMA/510(k) Submissions}} "
        f"& {sub_total} & - & - & -\\\\"
    )
    lines.append(_count_row("Number of Device Types", "Number of Device Types",
                            panel="I. FDA Administrative Data"))
    lines.append(_dist_row("Submissions per Device Type", "Submissions per Device Type"))
    lines.append(" &  &  &  &  \\\\")  # spacer row
    lines.append(_count_row("Total Submitting Firms", "Total Submitting Firms"))
    lines.append(_dist_row("Firms per Device Type", "Firms per Device Type"))

    # Regulatory Proficiency with † and 'yrs'
    r_prof = _r("Firm Regulatory Proficiency (years)")
    prof_n = _fmt_int(r_prof["N"])
    prof_mean = f"{r_prof['mean']:.1f} yrs"
    prof_sd = f"{r_prof['std']:.1f} yrs"
    prof_min = f"{r_prof['min']:.0f}"
    prof_max = f"{r_prof['max']:.1f} yrs"
    lines.append(
        f"\\hspace{{4mm}}Firm Regulatory Proficiency\\dag "
        f"& {prof_n} & {prof_mean} &  {prof_sd} & [{prof_min}, {prof_max}] \\\\"
    )
    lines.append("")
    lines.append("\\addlinespace")

    # Subpanel B header with inline total
    r_aer = _r("Total Adverse Event Reports")
    lines.append(
        f"\\textit{{B. Adverse Event Reports}} "
        f"& {_fmt_magnitude(r_aer['N'])} & - & - & -\\\\"
    )
    lines.append(_count_row("Number of Device Types Reporting",
                            "Number of Device Types Reporting"))
    lines.append(_dist_row("Adverse Events per Device Type",
                            "Adverse Events per Device Type"))
    lines.append(_dist_row("Serious Events per Device Type",
                            "Serious Events per Device Type"))

    # Assets of Offending Firms (values in CSV are in millions)
    r_assets = _r("Assets of Offending Firms")
    lines.append(_plain_row(
        "Assets of Offending Firms",
        n=_fmt_int(r_assets["N"]),
        mean=_fmt_dollars(r_assets["mean"]),
        sd=_fmt_dollars(r_assets["std"]),
        rng=f"[{_fmt_dollars(r_assets['min'])}, {_fmt_dollars(r_assets['max'])}]",
    ))
    lines.append("")
    lines.append("\\addlinespace")

    # ── Panel II: Patents ──
    r_totpat = _r("Total Patents")
    lines.append(
        f"\\multicolumn{{5}}{{l}}{{\\textbf{{II. Dimensions Device Patents "
        f"(N = {_fmt_int(r_totpat['N'])})}}}} \\\\"
    )
    lines.append("")
    lines.append(_count_row("Number of Device Types", "Number of Device Types",
                            panel="II. Dimensions Device Patents"))
    lines.append(_dist_row("Patents per Device Type", "Patents per Device Type"))
    lines.append(_dist_row("Citations per Patent", "Citations per Patent"))

    # Patent Market Valuation (values in CSV are in millions)
    r_val = _r("Patent Market Valuation")
    lines.append(_plain_row(
        "Patent Market Valuation",
        n=_fmt_int(r_val["N"]),
        mean=_fmt_dollars(r_val["mean"]),
        sd=_fmt_dollars(r_val["std"]),
        rng=f"[{_fmt_dollars(r_val['min'])}, {_fmt_dollars(r_val['max'])}]",
    ))

    # Applicant Assets (values in CSV are in millions)
    r_app = _r("Applicant Assets")
    lines.append(_plain_row(
        "Applicant Assets",
        n=_fmt_int(r_app["N"]),
        mean=_fmt_dollars(r_app["mean"]),
        sd=_fmt_dollars(r_app["std"]),
        rng=f"[{_fmt_dollars(r_app['min'])}, {_fmt_dollars(r_app['max'])}]",
    ))
    lines.append("")
    lines.append("\\addlinespace")

    # ── Panel III: MarketScan ──
    # Extract the panel header (includes computed total procedures)
    panel3_header = df_stats[
        df_stats["panel"].str.startswith("III.", na=False)
    ].iloc[0]["panel"]
    lines.append(
        f"\\multicolumn{{5}}{{l}}{{\\textbf{{{panel3_header}}}}} \\\\"
    )
    lines.append("")
    lines.append(_count_row("Number of Procedure Codes", "Number of Procedure Codes"))

    # Procedures per Code (plain integers, max uses magnitude suffix)
    r_proc = _r("Procedures per Code")
    lines.append(_plain_row(
        "Procedures per Code",
        mean=_fmt_int(r_proc["mean"]),
        sd=_fmt_int(r_proc["std"]),
        rng=f"[{_fmt_int(r_proc['min'])}, {_fmt_magnitude(r_proc['max'])}]",
    ))

    # Price per Procedure-Year (values in CSV are in dollars)
    r_price = _r("Price per Procedure-Year")
    price_mean = f"\\${r_price['mean']:,.1f}"
    price_sd = f"\\${r_price['std']:,.1f}"
    price_min = f"\\${r_price['min']:,.0f}"
    price_max = f"\\${r_price['max']:,.0f}"
    lines.append(_plain_row(
        "Price per Procedure-Year",
        n=_fmt_int(r_price["N"]),
        mean=price_mean,
        sd=price_sd,
        rng=f"[{price_min}, {price_max}]",
    ))
    lines.append("")
    lines.append("\\addlinespace")
    lines.append("\\bottomrule ")
    lines.append("\\end{tabular}")

    # Footnote. The publicly-traded share is computed from the table's own counts (patents carrying a
    # market value / total patents). r_val = Patent Market Valuation N; r_totpat = Total Patents N.
    pt_share = public_patent_share(df_stats)
    lines.append("\\caption*{\\begin{footnotesize}%")
    lines.append(
        "\\textit{Note}: Table \\ref{tab:SummaryStatistics_AllClasses_Reorg} "
        "provides summary statistics for each class independently. "
        "See \\citet{kogan:2017} for more information on the patent market "
        "valuation data, which was merged into the patent dataset. "
        "The CRSP/Compustat database was used to derive the total assets of "
        "firms applying for patent protection as a proxy for firm size. "
        "Market values and applicant assets are only available for patents "
        f"filed by publicly traded firms, representing roughly {pt_share:.0f}\\% of the "
        "total sample of patents. Missing observations account for "
        "discrepancies between (i) the total FDA device types (5,542) and "
        "the number represented in device submissions, adverse event reports, "
        "and patents (many device types have no associated patents); "
        "(ii) the total number of patents and the number with market "
        "valuations and applicant assets; and (iii) the total number of "
        "claims and those containing amounts paid. "
        "\\dag``Regulatory proficiency'' indicates the total number of days "
        "a firm has experienced approval delays across all its submitted devices."
    )
    lines.append("\\end{footnotesize}}")
    lines.append("\\label{tab:SummaryStatistics}")
    lines.append("\\end{center}")
    lines.append("\\end{table}")

    return "\n".join(lines)


def format_table_d14_latex(df_stats, pt_share):
    """
    Format Table D.14 as a LaTeX string. pt_share is public_patent_share() of Table 1; the note prints it.

    Matches the paper's Appendix Table D.14 (SummaryStatistics_AllClasses_Reorg):
    columns are Class I, Class II, Class III. Includes subsection headers within
    Panel A, currency formatting for asset/valuation rows, and LaTeX-safe commas.
    """
    # Variables whose values are stored in millions of dollars
    CURRENCY_VARS = {
        "Assets of offending firms", "Patent market valuation", "Applicant assets",
    }
    # Variables displayed with "yrs" suffix
    YRS_VARS = {"Firm regulatory proficiency (years)"}
    # Display name overrides for the table
    DISPLAY_NAMES = {
        "Firm regulatory proficiency (years)": "Firm regulatory proficiency*",
    }
    # Subsection headers within Panel A
    SECTION_DISPLAY = {
        "Device submissions": "Device submissions",
        "Adverse event reports": "Adverse event reports (AERs)",
    }

    def _lc(s):
        """Replace commas with LaTeX-safe {,} in number strings."""
        return str(s).replace(",", "{,}")

    def _fmt_currency(val_m, decimals=2):
        """Format a value in millions as human-readable currency."""
        if pd.isna(val_m):
            return "-"
        aval = abs(val_m)
        if aval >= 1_000_000:
            s = f"\\${val_m / 1_000_000:,.{decimals}f}T"
        elif aval >= 1_000:
            s = f"\\${val_m / 1_000:,.{decimals}f}B"
        elif aval >= 0.01:
            s = f"\\${val_m:,.{decimals}f}M"
        else:
            raw = val_m * 1_000_000
            s = f"\\${raw:,.0f}" if raw >= 1 else f"\\${raw:,.2f}"
        return _lc(s)

    def _fmt_val(x, decimals=2):
        """Format a number with LaTeX-safe commas."""
        if pd.isna(x):
            return "-"
        return _lc(f"{x:,.{decimals}f}")

    def _fmt_int(x):
        """Format an integer with LaTeX-safe commas."""
        if pd.isna(x):
            return "-"
        return _lc(f"{int(x):,}")

    # Normalize section column (NaN → "" for safe comparisons)
    df_stats = df_stats.copy()
    df_stats["section"] = df_stats["section"].fillna("")

    # Ordered unique variables
    variables_order = list(dict.fromkeys(df_stats["variable"]))

    # Which variables have distributional stats (for [2pt] spacing decisions)
    has_dist = set()
    for var in variables_order:
        var_rows = df_stats[df_stats.variable == var]
        if var_rows["std"].notna().any():
            has_dist.add(var)

    # Build structured rows with formatting
    output_rows = []
    for vi, var in enumerate(variables_order):
        var_rows = df_stats[df_stats.variable == var]
        if len(var_rows) == 0:
            continue
        panel = var_rows.iloc[0]["panel"]
        section = var_rows.iloc[0].get("section", "")
        is_panel_a = "A." in panel
        is_currency = var in CURRENCY_VARS
        is_yrs = var in YRS_VARS
        display_var = DISPLAY_NAMES.get(var, var)
        var_prefix = "\\quad " if is_panel_a else ""

        vals = {r["class"]: r for _, r in var_rows.iterrows()}
        main_cells = [f"{var_prefix}{display_var}"]
        detail_cells = [""]
        has_details = False

        for cls in ["Class I", "Class II", "Class III"]:
            if cls not in vals:
                main_cells.append("-")
                detail_cells.append("")
                continue
            r = vals[cls]
            if not pd.isna(r.get("value", np.nan)):
                main_cells.append(_fmt_int(r["value"]))
                detail_cells.append("")
            elif not pd.isna(r.get("mean", np.nan)):
                # Main value
                if is_currency:
                    main_cells.append(_fmt_currency(r["mean"]))
                elif is_yrs:
                    main_cells.append(f"{r['mean']:.2f} yrs")
                else:
                    main_cells.append(_fmt_val(r["mean"]))
                # Detail line (SD, min, max)
                if not pd.isna(r.get("std", np.nan)):
                    has_details = True
                    if is_currency:
                        sd_s = _fmt_currency(r["std"])
                        mn_s = _fmt_currency(r["min"])
                        mx_s = _fmt_currency(r["max"])
                    elif is_yrs:
                        sd_s = f"{r['std']:.2f} yrs"
                        mn_s = str(int(round(r["min"])))
                        mx_s = str(int(round(r["max"])))
                    else:
                        sd_s = _fmt_val(r["std"])
                        mn_s = _fmt_val(r["min"], decimals=0)
                        mx_s = _fmt_val(r["max"], decimals=0)
                    detail_cells.append(
                        f"{{\\scriptsize [{sd_s}]; [{mn_s}, {mx_s}]}}"
                    )
                else:
                    detail_cells.append("")
            else:
                main_cells.append("-")
                detail_cells.append("")

        # [2pt] on main line: add if count-only row precedes a distributional row
        next_var = variables_order[vi + 1] if vi + 1 < len(variables_order) else None
        if not has_details and next_var in has_dist:
            main_suffix = " \\\\[2pt]"
        else:
            main_suffix = " \\\\"

        # [2pt] on detail line: add unless this is the last var in its section
        if has_details:
            next_same_section = (
                next_var is not None
                and vi + 1 < len(variables_order)
                and df_stats[df_stats.variable == next_var].iloc[0].get("section", "")
                == section
                and df_stats[df_stats.variable == next_var].iloc[0]["panel"] == panel
            )
            detail_suffix = " \\\\[2pt]" if next_same_section else " \\\\"
        else:
            detail_suffix = None

        output_rows.append({
            "panel": panel,
            "section": section,
            "main_line": " & ".join(main_cells) + main_suffix,
            "detail_line": (
                " & ".join(detail_cells) + detail_suffix
            ) if has_details else None,
        })

    # Assemble LaTeX
    lines = []
    lines.append("\\begin{table}[t]")
    lines.append("\\centering")
    lines.append("\\caption{\\textbf{Summary Statistics by FDA Class}}")
    lines.append("\\label{tab:SummaryStatistics_AllClasses_Reorg}")
    lines.append("\\begin{threeparttable}")
    lines.append("\\footnotesize")
    lines.append("\\setlength{\\tabcolsep}{4pt}")
    lines.append("\\renewcommand{\\arraystretch}{1.12}")
    lines.append("")

    tab_spec = (
        "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.42\\textwidth}"
        "*3{>{\\centering\\arraybackslash}p{0.17\\textwidth}}@{}}"
    )
    current_panel = ""
    current_section = ""

    for row in output_rows:
        panel = row["panel"]
        section = row["section"]

        # Panel transition
        if panel != current_panel:
            if current_panel:
                lines.append("\\midrule")
                lines.append("\\end{tabular}")
                lines.append("")
                lines.append("\\vspace{2pt}")
                lines.append("")
            current_panel = panel
            current_section = ""
            if "A." in panel:
                panel_label = "Panel A: FDA Administrative Data"
            else:
                panel_label = "Panel B: Dimensions Device Patents"
            lines.append(tab_spec)
            if "A." in panel:
                lines.append("\\hline")
                lines.append("\\hline")
            lines.append(
                f" \\textbf{{{panel_label}}} & \\textbf{{Class I}}"
                f" & \\textbf{{Class II}} & \\textbf{{Class III}} \\\\"
            )
            lines.append("\\midrule")

        # Section transition within Panel A
        if "A." in panel and section and section != current_section:
            if current_section:
                lines.append("\\addlinespace")
            section_display = SECTION_DISPLAY.get(section, section)
            lines.append(f"\\emph{{{section_display}}} & & & \\\\")
            current_section = section

        lines.append(row["main_line"])
        if row["detail_line"]:
            lines.append(row["detail_line"])

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("")
    lines.append(
        "\\begin{tablenotes}[flushleft,para]\\footnotesize\n"
        "\\item[] Note: For rows with distributional stats, the first line "
        "shows the \\emph{mean}; the second line lists \\emph{SD} and "
        "\\emph{range} in brackets. Panel~A reports FDA administrative "
        "aggregates; Panel~B reports Dimensions patent statistics. Patent "
        "market valuation data are from \\citet{kogan:2017}. Firm total "
        "assets are from CRSP/Compustat (proxy for firm size); market values "
        "and applicant assets are observed only for patents filed by public "
        f"firms (\\(\\sim\\){pt_share:.0f}\\% of patents). *``Regulatory proficiency'' "
        "indicates the total number of days a firm has experienced approval "
        "delays across all its submitted devices."
    )
    lines.append("\\end{tablenotes}")
    lines.append("")
    lines.append("\\end{threeparttable}")
    lines.append("\\end{table}")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def _abort_on_missing_inputs():
    """Log every missing required input and return the module's non-zero exit code."""
    logging.error("=" * 60)
    logging.error(
        f"09_summary_stats: ABORTING -- {len(_MISSING_REQUIRED)} required input(s) missing. "
        "Table 1 and Table D.14 would be written with empty rows, so nothing is written."
    )
    for item in _MISSING_REQUIRED:
        logging.error(f"  - {item}")
    logging.error(
        "On the restricted route, supply these from the licensed sources listed in DATA_INPUTS.md. "
        "On the simulated route, run "
        "`python3 synthetic_pipeline/materialize_simulation.py --source-dir <payload>` "
        "(or `--for-gen-run` followed by the simulated-data route, which regenerates the derived inputs) "
        "before this step."
    )
    logging.error("=" * 60)
    return 1


def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    t_start = time.time()

    # ================================================================
    # Load data
    # ================================================================
    logging.info("=" * 60)
    logging.info("Loading data for summary statistics...")

    synth_number = load_synth_number()
    if synth_number is None:
        # The crosswalk keys every later loader, so this one cannot be deferred.
        return _abort_on_missing_inputs()

    # FDA submissions (510k + PMA)
    submissions = load_fda_submissions()

    # Patent data with citations, xi, firm size
    all_pats, all_pats_cites, all_pats_forxi = load_patent_data(synth_number)

    # Adverse events
    df_ae = load_adverse_event_data(synth_number)

    # Device market data (unique devices, firms)
    market_data = load_device_market_data()

    # Regulatory proficiency
    lbd_df = load_regulatory_proficiency(synth_number)

    # Adverse event firm sizes
    w_fsize = load_adverse_firm_sizes(synth_number)

    # MarketScan claims data (Panel III; omitted only on an explicit opt-out)
    claims_df = load_claims_data()

    # Fail closed BEFORE writing anything: a table written from a partially loaded set of
    # inputs would carry empty rows and would still look like a successful step.
    if _MISSING_REQUIRED:
        return _abort_on_missing_inputs()

    # ================================================================
    # Table 1: Aggregate Summary Statistics
    # ================================================================
    logging.info("=" * 60)
    logging.info("Computing Table 1: Summary Statistics")

    df_table1 = compute_table1(
        submissions, synth_number, all_pats, all_pats_cites,
        all_pats_forxi, df_ae, market_data, lbd_df, w_fsize,
        claims_df=claims_df
    )

    # Save CSV
    csv_path = config.TABLES_DIR / "Table_1_summary_stats.csv"
    df_table1.to_csv(csv_path, index=False)
    logging.info(f"  Saved CSV: {csv_path}")

    # Save LaTeX
    tex_str = format_table1_latex(df_table1)
    tex_path = config.TABLES_DIR / "Table_1_summary_stats.tex"
    with open(tex_path, "w") as f:
        f.write(tex_str)
    logging.info(f"  Saved LaTeX: {tex_path}")

    # Print key numbers to console
    logging.info("  Key summary numbers:")
    for _, row in df_table1.iterrows():
        if not pd.isna(row["mean"]):
            logging.info(f"    {row['variable']}: mean={row['mean']:.2f}, std={row['std']:.2f}")
        elif not pd.isna(row["N"]):
            logging.info(f"    {row['variable']}: N={row['N']:,.0f}")

    # ================================================================
    # Table D.14: Summary Statistics by FDA Class
    # ================================================================
    logging.info("=" * 60)
    logging.info("Computing Table D.14: Summary Statistics by FDA Class")

    df_table_d14 = compute_table_d14(
        submissions, synth_number, all_pats, all_pats_cites,
        all_pats_forxi, df_ae, market_data, lbd_df, w_fsize
    )

    # Save CSV
    csv_path_d14 = config.TABLES_DIR / "Table_D14_summary_stats_by_class.csv"
    df_table_d14.to_csv(csv_path_d14, index=False)
    logging.info(f"  Saved CSV: {csv_path_d14}")

    # Save LaTeX
    tex_str_d14 = format_table_d14_latex(df_table_d14, public_patent_share(df_table1))
    tex_path_d14 = config.TABLES_DIR / "Table_D14_summary_stats_by_class.tex"
    with open(tex_path_d14, "w") as f:
        f.write(tex_str_d14)
    logging.info(f"  Saved LaTeX: {tex_path_d14}")

    # Print key numbers by class
    logging.info("  Key by-class numbers:")
    for cls in ["Class I", "Class II", "Class III"]:
        cls_rows = df_table_d14[df_table_d14["class"] == cls]
        pats_row = cls_rows[cls_rows.variable == "Total patents (N)"]
        if len(pats_row) > 0 and not pd.isna(pats_row.iloc[0].get("value", np.nan)):
            logging.info(f"    {cls} total patents: {int(pats_row.iloc[0]['value']):,}")

    elapsed = time.time() - t_start
    logging.info(f"Summary statistics complete in {elapsed:.1f}s.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
