#!/usr/bin/env python3
"""Score the invention-year validation sample with design weights.

Usage:  python3 score_validation.py [--tol YEARS] [--adjudicated FILE]

Expects, in this directory:
  sample_KEY.csv                 (written when the sample was drawn)
  coding_sheet_coder1.csv        (coder 1, blind)
  coding_sheet_coder2.csv        (coder 2, blind)          -- optional but strongly preferred
  coding_sheet_adjudicated.csv   (adjudicated labels)      -- optional; falls back to coder1
Every estimate uses design weights 1/pi. Unweighted means estimate nothing.
"""
import argparse, csv, math, pathlib, statistics, sys, collections

HERE = pathlib.Path(__file__).resolve().parent
THR = 1959          # invention year < 1959  <=>  device age > 60 in 2019

def read(name, needed=True):
    p = HERE / name
    if not p.exists():
        if needed: sys.exit(f"missing required file: {p}")
        return None
    return {r["row"]: r for r in csv.DictReader(open(p, newline="", encoding="utf8", errors="replace"))}

def year(v):
    try: return int(float(v))
    except Exception: return None

def wmean(pairs):                      # pairs of (value, weight)
    W = sum(w for _, w in pairs)
    return (sum(v * w for v, w in pairs) / W) if W else float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=int, default=0, help="years of slack before calling it an error")
    ap.add_argument("--adjudicated", default="coding_sheet_adjudicated.csv")
    a = ap.parse_args()

    key = read("sample_KEY.csv")
    c1 = read("coding_sheet_coder1.csv", needed=False)
    c2 = read("coding_sheet_coder2.csv", needed=False)
    adj = read(a.adjudicated, needed=False)
    if not (c1 or adj):
        sys.exit("No coded sheet found. Fill coding_sheet_BLIND.csv per CODING_PROTOCOL.md first,\n"
                 "save it as coding_sheet_coder1.csv (and coder2), then re-run.")

    if c1 and c2:
        both = [(year(c1[r]["coder_year"]), year(c2[r]["coder_year"])) for r in c1 if r in c2]
        both = [(x, y) for x, y in both if x is not None and y is not None]
        exact = sum(1 for x, y in both if x == y)
        w5 = sum(1 for x, y in both if abs(x - y) <= 5)
        print(f"=== inter-coder agreement (n={len(both)}) ===")
        print(f"  exact        : {exact}/{len(both)} ({exact/max(len(both),1):.1%})")
        print(f"  within 5 yr  : {w5}/{len(both)} ({w5/max(len(both),1):.1%})")
        print("  (this is the ceiling on measurable model accuracy)\n")

    hand = adj or c1
    rows = []
    for r, k in key.items():
        h = year((hand.get(r) or {}).get("coder_year", ""))
        m = year(k["model_year"])
        if h is None or m is None: continue
        rows.append({"stratum": k["stratum"], "w": 1.0 / float(k["pi"]),
                     "m": m, "h": h, "err": m - h,
                     "mis": (m < THR) != (h < THR)})
    if not rows: sys.exit("no rows with both a coded year and a model year")
    coded = len(rows); blank = len(key) - coded
    print(f"=== coverage ===\n  coded {coded} of {len(key)} sampled "
          f"({blank} blank/undeterminable, excluded)\n")

    def block(label, sel):
        s = [r for r in rows if sel(r)]
        if not s: return
        W = sum(r["w"] for r in s)
        err_rate = sum(r["w"] for r in s if abs(r["err"]) > a.tol) / W
        bias = wmean([(r["err"], r["w"]) for r in s])
        mis = sum(r["w"] for r in s if r["mis"]) / W
        n = len(s)
        se_b = (statistics.pstdev([r["err"] for r in s]) / math.sqrt(n)) if n > 1 else float("nan")
        print(f"  {label:28s} n={n:4d}  err>{a.tol}yr={err_rate:6.1%}  "
              f"signed bias={bias:+7.2f} yr (SE {se_b:.2f})  threshold misclass={mis:6.2%}")

    print(f"=== weighted error (tolerance {a.tol} yr; THR={THR}) ===")
    block("ALL", lambda r: True)
    for st in sorted({r["stratum"] for r in rows}):
        block(st, lambda r, st=st: r["stratum"] == st)
    print("\n  signed bias is E[model - hand] in years: positive means the model dates devices too late.")
    print("  threshold misclass is the share whose over-60 classification the model gets wrong —")
    print("  the quantity that moves the published Class II maturity count.")

if __name__ == "__main__":
    main()
