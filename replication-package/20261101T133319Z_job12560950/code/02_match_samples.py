#!/usr/bin/env python
"""
02_match_samples.py — Produce all matched sample CSVs.

Runs Mahalanobis matching for each (event, match-type) combination.
Uncomments the matching calls that were commented out in Replication_analysis.py
lines 930-994.

Inputs: data/derived/Full_sample.csv
Outputs: data/derived/matched_sample_*.csv (7 files)
"""

import sys
import logging
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.MODULES_DIR))
import match_mahal

import numpy as np
np.random.seed(config.RANDOM_SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "02_match_samples.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# ============================================================================
# Matching specifications
# ============================================================================
MATCH_SPECS = [
    {
        "name": "matched_sample_2_1_onepat",
        "event": "2_1", "topn": 2,
        "adverse": False, "innovation": False, "universe": False,
        "quality": False, "petitioned": False,
    },
    {
        "name": "matched_sample_2_1_onepat_innovation",
        "event": "2_1", "topn": 2,
        "adverse": False, "innovation": True, "universe": False,
        "quality": False, "petitioned": False,
    },
    {
        # 2->1 quality variant (mirror of the 3_2 quality spec). Previously OMITTED from
        # MATCH_SPECS, so this file (used by 14_breakthrough for both reclass types) was a
        # shipped static intermediate the pipeline could not regenerate. Regeneration here
        # reproduces the shipped file cell-for-cell (verified: 17,160 rows x 121 cols, 0
        # differing cells; column order aside), so estimates are unchanged and the docstring's
        # "7 files" is now correct.
        "name": "matched_sample_2_1_onepat_innovation_quality",
        "event": "2_1", "topn": 2,
        "adverse": False, "innovation": False, "universe": False,
        "quality": True, "petitioned": False,
    },
    {
        "name": "matched_sample_3_2_onepat",
        "event": "3_2", "topn": 2,
        "adverse": False, "innovation": False, "universe": False,
        "quality": False, "petitioned": False,
    },
    {
        "name": "matched_sample_3_2_onepat_innovation",
        "event": "3_2", "topn": 2,
        "adverse": False, "innovation": True, "universe": False,
        "quality": False, "petitioned": False,
    },
    {
        "name": "matched_sample_3_2_onepat_innovation_quality",
        "event": "3_2", "topn": 2,
        "adverse": False, "innovation": False, "universe": False,
        "quality": True, "petitioned": False,
    },
    {
        "name": "matched_sample_3_2_onepat_innovation_petitioned",
        "event": "3_2", "topn": 2,
        "adverse": False, "innovation": True, "universe": False,
        "quality": False, "petitioned": True,
    },
]


def main():
    config.DERIVED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for spec in MATCH_SPECS:
        name = spec["name"]
        logging.info("=" * 60)
        logging.info(f"Starting: {name}")
        t0 = time.time()

        firms = match_mahal.get_match_mahalanobis(
            event=spec["event"],
            topn=spec["topn"],
            adverse=spec["adverse"],
            innovation=spec["innovation"],
            universe=spec["universe"],
            quality=spec["quality"],
            petitioned=spec["petitioned"],
        )

        outpath = config.DERIVED_DATA_DIR / f"{name}.csv"
        firms.to_csv(outpath, index=False)

        n_treated = firms[firms.treatment == 1]["PRODUCTCODE"].nunique()
        n_control = firms[firms.treatment == 0]["PRODUCTCODE"].nunique()
        n_total = len(firms.drop_duplicates(["PRODUCTCODE", "year"]))

        elapsed = time.time() - t0
        logging.info(
            f"  Saved: {outpath} | Treated PCs: {n_treated}, Control PCs: {n_control}, "
            f"Total PC-years: {n_total} | Time: {elapsed:.1f}s"
        )

    logging.info("All matching complete.")


if __name__ == "__main__":
    sys.exit(main())
