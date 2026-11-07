"""Turn the re-draw responses into five drop-in replacements for the deposited
`innovation_year_2_1_FDA_project.csv`, and report item-level instability.

Each output has the deposited schema (PRODUCTCODE,years) and the deposited row order, so the
only thing that changes when one is substituted into the tree is the invention-year vector.

Usage:  python3 build_draw_files.py <deposited innovation_year_2_1_FDA_project.csv>
"""
import csv, json, pathlib, re, statistics, sys

YEAR = re.compile(r"Year:\s*(\d{4})")
HERE = pathlib.Path(__file__).parent
OUT = HERE / "draw_files"


def main(deposited_csv):
    order, dep = [], {}
    for r in csv.DictReader(open(deposited_csv)):
        order.append(r["PRODUCTCODE"])
        dep[r["PRODUCTCODE"]] = r["years"]

    draws = {}
    errors = 0
    sources = sys.argv[2:] or [str(HERE / "iy_2_1" / "raw_responses.jsonl")]
    for src in sources:
        for line in pathlib.Path(src).read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if "error" in rec:
                errors += 1
                continue
            m = YEAR.search(rec["raw_response"] or "")
            draws.setdefault(rec["draw"], {})[rec["productcode"]] = int(m.group(1)) if m else None
    print(f"pooled {len(sources)} response file(s)")

    print(f"draws: {sorted(draws)}  errors: {errors}")
    OUT.mkdir(exist_ok=True)
    for d in sorted(draws):
        path = OUT / f"draw{d+1}" / "innovation_year_2_1_FDA_project.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        unparsed = 0
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["PRODUCTCODE", "years"])
            for pc in order:
                y = draws[d].get(pc)
                if y is None:
                    unparsed += 1
                w.writerow([pc, "" if y is None else y])
        print(f"  draw{d+1}: wrote {path.name} ({len(order)} rows, {unparsed} unparsed)")

    # ---- item-level instability -------------------------------------------------------
    moved, spreads, repro = 0, [], 0
    for pc in order:
        ys = [draws[d].get(pc) for d in sorted(draws)]
        ys = [y for y in ys if y is not None]
        if not ys:
            continue
        if len(set(ys)) > 1:
            moved += 1
            spreads.append(max(ys) - min(ys))
        try:
            if all(y == int(float(dep[pc])) for y in ys):
                repro += 1
        except (ValueError, TypeError):
            pass
    n = len(order)
    print(f"\n=== ITEM-LEVEL, {n} Class II->I product codes x {len(draws)} draws ===")
    print(f"  year changes across draws        : {moved}/{n} ({moved/n:.0%})")
    if spreads:
        print(f"  spread among those              : median {statistics.median(spreads):.0f}, "
              f"mean {statistics.mean(spreads):.1f}, max {max(spreads)}")
    print(f"  all draws reproduce the deposited year: {repro}/{n} ({repro/n:.0%})")


if __name__ == "__main__":
    main(sys.argv[1])
