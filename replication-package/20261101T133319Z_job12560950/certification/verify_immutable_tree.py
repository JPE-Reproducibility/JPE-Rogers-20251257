#!/usr/bin/env python3
"""Hash-bind all extracted package members outside the pipeline's mutable data/output trees."""
import argparse
import hashlib
import json
import os
from pathlib import Path

MUTABLE_PREFIXES = ("data/", "output/")


def collect(root):
    root = Path(root).resolve()
    values = {}
    for dirpath, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(dirpath) / name
            if path.is_symlink():
                raise SystemExit(f"symlink in extracted package: {path.relative_to(root)}")
        for name in files:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            if rel.startswith(MUTABLE_PREFIXES):
                continue
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(block)
            values[rel] = digest.hexdigest()
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    manifest = Path(args.manifest)
    current = collect(args.root)
    if args.write:
        manifest.write_text(json.dumps(current, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE: {len(current)} immutable-member hashes")
        return 0
    expected = json.loads(manifest.read_text(encoding="utf-8"))
    missing = sorted(set(expected) - set(current))
    extra = sorted(set(current) - set(expected))
    changed = sorted(path for path in set(expected) & set(current) if expected[path] != current[path])
    if missing or extra or changed:
        raise SystemExit(
            f"immutable tree changed: missing={missing[:20]} extra={extra[:20]} "
            f"changed={changed[:20]}"
        )
    print(f"PASS: {len(current)} immutable package members unchanged after certification run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
