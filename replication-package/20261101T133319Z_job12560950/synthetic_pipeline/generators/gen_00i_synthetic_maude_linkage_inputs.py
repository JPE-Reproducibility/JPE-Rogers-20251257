#!/usr/bin/env python3
"""Build synthetic raw inputs for the MAUDE manufacturer-to-firm linkage.

This Stage-B generator consumes only the already-synthetic adverse-event linkage
view made by gen_00d. It converts that view into raw-shaped synthetic inputs
that the synthetic branch of gen_07 joins deterministically. The precomputed
derived linkage is then removed, forcing the certified from-raw route to execute
gen_07 rather than reuse a frozen restricted-derived stand-in.

Outputs
-------
All_Adverse_Event_Manufacturers.csv             -> data/raw/MAUDE/
all_permnos_fname_adverse_events_oct22_24.csv   -> data/raw/MAUDE/
manual_permno_corrections.csv                   -> data/raw/

The third is a synthetic twin of a RESTRICTED file. The real
`data/raw/manual_permno_corrections.csv` is the author's hand-coded
manufacturer-name -> CRSP PERMNO crosswalk; CRSP PERMNO is proprietary, so the real
file is excluded from the deposit. Without a twin the simulated-data route had no
`data/raw/manual_permno_corrections.csv` at all, and step 35
(15_intext_derived_numbers.py) recorded its `maude_handlinked_manufacturers` scalar as
a MISSING INPUT -- which fails the strict in-text gate on BOTH routes.

The twin reproduces the real file's HEADER, its column dtypes and its row count, and
nothing else: every name in it is a synthetic manufacturer name this generator itself
produces, and every PERMNO is drawn from the synthetic PERMNO domain (the same
26,000-value domain that backs `compustat_firm_data.csv`). Each row is fully populated
by the fixed public rule documented at MANUAL_CORRECTION_LIST_ROWS below; the real file's
per-column fill pattern is NOT reproduced and no count taken from it appears here. The
70-row count is the public figure the README and WRDS_EXTRACTION_ROADMAP.md already state
(and that gen_07's own docstring names), not a measurement made for this generator. No
real value was read or retained -- only the real file's header line and a dtype probe were
inspected to write this.

gen_07's SYNTHETIC branch does not read the crosswalk (it short-circuits to
_generate_synthetic before _load_manual_corrections is ever called), so the twin changes
nothing about how the simulated linkage is built. It exists so the simulated route can
compute the same registered in-text scalar the real route does.
"""
import csv
import json
import os
from pathlib import Path

import pandas as pd

import synthetic_paths


INTERNAL = synthetic_paths.internal_dir()
SOURCE = INTERNAL / "synthetic_dimensions_wrds" / "all_adv_events_w_permno5.csv"
OUT = INTERNAL / "synthetic_maude_linkage"
MANUFACTURERS = OUT / "All_Adverse_Event_Manufacturers.csv"
FIRMS = OUT / "all_permnos_fname_adverse_events_oct22_24.csv"
MANUAL_CORRECTIONS = OUT / "manual_permno_corrections.csv"

# The real crosswalk's header, in order. `contains` holds a JSON-encoded pattern (a string,
# or a list of strings that must all appear); gen_07's _load_manual_corrections calls
# json.loads on it, so the twin must be JSON too.
MANUAL_CORRECTION_COLS = ["contains", "not_contains", "permno", "stock_name",
                          "manual_stock", "no_guard", "undo"]
# 70 hand-coded corrections. This is the PUBLIC count: README.md and WRDS_EXTRACTION_ROADMAP.md
# both state it, and code/00_generate_data/gen_07_adverse_permno.py's own docstring names it. It is
# not a measurement taken from the restricted file for this generator's benefit.
MANUAL_CORRECTION_ROWS = 70          # 70 data rows (71 lines with the header)
# FILL RULE (fixed, public, and deliberately NOT the real file's). Every cell of every column is
# populated, so the twin encodes no per-column fill count from the restricted crosswalk. Two
# columns still need a literal chosen with care to keep the dtypes the real file has on read:
#   * `permno` and `manual_stock` must read as float64  -> numeric literals;
#   * `no_guard` and `undo` must read as object         -> a NON-boolean, NON-numeric truthy
#     token, because a column of "TRUE" alone is inferred as bool and a column of "1" as float64.
#     gen_07's parser treats any non-empty cell as True (`if row.get("no_guard")`), so the token's
#     spelling is irrelevant to it.
MANUAL_CORRECTION_FLAG_TOKEN = "Y"
# `contains` fill rule: every tenth row (0, 10, ... 60) holds a two-element pattern and row 5 holds
# a one-element list; the remaining 62 rows hold a plain JSON string. This exercises both of
# gen_07's json.loads branches (string and list) without reference to the real file's mix.
MANUAL_CORRECTION_LIST_ROWS = {i: 2 for i in range(0, MANUAL_CORRECTION_ROWS, 10)}
MANUAL_CORRECTION_LIST_ROWS[5] = 1                                # row index -> list length


def _firm_name(permno):
    value = pd.to_numeric(permno, errors="coerce")
    if pd.isna(value):
        return None
    return f"SYNTHETIC FIRM {int(value)}"


def write_manual_permno_corrections(permnos):
    """Write the synthetic twin of the restricted manufacturer -> PERMNO crosswalk.

    `permnos` is the synthetic PERMNO domain this generator has just seen in the synthetic
    adverse-event linkage -- the same domain compustat_firm_data.csv uses. Selection is a
    fixed stride over that sorted domain and every cell is populated by the fixed public rule
    documented at the top of this module, so the writer draws no random numbers at all and two
    clean generations produce byte-identical output.
    """
    ordered = sorted(int(p) for p in permnos)
    if len(ordered) < MANUAL_CORRECTION_ROWS:
        raise SystemExit(
            f"gen_00i: only {len(ordered)} synthetic PERMNOs available; the manual-corrections "
            f"twin needs {MANUAL_CORRECTION_ROWS}.")
    stride = len(ordered) // MANUAL_CORRECTION_ROWS
    chosen = [ordered[i * stride] for i in range(MANUAL_CORRECTION_ROWS)]

    rows = []
    for i, permno in enumerate(chosen):
        name = _firm_name(permno)
        list_len = MANUAL_CORRECTION_LIST_ROWS.get(i)
        if list_len == 2:
            contains = json.dumps([name, "SYNTHETIC"])
        elif list_len == 1:
            contains = json.dumps([name])
        else:
            contains = json.dumps(name)
        rows.append({
            "contains": contains,
            "not_contains": "SYNTHETIC UNMATCHED",
            "permno": f"{float(permno):.1f}",
            "stock_name": name,
            "manual_stock": "1.0",
            # See MANUAL_CORRECTION_FLAG_TOKEN: a non-boolean, non-numeric truthy token keeps
            # these two columns object-typed on read (all-"TRUE" would be inferred as bool, all-"1"
            # as float64) while gen_07 still reads them as True.
            "no_guard": MANUAL_CORRECTION_FLAG_TOKEN,
            "undo": MANUAL_CORRECTION_FLAG_TOKEN,
        })

    with open(MANUAL_CORRECTIONS, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANUAL_CORRECTION_COLS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"gen_00i: wrote {MANUAL_CORRECTIONS.name}: {len(rows)} synthetic hand-linked "
          f"manufacturer patterns (synthetic firm names; PERMNOs from the synthetic domain)")


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"gen_00i: required synthetic source is missing: {SOURCE}")
    if OUT.exists():
        raise SystemExit(f"gen_00i: refusing to reuse existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    tmp = MANUFACTURERS.with_suffix(".csv.tmp")
    permnos = set()
    wrote_header = False
    rows = 0
    for chunk in pd.read_csv(
        SOURCE,
        usecols=["MDR_REPORT_KEY", "permno"],
        chunksize=500_000,
        low_memory=False,
    ):
        numeric = pd.to_numeric(chunk["permno"], errors="coerce")
        permnos.update(numeric.dropna().astype("int64").tolist())
        names = numeric.map(_firm_name)
        missing = names.isna()
        names.loc[missing] = (
            "SYNTHETIC UNMATCHED "
            + chunk.loc[missing, "MDR_REPORT_KEY"].astype(str)
        )
        out = pd.DataFrame({
            "MDR_REPORT_KEY": chunk["MDR_REPORT_KEY"],
            "MANUFACTURER_D_NAME": names,
        })
        out.to_csv(tmp, mode="a", header=not wrote_header, index=False)
        wrote_header = True
        rows += len(out)

    firms = pd.DataFrame({"permno": sorted(permnos)})
    firms["firm_name"] = firms["permno"].map(_firm_name)
    firms.to_csv(FIRMS, index=False)
    os.replace(tmp, MANUFACTURERS)
    write_manual_permno_corrections(permnos)
    SOURCE.unlink()

    print(f"gen_00i: wrote {MANUFACTURERS.name}: {rows:,} rows")
    print(f"gen_00i: wrote {FIRMS.name}: {len(firms):,} firms")
    print("gen_00i: removed the precomputed derived linkage; gen_07 must recreate it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
