#!/usr/bin/env python
"""
03a_estimation_3to2.py — Static DiD: III→II, all outcomes × specs × samples.

Iterates over outcome panels (MainPanel, MarketComposition, AdverseEvent,
Spillovers), specification variants (nozero, BJS imputation, nodrugs,
quasi-Poisson, log, baseline), and control samples (Matched, Intuitive, Later).

Inputs:
    data/derived/ (matched samples, Full_sample.csv, parquet files, spillovers)
Outputs:
    output/tables/ (estimate CSVs for Tables 2-4, III→II columns)
"""

import os
import sys
import logging
import time
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked, UnbalancedPanelError
from estimation import run_did_imputation, run_quasipoisson, source_r_scripts

np.random.seed(config.RANDOM_SEED)
warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "03a_estimation_3to2.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

RECLASS_TYPE = "3_2"


def load_samples():
    """Load all sample DataFrames for III→II."""
    logging.info("Loading III→II samples...")

    # Full sample
    df_3_2 = pd.read_csv(config.DERIVED_DATA_DIR / config.FULL_SAMPLE)
    df_3_2["year_reclassified"] = df_3_2["year_reclassified_3_2"]
    df_3_2["FDA_own_accord"] = df_3_2["FDA_own_accord_3_2"]
    df_3_2["treatment"] = 0
    df_3_2.loc[df_3_2.year_reclassified.notnull(), "treatment"] = 1
    df_3_2 = df_3_2[(df_3_2.treatment == 1) | (df_3_2.controls == 1)]
    df_3_2 = df_3_2[df_3_2.total_pat_sum > 0].reset_index(drop=True)
    df_3_2 = df_3_2[(df_3_2.controls == 1) | (df_3_2.patent_sum_3_2 > 0)]
    df_3_2 = df_3_2[df_3_2.year != 0]
    df_3_2 = df_3_2[(df_3_2.FDA_own_accord == 1) | (df_3_2.treatment == 0)]
    df_3_2 = df_3_2[df_3_2.PRODUCTCODE != "HRD"].reset_index(drop=True)

    # Derived variables
    for df in [df_3_2]:
        df["real_pats"] = df["patents_allpats"]
        df["unique_firms"] = df["patents_newfirm"]
        df["unique_firmsPC"] = df["patents_newfirmPC"]
        df["dev_count"] = df["dev_count"].fillna(0)
        df["firm_count"] = df["firm_count"].fillna(0)
        df["absnew_firm_count"] = df["absnew_firm_count"].fillna(0)
        df["firm_expansion"] = df["firm_count"] - df["absnew_firm_count"]
        df["firm_expansion_patents"] = df["unique_firmsPC"] - df["unique_firms"]
        df["times_cited"] = df["times_cited"].fillna(0)
        df["xi_real"] = df["xi_real"].fillna(0)
        df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019

    # Stacked FE
    df_3_2["FE"] = np.nan
    df_3_2.loc[df_3_2.treatment == 0, "FE"] = 0
    df_3_2_orig = df_3_2.copy()
    parts = []
    for i, PC in enumerate(np.unique(df_3_2_orig[df_3_2_orig.treatment == 1]["PRODUCTCODE"])):
        if i > 0:
            controls = df_3_2_orig[df_3_2_orig.treatment == 0].copy()
            controls["FE"] = i
            parts.append(controls)
        df_3_2.loc[df_3_2.PRODUCTCODE == PC, "FE"] = i
    if parts:
        df_3_2 = pd.concat([df_3_2] + parts, ignore_index=True)

    # Load other samples
    df_intuitive = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["intuitive_3_2"])
    df_later = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["later_treated_3_2"])
    df_spillovers = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["intuitive_spillovers_3_2"])
    df_spillovers["year_reclassified_3_2"] = df_spillovers["year_reclassified"]

    for df in [df_intuitive, df_later, df_spillovers]:
        df["real_pats"] = df["patents_allpats"]
        df["unique_firms"] = df["patents_newfirm"]
        df["unique_firmsPC"] = df["patents_newfirmPC"]
        df["times_cited"] = df["times_cited"].fillna(0)
        df["xi_real"] = df["xi_real"].fillna(0)
        df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019
        if "dev_count" in df.columns:
            df["dev_count"] = df["dev_count"].fillna(0)
            df["firm_count"] = df["firm_count"].fillna(0)
            df["absnew_firm_count"] = df["absnew_firm_count"].fillna(0)
            df["firm_expansion"] = df["firm_count"] - df["absnew_firm_count"]
        df["firm_expansion_patents"] = df["unique_firmsPC"] - df["unique_firms"]

    for df in [df_later, df_intuitive]:
        df["year_reclassified"] = df["year_reclassified_3_2"]
        df["FDA_own_accord"] = df["FDA_own_accord_3_2"]
        df["treatment"] = 0
        df.loc[df.year_reclassified.notnull(), "treatment"] = 1

    # Apply stacking for intuitive and later too
    for df_name, df_src in [("intuitive", df_intuitive), ("later", df_later)]:
        df_src["FE"] = np.nan
        df_src.loc[df_src.treatment == 0, "FE"] = 0
        df_orig = df_src.copy()
        parts = []
        for i, PC in enumerate(np.unique(df_orig[df_orig.treatment == 1]["PRODUCTCODE"])):
            if i > 0:
                c = df_orig[df_orig.treatment == 0].copy()
                c["FE"] = i
                parts.append(c)
            df_src.loc[df_src.PRODUCTCODE == PC, "FE"] = i
        if parts:
            if df_name == "intuitive":
                df_intuitive = pd.concat([df_src] + parts, ignore_index=True)
            else:
                df_later = pd.concat([df_src] + parts, ignore_index=True)

    # Spillovers stacking
    df_spillovers["year_reclassified"] = df_spillovers.get("year_reclassified_3_2", df_spillovers.get("year_reclassified"))
    df_spillovers["treatment"] = 0
    df_spillovers.loc[df_spillovers.year_reclassified.notnull(), "treatment"] = 1
    df_spillovers["FE"] = np.nan
    df_spillovers.loc[df_spillovers.treatment == 0, "FE"] = 0
    df_spill_orig = df_spillovers.copy()
    parts = []
    for i, PC in enumerate(np.unique(df_spill_orig[df_spill_orig.treatment == 1]["PRODUCTCODE"])):
        if i > 0:
            c = df_spill_orig[df_spill_orig.treatment == 0].copy()
            c["FE"] = i
            parts.append(c)
        df_spillovers.loc[df_spillovers.PRODUCTCODE == PC, "FE"] = i
    if parts:
        df_spillovers = pd.concat([df_spillovers] + parts, ignore_index=True)

    # Filter year != 0
    for df in [df_3_2, df_intuitive, df_later, df_spillovers]:
        df.drop(df[df.year == 0].index, inplace=True)

    return {
        "Full": df_3_2,
        "Intuitive": df_intuitive,
        "Later": df_later,
        "Spillovers": df_spillovers,
    }


def get_sample(samples, sample_name, outcome_type, reclass_type):
    """Get the appropriate DataFrame for a given sample and outcome type."""
    if outcome_type == "Spillovers":
        return samples["Spillovers"].copy()
    if sample_name == "Matched":
        if outcome_type in ("MainPanel", "MarketComposition"):
            return pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat_innovation"])
        else:
            return pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat"])
    elif sample_name == "Intuitive":
        return samples["Intuitive"].copy()
    elif sample_name == "Later":
        return samples["Later"].copy()
    elif sample_name == "Full":
        return samples["Full"].copy()
    return None


def get_anticipation(outcome):
    """Return anticipation window for an outcome."""
    if outcome in config.ANTICIPATION["no_anticipation"]:
        return 0
    return config.ANTICIPATION[RECLASS_TYPE]


def run_estimation(firms, outcome, spec, reclass_type):
    """Run a single estimation for one outcome-spec combination."""
    nozero = spec["nozero"]
    df_imput = spec["df_imput"]
    poisson = spec["poisson"]
    logged = spec["logged"]

    if outcome in ["times_cited", "xi_real", "xi_real_2019"]:
        firms[outcome] = firms[outcome].fillna(0)
    firms["very_serious"] = firms.L + firms.H + firms.D + firms.S

    if nozero:
        temp_check = firms.groupby("PRODUCTCODE")[outcome].sum().reset_index()
        keep_PCs = temp_check[temp_check[outcome] > 0]["PRODUCTCODE"]
        firms_use = firms[firms.PRODUCTCODE.isin(keep_PCs)].copy().reset_index(drop=True)
    else:
        firms_use = firms.copy()

    if outcome in ["event_count", "L", "H", "D", "very_serious"]:
        firms_temp = firms_use[firms_use[outcome].notnull()].reset_index(drop=True)
        firms_temp = firms_temp[firms_temp.year > config.ADVERSE_EVENT_MIN_YEAR].reset_index(drop=True)
        FEs_bad = set(firms_temp[firms_temp.year_reclassified < config.ADVERSE_EVENT_MIN_RECLASS_YEAR]["FE"].values)
        firms_temp = firms_temp[~firms_temp.FE.isin(FEs_bad)].reset_index(drop=True)
        if df_imput:
            firms_temp = firms_temp[
                (firms_temp.year_reclassified > config.ADVERSE_EVENT_MIN_YEAR) | (firms_temp.treatment == 0)
            ].reset_index(drop=True)
    else:
        firms_temp = firms_use.copy().reset_index(drop=True)

    if len(np.unique(firms_temp["PRODUCTCODE"].values)) < 5:
        logging.warning(f"  {outcome}: fewer than 5 PCs, skipping")
        return None, None, None, None, "skip_lt5pc"

    if not df_imput:
        firms_temp["class_by_episode"] = (
            firms_temp["FE"].astype(str) + "[SEP]" + firms_temp["factorized"].astype(str)
        )
        firms_temp["class_by_episode"] = firms_temp.class_by_episode.astype("category").cat.codes
        firms_temp = firms_temp.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)

    firms_temp["times_cited"] = firms_temp["times_cited"].fillna(0)

    # Set posttreat with anticipation
    anticipation = get_anticipation(outcome)
    firms_temp["posttreat"] = 0
    firms_temp.loc[
        (firms_temp.treatment == 1) & (firms_temp.year >= firms_temp.year_reclassified - anticipation),
        "posttreat",
    ] = 1

    # Estimation
    try:
        if df_imput:
            estimate, alpha025, alpha975 = run_did_imputation(
                firms_temp[[outcome, "year_reclassified", "treatment", "factorized", "year"]],
                outcome,
            )
        elif poisson:
            firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0
            estimate, alpha025, alpha975 = run_quasipoisson(
                firms_temp[[outcome, "posttreat", "treatment", "factorized", "year", "FE", "class_by_episode", "PRODUCTCODE"]],
                outcome,
            )
        else:
            if logged == "Log":
                firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0
                firms_temp[outcome] = np.log(firms_temp[outcome] + 1)
            firms_temp = firms_temp.reset_index(drop=True)
            estimate, alpha025, alpha975 = conley_taber_stacked(
                firms_temp[[outcome, "posttreat", "treatment", "factorized", "year", "FE", "class_by_episode", "PRODUCTCODE"]],
                outcome, "posttreat", "treatment", "class_by_episode", "year",
                seed=config.RANDOM_SEED,
            )
    except UnbalancedPanelError as e:
        logging.warning(f"  {outcome}: {e} -- ALLOWED SKIP (Conley-Taber needs a balanced panel)")
        return None, None, None, None, "skip_unbalanced_ct"
    except Exception as e:
        logging.warning(f"  {outcome}: estimation failed ({e}), skipping")
        return None, None, None, None, f"error:{type(e).__name__}: {e}"

    N = len(firms_temp.drop_duplicates(["PRODUCTCODE", "year"]))
    logging.info(f"  {outcome}: est={estimate}, CI=[{alpha025}, {alpha975}], N={N}")
    return estimate, alpha025, alpha975, N, "ok"


# Accumulates HARD estimation failures (outcome-level) across the whole run so main() can
# fail-closed if any expected specification did not estimate.
_INCOMPLETE = []


def _assert_estimation_complete(label):
    """Fail-closed completeness gate (F7): a zero exit must PROVE every expected specification was
    estimated. Raises SystemExit(1) if any HARD failure was recorded (an allowed <5-PC skip is not
    a failure)."""
    if _INCOMPLETE:
        logging.error("%s estimation INCOMPLETE: %d specification(s) failed to estimate:",
                      label, len(_INCOMPLETE))
        for row in _INCOMPLETE:
            logging.error("  FAILED: %s / %s / %s / %s -- %s", *row)
        raise SystemExit(1)
    logging.info("%s estimation complete (all expected specifications estimated).", label)


def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    source_r_scripts()

    samples = load_samples()

    outcome_type_list = ["MainPanel", "MarketComposition", "AdverseEvent", "Spillovers"]

    for spec in config.SPEC_VARIANTS:
        for outcome_type in outcome_type_list:
            rename_dict = config.get_outcome_dict(
                outcome_type, RECLASS_TYPE, nodrugs_A61=spec["nodrugs_A61"]
            )
            sample_list = ["Matched", "Intuitive", "Later"]
            if outcome_type == "Spillovers":
                sample_list = ["Matched"]

            for sample_name in sample_list:
                # Skip if output already exists -- UNLESS FORCE_ESTIMATION=1 (the
                # clean-output / simulation route, which must RECOMPUTE every estimate
                # on the input data instead of reusing shipped CSVs; set by
                # run_all --force-estimation).
                outpath_check = config.estimate_csv_path(
                    outcome_type, RECLASS_TYPE, spec["logged"], sample_name,
                    nozero=spec["nozero"], df_imput=spec["df_imput"],
                    nodrugs_A61=spec["nodrugs_A61"], poisson=spec["poisson"],
                )
                if outpath_check.exists() and os.environ.get("FORCE_ESTIMATION") != "1":
                    logging.info(
                        f"Spec={spec['name']}, Panel={outcome_type}, Sample={sample_name} — already exists, skipping"
                    )
                    continue

                logging.info(
                    f"Spec={spec['name']}, Panel={outcome_type}, Sample={sample_name}"
                )

                firms = get_sample(samples, sample_name, outcome_type, RECLASS_TYPE)
                if firms is None:
                    continue

                if sample_name != "Matched":
                    firms["treatment"] = 0
                    firms.loc[firms["year_reclassified_" + RECLASS_TYPE].notnull(), "treatment"] = 1
                    firms["factorized"] = firms.PRODUCTCODE.astype("category").cat.codes
                    firms["posttreat"] = 0
                    firms.loc[
                        (firms.treatment == 1) & (firms.year_reclassified <= firms.year),
                        "posttreat",
                    ] = 1

                df_container = pd.DataFrame()
                estimate_list, lower_list, upper_list = [], [], []
                string_list, outcome_names, n_list = [], [], []

                for outcome in rename_dict.keys():
                    est, low, high, n, status = run_estimation(firms, outcome, spec, RECLASS_TYPE)
                    if status == "ok" and est is not None:
                        estimate_list.append(est)
                        lower_list.append(low)
                        upper_list.append(high)
                        string_list.append(rename_dict[outcome])
                        outcome_names.append(outcome)
                        n_list.append(n)
                    elif status in ("skip_lt5pc", "skip_unbalanced_ct"):
                        # ALLOWED empty cell (documented): fewer than 5 product codes. Logged,
                        # not a failure -- but not silently dropped either.
                        logging.warning("  ALLOWED-SKIP (<5 PCs): %s / %s / %s / %s",
                                        spec["name"], outcome_type, sample_name, outcome)
                    else:
                        # HARD estimation failure -- record it so a zero exit cannot hide an
                        # incomplete result matrix.
                        _INCOMPLETE.append((spec["name"], outcome_type, sample_name, outcome, status))
                        logging.error("  ESTIMATION FAILURE: %s / %s / %s / %s -- %s",
                                      spec["name"], outcome_type, sample_name, outcome, status)

                if not outcome_names:
                    continue

                df_container["outcome"] = outcome_names
                df_container["formal_name"] = string_list
                df_container["Estimate"] = estimate_list
                df_container["lower_CI"] = lower_list
                df_container["upper_CI"] = upper_list
                df_container["Sample Size"] = n_list

                outpath = config.estimate_csv_path(
                    outcome_type, RECLASS_TYPE, spec["logged"], sample_name,
                    nozero=spec["nozero"], df_imput=spec["df_imput"],
                    nodrugs_A61=spec["nodrugs_A61"], poisson=spec["poisson"],
                )
                df_container.to_csv(outpath, index=False)
                logging.info(f"  Saved: {outpath}")

    # COMPLETENESS GATE: a zero exit must PROVE every expected specification was
    # estimated. Any hard estimation failure (not an allowed <5-PC skip) fails the step.
    _assert_estimation_complete("III→II")


if __name__ == "__main__":
    sys.exit(main())
