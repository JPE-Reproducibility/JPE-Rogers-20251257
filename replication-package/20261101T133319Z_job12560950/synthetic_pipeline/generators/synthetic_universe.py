"""
synthetic_universe.py -- STAGE B backbone: build the fresh synthetic ENTITY UNIVERSES once,
then every patent-/firm-bearing file is a VIEW over them. This is the "generate, don't map"
core: there is no real->synthetic id map anywhere; the universes are drawn from committed
public parameters + a public seed via independent_universe primitives.

Two canonical universes:
  * FIRM universe   : fresh permno/gvkey ids (>= 1M), a patent-owning subset, synthetic
                      firm-size driver. Cardinality = committed rounded param.
  * PATENT universe : fresh patnum ids (>= 90M); each patent assigned (by DRAW, not by real id)
                      a PUBLIC product code (theta-weighted), an owning firm (independent
                      co-membership over the patent-owning firm subset), a filing year, and
                      theta-driven outcomes (xi, cites, breakthrough, safety).

Internal join consistency (what audit_simulated_data._cross_file_consistency needs):
  patent.permno is a subset of firm.permno  (patents<->firms join resolves)
  patent.PRODUCTCODE is a subset of the public code list  (patents<->panels join resolves)
Because both universes are generated (not mapped from real rows), the real firm/patent
co-membership partition does NOT survive, yet the synthetic joins are internally exact.

Decoupled from real-data reads for testability: callers pass the committed cardinalities and the
theta code list + weights (which gen_00b builds from the PUBLIC product-code list). `_selftest()`
runs with fixture params -- no real data -- and asserts determinism, fake-domain, internal join
consistency, independence of co-membership, and >=1 obs support.
"""
import numpy as np
import pandas as pd

import independent_universe as iu


def build_firm_universe(n_firms, n_patent_owning, salt="firms",
                        size_family=None):
    """Return a firms DataFrame with fresh permno + gvkey ids and a patent-owning flag.

    n_firms, n_patent_owning: committed ROUNDED cardinalities (from simulation_parameters.json).
    No real firm id is read; ids are a seeded sample of the fake link domain."""
    n_firms = int(n_firms)
    n_patent_owning = min(int(n_patent_owning), n_firms)
    permno = iu.generate_permno_ids(n_firms, salt=f"{salt}|permno")
    gvkey = iu.generate_entity_ids(n_firms, iu.LINK_FAKE_MIN, iu.LINK_FAKE_SPACE,
                                   salt=f"{salt}|gvkey")
    # choose the patent-owning subset deterministically (seeded), independent of any real flag
    rng = iu.iu_rng("patent_owning", salt, n_firms, n_patent_owning)
    own_idx = rng.choice(n_firms, size=n_patent_owning, replace=False)
    is_owner = np.zeros(n_firms, dtype=bool)
    is_owner[own_idx] = True
    # a synthetic firm-size driver (lognormal), purely generative
    firmsize = np.round(iu.iu_rng("firmsize", salt, n_firms).lognormal(4.0, 1.3, size=n_firms), 4)
    return pd.DataFrame({
        "permno": permno,
        "gvkey": gvkey,
        "is_patent_owner": is_owner,
        "firmsize_driver": firmsize,
    })


def build_patent_universe(n_patents, codes, weights, firms,
                          salt="patents", firm_size_family=None,
                          theta_lookup=None, design=None):
    """Return a patents DataFrame: fresh patnum, a theta-weighted PUBLIC product code, an owning
    firm (independent co-membership), a filing year, and theta-driven outcomes.

    n_patents  : committed ROUNDED patent cardinality.
    codes,weights : the PUBLIC product-code list + theta pat_weight (from gen_00b.load_theta()).
    firms      : the firm universe from build_firm_universe (uses its patent-owning subset).
    theta_lookup(pc_array, col) -> per-patent effect (optional; gen_00b.theta_lookup in real runs).
    """
    n = int(n_patents)
    patnum = iu.generate_patent_ids(n, salt=f"{salt}|patnum")
    # product code by DRAW from the theta-weighted PUBLIC list (NOT hash of a real id)
    pc = iu.assign_public_codes(n, np.asarray(codes), np.asarray(weights, dtype=float),
                                salt=f"{salt}|pc")
    # owning firm: assign the n patents to the patent-owning firm subset with INDEPENDENT
    # co-membership (drawn size distribution), so real firm<->patent grouping does not survive
    owners = firms.loc[firms["is_patent_owner"], "permno"].to_numpy()
    if owners.size == 0:
        owners = firms["permno"].to_numpy()
    fam = firm_size_family or {"kind": "nbinom", "r": 2.0, "p": 0.25}
    permno = iu.assign_membership(n, owners, fam, salt=f"{salt}|patent_firm")
    # Filing year is generated once in the canonical universe and reused by every patent
    # view.  The earlier implementation retained each source file's row year, so the same
    # synthetic patent could acquire inconsistent years across files.
    yr_rng = iu.iu_rng("filing_year", salt, n)
    filing_year = yr_rng.integers(1976, 2020, size=n)
    required_support = np.zeros(n, dtype=bool)

    # Deterministic support contract for matched/event-study samples. Sampling weights
    # make empty cells unlikely, not impossible. Reserve one Grant-eligible patent for
    # every public product code so gen_01's later-treated matching cannot exhaust the
    # public good-control pool merely because synthetic controls were patent-empty.
    # Place treated support strictly before its earliest public event year.
    if design is not None:
        d = pd.DataFrame(design).copy()
        required = {"PRODUCTCODE", "is_control", "year_reclassified_2_1",
                    "year_reclassified_3_2", "panel_support_year",
                    "pre_event_support_year", "support_2_1",
                    "analysis_support_year"}
        missing = required - set(d.columns)
        if missing:
            raise ValueError(f"patent-universe design missing columns: {sorted(missing)}")
        d = d[d["PRODUCTCODE"].isin(np.asarray(codes))].drop_duplicates("PRODUCTCODE")
        y21 = pd.to_numeric(d["year_reclassified_2_1"], errors="coerce")
        y32 = pd.to_numeric(d["year_reclassified_3_2"], errors="coerce")
        eligible = d.copy()
        if len(eligible) > n:
            raise ValueError(
                f"patent universe has {n} rows but needs {len(eligible)} support rows"
            )
        support_rng = iu.iu_rng("event_support", salt, n, len(eligible))
        positions = support_rng.choice(n, size=len(eligible), replace=False)
        for pos, row in zip(positions, eligible.itertuples(index=False)):
            pc[pos] = row.PRODUCTCODE
            required_support[pos] = True
            if pd.isna(row.analysis_support_year):
                raise ValueError(f"product code {row.PRODUCTCODE} has no analysis support year")
            filing_year[pos] = int(row.analysis_support_year)

    # theta-driven outcomes (fall back to seeded draws when no real theta is supplied, e.g. tests)
    if theta_lookup is not None:
        mu_xi = theta_lookup(pc, "mu_xi")
        mu_cite = theta_lookup(pc, "mu_cite")
        p_bk = theta_lookup(pc, "p_breakthrough")
        p_sf = theta_lookup(pc, "p_safety")
    else:
        r = iu.iu_rng("outcome_fallback", salt, n)
        mu_xi = r.lognormal(1.0, 0.9, size=n)
        mu_cite = r.gamma(2.0, 6.0, size=n)
        p_bk = np.full(n, 0.15)
        p_sf = np.full(n, 0.22)
    o = iu.iu_rng("outcomes", salt, n)
    xi = np.round(o.lognormal(np.log(np.clip(mu_xi, 1e-3, None)), 0.5), 4)
    cites = o.poisson(np.clip(mu_cite, 0.0, None)).astype(float)
    breakthrough = (o.random(n) < np.clip(p_bk, 0.0, 1.0)).astype(int)
    safety = (o.random(n) < np.clip(p_sf, 0.0, 1.0)).astype(int)

    return pd.DataFrame({
        "patnum": patnum,
        "PRODUCTCODE": pc,
        "permno": permno,
        "filing_year": filing_year,
        "required_support": required_support,
        "xi": xi,
        "cites": cites,
        "breakthrough": breakthrough,
        "safety": safety,
    })


# ======================================================================================
# Self-test -- fixture params, NO real data. Asserts the universe contract.
# ======================================================================================
def _selftest():
    problems = []

    def check(c, m):
        if not c:
            problems.append(m)

    # fixture committed params (rounded cardinalities) + a public code list with theta weights
    codes = np.array([f"PC{i:04d}" for i in range(300)])
    weights = np.arange(1, 301, dtype=float)
    firms = build_firm_universe(n_firms=26_000, n_patent_owning=4_500, salt="t")
    design = pd.DataFrame({
        "PRODUCTCODE": codes,
        "is_control": np.arange(len(codes)) % 9 == 0,
        "year_reclassified_2_1": np.where(np.arange(len(codes)) % 50 == 0, 1996, np.nan),
        "year_reclassified_3_2": np.where(np.arange(len(codes)) % 70 == 0, 2015, np.nan),
        "panel_support_year": 1990,
        "pre_event_support_year": np.where(
            (np.arange(len(codes)) % 50 == 0) | (np.arange(len(codes)) % 70 == 0),
            1990, np.nan),
        "support_2_1": np.arange(len(codes)) % 50 == 0,
        "analysis_support_year": 1990,
    })
    pats = build_patent_universe(n_patents=120_000, codes=codes, weights=weights, firms=firms,
                                 salt="t", design=design)

    # (A) fresh, distinct, in-domain ids
    check(firms["permno"].is_unique, "firm permno not unique")
    check(firms["gvkey"].is_unique, "firm gvkey not unique")
    check(firms["permno"].min() >= iu.LINK_FAKE_MIN, "firm permno below fake domain")
    check(pats["patnum"].is_unique, "patnum not unique")
    check(pats["patnum"].min() >= iu.PATENT_FAKE_MIN, "patnum below fake domain")

    # (B) internal join consistency: patent.permno subset of firm.permno; PC subset of code list
    owners = set(firms.loc[firms.is_patent_owner, "permno"])
    check(set(pats["permno"]).issubset(owners), "patent permno not a subset of owning firms")
    check(set(pats["PRODUCTCODE"]).issubset(set(codes)), "patent PC not a subset of code list")

    # (C) support: every used firm has >=1 patent; every public code appears; PC weighted
    vc = pats["permno"].value_counts()
    check(vc.min() >= 1, "a used firm has 0 patents")
    hi = (pats.PRODUCTCODE == codes[-1]).sum(); lo = (pats.PRODUCTCODE == codes[0]).sum()
    check(hi > lo, "product-code assignment ignored theta weights")
    support = pats.merge(design, on="PRODUCTCODE", how="left")
    for event in ("2_1", "3_2"):
        ycol = f"year_reclassified_{event}"
        treated = design.loc[design[ycol].notna(), "PRODUCTCODE"]
        pre = support.loc[support["filing_year"] < support[ycol], "PRODUCTCODE"]
        check(set(treated).issubset(set(pre)), f"{event} treated code lacks pre-event support")
    check(set(design["PRODUCTCODE"]).issubset(set(pats["PRODUCTCODE"])),
          "public product code lacks patent support")
    expected_year = design.set_index("PRODUCTCODE")["analysis_support_year"]
    observed = pats[pats.required_support].set_index("PRODUCTCODE")["filing_year"]
    check((observed.reindex(design.PRODUCTCODE) == expected_year.reindex(design.PRODUCTCODE)).all(),
          "support patent misses its committed analysis-support year")

    # (D) determinism: rebuild -> byte identical
    firms2 = build_firm_universe(26_000, 4_500, salt="t")
    pats2 = build_patent_universe(120_000, codes, weights, firms2, salt="t", design=design)
    check(firms.equals(firms2), "firm universe not deterministic")
    check(pats.equals(pats2), "patent universe not deterministic")

    # (E) independence: the patent->firm co-membership must NOT reproduce a real partition.
    # Build a fake "real" firm assignment of the SAME patents and confirm ~chance agreement.
    rng0 = np.random.default_rng(7)
    real_firm = rng0.integers(0, 4_500, size=len(pats))
    a = rng0.integers(0, len(pats), size=200_000); b = rng0.integers(0, len(pats), size=200_000)
    m = a != b; a, b = a[m], b[m]
    real_co = real_firm[a] == real_firm[b]
    syn_co = pats["permno"].to_numpy()[a] == pats["permno"].to_numpy()[b]
    lift = abs(syn_co[real_co].mean() - syn_co.mean()) if real_co.any() else 0.0
    check(lift < 0.01, f"patent->firm co-membership correlated with a real partition (lift={lift:.4f})")

    # (F) cardinalities honor the committed rounded params (not some exact real count)
    check(firms.shape[0] == 26_000 and pats.shape[0] == 120_000, "cardinality != committed param")

    if problems:
        print("synthetic_universe self-test: FAIL")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("synthetic_universe self-test: PASS "
          "(fresh universes, internal joins resolve, weighted+supported, deterministic, "
          "co-membership independent, committed cardinalities)")


if __name__ == "__main__":
    _selftest()
