#!/usr/bin/env python3
"""Fail-closed verification of the machine-generated manuscript-scalar report."""
import argparse
import csv
import math
from pathlib import Path


def load_inventory(path):
    names = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value and not value.startswith("#"):
            names.append(value)
    if not names or len(names) != len(set(names)):
        raise SystemExit("in-text inventory is empty or contains duplicate names")
    return set(names)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--route", choices=("synthetic", "real"), required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    expected = load_inventory(root / "certification" / "INTEXT_NUMBER_INVENTORY.txt")
    report = root / "output" / "tables" / "intext_numbers_report.csv"
    if not report.is_file() or report.is_symlink():
        raise SystemExit(f"missing or symlinked in-text report: {report}")
    with report.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["name", "value", "status", "note"]:
            raise SystemExit(f"unexpected in-text report schema: {reader.fieldnames}")
        rows = list(reader)
    names = [row["name"] for row in rows]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    missing = sorted(expected - set(names))
    extra = sorted(set(names) - expected)
    bad = []
    for row in rows:
        try:
            finite = math.isfinite(float(row["value"]))
        except (TypeError, ValueError):
            finite = False
        if not finite:
            bad.append(f"{row['name']}: non-finite value {row['value']!r}")
        if args.route == "real" and row["status"] != "ok":
            bad.append(f"{row['name']}: real-route status {row['status']!r}")
    if duplicates or missing or extra or bad:
        raise SystemExit(
            f"in-text report failed: duplicates={duplicates}; missing={missing}; extra={extra}; "
            f"bad={bad[:20]}"
        )
    print(f"PASS: {len(rows)}/{len(expected)} unique finite in-text values; route={args.route}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
