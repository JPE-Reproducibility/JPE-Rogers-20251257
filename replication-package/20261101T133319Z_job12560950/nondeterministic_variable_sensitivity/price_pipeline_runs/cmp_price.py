"""Compare the price and utilization estimates across the baseline and every re-draw.

The baseline run uses the deposited concordance and reproduces
output/tables/price_utilization_estimates.csv byte for byte; each draw run substitutes one
re-drawn concordance and changes nothing else. An estimate missing from a draw is reported as a
smaller n rather than dropped silently: a sparse draw can leave a panel unbuildable or an estimate
unidentified, which is a result in its own right.

Usage:  python3 cmp_price.py <results dir> [--full]

The results dir holds one subdirectory per run, each with a price_utilization_estimates.csv.
Whichever subdirectory name contains "baseline" is treated as the baseline; the rest are draws,
ordered naturally. --full prints every estimate rather than the load-bearing selection.
"""
import csv, pathlib, re, statistics, sys

KEY = ("reclass_type", "outcome", "method", "sample")
HEADLINE = [
    (("2_1", "BilledAmt", "BJS_imputation", "All CPTs"), "II->I billed, BJS, all CPTs   [load-bearing]"),
    (("2_1", "BilledAmt", "Conley_Taber", "All CPTs"),   "II->I billed, CT, all CPTs    [load-bearing]"),
    (("2_1", "BilledAmt", "BJS_imputation", "Matched"),  "II->I billed, BJS, matched"),
    (("3_2", "BilledAmt", "BJS_imputation", "All CPTs"), "III->II billed, BJS, all CPTs [fragile panel]"),
    (("3_2", "BilledAmt", "BJS_imputation", "Expert"),   "III->II billed, BJS, expert   [control]"),
    (("3_2", "BilledAmt", "Conley_Taber", "Expert"),     "III->II billed, CT, expert    [control]"),
]


def natural(name):
    m = re.search(r"(\d+)$", name)
    return (0 if "baseline" in name else 1, int(m.group(1)) if m else 0, name)


def load(d):
    p = d / "price_utilization_estimates.csv"
    if not p.exists():
        return {}
    with open(p, newline="", encoding="utf8", errors="replace") as fh:
        return {tuple(r[k] for k in KEY): r["Estimate"] for r in csv.DictReader(fh)}


def main(results_dir, full=False):
    root = pathlib.Path(results_dir)
    runs = sorted((d for d in root.iterdir() if d.is_dir()), key=lambda d: natural(d.name))
    if not runs:
        sys.exit(f"no run subdirectories under {root}")
    # EVERY directory whose name contains "baseline" is a baseline, not a draw. The inertness of
    # the harness was re-checked as each guard was added, so there is more than one; folding them
    # into the draws would seed the distribution with copies of the deposited value.
    bases = [d for d in runs if "baseline" in d.name]
    draws = [d for d in runs if "baseline" not in d.name]
    tables = {d.name: load(d) for d in runs}

    print(f"baseline runs: {len(bases)} ({', '.join(d.name for d in bases)})")
    if len(bases) > 1:
        sigs = {frozenset(tables[d.name].items()) for d in bases}
        print(f"  all baseline runs agree: {len(sigs) == 1}")
    base_dir = bases[-1] if bases else None
    print(f"reference baseline: {base_dir.name if base_dir else '(none)'}   draws: {len(draws)}")
    for d in draws:
        print(f"  {d.name}: {len(tables[d.name])} estimates")

    base = tables[base_dir.name] if base_dir else {}
    keys = HEADLINE
    if full:
        keys = [(k, " ".join(k)) for k in sorted({k for t in tables.values() for k in t})]

    for key, label in keys:
        vals = [float(tables[d.name][key]) for d in draws
                if tables[d.name].get(key) not in (None, "")]
        absent = [d.name for d in draws if tables[d.name].get(key) in (None, "")]
        b = base.get(key)
        print(f"\n{label}")
        print(f"  deposited {float(b):+.4f}" if b not in (None, "") else "  deposited (absent)")
        if vals:
            print(f"  draws n={len(vals)}  mean {statistics.mean(vals):+.4f}  "
                  f"SD {statistics.pstdev(vals):.4f}  "
                  f"range [{min(vals):+.4f}, {max(vals):+.4f}]")
            print(f"  sorted: {', '.join(f'{v:+.2f}' for v in sorted(vals))}")
            if b not in (None, ""):
                print(f"  sign preserved in every draw: "
                      f"{all((v < 0) == (float(b) < 0) for v in vals)}"
                      f"   deposited inside the draw range: "
                      f"{min(vals) <= float(b) <= max(vals)}")
        if absent:
            print(f"  unavailable in: {', '.join(absent)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else "hresults", full="--full" in sys.argv)
