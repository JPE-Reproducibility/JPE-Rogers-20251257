#!/usr/bin/env python3
"""Fail-closed verification that the MAUDE manufacturer list rebuilds from shipped inputs.

data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv is a two-column projection of the 23
public FDA MAUDE device files under data/raw/MAUDE/device_data/. It is omitted from the
public package for its size (306 MB); nothing in it is restricted. This script rebuilds it
from those shipped files and checks the result against the digest of the deposited input, so
the omission is verifiable rather than asserted.

The source-file concatenation order is pinned in MAUDE_MFR_SOURCE_ORDER.txt: the deposited
vintage was written by a notebook that iterated os.listdir() without sorting, and the order
matters because gen_07 takes drop_duplicates("MANUFACTURER_D_NAME") (keep-first) before the
dedupe, so a differently ordered rebuild holds identical content but may cluster differently.

  python3 certification/verify_maude_manufacturer_rebuild.py --root .
  python3 certification/verify_maude_manufacturer_rebuild.py --root . --inputs-only
"""
import argparse
import csv
import hashlib
from pathlib import Path

EXPECTED_SHA256 = "8833a9a01599c145f84274cfabdf9d9d87ac8ddd897115d7a428ed28dd768f19"
EXPECTED_ROWS = 9238809
EXPECTED_BYTES = 305836795
TARGET = "data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv"
COLUMNS = ["MDR_REPORT_KEY", "MANUFACTURER_D_NAME"]


def load_order(path):
    if not path.is_file():
        raise SystemExit(f"missing source-order manifest: {path}")
    names = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]
    if len(names) != len(set(names)) or not names:
        raise SystemExit(f"source-order manifest is empty or has duplicates: {path}")
    return names


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_inputs(root, order):
    """Every source file must match the sha256 pinned for the public inputs."""
    pinned = {}
    with (root / "certification" / "PUBLIC_INPUT_HASHES.csv").open(encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if len(row) >= 2 and not row[0].lstrip().startswith("#"):
                pinned[row[0].strip()] = row[1].strip()
    device_dir = root / "data" / "raw" / "MAUDE" / "device_data"
    failures = []
    for name in order:
        path = device_dir / name
        rel = f"data/raw/MAUDE/device_data/{name}"
        if not path.is_file() or path.is_symlink():
            failures.append(f"{rel}: missing or symlinked")
            continue
        if rel not in pinned:
            failures.append(f"{rel}: not pinned in PUBLIC_INPUT_HASHES.csv")
            continue
        got = sha256_file(path)
        if got != pinned[rel]:
            failures.append(f"{rel}: sha256 {got} != pinned {pinned[rel]}")
    if failures:
        raise SystemExit("source inputs failed verification:\n  " + "\n  ".join(failures))
    return len(order)


class Sha256Sink:
    """Text sink so to_csv can be digested without materializing 306 MB."""

    def __init__(self):
        self._digest = hashlib.sha256()
        self.length = 0

    def write(self, chunk):
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        self._digest.update(chunk)
        self.length += len(chunk)
        return len(chunk)

    def hexdigest(self):
        return self._digest.hexdigest()


def rebuild(root, order):
    import pandas as pd

    device_dir = root / "data" / "raw" / "MAUDE" / "device_data"
    frames = []
    for name in order:
        frames.append(pd.read_csv(str(device_dir / name), encoding="ISO-8859-1",
                                  on_bad_lines="skip", sep="|", usecols=COLUMNS))
    frame = pd.concat(frames, ignore_index=True)[COLUMNS]
    sink = Sha256Sink()
    frame.to_csv(sink, index=False, lineterminator="\n")
    return len(frame), sink.length, sink.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--inputs-only", action="store_true",
                        help="verify the 23 source files against their pinned hashes and stop")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    order = load_order(root / "certification" / "MAUDE_MFR_SOURCE_ORDER.txt")

    n_inputs = check_inputs(root, order)
    if args.inputs_only:
        print(f"PASS: {n_inputs}/{n_inputs} MAUDE source files match PUBLIC_INPUT_HASHES.csv "
              "(rebuild not attempted: --inputs-only)")
        return 0

    rows, nbytes, got = rebuild(root, order)
    problems = []
    if rows != EXPECTED_ROWS:
        problems.append(f"rows {rows:,} != expected {EXPECTED_ROWS:,}")
    if nbytes != EXPECTED_BYTES:
        problems.append(f"bytes {nbytes:,} != expected {EXPECTED_BYTES:,}")
    if got != EXPECTED_SHA256:
        problems.append(f"sha256 {got} != expected {EXPECTED_SHA256}")
    if problems:
        raise SystemExit(
            f"rebuild of {TARGET} does not reproduce the deposited input:\n  "
            + "\n  ".join(problems)
            + "\nThe dedupe downstream of this file is order-sensitive, so a rebuild that does "
              "not reproduce the digest must not be substituted for it. Check that pandas is "
              "the pinned 2.3.3 -- the parse drops malformed source lines."
        )

    # If the deposited input is present, confirm the on-disk copy too.
    deposited = root / TARGET
    if deposited.is_file() and not deposited.is_symlink():
        on_disk = sha256_file(deposited)
        if on_disk != EXPECTED_SHA256:
            raise SystemExit(f"deposited {TARGET} has sha256 {on_disk}, expected {EXPECTED_SHA256}")
        where = "rebuild and deposited copy both match"
    else:
        where = "deposited copy absent; rebuild matches the pinned digest"

    print(f"PASS: {TARGET} rebuilt byte-identically from {n_inputs} shipped source files "
          f"({rows:,} rows, {nbytes:,} B, sha256 {got[:12]}...); {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
