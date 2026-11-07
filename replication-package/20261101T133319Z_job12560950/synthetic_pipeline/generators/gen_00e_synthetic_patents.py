"""
gen_00e_synthetic_patents.py -- Phase 3 synthetic Dimensions patent files.

INDEPENDENT-UNIVERSE REDESIGN (2026-08-08)
-----------------------------------------------------------
Reads NO real restricted data. Every patent file is built from:
  * the committed interlock spec `params["files"][name]` (Stage-A gen_00a): ROUNDED row count +
    per-column role with only ROUNDED cardinalities / SMOOTHED size families / ROUNDED missingness
    rates -- never an exact real distinct-count, size multiset, or NaN count;
  * the canonical fresh patent universe (universe_backend): patnum / owning permno / PUBLIC product
    code / filing year sampled per row (no real patent id or source-row year retained);
  * synthetic re-identifying attributes (cpc / jurisdiction / type / status / dates / text), NEWLY
    DRAWN (the real (year,type,cpc,jurisdiction) tuple is a 96% fingerprint, so it must be synthetic).

Firm / assignee / inventor identity columns become FRESH tokens with a ROUNDED cardinality +
SMOOTHED size family + INDEPENDENT co-membership (independent_universe.generate_identity_column);
continuous value columns are drawn with missingness at the committed ROUNDED rate
(independent_universe.draw_missingness_rate). No resample_identity / redraw_missingness anywhere.

AUTHOR-SIDE generation; publishable outputs emitted through simulated_data/ after gen_00g.
Deterministic (public seed via independent_universe).
"""
import os
import re
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
# DERIVED/RAW retained ONLY so gen_00a (Stage A) can resolve this generator's real-file paths when
# it extracts the committed specs. gen_00e itself NEVER reads from them.
DERIVED = os.path.join(ROOT, "data", "derived")
RAW = os.path.join(ROOT, "data", "raw")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import synthetic_paths
from synthetic_seed import seed

OUT = os.path.join(str(synthetic_paths.internal_dir()), "synthetic_patents")
SEED = seed(12345)

import gen_00b_pc_effects as pcmod   # shared PC-level random-effects (theta stratification)
import universe_backend as ub        # canonical patent universe + committed specs
import independent_universe as iu     # fresh id / missingness primitives (no real->fake map)

# Columns kept structural (ids de-identified downstream by gen_00g) / public calendar.
KEEP = re.compile(r"^(id|patnum|patent_id|year|filename|Unnamed.*|index)$", re.I)
# F1 re-identifying attributes SYNTHESIZED (never pass-through):
CPC_RE = re.compile(r"^cpc", re.I)
JUR_RE = re.compile(r"^jurisdiction$", re.I)
PTYPE_RE = re.compile(r"^(type|patent_type|patent_application_type|wipo_kind)$", re.I)
STATUS_RE = re.compile(r"^(filing_status|series_code|rule_47_flag|withdrawn)$", re.I)
DATE_RE = re.compile(r"(filing_date|patent_date|_date)$", re.I)
TEXT = re.compile(r"(title|abstract|^input$|prompt_and_input|_text$|^text$)", re.I)
FIRM = re.compile(r"(assignee|inventor|grid|orig_|firmname|conm|permno|gvkey)", re.I)

# --- synthetic CPC vocabulary (A61-family SHAPED so the device/drug A61-vs-A61P filter works) ---
_CPC_A61_DEVICE = ["A61B", "A61F", "A61M", "A61N", "A61C", "A61G", "A61H", "A61J", "A61L"]
_CPC_A61_DRUG = ["A61P", "A61K"]
_CPC_OTHER = ["G01N", "G06F", "H04L", "C12N", "B01L", "G16H", "F16K", "H01L"]
_JURISDICTIONS = ["US", "EP", "WO", "JP", "CN", "DE", "KR"]
_PTYPES = ["Company", "Individual"]
_STATUSES = ["Grant", "Application"]


def _synth_cpc(n, rng):
    """n synthetic CPC code LISTS (stringified). ~40% A61-family device patents; ~30% of those also
    carry an A61P drug code, so the device/drug distinction survives without any real per-patent set."""
    out = np.empty(n, dtype=object)
    r = rng.random(n)
    for i in range(n):
        k = int(rng.integers(1, 5))
        if r[i] < 0.40:
            subs = rng.choice(_CPC_A61_DEVICE, size=k)
            codes = [f"{s}{rng.integers(1, 99)}/{rng.integers(1000, 99999)}" for s in subs]
            if rng.random() < 0.30:
                codes.append(f"A61P{rng.integers(1, 45)}/{int(rng.integers(1, 20)):02d}")
        else:
            subs = rng.choice(_CPC_OTHER, size=k)
            codes = [f"{s}{rng.integers(1, 99)}/{rng.integers(1000, 99999)}" for s in subs]
        out[i] = str(codes)
    return out


def _synth_date_near_year(years, rng):
    """Synthetic YYYY-MM-DD near each row's public filing `year`."""
    yrs = np.asarray(years)
    n = len(yrs)
    mm = rng.integers(1, 13, size=n); dd = rng.integers(1, 29, size=n)
    return np.array([f"{int(y):04d}-{int(m):02d}-{int(d):02d}" for y, m, d in zip(yrs, mm, dd)],
                    dtype=object)


def _synth_grid_json(n, cardinality, salt):
    """`original_assignees` is a JSON list `[{'id':'grid.X',...}]` gen_01 literal_eval-parses to pull
    the GRID firm id. Emit a valid one-element JSON list per row over FRESH grid ids drawn with a
    committed cardinality + independent co-membership -- no real grid/firm/name survives, and the
    column stays object so gen_01's merge against GRID/types.csv still parses."""
    toks = iu.generate_identity_column(n, int(cardinality) or 100,
                                       {"kind": "nbinom", "r": 1.5, "p": 0.1}, salt, numeric=False)
    uniq = list(pd.unique(pd.Series(toks)))
    letters = "abcdefghijklmnopqrstuvwxyz"
    gmap = {t: f"grid.{7000000 + i}.{letters[i % 26]}" for i, t in enumerate(uniq)}
    out = np.empty(n, dtype=object)
    for i in range(n):
        g = gmap[toks[i]]
        out[i] = ("[{'id': '%s', 'acronym': 'SYNACR', 'name': 'SYN Firm', "
                  "'city_name': 'SYN City', 'country_name': 'United States'}]" % g)
    return out


# outcome columns drawn CONDITIONAL on the resimulated product code (estimator support).
OUT_CITE = re.compile(r"^(times_cited|cites)$", re.I)
OUT_SAFETY = re.compile(r"^(safety|safety_tag)$", re.I)
OUT_SAFETY_AUX = re.compile(r"^(cost|quality)$", re.I)
OUT_SAFETY_SIM = re.compile(r"^safety_similarity$", re.I)

_MED = ("device method system apparatus surgical implant catheter sensor stent valve "
        "electrode probe imaging diagnostic therapeutic monitor pump membrane polymer "
        "coating tissue fluid pressure signal assembly housing conduit lumen guidewire "
        "balloon ablation suture prosthesis actuator controller module biocompatible "
        "delivery deployment expandable flexible needle syringe reservoir").split()
VOCAB = _MED + [f"term{i:04d}" for i in range(4000)]

FILES = [  # (subdir, name)
    ("d", "safety_vars_allpats.csv"), ("d", "safety_vars_allpats_v2.csv"),
    ("d", "safety_vars_allpats_updated_v2.csv"), ("d", "safety_tagged_patents.csv"),
    ("r", "all_PC_pats.csv"), ("r", "expanded_2_1_pats.csv"), ("r", "expanded_3_2_pats.csv"),
    ("r", "missed_2_1_pats.csv"), ("r", "all_pats_wtitlesCPC.csv"),
    ("r", "FDA_pats_original_firmname.csv"),
    ("r", "Applicant_Cites_Only.csv"),
    ("r", "PC_by_year_cites_ApplicantOnly.csv"),
    ("r", "PC_by_year_diff_ind_appl_only.csv"),
    ("r", os.path.join("new_patent_analysis", "all_device_patents_w_pc.csv")),
]

# --------------------------------------------------------------------------------------
# Applicant_Cites_Only.csv -- UNIVERSE-DERIVED, no committed per-file spec.
# --------------------------------------------------------------------------------------
# This is the forward-citation lookup `code/09_summary_stats.py` merges onto the patent panel
# to compute the "Citations per Patent" rows of Table 1 and Table D.14. It is generated WITHOUT
# any committed interlock spec -- i.e. without any new restricted-derived parameter -- because
# everything it needs is already determined by artifacts that ship:
#
#   * its ROW SET is the synthetic patent universe itself: exactly one row per patent in
#     universe_backend.patent_universe(), whose size is the committed ROUNDED entity cardinality
#     params["entities"]["patents"]["cardinality"]. So n_rows is a documented FUNCTION of the
#     simulated universe, not a disclosed real extract size (see DGP_DESIGN.md Section 3.1).
#   * its KEY is that universe's `patnum`, i.e. the digit core of the `US-<patnum>-B2` ids the
#     other patent files carry, so the merge in 09_summary_stats resolves for every patent.
#   * its PRODUCTCODE is the universe's already-resimulated public FDA product code.
#   * its OUTCOME is drawn from the shipped seeded PC random-effects table (pc_effects.parquet,
#     column `mu_cite`) with the package's iu_rng seeding discipline -- the same machinery
#     `process_pc_year` uses for the PC-year citation panels.
#
# Column NAMES and column KINDS are structural metadata of the real file (JPE confidential.html
# treats type/format fidelity as required and as non-disclosive); the VALUES are fully simulated.
APPLICANT_CITES = "Applicant_Cites_Only.csv"
# Ordered schema of the real file: USID integer key, public FDA product code, integer citation count.
APPLICANT_CITES_ORDER = ["USID", "PRODUCTCODE", "times_cited"]


def process_applicant_cites(name, theta):
    """Generate `Applicant_Cites_Only.csv` from the synthetic patent universe (see the block
    comment above). Deterministic in the public seed; reads no real data and no per-file spec."""
    patents = ub.patent_universe()
    patnums = patents["patnum"].to_numpy(dtype=np.int64)
    pc = patents["PRODUCTCODE"].astype(str).to_numpy()
    n = len(patnums)
    mu = pcmod.theta_lookup(pc, "mu_cite", theta)
    rng = iu.iu_rng("applicant_cites", name, n)
    df = pd.DataFrame({
        "USID": patnums,
        "PRODUCTCODE": pc,
        "times_cited": rng.poisson(np.clip(mu, 0, None)).astype("int64"),
    }, columns=APPLICANT_CITES_ORDER)
    if not df["USID"].is_unique:
        raise SystemExit(f"gen_00e: {name} key USID is not unique -- the patent universe is "
                         "expected to carry one row per patent.")
    # Defense in depth: USID is a patent number, so it must lie in the synthetic patent domain.
    # (gen_00g's fake-domain gate covers id/patnum/patent_id columns, not this one.)
    if int(df["USID"].min()) < iu.PATENT_FAKE_MIN:
        raise SystemExit(f"gen_00e: {name} carries a USID below the synthetic patent domain "
                         f"({iu.PATENT_FAKE_MIN}) -- refusing to write a possibly real patent id.")
    outp = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    df.to_csv(outp, index=False)
    print(f"  wrote {name:<46} ({len(df):>10,} rows; 1 row per universe patent) "
          f"[USID=patnum; times_cited~Poisson(theta.mu_cite)]")


def _text_pool(rng, k=8000):
    return np.array([" ".join(rng.choice(VOCAB, size=rng.integers(20, 90))) for _ in range(k)],
                    dtype=object)


def _num_column(n, missing_rate, salt):
    rng = iu.iu_rng("num", salt, n)
    out = np.round(rng.uniform(0, 1000, size=int(n)), 3)
    if missing_rate and float(missing_rate) > 0:
        out[iu.draw_missingness_rate(int(n), float(missing_rate), salt)] = np.nan
    return out


# PC-year citation panels: (year, PRODUCTCODE) public; only the citation COUNT restricted.
PC_YEAR_FILES = {"PC_by_year_cites_ApplicantOnly.csv", "PC_by_year_diff_ind_appl_only.csv"}

# Event-specific SUPPLEMENTS scoped to their public reclassification event (see universe_backend).
SUPPLEMENT_EVENT = {
    "missed_2_1_pats.csv": "2_1",
    "expanded_2_1_pats.csv": "2_1",
    "expanded_3_2_pats.csv": "3_2",
}


# Public calendar span of the PC-year citation panels (FDA product codes x patent-era years). Used to
# build a UNIQUE (PRODUCTCODE, year) grid -- see process_pc_year.
PCYEAR_YMIN = 1976
PCYEAR_YMAX = 2019                                       # exclusive -> years 1976..2018


def process_pc_year(name, theta, spec):
    """PC-year citation panel. STRUCTURAL FIDELITY: this file must have UNIQUE (PRODUCTCODE, year) --
    gen_01_main_panels.phase_05 LEFT-merges it into the master panel on (PRODUCTCODE, year) with no
    dedup, so a duplicate key here fans out Full_sample and breaks every downstream (PC,year) unstack
    (11b Fig D.14) and stacked-DiD pivot (conley_taber). The real file is a one-row-per-code-year
    citation panel, so unique (PC,year) is PUBLIC panel structure (FDA product-code list x calendar),
    NOT a restricted statistic -- reproducing it discloses nothing. We therefore build a UNIQUE
    (code x year) grid over a theta-weighted subset of the PUBLIC product codes, sized to the committed
    ROUNDED row count, instead of sampling (code, year) with replacement (which produced duplicate
    keys). Citation counts are drawn from theta; no real read; deterministic (public seed)."""
    order = spec["order"]; cols = spec["columns"]; n = int(spec["n_rows"])
    codes = theta["PRODUCTCODE"].astype(str).to_numpy()
    weights = np.clip(theta["pat_weight"].to_numpy(dtype=float), 0.0, None) + 1e-9  # floor -> all eligible
    years = np.arange(PCYEAR_YMIN, PCYEAR_YMAX)
    n_years = len(years)
    # choose DISTINCT codes (theta-weighted, WITHOUT replacement) so the full (code x year) grid is
    # ~n rows; cross with the public year span -> a UNIQUE (PRODUCTCODE, year) grid.
    n_codes = int(min(len(codes), max(1, round(n / n_years))))
    crng_codes = iu.iu_rng("pcyear_codes", name, n, len(codes))
    picked = crng_codes.choice(len(codes), size=n_codes, replace=False, p=weights / weights.sum())
    picked_codes = codes[picked]
    pc = np.repeat(picked_codes, n_years)
    year = np.tile(years, n_codes).astype(float)
    if len(pc) > n:                                      # trim to the committed rounded row count
        pc = pc[:n]; year = year[:n]                     # (still UNIQUE (PRODUCTCODE, year))
    m = len(pc)                                          # actual row count (~ committed rounded n)
    mu = pcmod.theta_lookup(pc, "mu_cite", theta)
    crng = iu.iu_rng("pcyear_cite", name, m)
    out = {}
    for col in order:
        c = str(col)
        if c == "PRODUCTCODE":
            out[c] = pc
        elif c == "year":
            out[c] = year
        elif c in ("times_cited", "times_cited_outside_ind"):
            out[c] = crng.poisson(np.clip(mu, 0, None)).astype(float)
        else:
            cspec = cols.get(c, {"role": "num", "missing_rate": 0.0})
            if cspec.get("role") == "id":
                out[c] = iu.generate_identity_column(m, int(cspec.get("cardinality", 1)),
                                                     cspec.get("size_family", {"kind": "uniform"}),
                                                     "pcyear|" + name + "|" + c,
                                                     numeric=bool(cspec.get("numeric", False)))
            else:
                out[c] = _num_column(m, cspec.get("missing_rate", 0.0), "pcyear|" + name + "|" + c)
    df = pd.DataFrame(out, columns=[str(c) for c in order])
    outp = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    df.to_csv(outp, index=False)
    dups = int(df.duplicated(subset=[c for c in ("PRODUCTCODE", "year") if c in df.columns]).sum())
    print(f"  wrote {name:<46} ({len(df):>10,} rows; {dups} dup (PC,year)) [PC-year: unique public grid]")


def _require_spec(name, specs):
    """Return the committed interlock spec for `name`, or FAIL CLOSED.

    A file listed in FILES but absent from the committed params would be silently omitted from
    the payload, and the consumer would then degrade on the missing input while the run still
    reported success. A listed file with no spec is a hard error: either the spec must be
    committed, or the file must be generated
    by a dedicated universe-derived generator (see process_applicant_cites) and registered in
    SPEC_FREE_FILES below."""
    spec = specs.get(name)
    if spec is None:
        raise SystemExit(
            f"gen_00e: no committed interlock spec for {name!r}. Every file listed in FILES must "
            f"either have a spec in simulation_parameters.json['files'] (run gen_00a Stage A in the "
            f"authorized environment to extract it) or be listed in SPEC_FREE_FILES with a dedicated "
            f"generator. Refusing to ship a payload that silently omits a simulated input."
        )
    return spec


# Files generated WITHOUT a committed per-file spec, each by its own dedicated generator.
# Keep this set tiny and explicit: it is the only escape hatch from _require_spec.
SPEC_FREE_FILES = {APPLICANT_CITES}


def process(name, theta, specs):
    base = os.path.basename(name)
    if base in SPEC_FREE_FILES or name in SPEC_FREE_FILES:
        if base == APPLICANT_CITES:
            process_applicant_cites(name, theta); return
        raise SystemExit(f"gen_00e: {name!r} is marked spec-free but has no dedicated generator.")
    if base in PC_YEAR_FILES or name in PC_YEAR_FILES:
        process_pc_year(name, theta, _require_spec(name, specs)); return
    spec = _require_spec(name, specs)
    order = spec["order"]; cols = spec["columns"]; n = int(spec["n_rows"])
    rng = iu.iu_rng("gen00e", os.path.basename(name), n)
    pool = _text_pool(rng)

    # independent-universe: a patent file's rows are SAMPLED from the canonical patent universe.
    idcol = next((c for c in ("id", "patent_id", "patnum") if c in order), None)
    patnums = None; patent_attrs = None; pc_row = None; years = None
    if idcol is not None:
        uni_n = len(ub.patent_universe())
        if n > uni_n:
            n = uni_n
        base_name = os.path.basename(name)
        event = SUPPLEMENT_EVENT.get(base_name)
        if event:
            allowed = theta.loc[theta[f"is_reclass_{event}"].astype(bool), "PRODUCTCODE"]
            patnums = ub.assign_patent_rows_for_codes(
                n, allowed, salt="gen00e|" + base_name, require_pre_event=True)
        else:
            patnums = ub.assign_patent_rows(n, salt="gen00e|" + base_name)
        patent_attrs = ub.attrs_for_patents(patnums)
        pc_row = patent_attrs["PRODUCTCODE"].to_numpy()
        years = patent_attrs["filing_year"].to_numpy(dtype=int)

    out = {}
    for col in order:
        c = str(col)
        cspec = cols.get(c, {"role": "num", "missing_rate": 0.0})
        if c in ("id", "patnum", "patent_id") and patnums is not None:
            dt = str(cspec.get("dtype", "int64"))
            if c == "id":
                out[c] = ("US-" + pd.Series(patnums).astype("int64").astype(str) + "-B2").to_numpy()
            elif dt == "object":
                out[c] = pd.Series(patnums).astype("int64").astype(str).to_numpy()
            else:
                out[c] = patnums
        elif c == "PRODUCTCODE" and pc_row is not None:
            out[c] = pc_row
        elif c == "year" and years is not None:
            out[c] = years
        elif OUT_CITE.match(c) and pc_row is not None:
            out[c] = rng.poisson(pcmod.theta_lookup(pc_row, "mu_cite", theta)).astype(float)
        elif OUT_SAFETY.match(c) and pc_row is not None:
            out[c] = (rng.random(n) < pcmod.theta_lookup(pc_row, "p_safety", theta)).astype(int)
        elif OUT_SAFETY_AUX.match(c) and pc_row is not None:
            out[c] = (rng.random(n) < 0.6 * pcmod.theta_lookup(pc_row, "p_safety", theta)).astype(int)
        elif OUT_SAFETY_SIM.match(c) and pc_row is not None:
            base = pcmod.theta_lookup(pc_row, "p_safety", theta)
            out[c] = np.clip(base + rng.normal(0, 0.10, n), 0, 1).round(4)
        elif CPC_RE.match(c):
            out[c] = _synth_cpc(n, rng)
        elif JUR_RE.match(c):
            out[c] = rng.choice(_JURISDICTIONS, size=n, p=[0.60, 0.15, 0.10, 0.06, 0.05, 0.02, 0.02])
        elif PTYPE_RE.match(c):
            out[c] = rng.choice(_PTYPES, size=n, p=[0.85, 0.15])
        elif STATUS_RE.match(c):
            status = rng.choice(_STATUSES, size=n, p=[0.90, 0.10])
            if c.lower() == "filing_status" and patent_attrs is not None:
                support = patent_attrs["required_support"].to_numpy(dtype=bool)
                status[support] = "Grant"
            out[c] = status
        elif DATE_RE.search(c):
            yv = years if years is not None else rng.integers(1990, 2015, size=n)
            out[c] = _synth_date_near_year(yv, rng)
        elif c == "original_assignees":
            out[c] = _synth_grid_json(n, cspec.get("cardinality", 100), "patents|original_assignees")
        elif TEXT.search(c):
            out[c] = pool[rng.integers(0, len(pool), size=n)]
        elif FIRM.search(c) or cspec.get("role") == "id":
            out[c] = iu.generate_identity_column(n, int(cspec.get("cardinality", 1)),
                                                 cspec.get("size_family", {"kind": "uniform"}),
                                                 "patents|" + c,
                                                 numeric=bool(cspec.get("numeric", False)))
        elif KEEP.match(c) and patnums is None:
            # structural column on a NON-patent file with no universe source -> generic draw
            out[c] = _num_column(n, cspec.get("missing_rate", 0.0), "patents|" + c)
        else:
            out[c] = _num_column(n, cspec.get("missing_rate", 0.0), "patents|" + c)
    df = pd.DataFrame(out, columns=[str(c) for c in order])
    outp = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    df.to_csv(outp, index=False)
    tag = " [code+outcomes~theta]" if pc_row is not None else ""
    print(f"  wrote {name:<46} ({len(df):>10,} rows){tag}")


def main():
    os.makedirs(OUT, exist_ok=True)
    theta = pcmod.load_theta()
    ub.build_universes()                     # canonical patent universe (cached) before any file
    specs = ub.file_specs()
    if not specs:
        raise SystemExit("gen_00e: committed params have no 'files' specs -- run gen_00a (Stage A) "
                         "to extract the interlock specs before generating.")
    for _kind, name in FILES:
        process(name, theta, specs)
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
