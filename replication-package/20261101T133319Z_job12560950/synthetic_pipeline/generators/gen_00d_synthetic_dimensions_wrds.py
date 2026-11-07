"""
gen_00d_synthetic_dimensions_wrds.py -- SYNTHETIC Dimensions + WRDS/CRSP-Compustat
stand-in generator (Phase 1 of the simulated-data route).

INDEPENDENT-UNIVERSE REDESIGN (2026-08-08)
-----------------------------------------------------------
This generator now reads NO real restricted data. Every file is built from:
  * the committed interlock spec `params["files"][name]` (Stage-A gen_00a): ROUNDED row count +
    per-column role (public/key/id/num/date) with only ROUNDED cardinalities, SMOOTHED size
    families, and ROUNDED missingness rates -- never an exact real distinct-count, group-size
    multiset, or NaN count;
  * the committed PUBLIC master skeleton (Full_sample's public PC x year design, all public);
  * the fresh synthetic firm/patent universes (universe_backend + independent_universe).
So no shipped synthetic file discloses the exact real (a) column distinct-count, (b) group-size
multiset, (c) per-column NaN count, or (d) file row count -- the four leaks the re-audit flagged
(the demonstrated case: Adverse_fsize's 9,677,786 rows + clean_name's 45,623 distinct multiset).

WHAT IS REAL VS SYNTHETIC (column roles, per the committed spec)
---------------------------------------------------------------
- PUBLIC (STRUCTURE): PRODUCTCODE, year, the reclassification / event-time / treatment design,
  device descriptors, reclass flags -- rebuilt from the committed public master skeleton (public).
- MERGE KEYS (key): permno / LPERMNO / gvkey -- drawn from the shared firm universe so cross-file
  firm joins resolve (no real->fake map anywhere).
- IDENTITY (id): firm / assignee / inventor names, clean_name, stock_name, conm, GRID, orig_* --
  FRESH tokens with a ROUNDED cardinality + SMOOTHED size family + INDEPENDENT co-membership
  (independent_universe.generate_identity_column). The real distinct-count and size multiset are
  NOT inputs, so neither survives.
- NUMERIC (num): restricted outcome values -- drawn (uniform01k), with missingness applied at the
  committed ROUNDED rate (independent_universe.draw_missingness_rate), so the exact NaN count and
  the per-row NaN fingerprint are both gone.

AUTHOR-SIDE generation; outputs ship pre-built. Deterministic (public seed via independent_universe).
"""

import os
import re
import sys
from collections import Counter
import numpy as np
import pandas as pd
from synthetic_seed import seed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
# DERIVED/RAW are retained ONLY so gen_00a (Stage A) can resolve this generator's real-file paths
# when it extracts the committed specs. gen_00d itself NEVER reads from them.
DERIVED = os.path.join(ROOT, "data", "derived")
RAW = os.path.join(ROOT, "data", "raw")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import synthetic_paths

OUT = os.path.join(str(synthetic_paths.internal_dir()), "synthetic_dimensions_wrds")
SEED = seed(12345)
SENTINEL = -99999999999999.0

import gen_00b_pc_effects as pcmod   # shared PC-level random-effects (theta stratification)
import universe_backend as ub        # firm+patent universes + committed specs + public skeleton
import materialize_from_universe as mat
import independent_universe as iu     # fresh id / missingness primitives (no real->fake map)

# --- column classes (kept for reference + public-column derivation) ---------
STRUCTURE = re.compile(
    r"^(PRODUCTCODE.*|year|treatment.*|year_reclass.*|event_time.*|ET|FE|factorized.*|posttreat.*|"
    r"class_by_episode.*|FDA_own_accord.*|use_case|controls|"
    r"Reg_Change_List|REGULATIONNUMBER.*|DEVICECLASS|"
    r"DEVICENAME|DESCRIPTION_OF_REGNUM.*|SUBPART_DESCRIPTION.*|PART_DESCRIPTION.*|SUBMISSION_TYPE_ID.*|"
    r"MDR_REPORT_KEY|DEVICE_PROBLEM_CODE|PROBLEM_DESCRIPTION|Petition.*|date_proposed.*|"
    r"type|indfmt|consol|popsrc|"
    r"datafmt|curcd|costat|file_year|CPI|Unnamed.*|index)$", re.I)
IDENTITY = re.compile(
    r"(gvkey|clean_name|stock_name|assignee|inventor|grid|conm|orig_)", re.I)
LINKKEY = re.compile(r"^(permno|LPERMNO|gvkey|GVKEY)$")

# MASTER_COLS: patent-derived columns every downstream PC-year panel inherits from the SYNTHETIC
# Full_sample (overwritten via _merge_master), so panels carry synthetic (not real) flags.
MASTER_COLS = ["patents_allpats", "patent_sum_2_1", "patent_sum_3_2", "total_pat_sum",
               "use_2_1_treat", "use_3_2_treat", "one_pat_atleast"]
_MASTER = None    # synthetic Full_sample [PRODUCTCODE, year, MASTER_COLS], cached after built

# derived files (CSV + parquet) + one raw WRDS file. 3_2 parquet variants auto-added.
FILES = [
    ("d", "Full_sample.csv"),
    ("d", "matched_pairs_intuitive_2_1.csv"),
    ("d", "safety_did_analysis.csv"), ("d", "safety_did_analysis_3_2.csv"),
    ("d", "all_patents_w_xi_oct22_24.csv"),
    ("d", "intuitive_2_1_oct22_24.csv"), ("d", "intuitive_3_2_oct22_24_similarity.csv"),
    ("d", "intuitive_spillovers_3_2_oct22_24.csv"),
    ("d", "later_treated_2_1_oct22_24.csv"), ("d", "later_treated_3_2_oct22_24.csv"),
    ("d", "spillovers_2_1_oct22_24.csv"),
    ("d", "frequency_df_2to1_variety.csv"), ("d", "frequency_df_3to2_variety.csv"),
    ("d", "all_adv_events_w_permno5.csv"),
    ("d", "Adverse_fsize_ready_all4_oct22_24.csv"),
    ("d", "data_2_1_full.parquet"), ("d", "data_2_1_intuitive.parquet"),
    ("d", "data_2_1_latertreat.parquet"), ("d", "data_2_1_spillovers.parquet"),
    ("r", "compustat_firm_data.csv"),
]
for base in ("data_3_2_full", "data_3_2_intuitive", "data_3_2_latertreat", "data_3_2_spillovers"):
    if os.path.exists(os.path.join(DERIVED, base + ".parquet")):
        FILES.append(("d", base + ".parquet"))

# Anchors that generate directly from the fresh universe (schema from the committed spec order).
ANCHORS = {"Full_sample.csv", "all_patents_w_xi_oct22_24.csv", "compustat_firm_data.csv"}


# ==========================================================================================
# generic column primitives (all seeded by the PUBLIC seed via independent_universe.iu_rng)
# ==========================================================================================
def _num_column(n, missing_rate, salt):
    """A numeric value column: draw every cell uniform01k, then apply missingness at the COMMITTED
    ROUNDED rate (~Binomial(n, rate)) -- never the exact real NaN count, never the real NaN pattern."""
    rng = iu.iu_rng("num", salt, n)
    out = np.round(rng.uniform(0, 1000, size=int(n)), 3)
    if missing_rate and float(missing_rate) > 0:
        out[iu.draw_missingness_rate(int(n), float(missing_rate), salt)] = np.nan
    return out


def _date_column(kind, n, salt):
    """A synthetic date column. fyear -> a synthetic fiscal year (float); datadate -> YYYY-MM-DD."""
    rng = iu.iu_rng("date", salt, n)
    yy = rng.integers(1985, 2019, size=int(n))
    if kind == "fyear":
        return yy.astype(float)
    mm = rng.integers(1, 13, size=int(n)); dd = rng.integers(1, 29, size=int(n))
    return np.array([f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in zip(yy, mm, dd)], dtype=object)


def _id_column(n, spec, salt):
    """A NON-merge identity column: FRESH tokens with the committed ROUNDED cardinality + SMOOTHED
    size family + independent co-membership. No real distinct-count or size multiset is an input."""
    return iu.generate_identity_column(int(n), int(spec.get("cardinality", 1)),
                                       spec.get("size_family", {"kind": "uniform"}), salt,
                                       numeric=bool(spec.get("numeric", False)))


def _coalesce_reclass(skel):
    """Per-row reclassification year = year_reclassified_2_1 if present else year_reclassified_3_2
    (NaN for never-reclassified controls). Used to derive the public event-study design columns."""
    n = len(skel)
    y21 = (pd.to_numeric(skel["year_reclassified_2_1"], errors="coerce").to_numpy(dtype=float)
           if "year_reclassified_2_1" in skel.columns else np.full(n, np.nan))
    y32 = (pd.to_numeric(skel["year_reclassified_3_2"], errors="coerce").to_numpy(dtype=float)
           if "year_reclassified_3_2" in skel.columns else np.full(n, np.nan))
    return np.where(~np.isnan(y21), y21, y32)


# small synthetic public MAUDE vocab (device-problem taxonomy is public; the SET tied to a device
# is what re-identifies, so synthetic per-row codes preserve the public categorical without a leak).
_DPC_CODES = [str(c) for c in range(1000, 1120)]
_DPC_DESC = [f"synthetic device problem {i}" for i in range(60)]


def _public_column(col, skel, spec, salt, episode=None, reclass_col=None):
    """Value for a PUBLIC (STRUCTURE) column, WITHOUT reading real data. If the column is in the
    committed public master skeleton, take it verbatim (public design). Otherwise DERIVE the public
    event-study design from (year, reclassification year) or draw a public categorical. Everything
    here is public by construction (FDA/Federal-Register design + calendar + MAUDE taxonomy).

    `episode` (per-row stack index from _sample_public_skeleton) distinguishes stacks in a TILED
    panel so the stacked-DiD grouping keys (FE / class_by_episode) stay UNIQUE per (stack, unit,
    year) -- see _sample_public_skeleton. The unit key (`factorized`) does NOT use the episode."""
    n = len(skel)
    c = str(col); cl = c.lower()
    if c in skel.columns:
        return skel[c].to_numpy()
    year = (pd.to_numeric(skel["year"], errors="coerce").to_numpy(dtype=float)
            if "year" in skel.columns else np.full(n, np.nan))
    # For a RECLASS-SPECIFIC panel (data_2_1_* / data_3_2_* / the intuitive-later-spillovers panels), the
    # treatment / year_reclassified / posttreat / event_time columns must key on THAT panel's own
    # reclassification column only -- NOT the 2_1-OR-3_2 coalesce. Otherwise the II->I "Full" panel
    # (data_2_1_full) flags the 3->2-reclassified codes as treated too, inflating the D.1 treated count
    # to 356+29=385 > the 356 II->I universe (10c generate_d1 QC). The master (Full_sample) has both
    # reclassifications by design and passes reclass_col=None -> keeps the coalesce.
    yre = (pd.to_numeric(skel[reclass_col], errors="coerce").to_numpy(dtype=float)
           if reclass_col and reclass_col in skel.columns else _coalesce_reclass(skel))
    treated = ~np.isnan(yre)
    if cl in ("year_reclassified", "year_reclassfinal", "year_reclassified_controls"):
        return yre
    if cl.startswith("treatment") or cl == "treated":
        return treated.astype(float)
    if cl == "posttreat" or cl.startswith("posttreat"):
        return np.where(treated & (year >= yre), 1.0, 0.0)
    if cl in ("event_time", "et", "year_reclass_et") or cl.startswith("event_time") or cl.startswith("year_reclass_et"):
        return year - yre                                   # NaN for controls (same as real)
    if cl in ("factorized", "fe") or cl.startswith("factorized") or cl.startswith("class_by_episode"):
        pcodes = (skel["PRODUCTCODE"].astype(str).to_numpy()
                  if "PRODUCTCODE" in skel.columns else np.arange(n).astype(str))
        ep = (np.asarray(episode) if episode is not None and len(episode) == n
              else np.zeros(n, dtype=np.int64))
        # `factorized` = UNIT key (PRODUCTCODE only). `class_by_episode` = STACK x UNIT key
        # (episode-distinguished). `FE` = the STACK index (episode) ALONE.
        if cl == "factorized" or cl.startswith("factorized"):
            return pd.factorize(pcodes)[0].astype(float)
        if cl.startswith("class_by_episode"):
            keys = np.array([f"{int(e)}|{p}|{int(t)}" for e, p, t in zip(ep, pcodes, treated)], dtype=object)
            return pd.factorize(keys)[0].astype(float)
        # FE must be the STACK index only. The stacked estimators absorb `factorized^FE` (unit-in-
        # stack) AND `year^FE` (year-in-stack) via fixest. If FE encoded (episode|PC), then `year^FE`
        # would be (year, stack, unit): every (year, FE) cell is a lone row, feols drops them all as
        # singletons, and posttreat is absorbed -> "posttreat is collinear with the fixed effects"
        # (the II->I 03b regression). FE = episode keeps year^FE = (year, stack), so the within-stack
        # DiD contrast survives. (FE, factorized, year) stays unique: the stacked skeleton never
        # repeats a (stack, PC, year) triple.
        return np.asarray(ep, dtype=float)
    if cl.startswith("unnamed") or cl == "index":
        return np.arange(n)
    if cl == "mdr_report_key":
        return iu.iu_rng("mdr", salt, n).integers(1_000_000, 9_999_999, size=n)
    if cl == "device_problem_code":
        return iu.iu_rng("dpc", salt, n).choice(_DPC_CODES, size=n)
    if cl == "problem_description":
        return iu.iu_rng("pdesc", salt, n).choice(_DPC_DESC, size=n)
    if cl == "file_year":
        return iu.iu_rng("fileyr", salt, n).integers(1995, 2019, size=n).astype(float)
    if cl == "cpi":
        return np.round(iu.iu_rng("cpi", salt, n).uniform(150, 260, size=n), 3)
    # fallback: keep the column present + typed (a public constant token / zero -- no real value)
    dt = str(spec.get("dtype", "object"))
    if "float" in dt or "int" in dt:
        return np.zeros(n, dtype=float)
    return np.array([f"PUB_{c}"] * n, dtype=object)


def _cast_dtype(arr, dt):
    """Best-effort cast a generated column to its committed dtype (schema fidelity). Leaves the
    column as-is when a cast is impossible (e.g. NaN in an int column stays float)."""
    if dt is None:
        return arr
    try:
        s = pd.Series(arr)
        if dt.startswith("int"):
            return s.astype("int64").to_numpy() if not s.isna().any() else s.to_numpy()
        if dt.startswith("float"):
            return pd.to_numeric(s, errors="coerce").astype("float64").to_numpy()
        if dt == "bool":
            return s.astype(bool).to_numpy()
    except (ValueError, TypeError):
        return arr
    return arr


# ==========================================================================================
# Full_sample.csv -- the master PC-year panel. Public columns from the committed public master
# skeleton; patent/firm/safety values are theta-conditioned synthetic DRAWS; patent-derived flags
# re-derived from the synthetic patents_allpats (gen_01's exact formulas). See DGP_DESIGN.md.
# ==========================================================================================
_FS_PUBLIC = {
    "PRODUCTCODE", "Reg_Change_List", "use_case", "REGULATIONNUMBER", "DEVICECLASS",
    "SUBMISSION_TYPE_ID", "DEVICENAME", "DESCRIPTION_OF_REGNUM", "SUBPART_DESCRIPTION",
    "year", "FDA_own_accord", "DESCRIPTION_OF_REGNUM_3_2", "year_reclassified_3_2",
    "FDA_own_accord_3_2", "PART_DESCRIPTION_3_2", "Petition_DeNovo_Filing_Date_3_2",
    "REGULATIONNUMBER_3_2", "date_proposed_3_2", "SUBMISSION_TYPE_ID_3_2",
    "SUBPART_DESCRIPTION_3_2", "year_reclassified_2_1", "controls",
}
_FS_REDERIVED = {"patent_sum_2_1", "patent_sum_3_2", "total_pat_sum", "one_pat_atleast",
                 "use_2_1_treat", "use_3_2_treat"}
_FS_COUNT_FAMILY = re.compile(
    r"^(patents_(newfirmPC|newfirm|pats_nodrugs)|"
    r"(Archive|Company|Education|Facility|Government|Healthcare|Nonprofit|Other)"
    r"_(allpats|newfirmPC|newfirm))$")
_FS_SAFETY_MATRIX = re.compile(r"^[A-Z]$|^[A-Z]_[A-Z]$")


def _rederive_full_sample(df):
    """Re-derive patent-derived flags from the synthetic patents_allpats, EXACTLY as
    gen_01_main_panels.py, so use_*_treat / patent_sum_* / one_pat_atleast are internally
    consistent with the synthetic counts (and leak no real 'had-patents')."""
    yr = pd.to_numeric(df["year"], errors="coerce")
    y21 = pd.to_numeric(df.get("year_reclassified_2_1"), errors="coerce")
    y32 = pd.to_numeric(df.get("year_reclassified_3_2"), errors="coerce")
    if "controls" not in df:
        df["controls"] = 0
    df["patent_sum_2_1"] = df[(yr < y21) & y21.notnull()].groupby(
        "PRODUCTCODE")["patents_allpats"].transform("sum")
    df["patent_sum_2_1"] = df.groupby("PRODUCTCODE")["patent_sum_2_1"].transform(lambda v: v.ffill())
    df["use_2_1_treat"] = 0
    df.loc[(df["controls"] == 1) | (df["patent_sum_2_1"] > 0), "use_2_1_treat"] = 1
    df["patent_sum_3_2"] = df[(yr < y32) & y32.notnull()].groupby(
        "PRODUCTCODE")["patents_allpats"].transform("sum")
    df["patent_sum_3_2"] = df.groupby("PRODUCTCODE")["patent_sum_3_2"].transform(lambda v: v.ffill())
    df["use_3_2_treat"] = 0
    df.loc[(df["controls"] == 1) | (df["patent_sum_3_2"] > 0), "use_3_2_treat"] = 1
    df["total_pat_sum"] = df.groupby("PRODUCTCODE")["patents_allpats"].transform("sum")
    df["one_pat_atleast"] = 0
    df.loc[df["total_pat_sum"] > 0, "one_pat_atleast"] = 1


def process_full_sample(order, cols, master_pub, theta):
    """Build the 110-col master from the committed public skeleton (public cols) + theta (outcomes)
    + committed specs (id/num). Row count = public panel size (public PC x year design)."""
    df = pd.DataFrame({c: master_pub[c].to_numpy() for c in master_pub.columns})
    n = len(df)
    rng = iu.iu_rng("Full_sample", SEED, n)
    pc = df["PRODUCTCODE"].astype(str).to_numpy()
    year = pd.to_numeric(df["year"], errors="coerce").fillna(0).to_numpy(dtype=float)
    y21 = (pd.to_numeric(df.get("year_reclassified_2_1", pd.Series([np.nan] * n)),
                         errors="coerce").to_numpy(dtype=float))
    y32 = (pd.to_numeric(df.get("year_reclassified_3_2", pd.Series([np.nan] * n)),
                         errors="coerce").to_numpy(dtype=float))
    post = np.clip(np.nan_to_num((year >= y21).astype(float)) +
                   np.nan_to_num((year >= y32).astype(float)), 0, 1)
    lam = pcmod.theta_lookup(pc, "lambda_pat", theta)
    te = pcmod.theta_lookup(pc, "treat_effect", theta)
    mu_cite = pcmod.theta_lookup(pc, "mu_cite", theta)
    mu_xi = pcmod.theta_lookup(pc, "mu_xi", theta)
    mu_fs = pcmod.theta_lookup(pc, "mu_firmsize", theta)
    p_saf = pcmod.theta_lookup(pc, "p_safety", theta)
    lam_ae = pcmod.theta_lookup(pc, "lambda_ae", theta)
    yr_norm = np.clip((year - 1995) / 25.0, -1.2, 1.2)
    shift = 1.0 + te * post
    patents_allpats = rng.poisson(np.clip(lam * (1 + 0.3 * yr_norm) * shift, 0, None)).astype(float)
    _newfirmPC_vals = np.round(patents_allpats * rng.uniform(0.20, 0.70, size=n))
    _newfirm_vals = np.round(_newfirmPC_vals * rng.uniform(0.0, 0.85, size=n))

    for col in order:
        c = str(col)
        if c in _FS_PUBLIC or c in _FS_REDERIVED:
            continue                                  # public kept (from skeleton); flags re-derived
        if c == "patents_allpats":
            df[col] = patents_allpats
        elif c == "patents_newfirmPC":
            df[col] = _newfirmPC_vals
        elif c == "patents_newfirm":
            df[col] = _newfirm_vals
        elif _FS_COUNT_FAMILY.match(c):
            df[col] = np.round(patents_allpats * rng.uniform(0.05, 0.7)).astype(float)
        elif c in ("times_cited", "times_cited_outside_ind"):
            df[col] = rng.poisson(mu_cite).astype(float)
        elif c == "xi_real":
            df[col] = np.round(mu_xi * rng.lognormal(0, 0.5, n) * shift, 4)
        elif c == "firm_size":
            df[col] = np.round(mu_fs * rng.lognormal(0, 0.4, n), 3)
        elif c == "dev_count":
            df[col] = rng.poisson(np.clip(1 + 0.5 * lam * shift, 0, None)).astype(float)
        elif c in ("firm_count", "absnew_firm_count"):
            df[col] = rng.poisson(np.clip(0.5 + 0.3 * lam, 0, None)).astype(float)
        elif c == "event_count":
            df[col] = rng.poisson(np.clip(lam_ae * shift, 0, None)).astype(float)
        elif c == "PRODUCTCODE_COUNT":
            df[col] = (rng.poisson(5, n) + 1).astype(int)
        elif _FS_SAFETY_MATRIX.match(c):
            df[col] = rng.poisson(np.clip(p_saf * 3 * shift, 0, None)).astype(float)
        else:
            spec = cols.get(c, {"role": "num", "missing_rate": 0.0})
            role = spec.get("role")
            if role == "id":
                df[col] = _id_column(n, spec, "Full_sample|" + c)
            elif role == "key":
                df[col] = ub.assign_firm_rows(n, "Full_sample|" + c)
            elif role == "date":
                df[col] = _date_column(spec.get("kind", "datadate"), n, "Full_sample|" + c)
            elif role == "public":
                df[col] = _public_column(c, master_pub, spec, "Full_sample|" + c)
            else:
                df[col] = _num_column(n, spec.get("missing_rate", 0.0), "Full_sample|" + c)
    df["patents_allpats"] = patents_allpats           # ensure set regardless of column order
    _rederive_full_sample(df)
    df = df[[c for c in order]]                        # committed column order (schema fidelity)
    global _MASTER
    keep = ["PRODUCTCODE", "year"] + [c for c in MASTER_COLS if c in df.columns]
    _MASTER = df[keep].copy()
    return df


def _merge_master(df, name):
    """Overwrite a downstream PC-year panel's patent-derived columns with the SYNTHETIC master
    (Full_sample) values, joined on (PRODUCTCODE, year). Fail-closed on any unmatched panel key."""
    if _MASTER is None or "PRODUCTCODE" not in df.columns:
        return df
    cols = [c for c in MASTER_COLS if c in df.columns]
    if not cols:
        return df
    key = ["PRODUCTCODE", "year"] if "year" in df.columns and "year" in _MASTER.columns else ["PRODUCTCODE"]
    m = _MASTER[key + [c for c in cols if c in _MASTER.columns]].drop_duplicates(subset=key)
    merged = df.merge(m, on=key, how="left", suffixes=("", "_master"), indicator=True)
    unmatched_keys = int((merged["_merge"] == "left_only").sum())
    if unmatched_keys:
        raise SystemExit(f"gen_00d {name}: {unmatched_keys} rows have no synthetic-master (PRODUCTCODE"
                         f", year) key on {key} -- cannot inherit synthetic patent-derived values. "
                         f"Refusing to ship. Fix the public-skeleton coverage.")
    merged = merged.drop(columns=["_merge"])
    n_over = 0
    for c in cols:
        mc = c + "_master"
        if mc in merged.columns:
            df[c] = merged[mc].where(merged[mc].notna(), df[c].values).values
            n_over += 1
    return df, n_over


# ==========================================================================================
# all_patents_w_xi_oct22_24.csv -- the canonical patent universe projected to the real schema.
# ==========================================================================================
_AP_IND = re.compile(r"^(patents|Archive|Company|Education|Facility|Government|"
                     r"Healthcare|Nonprofit|Other)$")


def _allpatents_roles(order, cols):
    """Independent-universe role map for all_patents_w_xi: keys + outcomes from the canonical patent
    universe; identity columns become fresh tokens; remaining numerics drawn. No real read; column
    dtype comes from the committed spec, never from a real frame."""
    roles = {}
    for col in order:
        c = str(col); cl = c.lower()
        dt = str(cols.get(c, {}).get("dtype", "object"))
        is_num = dt.startswith("int") or dt.startswith("float")
        if c == "PRODUCTCODE":
            roles[c] = ("universe", "PRODUCTCODE")
        elif c in ("id", "patnum", "patent_id"):
            roles[c] = ("universe", "patnum")
        elif c == "application_id":
            roles[c] = ("value", {"kind": "uniform_int", "lo": 10_000_000, "hi": 89_000_000})
        elif cl in ("permno", "lpermno"):
            roles[c] = ("universe", "permno")
        elif c == "year":
            roles[c] = ("universe", "filing_year")
        elif c == "cites":
            roles[c] = ("universe", "cites")
        elif c in ("xi_real", "xi_nominal"):
            roles[c] = ("universe", "xi")
        elif c == "patents":
            roles[c] = ("const", 1)
        elif _AP_IND.match(c):
            roles[c] = ("value", {"kind": "bernoulli", "p": 0.2})
        elif c == "firm_size":
            roles[c] = ("value", {"kind": "lognormal", "mu": 4.0, "sigma": 0.4})
        elif c == "CPI":
            roles[c] = ("value", {"kind": "lognormal", "mu": 5.0, "sigma": 0.15})
        elif c == "GRID":
            roles[c] = ("value", {"kind": "tokens", "prefix": "grid.", "cardinality": 7000})
        elif IDENTITY.search(c) or not is_num:
            tag = re.sub(r"[^A-Za-z0-9]", "", c)[:6]
            card = int(cols.get(c, {}).get("cardinality", 2000)) or 2000
            roles[c] = ("value", {"kind": "tokens", "prefix": f"SYN{tag}_", "cardinality": card})
        else:
            roles[c] = ("value", {"kind": "lognormal", "mu": 1.0, "sigma": 1.0})
    return roles


def process_all_patents(order, cols, theta):
    """all_patents_w_xi = the patent universe projected to the real schema. Row count = committed
    rounded patent cardinality (len(universe)); patnum/permno/PC fresh + join-consistent."""
    pu = ub.patent_universe()
    roles = _allpatents_roles(order, cols)
    out = mat.materialize("all_patents_w_xi", order, roles, len(pu), sampled_universe=pu,
                          salt="all_patents")
    # `id` is the wrapped "US-<n>-<kind>" string; `patent_id`/`patnum` are the plain number. Decide by
    # the committed dtype (object -> plain digit string; numeric -> int), consistent across files.
    for c in out.columns:
        if c == "id":
            out[c] = "US-" + pd.Series(out["patnum"]).astype("int64").astype(str) + "-B2"
        elif c == "patent_id":
            dt = str(cols.get(c, {}).get("dtype", "int64"))
            if dt == "object":
                out[c] = pd.Series(out["patnum"]).astype("int64").astype(str).values
    return out


def process_compustat(order, cols):
    """compustat = the canonical FIRM universe (permno+gvkey PAIRED), one row per firm-year. Row
    count = committed rounded cardinality; EVERY universe firm appears >=1 time (firm joins never
    drop). fyear/datadate synthetic; conm a fresh token; financials drawn. No real read."""
    params = ub.load_params()
    n_rows = int(params["entities"].get("firms_permno", {}).get("n_rows", 280_000))
    permno, gvkey = ub.assign_firm_pairs(n_rows, salt="compustat")
    drng = iu.iu_rng("compustat_dates", n_rows)
    yy = drng.integers(1985, 2019, size=n_rows); mm = drng.integers(1, 13, size=n_rows)
    dd = drng.integers(1, 29, size=n_rows)
    datadate = np.array([f"{y:04d}-{m:02d}-{d:02d}" for y, m, d in zip(yy, mm, dd)], dtype=object)
    roles = {}
    for col in order:
        c = str(col); cl = c.lower()
        if cl == "lpermno" or c == "LPERMNO":
            roles[c] = ("public", permno)
        elif cl == "gvkey" or c == "GVKEY":
            roles[c] = ("public", gvkey)
        elif cl == "datadate":
            roles[c] = ("public", datadate)
        elif cl == "fyear":
            roles[c] = ("value", {"kind": "uniform_int", "lo": 1985, "hi": 2019})
        elif c == "conm":
            roles[c] = ("value", {"kind": "tokens", "prefix": "FIRM_", "cardinality": 26_000})
        elif c in ("indfmt", "consol", "popsrc", "datafmt", "curcd", "costat"):
            roles[c] = ("value", {"kind": "tokens", "prefix": c[:3] + "_", "cardinality": 4})
        elif str(cols.get(c, {}).get("dtype", "object")).startswith(("int", "float")):
            roles[c] = ("value", {"kind": "lognormal", "mu": 3.0, "sigma": 1.5})
        else:
            roles[c] = ("value", {"kind": "tokens", "prefix": "V_", "cardinality": 100})
    return mat.materialize("compustat_firm_data", order, roles, n_rows, salt="compustat")


# ==========================================================================================
# STACKED-DiD SUBSAMPLE PANELS -- whole-product-code straddle skeleton (fixes the derived-input
# regression where 03a/03b/07's `posttreat | class_by_episode + year` was "collinear with the fixed
# effects"). These panels feed the stacked event-study estimators; each must carry every treated PC's
# FULL public year range so the treated unit STRADDLES its public reclassification year (pre + post)
# within its FE/stack class. A random (PC,year) CELL sample (the generic sampler) fragments each PC's
# years, so treated units never straddle and posttreat is absorbed. The simulated-data route builds these via
# code/00_generate_data/gen_04_parquets.py (+ gen_01) with proper event-time windows; this reproduces
# that structure directly from the committed PUBLIC master skeleton (public columns only, no real read).
# name -> the public reclassification-year column that defines "treated" for that panel.
_STRADDLE_PANELS = {
    "intuitive_2_1_oct22_24.csv": "year_reclassified_2_1",
    "later_treated_2_1_oct22_24.csv": "year_reclassified_2_1",
    "spillovers_2_1_oct22_24.csv": "year_reclassified_2_1",
    "data_2_1_intuitive.parquet": "year_reclassified_2_1",
    "data_2_1_latertreat.parquet": "year_reclassified_2_1",
    "data_2_1_spillovers.parquet": "year_reclassified_2_1",
    "intuitive_3_2_oct22_24_similarity.csv": "year_reclassified_3_2",
    "later_treated_3_2_oct22_24.csv": "year_reclassified_3_2",
    "intuitive_spillovers_3_2_oct22_24.csv": "year_reclassified_3_2",
    "data_3_2_intuitive.parquet": "year_reclassified_3_2",
    "data_3_2_latertreat.parquet": "year_reclassified_3_2",
    "data_3_2_spillovers.parquet": "year_reclassified_3_2",
    # The safety-emphasis event-study DiD panels (06a_safety_analysis.py output on the simulated-data route):
    # 04_event_studies reads them PRE-STACKED and uses their posttreat/ET directly -- if no treated unit
    # straddles its reclass year, posttreat is all-zero and 04:252 `df[df.posttreat>0].index[0]` raises
    # IndexError -> the 2_1_nolog_safety_prop figure is never written (step-36 audit_pipeline "missing
    # figure"). So build them like the pre-stacked parquets (one stack per treated PC + controls).
    "safety_did_analysis.csv": "year_reclassified_2_1",
    "safety_did_analysis_3_2.csv": "year_reclassified_3_2",
}

# Straddle CSV panels that 04 consumes ALREADY-STACKED (not re-stacked at runtime like the intuitive/
# later CSVs that 03a stacks) -> build them with the pre-stacked (gen_04 _stack_FE) skeleton, not the
# unstacked whole-PC one, so their committed FE/class_by_episode/posttreat/ET are a live DiD contrast.
_STACKED_CSV_PANELS = {"safety_did_analysis.csv", "safety_did_analysis_3_2.csv"}


def _balanced_year_grid(mp, year):
    """Group the master rows by PRODUCTCODE onto the SINGLE dominant public year grid (the modal set of
    calendar years > 0, i.e. 1976-2019). Return (pos_by_pc, n_years) where pos_by_pc maps each PC that
    covers that grid EXACTLY to its year-sorted row indices ON the grid (the year==0 sentinel dropped);
    PCs that do not cover the grid are omitted. Every kept PC then has exactly n_years rows, so every
    emitted (stack, PC) cluster is a complete year block -- the balanced cluster-by-year layout the
    stacked permutation estimator (code/modules/conley_taber.py::_gen_matrix) requires. An off-grid PC
    would give a short/long residual block -> ValueError 'cannot assign slice from input of different
    size'. Public design only; deterministic."""
    raw = mp.groupby("PRODUCTCODE", sort=True).indices
    ys = {p: frozenset(int(v) for v in year[ix] if v > 0) for p, ix in raw.items()}
    modal = Counter(ys.values()).most_common(1)[0][0]
    modal_arr = np.array(sorted(modal))
    bal = {}
    for p, ix in raw.items():
        if ys[p] == modal:
            keep = ix[np.isin(year[ix], modal_arr)]
            bal[p] = keep[np.argsort(year[keep])]
    return bal, len(modal_arr)


def _classify_treated_controls(bal, year, yre, ctrl):
    """Split the balanced-grid PCs into treated STRADDLERS (reclass year inside the grid -> pre + post
    rows) and never-treated CONTROLS. Deterministic (bal is in sorted-PC order)."""
    treated, controls = [], []
    for p, ix in bal.items():
        rv = yre[ix]; rv = rv[~np.isnan(rv)]
        if rv.size:
            r0 = float(rv[0]); yy = year[ix]
            if np.any((yy > 0) & (yy < r0)) and np.any(yy >= r0):
                treated.append(p)
        elif ctrl is None or bool(np.any(ctrl[ix] == 1)):
            controls.append(p)
    return treated, controls


def _sample_straddle_skeleton(master_pub, n_rows, reclass_col, salt):
    """Return (skeleton_rows, episode) for an UNSTACKED per-PC subsample CSV (intuitive/later/spillovers
    CSVs, read + stacked at runtime by 03a). Whole balanced product codes only, treated straddlers
    interleaved 1:1 with controls, ~round(n_rows / n_years) of them (so row count ~= the committed
    rounded n_rows while every PC stays a complete year block for the downstream stacked estimator).
    Single episode (03a builds its own FE stacks). Public columns only; no real read; deterministic."""
    mp = master_pub.reset_index(drop=True)
    N = len(mp); n = int(n_rows)
    if N == 0 or n <= 0:
        return mp.iloc[0:0].copy(), np.zeros(0, dtype=np.int64)
    if reclass_col not in mp.columns or "PRODUCTCODE" not in mp.columns or "year" not in mp.columns:
        return _sample_public_skeleton(master_pub, n_rows, salt)          # fail-safe: generic sampler
    year = pd.to_numeric(mp["year"], errors="coerce").to_numpy(dtype=float)
    yre = pd.to_numeric(mp[reclass_col], errors="coerce").to_numpy(dtype=float)
    ctrl = (pd.to_numeric(mp["controls"], errors="coerce").fillna(0).to_numpy()
            if "controls" in mp.columns else None)
    bal, ny = _balanced_year_grid(mp, year)
    treated, controls = _classify_treated_controls(bal, year, yre, ctrl)
    if not treated or not controls:
        return _sample_public_skeleton(master_pub, n_rows, salt)          # fail-safe (should not hit)
    seq, ti, ci = [], 0, 0                               # interleave treated straddlers with controls
    while ti < len(treated) or ci < len(controls):
        if ti < len(treated):
            seq.append(treated[ti]); ti += 1
        if ci < len(controls):
            seq.append(controls[ci]); ci += 1
    # whole balanced PCs, sized to the LARGEST k*n_years that does not EXCEED the committed rounded
    # n_rows (floor, not round). Rounding up can land exactly on the real file size (e.g. 23*44 = 1,012
    # = the real later_treated_3_2), which the tree audit fail-closes on ("exact real row count"); the
    # floor value stays a rounded-order count, is a multiple of n_years (balance), and keeps >5 treated.
    m = max(1, int(n // ny))
    seq = seq[:m]
    idx = np.concatenate([bal[p] for p in seq])          # every PC a complete year block; (PC,year) unique
    episode = np.zeros(len(idx), dtype=np.int64)
    return mp.iloc[idx].reset_index(drop=True), episode


def _sample_stacked_skeleton(master_pub, n_rows, reclass_col, salt):
    """Return (skeleton_rows, episode) for a PRE-STACKED subsample parquet (data_2_1_* / data_3_2_*),
    reproducing code/00_generate_data/gen_04_parquets.py::_stack_FE: one stack per treated PC, each
    stack = that ONE treated PC (whole, straddling its public reclassification year) PLUS a fixed pool
    of never-treated CONTROL PCs (duplicated into every stack). `episode` = the STACK index, which
    _public_column emits as the `FE` column. This is the structure 03b/07 need: fixest absorbs
    `factorized^FE` (unit-in-stack) and `year^FE` (year-in-stack); with FE = stack, each (year, stack)
    cell holds one treated + the controls, so posttreat is a live within-stack DiD contrast rather than
    a dropped singleton. Every PC is a COMPLETE year block (balanced grid), so each cluster has exactly
    n_years rows -- required by the stacked permutation estimator. Only whole balanced stacks are
    emitted, so the row total is the nearest achievable multiple of the stack size to the committed
    rounded n_rows (exact n_rows is generally unreachable with a balanced grid, and a partial trailing
    stack would reintroduce the unbalanced-cluster ValueError). (stack, PC, year) never repeats, so
    (FE, factorized, year) is unique. The stack count and controls-per-stack are derived from n_rows +
    the public n_years alone, never a real count. Public columns only; no real read; deterministic."""
    mp = master_pub.reset_index(drop=True)
    N = len(mp); n = int(n_rows)
    if N == 0 or n <= 0:
        return mp.iloc[0:0].copy(), np.zeros(0, dtype=np.int64)
    if reclass_col not in mp.columns or "PRODUCTCODE" not in mp.columns or "year" not in mp.columns:
        return _sample_public_skeleton(master_pub, n_rows, salt)
    year = pd.to_numeric(mp["year"], errors="coerce").to_numpy(dtype=float)
    yre = pd.to_numeric(mp[reclass_col], errors="coerce").to_numpy(dtype=float)
    ctrl = (pd.to_numeric(mp["controls"], errors="coerce").fillna(0).to_numpy()
            if "controls" in mp.columns else None)
    bal, ny = _balanced_year_grid(mp, year)
    treated, controls = _classify_treated_controls(bal, year, yre, ctrl)
    if not treated or not controls:
        return _sample_public_skeleton(master_pub, n_rows, salt)
    # Balanced like gen_04 (~k treated stacks x ~c controls, k ~= c ~= sqrt(n_rows / n_years)). c and k
    # are derived from the committed n_rows + public n_years ALONE, so no real treated/control count is
    # disclosed. Whole balanced stacks only -> the row total is a multiple of the stack size (a partial
    # trailing stack would reintroduce the unbalanced-cluster ValueError).
    #   JPE privacy (ship a ROUNDED row count -- never the exact real file size): the safety-DiD CSVs are
    # consumed already-stacked, so their emitted row total is the file size a reviewer sees. n_rows is
    # round_cardinality-clean (2 sig figs, != the non-round real). When the public year span divides it,
    # the generator factors m = n_rows/ny into a near-square k*(1+c) and emits EXACTLY the rounded
    # n_rows -- a rounded count that cannot reproduce a non-round real size. (Snapping to the NEAREST multiple can, by
    # coincidence, land back on the exact real -- e.g. 9900 -> 14*16*44 = 9856 -- which the fail-closed
    # privacy audit rejects.) Parquet stacked panels keep the nearest-multiple geometry unchanged.
    nctl = len(controls)
    c = k = None
    if salt in _STACKED_CSV_PANELS and ny > 0 and n % ny == 0:
        m = n // ny                                                        # blocks = k * (1+c)
        best = None
        for b in range(3, min(m, nctl + 1) + 1):                          # 1+c in [3 .. #controls+1] -> c>=2
            if m % b == 0:
                score = abs(b - m ** 0.5)                                  # prefer near-square (k ~= 1+c)
                if best is None or score < best[0]:
                    best = (score, b - 1, m // b)                          # (score, c, k)
        if best is not None:
            _, c, k = best                                                 # total == n_rows exactly (rounded)
    if c is None:                                                          # nearest multiple of the stack size
        c = min(nctl, max(2, int(round((n / ny) ** 0.5))))
        k = max(1, int(round(n / ((1 + c) * ny))))
    control_block = np.concatenate([bal[p] for p in controls[:c]])        # c complete-grid controls
    idx_parts, ep_parts = [], []
    for i in range(k):
        t = treated[i % len(treated)]                    # one treated PC per stack (cycle if k > n_treated)
        part = np.concatenate([bal[t], control_block])   # 1 treated + c controls, each a complete block
        idx_parts.append(part); ep_parts.append(np.full(len(part), i, dtype=np.int64))
    idx = np.concatenate(idx_parts)
    episode = np.concatenate(ep_parts)
    return mp.iloc[idx].reset_index(drop=True), episode


# ------------------------------------------------------------------------------------------
# Sparse adverse-event severity counts (fixes the derived-input "dependent variable is a constant"
# failure in 07_firm_heterogeneity). Real MAUDE coverage is SPARSE in (PRODUCTCODE, year): most
# device-years have NO adverse events. Drawing the severity columns as a dense uniform(0,1000) over a
# whole-grid skeleton makes EVERY device-year eventful, so 07's binarized v_serious collapses to a
# constant and feols cannot estimate. We instead gate each device-year on an "eventful" flag (only
# ~_EVENT_RATE carry events) and draw a small Poisson count for eventful rows only.
# ------------------------------------------------------------------------------------------
_EVENT_RATE = 0.35


def _eventful_mask(skel, salt):
    """Per-row boolean: does this row's (PRODUCTCODE, year) device-year carry any adverse events?
    Only ~_EVENT_RATE of distinct device-years do (the rest get zero counts), re-imposing MAUDE's
    (PC,year) sparsity on the whole-grid synthetic skeleton. Deterministic (public seed)."""
    n = len(skel)
    if n == 0 or "PRODUCTCODE" not in skel.columns or "year" not in skel.columns:
        return np.ones(n, dtype=bool)
    pc = pd.factorize(skel["PRODUCTCODE"].astype(str).to_numpy())[0].astype(np.int64)
    yr = pd.to_numeric(skel["year"], errors="coerce").fillna(-1).astype(np.int64).to_numpy()
    cell = pc * np.int64(100000) + (yr + np.int64(10000))
    uniq, inv = np.unique(cell, return_inverse=True)
    active_cell = iu.iu_rng("eventful", salt, len(uniq)).random(len(uniq)) < _EVENT_RATE
    return active_cell[inv]


def _safety_column(n, salt, active):
    """Adverse-event severity count for one row: 0 when its device-year is not eventful (`active`
    False), else a small Poisson count. Sparse like MAUDE -- never a dense uniform(0,1000) draw."""
    vals = iu.iu_rng("safety", salt, int(n)).poisson(0.6, size=int(n)).astype(float)
    if active is not None and len(active) == int(n):
        vals = np.where(active, vals, 0.0)
    return vals


# ==========================================================================================
# generic (non-anchor) files -- built column-by-column from the committed spec + public skeleton.
# ==========================================================================================
def _process_generic(name, order, cols, n_rows, master_pub, theta):
    # Panel-specific reclassification column: the reclass-derived public columns (treatment /
    # year_reclassified / posttreat / event_time) must key on THIS panel's own reclassification only,
    # not the 2_1-OR-3_2 coalesce. Straddle panels carry it in _STRADDLE_PANELS; the generic data_2_1_*
    # / data_3_2_* panels (incl. data_2_1_full, the II->I "Full" panel 03b/generate_d1 count) + any
    # 2_1/3_2-named panel derive it from the name. Non-reclass panels get rc=None (-> coalesce, a no-op
    # when they carry no reclass column).
    rc = _STRADDLE_PANELS.get(name)
    if rc is None:
        if "3_2" in name:
            rc = "year_reclassified_3_2"
        elif "2_1" in name:
            rc = "year_reclassified_2_1"
    if name in _STRADDLE_PANELS:
        if name.endswith(".parquet") or name in _STACKED_CSV_PANELS:
            # PRE-STACKED panels consumed directly by 03b/07/04-safety -> gen_04 clean-stacked form
            # (FE = stack). Includes the safety-DiD CSVs, which 04 reads already-stacked.
            skel, episode = _sample_stacked_skeleton(master_pub, n_rows, rc, name)
        else:
            # UNSTACKED per-PC CSV panels -> stacked at runtime by 03a; keep whole-PC straddle rows.
            skel, episode = _sample_straddle_skeleton(master_pub, n_rows, rc, name)
    else:
        skel, episode = _sample_public_skeleton(master_pub, n_rows, name)
    n = len(skel)
    saf_active = _eventful_mask(skel, name)          # per-(PC,year) adverse-event gate (sparse counts)
    out = {}
    n_id = n_val = n_pub = n_key = 0
    for col in order:
        c = str(col)
        spec = cols.get(c, {"role": "num", "missing_rate": 0.0})
        role = spec.get("role")
        if role == "public":
            out[c] = _public_column(c, skel, spec, name + "|" + c, episode=episode, reclass_col=rc); n_pub += 1
        elif role == "key":
            out[c] = ub.assign_firm_rows(n, name + "|" + c); n_key += 1
        elif role == "date":
            out[c] = _date_column(spec.get("kind", "datadate"), n, name + "|" + c); n_val += 1
        elif role == "id":
            out[c] = _id_column(n, spec, name + "|" + c); n_id += 1
        elif _FS_SAFETY_MATRIX.match(c):
            out[c] = _safety_column(n, name + "|" + c, saf_active); n_val += 1
        else:
            out[c] = _num_column(n, spec.get("missing_rate", 0.0), name + "|" + c); n_val += 1
        out[c] = _cast_dtype(out[c], spec.get("dtype"))
    df = pd.DataFrame(out, columns=[str(c) for c in order])
    n_master = 0
    if any(c in df.columns for c in MASTER_COLS):
        res = _merge_master(df, name)
        if isinstance(res, tuple):
            df, n_master = res
    return df, (n_id, n_val, n_pub, n_key, n_master)


def _sample_public_skeleton(master_pub, n_rows, salt):
    """Return (skeleton_rows, episode) for a generic panel, each row carrying a UNIQUE public
    (PRODUCTCODE, year) from the committed master grid. STRUCTURAL FIDELITY: the estimators unstack on
    (PRODUCTCODE, year) and pivot stacked-DiD on (FE/class_by_episode, year), so a panel must NOT carry
    RANDOM duplicate (PC,year) rows. When n_rows <= grid size the generator takes a seeded sample
    WITHOUT replacement (unique (PC,year), one stack). When n_rows exceeds the grid it TILES a fixed
    grid permutation across ceil(n/N) stacks and returns a per-row `episode` (stack index), so the panel is a
    proper (unit x year x stack) structure -- (PRODUCTCODE, year, episode) is UNIQUE and, with the
    episode-distinguished FE (see _public_column), (FE, factorized, year) is unique -- instead of random
    duplicate keys. Row count stays the committed ROUNDED n_rows; public structure; no real read."""
    N = len(master_pub)
    n = int(n_rows)
    if N == 0 or n <= 0:
        return master_pub.iloc[0:0].copy(), np.zeros(0, dtype=np.int64)
    rng = iu.iu_rng("pubskel", salt, n, N)
    if n <= N:
        idx = rng.choice(N, size=n, replace=False)          # unique (PC,year); single stack
        episode = np.zeros(n, dtype=np.int64)
    else:
        reps = int(np.ceil(n / N))
        order = rng.permutation(N)                           # fixed grid order, tiled across stacks
        idx = np.tile(order, reps)[:n]                       # (PC,year,episode) unique
        episode = np.repeat(np.arange(reps, dtype=np.int64), N)[:n]
    return master_pub.iloc[idx].reset_index(drop=True), episode


def process(name, theta, specs, master_pub):
    spec = specs.get(name)
    if spec is None:
        # FAIL CLOSED. A file listed for generation but absent from the committed params would
        # be silently omitted from the payload, and the consumer would then degrade on the
        # missing input while the run still reported success. A listed file with no committed
        # spec is a hard error.
        raise SystemExit(
            f"gen_00d: no committed interlock spec for {name!r}. Every file listed for generation "
            f"must have a spec in simulation_parameters.json['files'] (run gen_00a Stage A in the "
            f"authorized environment to extract it). Refusing to ship a payload that silently "
            f"omits a simulated input."
        )
    order = spec["order"]
    cols = spec["columns"]
    n_rows = int(spec["n_rows"])

    if name == "Full_sample.csv":
        df = process_full_sample(order, cols, master_pub, theta)
        df.to_csv(os.path.join(OUT, name), index=False)
        print(f"  wrote {name:<48} ({len(df):>9,} rows; PANEL from public skeleton + theta)")
        return
    if name == "all_patents_w_xi_oct22_24.csv":
        df = process_all_patents(order, cols, theta)
        df.to_csv(os.path.join(OUT, name), index=False)
        print(f"  wrote {name:<48} ({len(df):>9,} rows; PATENT universe: fresh patnum/permno/PC)")
        return
    if name == "compustat_firm_data.csv":
        df = process_compustat(order, cols)
        df.to_csv(os.path.join(OUT, name), index=False)
        print(f"  wrote {name:<48} ({len(df):>9,} rows; FIRM universe: permno+gvkey paired)")
        return

    df, (n_id, n_val, n_pub, n_key, n_master) = _process_generic(
        name, order, cols, n_rows, master_pub, theta)
    outp = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    if name.endswith(".parquet"):
        df.to_parquet(outp, index=False)
    else:
        df.to_csv(outp, index=False)
    print(f"  wrote {name:<48} ({len(df):>9,} rows [rounded]; {n_id} id, {n_val} value, "
          f"{n_pub} public, {n_key} key, {n_master} master-merged)")


def main():
    os.makedirs(OUT, exist_ok=True)
    theta = pcmod.load_theta()
    ub.build_universes()                     # firm + patent universes (cached) BEFORE any file
    specs = ub.file_specs()
    if not specs:
        raise SystemExit("gen_00d: committed params have no 'files' specs -- run gen_00a (Stage A) "
                         "to extract the interlock specs before generating.")
    master_pub = ub.public_master_skeleton()
    for _kind, name in FILES:
        process(name, theta, specs, master_pub)
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
