#!/usr/bin/env python3
"""Actual-payload contract validator (fully fail-closed).

Cross-checks the SHIPPED synthetic payload against the committed schema contract on EVERY structural
dimension, so a committed contract can never silently disagree with the bytes that ship:

  * EXACT file set per section (no extra, no missing) -- marketscan_files -> synthetic_marketscan/,
    nexis_files -> synthetic_nexis/;
  * row count == committed rows;
  * ordered column list == committed columns;
  * column kind == committed column_kinds (the shipped dtype/format must match the real committed
    schema: a real date column ships as a genuine date, a real numeric column as a genuine numeric, a
    real coded-string column as a genuine string -- the ONLY tolerated divergence is the
    integer<->number numeric family, a CSV-format artifact: a whole-number column round-trips as
    float64 the instant one cell is NaN, which is not a generator defect);
  * file format == committed format;
  * per-column cardinality == the shipped distinct-count, and cardinality <= rows.

Root cause it guards (independent audit, 2026-09-02): the coarsening could round a distinct-count up
past the row count, whereupon the generator silently clamped -> contract != payload. The generator now
caps + fails closed; this is the independent actual-payload cross-check that the two agree.

Root cause the KIND check guards (independent audit, 2026-09-04): the generator was re-typing ~50 of
~1,124 MarketScan/Nexis columns (real date -> synthetic string; real string -> synthetic number; a
"COMPAN" substring match swallowing an unrelated "Company type" numeric column; a pure-digit synthetic
HCPCS code round-tripping through CSV as int64) and this validator's kind check existed but was never
called, so the mismatch shipped undetected. The generator now preserves each column's real kind; this
check is the independent fail-closed proof that it does, for every column, every run.

Run from the package root:  python3 certification/validate_payload_contract.py
Exit 0 on full agreement, 1 on any disagreement, 2 on a setup error.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
# Reuse the contract generator's kind/reader so the validator's inference matches how the contract
# itself was built (single source of truth for _kind and _read).
from generate_simulation_schema_contract import _kind, _read  # noqa: E402

ROOT = _HERE.parent
CONTRACT = ROOT / "synthetic_pipeline" / "_synthetic_source_internal" / "simulation_schema_contract.json"
SIM = ROOT / "synthetic_pipeline" / "simulated_data"
SECTIONS = {"marketscan_files": "synthetic_marketscan", "nexis_files": "synthetic_nexis"}


def _kinds_compatible(contract_kind: str, payload_kind: str) -> bool:
    """The committed kind describes the REAL column and the synthetic payload must ship the SAME
    kind -- JPE's confidential.html column-type-fidelity requirement (values stay fake; type/format
    is metadata, not a privacy leak). The one tolerated divergence is the integer<->number numeric
    family: a whole-number CSV column round-trips as float64 the instant any cell is NaN (CSV has no
    int-with-NaN representation), which is a CSV format limitation, not a generator defect. Every
    other kind change -- including a committed date/number/integer column shipping as a bare string,
    or a committed string column shipping as a number -- is a real re-typing defect and fails."""
    if contract_kind == payload_kind:
        return True
    if {contract_kind, payload_kind} <= {"integer", "number"}:
        return True
    return False


def main() -> int:
    if not CONTRACT.is_file():
        print(f"FATAL: committed contract not found: {CONTRACT}")
        return 2
    if not SIM.is_dir():
        print(f"FATAL: shipped simulated_data not found: {SIM} (run the generators first)")
        return 2
    contract = json.loads(CONTRACT.read_text())
    problems: list[str] = []
    n_files = 0
    n_cards = 0
    n_kinds = 0

    for section, sub in SECTIONS.items():
        base = SIM / sub
        spec_files = contract.get(section, {})
        expected = set(spec_files.keys())
        actual = set()
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    actual.add(p.relative_to(base).as_posix())
        for extra in sorted(actual - expected):
            problems.append(f"[{section}] payload file NOT in contract: {extra}")
        for miss in sorted(expected - actual):
            problems.append(f"[{section}] contract file MISSING from payload: {miss}")

        for rel, spec in spec_files.items():
            p = base / rel
            if not p.is_file():
                continue  # already reported as missing
            n_files += 1
            rows = int(spec.get("rows", -1))
            fmt = p.suffix.lower().lstrip(".")
            if fmt != spec.get("format"):
                problems.append(f"[{section}] {rel}: format {fmt!r} != committed {spec.get('format')!r}")
            try:
                frame = _read(p)
            except Exception as e:  # noqa: BLE001
                problems.append(f"[{section}] {rel}: unreadable payload ({e})")
                continue
            if len(frame) != rows:
                problems.append(f"[{section}] {rel}: rows {len(frame)} != committed {rows}")
            if list(frame.columns) != list(spec.get("columns", [])):
                problems.append(f"[{section}] {rel}: ordered column list differs from committed contract")
            # Column KIND fidelity: the shipped dtype must match the committed real column_kinds (see
            # _kinds_compatible above for the one tolerated CSV-format exception). Checked by column
            # name (not shipped order), so this fires independently of the ordered-column-list check.
            for col, expected_kind in (spec.get("column_kinds") or {}).items():
                if col not in frame.columns:
                    continue  # already reported via the ordered-column-list / missing-column checks
                n_kinds += 1
                actual_kind = _kind(frame[col].dtype)
                if not _kinds_compatible(expected_kind, actual_kind):
                    problems.append(
                        f"[{section}] {rel}:{col}: shipped kind {actual_kind!r} incompatible with "
                        f"committed kind {expected_kind!r}"
                    )
            for col, card in (spec.get("cardinalities") or {}).items():
                n_cards += 1
                card = int(card)
                if card > rows:
                    problems.append(f"[{section}] {rel}:{col}: committed cardinality {card} > rows {rows} (impossible)")
                if col not in frame.columns:
                    problems.append(f"[{section}] {rel}:{col}: committed cardinality but column absent from payload")
                    continue
                actual_nu = int(frame[col].dropna().nunique())
                if actual_nu != card:
                    problems.append(f"[{section}] {rel}:{col}: shipped distinct {actual_nu} != committed cardinality {card}")

    if problems:
        print("FAIL -- payload/contract disagreements:")
        for pr in problems[:50]:
            print(f"  {pr}")
        if len(problems) > 50:
            print(f"  ... and {len(problems) - 50} more")
        print(f"  ({len(problems)} problem(s); {n_files} files, {n_kinds} kinds, "
              f"{n_cards} cardinalities checked)")
        return 1
    print(f"PASS -- {n_files} shipped files match the committed contract on file-set, rows, ordered "
          f"columns, kinds, format, and cardinalities ({n_kinds} kinds, {n_cards} cardinalities checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
