#!/usr/bin/env Rscript
# install_r_packages.R -- install the R library for the pipeline.
#
# This Docker image is a clean-room CROSS-CHECK, not the authoritative env. The
# authoritative reference is x86_64 R 4.0.1 + fixest 0.12.1 (that binary loads
# under R 4.0.1 and BYTE-REPRODUCES the deposit; see the package README's R
# section and certification/ENVIRONMENT_EVIDENCE.txt). This image instead uses
# fixest 0.10.4 because rocker/r-ver:4.1.3 ships it as a binary in its default
# 2022 Posit Package Manager snapshot, along with the matching 2022-era set
# (Matrix 1.4, did 2.1.1, ...), so the bulk installs as binaries with no version
# conflicts. 0.10.4 cross-checks the deposit to within 0.1-0.6% (a platform/BLAS
# effect, not the fixest version). rocker's Rprofile.site already sets the binary
# repo + HTTPUserAgent; do NOT override it.
#
# The BJS estimator actually used is didimputation (Borusyak-Jaravel-Spiess), pinned
# by exact version. did2s (Gardner two-stage) is pinned too ONLY for frozen-library
# parity -- it is NOT invoked by any pipeline script (the sole reference is a
# commented-out example-data load in r_scripts/preprocess*.R); it is retained so the
# container matches certification/ENVIRONMENT_EVIDENCE.txt exactly, not because any
# estimate depends on it. `did` (Callaway-Sant'Anna) is likewise library()-loaded but
# never used for an estimate, so its snapshot version is fine. data.table here is the container snapshot
# (2022) version 1.14.2; the AUTHORITATIVE reference loaded data.table 1.17.2
# (see certification/ENVIRONMENT_EVIDENCE.txt). data.table is used for data
# wrangling, not estimation, so its version is not outcome-critical.

options(timeout = 1800, Ncpus = max(1L, parallel::detectCores()))
ppm <- getOption("repos")  # rocker 4.1.3 default = focal/2022-04-21 binary repo
cat("Binary repo (from rocker):", ppm, "\n")

install.packages("remotes")

# Pipeline surface as binaries from the 2022 snapshot. fixest resolves to
# 0.10.4 (the container cross-check version; the AUTHORITATIVE estimator is
# 0.12.1, see the package README); data.table/Matrix/did to the compatible
# 2022-era versions.
install.packages(c("fixest", "data.table", "tidyverse", "extrafont",
                   "sandwich", "broom", "lmtest", "BMisc", "Rcpp",
                   "RcppArmadillo", "did"))

# BJS estimators pinned exactly (compile from the CRAN archive where needed).
archive_repos <- c(ppm, CRAN = "https://cloud.r-project.org")
pins <- list(didimputation = "0.3.0", did2s = "0.4.0")
for (pkg in names(pins)) {
  message(sprintf("install_version: %s == %s", pkg, pins[[pkg]]))
  remotes::install_version(pkg, version = pins[[pkg]], repos = archive_repos,
                           upgrade = "never", dependencies = TRUE)
}

# ---- Verify the numerically-critical versions ----
must <- c(fixest = "0.10.4", didimputation = "0.3.0", did2s = "0.4.0")
present_only <- c("data.table", "tidyverse", "dplyr", "extrafont", "sandwich",
                  "BMisc", "did")
cat("\n== R library ==\n")
bad <- character(0)
for (p in c(names(must), present_only)) {
  v <- tryCatch(as.character(packageVersion(p)), error = function(e) "MISSING")
  exp <- if (p %in% names(must)) must[[p]] else NA_character_
  flag <- if (!is.na(exp) && v != exp) sprintf("  <-- expected %s", exp) else ""
  if ((!is.na(exp) && v != exp) || v == "MISSING") bad <- c(bad, p)
  cat(sprintf("  %-14s %s%s\n", p, v, flag))
}
if (length(bad)) stop("version requirements not satisfied for: ", paste(bad, collapse = ", "))
cat("\nR package install complete.\n")
