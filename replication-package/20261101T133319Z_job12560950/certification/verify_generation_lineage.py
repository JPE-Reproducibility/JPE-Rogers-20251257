#!/usr/bin/env python3
"""verify_generation_lineage.py -- the CONSTRUCTION-PROOF lineage gate.
Non-disclosure is established by construction: every column of the CANONICAL synthetic payload
(synthetic_pipeline/simulated_data/, the files listed in MATERIALIZE_DESTINATIONS.tsv) is generated from a
NON-RESTRICTED source (committed parameters / public source), never copied from restricted data.
GENERATION_LINEAGE.csv records that mapping; this validator fails CLOSED if:

  * a canonical payload column has NO lineage row, a lineage row references a column not in the
    canonical payload (extra), a present payload file is UNREADABLE, or a materialized_destination is not in
    the reviewed materialization map (drift). A payload file ABSENT locally (generated at cycle) must carry a
    FILE-LEVEL lineage row; columns are enumerated at cycle.
  * a lineage row fails strict schema: source_kind not in the allowed non-restricted set, source_ref
    not a FOREIGN KEY into the reviewed input registry (GENERATION_INPUTS.csv), missing generator_ref,
    non-ISO review_date, or empty reviewer/transformation. A declaration alone is not a proof; these
    foreign keys + generator references bind it toward the actual generator (definitive binding is the
    instrumented clean-room run at cycle).

Content-detection heuristics are DEFENSE-IN-DEPTH, not proof: non-disclosure rests on the
construction recorded here. `--selftest` fixtures.
"""
import argparse
import csv
import os
import re
import sys

VALID_SOURCE_KIND = {"committed_param", "public", "synthesized"}
FIELDS = ["synthetic_file", "synthetic_column", "materialized_destination", "source_kind", "source_ref",
          "transformation", "generator_ref", "reviewer", "review_date"]
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FILE_LEVEL = "<generated-at-cycle>"


def _materialization_map(root):
    """-> {canonical_src: dest} from MATERIALIZE_DESTINATIONS.tsv (the reviewed source->dest map)."""
    mp = {}
    p = os.path.join(root, "certification", "MATERIALIZE_DESTINATIONS.tsv")
    if os.path.isfile(p):
        for line in open(p, encoding="utf-8"):
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    mp[parts[0].strip()] = parts[1].strip()
    return mp


def _input_registry(root):
    """The reviewed non-restricted input registry (GENERATION_INPUTS.csv) -- lineage source_ref must FK here."""
    reg = set()
    p = os.path.join(root, "certification", "GENERATION_INPUTS.csv")
    if os.path.isfile(p):
        for r in csv.DictReader(open(p, encoding="utf-8", newline="")):
            n = (r.get("input") or "").strip()
            if n:
                reg.add(n); reg.add(os.path.basename(n))
    return reg


def _hdr(path):
    import pandas as pd
    lp = path.lower()
    if lp.endswith(".parquet"):
        return list(pd.read_parquet(path).columns)
    if lp.endswith(".xlsx"):
        return list(pd.read_excel(path, nrows=0).columns)
    return list(pd.read_csv(path, nrows=0).columns)


# A lineage row whose reviewer field starts with this marker has been WRITTEN but not yet signed
# off by the author. It is not a schema violation -- the row is complete and honest -- but a sealed
# package may not contain one, so --final turns it into a hard failure and a non-final run reports
# it as a warning.
UNSIGNED_REVIEWER_PREFIX = "PENDING AUTHOR SIGN-OFF"


def _unsigned_rows(rows):
    """-> ['<file> :: <column>'] for every row still awaiting the author's sign-off."""
    out = []
    for r in rows:
        if (r.get("reviewer") or "").strip().upper().startswith(UNSIGNED_REVIEWER_PREFIX):
            out.append(f"{(r.get('synthetic_file') or '').strip()} :: "
                       f"{(r.get('synthetic_column') or '').strip()}")
    return out


def _validate(rows, canonical, registry, valid_dests):
    """rows: lineage dicts. canonical: {src_file: set(columns) | None-if-absent}. registry: FK set.
    valid_dests: set of dest paths from the map. -> [problems]."""
    problems = []
    have = {}   # src_file -> set(columns present in lineage)
    seen = set()
    for i, r in enumerate(rows, 1):
        f = (r.get("synthetic_file") or "").strip(); c = (r.get("synthetic_column") or "").strip()
        sk = (r.get("source_kind") or "").strip().lower()
        where = f"row {i} [{f} | {c}]"
        if not f or not c:
            problems.append(f"{where}: empty file/column"); continue
        if (f, c) in seen:
            problems.append(f"{where}: duplicate lineage row")
        seen.add((f, c)); have.setdefault(f, set()).add(c)
        # destination must be in the reviewed materialization map (no drift)
        dest = (r.get("materialized_destination") or "").strip()
        if dest not in valid_dests:
            problems.append(f"{where}: materialized_destination {dest!r} not in the reviewed materialization map")
        # strict schema + foreign keys
        if sk not in VALID_SOURCE_KIND:
            problems.append(f"{where}: source_kind {sk!r} not in {sorted(VALID_SOURCE_KIND)} (restricted forbidden)")
        if "restrict" in sk:
            problems.append(f"{where}: declares a RESTRICTED source -- forbidden by construction")
        ref = (r.get("source_ref") or "").strip()
        if ref not in registry and os.path.basename(ref) not in registry:
            problems.append(f"{where}: source_ref {ref!r} is not in the reviewed input registry (GENERATION_INPUTS.csv)")
        if not (r.get("generator_ref") or "").strip():
            problems.append(f"{where}: empty generator_ref (must name the generator file/function)")
        if not (r.get("transformation") or "").strip():
            problems.append(f"{where}: empty transformation")
        if not (r.get("reviewer") or "").strip():
            problems.append(f"{where}: empty reviewer")
        if not _ISO.match((r.get("review_date") or "").strip()):
            problems.append(f"{where}: review_date not ISO YYYY-MM-DD ({r.get('review_date')!r})")
    # EXACT set equality against the canonical payload columns
    for src, cols in canonical.items():
        if cols is None:   # absent locally -> must carry a FILE-LEVEL row
            if _FILE_LEVEL not in have.get(src, set()):
                problems.append(f"cycle-generated payload file has NO file-level lineage row: {src}")
            continue
        got = have.get(src, set()) - {_FILE_LEVEL}
        for c in sorted(cols - got):
            problems.append(f"canonical payload column has NO lineage row: {src} :: {c}")
        for c in sorted(got - cols):
            problems.append(f"lineage row references a column NOT in the canonical payload: {src} :: {c}")
    for f in sorted(set(have) - set(canonical)):
        problems.append(f"lineage row references a file NOT in the canonical payload: {f}")
    if not rows:
        problems.append("generation-lineage contract is empty")
    return problems


def _canonical_payload(root):
    """-> {src_file: set(columns) or None if absent locally}. UNREADABLE present files raise via the caller."""
    mp = _materialization_map(root)
    out = {}
    unreadable = []
    for src in mp:
        p = os.path.join(root, src)
        if not os.path.isfile(p):
            out[src] = None   # absent locally -> generated at cycle (file-level row required)
            continue
        try:
            out[src] = {str(c).strip() for c in _hdr(p)}
        except Exception:  # noqa: BLE001
            unreadable.append(src)
    return out, unreadable, set(mp.values())


def _selftest():
    fails = 0

    def check(name, rows, canonical, reg, dests, expect_ok):
        nonlocal fails
        probs = _validate(rows, canonical, reg, dests)
        ok = not probs
        good = ok == expect_ok
        print(f"  selftest {name}: {'OK' if good else 'FAIL'} (valid={ok}, expected={expect_ok})"
              f"{'' if good else ' :: '+str(probs[:2])}")
        if not good:
            fails += 1

    R = lambda **k: {**{f: "" for f in FIELDS}, **k}
    reg = {"simulation_parameters.json"}; dests = {"data/x.csv"}
    good = R(synthetic_file="sp/x.csv", synthetic_column="a", materialized_destination="data/x.csv",
             source_kind="synthesized", source_ref="simulation_parameters.json", transformation="drawn",
             generator_ref="build_simulation.py", reviewer="Parker Rogers", review_date="2026-09-09")
    canon = {"sp/x.csv": {"a"}}
    check("complete_passes", [good], canon, reg, dests, True)
    check("unmapped_column_fails", [good], {"sp/x.csv": {"a", "b"}}, reg, dests, False)
    check("extra_column_fails", [good, {**good, "synthetic_column": "z"}], canon, reg, dests, False)
    check("restricted_source_kind_fails", [{**good, "source_kind": "restricted"}], canon, reg, dests, False)
    check("bad_source_ref_fk_fails", [{**good, "source_ref": "totally invented public source"}], canon, reg, dests, False)
    check("bad_date_fails", [{**good, "review_date": "never-a-date"}], canon, reg, dests, False)
    check("dest_drift_fails", [{**good, "materialized_destination": "data/OTHER.csv"}], canon, reg, dests, False)
    check("missing_generator_ref_fails", [{**good, "generator_ref": ""}], canon, reg, dests, False)
    check("absent_file_needs_filelevel_row",
          [R(synthetic_file="sp/gen.csv", synthetic_column="<generated-at-cycle>", materialized_destination="data/g.csv",
             source_kind="synthesized", source_ref="simulation_parameters.json", transformation="cycle",
             generator_ref="materialize_simulation.py", reviewer="P", review_date="2026-09-09")],
          {"sp/gen.csv": None}, reg, {"data/g.csv"}, True)
    check("absent_file_without_row_fails", [], {"sp/gen.csv": None}, reg, {"data/g.csv"}, False)
    # the unsigned-reviewer marker: not a schema violation, but detectable for --final
    unsigned_row = {**good, "reviewer": f"{UNSIGNED_REVIEWER_PREFIX} (remediation)"}
    check("unsigned_reviewer_is_not_a_schema_violation", [unsigned_row], canon, reg, dests, True)
    for name, rows_, expect in (("unsigned_reviewer_detected", [unsigned_row], 1),
                                ("signed_reviewer_not_detected", [good], 0)):
        got = len(_unsigned_rows(rows_))
        ok = got == expect
        print(f"  selftest {name}: {'OK' if ok else 'FAIL'} (unsigned={got}, expected={expect})")
        if not ok:
            fails += 1
    print(f"LINEAGE_SELFTEST_FAILURES={fails}")
    return 0 if fails == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--final", action="store_true",
                    help="sealing a package: a lineage row still marked "
                         f"'{UNSIGNED_REVIEWER_PREFIX}' is a hard failure, not a warning")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    p = os.path.join(a.root, "certification", "GENERATION_LINEAGE.csv")
    if not os.path.isfile(p):
        print(f"FAIL: generation-lineage contract missing: {p}"); return 2
    rows = list(csv.DictReader(open(p, encoding="utf-8", newline="")))
    canonical, unreadable, valid_dests = _canonical_payload(a.root)
    problems = []
    for u in unreadable:   # an UNREADABLE present payload file is fatal, never skipped
        problems.append(f"canonical payload file is present but UNREADABLE (fatal): {u}")
    problems += _validate(rows, canonical, _input_registry(a.root), valid_dests)
    from collections import Counter
    print(f"canonical payload files={len(canonical)} lineage rows={len(rows)} "
          f"by_source_kind={dict(Counter((r.get('source_kind') or '').strip() for r in rows))}")
    unsigned = _unsigned_rows(rows)
    if unsigned and a.final:
        problems.append(
            f"{len(unsigned)} lineage row(s) still carry reviewer "
            f"'{UNSIGNED_REVIEWER_PREFIX}...': the author must review and sign them before a package "
            f"is sealed -- " + "; ".join(unsigned[:5]))
    if problems:
        print(f"GENERATION_LINEAGE_VIOLATIONS={len(problems)}")
        for pr in problems[:40]:
            print("  " + pr)
        return 1
    if unsigned:
        print(f"WARNING: GENERATION_LINEAGE_UNSIGNED_ROWS={len(unsigned)} "
              f"(reviewer = '{UNSIGNED_REVIEWER_PREFIX}...'). The contract is complete, but these rows "
              f"are not yet author-signed; --final refuses to pass while any remain:")
        for u in unsigned[:10]:
            print("  " + u)
    print("GENERATION_LINEAGE_VIOLATIONS=0 (every canonical payload column has a reviewed non-restricted lineage)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
