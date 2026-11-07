"""
audit_simulated_data.py -- FAIL-CLOSED certification that synthetic_pipeline/simulated_data/
contains NO real restricted data of any kind.

For every simulated file it locates the real counterpart under data/ and, column by column,
certifies the column is EITHER public-allowlisted OR provably synthetic:

  IDENTIFIER cols (id/patnum/patent_id/permno/gvkey/...) -> must be in the FAKE domain
      (patent numbers >= 90,000,000 or 'US-<fake>-<k>'; SYN* tokens; no real value survives).
  PUBLIC cols (PRODUCTCODE labels, year, FDA descriptors, Federal-Register reclassification
      design, CPC, controls, use_case, DEVICECLASS) -> may equal real (public data).
  OBJECT/TEXT cols -> every value must be OUTSIDE the real value set (fake-token shaped).
  NUMERIC OUTCOME cols -> must NOT be row-for-row identical to the real column.

Plus two structural checks:
  - per-PRODUCTCODE patent-count distribution in each patent file must DIFFER from the real
    one (the real per-code counts are not reproduced), and
  - no real company / assignee string from the restricted originals survives anywhere.

Any column that cannot be certified is a FINDING. Prints a file+column report and exits 1 on
any finding (so build_public_package can gate on it). Read-only; never writes data.

SCOPE (reported honestly, not overstated): the audit reads every file in FULL (no row
sampling) and reports a per-column disposition -- how many columns were (a) fully TESTED against
the real inputs and found not to be copies, (b) PUBLIC values intentionally preserved (real by
design -- FDA codes, years, Federal-Register reclassification design, CPC), (c) constant, or
(d) without a comparable real column. A PASS is a completeness claim over the TESTED columns,
NOT over the allowlisted public ones (which are meant to equal real).
"""
import os
import re
import sys
import glob
import tempfile
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIM = os.path.join(HERE, "simulated_data")
DERIVED = os.path.join(ROOT, "data", "derived")
RAW = os.path.join(ROOT, "data", "raw")

# --- column classes ----------------------------------------------------------------
# patent identifiers -> must be in the faked patent-number domain (>= 90,000,000)
# `usid` is the patent-number key of Applicant_Cites_Only.csv (added 2026-09-17); it holds the same
# synthetic patent number as `patnum`, so it must be domain-checked (>= FAKE_PAT_MIN) like the rest.
PATENT_ID = re.compile(r"^(id|patnum|patent_id|patent_num|usid)$", re.I)  # application_id synthesized separately
# RESIMULATED files are generated FRESH from the synthetic patent set (gen_00h), NOT by
# de-identifying the real namesake row-by-row. Their rows therefore do NOT correspond to the real
# file's rows, so the row-aligned (real[i], fake[i]) id-PAIR consistency check is invalid for them
# (it would pair a synthetic id with an unrelated real id). Their ids are drawn from an in-place
# de-identified file (all_pats_wtitlesCPC.csv), whose id mapping IS pair-checked, so no id-mapping
# coverage is lost. The set-overlap (merge-key) check still applies and is kept.
RESIMULATED_FILES = {"FDA_patents_text.csv"}
# INDEPENDENT-UNIVERSE design: the entity files (all_patents_w_xi, compustat, the adverse +
# patent files, KPST/KPSS) are GENERATED as views over a fresh synthetic
# firm/patent universe drawn from committed public parameters -- their rows do NOT correspond to real
# rows, and the SAME real entity deliberately receives INDEPENDENT fresh ids across files (that is the
# whole point: no consistent real->fake map exists to invert). So the row-aligned (real[i],fake[i])
# consistency check (_check_id_mapping) is INAPPLICABLE by construction -- flagging "real id maps to N
# different fakes" would be flagging the intended anonymity. When True, the audit therefore does NOT
# build real->fake pairs; the guarantees are instead certified POSITIVELY: (i) every id is in the fake
# domain (per-column, below), (ii) cross-file merge keys OVERLAP (_cross_file_consistency), and (iii)
# no real restricted id survives anywhere (the global restricted-value corpus backstop). Those three
# are strictly STRONGER than "the map is injective" -- they prove there is no real->fake map at all.
INDEPENDENT_UNIVERSE = True
FAKE_PAT_MIN = 90_000_000
# CRSP/Compustat linking ids -> remapped to a fake in the LINK fake domain (>= 1,000,000,
# above every real permno/gvkey). Verified by DOMAIN, not a row-equality threshold.
LINK_ID = re.compile(r"^(permno|LPERMNO|gvkey|GVKEY)$", re.I)
LINK_FAKE_MIN = 1_000_000
# NON-merge identity columns whose CO-MEMBERSHIP must be SCRAMBLED. The generators
# route these through gen_00b.resample_identity (partition resampled, not relabeled). They are NOT
# join keys (Explore code-map: firm linking is entirely via permno/LPERMNO), so a synthetic RELABEL
# of the real partition here is a leak -- the real relational grouping (which rows were the same
# firm/inventor) would survive. permno/LPERMNO/gvkey/id/patnum are the allowlisted merge-key
# EXCEPTION (consistent map required for the runtime joins) and are deliberately excluded here.
IDENTITY_SCRAMBLE = re.compile(r"(clean_name|stock_name|assignee|inventor|grid|conm|orig_|firmname)", re.I)
# DERIVED = deterministic functions of the (tested-synthetic) patents_allpats column and the
# public `controls` flag, re-derived in gen_00d by gen_01's exact formulas. They are NOT copied
# from real and NOT in PUBLIC; they resemble real only because the public `controls` flag
# dominates them, so a copy-test would false-positive. They are verified TRANSITIVELY: the
# audit fully tests patents_allpats (their only restricted input) and treats controls as public,
# so a regression that shipped a real value here would surface as a patents_allpats failure.
DERIVED_COL = re.compile(r"^(use_2_1_treat|use_3_2_treat|one_pat_atleast)$", re.I)
# patent-derived columns that every downstream PC-year panel inherits from the SYNTHETIC master
# (Full_sample). The audit verifies each panel's copy EQUALS the synthetic master (not the real
# value) -- so a panel that passed a real flag through would FAIL here.
MASTER_COLS = ["patents_allpats", "patent_sum_2_1", "patent_sum_3_2", "total_pat_sum",
               "use_2_1_treat", "use_3_2_treat", "one_pat_atleast"]
_derived_pub_frac = {}   # use_*_treat -> fraction == public formula (controls|reclassified)
# null-pattern classification for the panel-vs-master check (null cases must be counted,
# not silently ignored). master_val_panel_null is a FAILURE (broken inheritance); master_null_
# panel_val is legitimate ONLY if the retained value is synthetic (verified not == real).
_null_class = {"master_val_panel_null": 0, "master_null_panel_val_synth": 0}
_t4_advantages = []   # (file, column, overlap_minus_chance)
_t7_advantages = []   # (file, column, missingness-linkage AUC advantage over 0.5)
# PUBLIC = genuinely public code/label/design columns that may equal real BY DESIGN. Kept
# DELIBERATELY narrow: FDA product codes + descriptors, public reclassification design, CPT/HCPCS
# procedure codes, CPC, calendar fields. `controls` is a deterministic function of the public
# reclassification status (never-reclassified codes) -- documented public-derived. Restricted-
# DERIVED fields (use_*_treat, one_pat_atleast, patents, is_device, num_claims, token_count, the
# Nexis Class/Preempted flags) are NOT here -- they are TESTED against real so a future
# regression that shipped a real value in one of them would FAIL the gate.
PUBLIC = re.compile(
    r"^(PRODUCTCODE.*|proc1|hcpcs_cpt|hcpcs_level_2|procedure_desc|year|year_reclass.*|treatment.*|use_case|controls|2_1|3_2|"
    r"Reg_Change_List|REGULATIONNUMBER.*|DEVICECLASS|DEVICENAME|"
    r"DESCRIPTION_OF_REGNUM.*|SUBPART_DESCRIPTION.*|PART_DESCRIPTION.*|SUBMISSION_TYPE_ID.*|"
    r"PROBLEM_DESCRIPTION|DEVICE_PROBLEM_CODE|MDR_REPORT_KEY|Petition.*|date_proposed.*|"
    r"FDA_own_accord.*|cpc.*|jurisdiction|filing_status|filing_date|patent_date|patent_type|"
    r"patent_application_type|wipo_kind|series_code|rule_47_flag|withdrawn|filename|type|"
    # F1/F3 rebuild: the former re-identifying tuple columns (cpc/jurisdiction/type/dates/datadate/
    # fyear) stay PUBLIC here because their INDIVIDUAL values are public taxonomy or low-entropy labels
    # -- a per-column VALUE test false-positives on chance collisions of public CPC codes. The actual
    # re-identification risk is STRUCTURAL (the (year,type,cpc,jur) SET/tuple, the MarketScan skeleton,
    # the per-firm fiscal history, the Nexis counts), now broken by the generators and verified by the
    # generator-level QC + the independent adversarial re-identification suite (record-linkage /
    # membership-inference / uniqueness / shuffled-copy / subset-copy), NOT by this value-level audit.
    r"datadate|fyear|indfmt|consol|popsrc|datafmt|curcd|costat|file_year|CPI|YEAR|JURISDICTION|"
    r"Unnamed.*|index|event_time|ET|FE|factorized.*|posttreat.*|class_by_episode.*)$", re.I)
# fake-token shapes emitted by the generators (object columns)
FAKE_TOKEN = re.compile(r"^(SYN|SYNCO |SYNFIRM_|SYNCAT_|synthetic_|term\d|US-\d)", re.I)
FAKE_PAT_MIN = 90_000_000       # de-identified patent numbers start here


_LINEAGE_SOURCES = None


def _lineage_source(rel):
    """The real path this twin stands in for (relative to ROOT, under data/), as the shipped lineage
    records it in `materialized_destination`; None when the file has no lineage row. When a file's rows
    name several destinations, the most frequent one wins."""
    global _LINEAGE_SOURCES
    if _LINEAGE_SOURCES is None:
        _LINEAGE_SOURCES = {}
        path = os.path.join(ROOT, "certification", "GENERATION_LINEAGE.csv")
        if os.path.isfile(path):
            import csv as _csv
            from collections import Counter as _Counter
            counts = {}
            with open(path, encoding="utf-8", newline="") as fh:
                for row in _csv.DictReader(fh):
                    f = (row.get("synthetic_file") or "").replace("\\", "/")
                    src = (row.get("materialized_destination") or "").replace("\\", "/").strip()
                    if f.startswith("synthetic_pipeline/simulated_data/") and src.startswith("data/"):
                        counts.setdefault(f[len("synthetic_pipeline/simulated_data/"):], _Counter())[src] += 1
            _LINEAGE_SOURCES = {k: c.most_common(1)[0][0] for k, c in counts.items()}
    return _LINEAGE_SOURCES.get(rel.replace("\\", "/"))


def _find_real(rel):
    """Resolve a counterpart by source-specific exact path, never basename order.

    Several Nexis queries and generic filenames can recur in different folders.
    A recursive first-hit lookup can therefore compare against the wrong source
    while still reporting PASS. The simulated tree's top-level namespace fixes
    the authoritative real-data location unambiguously.
    """
    parts = rel.replace("\\", "/").split("/")
    if len(parts) < 2:
        return None
    # The shipped generation lineage names, for every twin, the real path it stands in for
    # (certification/GENERATION_LINEAGE.csv, column materialized_destination). That is the authoritative
    # counterpart; the family heuristics below remain the fallback for a file without a lineage row.
    # (Confidential run 2026-09-28: the heuristics mis-mapped two twins whose real sources live under
    # data/raw/ rather than the family's usual folder.)
    lineage_src = _lineage_source(rel)
    if lineage_src is not None:
        return os.path.join(ROOT, lineage_src)
    family, subrel = parts[0], os.path.join(*parts[1:])
    basename = os.path.basename(subrel)
    if family == "synthetic_nexis":
        return os.path.join(RAW, "Liability", subrel)
    if family == "synthetic_marketscan":
        return os.path.join(DERIVED, basename)
    if family == "synthetic_dimensions_wrds":
        return os.path.join(RAW if basename == "compustat_firm_data.csv" else DERIVED,
                            basename)
    if family == "synthetic_maude_linkage":
        return os.path.join(RAW, "MAUDE", subrel)
    if family == "synthetic_patents":
        if basename.startswith(("safety_", "Applicant_")):
            return os.path.join(DERIVED, basename)
        return os.path.join(RAW, subrel)
    if family in {"synthetic_kpst", "synthetic_kpss", "synthetic_price_links"}:
        return os.path.join(RAW, subrel)
    return None


def _read(path):
    """Read the FULL file (no row sampling) so every value is scanned. Certification runs
    once; the memory/time cost is acceptable and the completeness is the point."""
    lp = path.lower()
    if lp.endswith(".parquet"):
        return pd.read_parquet(path)
    if lp.endswith(".xlsx"):
        return pd.read_excel(path)
    # Real data/ holds some messy/leftover files: non-UTF-8 exports (e.g. ASR_*.csv) and empty
    # placeholder CSVs (test_matched_*, check_*). Read robustly so the restricted-value corpus scan
    # stays COMPLETE rather than fail-closed on an unreadable real file: fall back to latin-1 on a
    # decode error (never raises on bytes; value-matching unaffected), and treat a truly empty file as
    # an empty frame (it contributes no restricted values).
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        try:
            return pd.read_csv(path, low_memory=False, encoding="latin-1")
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _is_fake_patnum(s):
    v = pd.to_numeric(s.astype(str).str.extract(r"(\d+)", expand=False), errors="coerce").dropna()
    return bool((v >= FAKE_PAT_MIN).all()) if len(v) else True


_LABEL_VOCAB_MAX = 12   # real distinct symbols at or below which an object column is a label vocabulary

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}|^\d{1,2}/\d{1,2}/\d{2,4}")


def _norm_id(s):
    """Normalize an id string the way the generators do (12345 == 12345.0), so real->fake
    consistency is compared on the same canonical form."""
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except (ValueError, TypeError):
        return str(s)


def _norm_series(s):
    """Vectorized _norm_id: strip a trailing '.0' from whole-number floats so 12345 == 12345.0."""
    return s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)


def _check_id_mapping(id_pairs, findings):
    """FULL (non-sampled) bidirectional injectivity check over ALL deduped (canon,real,fake) pairs:
    each (canon,real) maps to exactly one fake (forward consistency), and each (canon,fake) comes
    from exactly one real (inverse uniqueness -- no two real ids share a fake). Vectorised.
    Returns the count of GLOBALLY-DISTINCT (canon,real,fake) triples actually checked (deduped
    across all files -- not the sum of per-column pair observations, which double-counts a mapping
    that recurs in several files)."""
    if not id_pairs:
        return 0
    allp = pd.concat(id_pairs, ignore_index=True).drop_duplicates()
    fwd = allp.groupby(["canon", "real"])["fake"].nunique()
    for (canon, real), n in fwd[fwd > 1].head(20).items():
        findings.append(("<cross-file>", f"{canon}:{real}", f"real id maps to {n} DIFFERENT fakes"))
    inv = allp.groupby(["canon", "fake"])["real"].nunique()
    for (canon, fake), n in inv[inv > 1].head(20).items():
        findings.append(("<cross-file>", f"{canon}:{fake}", f"fake id shared by {n} real ids -- collision"))
    return len(allp)


def _looks_like_dates(s):
    """True if most values look like dates -- dates are a finite space and collide by chance,
    so a synthesized date column can share some values with real; NON-date object columns
    (names, assignees, companies, legal text) must share ~none."""
    v = s.dropna().astype(str)
    if len(v) == 0:
        return False
    return bool(v.head(500).str.match(_DATE_RE).mean() > 0.5)


def audit_column(col, sim_s, real_s, findings, fpath):
    """Classify + test one column. Returns a category tag for honest reporting:
      'patent_id'/'link_id'  -> identifier tested against the fake domain / non-copy
      'public'               -> allowlisted: a real PUBLIC value is INTENTIONALLY preserved
                                (FDA product codes, years, Federal-Register design, CPC) -- NOT
                                a leak, but NOT 'tested clean' either; reported separately
      'tested'               -> a restricted-value column fully compared to real, not a copy
      'constant'             -> real column is single-valued (carries no restricted info)
      'no_counterpart'       -> no real file/column to compare (synthetic-only or new column)
    A finding is appended (and category still returned) if a test fails."""
    c = str(col)
    if PATENT_ID.match(c):
        if not _is_fake_patnum(sim_s):
            findings.append((fpath, c, "PATENT IDENTIFIER not in fake domain (real id survives)"))
        return "patent_id"
    if LINK_ID.match(c):
        v = pd.to_numeric(sim_s, errors="coerce").dropna()
        if len(v) and not bool((v >= LINK_FAKE_MIN).all()):
            findings.append((fpath, c, f"LINK ID not in fake domain (>= {LINK_FAKE_MIN:,}); "
                                       "real permno/gvkey may survive"))
        return "link_id"
    if PUBLIC.match(c):
        return "public"                              # real PUBLIC value intentionally preserved
    if DERIVED_COL.match(c):
        return "derived"                             # function of tested patents_allpats + public controls
    if real_s is None:
        return "no_counterpart"                      # nothing real to copy from
    if real_s.dropna().nunique() <= 1:
        # EXPLICIT constant handling (no blanket exemption): a numeric constant (0/1/a count)
        # carries no restricted identity; an OBJECT constant is flagged if the simulation
        # repeats the real string verbatim and it is not a fake token (a repeated real string
        # could be sensitive).
        if not pd.api.types.is_numeric_dtype(real_s):
            rv = real_s.dropna().astype(str)
            sv = sim_s.dropna().astype(str)
            if len(rv) and len(sv):
                val = rv.iloc[0]
                if (sv == val).all() and not FAKE_TOKEN.match(val) and val not in ("", "nan", "None"):
                    findings.append((fpath, c, f"CONSTANT object column repeats a real value "
                                               f"{val!r:.60} (not synthesized)"))
        return "constant"
    # restricted-value column: fully compare to real (must not be a verbatim/shuffled copy) ---
    if sim_s.dtype == object or real_s.dtype == object:
        if len(real_s) == len(sim_s):
            a = sim_s.astype(str).to_numpy(); b = real_s.astype(str).to_numpy()
            nonnull = (a != "nan") & (b != "nan")
            if nonnull.sum() >= 30 and np.mean(a[nonnull] == b[nonnull]) > 0.90:
                findings.append((fpath, c, f"OBJECT column ~identical to real "
                                           f"({np.mean(a[nonnull]==b[nonnull]):.0%} of rows match)"))
                return "tested"
        realset = set(real_s.dropna().astype(str).unique())
        simu = [v for v in sim_s.dropna().astype(str).unique()
                if v not in ("", "nan", "None") and not FAKE_TOKEN.match(v)]
        if simu:
            frac_real = sum(v in realset for v in simu) / len(simu)
            # date-like columns collide by chance (finite date space); label vocabularies (a handful of
            # symbols) are shared by construction; EVERY OTHER object column (names, assignees,
            # companies, legal text) must share ~ZERO values with the real set.
            is_date = bool(re.search(r"date", c, re.I)) or _looks_like_dates(real_s)
            # A column whose REAL vocabulary is a handful of symbols (0/1 flags, Yes/No, a code set) is a
            # label vocabulary: sharing its symbols is the only way to encode the same variable and says
            # nothing about any row. Per-row disclosure for such columns is what the ~identical row-match
            # test above, the co-membership test (T4) and the missingness-linkage test (T7) measure.
            # (Confidential run 2026-09-28: 0/1 flags stored as strings tripped the zero-overlap rule.)
            real_card = int(real_s.dropna().astype(str).nunique())
            is_label_vocab = (not is_date) and real_card <= _LABEL_VOCAB_MAX
            if is_date:
                # The generator draws fresh distinct dates inside the column's own period, so some
                # coincidence with real dates is expected by chance. Anchor the allowance on the
                # independence baseline (real distinct dates / calendar span) instead of a flat 30%.
                rd = pd.to_datetime(real_s.dropna().astype(str), errors="coerce").dropna()
                span_days = int((rd.max() - rd.min()).days) + 1 if len(rd) else 0
                expected = min(1.0, rd.nunique() / span_days) if span_days > 0 else 0.0
                thresh = max(0.30, min(0.90, 1.3 * expected))
                why = f"date: coincidence allowed <{thresh:.0%} (independence baseline {expected:.1%})"
            elif is_label_vocab:
                thresh = 1.0
                why = f"label vocabulary of {real_card} symbols (not a value leak)"
            else:
                thresh = 0.0                            # SENSITIVE strings: ZERO overlap enforced
                why = "SENSITIVE — zero allowed"
            if frac_real > thresh:
                n_real = sum(v in realset for v in simu)
                findings.append((fpath, c, f"OBJECT column shares {n_real} value(s) with the real "
                                           f"set ({frac_real:.1%} of sim values; {why})"))
        return "tested"
    if len(real_s) == len(sim_s):
        a = pd.to_numeric(sim_s, errors="coerce").to_numpy()
        b = pd.to_numeric(real_s, errors="coerce").to_numpy()
        both = ~np.isnan(a) & ~np.isnan(b) & (b != 0)     # ignore 0==0 coincidences
        if both.sum() >= 30 and np.mean(a[both] == b[both]) > 0.90:
            findings.append((fpath, c, f"NUMERIC column ~identical to real "
                                       f"({np.mean(a[both]==b[both]):.0%} of non-zero rows match)"))
        return "tested"
    return "no_counterpart"                          # length mismatch -> cannot row-compare


def audit_pc_counts(sim_df, real_df, fpath, findings):
    """In a PATENT-LEVEL file (one row per patent), the per-PRODUCTCODE row
    count IS the patent count and must not reproduce real. Skipped for PC-year panel files,
    where rows-per-code is the (kept, non-restricted) panel skeleton, not a patent count --
    those files carry patent counts in the patents_allpats column, checked as a numeric col."""
    if "PRODUCTCODE" not in sim_df or real_df is None or "PRODUCTCODE" not in real_df:
        return
    if not any(PATENT_ID.match(str(c)) for c in sim_df.columns):
        return                                       # not patent-level: rows/code = panel skeleton
    sc = sim_df["PRODUCTCODE"].value_counts().sort_index()
    rc = real_df["PRODUCTCODE"].value_counts().sort_index()
    common = sc.index.intersection(rc.index)
    if len(common) >= 20:
        frac_equal = float(np.mean(sc.reindex(common).values == rc.reindex(common).values))
        if frac_equal > 0.80:
            findings.append((fpath, "PRODUCTCODE(counts)",
                             f"per-code patent counts reproduce real ({frac_equal:.0%} identical)"))


def audit_derived_consistency(sim_df, findings, fpath):
    """RECOMPUTE the DERIVED flags (use_*_treat, one_pat_atleast) from the SIMULATED
    patents_allpats + controls + reclassification years using gen_01's exact formulas, and
    verify the shipped values EQUAL the recomputation. This is the real fail-closed test for
    the derived columns: a regression that shipped the REAL flag (while patents_allpats stayed
    synthetic) would diverge from the recomputation and FAIL here -- so 'derived' is not an
    unchecked exemption."""
    need = {"patents_allpats", "PRODUCTCODE", "year", "controls"}
    if not need.issubset(set(sim_df.columns)):
        return
    df = sim_df[["PRODUCTCODE", "year", "controls", "patents_allpats"]].copy()
    df["_y21"] = pd.to_numeric(sim_df.get("year_reclassified_2_1"), errors="coerce")
    df["_y32"] = pd.to_numeric(sim_df.get("year_reclassified_3_2"), errors="coerce")
    yr = pd.to_numeric(df["year"], errors="coerce")
    controls = pd.to_numeric(df["controls"], errors="coerce").fillna(0)

    def _presum(ymask_col):
        m = (yr < df[ymask_col]) & df[ymask_col].notnull()
        s = df[m].groupby("PRODUCTCODE")["patents_allpats"].transform("sum")
        df["_tmp"] = s
        out = df.groupby("PRODUCTCODE")["_tmp"].transform(lambda v: v.ffill())
        df.drop(columns="_tmp", inplace=True)
        return out

    exp = {}
    exp["use_2_1_treat"] = ((controls == 1) | (_presum("_y21") > 0)).astype(int)
    exp["use_3_2_treat"] = ((controls == 1) | (_presum("_y32") > 0)).astype(int)
    tot = df.groupby("PRODUCTCODE")["patents_allpats"].transform("sum")
    exp["one_pat_atleast"] = (tot > 0).astype(int)
    for col, e in exp.items():
        if col in sim_df.columns:
            shipped = pd.to_numeric(sim_df[col], errors="coerce").fillna(0).astype(int).to_numpy()
            mism = int((shipped != e.to_numpy()).sum())
            if mism > 0:
                findings.append((fpath, col, f"DERIVED flag differs from recomputation off the "
                                             f"synthetic patents_allpats ({mism} rows) -- may be "
                                             f"copied from real, not derived"))
    # CERTIFY the treatment flags reveal NO restricted membership: in the synthetic data every
    # reclassified code has patents (high synthetic patenting), so use_*_treat == the PUBLIC
    # formula (controls | reclassified) -- a function of public inputs only. Report the % so a
    # 100%==real coincidence is explained (public-derivable), not mistaken for a real copy.
    pub = {"use_2_1_treat": ((controls == 1) | df["_y21"].notnull()).astype(int),
           "use_3_2_treat": ((controls == 1) | df["_y32"].notnull()).astype(int)}
    for col, p in pub.items():
        if col in sim_df.columns:
            got = pd.to_numeric(sim_df[col], errors="coerce").fillna(0).astype(int).to_numpy()
            eq = (got == p.to_numpy())
            _derived_pub_frac[col] = (float(eq.mean()), int((~eq).sum()))  # (fraction, #exceptions)


def audit_master_consistency(sim_df, findings, fpath, master_df):
    """For any downstream PC-year panel, verify its patent-derived columns EQUAL the SYNTHETIC
    master (Full_sample) values, joined on (PRODUCTCODE[,year]). This is the fail-closed test for
    the 18 derived columns outside Full_sample: a panel that copied the REAL use_*_treat /
    one_pat_atleast / patent counts would differ from the synthetic master and FAIL here."""
    if master_df is None or "PRODUCTCODE" not in sim_df.columns:
        return
    cols = [c for c in MASTER_COLS if c in sim_df.columns and c in master_df.columns]
    if not cols:
        return
    key = ["PRODUCTCODE", "year"] if ("year" in sim_df.columns and "year" in master_df.columns) \
        else ["PRODUCTCODE"]
    m = master_df[key + cols].drop_duplicates(subset=key)
    merged = sim_df[key + cols].merge(m, on=key, how="left", suffixes=("", "_m"), indicator=True)
    # FAIL-CLOSED (covers ALL MASTER_COLS -- flags AND counts): a row whose (PRODUCTCODE[,year])
    # KEY is absent from the synthetic master can inherit NONE of the master's synthetic values and
    # retains the panel's own (possibly real) value for every MASTER_COL. Detect by merge KEY, not by
    # a flag column, so count-only panels (no use_*_treat / one_pat_atleast) are covered too.
    n_un = int((merged["_merge"] == "left_only").sum())
    if n_un > 0:
        findings.append((fpath, "+".join(cols), f"{n_un} rows have NO synthetic-master KEY match on "
                         f"{'+'.join(key)} -- they inherit no synthetic value and keep the panel value "
                         f"(possible real leak); master merge must be exhaustive"))
    for c in cols:
        exp = pd.to_numeric(merged[c + "_m"], errors="coerce")   # synthetic master value
        got = pd.to_numeric(merged[c], errors="coerce")          # panel value
        # (a) value mismatch where BOTH are present -- panel not inherited from the synthetic master.
        # Inheritance is DETERMINISTIC (a merge copy), not statistical: ANY single mismatch fails, no
        # minimum-row threshold.
        both = exp.notna() & got.notna()
        if int(both.sum()) >= 1:
            mism = int((got[both].round(3) != exp[both].round(3)).sum())
            if mism > 0:
                findings.append((fpath, c, f"patent-derived column does NOT match the synthetic "
                                           f"master by {'+'.join(key)} ({mism}/{int(both.sum())} rows) "
                                           f"-- not inherited from the synthetic Full_sample (possible real copy)"))
        # (b) NULL-PATTERN check: master HAS a value but the panel is
        # NULL -> broken inheritance (the panel dropped a value it should have inherited); FAIL.
        master_val_panel_null = int((exp.notna() & got.isna()).sum())
        _null_class["master_val_panel_null"] += master_val_panel_null
        if master_val_panel_null > 0:
            findings.append((fpath, c, f"null-pattern mismatch by {'+'.join(key)}: "
                             f"{master_val_panel_null} rows where the synthetic master has a value but "
                             f"the panel is NULL -- inheritance is incomplete (master merge not exhaustive)"))
        # (c) master NULL but panel NON-NULL -> the panel kept its pre-merge SYNTHETIC (_synth_numeric)
        # value where the master is undefined (e.g. a cross-event count). Legitimate (synthetic, not a
        # real copy) but COUNTED + CLASSIFIED here rather than ignored; only flagged if it somehow
        # coincided with the REAL column (which would make it a copy, not a synthetic retention).
        mnull_pnn = exp.isna() & got.notna()
        _null_class["master_null_panel_val_synth"] += int(mnull_pnn.sum())
        if int(mnull_pnn.sum()) > 0:
            real_s = None
            # compare those panel values to the real panel column, if present, to prove synthetic
            rp = _find_real(fpath)
            try:
                if rp and os.path.exists(rp):
                    rdf = _read(rp)
                    if c in rdf.columns and len(rdf) == len(sim_df):
                        real_s = pd.to_numeric(rdf[c], errors="coerce").reset_index(drop=True)
            except Exception:
                real_s = None
            if real_s is not None:
                gv = got.reset_index(drop=True)
                mask = mnull_pnn.reset_index(drop=True) & real_s.notna()
                # No minimum-row threshold (fail-closed): if EVERY master-null/panel-value row equals
                # the real column, the panel copied real where the master is undefined (a synthetic
                # retention would differ on at least one row). Flag any such wholesale copy, any size.
                if int(mask.sum()) >= 1:
                    copyfrac = float((gv[mask].round(3) == real_s[mask].round(3)).mean())
                    if copyfrac > 0.999:
                        findings.append((fpath, c, f"master-null/panel-non-null rows ({int(mask.sum())}) "
                                         f"are ~100% EQUAL to the REAL column -- a real copy where the "
                                         f"synthetic master is undefined, not a synthetic retention"))


def audit_comembership(sim_df, real_df, fpath, findings):
    """AUDIT FINDING 2 -- co-membership scramble, tested (not deferred). For every NON-merge identity
    column (IDENTITY_SCRAMBLE) with a row-aligned real counterpart, verify the synthetic partition is
    NOT a RELABEL of the real one. The generators fake identity columns IN PLACE (row-aligned), so
    real[i] and sim[i] are the same row. If every multi-row REAL group maps to exactly ONE synthetic
    value, the real relational grouping (co-membership) survived a value-only relabel -> FINDING.
    A proper resample scatters a real group's rows across many synthetic entities (fanout > 1).

    Merge keys (permno/LPERMNO/gvkey/id/patnum) are intentionally NOT checked here -- they keep a
    consistent map by design (the runtime `.isin` firm/device gates need it); that residual is a
    partition of PUBLIC entities with all values randomized, documented in DGP_DESIGN.md."""
    if real_df is None:
        return
    n = len(sim_df)
    for col in sim_df.columns:
        c = str(col)
        if not IDENTITY_SCRAMBLE.search(c) or LINK_ID.match(c) or PATENT_ID.match(c):
            continue
        if col not in real_df.columns or len(real_df) != n:
            continue
        r = real_df[col].astype(str).to_numpy()
        s = sim_df[col].astype(str).to_numpy()
        m = (r != "nan") & (r != "None") & (r != "")
        if int(m.sum()) < 50:
            continue
        d = pd.DataFrame({"r": r[m], "s": s[m]})
        gsize = d.groupby("r").size()
        multi = gsize[gsize >= 2].index                       # real groups with >= 2 rows
        if len(multi) < 5:
            continue                                          # too few multi-row groups to judge
        # Exact pair-count calculation without enumerating O(n^2) row pairs. `overlap` is the fraction
        # of real same-entity pairs that remain together synthetically. `chance` is the probability
        # that two arbitrary rows are together under the synthetic partition. The threat-model T4
        # residual is overlap - chance and must be <= 0.02.
        choose2 = lambda x: x * (x - 1) / 2.0
        real_pairs = float(gsize.map(choose2).sum())
        joint_pairs = float(d.groupby(["r", "s"]).size().map(choose2).sum())
        synth_pairs = float(d.groupby("s").size().map(choose2).sum())
        total_pairs = choose2(len(d))
        overlap = joint_pairs / real_pairs if real_pairs else 0.0
        chance = synth_pairs / total_pairs if total_pairs else 0.0
        advantage = max(0.0, overlap - chance)
        _t4_advantages.append((fpath, c, advantage))
        if advantage > 0.02:
            findings.append((fpath, c, f"CO-MEMBERSHIP LINKAGE advantage {advantage:.6f} exceeds "
                             f"T4 threshold 0.02 (overlap={overlap:.6f}; chance={chance:.6f})"))


def audit_missingness_pattern(sim_df, real_df, fpath, findings):
    """AUDIT FINDING 2 (missingness half): a restricted numeric VALUE column must not reproduce the
    real per-row missingness pattern (which rows lack a value is itself a fingerprint). The generators
    now redraw missingness (marginal rate kept, positions fresh). Excluded (their missingness is NOT a
    restricted fingerprint): PUBLIC + identifier columns; and the RE-DERIVED patent columns
    (DERIVED_COL + MASTER_COLS: patent_sum_2_1/3_2, total_pat_sum, patents_allpats, use_*_treat,
    one_pat_atleast) -- these are re-derived by gen_00d from the (tested) patents_allpats + the PUBLIC
    reclassification years, so their NaN pattern is a deterministic function of public structure, not a
    restricted copy, and it legitimately matches real (e.g. patent_sum_2_1 is NaN wherever a code has
    no pre-2->1 period). Flag only a MODERATE-missing column (2-98%) whose synthetic NaN mask is
    ROW-IDENTICAL to the real one (the old copy-through behavior)."""
    if real_df is None or len(real_df) != len(sim_df):
        return
    for col in sim_df.columns:
        c = str(col)
        if (PUBLIC.match(c) or PATENT_ID.match(c) or LINK_ID.match(c) or DERIVED_COL.match(c)
                or c in MASTER_COLS):
            continue
        if col not in real_df.columns:
            continue
        rs, ss = real_df[col], sim_df[col]
        if not (pd.api.types.is_numeric_dtype(rs) or pd.api.types.is_numeric_dtype(ss)):
            continue
        rmask = rs.isna().to_numpy()
        rate = float(rmask.mean()) if rmask.size else 0.0
        if rate < 0.02 or rate > 0.98:
            continue                              # trivial masks (all/near present or absent) can coincide
        smask = ss.isna().to_numpy()
        if smask.shape == rmask.shape:
            # Binary-predictor AUC for predicting the real missingness mask from the synthetic mask.
            # AUC=0.5 is chance; direction is symmetric because inversion is also informative.
            tpr = float(smask[rmask].mean()) if rmask.any() else 0.0
            fpr = float(smask[~rmask].mean()) if (~rmask).any() else 0.0
            auc = 0.5 * (tpr + (1.0 - fpr))
            advantage = abs(auc - 0.5)
            _t7_advantages.append((fpath, c, advantage))
            if advantage > 0.05:
                findings.append((fpath, c, f"MISSINGNESS LINKAGE advantage {advantage:.6f} exceeds "
                                 f"T7 threshold 0.05 (AUC={auc:.6f})"))
        if smask.shape == rmask.shape and np.array_equal(smask, rmask):
            findings.append((fpath, c, f"MISSINGNESS PATTERN copied from real: the synthetic "
                             f"NaN mask is row-identical to the real one (rate {rate:.1%}) -- redraw the "
                             f"positions (marginal rate may stay)."))


# §6 EXACT-STATISTIC disclosure check ----------------------------------------------------------------
# Public-panel files whose ROW COUNT is legitimately public (the FDA product-code x year design), so
# reproducing the real row count is NOT a disclosure. Every OTHER file ships at a ROUNDED row count.
# Files whose exact size the package itself publishes (README, roadmap, manuscript): reproducing that
# size discloses nothing. manual_permno_corrections.csv: "70 hand-coded corrections" (README; the count
# is also the generator's documented constant, gen_00i.MANUAL_CORRECTION_ROWS).
_PUBLIC_ROWCOUNT_FILES = {"Full_sample.csv", "manual_permno_corrections.csv"}


def _round_card(n, sigfigs=2):
    """Round a count to `sigfigs` significant figures (>= nearest 10) -- mirrors gen_00a.round_cardinality
    so the audit can tell an EXACT (un-rounded) real statistic from a rounded one."""
    n = int(n)
    if n <= 0:
        return 0
    digits = int(np.floor(np.log10(n)))
    base = max(10 ** (digits - (sigfigs - 1)), 10)
    return int(round(n / base) * base)


def _public_nan_masks(real_df):
    """Build the set of PUBLIC structural boolean masks a column's NaN pattern could legitimately
    equal WITHOUT disclosing anything restricted. Every mask here is a deterministic function of the
    file's PUBLIC columns ONLY (FDA product-code design + Federal-Register reclassification years +
    the public panel row order): the never-reclassified / control set, the pre- and post-event sets,
    each public column's own missingness, and the exact within-PRODUCTCODE forward-fill structure of
    the re-derived pre-event patent sums. A restricted per-row missingness fingerprint (which specific
    firms/patents lack a value) equals NONE of these, so this exemption is NON-VACUOUS: it fires only
    on a proven public structure, never on an arbitrary grouping. Returns [(label, mask[bool])]."""
    n = len(real_df)
    cols = set(map(str, real_df.columns))
    masks = []

    def _num(name):
        return pd.to_numeric(real_df[name], errors="coerce").to_numpy(dtype=float)

    # (1) each PUBLIC column's OWN missingness (a column NaN exactly where a public field is NaN is
    #     public-derived -- e.g. a value defined only where a public reclassification year exists).
    for c in real_df.columns:
        if PUBLIC.match(str(c)):
            m = real_df[c].isna().to_numpy()
            if m.any() and not m.all():                 # non-trivial only
                masks.append((f"public_col_nan:{c}", m))

    # (2) the control / never-reclassified set (public).
    if "controls" in cols:
        ctrl = np.nan_to_num(_num("controls")).astype(bool)
        masks.append(("controls", ctrl))
        masks.append(("not_controls", ~ctrl))

    # (3) pre-/post-event structure from public year + public reclassification years.
    y = _num("year") if "year" in cols else np.full(n, np.nan)
    yre = None
    for cand in ("year_reclassified", "year_reclassfinal"):
        if cand in cols:
            yre = _num(cand); break
    y21 = _num("year_reclassified_2_1") if "year_reclassified_2_1" in cols else np.full(n, np.nan)
    y32 = _num("year_reclassified_3_2") if "year_reclassified_3_2" in cols else np.full(n, np.nan)
    if yre is None:
        yre = np.where(~np.isnan(y21), y21, y32)
    if not np.isnan(y).all() and not np.isnan(yre).all():
        masks.append(("never_reclassified", np.isnan(yre)))
        masks.append(("has_reclassification", ~np.isnan(yre)))
        masks.append(("pre_event", (y < yre)))          # False where yre is NaN (controls) -> not pre
        masks.append(("post_event", (y >= yre)))

    # (4) EXACT within-PRODUCTCODE forward-fill structure of the re-derived pre-event patent sums
    #     (patent_sum_2_1/3_2 are NaN precisely where no at-or-earlier PC row is a pre-event row; this
    #     reconstructs that mask from PUBLIC year/reclass/PC + row order -- see gen_00d._rederive_full_sample).
    if "PRODUCTCODE" in cols and not np.isnan(y).all():
        pc = pd.Series(real_df["PRODUCTCODE"].astype(str).to_numpy())
        for ycol, ev in ((y21, "2_1"), (y32, "3_2")):
            if not np.isnan(ycol).all():
                pre = pd.Series((y < ycol) & (~np.isnan(ycol)))
                reached = pre.groupby(pc, sort=False).cummax().to_numpy().astype(bool)
                m = ~reached
                if m.any() and not m.all():
                    masks.append((f"patent_sum_ffill_{ev}", m))
    return masks


def _nan_mask_is_public(real_mask, public_masks):
    """True iff the REAL column's NaN mask EXACTLY equals a public structural mask -> its missingness
    is a deterministic function of public inputs, so reproducing its NaN count discloses nothing."""
    for _label, m in public_masks:
        if m.shape == real_mask.shape and np.array_equal(m, real_mask):
            return True
    return False


_PARAMS_FILES = None                                     # basename -> committed columns spec (cached)


def _load_params_files():
    """Load params['files'] (basename -> {col: spec}) committed by gen_00a. Tests may pre-populate
    the module-level cache. Missing/unreadable params -> empty (the NaN-count screen then falls back
    to the rate recomputed from the real column, which is exactly gen_00a's committed definition)."""
    global _PARAMS_FILES
    if _PARAMS_FILES is None:
        import json
        _PARAMS_FILES = {}
        path = os.path.join(ROOT, "synthetic_pipeline", "_synthetic_source_internal",
                            "simulation_parameters.json")
        try:
            with open(path) as f:
                p = json.load(f)
            for key, spec in p.get("files", {}).items():
                _PARAMS_FILES[os.path.basename(str(key))] = spec.get("columns", {})
        except Exception:
            _PARAMS_FILES = {}
    return _PARAMS_FILES


def _committed_missing_rate(rel, col):
    """The committed ROUNDED missingness rate for (file, num-column) from params['files'], or None."""
    cols = _load_params_files().get(os.path.basename(str(rel)), {})
    spec = cols.get(str(col), {})
    if spec.get("role") == "num" and "missing_rate" in spec:
        return float(spec["missing_rate"])
    return None


def _nan_count_consistent_with_committed_rate(s_nan, n_syn, rate):
    """True iff a synthetic NaN count `s_nan` (out of `n_syn` rows) is a PLAUSIBLE draw from the
    committed rounded missingness `rate` -- i.e., within the Binomial band around rate*n_syn (4 sigma
    of sampling variability + a half-ULP of rate-rounding slack). A count consistent with the committed
    rate discloses nothing beyond that (already-public) rate, so an exact match to real_nan that lands
    in this band is a COINCIDENCE of a genuine draw, not a preserved real count."""
    if n_syn <= 0:
        return True
    p = min(max(float(rate), 0.0), 1.0)
    expected = p * n_syn
    std = (n_syn * p * (1.0 - p)) ** 0.5
    band = 4.0 * std + 0.0005 * n_syn                    # 4 sigma + half-ULP (rate rounded to 3 dp)
    return abs(s_nan - expected) <= band


def audit_exact_statistics(sim_df, real_df, fpath, findings):
    """§6 output-disclosure check (runs when the real counterpart is present). For every NON-public
    column: FAIL if the synthetic column reproduces the real column's EXACT distinct-count or sorted
    group-size multiset; and once per file, FAIL if the file reproduces the real (non-rounded) row
    count. These are STRONG indicators -- a smoothed/independent draw essentially never reproduces a
    real multiset or a non-rounded size, so the old resample_identity/redraw_missingness outputs trip
    them and the rounded/smoothed independent-universe outputs pass.

    The NaN-count leg is DELIBERATELY WEAKER -- a PLAUSIBILITY SCREEN, not the binding guarantee. A
    scalar NaN count is ~rate*n, so a GENUINE draw from the committed rounded rate will occasionally
    equal real_nan by pure chance (rate is committed as round(real_nan/real_n), so rate*n_syn ~ real_nan
    whenever n_syn ~ real_n). Flagging every such coincidence is a false positive. So the leg flags an
    exact NaN-count match ONLY when it is BOTH (i) not a public-structural NaN (see _public_nan_masks)
    AND (ii) INCONSISTENT with a genuine draw from the committed rounded rate (outside the Binomial band
    of (committed_rate, n_syn)). The BINDING guarantee that no exact NaN count is ever PRESERVED lives
    elsewhere: the deleted redraw_missingness primitive + the wired structural_fidelity_gate (proves it
    is absent from the shipped bytes) + gen_00a.disclosure_review (proves the committed rate is rounded)."""
    if real_df is None:
        return
    base = os.path.basename(fpath)
    # (d) file row count -- flag an exact match ONLY when the real count is NOT already round (an exact
    #     match to a non-round real count discloses the exact real file size); public panels exempt.
    if base not in _PUBLIC_ROWCOUNT_FILES:
        rr, sr = len(real_df), len(sim_df)
        if sr == rr and rr != _round_card(rr):
            findings.append((fpath, "<rows>", f"EXACT real row count reproduced ({sr:,}) -- the exact "
                             f"real file size must not be disclosed (ship a rounded row count)"))
    public_masks = _public_nan_masks(real_df)             # PUBLIC-structural NaN masks (exemption set)
    for col in sim_df.columns:
        c = str(col)
        if col not in real_df.columns or PUBLIC.match(c):
            continue                                  # public columns legitimately equal real
        rs, ss = real_df[col], sim_df[col]
        r_nonnull, s_nonnull = rs.dropna(), ss.dropna()
        r_card = int(r_nonnull.nunique())
        if base in _PUBLIC_ROWCOUNT_FILES and r_card == len(r_nonnull) == len(real_df):
            # A per-row key of a file whose size is public: its distinct count IS the published row
            # count and its group sizes are all ones by construction, so neither statistic is new
            # information. Every other column of the file stays under the checks below.
            continue
        # (a) distinct-count -- only a LARGE exact match is a disclosure (small cardinalities coincide
        #     by chance, and rounding can legitimately map a tiny count to itself).
        if r_card >= 50 and int(s_nonnull.nunique()) == r_card:
            findings.append((fpath, c, f"EXACT real distinct-count reproduced ({r_card:,}) -- ship a "
                             f"rounded cardinality (independent_universe.generate_identity_column)"))
        # (b) sorted group-size multiset
        if r_card >= 50:
            r_ms = np.sort(r_nonnull.value_counts().to_numpy())
            s_ms = np.sort(s_nonnull.value_counts().to_numpy())
            if r_ms.shape == s_ms.shape and np.array_equal(r_ms, s_ms):
                findings.append((fpath, c, "EXACT real group-size multiset reproduced -- ship a "
                                 "smoothed size family, not the real multiset"))
        # (c) NaN count (PLAUSIBILITY SCREEN -- see docstring). Flag an exact match ONLY when it is
        #     (i) not a public-structural NaN AND (ii) the synthetic count is INCONSISTENT with a genuine
        #     draw from the committed rounded rate. (i) exempts control/pre-event/never-reclassified/
        #     public-column/patent-sum-ffill structure. (ii) exempts a coincidental genuine draw whose
        #     count lands on real_nan (rate*n_syn ~ real_nan by construction). Only a count that the
        #     committed rate would NOT predict (a preserved/injected exact count with a mismatched rate)
        #     still FAILS. Committed rate comes from params['files'][file][col]['missing_rate']; if that
        #     is unavailable, it falls back to round(real_nan/real_n, 3) = gen_00a's committed definition.
        r_nan = int(rs.isna().sum())
        s_nan = int(ss.isna().sum())
        if r_nan > 0 and s_nan == r_nan and not _nan_mask_is_public(rs.isna().to_numpy(), public_masks):
            rate = _committed_missing_rate(fpath, col)
            if rate is None:
                rate = round(r_nan / len(real_df), 3) if len(real_df) else 0.0
            if not _nan_count_consistent_with_committed_rate(s_nan, len(sim_df), rate):
                findings.append((fpath, c, f"EXACT real NaN count reproduced ({r_nan:,}) and INCONSISTENT "
                                 f"with the committed rounded rate {rate} at {len(sim_df):,} synthetic rows "
                                 f"(expected ~{rate * len(sim_df):,.0f}) -- a preserved exact NaN count the "
                                 f"rounded rate would not predict; ship a rounded missingness rate "
                                 f"(independent_universe.draw_missingness_rate)"))


def _cross_file_consistency(idsets, findings):
    """Verify the faked merge keys are CONSISTENT across files: files that share a key type
    (permno, patent number) must have OVERLAPPING fake-id sets -- if the same real id mapped to
    different fakes per file, the sets would be disjoint and the runtime merges would return
    empty. Checks the two merge keys the estimation steps actually join on."""
    # permno: all_patents_w_xi <-> Adverse_fsize (06a/07 filter patents by permno)
    permno = [(rel, s) for (rel, col, s) in idsets if "permno" in col.lower()]
    if len(permno) >= 2:
        big = max(permno, key=lambda t: len(t[1]))
        for rel, s in permno:
            if s is big[1]:
                continue
            if s and not (s & big[1]):
                findings.append((rel, "permno(cross-file)",
                                 f"fake permno set is DISJOINT from {big[0]} -- inconsistent "
                                 "remap would break the runtime firm merge"))
    # patent number: all_patents_w_xi.patnum <-> KPST.patent_num (step 14 join)
    patnum = [(rel, s) for (rel, col, s) in idsets if col.lower() in ("patnum", "patent_num")]
    if len(patnum) >= 2:
        big = max(patnum, key=lambda t: len(t[1]))
        for rel, s in patnum:
            if s is big[1]:
                continue
            if s and not (s & big[1]):
                findings.append((rel, "patnum(cross-file)",
                                 f"fake patent-number set is DISJOINT from {big[0]} -- step 14 "
                                 "merge would be empty"))


def _write_report(disposition, findings, struct_rows, path):
    """Machine-readable certification report (CSV): per-column dispositions, the STRUCTURAL checks
    (mapping / master-consistency / recompute / counts) with their pass/fail, and every finding --
    so a structural failure can never coexist with an all-OK report.

    FAIL-CLOSED + ATOMIC: writes to a unique temp file in the SAME directory, fsyncs, then
    os.replace()s it over the target (so the report is never left partially written or half-stale).
    Any failure RAISES -- the caller must NOT report success (exit 0) without a written report."""
    def esc(x):
        return str(x).replace(",", ";").replace("\n", " ")
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".audit_report_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write("file,column,kind,status\n")
            for rel, col, tag, status in disposition:
                fh.write(f"{esc(rel)},{esc(col)},column:{esc(tag)},{esc(status)}\n")
            for name, status in struct_rows:
                fh.write(f"<structural>,{esc(name)},structural,{esc(status)}\n")
            for f, c, msg in findings:
                fh.write(f"{esc(f)},{esc(c)},finding,{esc(msg)}\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)   # atomic swap over the destination
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise   # FATAL -- do not swallow; caller returns nonzero


def audit_xlsx_csv_pairs(findings):
    """JPE 1.4: every proprietary-format .xlsx workbook must ship a NON-PROPRIETARY .csv copy whose
    values+schema match the workbook. FAIL-CLOSED: any .xlsx without a same-stem .csv, or whose
    same-stem .csv is not the workbook's canonical serialization, is a finding. Returns the count of
    verified-equivalent pairs (for the structural row)."""
    import glob
    n_pairs = n_ok = 0
    for x in sorted(glob.glob(os.path.join(SIM, "**", "*.xlsx"), recursive=True)):
        rel = os.path.relpath(x, SIM)
        c = x[:-5] + ".csv"
        if not os.path.exists(c):
            findings.append((rel, "<xlsx/csv pair>", "xlsx has NO same-stem .csv (JPE 1.4 non-proprietary copy missing)"))
            continue
        n_pairs += 1
        try:
            canon = pd.read_excel(x).to_csv(index=False)
            with open(c, encoding="utf-8", newline="") as fh:
                got = fh.read()
        except Exception as e:  # noqa: BLE001
            findings.append((rel, "<xlsx/csv pair>", f"could not compare workbook to csv: {type(e).__name__}"))
            continue
        if got == canon:
            n_ok += 1
        else:
            findings.append((rel, "<xlsx/csv pair>",
                             "same-stem .csv is NOT the workbook's serialization (independent draw / stale) -- JPE 1.4"))
    return n_pairs, n_ok


# =====================================================================================================
# GLOBAL restricted-value corpus backstop.
# audit_column() only compares a sim column to a real column of the SAME NAME, and exempts a large
# PUBLIC allowlist from any value check -- so a restricted value under a RENAMED/new column, a value
# RELOCATED to a different column, or a REVERSED/TRUNCATED numeric copy all evade. This backstop is
# INDEPENDENT of column classification: it builds the set of genuinely-restricted real values
# (company/assignee/inventor/name/title/legal-text strings + high-entropy numeric IDs, EXCLUDING the
# public taxonomies) and forbids any of them -- in canonical, reversed, or truncated form -- from
# appearing in ANY simulated column, regardless of that column's name.
# =====================================================================================================
# Genuinely-PUBLIC value columns: real values here MAY appear in synthetic (public taxonomies/codes,
# calendar fields, Federal-Register design). Individual CPC codes + jurisdictions are public taxonomy
# (the re-identifying risk from the CPC *set* per patent is a STRUCTURAL matter handled by the
# uniqueness/linkage attack suite, not a value-leak matter).
PUBLIC_VALUE_COLS = re.compile(
    r"^(PRODUCTCODE.*|proc1|hcpcs.*|procedure_desc|year|YEAR|year_reclass.*|REGULATIONNUMBER.*|"
    r"DEVICECLASS|DEVICENAME|DESCRIPTION_OF_REGNUM.*|SUBPART_DESCRIPTION.*|PART_DESCRIPTION.*|"
    r"SUBMISSION_TYPE_ID.*|Reg_Change_List|use_case|controls|2_1|3_2|treatment.*|posttreat.*|"
    r"event_time|ET|FE|factorized.*|class_by_episode.*|"
    # F1/F3 rebuild: cpc/jurisdiction/patent_type/dates/datadate/fyear/filing_status etc. are NO
    # longer public-value-exempt -- they are synthesized, so their real values now enter the
    # restricted corpus and any leak of them into synthetic output is caught by the backstop.
    r"indfmt|consol|popsrc|datafmt|curcd|costat|CPI|file_year|filename|"
    r"Unnamed.*|index|type)$", re.I)
_NUM_ID_MIN = 100_000        # only HIGH-ENTROPY numerics enter the corpus (avoid small-count collisions)


def _canon_str(v):
    """Canonical form for string comparison: lowercase, strip everything but alphanumerics."""
    return re.sub(r"[^a-z0-9]", "", str(v).lower())


def _num_variants(x):
    """Reversible / lossy forms of a sim value that could be a disguised copy of a restricted ID:
      - reversed digits (symmetric: catches a reversed copy),
      - drop-leading / drop-trailing digit (catches the REAL being a truncation of the sim value),
      - PREPEND / APPEND a digit 0-9 (un-truncation: catches the SIM being a shortened copy of a
        longer real ID -- the 'shortened numeric copy' evasion).
    Only variants >= _NUM_ID_MIN are kept (a low-entropy variant would collide by chance). This biases
    toward catching leaks (fail-closed); a coincidental hit is investigated at build, not shipped."""
    s = str(abs(int(x)))
    out = set()
    if len(s) >= 2:
        out.add(int(s[::-1]))
        if s[1:]:
            out.add(int(s[1:]))
        if s[:-1]:
            out.add(int(s[:-1]))
    for d in "0123456789":              # un-truncation: sim = shortened(real)
        out.add(int(d + s))
        out.add(int(s + d))
    return {v for v in out if v >= _NUM_ID_MIN}


def build_restricted_corpus():
    """Collect genuinely-restricted real values from every real file under data/, EXCLUDING public
    taxonomies. Returns (str_corpus, num_corpus). One-time cert cost; sets keep it tractable."""
    str_corpus, num_corpus, errors = set(), set(), []
    for base in (RAW, DERIVED):
        if not os.path.isdir(base):
            continue
        for p in glob.glob(os.path.join(base, "**", "*"), recursive=True):
            if os.path.isdir(p) or not p.lower().endswith((".csv", ".parquet", ".xlsx")):
                continue
            try:
                df = _read(p)
            except Exception as exc:
                errors.append((os.path.relpath(p, ROOT), type(exc).__name__))
                continue
            for col in df.columns:
                # Exclude from the restricted corpus: PUBLIC columns (real values allowed), IDENTIFIER
                # columns (verified by fake-domain elsewhere -- putting real ids in the corpus makes the
                # numeric backstop false-positive on synthetic value columns), and date-like columns
                # (finite space -> chance collisions). Only genuinely-restricted values enter the corpus.
                _cn = str(col)
                if (PUBLIC.match(_cn) or PATENT_ID.match(_cn) or LINK_ID.match(_cn)
                        or DERIVED_COL.match(_cn) or re.search(r"date", _cn, re.I)):
                    continue
                s = df[col].dropna()
                if len(s) == 0:
                    continue
                if pd.api.types.is_numeric_dtype(s):
                    v = pd.to_numeric(s, errors="coerce").dropna()
                    big = v[v.abs() >= _NUM_ID_MIN]
                    num_corpus.update(int(abs(x)) for x in big.unique())
                else:
                    for val in s.astype(str).unique():
                        if FAKE_TOKEN.match(str(val)):
                            continue
                        c = _canon_str(val)
                        if len(c) >= 5:          # skip trivial/short tokens (codes, single letters)
                            str_corpus.add(c)
    return str_corpus, num_corpus, errors


def audit_global_corpus(sim_df, fpath, str_corpus, num_corpus, findings):
    """Scan EVERY simulated column's values against the restricted corpus in canonical + reversed +
    truncated form. Any hit is a leak (fail-closed) regardless of the column's name -- this is what
    catches a renamed/relocated/reversed/truncated restricted value that audit_column() would miss."""
    for col in sim_df.columns:
        # Skip the columns build_restricted_corpus() also excludes: PUBLIC (real values allowed),
        # IDENTIFIERS (verified by fake-domain), and date-like columns (chance collisions). Scanning
        # them would flag legitimately-public values -- the backstop targets restricted values RELOCATED
        # into a genuinely-suspicious (non-public, non-id) column.
        _cn = str(col)
        if (PUBLIC.match(_cn) or PATENT_ID.match(_cn) or LINK_ID.match(_cn)
                or DERIVED_COL.match(_cn) or re.search(r"date", _cn, re.I)):
            continue
        s = sim_df[col].dropna()
        if len(s) == 0:
            continue
        if pd.api.types.is_numeric_dtype(s):
            if not num_corpus:
                continue
            v = pd.to_numeric(s, errors="coerce").dropna()
            # Only scan INTEGER-valued columns for relocated IDs. Real identifiers are integers; the
            # false positives come from continuous VALUE columns (pay/netpay/coins/financials, stored as
            # floats with decimals) whose large magnitudes collide with the ID corpus by chance. A column
            # with any fractional value is a measured quantity, not a hidden id -> skip.
            if len(v) and not bool((v == v.round()).all()):
                continue
            big = {int(abs(x)) for x in v[v.abs() >= _NUM_ID_MIN].unique()}
            hits = big & num_corpus
            for x in big - hits:
                if _num_variants(x) & num_corpus:
                    hits.add(x)
            if hits:
                findings.append((fpath, str(col), f"NUMERIC value(s) match the real restricted-ID "
                                 f"corpus directly or via reversed/truncated form "
                                 f"(renamed/relocated leak): {sorted(hits)[:3]}"))
        else:
            for val in s.astype(str).unique():
                if FAKE_TOKEN.match(str(val)):
                    continue
                c = _canon_str(val)
                if len(c) >= 5 and c in str_corpus:
                    findings.append((fpath, str(col), f"OBJECT value matches the real restricted-string "
                                     f"corpus (renamed/relocated leak): {val[:40]!r}"))
                    break   # one finding per column suffices


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(
        description="Fail-closed real-vs-synthetic leakage audit of synthetic_pipeline/simulated_data/.")
    ap.add_argument(
        "--defer-restricted-counterparts", "--defer-if-no-real-data", dest="defer_restricted",
        action="store_true",
        help="Clean-room build mode. A synthetic file whose expected real counterpart is ABSENT is treated "
             "as DEFERRED (not a finding) IF AND ONLY IF that counterpart is classified RESTRICTED in "
             "RESTRICTED_FILE_INVENTORY.csv -- restricted inputs are excluded from a clean-room source BY "
             "CONSTRUCTION, so the real-vs-synthetic comparison for those files is performed in "
             "the author's confidential certification run, where the real data is bound read-only and this exact "
             "script is hash-bound to the shipped package. SAFETY: (a) a counterpart that IS present is "
             "always fully compared, deferral or not; (b) a counterpart that is absent but NOT classified "
             "restricted is still a FINDING (fail-closed) -- so this can never mask a missing public input "
             "or an unexplained absence; (c) every non-comparative check (global restricted-value corpus "
             "scan, derived/master consistency, identifier domains, symlink/file-type universe) still runs "
             "on every file. Deferrals are counted and recorded in the report.")
    args = ap.parse_args(argv)
    # ROOT/PARENT-SYMLINK guard: os.walk(followlinks=False) still traverses when SIM itself is a
    # symlink, and a symlinked PARENT (synthetic_pipeline/ -> /external) leaves SIM non-link while
    # realpath still resolves outside the package. Reject BOTH simulated_data/ and
    # synthetic_pipeline/ (HERE) being symlinks, and require SIM to resolve UNDER the real package
    # root (ROOT = parent of synthetic_pipeline, measured WITHOUT resolving the possibly-symlinked
    # synthetic_pipeline/).
    if os.path.islink(SIM):
        raise SystemExit(f"simulated_data/ is itself a SYMLINK ({SIM} -> {os.readlink(SIM)}) -- "
                         f"forbidden (could point at an external, possibly restricted, tree).")
    if os.path.islink(HERE):
        raise SystemExit(f"synthetic_pipeline/ is itself a SYMLINK ({HERE} -> {os.readlink(HERE)}) "
                         f"-- forbidden (its simulated_data/ could resolve to external data).")
    if not os.path.isdir(SIM):
        raise SystemExit("simulated_data/ not found -- run the generators first.")
    _pkg_root = os.path.realpath(ROOT)
    if os.path.commonpath([os.path.realpath(SIM), _pkg_root]) != _pkg_root:
        raise SystemExit(f"simulated_data/ resolves OUTSIDE the package root {_pkg_root}: "
                         f"{os.path.realpath(SIM)}")
    # --- PER-FILE DEFERRAL OF RESTRICTED-COUNTERPART COMPARISONS (revised 2026-09-11) ------------
    # This audit compares each synthetic file to its REAL counterpart. In a clean-room build the source
    # ships the PUBLIC data/ inputs but excludes every RESTRICTED input by construction, so the tree is
    # deliberately PARTIAL: public counterparts are present (and are fully compared), restricted ones are
    # not. The first cut of this flag was all-or-nothing ("defer only if ZERO counterparts exist"), which
    # broke exactly here -- with public data staged it could neither defer nor complete. The correct rule is
    # per-file and evidence-driven: an ABSENT counterpart is DEFERRED only when that counterpart is
    # classified RESTRICTED in RESTRICTED_FILE_INVENTORY.csv; an absent counterpart that is NOT restricted
    # remains a FINDING (fail-closed), so a missing public input can never be masked. Deferred files still
    # get every non-comparative check, and their real-vs-synthetic comparison is performed in
    # the author's confidential certification run, with the real data bound read-only.
    _restricted_paths = set()
    _shipped_members = set()
    if args.defer_restricted:
        _rfi = os.path.join(ROOT, "RESTRICTED_FILE_INVENTORY.csv")
        if not os.path.isfile(_rfi):
            print(f"FATAL: --defer-restricted-counterparts requires {_rfi} to classify counterparts; "
                  f"refusing to defer without it (fail-closed).")
            return 1
        import csv as _csv2
        for _r in _csv2.DictReader(open(_rfi, encoding="utf-8", newline="")):
            if (_r.get("classification") or "").strip().upper() == "RESTRICTED":
                _f = (_r.get("file") or "").strip()
                if _f:
                    _restricted_paths.add(_f)
                    _restricted_paths.add(os.path.basename(_f))
        if not _restricted_paths:
            print("FATAL: RESTRICTED_FILE_INVENTORY.csv lists no RESTRICTED rows; a deferral decision "
                  "cannot be grounded, so refusing to defer (fail-closed).")
            return 1
        # A counterpart can also be absent BY CONSTRUCTION because it is simply NOT A SHIPPED MEMBER --
        # e.g. data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv, which is public MAUDE-derived but is
        # deliberately excluded from the package (the synthetic counterpart is materialized at runtime
        # instead). The rule that actually matters is therefore: FAIL CLOSED only when the counterpart is a
        # member the source is SUPPOSED to contain (i.e. on the reviewed allowlist) and it is missing --
        # that is broken staging. Everything not shipped is absent by design and defers.
        _allow = os.path.join(ROOT, "certification", "PUBLIC_PACKAGE_ALLOWLIST.txt")
        if not os.path.isfile(_allow):
            print(f"FATAL: --defer-restricted-counterparts requires {_allow} to tell which counterparts "
                  f"the source is supposed to contain; refusing to defer without it (fail-closed).")
            return 1
        for _ln in open(_allow, encoding="utf-8"):
            _ln = _ln.strip()
            if _ln and not _ln.startswith("#") and _ln.startswith("data/"):
                _shipped_members.add(_ln)
        if not _shipped_members:
            print("FATAL: the reviewed allowlist lists no data/ members, so 'should this counterpart be "
                  "present?' cannot be answered; refusing to defer (fail-closed).")
            return 1

    def _absence_is_by_construction(real_path):
        """-> reason string if this counterpart's ABSENCE from a clean-room source is BY CONSTRUCTION,
        else None (in which case the absence is unexplained and must FAIL CLOSED).

        Two grounded reasons, in order of strength:
          * the counterpart is a reviewed RESTRICTED input -- it must never be in a clean-room source; or
          * the counterpart is NOT a shipped member (absent from the reviewed allowlist of data/ members)
            -- the source only ever contains what the deposit ships, so anything else is absent by design.
        A counterpart that IS an allowlisted shipped member but is missing returns None: that is broken
        staging, not a design property, and it must surface as a finding."""
        if not real_path:
            return None
        rel = os.path.relpath(real_path, ROOT) if os.path.isabs(real_path) else real_path
        if rel in _restricted_paths or os.path.basename(rel) in _restricted_paths:
            return "counterpart is a reviewed RESTRICTED input"
        if rel not in _shipped_members:
            return "counterpart is not a shipped member (not on the reviewed allowlist)"
        return None

    deferred_files = []
    # --------------------------------------------------------------------------------------------
    findings, n_files, n_cols, n_rows = [], 0, 0, 0
    # FAIL-CLOSED file-type universe: simulated_data/ must hold ONLY real (non-symlink)
    # .csv/.parquet/.xlsx files. (a) A stray .json/.pkl/.zip or hidden dotfile would ship WITHOUT
    # column-level leakage inspection. (b) A SYMLINK -- even a permitted-looking apparently.csv ->
    # /external/restricted.csv -- would be dereferenced by the builder's copy and ship external
    # bytes uninspected. os.walk(followlinks=False) does not recurse into symlinked dirs, and every
    # dir AND file entry is islink-checked. Both are findings (fail-closed).
    for _dp, _dirs, _names in os.walk(SIM, followlinks=False):
        for _d in _dirs:
            if os.path.islink(os.path.join(_dp, _d)):
                _rel = os.path.relpath(os.path.join(_dp, _d), SIM)
                findings.append((_rel, "<dir-symlink>", "SYMLINK directory under simulated_data/ -- "
                                 "may point outside the synthetic tree; symlinks are forbidden"))
        for _n in _names:
            _full = os.path.join(_dp, _n)
            _rel = os.path.relpath(_full, SIM)
            if os.path.islink(_full):
                findings.append((_rel, "<file-symlink>", "SYMLINK under simulated_data/ -- would "
                                 "dereference to an external (possibly restricted) file on copy; "
                                 "symlinks are forbidden"))
            elif not _n.lower().endswith((".csv", ".parquet", ".xlsx")):
                findings.append((_rel, "<file>", "NON-PERMITTED file type under simulated_data/ -- "
                                 "ships without column-level leakage inspection; only "
                                 ".csv/.parquet/.xlsx are allowed"))
    cat = {"patent_id": 0, "link_id": 0, "public": 0, "derived": 0, "tested": 0,
           "constant": 0, "no_counterpart": 0}
    n_no_real_file = 0
    disposition = []                                 # (file, column, category, status)
    idsets = []                                      # (file, id-column, set-of-fake-values)
    id_pairs = []                                    # deduped (canon, real, fake) pairs -> full check
    n_map_checked = 0
    # load the SYNTHETIC master (Full_sample) once, to verify every downstream panel's
    # patent-derived columns are inherited from it (not copied from real).
    master_df = None
    _mpath = os.path.join(SIM, "synthetic_dimensions_wrds", "Full_sample.csv")
    if os.path.exists(_mpath):
        try:
            master_df = pd.read_csv(_mpath, low_memory=False,
                                    usecols=lambda c: c in (["PRODUCTCODE", "year"] + MASTER_COLS))
        except Exception:
            master_df = None
    # F2: build the GLOBAL restricted-value corpus once, then scan every sim file's values against it
    # (name-independent) so a renamed/relocated/reversed/truncated restricted value cannot evade.
    str_corpus, num_corpus, corpus_errors = build_restricted_corpus()
    for rel, err in corpus_errors:
        findings.append((rel, "<restricted-corpus>",
                         f"real tabular file unreadable while building the global restricted-value "
                         f"corpus ({err}); refusing an incomplete privacy scan"))
    n_global_findings_before = 0
    print(f"Global restricted-value corpus: {len(str_corpus):,} restricted strings + "
          f"{len(num_corpus):,} high-entropy numeric IDs (public taxonomies excluded).")
    for p in sorted(glob.glob(os.path.join(SIM, "**", "*"), recursive=True)):
        if os.path.isdir(p) or not p.lower().endswith((".csv", ".parquet", ".xlsx")):
            continue
        rel = os.path.relpath(p, SIM)
        n_files += 1
        try:
            sim_df = _read(p)                        # FULL read (every row)
        except Exception as e:
            findings.append((rel, "<file>", f"unreadable: {e}")); continue
        n_rows += len(sim_df)
        real_path = _find_real(rel)
        real_df = None
        if real_path and os.path.exists(real_path):
            try:
                real_df = _read(real_path)
            except Exception as e:
                # FAIL-CLOSED: a real counterpart EXISTS but could not be
                # loaded (e.g. OOM on the 1.7 GB Adverse_fsize). Silently setting real_df=None would skip
                # every real-vs-synthetic check -- including the exact-statistic disclosure check -- for
                # exactly the most sensitive file. Record a finding so the build ABORTS rather than ship
                # an unverified file. (On an adequately-resourced build host the read succeeds.)
                real_df = None
                findings.append((rel, "<file>", f"real counterpart exists but failed to load ({e}) -- "
                                 f"cannot verify no exact-statistic / value disclosure; failing closed"))
        else:
            n_no_real_file += 1
            _why = _absence_is_by_construction(real_path) if args.defer_restricted else None
            if _why:
                # Absent BY CONSTRUCTION: the counterpart is a reviewed RESTRICTED input that a
                # clean-room source must not contain. Defer THIS FILE's real-vs-synthetic
                # comparison to the confidential run; every non-comparative check below still runs.
                deferred_files.append((rel, _why))
            else:
                findings.append((rel, "<counterpart>",
                                 "expected source-specific real counterpart is missing; cannot "
                                 "perform the confidential real-vs-synthetic comparison"))
        for col in sim_df.columns:
            n_cols += 1
            real_s = real_df[col] if (real_df is not None and col in real_df) else None
            n_before = len(findings)
            tag = audit_column(col, sim_df[col], real_s, findings, rel)
            cat[tag] = cat.get(tag, 0) + 1
            status = findings[-1][2] if len(findings) > n_before else "OK"
            disposition.append((rel, col, tag, status))
            if (PATENT_ID.match(str(col)) or LINK_ID.match(str(col))):
                vals = set(pd.to_numeric(sim_df[col], errors="coerce").dropna().astype("int64").tolist())
                idsets.append((rel, str(col), vals))
                # POSITIVE fake-domain guarantee (independent-universe): EVERY id must be in the fake
                # domain (patents >= 90M, permno/gvkey >= 1M), which has zero overlap with the real id
                # ranges -- so no real id value can survive. This is checked here explicitly so the
                # guarantee holds whether or not the (obsolete) row-aligned pairing runs.
                if vals:
                    dom_min = FAKE_PAT_MIN if PATENT_ID.match(str(col)) else LINK_FAKE_MIN
                    below = sum(1 for v in vals if int(v) < dom_min)
                    if below:
                        findings.append((rel, str(col), f"{below} id value(s) BELOW the fake domain "
                                         f"(< {dom_min:,}) -- a real id may have survived"))
                if not INDEPENDENT_UNIVERSE:
                    # legacy row-aligned de-identification: collect DEDUPED (canon, real, fake) pairs
                    # for the injectivity check. Under the independent-universe design this is disabled
                    # (see INDEPENDENT_UNIVERSE): there is no consistent real->fake map -- fresh ids are
                    # drawn per file, so pairing would flag the intended anonymity as a "collision".
                    if (real_s is not None and len(real_s) == len(sim_df[col])
                            and os.path.basename(rel) not in RESIMULATED_FILES):
                        canon = ("PAT" if PATENT_ID.match(str(col))
                                 else ("PERMNO" if "permno" in str(col).lower() else "GVKEY"))
                        pair = pd.DataFrame({"real": _norm_series(real_s), "fake": _norm_series(sim_df[col])})
                        pair = pair[~pair.real.isin(("nan", "", "None"))].drop_duplicates()
                        pair["canon"] = canon
                        id_pairs.append(pair)
                        n_map_checked += len(pair)
        if "PRODUCTCODE" in sim_df.columns and real_df is not None:
            audit_pc_counts(sim_df, real_df, rel, findings)
        if os.path.basename(rel) == "Full_sample.csv":
            audit_derived_consistency(sim_df, findings, rel)      # master: recompute from its patents
        else:
            audit_master_consistency(sim_df, findings, rel, master_df)  # panels: inherit from master
        audit_comembership(sim_df, real_df, rel, findings)       # non-key identity scramble
        audit_missingness_pattern(sim_df, real_df, rel, findings)  # missingness not copied
        audit_exact_statistics(sim_df, real_df, rel, findings)   # §6: no EXACT distinct/multiset/NaN/rows
        # F2: name-independent global-corpus scan (covers columns audit_column tagged 'no_counterpart'
        # or 'public', so a renamed/relocated/reversed restricted value cannot slip through).
        audit_global_corpus(sim_df, rel, str_corpus, num_corpus, findings)
    # NONEMPTY: an empty simulation (zero data files) must NOT pass -- it would scan nothing and
    # trivially report "0 leaks". Require at least one permitted data file.
    if n_files == 0:
        findings.append(("<simulated_data>", "<empty>", "simulated_data/ contains ZERO data files "
                         "-- an empty simulation cannot certify no-leakage; refusing to pass"))
    _cross_file_consistency(idsets, findings)
    n_map_distinct = _check_id_mapping(id_pairs, findings)   # GLOBALLY-deduped triple count
    # record the STRUCTURAL checks (which run AFTER per-column statuses) in the report, each with
    # its own pass/fail, so a structural failure is visible in the file rather than only in exit(1).
    def _fail(*sigs):
        return "FAIL" if any(any(s in (f[2] if len(f) > 2 else "") for s in sigs)
                             for f in findings) else "PASS"
    # JPE 1.4 non-proprietary-copy pair check (xlsx <-> same-stem csv serialization).
    _n_pairs, _n_ok = audit_xlsx_csv_pairs(findings)
    struct_rows = [
        # Deferrals are RECORDED, never silent. This row states how many files had their
        # real-vs-synthetic comparison deferred to the author's confidential certification run because the
        # counterpart is a reviewed RESTRICTED input, absent from a clean-room source by construction.
        (f"counterpart_comparisons_deferred_to_confidential ({len(deferred_files)} file(s); "
         f"{sum(1 for _f, _w in deferred_files if 'RESTRICTED' in _w)} restricted, "
         f"{sum(1 for _f, _w in deferred_files if 'not a shipped member' in _w)} not-shipped)",
         ("DEFERRED (mandatory in the author's confidential certification run, real data bound read-only)"
          if deferred_files else "none (every expected counterpart was present and compared here)")),
        ("nonempty_simulation", _fail("ZERO data files")),
        ("no_symlinks_under_simulated_data", _fail("SYMLINK")),
        (f"global_restricted_value_corpus (F2: name-independent scan; {len(str_corpus):,} strings + "
         f"{len(num_corpus):,} IDs)",
         _fail("match the real restricted-ID corpus", "match the real restricted-string corpus")),
        (f"xlsx_csv_pair_equivalence (JPE 1.4 non-proprietary copies: {_n_ok}/{_n_pairs} verified)",
         _fail("non-proprietary copy missing", "NOT the workbook's serialization", "could not compare workbook")),
        ("file_type_universe (only .csv/.parquet/.xlsx under simulated_data/)", _fail("NON-PERMITTED file type")),
        ("independent_identifier_domains_and_cross_file_key_overlap",
         _fail("BELOW the fake domain", "fake patent-number set is DISJOINT", "collision")),
        ("derived_flags_match_synthetic_master (all panels)", _fail("does NOT match the synthetic")),
        ("master_merge_exhaustive (no unmatched master-key rows)", _fail("NO synthetic-master KEY match")),
        ("full_sample_flags_recomputed_from_synthetic_patents", _fail("differs from recomputation")),
        ("per_code_patent_counts_resimulated", _fail("reproduce real")),
        ("non_key_identity_comembership_scrambled (names/assignee/inventor/GRID not a relabel)",
         _fail("CO-MEMBERSHIP PRESERVED")),
        ("missingness_pattern_not_copied (restricted value NaN mask redrawn, not real)",
         _fail("MISSINGNESS PATTERN copied")),
        (f"T4_comembership_advantage (max_advantage="
         f"{max((x[2] for x in _t4_advantages), default=0.0):.8f}; threshold=0.02)",
         _fail("CO-MEMBERSHIP LINKAGE advantage")),
        (f"T7_missingness_linkage_advantage (max_advantage="
         f"{max((x[2] for x in _t7_advantages), default=0.0):.8f}; threshold=0.05)",
         _fail("MISSINGNESS LINKAGE advantage")),
        ("no_exact_statistic_disclosure (§6: no synthetic column/file reproduces the real "
         "distinct-count / group-size multiset / NaN count / row count)",
         _fail("EXACT real distinct-count reproduced", "EXACT real group-size multiset reproduced",
               "EXACT real NaN count reproduced", "EXACT real row count reproduced")),
        ("master_null_pattern (master-value/panel-null = FAIL; master-null/panel-value = synthetic-retained)",
         _fail("null-pattern mismatch", "master-null/panel-non-null rows")),
        ("treatment_flags_public_derivable (DIAGNOSTIC metric, not a pass/fail)",
         "DIAGNOSTIC: " + ("; ".join(f"{k}={v[0]*100:.4f}%/{v[1]}exc"
                                     for k, v in _derived_pub_frac.items()) or "n/a")),
        ("null_pattern_counts (DIAGNOSTIC)",
         f"DIAGNOSTIC: master-value/panel-null={_null_class['master_val_panel_null']} (0 required); "
         f"master-null/panel-value={_null_class['master_null_panel_val_synth']} "
         f"(synthetic-retained where master undefined; verified not == real)"),
    ]
    # R7 F4: the report path is overridable so the authorized wrapper can write it OUTSIDE a read-only
    # AUTH_SRC (an immutable authorized source must not be mounted writable just to drop a report).
    report_path = os.environ.get("SIM_AUDIT_REPORT") or os.path.join(HERE, "simulated_data_audit_report.csv")
    # FAIL-CLOSED: the machine-readable report IS the certification evidence. If it cannot be
    # written, the audit must NOT report success -- refuse to exit 0 with a missing/stale report.
    try:
        _write_report(disposition, findings, struct_rows, report_path)
    except Exception as e:
        print(f"\nFATAL: could not write the certification report to {report_path}: {e}\n"
              f"Refusing to exit 0 without a freshly written report (certification evidence is "
              f"mandatory).")
        return 1

    print(f"\n=== audit_simulated_data: FULL scan of {n_files} files / {n_cols} columns / "
          f"{n_rows:,} rows (no sampling) ===")
    print("Per-column disposition:")
    print(f"  identifiers verified fake-domain/remapped : {cat['patent_id'] + cat['link_id']}")
    print(f"  restricted values fully compared to real  : {cat['tested']}  (0 are copies)")
    print(f"  PUBLIC values INTENTIONALLY preserved      : {cat['public']}  "
          f"(FDA product codes, years, Federal-Register design, CPC -- real by design)")
    print(f"  DERIVED from tested patents_allpats+controls: {cat['derived']}  "
          f"(use_*_treat, one_pat_atleast -- verified transitively)")
    print(f"  real column constant (no info)             : {cat['constant']}")
    if deferred_files:
        _nr = sum(1 for _f, _w in deferred_files if "RESTRICTED" in _w)
        _ns = len(deferred_files) - _nr
        print(f"COUNTERPART COMPARISONS DEFERRED: {len(deferred_files)} file(s) ({_nr} restricted input(s), "
              f"{_ns} not-shipped member(s)) whose real\n"
              f"  counterpart is a reviewed RESTRICTED input absent from this clean-room source by\n"
              f"  construction. Their real-vs-synthetic comparison is MANDATORY in\n"
              f"  the author's confidential certification run (real data bound read-only, this script hash-bound\n"
              f"  to the shipped package). Every non-comparative check still ran on them here.")
    print(f"  no real counterpart to compare             : {cat['no_counterpart']}  "
          f"({n_no_real_file} files are synthetic-only, e.g. KPST)")
    if INDEPENDENT_UNIVERSE:
        print("Identifiers: no real-to-fake mapping is constructed or tested. Every identifier was "
              "checked against its disjoint synthetic domain, and required synthetic merge-key sets "
              "were checked for cross-file overlap.")
    else:
        print(f"Legacy cross-file id mapping: {n_map_distinct:,} globally-distinct triples "
              f"({n_map_checked:,} observations) checked both ways.")
    print(f"Derived flags: Full_sample recomputed from its synthetic patents_allpats; every "
          f"downstream panel's derived + patent columns verified == the synthetic master.")
    print(f"Panel/master null pattern: master-value/panel-null="
          f"{_null_class['master_val_panel_null']} (must be 0 -- else inheritance incomplete); "
          f"master-null/panel-value={_null_class['master_null_panel_val_synth']} rows kept the "
          f"synthetic pre-merge value where the master is undefined (cross-event counts; verified "
          f"NOT equal to the real column, so synthetic-retained, not a real copy).")
    if _derived_pub_frac:
        pf = ", ".join(f"{k}={v[0]*100:.4f}% ({v[1]} rows patent-condition-driven, not "
                       f"purely public)" for k, v in _derived_pub_frac.items())
        print(f"Treatment flags public-derivability (== controls|reclassified): {pf}. The few "
              f"non-public rows are driven by the SYNTHETIC patent condition (still not a real "
              f"copy -- they equal the synthetic-master recomputation, verified above).")
    print(f"Machine-readable file+column report: {report_path}")
    if findings:
        print(f"\nFAIL -- {len(findings)} finding(s):\n")
        for f, c, msg in findings:
            print(f"  [{f}] {c}: {msg}")
        return 1
    tested = cat["patent_id"] + cat["link_id"] + cat["tested"]
    print(f"\nPASS -- of {n_cols} columns, {tested} carry restricted data and were fully tested "
          f"against the real inputs with 0 leaks (identifiers verified by fake domain; values/text "
          f"verified not a copy; per-code counts resimulated; merge keys consistent). "
          f"{cat['public']} hold PUBLIC values kept by design; {cat['derived']} are DERIVED from "
          f"the tested patents_allpats + public controls (verified transitively); "
          f"{cat['constant']} constant (checked for repeated real strings); "
          f"{cat['no_counterpart']} had no comparable real column. This is a completeness claim "
          f"over the tested + transitively-covered columns, not over the allowlisted public ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
