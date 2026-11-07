# syntax=docker/dockerfile:1
# Reproducible environment for the replication package.
#
# Clean-room cross-check of the toolchain: Python 3.9.13 + the freeze, and
# R 4.1.3 with fixest 0.10.4. NOTE: the AUTHORITATIVE reference environment is
# x86_64 R 4.0.1 + fixest 0.12.1 -- that loads under R 4.0.1 (the 0.12.1 binary
# is first on .libPaths) and BYTE-REPRODUCES the deposited tables. This image
# uses 0.10.4 because rocker/r-ver:4.1.3's 2022 snapshot ships it as a binary
# (the authoritative 0.12.1 binary loads and byte-reproduces under R 4.0.1)
# alongside the matching 2022-era set (Matrix 1.4,
# did 2.1.1, data.table 1.14); didimputation/BJS compiles cleanly. 0.10.4 here is
# a cross-check, not the authoritative estimator.
#
# REPRODUCTION SCOPE: substantive, not byte-exact. The manuscript was computed on
# macOS (Apple Accelerate BLAS); this Linux container uses OpenBLAS, so estimates
# match to ~0.1-0.6% (one ill-conditioned outcome ~3.6%). fixest version is NOT
# the cause -- 0.10.4 and 0.12.1 give identical in-container results. Byte-exact
# reproduction requires the original macOS env. See docker/DOCKER_GUIDE.md.
#
# Build (from the replication_package/ root):
#   docker build -f docker/Dockerfile -t fda-repro .          # native x86_64
#   DOCKER_BUILDKIT=1 docker build --platform linux/amd64 ... # Apple Silicon
# Run: see docker/DOCKER_GUIDE.md
#
# syntax=docker/dockerfile:1
ARG R_VERSION=4.1.3
# WS8 round-2 finding 9: the CERTIFIED image MUST pin the base by DIGEST (a mutable tag is not
# reproducible). Resolve the digest ONCE with:
#     docker buildx imagetools inspect rocker/r-ver:4.1.3      # -> Digest: sha256:<64hex>
# then build the certified image with:
#     docker build --build-arg BASE_REF=rocker/r-ver@sha256:<64hex> -f docker/Dockerfile -t fda-repro .
# and record that digest in the build evidence / evidence index. Dev builds may use the tag default.
ARG BASE_REF=rocker/r-ver:${R_VERSION}
FROM ${BASE_REF}

# ---------------------------------------------------------------------------
# System libraries: compilers (R source pkgs + Python build) and the -dev
# headers the tidyverse / ragg / textshaping / Python stack need.
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gfortran pkg-config \
      libcurl4-openssl-dev libssl-dev libxml2-dev libgit2-dev \
      libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
      libfreetype6-dev libpng-dev libtiff-dev libjpeg-dev \
      libgmp-dev libmpfr-dev libglpk-dev \
      zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
      libffi-dev liblzma-dev libncurses-dev tk-dev uuid-dev \
      wget curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# LaTeX toolchain -- required by the STRICT certified build (build_public_package
# --final), which compiles the manuscript as a MANDATORY gate. paper/build_manuscript.py
# runs pdflatex (-interaction=nonstopmode) + bibtex over 3 passes; JPE_submission_v8.tex
# (\documentclass{article}) pulls 35 packages spanning latex-base/recommended/extra,
# fonts-recommended/extra, pictures (tikz), and science. texlive-full is installed so the
# rebuild is ONE-SHOT with no missing-.sty iteration -- correctness over image size for a
# submission-grade reproduction image. (Leaner alternative if size ever matters: texlive-
# latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
# texlive-fonts-extra texlive-pictures texlive-science texlive-bibtex-extra latexmk.)
# ---------------------------------------------------------------------------
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends texlive-full \
 && rm -rf /var/lib/apt/lists/* \
 && pdflatex --version | head -1 && bibtex --version | head -1

# ---------------------------------------------------------------------------
# Python 3.9.13 -- the verified interpreter (built --enable-shared so rpy2 and
# the scientific stack link cleanly).
# ---------------------------------------------------------------------------
ARG PYTHON_VERSION=3.9.13
RUN cd /tmp \
 && wget -q https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
 && tar xzf Python-${PYTHON_VERSION}.tgz && cd Python-${PYTHON_VERSION} \
 && ./configure --enable-shared --prefix=/usr/local \
 && make -j"$(nproc)" && make altinstall && ldconfig \
 && cd / && rm -rf /tmp/Python-${PYTHON_VERSION}*
RUN ln -sf /usr/local/bin/python3.9 /usr/local/bin/python3 \
 && ln -sf /usr/local/bin/python3.9 /usr/local/bin/python \
 && python3 -m pip install --no-cache-dir --upgrade "pip==24.0" "setuptools<70" wheel

# ---------------------------------------------------------------------------
# R packages: restore the exact pinned library from renv.lock.
# ---------------------------------------------------------------------------
ENV RENV_PPM_SNAPSHOT=https://packagemanager.posit.co/cran/2025-05-15
COPY docker/renv.lock /opt/renv/renv.lock
COPY docker/install_r_packages.R /opt/renv/install_r_packages.R
RUN Rscript /opt/renv/install_r_packages.R

# ---------------------------------------------------------------------------
# Python packages: the exact transitive freeze.
# ---------------------------------------------------------------------------
COPY requirements-lock.txt /opt/py/requirements-lock.txt
# PySimpleGUI 4.47.0 was withdrawn from PyPI (the project went commercial and
# removed old releases). It is an interactive-GUI dependency of the dedupe
# labeler and is NOT imported by the headless pipeline, so it is filtered out.
# --no-deps: requirements-lock.txt is a complete `pip freeze`, so every
# transitive dependency is already pinned; installing with the resolver enabled
# makes pip reject the (self-consistent) set. --no-deps installs the exact
# frozen versions as-is.
RUN grep -viE '^(PySimpleGUI|pyreadstat)[=<>]' /opt/py/requirements-lock.txt > /tmp/reqs.txt \
 && python3 -m pip install --no-cache-dir --no-deps \
      --timeout 120 --retries 8 -r /tmp/reqs.txt
# torch from the freeze is the Linux CUDA build, which fails to import without
# nvidia-* libs (the macOS freeze has none). Re-install the CPU build (same
# version) so sentence-transformers/torch import in this CPU-only container --
# needed only by 06c/--regenerate-safety-embeddings (skipped by default). The
# macOS env was CPU too, so the CPU build matches it.
RUN python3 -m pip install --no-cache-dir --timeout 120 --retries 8 \
      torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu
# NLTK corpora used by the safety-text steps (06b/gen_07), baked in so the
# container runs offline.
ENV NLTK_DATA=/opt/nltk_data
# FATAL (WS8 round-2 finding 9): the corpus download must succeed AND every required corpus must be
# importable/openable, or the image build FAILS. The former `|| true` let the image build without the
# corpora the safety-text route (06b/gen_07) needs, a fail-open dependency.
# FATAL still, but ROBUST (CI build 2026-09-07): the plain `nltk.downloader` downloaded wordnet + omw-1.4
# but did NOT auto-unzip them (punkt/stopwords unzipped, wordnet/omw did not), so `find('corpora/wordnet')`
# raised "Resource wordnet not found" and the build failed. Fix: download each package with retries, then
# EXPLICITLY extract any package left as a .zip (via python's zipfile -- no unzip-binary dependency), then
# verify. Any failure is still fatal (the safety-text route 06b/gen_07 needs these corpora).
# R11 (2026-09-12): nltk 3.9.x (the pinned 3.9.2) loads sentence tokenization from `punkt_tab`, not the old
# pickled `punkt`. The image baked only `punkt`, so word_tokenize raised "Resource punkt_tab not found" in
# 06b/06c/11a under the network-denied capture (capture 10387019 validation). Earlier runs never noticed:
# they were not contained, and the scripts' own nltk.download("punkt_tab") silently fetched it into ~.
# punkt_tab is now baked and verified, and the build fails unless word_tokenize works offline.
RUN python3 - <<'PYEOF'
import nltk, zipfile, glob, os, sys
d = "/opt/nltk_data"
for pkg in ("punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"):
    ok = False
    for _ in range(3):
        try:
            if nltk.download(pkg, download_dir=d, quiet=True):
                ok = True
                break
        except Exception as e:
            print(f"nltk.download({pkg}) attempt error: {e}", file=sys.stderr)
    if not ok:
        sys.exit(f"FATAL: nltk.download failed for {pkg}")
# Some packages arrive as a .zip without being auto-unzipped -> extract every remaining zip so find() works.
for z in glob.glob(os.path.join(d, "**", "*.zip"), recursive=True):
    target = z[:-4]
    if not os.path.isdir(target):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(os.path.dirname(z))
        print(f"extracted {z}")
# Verify (fail-closed): every corpus must be findable AND usable.
nltk.data.path.insert(0, d)
for p in ("tokenizers/punkt", "tokenizers/punkt_tab/english", "corpora/stopwords", "corpora/wordnet",
          "corpora/omw-1.4"):
    nltk.data.find(p)
from nltk.corpus import stopwords, wordnet
assert stopwords.words("english") and wordnet.synsets("device"), "corpus present but unusable"
# Functional, offline: the exact call 06b/06c/11a make must work with no network.
assert nltk.word_tokenize("A device. Another sentence.") == ["A", "device", ".", "Another", "sentence", "."], \
    "word_tokenize unusable offline (punkt_tab missing?)"
print("NLTK corpora verified: punkt, punkt_tab, stopwords, wordnet, omw-1.4; word_tokenize works offline")
PYEOF

# ---------------------------------------------------------------------------
# Runtime environment: rpy2 loads the system R in-process.
# ---------------------------------------------------------------------------
ENV R_HOME=/usr/local/lib/R
ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib:/usr/local/lib
ENV MPLBACKEND=Agg

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# The replication package (code + data, incl. restricted inputs) is MOUNTED at
# run time, not baked into the image. See docker/DOCKER_GUIDE.md.
WORKDIR /replication
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["--help"]
