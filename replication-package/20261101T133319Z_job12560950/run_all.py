#!/usr/bin/env python3
"""
Master orchestrator for the full replication pipeline.

Executes all scripts in dependency order — from raw data generation through
analysis, table/figure production, and final audit.

THREE SUPPORTED ROUTES, and there is no bare "run everything" invocation: a
route flag is required, because the routes read different inputs and are
graded against different targets.

    cd replication_package/

    # (1) SIMULATED-DATA ROUTE — the route any reader can run; no restricted
    #     data. Runs every step from the first cleaning script. Prepare inputs
    #     first (materialize --for-gen-run, then the preflight):
    python3 synthetic_pipeline/materialize_simulation.py --for-gen-run
    python3 synthetic_pipeline/preflight_from_raw.py
    python3 run_all.py --synthetic-from-raw --clean-output \
        --regenerate-safety-keywords --regenerate-safety-embeddings

    # (2) REAL-DATA ROUTE — runs only where the licensed inputs and the
    #     restricted derived data are present. Starts from data/derived/:
    python3 run_all.py --skip-gen --force-estimation --strict-cert

    # (3) REAL-DATA ROUTE FROM RAW — as (2), but rebuilding the derived data
    #     first. Needs every licensed RAW input, not only the derived panels,
    #     and does not reproduce every shipped file byte-for-byte; the
    #     differences are set out in README.md, "Route 3 -- the real-data route from raw":
    python3 run_all.py --real-from-raw --force-estimation --strict-cert

The driver sets the reproducibility environment for every step itself:
PYTHONHASHSEED=0, single-threaded BLAS/OpenMP, package-owned matplotlib/XDG/NLTK
caches, and the in-text gate variables FDA_STRICT_INTEXT=1 and FDA_INTEXT_ROUTE
(synthetic on route 1, real on routes 2 and 3). Nothing has to be exported by hand.

Development-only options (never part of a reported reproduction):
    --skip-estimation      reuse existing estimate CSVs in output/tables/
    --audit-only           run only the final manuscript-exhibit audit
    --from-step N          resume at step N (real-data route only)
    --continue-on-fail     do not stop at the first failing step
    --no-strict-intext     do not fail the run when in-text numbers or the
                           computational appendix tables are not regenerated
    --regenerate-lbd       rerun the frozen entity-resolution artifacts

Execution order (dependency DAG linearized):
    gen        (steps 1-8):   Data generation (00_generate_data/)
    samples    (steps 9-10):  Sample construction & invention years
    estimation (steps 11-12): Estimation (static DiD, requires R/fixest via rpy2)
    analysis   (steps 13-30): Analysis, figures, tables, appendix analyses
    formatting (step 31):     Final table formatting (depends on 06b/06c + 11d)
    exhibits   (steps 32-35): Manuscript-specific exhibits, in-text numbers
    audit      (step 36):     Manuscript exhibit audit & HTML comparison

36 steps execute on either route. The step table carries a 37th entry because
gen_02 (price matching) appears twice: it is skipped at its step-2 position on
the simulated-data route and re-executed after step 9, where its input exists.
Exactly one of the two runs on any route, so the progress counter reads "/36".

Critical dependency: Step 31 (10b_format_remaining_tables.py) MUST run after
steps 16-17 (06b/06c safety CSVs) and step 25 (11d coefficient tables).

===========================================================================
REPRODUCIBILITY POLICY — what is estimated-from-data vs. frozen-by-design
===========================================================================
Every regression estimate and every manuscript exhibit is COMPUTED FROM DATA by
the estimation routines (run_did_imputation, run_quasipoisson,
conley_taber_stacked in 03a/03b/04/05/06a/etc.). A few pieces are frozen
artifacts that are not re-derived on every default run; each is produced from
data by shipped code, pinned by SHA-256, and regenerable with the flag named
below (JPE Data Policy 2.2 / AEA seeded-step guidance):

  1. FROZEN, SEEDED EXTERNAL ARTIFACTS (skipped by default, generator ships):
     - LBD entity-resolution clusters (gen_03_lbd / gen_03b): produced by
       `pandas_dedupe`, which is NON-DETERMINISTIC across runs. The panel is
       generated from data by the shipped code and frozen so the deposited
       numbers are stable; rerun with --regenerate-lbd.
     - GPT/API invention-year CSVs (step 10): derived from data via an external
       LLM/API call that cannot be re-executed deterministically inside the
       package. The extraction code ships for provenance; the CSVs are the frozen
       output.
     - Safety keyword / embedding artifacts (steps 16-17, 06b/06c): high-RAM
       Word2Vec / sentence-transformer models, frozen by default because they are
       expensive, not because they are irreproducible. The Word2Vec training call
       is seeded AND single-threaded (workers=1, seed=config.RANDOM_SEED), and
       re-running step 16 reproduces its own artifacts bit-identically. Rerun with
       --regenerate-safety-keywords / --regenerate-safety-embeddings.
     These are DERIVED FROM DATA by shipped code and seeded/frozen only because
     they are non-deterministic or computationally heavy — the accepted reason to
     freeze a step.

  2. MANUAL CONCEPTUAL DIAGRAMS (two, both hand-drawn schematics — ILLUSTRATIONS
     of the policy design / data catalog, not econometric outputs; they plot no
     estimate and are copied into output/, not "generated," because there is
     nothing to estimate):
       - Deregulation_May31_23_Paper.png (Figure 2, reclassification schematic) —
         copied by copy_manual_figure() from manual_figures/, where its editable
         draw.io source also ships.
       - Data_new_latest.png (Figure D.2, data-catalog diagram) — copied by
         11g_descriptive_figures.py from data/raw/.
     These are the ONLY two manuscript figures not produced by an estimation
     script; every result-bearing figure is generated from data by 04/05/06a/11a/etc.

  3. LDA MODELS (11a_product_variety): the topic model is trained from the patent
     text when no cached model exists; the synthetic-data run deletes the cached
     models and retrains on synthetic text. On the real-data route the cached
     models are FROZEN INPUTS, like the safety artifacts: LDA fitting is not
     bitwise portable across environments, so a retrain, even with the same seed,
     is not guaranteed to reproduce the shipped models or Figure D.5. The 14 model
     files are therefore frozen, hash-verified inputs: run_all verifies them
     against EXPECTED_FROZEN_INPUT_HASHES_REAL.csv and, under --strict-cert,
     refuses to run without them (see README, "Why four artifacts are frozen
     rather than regenerated").

The cost-benefit innovation benefit is likewise data-driven: step 34
(16_total_patent_value_did.py) estimates the total-patent-value DiD and writes
cost_benefit_total_value_did.csv, which step 35 (15_intext_derived_numbers.py)
reads to reproduce the tab:CostBenefits benefit; no dollar constant appears in
either script.

EXECUTION RELIABILITY (rpy2/R): the R bridge (rpy2) occasionally cannot import in
API mode and falls back to ABI mode, in which a single R/feols error can corrupt
the R session for the rest of that process. To keep the one-command run reliable,
run_step() automatically retries a step ONCE in a fresh subprocess when the failure
output shows a transient R/rpy2 marker (a fresh process recovers with byte-identical
outputs). This is a resilience wrapper only; it never alters results, and if the
environment loads rpy2 in API mode the retry never triggers.
"""

import subprocess
import sys
import time
import shutil
import argparse
import logging
import os
import csv
import hashlib
from pathlib import Path

# ============================================================================
# Pipeline steps in dependency order
# ============================================================================
STEPS = [
    # ------------------------------------------------------------------
    # Phase 1: Data generation (from raw → derived)
    # ------------------------------------------------------------------
    {"step": 1,  "script": "00_generate_data/gen_01_main_panels.py",
     "desc": "Main panels (Full_sample, patents, matched samples)",
     "phase": "gen"},
    {"step": 2,  "script": "00_generate_data/gen_02_price_matching.py",
     "desc": "Price matching (constrained_adv_event, needs MarketScan)",
     "phase": "gen"},
    {"step": 3,  "script": "00_generate_data/gen_03b_lbd_clusters.py",
     "desc": "Dedupe clusters (pandas_dedupe, must precede gen_03)",
     "phase": "gen"},
    {"step": 4,  "script": "00_generate_data/gen_03_lbd.py",
     "desc": "Learning-by-doing approval time (needs gen_03b output)",
     "phase": "gen"},
    {"step": 5,  "script": "00_generate_data/gen_04_parquets.py",
     "desc": "Pre-built parquet files for II→I (needs gen_01)",
     "phase": "gen"},
    {"step": 6,  "script": "00_generate_data/gen_05_adverse_fsize.py",
     "desc": "Adverse event firm size (needs MAUDE data)",
     "phase": "gen"},
    {"step": 7,  "script": "00_generate_data/gen_06_adv_2020.py",
     "desc": "Adverse events 2020-2022 (needs MAUDE 2020)",
     "phase": "gen"},
    {"step": 8,  "script": "00_generate_data/gen_07_adverse_permno.py",
     "desc": "Adverse event PERMNOs (entity resolution)",
     "phase": "gen"},

    # ------------------------------------------------------------------
    # Phase 2: Sample construction
    # ------------------------------------------------------------------
    {"step": 9,  "script": "02_match_samples.py",
     "desc": "Mahalanobis matched samples",
     "phase": "samples"},
    {"step": 10, "script": "12_invention_year_generation.py",
     "desc": "Invention year CSVs for experience analysis",
     "phase": "samples"},

    # BOTH FROM-RAW ROUTES: gen_02 (price matching) is a gen-phase transformation that reads the
    # ANALYSIS-phase matched sample produced by step 9, so it cannot run at its step-2 position (no
    # matched sample exists yet). Wherever the gen phase runs it is therefore DEFERRED to here and
    # EXECUTED on that route's MarketScan claims (data/derived/outpatient_combined_censored.csv --
    # materialized from the gen_00c tree on the simulated route, the licensed extract on the real
    # one), that route's GPT price links, and the fresh step-9 matched sample; it overwrites the
    # constrained_adv_event_* that feeds step 13. This RUNS the price-matching transformation
    # rather than freezing its output. Where the gen phase does not run, this entry is skipped
    # (gen_from_raw_only).
    {"step": 37, "script": "00_generate_data/gen_02_price_matching.py",
     "desc": "Price matching on the MarketScan claims, deferred to run after the step-9 matched "
             "sample (both from-raw routes)",
     "phase": "samples", "gen_from_raw_only": True},

    # ------------------------------------------------------------------
    # Phase 3: Estimation (static DiD via R/fixest)
    # ------------------------------------------------------------------
    {"step": 11, "script": "03a_estimation_3to2.py",
     "desc": "Static DiD estimation III→II",
     "phase": "estimation"},
    {"step": 12, "script": "03b_estimation_2to1.py",
     "desc": "Static DiD estimation II→I",
     "phase": "estimation"},

    # ------------------------------------------------------------------
    # Phase 4: Analysis, figures, tables
    # ------------------------------------------------------------------
    {"step": 13, "script": "04_event_studies.py",
     "desc": "Event study figures (27 specifications)"},
    {"step": 14, "script": "05_price_analysis.py",
     "desc": "Price & utilization analysis"},
    {"step": 15, "script": "06a_safety_analysis.py",
     "desc": "Safety patent emphasis DiD"},
    {"step": 16, "script": "06b_validate_safety.py",
     "desc": "Safety robustness: keyword validation (~16 min)"},
    {"step": 17, "script": "06c_validate_safety_embed.py",
     "desc": "Safety robustness: embedding distance (~48 min, high RAM)"},
    {"step": 18, "script": "07_firm_heterogeneity.py",
     "desc": "Firm-size heterogeneity analysis"},
    {"step": 19, "script": "08_lbd_simulation.py",
     "desc": "LBD simulation & calibration"},
    {"step": 20, "script": "09_summary_stats.py",
     "desc": "Summary statistics tables"},
    {"step": 21, "script": "10_table_formatting.py",
     "desc": "Format main LaTeX tables (32 tables)"},

    # ------------------------------------------------------------------
    # Phase 5: Appendix analysis
    # ------------------------------------------------------------------
    {"step": 22, "script": "11a_product_variety.py",
     "desc": "Product variety LDA (Fig D.5)"},
    {"step": 23, "script": "11b_recall_analysis.py",
     "desc": "Recall analysis (Fig D.14-15)"},
    {"step": 24, "script": "11c_liability.py",
     "desc": "Liability & bankruptcy (Fig D.10)"},
    {"step": 25, "script": "11d_reg_design.py",
     "desc": "Regulation design experience (Fig D.11-12, coefficient tables for 10b)"},
    {"step": 26, "script": "11e_new_entry_2015.py",
     "desc": "New firm entry post-2015 (Fig D.16)"},
    {"step": 27, "script": "11f_reg_background.py",
     "desc": "Regulatory background distributions (Fig D.1)"},
    {"step": 28, "script": "11g_descriptive_figures.py",
     "desc": "Descriptive figures (Fig D.2)"},
    {"step": 29, "script": "13_restricted_samples.py",
     "desc": "Restricted sample robustness (Table D.16)"},
    {"step": 30, "script": "14_breakthrough_patents.py",
     "desc": "Breakthrough patent analysis"},

    # ------------------------------------------------------------------
    # Phase 6: Final formatting (MUST follow 06b/06c + 11d)
    # ------------------------------------------------------------------
    {"step": 31, "script": "10b_format_remaining_tables.py",
     "desc": "Format remaining tables (needs 11d + 06b/06c CSVs)"},

    # ------------------------------------------------------------------
    # Phase 7: Manuscript-specific exhibits not covered by the DiD pipeline
    # (contact-lens case study, cost-benefit total-value DiD, derived in-text
    # numbers). Part of the master script so one command reproduces every
    # exhibit.
    # ------------------------------------------------------------------
    {"step": 32, "script": "12_contact_lens_case_study.py",
     "desc": "Contact-lens case study figures (Fig 1 panels in v6)",
     "phase": "exhibits"},
    {"step": 33, "script": "15b_event_study_HD_coefficients.py",
     "desc": "Event-study half-distance coefficients (feeds 15_intext safety %)",
     "phase": "exhibits", "env": {"RUN_ES_HD": "1"}},
    {"step": 34, "script": "16_total_patent_value_did.py",
     "desc": "Total-value DiD for the cost-benefit table (tab:CostBenefits)",
     "phase": "exhibits", "env": {"RUN_TOTAL_VALUE_DID": "1"}},
    {"step": 35, "script": "15_intext_derived_numbers.py",
     "desc": "Derived in-text numbers (>150% safety, ~$26-28M cost-benefit)",
     "phase": "exhibits"},

    # ------------------------------------------------------------------
    # Phase 8: Audit
    # ------------------------------------------------------------------
    {"step": 36, "script": "audit_pipeline_current.py",
     "desc": "current manuscript (v8) vs replication audit + HTML comparison",
     "phase": "audit"},
]


# PUBLIC_MODE_RESTRICTED_SKIPS was removed with --public-mode (2026-09-11). Which exhibits depend on
# which restricted source is documented in MANUSCRIPT_EXHIBIT_DATA_DEPENDENCIES.md and
# RESTRICTED_FILE_INVENTORY.csv.


FROZEN_LBD_STEPS = {
    3: (
        "LBD dedupe clusters are treated as a frozen entity-resolution artifact "
        "for the manuscript replication. This is not documented as proven "
        "stochasticity; rather, this pandas_dedupe provenance path is not "
        "guaranteed to be stable across environments/orderings unless the "
        "exact stack and inputs are pinned. Use --regenerate-lbd only for a "
        "provenance/robustness rerun."
    ),
    4: (
        "LBD approval-time panel is treated as a frozen entity-resolution "
        "artifact for the manuscript replication. Regeneration may change the "
        "regulatory-proficiency summary statistics if the dedupe cluster output "
        "differs. Use --regenerate-lbd only for a provenance/robustness rerun."
    ),
}


STATIC_PROVENANCE_STEPS = {
    10: (
        "Invention-year CSVs are pre-generated static GPT/API-derived data "
        "files. The script is retained for provenance documentation and is "
        "intentionally not runnable in the replication pipeline."
    ),
}


# The simulated-data route has no frozen transformation steps. Its simulator
# supplies raw-shaped MAUDE linkage inputs; gen_07 performs a deterministic exact
# synthetic linkage. LBD clustering also has a deterministic synthetic branch,
# and step 10 validates acquired invention-year inputs without an API call.
FROZEN_SYNTHETIC_GEN_STEPS = {}

# gen_02 (price matching) is a gen-phase transformation that reads the ANALYSIS-phase matched sample
# (step 9), so it cannot run at its step-2 position. On the --synthetic-from-raw route it is DEFERRED:
# skipped at step 2 (NOT counted as a frozen skip -- it is not frozen) and EXECUTED after step 9 as the
# gen_from_raw_only step 37, on that route's MarketScan claims + GPT price links +
# fresh step-9 matched sample. This RUNS the transformation instead of freezing its output.
DEFERRED_TO_POST_MATCHING_STEPS = {
    2: "gen_02 price-matching deferred to run after step 9 (executed as step 37 on this route's "
    "MarketScan claims).",
}


PRECOMPUTED_SAFETY_EMBEDDING_STEPS = {
    17: (
        "Safety embedding-distance outputs are treated as included "
        "precomputed artifacts in the default manuscript replication. The "
        "high-RAM sentence-transformer script is retained and can be rerun "
        "with --regenerate-safety-embeddings."
    ),
}


PRECOMPUTED_SAFETY_KEYWORD_STEPS = {
    16: (
        "Safety refined-keyword outputs are treated as included precomputed "
        "artifacts in the default manuscript replication. The high-RAM "
        "Word2Vec/keyword script is retained and can be rerun with "
        "--regenerate-safety-keywords."
    ),
}


SAFETY_EMBEDDING_OUTPUTS = [
    Path("data/derived/safety_tagged_patents.csv"),
    Path("output/tables/safety_embedding_distance_estimates.csv"),
    Path("output/tables/safety_embedding_percentile_robustness.csv"),
    Path("output/tables/safety_embedding_percentile_used.txt"),
]


SAFETY_KEYWORD_OUTPUTS = [
    Path("data/derived/safety_vars_allpats_v2.csv"),
    Path("data/derived/safety_vars_allpats_updated_v2.csv"),
    Path("output/tables/safety_refined_keywords_estimates.csv"),
    Path("output/tables/safety_term_share.csv"),
]

# The step-16/17 OUTPUT tables that the real-data route takes as given (steps 16 and 17 are skipped
# there as precomputed): the certification harness clears output/ and restores exactly these, pin-checked
# against EXPECTED_INTERMEDIATE_HASHES.csv; --clean-output refuses to delete them unless the matching
# --regenerate-safety-* flag will rebuild them. The simulated-data route regenerates all of them.
FROZEN_SAFETY_OUTPUT_TABLES = {
    "--regenerate-safety-keywords": [p for p in SAFETY_KEYWORD_OUTPUTS if p.parts[0] == "output"],
    "--regenerate-safety-embeddings": [p for p in SAFETY_EMBEDDING_OUTPUTS if p.parts[0] == "output"],
}


# Step 11a's cached LDA models, 7 files per label (gensim writes three
# sidecar files next to each lda_<label>.model). FROZEN INPUTS on the real-data route: LDA fitting is not
# bitwise portable across environments, so a retrain, even with the same seed, is not guaranteed to
# reproduce the shipped models or Figure D.5; the 14 files are hash-verified by verify_frozen_artifact_integrity
# against EXPECTED_FROZEN_INPUT_HASHES_REAL.csv (see README, "Why four artifacts are frozen rather than
# regenerated"). The synthetic route deletes and retrains them.
FROZEN_LDA_MODELS = [Path(f"data/derived/{name}") for label in ("2to1", "3to2") for name in (
    f"lda_{label}.model", f"lda_{label}.model.expElogbeta.npy", f"lda_{label}.model.id2word",
    f"lda_{label}.model.state", f"lda_bigram_{label}.model", f"lda_trigram_{label}.model",
    f"lda_dictionary_{label}.dict")]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def verify_frozen_artifact_integrity(root_dir, regenerate_safety_keywords=False,
                                     regenerate_safety_embeddings=False,
                                     real_data_route=False, strict=False):
    """Verify shipped FROZEN artifacts by
    HASH at run time, and FAIL CLOSED.

    run_all reuses precomputed safety artifacts (steps 16/17) instead of regenerating them (the
    restricted text inputs are not in the public package). Accepting them by mere existence means a
    corrupted or tampered frozen artifact would be used silently.

    An artifact that EXISTS but is NOT in either
    certification/EXPECTED_INTERMEDIATE_HASHES.csv (the two output/tables estimate files) or
    certification/EXPECTED_FROZEN_INPUT_HASHES.csv (the three data/derived frozen inputs) is a HARD
    FAILURE -- an unmanifested frozen input cannot be verified, so the run refuses to proceed on
    it. The ONE exemption is the
    audit's own caveat: an artifact that WILL be overwritten before use (its step 16/17 is being
    regenerated this run) does not need frozen verification, and is skipped. On the synthetic route
    the harness passes --regenerate-safety-* so the materialized (synthetic) safety files are skipped;
    on the real-data route they are used frozen and MUST be manifested + hash-match.
    Skips cleanly only if the manifest itself is absent (a bare dev run).

    ROUTE-AWARE frozen-input manifest: the SYNTHETIC safety artifacts (shipped in the public package)
    and the REAL safety artifacts (rebuilt by the Data Editor from the restricted text) hash to
    DIFFERENT values, so one manifest cannot verify both. `EXPECTED_FROZEN_INPUT_HASHES.csv` carries the
    SYNTHETIC hashes (the default / public+synthetic route). When real_data_route is True the check
    instead uses `EXPECTED_FROZEN_INPUT_HASHES_REAL.csv` if it is present; if that real manifest is
    absent it falls back to the synthetic one with a warning (it will then mismatch the real artifacts,
    which is the correct fail-closed behaviour -- regenerate the safety artifacts or supply the real
    manifest).

    STRICT (final-certification) mode (strict=True, set by run_all --strict-cert):
    the integrity check may NOT be skipped and may NOT fall back to another route's manifest. A missing
    intermediate manifest, or a real-data route whose EXPECTED_FROZEN_INPUT_HASHES_REAL.csv is absent, is
    a HARD FAILURE (SystemExit), not a warning/skip. Certification must verify every frozen artifact
    against its OWN route's manifest or refuse to run."""
    manifest = root_dir / "certification" / "EXPECTED_INTERMEDIATE_HASHES.csv"
    if not manifest.exists():
        if strict:
            raise SystemExit(
                f"FATAL (strict-cert): frozen-artifact manifest {manifest.name} is absent -- final "
                f"certification cannot skip the runtime hash check.")
        logging.info("Frozen-artifact integrity: manifest absent (%s) -- skipping runtime hash check.",
                     manifest.name)
        return
    expected = {}
    # The frozen safety artifacts live in TWO manifests: the two output/tables/*.csv estimate files are
    # build-verified outputs in EXPECTED_INTERMEDIATE_HASHES.csv (which the build's output-hash verifier
    # requires to be output/-only, matching its canonical inventory); the three data/derived/*.csv
    # frozen INPUTS are carried separately in EXPECTED_FROZEN_INPUT_HASHES.csv so they do not pollute
    # that output manifest. Both feed this one run-time integrity check.
    frozen_input_manifest = root_dir / "certification" / "EXPECTED_FROZEN_INPUT_HASHES.csv"
    if real_data_route:
        real_manifest = root_dir / "certification" / "EXPECTED_FROZEN_INPUT_HASHES_REAL.csv"
        if real_manifest.exists():
            frozen_input_manifest = real_manifest
            logging.info("Frozen-artifact integrity: real-data route -> using %s", real_manifest.name)
        elif strict:
            raise SystemExit(
                f"FATAL (strict-cert): real-data route but the real-route manifest {real_manifest.name} "
                f"is absent. Final certification REQUIRES the route-specific manifest and must NOT fall "
                f"back to the synthetic manifest. Supply {real_manifest.name} (authoritative real-artifact "
                f"hashes) before certifying the real-data route.")
        else:
            logging.warning(
                "Frozen-artifact integrity: real-data route but %s is absent -- falling back to the "
                "SYNTHETIC manifest %s, which will NOT match the real artifacts (fail-closed). Supply "
                "the real manifest or regenerate the safety artifacts with --regenerate-safety-*.",
                real_manifest.name, frozen_input_manifest.name)
    for m in (manifest, frozen_input_manifest):
        if not m.exists():
            continue
        with open(m, newline="") as fh:
            for row in csv.DictReader(fh):
                expected[row["output_file"].replace("\\", "/")] = row["sha256"]
    # Per-artifact "overwritten before use" exemption: a keyword output is regenerated iff
    # --regenerate-safety-keywords; an embedding output iff --regenerate-safety-embeddings.
    will_regen = set()
    if regenerate_safety_keywords:
        will_regen |= {str(r).replace("\\", "/") for r in SAFETY_KEYWORD_OUTPUTS}
    if regenerate_safety_embeddings:
        will_regen |= {str(r).replace("\\", "/") for r in SAFETY_EMBEDDING_OUTPUTS}
    checked, mismatched, unmanifested, skipped = 0, [], [], 0
    missing_frozen = []
    for rel in SAFETY_EMBEDDING_OUTPUTS + SAFETY_KEYWORD_OUTPUTS:
        p = root_dir / rel
        key = str(rel).replace("\\", "/")
        if not p.exists():
            # A frozen artifact that is ABSENT cannot be hash-verified, and the step that would
            # consume it reads whatever appears in its place. Under --strict-cert that is fatal
            # unless this run regenerates the artifact (the same rule the LDA models already had);
            # otherwise it is a loud warning. Silently skipping it let a run report
            # "N hash-verified, 0 unmanifested" while a pinned artifact was simply gone.
            if key not in will_regen:
                missing_frozen.append(key)
            continue
        if key in will_regen:
            skipped += 1            # overwritten before use this run -> no frozen verification needed
            continue
        if key not in expected:
            unmanifested.append(key)
            continue
        got = _sha256(p)
        checked += 1
        if got != expected[key]:
            mismatched.append((key, expected[key][:12], got[:12]))
    # On the real-data route the cached LDA models are frozen inputs (see FROZEN_LDA_MODELS). A present
    # model must match its pin (a mismatch or a missing pin fails below, like the safety artifacts). A MISSING
    # model makes 11a retrain silently to a different Figure D.5, so it is FATAL under --strict-cert and a loud
    # warning otherwise. The synthetic route retrains them on simulated text by design and is not checked.
    if real_data_route:
        missing_lda = []
        for rel in FROZEN_LDA_MODELS:
            key = str(rel).replace("\\", "/")
            p = root_dir / rel
            if not p.exists():
                missing_lda.append(key)
                continue
            if key not in expected:
                unmanifested.append(key)
                continue
            got = _sha256(p)
            checked += 1
            if got != expected[key]:
                mismatched.append((key, expected[key][:12], got[:12]))
        if missing_lda:
            if strict:
                raise SystemExit(
                    f"FATAL (strict-cert): {len(missing_lda)} frozen LDA model file(s) are missing on the "
                    f"real-data route. Step 11a would retrain them, and LDA fitting is not bitwise portable "
                    f"across environments, so a retrain is not guaranteed to reproduce the shipped models or "
                    f"Figure D.5 (see README, 'Why four artifacts are frozen rather than regenerated'). Supply "
                    f"the pinned models (EXPECTED_FROZEN_INPUT_HASHES_REAL.csv): {missing_lda}")
            logging.warning("Frozen LDA models missing on the real-data route (%d files): step 11a will "
                            "RETRAIN them, and a retrain is not guaranteed to reproduce Figure D.5. %s",
                            len(missing_lda), missing_lda)
    if missing_frozen:
        if strict:
            raise SystemExit(
                f"FATAL (strict-cert): {len(missing_frozen)} pinned frozen artifact(s) are MISSING and "
                f"are not being regenerated by this run. Certification cannot verify an artifact that is "
                f"not there, and the step that reads it would silently use whatever replaces it. Restore "
                f"them from the deposit, or pass --regenerate-safety-keywords / "
                f"--regenerate-safety-embeddings: {missing_frozen}")
        logging.warning("Frozen artifact(s) MISSING and not regenerated this run (%d): %s. The "
                        "consuming step will fail or read a substitute.",
                        len(missing_frozen), missing_frozen)
    if mismatched:
        for key, exp, got in mismatched:
            logging.error("Frozen-artifact HASH MISMATCH: %s expected %s… got %s…", key, exp, got)
        raise SystemExit(f"Frozen-artifact integrity check FAILED: {len(mismatched)} shipped frozen "
                         f"artifact(s) do not match their expected hash in "
                         f"certification/EXPECTED_INTERMEDIATE_HASHES.csv / EXPECTED_FROZEN_INPUT_HASHES.csv "
                         f"(corrupted or tampered); refusing to run on unverified frozen inputs.")
    if unmanifested:
        for key in unmanifested:
            logging.error("Frozen-artifact UNMANIFESTED (cannot hash-verify, not regenerated): %s", key)
        raise SystemExit(f"Frozen-artifact integrity check FAILED: {len(unmanifested)} frozen "
                         f"artifact(s) EXIST but are not in EXPECTED_INTERMEDIATE_HASHES.csv / "
                         f"EXPECTED_FROZEN_INPUT_HASHES.csv and are not being regenerated this run -- "
                         f"refusing to use an unverifiable frozen input. Add its hash to the "
                         f"appropriate manifest, or regenerate it. {unmanifested}")
    logging.info("Frozen-artifact integrity: %d hash-verified, %d skipped (overwritten this run), "
                 "0 unmanifested.", checked, skipped)


def precomputed_safety_embedding_outputs_available(root_dir):
    """Return True if the included embedding-derived artifacts are present."""
    return all((root_dir / rel_path).exists() for rel_path in SAFETY_EMBEDDING_OUTPUTS)


def precomputed_safety_keyword_outputs_available(root_dir):
    """Return True if the included keyword-derived artifacts are present."""
    return all((root_dir / rel_path).exists() for rel_path in SAFETY_KEYWORD_OUTPUTS)


# The two directories a run regenerates. They are the same two the certification harness empties
# before a run, and the same two the output comparison reads. output/logs and output/_cache are
# run scaffolding, not exhibits, and are left alone.
EXHIBIT_OUTPUT_DIRS = ("output/figures", "output/tables")

# Restricted, author-built derived inputs. Their presence is what distinguishes a tree that can run
# the real-data route from a fresh public extraction (which has neither these nor the raw sources
# that would build them).
RESTRICTED_DERIVED_MARKERS = (
    Path("data/derived/Full_sample.csv"),
    Path("data/derived/matched_sample_3_2_onepat.csv"),
)

ROUTE_HELP = (
    "This package supports exactly three routes, and each needs its own flags.\n"
    "\n"
    "  (1) Simulated-data route -- no restricted data, runs every step:\n"
    "        python3 synthetic_pipeline/materialize_simulation.py --for-gen-run\n"
    "        python3 synthetic_pipeline/preflight_from_raw.py\n"
    "        python3 run_all.py --synthetic-from-raw --clean-output \\\n"
    "            --regenerate-safety-keywords --regenerate-safety-embeddings\n"
    "\n"
    "  (2) Real-data route -- only where the licensed inputs and the restricted derived\n"
    "      data are present:\n"
    "        python3 run_all.py --skip-gen --force-estimation --strict-cert\n"
    "\n"
    "  (3) Real-data route FROM RAW -- as (2), but rebuilding the derived data first. Needs\n"
    "      every licensed raw input, not only the derived panels, and does not reproduce every\n"
    "      shipped file byte-for-byte (see README.md, \"Route 3\"):\n"
    "        python3 run_all.py --real-from-raw --force-estimation --strict-cert\n"
    "\n"
    "See README.md. A bare `python3 run_all.py` is not a supported reproduction command."
)


def existing_exhibit_outputs(root_dir):
    """Every file currently under output/figures and output/tables, as paths relative to root."""
    found = []
    for rel in EXHIBIT_OUTPUT_DIRS:
        base = root_dir / rel
        if not base.is_dir():
            continue
        for dirpath, _dirs, names in os.walk(base):
            for name in names:
                found.append(str(Path(dirpath, name).relative_to(root_dir)))
    return sorted(found)


def assert_clean_output_is_safe(root_dir, regenerate_safety_keywords, regenerate_safety_embeddings):
    """--clean-output empties output/tables, which holds the step-16/17 output tables that are pinned
    frozen inputs rather than ordinary exhibits (FROZEN_SAFETY_OUTPUT_TABLES: the keyword and
    embedding estimate tables, the keyword share, the percentile-robustness table and its sidecar).
    Deleting any of them without regenerating it
    leaves the run with no way to produce it again -- steps 16/17 are skipped as precomputed
    unless the matching --regenerate-safety-* flag is passed. REFUSE, rather than delete and
    discover it four steps later. The simulated-data route always passes both flags (it
    regenerates both from the synthetic text), so this only bites a real-data --clean-output run."""
    guarded = (
        [(rel, regenerate_safety_keywords, "--regenerate-safety-keywords")
         for rel in FROZEN_SAFETY_OUTPUT_TABLES["--regenerate-safety-keywords"]]
        + [(rel, regenerate_safety_embeddings, "--regenerate-safety-embeddings")
           for rel in FROZEN_SAFETY_OUTPUT_TABLES["--regenerate-safety-embeddings"]]
    )
    unsafe = [(rel, flag) for rel, will_regen, flag in guarded
              if (root_dir / rel).exists() and not will_regen]
    if unsafe:
        raise SystemExit(
            "--clean-output would delete pinned frozen artifact(s) that this run does not "
            "regenerate:\n"
            + "\n".join(f"  {rel}  (needs {flag})" for rel, flag in unsafe)
            + "\nSteps 16/17 are skipped as precomputed unless the matching flag is passed, so the "
              "deleted file could not be rebuilt and step 31 would fail. Re-run with the flag(s) "
              "above, or without --clean-output."
        )


def clear_exhibit_outputs(root_dir):
    """Delete every file under output/figures and output/tables. Refuses to follow symlinks."""
    removed = 0
    for rel in EXHIBIT_OUTPUT_DIRS:
        base = root_dir / rel
        base.mkdir(parents=True, exist_ok=True)
        for dirpath, dirs, names in os.walk(base, followlinks=False):
            for name in dirs + names:
                path = Path(dirpath, name)
                if path.is_symlink():
                    raise SystemExit(f"refusing to clear output: symlink under {rel}: {path}")
            for name in names:
                Path(dirpath, name).unlink()
                removed += 1
    return removed


def execution_order(run_gen_phase):
    """The order in which run_all executes STEPS: list order, with two moves. Step numbers are unchanged, so
    the logs show step 15 before step 13.

    - Whenever the gen phase runs (--synthetic-from-raw or --real-from-raw): gen_05 consumes the
      manufacturer-to-PERMNO linkage, so gen_07 (step 8) runs before gen_05 (step 6). The documented
      --skip-gen real-data route never runs the gen phase, so the move is inert there.
    - Every route: 04_event_studies (step 13) reads data/derived/safety_did_analysis*.csv, which
      06a_safety_analysis (step 15) writes; 06a's header states it "MUST run before 04_event_studies.py". So
      06a runs before 04 on every route."""
    pipeline_steps = list(STEPS)
    if run_gen_phase:
        gen07 = next(s for s in pipeline_steps if s["step"] == 8)
        pipeline_steps.remove(gen07)
        gen05_index = next(i for i, s in enumerate(pipeline_steps) if s["step"] == 6)
        pipeline_steps.insert(gen05_index, gen07)
    safety06a = next(s for s in pipeline_steps if s["step"] == 15)
    pipeline_steps.remove(safety06a)
    ev04_index = next(i for i, s in enumerate(pipeline_steps) if s["step"] == 13)
    pipeline_steps.insert(ev04_index, safety06a)
    return pipeline_steps


def setup_logging(log_dir):
    """Configure logging to both file and console."""
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"run_all_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def copy_manual_figure(root_dir):
    """Copy the manually-created Figure 2 into replication output.

    Deregulation_May31_23_Paper.png is not produced by any script; it is a
    hand-drawn diagram. Its SOURCE ships inside the package at
    `manual_figures/Deregulation_May31_23_Paper.png` so it can be restored even
    after output/figures/ is cleared for a from-scratch run. The editable
    draw.io master, `manual_figures/Deregulation_May31_23_Paper.drawio`, ships
    beside it and is deliberately NOT copied into output/: output/ holds only
    what a run produces, and a source asset there would show up as an
    unaccounted extra in the output comparison.

    STATIC SCHEMATIC, NOT A COMPUTED EXHIBIT: this figure is a CONCEPTUAL SCHEMATIC
    of the FDA reclassification design (a hand-drawn diagram), not an econometric
    output. It plots no coefficient, dataset, or estimate, so there is nothing to
    regenerate from data -- it is copied into output/ as a static asset, the same
    way a paper includes a hand-drawn framework figure. It is one of only TWO
    manuscript figures not produced by an estimation script (the other is the
    data-catalog diagram Data_new_latest.png / Figure D.2, copied by
    11g_descriptive_figures.py); every result-bearing figure is
    generated from data by 04/05/06a/11a/etc. See the REPRODUCIBILITY POLICY block
    at the top of this file.
    """
    dst = root_dir / "output" / "figures" / "Deregulation_May31_23_Paper.png"
    # Prefer the PACKAGED source (ships in the deposit → survives clearing output/);
    # fall back to the author dev-layout parent Figures/, then to an existing copy.
    packaged_src = root_dir / "manual_figures" / "Deregulation_May31_23_Paper.png"
    dev_src = root_dir.parent / "Figures" / "Deregulation_May31_23_Paper.png"
    src = packaged_src if packaged_src.exists() else dev_src

    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Treat the manual figure as a package output. Do not preserve the
        # original file mtime, or the audit can falsely flag it as stale.
        shutil.copyfile(src, dst)
        logging.info("Copied manual figure from %s/: %s", src.parent.name, dst.name)
    elif dst.exists():
        os.utime(dst, None)
        logging.info("Using included manual figure: %s", dst.name)
    else:
        logging.warning(
            "Manual figure not found (looked in manual_figures/ and ../Figures/): %s",
            dst.name,
        )


def build_child_env(root_dir, intext_route="real", strict_intext=True):
    """Construct an ISOLATED environment for subprocess steps.

    (1) SCRUB host injection vectors the pipeline never needs -- PYTHONPATH (every
        step self-manages sys.path via config.MODULES_DIR/ROOT inserts),
        PYTHONSTARTUP, and USER-level R profile/environ files -- so a developer's
        stray host settings cannot silently alter a run.
    (1b) SCRUB the package's own escape-hatch / specification-override variables
        (FDA_SKIP_MARKETSCAN_PANEL, FDA_SAFETY_SIMILARITY_*, FDA_FORCE_SAFETY_*,
        FDA_SYNTHETIC_MODE). They remain usable when a replicator invokes a single
        script directly -- each script prints a loud banner when it honours one --
        but they never survive from the host into a driver-launched step.
    (2) HARD-SET (not setdefault) the reproducibility-critical vars so a preset
        host value can NEVER override the package's intended value. This includes
        the in-text gate: step 35 only FAILS on an unproduced in-text number or an
        ungenerated computational appendix table when FDA_STRICT_INTEXT=1, and it
        grades against the real manuscript targets unless FDA_INTEXT_ROUTE says
        otherwise. Leaving either to the caller meant the documented commands
        could report success on a run that produced neither, so run_all sets both
        itself from the route flags (--no-strict-intext opts out, for development).
    The frozen-env reproduction legitimately sets R_HOME/R_LIBS_USER/NLTK_DATA (see
    the runbook / Docker %environment); those are left intact but LOGGED so any
    value is visible in the run log rather than silently trusted."""
    env = dict(os.environ)
    # (1) scrub pure host-injection vectors (safe: steps self-manage sys.path; the
    #     reproduction never relies on these).
    for _inj in ("PYTHONPATH", "PYTHONSTARTUP", "R_PROFILE_USER", "R_ENVIRON_USER"):
        env.pop(_inj, None)
    # (1b) scrub the package's OWN escape hatches and specification overrides. Each of these is a
    #      switch a replicator may legitimately set when running a SINGLE script by hand (the script
    #      then prints a loud banner saying so), but none of them may reach a driver-launched step:
    #      this driver's documented commands must always mean the same thing.
    #        FDA_SKIP_MARKETSCAN_PANEL   -- would drop the price/utilization exhibits (step 14) and
    #                                       Table 1 Panel III (step 20) while the run still exits 0;
    #        FDA_SAFETY_SIMILARITY_*     -- the safety-tagging threshold, i.e. a SPECIFICATION constant;
    #        FDA_FORCE_SAFETY_*          -- the driver sets these itself from --regenerate-safety-*
    #                                       (below), so a host value must not pre-empt the flag;
    #        FDA_SYNTHETIC_MODE          -- the route, set by the driver from --synthetic-from-raw only.
    for _override in ("FDA_SKIP_MARKETSCAN_PANEL",
                      "FDA_SAFETY_SIMILARITY_PERCENTILE",
                      "FDA_SAFETY_SIMILARITY_PERCENTILES_ROBUST",
                      "FDA_FORCE_SAFETY_KEYWORDS",
                      "FDA_FORCE_SAFETY_EMBEDDINGS",
                      "FDA_SYNTHETIC_MODE"):
        if _override in env:
            logging.warning(
                "build_child_env: IGNORING host %s=%r. Package override variables never reach a "
                "driver-launched step; they apply only when a script is invoked directly.",
                _override, env[_override])
        env.pop(_override, None)
    cache_dir = root_dir / "output" / "_cache"
    mpl_dir = cache_dir / "matplotlib"
    xdg_dir = cache_dir / "xdg"
    nltk_dir = cache_dir / "nltk_data"
    for path in (mpl_dir, xdg_dir, nltk_dir):
        path.mkdir(parents=True, exist_ok=True)
    # (2) HARD-SET package-controlled vars (host value must NOT win). These point at
    #     package-owned writable cache dirs or are determinism-critical.
    env["MPLBACKEND"] = "Agg"
    env["MPLCONFIGDIR"] = str(mpl_dir)
    env["XDG_CACHE_HOME"] = str(xdg_dir)
    # NLTK_DATA is left to the reproduction env (the Docker image bakes a corpus at
    # /opt/nltk_data and sets NLTK_DATA to it; a bare host falls back to the package
    # cache). setdefault, not hard-set, so the baked corpus is not shadowed.
    env.setdefault("NLTK_DATA", str(nltk_dir))
    # Deterministic Python hashing so dict/set-ordering-sensitive steps reproduce
    # exactly (notably the pandas_dedupe entity resolution behind the LBD panel).
    # HARD-SET: a host PYTHONHASHSEED must not silently change LBD determinism.
    env["PYTHONHASHSEED"] = "0"
    # Pin R fixest / BLAS / OpenMP to a SINGLE thread. Multithreaded fixest residualization has a
    # run-to-run floating-point summation-order non-determinism that (a) is amplified into a visibly
    # different point estimate on one ill-conditioned difference-of-counts robustness cell (II->I
    # MarketComposition, excluding-zero, LaterTreat, firm_expansion_patents: 1.961 <-> 3.516) and
    # (b) causes intermittent rpy2/R SIGABRT crashes in the II->I estimation (step 12). Single-thread
    # is deterministic AND stable (verified 20/20 identical, 0 crashes). Determinism > speed here.
    for _tvar in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                  "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[_tvar] = "1"
    # In-text / appendix-table gate. HARD-SET from the route so no caller has to export it and no
    # stale host value can downgrade the gate.
    if intext_route not in ("real", "synthetic"):
        raise ValueError(f"intext_route must be 'real' or 'synthetic', got {intext_route!r}")
    env["FDA_INTEXT_ROUTE"] = intext_route
    env["FDA_STRICT_INTEXT"] = "1" if strict_intext else "0"
    return env


# A step that embeds R via rpy2 can fail TRANSIENTLY: when rpy2 cannot import in
# API mode it falls back to ABI mode, in which a single feols/R error can corrupt
# the R session for the remainder of that process (a per-figure error caught by
# 04_event_studies then cascades to a hard process exit). A fresh subprocess
# recovers reliably with byte-identical outputs. When a failure's output contains
# one of these markers, run_step retries the step ONCE in a fresh process.
_R_TRANSIENT_MARKERS = (
    "rpy2", "RRuntimeError", "Problem evaluating the fixed-effects",
    "_R_BaseEnv", "rinterface_lib.embedded",
)


_TXN_OUTPUT_DIRS = ("output", "data/derived")


def _snapshot_output_paths(root_dir):
    """Set of file paths currently under the step-writable output dirs. Used for transactional
    retries: a failed attempt's NEW files are removed before a clean retry."""
    seen = set()
    for d in _TXN_OUTPUT_DIRS:
        base = root_dir / d
        if not base.exists():
            continue
        for dp, _dirs, names in os.walk(base):
            for n in names:
                seen.add(os.path.join(dp, n))
    return seen


def run_step(step_info, code_dir, root_dir, child_env, progress=None):
    """Run a single script and return success/failure.

    R-embedding steps are retried once in a fresh subprocess on a transient
    rpy2/ABI-mode failure (see _R_TRANSIENT_MARKERS and the REPRODUCIBILITY
    POLICY block at the top of this file). Retries are TRANSACTIONAL: any output
    files a failed attempt created are removed before the next attempt."""
    script_path = code_dir / step_info["script"]
    if not script_path.exists():
        # FAIL-CLOSED: a missing pipeline script is a genuine gap, not a benign skip. The legitimate
        # skips (static-provenance / precomputed safety steps) `continue` BEFORE run_step is called,
        # so reaching here with an absent script means the pipeline is incomplete. Returning success
        # would let "~27/0/9 + audit completed" hide a missing script -- so fail.
        logging.error(
            "Step %d: %s NOT FOUND -- pipeline is incomplete (failing, not skipping)",
            step_info["step"], step_info["script"]
        )
        return False

    # progress is (position_in_this_route, steps_scheduled_for_this_route). The step-table number
    # is printed too, because execution order and numbering differ and --from-step / the README
    # overview speak in numbers.
    if progress:
        logging.info(
            "Step %d/%d (step table #%d): Starting %s (%s)",
            progress[0], progress[1], step_info["step"], step_info["script"], step_info["desc"],
        )
    else:
        logging.info(
            "Step (step table #%d): Starting %s (%s)",
            step_info["step"], step_info["script"], step_info["desc"],
        )
    t0 = time.time()

    # Per-step environment overrides (e.g. RUN_TOTAL_VALUE_DID=1 for step 33).
    step_env = child_env
    if step_info.get("env"):
        step_env = dict(child_env)
        step_env.update(step_info["env"])

    # Per-step interpreter override (optional, general capability): the certified route runs every
    # step -- including step 17 (06c safety embedding) -- under the single numpy 1.26.4 interpreter,
    # with no separate sub-environment. FDA_SAFETY_EMBED_PYTHON is an optional escape hatch: if it is
    # set, 06c runs under that interpreter instead, so a run whose default interpreter is not numpy
    # 1.26.4 can still regenerate the safety-embedding exhibit under a compatible one. Otherwise 06c
    # runs under the default interpreter like every other step.
    interpreter = sys.executable
    embed_py = os.environ.get("FDA_SAFETY_EMBED_PYTHON")
    if embed_py and str(step_info["script"]).endswith("06c_validate_safety_embed.py"):
        interpreter = embed_py
        logging.info("Step %d: using optional FDA_SAFETY_EMBED_PYTHON override interpreter %s "
                     "(certified route uses the single numpy 1.26.4 interpreter; this override is off by default)",
                     step_info["step"], embed_py)

    # Up to two automatic retries for transient R/rpy2 (ABI-mode) failures. Heavy
    # steps make many feols calls per run (11a ~1/topic, 14/04 several), so the
    # chance of hitting the intermittent ABI-mode R-session corruption somewhere in
    # a run is higher for them; a couple of fresh-process retries clears it.
    max_attempts = 3
    # Transactional-retry baseline: snapshot output files BEFORE the first attempt so a failed
    # attempt's NEW partial outputs can be cleared before the retry.
    _pre_outputs = _snapshot_output_paths(root_dir)
    for attempt in range(1, max_attempts + 1):
        result = subprocess.run(
            [interpreter, str(script_path)],
            cwd=str(root_dir),  # run from replication_package root
            env=step_env,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - t0
        # Opt-in per-step log capture (off by default → real-data runs are byte-identical).
        # Set FDA_STEP_LOG_DIR to preserve each child's combined stdout+stderr even on SUCCESS
        # (subprocess capture_output otherwise discards successful child stderr). Used by the
        # synthetic-route certification harness so the actual in-run step logs (e.g. 06c's
        # rpy2 API-mode + packaged-model messages) are auditable, not a separate rerun.
        _step_log_dir = os.environ.get("FDA_STEP_LOG_DIR")
        if _step_log_dir:
            # FAIL-CLOSED: when a caller explicitly asks for per-step logs (certification),
            # a log-write failure is FATAL — a missing/partial log invalidates the evidence.
            _sld = Path(_step_log_dir)
            _sld.mkdir(parents=True, exist_ok=True)
            _stem = Path(step_info["script"]).stem
            _suffix = f"_attempt{attempt}" if attempt > 1 else ""
            _lp = _sld / f"step_{step_info['step']:02d}_{_stem}{_suffix}.log"
            with open(_lp, "w") as _fh:
                _fh.write(f"# step {step_info['step']} : {step_info['script']}\n")
                _fh.write(f"# interpreter: {interpreter}\n")
                _fh.write(f"# returncode: {result.returncode}  elapsed: {elapsed:.1f}s  attempt: {attempt}\n")
                _fh.write("# ---- stdout ----\n")
                _fh.write(result.stdout or "")
                _fh.write("\n# ---- stderr ----\n")
                _fh.write(result.stderr or "")
                _fh.flush()
                os.fsync(_fh.fileno())
        if result.returncode == 0:
            note = f" (recovered on attempt {attempt})" if attempt > 1 else ""
            logging.info("Step %d: Completed in %.1fs%s", step_info["step"], elapsed, note)
            if result.stdout.strip():
                # Show tail of output for monitoring
                logging.debug("  stdout (last 500): %s", result.stdout.strip()[-500:])
            return True

        combined = (result.stdout or "") + (result.stderr or "")
        # A rpy2 ABI-mode "hard process exit" (the R-session corruption documented above) can SEGFAULT
        # the interpreter, which leaves EMPTY stdout/stderr -- so no marker string matches. Detect that
        # case by the negative returncode (subprocess.run reports -N when the child was killed by
        # signal N, e.g. -11 = SIGSEGV) and treat it as the same transient failure: the documented
        # fresh-subprocess recovery (byte-identical outputs) applies to these hard exits too.
        transient = result.returncode < 0 or any(m in combined for m in _R_TRANSIENT_MARKERS)
        if attempt < max_attempts and transient:
            # Transactional retry: remove any NEW output files this failed attempt created so the
            # retry starts clean. Only NEW files (not in the pre-attempt snapshot) are removed, so a
            # pre-existing input a step reads is never deleted; deterministic steps overwrite their own
            # outputs anyway, so this only clears orphan partials from a variable-output step.
            _orphans = _snapshot_output_paths(root_dir) - _pre_outputs
            for _f in _orphans:
                try:
                    os.remove(_f)
                except OSError:
                    pass
            if _orphans:
                logging.warning("Step %d: cleared %d partial output file(s) from the failed attempt "
                                "before retry.", step_info["step"], len(_orphans))
            logging.warning(
                "Step %d: attempt %d hit a transient R/rpy2 error after %.1fs; "
                "retrying once in a fresh process (rpy2 ABI-mode fragility — see the "
                "REPRODUCIBILITY POLICY block).", step_info["step"], attempt, elapsed,
            )
            t0 = time.time()
            continue

        logging.error(
            "Step %d: FAILED after %.1fs (attempt %d)\nstdout (last 2000):\n%s\n"
            "stderr (last 2000):\n%s",
            step_info["step"], elapsed, attempt,
            result.stdout[-2000:] if result.stdout else "(empty)",
            result.stderr[-2000:] if result.stderr else "(empty)",
        )
        return False


# Data files a producer step must write on EVERY run. The real-data route
# starts from the authorized overlay, which also carries an earlier run's copy of each (they are corpus
# sources the privacy audits read), so a producer that exited 0 without rewriting one would leave that stale
# copy for every later consumer. run_step_checked() fails such a step before any consumer runs; stage 3 also
# deletes these files before run_all (REAL_REGENERATED_DERIVED) and checks that each was rewritten. Source: a
# full real-data run's write trace in the certification image, which recorded exactly these files under data/.
STEP_DECLARED_DATA_OUTPUTS = {
    "02_match_samples.py": [f"data/derived/matched_sample_{name}.csv" for name in (
        "2_1_onepat", "2_1_onepat_innovation", "2_1_onepat_innovation_quality", "3_2_onepat",
        "3_2_onepat_innovation", "3_2_onepat_innovation_quality", "3_2_onepat_innovation_petitioned")],
    "06a_safety_analysis.py": ["data/derived/safety_did_analysis.csv", "data/derived/safety_did_analysis_3_2.csv"],
}


def declared_output_problems(step_info, root_dir, t_start):
    """The step's declared data outputs that are missing, empty, or older than the step's start."""
    problems = []
    for rel in STEP_DECLARED_DATA_OUTPUTS.get(Path(step_info["script"]).name, []):
        p = Path(root_dir) / rel
        if not p.is_file():
            problems.append(f"{rel} was not written")
        elif p.stat().st_size == 0:
            problems.append(f"{rel} is empty")
        elif p.stat().st_mtime < t_start - 1.0:  # 1 s allows for coarse filesystem timestamps
            problems.append(f"{rel} was not rewritten by this step (it predates the step)")
    return problems


def run_step_checked(step_info, code_dir, root_dir, child_env, progress=None):
    """run_step(), then require every declared data output to have been (re)written by this step. A step that
    exits 0 without writing one FAILS, so the run stops before a consumer can read an earlier copy."""
    t_start = time.time()
    if not run_step(step_info, code_dir, root_dir, child_env, progress=progress):
        return False
    problems = declared_output_problems(step_info, root_dir, t_start)
    for msg in problems:
        logging.error("Step %d: exited 0 but %s", step_info["step"], msg)
    return not problems


def main():
    parser = argparse.ArgumentParser(
        description="Run the full replication pipeline in dependency order.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
The two supported routes (see README.md):

  # (1) Simulated-data route -- no restricted data, runs all 36 steps
  python3 synthetic_pipeline/materialize_simulation.py --for-gen-run
  python3 synthetic_pipeline/preflight_from_raw.py
  python3 run_all.py --synthetic-from-raw --clean-output \\
      --regenerate-safety-keywords --regenerate-safety-embeddings

  # (2) Real-data route -- licensed inputs and restricted derived data present
  python3 run_all.py --skip-gen --force-estimation --strict-cert

run_all sets the reproducibility environment for every step itself (PYTHONHASHSEED=0,
single-threaded BLAS/OpenMP, package-owned caches, FDA_STRICT_INTEXT=1 and
FDA_INTEXT_ROUTE). Nothing needs to be exported by hand.

Development-only options: --skip-estimation, --audit-only, --from-step,
--continue-on-fail, --no-strict-intext, --regenerate-lbd.
""",
    )
    parser.add_argument(
        "--from-step", type=int, default=1,
        help=(
            "DEVELOPMENT ONLY. Resume at step N, skipping every step that precedes it in this "
            "route's execution order (not every step with a smaller number -- the order is not "
            "the numbering; see execution_order()). Rejected on --synthetic-from-raw, which must "
            "run complete."
        ),
    )
    parser.add_argument(
        "--skip-gen", action="store_true",
        help=("Real-data route: skip the gen phase (steps 1-8) and start from the derived data "
              "already in data/derived/."),
    )
    parser.add_argument(
        "--skip-estimation", action="store_true",
        help=("DEVELOPMENT ONLY. Skip the gen, samples and estimation phases (steps 1-12) and "
              "reuse the estimate CSVs already in output/tables/."),
    )
    parser.add_argument(
        "--audit-only", action="store_true",
        help="DEVELOPMENT ONLY. Run only the final manuscript-exhibit audit (step 36).",
    )
    parser.add_argument(
        "--continue-on-fail", action="store_true",
        help="Continue past failures instead of stopping",
    )
    # RETIRED (2026-09-11): kept only so an old command gets an explanation instead of an argparse
    # error. Hidden from --help; exits immediately (see the check right after parse_args()).
    parser.add_argument("--public-mode", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--regenerate-lbd", action="store_true",
        help=(
            "Regenerate optional/frozen LBD entity-resolution artifacts "
            "(steps 3-4). By default these are skipped so the included frozen "
            "artifact exactly reproduces the manuscript summary statistics. "
            "This option is for provenance/robustness, not the default "
            "manuscript replication."
        ),
    )
    parser.add_argument(
        "--regenerate-safety-embeddings", action="store_true",
        help=(
            "Rerun step 17, the high-RAM sentence-transformer safety-embedding "
            "validation. By default, the pipeline uses the included "
            "deterministic safety_tagged_patents.csv and "
            "safety_embedding_distance_estimates.csv artifacts."
        ),
    )
    parser.add_argument(
        "--regenerate-safety-keywords", action="store_true",
        help=(
            "Rerun step 16, the high-RAM Word2Vec safety-keyword validation. "
            "By default, the pipeline uses the included "
            "safety_vars_allpats_v2.csv, safety_vars_allpats_updated_v2.csv, "
            "and safety_refined_keywords_estimates.csv artifacts."
        ),
    )
    parser.add_argument(
        "--force-estimation", action="store_true",
        help=(
            "Force steps 03a/03b to RECOMPUTE every estimate CSV even if one already exists "
            "(they skip-if-exists by default), so the ~100 estimate tables come from the input "
            "data rather than from whatever the tree already held. IMPLIED by "
            "--synthetic-from-raw and by --strict-cert, so both reported routes always force it; "
            "pass it explicitly for any other run. (Overwrites the estimate CSVs in the run "
            "tree, so run on a copy.)"
        ),
    )
    parser.add_argument(
        "--real-from-raw", action="store_true",
        help=(
            "REAL-DATA ROUTE, FROM RAW: run the gen phase (steps 1-8) on the licensed raw inputs "
            "instead of starting from the restricted derived data. Needs every restricted input, not "
            "only the derived panels; see README. gen_02 (price matching) is DEFERRED and executed "
            "after step 9 because it reads the step-9 matched sample, and gen_07 runs before gen_05 "
            "because gen_05 consumes its linkage -- the same two moves the simulated route makes. "
            "The LBD clustering steps stay frozen unless --regenerate-lbd is also given: the "
            "clustering reproduces the same partition but relabels cluster ids. Step 10 is not run on "
            "any route. Mutually exclusive with --skip-gen and with --synthetic-from-raw. Use WITH "
            "--force-estimation. Regenerated derived files are not byte-identical to every shipped "
            "copy; README.md, \"Route 3 -- the real-data route from raw\", states which differ and why."
        ),
    )
    parser.add_argument(
        "--synthetic-from-raw", action="store_true",
        help=(
            "SIMULATED-DATA ROUTE: RUN the deterministic cleaning scripts (gen_01 main panels, gen_04 "
            "parquets, gen_05 adverse-fsize, gen_06 adv-2020) on the SYNTHETIC RAW inputs instead of "
            "--skip-gen, so the synthetic route runs 'from the first cleaning script'. gen_02 (price "
            "matching) is DEFERRED and executed after step 9 on the synthetic MarketScan (it reads the "
            "step-9 matched sample). LBD clustering and the MAUDE-to-firm linkage use deterministic "
            "synthetic-only branches, and the external-API invention-year inputs are validated locally. "
            "No transformation step is skipped on this route. "
            "Use WITH --force-estimation, and materialize with --for-gen-run first so gen_01's raw "
            "inputs (e.g. PC_by_year_*) are placed in data/raw/. Mutually exclusive with --skip-gen. "
            "Implies --force-estimation, and requires an empty output/figures + output/tables "
            "(see --clean-output)."
        ),
    )
    parser.add_argument(
        "--strict-cert", action="store_true",
        help=(
            "FINAL-CERTIFICATION mode: the frozen-artifact integrity check may not "
            "be skipped and may not fall back to another route's manifest. A missing intermediate manifest, "
            "or a real-data route whose EXPECTED_FROZEN_INPUT_HASHES_REAL.csv is absent, becomes a HARD "
            "FAILURE instead of a warning/skip. Use for the certified build; omit for dev runs."
        ),
    )
    parser.add_argument(
        "--clean-output", action="store_true",
        help=(
            "Delete every file under output/figures and output/tables before the run, so each "
            "exhibit is produced by this run and not left over from an earlier one. The "
            "simulated-data route REQUIRES an empty pair of directories: without this flag it "
            "refuses to start while either contains a file. output/logs and output/_cache are "
            "not touched. On the real-data route, note that steps 16/17 are skipped as "
            "precomputed and read output/tables/safety_{refined_keywords,embedding_distance}_"
            "estimates.csv: clear those and you must either restore them or pass "
            "--regenerate-safety-keywords / --regenerate-safety-embeddings."
        ),
    )
    parser.add_argument(
        "--no-strict-intext", action="store_true",
        help=(
            "DEVELOPMENT ONLY. Do not set FDA_STRICT_INTEXT=1, so step 35 reports an in-text "
            "number it could not compute, or a computational appendix table it could not "
            "generate, without failing the run. Never use this for a reproduction: it is exactly "
            "the condition under which a run can print 'Succeeded: 36' having produced neither."
        ),
    )
    args = parser.parse_args()

    if args.public_mode:
        raise SystemExit(
            "--public-mode has been retired and is not part of the deposit. Its public-safe subset "
            "cannot run on a fresh extraction: 11d_reg_design.py reads data/derived/Full_sample.csv and "
            "two matched samples, and 08_lbd_simulation.py reads a matched sample. None of these ship "
            "(all are restricted-derived), and that mode neither materialized synthetic versions of "
            "them nor ran the steps that build them. Use the publishable-synthetic route instead "
            "(README.md, \"Route 1 -- the simulated-data route\"), which runs every step."
        )
    if args.real_from_raw and args.skip_gen:
        raise SystemExit(
            "--real-from-raw is mutually exclusive with --skip-gen: one runs the gen phase on the "
            "licensed raw inputs, the other skips it and starts from the restricted derived data. "
            "Pick one."
        )
    if args.real_from_raw and args.synthetic_from_raw:
        raise SystemExit(
            "--real-from-raw and --synthetic-from-raw are mutually exclusive: they are the real and "
            "the simulated route, and a run is one or the other."
        )
    if args.synthetic_from_raw and args.skip_gen:
        raise SystemExit(
            "--synthetic-from-raw is mutually exclusive with --skip-gen: the whole "
            "point of the simulated-data route is to RUN the cleaning scripts (gen_01/04/05/06), not skip "
            "the gen phase. Use --synthetic-from-raw --clean-output."
        )
    if args.synthetic_from_raw and args.from_step != 1:
        raise SystemExit(
            "--from-step cannot be combined with --synthetic-from-raw. That route is defined as a "
            "complete run from the first cleaning script, and a partial one is not evidence of "
            "anything: its later steps would read whatever an earlier run happened to leave behind. "
            "Rerun it complete (with --clean-output)."
        )

    root_dir = Path(__file__).resolve().parent
    code_dir = root_dir / "code"
    log_dir = root_dir / "output" / "logs"

    # ROUTE. --synthetic-from-raw is the simulated-data route; everything else reads the real
    # derived data. A bare invocation with no route flag at all is not a supported reproduction
    # command: on a fresh public extraction it fails inside step 1 for want of inputs that do not
    # ship, which reads as a broken package rather than as the wrong command.
    intext_route = "synthetic" if args.synthetic_from_raw else "real"
    # Whether the gen phase (steps 1-8) executes. Both from-raw routes need the same two
    # reorderings; the documented --skip-gen route needs neither, because it runs no gen step.
    run_gen_phase = args.synthetic_from_raw or args.real_from_raw
    any_route_flag = (args.synthetic_from_raw or args.real_from_raw or args.skip_gen
                      or args.skip_estimation or args.audit_only)
    if not any_route_flag:
        # A bare invocation is refused BEFORE step 1, on every tree. It used to be refused only
        # where the restricted derived data was absent, which meant that on a complete real tree a
        # bare run started the gen phase -- without the two reorderings a from-raw run needs -- and
        # rewrote data/derived/Applicant_Device_data.csv before gen_01 stopped it. Refusing here
        # keeps a run that names no route from writing to data/ at all.
        missing_markers = [str(m) for m in RESTRICTED_DERIVED_MARKERS
                           if not (root_dir / m).is_file()]
        detail = ("\nThis tree also does not hold the restricted derived data that the real-data "
                  "routes start from (missing: " + ", ".join(missing_markers) + ").\n"
                  if missing_markers else "")
        raise SystemExit(
            "No route selected, so nothing was run and nothing was written. A bare "
            "`python3 run_all.py` is not a reproduction command: choose one of the routes below.\n"
            + detail + "\n" + ROUTE_HELP
        )

    # CLEAN RUN. The deposited output/ holds the manuscript's real-data exhibits. Running the
    # simulated-data route on top of them would leave any exhibit a step failed to write looking
    # like a success, and would mix real and simulated files in the tree the comparison reads.
    stale_outputs = existing_exhibit_outputs(root_dir)
    if args.clean_output:
        assert_clean_output_is_safe(root_dir, args.regenerate_safety_keywords,
                                    args.regenerate_safety_embeddings)
        if stale_outputs:
            print(f"--clean-output: deleting {len(stale_outputs)} pre-existing file(s) under "
                  + " and ".join(EXHIBIT_OUTPUT_DIRS))
        clear_exhibit_outputs(root_dir)
    elif args.synthetic_from_raw and stale_outputs:
        raise SystemExit(
            f"Refusing to start the simulated-data route: {len(stale_outputs)} file(s) already "
            f"exist under {' and '.join(EXHIBIT_OUTPUT_DIRS)} (e.g. {stale_outputs[0]}).\n"
            "Those are the deposited real-data exhibits, or an earlier run's. A step that then "
            "produced nothing would leave them in place and the run would still report success.\n"
            "Delete them, or pass --clean-output to have this driver delete them for you."
        )

    log_file = setup_logging(log_dir)
    logging.info("=" * 70)
    logging.info("REPLICATION PIPELINE")
    logging.info("=" * 70)
    logging.info("Log file: %s", log_file)
    logging.info("Python:   %s", sys.executable)
    logging.info("Root:     %s", root_dir)
    # Verify shipped FROZEN artifacts by hash (not existence) before the pipeline may reuse them.
    verify_frozen_artifact_integrity(
        root_dir,
        regenerate_safety_keywords=args.regenerate_safety_keywords,
        regenerate_safety_embeddings=args.regenerate_safety_embeddings,
        # Real-data route = not the synthetic-from-raw route; it reuses the REAL frozen safety
        # artifacts, so verify against the REAL manifest (route-aware).
        real_data_route=(not args.synthetic_from_raw),
        # STRICT/final-cert mode: no skip, no cross-route fallback -- a missing or wrong-route manifest
        # is a hard failure.
        strict=args.strict_cert,
    )
    child_env = build_child_env(root_dir, intext_route=intext_route,
                                strict_intext=not args.no_strict_intext)
    if args.synthetic_from_raw:
        child_env["FDA_SYNTHETIC_MODE"] = "1"
        logging.info("Simulated-data route: deterministic synthetic transformations enabled")
    logging.info("Route:    %s", "simulated data" if args.synthetic_from_raw else "real data")
    logging.info("MPLBACKEND: %s", child_env["MPLBACKEND"])
    logging.info("MPLCONFIGDIR: %s", child_env["MPLCONFIGDIR"])
    logging.info("FDA_INTEXT_ROUTE: %s", child_env["FDA_INTEXT_ROUTE"])
    if args.no_strict_intext:
        logging.warning(
            "FDA_STRICT_INTEXT is OFF (--no-strict-intext): step 35 will REPORT, not fail on, an "
            "in-text number or computational appendix table it could not produce. Development only."
        )
    else:
        logging.info("FDA_STRICT_INTEXT: 1 (step 35 fails the run on any unproduced in-text "
                     "number or computational appendix table)")
    # Estimation is FORCED on both reported routes. 03a/03b skip any estimate CSV that already
    # exists unless FORCE_ESTIMATION=1, so without this a run on a tree that still held the
    # deposited estimate tables would reuse ~100 of them and report success.
    force_estimation = args.force_estimation or args.synthetic_from_raw or args.strict_cert
    if force_estimation:
        child_env["FORCE_ESTIMATION"] = "1"
        if not args.force_estimation:
            logging.info("Force estimation: implied by %s",
                         "--synthetic-from-raw" if args.synthetic_from_raw else "--strict-cert")
        logging.info("Force estimation: yes (03a/03b will recompute all estimates)")
    if args.regenerate_safety_keywords:
        # Running step 16 is not enough: 06b has its OWN internal skip guard
        # (FDA_FORCE_SAFETY_KEYWORDS != "1" AND precomputed outputs exist -> returns early using
        # the included artifacts). Set the env var so the flag actually forces regeneration from
        # the (synthetic) patent text. (Step 17 / 06c has no internal guard, so running it suffices.)
        child_env["FDA_FORCE_SAFETY_KEYWORDS"] = "1"
        logging.info("Regenerate safety keywords: yes (06b will retrain Word2Vec on the patent text)")

    # Determine which phases to skip
    skip_phases = set()
    if args.skip_gen or args.skip_estimation:
        skip_phases.add("gen")
    if args.skip_estimation:
        skip_phases.add("samples")
        skip_phases.add("estimation")
    if args.audit_only:
        # Skip everything except audit
        skip_phases.update({"gen", "samples", "estimation"})

    t_total = time.time()
    failed = []
    skipped = []
    succeeded = []

    pipeline_steps = execution_order(run_gen_phase)

    # Steps actually scheduled for THIS route: the step table has 37 entries because gen_02 appears
    # twice (once in place, once deferred past step 9), and exactly one of the two runs on any
    # route. The progress counter reports this count, so it agrees with the documented 36.
    scheduled_steps = [
        s for s in pipeline_steps
        if not (s.get("gen_from_raw_only") and not run_gen_phase)
        and not (run_gen_phase and s["step"] in DEFERRED_TO_POST_MATCHING_STEPS)
    ]
    route_total = len(scheduled_steps)
    # Position of each scheduled step in this route's execution order, for the progress counter.
    # It is NOT the step-table number: execution order and numbering differ (see execution_order()).
    step_position = {id(s): i + 1 for i, s in enumerate(scheduled_steps)}
    logging.info("Steps in this route's step table: %d (steps that a flag such as --skip-gen or a "
                 "precomputed-artifact default excludes are counted here and reported as skipped "
                 "in the final tally)", route_total)

    # --from-step resumes at a POSITION in this route's execution order, not at a step NUMBER.
    # The two differ: execution_order() runs step 15 before 13 on every route and step 8 before 6
    # whenever the gen phase runs, and the deferred gen_02 re-run carries number 37 while executing
    # right after step 9. Filtering on the number alone would run steps whose predecessors were
    # skipped (e.g. --from-step 13 would still run the number-37 gen-phase entry).
    from_index = 0
    if args.from_step != 1:
        scheduled_ids = {id(s) for s in scheduled_steps}
        matches = [i for i, s in enumerate(pipeline_steps)
                   if s["step"] == args.from_step and id(s) in scheduled_ids]
        if not matches:
            raise SystemExit(
                f"--from-step {args.from_step}: not a step this route executes. Valid step numbers: "
                + ", ".join(str(n) for n in sorted(s["step"] for s in scheduled_steps))
            )
        from_index = matches[0]

    for position, step_info in enumerate(pipeline_steps):
        step_num = step_info["step"]
        phase = step_info.get("phase", "")

        # Skip by --from-step (by position in this route's execution order)
        if position < from_index:
            skipped.append(step_info)
            continue

        # A step marked gen_from_raw_only (the deferred post-step-9 gen_02 re-run) exists ONLY
        # where the gen phase runs; otherwise it is not part of the pipeline, so
        # it is not executed AND not counted as a skip. Checked BEFORE the phase-skip branch so the
        # tally counts exactly the steps this route schedules.
        if step_info.get("gen_from_raw_only") and not run_gen_phase:
            continue

        # Skip by phase flags
        if phase in skip_phases:
            logging.info(
                "Step %d: Skipped (%s phase, --skip flag)", step_num, phase
            )
            skipped.append(step_info)
            continue

        if step_num in FROZEN_LBD_STEPS and not (args.regenerate_lbd or args.synthetic_from_raw):
            logging.info(
                "Step %d: Skipped by default (%s)",
                step_num,
                FROZEN_LBD_STEPS[step_num],
            )
            skipped.append(step_info)
            continue

        # gen_02 is deferred to run after step 9 wherever the gen phase runs (executed as the
        # gen_from_raw_only step 37). Skip it at its step-2 position, but do NOT count it as a
        # skip -- it is executed later, so it belongs in neither the succeeded nor the skipped tally here.
        if run_gen_phase and step_num in DEFERRED_TO_POST_MATCHING_STEPS:
            logging.info(
                "Step %d: Deferred to run after step 9 (%s)",
                step_num,
                DEFERRED_TO_POST_MATCHING_STEPS[step_num],
            )
            continue

        if args.synthetic_from_raw and step_num in FROZEN_SYNTHETIC_GEN_STEPS:
            logging.info(
                "Step %d: Skipped (--synthetic-from-raw frozen gen step: %s)",
                step_num,
                FROZEN_SYNTHETIC_GEN_STEPS[step_num],
            )
            skipped.append(step_info)
            continue

        if step_num in STATIC_PROVENANCE_STEPS and not args.synthetic_from_raw:
            logging.info(
                "Step %d: Skipped by default (%s)",
                step_num,
                STATIC_PROVENANCE_STEPS[step_num],
            )
            skipped.append(step_info)
            continue

        if (
            step_num in PRECOMPUTED_SAFETY_KEYWORD_STEPS
            and not args.regenerate_safety_keywords
        ):
            if not precomputed_safety_keyword_outputs_available(root_dir):
                logging.error(
                    "Step %d cannot be skipped because required precomputed "
                    "safety-keyword outputs are missing: %s",
                    step_num,
                    ", ".join(str(path) for path in SAFETY_KEYWORD_OUTPUTS),
                )
                failed.append(step_info)
                if not args.continue_on_fail:
                    break
            logging.info(
                "Step %d: Skipped by default (%s)",
                step_num,
                PRECOMPUTED_SAFETY_KEYWORD_STEPS[step_num],
            )
            skipped.append(step_info)
            continue

        if (
            step_num in PRECOMPUTED_SAFETY_EMBEDDING_STEPS
            and not args.regenerate_safety_embeddings
        ):
            if not precomputed_safety_embedding_outputs_available(root_dir):
                logging.error(
                    "Step %d cannot be skipped because required precomputed "
                    "safety-embedding outputs are missing: %s",
                    step_num,
                    ", ".join(str(path) for path in SAFETY_EMBEDDING_OUTPUTS),
                )
                failed.append(step_info)
                if not args.continue_on_fail:
                    break
            logging.info(
                "Step %d: Skipped by default (%s)",
                step_num,
                PRECOMPUTED_SAFETY_EMBEDDING_STEPS[step_num],
            )
            skipped.append(step_info)
            continue

        # --audit-only: skip everything that isn't audit
        if args.audit_only and phase != "audit":
            skipped.append(step_info)
            continue

        if phase == "audit":
            copy_manual_figure(root_dir)

        ok = run_step_checked(step_info, code_dir, root_dir, child_env,
                              progress=(step_position.get(id(step_info), 0), route_total))
        if ok:
            succeeded.append(step_info)
        else:
            failed.append(step_info)
            if not args.continue_on_fail:
                logging.error(
                    "Stopping at step %d. Use --continue-on-fail to proceed past errors.",
                    step_num,
                )
                break

    # Summary
    elapsed_total = time.time() - t_total
    logging.info("")
    logging.info("=" * 70)
    logging.info("SUMMARY  (%.1fs total)", elapsed_total)
    logging.info("=" * 70)
    logging.info("  Succeeded: %d", len(succeeded))
    logging.info("  Failed:    %d", len(failed))
    logging.info("  Skipped:   %d", len(skipped))

    if failed:
        logging.error("")
        logging.error("Failed steps:")
        for f in failed:
            logging.error("  Step %d: %s — %s", f["step"], f["script"], f["desc"])
        sys.exit(1)
    else:
        logging.info("")
        logging.info("All executed steps completed successfully.")


if __name__ == "__main__":
    main()
