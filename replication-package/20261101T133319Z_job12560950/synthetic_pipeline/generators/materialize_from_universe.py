"""
materialize_from_universe.py -- Phase 2.3 wiring ENGINE. Turns the canonical synthetic universes
(synthetic_universe.build_patent_universe / build_firm_universe) into each individual output file
as a VIEW/SUBSET of the SAME universe, so cross-file joins resolve WITHOUT any real id.

The key idea that replaces gen_00g's single real->fake patnum map: every patent-bearing file
SAMPLES its rows from the one canonical patent universe (carrying the canonical patnum), and every
firm-bearing file references the one canonical firm universe (canonical permno). Two files that
each sample from the universe therefore have OVERLAPPING keys that are both subsets of the
universe -- exactly the cross-file merge-key overlap audit_simulated_data._cross_file_consistency
checks -- and there is no real->synthetic correspondence anywhere.

Contract per file = a ROLE MAP: {output_col: role}, where role is one of
    ("universe", src_col)   take the value from the sampled universe row (renamed)
    ("value", spec)         draw generatively from a committed distribution spec
    ("const", v)            constant fill
    ("public", series)      keep a PUBLIC real column verbatim (panels only; e.g. PRODUCTCODE,year)
plus an optional missingness rate per column (committed). The engine reads NO real data; callers
pass the real SCHEMA (column names/order) and any PUBLIC columns explicitly. Self-test uses
fixtures only and proves cross-file key overlap, schema fidelity, no-real-values, and support.
"""
import numpy as np
import pandas as pd

import independent_universe as iu


def sample_entities(universe, key_col, n_rows, salt, replace=False):
    """Return n_rows rows sampled from `universe` (a fresh universe DataFrame). Without replacement
    when the file is one-row-per-entity (n_rows <= len) -> the sampled keys are a SUBSET of the
    universe (joins resolve); with replacement for files that repeat an entity across rows.
    Deterministic in (PUBLIC_SEED, salt)."""
    n_rows = int(n_rows)
    N = len(universe)
    if N == 0 or n_rows <= 0:
        return universe.iloc[0:0].copy()
    rng = iu.iu_rng("sample_entities", salt, key_col, n_rows, N)
    if not replace and n_rows <= N:
        idx = rng.choice(N, size=n_rows, replace=False)
    else:
        idx = rng.integers(0, N, size=n_rows)
    return universe.iloc[idx].reset_index(drop=True)


def _draw_value(spec, n, salt):
    """Draw n values from a committed distribution spec for a file-only value column."""
    rng = iu.iu_rng("matval", salt, spec.get("kind"), n)
    kind = spec.get("kind")
    if kind == "lognormal":
        return np.round(rng.lognormal(spec.get("mu", 0.0), spec.get("sigma", 1.0), size=n), 4)
    if kind == "normal":
        return np.round(rng.normal(spec.get("mu", 0.0), spec.get("sigma", 1.0), size=n), 4)
    if kind == "poisson":
        return rng.poisson(spec.get("lam", 1.0), size=n).astype(float)
    if kind == "bernoulli":
        return (rng.random(n) < spec.get("p", 0.5)).astype(int)
    if kind == "uniform_int":
        return rng.integers(spec.get("lo", 0), spec.get("hi", 2), size=n)
    if kind == "choice":
        return rng.choice(np.asarray(spec["values"]), size=n)
    if kind == "tokens":
        # fresh identity tokens with committed cardinality K and INDEPENDENT co-membership (each row
        # drawn independently). Replaces reading a real identity column (GRID/assignee/inventor/...).
        K = max(int(spec.get("cardinality", max(n // 10, 1))), 1)
        prefix = spec.get("prefix", "SYN")
        idx = rng.integers(0, K, size=n)
        return np.array([f"{prefix}{i:07d}" for i in range(K)], dtype=object)[idx]
    raise ValueError(f"_draw_value: unknown value spec {kind!r}")


def materialize(name, schema, role_map, n_rows, sampled_universe=None,
                missingness=None, salt=None):
    """Build one output DataFrame with EXACTLY `schema` columns (names + order), each populated per
    its role. `sampled_universe` is a frame already sampled to n_rows (from sample_entities) whose
    columns supply the ("universe", src) roles. Returns the DataFrame.

    Guarantees: output columns == schema (order preserved); universe-sourced key columns carry
    canonical universe ids (so cross-file joins resolve); value columns are generative; missingness
    applied at committed RATES (never exact counts)."""
    salt = salt or name
    n_rows = int(n_rows)
    out = {}
    for col in schema:
        role = role_map.get(col)
        if role is None:
            raise ValueError(f"materialize[{name}]: no role for column {col!r}")
        kind = role[0]
        if kind == "universe":
            src = role[1]
            if sampled_universe is None or src not in sampled_universe.columns:
                raise ValueError(f"materialize[{name}]: universe col {src!r} missing for {col!r}")
            out[col] = np.asarray(sampled_universe[src].to_numpy())[:n_rows]
        elif kind == "value":
            out[col] = _draw_value(role[1], n_rows, f"{salt}|{col}")
        elif kind == "const":
            out[col] = np.full(n_rows, role[1])
        elif kind == "public":
            series = np.asarray(role[1])
            if len(series) != n_rows:
                raise ValueError(f"materialize[{name}]: public col {col!r} len {len(series)} != {n_rows}")
            out[col] = series
        else:
            raise ValueError(f"materialize[{name}]: unknown role {kind!r} for {col!r}")
    df = pd.DataFrame(out, columns=list(schema))
    # apply committed-rate missingness to declared columns (breaks the exact-count + fingerprint leaks)
    for col, rate in (missingness or {}).items():
        if col in df.columns:
            mask = iu.draw_missingness(n_rows, rate, f"{salt}|miss|{col}")
            df.loc[mask, col] = np.nan
    return df


# ======================================================================================
# Self-test -- fixtures only. Proves cross-file key overlap + schema + no-real + support.
# ======================================================================================
def _selftest():
    import synthetic_universe as su
    problems = []

    def check(c, m):
        if not c:
            problems.append(m)

    codes = np.array([f"PC{i:04d}" for i in range(200)])
    weights = np.arange(1, 201, dtype=float)
    firms = su.build_firm_universe(26_000, 4_500, salt="mt")
    patents = su.build_patent_universe(120_000, codes, weights, firms, salt="mt")

    # File A: the full patent list (all_patents_w_xi analogue) -- one row per patent.
    schemaA = ["patnum", "PRODUCTCODE", "permno", "xi", "cites", "extra_flag"]
    rolesA = {
        "patnum": ("universe", "patnum"),
        "PRODUCTCODE": ("universe", "PRODUCTCODE"),
        "permno": ("universe", "permno"),
        "xi": ("universe", "xi"),
        "cites": ("universe", "cites"),
        "extra_flag": ("value", {"kind": "bernoulli", "p": 0.2}),
    }
    sampA = sample_entities(patents, "patnum", len(patents), salt="fileA", replace=False)
    fileA = materialize("A", schemaA, rolesA, len(sampA), sampled_universe=sampA,
                        missingness={"xi": 0.05}, salt="fileA")

    # File B: a SUBSET patent file (safety_vars analogue) -- fewer patents, sampled from the SAME
    # universe. Its patnums MUST be a subset of File A's (joins resolve) with no real id anywhere.
    schemaB = ["patnum", "safety_flag"]
    rolesB = {"patnum": ("universe", "patnum"), "safety_flag": ("value", {"kind": "bernoulli", "p": 0.3})}
    sampB = sample_entities(patents, "patnum", 40_000, salt="fileB", replace=False)
    fileB = materialize("B", schemaB, rolesB, len(sampB), sampled_universe=sampB, salt="fileB")

    # (1) schema fidelity
    check(list(fileA.columns) == schemaA, "fileA schema mismatch")
    check(list(fileB.columns) == schemaB, "fileB schema mismatch")

    # (2) CROSS-FILE key overlap: both files' patnums subset the universe; B subset of A
    uni_keys = set(patents["patnum"])
    check(set(fileA["patnum"]).issubset(uni_keys), "fileA patnum not subset of universe")
    check(set(fileB["patnum"]).issubset(uni_keys), "fileB patnum not subset of universe")
    check(set(fileB["patnum"]).issubset(set(fileA["patnum"])),
          "fileB patnums not joinable to fileA (cross-file overlap broken)")
    # the merge actually resolves (non-empty, all B rows match)
    merged = fileB.merge(fileA[["patnum", "PRODUCTCODE"]], on="patnum", how="left")
    check(merged["PRODUCTCODE"].notna().all(), "fileB->fileA join dropped rows")

    # (3) ids in fake domains; no real correspondence (ids are the universe's fresh ids)
    check(fileA["patnum"].min() >= iu.PATENT_FAKE_MIN, "fileA patnum below fake domain")
    check(fileA["permno"].min() >= iu.LINK_FAKE_MIN, "fileA permno below fake domain")

    # (4) missingness applied at ~rate, deterministic
    check(abs(fileA["xi"].isna().mean() - 0.05) < 0.01, f"xi missingness off {fileA['xi'].isna().mean():.3f}")
    fileA2 = materialize("A", schemaA, rolesA, len(sampA), sampled_universe=sampA,
                         missingness={"xi": 0.05}, salt="fileA")
    check(fileA.equals(fileA2), "materialize not deterministic")

    # (5) value columns are generative (present, right support)
    check(set(fileA["extra_flag"].unique()) <= {0, 1}, "extra_flag not bernoulli")

    # (6) fail closed on a missing role
    try:
        materialize("bad", ["x"], {}, 5); problems.append("materialize passed a missing role")
    except ValueError:
        pass

    if problems:
        print("materialize_from_universe self-test: FAIL")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("materialize_from_universe self-test: PASS "
          "(schema fidelity; cross-file key overlap B⊆A⊆universe with joins resolving; fake "
          "domains; rate-based missingness; deterministic; fail-closed)")


if __name__ == "__main__":
    _selftest()
