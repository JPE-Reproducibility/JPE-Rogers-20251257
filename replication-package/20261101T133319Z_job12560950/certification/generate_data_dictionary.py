#!/usr/bin/env python3
"""generate_data_dictionary.py -- machine-readable PER-COLUMN metadata (JPE 1.5) for the synthetic tree.

The deposit already ships a narrative codebook (`CODEBOOK.md`, variable schemes) and a file-level
manifest (`data_input_manifest.csv`), which satisfy the JPE 1.5 metadata requirement. This adds a
per-COLUMN data dictionary over every synthetic file so a reviewer has a column-level schema without
opening each CSV: for each (file, column) it records the dtype, the non-null rate, and the column's
PRIVACY CLASS (public / synthetic-value / merge-key-id / scrambled-identity / derived), reusing the
exact classification regexes from `audit_simulated_data.py` so the dictionary can never disagree with
what the leakage/structure audit enforces.

Output: certification/DATA_DICTIONARY.csv with JPE 1.5 per-column metadata:
  file, column, dtype, description, units, non_null_pct, n_missing, missing_meaning,
  n_unique, allowed_values_or_range, class
Stats are computed over the FULL column (not a sample) so ranges/allowed values are exact.
Run any time (reads only the synthetic tree; no real data needed). Deterministic.

FAIL-CLOSED INVENTORY CHECK (added 2026-09-17): the set of files the dictionary covers must equal
the reviewed payload inventory in certification/regen_determinism/simulated_data_expected_files.txt,
exactly. Previously this script simply described whatever happened to be on disk, so a stale tree
produced a stale dictionary that still passed the build gate -- the shipped copy documented a
retired file and omitted two live ones while the README claimed it "always reflects the exact
package's inventory". A set-difference in either direction now exits non-zero.
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIM = os.path.join(ROOT, "synthetic_pipeline", "simulated_data")
sys.path.insert(0, os.path.join(ROOT, "synthetic_pipeline"))
import audit_simulated_data as A            # reuse the audit's column-class regexes (single source of truth)


def _classify(col):
    """Map a column to its privacy class using the SAME regexes the audit enforces.
    Returns (class, description). The description doubles as the JPE 1.5 variable description."""
    c = str(col)
    if A.PATENT_ID.match(c):
        return "merge-key-id:patent", "De-identified synthetic patent number (fake domain >= 90,000,000); merge key across patent files."
    if A.LINK_ID.match(c):
        return "merge-key-id:firm", "Firm link id mapped to a consistent fake value (>= 1,000,000); links firm-level synthetic records. Public entity."
    if A.PUBLIC.match(c):
        return "public", "Public FDA / Federal-Register / CPT-CPC / calendar value, kept at its real public value by design."
    if A.DERIVED_COL.match(c):
        return "derived", "Deterministic function of the synthetic patents and public controls (not an independent draw)."
    if A.IDENTITY_SCRAMBLE.search(c):
        return "scrambled-identity", "Firm / assignee / inventor / GRID identity, independently resampled so real co-membership is broken."
    return "synthetic-value", "Restricted outcome value replaced by a randomized synthetic draw (no real value retained)."


def _missing_meaning(cls):
    return {
        "public": "NaN where the public design carries no value for that row (e.g., control / never-reclassified device types).",
        "derived": "NaN where the underlying synthetic patents/controls have no value to derive from.",
        "synthetic-value": "NaN drawn at the committed synthetic missingness rate (structural, not a real missing pattern).",
        "scrambled-identity": "NaN where the resampled partition assigns no entity.",
        "merge-key-id:patent": "NaN where no patent is linked on that row.",
        "merge-key-id:firm": "NaN where no firm is linked on that row.",
    }.get(cls, "NaN meaning follows the column class.")


def _units(col):
    c = str(col).lower()
    if re.search(r"(^|_)(year|yr|fyear)($|_)|datadate|reclass_year|year_", c):
        return "calendar year"
    if re.search(r"amount|paid|billed|value|cost|price|payment|assets|_2019m|usd|dollar|xi_", c):
        return "USD"
    if re.search(r"pct|percent|share|_rate|ratio", c):
        return "share / ratio"
    if re.search(r"count|num|patents|events|reports|claims|enrollees|_size|n_", c):
        return "count"
    return ""


def _coarse_number(value):
    """Two-significant-figure display for synthetic metadata, never an exact extremum."""
    value = float(value)
    if not np.isfinite(value) or value == 0:
        return "0"
    digits = 1 - int(np.floor(np.log10(abs(value))))
    return f"{round(value, digits):g}"


def _allowed_or_range(s, cls):
    """Public values may be exact; synthetic metadata is deliberately coarse."""
    v = s.dropna()
    if not len(v):
        return ""
    if cls == "merge-key-id:patent":
        return "synthetic identifier domain >= 90,000,000"
    if cls == "merge-key-id:firm":
        return "synthetic identifier domain >= 1,000,000"
    if pd.api.types.is_numeric_dtype(s):
        try:
            if cls == "public":
                return f"[{v.min():g}, {v.max():g}]"
            return f"approximate synthetic support [{_coarse_number(v.min())}, {_coarse_number(v.max())}]"
        except (TypeError, ValueError):
            return ""
    u = pd.Index(v.astype(str)).unique()
    if cls != "public":
        return f"{len(u)} synthetic categories (values not enumerated)"
    if len(u) <= 20:
        return "{" + ", ".join(sorted(u)[:20]) + "}"
    ex = "; ".join(sorted(u)[:5])
    return f"{len(u)} distinct; e.g. {ex}"


def _read_full(path):
    lp = path.lower()
    if lp.endswith(".parquet"):
        return pd.read_parquet(path)
    if lp.endswith(".xlsx"):
        return pd.read_excel(path)
    return pd.read_csv(path, low_memory=False)


def main():
    # No options: refuse anything on the command line rather than silently starting a run that
    # rewrites certification/DATA_DICTIONARY.csv (the generator reads the whole simulated payload).
    if len(sys.argv) > 1:
        print("usage: generate_data_dictionary.py  (no arguments; rebuilds certification/DATA_DICTIONARY.csv "
              "from synthetic_pipeline/simulated_data/)")
        return 0 if sys.argv[1] in ("-h", "--help") else 2
    if not os.path.isdir(SIM):
        print(f"FATAL: simulated_data/ not found at {SIM} -- run the generators first."); return 1
    rows = []
    cols_out = ["file", "column", "dtype", "description", "units", "non_null_pct",
                "n_missing", "missing_meaning", "n_unique", "allowed_values_or_range", "class"]
    files = sorted(glob.glob(os.path.join(SIM, "**", "*"), recursive=True))
    n_files = 0
    for p in files:
        if os.path.isdir(p) or not p.lower().endswith((".csv", ".parquet", ".xlsx")):
            continue
        rel = os.path.relpath(p, SIM).replace(os.sep, "/")
        try:
            df = _read_full(p)                              # FULL column stats (exact ranges/allowed values)
        except Exception as e:                              # noqa: BLE001
            rows.append((rel, "<unreadable>", "", f"{type(e).__name__}: {e}", "", "", "", "", "", "", "error"))
            continue
        n_files += 1
        n_rows = len(df)
        for col in df.columns:
            s = df[col]
            dtype = str(s.dtype)
            nn = float(s.notna().mean()) * 100.0 if n_rows else 0.0
            n_missing = int(s.isna().sum())
            cls, desc = _classify(col)
            rows.append((rel, str(col), dtype, desc, _units(col), f"{nn:.1f}",
                         n_missing, _missing_meaning(cls), int(s.nunique(dropna=True)),
                         _allowed_or_range(s, cls), cls))

    # Fail closed BEFORE writing: the dictionary must cover exactly the reviewed payload inventory.
    covered = {r[0] for r in rows}
    inventory_path = os.path.join(HERE, "regen_determinism", "simulated_data_expected_files.txt")
    if not os.path.isfile(inventory_path):
        print(f"FATAL: reviewed payload inventory not found: {inventory_path}")
        return 1
    expected = set()
    prefix = "simulated_data/"
    for line in open(inventory_path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        expected.add(line[len(prefix):] if line.startswith(prefix) else line)
    missing = sorted(expected - covered)
    extra = sorted(covered - expected)
    if missing or extra:
        print("FATAL: DATA_DICTIONARY would not match the reviewed payload inventory "
              f"({os.path.relpath(inventory_path, ROOT)}).")
        for rel in missing:
            print(f"  in the reviewed inventory but NOT documented: {rel}")
        for rel in extra:
            print(f"  documented but NOT in the reviewed inventory: {rel}")
        print("  Regenerate synthetic_pipeline/simulated_data/ with "
              "synthetic_pipeline/build_simulation.py, or update the inventory, before rerunning.")
        return 1

    out = os.path.join(HERE, "DATA_DICTIONARY.csv")
    dd = pd.DataFrame(rows, columns=cols_out)
    dd.to_csv(out, index=False)
    by = dd["class"].value_counts()
    print(f"Per-column data dictionary (JPE 1.5, full-column stats): {n_files} synthetic files "
          f"/ {len(dd):,} columns -> {out}")
    print(f"  file set == the reviewed {len(expected)}-file payload inventory (exact).")
    for cls, n in by.items():
        print(f"  {cls:22s} {n:>5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
