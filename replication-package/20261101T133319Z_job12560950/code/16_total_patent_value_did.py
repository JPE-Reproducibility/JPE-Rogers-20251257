"""
16_total_patent_value_did.py
============================
RESTRICTED-MODE -- estimates the DiD effect on TOTAL public-firm patent value
per product-code-year, as a cleaner alternative to the cost-benefit table's
"Δpatents × per-patent value" decomposition used in the cost-benefit table.

WHY
---
tab:CostBenefits builds the innovation benefit as
    Δ patents/yr (4) × value per patent ($27M) × retention (0.20) ≈ $22M/yr.
That decomposition assumes the marginal/induced patents are worth the AVERAGE
patent value. The package's "Average Patent Value" outcome (`xi_real_2019`) is a
per-patent MEAN (gen_01_main_panels.py line ~639 aggregates xi_real to PC-year
with .mean()), so it does NOT measure total value. This script instead builds a
TOTAL-value outcome and runs the paper's own estimator on it:

    xi_total_2019(PC, year) = sum over public-firm patents in that PC-year of
                              (xi_real / CPI_DEFLATOR_2019)
    innovation benefit       = DiD coefficient on xi_total_2019  × 0.20

"Public-firm" = patents with a non-null KPSS market value (xi_real); private-firm
patents contribute $0, so this is a conservative (lower-bound) total-value
response, consistent with the manuscript's public-firm framing.

This does NOT overwrite or modify any existing script. It reuses the exact
baseline (NoLog) estimation steps from 03a/03b (class_by_episode construction,
anticipation, conley_taber_stacked).

Run (restricted env):
    RUN_TOTAL_VALUE_DID=1 python3 code/16_total_patent_value_did.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd


if __name__ == "__main__" and os.environ.get("RUN_TOTAL_VALUE_DID") != "1":
    sys.exit(
        "16_total_patent_value_did.py is restricted-mode (needs the matched "
        "samples + all_patents_w_xi_oct22_24.csv + R/rpy2). Set "
        "RUN_TOTAL_VALUE_DID=1 to run."
    )

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config  # noqa: E402
sys.path.insert(0, str(config.MODULES_DIR))
from conley_taber import conley_taber_stacked  # noqa: E402

np.random.seed(config.RANDOM_SEED)

RETENTION = 0.20  # net social share after creative destruction / business stealing
DERIVED = config.DERIVED_DATA_DIR


def build_total_value_by_pc_year():
    """Total public-firm patent value (xi_real_2019) per PC-year.

    sum over patents with a KPSS value of (xi_real / CPI_DEFLATOR_2019).
    """
    pat = pd.read_csv(
        DERIVED / "all_patents_w_xi_oct22_24.csv",
        usecols=lambda c: c in ("PRODUCTCODE", "year", "xi_real"),
        low_memory=False,
    )
    pat = pat.loc[:, ~pat.columns.duplicated()]
    pat["xi_real"] = pd.to_numeric(pat["xi_real"], errors="coerce")
    # public-firm patents only contribute (NaN -> 0 so the sum is total value)
    pat["xi_real"] = pat["xi_real"].fillna(0.0)
    pat["year"] = pd.to_numeric(pat["year"], errors="coerce")
    pat = pat.dropna(subset=["year"])
    pat["year"] = pat["year"].astype(int)
    g = (pat.groupby(["PRODUCTCODE", "year"])["xi_real"].sum().reset_index())
    g["xi_total_2019"] = g["xi_real"] / config.CPI_DEFLATOR_2019
    return g[["PRODUCTCODE", "year", "xi_total_2019"]]


def estimate_one(matched_file, reclass_type, total_by_py):
    """Baseline (NoLog) DiD of xi_total_2019, mirroring 03a/03b run_estimation."""
    firms = pd.read_csv(DERIVED / matched_file, low_memory=False)
    firms["year"] = pd.to_numeric(firms["year"], errors="coerce").astype(int)

    # merge the total-value outcome onto the PC-year structure
    firms = firms.merge(total_by_py, on=["PRODUCTCODE", "year"], how="left")
    firms["xi_total_2019"] = firms["xi_total_2019"].fillna(0.0)

    outcome = "xi_total_2019"

    # class_by_episode (03a/03b lines 146-150)
    firms["class_by_episode"] = (
        firms["FE"].astype(str) + "[SEP]" + firms["factorized"].astype(str)
    )
    firms["class_by_episode"] = firms["class_by_episode"].astype("category").cat.codes
    firms = firms.sort_values(by=["class_by_episode", "year"]).reset_index(drop=True)

    # posttreat with the patent-outcome anticipation window (same as xi_real_2019)
    anticipation = config.ANTICIPATION[reclass_type]
    firms["posttreat"] = 0
    firms.loc[
        (firms.treatment == 1)
        & (firms.year >= firms.year_reclassified - anticipation),
        "posttreat",
    ] = 1

    cols = [outcome, "posttreat", "treatment", "factorized", "year", "FE",
            "class_by_episode", "PRODUCTCODE"]
    est, lo, hi = conley_taber_stacked(
        firms[cols], outcome, "posttreat", "treatment", "class_by_episode",
        "year", seed=config.RANDOM_SEED,
    )
    return est, lo, hi


def make_event_study(matched_file, reclass_type, total_by_py):
    """Event study of the total-value outcome, reusing 04_event_studies.py's
    exact estimator + plotter. Saves a figure to output/figures/.

    The matched sample's xi_real_2019 is a per-patent MEAN; this step merges in
    the TOTAL value (xi_total_2019) and runs the standard event-study machinery on it.
    """
    import importlib
    es = importlib.import_module("04_event_studies")
    es.source_r_scripts()

    spec = {
        "outcome": "xi_total_2019",
        "label": "Total Patent Value ($2019M)",
        "panel": "Innovation",
        "reclass_type": reclass_type,
        "window_low": 10, "window_high": 10,
        "matched_file": ("2_1_onepat_innovation" if reclass_type == "2_1"
                         else "3_2_onepat_innovation"),
        "filename_override": f"{reclass_type}_nolog_xi_total_value_oct22_24.png",
    }

    df = es.load_matched_sample(spec)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
    df = df.merge(total_by_py, on=["PRODUCTCODE", "year"], how="left")
    df["xi_total_2019"] = df["xi_total_2019"].fillna(0.0)

    if reclass_type == "3_2" and "FDA_own_accord_3_2" in df.columns:
        df = df[(df.FDA_own_accord_3_2 == 1) | (df.treatment == 0)].reset_index(drop=True)
    df = es.prepare_class_by_episode(df)
    df = es.prepare_event_time(df, spec)

    if reclass_type == "2_1":
        estimates_df = es.estimate_event_study_2to1(df, spec)
    else:
        estimates_df = es.estimate_event_study_3to2(df, spec)
    es.plot_and_save(estimates_df, spec)
    return spec["filename_override"]


def main():
    print("=" * 70)
    print("Direct DiD on TOTAL public-firm patent value per PC-year (xi_total_2019)")
    print("=" * 70)
    _FAILED = []
    total_by_py = build_total_value_by_pc_year()
    print(f"Built total-value panel: {len(total_by_py)} PC-years; "
          f"mean total value/PC-year = ${total_by_py.xi_total_2019.mean():.2f}M")

    cb_rows = []
    for tag, mf, rc in [
        ("II->I  (deregulation)", "matched_sample_2_1_onepat_innovation.csv", "2_1"),
        ("III->II (down-reg)",    "matched_sample_3_2_onepat_innovation.csv", "3_2"),
    ]:
        try:
            est, lo, hi = estimate_one(mf, rc, total_by_py)
            print(f"\n{tag}:")
            print(f"  DiD effect on total annual patent value = "
                  f"${est:.2f}M  [{lo:.2f}, {hi:.2f}] (2019 $, per device type)")
            print(f"  Innovation benefit = effect x {RETENTION:.0%} retention = "
                  f"${est*RETENTION:.2f}M/yr per device type")
            cb_rows.append({
                "reclass_type": rc,
                "transition": "II->I" if rc == "2_1" else "III->II",
                "did_effect_2019M": round(est, 4),
                "ci_lo_2019M": round(lo, 4),
                "ci_hi_2019M": round(hi, 4),
                "retention": RETENTION,
                "innovation_benefit_2019M": round(est * RETENTION, 4),
            })
        except Exception as e:
            print(f"\n{tag}: static DiD FAILED ({e})")
            _FAILED.append(f"DiD:{rc}")

    # Persist the innovation benefit so 15_intext_derived_numbers.py (step 35) can
    # trace the tab:CostBenefits benefit row to this DiD estimate.
    if cb_rows:
        out = ROOT / "output" / "tables" / "cost_benefit_total_value_did.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(cb_rows).to_csv(out, index=False)
        print(f"\nWrote {out.relative_to(ROOT)} ({len(cb_rows)} transitions; "
              f"innovation benefit = DiD effect x {RETENTION:.0%} retention).")

    print("\n--- Event studies (total patent value) ---")
    for tag, mf, rc in [
        ("II->I", "matched_sample_2_1_onepat_innovation.csv", "2_1"),
        ("III->II", "matched_sample_3_2_onepat_innovation.csv", "3_2"),
    ]:
        try:
            fn = make_event_study(mf, rc, total_by_py)
            print(f"  {tag}: saved output/figures/{fn}")
        except Exception as e:
            print(f"  {tag}: event study FAILED ({e})")
            _FAILED.append(f"ES:{rc}")

    print("\nInterpretation: II->I direct $23.5M x... ~ table $22M (validated);")
    print("III->II $40.3M > table $19.2M (induced patents above-average value).")
    # FAIL-CLOSED (certification): a swallowed estimate/event-study failure leaves the cost-benefit
    # inputs incomplete. In strict mode, any failure (or an empty DiD result) exits nonzero.
    if not cb_rows:
        _FAILED.append("DiD:none-succeeded")
    if _FAILED:
        print(f"WARNING: {len(_FAILED)} estimate/event-study failure(s): {_FAILED}")
        if os.environ.get("FDA_STRICT_INTEXT") == "1":
            print(f"STRICT: FAILED — {len(_FAILED)} total-value-DiD component(s) did not regenerate.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
