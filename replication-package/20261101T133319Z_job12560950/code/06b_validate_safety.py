#!/usr/bin/env python
"""
06b_validate_safety.py -- Safety robustness: refined keyword classification.

FROZEN ARTIFACT (JPE Data Policy 2.2): this script TRAINS a
Word2Vec model on patent text and derives the refined-keyword safety estimates
FROM DATA. It is memory/compute heavy, so run_all treats its outputs as
precomputed artifacts by default and re-runs this script only under
--regenerate-safety-keywords. Freezing an expensive step is standard practice.
See the REPRODUCIBILITY POLICY block in run_all.py.

DETERMINISM: the Word2Vec training call is seeded AND single-threaded
(workers=1, seed=config.RANDOM_SEED), so re-running this step reproduces its
own output run to run. The shipped real-data artifacts
(data/derived/safety_vars_allpats*_v2.csv and
output/tables/safety_refined_keywords_estimates.csv) are the frozen ones the
manuscript reports.

Validates the main safety-emphasis results from 06a by using a Word2Vec-based
refinement of the safety keyword list. Trains Word2Vec on patent abstracts,
embeds safety keywords and reference sentences, computes cosine similarity,
and retains only keywords above a similarity threshold (0.7). Then re-applies
keyword extraction with the refined set and re-runs the safety DiD analysis.

This script mirrors validate_safety.py from the original codebase. The two
keyword files it produces (v2 and updated_v2) serve as alternative safety
measures for the robustness check in the paper.

Inputs:
    data/raw/FDA_patents_text.csv          (patent title+abstract text)
    data/derived/safety_vars_allpats.csv   (baseline safety flags from 06a)
    data/derived/all_patents_w_xi_oct22_24.csv
    data/derived/matched_sample_2_1_onepat.csv
    data/derived/matched_sample_3_2_onepat.csv
    data/derived/Adverse_fsize_ready_all4_oct22_24.csv

Outputs:
    data/derived/safety_vars_allpats_v2.csv           (keyword-only flags)
    data/derived/safety_vars_allpats_updated_v2.csv   (refined keyword flags)
    data/derived/word2vec_patent_corpus.model          (trained Word2Vec model)
    output/tables/safety_refined_keywords_estimates.csv  (incl. the n_obs column
        the safety-robustness table caption reports)
    output/tables/safety_term_share.csv   (in-text: the ~2% safety-term share)
"""

import sys
import logging
import time
import re
import os
from pathlib import Path

import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from flashtext import KeywordProcessor
from gensim.models import Word2Vec
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
        logging.FileHandler(config.LOGS_DIR / "06b_validate_safety.log"),
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
# Word2Vec helpers
# ============================================================================

def get_sentence_embedding(tokens, model):
    """Average Word2Vec token embeddings for a token list."""
    embeddings = [model.wv[t] for t in tokens if t in model.wv]
    if embeddings:
        return np.mean(embeddings, axis=0)
    return np.zeros(model.vector_size)


def get_keyword_embeddings(keywords, model):
    """Retrieve Word2Vec vectors for each keyword in the vocabulary."""
    vectors = {}
    missing = []
    for kw in keywords:
        if kw in model.wv:
            vectors[kw] = model.wv[kw]
        else:
            missing.append(kw)
    if missing:
        logging.warning(f"Keywords not in Word2Vec vocabulary: {missing}")
    return vectors


def compute_similarity(keyword_vectors, reference_vector):
    """Cosine similarity of each keyword vector to a reference centroid."""
    sims = {}
    for kw, vec in keyword_vectors.items():
        sims[kw] = cosine_similarity(vec.reshape(1, -1), reference_vector)[0][0]
    return sims


# ============================================================================
# Keyword extraction
# ============================================================================

SAFETY_KEYWORDS = [
    "safety", "safe", "safer", "endangering", "precautions", "unsafe",
    "hazardous", "failsafe", "safely", "dangerous", "hazard", "danger",
    "harming", "injuring", "injury", "jeopardizing", "risking", "risk",
    "complication", "life-threatening",
]

COST_KEYWORDS = [
    "cost", "price", "economic", "costs", "revenue", "savings",
    "discount", "premiums", "pricing", "budget", "expense",
    "expensive", "costly", "prices", "complexity",
]

QUALITY_KEYWORDS = [
    "performance", "reliability", "performances", "quality",
    "durability", "accuracy", "robustness", "reproducibility",
    "transferability", "effectiveness", "sensitivity",
]

REFERENCE_SAFETY_SENTENCES = [
    "The device incorporates multiple safety mechanisms to prevent accidents.",
    "Safety protocols must be strictly followed in all operational procedures.",
    "Ensuring user safety is paramount in the design of this system.",
    "The material is certified for safety under international standards.",
    "Safety features include automatic shut-off and emergency alerts.",
]


def set_flag(processor, text):
    """Return 1 if any keyword is found in text, else 0."""
    return 1 if processor.extract_keywords(text) else 0


# ============================================================================
# Safety DiD helpers (parallel 06a pipeline with alternative safety measure)
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
    """Build the safety DiD panel with alternative safety classification."""
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
# In-text number emission (JPE Policy 2.2)
# ============================================================================

def emit_safety_term_share():
    """Emit the share of patents whose title or abstract contains at least one of
    the safety terms, to output/tables/safety_term_share.csv.

    The appendix states "only about two percent of patents include such terms" as
    the reason for aggregating the measure to the device-type-year level. The
    per-patent flags ship (data/derived/safety_vars_allpats_v2.csv, written above
    from SAFETY_KEYWORDS -- the same twenty terms the appendix lists), but their
    mean was never computed anywhere. The refined-keyword share is emitted next to
    it so the two measures cannot be confused.
    """
    rows = []
    for fname, col, label, stated in (
            ("safety_vars_allpats_v2.csv", "safety",
             "Share of patents whose title or abstract contains a safety keyword", 2.0),
            ("safety_vars_allpats_updated_v2.csv", "safety_refined",
             "Share of patents flagged by the Word2Vec-refined keyword set", "")):
        path = config.DERIVED_DATA_DIR / fname
        if not path.exists():
            # Both official routes supply these per-patent flag files (the restricted route
            # regenerates them here, the simulated route materializes them), so an absent one
            # means a required input is missing, not that this share is optional.
            raise FileNotFoundError(
                f"safety-term share: required input {path} not found. Run the data-generation "
                "steps (restricted route) or materialize the simulated payload before step 16.")
        df = pd.read_csv(path, usecols=[col])
        rows.append({
            "metric": f"{col}_term_share_pct",
            "description": label,
            "n_patents": int(len(df)),
            "computed": round(100.0 * float(df[col].mean()), 4),
            "manuscript_value": stated,
        })
    if not rows:
        raise RuntimeError(
            "safety-term share export FAILED: neither per-patent safety flag file is "
            "present, so the manuscript's ~2%% share has no producing output")
    out_path = config.TABLES_DIR / "safety_term_share.csv"
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["metric", "description", "n_patents", "computed",
                                "manuscript_value"]).to_csv(out_path, index=False)
    for r in rows:
        logging.info(f"  [safety share] {r['metric']}: {r['computed']}% of {r['n_patents']} patents")
    logging.info(f"Saved safety-term share: {out_path}")


def emit_safety_panel_sizes():
    """Add/refresh the `n_obs` column of output/tables/safety_refined_keywords_estimates.csv.

    The manuscript's safety-robustness table caption states a sample size for each
    panel. This emits the per-panel observation count (`n_obs`) so the Table D.12
    sample sizes are printed from program output by 10b_format_remaining_tables.py.
    It rebuilds each panel from the refined per-patent flags
    -- the same construction _run_safety_did estimates on -- and records its
    device-type-by-year observation count. It touches ONLY the n_obs column: no
    estimate, CI or baseline is recomputed or rewritten.
    """
    # Fail closed: without n_obs, step 31 cannot print the sample-size row of Table D.12
    # (10b_format_remaining_tables.py raises on a missing n_obs column). A silent skip here
    # would surface much later as a confusing formatting error.
    est_path = config.TABLES_DIR / "safety_refined_keywords_estimates.csv"
    if not est_path.exists():
        raise FileNotFoundError(
            f"safety panel sizes: {est_path} not found -- the refined-keyword estimates must "
            "exist before their sample sizes can be recorded.")
    flags_path = config.DERIVED_DATA_DIR / "safety_vars_allpats_updated_v2.csv"
    if not flags_path.exists():
        raise FileNotFoundError(
            f"safety panel sizes: required input {flags_path} not found. Run the data-generation "
            "steps (restricted route) or materialize the simulated payload before step 16.")

    df_safety = pd.read_csv(flags_path)
    df_safety = df_safety.rename(columns={"safety_refined": "safety"})
    df_safety["patents"] = 1
    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])

    sizes = {}
    for rc in ("2_1", "3_2"):
        matched = pd.read_csv(
            config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[f"{rc}_onepat"])
        panel = _build_safety_panel(df_safety, all_pats, matched, rc)
        sizes[rc] = int(len(panel))
        logging.info(f"  [safety N] {rc} panel: {sizes[rc]} device-type-year observations")

    # Read as text so the existing estimate/CI/baseline cells are written back
    # byte-for-byte: this emitter adds a column, it must never reformat a number.
    est = pd.read_csv(est_path, dtype=str)
    est["n_obs"] = est["reclass_type"].astype(str).map(
        {k: str(v) for k, v in sizes.items()})
    est.to_csv(est_path, index=False)
    logging.info(f"  [safety N] wrote n_obs into {est_path.name}")


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    config.DERIVED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting safety robustness: refined keywords...")

    precomputed_outputs = [
        config.DERIVED_DATA_DIR / "safety_vars_allpats_v2.csv",
        config.DERIVED_DATA_DIR / "safety_vars_allpats_updated_v2.csv",
        config.TABLES_DIR / "safety_refined_keywords_estimates.csv",
    ]
    if (
        os.environ.get("FDA_FORCE_SAFETY_KEYWORDS") != "1"
        and all(path.exists() for path in precomputed_outputs)
    ):
        logging.info(
            "Using included safety keyword-validation artifacts "
            "(set FDA_FORCE_SAFETY_KEYWORDS=1 to regenerate the high-RAM "
            "Word2Vec/keyword pipeline)."
        )
        emit_safety_term_share()
        emit_safety_panel_sizes()
        # Table D.12 itself is written by step 31 (10b_format_remaining_tables.py), which also
        # has 06c's embedding-distance estimates. See the note above __main__.
        return 0

    # Download NLTK resources
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)

    stop_words = set(stopwords.words("english"))

    # ------------------------------------------------------------------
    # Step 1: Load patent text data
    # ------------------------------------------------------------------
    text_path = config.RAW_DATA_DIR / "FDA_patents_text.csv"
    logging.info(f"Loading patent text from {text_path}...")
    title_abstract = pd.read_csv(text_path)
    logging.info(f"Loaded {len(title_abstract)} patent texts.")

    # Clean and tokenize
    logging.info("Cleaning and tokenizing patent text...")
    title_abstract["clean_input"] = title_abstract["input"].apply(clean_text)
    title_abstract["tokens"] = title_abstract["clean_input"].apply(word_tokenize)
    title_abstract["tokens"] = title_abstract["tokens"].apply(
        lambda toks: remove_stopwords(toks, stop_words)
    )

    # ------------------------------------------------------------------
    # Step 2: Train Word2Vec on patent corpus
    # ------------------------------------------------------------------
    logging.info("Training Word2Vec model...")
    t0 = time.time()
    corpus = title_abstract["tokens"].tolist()
    # Determinism (JPE Policy 2.1b): gensim's Word2Vec is reproducible ONLY when it
    # is both seeded AND restricted to a single worker thread -- with workers>1 the
    # order in which threads consume sentences is set by OS scheduling, so upstream
    # documentation states that "for a fully deterministically-reproducible run, you
    # must also limit the model to a single worker thread (workers=1)".
    word2vec_model = Word2Vec(
        sentences=corpus, vector_size=100, window=5, min_count=5,
        workers=1, seed=config.RANDOM_SEED,
    )
    logging.info(f"Word2Vec trained in {time.time() - t0:.1f}s.")

    model_path = config.DERIVED_DATA_DIR / "word2vec_patent_corpus.model"
    word2vec_model.save(str(model_path))
    logging.info(f"Saved Word2Vec model: {model_path}")

    # ------------------------------------------------------------------
    # Step 3: Compute reference safety embedding (centroid of reference
    #         sentence embeddings)
    # ------------------------------------------------------------------
    processed_ref = []
    for sent in REFERENCE_SAFETY_SENTENCES:
        tokens = remove_stopwords(word_tokenize(clean_text(sent)), stop_words)
        processed_ref.append(tokens)

    ref_embeddings = [get_sentence_embedding(toks, word2vec_model) for toks in processed_ref]
    safety_reference_vector = np.mean(ref_embeddings, axis=0).reshape(1, -1)

    # ------------------------------------------------------------------
    # Step 4: Initial keyword extraction (all keywords)
    # ------------------------------------------------------------------
    logging.info("Applying initial keyword extraction...")

    safety_processor = KeywordProcessor(case_sensitive=False)
    cost_processor = KeywordProcessor(case_sensitive=False)
    quality_processor = KeywordProcessor(case_sensitive=False)

    safety_processor.add_keywords_from_list(SAFETY_KEYWORDS)
    cost_processor.add_keywords_from_list(COST_KEYWORDS)
    quality_processor.add_keywords_from_list(QUALITY_KEYWORDS)

    title_abstract["safety"] = title_abstract["clean_input"].apply(
        lambda x: set_flag(safety_processor, x)
    )
    title_abstract["cost"] = title_abstract["clean_input"].apply(
        lambda x: set_flag(cost_processor, x)
    )
    title_abstract["quality"] = title_abstract["clean_input"].apply(
        lambda x: set_flag(quality_processor, x)
    )

    # Save v2 (all keywords, before refinement)
    v2_path = config.DERIVED_DATA_DIR / "safety_vars_allpats_v2.csv"
    title_abstract[["id", "safety", "cost", "quality"]].to_csv(v2_path, index=False)
    logging.info(f"Saved initial keyword flags: {v2_path}")

    # ------------------------------------------------------------------
    # Step 5: Refine safety keywords via Word2Vec similarity
    # ------------------------------------------------------------------
    logging.info("Computing keyword-reference similarity for refinement...")

    safety_keyword_vectors = get_keyword_embeddings(SAFETY_KEYWORDS, word2vec_model)
    safety_similarities = compute_similarity(safety_keyword_vectors, safety_reference_vector)

    sim_df = (
        pd.DataFrame.from_dict(safety_similarities, orient="index", columns=["cosine_similarity"])
        .sort_values(by="cosine_similarity", ascending=False)
    )
    logging.info(f"Keyword similarities:\n{sim_df.to_string()}")

    similarity_threshold = 0.7
    refined_keywords = sim_df[sim_df["cosine_similarity"] >= similarity_threshold].index.tolist()
    logging.info(
        f"Refined keywords (threshold={similarity_threshold}): {refined_keywords}"
    )

    # ------------------------------------------------------------------
    # Step 6: Re-apply safety flags with refined keywords
    # ------------------------------------------------------------------
    logging.info("Re-applying safety flags with refined keywords...")
    safety_processor_refined = KeywordProcessor(case_sensitive=False)
    safety_processor_refined.add_keywords_from_list(refined_keywords)

    title_abstract["safety_refined"] = title_abstract["clean_input"].apply(
        lambda x: 1 if safety_processor_refined.extract_keywords(x) else 0
    )

    updated_path = config.DERIVED_DATA_DIR / "safety_vars_allpats_updated_v2.csv"
    title_abstract[["id", "safety_refined", "cost", "quality"]].to_csv(
        updated_path, index=False
    )
    logging.info(f"Saved refined keyword flags: {updated_path}")

    n_orig = title_abstract["safety"].sum()
    n_refined = title_abstract["safety_refined"].sum()
    logging.info(
        f"Safety flags: original={n_orig}, refined={n_refined} "
        f"(change: {n_refined - n_orig})"
    )

    # ------------------------------------------------------------------
    # Step 7: Re-run safety DiD with refined keywords
    # ------------------------------------------------------------------
    logging.info("Re-running safety DiD with refined keywords...")

    # Prepare the safety variable for the DiD pipeline
    df_safety = title_abstract[["id", "safety_refined", "cost", "quality"]].copy()
    df_safety = df_safety.rename(columns={"safety_refined": "safety"})
    df_safety["patents"] = 1

    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])

    results = []

    # II->I
    logging.info("=" * 60)
    logging.info("Refined-keyword safety DiD: II->I")
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
    logging.info("Refined-keyword safety DiD: III->II")
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
    out_csv = config.TABLES_DIR / "safety_refined_keywords_estimates.csv"
    results_df.to_csv(out_csv, index=False)
    logging.info(f"Saved estimates: {out_csv}")
    logging.info(f"\n{results_df.to_string(index=False)}")

    # ------------------------------------------------------------------
    # In-text numbers (JPE 2.2): the ~2% safety-term share and the panel sizes
    # the robustness table's caption reports.
    # ------------------------------------------------------------------
    emit_safety_term_share()
    emit_safety_panel_sizes()

    logging.info("Safety refined-keyword validation complete.")
    return 0


# Table D.12 (safety robustness) is formatted by code/10b_format_remaining_tables.py, which runs
# at step 31 -- AFTER step 17 (06c) has produced the embedding-distance estimates this step cannot
# see. This step produces only the estimates CSV (including its n_obs column); the single writer of
# output/tables/Formatted/TableD12_SafetyRobustness.tex is 10b_format_remaining_tables.py.


if __name__ == "__main__":
    sys.exit(main())
