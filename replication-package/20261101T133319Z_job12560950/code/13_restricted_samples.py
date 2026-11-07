#!/usr/bin/env python
"""
13_restricted_samples.py -- Table D.15: Restricted-sample robustness checks.

Two restricted-sample variants of the main innovation DiD:
  (1) GPT-4o Identified Devices: re-matches using only device patents
      identified via GPT-4o classification, then runs Conley-Taber on
      the device-patent count outcome.
  (2) Health Patents (No Drugs): uses the standard matched innovation sample
      but restricts the outcome to patents_pats_nodrugs (health patents
      excluding pharmaceutical A61 patents).

Both are run as OLS (linear) with Conley-Taber permutation inference,
for each reclassification direction (III->II, II->I).

Source: Replication_analysis.py lines 3630-3845.

Inputs:
    data/derived/matched_sample_{reclass}_onepat_innovation.csv
    data/derived/Full_sample.csv  (via match_mahal for GPT-4o re-matching)
    data/raw/new_patent_analysis/all_device_patents_w_pc.csv
    data/derived/all_patents_w_xi_oct22_24.csv

Outputs:
    output/tables/RestrictedSamples_estimates.csv
    output/tables/Formatted/TableD15_RestrictedSamples.tex
"""

import sys
import logging
import time
from pathlib import Path

import pandas as pd
import numpy as np
import scipy.stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked
from estimation import source_r_scripts
from match_mahal import get_match_mahalanobis_cond
from table_format import compute_se, significance_stars

np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "13_restricted_samples.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


# ============================================================================
# Outcome definitions
# ============================================================================

# outcome_key -> (formal_name, restriction_label, requires_is_dev_matching)
OUTCOMES = {
    "real_pats_dev_gpt4o": ("Patenting Rate", "GPT-4o Identified Devices", True),
    "patents_pats_nodrugs": ("Patenting Rate", "Health Patents (No Drugs)", False),
}


# ============================================================================
# Helper: prepare matched sample for GPT-4o device restriction
# ============================================================================

def load_gpt4o_sample(reclass_type):
    """
    Run conditional Mahalanobis matching with condition='is_dev'.

    Returns a DataFrame with 'real_pats_dev_gpt4o' as the device-patent
    outcome (renamed from 'patents_devpats_gpt4o').
    """
    logging.info(f"  Running GPT-4o device matching for {reclass_type}...")
    firms = get_match_mahalanobis_cond(
        event=reclass_type,
        topn=2,
        adverse=False,
        innovation=True,
        condition="is_dev",
        quality=False,
        petitioned=False,
    )
    firms = firms.drop_duplicates(["PRODUCTCODE", "year"])

    # Create the outcome alias (match_mahal creates patents_devpats_gpt4o)
    if "patents_devpats_gpt4o" in firms.columns:
        firms["real_pats_dev_gpt4o"] = firms["patents_devpats_gpt4o"]
    else:
        logging.warning("  Column 'patents_devpats_gpt4o' not found after matching.")
        firms["real_pats_dev_gpt4o"] = 0

    logging.info(
        f"  GPT-4o sample: {len(firms)} obs, "
        f"{firms['PRODUCTCODE'].nunique()} PCs"
    )
    return firms


def load_nodrugs_sample(reclass_type):
    """
    Load the standard matched innovation sample for no-drugs outcome.

    The outcome 'patents_pats_nodrugs' already exists in the matched CSV.
    """
    sample_key = f"{reclass_type}_onepat_innovation"
    path = config.DERIVED_DATA_DIR / config.MATCHED_SAMPLES[sample_key]
    logging.info(f"  Loading standard matched sample from {path}")
    firms = pd.read_csv(path)
    firms = firms.drop_duplicates(["PRODUCTCODE", "year"])
    logging.info(
        f"  No-drugs sample: {len(firms)} obs, "
        f"{firms['PRODUCTCODE'].nunique()} PCs"
    )
    return firms


# ============================================================================
# Core estimation
# ============================================================================

def run_single_estimation(firms, outcome, reclass_type):
    """
    Run Conley-Taber stacked DiD (OLS) for a single outcome.

    Sets up class_by_episode, posttreat with anticipation, then estimates.

    Returns (estimate, lower_CI, upper_CI, N, baseline_mean, baseline_sd).
    """
    firms_temp = firms.copy().reset_index(drop=True)

    if firms_temp["PRODUCTCODE"].nunique() < 5:
        logging.warning(f"  {outcome}: fewer than 5 PCs, skipping")
        return None

    # class_by_episode fixed effect
    firms_temp["class_by_episode"] = (
        firms_temp["FE"].astype(str) + "[SEP]" + firms_temp["factorized"].astype(str)
    )
    firms_temp["class_by_episode"] = (
        firms_temp["class_by_episode"].astype("category").cat.codes
    )
    firms_temp = firms_temp.sort_values(
        by=["class_by_episode", "year"]
    ).reset_index(drop=True)

    # Posttreat with anticipation (innovation outcomes)
    anticipation = config.ANTICIPATION[reclass_type]
    firms_temp["posttreat"] = 0
    firms_temp.loc[
        (firms_temp.treatment == 1)
        & (firms_temp.year >= firms_temp.year_reclassified - anticipation),
        "posttreat",
    ] = 1
    firms_temp = firms_temp.reset_index(drop=True)

    # Estimation: linear OLS with Conley-Taber
    cols = [
        outcome, "posttreat", "treatment", "factorized",
        "year", "FE", "class_by_episode", "PRODUCTCODE",
    ]
    try:
        estimate, alpha025, alpha975 = conley_taber_stacked(
            firms_temp[cols],
            outcome, "posttreat", "treatment", "class_by_episode", "year",
            seed=config.RANDOM_SEED,
        )
    except Exception as e:
        logging.warning(f"  {outcome}: estimation failed ({e})")
        return None

    N = len(firms_temp.drop_duplicates(["PRODUCTCODE", "year"]))

    # Pre-treatment baseline mean (event_time in [-5, -1])
    firms_temp["event_time"] = firms_temp["year"] - firms_temp["year_reclassified"]
    pre_mask = (
        (firms_temp.treatment == 1)
        & (firms_temp.event_time < 0)
        & (firms_temp.event_time > -6)
    )
    baseline_mean = firms_temp.loc[pre_mask, outcome].mean()
    baseline_sd = firms_temp.loc[pre_mask, outcome].std()

    # Fallback for zero baseline
    if baseline_mean == 0:
        pre_mask2 = (
            (firms_temp.treatment == 1)
            & (firms_temp.event_time < 0)
            & (firms_temp.event_time > -10)
        )
        baseline_mean = firms_temp.loc[pre_mask2, outcome].mean()
    if baseline_mean == 0:
        pre_mask3 = (firms_temp.treatment == 1) & (firms_temp.event_time < 0)
        baseline_mean = firms_temp.loc[pre_mask3, outcome].mean()

    logging.info(
        f"  {outcome} [{reclass_type}]: est={estimate}, "
        f"CI=[{alpha025}, {alpha975}], N={N}, "
        f"pre-mean={baseline_mean:.2f}"
    )

    return {
        "estimate": estimate,
        "lower_CI": alpha025,
        "upper_CI": alpha975,
        "N": N,
        "baseline_mean": baseline_mean,
        "baseline_sd": baseline_sd,
    }


# ============================================================================
# LaTeX formatting
# ============================================================================

def format_latex_table(df_results):
    """
    Format Table D.15 as a LaTeX row-fragment .tex file.

    Structure: two panels (a) Class III to II, (b) Class II to I.
    Each panel has two rows: GPT-4o Devices, Health No Drugs.
    Columns: Outcome | Pre-mean | Estimate (SE).
    """
    lines = []

    panel_labels = {
        "3_2": "A. Class III to II",
        "2_1": "B. Class II to I",
    }

    first_panel = True
    for reclass_type in ["3_2", "2_1"]:
        panel = df_results[df_results.reclass_type == reclass_type]
        if not first_panel:
            lines.append("\\hline")
        lines.append("& & \\\\")
        lines.append(
            f"\\textbf{{{panel_labels[reclass_type]}}} & & \\\\"
        )
        lines.append("& & \\\\")

        for _, row in panel.iterrows():
            est = row["Estimate"]
            se = row["SE"]
            stars = significance_stars(est, se)
            pre_mean = row["baseline"]
            pre_sd = row["baseline_sd"]

            if stars:
                est_str = f"{est:.2f}\\textsuperscript{{{stars}}}"
            else:
                est_str = f"{est:.2f}"
            pre_str = f"{pre_mean:.2f}"
            label = row["restriction_label"]

            lines.append(f"\\hspace{{6mm}}{label} & {pre_str} & {est_str} \\\\")
            lines.append(f" & ({pre_sd:.2f}) & ({se:.2f}) \\\\")

        first_panel = False

    return "\n".join(lines) + "\n"


# ============================================================================
# Additive emitter: patent-collection universe counts (JPE patent-collection
# robustness appendix)
# ============================================================================
# The appendix ("Restricted samples and robustness") states three universe
# counts that no other package output reports:
#   - 875,324 : patents linked to FDA device types by the keyword method, 1996-2015
#   - 171,682 : keyword patents with an A61 CPC code and no A61P (drug) code, 1996-2015
#   - 302,140 : utility patents flagged as devices by GPT-4o, 1996-2015
# The helpers below recompute each count from the frozen inputs already present
# and write them to a NEW CSV. They are READ-ONLY: they never alter any existing
# output value, coefficient, or file, and are fully guarded so a missing
# restricted input is recorded as NaN rather than raising into the pipeline.

def _count_keyword_universe_window(path, lo, hi):
    """Unique keyword-linked patents (all_patents_w_xi 'id') dated [lo, hi]."""
    ids = set()
    for ch in pd.read_csv(path, usecols=["id", "year"], chunksize=200000,
                          low_memory=False):
        y = pd.to_numeric(ch["year"], errors="coerce")
        sub = ch[(y >= lo) & (y <= hi)]
        ids.update(sub["id"].astype(str))
    return len(ids)


def _count_keyword_universe(path):
    """Unique keyword-linked patents (all_patents_w_xi 'id') dated 1996-2015."""
    return _count_keyword_universe_window(path, 1996, 2015)


def _count_keyword_universe_1976_2019(path):
    """Unique keyword-linked patents dated 1976-2019 -- the full patent-collection
    window stated in the data section ("over 1.2 million medical device patents
    from 1976-2019"), as distinct from the 1996-2015 estimation window."""
    return _count_keyword_universe_window(path, 1976, 2019)


def _count_a61_nodrug(path):
    """Unique keyword patents with >=1 A61 CPC code and no A61P code, 1996-2015."""
    import ast
    import re as _re
    ids = set()
    for ch in pd.read_csv(path, usecols=["id", "year", "cpc"], chunksize=100000,
                          low_memory=False):
        y = pd.to_numeric(ch["year"], errors="coerce")
        inwin = (y >= 1996) & (y <= 2015)
        for idv, cpc, w in zip(ch["id"].astype(str), ch["cpc"], inwin):
            if not w or pd.isna(cpc):
                continue
            s = str(cpc)
            try:
                codes = ast.literal_eval(s)
                if isinstance(codes, str):
                    codes = [codes]
                codes = [str(c) for c in codes]
            except Exception:
                codes = _re.findall(r"[A-H]\d{2}[A-Z]?[0-9/]*", s)
            a61 = [c for c in codes if c.startswith("A61")]
            if not a61:
                continue
            # keep if it has a non-drug A61 code AND carries no A61P (drug) code
            if any(not c.startswith("A61P") for c in a61) and \
               not any(c.startswith("A61P") for c in codes):
                ids.add(idv)
    return len(ids)


def _count_gpt4o_devices(path):
    """Unique GPT-4o-flagged utility device patents dated 1996-2015."""
    ids = set()
    for ch in pd.read_csv(
        path, usecols=["patent_id", "year", "is_device", "patent_type"],
        chunksize=200000, low_memory=False,
    ):
        y = pd.to_numeric(ch["year"], errors="coerce")
        sub = ch[(ch["is_device"] == 1) & (ch["patent_type"] == "utility")
                 & (y >= 1996) & (y <= 2015)]
        ids.update(sub["patent_id"].astype(str))
    return len(ids)


def emit_patent_collection_counts():
    """
    Additive emitter (read-only): recompute the three patent-collection universe
    counts stated in the JPE patent-collection robustness appendix and write them
    to a NEW CSV (output/tables/PatentCollectionCounts.csv). Guarded so a missing
    restricted input is recorded as NaN rather than raising.
    """
    keyword_path = config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"]
    cpc_path = config.RAW_DATA_DIR / "all_pats_wtitlesCPC.csv"
    gpt_path = (config.RAW_DATA_DIR / "new_patent_analysis"
                / "all_device_patents_w_pc.csv")

    specs = [
        ("keyword_linked_patents_1976_2019",
         "Patents linked to FDA device types by the keyword method, 1976-2019 "
         "(unique 'id'); the full patent-collection window stated in the data "
         "section",
         keyword_path, _count_keyword_universe_1976_2019, 1200000, "ge"),
        ("keyword_linked_patents_1996_2015",
         "Patents linked to FDA device types by the keyword method, 1996-2015 "
         "(unique 'id')",
         keyword_path, _count_keyword_universe, 875324, "eq"),
        ("a61_nondrug_patents_1996_2015",
         "Keyword patents with an A61 CPC code and no A61P (drug) code, 1996-2015 "
         "(unique 'id')",
         cpc_path, _count_a61_nodrug, 171682, "eq"),
        ("gpt4o_device_utility_patents_1996_2015",
         "Utility patents flagged as devices by GPT-4o, 1996-2015 "
         "(unique 'patent_id')",
         gpt_path, _count_gpt4o_devices, 302140, "eq"),
    ]

    rows = []
    for metric, desc, path, fn, stated, relation in specs:
        computed = np.nan
        if Path(path).exists():
            try:
                computed = fn(path)
                logging.info(f"  [patent-counts] {metric}: computed={computed} "
                             f"(manuscript={stated})")
            except Exception as e:  # never break the pipeline
                logging.warning(f"  [patent-counts] {metric}: failed ({e})")
        else:
            logging.warning(f"  [patent-counts] {metric}: input missing ({path}); "
                            f"recording NaN")
        # The manuscript states three of these counts exactly and one of them as a
        # lower bound ("over 1.2 million"), so the check follows the statement.
        if pd.isna(computed):
            reproduces = False
        elif relation == "ge":
            reproduces = int(computed) >= stated
        else:
            reproduces = int(computed) == stated
        rows.append({
            "metric": metric,
            "description": desc,
            "source_file": Path(path).name,
            "computed_count": computed,
            "manuscript_value": stated,
            "manuscript_relation": relation,
            "reproduces": reproduces,
        })

    out_path = config.TABLES_DIR / "PatentCollectionCounts.csv"
    pd.DataFrame(rows).to_csv(out_path, index=False)
    logging.info(f"Saved patent-collection counts: {out_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    t0 = time.time()
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    (config.TABLES_DIR / "Formatted").mkdir(parents=True, exist_ok=True)

    source_r_scripts()

    logging.info("=" * 60)
    logging.info("13_restricted_samples.py — Table D.15")
    logging.info("=" * 60)

    # Collect results
    results = []

    for reclass_type in ["3_2", "2_1"]:
        logging.info(f"\n--- Reclassification: {reclass_type} ---")

        for outcome_key, (formal_name, restriction_label, is_dev) in OUTCOMES.items():

            # Load the appropriate sample
            if is_dev:
                firms = load_gpt4o_sample(reclass_type)
            else:
                firms = load_nodrugs_sample(reclass_type)

            # Run estimation
            result = run_single_estimation(firms, outcome_key, reclass_type)

            if result is not None:
                se = compute_se(
                    result["estimate"], result["lower_CI"], result["upper_CI"]
                )
                results.append({
                    "outcome": outcome_key,
                    "formal_name": formal_name,
                    "restriction_label": restriction_label,
                    "reclass_type": reclass_type,
                    "Estimate": result["estimate"],
                    "lower_CI": result["lower_CI"],
                    "upper_CI": result["upper_CI"],
                    "SE": se,
                    "baseline": result["baseline_mean"],
                    "baseline_sd": result["baseline_sd"],
                    "Sample Size": result["N"],
                    "Model": "linear",
                })

    # Build results DataFrame
    df_results = pd.DataFrame(results)

    # Compute t-stats and stars
    df_results["tstat"] = np.abs(df_results["Estimate"] / df_results["SE"])
    ninety = scipy.stats.norm.ppf(0.95)
    ninety5 = scipy.stats.norm.ppf(0.975)
    ninety9 = scipy.stats.norm.ppf(0.995)
    ninety9point9 = scipy.stats.norm.ppf(0.9995)
    df_results["stars"] = ""
    df_results.loc[df_results["tstat"] > ninety, "stars"] = "+"
    df_results.loc[df_results["tstat"] > ninety5, "stars"] = "*"
    df_results.loc[df_results["tstat"] > ninety9, "stars"] = "**"
    df_results.loc[df_results["tstat"] > ninety9point9, "stars"] = "***"

    # Log summary
    logging.info("\n" + "=" * 60)
    logging.info("RESULTS SUMMARY — Table D.15 (Restricted Samples)")
    logging.info("=" * 60)
    for _, row in df_results.iterrows():
        logging.info(
            f"  {row['reclass_type']} | {row['restriction_label']:20s} | "
            f"pre-mean={row['baseline']:.2f} | "
            f"est={row['Estimate']:.2f}{row['stars']} ({row['SE']:.2f}) | "
            f"N={int(row['Sample Size'])}"
        )

    # Verification against manuscript targets
    logging.info("\n--- Manuscript target comparison ---")
    targets = {
        ("3_2", "GPT-4o Devices"): {"pre_mean": 5.02, "est": 7.80, "se": 2.52},
        ("3_2", "Health No Drugs"): {"pre_mean": 4.55, "est": 11.71, "se": 3.60},
        ("2_1", "GPT-4o Devices"): {"pre_mean": 3.40, "est": 4.46, "se": 1.21},
        ("2_1", "Health No Drugs"): {"pre_mean": 3.88, "est": 0.34, "se": 1.85},
    }
    for _, row in df_results.iterrows():
        key = (row["reclass_type"], row["restriction_label"])
        if key in targets:
            t = targets[key]
            logging.info(
                f"  {key}: target est={t['est']:.2f} SE=({t['se']:.2f}) "
                f"pre-mean={t['pre_mean']:.2f} | "
                f"actual est={row['Estimate']:.2f} SE=({row['SE']:.2f}) "
                f"pre-mean={row['baseline']:.2f}"
            )

    # Save raw estimates CSV
    csv_path = config.TABLES_DIR / "RestrictedSamples_estimates.csv"
    df_results.to_csv(csv_path, index=False)
    logging.info(f"\nSaved estimates CSV: {csv_path}")

    # Save formatted LaTeX
    tex_content = format_latex_table(df_results)
    tex_path = config.TABLES_DIR / "Formatted" / "TableD15_RestrictedSamples.tex"
    with open(tex_path, "w") as f:
        f.write(tex_content)
    logging.info(f"Saved LaTeX fragment: {tex_path}")

    # Additive emitter (read-only, new CSV only): patent-collection universe
    # counts stated in the appendix. Guarded so it can never break the pipeline.
    try:
        emit_patent_collection_counts()
    except Exception as e:
        logging.warning(f"emit_patent_collection_counts skipped: {e}")

    elapsed = time.time() - t0
    logging.info(f"\nTotal runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    sys.exit(main())
