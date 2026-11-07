#!/usr/bin/env python3.9
"""STRICT, FAIL-CLOSED full-number comparison of regenerated vs committed outputs.

Certification-grade: given a FIXED inventory of the files that MUST reproduce, this
compares EVERY numeric cell (point estimate, both CI endpoints, SE, sample size,
summary-stat values, ...) plus string cells of every inventory file, and EXITS
NONZERO if ANY inventory file is missing, unreadable, shape/column-changed,
numerically different, or (by default) non-byte-identical. It never silently skips.

This replaces an earlier fail-open version that iterated whatever CSVs happened to
exist, skipped missing regenerated files, and always exited 0 -- so a corrupted or
missing output could be reported as "compared" while the process still "passed".

Usage:
  compare_all_numbers.py --regen <REGEN_out> --committed <COMMITTED_out> \
      --inventory <FILE> --out <OUT_CSV> [--prerun MANIFEST] [--allow-numeric-equal]

  --inventory        : REQUIRED. A text file listing the relative CSV paths that MUST
                       reproduce (one per line; '#' comments allowed). The comparison
                       set is EXACTLY this list -- not "whatever exists".
  --allow-numeric-equal : relax the pass bar from byte-identity to numeric+string
                       equality (for adjudicated formatting-only differences). Default
                       is byte-identity (strictest). Even relaxed, ANY numeric or string
                       difference still fails.
  --prerun MANIFEST  : optional; marks per-file regeneration (mtime advanced).

Exit code: 0 iff EVERY inventory file PASSED; 1 otherwise. A one-line SUMMARY and a
per-file report (with a FAIL reason for each failing file) are always written.
"""
import argparse
import csv
import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LO = {"lower_cb", "lower_CI", "conf.low", "lower", "ci_low", "lower_ci"}
HI = {"upper_cb", "upper_CI", "conf.high", "upper", "ci_high", "upper_ci"}


def _numeric(series):
    """Coerce a column to float64 for numeric comparison.

    `pd.to_numeric` leaves a BOOLEAN column as bool dtype, and numpy refuses the `-`
    operator on booleans, so this comparator crashed with "numpy boolean subtract" on
    any governed output carrying a True/False column (the `reproduces` flag in
    output/tables/PatentCollectionCounts.csv). Casting to float64 makes a boolean
    column compare as 0.0/1.0, so a flag that FLIPS is reported as a difference
    rather than skipped -- which is what the comparator is for. Non-numeric text
    still coerces to NaN and falls through to the string comparison below.
    """
    return pd.to_numeric(series, errors="coerce").astype("float64")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sig(lo, hi):
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return None
    return (lo > 0 and hi > 0) or (lo < 0 and hi < 0)


# The comparator is BOUND to the canonical inventory shipped beside it, and to the exact count of
# certified numeric CSVs. Passing a different/short/../ inventory cannot trivially pass.
CANONICAL_INVENTORY = Path(__file__).resolve().parent / "COMPARATOR_INVENTORY.txt"
EXPECTED_COUNT = 152   # kept in step with COMPARATOR_INVENTORY.txt (manufacturer_linkage_coverage added 2026-09-22)


def _safe_rel(rel):
    """A certification path must be a SAFE relative CSV path: no absolute, no drive, no '..', no
    leading '/', POSIX-style, ending in .csv."""
    r = rel.replace("\\", "/")
    if not r.endswith(".csv"):
        return False
    if r.startswith("/") or ":" in r.split("/")[0] or ".." in r.split("/"):
        return False
    return True


def load_inventory(path):
    # BIND to the canonical inventory: the supplied path must resolve to the shipped
    # COMPARATOR_INVENTORY.txt (realpath equality), so an out-of-tree/'../' inventory is rejected.
    if path.resolve() != CANONICAL_INVENTORY:
        raise SystemExit(
            f"FATAL: --inventory must be the canonical {CANONICAL_INVENTORY} "
            f"(got {path.resolve()}). The comparator is bound to the shipped "
            f"{EXPECTED_COUNT}-file inventory."
        )
    inv = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            inv.append(line)
    if len(inv) != len(set(inv)):
        dups = sorted({p for p in inv if inv.count(p) > 1})
        raise SystemExit(f"FATAL: inventory has duplicate entries: {dups[:5]}")
    bad = [r for r in inv if not _safe_rel(r)]
    if bad:
        raise SystemExit(f"FATAL: inventory has unsafe/non-CSV path(s): {bad[:5]}")
    if len(inv) != EXPECTED_COUNT:
        raise SystemExit(f"FATAL: inventory must list EXACTLY {EXPECTED_COUNT} CSVs; found {len(inv)}.")
    return inv


def _resolves_inside(base: Path, rel: str) -> bool:
    """True iff base/rel (symlinks resolved) stays inside base -- rejects symlink/'..' escapes."""
    try:
        broot = base.resolve()
        full = (base / rel).resolve()
        return full == broot or str(full).startswith(str(broot) + "/")
    except OSError:
        return False


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--regen", required=True, type=Path)
    ap.add_argument("--committed", required=True, type=Path)
    ap.add_argument("--inventory", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--prerun", type=Path, default=None)
    ap.add_argument("--allow-numeric-equal", action="store_true")
    return ap.parse_args()


def main():
    a = parse_args()
    inventory = load_inventory(a.inventory)
    pre = {}
    if a.prerun and a.prerun.exists():
        for line in a.prerun.read_text().splitlines():
            p = line.split(" ", 2)
            if len(p) == 3:
                pre[p[2]] = float(p[0])

    def regenerated(f):
        if not pre:
            return "n/a"
        k = str(f)
        return (k not in pre) or (os.path.getmtime(f) - pre[k] > 1)

    rows = []
    n_pass = n_fail = 0
    worst_abs = worst_rel = 0.0
    sign_changes = sig_changes = 0
    fail_reasons = []

    for rel in inventory:
        cf = a.committed / rel
        rf = a.regen / rel
        status = "PASS"
        reason = ""
        regen = "n/a"
        byte_id = False
        fmax_abs = fmax_rel = 0.0
        sc_n = sg_n = 0
        diff_cols = []

        if not _resolves_inside(a.committed, rel) or not _resolves_inside(a.regen, rel):
            status, reason = "FAIL", "PATH_ESCAPE/SYMLINK (resolves outside the output tree)"
        elif not cf.exists():
            status, reason = "FAIL", "COMMITTED_MISSING"
        elif not rf.exists():
            status, reason = "FAIL", "REGEN_MISSING"
        else:
            regen = regenerated(rf)
            try:
                byte_id = sha(cf) == sha(rf)
            except OSError as e:
                status, reason = "FAIL", f"UNREADABLE_BYTES({e})"
            if status == "PASS":
                try:
                    dfa = pd.read_csv(cf)
                    dfb = pd.read_csv(rf)
                except Exception as e:  # noqa: BLE001
                    status, reason = "FAIL", f"READ_ERR({type(e).__name__})"
            if status == "PASS":
                if list(dfa.columns) != list(dfb.columns) or dfa.shape != dfb.shape:
                    status, reason = "FAIL", f"SHAPE/COLS({dfa.shape}->{dfb.shape})"
            if status == "PASS":
                for c in dfa.columns:
                    ac = _numeric(dfa[c])
                    bc = _numeric(dfb[c])
                    # NULL-MASK: a cell going blank<->value (e.g. ""->999) is a difference even if the
                    # numeric max ignores NaN. Compare the missingness pattern of the ORIGINAL cells.
                    a_na = dfa[c].isna() | (dfa[c].astype(str).str.strip() == "")
                    b_na = dfb[c].isna() | (dfb[c].astype(str).str.strip() == "")
                    if (a_na.values != b_na.values).any():
                        diff_cols.append(f"{c}(null-pattern)")
                    if ac.notna().any() or bc.notna().any():
                        d = (ac - bc).abs()
                        # NON-FINITE MISMATCH (fixed 2026-10-13): inf is NOT NaN, so a cell that is
                        # inf in one copy and finite in the other gives |diff| = inf. The former line
                        # tested `np.isfinite(np.nanmax(d))` and fell back to mx = 0.0, which zeroed
                        # the column maximum and -- because the verdict is `not diff_cols` -- hid
                        # EVERY difference in that column: a regenerated file whose estimate had gone
                        # 1.100 -> 9.900 and flipped sign reported "max|abs diff| = 0" and PASSED.
                        # A finiteness mismatch is now itself a difference, and the column maximum is
                        # taken over the finite diffs instead of being discarded.
                        finite_a = np.isfinite(ac.values)
                        finite_b = np.isfinite(bc.values)
                        present = ac.notna().values | bc.notna().values
                        if ((finite_a != finite_b) & present).any():
                            diff_cols.append(f"{c}(non-finite in one copy)")
                        finite_diffs = d.values[np.isfinite(d.values)]
                        mx = float(finite_diffs.max()) if finite_diffs.size else 0.0
                        if mx > 0:
                            denom = np.maximum(ac.abs(), 1e-12)
                            colrel = float(np.nanmax((d / denom).values))
                            diff_cols.append(f"{c}(|Δ|={mx:.4g})")
                            fmax_abs = max(fmax_abs, mx)
                            fmax_rel = max(fmax_rel, colrel)
                    if not ac.notna().any() and not bc.notna().any():
                        if (dfa[c].astype(str) != dfb[c].astype(str)).any():
                            diff_cols.append(f"{c}(str)")
                ecol = next((c for c in ["Effect", "Estimate", "estimate", "coef"] if c in dfa.columns), None)
                lo = next((c for c in dfa.columns if c in LO), None)
                hi = next((c for c in dfa.columns if c in HI), None)
                if ecol:
                    ae = _numeric(dfa[ecol])
                    be = _numeric(dfb[ecol])
                    m = ae.notna() & be.notna()
                    sc_n = int((np.sign(ae[m]) != np.sign(be[m])).sum())
                    if lo and hi:
                        alo = _numeric(dfa[lo]); ahi = _numeric(dfa[hi])
                        blo = _numeric(dfb[lo]); bhi = _numeric(dfb[hi])
                        for i in dfa.index:
                            s1, s2 = sig(alo[i], ahi[i]), sig(blo[i], bhi[i])
                            if s1 is not None and s2 is not None and s1 != s2:
                                sg_n += 1
                sign_changes += sc_n
                sig_changes += sg_n
                worst_abs = max(worst_abs, fmax_abs)
                worst_rel = max(worst_rel, fmax_rel)
                # PASS criterion
                numeric_string_equal = not diff_cols
                if byte_id:
                    status = "PASS"
                elif a.allow_numeric_equal and numeric_string_equal:
                    status = "PASS"
                    reason = "NUMERIC_EQUAL_BYTE_DIFF(accepted)"
                elif numeric_string_equal:
                    status, reason = "FAIL", "NON_BYTE_IDENTICAL(numeric-equal; needs --allow-numeric-equal)"
                else:
                    status, reason = "FAIL", "NUMERIC/STRING_DIFF: " + "; ".join(diff_cols[:6])

        if status == "PASS":
            n_pass += 1
        else:
            n_fail += 1
            fail_reasons.append(f"{rel}: {reason}")
        rows.append([rel, status, reason, regen, byte_id,
                     f"{fmax_abs:.6g}", f"{fmax_rel:.3g}", sc_n, sg_n])

    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "status", "reason", "regenerated", "byte_identical",
                    "max_abs_diff", "max_rel_diff", "sign_changes", "significance_changes"])
        w.writerows(rows)

    total = len(inventory)
    print(f"SUMMARY: {n_pass}/{total} PASS, {n_fail} FAIL "
          f"(inventory={total}, pass_bar={'numeric+string equal' if a.allow_numeric_equal else 'byte-identical'})")
    print(f"  worst max|abs diff| = {worst_abs:.6g} | sign changes = {sign_changes} | "
          f"significance changes = {sig_changes}")
    print(f"  per-file detail -> {a.out}")
    if fail_reasons:
        print(f"  FAILURES ({len(fail_reasons)}):")
        for r in fail_reasons[:40]:
            print(f"    {r}")
        if len(fail_reasons) > 40:
            print(f"    ... and {len(fail_reasons) - 40} more (see {a.out})")
    # FAIL-CLOSED: nonzero unless EVERY inventory file passed.
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
