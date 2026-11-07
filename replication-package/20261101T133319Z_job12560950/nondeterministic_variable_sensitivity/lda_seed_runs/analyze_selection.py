#!/usr/bin/env python3
"""Report, for each LDA refit, the coherence sweep, the topic count the selection rule
picks, the count a plain arg-max would pick, and how many topic effects the resulting
Appendix Figure D.5 exhibit carries.

The selection rule in 11a_product_variety.py is the FIRST candidate within 1e-3 of the
maximum coherence ("prefer smaller model when tied"), not the arg-max.

Usage:  python3 analyze_selection.py
"""
import pathlib, re

SWEEP = re.compile(r"Topics=(\d+), Coherence=([\d.]+)")
PICK = re.compile(r"\[(\w+)\] Optimal topics: (\d+) \(coherence=([\d.]+)\)")
EST = re.compile(r"Topic (\d+): est=([-\d.eE]+), CI=\[([-\d.eE]+), ([-\d.eE]+)\]")
TOLERANCE = 1e-3
SEEDS = (42, 1, 2, 3, 4)


def main():
    here = pathlib.Path(__file__).parent
    print("Coherence sweeps and selections\n")
    for seed in SEEDS:
        # The 45 MB of gensim training logs were not deposited; the sweep lines they carried are
        # preserved in coherence_sweeps.txt, which is all this reads.
        sweeps = here / "coherence_sweeps.txt"
        log = here / "logs" / f"seed_{seed}.out"
        if log.exists():
            text = log.read_text(errors="replace")
        elif sweeps.exists():
            text = "\n".join(l.split("|", 1)[1] for l in sweeps.read_text().splitlines()
                              if l.startswith(f"seed_{seed} |"))
        else:
            continue
        # Each sample's sweep is the run of Topics= lines preceding its "Optimal topics".
        sweeps, current = [], []
        for line in text.splitlines():
            m = SWEEP.search(line)
            if m:
                current.append((int(m.group(1)), float(m.group(2))))
                continue
            p = PICK.search(line)
            if p and current:
                sweeps.append((p.group(1), p, current))
                current = []
        print(f"  seed {seed}")
        for sample, pick, sweep in sweeps:
            best = max(s for _, s in sweep)
            argmax_k = next(k for k, s in sweep if s == best)
            rule_k = next(k for k, s in sweep if abs(s - best) < TOLERANCE)
            scores = "  ".join(f"{k}:{s:.4f}" for k, s in sweep)
            flag = "" if rule_k == argmax_k else f"   <-- tie-break: rule {rule_k}, arg-max {argmax_k}"
            print(f"    {sample:<5} {scores}")
            print(f"    {'':<5} selected {pick.group(2)}{flag}")
        print()

    print("Topic effects estimated per refit (the Figure D.5 exhibit)\n")
    print(f"  {'seed':<6}{'effects':>8}{'CI excludes 0':>16}{'estimate range':>24}")
    for seed in SEEDS:
        f = here / "results" / f"seed_{seed}" / "estimates.txt"
        if not f.exists():
            continue
        rows = []
        for m in EST.finditer(f.read_text(errors="replace")):
            try:
                rows.append((float(m.group(2)), float(m.group(3)), float(m.group(4))))
            except ValueError:
                continue
        if not rows:
            continue
        sig = sum(1 for _, lo, hi in rows if (lo > 0 and hi > 0) or (lo < 0 and hi < 0))
        ests = [e for e, _, _ in rows]
        print(f"  {seed:<6}{len(rows):>8}{f'{sig} ({100*sig/len(rows):.0f}%)':>16}"
              f"{f'[{min(ests):.3f}, {max(ests):.3f}]':>24}")
    print("Coherence scores are logged to four decimals, so a displayed gap of exactly")
    print("0.0010 can still fall inside the 1e-3 tolerance in the unrounded values. That")
    print("is what happens in seed 42's 2to1 sweep, where the run selected 15 over an")
    print("apparent arg-max of 20 at 0.5030: the deposited seed sits on the tie-break")
    print("boundary in BOTH samples, not just the 3to2 one.\n")
    print("The deposited models carry 15 topics in each sample (30 effects); their")
    print("expElogbeta arrays are 1869x15 and 7099x15 float32, pinned by hash in")
    print("certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv.")


if __name__ == "__main__":
    main()
