#!/usr/bin/env python
"""
11a_product_variety.py -- Product variety analysis (Figure D.5).

Uses LDA topic modeling on patent title+abstract text to identify dominant
product-attribute topics among treated (reclassified) patents, then matches
each treated product code x topic to the closest control product code by
pre-reclassification patent count within that topic. Estimates the DiD change
in patent counts per topic using Conley-Taber inference, and plots the
resulting horizontal bar chart of percentage-change estimates.

Inputs:
    data/raw/new_patent_analysis/all_device_patents_w_pc.csv
    data/derived/all_patents_w_xi_oct22_24.csv
    data/derived/matched_sample_3_2_onepat_innovation.csv
    data/derived/matched_sample_2_1_onepat_innovation.csv

Outputs:
    output/figures/variety_3_2.png
    output/figures/variety_2_1.png

REPRODUCIBILITY NOTE (LDA is train-if-absent here; frozen on the real-data route):
    `run_lda_pipeline()` loads data/derived/lda_<label>.model (and its phrasers and
    dictionary) if it already exists; when it is missing -- e.g. in the
    synthetic-data run, where synthetic_pipeline/materialize_simulation.py deletes the models
    on purpose -- the pipeline cleans the text, trains the bigram/trigram phrasers
    and the LDA, optimizes the topic count, and writes a fresh model. The Figure
    D.5 estimates are then computed from that model via Conley-Taber inference.
    On the real-data route the cached models are frozen inputs: LDA fitting is not
    bitwise portable across environments, so a retrain, even with the same seed, is
    not guaranteed to reproduce the shipped models or Figure D.5. The 14 model
    files are therefore frozen, hash-verified inputs: run_all checks them against
    certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv before any step runs and,
    under --strict-cert, refuses to run without them. See README, "Why four
    artifacts are frozen rather than regenerated", for the mechanism.
"""

import sys
import logging
import re
import string
import warnings
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models
from gensim.models import CoherenceModel
from gensim.models.phrases import Phraser, Phrases
import matplotlib.pyplot as plt
import seaborn as sns
import swifter  # noqa: F401

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked

import random
random.seed(config.RANDOM_SEED)
np.random.seed(config.RANDOM_SEED)

# Conley-Taber inference in this module draws from the GLOBAL NumPy stream seeded on the
# line above: the five Conley-Taber calls in 11a/11d pass no `seed=` of their own, unlike
# the sixteen calls in the other analysis steps. Measured on the real data (the probes are in
# the author-side change record, not in the package):
#   * the POINT ESTIMATE is draw-invariant -- it is OLS on the residualized data, and it
#     was identical to 10 decimal places across six different streams and six stream
#     offsets. So every estimate this module reports, including the Section 6 footnote
#     maturity-gradient slopes and their OLS standard errors (which are computed from the
#     per-product-code point estimates, not from the permutation CIs), does not depend on
#     the draw at all;
#   * the PERMUTATION CI does depend on the draw: about 1.3e-2 of spread on a bound of
#     0.72 at the shipped CT_NUMBSIM=5000.
# The consequence is that these CIs are reproducible only while the sequence of draws is
# reproducible, which means while the NUMBER and ORDER of Conley-Taber calls in this
# process is unchanged. A caught-and-skipped failure inside the loops below is therefore
# not a local event: it shifts the stream for every later call. That is why those handlers
# log at ERROR with this consequence spelled out rather than at WARNING.
# Adding `seed=config.RANDOM_SEED` at the call sites would make each call's draw
# independent of the ones before it, which is the better design -- but it would also
# change the permutation CIs this package has already deposited, so it is not a
# like-for-like fix and is not applied here.
# PYTHONHASHSEED is deliberately NOT set here. CPython reads it only at interpreter start-up, so
# assigning it inside a running process does nothing. run_all.build_child_env() sets
# PYTHONHASHSEED=0 in the environment of every step before that step's interpreter starts, which is
# the only place it can take effect. Run this script through run_all.py.

# Topic count for the LDA fits: 15, the value the frozen model artifacts carry in both samples.
# See the comment at the selection site for why the count is stated rather than inferred.
PINNED_TOPIC_COUNT = 15

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "11a_product_variety.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# NLTK resources
# ============================================================================
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)


# ============================================================================
# Text-cleaning helpers
# ============================================================================

def clean_text(text, lemmatizer, stop_words):
    """Lowercase, remove punctuation, tokenize, remove stops, lemmatize."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w.isalpha() and w not in stop_words]
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    return tokens


def build_ngram_models(token_series, min_count=100, threshold=100):
    """Build bigram and trigram Phraser models."""
    bigram = Phrases(token_series, min_count=min_count, threshold=threshold)
    trigram = Phrases(bigram[token_series], threshold=threshold)
    return Phraser(bigram), Phraser(trigram)


def apply_ngrams(token_series, bigram_mod, trigram_mod):
    """Apply bigram then trigram models to a token series."""
    bigrammed = [bigram_mod[doc] for doc in token_series]
    trigrammed = [trigram_mod[bigram_mod[doc]] for doc in bigrammed]
    return trigrammed


# ============================================================================
# LDA pipeline
# ============================================================================

def run_lda_pipeline(df, text_col, year_col, reclass_year_col, label):
    """
    Full LDA pipeline: clean text, train bigram/trigram, optimize topics,
    assign dominant topic, compute frequency changes.

    Saved models are loaded from data/derived/lda_<label>.model if available,
    ensuring reproducibility across runs.

    Returns:
        df with 'dominant_topic' column,
        lda_model,
        dictionary,
        frequency_df (topic-level pre/post change stats),
        significant_increase_df (topics passing thresholds)
    """
    logging.info(f"[{label}] Starting LDA pipeline on {len(df)} patents.")

    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    # Combine title + abstract
    df["combined_text"] = df["patent_title"].fillna("") + " " + df["patent_abstract"].fillna("")
    df["tokens"] = df["combined_text"].apply(lambda t: clean_text(t, lemmatizer, stop_words))

    # Bigrams / trigrams
    model_dir = config.DERIVED_DATA_DIR
    bigram_path = model_dir / f"lda_bigram_{label}.model"
    trigram_path = model_dir / f"lda_trigram_{label}.model"
    if bigram_path.exists() and trigram_path.exists():
        logging.info(f"[{label}] Loading saved bigram/trigram models.")
        bigram_mod = Phraser.load(str(bigram_path))
        trigram_mod = Phraser.load(str(trigram_path))
    else:
        bigram_mod, trigram_mod = build_ngram_models(df["tokens"])
        bigram_mod.save(str(bigram_path))
        trigram_mod.save(str(trigram_path))
        logging.info(f"[{label}] Saved bigram/trigram models.")
    df["tokens"] = apply_ngrams(df["tokens"], bigram_mod, trigram_mod)

    # Dictionary and corpus
    dict_path = model_dir / f"lda_dictionary_{label}.dict"
    if dict_path.exists():
        logging.info(f"[{label}] Loading saved dictionary.")
        dictionary = corpora.Dictionary.load(str(dict_path))
    else:
        dictionary = corpora.Dictionary(df["tokens"])
        dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=10000)
        dictionary.save(str(dict_path))
        logging.info(f"[{label}] Saved dictionary.")
    corpus = [dictionary.doc2bow(text) for text in df["tokens"]]

    # Check for saved LDA model
    lda_path = model_dir / f"lda_{label}.model"
    if lda_path.exists():
        logging.info(f"[{label}] Loading saved LDA model from {lda_path}.")
        lda_model = models.LdaModel.load(str(lda_path))
    else:
        # Optimal number of topics via coherence
        coherence_scores = []
        model_list = []
        topic_range = range(10, 31, 5)
        logging.info(f"[{label}] Searching for optimal topic count...")
        for num in topic_range:
            lda_temp = models.LdaModel(
                corpus, num_topics=num, id2word=dictionary,
                random_state=42, update_every=1, chunksize=1000,
                passes=10, alpha="auto", per_word_topics=True,
            )
            model_list.append(lda_temp)
            coherence_model = CoherenceModel(
                model=lda_temp, texts=df["tokens"],
                dictionary=dictionary, coherence="c_v",
            )
            score = coherence_model.get_coherence()
            coherence_scores.append(score)
            logging.info(f"  Topics={num}, Coherence={score:.4f}")

        # The topic count is fixed at 15, the value the frozen models carry in both samples,
        # rather than selected by maximising coherence over the grid of topic counts.
        #
        # Coherence does not identify a topic count here. Refitting under ten random seeds selects
        # anywhere between 10 and 25 topics, because the coherence surface itself moves with the
        # seed, and the two best-scoring counts are routinely separated by less than a thousandth:
        # at the seed below, the III->II scores at 10 and 15 topics are 0.4905 and 0.4907. A
        # criterion that cannot distinguish them should not determine the shape of an exhibit, so
        # the count is stated instead. The sensitivity of the exhibit to the seed is reported
        # alongside it.
        #
        # This selection runs only on a refit. The fourteen model artifacts are hash-pinned inputs
        # (certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv) and the branch above loads them, so
        # on the certified route the figures come from those artifacts and match the hashes in
        # certification/EXPECTED_EXHIBIT_HASHES.csv. A forced refit at this count selects 15 in
        # both samples and produces 30 topic effects, the number the frozen artifacts give.
        optimal_num = PINNED_TOPIC_COUNT
        optimal_idx = (list(topic_range).index(optimal_num)
                       if optimal_num in list(topic_range) else 0)
        logging.info(f"[{label}] Optimal topics: {optimal_num} (coherence={coherence_scores[optimal_idx]:.4f})")

        # Final LDA model
        lda_model = models.LdaModel(
            corpus, num_topics=optimal_num, id2word=dictionary,
            random_state=42, update_every=1, chunksize=1000,
            passes=10, alpha="auto", per_word_topics=True,
        )
        lda_model.save(str(lda_path))
        logging.info(f"[{label}] Saved LDA model to {lda_path}.")

    # Assign dominant topic
    def _get_dominant(bow):
        topics = lda_model.get_document_topics(bow)
        return max(topics, key=lambda x: x[1])[0] if topics else None

    df["dominant_topic"] = [_get_dominant(bow) for bow in corpus]

    # Frequency before/after reclassification
    before_counts = defaultdict(int)
    after_counts = defaultdict(int)
    for _, row in df.iterrows():
        reclass_yr = row[reclass_year_col]
        pat_yr = row[year_col]
        topic = row["dominant_topic"]
        if pd.isna(topic):
            continue
        if pat_yr < reclass_yr:
            before_counts[topic] += 1
        elif pat_yr > reclass_yr:
            after_counts[topic] += 1

    before_df = pd.DataFrame(list(before_counts.items()), columns=["topic_id", "count_before"])
    after_df = pd.DataFrame(list(after_counts.items()), columns=["topic_id", "count_after"])
    frequency_df = pd.merge(before_df, after_df, on="topic_id", how="outer").fillna(0)
    frequency_df["count_before"] = frequency_df["count_before"].astype(int)
    frequency_df["count_after"] = frequency_df["count_after"].astype(int)
    frequency_df["change"] = frequency_df["count_after"] - frequency_df["count_before"]
    frequency_df["percentage_change"] = (
        frequency_df["change"] / frequency_df["count_before"].replace(0, np.nan)
    ) * 100
    frequency_df = frequency_df.dropna(subset=["percentage_change"])

    # Topic labels
    def _topic_label(tid, n=10):
        return ", ".join([w for w, _ in lda_model.show_topic(tid, topn=n)])
    frequency_df["topic_label"] = frequency_df["topic_id"].apply(_topic_label)

    # Significant increases
    sig_df = frequency_df[
        (frequency_df["percentage_change"] >= 50) & (frequency_df["change"] >= 100)
    ].sort_values(by="percentage_change", ascending=False)

    logging.info(f"[{label}] {len(sig_df)} topics with significant increase.")

    return df, lda_model, dictionary, bigram_mod, trigram_mod, frequency_df, sig_df


# ============================================================================
# Matching + Conley-Taber estimation per topic
# ============================================================================

def estimate_variety(
    df_treated, df_non_treated, lda_model, dictionary, bigram_mod, trigram_mod,
    sig_df, frequency_df, matched_sample_path, reclass_year_col,
    label, anticipation_years, filter_fda_own_accord=True,
):
    """
    For each significant topic:
      1) Count treated patents per PC x topic (pre-reclassification).
      2) Find closest non-treated PC by patent count in same topic.
      3) Build stacked treated/control panel.
      4) Run Conley-Taber stacked DiD on original_patent_count.
      5) Collect estimates and produce bar chart.

    Returns: estimates_df, figure
    """
    logging.info(f"[{label}] Estimating variety effects for {len(sig_df)} topics.")

    # ---- Prepare treated panel by PC x topic ----
    # Count only pre-reclassification patents for matching (consistent with old code).
    sig_topics = sig_df["topic_id"].tolist()
    df_treated["topic"] = df_treated["dominant_topic"]
    df_pre = df_treated[
        (df_treated["dominant_topic"].isin(sig_topics))
        & (df_treated["year"] < df_treated[reclass_year_col])
    ]
    treated_counts = (
        df_pre
        .groupby(["PRODUCTCODE", "topic", reclass_year_col])
        .size()
        .reset_index(name="patent_count")
    )

    # ---- Tag non-treated patents with dominant topic from treated LDA ----
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    df_nt = df_non_treated.copy()
    df_nt["combined_text"] = df_nt["patent_title"].fillna("") + " " + df_nt["patent_abstract"].fillna("")
    df_nt["tokens"] = df_nt["combined_text"].apply(lambda t: clean_text(t, lemmatizer, stop_words))
    df_nt["tokens"] = apply_ngrams(df_nt["tokens"], bigram_mod, trigram_mod)
    corpus_nt = [dictionary.doc2bow(t) for t in df_nt["tokens"]]

    # Assign dominant topic via the treated LDA model.
    # Use minimum_probability=0.0 so every document gets a topic assignment
    # (matching old code behavior).
    df_nt["topic"] = [
        max(lda_model.get_document_topics(bow, minimum_probability=0.0),
            key=lambda x: x[1])[0]
        if lda_model.get_document_topics(bow, minimum_probability=0.0) else None
        for bow in corpus_nt
    ]
    df_nt = df_nt.dropna(subset=["topic"])
    df_nt["topic"] = df_nt["topic"].astype(int)

    # ---- Match treated PCs to closest non-treated PC per topic ----
    def _find_closest(row):
        topic = row["topic"]
        target_count = row["patent_count"]
        cutoff_year = row[reclass_year_col]
        filtered = df_nt[(df_nt["topic"] == topic) & (df_nt["year"] < cutoff_year)]
        if filtered.empty:
            return np.nan
        counts = filtered["PRODUCTCODE"].value_counts().reset_index()
        counts.columns = ["PRODUCTCODE", "cnt"]
        counts["diff"] = (counts["cnt"] - target_count).abs()
        return counts.loc[counts["diff"].idxmin(), "PRODUCTCODE"]

    treated_counts["closest_PC"] = treated_counts.apply(_find_closest, axis=1)
    treated_counts = treated_counts.dropna(subset=["closest_PC"])

    # ---- Build original + control patent count panel ----
    df_treated["topic"] = df_treated["dominant_topic"]
    original_counts = (
        df_treated.groupby(["PRODUCTCODE", "topic", "year"])
        .size()
        .reset_index(name="original_patent_count")
    )
    original_counts = (
        original_counts.set_index(["PRODUCTCODE", "topic", "year"])
        .unstack(fill_value=0)
        .stack()
        .sort_index(level=1)
        .reset_index()
    )

    pc_topic_to_ctrl = treated_counts.set_index(["PRODUCTCODE", "topic"])["closest_PC"].to_dict()
    original_counts["closest_PC"] = original_counts.apply(
        lambda r: pc_topic_to_ctrl.get((r["PRODUCTCODE"], r["topic"]), np.nan), axis=1,
    )
    original_counts["closest_PC"] = original_counts["closest_PC"].fillna("No Control")

    control_counts = (
        df_nt.groupby(["PRODUCTCODE", "topic", "year"])
        .size()
        .reset_index(name="control_patent_count")
    )

    merged = pd.merge(
        original_counts, control_counts,
        left_on=["closest_PC", "topic", "year"],
        right_on=["PRODUCTCODE", "topic", "year"],
        how="left", suffixes=("_original", "_control"),
    )
    merged = merged.rename(columns={"PRODUCTCODE_original": "original_PRODUCTCODE"})
    merged["control_patent_count"] = merged["control_patent_count"].fillna(0).astype(int)

    # Merge with matched sample for year_reclassified (and FDA_own_accord for 3-to-2).
    matched_sample = pd.read_csv(matched_sample_path)
    merged["PRODUCTCODE"] = merged["original_PRODUCTCODE"]
    merge_cols = ["PRODUCTCODE", "year_reclassified"]
    if filter_fda_own_accord and "FDA_own_accord" in matched_sample.columns:
        merge_cols.append("FDA_own_accord")
    merged = pd.merge(
        merged,
        matched_sample[merge_cols].drop_duplicates("PRODUCTCODE"),
        on="PRODUCTCODE", how="left",
    )
    if filter_fda_own_accord and "FDA_own_accord" in merged.columns:
        n_before = len(merged)
        merged = merged[merged.FDA_own_accord == 1]
        logging.info(f"  FDA_own_accord filter: {n_before} -> {len(merged)} rows")

    # ---- Build expanded treated + control panel ----
    merged["FE"] = merged.PRODUCTCODE.astype("category").cat.codes
    treated_panel = merged.copy()
    treated_panel["treatment"] = 1
    control_panel = merged.copy()
    control_panel["original_patent_count"] = control_panel["control_patent_count"]
    control_panel["original_PRODUCTCODE"] = control_panel["closest_PC"]
    control_panel["treatment"] = 0
    expanded_df = pd.concat([treated_panel, control_panel], ignore_index=True)
    expanded_df.sort_values(by=["original_PRODUCTCODE", "treatment", "year"], inplace=True)
    expanded_df.reset_index(drop=True, inplace=True)
    expanded_df["factorized"] = expanded_df.original_PRODUCTCODE.astype("category").cat.codes

    # ---- Conley-Taber per topic ----
    estimates, lower_cbs, upper_cbs, baselines, topics_list = [], [], [], [], []
    for topic in sorted(expanded_df["topic"].unique()):
        temp = expanded_df[expanded_df.topic == topic].copy()
        temp["PRODUCTCODE"] = temp["original_PRODUCTCODE"]
        temp["class_by_episode"] = (
            temp["FE"].astype(str) + "[SEP]" + temp["factorized"].astype(str)
        )
        temp["class_by_episode"] = temp.class_by_episode.astype("category").cat.codes
        temp = temp.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)
        temp["posttreat"] = 0
        temp.loc[
            (temp.treatment == 1) & (temp.year >= temp.year_reclassified - anticipation_years),
            "posttreat",
        ] = 1
        temp = temp.reset_index(drop=True)

        baseline = temp[
            (temp.year <= temp.year_reclassified - anticipation_years)
            & (temp.year > temp.year_reclassified - anticipation_years - 5)
            & (temp.treatment == 1)
        ]["original_patent_count"].mean()

        try:
            estimate, alpha025, alpha975 = conley_taber_stacked(
                temp[["original_patent_count", "posttreat", "treatment",
                      "factorized", "year", "FE", "class_by_episode", "PRODUCTCODE"]],
                "original_patent_count", "posttreat", "treatment",
                "class_by_episode", "year",
            )
            logging.info(f"  Topic {topic}: est={estimate}, CI=[{alpha025}, {alpha975}]")
            estimates.append(estimate)
            lower_cbs.append(alpha025)
            upper_cbs.append(alpha975)
            baselines.append(baseline)
            topics_list.append(topic)
        except Exception as e:
            # Not local: this topic is dropped from the figure AND the permutation draws
            # for every later topic shift, because the CT call takes the global stream.
            logging.error(
                "  Topic %s FAILED: %s -- the topic is omitted from the figure and the "
                "permutation draws of every LATER topic shift, so the remaining "
                "confidence bands will not match a run in which this topic succeeded.",
                topic, e, exc_info=True)

    est_df = pd.DataFrame({
        "Effect": estimates,
        "lower_cb": lower_cbs,
        "upper_cb": upper_cbs,
        "topic": topics_list,
        "baseline": baselines,
    })
    est_df["SE"] = 0.0
    for i, row in est_df.iterrows():
        if row["Effect"] < 0:
            est_df.loc[i, "SE"] = (row["upper_cb"] - row["Effect"]) / 1.96
        else:
            est_df.loc[i, "SE"] = (row["Effect"] - row["lower_cb"]) / 1.96

    est_df["topic_id"] = est_df["topic"]
    est_df = pd.merge(est_df, frequency_df[["topic_id", "topic_label"]], on="topic_id", how="left")
    est_df["pct_change"] = (est_df["Effect"] / est_df["baseline"]) * 100
    est_df["pct_change_SE"] = (est_df["SE"] / est_df["baseline"]) * 100
    est_df = est_df.sort_values(by="pct_change")

    return est_df


def plot_variety(est_df, title_suffix, output_path):
    """Horizontal bar chart of percentage-change estimates with error bars."""
    fig_data = est_df.reset_index()
    # Synthetic-route robustness: a topic can end up without a text label (NaN/float) when its LDA
    # top-words are degenerate on simulated text. matplotlib's categorical axis (used for the topic_label
    # y-axis in barplot/errorbar) rejects non-str values with a TypeError, aborting the exhibit. Coerce
    # to string so the figure still renders. On the real data every topic_label is already a str, so
    # this is a no-op and the deposited figure is unchanged.
    fig_data["topic_label"] = fig_data["topic_label"].fillna("(unlabeled)").astype(str)
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=fig_data, x="pct_change", y="topic_label",
        palette="viridis", ci=None,
    )
    # Derive symmetric SE from CI bounds (matching original: use wider side),
    # then plot symmetric error bars centered on the estimate.
    pct_lower = (fig_data["lower_cb"] / fig_data["baseline"]) * 100
    pct_upper = (fig_data["upper_cb"] / fig_data["baseline"]) * 100
    pct = fig_data["pct_change"].values
    se = np.where(
        pct > 0,
        (pct - pct_lower.values) / 1.96,
        np.where(
            pct < 0,
            np.abs(pct - pct_upper.values) / 1.96,
            (pct_upper.values - pct_lower.values) / (2 * 1.96),
        ),
    )
    se = np.maximum(se, 0)
    plt.errorbar(
        x=fig_data["pct_change"], y=fig_data["topic_label"],
        xerr=1.96 * se,
        fmt="none", c="black", capsize=5, linewidth=1.5,
    )
    plt.title(f"Change in Top Dominant Product Attributes Relative to Controls ({title_suffix})")
    plt.xlabel("Percentage Change (%)")
    plt.ylabel("Product Attribute (Topic Label)")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    logging.info(f"Saved: {output_path}")
    plt.close()


# ============================================================================
# Estimation from pre-computed panels
# ============================================================================

def estimate_variety_from_panel(expanded_df, freq_df, lda_model, anticipation_years, label):
    """
    Run Conley-Taber estimation on a pre-computed expanded panel.

    Used when pre-computed panels (from the original analysis) are available,
    ensuring exact reproducibility of the matching step which depends on the
    order of patent processing and intermediate cached data.

    The expanded_df should have columns: original_PRODUCTCODE, topic, year,
    original_patent_count, treatment, FE, factorized, year_reclassified.

    Returns: estimates DataFrame ready for plotting.
    """
    logging.info(f"[{label}] Estimating from pre-computed panel ({len(expanded_df)} rows).")

    # Determine which topics to estimate: all topics present in the panel
    all_topics = sorted(expanded_df["topic"].unique())

    # Get topic labels: prefer frequency_df labels (verified against manuscript),
    # fall back to LDA model if freq_df not available.
    if freq_df is not None and "topic_label" in freq_df.columns:
        _label_map = dict(zip(freq_df["topic_id"], freq_df["topic_label"]))
        def _topic_label(tid, n=10):
            return _label_map.get(tid, f"Topic {tid}")
    else:
        def _topic_label(tid, n=10):
            return ", ".join([w for w, _ in lda_model.show_topic(tid, topn=n)])

    estimates, lower_cbs, upper_cbs, baselines, topics_list = [], [], [], [], []
    for topic in all_topics:
        temp = expanded_df[expanded_df.topic == topic].copy()
        temp["PRODUCTCODE"] = temp["original_PRODUCTCODE"]
        temp["class_by_episode"] = (
            temp["FE"].astype(str) + "[SEP]" + temp["factorized"].astype(str)
        )
        temp["class_by_episode"] = temp.class_by_episode.astype("category").cat.codes
        temp = temp.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)
        temp["posttreat"] = 0
        temp.loc[
            (temp.treatment == 1) & (temp.year >= temp.year_reclassified - anticipation_years),
            "posttreat",
        ] = 1
        temp = temp.reset_index(drop=True)

        baseline = temp[
            (temp.year <= temp.year_reclassified - anticipation_years)
            & (temp.year > temp.year_reclassified - anticipation_years - 5)
            & (temp.treatment == 1)
        ]["original_patent_count"].mean()

        try:
            estimate, alpha025, alpha975 = conley_taber_stacked(
                temp[["original_patent_count", "posttreat", "treatment",
                      "factorized", "year", "FE", "class_by_episode", "PRODUCTCODE"]],
                "original_patent_count", "posttreat", "treatment",
                "class_by_episode", "year",
            )
            logging.info(f"  Topic {topic}: est={estimate}, CI=[{alpha025}, {alpha975}]")
            estimates.append(estimate)
            lower_cbs.append(alpha025)
            upper_cbs.append(alpha975)
            baselines.append(baseline)
            topics_list.append(topic)
        except Exception as e:
            # Not local: this topic is dropped from the figure AND the permutation draws
            # for every later topic shift, because the CT call takes the global stream.
            logging.error(
                "  Topic %s FAILED: %s -- the topic is omitted from the figure and the "
                "permutation draws of every LATER topic shift, so the remaining "
                "confidence bands will not match a run in which this topic succeeded.",
                topic, e, exc_info=True)

    est_df = pd.DataFrame({
        "Effect": estimates,
        "lower_cb": lower_cbs,
        "upper_cb": upper_cbs,
        "topic": topics_list,
        "baseline": baselines,
    })
    est_df["SE"] = 0.0
    for i, row in est_df.iterrows():
        if row["Effect"] < 0:
            est_df.loc[i, "SE"] = (row["upper_cb"] - row["Effect"]) / 1.96
        else:
            est_df.loc[i, "SE"] = (row["Effect"] - row["lower_cb"]) / 1.96

    est_df["topic_id"] = est_df["topic"]
    est_df["topic_label"] = est_df["topic_id"].apply(_topic_label)
    est_df["pct_change"] = (est_df["Effect"] / est_df["baseline"]) * 100
    est_df["pct_change_SE"] = (est_df["SE"] / est_df["baseline"]) * 100
    est_df = est_df.sort_values(by="pct_change")

    return est_df


# ============================================================================
# Main
# ============================================================================

def main():
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting product variety analysis (Figure D.5)...")

    # Check for pre-computed panels (from original analysis).
    # These panels embed the original LDA topic assignments and matching,
    # ensuring exact reproducibility of the manuscript figures.
    panel_3_2_path = config.DERIVED_DATA_DIR / "expanded_df_3_2_variety.csv"
    panel_2_1_path = config.DERIVED_DATA_DIR / "expanded_df_2_1_variety.csv"
    use_precomputed = panel_3_2_path.exists() and panel_2_1_path.exists()

    if use_precomputed:
        logging.info("Found pre-computed panels. Loading for exact reproducibility.")
        expanded_3_2 = pd.read_csv(panel_3_2_path)
        expanded_2_1 = pd.read_csv(panel_2_1_path)

        # Load frequency DataFrames for verified topic labels
        freq_3to2_path = config.DERIVED_DATA_DIR / "frequency_df_3to2_variety.csv"
        freq_2to1_path = config.DERIVED_DATA_DIR / "frequency_df_2to1_variety.csv"
        freq_3to2 = pd.read_csv(freq_3to2_path) if freq_3to2_path.exists() else None
        freq_2to1 = pd.read_csv(freq_2to1_path) if freq_2to1_path.exists() else None

        # Load LDA models as fallback for topic labels
        lda_3to2_path = config.DERIVED_DATA_DIR / "lda_3to2.model"
        lda_2to1_path = config.DERIVED_DATA_DIR / "lda_2to1.model"

        # Require at least frequency_df OR LDA models for labels
        have_labels = (freq_3to2 is not None and freq_2to1 is not None)
        have_models = lda_3to2_path.exists() and lda_2to1_path.exists()
        if not have_labels and not have_models:
            logging.info("Neither frequency_df nor LDA models found. Running full pipeline...")
            use_precomputed = False

    if use_precomputed:
        lda_3to2 = models.LdaModel.load(str(lda_3to2_path)) if lda_3to2_path.exists() else None
        lda_2to1 = models.LdaModel.load(str(lda_2to1_path)) if lda_2to1_path.exists() else None

        # Panel A: III -> II
        logging.info("=== Panel A: III -> II (pre-computed) ===")
        est_3to2 = estimate_variety_from_panel(
            expanded_3_2, freq_3to2, lda_3to2,
            anticipation_years=2, label="3to2",
        )
        plot_variety(est_3to2, "3 to 2", config.FIGURES_DIR / "variety_3_2.png")

        # Panel B: II -> I
        logging.info("=== Panel B: II -> I (pre-computed) ===")
        est_2to1 = estimate_variety_from_panel(
            expanded_2_1, freq_2to1, lda_2to1,
            anticipation_years=1, label="2to1",
        )
        plot_variety(est_2to1, "2 to 1", config.FIGURES_DIR / "variety_2_1.png")

        logging.info("Product variety analysis complete (from pre-computed panels).")
        return

    # ---- Full pipeline (no pre-computed panels) ----
    logging.info("No pre-computed panels found. Running full LDA + matching pipeline.")

    # ---- Load patent data ----
    dev_pats = pd.read_csv(config.RAW_DATA_DIR / "new_patent_analysis" / "all_device_patents_w_pc.csv")
    all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])

    # Clean patent IDs and restrict to device patents
    all_pats["patent_id"] = all_pats["id"].astype(str).str.split("-").str[1]
    all_pats["patent_id"] = all_pats["patent_id"].apply(lambda s: re.sub(r"\D", "", s))
    all_pats["patent_id"] = all_pats["patent_id"].astype(str)
    dev_pats["patent_id"] = dev_pats["patent_id"].astype(str)
    all_pats = all_pats[all_pats.patent_id.isin(dev_pats["patent_id"])]
    all_pats = pd.merge(
        all_pats, dev_pats[["patent_id", "patent_title", "patent_abstract"]],
        on="patent_id", how="left",
    )
    logging.info(f"Loaded {len(all_pats)} device patents.")

    # ---- Load matched samples for reclassification year info ----
    df_3_2 = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat_innovation"])
    df_3_2 = df_3_2[df_3_2.treatment == 1].drop_duplicates("PRODUCTCODE")
    df_3_2 = df_3_2[df_3_2.FDA_own_accord == 1]
    df_3_2["year_reclassified_3_2"] = df_3_2["year_reclassified"]

    df_2_1 = pd.read_csv(config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat_innovation"])
    df_2_1 = df_2_1[df_2_1.treatment == 1].drop_duplicates("PRODUCTCODE")
    df_2_1["year_reclassified_2_1"] = df_2_1["year_reclassified"]

    # Merge reclassification years onto patent data
    all_pats = pd.merge(all_pats, df_3_2[["PRODUCTCODE", "year_reclassified_3_2"]], how="left")
    all_pats = pd.merge(all_pats, df_2_1[["PRODUCTCODE", "year_reclassified_2_1"]], how="left")

    # ================================================================
    # Panel A: III -> II
    # ================================================================
    logging.info("=== Panel A: III -> II ===")
    df_filtered_3to2 = all_pats[all_pats["year_reclassified_3_2"].notna()].copy()
    df_filtered_3to2["year_reclassified_3_2"] = df_filtered_3to2["year_reclassified_3_2"].astype(int)
    df_filtered_3to2["year"] = df_filtered_3to2["year"].astype(int)

    df_filtered_3to2, lda_3to2, dict_3to2, bi_3to2, tri_3to2, freq_3to2, sig_3to2 = run_lda_pipeline(
        df_filtered_3to2, "combined_text", "year", "year_reclassified_3_2", "3to2",
    )

    # Non-treated patents (neither 3->2 nor 2->1)
    df_non = all_pats[
        all_pats["year_reclassified_3_2"].isna() & all_pats["year_reclassified_2_1"].isna()
    ].copy()
    df_non["year"] = df_non["year"].astype(int)

    est_3to2 = estimate_variety(
        df_filtered_3to2, df_non,
        lda_3to2, dict_3to2, bi_3to2, tri_3to2,
        sig_3to2, freq_3to2,
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["3_2_onepat_innovation"],
        "year_reclassified_3_2", "3to2",
        anticipation_years=2, filter_fda_own_accord=True,
    )
    plot_variety(est_3to2, "3 to 2", config.FIGURES_DIR / "variety_3_2.png")

    # ================================================================
    # Panel B: II -> I
    # ================================================================
    logging.info("=== Panel B: II -> I ===")
    df_filtered_2to1 = all_pats[all_pats["year_reclassified_2_1"].notna()].copy()
    df_filtered_2to1["year_reclassified_2_1"] = df_filtered_2to1["year_reclassified_2_1"].astype(int)
    df_filtered_2to1["year"] = df_filtered_2to1["year"].astype(int)

    df_filtered_2to1, lda_2to1, dict_2to1, bi_2to1, tri_2to1, freq_2to1, sig_2to1 = run_lda_pipeline(
        df_filtered_2to1, "combined_text", "year", "year_reclassified_2_1", "2to1",
    )

    est_2to1 = estimate_variety(
        df_filtered_2to1, df_non,
        lda_2to1, dict_2to1, bi_2to1, tri_2to1,
        sig_2to1, freq_2to1,
        config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES["2_1_onepat_innovation"],
        "year_reclassified_2_1", "2to1",
        anticipation_years=1, filter_fda_own_accord=False,
    )
    plot_variety(est_2to1, "2 to 1", config.FIGURES_DIR / "variety_2_1.png")

    logging.info("Product variety analysis complete.")


if __name__ == "__main__":
    sys.exit(main())
