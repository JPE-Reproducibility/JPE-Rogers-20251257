#!/usr/bin/env python
"""
06c_validate_safety_embed.py -- Safety robustness: embedding-distance measure.

FROZEN ARTIFACT (regenerable with --regenerate-safety-embeddings; pinned by
SHA-256 because the encoder is RAM and CPU heavy): this script encodes patent
text with a sentence-transformer and derives the embedding-distance safety
estimates FROM DATA. The encoder is a packaged sentence-transformer run as a
deterministic forward pass -- it draws no random numbers, so no seed is involved
-- but it is RAM and CPU heavy, so run_all treats its outputs as precomputed
artifacts by default and re-runs this script only under
--regenerate-safety-embeddings. Freezing an expensive step is standard practice
(JPE Data Policy 2.2). See the REPRODUCIBILITY POLICY block in run_all.py.

Validates the main safety-emphasis results from 06a by using sentence-
transformer embeddings (all-MiniLM-L6-v2) instead of keyword matching.
For each patent, the script encodes its cleaned abstract, computes cosine
similarity to a centroid of reference safety sentences, and tags patents
above the 99th percentile as safety-related. The embedding-based safety
variable then feeds into the same DiD pipeline used in 06a.

This provides a complementary validation to 06b (refined keywords) by
using a continuous, corpus-based measure of safety relevance.

Inputs:
    data/raw/FDA_patents_text.csv            (patent title+abstract text)
    data/derived/all_patents_w_xi_oct22_24.csv
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_3_2_onepat.csv
    data/derived/Adverse_fsize_ready_all4_oct22_24.csv

Outputs:
    data/derived/safety_tagged_patents.csv
    output/tables/safety_embedding_distance_estimates.csv
    output/tables/safety_embedding_percentile_robustness.csv
        (the reported 99th-percentile threshold and the 95th-percentile
         robustness the appendix refers to; see emit_percentile_robustness)
    output/tables/safety_embedding_percentile_used.txt
        (one line, `similarity_percentile=<value>`: the safety-tagging threshold
         this run applied; see write_percentile_sidecar)
"""

import os
os.environ["USE_TF"] = "0"  # Prevent sentence-transformers from loading TensorFlow

import sys
import logging
import time
import re
from pathlib import Path

import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked
from match_mahal import get_similar

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "06c_validate_safety_embed.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


# ============================================================================
# Text preprocessing
# ============================================================================

def clean_text(text):
    """Lowercase, remove punctuation, collapse whitespace."""
    if pd.isnull(text) or not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_stopwords(tokens, stop_words):
    """Remove English stopwords from token list."""
    return [t for t in tokens if t not in stop_words]


# ============================================================================
# Constants
# ============================================================================

REFERENCE_SAFETY_SENTENCES = [
    "The device incorporates multiple safety mechanisms to prevent accidents.",
    "Safety protocols must be strictly followed in all operational procedures.",
    "Ensuring user safety is paramount in the design of this system.",
    "The material is certified for safety under international standards.",
    "Safety features include automatic shut-off and emergency alerts.",
]

# Similarity threshold for tagging a patent as safety-related. The manuscript
# reports the 99th percentile and states that "results are similar at the 95th".
# SIMILARITY_PERCENTILE is the reported threshold; SIMILARITY_PERCENTILES_ROBUST
# lists the additional thresholds whose estimates are emitted as robustness rows
# by emit_percentile_robustness().
#
# These two constants are the SPECIFICATION the manuscript reports, not tuning knobs.
# They can be overridden for a sensitivity run of THIS SCRIPT INVOKED DIRECTLY:
#   FDA_SAFETY_SIMILARITY_PERCENTILE=0.99
#   FDA_SAFETY_SIMILARITY_PERCENTILES_ROBUST=0.95
# An override prints a loud banner (below) and is written into
# output/tables/safety_embedding_percentile_used.txt and into every row of
# output/tables/safety_embedding_percentile_robustness.csv, so no estimate can be silent about
# the threshold that produced it. run_all.py SCRUBS both variables from every step it launches, so
# a stray host export can never change the reported specification of a driver-run reproduction.
_PCT_ENV = "FDA_SAFETY_SIMILARITY_PERCENTILE"
_PCT_ROBUST_ENV = "FDA_SAFETY_SIMILARITY_PERCENTILES_ROBUST"
SIMILARITY_PERCENTILE_DEFAULT = 0.99
SIMILARITY_PERCENTILES_ROBUST_DEFAULT = "0.95"
SIMILARITY_PERCENTILE = float(
    os.environ.get(_PCT_ENV, str(SIMILARITY_PERCENTILE_DEFAULT)))
SIMILARITY_PERCENTILES_ROBUST = tuple(
    float(x) for x in os.environ.get(
        _PCT_ROBUST_ENV, SIMILARITY_PERCENTILES_ROBUST_DEFAULT).split(",") if x.strip()
)
for _var, _override, _default in ((_PCT_ENV, os.environ.get(_PCT_ENV), str(SIMILARITY_PERCENTILE_DEFAULT)),
                                  (_PCT_ROBUST_ENV, os.environ.get(_PCT_ROBUST_ENV),
                                   SIMILARITY_PERCENTILES_ROBUST_DEFAULT)):
    if _override is not None and _override != _default:
        print("=" * 78)
        print(f"!! SPECIFICATION OVERRIDE IN EFFECT: {_var}={_override!r} (package default {_default}).")
        print("!! The safety-tagging threshold is the specification the manuscript reports. This run")
        print("!! is a SENSITIVITY run, NOT a reproduction of the reported estimates; its outputs must")
        print("!! not be compared against the deposited ones. Unset the variable to reproduce.")
        print("=" * 78)
MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_ENV_VAR = "FDA_SPILLOVERS_SENTENCE_MODEL"


def find_local_model_snapshot():
    """Find the embedding model. PREFERS the model SHIPPED IN THE PACKAGE
    (`models/all-MiniLM-L6-v2/`, Apache-2.0, redistributable) so a clean-room reviewer needs no
    Hugging Face cache and no network; then falls back to a cached HF snapshot."""
    # 1) package-shipped model (package root = parent of code/)
    shipped = Path(__file__).resolve().parents[1] / "models" / "all-MiniLM-L6-v2"
    if (shipped / "modules.json").exists() and (shipped / "config.json").exists():
        return shipped

    hub_dirs = []
    if os.environ.get("HF_HOME"):
        hub_dirs.append(Path(os.environ["HF_HOME"]) / "hub")
    if os.environ.get("XDG_CACHE_HOME"):
        hub_dirs.append(Path(os.environ["XDG_CACHE_HOME"]) / "huggingface" / "hub")
    hub_dirs.append(Path.home() / ".cache" / "huggingface" / "hub")

    seen = set()
    for hub_dir in hub_dirs:
        if hub_dir in seen:
            continue
        seen.add(hub_dir)
        model_dir = hub_dir / "models--sentence-transformers--all-MiniLM-L6-v2"
        snapshots_dir = model_dir / "snapshots"
        if not snapshots_dir.exists():
            continue

        candidates = []
        refs_main = model_dir / "refs" / "main"
        if refs_main.exists():
            commit = refs_main.read_text().strip()
            if commit:
                candidates.append(snapshots_dir / commit)
        candidates.extend(
            sorted(
                [p for p in snapshots_dir.iterdir() if p.is_dir()],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        )
        for candidate in candidates:
            if (candidate / "modules.json").exists() and (candidate / "config.json").exists():
                return candidate
    return None


def load_sentence_transformer_model():
    """Load the embedding model from a local cache when available.

    The replication pipeline should not fail just because Hugging Face is
    unreachable if the reviewer already has the model cached locally.
    """
    model_path = os.environ.get(MODEL_ENV_VAR)
    if model_path:
        logging.info(f"Loading SentenceTransformer model from ${MODEL_ENV_VAR}: {model_path}")
        return SentenceTransformer(model_path)

    local_snapshot = find_local_model_snapshot()
    if local_snapshot is not None:
        logging.info(f"Loading SentenceTransformer model from local snapshot: {local_snapshot}")
        return SentenceTransformer(str(local_snapshot))

    try:
        logging.info(f"Loading cached SentenceTransformer model: {MODEL_NAME}")
        return SentenceTransformer(MODEL_NAME, local_files_only=True)
    except TypeError:
        logging.warning(
            "Installed sentence-transformers does not support local_files_only; "
            "falling back to the default model loader."
        )
    except Exception as exc:
        logging.warning(
            f"Cached model load failed for {MODEL_NAME}: {exc}. "
            f"Falling back to Hugging Face resolution. For offline runs, set "
            f"${MODEL_ENV_VAR} to a local model snapshot path."
        )

    return SentenceTransformer(MODEL_NAME)


# ============================================================================
# Safety DiD helpers (parallel 06a pipeline with embedding-based safety)
# ============================================================================

def _nn_match_safety(df_orig, reclass_type):
    """Nearest-neighbor matching on pre-event safety_prop (identical to 06a)."""
    temp_parts = []
    control_list = []
    treated_pcs = np.unique(df_orig[df_orig.treatment_final == 1]["PRODUCTCODE"])

    for i, PC in enumerate(treated_pcs):
        treated = df_orig[df_orig.PRODUCTCODE == PC].copy()
        yr_reclass = treated["year_reclassified"].values[0]
        treated["event_time"] = treated["year"] - int(float(yr_reclass))

        control = df_orig[
            (df_orig.treatment_final == 0) & ~(df_orig.PRODUCTCODE.isin(control_list))
        ].copy()
        if len(control) == 0:
            control = df_orig[df_orig.treatment_final == 0].copy()

        control["event_time"] = control["year"] - int(float(yr_reclass))

        control_meaned = (
            control[(control.event_time < 0) & (control.event_time > -3)]
            .groupby("PRODUCTCODE").mean(numeric_only=True).reset_index()
        )
        treated_meaned = treated[
            (treated.event_time < 0) & (treated.event_time > -3)
        ].mean(numeric_only=True)

        if len(control_meaned) == 0:
            logging.warning(f"No controls for {PC}. Skipping.")
            continue

        sim_distances, sim_indices = get_similar(
            treated_meaned[["safety_prop"]].values,
            control_meaned[["safety_prop"]].values,
            topn=1,
        )
        PC_CONTROL = control_meaned.iloc[sim_indices]["PRODUCTCODE"].values[0]
        control_list.append(PC_CONTROL)

        control_keep = df_orig[df_orig.PRODUCTCODE == PC_CONTROL].copy()
        control_keep["FE"] = i
        treated["FE"] = i

        temp_parts.append(control_keep)
        temp_parts.append(treated)

    temp = pd.concat(temp_parts, ignore_index=True)
    temp = temp.drop_duplicates(subset=["year", "PRODUCTCODE", "FE"])
    return temp


def _build_safety_panel(df_safety_raw, all_pats, matched_sample, reclass_type):
    """Build the safety DiD panel with embedding-based safety classification."""
    if reclass_type == "2_1":
        df_safety_keep = df_safety_raw[
            df_safety_raw.id.isin(all_pats[all_pats.firm_size.notnull()]["id"])
        ]
        df_safety_keep = pd.merge(
            df_safety_keep,
            all_pats[["id", "firm_size", "permno", "PRODUCTCODE", "year"]],
            how="left", on="id",
        )
        w_fsize = pd.read_csv(
            config.DERIVED_DATA_DIR / "Adverse_fsize_ready_all4_oct22_24.csv"
        )
        df_safety_keep_w_permno = df_safety_keep[
            df_safety_keep.permno.isin(w_fsize.permno)
        ]
    else:
        df_safety_keep_vars = pd.merge(
            df_safety_raw,
            all_pats[["id", "PRODUCTCODE", "year"]],
            how="left", on="id",
        )
        df_safety_keep_w_permno = df_safety_keep_vars.copy()

    # Merge treatment status
    df_safety_keep_w_permno = pd.merge(
        df_safety_keep_w_permno,
        matched_sample[["PRODUCTCODE", "treatment"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )
    df_safety_keep_w_permno = df_safety_keep_w_permno[
        (df_safety_keep_w_permno.PRODUCTCODE.isin(matched_sample.PRODUCTCODE.values))
        | df_safety_keep_w_permno.treatment.isnull()
    ]

    # Aggregate to PC-year
    df_dd = df_safety_keep_w_permno.copy()
    df_dd = df_dd[df_dd.year >= 1976]
    df_dd = (
        df_dd[["PRODUCTCODE", "year", "patents", "safety"]]
        .groupby(["PRODUCTCODE", "year"]).sum().reset_index()
    )

    # Balance panel
    df_dd = (
        df_dd.set_index(["PRODUCTCODE", "year"])
        .unstack(fill_value=0).stack()
        .sort_index(level=1).reset_index()
    )

    # Merge treatment info
    df_dd = pd.merge(
        df_dd,
        matched_sample[["PRODUCTCODE", "treatment", "year_reclassified"]].drop_duplicates(),
        on="PRODUCTCODE", how="left",
    )
    df_dd.loc[df_dd.treatment.isnull(), "treatment"] = 0
    df_dd = df_dd.reset_index(drop=True)

    df_dd["year_reclassfinal"] = df_dd.groupby("PRODUCTCODE")[
        "year_reclassified"
    ].transform(pd.Series.max)
    df_dd["treatment_final"] = df_dd.groupby("PRODUCTCODE")[
        "treatment"
    ].transform(pd.Series.max)
    df_dd["treatment"] = df_dd["treatment_final"]
    df_dd["year_reclassified"] = df_dd["year_reclassfinal"]

    df_dd["FE"] = np.nan
    df_dd.loc[df_dd.treatment == 0, "FE"] = 0
    df_dd["safety_prop"] = df_dd["safety"] / df_dd["patents"]
    df_dd["safety_prop"] = df_dd["safety_prop"].fillna(0)

    # NN match
    df_dd = _nn_match_safety(df_dd, reclass_type)

    # Post-matching setup
    df_dd.loc[df_dd.treatment == 0, "year_reclassified"] = np.nan
    df_dd["year_reclass_ET"] = df_dd.groupby(["FE"])["year_reclassified"].transform(
        pd.Series.max
    )
    df_dd["factorized"] = df_dd.PRODUCTCODE.astype("category").cat.codes
    df_dd["class_by_episode"] = (
        df_dd["FE"].astype(int).astype(str) + "[SEP]" + df_dd["factorized"].astype(str)
    )
    df_dd["class_by_episode"] = df_dd.class_by_episode.astype("category").cat.codes

    df_dd["posttreat"] = 0
    df_dd.loc[
        (df_dd.treatment == 1) & (df_dd.year >= df_dd.year_reclassified - 1),
        "posttreat",
    ] = 1
    df_dd["ET"] = df_dd["year"] - df_dd["year_reclass_ET"] + 1

    df_dd.loc[df_dd["safety_prop"] > 0, "safety_prop"] = 1
    df_dd["baseline_event_count"] = df_dd.groupby("PRODUCTCODE")[
        "safety_prop"
    ].transform(pd.Series.max)
    df_dd = df_dd.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)

    n_treated = len(set(df_dd[df_dd.treatment_final == 1]["PRODUCTCODE"]))
    n_control = len(set(df_dd[df_dd.treatment_final == 0]["PRODUCTCODE"]))
    logging.info(f"Safety panel ({reclass_type}): {n_treated} treated, {n_control} control PCs")

    return df_dd


def _run_safety_did(df_dd, reclass_type):
    """Run Conley-Taber stacked DiD on the safety panel."""
    mask = (
        (df_dd.treatment_final == 1)
        & (df_dd.year - df_dd.year_reclassfinal < -1)
        & (df_dd.year - df_dd.year_reclassfinal > -4)
    )
    baseline_mean = df_dd.loc[mask, "safety_prop"].mean()
    baseline_std = df_dd.loc[mask, "safety_prop"].std()

    logging.info(
        f"Baseline safety_prop ({reclass_type}): "
        f"mean={baseline_mean:.4f}, std={baseline_std:.4f}"
    )

    cols = [
        "safety_prop", "posttreat", "treatment", "class_by_episode",
        "year", "factorized", "FE", "PRODUCTCODE",
    ]
    estimate, alpha025, alpha975 = conley_taber_stacked(
        df_dd[cols], "safety_prop", "posttreat", "treatment",
        "class_by_episode", "year", seed=config.RANDOM_SEED,
    )
    se = (estimate - alpha025) / 1.96
    logging.info(
        f"Safety DiD ({reclass_type}): est={estimate:.3f}, "
        f"CI=[{alpha025:.3f}, {alpha975:.3f}], SE={se:.3f}"
    )
    return estimate, alpha025, alpha975, baseline_mean, baseline_std


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    config.DERIVED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting safety robustness: embedding distance...")

    # Download NLTK resources
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)

    stop_words = set(stopwords.words("english"))

    # ------------------------------------------------------------------
    # Step 1: Load patent text data
    # ------------------------------------------------------------------
    text_path = config.RAW_DATA_DIR / "FDA_patents_text.csv"
    logging.info(f"Loading patent text from {text_path}...")
    title_abstract = pd.read_csv(text_path)
    logging.info(f"Loaded {len(title_abstract)} patent texts.")

    # Clean text and remove stopwords for the processed version
    logging.info("Cleaning and tokenizing patent text...")
    title_abstract["clean_input"] = title_abstract["input"].apply(clean_text)
    title_abstract["tokens"] = title_abstract["clean_input"].apply(word_tokenize)
    title_abstract["tokens"] = title_abstract["tokens"].apply(
        lambda toks: remove_stopwords(toks, stop_words)
    )
    # Reconstruct cleaned text without stopwords (used for embedding)
    title_abstract["clean_input_nostop"] = title_abstract["tokens"].apply(
        lambda tokens: " ".join(tokens)
    )

    # ------------------------------------------------------------------
    # Step 2: Load sentence-transformer model
    # ------------------------------------------------------------------
    logging.info(f"Loading SentenceTransformer model: {MODEL_NAME}...")
    sentence_model = load_sentence_transformer_model()
    logging.info("Model loaded.")

    # ------------------------------------------------------------------
    # Step 3: Preprocess reference sentences and compute centroid
    # ------------------------------------------------------------------
    processed_ref = []
    for sent in REFERENCE_SAFETY_SENTENCES:
        tokens = remove_stopwords(word_tokenize(clean_text(sent)), stop_words)
        processed_ref.append(" ".join(tokens))

    logging.info("Generating embeddings for reference safety sentences...")
    _ref_tensor = sentence_model.encode(processed_ref, convert_to_tensor=True)
    reference_embeddings = _ref_tensor.cpu().numpy()
    safety_reference_vector = np.mean(reference_embeddings, axis=0).reshape(1, -1)
    logging.info("Safety reference vector computed.")

    # ------------------------------------------------------------------
    # Step 4: Generate embeddings for all patent texts
    # ------------------------------------------------------------------
    logging.info("Generating embeddings for patent texts (this may take a while)...")
    t0 = time.time()

    # Batch encode for efficiency (sentence-transformers supports batch encoding)
    texts = title_abstract["clean_input_nostop"].fillna("").tolist()
    # Default return is numpy array — avoids O(n^2) tensor concatenation
    patent_embeddings = sentence_model.encode(
        texts, show_progress_bar=True, batch_size=256,
    )
    # Match original: empty texts get zero vectors (not model's [CLS] output)
    empty_mask = np.array([t.strip() == "" for t in texts])
    n_empty = empty_mask.sum()
    if n_empty > 0:
        patent_embeddings[empty_mask] = 0.0
        logging.info(f"Zeroed embeddings for {n_empty} empty-text patents.")
    logging.info(f"Patent embeddings generated in {time.time() - t0:.1f}s.")

    # ------------------------------------------------------------------
    # Step 5: Compute cosine similarity to safety reference
    # ------------------------------------------------------------------
    logging.info("Computing cosine similarity to safety reference...")
    # patent_embeddings is (N, dim), safety_reference_vector is (1, dim)
    similarities = cosine_similarity(patent_embeddings, safety_reference_vector).flatten()
    title_abstract["safety_similarity"] = similarities

    # ------------------------------------------------------------------
    # Step 6: Tag patents based on 99th percentile threshold
    # ------------------------------------------------------------------
    # The cutoff is the SIMILARITY_PERCENTILE quantile of safety_similarity
    # (the 99th percentile in the published specification).
    threshold = title_abstract["safety_similarity"].quantile(SIMILARITY_PERCENTILE)
    logging.info(f"{SIMILARITY_PERCENTILE:.0%} percentile threshold: {threshold:.4f}")

    title_abstract["safety_tag"] = 0
    title_abstract.loc[
        title_abstract["safety_similarity"] > threshold, "safety_tag"
    ] = 1

    n_tagged = title_abstract["safety_tag"].sum()
    logging.info(
        f"Tagged {n_tagged}/{len(title_abstract)} patents as safety-related "
        f"(threshold=p{SIMILARITY_PERCENTILE * 100:g}={threshold:.4f})"
    )
    logging.info(
        f"Similarity stats: mean={similarities.mean():.4f}, "
        f"median={np.median(similarities):.4f}, "
        f"std={similarities.std():.4f}"
    )

    # Save tagged patents
    tagged_path = config.DERIVED_DATA_DIR / "safety_tagged_patents.csv"
    title_abstract[["id", "safety_similarity", "safety_tag"]].to_csv(
        tagged_path, index=False
    )
    logging.info(f"Saved tagged patents: {tagged_path}")

    # ------------------------------------------------------------------
    # Step 7: Re-run safety DiD with embedding-based classification
    # ------------------------------------------------------------------
    logging.info("Re-running safety DiD with embedding-based safety measure...")

    # Prepare safety variable: rename safety_tag -> safety for pipeline compat
    df_safety = title_abstract[["id", "safety_tag"]].copy()
    df_safety = df_safety.rename(columns={"safety_tag": "safety"})
    df_safety["patents"] = 1

    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])

    results = []

    # II->I
    logging.info("=" * 60)
    logging.info("Embedding-based safety DiD: II->I")
    t0 = time.time()
    matched_21 = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat"])
    df_safety_21 = _build_safety_panel(df_safety, all_pats, matched_21, "2_1")
    est_21 = _run_safety_did(df_safety_21, "2_1")
    results.append({
        "reclass_type": "2_1",
        "estimate": est_21[0], "ci_lower": est_21[1], "ci_upper": est_21[2],
        "baseline_mean": est_21[3], "baseline_std": est_21[4],
    })
    logging.info(f"II->I completed in {time.time() - t0:.1f}s")

    # III->II
    logging.info("=" * 60)
    logging.info("Embedding-based safety DiD: III->II")
    t0 = time.time()
    matched_32 = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat"])
    df_safety_32 = _build_safety_panel(df_safety, all_pats, matched_32, "3_2")
    est_32 = _run_safety_did(df_safety_32, "3_2")
    results.append({
        "reclass_type": "3_2",
        "estimate": est_32[0], "ci_lower": est_32[1], "ci_upper": est_32[2],
        "baseline_mean": est_32[3], "baseline_std": est_32[4],
    })
    logging.info(f"III->II completed in {time.time() - t0:.1f}s")

    # Save results table
    results_df = pd.DataFrame(results)
    out_csv = config.TABLES_DIR / "safety_embedding_distance_estimates.csv"
    results_df.to_csv(out_csv, index=False)
    logging.info(f"Saved estimates: {out_csv}")
    logging.info(f"\n{results_df.to_string(index=False)}")

    # Record the threshold that produced these estimates in a sidecar, so the specification can
    # never be read off the wrong source (or guessed). The estimates table itself keeps the frozen
    # six-column schema the deposit ships and the manuscript's appendix quotes; the threshold lives
    # here and, per percentile, in safety_embedding_percentile_robustness.csv.
    write_percentile_sidecar()

    # ------------------------------------------------------------------
    # Step 8: Alternative similarity thresholds (JPE 2.2 in-text claim)
    # ------------------------------------------------------------------
    # The appendix states "Using the 99th similarity percentile as the threshold
    # (results are similar at the 95th)". Nothing implemented the 95th, so the
    # parenthetical had no producing program. Re-thresholding is CHEAP: the
    # per-patent cosine similarity is already stored in safety_tagged_patents.csv,
    # so no re-embedding is needed.
    emit_percentile_robustness()

    logging.info("Safety embedding-distance validation complete.")


PERCENTILE_SIDECAR_NAME = "safety_embedding_percentile_used.txt"


def write_percentile_sidecar():
    """Write the one-line sidecar naming the safety-tagging percentile this run used.

    output/tables/safety_embedding_percentile_used.txt, a single
    `similarity_percentile=<value>` line. It is route-invariant (the threshold is a package
    constant, and run_all.py scrubs the override variable from every step it launches), so the
    real-route and simulated-route copies are byte-identical. It exists because
    safety_embedding_distance_estimates.csv is frozen at the six-column schema the deposit ships:
    the specification must still be recorded next to the estimates it produced.
    """
    out_path = config.TABLES_DIR / PERCENTILE_SIDECAR_NAME
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(f"similarity_percentile={SIMILARITY_PERCENTILE:g}\n")
    logging.info(f"Saved percentile sidecar: {out_path}")
    return out_path


def emit_percentile_robustness(percentiles=None):
    """Re-threshold the stored per-patent safety similarities at alternative
    percentiles and re-run the same DiD, writing the results to
    output/tables/safety_embedding_percentile_robustness.csv.

    Reads data/derived/safety_tagged_patents.csv (id, safety_similarity,
    safety_tag), which the embedding pass above already wrote, so this costs one
    DiD per (percentile x pathway) and never re-encodes any patent text. The
    reported 99th-percentile threshold is included as the first block so the
    comparison the manuscript makes is in one file.

    Runnable on its own, without the embedding pass, via
        python3 code/06c_validate_safety_embed.py --percentile-robustness-only
    """
    tagged_path = config.DERIVED_DATA_DIR / "safety_tagged_patents.csv"
    if not tagged_path.exists():
        raise FileNotFoundError(
            f"{tagged_path} is absent; run the embedding pass first so the stored "
            f"per-patent similarities exist")
    if percentiles is None:
        percentiles = (SIMILARITY_PERCENTILE,) + tuple(SIMILARITY_PERCENTILES_ROBUST)

    tagged = pd.read_csv(tagged_path)
    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])
    matched = {rc: pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[f"{rc}_onepat"])
               for rc in ("2_1", "3_2")}

    rows = []
    for pct in percentiles:
        threshold = tagged["safety_similarity"].quantile(pct)
        df_safety = pd.DataFrame({"id": tagged["id"]})
        df_safety["safety"] = (tagged["safety_similarity"] > threshold).astype(int)
        df_safety["patents"] = 1
        logging.info(f"[percentile robustness] p{pct * 100:g}: threshold={threshold:.4f}, "
                     f"tagged={int(df_safety['safety'].sum())}")
        for rc in ("2_1", "3_2"):
            panel = _build_safety_panel(df_safety, all_pats, matched[rc], rc)
            est, lo, hi, base_mean, base_std = _run_safety_did(panel, rc)
            rows.append({
                "similarity_percentile": pct,
                "similarity_threshold": round(float(threshold), 6),
                "reclass_type": rc,
                "estimate": est, "ci_lower": lo, "ci_upper": hi,
                "baseline_mean": base_mean, "baseline_std": base_std,
                "n_obs": int(len(panel)),
            })

    out_path = config.TABLES_DIR / "safety_embedding_percentile_robustness.csv"
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    logging.info(f"Saved percentile robustness: {out_path}")
    return out_path


if __name__ == "__main__":
    if "--percentile-robustness-only" in sys.argv:
        # Cheap path: re-threshold the stored similarities without re-embedding.
        emit_percentile_robustness()   # returns the path it wrote; raises on failure
        sys.exit(0)
    else:
        sys.exit(main() or 0)
