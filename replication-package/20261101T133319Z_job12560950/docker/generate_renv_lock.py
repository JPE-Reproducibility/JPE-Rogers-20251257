#!/usr/bin/env python3
"""
generate_renv_lock.py -- write docker/renv.lock as a RECORD of an R library.

Input, in this order of preference:
  1. docker/container_r_library.tsv -- the tab-separated (Package<TAB>Version)
     capture of the R library inside the built container image;
  2. r_requirements-lock.txt -- the same format for the macOS R 4.0.1 library
     that produced the deposited outputs, used only if (1) is absent.

WHAT THIS FILE IS NOT. The resulting docker/renv.lock is NOT restored anywhere.
docker/install_r_packages.R -- the only R install step the image runs -- never
reads it: there is no renv::restore() call in this package, and the R library in
the certified image was built by install.packages() from the base image's
repository plus three exact remotes::install_version() pins (fixest 0.10.4,
didimputation 0.3.0, did2s 0.4.0). The comment above the COPY in
docker/Dockerfile that says the image restores "the exact pinned library from
renv.lock" is inaccurate; that file is held byte-identical to the copy the
certified image was built from and so is not edited. The authoritative pin on
the R library is the image hash in certification/EXPECTED_SIF_SHA, and the
record of what that image contains is docker/container_r_library.tsv. See the
"R packages" section of the README and docker/DOCKER_GUIDE.md.

renv.lock is therefore useful for two things only: reading the recorded version
set in a standard format, and feeding renv::restore() yourself if you want to
attempt to rebuild a comparable library outside the image. Such a restore is not
part of any documented reproduction route and is not expected to reproduce the
image byte-for-byte.

Base/recommended R packages that ship with R itself are excluded -- they are
provided by the R installation, not installed from a repository.

Usage:
    python3 docker/generate_renv_lock.py            # writes docker/renv.lock
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(HERE)
# Prefer the ACTUAL in-image R library (captured from the built container) so
# the lockfile matches what the container reproduces with. Falls back to the
# macOS verified-library snapshot if the container capture is absent.
_CONTAINER = os.path.join(HERE, "container_r_library.tsv")
LOCK_IN = _CONTAINER if os.path.exists(_CONTAINER) else os.path.join(PKG_ROOT, "r_requirements-lock.txt")
LOCK_OUT = os.path.join(HERE, "renv.lock")

# R version the container installs against. The AUTHORITATIVE reference is
# R 4.0.1 + fixest 0.12.1 on macOS (byte-reproduces the deposit); this container
# uses R 4.1.3 (closest well-supported R) + fixest 0.10.4 from rocker's 2022
# snapshot as a near-identical CROSS-CHECK. Override with RENV_R_VERSION.
R_VERSION = os.environ.get("RENV_R_VERSION", "4.1.3")

# A dated Posit Public Package Manager snapshot gives reproducible *binary*
# Linux builds for the bulk of the tree; exact non-snapshot pins (e.g. fixest
# 0.12.1) fall back to the CRAN source archive during restore.
PPM_SNAPSHOT = os.environ.get(
    "RENV_PPM_SNAPSHOT", "https://p3m.dev/cran/__linux__/focal/2022-04-21"
)

# Authoritative pins for the estimation-critical packages (from README §R).
# r_requirements-lock.txt is DEDUPLICATED to the canonical loaded versions: a
# package present in both the framework library (stale) and the user library
# (canonical, loaded first) appears once. These overrides pin the container's
# verified cross-check versions.
# When generated from container_r_library.tsv these are already correct; the
# overrides only matter for the fallback (macOS r_requirements-lock.txt, which
# is the authoritative single-version lock). Container (cross-check) estimator =
# fixest 0.10.4; the authoritative reference estimator is fixest 0.12.1.
CRITICAL_OVERRIDES = {
    "fixest": "0.10.4",
    "didimputation": "0.3.0",
    "did2s": "0.4.0",
}


def _version_key(v):
    """Sort key for R-style versions ('1.17.2', '1.4-5', '0.11.2.4.0')."""
    parts = v.replace("-", ".").split(".")
    key = []
    for p in parts:
        try:
            key.append((1, int(p)))
        except ValueError:
            key.append((0, p))
    return key


# Packages bundled with R (base + recommended): provided by the R install,
# never restored from a repository.
BASE_PKGS = {
    "base", "compiler", "datasets", "grDevices", "graphics", "grid",
    "methods", "parallel", "splines", "stats", "stats4", "tcltk", "tools",
    "translations", "utils",
}
RECOMMENDED_PKGS = {
    "boot", "class", "cluster", "codetools", "foreign", "KernSmooth",
    "lattice", "MASS", "Matrix", "mgcv", "nlme", "nnet", "rpart", "spatial",
    "survival",
}
SKIP = BASE_PKGS | RECOMMENDED_PKGS


def main():
    packages = {}
    with open(LOCK_IN) as fh:
        header = fh.readline()  # "Package\tVersion"
        for line in fh:
            line = line.rstrip("\n")
            if not line or "\t" not in line:
                continue
            name, version = line.split("\t", 1)
            name, version = name.strip(), version.strip()
            if not name or name in SKIP:
                continue
            # On a duplicate, keep the newer version (= user-lib canonical).
            prev = packages.get(name)
            if prev and _version_key(prev["Version"]) >= _version_key(version):
                continue
            packages[name] = {
                "Package": name,
                "Version": version,
                "Source": "Repository",
                "Repository": "CRAN",
            }

    # Force the estimation-critical pins to the verified versions.
    for name, version in CRITICAL_OVERRIDES.items():
        packages[name] = {
            "Package": name, "Version": version,
            "Source": "Repository", "Repository": "CRAN",
        }

    lock = {
        "R": {
            "Version": R_VERSION,
            "Repositories": [{"Name": "CRAN", "URL": PPM_SNAPSHOT}],
        },
        "Packages": dict(sorted(packages.items())),
    }
    with open(LOCK_OUT, "w") as fh:
        json.dump(lock, fh, indent=2)
        fh.write("\n")
    print(f"Wrote {LOCK_OUT}: {len(packages)} packages pinned "
          f"(R {R_VERSION}, repo {PPM_SNAPSHOT})")


if __name__ == "__main__":
    main()
