#!/usr/bin/env python3
"""Compare independently generated synthetic payloads against the shipped payload."""
import argparse
import hashlib
import os
from pathlib import Path

EXTENSIONS = {".csv", ".parquet", ".xlsx"}


def inventory(root):
    root = Path(root).resolve()
    if not root.is_dir() or root.is_symlink():
        raise SystemExit(f"payload is missing, not a directory, or a symlink: {root}")
    values = {}
    for dirpath, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            if (Path(dirpath) / name).is_symlink():
                raise SystemExit(f"symlink in payload: {Path(dirpath) / name}")
        for name in files:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            if path.suffix.lower() not in EXTENSIONS:
                raise SystemExit(f"unsupported payload file: {rel}")
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(block)
            values[rel] = digest.hexdigest()
    if not values:
        raise SystemExit(f"empty payload: {root}")
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shipped", required=True)
    parser.add_argument("--generation-one", required=True)
    parser.add_argument("--generation-two", required=True)
    parser.add_argument("--expected", required=True)
    args = parser.parse_args()
    expected = {
        line.strip().removeprefix("simulated_data/")
        for line in Path(args.expected).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    if not expected:
        raise SystemExit("expected payload inventory is empty")
    payloads = {
        "shipped": inventory(args.shipped),
        "generation_one": inventory(args.generation_one),
        "generation_two": inventory(args.generation_two),
    }
    problems = []
    for label, values in payloads.items():
        if set(values) != expected:
            problems.append(
                f"{label}: missing={sorted(expected - set(values))[:20]} "
                f"extra={sorted(set(values) - expected)[:20]}"
            )
    baseline = payloads["shipped"]
    for label in ("generation_one", "generation_two"):
        different = sorted(path for path in expected if payloads[label].get(path) != baseline.get(path))
        if different:
            problems.append(f"{label}: {len(different)} hash difference(s): {different[:20]}")
    if problems:
        raise SystemExit("payload identity failed:\n  " + "\n  ".join(problems))
    print(f"PASS: {len(expected)} files; two clean generations are byte-identical to each other "
          "and to the shipped simulated_data payload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
