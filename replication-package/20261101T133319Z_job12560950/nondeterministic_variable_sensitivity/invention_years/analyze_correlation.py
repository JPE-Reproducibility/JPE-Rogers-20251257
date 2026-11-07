#!/usr/bin/env python3
"""Recompute the published hand-vs-model invention-year correlation and its re-draw
distribution for the 25 down-regulated (Class III->II) device types.

Usage:  python3 analyze_correlation.py <deposited innovation_year_FDA_project.csv>

The deposited file carries both series: `yr_invent_or_comm_avail` (hand-coded) and
`years` (parsed from the archived 2024 model response via the `Year: (\\d{4})` regex).
`raw_responses.jsonl` in this directory holds five fresh draws for the same 25 queries,
verbatim, against gpt-4o-2024-08-06 at temperature=0.
"""
import csv, json, math, pathlib, re, statistics, sys

YEAR = re.compile(r"Year:\s*(\d{4})")


def parse_year(text):
    m = YEAR.search(text or "")
    return int(m.group(1)) if m else None


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def main(deposited_csv):
    rows = list(csv.DictReader(open(deposited_csv)))
    hand = {r["query"].strip(): float(r["yr_invent_or_comm_avail"]) for r in rows}
    arch = {r["query"].strip(): float(r["years"]) for r in rows}

    draws = {}
    here = pathlib.Path(__file__).parent
    for line in (here / "raw_responses.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if "error" in rec:
            continue
        y = parse_year(rec["raw_response"])
        if y is not None:
            draws.setdefault(rec["draw"], {})[rec["query"].strip()] = y

    keys = [q for q in hand if q in draws[0]]
    print(f"paired device types: {len(keys)}   draws: {len(draws)}")

    r_arch = pearson([hand[q] for q in keys], [arch[q] for q in keys])
    print(f"\narchived 2024 responses : r = {r_arch:.4f}   (manuscript prints 0.76)")
    rs = []
    for d in sorted(draws):
        ks = [q for q in keys if draws[d].get(q)]
        r = pearson([hand[q] for q in ks], [float(draws[d][q]) for q in ks])
        rs.append(r)
        print(f"  draw {d}: n={len(ks)}  r = {r:.4f}")
    print(f"re-draw mean r = {statistics.mean(rs):.4f}  SD = {statistics.pstdev(rs):.4f}"
          f"  range {min(rs):.4f}-{max(rs):.4f}")

    exact = [q for q in keys if arch[q] == hand[q]]
    rest = [q for q in keys if q not in exact]
    print(f"\ndevice types where the 2024 response matched the hand year exactly: {len(exact)}")
    print(f"excluding them (n={len(rest)}):")
    print(f"  archived  r = {pearson([hand[q] for q in rest], [arch[q] for q in rest]):.4f}")
    rs2 = [pearson([hand[q] for q in rest if draws[d].get(q)],
                   [float(draws[d][q]) for q in rest if draws[d].get(q)])
           for d in sorted(draws)]
    print(f"  re-draw mean r = {statistics.mean(rs2):.4f}  SD {statistics.pstdev(rs2):.4f}")

    spreads = []
    for q in keys:
        ys = [draws[d][q] for d in sorted(draws) if draws[d].get(q)]
        if len(set(ys)) > 1:
            spreads.append(max(ys) - min(ys))
    print(f"\ndevice types whose year changes across draws: {len(spreads)}/{len(keys)}"
          f"  (mean spread {statistics.mean(spreads):.1f}, max {max(spreads)})")
    reproduced = sum(1 for q in keys
                     if all(draws[d].get(q) == arch[q] for d in sorted(draws)))
    print(f"device types where all draws reproduce the archived 2024 year: {reproduced}/{len(keys)}")


if __name__ == "__main__":
    main(sys.argv[1])
