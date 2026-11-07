#!/usr/bin/env python3
"""
convert_nexis_to_csv.py — JPE Policy 1.4 non-proprietary mirrors for the Nexis exports.

The Nexis Results-list exports are proprietary `.xlsx` (Excel) workbooks. Policy 1.4
requires a non-proprietary copy when a proprietary format is used. This script writes a
UTF-8 **CSV mirror** next to every Results-list workbook under `data/raw/Liability/`
(and `medtech/`), and emits a hash manifest (`NEXIS_FORMAT_MIRROR_HASHES.csv`) recording
the SHA-256 and row count of both the `.xlsx` and its `.csv` mirror.

These mirrors live in the **restricted** Liability directory (excluded from the public
package); they accompany the raw exports in the editor-confidential Nexis delivery so the
Data Editor can verify Figure D.10 from a non-proprietary copy. `11c_liability.py`
reads the `.xlsx`; the CSV is a value- and schema-equivalent, format-open companion
(CSV cannot be byte-identical to XLSX; equivalence is at the cell-value and column level).

Run: `python3 code/00_generate_data/convert_nexis_to_csv.py`
(derives the package root from __file__; override with PKG_SRC).
"""
import os, glob, hashlib, csv, sys
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("PKG_SRC") or os.path.abspath(os.path.join(_HERE, "..", ".."))
LIAB = os.path.join(SRC, "data", "raw", "Liability")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isdir(LIAB):
        print(f"Liability dir not found: {LIAB}", file=sys.stderr)
        sys.exit(1)
    workbooks = sorted(glob.glob(os.path.join(LIAB, "*.xlsx")) +
                       glob.glob(os.path.join(LIAB, "medtech", "*.xlsx")))
    # Results lists only (skip the FDB device cross-reference, which is not a Nexis export)
    workbooks = [w for w in workbooks if os.path.basename(w).startswith("Results list")]
    rows = []
    for x in workbooks:
        csv_path = x[:-5] + ".csv"
        df = pd.read_excel(x)
        df.to_csv(csv_path, index=False, encoding="utf-8")
        rows.append({
            "xlsx": os.path.relpath(x, SRC),
            "csv": os.path.relpath(csv_path, SRC),
            "n_rows": len(df),
            "xlsx_sha256": sha256(x),
            "csv_sha256": sha256(csv_path),
        })
    manifest = os.path.join(LIAB, "NEXIS_FORMAT_MIRROR_HASHES.csv")
    with open(manifest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["xlsx", "csv", "n_rows", "xlsx_sha256", "csv_sha256"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} CSV mirrors + manifest {os.path.relpath(manifest, SRC)}")
    print(f"  total rows mirrored: {sum(r['n_rows'] for r in rows)}")


if __name__ == "__main__":
    main()
