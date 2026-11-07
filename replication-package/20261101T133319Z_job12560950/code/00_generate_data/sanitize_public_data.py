#!/usr/bin/env python3
"""
Fail-closed public-data sanitizer (JPE public Dataverse build).

Runs on the PUBLIC BUILD OUTPUT (after the package build applies its exclusions),
never on the canonical editor-confidential source. It enforces, deterministically:

  1. EXPLICIT per-file PUBLIC SCHEMAS for the mixed master panel(s): keep ONLY the
     listed public variables (FDA registry/MAUDE outcomes + public reclassification
     facts); drop everything else. Values are read as text so kept columns are
     BYTE-IDENTICAL (no None->blank / float round-trip).
  2. CLASSIFY EVERY shipping tabular file: each must be either (a) a SCHEMA target,
     or (b) verified to contain no restricted-derived columns. ANY unclassified or
     restricted-bearing file -> the script FAILS (non-zero exit).
  3. POST-WRITE VALIDATION: row counts preserved; no restricted column survives;
     output schema == declared schema.

Restricted-lineage selected/matched panels and Dimensions-derived files are
excluded upstream by the build's exclusion rules, not shipped at all. The public
package therefore reproduces public-OUTCOME estimates only via the editor
(restricted) package; it intentionally ships no patent-derived membership.

Emits certification/SANITIZER_REPORT.csv (pre/post sha256, rows, cols, dropped).
Usage:  python3 code/00_generate_data/sanitize_public_data.py <public_build_root>
"""
import sys, os, glob, csv, re, hashlib
import pandas as pd

# --- fail-closed file-type universe -------------------------------------------
# Every file under data/ must be one this program can OPEN AND SCAN. Case-insensitive.
# A tabular file it cannot read is a HARD FAILURE (never a silent skip). Genuinely
# non-tabular sidecars (docs/images) are allowlisted by extension so their
# presence is accounted for, not ignored.
TABULAR_EXTS = (".csv", ".tsv", ".txt", ".parquet", ".feather", ".xlsx", ".xls",
                ".dta", ".sas7bdat", ".json", ".pkl", ".pickle")
NONTABULAR_OK_EXTS = (".md", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg",
                      ".do", ".r", ".py", ".sh", ".tex", ".log", ".yml", ".yaml",
                      ".gitignore", ".gitkeep", ".sql", ".html")
# Magic-byte signatures for binary sidecars, and the set of text sidecars. A non-tabular sidecar accepted
# by EXTENSION must actually BE that format (external-audit F4, 2026-09-07): arbitrary bytes parked at a
# .png/.pdf/... path -- a hypothetical restricted payload -- must NOT pass as a "safe sidecar" unchecked.
SIDECAR_MAGIC = {
    ".png": [b"\x89PNG\r\n\x1a\n"], ".jpg": [b"\xff\xd8\xff"], ".jpeg": [b"\xff\xd8\xff"],
    ".gif": [b"GIF87a", b"GIF89a"], ".pdf": [b"%PDF-"],
}
SIDECAR_TEXT = (".md", ".do", ".r", ".py", ".sh", ".tex", ".log", ".yml", ".yaml", ".gitignore",
                ".sql", ".html", ".svg")


def verify_sidecar_format(full, low):
    """Return None if the non-tabular sidecar's CONTENT matches its declared extension, else a failure
    reason string (external-audit F4). Binary media must carry the right magic bytes; text sidecars must be
    valid UTF-8 with no NUL byte. Unlisted-but-allowlisted extensions (e.g. .gitkeep) pass unchecked."""
    mext = next((m for m in SIDECAR_MAGIC if low.endswith(m)), None)
    if mext:
        try:
            head = open(full, "rb").read(16)
        except Exception as e:                                   # noqa: BLE001
            return f"unreadable ({type(e).__name__})"
        if not any(head.startswith(s) for s in SIDECAR_MAGIC[mext]):
            return f"extension {mext} but content lacks its magic bytes (opaque/hidden payload?)"
        return None
    ext = os.path.splitext(low)[1]
    if ext in SIDECAR_TEXT:
        try:
            data = open(full, "rb").read()
        except Exception as e:                                   # noqa: BLE001
            return f"unreadable ({type(e).__name__})"
        if b"\x00" in data:
            return f"{ext} declared as text but contains NUL bytes (binary/hidden payload?)"
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return f"{ext} declared as text but is not valid UTF-8 (binary/hidden payload?)"
    return None
# high-signal restricted VALUE markers (word-boundary, case-insensitive) that must
# not appear inside cell contents even when the COLUMN NAME looks innocuous.
# Restricted-identifier LABELS appearing as cell values (a restricted merge leaked under an innocuous
# header). The word markers are specific restricted terms that do not occur in public FDA text. `npi`
# is narrowed to the actual National-Provider-Identifier FORM (the label adjacent to a 10-digit id):
# a bare `\bnpi\b` false-positived on public FDA device MODELS like "NPI-200" (3-4 digits). MarketScan
# claims (the only source with real NPIs) are excluded wholesale, so this only ever fired falsely.
VALUE_MARKERS = re.compile(
    r"\b(?:permno|lpermno|gvkey|patnum|assignee|inventor_id)\b|\bnpi\b\W{0,3}\d{10}\b", re.I)

# --- explicit per-file PUBLIC SCHEMA (keep ONLY these; drop the rest) ----------
# Full_sample public schema = FDA registry metadata + public reclassification FACTS
# + public outcomes (510(k)/PMA registry counts + MAUDE adverse-event count matrix).
# Excludes ALL patent/firm-size columns AND the patent-derived membership flags
# (controls, use_2_1_treat, use_3_2_treat, unique_firms*). Verified to match the
# file's actual columns; the sanitizer FAILS if any listed column is absent.
PUBLIC_SCHEMAS = {}
# EMPTY BY DESIGN. The only schema target was data/derived/Full_sample.csv --
# the RESTRICTED mixed master, which is not shipped: it is created at RUNTIME on a fresh
# extraction from the canonical synthetic payload + public_master_skeleton.parquet, and the builder
# is structurally barred from copying it (the build's exclusion rules). Column-stripping a mixed
# master is NOT sanitization anyway -- row membership, ordering and missingness remain disclosure
# surfaces -- so the strip step is retired rather than relocated. Step 2 below (CLASSIFY EVERY
# shipping tabular file: schema target OR verified free of restricted-derived columns) still runs
# and is now STRICTER, since no file is exempt as a schema target. The historical 71-column public
# schema is preserved in the author's version history of this file.

# patterns that mark a restricted-derived column (validation / classification)
RESTR_SUBSTR = ["pay","proc_count","coins","billedamt","paidamt","utilization","n_claims",
  "firm_size","permno","lpermno","gvkey","_assets","compustat","patent","patnum","_allpats","_newfirm",
  "pats_nodrug","pat_sum","real_pats","one_pat","total_pat","inventor","assignee","xi_real",
  "xi_nominal","xi_","cites","citation","times_cited","safety","baseline_event_count",
  "use_2_1_treat","use_3_2_treat","unique_firms","firm_expansion_patents"]
# files whose restricted-looking column names are actually PUBLIC (KPSS open release)
PUBLIC_OK = {"data/raw/KPSS_2019_public.csv","data/raw/KPST_Breakthrough.csv"}

# pandas_dedupe settings sidecars: the learned model (an EXTENSIONLESS binary, so it can't be
# classified by extension) and its training-pair JSON, under data/derived/dedupe_settings*/. They
# carry ONLY public FDA 510(k)/MAUDE fields (APPLICANT/KNUMBER/DEVICENAME/PRODUCTCODE) and learned
# dedup weights -- never a restricted (Dimensions/WRDS/MarketScan/Nexis) source. We do NOT skip them
# (that would be fail-open); they are VERIFIED by scanning their raw bytes for any restricted-SOURCE
# identifier token, which could not appear in FDA dedup data, and abort if one does. (is_restricted
# is a column-name SUBSTRING heuristic and would false-positive on device-name values like "safety
# needle", so the value scan below uses these exact, unambiguous restricted-source tokens instead.)
DEDUPE_SIDECAR = re.compile(
    r"(^|/)dedupe_settings[^/]*/(?:[^/]+/)?(dedupe_dataframe_learned_settings|dedupe_dataframe_training\.json)$")
_RESTRICTED_SOURCE_TOKENS = (b"gvkey", b"lpermno", b"permno", b"xi_real", b"xi_nominal",
                             b"orig_assignee", b"compustat", b"billedamt", b"paidamt",
                             b"proc_count", b"n_claims", b"marketscan", b"coinsurance")

def is_restricted(col):
    c=col.lower().strip()
    if c in ("year","firm_expansion"): return False
    if c=="xi": return True
    return any(k in c for k in RESTR_SUBSTR)

def read_tabular_full(p):
    """Read a tabular file of ANY supported type IN FULL (values, not just headers).
    Raises on any failure -- the caller MUST treat an exception as a hard failure
    (fail-closed), never a silent skip. Values are read as text so nothing is
    coerced/dropped before scanning."""
    lp=p.lower()
    if lp.endswith(".parquet"): return pd.read_parquet(p)
    if lp.endswith(".feather"): return pd.read_feather(p)
    if lp.endswith((".xlsx",".xls")): return pd.read_excel(p, dtype=str)
    if lp.endswith(".dta"): return pd.read_stata(p)
    if lp.endswith(".sas7bdat"): return pd.read_sas(p)
    if lp.endswith(".json"):
        try:
            return pd.read_json(p, dtype=str)
        except Exception:
            # Irregular/large JSON (e.g. the openFDA recall dump {meta, results:[...]}, which
            # pd.read_json rejects with "Mixing dicts"): read it as raw text so every byte is still
            # exposed to the restricted-value scan (fail-closed), without needing the exact schema.
            with open(p, encoding="latin-1") as fh:
                return pd.DataFrame({"_rawtext": fh.read().splitlines() or [""]})
    if lp.endswith((".pkl",".pickle")): return pd.read_pickle(p)
    # Delimited text. The goal is to READ THE FULL CONTENT for restricted-value scanning, not to
    # recover the exact schema -- so try the plausible delimiters and both encodings, and if every
    # structured parse fails (irregular/quoted public FDA dumps: MAUDE masterevent/patient/device_data,
    # PMA approvals, recall, foiclass), fall back to reading every line as a single raw column. That
    # still exposes every byte to the value scan (fail-closed: content is always inspected, never
    # skipped) even when the file is not cleanly rectangular.
    seps = ["\t"] if lp.endswith(".tsv") else [",", "|", "\t"]
    for enc in (None, "latin-1"):
        for trysep in seps:
            try:
                return pd.read_csv(p, dtype=str, keep_default_na=False, sep=trysep,
                                   engine="python", encoding=enc)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    with open(p, encoding="latin-1") as fh:
        return pd.DataFrame({"_rawtext": fh.read().splitlines()})

def scan_values(df):
    """Return (col, sample) for any column whose CELL VALUES contain a restricted
    marker -- catches restricted content hidden under an innocuous header."""
    hits=[]
    for c in df.columns:
        s=df[c].astype(str)
        m=s.str.contains(VALUE_MARKERS, na=False, regex=True)
        if bool(m.any()):
            hits.append((str(c), s[m].iloc[0][:60]))
    return hits

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as fh:
        for b in iter(lambda: fh.read(1<<20), b""): h.update(b)
    return h.hexdigest()

def fail(msg): print(f"SANITIZER FAILURE: {msg}", file=sys.stderr); sys.exit(2)

def main(root):
    rep=[]
    # 1. apply schemas (FAIL on missing schema target)
    for rel, schema in PUBLIC_SCHEMAS.items():
        p=os.path.join(root, rel)
        if not os.path.exists(p): fail(f"expected schema target missing: {rel}")
        pre=sha(p); n0=sum(1 for _ in open(p))-1
        df=pd.read_csv(p, dtype=str, keep_default_na=False)   # literal-preserve
        before=list(df.columns)
        missing=[c for c in schema if c not in before]
        if missing: fail(f"{rel}: schema columns absent from file: {missing}")
        keep=[c for c in before if c in schema]
        dropped=[c for c in before if c not in schema]
        out=df[keep]
        # validate: no restricted column survives + row count preserved
        bad=[c for c in keep if is_restricted(c)]
        if bad: fail(f"{rel}: restricted columns in declared schema: {bad}")
        out.to_csv(p, index=False)
        n1=sum(1 for _ in open(p))-1
        if n1!=n0: fail(f"{rel}: row count changed {n0}->{n1}")
        rep.append([rel,n1,len(before),len(keep),len(dropped),"|".join(dropped),pre,sha(p)])
    # 2. classify EVERY other file under data/ (FAIL-CLOSED). Walk the whole tree
    #    case-insensitively -- not just lowercase *.csv/*.parquet. For each shipping
    #    file: a tabular file MUST be readable in full and free of restricted
    #    columns AND restricted cell-values; an unreadable tabular file, an
    #    unknown/unsupported extension, or a symlink is a HARD FAILURE (never a
    #    silent skip). Non-tabular sidecars are allowlisted by extension so they
    #    are accounted for rather than ignored.
    schema_rels=set(PUBLIC_SCHEMAS)
    unclassified=[]; n_scanned=0; n_sidecar=0
    data_root=os.path.join(root,"data")
    for dp,dirs,names in os.walk(data_root, followlinks=False):
        # a symlinked directory could resolve outside the package -> fail
        for d in dirs:
            if os.path.islink(os.path.join(dp,d)):
                fail(f"symlinked directory under data/: {os.path.relpath(os.path.join(dp,d),root)}")
        for name in names:
            full=os.path.join(dp,name); rel=os.path.relpath(full,root)
            if os.path.islink(full):
                fail(f"symlinked file under data/ (would dereference to external bytes): {rel}")
            if rel in schema_rels or rel in PUBLIC_OK:
                continue
            low=name.lower()
            if low.endswith(NONTABULAR_OK_EXTS):
                # F4: a sidecar accepted by extension must actually BE that format (magic/UTF-8), else it
                # could be an opaque restricted payload hidden under an innocuous extension.
                reason = verify_sidecar_format(full, low)
                if reason:
                    fail(f"non-tabular sidecar FORMAT MISMATCH ({rel}): {reason}")
                n_sidecar+=1; continue
            if DEDUPE_SIDECAR.search(rel.replace(os.sep, "/")):
                # VERIFY (not skip) the extensionless dedup model + its training JSON: scan raw bytes
                # for any restricted-SOURCE identifier; abort fail-closed if one appears.
                with open(full, "rb") as fh:
                    raw = fh.read().lower()
                hit = sorted({t.decode() for t in _RESTRICTED_SOURCE_TOKENS if t in raw})
                if hit:
                    fail(f"pandas_dedupe sidecar carries restricted-source token(s) {hit[:5]}: {rel}")
                n_sidecar+=1; continue
            if not low.endswith(TABULAR_EXTS):
                fail(f"UNKNOWN file type under data/ (cannot verify it carries no restricted data): {rel}")
            # tabular -> MUST read in full; an exception is fail-closed, not a skip
            try:
                df=read_tabular_full(full)
            except Exception as e:
                fail(f"tabular file could not be read for scanning (fail-closed): {rel}: {type(e).__name__}: {e}")
            n_scanned+=1
            r=[c for c in df.columns if is_restricted(str(c))]
            v=scan_values(df)
            if r or v:
                unclassified.append((rel, r, v))
    if unclassified:
        for rel,r,v in unclassified:
            if r: print(f"  RESTRICTED COLUMN(S) in {rel}: {r[:6]}", file=sys.stderr)
            if v: print(f"  RESTRICTED VALUE(S) in {rel}: {v[:3]}", file=sys.stderr)
        fail(f"{len(unclassified)} shipping file(s) carry restricted columns/values but are not schema-handled or excluded")
    print(f"  classified {n_scanned} tabular file(s) (full read + value scan) and "
          f"{n_sidecar} non-tabular sidecar(s); 0 restricted columns/values found.")
    # 3. report
    repp=os.path.join(root,"certification","SANITIZER_REPORT.csv")
    os.makedirs(os.path.dirname(repp), exist_ok=True)
    with open(repp,"w",newline="") as fh:
        w=csv.writer(fh)
        w.writerow(["file","rows","cols_before","cols_after","cols_dropped","dropped_columns","sha256_before","sha256_after"])
        w.writerows(rep)
    print(f"OK: sanitized {len(rep)} schema panel(s); all other shipping data files verified free of restricted columns AND values (full read, case-insensitive, fail-closed).")
    for r in rep: print(f"  {r[0]}: {r[1]} rows, {r[2]}->{r[3]} cols (dropped {r[4]})")
    return 0

if __name__=="__main__":
    if len(sys.argv)<2: sys.exit("usage: sanitize_public_data.py <public_build_root>")
    sys.exit(main(sys.argv[1]))
