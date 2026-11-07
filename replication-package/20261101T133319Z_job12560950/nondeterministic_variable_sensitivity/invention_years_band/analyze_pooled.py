#!/usr/bin/env python3
"""Pool the near-threshold and out-of-band invention-year draws and report how often
the returned year moves, and how often it moves across the 60-year device-experience
threshold that the Class II maturity count in 11d_reg_design.py applies.

Reads both archives:
  invention_years_band/raw_responses.jsonl        (612 codes within 6 years of 1959)
  invention_years_outofband/raw_responses.jsonl   (360 codes drawn further out)

Usage:  python3 analyze_pooled.py
"""
import json, math, pathlib, re, statistics

THRESHOLD_YEAR = 1959          # MANUSCRIPT_MATURITY_THRESHOLD_YEARS = 60, applied in 2019
YEAR = re.compile(r"Year:\s*(\d{4})")
ARCHIVES = ("invention_years_band", "invention_years_outofband")


def wilson(k, n, z=1.96):
    """Score interval; the normal approximation is unusable at these rates."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (centre - half), 100 * (centre + half)


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    items = {}
    for archive in ARCHIVES:
        path = root / archive / "raw_responses.jsonl"
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if "error" in rec:
                continue
            m = YEAR.search(rec["raw_response"] or "")
            if not m:
                continue
            key = (archive, rec["productcode"] if "productcode" in rec else rec["pc"])
            entry = items.setdefault(key, {"deposited": rec["deposited_year"],
                                           "in_band": rec["in_band"], "years": []})
            entry["years"].append(int(m.group(1)))

    groups = {"near-threshold": [], "out-of-band": []}
    for entry in items.values():
        groups["near-threshold" if entry["in_band"] else "out-of-band"].append(entry)

    print(f"{'stratum':<16}{'n':>5}{'year moves':>16}{'crosses 60 yr':>16}   95% CI on crossing")
    rates = {}
    for name, entries in groups.items():
        n = len(entries)
        moved = sum(1 for e in entries if len(set(e["years"])) > 1)
        crossed = sum(1 for e in entries
                      if len({y < THRESHOLD_YEAR for y in e["years"]}) > 1)
        lo, hi = wilson(crossed, n)
        rates[name] = (n, crossed / n)
        print(f"{name:<16}{n:>5}{moved:>8} ({100*moved/n:4.1f}%)"
              f"{crossed:>8} ({100*crossed/n:4.1f}%)   [{lo:.2f}%, {hi:.2f}%]")

    spreads = [max(e["years"]) - min(e["years"]) for es in groups.values() for e in es
               if len(set(e["years"])) > 1]
    print(f"\nrevision spread among the {len(spreads)} codes that move: "
          f"median {statistics.median(spreads):.0f}, mean {statistics.mean(spreads):.1f}, "
          f"90th pct {sorted(spreads)[int(0.9*len(spreads))]}, max {max(spreads)}")

    # Extrapolate to the full Class II code set the maturity count is taken over.
    POPULATION = 2784
    near_n, near_rate = rates["near-threshold"]
    far_rate = rates["out-of-band"][1]
    expected = near_n * near_rate + (POPULATION - near_n) * far_rate
    print(f"\nimplied crossings over all {POPULATION} codes: "
          f"{near_n}x{near_rate:.3f} + {POPULATION-near_n}x{far_rate:.3f} = {expected:.0f}"
          f"  ({100*expected/POPULATION:.1f}%)")
    print("Crossings run in both directions, so this bounds churn, not net movement.")


if __name__ == "__main__":
    main()
