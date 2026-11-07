"""
15b_event_study_HD_coefficients.py
==================================
RESTRICTED-MODE — recovers the per-event-time coefficients and treated-group
level trajectories for the disaggregated 2->1 adverse-event outcomes that the
Results section cites in-text but that the main pipeline does not produce as
standalone figures.

Context: the headline 2->1 adverse-event EVENT-STUDY figure is on `v_serious`
(the composite serious-event rate). The in-text magnitudes
  "approximately 77% reduction in annual hospitalizations and a suggestive
   40-70% decline in deaths" (Results)
are about the DISAGGREGATED Hospitalization (H) and Mortality (D) outcomes.
This script applies the SAME event-study estimator (estimate_event_study_2to1)
to H and D (and v_serious, for cross-check) and writes the per-ET effects plus
treated/control level means to:

    output/tables/event_study_coefficients/ES_coefs_2_1_{v_serious,H,D}.csv

`15_intext_derived_numbers.py` then computes the % reductions from these files.

Counterfactual definition (important): in this stacked design the control group
is pooled (never-treated; all observations sit at ET==0), so there is NO
control-group event-time SLOPE to project. The reproducible counterfactual is
therefore the MODEL-IMPLIED counterfactual level at horizon h:

    counterfactual_level(h) = treated_mean(h) - Effect(h)
    pct_reduction(h)        = |Effect(h)| / counterfactual_level(h)

The recovered percentages depend on the horizon window; `15_intext_derived_numbers.py`
computes the reported values from these CSVs (manuscript: approximately 77% for
hospitalizations, 40-70% for deaths).

This script does NOT produce any manuscript figure and does NOT modify existing
outputs. Its CSVs are restricted-derived (require matched_sample_2_1_onepat.csv)
and are excluded from the public package.

Run (restricted env only):
    RUN_ES_HD=1 python3 code/15b_event_study_HD_coefficients.py
"""

from __future__ import annotations

import os
import sys
import importlib
from pathlib import Path

import numpy as np
import pandas as pd


if __name__ == "__main__" and os.environ.get("RUN_ES_HD") != "1":
    sys.exit(
        "15b_event_study_HD_coefficients.py is restricted-mode (needs "
        "matched_sample_2_1_onepat.csv + R/rpy2). Set RUN_ES_HD=1 to run. It "
        "writes output/tables/event_study_coefficients/ES_coefs_2_1_*.csv used "
        "by 15_intext_derived_numbers.py for the in-text safety % reductions."
    )

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "code"))
import config  # noqa: E402

np.random.seed(config.RANDOM_SEED)

es = importlib.import_module("04_event_studies")

# 2->1 adverse-event event-study spec template (matches FIGURE_SPECS entry).
BASE = {
    "panel": "Adverse_Events",
    "reclass_type": "2_1",
    "window_low": 4,
    "window_high": 15,
    "matched_file": "2_1_onepat",
}
OUTCOMES = [
    ("v_serious", "Serious Event Rate"),
    ("H", "Hospitalization Rate"),
    ("D", "Mortality Rate"),
]


def recover_one(outcome, label, out_dir):
    spec = dict(BASE, outcome=outcome, label=label)
    df = es.load_matched_sample(spec)
    df = df[df.year > config.ADVERSE_EVENT_MIN_YEAR].reset_index(drop=True)
    df = es.prepare_class_by_episode(df)
    df = es.prepare_event_time(df, spec)
    if outcome not in df.columns:
        # A missing outcome is a FAILURE, not a benign skip: main() records it as a failed outcome
        # and (in strict mode) exits nonzero, so the downstream in-text % reductions cannot be
        # silently left incomplete.
        raise RuntimeError(f"outcome '{outcome}' not present in matched sample columns")
    estimates_df = es.estimate_event_study_2to1(df, spec)
    g = df.groupby(["treatment", "ET"])[outcome].agg(["mean", "count"]).reset_index()
    t = (g[g.treatment == 1].rename(columns={"mean": "treated_mean", "count": "n_treated"})
         [["ET", "treated_mean", "n_treated"]])
    c = (g[g.treatment == 0].rename(columns={"mean": "control_mean", "count": "n_control"})
         [["ET", "control_mean", "n_control"]])
    merged = estimates_df.merge(t, on="ET", how="left").merge(c, on="ET", how="left")
    out_path = out_dir / f"ES_coefs_2_1_{outcome}.csv"
    merged.to_csv(out_path, index=False)
    print(f"  wrote {out_path.name} ({len(merged)} event-times)")


def main():
    es.source_r_scripts()
    out_dir = config.TABLES_DIR / "event_study_coefficients"
    out_dir.mkdir(parents=True, exist_ok=True)
    failed = []
    for outcome, label in OUTCOMES:
        try:
            recover_one(outcome, label, out_dir)
        except Exception as e:
            print(f"  [{outcome}] FAILED: {e}")
            failed.append(outcome)
    print("Done. Run 15_intext_derived_numbers.py to compute the % reductions.")
    # FAIL-CLOSED (certification): a swallowed per-outcome failure leaves the downstream in-text
    # % reductions incomplete. In strict mode, any failed outcome makes this step exit nonzero.
    if failed:
        print(f"WARNING: {len(failed)} outcome(s) failed: {failed}")
        if os.environ.get("FDA_STRICT_INTEXT") == "1":
            print(f"STRICT: FAILED — {len(failed)} event-study outcome(s) did not regenerate.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
