#!/usr/bin/env python3
"""Manufacturer -> CRSP/Compustat linkage coverage behind the firm-size sentence in the
data section (tex:305): "working down the report-count ranking: the 300 largest reporters
account for 84 percent of all reports, of which 88 are private firms with no public-firm
match and the remainder are linked by automated name clustering with hand-coded
corrections."

WHY THIS EXISTS
---------------
No shipped program selected a top-N set of manufacturers, so a reader auditing the code
found 70 hand-coded patterns in data/raw/manual_permno_corrections.csv and no "300"
anywhere, and the sentence looked like a rule the package does not implement. The
selection was real -- the author worked down the MAUDE report-count ranking -- and 70
patterns cover the top 300 because most of the 300 either need no hand-coded line at all
(the dedupe + CRSP merge already links them, or they are private firms with no public-firm
match) or are caught by a pattern that also catches their siblings.

This module emits that reconciliation as a shipped table, and step 35
(15_intext_derived_numbers.py) registers the three numbers the manuscript prints --
top_n, top_n_report_share_pct, top_n_unlinked -- so the fail-closed in-text gate checks
them against this table from now on.

OUTPUT
------
output/tables/manufacturer_linkage_coverage.csv -- one row per metric:
    metric, value, description

DISCLOSURE NOTE
---------------
Manufacturer names and report counts come from MAUDE, which is public. The CRSP/Compustat
permno values are licensed and are NOT written here: only counts and coverage flags
derived from them are reported.

INPUTS (already in the package; the synthetic route materialises its twins to the same
two paths, so this runs on both routes)
    data/derived/all_adv_events_w_permno5.csv   (clean_name, permno, manually_encoded)
    data/raw/manual_permno_corrections.csv      (the hand-coded `contains` patterns)

The pattern semantics here mirror _apply_manual_corrections() in
code/00_generate_data/gen_07_adverse_permno.py exactly: `contains` is a JSON string or a
JSON list of substrings that must ALL appear (pandas .str.contains is a regex search, so
re.search is used here), and `not_contains` excludes. gen_07's ordering guard and `undo`
rows decide which correction wins for a given row; they are deliberately NOT replayed
here, because the question this table answers is "which of the top 300 names does each
hand-coded line reach", not "which line won". The hand-assigned count below comes from
gen_07's own `manually_encoded` flag, so it does reflect the guard.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

TOP_N = 300
CHUNK = 750_000

EVENTS_REL = Path("data") / "derived" / "all_adv_events_w_permno5.csv"
CORRECTIONS_REL = Path("data") / "raw" / "manual_permno_corrections.csv"
OUTPUT_REL = Path("output") / "tables" / "manufacturer_linkage_coverage.csv"


def _accumulate(events_path: Path):
    """Stream the event file, holding only per-name counters (keeps memory flat)."""
    counts: Counter = Counter()
    linked: dict[str, bool] = {}
    manual: dict[str, bool] = {}
    cols = ["clean_name", "permno", "manually_encoded"]
    for chunk in pd.read_csv(events_path, usecols=cols, chunksize=CHUNK, low_memory=False):
        chunk["clean_name"] = chunk["clean_name"].astype(str).str.lower()
        counts.update(chunk["clean_name"].value_counts().to_dict())
        grouped = chunk.groupby("clean_name").agg(
            has_permno=("permno", lambda s: s.notna().any()),
            has_manual=("manually_encoded", lambda s: (s == 1).any()),
        )
        for name, row in grouped.iterrows():
            linked[name] = linked.get(name, False) or bool(row.has_permno)
            manual[name] = manual.get(name, False) or bool(row.has_manual)
    return counts, linked, manual


def load_patterns(corrections_path: Path):
    """The hand-coded lines, parsed the way gen_07 parses them."""
    out = []
    with open(corrections_path, newline="") as fh:
        for row in csv.DictReader(fh):
            contains = json.loads(row["contains"])
            if isinstance(contains, str):
                contains = [contains]
            out.append({"contains": [str(c).lower() for c in contains],
                        "not_contains": (row.get("not_contains") or "").lower() or None})
    return out


def _line_matches(name: str, line: dict) -> bool:
    """gen_07's mask, for one name: every `contains` substring must appear (regex search,
    as pandas .str.contains does), and `not_contains` must not."""
    if not all(re.search(pat, name) for pat in line["contains"]):
        return False
    if line["not_contains"] and re.search(line["not_contains"], name):
        return False
    return True


def build_coverage(events_path: Path, corrections_path: Path | None = None) -> pd.DataFrame:
    counts, linked, manual = _accumulate(events_path)
    total_reports = sum(counts.values())
    top = [name for name, _ in counts.most_common(TOP_N)]
    top_reports = sum(counts[n] for n in top)

    n_linked = sum(linked.get(n, False) for n in top)
    n_manual = sum(manual.get(n, False) for n in top)
    n_auto = n_linked - n_manual
    n_unlinked = len(top) - n_linked

    rows = [
        # --- the three values the manuscript prints at tex:305 -------------------
        ("top_n", TOP_N,
         "Rank cut the manuscript describes: the largest MAUDE-reporting manufacturers"),
        ("top_n_report_share_pct", round(100 * top_reports / total_reports, 1) if total_reports else "",
         f"Share of all reports accounted for by the top {TOP_N} names"),
        ("top_n_unlinked", n_unlinked,
         f"Of the top {TOP_N}, names with no public-firm match (private manufacturers)"),
        # --- the universe those three are cut from -------------------------------
        ("maude_reports", total_reports,
         "MAUDE reports in the manufacturer-linked event file"),
        ("distinct_manufacturer_names", len(counts),
         "Distinct cleaned manufacturer names in that file"),
        ("top_n_linked_to_permno", n_linked,
         f"Of the top {TOP_N}, names linked to a CRSP/Compustat permno by any route"),
        ("top_n_linked_automatically", n_auto,
         f"Of the top {TOP_N}, names the dedupe + CRSP merge linked with no hand-coded line"),
        ("top_n_hand_assigned", n_manual,
         f"Of the top {TOP_N}, names carrying a hand-coded assignment (gen_07's "
         "manually_encoded flag)"),
    ]

    if corrections_path is not None and Path(corrections_path).exists():
        lines = load_patterns(Path(corrections_path))
        per_line = [sum(1 for n in top if _line_matches(n, ln)) for ln in lines]
        covered = {n for n in top for ln in lines if _line_matches(n, ln)}
        widest = max(zip(per_line, [",".join(ln["contains"]) for ln in lines]),
                     default=(0, ""))
        rows += [
            ("hand_coded_lines", len(lines),
             "Rows in data/raw/manual_permno_corrections.csv -- substring patterns, not firms"),
            ("top_n_names_covered_by_lines", len(covered),
             f"Top-{TOP_N} names matched by at least one hand-coded pattern"),
            ("names_per_hand_coded_line", round(len(covered) / len(lines), 1) if lines else "",
             f"Mean top-{TOP_N} names matched per hand-coded line"),
            ("widest_line_names_matched", widest[0],
             f"Top-{TOP_N} names matched by the broadest single pattern ('{widest[1]}')"),
        ]
    else:
        note = "not computed: data/raw/manual_permno_corrections.csv absent (restricted input)"
        rows += [("hand_coded_lines", "", note),
                 ("top_n_names_covered_by_lines", "", note),
                 ("names_per_hand_coded_line", "", note),
                 ("widest_line_names_matched", "", note)]

    return pd.DataFrame(rows, columns=["metric", "value", "description"])


def write_coverage(root: Path, events_path: Path | None = None, quiet: bool = False) -> Path:
    """Build the table and write it to output/tables/. Returns the path written."""
    root = Path(root)
    events = Path(events_path) if events_path is not None else root / EVENTS_REL
    corrections = root / CORRECTIONS_REL
    if not events.exists():
        raise FileNotFoundError(f"manufacturer linkage coverage needs {events}")
    df = build_coverage(events, corrections)
    out_path = root / OUTPUT_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    if not quiet:
        for _, r in df.iterrows():
            print(f"    {r['metric']:32s} {str(r['value']):>12}   {r['description']}")
        print(f"    Saved: {out_path}")
    return out_path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    print("=== manufacturer_linkage_coverage ===")
    write_coverage(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
