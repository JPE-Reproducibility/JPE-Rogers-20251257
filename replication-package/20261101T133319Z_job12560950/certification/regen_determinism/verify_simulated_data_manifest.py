#!/usr/bin/env python3
"""Portable, order-independent verification of the shipped synthetic-data SHA-256 manifest
(`certification/regen_determinism/simulated_data_sha256.txt`).

Unlike a `find | sort | shasum | diff` pipeline, this does NOT depend on shell-vs-Python
sort collation: it compares PATH SETS and recomputes hashes, so element order is irrelevant.

Checks (exits NONZERO on ANY discrepancy):
  - every `.csv` / `.parquet` / `.xlsx` under `synthetic_pipeline/simulated_data/` is present
    in the manifest, and vice-versa (reports `missing` = in manifest, not on disk; `extra` =
    on disk, not in manifest);
  - no duplicate paths in the manifest;
  - every file's recomputed SHA-256 equals the manifest hash.

Run from anywhere:
    python3 certification/regen_determinism/verify_simulated_data_manifest.py
Exit 0 = verified; exit 1 = discrepancy (details printed).
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "simulated_data_sha256.txt")
# package root = two levels up from certification/regen_determinism/
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SP = os.path.join(ROOT, "synthetic_pipeline")
SIM = os.path.join(SP, "simulated_data")
EXPECTED = os.path.join(HERE, "simulated_data_expected_files.txt")
EXTS = (".csv", ".parquet", ".xlsx")   # the ONLY permitted synthetic-data file types
HEX64 = re.compile(r"^[0-9a-f]{64}$")   # SHA-256 as exactly 64 lowercase hex chars


def load_expected():
    """The canonical set of relative paths (under synthetic_pipeline/) the simulation MUST contain.
    Shipped alongside the manifest so an empty/shrunk/inflated simulation fails against a FIXED
    expectation, not merely against a manifest regenerated from whatever files happen to exist.
    Parsed strictly (like the hash manifest): each line must be a safe relative simulated_data/
    path with a permitted extension, and DUPLICATES are reported (not silently collapsed).
    Returns (set-or-None, duplicate-list, malformed-(lineno,text)-list)."""
    if not os.path.exists(EXPECTED):
        return None, [], []
    expected, dups, malformed, seen = set(), [], [], set()
    with open(EXPECTED, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            rel = raw.rstrip("\n")
            if not rel.strip():
                continue
            if (rel != rel.strip() or rel.startswith("/") or "\\" in rel or ".." in rel.split("/")
                    or not rel.startswith("simulated_data/") or not rel.lower().endswith(EXTS)):
                malformed.append((lineno, rel[:80]))
                continue
            if rel in seen:
                dups.append(rel)
            seen.add(rel)
            expected.add(rel)
    return expected, dups, malformed


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(path):
    """Return (dict rel_path -> hash, list of duplicate rel_paths, list of malformed (lineno,text)).
    Each line MUST be exactly: 64 lowercase hex, two spaces, then a safe relative path under
    simulated_data/ (no absolute path, no backslash, no '..' component, permitted extension).
    Anything else is reported as malformed rather than parsed loosely."""
    mapping, dups, seen, malformed = {}, [], set(), []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            if not line:
                continue
            if len(line) < 67 or not HEX64.match(line[:64]) or line[64:66] != "  ":
                malformed.append((lineno, line[:80]))
                continue
            rel = line[66:]
            if (rel.startswith("/") or "\\" in rel or ".." in rel.split("/")
                    or not rel.startswith("simulated_data/")
                    or not rel.lower().endswith(EXTS)):
                malformed.append((lineno, line[:80]))
                continue
            if rel in seen:
                dups.append(rel)
            seen.add(rel)
            mapping[rel] = line[:64]
    return mapping, dups, malformed


def main():
    if not os.path.exists(MANIFEST):
        print(f"FAIL: manifest not found: {MANIFEST}")
        return 1
    # ROOT/PARENT-SYMLINK guard: os.walk(followlinks=False) still traverses when the START dir is
    # a symlink, and a symlinked PARENT (synthetic_pipeline/ -> /external) makes SIM itself non-link
    # while realpath still resolves outside the package. Reject BOTH simulated_data/ and
    # synthetic_pipeline/ being symlinks, and require SIM to resolve UNDER the real package root
    # (ROOT, measured WITHOUT resolving the possibly-symlinked synthetic_pipeline/).
    if os.path.islink(SIM):
        print(f"FAIL: simulated_data/ is itself a SYMLINK ({SIM} -> {os.readlink(SIM)}) -- forbidden")
        return 1
    if os.path.islink(SP):
        print(f"FAIL: synthetic_pipeline/ is itself a SYMLINK ({SP} -> {os.readlink(SP)}) -- forbidden")
        return 1
    if not os.path.isdir(SIM):
        print(f"FAIL: simulated_data not found: {SIM}")
        return 1
    _pkg_root = os.path.realpath(ROOT)
    if os.path.commonpath([os.path.realpath(SIM), _pkg_root]) != _pkg_root:
        print(f"FAIL: simulated_data/ resolves OUTSIDE the package root {_pkg_root}: "
              f"{os.path.realpath(SIM)}")
        return 1

    manifest, dups, malformed = parse_manifest(MANIFEST)
    man_set = set(manifest)
    expected, exp_dups, exp_malformed = load_expected()

    # Enumerate EVERY entry under simulated_data/ WITHOUT following symlinks. Permitted-extension
    # real files must match the manifest; any file with a non-permitted extension, and ANY symlink
    # (file or directory, even a permitted-looking one), is a fail-closed error (a symlink would
    # dereference to an external, possibly restricted, file).
    fs = set()
    unpermitted = []
    symlinks = []
    for dirpath, dirs, names in os.walk(SIM, followlinks=False):
        for d in dirs:
            if os.path.islink(os.path.join(dirpath, d)):
                symlinks.append(os.path.relpath(os.path.join(dirpath, d), SP).replace(os.sep, "/"))
        for n in names:
            full = os.path.join(dirpath, n)
            rel = os.path.relpath(full, SP).replace(os.sep, "/")
            if os.path.islink(full):
                symlinks.append(rel)
            elif n.lower().endswith(EXTS):
                fs.add(rel)
            else:
                unpermitted.append(rel)

    missing = sorted(man_set - fs)   # in manifest, not on disk
    extra = sorted(fs - man_set)     # on disk, not in manifest
    problems = 0

    # NONEMPTY + EXPECTED-INVENTORY: an empty simulation (0 files, empty manifest) must NOT pass.
    # Compare the filesystem AND manifest against the FIXED shipped inventory of expected paths,
    # so a shrunk/empty/inflated simulation fails against a canonical expectation.
    if not fs:
        problems += 1
        print("FAIL: simulated_data/ contains ZERO permitted files -- an empty simulation is not "
              "a valid deposit.")
    if exp_malformed:
        problems += len(exp_malformed)
        print(f"FAIL: {len(exp_malformed)} malformed line(s) in the expected inventory "
              f"(need a safe simulated_data/ path with a permitted extension):")
        for lineno, text in exp_malformed:
            print(f"  line {lineno}: {text!r}")
    if exp_dups:
        problems += len(exp_dups)
        print(f"FAIL: {len(exp_dups)} duplicate path(s) in the expected inventory:")
        for d in sorted(set(exp_dups)):
            print(f"  inventory-dup: {d}")
    if expected is None:
        problems += 1
        print(f"FAIL: expected-file inventory not found ({EXPECTED}); cannot confirm the exact "
              f"simulation file set.")
    elif not expected:
        problems += 1
        print(f"FAIL: expected-file inventory is empty ({EXPECTED}).")
    else:
        exp_missing = sorted(expected - fs)    # expected by inventory, not on disk
        exp_unexpected = sorted(fs - expected)  # on disk, not in the expected inventory
        man_vs_exp = sorted(man_set ^ expected)  # manifest disagrees with inventory (either way)
        if exp_missing:
            problems += len(exp_missing)
            print(f"FAIL: {len(exp_missing)} expected file(s) MISSING from simulated_data/:")
            for m in exp_missing:
                print(f"  expected-missing: {m}")
        if exp_unexpected:
            problems += len(exp_unexpected)
            print(f"FAIL: {len(exp_unexpected)} file(s) present but NOT in the expected inventory:")
            for e in exp_unexpected:
                print(f"  unexpected: {e}")
        if man_vs_exp:
            problems += len(man_vs_exp)
            print(f"FAIL: {len(man_vs_exp)} manifest path(s) disagree with the expected inventory:")
            for x in man_vs_exp:
                print(f"  manifest!=expected: {x}")

    if malformed:
        problems += len(malformed)
        print(f"FAIL: {len(malformed)} malformed manifest line(s) "
              f"(need 64 lowercase hex + two spaces + safe simulated_data/ path):")
        for lineno, text in malformed:
            print(f"  line {lineno}: {text!r}")
    if symlinks:
        problems += len(symlinks)
        print(f"FAIL: {len(symlinks)} symlink(s) under simulated_data/ (forbidden -- a symlink can "
              f"dereference to an external, possibly restricted, file):")
        for s in sorted(symlinks):
            print(f"  symlink: {s}")
    if unpermitted:
        problems += len(unpermitted)
        print(f"FAIL: {len(unpermitted)} file(s) under simulated_data/ with a NON-PERMITTED "
              f"extension (only {EXTS} may ship -- others bypass leakage inspection):")
        for u in sorted(unpermitted):
            print(f"  unpermitted: {u}")
    if dups:
        problems += len(dups)
        print(f"FAIL: {len(dups)} duplicate path(s) in manifest:")
        for d in sorted(set(dups)):
            print(f"  dup: {d}")
    if missing:
        problems += len(missing)
        print(f"FAIL: {len(missing)} manifest path(s) not on disk:")
        for m in missing:
            print(f"  missing: {m}")
    if extra:
        problems += len(extra)
        print(f"FAIL: {len(extra)} disk file(s) not in manifest:")
        for e in extra:
            print(f"  extra: {e}")

    bad = 0
    for rel in sorted(man_set & fs):
        got = sha256(os.path.join(SP, rel))
        if got != manifest[rel]:
            bad += 1
            print(f"FAIL: hash mismatch: {rel}\n  manifest={manifest[rel]}\n  actual  ={got}")
    problems += bad

    if problems:
        print(f"\nMANIFEST VERIFICATION FAILED: {problems} discrepancy(ies).")
        return 1
    print(f"OK: {len(man_set)} synthetic files verified "
          f"(matches the {len(expected)}-file expected inventory; path sets match; SHA-256 match; "
          f"no missing/extra/duplicate/symlink; simulated_data/ is a real in-package directory).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
