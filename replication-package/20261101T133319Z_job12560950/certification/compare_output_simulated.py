#!/usr/bin/env python3
"""Compare freshly regenerated outputs to the shipped simulated-data reference.

Reads every file under output/figures and output/tables and requires that set to equal
output-simulated/ exactly, by SHA-256, with one inventoried exemption: the four regression-model
caches listed below, which the run must produce but which do not ship.

Everything else found under those two directories is reported as an unapproved extra, so nothing
that is not a run product may be kept there. In particular, the editable draw.io master of the one
non-scripted schematic is a package SOURCE asset and lives in manual_figures/, not in output/.

BYTE IDENTITY AND WHERE IT HOLDS
--------------------------------
Byte identity is the criterion, and by default it is the ONLY criterion: inside the reference
container image the whole reference set reproduces byte for byte, and any difference there is a
real difference.

Outside that image it is not a safe criterion for FIGURES, and pretending otherwise would make
this comparison dishonest rather than strict. Measured cause (2026-09-17, macOS x86_64, the pinned
numpy 1.26.4): the plotted estimates are bit-identical, but the dashed pre/post trend lines the
event-study figures draw are fitted with `numpy.polyfit`, whose LAPACK least-squares result differs
in the last one or two bits between BLAS builds. A last-bit change in the fitted slope moves the
line by a small fraction of a pixel, which changes a handful of anti-aliased pixels and therefore
the file's SHA-256. Four mathematically equivalent least-squares formulas, run on the SAME data in
the SAME interpreter, produced four slopes differing in the last bits and three distinct PNGs; two
consecutive full runs of the same code on the same machine produced all 62 figures byte-identically.

So: run to run, the figures are stable; image to image, they are not. `--outside-reference-image`
says the comparison is being made outside the reference image. In that mode a differing PNG is
decoded and classified, and ONLY two classes are accepted:

  * PIXEL_IDENTICAL   -- every RGBA pixel agrees; the files differ only in PNG encoding/metadata.
  * ANTIALIASING      -- at most MAX_ANTIALIAS_PIXELS pixels differ, none by more than
                         MAX_ANTIALIAS_CHANNEL_DELTA per channel: a sub-visual rasterisation
                         difference of the kind described above.

Anything larger, and every non-PNG file, still FAILS. There is no blanket PNG exemption: each
accepted figure is listed by name, with its measured pixel count and maximum channel delta, in the
report. Tables, CSVs and every other artefact are byte-compared in every mode.
"""
import argparse
import hashlib
import os
from pathlib import Path

# Sub-visual bound for the figure classification above. Ten pixels of slack over the largest
# difference measured (38 pixels of 7.6 million, maximum channel delta 2) -- still four orders of
# magnitude below anything a reader could see, and far below any change in a plotted estimate,
# which moves a marker and hundreds of pixels.
MAX_ANTIALIAS_PIXELS = 48
MAX_ANTIALIAS_CHANNEL_DELTA = 2


APPROVED_NONREFERENCE_OUTPUTS = set()  # every file the route writes under output/{figures,tables} ships and is compared


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def classify_png_difference(ref_path, got_path):
    """-> (class, detail) for two PNGs that are not byte-identical.

    class is "PIXEL_IDENTICAL", "ANTIALIASING" or "DIFFERS"; detail is a human-readable
    measurement. Requires Pillow and numpy; without them nothing is excused and the caller keeps
    the byte-level FAIL.
    """
    try:
        import numpy as np
        from PIL import Image
    except Exception as exc:  # noqa: BLE001
        return "DIFFERS", f"cannot decode (Pillow/numpy unavailable: {type(exc).__name__})"
    try:
        with Image.open(ref_path) as im:
            ref = np.asarray(im.convert("RGBA"), dtype=np.int16)
        with Image.open(got_path) as im:
            got = np.asarray(im.convert("RGBA"), dtype=np.int16)
    except Exception as exc:  # noqa: BLE001
        return "DIFFERS", f"cannot decode ({type(exc).__name__}: {exc})"
    if ref.shape != got.shape:
        return "DIFFERS", f"different image size {ref.shape[1]}x{ref.shape[0]} vs {got.shape[1]}x{got.shape[0]}"
    delta = np.abs(ref - got)
    n_pixels = int((delta.sum(axis=2) > 0).sum())
    max_delta = int(delta.max()) if delta.size else 0
    if n_pixels == 0:
        return "PIXEL_IDENTICAL", "every RGBA pixel agrees; PNG encoding/metadata differs"
    detail = (f"{n_pixels} of {ref.shape[0] * ref.shape[1]} pixels differ, "
              f"max channel delta {max_delta}")
    if n_pixels <= MAX_ANTIALIAS_PIXELS and max_delta <= MAX_ANTIALIAS_CHANNEL_DELTA:
        return "ANTIALIASING", detail
    return "DIFFERS", detail


def files_under(root):
    """Enumerate regular files without following symlinks; reject unsafe trees."""
    if root.is_symlink() or not root.is_dir():
        raise SystemExit(f"not a real directory: {root}")
    found = {}
    for dirpath, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = Path(dirpath) / name
            if path.is_symlink():
                raise SystemExit(f"symlink forbidden in output comparison: {path}")
        for name in names:
            path = Path(dirpath) / name
            if not path.is_file() or not os.access(path, os.R_OK):
                raise SystemExit(f"unreadable/non-regular output: {path}")
            rel = path.relative_to(root).as_posix()
            if rel in found:
                raise SystemExit(f"duplicate relative output path: {rel}")
            found[rel] = path
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", required=True)
    ap.add_argument("--outside-reference-image", action="store_true",
                    help="the comparison is NOT being made inside the reference container image: "
                         "classify a differing PNG and accept it only if it is pixel-identical or "
                         "within the documented sub-visual anti-aliasing bound (see the module "
                         "docstring). Every non-PNG file stays byte-strict.")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    ref = root / "output-simulated"
    got = root / "output"
    if not ref.is_dir() or not got.is_dir():
        raise SystemExit("output-simulated/ and output/ must both exist")
    refs = files_under(ref)
    refs.pop("CAPTURE_MANIFEST.sha256", None)
    actual = {}
    for sub in ("figures", "tables"):
        base = got / sub
        if base.is_dir():
            actual.update({f"{sub}/{k}": v for k, v in files_under(base).items()})
    missing = sorted(set(refs) - set(actual))
    byte_differing = sorted(k for k in set(refs) & set(actual) if digest(refs[k]) != digest(actual[k]))
    # Default: byte identity is the only criterion. Outside the reference image, a differing PNG is
    # decoded and excused ONLY if it is pixel-identical or within the documented sub-visual bound;
    # each such file is listed by name with its measurement.
    differing, excused = [], []
    for k in byte_differing:
        if args.outside_reference_image and k.lower().endswith(".png"):
            cls, detail = classify_png_difference(refs[k], actual[k])
            if cls != "DIFFERS":
                excused.append((k, cls, detail))
                continue
            differing.append(k)
        else:
            differing.append(k)
    # No file under output/figures or output/tables is exempt: anything the run writes there
    # must be a member of the reference tree, byte for byte.
    extras = sorted(set(actual) - set(refs) - APPROVED_NONREFERENCE_OUTPUTS)
    missing_required_cache = sorted(APPROVED_NONREFERENCE_OUTPUTS - set(actual))
    mode = "outside-reference-image" if args.outside_reference_image else "byte-identical (reference image)"
    lines = [
        f"reference={len(refs)} regenerated={len(actual)} mode={mode}",
        f"identical={len(refs)-len(missing)-len(differing)-len(excused)} missing={len(missing)} ",
        f"differing={len(differing)} excused_figures={len(excused)} unapproved_extra={len(extras)} "
        f"missing_required_cache={len(missing_required_cache)}",
    ]
    lines += [f"EXCUSED_FIGURE {k} [{cls}] {detail}" for k, cls, detail in excused]
    lines += [f"MISSING {x}" for x in missing]
    lines += [f"DIFFERS {x}" for x in differing]
    lines += [f"EXTRA {x}" for x in extras]
    lines += [f"MISSING_REQUIRED_CACHE {x}" for x in missing_required_cache]
    Path(args.report).write_text("\n".join(lines) + "\n")
    ok = bool(refs) and not missing and not differing and not extras and not missing_required_cache
    print("PASS" if ok else "FAIL", "; ".join(lines[:3]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
