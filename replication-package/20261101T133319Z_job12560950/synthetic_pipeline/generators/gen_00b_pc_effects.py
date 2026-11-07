"""
gen_00b_pc_effects.py -- the STRATIFICATION foundation for the publishable simulation.

Every other synthetic generator (gen_00d Full_sample, gen_00e patents, gen_00g KPST)
draws its restricted values conditional on a shared, per-product-code random-effects
table `theta`, so the simulated world *clusters* the way the estimators need (non-
degenerate fixed-effect groups, populated event-time cells, non-degenerate rare
binaries, matched-control availability) -- WITHOUT copying any real restricted cell.

What is read here is PUBLIC only: the product-code list, the reclassification years
(Federal Register), and the never-reclassified control designation (a deterministic
function of the reclassification years). No restricted value is read or emitted.

Outputs (cached, deterministic, seeded) into _synthetic_source_internal/:
  pc_effects.parquet   -- one row per product code: design flags + theta effects
The module also exposes helpers used by the other generators:
  load_theta()                 -> the pc_effects table (builds+caches on first call)
  assign_pc(id_values)         -> hash-based, weight-proportional PC per patent id
                                  (consistent across files; floored weights => support)
  synth_counts(pc, year, ...)  -> per-row counts drawn from theta (Poisson/NegBin)
"""
import os
import sys
import json
import hashlib
import re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DERIVED = os.path.join(ROOT, "data", "derived")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import synthetic_paths

INTERNAL = str(synthetic_paths.internal_dir())
CACHE = os.path.join(INTERNAL, "pc_effects.parquet")
FULL_SAMPLE = os.path.join(DERIVED, "Full_sample.csv")
SYNTH_NUMBER = os.path.join(DERIVED, "RegNum_Factorized_Synth.csv")
GOOD_CONTROLS = os.path.join(ROOT, "data", "raw", "Good_2_1_Control_2_1.txt")
RECALL_JSON = os.path.join(ROOT, "data", "raw", "device-recall-0001-of-0001-2.json")
SEED = 20260708

# --- public design columns read from Full_sample (PUBLIC: FDA + Federal Register) -----
_PUBLIC_DESIGN = ["PRODUCTCODE", "year", "year_reclassified_2_1",
                  "year_reclassified_3_2", "controls"]

# theta hyperparameters -- chosen so the simulated panel has realistic heterogeneity and
# every rare binary stays non-degenerate (base rate ~10-20% with PC-level spread).
_MIN_ELIGIBLE_WEIGHT = 0.35   # floor on the patent sampling weight for reclass/control PCs


def _rng(*tags):
    """A deterministic Generator seeded by SEED + a stable hash of the tags."""
    h = hashlib.md5(("|".join(str(t) for t in tags)).encode()).hexdigest()[:12]
    return np.random.default_rng(SEED + int(h, 16))


def _build():
    """Build the per-PC design + theta table from the PUBLIC Full_sample columns."""
    if not os.path.exists(FULL_SAMPLE):
        raise SystemExit(f"gen_00b: {FULL_SAMPLE} not found (need the real panel to read "
                         "the PUBLIC product-code list + reclassification design).")
    usecols = [c for c in _PUBLIC_DESIGN
               if c in pd.read_csv(FULL_SAMPLE, nrows=0).columns]
    df = pd.read_csv(FULL_SAMPLE, usecols=usecols, low_memory=False)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    g = df.groupby("PRODUCTCODE", sort=True)
    pc = pd.DataFrame(index=g.size().index)
    pc["is_reclass_2_1"] = g["year_reclassified_2_1"].apply(lambda s: s.notnull().any()) \
        if "year_reclassified_2_1" in df else False
    pc["is_reclass_3_2"] = g["year_reclassified_3_2"].apply(lambda s: s.notnull().any()) \
        if "year_reclassified_3_2" in df else False
    pc["is_control"] = g["controls"].max().astype(bool) if "controls" in df else False
    pc["eligible"] = pc["is_reclass_2_1"] | pc["is_reclass_3_2"] | pc["is_control"]

    # Public event years are part of the simulation design, not restricted outcomes.
    # The patent-universe generator uses them to place selected treated support at an
    # observed pre-event panel year. A positive sampling weight alone cannot guarantee
    # that structural match.
    for event in ("2_1", "3_2"):
        col = f"year_reclassified_{event}"
        if col in df:
            pc[col] = g[col].apply(
                lambda s: pd.to_numeric(s, errors="coerce").dropna().iloc[0]
                if pd.to_numeric(s, errors="coerce").notna().any() else np.nan
            )
        else:
            pc[col] = np.nan

    # A patent contributes to gen_01 only when its filing year coincides with a
    # PRODUCTCODE-year row in the public FDA panel. Record an observed year for every
    # code and, where possible, an observed pre-event year for treated codes.
    pc["panel_support_year"] = g["year"].min()
    earliest_event = pc[["year_reclassified_2_1", "year_reclassified_3_2"]].min(axis=1)
    row_event = df["PRODUCTCODE"].map(earliest_event)
    pre_rows = df[row_event.notna() & (df["year"] < row_event)]
    pc["pre_event_support_year"] = pre_rows.groupby("PRODUCTCODE")["year"].max()

    # Selective II->I support is required because gen_01 phase 11 matches controls
    # one-to-one without replacement. Derive both sides from public inputs. Preserve
    # every treated code observed in public recall data (D.15 support), then fill a
    # seeded set to 75% of eligible treated codes, capped by public control capacity.
    required_public = [SYNTH_NUMBER, GOOD_CONTROLS, RECALL_JSON]
    missing_public = [p for p in required_public if not os.path.exists(p)]
    if missing_public:
        raise SystemExit(f"gen_00b: missing public support-design input(s): {missing_public}")

    synth = pd.read_csv(SYNTH_NUMBER, dtype={"REGULATIONNUMBER": str}, low_memory=False)
    synth["REGULATIONNUMBER"] = synth["REGULATIONNUMBER"].str.pad(
        width=8, side="right", fillchar="0"
    )
    synth = synth.drop_duplicates("PRODUCTCODE_x")
    synth["PRODUCTCODE"] = synth["PRODUCTCODE_x"].astype(str)
    with open(GOOD_CONTROLS) as handle:
        chunks = handle.read().split("§")
    good_regnums = set()
    for value in chunks:
        value = value.strip()
        if (re.search(r"\d\d\d+\.+\d", value)
                and not re.search(r"\d\d\d+\.+9", value)):
            good_regnums.add(value[:8])
    good_codes = set(synth.loc[
        synth["REGULATIONNUMBER"].isin(good_regnums), "PRODUCTCODE"
    ])

    has_window = df.loc[(df["year"] > 1991) & (df["year"] <= 1996)].groupby(
        "PRODUCTCODE"
    ).size().index
    has_window = set(has_window)
    control_capacity = set(pc.index[pc["is_control"]]) & good_codes & has_window
    eligible_21 = set(pc.index[
        pc["year_reclassified_2_1"].notna()
        & pc["pre_event_support_year"].notna()
    ]) & has_window

    with open(RECALL_JSON) as handle:
        recall_obj = json.load(handle)
    recall = pd.DataFrame(recall_obj.get("results", recall_obj))
    recall_codes = set(recall["product_code"].dropna().astype(str).str.strip())
    priority = sorted(eligible_21 & recall_codes)
    if len(priority) > len(control_capacity):
        raise ValueError(
            f"public recall-treated support ({len(priority)}) exceeds phase-11 "
            f"control capacity ({len(control_capacity)})"
        )
    target = min(len(control_capacity), max(len(priority), int(0.75 * len(eligible_21))))
    remainder = sorted(eligible_21 - set(priority))
    select_rng = _rng("phase11_support", len(eligible_21), len(control_capacity))
    if target > len(priority):
        chosen = list(select_rng.choice(
            np.asarray(remainder, dtype=object), size=target - len(priority), replace=False
        ))
    else:
        chosen = []
    support_21 = set(priority) | set(chosen)
    pc["support_2_1"] = pc.index.isin(support_21)

    pc["analysis_support_year"] = pc["panel_support_year"]
    treated_21 = pc["year_reclassified_2_1"].notna()
    pc.loc[treated_21 & pc["support_2_1"], "analysis_support_year"] = \
        pc.loc[treated_21 & pc["support_2_1"], "pre_event_support_year"]
    # 1900 is outside the public panel but before treatment, so inactive codes remain
    # valid in supplemental serializations without entering a PRODUCTCODE-year merge.
    pc.loc[treated_21 & ~pc["support_2_1"], "analysis_support_year"] = 1900
    treated_32 = pc["year_reclassified_3_2"].notna()
    pc.loc[treated_32, "analysis_support_year"] = \
        pc.loc[treated_32, "pre_event_support_year"]

    # --- draw theta per PC (deterministic) ---------------------------------------
    rng = _rng("theta")
    n = len(pc)
    pc["lambda_pat"] = np.round(rng.lognormal(mean=1.4, sigma=1.1, size=n), 4)        # patents/PC-yr
    pc["mu_cite"] = np.round(rng.gamma(shape=2.0, scale=6.0, size=n), 4)              # citation level
    pc["mu_xi"] = np.round(rng.lognormal(mean=1.0, sigma=0.9, size=n), 4)            # patent-value level
    pc["p_breakthrough"] = np.round(rng.beta(1.6, 9.0, size=n), 4)                    # ~15% breakthrough
    pc["p_safety"] = np.round(rng.beta(2.0, 7.0, size=n), 4)                          # ~22% safety emphasis
    pc["lambda_ae"] = np.round(rng.lognormal(mean=1.6, sigma=1.2, size=n), 4)         # adverse-event rate
    pc["mu_firmsize"] = np.round(rng.lognormal(mean=4.0, sigma=1.3, size=n), 4)       # firm size level
    pc["mu_price"] = np.round(rng.lognormal(mean=3.5, sigma=0.8, size=n), 4)          # procedure price level
    pc["treat_effect"] = np.round(rng.normal(0.0, 0.25, size=n), 4)                   # synthetic post shift

    # Patent sampling weight is proportional to lambda_pat and floored for codes that
    # can enter matched panels. Exact sample support is enforced separately above.
    w = pc["lambda_pat"].to_numpy(dtype=float)
    w = w / w.mean()
    floor = _MIN_ELIGIBLE_WEIGHT
    w = np.where(pc["eligible"].to_numpy() & (w < floor), floor, w)
    pc["pat_weight"] = np.round(w, 6)

    pc = pc.reset_index()
    os.makedirs(INTERNAL, exist_ok=True)
    pc.to_parquet(CACHE, index=False)
    return pc


def load_theta():
    """Return the per-PC design+theta table, building+caching it on first call."""
    if os.path.exists(CACHE):
        cached = pd.read_parquet(CACHE)
        required = {"year_reclassified_2_1", "year_reclassified_3_2",
                    "panel_support_year", "pre_event_support_year", "support_2_1",
                    "analysis_support_year"}
        if required.issubset(cached.columns):
            return cached
        # Upgrade old caches that had only boolean treatment flags.
    return _build()


# ---- helpers the other generators call --------------------------------------------

def _pc_cdf(theta):
    """Cumulative weight distribution over sorted PRODUCTCODEs for weighted assignment."""
    codes = theta["PRODUCTCODE"].to_numpy()
    w = theta["pat_weight"].to_numpy(dtype=float)
    cdf = np.cumsum(w)
    cdf = cdf / cdf[-1]
    return codes, cdf


def assign_pc(id_values, theta=None):
    """Assign each patent id a synthetic PRODUCTCODE, weight-proportional to theta and
    CONSISTENT across files (a given id value always maps to the same code, via a stable
    hash -> uniform(0,1) -> inverse-CDF over the weighted code list). High-lambda codes
    get more patents (clustering); reclass/control codes have floored weight (support)."""
    theta = load_theta() if theta is None else theta
    codes, cdf = _pc_cdf(theta)
    ids = pd.Series(id_values).astype("string").fillna("∅")
    # stable per-id uniform in [0,1): vectorised value hash (same id value -> same u across
    # every file, so the code assignment is consistent). Deterministic for a fixed pandas.
    h = pd.util.hash_pandas_object(ids, index=False).to_numpy(dtype=np.uint64)
    u = (h % np.uint64(1_000_000_007)).astype(np.float64) / 1_000_000_007.0
    idx = np.searchsorted(cdf, u, side="right")
    idx = np.clip(idx, 0, len(codes) - 1)
    return codes[idx]


def theta_lookup(pc_array, col, theta=None):
    """Map each row's PRODUCTCODE to its theta[col] effect (median-filled for any code
    not in the table). Used to draw patent-level outcomes conditional on the code."""
    theta = load_theta() if theta is None else theta
    lut = theta.set_index("PRODUCTCODE")[col]
    v = lut.reindex(pd.Index(pc_array)).to_numpy(dtype=float)
    return np.where(np.isnan(v), float(np.nanmedian(lut)), v)


def synth_counts(pc_array, base_col, theta=None, post_array=None, rng=None, dispersion=None):
    """Draw a per-row non-negative count from theta[pc][base_col] (a Poisson-ish mean),
    optionally shifted by theta.treat_effect where post_array is truthy. Vectorised."""
    theta = load_theta() if theta is None else theta
    rng = np.random.default_rng(SEED + 7) if rng is None else rng
    lut = theta.set_index("PRODUCTCODE")
    mean = lut[base_col].reindex(pd.Index(pc_array)).to_numpy(dtype=float)
    mean = np.where(np.isnan(mean), np.nanmedian(lut[base_col]), mean)
    if post_array is not None:
        te = lut["treat_effect"].reindex(pd.Index(pc_array)).to_numpy(dtype=float)
        te = np.where(np.isnan(te), 0.0, te)
        mean = mean * (1.0 + te * np.asarray(post_array, dtype=float))
    mean = np.clip(mean, 0.0, None)
    return rng.poisson(mean).astype(float)


# =====================================================================================================
# NOTE (2026-08-08): the former ANONYMITY primitives `resample_identity()` and
# `redraw_missingness()` were DELETED. They PRESERVED an exact real statistic -- resample_identity kept
# the exact real distinct-count AND the exact real group-size multiset; redraw_missingness kept the
# exact real NaN count -- which the re-audit showed leaks restricted structure. gen_00d/gen_00e now
# GENERATE identity columns and missingness from committed ROUNDED cardinalities + SMOOTHED size
# families + ROUNDED rates via independent_universe.generate_identity_column / draw_missingness_rate,
# so no exact real statistic is an input. The structural-fidelity check bans both deleted names
# from the shipped bytes; this module keeps only the PUBLIC theta machinery above.
# =====================================================================================================


if __name__ == "__main__":
    t = _build()
    print(f"gen_00b: built pc_effects for {len(t):,} product codes -> {CACHE}")
    print(f"  reclass_2_1={int(t.is_reclass_2_1.sum())}  reclass_3_2={int(t.is_reclass_3_2.sum())}  "
          f"controls={int(t.is_control.sum())}  eligible={int(t.eligible.sum())}")
    print(f"  lambda_pat: mean={t.lambda_pat.mean():.2f} p90={t.lambda_pat.quantile(.9):.2f}  "
          f"p_breakthrough mean={t.p_breakthrough.mean():.3f}  p_safety mean={t.p_safety.mean():.3f}")
