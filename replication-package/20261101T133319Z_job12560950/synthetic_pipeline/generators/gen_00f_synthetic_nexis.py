"""
gen_00f_synthetic_nexis.py -- Phase 4 synthetic Nexis Uni / LexisNexis Liability files.

Synthesizes the legal Results-list exports that `11c_liability.py` reads to build the
liability / preemption / bankruptcy trends (Fig D.9/D.10). Design:

- MATCH structure: exact per-file dimensions, names, coarse types, and formats come
  from the disclosure-reviewed committed structural contract.
- SYNTHESIZE the Nexis-pulled text: CASE NAME, CITE, SUMMARY, COURT, DATE DECIDED, and
  the GPT summary/response columns -> synthetic placeholder legal strings.
- RANDOMIZE the coded flags (Class / Device / Preempted -> 0/1).

Writes each file back in its original format (.xlsx for the Results lists 11c reads, plus
the .csv mirrors and the encoding CSVs). Outputs to
confidential-data-not-for-publication/synthetic_nexis/. Deterministic (seeded).
"""
import datetime
import os
import re
import json
import shutil
import zipfile
import numpy as np
import pandas as pd

# Deterministic .xlsx writing --------------------------------------------------------------------
# pandas/openpyxl embed the current wall-clock time in docProps/core.xml (created/modified) and in
# each zip entry's mtime, so two identical runs produce byte-DIFFERENT .xlsx. JPE confidential.html
# step 3 requires the simulated data to be EXACTLY reproducible, so both are normalised: a fixed doc
# timestamp + a fixed zip entry date + sorted members + fixed compression -> byte-identical output.
_FIXED_TS = "2020-01-01T00:00:00Z"
_FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)


def _write_xlsx_deterministic(df, outp):
    """Write df to outp as a byte-deterministic .xlsx (no embedded wall-clock time)."""
    df.to_excel(outp, index=False, engine="openpyxl")
    with zipfile.ZipFile(outp, "r") as zin:
        members = {name: zin.read(name) for name in zin.namelist()}
    core = "docProps/core.xml"
    if core in members:
        txt = members[core].decode("utf-8")
        txt = re.sub(r"(<dcterms:created[^>]*>)[^<]*(</dcterms:created>)",
                     r"\g<1>%s\g<2>" % _FIXED_TS, txt)
        txt = re.sub(r"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)",
                     r"\g<1>%s\g<2>" % _FIXED_TS, txt)
        members[core] = txt.encode("utf-8")
    with zipfile.ZipFile(outp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in sorted(members):
            zi = zipfile.ZipInfo(name, date_time=_FIXED_ZIP_DT)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, members[name])

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if HERE not in os.sys.path:
    os.sys.path.insert(0, HERE)
import synthetic_paths
from synthetic_seed import seed
import independent_universe as iu
# Single source of truth for column KIND classification -- the SAME `_kind()` function
# certification/validate_payload_contract.py uses to cross-check the shipped payload against
# the committed contract. Importing it (rather than re-deriving the mapping) guarantees the
# generator's own kind-fidelity coercion below can never silently drift from the validator.
_CERT_DIR = os.path.join(ROOT, "certification")
if _CERT_DIR not in os.sys.path:
    os.sys.path.insert(0, _CERT_DIR)
from generate_simulation_schema_contract import _kind as _contract_kind

INTERNAL = str(synthetic_paths.internal_dir())
OUT = os.path.join(INTERNAL, "synthetic_nexis")
SCHEMA_CONTRACT = os.path.join(INTERNAL, "simulation_schema_contract.json")
SEED = seed(12345)

# FAIL-CLOSED + F3: keep NOTHING real. Two-significant-figure row approximations and exact
# column/type/format schemas are committed structural metadata, pending the Data Editor's written
# technical acceptance of the close-row design; YEAR is drawn within the filename's
# public period, JURISDICTION is a synthetic categorical, and every text column is synthesized. Only
# `YEAR` (tort: groupby-year count) and `CITE` (non-null, counted) and `Company` (medtech: distinct
# count) drive any figure, per the downstream data-flow map -- all satisfied synthetically.
PUBLIC_KEEP = re.compile(r"^(Unnamed.*|index)$", re.I)   # structural only -- NO real values kept
FLAG = re.compile(r"^(Class|Device|Preempted)$", re.I)

_COURTS = ["Synthetic District Court", "Synthetic Court of Appeals", "Synthetic Superior Court",
           "Synthetic Supreme Court", "Synthetic Circuit Court"]
_JURIS = ["Synthetic Federal", "Synthetic State A", "Synthetic State B", "Synthetic State C"]


def _period_from_name(basename):
    """Parse the YEAR period from the (public, structural) filename; default 1985-2007."""
    yrs = sorted(int(y) for y in re.findall(r"(19\d\d|20\d\d)", basename))
    if len(yrs) >= 2:
        return yrs[0], yrs[-1]
    if len(yrs) == 1:
        return yrs[0], yrs[0] + 5
    return 1985, 2007


def _synth_series(name, n, lo, hi, rng, kind="string"):
    """n SYNTHETIC values for column `name`, YEAR drawn within [lo, hi]."""
    c = str(name); cu = c.upper()
    if PUBLIC_KEEP.match(c):
        return np.arange(n)                               # structural index only
    if cu == "YEAR":
        return rng.integers(lo, hi + 1, size=n)           # within the filename's public period
    if FLAG.match(c):
        vals = rng.integers(0, 2, size=n)
        # Class/Device/Preempted ship as a STRING-kind column in some Nexis files (real cells were
        # coded as text) and as a numeric-kind column in others -- match whichever the committed
        # contract says instead of always emitting a float, or the payload kind flips against the
        # committed real kind (string<->number type mismatch). A "0"/"1" TEXT encoding does not
        # survive a CSV round-trip as a string: every value still parses as a plain integer, so
        # pd.read_csv (the same reader the contract/validator use) infers int64 right back -- use a
        # non-numeric-parseable token (Yes/No) so the column is unambiguously string on read-back.
        if kind == "string":
            return np.array(["Yes" if v else "No" for v in vals], dtype=object)
        return vals.astype(float)
    if cu == "CITE":                                       # counted (must be non-null)
        return np.array([f"{rng.integers(lo, hi+1)} SYN LEXIS {rng.integers(1,99999)}"
                         for _ in range(n)], dtype=object)
    if cu == "CASE NAME":
        return np.array([f"Synth{rng.integers(1000,9999)} v. Synth{rng.integers(1000,9999)}"
                         for _ in range(n)], dtype=object)
    if cu == "JURISDICTION":
        return rng.choice(_JURIS, size=n)                 # F3: synthetic (real jurisdiction not kept)
    if cu == "COURT":
        return rng.choice(_COURTS, size=n)
    if "DATE" in cu:
        # DATE DECIDED etc. are FREE (unused by 11c) -> draw over a WIDE range + full day precision so
        # synthetic dates don't chance-overlap the real dates in a narrow filename period. (The usual
        # DATE DECIDED column instead goes through the high-cardinality identity-column path below with
        # date_bounds=(lo, hi); this branch is the fallback for a date-kind/date-named column with too
        # few distinct real values to get a committed cardinality.) Emit real date objects when the
        # committed kind is "date" so the payload dtype matches; a "string"-kind date column (e.g. the
        # CSV twin of an xlsx date column) keeps the plain formatted-string representation.
        if kind == "date":
            return np.array([datetime.date(int(rng.integers(1970, 2021)), int(rng.integers(1, 13)),
                                            int(rng.integers(1, 29))) for _ in range(n)], dtype=object)
        return np.array([f"{rng.integers(1970,2021)}-{rng.integers(1,13):02d}-{rng.integers(1,29):02d}"
                         for _ in range(n)], dtype=object)
    if cu == "COMPANY":                                    # medtech: distinct-count signal -> many uniques
        return np.array([f"SYNCO {rng.integers(1,999999)} INC" for _ in range(n)], dtype=object)
    if kind == "integer":
        return rng.integers(0, 100_000, size=n)
    if kind == "number":
        return np.round(rng.uniform(0, 1_000_000, size=n), 3)
    tag = re.sub(r"[^a-z0-9]", "", c.lower())[:14] or "col"
    return np.array([f"synthetic_{tag}_{rng.integers(1,99999)}" for _ in range(n)], dtype=object)


def _coerce_to_contract_kinds(frame, kinds):
    """Final safety-net pass: force every column present in `kinds` (the committed schema
    contract's column_kinds) to actually carry that STRUCTURAL kind -- integer/number/date/
    string, per `_contract_kind()` (== certification/generate_simulation_schema_contract.py's
    `_kind()`, the same classifier certification/validate_payload_contract.py cross-checks the
    shipped payload against) -- regardless of how the column was built upstream. Only the DTYPE
    changes; every value stays synthetic. A column absent from `kinds` or from `frame` is left
    untouched, so this is safe to call with the full per-file column_kinds dict on any frame.
    """
    for col, kind in kinds.items():
        if col not in frame.columns:
            continue
        try:
            if kind == "string":
                frame[col] = frame[col].astype("string")
            elif kind == "integer":
                frame[col] = pd.to_numeric(frame[col], errors="raise").astype("Int64")
            elif kind == "number":
                frame[col] = pd.to_numeric(frame[col], errors="raise").astype(float)
            elif kind == "date":
                frame[col] = pd.to_datetime(frame[col])
            else:
                raise ValueError(f"unrecognized contract kind {kind!r}")
        except (ValueError, TypeError) as exc:
            raise SystemExit(
                f"_coerce_to_contract_kinds: cannot coerce column {col!r} to contract kind "
                f"{kind!r}: {exc}"
            ) from exc
        shipped = _contract_kind(frame[col].dtype)
        # Tolerate the same integer<->number CSV-NaN carve-out validate_payload_contract.py does
        # (a whole-number column round-trips as float64 the instant one cell is NaN); every other
        # disagreement means the coercion above did not actually reach the target kind.
        if shipped != kind and not ({shipped, kind} <= {"integer", "number"}):
            raise SystemExit(
                f"_coerce_to_contract_kinds: column {col!r} still kind {shipped!r} (dtype="
                f"{frame[col].dtype}) after coercing to contract kind {kind!r}"
            )
    return frame


def _load_contract():
    if not os.path.isfile(SCHEMA_CONTRACT):
        raise SystemExit(f"gen_00f: public schema contract missing: {SCHEMA_CONTRACT}")
    with open(SCHEMA_CONTRACT) as f:
        contract = json.load(f)
    specs = contract.get("nexis_files", {})
    if not specs:
        raise SystemExit("gen_00f: schema contract contains no Nexis files")
    for rel, spec in specs.items():
        if os.path.isabs(rel) or ".." in rel.split("/"):
            raise SystemExit(f"gen_00f: unsafe contract path: {rel}")
        if spec.get("format") not in {"csv", "xlsx"}:
            raise SystemExit(f"gen_00f: unsupported format for {rel}: {spec.get('format')}")
        cols = spec.get("columns", [])
        if not cols or set(cols) != set(spec.get("column_kinds", {})):
            raise SystemExit(f"gen_00f: invalid columns/kinds for {rel}")
        if int(spec.get("rows", 0)) <= 0:
            raise SystemExit(f"gen_00f: invalid contract row count for {rel}")
    return specs


def _frame(rel, spec):
    # Same-stem xlsx/csv pairs use the same seed and therefore the same values.
    stem = os.path.splitext(rel)[0]
    rng = np.random.default_rng(SEED + (sum(map(ord, stem)) % 9999))
    lo, hi = _period_from_name(os.path.basename(rel))
    n = int(spec["rows"])
    kinds = spec["column_kinds"]
    cards = spec.get("cardinalities", {})   # committed ROUNDED per-column distinct-counts (!= exact real)
    cols = {}
    for col in spec["columns"]:
        if col in cards:
            # High-cardinality column: draw via the independent-universe primitive so the synthetic
            # distinct-count == the committed ROUNDED cardinality (guaranteed != exact real) and the
            # group-size multiset comes from a smoothed family -- never the exact real multiset. Fully
            # populated (non-null), preserving the "counted" property CITE relies on. Uniform family =
            # max entropy (no size info disclosed). A committed "date" kind (the xlsx DATE DECIDED
            # column) draws fresh distinct calendar dates instead of string tokens, so the shipped
            # dtype matches the committed kind (kind fidelity is metadata, not a privacy leak).
            date_kw = {"date_bounds": (lo, hi)} if kinds[col] == "date" else {}
            cols[col] = iu.generate_identity_column(
                n, int(cards[col]), {"kind": "uniform"}, salt=f"nexis|{stem}|{col}", **date_kw)
        else:
            cols[col] = _synth_series(col, n, lo, hi, rng, kinds[col])
    df = pd.DataFrame(cols)
    # Final safety-net pass: force EVERY column to its contract-declared kind (not just "date"),
    # so the shipped dtype matches column_kinds regardless of which code path above produced it.
    # Both code paths above emit datetime.date objects for a "date"-kind column; the "date" branch
    # inside the coercion converts them to a real datetime64 dtype so to_excel writes a genuine
    # Excel date cell (kind fidelity) rather than a text cell. The CSV mirror (built by re-reading
    # this xlsx) serializes these as plain date strings, matching the CSV twin's own committed
    # "string" kind.
    df = _coerce_to_contract_kinds(df, kinds)
    return df


def _write(rel, df):
    outp = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    if rel.lower().endswith(".xlsx"):
        _write_xlsx_deterministic(df, outp)
    else:
        df.to_csv(outp, index=False)
    print(f"  wrote {rel[:60]:<60} ({len(df):>6,} rows)")


def main():
    specs = _load_contract()
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for rel in sorted(specs):
        if rel in written:
            continue
        stem, ext = os.path.splitext(rel)
        if ext.lower() == ".xlsx" and stem + ".csv" in specs:
            df = _frame(rel, specs[rel])
            _write(rel, df)
            # The CSV is a direct serialization of the deterministic workbook.
            csv_rel = stem + ".csv"
            csv_path = os.path.join(OUT, csv_rel)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            with open(csv_path, "w", newline="") as fh:
                fh.write(pd.read_excel(os.path.join(OUT, rel)).to_csv(index=False))
            print(f"  wrote {csv_rel[:60]:<60} ({len(df):>6,} rows; xlsx mirror)")
            written.update({rel, csv_rel})
            continue
        _write(rel, _frame(rel, specs[rel]))
        written.add(rel)
    expected = set(specs)
    actual = {
        os.path.relpath(os.path.join(dp, f), OUT).replace(os.sep, "/")
        for dp, _, fs in os.walk(OUT) for f in fs
    }
    if actual != expected:
        raise SystemExit(
            f"gen_00f: generated file-set drift; missing={sorted(expected-actual)}, "
            f"extra={sorted(actual-expected)}"
        )
    print(f"  -> {OUT}  ({len(actual)} contract-defined synthetic files; no licensed schema read)")


if __name__ == "__main__":
    main()
