#!/usr/bin/env python
"""
03b_estimation_2to1.py — Static DiD: II→I, all outcomes × specs × samples.

Mirror of 03a_estimation_3to2.py for Class II→I reclassifications.
Note: skips dev_count, firm_expansion, absnew_firm_count (no FDA data for Class I).

Inputs:
    data/derived/ (matched samples, parquet files, spillovers)
Outputs:
    output/tables/ (estimate CSVs for Tables 2-4, II→I columns)
"""

import sys
import logging
import time
import warnings
import os
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
        logging.FileHandler(config.LOGS_DIR / "03b_estimation_2to1.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

RECLASS_TYPE = "2_1"


def load_samples():
    """Load all sample DataFrames for II→I."""
    logging.info("Loading II→I samples...")

    # Load from parquet (pre-built with stacked FEs)
    df_2_1 = pd.read_parquet(config.DERIVED_DATA_DIR / config.PARQUET_FILES["data_2_1_full"])
    df_later = pd.read_parquet(config.DERIVED_DATA_DIR / config.PARQUET_FILES["data_2_1_latertreat"])
    df_intuitive = pd.read_parquet(config.DERIVED_DATA_DIR / config.PARQUET_FILES["data_2_1_intuitive"])
    df_spillovers = pd.read_parquet(config.DERIVED_DATA_DIR / config.PARQUET_FILES["data_2_1_spillovers"])
    df_spillovers["year_reclassified_2_1"] = df_spillovers["year_reclassified"]

    # Set treatment for intuitive and later
    for df in [df_intuitive, df_later]:
        df["year_reclassified"] = df["year_reclassified_2_1"]
        df["treatment"] = 0
        df.loc[df.year_reclassified.notnull(), "treatment"] = 1

    # Derived variables (parquets may already have these pre-computed)
    for df in [df_2_1, df_later, df_intuitive, df_spillovers]:
        if "real_pats" not in df.columns:
            df["real_pats"] = df["patents_allpats"]
        if "unique_firms" not in df.columns:
            df["unique_firms"] = df.get("patents_newfirm", 0)
        if "unique_firmsPC" not in df.columns:
            df["unique_firmsPC"] = df.get("patents_newfirmPC", 0)
        df["times_cited"] = df["times_cited"].fillna(0)
        if "xi_real" in df.columns:
            df["xi_real"] = df["xi_real"].fillna(0)
        if "xi_real_2019" not in df.columns:
            df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019
        if "firm_expansion_patents" not in df.columns:
            df["firm_expansion_patents"] = df["unique_firmsPC"] - df["unique_firms"]

    return {
        "Full": df_2_1,
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
            return pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat_innovation"])
        else:
            return pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"])
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
        if "FE" in firms_temp.columns:
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


def emit_d1_treated_count(samples):
    """Output-only provenance for Table D.1 (JPE 2.2): write the II->I FINAL treated device-type
    count -- the number of unique treated (treatment==1) device types in the II->I estimating panel.
    This is the ``130'' cell in Table D.1, Panel A. It is a COUNT of the estimating sample, not an
    estimate, and does not touch any regression. Read by 10c_generate_appendix_tables.generate_d1().
    """
    full = samples["Full"]
    if "treatment" in full.columns:
        treated_mask = full["treatment"] == 1
    else:  # fall back to the treatment definition used elsewhere in this module
        treated_mask = full["year_reclassified_2_1"].notnull()
    n_treated = int(full.loc[treated_mask, "PRODUCTCODE"].nunique())
    out = config.TABLES_DIR / "d1_treated_counts.csv"
    pd.DataFrame([{"reclass_type": "2_1", "n_treated": n_treated}]).to_csv(out, index=False)
    logging.info(f"D.1 provenance: II->I final treated device-type count = {n_treated} -> {out}")


# Accumulates HARD estimation failures (outcome-level) so main() can fail-closed if any expected
# specification did not estimate.
_INCOMPLETE = []


def _assert_estimation_complete(label):
    """Fail-closed completeness gate (F7): raises SystemExit(1) if any HARD estimation failure was
    recorded (an allowed <5-PC skip is not a failure)."""
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
    emit_d1_treated_count(samples)  # JPE 2.2 provenance for Table D.1 (output-only)

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
                        logging.warning("  ALLOWED-SKIP (<5 PCs): %s / %s / %s / %s",
                                        spec["name"], outcome_type, sample_name, outcome)
                    else:
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

    _assert_estimation_complete("II→I")


if __name__ == "__main__":
    sys.exit(main())
