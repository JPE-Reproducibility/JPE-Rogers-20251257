"""
universe_backend.py -- the shared bridge the entity generators (gen_00d/00e/00g) call instead of
the real-id maps `_link_remap` / `build_map` / `assign_pc`. It builds the two canonical universes
ONCE (from the committed Stage-A parameters + theta), caches them, and hands out firm/patent ids
sampled from those universes with INDEPENDENT co-membership.

Why this gives cross-file consistency WITHOUT a real->fake map:
  * compustat is emitted AS the firm universe (permno+gvkey paired).
  * all_patents_w_xi is emitted AS the patent universe (patnum + a universe permno + a public PC).
  * every other firm-bearing file assigns its rows firms SAMPLED from the SAME firm universe, and
    every other patent-bearing file assigns its rows patents SAMPLED from the SAME patent universe.
  Because all files draw from the one universe, their keys OVERLAP (joins resolve), and because the
  per-row assignment is an independent draw (not a function of any real id), the real co-membership
  partition does NOT survive and there is nothing to invert.

Deterministic in the committed PUBLIC seed. Reads the committed parameter file (public); reads NO
real restricted data. Test fixtures require an explicit opt-in and can never silently replace the
committed production parameters.
"""
import os
import json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
import synthetic_paths

INTERNAL = str(synthetic_paths.internal_dir())
PARAMS = os.path.join(INTERNAL, "simulation_parameters.json")
FIRM_CACHE = os.path.join(INTERNAL, "firm_universe.parquet")
PATENT_CACHE = os.path.join(INTERNAL, "patent_universe.parquet")
PUBLIC_MASTER_SKELETON = os.path.join(INTERNAL, "public_master_skeleton.parquet")

import independent_universe as iu
import synthetic_universe as su
import gen_00b_pc_effects as pcmod

# Fallback committed params for unit tests (no real data / no parameter file present).
_FIXTURE = {
    "product_codes": [{"code": f"PC{i:04d}", "reclass_2_1": i % 50 == 0,
                       "reclass_3_2": i % 70 == 0, "control": i % 9 == 0} for i in range(300)],
    "entities": {
        "patents": {"cardinality": 120_000, "size_family": {"kind": "geometric", "p": 0.999}},
        "firms_permno": {"cardinality": 26_000, "size_family": {"kind": "nbinom", "r": 1.36, "p": 0.11}},
        "firms_gvkey": {"cardinality": 25_000, "size_family": {"kind": "nbinom", "r": 1.28, "p": 0.10}},
        "adverse_firms": {"cardinality": 4_600, "size_family": {"kind": "nbinom", "r": 1.5, "p": 0.001}},
    },
    "patents_per_firm": {"kind": "nbinom", "r": 2.0, "p": 0.25},
}


def load_params(allow_fixture=False):
    if os.path.exists(PARAMS):
        with open(PARAMS) as f:
            return json.load(f)
    if allow_fixture or os.environ.get("FDA_SYNTHETIC_TEST_FIXTURE") == "1":
        return _FIXTURE
    raise SystemExit(
        f"Committed synthetic parameters are missing: {PARAMS}. Refusing to fall back "
        "to the small test fixture in a production generation run."
    )


_FIRM = None
_PATENT = None


def _theta_design():
    """Return the public code design and patent weights used by the universe.

    Event years are required to enforce pre-event patent support.  The fixture
    fallback supplies public, synthetic event years for tests.
    """
    try:
        theta = pcmod.load_theta()
        cols = ["PRODUCTCODE", "pat_weight", "is_control",
                "year_reclassified_2_1", "year_reclassified_3_2",
                "panel_support_year", "pre_event_support_year", "support_2_1",
                "analysis_support_year"]
        missing = set(cols) - set(theta.columns)
        if missing:
            raise ValueError(f"theta missing support-design columns: {sorted(missing)}")
        return theta[cols].copy()
    except Exception:
        if os.environ.get("FDA_SYNTHETIC_TEST_FIXTURE") != "1":
            raise
        p = load_params()
        rows = []
        for c in p["product_codes"]:
            # Older committed parameter files carry public treatment booleans but
            # not event years.  Use conservative public cohort defaults until the
            # parameter file is refreshed; a pre-1996 patent supports either II->I
            # cohort and 2015 is the III->II cohort used by the pipeline.
            rows.append({
                "PRODUCTCODE": c["code"],
                "pat_weight": 1.0,
                "is_control": bool(c.get("control", False)),
                "year_reclassified_2_1": 1996 if c.get("reclass_2_1", False) else np.nan,
                "year_reclassified_3_2": 2015 if c.get("reclass_3_2", False) else np.nan,
                "panel_support_year": 1990,
                "pre_event_support_year": (
                    1990 if c.get("reclass_2_1", False) or c.get("reclass_3_2", False)
                    else np.nan
                ),
                "support_2_1": bool(c.get("reclass_2_1", False)),
                "analysis_support_year": 1990,
            })
        return pd.DataFrame(rows)


def _has_required_patent_support(patents, design):
    """Whether a cached universe satisfies the current event-support contract."""
    required = {"PRODUCTCODE", "filing_year", "patnum", "required_support"}
    if not required.issubset(patents.columns) or patents["patnum"].duplicated().any():
        return False
    support_rows = patents[patents["required_support"].astype(bool)]
    present = set(support_rows["PRODUCTCODE"])
    # The later-treated estimator selects controls using public regulation metadata,
    # not only the narrower `is_control` flag. Reserve support for every public code.
    if not set(design["PRODUCTCODE"]).issubset(present):
        return False
    expected = design.set_index("PRODUCTCODE")
    actual = support_rows.drop_duplicates("PRODUCTCODE").set_index("PRODUCTCODE")
    if not (actual.reindex(expected.index)["filing_year"]
            == expected["analysis_support_year"]).all():
        return False
    for event in ("2_1", "3_2"):
        ycol = f"year_reclassified_{event}"
        eligible = design[ycol].notna() & design["pre_event_support_year"].notna()
        if event == "2_1":
            eligible &= design["support_2_1"].astype(bool)
        treated = design.loc[
            eligible,
            ["PRODUCTCODE", ycol, "pre_event_support_year"],
        ]
        if treated.empty:
            continue
        merged = support_rows[["PRODUCTCODE", "filing_year"]].merge(treated, on="PRODUCTCODE")
        supported = set(merged.loc[
            (merged["filing_year"] < merged[ycol])
            & (merged["filing_year"] == merged["pre_event_support_year"]),
            "PRODUCTCODE",
        ])
        if not set(treated["PRODUCTCODE"]).issubset(supported):
            return False
    return True


def build_universes(force=False):
    """Build + cache the firm and patent universes from committed params + theta. Idempotent."""
    global _FIRM, _PATENT
    if _FIRM is not None and _PATENT is not None and not force:
        return _FIRM, _PATENT
    design = _theta_design()
    if not force and os.path.exists(FIRM_CACHE) and os.path.exists(PATENT_CACHE):
        cached_firm = pd.read_parquet(FIRM_CACHE)
        cached_patent = pd.read_parquet(PATENT_CACHE)
        if _has_required_patent_support(cached_patent, design):
            _FIRM, _PATENT = cached_firm, cached_patent
            return _FIRM, _PATENT
    p = load_params()
    ent = p["entities"]
    n_firm = int(ent["firms_permno"]["cardinality"])
    n_pat = int(ent["patents"]["cardinality"])
    # patent-owning subset ~ the adverse/patent firm cardinality (committed, rounded)
    n_owner = int(ent.get("adverse_firms", {}).get("cardinality", max(n_firm // 5, 1)))
    codes = design["PRODUCTCODE"].to_numpy()
    weights = design["pat_weight"].to_numpy(dtype=float)
    firms = su.build_firm_universe(n_firm, n_owner, salt="universe|firms")
    ppf = p.get("patents_per_firm", {"kind": "nbinom", "r": 2.0, "p": 0.25})
    patents = su.build_patent_universe(
        n_pat, codes, weights, firms, salt="universe|patents",
        firm_size_family=ppf, design=design,
    )
    os.makedirs(INTERNAL, exist_ok=True)
    firms.to_parquet(FIRM_CACHE, index=False)
    patents.to_parquet(PATENT_CACHE, index=False)
    _FIRM, _PATENT = firms, patents
    return firms, patents


def firm_universe():
    return build_universes()[0]


def patent_universe():
    return build_universes()[1]


_PUBLIC_MASTER = None


def public_master_skeleton():
    """Return the committed PUBLIC master skeleton (Full_sample's public PC x year design columns),
    written by gen_00a. All columns are public (FDA product-code + Federal-Register reclassification
    design + calendar); this is NOT a real restricted read. gen_00d rebuilds every panel's public
    columns from this, so it never reads the real master. Cached after first load."""
    global _PUBLIC_MASTER
    if _PUBLIC_MASTER is None:
        if not os.path.exists(PUBLIC_MASTER_SKELETON):
            raise SystemExit(
                f"public master skeleton missing: {PUBLIC_MASTER_SKELETON}. Run gen_00a (Stage A) "
                "first -- it commits the public PC x year design gen_00d builds panels from."
            )
        _PUBLIC_MASTER = pd.read_parquet(PUBLIC_MASTER_SKELETON)
    return _PUBLIC_MASTER


def file_specs():
    """Return the committed per-file interlock specs (params['files']) gen_00d/gen_00e consume."""
    return load_params().get("files", {})


def assign_firm_rows(n_rows, salt, size_family=None):
    """Return an int64 array of length n_rows of permnos SAMPLED from the firm universe with
    independent co-membership (drop-in for `_link_remap` on a permno/LPERMNO column). The permnos
    are a subset of the firm universe -> they join to compustat's LPERMNO."""
    firms, _ = build_universes()
    fam = size_family or {"kind": "nbinom", "r": 1.5, "p": 0.05}
    return iu.assign_membership(int(n_rows), firms["permno"].to_numpy(), fam, salt=f"firm|{salt}")


def assign_firm_pairs(n_rows, salt, size_family=None):
    """Return (permno[], gvkey[]) of length n_rows, PAIRED from the firm universe with independent
    co-membership and EVERY universe firm covered >=1 time (support). Used for compustat, the firm
    ANCHOR: because every universe firm appears >=1 time, any other file's permnos (all drawn from
    the universe) are a subset of compustat's LPERMNO, so firm joins never drop rows."""
    firms, _ = build_universes()
    n = int(n_rows)
    idx_space = np.arange(len(firms), dtype=np.int64)
    fam = size_family or {"kind": "nbinom", "r": 1.36, "p": 0.11}
    # assign_membership over ENTITY INDICES guarantees >=1 obs/entity when n_rows >= n_firms
    firm_idx = iu.assign_membership(n, idx_space, fam, salt=f"firmpair|{salt}")
    permno = firms["permno"].to_numpy()[firm_idx]
    gvkey = firms["gvkey"].to_numpy()[firm_idx]
    return permno.astype(np.int64), gvkey.astype(np.int64)


def attrs_for_patents(patnums):
    """Return the patent-universe rows (PRODUCTCODE, permno, xi, cites, ...) for the given patnums,
    so a patent-subset file can attach a PC/firm consistent with the patent it sampled."""
    _, patents = build_universes()
    return patents.set_index("patnum").reindex(np.asarray(patnums)).reset_index()


def assign_patent_rows(n_rows, salt, replace=False):
    """Return an int64 array of length n_rows of patnums SAMPLED from the patent universe (drop-in
    for `build_map`/`assign_pc` on a patent file). Without replacement when one-row-per-patent."""
    _, patents = build_universes()
    key = patents["patnum"].to_numpy()
    N = len(key)
    n = int(n_rows)
    rng = iu.iu_rng("assign_patent_rows", salt, n, N)
    if not replace and n <= N:
        return key[rng.choice(N, size=n, replace=False)].astype(np.int64)
    return key[rng.integers(0, N, size=n)].astype(np.int64)


def assign_patent_rows_for_codes(n_rows, allowed_codes, salt, require_pre_event=False):
    """Sample a patent-file view from an event-specific product-code subset.

    The supplemental 2->1/3->2 files are replacements for base patent histories
    in ``gen_01_main_panels``. Assigning them across the whole code universe makes
    gen_01 discard the full base universe. This helper preserves their intended
    event scope and guarantees one qualifying support patent per allowed code.
    """
    _, patents = build_universes()
    design = _theta_design().set_index("PRODUCTCODE")
    allowed = pd.Index(pd.unique(pd.Series(list(allowed_codes), dtype=object))).dropna()
    pool = patents[patents["PRODUCTCODE"].isin(allowed)].copy()
    absent = sorted(set(allowed) - set(pool["PRODUCTCODE"]))
    if absent:
        raise ValueError(f"patent universe lacks {len(absent)} allowed product codes: {absent[:10]}")

    mandatory = []
    for code in allowed:
        candidates = pool[pool["PRODUCTCODE"] == code]
        if require_pre_event:
            row = design.loc[code]
            years = [row.get("year_reclassified_2_1"), row.get("year_reclassified_3_2")]
            years = [int(y) for y in years if pd.notna(y)]
            if years:
                candidates = candidates[candidates["filing_year"] < min(years)]
        if "required_support" in candidates and candidates["required_support"].any():
            candidates = candidates[candidates["required_support"]]
        if candidates.empty:
            raise ValueError(f"no qualifying support patent for product code {code}")
        mandatory.append(int(candidates.sort_values("patnum").iloc[0]["patnum"]))

    n = int(n_rows)
    if n < len(mandatory):
        raise ValueError(f"view has {n} rows but needs {len(mandatory)} mandatory support patents")
    # For II->I replacement views, inactive treated codes receive only their one
    # required out-of-panel sentinel. Drawing additional rows for them would undo the
    # selective-support contract and exhaust phase-11 controls again.
    is_21_view = (
        len(allowed) > 0
        and set(allowed).issubset(set(design.index[design["year_reclassified_2_1"].notna()]))
    )
    draw_pool = pool
    if is_21_view:
        active_codes = set(design.index[design["support_2_1"].astype(bool)])
        draw_pool = pool[pool["PRODUCTCODE"].isin(active_codes)]
        if draw_pool.empty:
            raise ValueError("II->I supplemental draw pool has no active product codes")
    keys = draw_pool["patnum"].to_numpy(dtype=np.int64)
    mandatory = np.asarray(mandatory, dtype=np.int64)
    remaining_pool = keys[~np.isin(keys, mandatory)]
    rng = iu.iu_rng("assign_patent_rows_for_codes", salt, n, len(keys))
    k = n - len(mandatory)
    if k <= len(remaining_pool):
        remainder = rng.choice(remaining_pool, size=k, replace=False)
    else:
        remainder = rng.choice(keys, size=k, replace=True)
    out = np.concatenate([mandatory, remainder]).astype(np.int64)
    return out[rng.permutation(len(out))]


# ======================================================================================
# Self-test -- fixture params, no real data. Proves cross-file overlap + independence.
# ======================================================================================
def _selftest():
    global _FIRM, _PATENT
    _FIRM = _PATENT = None
    # force fixture params by pointing PARAMS away (build from _FIXTURE)
    problems = []

    def check(c, m):
        if not c:
            problems.append(m)

    # build in-memory from fixture (no cache write during test)
    p = _FIXTURE
    ent = p["entities"]
    codes = np.array([c["code"] for c in p["product_codes"]])
    weights = np.arange(1, len(codes) + 1, dtype=float)
    firms = su.build_firm_universe(ent["firms_permno"]["cardinality"],
                                   ent["adverse_firms"]["cardinality"], salt="universe|firms")
    patents = su.build_patent_universe(ent["patents"]["cardinality"], codes, weights, firms,
                                       salt="universe|patents", firm_size_family=p["patents_per_firm"])
    _FIRM, _PATENT = firms, patents

    # (A) compustat = firm universe; an adverse file's permno subset of it (join resolves)
    adv_permno = iu.assign_membership(500_000, firms["permno"].to_numpy(),
                                      {"kind": "nbinom", "r": 1.5, "p": 0.001}, salt="firm|adverse")
    check(set(np.unique(adv_permno)).issubset(set(firms["permno"])),
          "adverse permno not subset of firm universe (join to compustat would drop rows)")

    # (B) a patent subset file's patnum subset of all_patents (= patent universe)
    saf = assign_patent_rows(40_000, salt="safety")
    check(set(np.unique(saf)).issubset(set(patents["patnum"])),
          "safety patnum not subset of patent universe")

    # (C) independence: adverse permno co-membership uncorrelated with a real partition
    rng0 = np.random.default_rng(3)
    real = rng0.integers(0, 4_600, size=len(adv_permno))
    a = rng0.integers(0, len(adv_permno), size=200_000); b = rng0.integers(0, len(adv_permno), size=200_000)
    m = a != b; a, b = a[m], b[m]
    rc = real[a] == real[b]; sc = adv_permno[a] == adv_permno[b]
    lift = abs(sc[rc].mean() - sc.mean()) if rc.any() else 0.0
    check(lift < 0.01, f"adverse firm co-membership correlated with real partition (lift={lift:.4f})")

    # (D) determinism
    saf2 = assign_patent_rows(40_000, salt="safety")
    check(np.array_equal(saf, saf2), "assign_patent_rows not deterministic")

    # (E) fake domains
    check(adv_permno.min() >= iu.LINK_FAKE_MIN, "permno below fake domain")
    check(saf.min() >= iu.PATENT_FAKE_MIN, "patnum below fake domain")

    _FIRM = _PATENT = None
    if problems:
        print("universe_backend self-test: FAIL")
        for x in problems:
            print("  -", x)
        raise SystemExit(1)
    print("universe_backend self-test: PASS "
          "(compustat=firm universe; adverse/safety keys subset -> joins resolve; co-membership "
          "independent; deterministic; fake domains)")


if __name__ == "__main__":
    _selftest()
