"""
gen_00a_extract_parameters.py -- STAGE A of the independent-universe redesign.

Stage A is the only real-data READ that produces committed params; gen_00d/gen_00e now read NO
real data -- they build every file from `simulation_parameters.json` (this program's output) +
the committed public master skeleton + the fresh synthetic universes. This program runs ONCE,
author-side, in the authorized environment, and emits `simulation_parameters.json` -- the
committed PUBLIC parameter file that the shipped generators (Stage B) consume. It ALSO commits
`public_master_skeleton.parquet` (Full_sample's PUBLIC columns only: the FDA product-code +
Federal-Register reclassification design, all public by construction). (gen_00b_pc_effects reads
the SAME public design columns of Full_sample to build the committed theta table -- also Stage A;
every other generator reads only these committed public artifacts + the synthetic caches.)

DISCLOSURE CONTRACT (THREAT_MODEL.md §5). Every value written here is either:
  (i)  already PUBLIC (FDA product-code list, Federal-Register reclassification design), or
  (ii) an AGGREGATE that has passed the numeric disclosure review below -- specifically:
        * cardinalities are ROUNDED to 2 significant figures (protects exact dataset sizes;
          a rounded N cannot single out a rare group -- T5/T6), never the exact count;
        * size distributions are stored as a SMOOTHED 2-moment family fit (nbinom/lognormal),
          NEVER the real group-size multiset (so no uniquely-sized group is disclosed);
        * missingness is stored as a rate ROUNDED to 3 decimals, never the exact NaN count;
        * schemas/dtypes/units are structural (public by construction).
  It NEVER writes: a real id, a real value, an exact real count, an exact real multiset, or any
  high-entropy real token. `disclosure_review()` asserts this before anything is emitted, and
  `_selftest()` (runs WITHOUT real data) checks the smoothing/rounding logic fails closed.

Stage B (`independent_universe.py` + gen_00b--h) then GENERATES a fresh universe from this file
+ a public seed, with no real->synthetic mapping of any kind.
"""
import os
import re
import sys
import json
import math
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DERIVED = os.path.join(ROOT, "data", "derived")
RAW = os.path.join(ROOT, "data", "raw")
INTERNAL = os.path.join(ROOT, "synthetic_pipeline", "_synthetic_source_internal")
OUT = os.path.join(INTERNAL, "simulation_parameters.json")
# committed PUBLIC master skeleton (Full_sample public columns only) -- the canonical public
# PC x year design gen_00d rebuilds Full_sample from, so gen_00d need not read the real master.
PUBLIC_MASTER_SKELETON = os.path.join(INTERNAL, "public_master_skeleton.parquet")

# Disclosure-review knobs (documented + auditable).
CARD_SIGFIGS = 2          # cardinalities rounded to 2 sig figs
RATE_DECIMALS = 3         # missingness rates rounded to 3 decimals
MIN_ROUND_BASE = 10       # never disclose a count finer than nearest 10

# ======================================================================================
# INTERLOCK CONTRACT (Stage A writes it here; gen_00d/gen_00e consume EXACTLY this shape).
# --------------------------------------------------------------------------------------
# params["files"][<relpath>] = {
#     "n_rows": round_cardinality(real_len),          # ROUNDED row count (never exact)
#     "order":  [col, ...],                           # committed column ORDER (schema fidelity;
#                                                     #   kept separately so json sort_keys is safe)
#     "columns": { col: <spec> },                     # per-column role spec, one of:
#        {"role":"public"}                                          <- STRUCTURE regex: public design,
#                                                                      values from the public master /
#                                                                      synthetic master (NOT stored)
#        {"role":"key","universe":"firm"}                            <- permno/LPERMNO/gvkey: from universe
#        {"role":"date","kind":"fyear"|"datadate"}                   <- generative date
#        {"role":"id","cardinality":round_cardinality(nunique),
#                     "size_family":fit_size_family(sizes),
#                     "numeric":bool}                                <- fresh tokens: ROUNDED cardinality
#                                                                      + SMOOTHED family (never the
#                                                                      exact distinct-count/multiset)
#        {"role":"num","missing_rate":smooth_rate(nan/n),
#                     "kind":"uniform01k"}                           <- value draw + ROUNDED missingness
#                                                                      rate (never the exact NaN count)
# The role classifier below MIRRORS gen_00d's column routing so id/num statistics land on the
# columns that consume them; gen_00e overrides its special columns (patnum/PC/year/cpc/text/...) by
# NAME at generation, so an over-broad committed role there is simply ignored (all committed stats
# are rounded/smoothed -> harmless either way). No EXACT statistic is ever written (disclosure_review
# asserts it).  Column classes (copied from gen_00d so the two stay in lock-step):
_STRUCTURE = re.compile(
    r"^(PRODUCTCODE.*|year|treatment.*|year_reclass.*|event_time.*|ET|FE|factorized.*|posttreat.*|"
    r"class_by_episode.*|FDA_own_accord.*|use_case|controls|"
    r"Reg_Change_List|REGULATIONNUMBER.*|DEVICECLASS|"
    r"DEVICENAME|DESCRIPTION_OF_REGNUM.*|SUBPART_DESCRIPTION.*|PART_DESCRIPTION.*|SUBMISSION_TYPE_ID.*|"
    r"MDR_REPORT_KEY|DEVICE_PROBLEM_CODE|PROBLEM_DESCRIPTION|Petition.*|date_proposed.*|"
    r"type|indfmt|consol|popsrc|"
    r"datafmt|curcd|costat|file_year|CPI|Unnamed.*|index)$", re.I)
_IDENTITY = re.compile(r"(gvkey|clean_name|stock_name|assignee|inventor|grid|conm|orig_)", re.I)
_LINKKEY = re.compile(r"^(permno|LPERMNO|gvkey|GVKEY)$")
_DATE_COLS = {"fyear", "datadate"}
# Full_sample PUBLIC columns committed verbatim to the public master skeleton (all public: FDA
# product-code design + Federal-Register reclassification design + calendar). Mirrors gen_00d._FS_PUBLIC.
PUBLIC_MASTER_COLS = [
    "PRODUCTCODE", "Reg_Change_List", "use_case", "REGULATIONNUMBER", "DEVICECLASS",
    "SUBMISSION_TYPE_ID", "DEVICENAME", "DESCRIPTION_OF_REGNUM", "SUBPART_DESCRIPTION",
    "year", "FDA_own_accord", "DESCRIPTION_OF_REGNUM_3_2", "year_reclassified_3_2",
    "FDA_own_accord_3_2", "PART_DESCRIPTION_3_2", "Petition_DeNovo_Filing_Date_3_2",
    "REGULATIONNUMBER_3_2", "date_proposed_3_2", "SUBMISSION_TYPE_ID_3_2",
    "SUBPART_DESCRIPTION_3_2", "year_reclassified_2_1", "controls",
]


# --------------------------------------------------------------------------------------
# Pure, locally-testable disclosure transforms (no real data needed to test these).
# --------------------------------------------------------------------------------------
def round_cardinality(n, sigfigs=CARD_SIGFIGS):
    """Round a count to `sigfigs` significant figures (>= nearest MIN_ROUND_BASE). A rounded
    cardinality reveals order-of-magnitude only, never the exact dataset size (T5/T6)."""
    n = int(n)
    if n <= 0:
        return 0
    digits = int(math.floor(math.log10(n)))
    base = max(10 ** (digits - (sigfigs - 1)), MIN_ROUND_BASE)
    return int(round(n / base) * base)


def smooth_rate(rate, decimals=RATE_DECIMALS):
    """Round a marginal rate to `decimals` (so it carries no exact count). Clamped to [0,1]."""
    return float(min(max(round(float(rate), decimals), 0.0), 1.0))


def round_sig(x, sig=3):
    """Round to `sig` significant figures. Unlike round(x, 2) -- which leaves a large moment (e.g. a
    variance of magnitude 1e8) at essentially full precision and thus SINGLE-RECORD-sensitive -- sig-fig
    rounding scales the granularity with the magnitude, so one real record's influence (which shifts a
    moment by << one significant figure) is absorbed. Satisfies the T6 single-record-influence bound for
    the committed size-family moments."""
    x = float(x)
    if x == 0.0 or not math.isfinite(x):
        return x
    return round(x, -int(math.floor(math.log10(abs(x)))) + (sig - 1))


def _family_at(sizes, sig):
    """The smoothed 2-moment family with both moments rounded to `sig` significant figures."""
    m = float(sizes.mean())
    v = float(sizes.var(ddof=0))
    m_r = round_sig(m, sig)
    v_r = round_sig(v, sig)
    if v_r > m_r > 0:
        p = m_r / v_r
        p = min(max(p, 1e-3), 0.999)
        r = max(m_r * p / (1.0 - p), 1e-3)
        return {"kind": "nbinom", "r": round(r, 3), "p": round(p, 3),
                "mean": m_r, "var": v_r}
    p = 1.0 / (1.0 + max(m_r - 1.0, 1e-3))
    return {"kind": "geometric", "p": round(min(max(p, 1e-3), 0.999), 3), "mean": m_r}


def _moment_unit(x, sig):
    x = abs(float(x))
    if x == 0.0 or not math.isfinite(x):
        return 1.0
    return 10 ** (int(math.floor(math.log10(x))) - (sig - 1))


def _family_within_one_unit(f0, f1, sig):
    """True when two committed families differ by at most one rounding step: means within one unit of
    the committed mean's last significant figure; variances likewise when both carry one; and when
    exactly one side is the geometric fallback (no variance), the other side's variance must lie within
    one unit of its mean -- the nbinom/geometric decision (var > mean) is itself a rounding boundary."""
    m0, m1 = f0.get("mean"), f1.get("mean")
    if m0 is None or m1 is None:
        return f0.get("kind") == f1.get("kind")
    if abs(float(m0) - float(m1)) > _moment_unit(m0, sig) + 1e-12:
        return False
    v0, v1 = f0.get("var"), f1.get("var")
    if v0 is not None and v1 is not None:
        return abs(float(v0) - float(v1)) <= _moment_unit(v0, sig) + 1e-12
    if v0 is None and v1 is None:
        return True
    v, m = (v0, m0) if v0 is not None else (v1, m1)
    return abs(float(v) - float(m)) <= _moment_unit(v, sig) + 1e-12
def fit_size_family(sizes, max_sig=3):
    """Fit a SMOOTHED 2-moment family to a real group-size array and return ONLY the smoothed
    parameters (never the multiset). Method of moments:
      * if variance > mean (over-dispersed, the usual case): negative-binomial (r, p)
      * else: a near-Poisson geometric fallback
    Only the mean and variance (both rounded) leave the real data -- two aggregate moments, which
    the disclosure review permits; the exact sizes do not.

    T6 (bounded single-record influence): the moments are committed at the FINEST precision --
    3, then 2, then 1 significant figures -- at which removing one real record from the largest
    group, or removing one singleton, changes neither committed moment by more than one unit of its
    last significant figure. Columns with many groups keep 3 figures; a column with only a handful
    of groups, where one record shifts the mean of the group sizes materially, is committed more
    coarsely. The choice is a deterministic function of the sizes, so the certification suite can
    recompute it (confidential run 2026-09-29: six such columns)."""
    sizes = np.asarray(sizes, dtype=float)
    sizes = sizes[sizes > 0]
    if sizes.size == 0:
        return {"kind": "uniform"}
    perturbed = []
    largest = sizes.copy(); j = int(np.argmax(largest))
    if largest[j] > 1:
        largest[j] -= 1
    else:
        largest = np.delete(largest, j)
    if largest.size:
        perturbed.append(largest)
    singleton = np.flatnonzero(sizes == 1)
    if len(singleton):
        rest = np.delete(sizes, int(singleton[0]))
        if rest.size:
            perturbed.append(rest)
    for sig in range(max_sig, 0, -1):
        base = _family_at(sizes, sig)
        if all(_family_within_one_unit(base, _family_at(q, sig), sig) for q in perturbed):
            return base
    return _family_at(sizes, 1)

def disclosure_review(params):
    """Assert the committed parameter dict contains only public/aggregate/smoothed values.
    Fails closed (raises) if it finds anything that looks like a raw real statistic: an exact
    (un-rounded) cardinality, a stored size multiset, or a rate with > RATE_DECIMALS precision.
    Returns a per-key review ledger for the audit trail."""
    ledger = []
    problems = []

    def review(key, ok, note):
        ledger.append({"key": key, "ok": bool(ok), "note": note})
        if not ok:
            problems.append(f"{key}: {note}")

    for name, spec in params.get("entities", {}).items():
        card = spec.get("cardinality")
        if card is not None:
            review(f"entities.{name}.cardinality",
                   card == round_cardinality(card),
                   "cardinality must be rounded to sig-figs (no exact count)")
        size = spec.get("size_family", {})
        review(f"entities.{name}.size_family",
               "sizes" not in size and size.get("kind") in
               {"nbinom", "geometric", "lognormal", "gamma", "uniform"},
               "must be a smoothed family, never a stored multiset")
    for col, rate in params.get("missingness", {}).items():
        review(f"missingness.{col}",
               rate == smooth_rate(rate),
               "rate must be rounded (no exact NaN count)")
    # INTERLOCK per-file specs: assert every committed statistic is rounded/smoothed (no raw stat).
    _smoothed_kinds = {"nbinom", "geometric", "lognormal", "gamma", "uniform"}
    for fname, fspec in params.get("files", {}).items():
        nr = fspec.get("n_rows")
        review(f"files.{fname}.n_rows",
               nr is not None and nr == round_cardinality(nr),
               "file row count must be rounded (no exact real row count)")
        for col, spec in fspec.get("columns", {}).items():
            role = spec.get("role")
            if role == "id":
                review(f"files.{fname}.columns.{col}.cardinality",
                       spec.get("cardinality") == round_cardinality(spec.get("cardinality", 0)),
                       "id cardinality must be rounded (no exact distinct-count)")
                fam = spec.get("size_family", {})
                review(f"files.{fname}.columns.{col}.size_family",
                       "sizes" not in fam and "multiset" not in fam
                       and fam.get("kind") in _smoothed_kinds,
                       "id size_family must be a smoothed family (no raw multiset)")
            elif role == "num":
                mr = spec.get("missing_rate")
                review(f"files.{fname}.columns.{col}.missing_rate",
                       mr is not None and mr == smooth_rate(mr),
                       "num missing_rate must be rounded (<=3 decimals, no exact NaN count)")
    # product codes + reclassification design are PUBLIC by construction -> allowed
    review("product_codes", isinstance(params.get("product_codes"), list),
           "public FDA code list")

    if problems:
        raise SystemExit("gen_00a disclosure review FAILED (fail closed):\n  " +
                         "\n  ".join(problems))
    return ledger


# --------------------------------------------------------------------------------------
# Real-data extraction (runs only in the authorized environment).
# --------------------------------------------------------------------------------------
def _read_public_design():
    """Public product-code list + reclass/control flags (FDA + Federal Register)."""
    fs = os.path.join(DERIVED, "Full_sample.csv")
    cols = ["PRODUCTCODE", "year_reclassified_2_1", "year_reclassified_3_2", "controls"]
    have = [c for c in cols if c in pd.read_csv(fs, nrows=0).columns]
    df = pd.read_csv(fs, usecols=have, low_memory=False)
    g = df.groupby("PRODUCTCODE", sort=True)
    out = []
    for code, idx in g.groups.items():
        sub = df.loc[idx]
        out.append({
            "code": str(code),
            "reclass_2_1": bool(sub.get("year_reclassified_2_1", pd.Series()).notnull().any())
                if "year_reclassified_2_1" in have else False,
            "reclass_3_2": bool(sub.get("year_reclassified_3_2", pd.Series()).notnull().any())
                if "year_reclassified_3_2" in have else False,
            "control": bool(sub["controls"].max()) if "controls" in have else False,
        })
    return out


def _entity_params(path, id_col, name):
    """Rounded cardinality + smoothed size family for one entity column of a real file."""
    if not os.path.exists(path):
        return None
    s = pd.read_csv(path, usecols=[id_col], low_memory=False)[id_col].dropna()
    if s.empty:
        return None
    sizes = s.value_counts().to_numpy()          # real group sizes (NOT stored)
    return {
        "cardinality": round_cardinality(s.nunique()),   # rounded, not exact
        "n_rows": round_cardinality(len(s)),             # rounded, not exact
        "size_family": fit_size_family(sizes),           # smoothed, not the multiset
    }


# --------------------------------------------------------------------------------------
# Per-file, per-column spec extraction (the INTERLOCK payload for gen_00d/gen_00e).
# --------------------------------------------------------------------------------------
def _classify_role(col, s):
    """Assign one interlock role to a column. Mirrors gen_00d's routing ORDER so the id/num
    disclosure statistics land on the same columns the generator will consume."""
    c = str(col)
    cl = c.lower()
    if _STRUCTURE.match(c):
        return "public"
    if cl in _DATE_COLS:
        return "date"
    if _LINKKEY.match(c):
        return "key"                                  # permno/LPERMNO/gvkey -> shared firm universe
    if _IDENTITY.search(c):
        return "id"
    if pd.api.types.is_numeric_dtype(s):
        return "num"
    return "id"                                       # object fallback -> fresh tokens (fail-closed)


def _column_spec(s, role, col):
    """Build the committed spec for one column. Only ROUNDED/SMOOTHED aggregates are stored; the
    raw distinct-count, group-size multiset, and exact NaN count NEVER leave real data. `dtype`
    (the pandas dtype string) is PUBLIC structural metadata kept so gen_00d/gen_00e reproduce the
    schema/dtype without reading the real file."""
    dt = str(s.dtype)
    if role == "public":
        return {"role": "public", "dtype": dt}
    if role == "key":
        return {"role": "key", "universe": "firm", "dtype": dt}
    if role == "date":
        return {"role": "date", "kind": ("fyear" if str(col).lower() == "fyear" else "datadate"),
                "dtype": dt}
    n = len(s)
    if role == "num":
        nan = int(pd.isna(s).sum())
        return {"role": "num",
                "missing_rate": smooth_rate((nan / n) if n else 0.0),   # ROUNDED (no exact NaN count)
                "kind": "uniform01k", "dtype": dt}
    # role == "id": fresh tokens with ROUNDED cardinality + SMOOTHED size family (no exact multiset)
    nn = s.dropna()
    sizes = nn.value_counts().to_numpy() if len(nn) else np.array([])
    return {"role": "id",
            "cardinality": round_cardinality(int(nn.nunique())),        # ROUNDED (no exact distinct)
            "size_family": fit_size_family(sizes),                      # SMOOTHED (no raw multiset)
            "numeric": bool(pd.api.types.is_numeric_dtype(s)), "dtype": dt}


def _read_any(path):
    return pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path, low_memory=False)


def _file_params(path):
    """Extract {n_rows (rounded), order, columns:{col:spec}} for one real file. Reads the full file
    once (author-side, one-time); only rounded/smoothed aggregates + the public schema leave it."""
    if not os.path.exists(path):
        return None
    df = _read_any(path)
    order, cols = [], {}
    for col in df.columns:
        role = _classify_role(col, df[col])
        order.append(str(col))
        cols[str(col)] = _column_spec(df[col], role, col)
    return {"n_rows": round_cardinality(len(df)), "order": order, "columns": cols}


def _gen_file_paths():
    """The SAME file lists gen_00d + gen_00e iterate, as (relpath_key, abs_path) pairs. Imported
    from the generators so the interlock file set is single-sourced (not re-hardcoded here)."""
    import importlib
    if HERE not in sys.path:
        sys.path.insert(0, HERE)                      # ensure the sibling generators import
    pairs = []                                        # (params-key relpath, absolute real path)
    for modname, base_default in (("gen_00d_synthetic_dimensions_wrds", None),
                                  ("gen_00e_synthetic_patents", None)):
        mod = importlib.import_module(modname)
        spec_free = set(getattr(mod, "SPEC_FREE_FILES", ()))   # universe-derived twins: no per-file spec
        for kind, name in mod.FILES:
            if name in spec_free:
                continue
            base = mod.DERIVED if kind == "d" else mod.RAW
            pairs.append((name, os.path.join(base, name)))
    # de-dupe while keeping order (a name can appear in only one generator, but guard anyway)
    seen, out = set(), []
    for k, p in pairs:
        if k not in seen:
            seen.add(k); out.append((k, p))
    return out


def _write_public_master_skeleton():
    """Commit Full_sample's PUBLIC columns (the canonical public PC x year design) so gen_00d can
    rebuild the master WITHOUT reading real data. Every column here is public by construction (FDA
    product-code design + Federal-Register reclassification design + calendar); its row count is the
    public panel size. Returns the number of rows written (0 if the master is absent)."""
    fs = os.path.join(DERIVED, "Full_sample.csv")
    if not os.path.exists(fs):
        return 0
    have = [c for c in PUBLIC_MASTER_COLS if c in pd.read_csv(fs, nrows=0).columns]
    skel = pd.read_csv(fs, usecols=have, low_memory=False)
    os.makedirs(INTERNAL, exist_ok=True)
    skel.to_parquet(PUBLIC_MASTER_SKELETON, index=False)
    return len(skel)


def extract(write=True):
    """Read real data and build the committed parameter dict (authorized env only)."""
    params = {
        "_schema": "simulation_parameters/v2",
        "_contract": "independent-universe; committed public params; see gen_00a header + THREAT_MODEL §5",
        "product_codes": _read_public_design(),
        "entities": {},
        "missingness": {},
        "files": {},                                  # INTERLOCK: per-file schema + rounded/smoothed specs
    }
    # entity universes (rounded cardinality + smoothed sizes). Paths per EXECUTABLE_INVENTORY.
    plan = [
        ("patents", os.path.join(DERIVED, "all_patents_w_xi_oct22_24.csv"), "patnum"),
        ("firms_permno", os.path.join(RAW, "compustat_firm_data.csv"), "LPERMNO"),
        ("firms_gvkey", os.path.join(RAW, "compustat_firm_data.csv"), "GVKEY"),
        ("adverse_firms", os.path.join(DERIVED, "all_adv_events_w_permno5.csv"), "permno"),
    ]
    for name, path, col in plan:
        try:
            ep = _entity_params(path, col, name)
        except (KeyError, ValueError):
            ep = None
        if ep is not None:
            params["entities"][name] = ep

    # INTERLOCK: per-file schema + rounded/smoothed column specs for every gen_00d/gen_00e file.
    for key, path in _gen_file_paths():
        fp = _file_params(path)
        if fp is not None:
            params["files"][key] = fp

    disclosure = disclosure_review(params)
    params["_disclosure_ledger"] = disclosure
    n_skel = 0
    if write:
        os.makedirs(INTERNAL, exist_ok=True)
        n_skel = _write_public_master_skeleton()      # commit the public PC x year design (all public)
        with open(OUT, "w") as f:
            json.dump(params, f, indent=2, sort_keys=True)
        print(f"gen_00a: wrote {OUT}  "
              f"({len(params['product_codes'])} product codes, "
              f"{len(params['entities'])} entity universes, {len(params['files'])} file specs; "
              f"public master skeleton {n_skel:,} rows; disclosure review PASS)")
    return params


# ======================================================================================
# Self-test -- runs WITHOUT real data; checks the disclosure transforms fail closed.
# ======================================================================================
def _selftest():
    problems = []

    def check(c, m):
        if not c:
            problems.append(m)

    # rounding hides exact counts
    check(round_cardinality(1_248_245) == 1_200_000, f"card round {round_cardinality(1_248_245)}")
    check(round_cardinality(25_748) == 26_000, f"card round {round_cardinality(25_748)}")
    check(round_cardinality(4_502) == 4_500, f"card round {round_cardinality(4_502)}")
    check(round_cardinality(7) == 10, "small counts floored to 10")
    check(round_cardinality(1_248_245) != 1_248_245, "exact count leaked through rounding")

    # rate smoothing
    check(smooth_rate(0.13712) == 0.137, f"rate {smooth_rate(0.13712)}")
    check(smooth_rate(1.5) == 1.0 and smooth_rate(-0.2) == 0.0, "rate not clamped")

    # size family: smoothed, stores no multiset, over-dispersed -> nbinom
    rng = np.random.default_rng(0)
    sizes = rng.negative_binomial(3, 0.25, size=5000) + 1
    fam = fit_size_family(sizes)
    check(fam["kind"] == "nbinom", f"expected nbinom, got {fam['kind']}")
    check("sizes" not in fam and "multiset" not in fam, "size family stored raw sizes (leak)")
    check(set(fam) <= {"kind", "r", "p", "mean", "var"}, f"unexpected keys {set(fam)}")

    # disclosure_review must PASS a clean dict and FAIL a leaky one
    clean = {
        "product_codes": [{"code": "ABC"}],
        "entities": {"firms": {"cardinality": round_cardinality(25_748),
                               "size_family": fit_size_family(sizes)}},
        "missingness": {"col_a": smooth_rate(0.137)},
        "files": {"f.csv": {"n_rows": round_cardinality(9_677_786), "order": ["a", "b", "c"],
                            "columns": {"a": {"role": "public"},
                                        "b": {"role": "id",
                                              "cardinality": round_cardinality(45_623),
                                              "size_family": fit_size_family(sizes), "numeric": False},
                                        "c": {"role": "num", "missing_rate": smooth_rate(0.137),
                                              "kind": "uniform01k"}}}},
    }
    try:
        disclosure_review(clean)
    except SystemExit:
        problems.append("disclosure_review rejected a clean dict")

    # --- interlock file-spec leaks must FAIL closed ------------------------------------
    def _files_leak(files):
        d = {"product_codes": [], "entities": {}, "missingness": {}, "files": files}
        try:
            disclosure_review(d)
            return False
        except SystemExit:
            return True

    check(_files_leak({"f": {"n_rows": 9_677_786, "columns": {}}}),          # EXACT row count
          "disclosure_review passed an EXACT file row count")
    check(_files_leak({"f": {"n_rows": round_cardinality(9_677_786), "columns": {
              "x": {"role": "id", "cardinality": 45_623,                      # EXACT distinct-count
                    "size_family": fit_size_family(sizes), "numeric": False}}}}),
          "disclosure_review passed an EXACT id cardinality")
    check(_files_leak({"f": {"n_rows": round_cardinality(100), "columns": {
              "x": {"role": "id", "cardinality": round_cardinality(45_623),
                    "size_family": {"kind": "nbinom", "sizes": [1, 2, 3]},    # stored multiset
                    "numeric": False}}}}),
          "disclosure_review passed a stored id size multiset")
    check(_files_leak({"f": {"n_rows": round_cardinality(100), "columns": {
              "x": {"role": "num", "missing_rate": 0.13712, "kind": "uniform01k"}}}}),  # unrounded rate
          "disclosure_review passed an unrounded num missing_rate")

    leaky_card = {"product_codes": [], "entities": {"f": {"cardinality": 25_748,  # exact!
                  "size_family": {"kind": "uniform"}}}, "missingness": {}}
    try:
        disclosure_review(leaky_card); problems.append("disclosure_review passed an EXACT cardinality")
    except SystemExit:
        pass

    leaky_multiset = {"product_codes": [], "entities": {"f": {"cardinality": round_cardinality(100),
                      "size_family": {"kind": "nbinom", "sizes": [1, 2, 3]}}}, "missingness": {}}
    try:
        disclosure_review(leaky_multiset); problems.append("disclosure_review passed a stored multiset")
    except SystemExit:
        pass

    leaky_rate = {"product_codes": [], "entities": {}, "missingness": {"c": 0.13712}}  # unrounded
    try:
        disclosure_review(leaky_rate); problems.append("disclosure_review passed an unrounded rate")
    except SystemExit:
        pass

    if problems:
        print("gen_00a self-test: FAIL")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("gen_00a self-test: PASS (cardinalities rounded, sizes smoothed, rates rounded, "
          "disclosure review fails closed on exact-count/multiset/unrounded-rate leaks)")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        extract(write=True)
