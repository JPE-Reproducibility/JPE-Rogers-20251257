#!/usr/bin/env python3
"""Fail-closed candidate ZIP identity, safety, and reviewed-member verification."""
import argparse
import hashlib
import stat
import zipfile
from pathlib import PurePosixPath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--sha256", required=True)
    args = ap.parse_args()

    digest = hashlib.sha256()
    with open(args.zip, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    got = digest.hexdigest()
    if got != args.sha256.lower():
        raise SystemExit(f"ZIP SHA mismatch: expected {args.sha256}, got {got}")

    with zipfile.ZipFile(args.zip) as zf:
        bad_crc = zf.testzip()
        if bad_crc:
            raise SystemExit(f"ZIP CRC failure: {bad_crc}")
        infos = zf.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)):
            raise SystemExit("ZIP contains duplicate member names")
        files = []
        lowered = {}
        roots = set()
        for info in infos:
            name = info.filename
            p = PurePosixPath(name)
            if (not name or "\\" in name or p.is_absolute() or ".." in p.parts
                    or ":" in p.parts[0]):
                raise SystemExit(f"unsafe ZIP member: {name!r}")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise SystemExit(f"ZIP symlink member forbidden: {name}")
            low = name.lower()
            if low in lowered and lowered[low] != name:
                raise SystemExit(f"case-colliding ZIP members: {lowered[low]} / {name}")
            lowered[low] = name
            if not info.is_dir():
                files.append(name)
                if p.name == "run_all.py":
                    roots.add(str(p.parent))
        if len(roots) != 1:
            raise SystemExit(f"expected one package root containing run_all.py, found {sorted(roots)}")
        root = next(iter(roots))
        prefix = "" if root == "." else root.rstrip("/") + "/"
        rel_files = {n[len(prefix):] for n in files if n.startswith(prefix)}
        if len(rel_files) != len(files):
            raise SystemExit("ZIP contains files outside the unique package root")
        allow_name = prefix + "certification/PUBLIC_PACKAGE_ALLOWLIST.txt"
        try:
            text = zf.read(allow_name).decode("utf-8")
        except KeyError:
            raise SystemExit("ZIP lacks PUBLIC_PACKAGE_ALLOWLIST.txt")
        allow = {line.strip() for line in text.splitlines()
                 if line.strip() and not line.startswith("#")}
        extra = sorted(rel_files - allow)
        missing = sorted(allow - rel_files)
        if extra or missing:
            raise SystemExit(
                f"ZIP/allowlist drift: extra={len(extra)} {extra[:8]}; "
                f"missing={len(missing)} {missing[:8]}"
            )
    print(f"PASS: ZIP SHA/CRC/path/symlink/root/allowlist checks; {len(rel_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
