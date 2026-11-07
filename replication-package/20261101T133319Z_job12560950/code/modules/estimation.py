"""
R-calling wrappers for estimation routines.

Wraps fixest::feols, feglm (quasi-Poisson), and BJS did_imputation via rpy2.
Sources R scripts once per session; subsequent calls reuse loaded functions.

Inputs: DataFrames passed to R functions
Outputs: (estimate, lower_CI, upper_CI) or (estimates, SEs) tuples
"""

import numpy as np
import pandas as pd

from rpy2 import robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

_R_SOURCED = False


def source_r_scripts():
    """Source all R scripts once per session."""
    global _R_SOURCED
    if _R_SOURCED:
        return
    r = robjects.r
    r["source"](str(config.R_SCRIPTS_DIR / "preprocess.R"))
    r["source"](str(config.R_SCRIPTS_DIR / "did_imputation_topython.R"))
    _R_SOURCED = True


def _to_r(df):
    """Convert pandas DataFrame to R DataFrame, then run R's garbage collector before the caller estimates.

    Without the gc, the full 04_event_studies.py process crashed inside feols with
    "malloc(): unsorted double linked list corrupted" on the simulated panels (three runs out of three
    on one machine; reproduced in every diagnostic run), while R alone on the same data never crashed
    and a gc here made the same process pass twice out of two. conley_taber.py has carried the same guard (see its notes on
    rpy2 heap accumulation), which is why 03a/03b/06a survived. gc() only reclaims memory and does not enter
    the computation: repeated runs with it were hash-identical."""
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df)
    robjects.r("gc()")
    return df_r


def _from_r(r_obj):
    """Convert R object to pandas."""
    with localconverter(ro.default_converter + pandas2ri.converter):
        return ro.conversion.rpy2py(r_obj)


# ============================================================================
# Static DiD estimators
# ============================================================================

def run_feols(df, outcome_var):
    """
    Run fixest::feols with stacked FE (filter_country from preprocess.R).

    Returns (coefficient, residuals_array).
    Used by ConleyTaberStacked for residualization.
    """
    source_r_scripts()
    fn = robjects.globalenv["filter_country"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coef = np.array(result[0]).item()
    resid = np.array(result[1:]).flatten()
    return coef, resid


def run_feols_2_1(df, outcome_var):
    """
    Run fixest::feols with clustered SEs (filter_country_2_1).

    Returns (estimate, SE).
    """
    source_r_scripts()
    fn = robjects.globalenv["filter_country_2_1"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coef = _from_r(result[0]).item() if hasattr(result[0], '__len__') else float(result[0])
    se = _from_r(result[1]).item() if hasattr(result[1], '__len__') else float(result[1])
    return coef, se


def run_feols_es_3to2(df, outcome_var):
    """
    Run event-study feols for III→II (filter_country_ES).

    Returns (coefficients_array, residuals_array).
    """
    source_r_scripts()
    fn = robjects.globalenv["filter_country_ES"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coefs = np.array(result[0])
    resid = np.array(result[1]).flatten()
    return coefs, resid


def run_feols_es_2to1(df, outcome_var):
    """
    Run event-study feols for II→I (filter_country_ES_2_1).

    Returns (coefficients_array, SEs_array).
    """
    source_r_scripts()
    fn = robjects.globalenv["filter_country_ES_2_1"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coefs = np.array(_from_r(result[0])).flatten()
    ses = np.array(_from_r(result[1])).flatten()
    return coefs, ses


def run_feols_es_2to1_utilization(df, outcome_var):
    """
    Run event-study feols for utilization II→I (filter_country_ES_2_1_utilization).

    Returns (coefficients_array, SEs_array).
    """
    source_r_scripts()
    fn = robjects.globalenv["filter_country_ES_2_1_utilization"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coefs = np.array(_from_r(result[0])).flatten()
    ses = np.array(_from_r(result[1])).flatten()
    return coefs, ses


def run_quasipoisson(df, outcome_var):
    """
    Run fixest quasi-Poisson regression (filter_country_quasipoisson).

    Returns (estimate, lower_CI, upper_CI).
    """
    source_r_scripts()
    fn = robjects.globalenv["filter_country_quasipoisson"]
    df_r = _to_r(df)
    result_r = fn(df_r, outcome_var)
    result = _from_r(result_r)
    estimate = np.round(result["estimate"].values[0], 2)
    conf_low = np.round(result["conf.low"].values[0], 2)
    conf_high = np.round(result["conf.high"].values[0], 2)
    return estimate, conf_low, conf_high


def run_did_imputation(df, outcome_var):
    """
    Run BJS did_imputation in a subprocess to avoid rpy2 segfaults.

    Writes data to temp CSV, runs R script, reads result CSV back.
    Returns (estimate, lower_CI, upper_CI).
    """
    import subprocess
    import tempfile
    import os
    import logging

    with tempfile.TemporaryDirectory() as tmpdir:
        input_csv = os.path.join(tmpdir, "input.csv")
        output_csv = os.path.join(tmpdir, "output.csv")
        df.to_csv(input_csv, index=False)

        r_script = f"""
library(didimputation)
df <- read.csv("{input_csv}")
df[df$treatment == 0, "year_reclassified"] <- 0
static <- did_imputation(data=df, yname="{outcome_var}",
    gname="year_reclassified", tname="year", idname="factorized")
static_df <- as.data.frame(static)
write.csv(static_df, "{output_csv}", row.names=FALSE)
"""
        r_file = os.path.join(tmpdir, "run_bjs.R")
        with open(r_file, "w") as f:
            f.write(r_script)

        result = subprocess.run(
            ["Rscript", r_file],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            logging.warning(f"BJS imputation failed for {outcome_var}: {result.stderr[:200]}")
            raise RuntimeError(f"BJS imputation failed: {result.stderr[:200]}")

        static = pd.read_csv(output_csv)
        estimate = np.round(static["estimate"].values[0], 2)
        conf_low = np.round(static["conf.low"].values[0], 2)
        conf_high = np.round(static["conf.high"].values[0], 2)
        return estimate, conf_low, conf_high


def run_recall_did(df, outcome_var):
    """
    Run recall-specific DiD (recall_DID from preprocess.R).

    Returns (coefficient, SE).
    """
    source_r_scripts()
    fn = robjects.globalenv["recall_DID"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coef = np.array(_from_r(result[0])).item()
    se = np.array(_from_r(result[1])).item()
    return coef, se


def run_recalls_es(df, outcome_var):
    """
    Run recall event-study (recalls_ES from preprocess.R).

    Returns (coefficients_array, SEs_array).
    """
    source_r_scripts()
    fn = robjects.globalenv["recalls_ES"]
    df_r = _to_r(df)
    result = fn(df_r, outcome_var)
    coefs = np.array(_from_r(result[0])).flatten()
    ses = np.array(_from_r(result[1])).flatten()
    return coefs, ses
