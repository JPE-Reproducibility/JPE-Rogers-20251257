# The reference container: obtaining it, rebuilding it, running in it

**Supporting reference; `README.md` governs.** Everything here is command detail
for the container environment `README.md` describes.

The reference environment for this package is a single container image. Inside
that image the pipeline's outputs are byte-identical to the deposited ones;
outside it they are not guaranteed to be (see section 6). The image is identified
by the SHA-256 of its Apptainer/Singularity `.sif` file, recorded in
`certification/EXPECTED_SIF_SHA`:

    b9f9ee2aea02c556475487668cf21fcccff0ef07cafd9369ce9100752b4d41a8  fda_np126.sif

Its conversion record, including the SHA-256 of each of the four recipe files the
image was built from, is in `certification/SIF_PROVENANCE.json`.

Its base image is pinned by digest:

    rocker/r-ver@sha256:96be237557b98e5d34957ed4fcbf386999981119086cd4b4cfbafd5c2a47a3f4   (= rocker/r-ver:4.1.3)

## 1. What is in the image

| Component | Version | How it is pinned |
|---|---|---|
| Base OS + R | `rocker/r-ver:4.1.3`, pinned by the digest above | `--build-arg BASE_REF=` |
| R | 4.1.3 | from the base image |
| Python | 3.9.13 | built from source in the Dockerfile |
| Python packages | the exact transitive freeze | `requirements-lock.txt`, installed with `--no-deps` and with `PySimpleGUI` (withdrawn from PyPI) and `pyreadstat` (not imported) filtered out; `torch==2.2.2` is then reinstalled from the PyTorch CPU index because the frozen wheel is the Linux CUDA build |
| numpy | 1.26.4 | in the freeze; the build fails if the image does not have it |
| fixest | **0.10.4** | resolved from the base image's repository; asserted at build time |
| didimputation / did2s | 0.3.0 / 0.4.0 | `remotes::install_version()`; asserted at build time |
| other R packages | see `docker/container_r_library.tsv` | **not** pinned — see section 5 |
| TeX Live | 2019 (`pdfTeX 3.14159265-2.6-1.40.20`) | `texlive-full` from the base image's Debian release |
| NLTK corpora | punkt, punkt_tab, stopwords, wordnet, omw-1.4 | baked into `/opt/nltk_data`; the build fails if `word_tokenize` does not work offline |

## 2. Obtaining the image

The certified image, `fda_np126.sif`, is deposited with this package, alongside the archive
rather than inside it. Check your copy with `sha256sum fda_np126.sif`; it must print the
value in `certification/EXPECTED_SIF_SHA`. That file is the only copy covered by the
byte-identity claims in `README.md`: a separately built or separately converted image is the
same software but is not byte-deterministic and will not match that value.

That file was converted with Apptainer 1.3.6 from an OCI image built from an immutable source
commit; `certification/SIF_PROVENANCE.json` holds the conversion record. Section 3 describes
rebuilding the image from the recipe if you cannot run the deposited one.

## 3. Rebuilding the image from the recipe

From the package root:

```bash
docker build \
  --build-arg BASE_REF=rocker/r-ver@sha256:96be237557b98e5d34957ed4fcbf386999981119086cd4b4cfbafd5c2a47a3f4 \
  -f docker/Dockerfile -t fda-repro .
```

On an Apple-silicon host, build the x86_64 image under emulation with the
daemon's BuildKit:

```bash
DOCKER_BUILDKIT=1 docker build --platform linux/amd64 \
  --build-arg BASE_REF=rocker/r-ver@sha256:96be237557b98e5d34957ed4fcbf386999981119086cd4b4cfbafd5c2a47a3f4 \
  -f docker/Dockerfile -t fda-repro .
```

Do **not** use the legacy builder with `--platform` (its intermediate images are
mis-tagged arm64) or a `buildx` docker-container builder (its QEMU fails on R's
`INSTALL` script).

`ARG BASE_REF` defaults to the floating tag `rocker/r-ver:4.1.3`. Always pass the
digest; the tag is mutable.

To convert a locally built image to a `.sif`:

```bash
docker save fda-repro -o fda-repro.tar
apptainer build fda_np126.sif docker-archive://fda-repro.tar
```

**Build time.** The only measured figure recorded in this package is "first build
~30–40 minutes, cached after". I have not re-measured it, and my own automated
build records no duration (its timeout is 300 minutes), so treat half an hour to
an hour on a fast machine with
a good network as the expectation: the build compiles CPython from source,
installs `texlive-full`, and installs about 200 R packages.

**A rebuilt image will not be byte-identical to the certified one.** The recipe is
not hermetic: every R package except the three asserted ones comes from live CRAN
at build time, TeX Live and the system libraries come from Debian mirrors,
CPython is downloaded from python.org, and the NLTK corpora are downloaded during
the build. A rebuild today therefore yields a different image hash and a
different R library than `docker/container_r_library.tsv` records. Byte-identity
of the outputs is certified only inside the exact image `b9f9ee2a…`. A rebuilt
image is expected to reproduce the results substantively; it is not covered by
the byte-identity claim.

The certified image was produced by a continuous-integration workflow in my own
repository, which pushes to my own registry namespace; the workflow's identity
and the SHA-256 of the file as it ran are recorded in
`certification/SIF_PROVENANCE.json`. That workflow is not a route a third party
can use; the `docker build` command above is.

## 4. Running the pipeline in the image

The image holds **only the environment**. The package is mounted at run time at
`/replication`:

```bash
PKG=/path/to/replication_package
docker run --rm -v "$PKG":/replication fda-repro <run_all.py flags>
```

Outputs land in the mounted `output/` and persist on the host. To leave the
deposited package untouched, run against a fresh extraction.

All of the package's own data, including the FDA adverse-event (MAUDE) inputs
under `data/raw/MAUDE/`, is public data shipped inside the package. Nothing has
to be mounted over it. The confidential inputs an authorized researcher would
supply for the real-data route are listed in `RESTRICTED_FILE_INVENTORY.csv` and
`DATA_INPUTS.md`.

Anything after the image name is passed straight to `run_all.py`. Do **not** pass
`--continue-on-fail`: a documented route must stop at the first failing step, and
a run that continued past a failure cannot be compared to the reference outputs.

### Simulated-data route (the route a replicator without the confidential data runs)

The certified form of this route is the harness
`certification/certify_fromraw_route.sh`, invoked as `README.md` documents
under "Route 1 -- the simulated-data route"; it takes the `.sif` and its SHA-256 and runs everything
inside the image itself. The underlying steps, which the harness runs for you,
are:

```bash
PYTHONHASHSEED=0 python3 synthetic_pipeline/build_simulation.py --output-dir /fresh/generated
python3 synthetic_pipeline/materialize_simulation.py --for-gen-run --source-dir /fresh/generated
python3 synthetic_pipeline/preflight_from_raw.py
python3 run_all.py --synthetic-from-raw --clean-output \
    --regenerate-safety-keywords --regenerate-safety-embeddings
python3 certification/compare_output_simulated.py --root . --report output/compare_report.txt
```

`run_all.py` sets `PYTHONHASHSEED=0`, single-threaded BLAS/OpenMP, the
package-owned matplotlib/XDG/NLTK cache directories and the strict in-text
settings for every step, so no environment variables need to be exported.
`--clean-output` empties `output/figures` and `output/tables` first; without it
the route refuses to start while either holds a file.

**Comparison target:** the deposited `output-simulated/` tree, compared with
`certification/compare_output_simulated.py`. Do not compare this route's results
to the deposited `output/`: `output/` holds the real-data results, and the
simulated values differ from them by design.

### Real-data route (authorized researchers only)

With the confidential inputs in place:

```bash
docker run --rm -v "$PKG":/replication fda-repro --skip-gen --force-estimation --strict-cert
```

**Comparison target:** the deposited `output/` tree.

## 5. The R library: what is actually pinned

`docker/install_r_packages.R` is the only R install step the image runs. It:

* installs `fixest`, `data.table`, `tidyverse`, `extrafont`, `sandwich`,
  `broom`, `lmtest`, `BMisc`, `Rcpp`, `RcppArmadillo` and `did` with a plain
  `install.packages()` from whatever `getOption("repos")` the base image sets —
  **no versions requested**;
* installs `didimputation` 0.3.0 and `did2s` 0.4.0 with
  `remotes::install_version(..., dependencies = TRUE)` against that repository
  plus live CRAN;
* then asserts exactly three versions and stops the build if any is wrong:
  `fixest 0.10.4`, `didimputation 0.3.0`, `did2s 0.4.0`.

So three packages are version-asserted at build time and the rest are whatever
the repositories served on the day of the build. The record of what the certified
image ended up with is `docker/container_r_library.tsv` (226 packages), listed
from inside the built image. It visibly mixes the base image's 2022 binary
snapshot (`tidyverse 1.3.1`, `ggplot2 3.3.5`, `Matrix 1.4-0`,
`data.table 1.14.2`, `fixest 0.10.4`) with packages published long afterwards and
pulled in as dependencies of the two `install_version()` calls: `dplyr 1.2.1`
(published on CRAN 2026-04-03), `BH 1.90.0-1` (2025-12-14), `tibble 3.3.1`
(2026-01-11), `bigD 0.3.1` (2025-04-03 — a package that did not exist in 2022).
That mixture is a correct record, not a mistake, and it is exactly why a rebuild
is not reproducible.

**`docker/renv.lock` is not restored.** Nothing in this package calls
`renv::restore()`. The Dockerfile carries a comment above the `COPY` saying the
image restores "the exact pinned library from renv.lock"; that comment is
inaccurate. The Dockerfile is kept byte-identical to the copy the certified image
was built from, so the correction is recorded here rather than made in the file.
`docker/renv.lock` is a record, written by `docker/generate_renv_lock.py` from
`docker/container_r_library.tsv`, and is hashed as a build-provenance input.

**`docker/install_r_packages.R`'s header needs the same correction.** Lines 3–7
of that file call this image "a clean-room CROSS-CHECK, not the authoritative
env" and name the original macOS machine (x86_64 R 4.0.1, `fixest` 0.12.1) as the
authoritative reference; line 11 adds that `fixest` 0.10.4 "cross-checks the
deposit to within 0.1-0.6%". Both statements predate the decision to certify the
deposit inside this image and are superseded by `README.md`. The environment in
which the deposited outputs are byte-reproducible is this image; the 0.1–0.6
percent figure turned out to be an artifact of running the image under x86_64
emulation on Apple silicon, and does not occur on native x86_64 Linux, where every
formatted table was byte-identical. `install_r_packages.R` is one of the four
recipe files whose SHA-256 is bound to the image in
`certification/SIF_PROVENANCE.json`, so it is kept byte-identical for the same
reason the Dockerfile is, and the correction is recorded here and in `README.md`
instead. The record its header points at,
`certification/ENVIRONMENT_EVIDENCE.txt`, ships with the package.

The authoritative pin on the R library is the image hash, not any lock file.

`r_requirements-lock.txt` is a different record again: the macOS R 4.0.1 library
on the author's machine, where the deposited outputs were originally computed
(`fixest 0.12.1`, `data.table 1.17.2`). It is a record of that environment, not an
install recipe.

To re-list the in-image library after a rebuild:

```bash
docker run --rm --entrypoint Rscript fda-repro -e \
  'ip <- installed.packages()[, c("Package","Version")];
   write.table(ip, "", sep="\t", quote=FALSE, row.names=FALSE)' \
  > container_r_library.tsv
```

## 6. What byte-identity means

`certification/compare_output_simulated.py` compares by SHA-256, with no
per-file-type exemption, and 66 of the 283 deposited `output-simulated/` members
are PNGs (134 PNGs ship in the package as a whole). **That bar is
met inside the exact image and is not promised outside it.** On another platform,
or in a rebuilt image, expect sub-pixel differences in rendered PNGs from font and
renderer differences while the content is the same. In that case compare figures
with `certification/compare_exhibit_fidelity.py`, which compares content rather
than bytes, and treat only the CSV and TeX members as byte-exact.

Evidence for the numerical side, on native x86_64 Linux:

* a full real-data run in the certified image on 2026-09-14 regenerated all 50
  formatted manuscript tables byte-identically; 10 event-study CSVs agreed to
  within 4.44e-14;
* a separate build of the same recipe (2026-09-05) regenerated all 50 formatted
  tables byte-identically; of 140 committed `output/tables` CSVs, 123 were
  byte-identical and 15 differed only in the last floating-point digits
  (max |Δ| 7.2e-14);
* switching `fixest` between 0.10.4 and 0.12.1, and switching the OpenBLAS kernel
  or using the reference BLAS, left every III→II estimate table byte-identical.

Run the image on **native x86_64**. The header comments of `docker/Dockerfile` and
`docker/install_r_packages.R` report ~0.1–0.6% cross-environment differences (one
outcome ~3.6%). Those differences came from running the container under x86_64
*emulation* on an Apple-silicon Mac and do not occur on native hardware. Both files
are kept byte-identical to the copies the certified image was built from, so the
correction lives here and in the README rather than in them.

## 7. Memory, CPU and disk

* **Memory.** The synthetic from-raw route was run with a 150 GB allocation and
  did not fail; use a machine with at least 64 GB for it. The real-data route's
  estimation steps are far lighter — peak resident set ≈ 9.8 GB in the measured
  run — and this guide's long-standing "give the VM ≥12 GB" figure applies to
  them. Under emulation on an Apple-silicon host the larger II→I panels can hit
  OOM below that, and a few R steps may need a retry (rpy2 under emulation is
  occasionally flaky; not an issue on native x86_64).
* **CPU.** The measured synthetic run used 12 cores; the measured real-data run
  used 8. `run_all.py` forces single-threaded BLAS, so extra cores help only the
  steps that parallelise themselves.
* **Disk.** The package is ≈22 GB unzipped and
  `materialize_simulation.py --for-gen-run` copies a further ≈6.5 GB into
  `data/`. Allow at least 32 GB free.
* **Runtime.** See the README's runtime figures: ≈9 hours for the synthetic
  from-raw route, ≈1 hour 20 minutes for the real-data route.

## 8. Building the manuscript

The image also carries the LaTeX toolchain, because the strict package build
compiles the manuscript as a mandatory gate:

```bash
docker run --rm -v "$PKG":/replication --entrypoint bash fda-repro \
  -lc 'cd /replication/paper && python3 build_manuscript.py JPE_submission_v8.tex'
```

`paper/build_manuscript.py` requires `pdflatex` and `bibtex` on `PATH` and fails
if either is missing. The deposited `paper/JPE_submission_v8_build.pdf` was
produced with the image's TeX Live 2019; a different TeX Live produces a valid PDF
with the same content but different bytes.
