"""Compare the market-age regression across the baseline and each substituted draw.

Reads the per-run output tables captured by run_11d.sh and prints the four age-slope rows and
the four zero-crossings side by side. The Class III->II rows are built from hand-coded years and
should not move: they are the invariant control.

Usage:  python3 cmp_11d.py <results dir>
"""
import csv, pathlib, sys

RES = pathlib.Path(sys.argv[1])
RUNS = ["baseline"] + [f"draw{i}" for i in range(1, 6)]


def load(run, name, key_cols, val_cols):
    p = RES / run / name
    if not p.exists():
        return None
    out = {}
    for r in csv.DictReader(open(p)):
        out[tuple(r[c] for c in key_cols)] = tuple(r[c] for c in val_cols)
    return out


def fmt(v, nd=6):
    try:
        return f"{float(v):.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


present = [r for r in RUNS if (RES / r / "maturity_gradient_slopes.csv").exists()]
print(f"runs with a slopes table: {', '.join(present) if present else 'none'}\n")

slopes = {r: load(r, "maturity_gradient_slopes.csv",
                  ["reclass_type", "outcome"], ["slope", "se", "pvalue", "n"]) for r in present}
if slopes:
    keys = sorted(next(iter(slopes.values())).keys())
    print("=== AGE SLOPE  (III->II rows use HAND-CODED years: invariant control) ===")
    for k in keys:
        tag = "  <-- control" if k[0] == "3_2" else "  <-- model-generated"
        print(f"\n{k[0]:>5} {k[1]}{tag}")
        print(f"  {'run':<10}{'slope':>14}{'s.e.':>12}{'p':>10}{'n':>6}")
        for r in present:
            v = slopes[r].get(k)
            if v:
                print(f"  {r:<10}{fmt(v[0]):>14}{fmt(v[1],6):>12}{fmt(v[2],4):>10}{v[3]:>6}")

cross = {r: load(r, "exp_impact_zero_crossings.csv",
                 ["reclass_type", "outcome"], ["zero_crossing_years"]) for r in present}
if cross and any(cross.values()):
    print("\n=== ZERO CROSSING (years) ===")
    keys = sorted(next(c for c in cross.values() if c).keys())
    print(f"  {'run':<10}" + "".join(f"{k[0]+'/'+k[1].replace('_est',''):>22}" for k in keys))
    for r in present:
        if not cross[r]:
            continue
        print(f"  {r:<10}" + "".join(f"{(cross[r].get(k) or ('-',))[0]:>22}" for k in keys))
