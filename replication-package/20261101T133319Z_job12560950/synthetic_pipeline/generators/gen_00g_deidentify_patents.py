"""
gen_00g_deidentify_patents.py -- assemble the independent-universe files into
the PUBLICLY REDISTRIBUTABLE simulation.

WHY
---
Upstream Stage-B generators create patent identifiers directly in a disjoint
synthetic domain. This assembler validates that invariant, preserves those
synthetic identifiers consistently across files, creates synthetic KPSS/KPST
interfaces, and publishes the staged files. It never accepts or remaps a real
patent identifier.

WHAT IT DOES
-----------
Builds one identity map over already-synthetic patent numbers and applies it
consistently across every patent-bearing file. Any number outside the committed
synthetic domain is a fatal upstream/privacy error.

The patent -> PRODUCTCODE assignment is RESIMULATED upstream (gen_00d/gen_00e via the
shared theta table): each patent is assigned a product code weight-proportional to a
synthetic per-code patenting level, with floored weights for reclass/control codes so the
estimators keep support. So the per-code patent counts this step sees are already synthetic
DRAWS, not real cells. This step only validates and preserves the already-synthetic
patent numbers consistently across files and simulates KPST over those fake numbers.

WHAT IT KEEPS (legitimately public / needed to run)
---------------------------------------------------
Real FDA product codes and years (public; ship in foiclass.txt; the contact-lens
case study references specific codes) and the real treatment flags (public
reclassification record). Control assignments are re-simulated downstream by
02_match_samples on the synthetic covariates.

Reads only Stage-B synthetic_* staging directories and writes simulated_data/.
Deterministic (seeded).
"""
import os
import re
import sys
import glob
import shutil

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import synthetic_paths
from synthetic_seed import seed

SRC = str(synthetic_paths.internal_dir())
OUT = str(synthetic_paths.simulated_data_dir())
SEED = seed(20260710)

import gen_00b_pc_effects as pcmod   # shared PC-level random-effects (breakthrough rate)

# id/patnum/patent_id all identify the SAME patent -> one shared number map (consistent).
# application_id is a DIFFERENT id space (its integers can coincide with patent numbers), so it
# is NOT here -- gen_00e synthesizes it independently, avoiding an application<->patent collision.
PAT_ID_COLS = {"id", "patnum", "patent_id"}          # columns that hold a patent (grant) id
# The numeric core of a patent number: the FULL contiguous digit run (\d+ matches
# the whole number, so replacing it can't touch other characters). Any digit length
# is caught -- plant patents (US-PP4036-P), statutory invention registrations down to
# a single digit (US-H5-H), design patents -- so no real identifier survives.
NUM_RE = re.compile(r"(\d+)")
# core = optional 1-2 series letters (PP plant, RE reissue, D design, ...) + the digits, taken
# from inside any 'US-...-KIND' wrapper. Keeping the letters distinguishes PP31040 from RE31040
# (different patents that share the number 31040) so they do NOT map to the same fake.
CORE_RE = re.compile(r"(?:US-?)?([A-Z]{0,2}\d+)", re.I)


def _num(x):
    """Extract the distinguishing core of a patent id ('US-4660238-A' -> '4660238',
    'PP31040' -> 'PP31040', 'US-PP31040-P' -> 'PP31040')."""
    if pd.isna(x):
        return None
    m = CORE_RE.search(str(x).strip())
    if m:
        return m.group(1).upper()
    m2 = NUM_RE.search(str(x))
    return m2.group(1) if m2 else None


def collect_patent_numbers(files):
    numbers = set()
    for f, cols in files:
        for chunk in pd.read_csv(f, usecols=cols, dtype=str, chunksize=500_000, low_memory=False):
            for c in cols:
                for v in chunk[c].dropna().map(_num).dropna().unique():
                    numbers.add(v)
    return numbers


FAKE_PAT_MIN = 90_000_000


def build_number_map(numbers):
    """Return an identity map only after every id passes the fake-domain gate."""
    ordered = sorted(numbers, key=lambda s: (len(s), s))
    invalid = []
    for r in ordered:
        try:
            already_fake = int(r) >= FAKE_PAT_MIN
        except (ValueError, TypeError):
            already_fake = False
        if not already_fake:
            invalid.append(r)
    if invalid:
        raise SystemExit(
            "gen_00g: patent identifiers outside the synthetic domain; refusing "
            f"to remap possible real identifiers (first values: {invalid[:10]})"
        )
    return {r: r for r in ordered}


def _remap_id_value(v, m):
    if pd.isna(v):
        return v
    n = _num(v)
    if n is None or n not in m:
        return v
    fake = m[n]
    s = str(v)
    return s.replace(n, fake) if (s.startswith("US") or "-" in s) else fake


def process_file(f, cols, m, pc_shuffle_rng):
    df = pd.read_csv(f, low_memory=False)
    for c in cols:
        df[c] = df[c].map(lambda v: _remap_id_value(v, m))
    # This step only de-identifies patent NUMBERS (above). The patent -> PRODUCTCODE
    # assignment was already RESIMULATED from theta in gen_00d/gen_00e (weight-proportional
    # with floored weights for reclass/control codes), so the per-code counts are synthetic
    # draws with the clustering the estimators need -- no shuffle here.
    dest = os.path.join(OUT, os.path.relpath(f, SRC))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    df.to_csv(dest, index=False)
    return len(df)


def generate_synthetic_kpst(rng):
    """Generate a SIMULATED KPST_Breakthrough.csv keyed on the fake device-patent
    numbers, with a non-degenerate breakthrough indicator.

    The real KPST (Kelly-Papanikolaou-Seru-Taddy, public) is keyed on real patent
    numbers, so it no longer matches the simulated (faked) patent ids -- the merge
    in 14_breakthrough_patents.py would yield an all-zero outcome and the estimator
    would fail on perfect separation. We instead simulate KPST over the fake device
    patents so the merge holds and the outcome has variation. 14 uses only
    `patent_num` and `bk_p90_alqsim05`; other columns are filled with the right
    schema so the file loads. Values are synthetic; results differ by construction.
    """
    ap = os.path.join(OUT, "synthetic_dimensions_wrds", "all_patents_w_xi_oct22_24.csv")
    apdf = pd.read_csv(ap, usecols=["patnum", "PRODUCTCODE"], low_memory=False).dropna(subset=["patnum"])
    apdf = apdf.drop_duplicates(subset="patnum")
    nums = apdf["patnum"].astype(int).to_numpy()
    n = len(nums)
    # breakthrough RATE varies by (resimulated) product code via theta.p_breakthrough, so
    # step 14's per-PC-year counts cluster (support + DiD variation), not a flat 15%.
    p_bk = pcmod.theta_lookup(apdf["PRODUCTCODE"].astype(str).to_numpy(), "p_breakthrough")
    kpst = pd.DataFrame({
        "patent_num": nums,
        "bsim5": rng.uniform(0, 1, n).round(4),
        "fsim01": rng.integers(0, 20000, n),
        "fsim25": rng.integers(0, 20000, n),
        "fsim610": rng.integers(0, 20000, n),
        "lqsim05": rng.uniform(0, 1, n).round(4),
        "lqsim010": rng.uniform(0, 1, n).round(4),
        "filed_year": rng.integers(1976, 2021, n),
        "issue_year": rng.integers(1976, 2021, n),
        # breakthrough ~ Bernoulli(p_breakthrough[code]) -> per-PC-year counts vary + cluster
        "bk_p90_alqsim05": (rng.uniform(0, 1, n) < p_bk).astype(int),
        "bk_p90_alqsim010": (rng.uniform(0, 1, n) < 0.7 * p_bk).astype(int),
        "fcitALL": rng.integers(0, 200, n),
    })
    dest = os.path.join(OUT, "synthetic_kpst", "KPST_Breakthrough.csv")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    kpst.to_csv(dest, index=False)
    print(f"  generated synthetic KPST_Breakthrough.csv ({n:,} fake device patents, "
          f"{int(kpst.bk_p90_alqsim05.sum()):,} breakthroughs)")


def generate_synthetic_kpss(rng):
    """Generate a SIMULATED KPSS_2019_public.csv keyed on the FAKE patent numbers, so the
    simulated-data route's gen_01 patent-value merge succeeds. The real KPSS (Kogan-Papanikolaou-Seru-
    Stoffman) is keyed on REAL patent numbers, so the faked synthetic patents find no match — then
    `xi_real` is all-null → the DiD `xi` spec is a constant (feglm aborts) and, because `permno`
    also rides in through this file, `firm_size` never attaches (safety / firm-heterogeneity empty
    out). We instead project the already-de-identified `all_patents_w_xi` — which gen_00d built with
    a fake `patnum`, a fake `permno` CONSISTENT with the synthetic Compustat's fake LPERMNO (same
    `_link_remap` map), and synthetic `xi_real`/`xi_nominal`/`cites` — into KPSS's schema, adding
    synthetic D/M/YYYY dates (gen_01 parses `year = filing_date.split('/')[2]`). So the from-raw
    gen_01 reconstructs the same patent→firm→value linkage the derived inputs already carry. Values are
    synthetic; results differ by construction. (The public real KPSS still ships; this override is
    applied only for the simulated-data route — see materialize_simulation.py --for-gen-run.)"""
    ap = os.path.join(OUT, "synthetic_dimensions_wrds", "all_patents_w_xi_oct22_24.csv")
    if not os.path.exists(ap):
        # FAIL CLOSED: skipping here would ship a payload without the synthetic KPSS interface
        # and leave gen_01's patent-value merge empty.
        raise SystemExit(
            f"gen_00g: cannot build the synthetic KPSS interface -- {ap} is missing. "
            "gen_00d must run (and publish all_patents_w_xi_oct22_24.csv) before gen_00g."
        )
    keep = {"patnum", "permno", "xi_real", "xi_nominal", "cites"}
    df = pd.read_csv(ap, usecols=lambda c: c in keep, low_memory=False)
    df = df.dropna(subset=["patnum"]).drop_duplicates(subset="patnum")
    n = len(df)
    yrs = rng.integers(1976, 2019, n)
    dmy = [f"{int(d)}/{int(mo)}/{int(y)}" for d, mo, y in
           zip(rng.integers(1, 28, n), rng.integers(1, 13, n), yrs)]
    xr = pd.to_numeric(df["xi_real"], errors="coerce").to_numpy() if "xi_real" in df \
        else np.round(rng.lognormal(2.0, 0.6, n), 4)
    xn = pd.to_numeric(df["xi_nominal"], errors="coerce").to_numpy() if "xi_nominal" in df \
        else np.round(xr * rng.uniform(0.7, 1.0, n), 4)
    xn = np.where(np.isnan(xn) | (xn == 0), 1.0, xn)          # gen_01: CPI = xi_real / xi_nominal
    permno = pd.to_numeric(df["permno"], errors="coerce").to_numpy() if "permno" in df \
        else rng.integers(1_000_000, 2_000_000, n).astype(float)
    permno = np.where(np.isnan(permno), rng.integers(1_000_000, 2_000_000, n), permno).astype("int64")
    kpss = pd.DataFrame({
        "patent_num": df["patnum"].astype("int64").to_numpy(),
        "xi_real": xr,
        "xi_nominal": xn,
        "cites": pd.to_numeric(df.get("cites"), errors="coerce").fillna(0).astype(int).to_numpy()
                 if "cites" in df else rng.poisson(5, n),
        "permno": permno,
        "issue_date": dmy,
        "filing_date": dmy,
    })
    dest = os.path.join(OUT, "synthetic_kpss", "KPSS_2019_public.csv")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    kpss.to_csv(dest, index=False)
    print(f"  generated synthetic KPSS_2019_public.csv ({n:,} fake patents; permno linked to synthetic "
          f"Compustat; xi non-constant)")


def main():
    # discover patent-bearing files + their patent columns
    pat_files = []
    all_csvs = glob.glob(os.path.join(SRC, "synthetic_*", "**", "*.csv"), recursive=True)
    for f in all_csvs:
        cols = pd.read_csv(f, nrows=0).columns.tolist()
        hits = [c for c in cols if c in PAT_ID_COLS]
        if hits:
            samp = pd.read_csv(f, usecols=hits, nrows=200, dtype=str, low_memory=False)
            if any(samp[c].map(_num).notna().any() for c in hits):
                pat_files.append((f, hits))

    print(f"Patent-bearing files: {len(pat_files)}")
    numbers = collect_patent_numbers(pat_files)
    print(f"Unique synthetic patent numbers validated: {len(numbers):,}")
    m = build_number_map(numbers)

    rng = np.random.default_rng(SEED)
    pat_paths = {f for f, _ in pat_files}

    # 1) copy every NON-patent synthetic file verbatim (already fully synthetic)
    n_copy = 0
    for f in glob.glob(os.path.join(SRC, "synthetic_*", "**", "*"), recursive=True):
        if os.path.isdir(f) or f in pat_paths:
            continue
        dest = os.path.join(OUT, os.path.relpath(f, SRC))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(f, dest)
        n_copy += 1

    # 2) validate/preserve every already-synthetic patent number consistently.
    for f, cols in pat_files:
        n = process_file(f, cols, m, rng)
        print(f"  de-identified {os.path.relpath(f, SRC):60s} ({n:>9,} rows; cols {cols})")

    # 3) simulate KPST_Breakthrough.csv over the fake device patents (the real KPST
    #    is keyed on real patent numbers and no longer matches the faked ids)
    generate_synthetic_kpst(rng)
    # 3b) simulate KPSS_2019_public.csv (patent value xi + permno) over the fake patent numbers, so the
    #     simulated-data route's gen_01 KPSS merge succeeds (xi non-constant + firm_size can attach).
    generate_synthetic_kpss(rng)

    print(f"Copied {n_copy} non-patent files verbatim.")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
