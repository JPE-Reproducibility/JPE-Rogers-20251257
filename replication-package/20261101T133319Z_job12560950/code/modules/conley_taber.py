"""
Conley-Taber permutation inference for stacked DiD.

De-duplicated from Replication_analysis.py (lines 42-416) and
Implications_for_reg_design.py (lines 75-132). Three public functions:

  conley_taber_stacked     — Primary estimator (R fixest residualization)
  conley_taber_stacked_es  — Event-study variant (single horizon estimate)
  conley_taber_simple      — pyhdfe residualization, optional controls

Inputs: DataFrames with panel structure
Outputs: (estimate, lower_CI, upper_CI) tuples
"""

import csv
import logging
import os

import numpy as np
from numba import jit
from sklearn import linear_model
import pyhdfe

from rpy2 import robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config


class UnbalancedPanelError(Exception):
    """Raised when feols removes observations during residualization, leaving a panel that the
    Conley-Taber permutation estimator (which requires a balanced cluster-by-year layout) cannot
    use. Callers treat it as an allowed, logged skip -- never a silent wrong answer or a crash."""


# ===========================================================================================
# INFERENCE-METHOD FALLBACKS
# ===========================================================================================
# Three places below cannot compute the permutation CI (feols removed observations, or a treated
# cluster is missing a year-row so the balanced grid cannot be laid out) and instead return the
# point estimate with a clustered-SE or OLS normal-approximation interval. The tuple they return is
# SHAPE-IDENTICAL to the permutation one, every consumer writes it into the same
# Effect/lower_cb/upper_cb columns, and some consumers then back-derive an "SE" from the CI width,
# so the output columns alone do not distinguish a substituted interval from a permutation one.
# Every substitution is therefore RECORDED, per call, to output/logs/inference_method_fallbacks.csv,
# with the route it happened on.
#
# On the real-data route the substitution happens on two rows, both II->I BilledAmt with
# conley_taber_stacked on the human-expert concordance: 8 of 118,414 observations removed by feols
# for Expert and 8 of 79,714 for Expert Matched. Those two rows of
# output/tables/price_utilization_estimates.csv carry method="Conley_Taber" with a clustered-SE
# normal-approximation interval (ci_method says so). No manuscript number is among them (the price
# footnote quotes the BJS_imputation rows, which do not come through here). The substitution is
# recorded, never refused: the shipped table legitimately contains those two rows.

INFERENCE_FALLBACKS = []
_FALLBACK_SIDECAR = "inference_method_fallbacks.csv"


def _route_is_simulated():
    """True only when the run is explicitly the simulated-data route. Anything else -- the real
    route, or a bare invocation with no route set -- counts as real, so the refusal is the default."""
    return (os.environ.get("FDA_INTEXT_ROUTE", "").strip().lower() == "synthetic"
            or os.environ.get("FDA_SYNTHETIC_MODE", "").strip() == "1")


def _record_inference_fallback(estimator, outcome_var, method, n_removed, detail=""):
    """Record that this interval is NOT a permutation interval. Appends one row per call, so the
    record survives across the separate step processes of a run."""
    row = {"estimator": estimator, "outcome_var": outcome_var, "fallback_method": method,
           "n_removed": n_removed, "detail": detail,
           "route": "simulated" if _route_is_simulated() else "real"}
    INFERENCE_FALLBACKS.append(row)
    try:
        # output/logs/, NOT output/tables/: this file only exists when a substitution happens, and
        # the simulated-route comparator requires the fixed reference set under output/tables to
        # match exactly, so a conditional member there would fail a run in which nothing fired.
        # output/logs is explicitly outside what the comparator reads.
        path = config.LOGS_DIR / _FALLBACK_SIDECAR
        path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not path.exists()
        with open(path, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(row))
            if write_header:
                w.writeheader()
            w.writerow(row)
    except Exception as exc:  # noqa: BLE001 -- recording must never mask the estimation itself
        logging.warning("    could not record the inference fallback to %s: %s",
                        _FALLBACK_SIDECAR, exc)




# preprocess.R's top level only DEFINES functions and sets idempotent globals (library() attaches +
# setFixest_nthreads(1)); it holds no per-call state. Re-sourcing it on EVERY estimation re-attaches
# tidyverse/didimputation/fixest/did dozens of times within one process -- a known rpy2 memory-churn
# pattern that can corrupt the (ABI-mode) R session into a hard process exit (SIGSEGV) deep into a
# long step like 03b. Source it ONCE per process instead: byte-identical results (the functions and
# the single-thread pin are unchanged), far less rpy2 churn. A fresh subprocess resets this flag.
_PREPROCESS_SOURCED = False


def _source_preprocess(r):
    global _PREPROCESS_SOURCED
    if not _PREPROCESS_SOURCED:
        r["source"](str(config.R_SCRIPTS_DIR / "preprocess.R"))
        _PREPROCESS_SOURCED = True


# ============================================================================
# Shared internals (formerly copy-pasted 4 times)
# ============================================================================

@jit(nopython=True)
def _gen_matrix(etat_mat, numbsim, nchst, stsim, eta1, nyrs):
    """Build simulated residual matrices. Numba-accelerated."""
    for isim in range(numbsim):
        for ist in range(nchst):
            trid = stsim[ist, isim]
            etat_mat[ist, :, isim] = eta1[trid * nyrs:(trid + 1) * nyrs].flatten()
    return etat_mat


def _simulation(eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
                stsim, countmax, tol, gamma, low):
    """Iterate to find Conley-Taber confidence bound."""
    i025 = int(np.floor(0.025 * numbsim))
    i975 = int(np.ceil(0.975 * numbsim))

    alpha0 = 0.0
    count = 0.0
    dif = 1.0

    while (dif > tol) and (count <= countmax):
        count += 1
        eta1 = eta - alpha0 * merit
        etat_mat = np.zeros((nchst, nyrs, numbsim))
        etat_mat = _gen_matrix(etat_mat, numbsim, nchst, stsim, eta1, nyrs)
        djt3d = np.repeat(djt[:, :, np.newaxis], numbsim, axis=2)
        dtil_mat = djt3d - np.mean(djt3d, axis=1).reshape(nchst, 1, numbsim)
        snum_mat = np.sum(dtil_mat * etat_mat, axis=1)
        sden_mat = np.sum(dtil_mat * dtil_mat, axis=1)
        snum_mat_summed = np.sum(snum_mat, axis=0)
        sden_mat_summed = np.sum(sden_mat, axis=0)
        asim = snum_mat_summed / sden_mat_summed
        asim = np.sort(asim, axis=0)

        if low:
            alpha_bound = alpha - asim[i975]
            alpha1 = alpha_bound
        else:
            alpha_bound = alpha - asim[i025]
            alpha1 = alpha_bound

        dif = np.abs((alpha0 - alpha1) / (alpha0 + 0.01))[0, 0]
        alpha0 = (gamma * alpha0 + (1 - gamma) * alpha1)[0, 0]

    if count >= countmax:
        print("Maximum number of iterations reached.")

    return alpha_bound


def _draw_stsim_clusters(df, group_name, nchst, numbsim, seed=None):
    """Draw random cluster assignments from unique group IDs."""
    if seed is not None:
        np.random.seed(seed)
    dropped = df.drop_duplicates(subset=["PRODUCTCODE", "year"])
    keep_clusters = np.unique(dropped[group_name].values)
    stsim = np.zeros((nchst, numbsim))
    for isim in range(numbsim):
        stsim[:, isim] = np.random.choice(
            keep_clusters, size=nchst, replace=False
        )
    return stsim


def _draw_stsim_indices(nchst, nnchst, numbsim, seed=None):
    """Draw random assignments from integer indices (0 .. nchst+nnchst-1)."""
    if seed is not None:
        np.random.seed(seed)
    stsim = np.zeros((nchst, numbsim))
    for isim in range(numbsim):
        stsim[:, isim] = np.random.choice(
            np.arange(0, nnchst + nchst), size=nchst, replace=False
        )
    return stsim


def _common_setup(df, posttreat_var, treatment_var, group_name, year_var):
    """Extract dimensions and djt matrix."""
    merit = df[posttreat_var].values.reshape(-1, 1)
    nchst = len(np.unique(df[df[treatment_var] == 1][group_name]))
    nnchst = len(np.unique(df[df[treatment_var] == 0][group_name]))
    nyrs = len(np.unique(df[year_var]))
    djt = (
        df[df[treatment_var] == 1]
        .pivot(index=group_name, columns=year_var, values=posttreat_var)
        .values
    )
    return merit, nchst, nnchst, nyrs, djt


def _run_bounds(eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
                stsim, countmax, tol, gamma):
    """Compute both upper and lower CI bounds."""
    alpha975 = _simulation(
        eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
        stsim.astype(int), countmax, tol, gamma, low=False
    )
    alpha025 = _simulation(
        eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
        stsim.astype(int), countmax, tol, gamma, low=True
    )
    return alpha025, alpha975


# ============================================================================
# Public API
# ============================================================================

def conley_taber_stacked(df, outcome_var, posttreat_var, treatment_var,
                         group_name, year_var, numbsim=None, seed=None,
                         countmax=None, tol=None, gamma=None):
    """
    Conley-Taber with R fixest residualization (stacked DiD).

    Uses filter_country() from preprocess.R for residualization, then
    permutation inference sampling from cluster IDs.
    """
    numbsim = numbsim or config.CT_NUMBSIM
    countmax = countmax or config.CT_COUNTMAX
    tol = tol or config.CT_TOL
    gamma = gamma or config.CT_GAMMA

    merit, nchst, nnchst, nyrs, djt = _common_setup(
        df, posttreat_var, treatment_var, group_name, year_var
    )

    # R residualization. filter_country returns resid(..., na.rm=FALSE): a residual vector aligned
    # 1:1 to the INPUT rows, with NA where feols removed an observation (a singleton or collinear
    # factorized^FE / year^FE level, or an NA outcome).
    r = robjects.r
    _source_preprocess(r)
    filter_fn = robjects.globalenv["filter_country"]
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df)
    # Trigger R's garbage collector before each residualization. Over a long step (03b runs dozens of
    # estimations on the much larger SYNTHETIC panels), rpy2's per-call data.frame conversions + feols
    # models accumulate unreclaimed R heap; without a gc the (ABI-mode) R session eventually corrupts
    # into a hard process exit (SIGSEGV/SIGABRT) mid-feols. An explicit gc() bounds that. No effect on
    # results (gc only reclaims memory); on the smaller real-data samples the session never grows
    # enough to matter, so real-data estimates are byte-identical.
    r("gc()")
    df_result_r = filter_fn(df_r, outcome_var)

    alpha = np.matrix(df_result_r[0])
    eta = np.array(df_result_r[1:]).reshape(-1, 1)

    # The permutation math below is not defined unless the TREATED panel is a balanced cluster-by-year
    # grid: _gen_matrix indexes eta as contiguous `nyrs` blocks, one per treated cluster (nchst*nyrs
    # cells total). Two ways that assumption fails:
    #   (a) feols removed an observation (a singleton/collinear factorized^FE / year^FE level, or an NA
    #       outcome) -> filter_country returns NA-marked residuals, so `eta` has NA; or
    #   (b) the treated panel was never balanced -- a treated cluster is missing one or more year-rows,
    #       so the treated (cluster x year) pivot `djt` has NA and eta's treated block is shorter than
    #       nchst*nyrs. This is the ValueError "cannot assign slice from input of different size" at
    #       _gen_matrix's `etat_mat[ist,:,isim] = eta1[trid*nyrs:(trid+1)*nyrs]`.
    # Case (b) also surfaces on the SYNTHETIC panels after the co-membership scramble (a fake
    # firm can land in an alternative control sample that has no row for some cluster-year). Either way
    # feols's coefficient is still valid, so it is reported with a clustered-SE normal-approximation
    # interval instead of the permutation bounds.
    # On the real price panel this branch fires for BilledAmt on the two II->I Expert-concordance
    # samples (8 of 118,414 observations removed for Expert; 8 of 79,714 for Expert Matched), so
    # those two Conley_Taber rows of price_utilization_estimates.csv carry a normal-approximation
    # interval. Every substitution is recorded in
    # output/logs/inference_method_fallbacks.csv. No manuscript number is affected: the price
    # footnote quotes the BJS_imputation rows, which are estimated elsewhere.
    if np.isnan(eta).any() or np.isnan(djt).any():
        n_removed = int(np.isnan(eta).sum()) + int(np.isnan(djt).sum())
        se_fn = robjects.globalenv["filter_country_se"]
        res_se = np.asarray(se_fn(df_r, outcome_var))   # reuse the already-built df_r; returns (coef, se)
        coef = float(res_se[0])
        se = float(res_se[1])
        if not np.isfinite(coef) or not np.isfinite(se):
            raise UnbalancedPanelError(
                f"feols removed {n_removed} of {len(eta)} observation(s) while residualizing "
                f"'{outcome_var}', and the clustered-SE fallback is non-finite; cannot infer."
            )
        _record_inference_fallback("conley_taber_stacked", outcome_var,
                                   "clustered-SE normal-approximation", n_removed,
                                   f"{n_removed} of {len(eta)} observation(s) removed by feols")
        logging.warning(
            "    conley_taber: feols removed %d of %d observation(s) for '%s'; the panel is "
            "unbalanced so the permutation CI is undefined -- reporting the feols point estimate "
            "with a clustered-SE normal-approximation 95%% CI for this sample "
            "(recorded in output/logs/%s).",
            n_removed, len(eta), outcome_var, _FALLBACK_SIDECAR,
        )
        return (
            np.round(coef, 3),
            np.round(coef - 1.96 * se, 3),
            np.round(coef + 1.96 * se, 3),
        )

    eta[df[df[posttreat_var] == 1].index] += alpha

    stsim = _draw_stsim_clusters(df, group_name, nchst, numbsim, seed=seed)
    alpha025, alpha975 = _run_bounds(
        eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
        stsim, countmax, tol, gamma
    )

    return (
        np.round(alpha[0, 0], 3),
        np.round(alpha025[0, 0], 3),
        np.round(alpha975[0, 0], 3),
    )


def conley_taber_stacked_es(df, outcome_var, posttreat_var, treatment_var,
                             group_name, year_var, index_int, numbsim=None,
                             seed=None, countmax=None, tol=None, gamma=None):
    """
    Conley-Taber event-study variant (single horizon).

    Uses filter_country_ES() from preprocess.R. Returns estimate for the
    event-time period specified by index_int.
    """
    numbsim = numbsim or config.CT_NUMBSIM
    countmax = countmax or config.CT_COUNTMAX
    tol = tol or config.CT_TOL
    gamma = gamma or config.CT_GAMMA

    merit, nchst, nnchst, nyrs, djt = _common_setup(
        df, posttreat_var, treatment_var, group_name, year_var
    )

    # R residualization (event-study)
    r = robjects.r
    _source_preprocess(r)
    filter_fn = robjects.globalenv["filter_country_ES"]
    with localconverter(ro.default_converter + pandas2ri.converter):
        df_r = ro.conversion.py2rpy(df)
    r("gc()")  # bound rpy2/R heap accumulation across the long run (see conley_taber_stacked note)
    df_result_r = filter_fn(df_r, outcome_var)

    coef_vec = np.array(df_result_r[0])
    alpha = np.matrix(coef_vec[index_int])
    eta = np.array(df_result_r[1]).reshape(-1, 1)

    # Same balanced-panel requirement as conley_taber_stacked, and the same two failure modes: feols
    # removed observations (filter_country_ES returns na.rm=FALSE residuals, so NA marks them -> `eta`
    # has NA), OR the treated panel was never balanced (a treated cluster missing a year-row -> the
    # treated pivot `djt` has NA and eta's treated block is short, the _gen_matrix slice ValueError).
    # The second mode surfaces on the SYNTHETIC panels after the co-membership scramble.
    # Either way report this horizon's feols coefficient with a clustered-SE normal-approximation CI so
    # the event-study figure still plots every horizon. Any substitution is recorded in
    # output/logs/inference_method_fallbacks.csv (see the note at the top of this file; the sidecar
    # is the record).
    if np.isnan(eta).any() or np.isnan(djt).any():
        n_removed = int(np.isnan(eta).sum()) + int(np.isnan(djt).sum())
        se_fn = robjects.globalenv["filter_country_es_se"]
        res_se = se_fn(df_r, outcome_var)
        se_vec = np.array(res_se[1])
        coef = float(coef_vec[index_int])
        se = float(se_vec[index_int])
        _record_inference_fallback("conley_taber_stacked_es", outcome_var,
                                   "clustered-SE normal-approximation", n_removed,
                                   f"horizon index {index_int}")
        logging.warning(
            "    conley_taber ES: feols removed %d observation(s) for '%s' (horizon index %d); "
            "unbalanced panel -> feols point estimate with a clustered-SE normal-approx CI "
            "(recorded in output/logs/%s).",
            n_removed, outcome_var, index_int, _FALLBACK_SIDECAR,
        )
        if np.isfinite(coef) and np.isfinite(se):
            return (np.round(coef, 3), np.round(coef - 1.96 * se, 3), np.round(coef + 1.96 * se, 3))
        return (np.round(coef, 3), np.nan, np.nan)   # last resort: plot the point, omit the band

    eta[df[df[posttreat_var] == 1].index] += alpha

    stsim = _draw_stsim_clusters(df, group_name, nchst, numbsim, seed=seed)
    alpha025, alpha975 = _run_bounds(
        eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
        stsim, countmax, tol, gamma
    )

    return (
        np.round(alpha[0, 0], 3),
        np.round(alpha025[0, 0], 3),
        np.round(alpha975[0, 0], 3),
    )


def conley_taber_simple(df, outcome_var, posttreat_var, treatment_var,
                        group_name, year_var, controls=None, numbsim=None,
                        seed=None, countmax=None, tol=None, gamma=None):
    """
    Conley-Taber with pyhdfe residualization.

    Uses Python-side fixed-effect absorption. Accepts optional control
    variables (from Implications_for_reg_design.py variant).
    Samples from integer indices rather than cluster IDs.
    """
    numbsim = numbsim or config.CT_NUMBSIM
    countmax = countmax or config.CT_COUNTMAX
    tol = tol or config.CT_TOL
    gamma = gamma or config.CT_GAMMA
    controls = controls or []

    merit, nchst, nnchst, nyrs, djt = _common_setup(
        df, posttreat_var, treatment_var, group_name, year_var
    )

    # pyhdfe residualization
    variables_list = [outcome_var, posttreat_var] + controls
    FE_list = [group_name, year_var]
    ids = df[FE_list]
    variables = df[variables_list]
    algorithm = pyhdfe.create(ids)
    residualized = algorithm.residualize(variables)

    # pyhdfe.create defaults to drop_singletons=True, so `residualized` can have FEWER rows than df
    # (singleton FE groups removed). The permutation code below indexes eta as a balanced panel and
    # `eta[df[...].index]` uses df's full positional index, so a shorter residual would raise/misalign
    # (the same failure mode as in conley_taber_stacked). The treated panel can ALSO be structurally
    # unbalanced (a treated cluster missing a year-row -> the treated pivot `djt` has NA and _gen_matrix
    # cannot lay the short treated block into the balanced grid) -- this surfaces on the SYNTHETIC panels
    # after the co-membership scramble. In either case the balanced-panel permutation CI is
    # undefined; report the OLS point estimate on the residualized data with a normal-approximation CI so
    # the exhibit still populates. Any substitution is recorded in
    # output/logs/inference_method_fallbacks.csv.
    if residualized.shape[0] != len(df) or np.isnan(djt).any():
        n_removed = (len(df) - residualized.shape[0]) + int(np.isnan(djt).sum())
        y = residualized[:, [0]]
        X = residualized[:, 1:]
        reg = linear_model.LinearRegression().fit(X, y)
        alpha_hat = float(reg.coef_[0, 0])
        resid = (y - reg.predict(X)).flatten()
        n_obs, k = X.shape
        sigma2 = float(resid @ resid) / max(n_obs - k, 1)
        se = float(np.sqrt(sigma2 * np.linalg.pinv(X.T @ X)[0, 0]))
        _record_inference_fallback("conley_taber_simple", outcome_var,
                                   "OLS normal-approximation", n_removed,
                                   "pyhdfe dropped singleton row(s) or the treated pivot has NA")
        logging.warning(
            "    conley_taber_simple: pyhdfe dropped %d singleton row(s) for '%s'; unbalanced panel "
            "-> OLS point estimate with a normal-approximation 95%% CI for this sample "
            "(recorded in output/logs/%s).",
            n_removed, outcome_var, _FALLBACK_SIDECAR,
        )
        if np.isfinite(alpha_hat) and np.isfinite(se):
            return (np.round(alpha_hat, 3), np.round(alpha_hat - 1.96 * se, 3),
                    np.round(alpha_hat + 1.96 * se, 3))
        return (np.round(alpha_hat, 3), np.nan, np.nan)

    y = residualized[:, [0]]
    X = residualized[:, 1:]
    regression = linear_model.LinearRegression()
    regression.fit(X, y)
    alpha = np.matrix(regression.coef_[0, 0])
    prediction = regression.predict(X)
    eta = y - prediction
    eta[df[df[posttreat_var] == 1].index] += alpha

    stsim = _draw_stsim_indices(nchst, nnchst, numbsim, seed=seed)
    alpha025, alpha975 = _run_bounds(
        eta, alpha, djt, merit, nchst, nnchst, nyrs, numbsim,
        stsim, countmax, tol, gamma
    )

    # Return full precision for small estimates (matching original ConleyTaber
    # which only rounds when |alpha| >= 0.1, and then to 10dp).
    # Rounding to 3dp distorts v_serious_rate estimates (~0.001-0.01 scale).
    est = alpha[0, 0]
    lb = alpha025[0, 0]
    ub = alpha975[0, 0]
    if abs(est) >= 0.1:
        return np.round(est, 10), np.round(lb, 10), np.round(ub, 10)
    return est, lb, ub
