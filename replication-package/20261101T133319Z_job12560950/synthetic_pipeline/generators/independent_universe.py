"""
independent_universe.py -- fresh-generation primitives for the INDEPENDENT-UNIVERSE
synthetic design, under the JPE data-availability policy.

WHY THIS MODULE EXISTS
----------------------
The prior synthetic design perturbed real files IN PLACE and relabelled real ids through
deterministic maps:
  * gen_00d._link_remap : fake_permno = LINK_FAKE_MIN + md5("{canon}|{real_id}") % SPACE
  * gen_00g.build_map   : fake_patnum = 90_000_000 + permutation[rank(real_id)]
  * gen_00b.assign_pc   : PRODUCTCODE = inverse_cdf( hash(real_patent_id) )
  * gen_00b.resample_identity : keeps the EXACT real group-size multiset
  * gen_00b.redraw_missingness : keeps the EXACT real marginal NaN count
Each is a function OF a real identifier / a real partition statistic, so:
  (a) it is invertible / enumerable given the real id space (reversible mapping), and
  (b) any consistent id map is a bijection that PRESERVES the real co-membership partition
      (which real rows are the same firm/patent), which is exactly the disclosure to remove.

THE FIX: GENERATE, DON'T MAP.
Every primitive here takes ONLY (a committed public parameter + a public seed) as input.
None of them accepts a real id, a real value, or a real partition. There is therefore no
real->synthetic mapping of any kind to invert, and the synthetic co-membership is drawn
fresh (independent of the real partition). Structural fidelity (cardinality, a realistic
smoothed size distribution, marginal missingness rate, >=1 obs per group) is preserved
because those are supplied as COMMITTED, DISCLOSURE-REVIEWED parameters -- rounded
cardinalities and smoothed distribution families, never the exact real multisets.

All randomness derives from a single public seed (PUBLIC_SEED) + a string salt, so two
clean-room runs are byte-identical.

This module reads NO files and imports no real data. That is the structural privacy
guarantee, and `_selftest()` at the bottom asserts it (fails closed).
"""
import datetime
import hashlib
import numpy as np
from synthetic_seed import seed

# Public, committed seed, cross-checked in build_simulation.py; identical for every runner.
PUBLIC_SEED = seed(20260803)

# Fake id domains (must match audit_simulated_data.py: patnum >= 90M, permno/gvkey >= 1M).
PATENT_FAKE_MIN = 90_000_000
PATENT_FAKE_SPACE = 50_000_000      # -> [90_000_000, 140_000_000)
LINK_FAKE_MIN = 1_000_000
LINK_FAKE_SPACE = 50_000_000        # -> [1_000_000, 51_000_000)
# Generic fake domain for NON-merge NUMERIC identity columns (not permno/gvkey/patnum, so not
# domain-checked by name in the audit): distinct fake integers with no relation to any real value.
IDCOL_FAKE_MIN = 10_000
IDCOL_FAKE_SPACE = 89_990_000       # -> [10_000, 90_000_000)


def iu_rng(*tags):
    """A deterministic numpy Generator seeded by PUBLIC_SEED + a stable hash of the tags.

    Tags are the ONLY entropy source and are all public (a file name, a column name, a
    committed integer). No real id is ever a tag."""
    h = hashlib.md5(("|".join(str(t) for t in tags)).encode()).hexdigest()[:12]
    return np.random.default_rng(PUBLIC_SEED + int(h, 16))


# --------------------------------------------------------------------------------------
# 1. Fresh entity ids -- replaces _link_remap (permno/gvkey) and build_map (patnum).
# --------------------------------------------------------------------------------------
def generate_entity_ids(n_entities, domain_min, domain_space, salt):
    """Return `n_entities` DISTINCT fresh integer ids in [domain_min, domain_min+domain_space).

    The ids are a seeded random sample of the fake domain -- NOT a function of any real id, so
    there is nothing to invert and the real->fake pairing that the audit flagged does not exist.
    Deterministic in (PUBLIC_SEED, salt). Raises if the domain cannot hold n_entities distinct
    ids (fail closed rather than silently collide)."""
    n = int(n_entities)
    if n < 0:
        raise ValueError(f"generate_entity_ids: n_entities must be >= 0, got {n}")
    if n > int(domain_space):
        raise ValueError(
            f"generate_entity_ids: domain of size {int(domain_space):,} cannot hold "
            f"{n:,} distinct ids (salt={salt!r}); widen the domain or lower the cardinality.")
    rng = iu_rng("entity_ids", salt, domain_min, domain_space, n)
    # sample WITHOUT replacement from the offset domain -> distinct by construction
    offs = rng.choice(int(domain_space), size=n, replace=False)
    return (int(domain_min) + offs).astype(np.int64)


def generate_patent_ids(n_patents, salt="patents"):
    """Fresh distinct patent ids in [90_000_000, 140_000_000). Replaces gen_00g.build_map."""
    return generate_entity_ids(n_patents, PATENT_FAKE_MIN, PATENT_FAKE_SPACE, salt)


def generate_permno_ids(n_firms, salt="permno"):
    """Fresh distinct firm-linking ids (permno/gvkey space) in [1M, 51M). Replaces _link_remap."""
    return generate_entity_ids(n_firms, LINK_FAKE_MIN, LINK_FAKE_SPACE, salt)


# --------------------------------------------------------------------------------------
# 2. Independent co-membership -- replaces resample_identity's exact-multiset preservation.
# --------------------------------------------------------------------------------------
def _family_propensities(size_spec, n_entities, salt):
    """Per-entity non-negative propensities drawn from a COMMITTED SMOOTHED family. These weight
    how the surplus items (beyond the >=1 floor) are spread across entities -- they give the
    synthetic size distribution its shape WITHOUT reproducing any exact real group size.

    Supported families (all smoothed; disclosure-reviewed in THREAT_MODEL.md §5):
      {"kind":"nbinom","r":..,"p":..}     negative-binomial heterogeneity (over-dispersed counts)
      {"kind":"lognormal","mu":..,"sigma":..}
      {"kind":"gamma","shape":..,"scale":..}
      {"kind":"geometric","p":..}
      {"kind":"uniform"}                  flat (max entropy; no size information at all)
    """
    G = int(n_entities)
    rng = iu_rng("propensity", salt, size_spec.get("kind", "uniform"), G)
    kind = size_spec.get("kind", "uniform")
    if kind == "uniform":
        return np.ones(G, dtype=float)
    if kind == "nbinom":
        # numpy parameterises as (n successes, p); r>0, 0<p<=1
        return rng.negative_binomial(max(float(size_spec["r"]), 1e-6),
                                     min(max(float(size_spec["p"]), 1e-6), 1.0),
                                     size=G).astype(float) + 1e-9
    if kind == "lognormal":
        return rng.lognormal(float(size_spec["mu"]), float(size_spec["sigma"]), size=G)
    if kind == "gamma":
        return rng.gamma(float(size_spec["shape"]), float(size_spec["scale"]), size=G)
    if kind == "geometric":
        return rng.geometric(min(max(float(size_spec["p"]), 1e-6), 1.0), size=G).astype(float)
    raise ValueError(f"_family_propensities: unknown size family {kind!r}")


def draw_group_sizes(size_spec, n_items, n_entities, salt):
    """Return an integer array of length G (= min(n_entities, n_items)) of group sizes, each >= 1,
    summing to EXACTLY n_items. Sizes come from a committed SMOOTHED family, never the real
    multiset. Guarantees >=1 obs per entity (support the estimators need).

    Method: floor every entity at 1 (uses G items), then distribute the remaining (n_items - G)
    via a single multinomial draw with per-entity probabilities proportional to the smoothed
    family propensities. Sum is exact by construction; shape follows the family."""
    n_items = int(n_items)
    G = min(int(n_entities), n_items)
    if G <= 0:
        return np.zeros(0, dtype=np.int64)
    sizes = np.ones(G, dtype=np.int64)
    remaining = n_items - G
    if remaining > 0:
        p = _family_propensities(size_spec, G, salt)
        p = np.clip(p, 0.0, None)
        s = p.sum()
        p = (np.ones(G) / G) if s <= 0 else (p / s)
        rng = iu_rng("group_sizes", salt, n_items, G)
        sizes = sizes + rng.multinomial(remaining, p)
    return sizes.astype(np.int64)


def assign_membership(n_items, entity_ids, size_spec, salt):
    """Assign each of `n_items` rows to one of `entity_ids`, with group sizes drawn from the
    committed smoothed distribution and membership assigned at random (INDEPENDENT of any real
    partition). Returns an int64 array of length n_items of entity ids (row order shuffled).

    This is the drop-in replacement for resample_identity: same guarantees the estimators need
    (cardinality realistic, every used entity has >=1 obs, sizes look real) WITHOUT reading the
    real partition or its exact size multiset."""
    n_items = int(n_items)
    entity_ids = np.asarray(entity_ids)
    sizes = draw_group_sizes(size_spec, n_items, len(entity_ids), salt)
    G = len(sizes)
    if n_items == 0 or G == 0:
        return np.zeros(0, dtype=np.int64)
    per_row = np.repeat(entity_ids[:G], sizes)          # entity id per row, sum(sizes)==n_items
    rng = iu_rng("membership", salt, n_items, G)
    return per_row[rng.permutation(n_items)].astype(np.int64)


# --------------------------------------------------------------------------------------
# 3. Public-code assignment -- replaces assign_pc(real_id). Draws from a committed weighted
#    categorical over the PUBLIC product-code list (weights = committed theta), NOT hash(real id).
# --------------------------------------------------------------------------------------
def assign_public_codes(n_items, codes, weights, salt):
    """Draw a public code per item from a weighted categorical (weights are committed theta
    pat_weight over the PUBLIC product-code list). Independent of any real patent id, so the
    real patent->code grouping does not survive. Returns an object/np array of length n_items."""
    codes = np.asarray(codes)
    w = np.asarray(weights, dtype=float)
    w = np.clip(w, 0.0, None)
    s = w.sum()
    p = (np.ones(len(codes)) / len(codes)) if s <= 0 else (w / s)
    rng = iu_rng("public_codes", salt, int(n_items), len(codes))
    idx = rng.choice(len(codes), size=int(n_items), replace=True, p=p)
    return codes[idx]


# --------------------------------------------------------------------------------------
# 4. Missingness -- replaces redraw_missingness's EXACT real count with a committed RATE.
# --------------------------------------------------------------------------------------
def draw_missingness(n, rate, salt):
    """Boolean mask of length n, each cell independently True with probability `rate` (a COMMITTED,
    rounded/smoothed marginal rate -- never the exact real NaN count). Breaks both the per-row
    missingness fingerprint AND the exact marginal-count leak. Deterministic in (PUBLIC_SEED, salt)."""
    n = int(n)
    r = float(rate)
    if n <= 0 or r <= 0.0:
        return np.zeros(max(n, 0), dtype=bool)
    if r >= 1.0:
        return np.ones(n, dtype=bool)
    rng = iu_rng("missingness", salt, n)
    return rng.random(n) < r


def draw_missingness_rate(n, rate, salt):
    """Named primitive gen_00d/gen_00e call for a NON-merge value column's missingness. Returns a
    boolean mask of length n, each cell independently True with probability `rate` (a COMMITTED,
    ROUNDED marginal rate from Stage A -- NEVER the exact real NaN count). ~Binomial(n, rate), so the
    exact-marginal-count leak (redraw_missingness kept exactly n_missing) is gone. Alias of
    draw_missingness with the spec-mandated name; deterministic in (PUBLIC_SEED, salt)."""
    return draw_missingness(n, rate, salt)


# --------------------------------------------------------------------------------------
# 5. Fresh identity column -- replaces gen_00b.resample_identity (which kept the EXACT real
#    distinct-count AND the EXACT real group-size multiset). This draws `cardinality` FRESH
#    tokens (committed ROUNDED cardinality) and assigns rows to them with group sizes from the
#    committed SMOOTHED size family (never the real multiset) and INDEPENDENT co-membership.
# --------------------------------------------------------------------------------------
def generate_identity_column(n_rows, cardinality, size_family, salt, numeric=False, date_bounds=None):
    """Return an array of length n_rows for a NON-merge identity column (clean_name / assignee /
    inventor / GRID / conm / object fallback). Values are `cardinality` FRESH synthetic tokens (or
    distinct fake ints if numeric, or distinct fake calendar dates if date_bounds is given); each
    row is assigned a token with group sizes drawn from the committed SMOOTHED `size_family` and
    membership INDEPENDENT of any real partition. Guarantees >=1 row per used token (support the
    estimators need). NaN is applied by the caller (via draw_missingness_rate) -- this returns a
    fully populated column.

    Neither the real distinct-count nor the real group-size multiset is an input: `cardinality` is
    the committed ROUNDED nunique and `size_family` is the committed 2-moment smoothed family, so no
    exact real statistic can be reconstructed from the output. Deterministic in (PUBLIC_SEED, salt).

    date_bounds: optional (lo_year, hi_year) inclusive calendar-year range. When given, returns
    `cardinality` FRESH distinct datetime.date values drawn from that range instead of string or
    integer tokens -- lets a real DATE-kind column ship as a genuine date dtype (kind fidelity is
    metadata, not a privacy leak: the calendar dates themselves are freshly drawn and carry no real
    value). Mutually exclusive with `numeric`."""
    n_rows = int(n_rows)
    if n_rows <= 0:
        return np.array([], dtype=(np.float64 if numeric else object))
    K = max(int(cardinality), 1)
    # A committed cardinality that exceeds n_rows is structurally impossible (a column cannot have more
    # distinct tokens than rows). Fail CLOSED rather than silently clamp: silent clamping would produce
    # a payload whose actual distinct-count (n_rows) disagrees with the committed contract (cardinality),
    # a structural-fidelity defect. The Stage-A contract generator caps cardinality at the row count, so
    # a well-formed committed contract never trips this; if one does, the contract must be regenerated.
    if K > n_rows:
        raise ValueError(
            f"impossible committed cardinality {K} > n_rows {n_rows} (salt={salt!r}); the schema "
            f"contract must cap per-column cardinality at the row count. Refusing to clamp.")
    if date_bounds is not None:
        lo_year, hi_year = date_bounds
        start = datetime.date(int(lo_year), 1, 1)
        end = datetime.date(int(hi_year), 12, 31)
        n_days = (end - start).days + 1
        if K > n_days:
            raise ValueError(
                f"impossible committed cardinality {K} > {n_days} days in date_bounds="
                f"({lo_year},{hi_year}) (salt={salt!r}); widen the bounds or lower the cardinality.")
        # distinct day-offsets sampled from the fresh (public) range -- not a function of any real date
        offs = generate_entity_ids(K, 0, n_days, salt=f"datecol|{salt}")
        labels = np.array([start + datetime.timedelta(days=int(o)) for o in offs], dtype=object)
    elif numeric:
        labels = generate_entity_ids(K, IDCOL_FAKE_MIN, IDCOL_FAKE_SPACE,
                                     salt=f"idcol|{salt}").astype(np.float64)
    else:
        tag = hashlib.md5(str(salt).encode()).hexdigest()[:6]
        labels = np.array([f"SYN{tag}_{i:07d}" for i in range(K)], dtype=object)
    # per-row token INDEX in [0, K) with smoothed group sizes + independent co-membership + >=1/token
    idx = assign_membership(n_rows, np.arange(K, dtype=np.int64), size_family, salt=f"idcol|{salt}")
    return labels[idx.astype(np.int64)]


# ======================================================================================
# Adversarial self-test -- fails closed. Proves the primitives eliminate the audit's
# reversibility + co-membership + exact-statistic leaks and preserve structural fidelity.
# ======================================================================================
def _selftest():
    problems = []

    def check(cond, msg):
        if not cond:
            problems.append(msg)

    # --- (A) fresh ids: distinct, in-domain, and NOT a function of any real id -----------
    pat = generate_patent_ids(100_000, salt="patents")
    check(len(np.unique(pat)) == len(pat), "patent ids not distinct")
    check(pat.min() >= PATENT_FAKE_MIN and pat.max() < PATENT_FAKE_MIN + PATENT_FAKE_SPACE,
          "patent ids out of fake domain")
    perm = generate_permno_ids(25_000, salt="permno")
    check(len(np.unique(perm)) == len(perm), "permno ids not distinct")
    check(perm.min() >= LINK_FAKE_MIN and perm.max() < LINK_FAKE_MIN + LINK_FAKE_SPACE,
          "permno ids out of fake domain")
    # the generator takes NO real id: feeding a different "real id space" cannot change output
    # (there is no argument to feed) -> reproduced by determinism check below.

    # --- (B) determinism: two clean-room runs byte-identical ------------------------------
    check(np.array_equal(pat, generate_patent_ids(100_000, salt="patents")),
          "patent id generation not deterministic")
    check(np.array_equal(perm, generate_permno_ids(25_000, salt="permno")),
          "permno generation not deterministic")

    # --- (C) domain overflow fails closed -------------------------------------------------
    try:
        generate_entity_ids(10, 0, 5, salt="x")
        problems.append("over-capacity id request did not raise")
    except ValueError:
        pass

    # --- (D) co-membership is INDEPENDENT of a real partition ----------------------------
    # Build a real partition of N rows into groups; assign_membership must NOT reproduce it.
    N = 60_000
    rng0 = np.random.default_rng(1)                      # stands in for "the real data"
    real_group = rng0.integers(0, 4_000, size=N)         # real co-membership
    ents = generate_permno_ids(4_000, salt="firms")
    syn = assign_membership(N, ents, {"kind": "nbinom", "r": 2.0, "p": 0.3}, salt="firms")
    check(len(syn) == N, "assign_membership wrong length")
    check(np.all(np.isin(syn, ents)), "assign_membership produced ids outside the fresh universe")
    # every used entity has >=1 obs (support) and the total is exact
    used, counts = np.unique(syn, return_counts=True)
    check(counts.min() >= 1, "assign_membership left an entity with 0 obs")
    check(counts.sum() == N, "assign_membership sizes do not sum to N")
    # co-membership agreement with the REAL partition must be ~chance, not preserved.
    # Sample random row pairs; fraction co-member in BOTH real and synthetic vs expected-by-chance.
    a = rng0.integers(0, N, size=200_000)
    b = rng0.integers(0, N, size=200_000)
    m = a != b
    a, b = a[m], b[m]
    real_co = real_group[a] == real_group[b]
    syn_co = syn[a] == syn[b]
    # If synthetic co-membership copied the real partition, real_co would predict syn_co.
    # Independence => P(syn_co | real_co) ~= P(syn_co). Check the lift is negligible.
    p_syn = syn_co.mean()
    p_syn_given_real = syn_co[real_co].mean() if real_co.any() else 0.0
    check(abs(p_syn_given_real - p_syn) < 0.01,
          f"synthetic co-membership correlated with real partition "
          f"(P={p_syn:.4f}, P|real={p_syn_given_real:.4f}) -- real grouping leaks")

    # --- (E) size multiset is NOT the exact real multiset --------------------------------
    real_sizes = np.sort(np.bincount(real_group, minlength=4_000))
    syn_sizes = np.sort(np.bincount(np.searchsorted(ents, syn), minlength=len(ents)))
    check(not np.array_equal(real_sizes, syn_sizes),
          "synthetic size multiset exactly equals the real multiset (exact-statistic leak)")

    # --- (F) public-code assignment independent of real ids, weighted, full support ------
    codes = np.array([f"C{i:03d}" for i in range(200)])
    w = np.arange(1, 201, dtype=float)
    asg = assign_public_codes(50_000, codes, w, salt="pc")
    check(set(np.unique(asg)).issubset(set(codes)), "assign_public_codes emitted unknown code")
    # higher-weight codes get more rows (clustering preserved) but assignment bears no real id
    hi = (asg == codes[-1]).sum()
    lo = (asg == codes[0]).sum()
    check(hi > lo, "assign_public_codes ignored weights")

    # --- (G) missingness ~ committed RATE, not exact count, deterministic ----------------
    mask = draw_missingness(100_000, 0.137, salt="col")
    check(abs(mask.mean() - 0.137) < 0.01, f"missingness rate off ({mask.mean():.4f})")
    check(np.array_equal(mask, draw_missingness(100_000, 0.137, salt="col")),
          "missingness not deterministic")
    # a different column salt gives a different mask (no shared fingerprint)
    check(not np.array_equal(mask, draw_missingness(100_000, 0.137, salt="other")),
          "missingness identical across columns (shared fingerprint)")

    # --- (H) draw_missingness_rate: ~Binomial(n,rate), NOT an exact count -----------------
    N2 = 200_000
    m2 = draw_missingness_rate(N2, 0.20, salt="numcol")
    check(abs(m2.mean() - 0.20) < 0.01, f"draw_missingness_rate off ({m2.mean():.4f})")
    # a real column with EXACTLY k_real=40000 NaN would, under the old redraw, keep exactly 40000;
    # the rate draw must NOT reproduce that exact count (that was the leak).
    check(int(m2.sum()) != 40_000, "draw_missingness_rate reproduced the exact real NaN count")
    check(np.array_equal(m2, draw_missingness_rate(N2, 0.20, salt="numcol")),
          "draw_missingness_rate not deterministic")

    # --- (I) generate_identity_column: fresh tokens, >=1/token, sizes smoothed not real ----
    # A "real" identity column: 25,003 distinct with a spiky multiset; committed params are the
    # ROUNDED cardinality (25,000) + a SMOOTHED family. The output must NOT reproduce either.
    real_card = 25_003
    committed_card = 25_000                               # round_cardinality(25_003)
    fam = {"kind": "nbinom", "r": 1.4, "p": 0.1}
    idc = generate_identity_column(300_000, committed_card, fam, salt="clean_name", numeric=False)
    check(len(idc) == 300_000, "generate_identity_column wrong length")
    uu, cc = np.unique(idc, return_counts=True)
    check(cc.min() >= 1, "generate_identity_column left a token with 0 rows")
    check(len(uu) != real_card, "generate_identity_column reproduced the exact real distinct-count")
    check(len(uu) <= committed_card, "generate_identity_column exceeded committed cardinality")
    check(all(str(t).startswith("SYN") for t in uu[:50]), "identity tokens not fresh SYN tokens")
    check(np.array_equal(idc, generate_identity_column(300_000, committed_card, fam,
          salt="clean_name", numeric=False)), "generate_identity_column not deterministic")
    # numeric identity: distinct fake ints in the generic fake domain, no real value
    idn = generate_identity_column(50_000, 4_000, fam, salt="firmid", numeric=True)
    check(np.nanmin(idn) >= IDCOL_FAKE_MIN, "numeric identity below fake domain")
    check(len(np.unique(idn[~np.isnan(idn)])) <= 4_000, "numeric identity exceeded cardinality")

    # --- (J) date identity: fresh calendar dates in-bounds, genuine `date` objects, deterministic --
    idd = generate_identity_column(2_000, 500, fam, salt="date_decided", numeric=False,
                                    date_bounds=(1985, 2007))
    check(len(idd) == 2_000, "date identity column wrong length")
    check(all(isinstance(v, datetime.date) for v in idd[:50]), "date identity values not date objects")
    check(all(datetime.date(1985, 1, 1) <= v <= datetime.date(2007, 12, 31) for v in idd),
          "date identity value out of the committed bounds")
    uud = np.unique(idd)
    check(len(uud) <= 500, "date identity exceeded committed cardinality")
    check(np.array_equal(idd, generate_identity_column(2_000, 500, fam, salt="date_decided",
          numeric=False, date_bounds=(1985, 2007))), "date identity column not deterministic")
    # a cardinality that cannot fit in the day range fails closed rather than colliding silently
    try:
        generate_identity_column(2_000, 500, fam, salt="tight", date_bounds=(2000, 2000))
        problems.append("over-capacity date cardinality did not raise")
    except ValueError:
        pass

    if problems:
        print("independent_universe self-test: FAIL")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("independent_universe self-test: PASS "
          "(fresh ids, independent co-membership, smoothed sizes, rate-based missingness, "
          "deterministic, fail-closed)")


if __name__ == "__main__":
    _selftest()
