#!/usr/bin/env python3
"""Regenerate / verify the three expected-output hash manifests:

  certification/EXPECTED_EXHIBIT_HASHES.csv        (figures + tables)
  certification/EXPECTED_INTERMEDIATE_HASHES.csv   (intermediate CSVs)
  certification/EXPECTED_MODEL_ARTIFACT_HASHES.csv (model artifacts)

Each manifest lists `output_file,sha256,bytes,lines_if_text` for a FIXED set of package outputs.
The FIXED set is pinned by a canonical PATH inventory shipped alongside each manifest
(`EXPECTED_*_PATHS.txt`), so swapping one declared output for a different valid output/ file is
caught even when the row count is preserved.

  * FINAL CERTIFICATION runs this in --write mode (after the certified real-data run) to refresh
    the manifests from the exact outputs that will ship.
  * THE BUILD runs it in verify mode (default) and ABORTS on any discrepancy.

Two of the three manifests cover files under output/. EXPECTED_MODEL_ARTIFACT_HASHES.csv covers the
editable draw.io master of the one non-scripted schematic, which is a package SOURCE asset and lives
under manual_figures/ -- it is not produced by a run and must not sit in output/, where it would
appear as an unaccounted extra in the output comparison. Each manifest therefore declares the single
directory its paths must stay under (MANIFEST_ROOTS). The run-time integrity check for FROZEN INPUTS
that live under data/derived/ (the three precomputed safety artifacts reused on the real-data route)
is kept in a SEPARATE manifest, certification/EXPECTED_FROZEN_INPUT_HASHES.csv, verified by
run_all.verify_frozen_artifact_integrity -- NOT by this script. Keeping data/derived paths out of the
three manifests preserves the invariant enforced below that every declared path resolves under its
manifest's declared root (see _safe_rel / _resolved_ok).

Fail-closed:
  * CANONICAL PATHS: the manifest's path set must equal the canonical inventory exactly, in BOTH
    modes. Adding or removing a governed output is a deliberate act, so --write refuses a path-set
    change unless --allow-path-set-change is passed, and then names every path it adds or removes.
    A plain --write re-pins the sha256 of the SAME set of outputs and names every one whose
    content changed.
  * strict schema: sha256 = 64 lowercase hex; bytes = non-negative int; lines_if_text = int or
    empty; exactly the 4 declared columns; safe UNIQUE paths under the manifest's declared root
    (no abs/'..'/backslash).
  * each declared output is a REGULAR FILE (no symlink) whose realpath stays under that root.
  * full verification of sha256 AND bytes AND (for text) line count against the file on disk.
  * --write validates the regenerated content FIRST and only then writes ATOMICALLY (temp +
    os.replace), so a failed refresh never mutates the manifest.

Usage:
  python3 certification/refresh_expected_output_hashes.py            # verify; exit 1 on any issue
  python3 certification/refresh_expected_output_hashes.py --write    # re-pin the SAME output set
  python3 certification/refresh_expected_output_hashes.py --write --allow-path-set-change
                                                                    # after editing EXPECTED_*_PATHS.txt
"""
import csv
import hashlib
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIELDS = ["output_file", "sha256", "bytes", "lines_if_text"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TEXT_EXTS = (".csv", ".tex", ".txt")

MANIFESTS = {
    "EXPECTED_EXHIBIT_HASHES.csv": "EXPECTED_EXHIBIT_PATHS.txt",
    "EXPECTED_INTERMEDIATE_HASHES.csv": "EXPECTED_INTERMEDIATE_PATHS.txt",
    "EXPECTED_MODEL_ARTIFACT_HASHES.csv": "EXPECTED_MODEL_ARTIFACT_PATHS.txt",
}

# The one directory each manifest's paths must stay under. Anything else is rejected as
# unsafe/out-of-tree, exactly as before -- this only says WHICH directory, per manifest.
MANIFEST_ROOTS = {
    "EXPECTED_EXHIBIT_HASHES.csv": "output/",
    "EXPECTED_INTERMEDIATE_HASHES.csv": "output/",
    "EXPECTED_MODEL_ARTIFACT_HASHES.csv": "manual_figures/",
}


def _hash_and_meta(path):
    h = hashlib.sha256()
    nbytes = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            nbytes += len(chunk)
    lines = ""
    if path.lower().endswith(TEXT_EXTS):
        with open(path, "rb") as fh:
            lines = str(sum(1 for _ in fh))
    return h.hexdigest(), nbytes, lines


def _safe_rel(rel, root_prefix="output/"):
    return bool(rel) and not rel.startswith("/") and "\\" not in rel \
        and ".." not in rel.split("/") and rel.startswith(root_prefix)


def _load_canonical(inv_name, problems, root_prefix="output/"):
    p = os.path.join(HERE, inv_name)
    if not os.path.exists(p):
        problems.append(f"canonical path inventory not found: {inv_name}")
        return None
    paths, seen = set(), set()
    for i, raw in enumerate(open(p, encoding="utf-8"), 1):
        rel = raw.rstrip("\n")
        if not rel.strip():
            continue
        if not _safe_rel(rel, root_prefix):
            problems.append(f"{inv_name}:{i}: unsafe/out-of-tree canonical path {rel!r} "
                            f"(must be under {root_prefix})")
            continue
        if rel in seen:
            problems.append(f"{inv_name}:{i}: duplicate canonical path {rel!r}")
            continue
        seen.add(rel)
        paths.add(rel)
    return paths


def _read_rows(mpath, problems, root_prefix="output/"):
    with open(mpath, newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            problems.append(f"{os.path.basename(mpath)}: empty file (no header)")
            return []
        if header != FIELDS:
            problems.append(f"{os.path.basename(mpath)}: bad header {header!r} (expected {FIELDS})")
            return []
        rows, seen = [], set()
        for i, raw in enumerate(reader, start=2):
            if len(raw) != 4:
                problems.append(f"{os.path.basename(mpath)}:{i}: expected 4 columns, got {len(raw)}")
                continue
            rel, sha, nbytes, lines = raw
            if not _safe_rel(rel, root_prefix):
                problems.append(f"{os.path.basename(mpath)}:{i}: unsafe/out-of-tree path {rel!r} "
                                f"(must be under {root_prefix})")
                continue
            if rel in seen:
                problems.append(f"{os.path.basename(mpath)}:{i}: duplicate path {rel!r}")
                continue
            seen.add(rel)
            if not HEX64.match(sha):
                problems.append(f"{os.path.basename(mpath)}:{i}: sha256 not 64 lowercase hex ({rel})")
                continue
            if not re.match(r"^\d+$", nbytes) or (lines != "" and not re.match(r"^\d+$", lines)):
                problems.append(f"{os.path.basename(mpath)}:{i}: bad bytes/lines_if_text ({rel})")
                continue
            rows.append({"output_file": rel, "sha256": sha, "bytes": nbytes, "lines_if_text": lines})
    return rows


def _resolved_ok(rel, problems, manifest_name, root_prefix="output/"):
    """The declared file must be a regular, in-tree, non-symlink file (or reported missing)."""
    allowed_root = os.path.realpath(os.path.join(ROOT, root_prefix.rstrip("/")))
    fpath = os.path.join(ROOT, rel)
    if os.path.islink(fpath):
        problems.append(f"{manifest_name}: {rel} is a SYMLINK (forbidden)")
        return None
    if not os.path.exists(fpath):
        problems.append(f"{manifest_name}: MISSING OUTPUT {rel} (declared, not on disk)")
        return None
    if not os.path.isfile(fpath):
        problems.append(f"{manifest_name}: {rel} is not a regular file")
        return None
    rp = os.path.realpath(fpath)
    if os.path.commonpath([rp, allowed_root]) != allowed_root:
        problems.append(f"{manifest_name}: {rel} resolves OUTSIDE {root_prefix} ({rp})")
        return None
    return fpath


def process(manifest_name, inv_name, write, allow_path_set_change=False):
    mpath = os.path.join(HERE, manifest_name)
    problems = []
    if not os.path.exists(mpath):
        return [f"manifest not found: {mpath}"], 0
    root_prefix = MANIFEST_ROOTS[manifest_name]
    canonical = _load_canonical(inv_name, problems, root_prefix)
    rows = _read_rows(mpath, problems, root_prefix)
    row_paths = {r["output_file"] for r in rows}

    # CANONICAL PATH SET must match exactly (catches swapped/added/removed paths at fixed count).
    # This is enforced in BOTH modes. Changing the SET of governed outputs is a deliberate act: it
    # means the package now produces (or no longer produces) a manuscript-backing file, and it must
    # be visible in the diff of EXPECTED_*_PATHS.txt rather than absorbed by a refresh. --write
    # therefore refuses a path-set change unless --allow-path-set-change is passed, and it then
    # NAMES every added and removed path. (A --write that merely re-pins the sha256 of the SAME set
    # of outputs after a certified run needs no flag; the changed shas are printed.)
    if canonical is not None:
        added = sorted(canonical - row_paths)       # declared in the inventory, absent from manifest
        removed = sorted(row_paths - canonical)     # in the manifest, no longer declared
        if added or removed:
            if not write:
                for extra in removed:
                    problems.append(f"{manifest_name}: path not in canonical inventory: {extra}")
                for miss in added:
                    problems.append(f"{manifest_name}: canonical path missing from manifest: {miss}")
            elif not allow_path_set_change:
                for extra in removed:
                    problems.append(f"{manifest_name}: --write would REMOVE governed output {extra} "
                                    f"(it is no longer in {inv_name})")
                for miss in added:
                    problems.append(f"{manifest_name}: --write would ADD governed output {miss} "
                                    f"(newly declared in {inv_name})")
                problems.append(f"{manifest_name}: the declared output SET changed "
                                f"(+{len(added)} / -{len(removed)}). Re-run with "
                                f"--allow-path-set-change if that is intended.")
            else:
                for extra in removed:
                    print(f"  {manifest_name}: REMOVING governed output {extra} "
                          f"(--allow-path-set-change)")
                for miss in added:
                    print(f"  {manifest_name}: ADDING governed output {miss} "
                          f"(--allow-path-set-change)")

    if write and canonical is not None:
        by_path = {r["output_file"]: r for r in rows}
        rows = [by_path.get(rel, {"output_file": rel, "sha256": "", "bytes": "", "lines_if_text": ""})
                for rel in sorted(canonical)]

    new_rows = []
    for r in rows:
        rel = r["output_file"]
        fpath = _resolved_ok(rel, problems, manifest_name, root_prefix)
        if fpath is None:
            new_rows.append(r)
            continue
        sha, nbytes, lines = _hash_and_meta(fpath)
        if write:
            # Name every CONTENT change, so a refresh that silently re-pins a changed exhibit
            # cannot pass unnoticed in a build log.
            if r["sha256"] and r["sha256"] != sha:
                print(f"  {manifest_name}: CONTENT CHANGED, re-pinning {rel} "
                      f"({r['sha256'][:12]}… -> {sha[:12]}…)")
            new_rows.append({"output_file": rel, "sha256": sha,
                             "bytes": str(nbytes), "lines_if_text": lines})
        else:
            if sha != r["sha256"]:
                problems.append(f"HASH MISMATCH: {rel}")
            elif str(nbytes) != r["bytes"] or lines != r["lines_if_text"]:
                problems.append(f"META MISMATCH (bytes/lines): {rel}")

    if write:
        # VALIDATE-THEN-WRITE: only rewrite if the regenerated manifest is internally valid AND
        # matches the canonical inventory. Never mutate on failure; write atomically.
        new_paths = {r["output_file"] for r in new_rows}
        if canonical is not None and new_paths != canonical:
            problems.append(f"{manifest_name}: regenerated path set does not match canonical "
                            f"inventory -- refusing to write (update {inv_name} deliberately if the "
                            f"declared file set changed).")
        if problems:
            return problems, len(rows)
        d = os.path.dirname(mpath) or "."
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".exp_hashes_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", newline="") as fh:
                # LF line endings: the shipped manifests use "\n", and csv's default
                # "\r\n" would rewrite every byte of every manifest on the first --write.
                w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
                w.writeheader()
                w.writerows(new_rows)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, mpath)
        except Exception:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise
    return problems, len(rows)


def main():
    argv = sys.argv[1:]
    known = {"--write", "--allow-path-set-change"}
    unknown = [a for a in argv if a not in known]
    if unknown:
        print(f"unknown argument(s): {unknown}. Usage: refresh_expected_output_hashes.py "
              f"[--write [--allow-path-set-change]]")
        return 2
    write = "--write" in argv
    allow_path_set_change = "--allow-path-set-change" in argv
    if allow_path_set_change and not write:
        print("--allow-path-set-change only applies to --write.")
        return 2
    print(f"Expected-output hash manifests: {'REGENERATE' if write else 'VERIFY'}"
          f"{' (path-set change allowed)' if allow_path_set_change else ''}")
    all_problems, total_rows = [], 0
    for manifest, inv in MANIFESTS.items():
        p, n = process(manifest, inv, write, allow_path_set_change=allow_path_set_change)
        all_problems.extend(p)
        total_rows += n
    for msg in all_problems:
        print(f"  {msg}")
    if all_problems:
        print(f"\n{'REGENERATION' if write else 'EXPECTED-OUTPUT VERIFICATION'} FAILED: "
              f"{len(all_problems)} issue(s) across {total_rows} declared outputs "
              f"(manifests left unchanged).")
        return 1
    print(f"\nOK: {total_rows} declared outputs match the canonical inventory + their expected "
          f"sha256/bytes/lines; no symlink/out-of-tree paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
