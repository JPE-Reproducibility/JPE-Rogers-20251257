"""
15_intext_derived_numbers.py
============================
Reproduce the DERIVED in-text numbers and the hand-laid-out cost-benefit table
(tab:CostBenefits) from already-generated pipeline outputs, so a reviewer can
trace every figure to code (JPE Policy 2.2).

This script does NOT add any figure or table to the manuscript. It recomputes
the magnitudes that the manuscript prose states but that are derived by
arithmetic from other exhibits:

  #4  ">150%" larger-firms safety innovation (Results, L441)
  #6  cost-benefit: $23.5M innovation + $4.3M safety = ~$28M (Reg Design, L517
      footnote + tab:CostBenefits); and the ~3,100 / ~540 Class II product-code
      counts. The innovation benefit is the total-patent-value DiD estimated by
      16_total_patent_value_did.py (run_all step 34); see derived_cost_benefit().
  #2  "~77% hospitalizations / 40-70% deaths" reduction (Results, L432) --
      computed via the author's counterfactual method (see below). Requires
      event-study per-event-time coefficients; see the NOTE on #2.

Inputs (all are aggregate pipeline OUTPUTS already in output/tables/, plus the
public FDA classification file -- NO restricted microdata is read here):
  - output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv
        (matched-control adverse-event level estimates: H = -1.773, D = -0.426)
  - output/tables/firm_heterogeneity_k_est.csv  (tercile level estimates)
  - output/tables/firm_heterogeneity_k_pct.csv  (tercile ratios; #4 = 1.612)
  - output/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv
  - output/tables/cost_benefit_total_value_did.csv  (written by run_all step 34 =
        16_total_patent_value_did.py: the DATA-DRIVEN total-patent-value DiD whose
        20%-retained value is the cost-benefit innovation benefit, ~$23.5M II->I)
  - data/raw/foiclass.txt  (Class II product-code universe, #6 counts)

Documented external constants (cited in the manuscript / tab:CostBenefits):
  - EPA value of a statistical life (VSL):           $10,000,000
  - Average inpatient hospitalization cost:          $22,000   (Cost of Hospital
                                                                Stay, 2019)
  - Creative-destruction / business-stealing retain: 20% of patent value
                                                      (80% discount; kogan:2017)

Run:
  python3 code/15_intext_derived_numbers.py
"""

from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "output" / "tables"
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"

# --- documented external constants -------------------------------------------
VSL = 10_000_000           # EPA value of a statistical life, USD
HOSP_COST = 22_000         # average inpatient hospitalization, USD (2019)
PATENT_RETENTION = 0.20    # retain 20% of patent value (80% creative-destruction discount)

# The market-age maturity threshold the MANUSCRIPT prints (Section 6: "roughly 60 years",
# "the 60-year maturity threshold"), used for the ~650 / ~29% Class II counts. Settled by
# the author 2026-09-21: the fitted crossing is 61.1 years with a 95% CI of [22, 100], so
# the paper prints a hedged benchmark rather than a two-significant-figure value. It is
# NOT the pipeline's own fitted zero-crossing: derived_exp_crossings() checks the two
# against each other and reports a divergence instead of hiding it inside a tolerance.
MANUSCRIPT_MATURITY_THRESHOLD_YEARS = 60

# Machine-readable in-text-number registry. Each headline magnitude records (name, value, status).
# status "ok" = computed from a present pipeline output; "pending" = its input was missing.
# In STRICT mode (FDA_STRICT_INTEXT=1, set by the certification harness for step 35) any "pending"
# makes this step exit NONZERO -- so "the process succeeded" cannot coexist with in-text
# numbers that were never regenerated.
INTEXT_REPORT = []
_MISSING_INPUTS = []


def record(name, value, status, note=""):
    INTEXT_REPORT.append({"name": name, "value": value, "status": status, "note": note})


def check(name, value, relation, note_prefix=""):
    """Record `name`=`value` with status 'ok' ONLY IF `value` actually satisfies `relation`
    against the manuscript-stated target; otherwise 'outside_manuscript' (a non-ok status the
    strict gate surfaces). `relation` is one of:
        ('gt',  t)          -> ok iff value >  t
        ('lt',  t)          -> ok iff value <  t
        ('approx', t, frac) -> ok iff |value - t| <= |t|*frac   (for manuscript '~t' magnitudes)
        ('printed', t, d)   -> ok iff value ROUNDS to the printed value t at the
                               manuscript's own printed precision: |value - t| <=
                               0.5 * 10**-d, where d is the number of decimals the
                               manuscript prints (d may be negative, e.g. d = -1 for
                               a value the manuscript states to one significant
                               figure such as "roughly 30 years"). The bound is
                               inclusive, so a value exactly on the half-ulp
                               boundary (e.g. 0.95 printed as 0.9) passes. This is
                               the check to use for every number the manuscript
                               prints as a literal; it is NOT a tolerance to be
                               widened, it is the precision the author chose.
    Returns True iff 'ok'."""
    if value is None:
        record(name, None, "pending", (note_prefix + "; " if note_prefix else "") + "value absent")
        return False
    kind = relation[0]
    if kind == "gt":
        ok, rel = value > relation[1], f"> {relation[1]:g}"
    elif kind == "lt":
        ok, rel = value < relation[1], f"< {relation[1]:g}"
    elif kind == "approx":
        t, frac = relation[1], relation[2]
        ok, rel = abs(value - t) <= abs(t) * frac, f"~{t:g} (±{frac:.0%})"
    elif kind == "printed":
        t, d = relation[1], relation[2]
        # The boundary is inclusive, with a 1e-9 relative slack so that a value
        # sitting exactly on the half-ulp (e.g. 1.45 printed as 1.5) is not failed
        # by binary floating-point representation error.
        half = 0.5 * (10.0 ** (-d))
        ok = abs(value - t) <= half * (1 + 1e-9) + 1e-12
        rel = f"printed {t:g} (rounds at {d:d} dp, ±{half:g})"
    else:
        ok, rel = False, f"?{relation}"
    verdict = "MATCH" if ok else "OUTSIDE MANUSCRIPT"
    # Display at least as many decimals as the relation CHECKS, or the report destroys the very
    # precision it just verified: a maturity slope of 0.0002 checked at 4 dp was being written to
    # the report as 0.0 by a flat round(value, 3).
    _dp = 3
    if kind == "printed":
        _dp = max(3, int(relation[2]))
    disp = round(value, _dp) if isinstance(value, float) else value
    print(f"     -> value {disp} vs manuscript {rel}: {verdict}")
    note = (note_prefix + "; " if note_prefix else "") + f"manuscript {rel}; {verdict}"
    record(name, disp, "ok" if ok else "outside_manuscript", note)
    return ok


def _read(path):
    if not path.exists():
        rel = path.relative_to(ROOT)
        print(f"  [skip] missing input: {rel}")
        _MISSING_INPUTS.append(str(rel))
        return None
    return pd.read_csv(path)


# The cost-benefit innovation benefit is read from cost_benefit_total_value_did.csv
# (step 34, 16_total_patent_value_did.py); no dollar constant appears in this script.


# ===========================================================================
# #4  ">150%" larger-firms safety innovation (Results, L441)
# ===========================================================================
def derived_safety_by_asset():
    print("\n[#4] Larger-firms safety innovation (manuscript: \">150%\")")
    pct = _read(TABLES / "firm_heterogeneity_k_pct.csv")
    if pct is None:
        print("     firm_heterogeneity_k_pct.csv not present (regenerates in "
              "restricted mode via 07_firm_heterogeneity.py).")
        record("larger_firm_safety_pct", None, "pending", "firm_heterogeneity_k_pct.csv absent")
        return
    row = pct[(pct.specification == "2_1_safety") & (pct.tercile == "Third")]
    if len(row):
        ratio = float(row["ratio"].iloc[0])
        print(f"     2_1_safety, Third (largest) tercile ratio = {ratio:.3f} "
              f"-> {ratio*100:.0f}% increase in P(>=1 safety innovation).")
        # 'ok' only if the ratio actually exceeds 150%.
        check("larger_firm_safety_pct", round(ratio * 100, 1), ("gt", 150.0),
              "larger-firm safety innovation (manuscript >150%)")
    else:
        record("larger_firm_safety_pct", None, "pending", "2_1_safety Third-tercile row absent")


# ===========================================================================
# #6  cost-benefit ($23.5M innovation + $4.3M safety ~= $28M) + Class II counts
# ===========================================================================
def derived_cost_benefit():
    print("\n[#6] Cost-benefit for Class II -> I deregulation "
          "(manuscript: ~$28M; tab:CostBenefits)")
    adv = _read(TABLES / "PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv")

    # --- safety side: hospitalizations + deaths avoided x unit values ---
    if adv is not None:
        h = float(adv.loc[adv.outcome == "H", "Estimate"].iloc[0])   # ~ -1.773
        d = float(adv.loc[adv.outcome == "D", "Estimate"].iloc[0])   # ~ -0.426
        safety_value = abs(d) * VSL + abs(h) * HOSP_COST
        print(f"     Hospitalization estimate H = {h:.3f}/yr  (tab:CostBenefits row: -1.77)")
        print(f"     Mortality estimate     D = {d:.3f}/yr  (tab:CostBenefits row: -0.43)")
        print(f"     Safety value = |D|*$10M VSL + |H|*$22k = "
              f"${abs(d)*VSL/1e6:.2f}M + ${abs(h)*HOSP_COST/1e6:.3f}M "
              f"= ${safety_value/1e6:.2f}M  (manuscript: ~$4.3M)")
        check("cost_benefit_safety_value_M", round(safety_value / 1e6, 3), ("printed", 4.3, 1),
              "cost-benefit safety side")
    else:
        safety_value = None
        record("cost_benefit_safety_value_M", None, "pending", "adverse-event estimates absent")

    # --- innovation side: total-value DiD (step 34) ---
    # The cost-benefit innovation benefit is the difference-in-differences effect
    # on the TOTAL market value of public-firm patents per device-type-year, times
    # the 20% retention share (JPE_submission_v8.tex L517 footnote + tab:CostBenefits).
    # That DiD is estimated from data by 16_total_patent_value_did.py (run_all
    # step 34), which writes cost_benefit_total_value_did.csv. We READ that estimate
    # here; it is reproducible from the shipped matched sample + all_patents_w_xi.
    cbv = _read(TABLES / "cost_benefit_total_value_did.csv")
    innovation_value = None
    if cbv is not None and "reclass_type" in cbv.columns:
        row = cbv[cbv.reclass_type.astype(str) == "2_1"]
        if len(row):
            did_effect = float(row["did_effect_2019M"].iloc[0]) * 1e6
            innovation_value = float(row["innovation_benefit_2019M"].iloc[0]) * 1e6
            print(f"     Total-value DiD effect (II->I) = ${did_effect/1e6:.1f}M/yr "
                  f"per device type (from step 34, cost_benefit_total_value_did.csv)")
            print(f"     Innovation benefit = ${did_effect/1e6:.1f}M * "
                  f"{PATENT_RETENTION:.0%} retention = ${innovation_value/1e6:.1f}M/yr "
                  f"(manuscript: ~$23.5M)")
            check("cost_benefit_innovation_value_M", round(innovation_value / 1e6, 3), ("printed", 23.5, 1),
                  "cost-benefit innovation side (data-driven total-value DiD)")
    if innovation_value is None:
        print("     [skip] cost_benefit_total_value_did.csv absent -- run step 34 "
              "(16_total_patent_value_did.py; restricted/synthetic mode) to generate "
              "the data-driven innovation benefit.")
        record("cost_benefit_innovation_value_M", None, "pending", "step-34 total-value DiD absent")

    if innovation_value is not None and safety_value is not None:
        net = innovation_value + safety_value
        print(f"     NET = ${innovation_value/1e6:.1f}M innovation + "
              f"${safety_value/1e6:.2f}M safety = ${net/1e6:.1f}M  (manuscript: ~$28M).")
        check("cost_benefit_net_M", round(net / 1e6, 3), ("printed", 28.0, 0), "cost-benefit net")
    else:
        record("cost_benefit_net_M", None, "pending", "innovation or safety side missing")

    # --- Class II maturity counts (Figure DeviceExperienceCurrent method; JPE 2.2) ---
    # The over-63-year count is COMPUTED from the invention-year data the SAME way the cited
    # figure builds it (11d_reg_design.py `Distribution_of_2_over_years`): 510(K) product codes
    # with invention-year data, post-2015 cross-section, device age = 2019 - invention year.
    DERIVED_DIR = ROOT / "data" / "derived"
    regnum_p = next((c for c in (DERIVED_DIR / "RegNum_Factorized_Synth.csv",
                                 RAW / "RegNum_Factorized_Synth.csv") if c.exists()), None)
    inv_p = RAW / "innovation_year_all_other_FDA_project.csv"
    fs_p = DERIVED_DIR / "Full_sample.csv"
    if regnum_p is not None and inv_p.exists() and fs_p.exists():
        sn = pd.read_csv(regnum_p, dtype=str, low_memory=False).drop_duplicates("PRODUCTCODE_x")
        sn["PRODUCTCODE"] = sn["PRODUCTCODE_x"]
        n_cls2 = int(sn.loc[sn.DEVICECLASS == "2", "PRODUCTCODE"].nunique())
        print(f"     Class II product codes (DEVICECLASS==2) = {n_cls2}  (manuscript: ~3,100).")
        # Printed as a diagnostic, not registered as a manuscript scalar: the manuscript prints no
        # Class II product-code COUNT anywhere -- it gives shares ("About 56\% of product codes are
        # Class II") -- so this count is not graded against ~3,100. The universe is printed above
        # for context; it is simply not a manuscript claim.
        inv = pd.read_csv(inv_p)
        inv510 = pd.merge(inv, sn[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]], on="PRODUCTCODE", how="left")
        inv510 = inv510[inv510.SUBMISSION_TYPE_ID == "510(K)"]
        fs = pd.read_csv(fs_p, low_memory=False)
        o2 = fs[fs.PRODUCTCODE.isin(inv510["PRODUCTCODE"])].merge(
            inv510[["PRODUCTCODE", "years"]], on="PRODUCTCODE", how="left")
        o2["exp_years"] = 2019 - o2["years"]
        d2 = (o2[o2.year > 2015.0].groupby(["PRODUCTCODE", "exp_years"]).mean(numeric_only=True)
              .reset_index().drop_duplicates("PRODUCTCODE"))
        n_cross = int(d2.PRODUCTCODE.nunique())
        n_over63 = int((d2.exp_years > MANUSCRIPT_MATURITY_THRESHOLD_YEARS).sum())
        rate = (n_over63 / n_cross) if n_cross else float("nan")
        print(f"     Class II over the {MANUSCRIPT_MATURITY_THRESHOLD_YEARS:g}-year maturity "
              f"threshold = {n_over63} of {n_cross} ({rate:.1%}) device types "
              f"(manuscript: ~650 / ~29%).")
        # The threshold above is the one the MANUSCRIPT prints. The pipeline's own
        # fitted zero-crossing (output/tables/exp_impact_zero_crossings.csv) differs;
        # the counts at that crossing are printed here -- not registered -- so the
        # size of the divergence is visible without editing this file.
        _cross = _read(TABLES / "exp_impact_zero_crossings.csv")
        if _cross is not None:
            _r = _cross[(_cross.reclass_type.astype(str) == "2_1")
                        & (_cross.outcome == "v_serious_est")]
            if len(_r):
                _t = float(_r["zero_crossing_years"].iloc[0])
                _n = int((d2.exp_years > _t).sum())
                print(f"     [for comparison] at the pipeline's own fitted crossing "
                      f"({_t:g} years): {_n} of {n_cross} ({_n / n_cross:.1%}) device types.")
        check("class_II_maturity_rate_pct", round(rate * 100, 1), ("printed", 29.0, 0),
              "Class II share over 60-yr maturity threshold (figure method)")
        check("class_II_over_threshold", n_over63, ("printed", 650, -1),
              "Class II count over 60-yr maturity threshold (figure method, reproducible)")
        # Class III (PMA) maturity: manuscript 'over 80% of Class III exceeding 30 years' (same figure method)
        invPMA = pd.merge(inv, sn[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]], on="PRODUCTCODE", how="left")
        invPMA = invPMA[invPMA.SUBMISSION_TYPE_ID == "PMA"]
        o3 = fs[fs.PRODUCTCODE.isin(invPMA["PRODUCTCODE"])].merge(
            invPMA[["PRODUCTCODE", "years"]], on="PRODUCTCODE", how="left")
        o3["exp_years"] = 2019 - o3["years"]
        d3 = (o3[o3.year > 2015.0].groupby(["PRODUCTCODE", "exp_years"]).mean(numeric_only=True)
              .reset_index().drop_duplicates("PRODUCTCODE"))
        n3 = int(d3.PRODUCTCODE.nunique())
        n3_over30 = int((d3.exp_years > 30).sum())
        rate3 = (n3_over30 / n3) if n3 else float("nan")
        print(f"     Class III over the 30-year maturity threshold = {n3_over30} of {n3} "
              f"({rate3:.1%}) device types (manuscript: 'over 80%').")
        check("class_III_maturity_rate_pct", round(rate3 * 100, 1), ("approx", 82.0, 0.10),
              "Class III share over 30-yr maturity threshold (figure method)")
    else:
        record("class_II_product_codes", None, "pending", "RegNum/invention/Full_sample absent")
        record("class_II_maturity_rate_pct", None, "pending", "RegNum/invention/Full_sample absent")
        record("class_II_over_threshold", None, "pending", "RegNum/invention/Full_sample absent")
        record("class_III_maturity_rate_pct", None, "pending", "RegNum/invention/Full_sample absent")


# ===========================================================================
# #2  "~77% hospitalizations / 40-70% deaths" reduction (Results, L432)
# ===========================================================================
def counterfactual_pct_reduction(estimate, control_slope, treated_pre_level, horizon):
    """Author's method: project the treated group's counterfactual level using
    the CONTROL group's slope from the treated pre-level, then express the
    treatment effect (estimate, e.g. the long-run event-time coefficient) as a
    fraction of that counterfactual level.

        counterfactual_level = treated_pre_level + control_slope * horizon
        pct_reduction        = estimate / counterfactual_level
    """
    cf = treated_pre_level + control_slope * horizon
    if cf == 0:
        return None
    return estimate / cf


def _cf_pct_from_es_csv(path):
    """Compute the % reduction at each post-period event time from an
    ES-coefficient CSV (cols: ET, Effect, treated_mean, control_mean).

    In this stacked design the control group is POOLED (never-treated; all at
    ET==0), so there is no control-group event-time slope to project. The
    reproducible counterfactual is therefore the MODEL-IMPLIED counterfactual
    level -- the treated level absent the treatment effect:

        counterfactual_level(h) = treated_mean(h) - Effect(h)
        pct_reduction(h)        = |Effect(h)| / counterfactual_level(h)
    """
    df = pd.read_csv(path)
    if not {"ET", "Effect", "treated_mean"} <= set(df.columns):
        return None
    df = df.set_index("ET")
    rows = []
    for h in sorted(x for x in df.index if x > 0):
        eff = float(df.loc[h, "Effect"])
        tm = float(df.loc[h, "treated_mean"])
        cf = tm - eff  # model-implied counterfactual level
        pct = abs(eff) / cf if cf else float("nan")
        rows.append((h, eff, cf, pct))
    return rows


def derived_safety_pct_reductions():
    print("\n[#2] Safety % reductions (manuscript: ~77% hosp, 40-70% deaths)")
    print("     METHOD: pct = |effect(h)| / counterfactual, where the control")
    print("     group is pooled (never-treated) so the counterfactual is the")
    print("     model-implied level: counterfactual = treated_mean(h) - effect(h).")
    es_dir = TABLES / "event_study_coefficients"
    if not es_dir.exists():
        print("     STATUS: pending. Run the full pipeline (restricted) so that")
        print("     04_event_studies.py writes output/tables/event_study_coefficients/")
        print("     ES_coefs_2_1_*.csv (the per-ET effects + treated/control level")
        print("     trajectories). The export hook is now in 04_event_studies.py;")
        print("     it just hasn't been run in this copy.")
        record("hosp_reduction_pct", None, "pending", "event_study_coefficients/ absent")
        record("death_reduction_pct", None, "pending", "event_study_coefficients/ absent")
        return
    # Find the 2_1 adverse-event outcome files (hospitalization, mortality, etc.)
    files = sorted(es_dir.glob("ES_coefs_2_1_*.csv"))
    if not files:
        print("     STATUS: ES-coefficient dir exists but no 2_1 files found.")
        record("hosp_reduction_pct", None, "pending", "no ES_coefs_2_1_*.csv files")
        record("death_reduction_pct", None, "pending", "no ES_coefs_2_1_*.csv files")
        return
    # Reported horizon window (locked): the long-run post-reclassification
    # decade ET 10-15. The cited ~77% (hosp) / 40-70% (deaths) are the central
    # reductions over this window; year-by-year estimates are noisy.
    H_LO, H_HI = 10, 15
    print(f"     Found {len(files)} ES-coefficient file(s). "
          f"Reported long-run window: ET {H_LO}-{H_HI}.")
    central = {}   # outcome-file stem -> central reduction % over the window
    for f in files:
        rows = _cf_pct_from_es_csv(f)
        if not rows:
            continue
        win = [r for r in rows if H_LO <= r[0] <= H_HI]
        pcts = [r[3] * 100 for r in win if r[3] == r[3]]  # drop nan
        print(f"     -- {f.name} --")
        for h, eff, cf, pct in win:
            print(f"        ET={h:>2}: effect={eff:+.3f}  cf_level={cf:.3f}  "
                  f"reduction={pct*100:.0f}%")
        if pcts:
            c = sorted(pcts)[len(pcts) // 2]
            central[f.stem] = c
            print(f"        => window ET{H_LO}-{H_HI}: range "
                  f"{min(pcts):.0f}-{max(pcts):.0f}%, central ~{c:.0f}%")
    print("     Manuscript: hosp ~77%, deaths 40-70%")
    print("     (central reductions over this long-run window; gate range in MANUSCRIPT_RANGE below).")
    # Register the hospitalization (H) and mortality/death (D) central reductions so their absence
    # is caught by the completeness gate (not silently omitted).
    # Compare the event-study central reduction (ET 10-15 median) against the manuscript's stated
    # range. A value outside the range records a non-"ok" status and fails the strict gate. NOTE: the
    # manuscript magnitudes (Sec 6, tab:AdverseEvent Panel B) are DiD-across-control-comparisons; the
    # value computed here is the event-study central over ET 10-15 -- a related but DISTINCT lens --
    # so an out-of-range value is a method-reconciliation item for the author, not an automatic
    # manuscript error.
    # MANUSCRIPT_RANGE brackets the printed ~77% (central 77.5%) with the tolerance the text implies.
    MANUSCRIPT_RANGE = {"hosp_reduction_pct": (72.0, 82.0), "death_reduction_pct": (40.0, 70.0)}
    for key, stem in (("hosp_reduction_pct", "ES_coefs_2_1_H"), ("death_reduction_pct", "ES_coefs_2_1_D")):
        if stem in central:
            val = round(central[stem], 1)
            lo, hi = MANUSCRIPT_RANGE[key]
            if lo <= val <= hi:
                record(key, val, "ok",
                       f"event-study central (ET10-15) {val}% within manuscript {lo:.0f}-{hi:.0f}%")
            else:
                record(key, val, "outside_manuscript_range",
                       f"event-study central (ET10-15) {val}% OUTSIDE manuscript {lo:.0f}-{hi:.0f}% "
                       f"-- author: reconcile method (manuscript magnitudes are DiD-across-controls, "
                       f"not the event-study median)")
        else:
            record(key, None, "pending", f"{stem}.csv absent or unusable")


# The COMPLETE set of in-text magnitudes this step must register. A number that is not recorded
# (e.g. a function returns early without a record() call) is caught here as a missing name.
def derived_exp_crossings():
    """#7 Market-age zero-crossings (Section 6): the fitted post-reclassification change in the
    serious-event measure crosses zero at ~30 years (III->II) and ~63 years (II->I). Reproduced from
    11d_reg_design.py's emitted output/tables/exp_impact_zero_crossings.csv (v_serious_est rows)."""
    print("\n[#7] Experience zero-crossings (manuscript: ~30 yrs III->II, ~63 yrs II->I; serious-event)")
    df = _read(TABLES / "exp_impact_zero_crossings.csv")
    if df is None:
        print("     exp_impact_zero_crossings.csv not present (regenerates via 11d_reg_design.py).")
        record("exp_crossing_serious_3_2", None, "pending", "exp_impact_zero_crossings.csv absent")
        record("exp_crossing_serious_2_1", None, "pending", "exp_impact_zero_crossings.csv absent")
        return
    # The check is against the value the manuscript prints, at the precision it prints it.
    #   II->I : the paper states "roughly 60 years" and "the 60-year maturity threshold",
    #           a hedged value -> checked at -1 decimals, exactly as III->II is.
    #   III->II: the paper states "roughly 30 years", a hedged one-significant-figure
    #           value -> checked at -1 decimals (i.e. rounds to the nearest 10).
    for rc, name, relation, printed in (
            ("3_2", "exp_crossing_serious_3_2", ("printed", 30.0, -1), "roughly 30"),
            ("2_1", "exp_crossing_serious_2_1", ("printed", 60.0, -1), "roughly 60")):
        row = df[(df.reclass_type.astype(str) == rc) & (df.outcome == "v_serious_est")]
        if len(row):
            yrs = float(row["zero_crossing_years"].iloc[0])
            print(f"     {rc} serious-event fit crosses zero at {yrs:.1f} years "
                  f"(manuscript prints {printed}).")
            check(name, round(yrs, 1), relation, f"{rc} serious-event zero-crossing")
        else:
            record(name, None, "pending", f"no v_serious_est crossing row for {rc}")


def derived_maturity_slopes():
    """#7b Section 6 footnote maturity-gradient age slopes (log(y+1) spec). Reproduced from
    11d_reg_design.py's emitted maturity_gradient_slopes.csv. Verified on the real-data run
    (2026-07-15) to reproduce the manuscript footnote exactly; the value here is the pipeline's,
    compared against the published slope."""
    print("\n[#7b] Maturity-gradient age slopes (Section 6 footnote)")
    df = _read(TABLES / "maturity_gradient_slopes.csv")
    # (reclass, outcome) -> (registry name, published manuscript slope)
    targets = {
        ("3_2", "v_serious_est"): ("maturity_slope_serious_3_2", -0.0170),
        ("3_2", "patent_est"):    ("maturity_slope_patent_3_2",  -0.0396),
        ("2_1", "v_serious_est"): ("maturity_slope_serious_2_1", -0.0015),
        ("2_1", "patent_est"):    ("maturity_slope_patent_2_1",   0.0002),
    }
    if df is None:
        print("     maturity_gradient_slopes.csv absent (regenerates via 11d_reg_design.py).")
        for (_rc, _oc), (name, _ms) in targets.items():
            record(name, None, "pending", "maturity_gradient_slopes.csv absent")
        return
    for (rc, oc), (name, ms) in targets.items():
        row = df[(df.reclass_type.astype(str) == rc) & (df.outcome == oc)]
        if len(row):
            slope = float(row["slope"].iloc[0])
            print(f"     {rc}/{oc}: β={slope:.4f} (manuscript {ms:.4f})")
            # Graded at the four decimals the footnote prints, via the same check() as every other
            # printed scalar.
            check(name, round(slope, 4), ("printed", ms, 4),
                  f"{rc}/{oc} maturity-gradient age slope (Section 6 footnote)")
        else:
            record(name, None, "pending", f"no {rc}/{oc} slope row")


# ===========================================================================
# HEADLINE MAGNITUDES (Results L210/L387/L212/L406) -- the "% more", fold, and
# price-decline magnitudes the prose states but does not write to a CSV. These
# are DERIVED additively from already-computed pipeline outputs; this block adds
# NO estimation and changes NO existing output. The established %-method is:
#   "% more"  = Estimate / UNROUNDED pre-event mean * 100
#   fold      = 1 + Estimate / UNROUNDED pre-event mean   ("double"/"fivefold")
#   price     = |log-coef| * 100                          (05 logs BilledAmt)
# The preferred column is the matched-control estimate = the "_xi_latest_" CSV.
# Pre-event means are computed from the shipped matched innovation sample by
# replicating 10_table_formatting.py::compute_pre_treatment_stats.
# ===========================================================================
def _pre_treatment_means(reclass_type, outcome_vars):
    """Replicate 10_table_formatting.py::compute_pre_treatment_stats -- treated units
    (treatment==1) with event_time in [-5,-1] -- on the shipped matched innovation
    sample data/derived/matched_sample_{reclass_type}_onepat_innovation.csv, and return
    {outcome_var: pre-event mean}. These UNROUNDED means are the denominators for the
    magnitudes below; they are computed from data here. Returns None if
    the sample is absent (fail-closed -- the caller then records the numbers pending)."""
    p = DERIVED / f"matched_sample_{reclass_type}_onepat_innovation.csv"
    if not p.exists():
        rel = p.relative_to(ROOT)
        print(f"  [skip] missing input: {rel}")
        _MISSING_INPUTS.append(str(rel))
        return None
    df = pd.read_csv(p, low_memory=False)
    if "treatment" not in df.columns:
        yr = "year_reclassified" if "year_reclassified" in df.columns else f"year_reclassified_{reclass_type}"
        df["treatment"] = 0
        df.loc[df[yr].notnull(), "treatment"] = 1
    if "event_time" not in df.columns:
        yr = "year_reclassified" if "year_reclassified" in df.columns else f"year_reclassified_{reclass_type}"
        df["event_time"] = df["year"] - df[yr]
    mask = (df["treatment"] == 1) & (df["event_time"] < 0) & (df["event_time"] > -6)
    pre = df.loc[mask]
    out = {}
    for v in outcome_vars:
        if v in pre.columns:
            m = float(pre[v].mean())
            out[v] = m if m == m else None  # drop NaN
        else:
            out[v] = None
    return out


def _pct_more(est_val, pre_mean):
    """'% more' = Estimate / unrounded pre-event mean * 100 (None if pre_mean unusable)."""
    if pre_mean is None or pre_mean == 0:
        return None
    return est_val / pre_mean * 100.0


def _fold(est_val, pre_mean):
    """fold = 1 + Estimate / unrounded pre-event mean ('double'/'fivefold'; None if unusable)."""
    if pre_mean is None or pre_mean == 0:
        return None
    return 1.0 + est_val / pre_mean


def derived_headline_innovation():
    """Innovation headline magnitudes (Results, L210 / L387; Table \\ref{tab:Innovation}).
    III->II preferred (matched, xi_latest): patents & submissions '140--350%'; citations
    'nearly three times' (~2.99x); market value 'double' (~2.00x). II->I: patents 62%,
    citations 87%, market value 'increased modestly' (~+18%, n.s.). Baselines '8 patents/yr,
    1 submission/yr' are the pre-event means themselves."""
    print("\n[H-innov] Headline innovation magnitudes (Results L210/L387; tab:Innovation)")
    # --- III->II (down-regulation) ---
    mp32 = _read(TABLES / "PaperMainPanel_3_2_Estimates_NoLog_xi_latest_oct22_24.csv")
    pm32 = _pre_treatment_means("3_2", ["real_pats", "dev_count", "times_cited", "xi_real_2019"])
    innov_32 = ("baseline_patents_per_yr", "baseline_submissions_per_yr",
                "innov_real_pats_pct_3_2", "innov_dev_count_pct_3_2",
                "innov_times_cited_fold_3_2", "innov_xi_value_fold_3_2")
    if mp32 is not None and pm32 is not None:
        def e(o):
            return float(mp32.loc[mp32["outcome"] == o, "Estimate"].iloc[0])
        # baselines = the pre-event means themselves
        check("baseline_patents_per_yr", round(pm32["real_pats"], 3), ("approx", 8.25, 0.02),
              "III->II pre-event patents/yr baseline (manuscript '8 patents/yr'; pre-mean 8.25)")
        check("baseline_submissions_per_yr", round(pm32["dev_count"], 3), ("approx", 0.95, 0.02),
              "III->II pre-event submissions/yr baseline (manuscript '1 submission/yr'; pre-mean 0.95)")
        v = _pct_more(e("real_pats"), pm32["real_pats"])
        print(f"     real_pats: {e('real_pats')}/{pm32['real_pats']:.4f} = {v:.1f}% (manuscript 140-350, low end)")
        check("innov_real_pats_pct_3_2", round(v, 1), ("approx", 140.0, 0.06),
              "III->II patenting-rate % more (manuscript 140-350%, low end of range)")
        v = _pct_more(e("dev_count"), pm32["dev_count"])
        print(f"     dev_count: {e('dev_count')}/{pm32['dev_count']:.4f} = {v:.1f}% (manuscript 140-350, high end)")
        check("innov_dev_count_pct_3_2", round(v, 1), ("approx", 350.0, 0.06),
              "III->II submission-rate % more (manuscript 140-350%, high end ~348)")
        v = _fold(e("times_cited"), pm32["times_cited"])
        print(f"     times_cited fold: {v:.3f}x (manuscript 'nearly three times' ~2.99x)")
        check("innov_times_cited_fold_3_2", round(v, 3), ("approx", 2.99, 0.03),
              "III->II citations fold (manuscript 'nearly three times' ~2.99x)")
        v = _fold(e("xi_real_2019"), pm32["xi_real_2019"])
        print(f"     xi_real_2019 fold: {v:.3f}x (manuscript 'double' ~2.00x)")
        check("innov_xi_value_fold_3_2", round(v, 3), ("approx", 2.00, 0.03),
              "III->II patent-value fold (manuscript 'double' ~2.00x)")
    else:
        for n in innov_32:
            record(n, None, "pending", "III->II main panel or matched innovation sample absent")
    # --- II->I (deregulation) ---
    mp21 = _read(TABLES / "PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv")
    pm21 = _pre_treatment_means("2_1", ["real_pats", "times_cited", "xi_real_2019"])
    innov_21 = ("innov_real_pats_pct_2_1", "innov_times_cited_pct_2_1", "innov_xi_value_fold_2_1")
    if mp21 is not None and pm21 is not None:
        def e2(o):
            return float(mp21.loc[mp21["outcome"] == o, "Estimate"].iloc[0])
        v = _pct_more(e2("real_pats"), pm21["real_pats"])
        print(f"     II->I real_pats: {v:.1f}% (manuscript 62%)")
        check("innov_real_pats_pct_2_1", round(v, 1), ("approx", 62.0, 0.05),
              "II->I patenting-rate % more (manuscript 62%)")
        v = _pct_more(e2("times_cited"), pm21["times_cited"])
        print(f"     II->I times_cited: {v:.1f}% (manuscript 87%)")
        check("innov_times_cited_pct_2_1", round(v, 1), ("approx", 87.0, 0.05),
              "II->I citations % more (manuscript 87%)")
        v = _fold(e2("xi_real_2019"), pm21["xi_real_2019"])
        print(f"     II->I xi_real_2019 fold: {v:.3f}x (=+{(v-1)*100:.0f}%; manuscript 'increased modestly', n.s.)")
        check("innov_xi_value_fold_2_1", round(v, 3), ("approx", 1.18, 0.06),
              "II->I patent-value fold ~1.18x (=+18%); manuscript 'increased modestly' (not significant)")
    else:
        for n in innov_21:
            record(n, None, "pending", "II->I main panel or matched innovation sample absent")


def derived_headline_market_price():
    """Market-composition + price headline magnitudes (Results, L212 / L406; tab:MarketComposition
    and the price analysis). III->II: new-firm entry (submissions) ~600% (computed ~628, reported to
    1 sig fig), new entry (patents) 164%, incumbent entry 'fivefold' (~5.9x). II->I: new entry (patents)
    72%; outpatient price decline 32% (|log-coef|*100 from 05's BilledAmt All-CPTs BJS-imputation row)."""
    print("\n[H-market] Headline market-composition + price magnitudes (Results L212/L406)")
    # --- III->II market composition ---
    mc32 = _read(TABLES / "PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_oct22_24.csv")
    pm32 = _pre_treatment_means("3_2", ["absnew_firm_count", "unique_firms", "firm_expansion"])
    mkt_32 = ("market_absnew_firm_pct_3_2", "market_unique_firms_pct_3_2", "market_firm_expansion_fold_3_2")
    if mc32 is not None and pm32 is not None:
        def e(o):
            return float(mc32.loc[mc32["outcome"] == o, "Estimate"].iloc[0])
        v = _pct_more(e("absnew_firm_count"), pm32["absnew_firm_count"])
        print(f"     absnew_firm_count (new entry, submissions): {v:.1f}% (computed ~628; manuscript 600, 1 sig fig)")
        check("market_absnew_firm_pct_3_2", round(v, 1), ("approx", 600.0, 0.06),
              "III->II new-firm entry (submissions) % more; computed ~628%, manuscript reports 600% (one sig fig)")
        v = _pct_more(e("unique_firms"), pm32["unique_firms"])
        print(f"     unique_firms (new entry, patents): {v:.1f}% (manuscript 164%)")
        check("market_unique_firms_pct_3_2", round(v, 1), ("approx", 164.0, 0.03),
              "III->II new entry (patents) % more (manuscript 164%)")
        v = _fold(e("firm_expansion"), pm32["firm_expansion"])
        print(f"     firm_expansion (incumbent entry) fold: {v:.3f}x (manuscript 'fivefold'; computed 5.88x)")
        check("market_firm_expansion_fold_3_2", round(v, 3), ("approx", 5.9, 0.03),
              "III->II incumbent-entry fold; computed 5.88x, manuscript prose 'fivefold'")
    else:
        for n in mkt_32:
            record(n, None, "pending", "III->II market composition or matched innovation sample absent")
    # --- II->I market composition ---
    mc21 = _read(TABLES / "PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_oct22_24.csv")
    pm21 = _pre_treatment_means("2_1", ["unique_firms"])
    if mc21 is not None and pm21 is not None:
        v = _pct_more(float(mc21.loc[mc21["outcome"] == "unique_firms", "Estimate"].iloc[0]), pm21["unique_firms"])
        print(f"     II->I unique_firms (new entry, patents): {v:.1f}% (manuscript 72%)")
        check("market_unique_firms_pct_2_1", round(v, 1), ("approx", 72.0, 0.03),
              "II->I new entry (patents) % more (manuscript 72%)")
    else:
        record("market_unique_firms_pct_2_1", None, "pending", "II->I market composition or matched innovation sample absent")
    # --- II->I outpatient price decline: |log-coef|*100 (05 logs BilledAmt) ---
    pu = _read(TABLES / "price_utilization_estimates.csv")
    if pu is not None:
        row = pu[(pu["outcome"] == "BilledAmt")
                 & (pu["reclass_type"].astype(str) == "2_1")
                 & (pu["sample"].astype(str).str.strip() == "All CPTs")
                 & (pu["method"] == "BJS_imputation")]
        if len(row):
            coef = float(row["Estimate"].iloc[0])
            v = abs(coef) * 100.0
            print(f"     II->I price |log-coef|*100 = |{coef}|*100 = {v:.1f}% (manuscript 32%)")
            check("price_billedamt_pct_2_1", round(v, 1), ("approx", 32.0, 0.03),
                  "II->I outpatient price decline = |log-coef|*100 (All CPTs, BJS-imputation) (manuscript 32%)")
        else:
            record("price_billedamt_pct_2_1", None, "pending", "no 2_1/BilledAmt/All-CPTs/BJS-imputation row")
    else:
        record("price_billedamt_pct_2_1", None, "pending", "price_utilization_estimates.csv absent")


EXPECTED_INTEXT_NAMES = {
    "case_study_patent_value_2019_millions",
    "spinal_audit_n_firms", "spinal_audit_n_subsidiaries", "spinal_audit_founded_median",
    "spinal_audit_founded_mean", "spinal_audit_n_acquired", "spinal_audit_us_based_pct",
    "larger_firm_safety_pct",            # #4  ">150%"
    "exp_crossing_serious_3_2",          # #7  ~30 years (III->II)
    "exp_crossing_serious_2_1",          # #7  ~63 years (II->I)
    "maturity_slope_serious_3_2",        # #7b footnote  -0.0170
    "maturity_slope_patent_3_2",         # #7b footnote  -0.0396
    "maturity_slope_serious_2_1",        # #7b footnote  -0.0015
    "maturity_slope_patent_2_1",         # #7b footnote   0.0002
    "cost_benefit_safety_value_M",       # #6  ~$4.3M
    "cost_benefit_innovation_value_M",   # #6  ~$23.5M
    "cost_benefit_net_M",                # #6  ~$28M
    "class_II_maturity_rate_pct",         # #6  ~24% over the 63-year threshold
    "class_II_over_threshold",           # #6  ~540 (about 24% of coded device types)
    "class_III_maturity_rate_pct",        # #6  >80% over the 30-year threshold
    "hosp_reduction_pct",                # #2  ~77%
    "death_reduction_pct",               # #2  40-70%
    # --- headline magnitudes (Results L210/L387/L212/L406) ---
    "baseline_patents_per_yr",           # 8.25 patents/yr (pre-mean)
    "baseline_submissions_per_yr",       # 0.95 submissions/yr (pre-mean)
    "innov_real_pats_pct_3_2",           # III->II patents % (140-350, low end)
    "innov_dev_count_pct_3_2",           # III->II submissions % (140-350, high end ~348)
    "innov_times_cited_fold_3_2",        # III->II citations 'nearly three times' ~2.99x
    "innov_xi_value_fold_3_2",           # III->II patent value 'double' ~2.00x
    "innov_real_pats_pct_2_1",           # II->I patents % (~62)
    "innov_times_cited_pct_2_1",         # II->I citations % (~87)
    "innov_xi_value_fold_2_1",           # II->I patent value ~1.18x (+18%, n.s.)
    "market_absnew_firm_pct_3_2",        # III->II new-firm entry (subm.) % (~628; manuscript 600)
    "market_unique_firms_pct_3_2",       # III->II new entry (pat.) % (~164)
    "market_firm_expansion_fold_3_2",    # III->II incumbent entry fold (~5.9; 'fivefold')
    "market_unique_firms_pct_2_1",       # II->I new entry (pat.) % (~72)
    "price_billedamt_pct_2_1",           # II->I outpatient price decline % (~32)
    "invention_year_gpt_corr",           # GPT-vs-hand invention-year validation r (~0.76)
    "case_study_patents_fold",           # contact-lens patents post/pre (>10, 'more than tenfold')
    "case_study_devices_fold",           # contact-lens submissions post/pre (~4, 'roughly quadrupled')
    "case_study_firms_fold",             # contact-lens firms post/pre (~5, 'fivefold')
    "breakthrough_panel_n",              # III->II breakthrough panel obs (1,584)
    "breakthrough_panel_mean",           # breakthrough count mean (~0.66)
    "breakthrough_panel_sd",             # breakthrough count s.d. (~3.20)
    "breakthrough_panel_max",            # breakthrough count max (51)
    "breakthrough_panel_pct_zero",       # breakthrough panel zero share (~81%)
    # --- event-study figure overlays and caption values (twelve \put overlays) ---
    "es_base_rate_3_2_real_pats",
    "es_base_rate_3_2_dev_count",
    "es_base_rate_2_1_real_pats",
    "es_base_rate_3_2_unique_firms",
    "es_base_rate_2_1_unique_firms",
    "es_base_rate_3_2_v_serious",
    "es_base_rate_2_1_v_serious",
    "es_base_rate_3_2_real_pats_petitioned",
    "es_base_rate_3_2_absnew_firm_count",
    "es_base_rate_3_2_firm_expansion",
    "es_base_rate_2_1_firm_expansion_patents",
    "es_base_rate_3_2_firm_expansion_patents",
    "normalizable_serious_per_procedure",  # 0.002 serious events per procedure
    "adverse_mortality_baseline_2_1",      # 0.2 deaths/yr pre-mean
    "es_alt_control_specs",                # the four "not shown" control-group ES
    # --- price: expert concordance and sample construction ---
    "price_billedamt_expert_3_2",
    "price_billedamt_expert_3_2_se",
    "price_billedamt_expert_2_1",
    "price_billedamt_expert_2_1_se",
    "price_devices_1998_cohort",
    "price_analytic_procedure_codes",
    "price_analytic_proc_code_year_obs",
    "price_expert_treated_device_types",
    "price_coverage_2_1",
    "price_coverage_3_2",
    # --- descriptive universes ---
    "class_I_share_pct",
    "class_I_exempt_share_pct",
    "class_II_share_pct",
    "class_III_share_pct",
    "fda_device_types",
    "maude_reports_millions",
    "maude_top_n_reporters", "maude_top_n_report_share_pct", "maude_top_n_unlinked",
    "patent_universe_1976_2019",
    "patent_universe_keyword",
    "patent_universe_a61_nodrug",
    "patent_universe_gpt4o",
    "safety_term_share_pct",
    "class2_device_types_2015",
    # --- regulation design, recalls and the 2015 event ---
    "dpm_top_decile_ratio",
    "recall_decline_per_device_type_year",
    "recall_decline_pct",
    "new_entry_2015_baseline_firms_per_yr",
    "new_entry_2015_effect_2yr",
    "new_entry_2015_pct_2yr",
    "new_entry_1996_8_effect_2yr",
    "new_entry_1996_8_pct_2yr",
    # --- precision of the maturity-gradient footnote, and its N ---
    "maturity_slope_serious_3_2_se",
    "maturity_slope_serious_3_2_p",
    "maturity_slope_patent_3_2_se",
    "maturity_slope_patent_3_2_p",
    "maturity_slope_serious_2_1_se",
    "maturity_slope_serious_2_1_p",
    "maturity_slope_patent_2_1_se",
    "maturity_slope_patent_2_1_p",
    "maturity_gradient_n",
    # --- remaining magnitudes stated in prose over shipped table cells ---
    "cost_benefit_did_effect_M",
    "adverse_hosp_per_yr_2_1",
    "adverse_death_per_yr_2_1",
    "restricted_gpt4o_share",
    "restricted_spillover_share",
    "lbd_pct_first_tercile",
    "lbd_pct_third_tercile",
    "safety_emphasis_pct_2_1",
    "sample_construction_reclass_total",
    "sample_construction_fda_initiated",
    "sample_construction_petitioned",
    "safety_embed_p99_2_1",
    "safety_embed_p95_2_1",
    "safety_embed_p99_3_2",
    "safety_embed_p95_3_2",
}


def _row_where(df, col, val):
    m = df[df[col].astype(str).str.startswith(str(val))]
    return m.iloc[0] if len(m) else None


def derived_case_study_ratios():
    """Contact-lens case-study ratios (intro L203), reconciled to the figure's 1984-2017 window and emitted
    by 12_contact_lens_case_study.py -> output/tables/contact_lens_case_study_ratios.csv. Manuscript:
    patents 'more than tenfold' (>10), device submissions 'roughly quadrupled' (~4), firms 'fivefold' (~5)."""
    print("\n[case study] contact-lens post/pre ratios (manuscript: >10x / ~4x / ~5x)")
    df = _read(TABLES / "contact_lens_case_study_ratios.csv")
    targets = {"patents_allpats": ("case_study_patents_fold", ("gt", 10.0)),
               "dev_count": ("case_study_devices_fold", ("approx", 4.0, 0.12)),
               "firm_count": ("case_study_firms_fold", ("approx", 5.0, 0.12))}
    if df is None or "measure" not in df.columns or "ratio" not in df.columns:
        for name, _ in targets.values():
            record(name, None, "pending", "contact_lens_case_study_ratios.csv absent (emitted by 12 on the run)")
        return
    for measure, (name, rel) in targets.items():
        r = _row_where(df, "measure", measure)
        if r is None:
            record(name, None, "pending", f"row {measure} absent")
        else:
            check(name, round(float(r["ratio"]), 3), rel, f"contact-lens {measure} post/pre ratio")


def derived_breakthrough_distribution():
    """III->II breakthrough-count device-type-year distribution (manuscript ~L1724, restated to the shipped
    1,584-obs panel), emitted by 14_breakthrough_patents.py -> output/tables/BreakthroughPanel_distribution.csv."""
    print("\n[breakthrough] III->II panel distribution (manuscript: n=1,584, mean~0.66, sd~3.20, max 51)")
    df = _read(TABLES / "BreakthroughPanel_distribution.csv")
    if df is None or "panel" not in df.columns:
        for n in ("breakthrough_panel_n", "breakthrough_panel_mean", "breakthrough_panel_sd", "breakthrough_panel_max"):
            record(n, None, "pending", "BreakthroughPanel_distribution.csv absent (emitted by 14 on the run)")
        return
    r = _row_where(df, "panel", "3_2")
    if r is None:
        for n in ("breakthrough_panel_n", "breakthrough_panel_mean", "breakthrough_panel_sd", "breakthrough_panel_max"):
            record(n, None, "pending", "3_2 panel row absent")
        return
    check("breakthrough_panel_n", int(r["n_obs"]), ("approx", 1584, 0.001), "III->II breakthrough panel N")
    check("breakthrough_panel_mean", round(float(r["mean"]), 3), ("approx", 0.66, 0.03), "breakthrough count mean")
    check("breakthrough_panel_sd", round(float(r["sd"]), 3), ("approx", 3.20, 0.03), "breakthrough count s.d.")
    check("breakthrough_panel_max", int(r["max"]), ("approx", 51, 0.02), "breakthrough count max")


def derived_invention_year_validation():
    """Manuscript footnote L500 + body L1795 + caption L2508: r=0.76 (p<0.001) hold-out validation between
    HAND-CODED and GPT-4o introduction years for the 25 down-regulated (III->II) device types. The raw
    GPT-4o responses + parsed years ship in data/raw/innovation_year_FDA_project.csv (yr_invent_or_comm_avail
    = hand-coded; years = GPT-parsed via the `Year: (\\d{4})` regex). Recompute so the 0.76 is machine-
    checkable. NOTE: data/raw/innovation_year_3_2_FDA_project.csv is the DOWNSTREAM age-calc file whose
    `years` were replaced with the hand-coded values (r=1.0); the VALIDATION lives in this sibling."""
    print("\n[validation] GPT-4o vs hand-coded invention-year correlation (manuscript ~0.76)")
    df = _read(RAW / "innovation_year_FDA_project.csv")
    if df is None or not {"yr_invent_or_comm_avail", "years"} <= set(df.columns):
        record("invention_year_gpt_corr", None, "pending",
               "innovation_year_FDA_project.csv (yr_invent_or_comm_avail/years) absent or missing columns")
        return
    x = pd.to_numeric(df["yr_invent_or_comm_avail"], errors="coerce")
    y = pd.to_numeric(df["years"], errors="coerce")
    mask = x.notna() & y.notna()
    if mask.sum() < 3:
        record("invention_year_gpt_corr", None, "pending", "too few paired invention-year rows")
        return
    r = float(x[mask].corr(y[mask]))
    print(f"     n={int(mask.sum())}  corr(hand, GPT) = {r:.4f}  (manuscript 0.76)")
    check("invention_year_gpt_corr", round(r, 3), ("approx", 0.76, 0.03),
          "GPT-vs-hand invention-year validation (manuscript r=0.76, p<0.001)")


# ===========================================================================
# JPE Policy 2.2 batch: every remaining numeric claim in the manuscript that a
# shipped program computes. Each block reads ONE pipeline output and registers
# its scalars against the value the manuscript PRINTS, at the precision the
# manuscript prints it (see check(..., ('printed', t, d))).
# ===========================================================================

# figure file -> (registry name, printed overlay value, printed decimals)
# The twelve "Base rate: X/yr" \put overlays on the manuscript's event-study
# figures, plus the serious-events-per-procedure value in the normalized panel's
# caption. Produced by 04_event_studies.write_event_study_base_rates().
_BASE_RATE_TARGETS = {
    "3_2_nolog_real_pats_oct22_24.png":
        ("es_base_rate_3_2_real_pats", 6.3, 1),
    "3_2_nolog_dev_count_oct22_24.png":
        ("es_base_rate_3_2_dev_count", 0.9, 1),
    "2_1_nolog_real_pats_oct22_24.png":
        ("es_base_rate_2_1_real_pats", 14.8, 1),
    "3_2_nolog_unique_firms_solo_CTs.png":
        ("es_base_rate_3_2_unique_firms", 3.0, 1),
    "2_1_nolog_unique_firms_oct22_24.png":
        ("es_base_rate_2_1_unique_firms", 6.8, 1),
    "3_2_nolog_v_serious_oct22_24.png":
        ("es_base_rate_3_2_v_serious", 0.6, 1),
    "2_1_nolog_v_serious_oct22_24.png":
        ("es_base_rate_2_1_v_serious", 0.5, 1),
    "3_2_nolog_real_pats_petitioned_oct22_24.png":
        ("es_base_rate_3_2_real_pats_petitioned", 7.5, 1),
    "3_2_nolog_absnew_firm_count_oct22_24.png":
        ("es_base_rate_3_2_absnew_firm_count", 0.1, 1),
    "3_2_nolog_firm_expansion_oct22_24.png":
        ("es_base_rate_3_2_firm_expansion", 0.3, 1),
    "2_1_nolog_firm_expansion_patents_oct22_24.png":
        ("es_base_rate_2_1_firm_expansion_patents", 2.2, 1),
    "3_2_nolog_firm_expansion_patents_oct22_24.png":
        ("es_base_rate_3_2_firm_expansion_patents", 1.5, 1),
    "2_1_nolog_v_serious_restrict_oct22_24.png":
        ("normalizable_serious_per_procedure", 0.002, 3),
    "2_1_nolog_D_oct22_24.png":
        ("adverse_mortality_baseline_2_1", 0.2, 1),
}


def derived_event_study_base_rates():
    """The pre-event base rates the manuscript prints on its event-study figures.

    Twelve values are typed as \\put overlays on the figures (Results and Appendix),
    a thirteenth is the normalized panel's caption value ("0.002 serious events per
    procedure"), and a fourteenth is the deaths-per-year pre-mean quoted in the
    Results text. All are now recomputed by 04_event_studies.py on the same
    estimation sample each figure uses and written to
    output/tables/event_study_base_rates.csv.
    """
    print("\n[base rates] event-study figure overlays (manuscript \\put values)")
    df = _read(TABLES / "event_study_base_rates.csv")
    if df is None or "figure_file" not in df.columns:
        for name, _t, _d in _BASE_RATE_TARGETS.values():
            record(name, None, "pending",
                   "event_study_base_rates.csv absent (emitted by 04 on the run)")
        return
    by_file = {}
    for _, r in df.iterrows():
        by_file.setdefault(str(r["figure_file"]), r)
    for fig_file, (name, printed, decimals) in _BASE_RATE_TARGETS.items():
        r = by_file.get(fig_file)
        if r is None:
            record(name, None, "pending", f"no base-rate row for {fig_file}")
            continue
        val = float(r["base_rate"])
        print(f"     {fig_file}: {val:.6g} (manuscript prints {printed:g})")
        check(name, round(val, 6), ("printed", printed, decimals),
              f"pre-event base rate printed on {fig_file}")


def derived_alt_control_event_studies():
    """The parallel-trends footnote states that the event-study coefficients "are
    similar to those estimated using the intuitive and later-treated controls (not
    shown)". The claim is comparative and hedged, so no magnitude of it is
    checkable; what IS checkable, and what was missing, is that the four
    alternative-control event studies exist at all. 04_event_studies.py now
    estimates them; this registers their presence so a run that stops producing
    them fails the gate."""
    print("\n[alt controls] 'not shown' intuitive / later-treated event studies")
    es_dir = TABLES / "event_study_coefficients"
    expected = ["ES_coefs_3_2_real_pats_intuitive.csv",
                "ES_coefs_3_2_real_pats_later.csv",
                "ES_coefs_2_1_real_pats_intuitive.csv",
                "ES_coefs_2_1_real_pats_later.csv"]
    present = [f for f in expected if (es_dir / f).exists()]
    for f in expected:
        if f not in present:
            print(f"  [skip] missing input: output/tables/event_study_coefficients/{f}")
            _MISSING_INPUTS.append(f"output/tables/event_study_coefficients/{f}")
    print(f"     {len(present)}/{len(expected)} alternative-control coefficient files present")
    check("es_alt_control_specs", len(present), ("printed", float(len(expected)), 0),
          "alternative-control (intuitive / later-treated) event-study coefficient files")


def _row(df, col, val):
    m = df[df[col].astype(str) == str(val)]
    return m.iloc[0] if len(m) else None


def derived_price_expert_concordance():
    """Price estimates from the HUMAN-EXPERT device-type-to-procedure concordance
    (the price footnote as settled by the author 2026-09-21: "52 treated device types",
    deregulation -0.18 (SE 0.07), down-regulation -0.09 (SE 0.03)).
    05_price_analysis.py now builds that concordance
    from data/raw/FDA_HCPCS_Xwalk_Moazzam.csv and writes its estimates with
    sample="Expert" (the preferred All-CPTs control construction)."""
    print("\n[price/expert] human-expert concordance robustness (manuscript fn to the price paragraph)")
    pu = _read(TABLES / "price_utilization_estimates.csv")
    targets = {"3_2": ("price_billedamt_expert_3_2", -0.09, 2,
                       "price_billedamt_expert_3_2_se", 0.03, 2),
               "2_1": ("price_billedamt_expert_2_1", -0.18, 2,
                       "price_billedamt_expert_2_1_se", 0.07, 2)}
    if pu is None:
        for rc, (n1, _t1, _d1, n2, _t2, _d2) in targets.items():
            record(n1, None, "pending", "price_utilization_estimates.csv absent")
            record(n2, None, "pending", "price_utilization_estimates.csv absent")
        return
    for rc, (n_est, t_est, d_est, n_se, t_se, d_se) in targets.items():
        row = pu[(pu["reclass_type"].astype(str) == rc)
                 & (pu["outcome"] == "BilledAmt")
                 & (pu["sample"].astype(str).str.strip() == "Expert")
                 & (pu["method"] == "BJS_imputation")]
        if not len(row):
            record(n_est, None, "pending", f"no Expert BilledAmt row for {rc}")
            record(n_se, None, "pending", f"no Expert BilledAmt row for {rc}")
            continue
        est = float(row["Estimate"].iloc[0])
        se = (float(row["upper_CI"].iloc[0]) - float(row["lower_CI"].iloc[0])) / (2 * 1.96)
        print(f"     {rc} Expert concordance: estimate {est:+.3f}, SE {se:.3f} "
              f"(manuscript {t_est:+g}, SE {t_se:g})")
        check(n_est, round(est, 4), ("printed", t_est, d_est),
              f"{rc} price estimate on the expert concordance")
        check(n_se, round(se, 4), ("printed", t_se, d_se),
              f"{rc} price standard error on the expert concordance")


def derived_price_sample_construction():
    """Price-data sample-construction counts stated in the data section: the 1998
    deregulation cohort (56 device types), the analytic claims panel (approximately
    17,400 procedure codes and 181,700 procedure-code-by-year observations), and the
    expert concordance's treated-device-type coverage (48). Emitted by
    05_price_analysis.emit_price_sample_construction_counts()."""
    print("\n[price/sample] price-data sample-construction counts (data section)")
    df = _read(TABLES / "price_sample_construction.csv")
    targets = {
        "devices_reclassified_1998_2_1": ("price_devices_1998_cohort", 56.0, 0),
        "analytic_procedure_codes": ("price_analytic_procedure_codes", 17400.0, -2),
        "analytic_proc_code_year_obs": ("price_analytic_proc_code_year_obs", 182200.0, -2),
        "expert_treated_device_types": ("price_expert_treated_device_types", 52.0, 0),
    }
    if df is None or "metric" not in df.columns:
        for name, _t, _d in targets.values():
            record(name, None, "pending", "price_sample_construction.csv absent (emitted by 05)")
        return
    for metric, (name, printed, decimals) in targets.items():
        r = _row(df, "metric", metric)
        if r is None:
            record(name, None, "pending", f"row {metric} absent")
            continue
        val = float(r["computed"])
        print(f"     {metric}: {val:g} (manuscript {printed:g})")
        check(name, val, ("printed", printed, decimals), metric)


# The manuscript's printed value for the case-study patent, in the paper's 2019-dollar convention
# (tex:203, "$760 million"): xi_real 295.66147 / CPI_DEFLATOR_2019 0.3891444 = 759.77.
MANUSCRIPT_CASE_STUDY_PATENT_VALUE_MILLIONS = 760


def derived_case_study_patent_value():
    """"One post-reclassification patent alone was valued at $... million (US-6478423-B1)" -- the contact-lens
    case study. The value is the Kogan et al. (2017) real patent value for that patent (xi_real, millions of
    1982 dollars, data/raw/KPSS_2019_public.csv) converted to 2019 dollars with the same deflator the rest
    of the paper uses (config.CPI_DEFLATOR_2019). On the simulated-data route the KPSS file is the
    fake-keyed twin, which does not contain the real patent number; the most valuable patent in the file
    stands in, so the lookup and the conversion are still exercised."""
    print("\n[case study] KPSS value of US-6478423-B1 in 2019 dollars")
    name = "case_study_patent_value_2019_millions"
    path = RAW / "KPSS_2019_public.csv"
    if not path.exists():
        _MISSING_INPUTS.append(str(path)); record(name, None, "pending", "KPSS_2019_public.csv absent"); return
    kp = pd.read_csv(path, usecols=["patent_num", "xi_real"])
    row = kp[kp["patent_num"].astype(str) == "6478423"]
    if len(row) == 0:
        if os.environ.get("FDA_INTEXT_ROUTE", "real") != "synthetic":
            record(name, None, "pending", "patent 6478423 not found in KPSS_2019_public.csv"); return
        row = kp.nlargest(1, "xi_real")
    sys.path.insert(0, str(ROOT))
    import config  # noqa: E402  (the deflator is defined once, in config.py)
    value = float(row["xi_real"].iloc[0]) / config.CPI_DEFLATOR_2019
    check(name, value, ("printed", MANUSCRIPT_CASE_STUDY_PATENT_VALUE_MILLIONS, -1),
          "KPSS xi_real / CPI_DEFLATOR_2019, millions of 2019 dollars")


def derived_spinal_entrant_audit():
    """Hand audit of new spinal-implant entrants quoted in the regulatory-proficiency footnote:
    "I sampled 20 new spinal-implant manufacturers ... Only one was a subsidiary ... median
    founding year = 2011, mean = 2011 ... only two of the 20 were acquired; 80% were U.S.-based".
    data/raw/spinal_entrant_audit.csv lists the 20 sampled 510(k) applicants (public FDA records,
    product code MAX, first submissions from 2007) with the four hand-coded attributes
    (US_based, subsidiary, acquired, founded). The statistics are tabulated here, never typed."""
    print("\n[spinal audit] 20 sampled spinal-implant entrants (manuscript: 1 subsidiary; median 2011, mean 2011; 2 acquired; 80% U.S.)")
    names = ("spinal_audit_n_firms", "spinal_audit_n_subsidiaries", "spinal_audit_founded_median",
             "spinal_audit_founded_mean", "spinal_audit_n_acquired", "spinal_audit_us_based_pct")
    path = RAW / "spinal_entrant_audit.csv"
    if not path.exists():
        _MISSING_INPUTS.append(str(path))
        for n in names:
            record(n, None, "pending", "data/raw/spinal_entrant_audit.csv absent")
        return
    df = pd.read_csv(path)
    check(names[0], float(len(df)), ("printed", 20, 0), "sampled entrants")
    check(names[1], float(df["subsidiary"].fillna(0).sum()), ("printed", 1, 0), "entrants that are subsidiaries")
    check(names[2], float(df["founded"].median()), ("printed", 2011, 0), "median founding year (firms with a recorded year)")
    check(names[3], float(df["founded"].mean()), ("printed", 2011, 0), "mean founding year (firms with a recorded year)")
    check(names[4], float(df["acquired"].fillna(0).sum()), ("printed", 2, 0), "entrants later acquired")
    check(names[5], float(100.0 * df["US_based"].mean()), ("printed", 80, 0), "share of entrants that are U.S.-based, percent")


def derived_class_structure():
    """FDA device-class structure quoted in the regulatory-background appendix and
    the data section: about 41% of product codes are Class I and roughly 90% of
    those are 510(k)-exempt; about 56% are Class II; roughly 2% are Class III; and
    the universe is "over 5,000 FDA-defined device types". All four are computed
    here from the SAME public classification file the cost-benefit block already
    opens (RegNum_Factorized_Synth.csv, one row per product code)."""
    print("\n[classes] FDA device-class shares (manuscript: 41% / 90% / 56% / 2%; >5,000 types)")
    names = ("class_I_share_pct", "class_I_exempt_share_pct", "class_II_share_pct",
             "class_III_share_pct", "fda_device_types")
    path = next((c for c in (DERIVED / "RegNum_Factorized_Synth.csv",
                             RAW / "RegNum_Factorized_Synth.csv") if c.exists()), None)
    if path is None:
        rel = "data/derived/RegNum_Factorized_Synth.csv"
        print(f"  [skip] missing input: {rel}")
        _MISSING_INPUTS.append(rel)
        for n in names:
            record(n, None, "pending", "RegNum_Factorized_Synth.csv absent")
        return
    sn = pd.read_csv(path, dtype=str, low_memory=False).drop_duplicates("PRODUCTCODE_x")
    total = int(sn["PRODUCTCODE_x"].nunique())
    cls = sn["DEVICECLASS"].astype(str).str.strip()
    n1 = int((cls == "1").sum())
    n2 = int((cls == "2").sum())
    n3 = int((cls == "3").sum())
    exempt1 = int(((cls == "1") & (sn["SUBMISSION_TYPE_ID"].astype(str).str.strip()
                                   == "510(K) Exempt")).sum())
    print(f"     {total} product codes; Class I {n1}, Class II {n2}, Class III {n3}; "
          f"510(k)-exempt Class I {exempt1}")
    check("class_I_share_pct", round(100.0 * n1 / total, 2), ("printed", 41.0, 0),
          "share of product codes that are Class I")
    check("class_I_exempt_share_pct", round(100.0 * exempt1 / n1, 2), ("printed", 90.0, -1),
          "share of Class I product codes exempt from premarket submission "
          "(manuscript 'roughly 90%', one significant figure)")
    check("class_II_share_pct", round(100.0 * n2 / total, 2), ("printed", 56.0, 0),
          "share of product codes that are Class II")
    check("class_III_share_pct", round(100.0 * n3 / total, 2), ("printed", 2.0, 0),
          "share of product codes that are Class III (manuscript 'roughly 2%')")
    check("fda_device_types", total, ("gt", 5000), "FDA-defined device types ('over 5,000')")


def derived_maude_universe():
    """MAUDE universe statements in the data section: the database "contains roughly
    9.7 million device-related reports", and the firm-size analysis "hand-link[s] the
    top 300 MAUDE-reporting manufacturers to CRSP/Compustat".

    The report count is the number of data rows in the MAUDE master event extract the
    pipeline reads (data/raw/MAUDE/masterevent.txt, read by
    code/00_generate_data/gen_01_main_panels.py). It is counted by streaming the file,
    never by loading it.

    The firm-size sentence was reconciled with the code on 2026-09-22. It now reads
    "working down the report-count ranking: the 300 largest reporters account for 84
    percent of all reports, of which 88 are private firms with no public-firm match and
    the remainder are linked by automated name clustering with hand-coded corrections",
    and all three printed values are emitted by
    code/modules/manufacturer_linkage_coverage.py (which gen_07 writes to
    output/tables/manufacturer_linkage_coverage.csv). The 70 rows of
    manual_permno_corrections.csv are substring patterns, not firms -- they are reported
    here as a diagnostic and are not compared against the manuscript's 300.
    """
    print("\n[MAUDE] adverse-event universe (manuscript: ~9.2 million reports; the top 300\n"
          "        reporters, 84% of reports, 88 of them private)")
    master = RAW / "MAUDE" / "masterevent.txt"
    if master.exists():
        n_rows = 0
        with open(master, "rb") as fh:
            for _ in fh:
                n_rows += 1
        n_rows = max(n_rows - 1, 0)   # drop the header line
        millions = n_rows / 1e6
        print(f"     masterevent.txt: {n_rows:,} data rows = {millions:.3f} million reports")
        check("maude_reports_millions", round(millions, 3), ("printed", 9.2, 1),
              "MAUDE device-related reports, in millions (rows of data/raw/MAUDE/masterevent.txt)")
    else:
        print("  [skip] missing input: data/raw/MAUDE/masterevent.txt")
        _MISSING_INPUTS.append("data/raw/MAUDE/masterevent.txt")
        record("maude_reports_millions", None, "pending", "masterevent.txt absent (restricted input)")

    # --- the top-300 report-count ranking behind the firm-size sentence -------------
    # Preferred source: the table gen_07 emits. If a route ran with --skip-gen, rebuild it
    # here from the same two inputs rather than reporting "pending" -- same module, same
    # numbers (code/modules/manufacturer_linkage_coverage.py).
    cov_path = TABLES / "manufacturer_linkage_coverage.csv"
    # The table is OPTIONAL here: on a --skip-gen route gen_07 has not run and the module rebuilds the
    # same numbers from the events file, so its absence is not a missing input (2026-10-03: registering
    # it as one made the strict gate fail on the analysis-only real route although 118/118 numbers
    # agreed). Only the absence of BOTH sources is a missing input.
    cov = pd.read_csv(cov_path) if cov_path.exists() else None
    if cov is None:
        events = DERIVED / "all_adv_events_w_permno5.csv"
        if events.exists():
            sys.path.insert(0, str(ROOT / "code" / "modules"))
            from manufacturer_linkage_coverage import write_coverage  # noqa: E402
            print(f"     {cov_path.name} absent; rebuilding from {events.name} "
                  "(gen_07 writes it on a full run) and writing it to output/tables/ -- the same module and "
                  "the same numbers, so the analysis-only route produces every inventory table")
            write_coverage(ROOT, events, quiet=True)
            cov = pd.read_csv(cov_path)
        else:
            print(f"  [skip] missing input: {cov_path.relative_to(ROOT)} (and {events.relative_to(ROOT)})")
            _MISSING_INPUTS.append(str(events.relative_to(ROOT)))
    printed = {"top_n": ("maude_top_n_reporters", 300.0, 0,
                         "rank cut worked down the MAUDE report-count ranking"),
               "top_n_report_share_pct": ("maude_top_n_report_share_pct", 84.0, 0,
                                          "share of all MAUDE reports held by the top 300 names"),
               "top_n_unlinked": ("maude_top_n_unlinked", 88.0, 0,
                                  "of the top 300, names with no public-firm match (private firms)")}
    if cov is not None:
        vals = dict(zip(cov["metric"].astype(str), cov["value"]))
        for metric, (name, target, dec, desc) in printed.items():
            if metric in vals and str(vals[metric]) not in ("", "nan"):
                check(name, float(vals[metric]), ("printed", target, dec), desc)
            else:
                record(name, None, "pending", f"{metric} absent from {cov_path.name}")
        n_lines = vals.get("hand_coded_lines", "")
        covered = vals.get("top_n_names_covered_by_lines", "")
        if str(n_lines) not in ("", "nan"):
            print(f"     [diagnostic] {n_lines} hand-coded substring patterns reach {covered} "
                  "of the top 300 names; patterns are not firms, so they are NOT compared "
                  "against the manuscript's 300")
    else:
        for name, _t, _d, _desc in printed.values():
            record(name, None, "pending",
                   "manufacturer_linkage_coverage.csv and all_adv_events_w_permno5.csv absent")


def derived_patent_universe():
    """Patent-collection universe counts (data section and the patent-collection
    robustness appendix): "over 1.2 million medical device patents from 1976-2019";
    875,324 keyword-linked patents in 1996-2015; 171,682 A61-non-drug patents; and
    302,140 GPT-4o-identified device patents. Emitted by
    13_restricted_samples.emit_patent_collection_counts()."""
    print("\n[patents] patent-collection universe counts")
    df = _read(TABLES / "PatentCollectionCounts.csv")
    targets = {
        "keyword_linked_patents_1976_2019": ("patent_universe_1976_2019", ("gt", 1_200_000)),
        "keyword_linked_patents_1996_2015": ("patent_universe_keyword", ("printed", 875324.0, 0)),
        "a61_nondrug_patents_1996_2015": ("patent_universe_a61_nodrug", ("printed", 171682.0, 0)),
        "gpt4o_device_utility_patents_1996_2015": ("patent_universe_gpt4o", ("printed", 302140.0, 0)),
    }
    if df is None or "metric" not in df.columns:
        for name, _rel in targets.values():
            record(name, None, "pending", "PatentCollectionCounts.csv absent (emitted by 13 on the run)")
        return
    for metric, (name, rel) in targets.items():
        r = _row(df, "metric", metric)
        if r is None or pd.isna(r["computed_count"]):
            record(name, None, "pending", f"row {metric} absent or NaN")
            continue
        val = int(float(r["computed_count"]))
        print(f"     {metric}: {val:,}")
        check(name, val, rel, metric)


def derived_safety_term_share():
    """The safety-measure appendix states "only about two percent of patents include
    such terms". Emitted by 06b_validate_safety.emit_safety_term_share() from the
    per-patent keyword flags."""
    print("\n[safety terms] share of patents containing a safety keyword (manuscript: ~2%)")
    df = _read(TABLES / "safety_term_share.csv")
    if df is None or "metric" not in df.columns:
        record("safety_term_share_pct", None, "pending",
               "safety_term_share.csv absent (emitted by 06b on the run)")
        return
    r = _row(df, "metric", "safety_term_share_pct")
    if r is None:
        record("safety_term_share_pct", None, "pending", "safety_term_share_pct row absent")
        return
    val = float(r["computed"])
    print(f"     {val:.4f}% of {int(r['n_patents']):,} patents")
    check("safety_term_share_pct", round(val, 4), ("printed", 2.0, 0),
          "share of patents whose title or abstract contains a safety keyword")


def derived_dpm_decile():
    """The regulation-design appendix states that "top-decile device types have
    roughly four times the proxy score of the 89th-percentile type". Emitted by
    11d_reg_design.emit_dpm_decile_ratio()."""
    print("\n[DPM] proxy Device Priority Model decile ratio (manuscript: roughly four times)")
    df = _read(TABLES / "dpm_decile_ratio.csv")
    if df is None or "metric" not in df.columns:
        record("dpm_top_decile_ratio", None, "pending",
               "dpm_decile_ratio.csv absent (emitted by 11d on the run)")
        return
    r = _row(df, "metric", "dpm_top_decile_ratio")
    if r is None:
        record("dpm_top_decile_ratio", None, "pending", "dpm_top_decile_ratio row absent")
        return
    val = float(r["computed"])
    print(f"     top-decile mean / 89th-percentile score = {val:.3f}x")
    check("dpm_top_decile_ratio", round(val, 3), ("printed", 4.0, 0),
          "top-decile proxy DPM relative to the 89th-percentile device type")


def derived_recall_numbers():
    """Recall paragraph: "The decline of about 0.5 recalls per device-type-year
    represents roughly a 50 percent reduction relative to the control mean", and
    "More than 200 Class II device types were reclassified in 2015". Emitted by
    11b_recall_analysis.emit_recall_in_text_numbers()."""
    print("\n[recalls] recall decline and 2015 cohort size")
    df = _read(TABLES / "recall_in_text_numbers.csv")
    targets = {
        "recall_decline_per_device_type_year": ("recall_decline_per_device_type_year",
                                                ("printed", -0.45, 2)),
        "recall_decline_pct_of_control_mean": ("recall_decline_pct", ("printed", 50.0, -1)),
        "class2_device_types_2015": ("class2_device_types_2015", ("gt", 200)),
    }
    if df is None or "metric" not in df.columns:
        for name, _rel in targets.values():
            record(name, None, "pending",
                   "recall_in_text_numbers.csv absent (emitted by 11b on the run)")
        return
    for metric, (name, rel) in targets.items():
        r = _row(df, "metric", metric)
        if r is None:
            record(name, None, "pending", f"row {metric} absent")
            continue
        val = float(r["computed"])
        print(f"     {metric}: {val:g}")
        check(name, round(val, 4), rel, metric)


def derived_new_entry_2015():
    """The 2015-event paragraph: new-entrant patenting "rises by roughly 39% within
    two years (base 11.9 entrants/yr), versus a statistically insignificant 13.7%
    rise within two years after the 1996/8 events", and its footnote: "The 2015 event
    adds about five new firms per year relative to pre-event means; the 1996/8 events
    add about one." The 2015 numbers come from 11e_new_entry_2015.py's new CSV; the
    1996/8 comparison is the matched-control new-entry event study's two-year
    coefficient over its own pre-event base rate (both already emitted by 04)."""
    print("\n[2015 entry] new-entrant patenting, 2015 event vs the 1996/8 events")
    df = _read(TABLES / "new_entry_2015_in_text.csv")
    targets = {
        "new_entry_2015_baseline_firms_per_yr": ("new_entry_2015_baseline_firms_per_yr",
                                                 ("printed", 11.9, 1)),
        "new_entry_2015_effect_2yr": ("new_entry_2015_effect_2yr", ("printed", 5.0, 0)),
        "new_entry_2015_pct_2yr": ("new_entry_2015_pct_2yr", ("printed", 39.0, 0)),
    }
    if df is None or "metric" not in df.columns:
        for name, _rel in targets.values():
            record(name, None, "pending",
                   "new_entry_2015_in_text.csv absent (emitted by 11e on the run)")
    else:
        for metric, (name, rel) in targets.items():
            r = _row(df, "metric", metric)
            if r is None:
                record(name, None, "pending", f"row {metric} absent")
                continue
            val = float(r["computed"])
            print(f"     {metric}: {val:g}")
            check(name, round(val, 4), rel, metric)

    # 1996/8 comparison: the same two-year horizon on the matched-control new-entry
    # event study (unique_firms = new-firm patenting), over its own pre-event base
    # rate -- the established "% more" convention used throughout this script.
    es = TABLES / "event_study_coefficients" / "ES_coefs_2_1_unique_firms.csv"
    br = _read(TABLES / "event_study_base_rates.csv")
    if not es.exists() or br is None:
        if not es.exists():
            print("  [skip] missing input: output/tables/event_study_coefficients/"
                  "ES_coefs_2_1_unique_firms.csv")
            _MISSING_INPUTS.append(
                "output/tables/event_study_coefficients/ES_coefs_2_1_unique_firms.csv")
        record("new_entry_1996_8_effect_2yr", None, "pending", "ES coefficients or base rates absent")
        record("new_entry_1996_8_pct_2yr", None, "pending", "ES coefficients or base rates absent")
        return
    coefs = pd.read_csv(es)
    row = coefs[coefs["ET"] == 2]
    base_row = br[br["figure_file"] == "2_1_nolog_unique_firms_oct22_24.png"]
    if not len(row) or not len(base_row):
        record("new_entry_1996_8_effect_2yr", None, "pending", "ET=2 row or base rate absent")
        record("new_entry_1996_8_pct_2yr", None, "pending", "ET=2 row or base rate absent")
        return
    eff = float(row["Effect"].iloc[0])
    base = float(base_row["base_rate"].iloc[0])
    pct = eff / base * 100.0
    print(f"     1996/8 events, two years out: effect {eff:.3f} firms/yr over a "
          f"{base:.3f} base = {pct:.1f}%")
    check("new_entry_1996_8_effect_2yr", round(eff, 4), ("printed", 1.0, 0),
          "1996/8 new-firm entry effect two years out ('about one' firm per year)")
    check("new_entry_1996_8_pct_2yr", round(pct, 2), ("printed", 13.0, 1),
          "1996/8 new-firm entry effect as a percentage of its pre-event base rate")


def derived_maturity_slope_precision():
    """The Section 6 maturity-gradient footnote prints a standard error and a p-value
    beside each of the four age slopes, and the accompanying text gives the number of
    down-regulated device types (N = 25). The slopes were registered; their precision
    and the N were not. All are in 11d's maturity_gradient_slopes.csv."""
    print("\n[#7c] Maturity-gradient standard errors, p-values and N (Section 6 footnote)")
    df = _read(TABLES / "maturity_gradient_slopes.csv")
    targets = {
        ("3_2", "v_serious_est"): ("maturity_slope_serious_3_2_se", 0.008, 3,
                                   "maturity_slope_serious_3_2_p", 0.060, 3),
        ("3_2", "patent_est"): ("maturity_slope_patent_3_2_se", 0.013, 3,
                                "maturity_slope_patent_3_2_p", 0.008, 3),
        ("2_1", "v_serious_est"): ("maturity_slope_serious_2_1_se", 0.001, 3,
                                   "maturity_slope_serious_2_1_p", 0.218, 3),
        ("2_1", "patent_est"): ("maturity_slope_patent_2_1_se", 0.001, 3,
                                "maturity_slope_patent_2_1_p", 0.876, 3),
    }
    if df is None:
        for (_rc, _oc), (n_se, _a, _b, n_p, _c, _d) in targets.items():
            record(n_se, None, "pending", "maturity_gradient_slopes.csv absent")
            record(n_p, None, "pending", "maturity_gradient_slopes.csv absent")
        record("maturity_gradient_n", None, "pending", "maturity_gradient_slopes.csv absent")
        return
    for (rc, oc), (n_se, t_se, d_se, n_p, t_p, d_p) in targets.items():
        row = df[(df.reclass_type.astype(str) == rc) & (df.outcome == oc)]
        if not len(row):
            record(n_se, None, "pending", f"no {rc}/{oc} row")
            record(n_p, None, "pending", f"no {rc}/{oc} row")
            continue
        se = float(row["se"].iloc[0])
        pv = float(row["pvalue"].iloc[0])
        print(f"     {rc}/{oc}: SE={se:.4f} (printed {t_se:g}), p={pv:.4f} (printed {t_p:g})")
        check(n_se, round(se, 6), ("printed", t_se, d_se), f"{rc}/{oc} age-slope standard error")
        check(n_p, round(pv, 6), ("printed", t_p, d_p), f"{rc}/{oc} age-slope p-value")
    row = df[(df.reclass_type.astype(str) == "3_2") & (df.outcome == "v_serious_est")]
    if len(row):
        n = int(row["n"].iloc[0])
        print(f"     down-regulated device types in the maturity gradient: N = {n}")
        check("maturity_gradient_n", n, ("printed", 25.0, 0),
              "down-regulated device types in the maturity-gradient sample (N = 25)")
    else:
        record("maturity_gradient_n", None, "pending", "no 3_2/v_serious_est row")


def derived_cost_benefit_did():
    """The cost-benefit footnote states "The point estimate is roughly $118 million"
    for the total-patent-value DiD before the 20% retention adjustment. Only the
    retained product was registered."""
    print("\n[#6b] Total-patent-value DiD point estimate (manuscript: ~$118 million)")
    df = _read(TABLES / "cost_benefit_total_value_did.csv")
    if df is None or "reclass_type" not in df.columns:
        record("cost_benefit_did_effect_M", None, "pending",
               "cost_benefit_total_value_did.csv absent")
        return
    row = df[df.reclass_type.astype(str) == "2_1"]
    if not len(row):
        record("cost_benefit_did_effect_M", None, "pending", "no 2_1 row")
        return
    val = float(row["did_effect_2019M"].iloc[0])
    print(f"     II->I total-value DiD = ${val:.3f}M per device type-year")
    check("cost_benefit_did_effect_M", round(val, 3), ("printed", 118.0, 0),
          "II->I total-patent-value DiD point estimate, 2019 $M")


def derived_adverse_event_levels():
    """The cost-benefit footnote states that "hospitalizations fall by 1.8 per year
    and deaths by 0.4" after deregulation. Both are matched-control level estimates
    already written by the estimation step."""
    print("\n[#6c] Adverse-event level effects (manuscript: 1.8 hospitalizations, 0.4 deaths per year)")
    adv = _read(TABLES / "PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv")
    if adv is None:
        record("adverse_hosp_per_yr_2_1", None, "pending", "adverse-event estimates absent")
        record("adverse_death_per_yr_2_1", None, "pending", "adverse-event estimates absent")
        return
    for outcome, name, printed in (("H", "adverse_hosp_per_yr_2_1", -1.8),
                                   ("D", "adverse_death_per_yr_2_1", -0.4)):
        row = adv[adv.outcome == outcome]
        if not len(row):
            record(name, None, "pending", f"no {outcome} row")
            continue
        val = float(row["Estimate"].iloc[0])
        print(f"     {outcome}: {val:+.3f} per year (manuscript {printed:+g})")
        check(name, round(val, 4), ("printed", printed, 1), f"II->I {outcome} level effect per year")


def derived_restricted_sample_shares():
    """The patent-collection robustness appendix states that on the GPT-4o-identified
    device sample "the absolute effect is about two-thirds of baseline", the residual
    "roughly one-third" being spillovers to patents outside that definition. Both are
    ratios of two shipped estimates."""
    print("\n[restricted] GPT-4o device-patent effect as a share of the baseline effect")
    rs = _read(TABLES / "RestrictedSamples_estimates.csv")
    mp = _read(TABLES / "PaperMainPanel_3_2_Estimates_NoLog_xi_latest_oct22_24.csv")
    if rs is None or mp is None:
        record("restricted_gpt4o_share", None, "pending", "restricted or main-panel estimates absent")
        record("restricted_spillover_share", None, "pending", "restricted or main-panel estimates absent")
        return
    row = rs[(rs["outcome"] == "real_pats_dev_gpt4o") & (rs["reclass_type"].astype(str) == "3_2")]
    base = mp[mp["outcome"] == "real_pats"]
    if not len(row) or not len(base):
        record("restricted_gpt4o_share", None, "pending", "GPT-4o or baseline row absent")
        record("restricted_spillover_share", None, "pending", "GPT-4o or baseline row absent")
        return
    share = float(row["Estimate"].iloc[0]) / float(base["Estimate"].iloc[0])
    print(f"     GPT-4o device patents {float(row['Estimate'].iloc[0]):.3f} / baseline "
          f"{float(base['Estimate'].iloc[0]):.3f} = {share:.3f}")
    check("restricted_gpt4o_share", round(share, 4), ("printed", 2.0 / 3.0, 2),
          "GPT-4o device-patent effect as a share of the baseline effect ('about two-thirds')")
    check("restricted_spillover_share", round(1.0 - share, 4), ("printed", 1.0 / 3.0, 2),
          "residual share attributed to spillovers ('roughly one-third')")


def derived_price_coverage_counts():
    """The data section states the price/utilization analysis is "feasible for 15
    deregulated device types" and "3 of the 12 down-regulated device types". Both are
    in 05's d1_price_coverage.csv (and are the cells Table D.1 Panel B prints)."""
    print("\n[coverage] price/utilization device-type coverage (manuscript: 15 and 3)")
    df = _read(TABLES / "d1_price_coverage.csv")
    if df is None or "reclass_type" not in df.columns:
        record("price_coverage_2_1", None, "pending", "d1_price_coverage.csv absent")
        record("price_coverage_3_2", None, "pending", "d1_price_coverage.csv absent")
        return
    for rc, name, printed in (("2_1", "price_coverage_2_1", 15.0),
                              ("3_2", "price_coverage_3_2", 3.0)):
        r = _row(df, "reclass_type", rc)
        if r is None:
            record(name, None, "pending", f"no {rc} row")
            continue
        val = int(r["n_covered"])
        print(f"     {rc}: {val} device types covered")
        check(name, val, ("printed", printed, 0), f"{rc} price/utilization device-type coverage")


def derived_lbd_tercile_pcts():
    """The learning-by-doing paragraph states that "least-experienced firms exhibit
    roughly a 280% increase, compared with about 65% for the most experienced".
    Both are the k_pct column of 08_lbd_simulation.py's tercile table."""
    print("\n[LBD] regulatory-proficiency terciles (manuscript: 280% and 65%)")
    df = _read(TABLES / "lbd_tercile_estimation.csv")
    if df is None or "tercile" not in df.columns:
        record("lbd_pct_first_tercile", None, "pending", "lbd_tercile_estimation.csv absent")
        record("lbd_pct_third_tercile", None, "pending", "lbd_tercile_estimation.csv absent")
        return
    for tercile, name, printed, decimals in (("First", "lbd_pct_first_tercile", 280.0, -1),
                                             ("Third", "lbd_pct_third_tercile", 65.0, 0)):
        r = _row(df, "tercile", tercile)
        if r is None:
            record(name, None, "pending", f"no {tercile} tercile row")
            continue
        val = float(r["k_pct"])
        print(f"     {tercile} tercile: {val:.2f}% (manuscript {printed:g}%)")
        check(name, round(val, 3), ("printed", printed, decimals),
              f"{tercile}-tercile regulatory-proficiency increase")


def derived_safety_emphasis_pct():
    """The Results state that "the probability that any patent emphasizes safety
    increases by about 80%". That is the II->I safety DiD estimate over its own
    pre-event mean, the two cells of the program-generated table row
    output/tables/Formatted/PaperRegTableSafety_IItoI_NoLog.tex (written by
    06a_safety_analysis.py). The division was done only in prose."""
    print("\n[safety] safety-emphasis increase over the pre-event mean (manuscript: ~80%)")
    path = TABLES / "Formatted" / "PaperRegTableSafety_IItoI_NoLog.tex"
    if not path.exists():
        rel = path.relative_to(ROOT)
        print(f"  [skip] missing input: {rel}")
        _MISSING_INPUTS.append(str(rel))
        record("safety_emphasis_pct_2_1", None, "pending",
               "PaperRegTableSafety_IItoI_NoLog.tex absent")
        return
    import re as _re
    txt = path.read_text()
    nums = _re.findall(r"(-?\d+\.\d+)", txt.split("\\\\")[0])
    if len(nums) < 2:
        record("safety_emphasis_pct_2_1", None, "pending",
               "could not parse the pre-mean and estimate from the table row")
        return
    pre_mean, est = float(nums[0]), float(nums[1])
    pct = est / pre_mean * 100.0 if pre_mean else float("nan")
    print(f"     estimate {est:g} over pre-mean {pre_mean:g} = {pct:.1f}%")
    check("safety_emphasis_pct_2_1", round(pct, 2), ("printed", 80.0, -1),
          "II->I safety-emphasis increase relative to the pre-event mean")


def derived_breakthrough_pct_zero():
    """The breakthrough-patent appendix states the device-type-year panel is
    "approximately 81% zeros". The distribution CSV already carried the column; it was
    the one moment of it that was never registered."""
    print("\n[breakthrough] III->II panel zero share (manuscript: ~81%)")
    df = _read(TABLES / "BreakthroughPanel_distribution.csv")
    if df is None or "panel" not in df.columns:
        record("breakthrough_panel_pct_zero", None, "pending",
               "BreakthroughPanel_distribution.csv absent (emitted by 14 on the run)")
        return
    r = _row_where(df, "panel", "3_2")
    if r is None:
        record("breakthrough_panel_pct_zero", None, "pending", "3_2 panel row absent")
        return
    val = float(r["pct_zero"])
    print(f"     {val:.2f}% of device-type-years are zero")
    check("breakthrough_panel_pct_zero", round(val, 2), ("printed", 81.0, 0),
          "share of zeros in the III->II breakthrough device-type-year panel")


def derived_sample_construction_counts():
    """Table D.1's treated-sample construction cells that the text repeats: 29 III->II
    reclassifications after excluding atypical cases, 12 FDA-initiated, and therefore
    17 petition-driven. 10c_generate_appendix_tables.py generates the table from
    documented constants; these register the three cells the prose quotes."""
    print("\n[D.1] treated-sample construction counts (manuscript: 29, 12, 17)")
    path = TABLES / "Formatted" / "TableD1_SampleConstruction.tex"
    names = ("sample_construction_reclass_total", "sample_construction_fda_initiated",
             "sample_construction_petitioned")
    if not path.exists():
        rel = path.relative_to(ROOT)
        print(f"  [skip] missing input: {rel}")
        _MISSING_INPUTS.append(str(rel))
        for n in names:
            record(n, None, "pending", "TableD1_SampleConstruction.tex absent")
        return
    import re as _re
    txt = path.read_text()

    def _cell(label):
        m = _re.search(_re.escape(label) + r"[^&]*&\s*(\d+)\s*&", txt)
        return int(m.group(1)) if m else None

    total = _cell("Excluding atypical reclassifications")
    fda = _cell("FDA-initiated only")
    if total is None or fda is None:
        for n in names:
            record(n, None, "pending", "could not parse the Table D.1 construction cells")
        return
    print(f"     excluding atypical: {total}; FDA-initiated: {fda}; petition-driven: {total - fda}")
    check("sample_construction_reclass_total", total, ("printed", 29.0, 0),
          "III->II reclassifications excluding atypical cases")
    check("sample_construction_fda_initiated", fda, ("printed", 12.0, 0),
          "FDA-initiated III->II reclassifications")
    check("sample_construction_petitioned", total - fda, ("printed", 17.0, 0),
          "petition-driven III->II reclassifications (29 - 12)")


def derived_safety_percentile_robustness():
    """The safety-robustness appendix states "Using the 99th similarity percentile as
    the threshold (results are similar at the 95th)". 06c now re-thresholds the stored
    per-patent similarities and re-estimates at both, so the parenthetical has a
    producing program. The 99th-percentile rows must reproduce the reported estimates
    (that is the check); the 95th-percentile rows are recorded so the comparison the
    sentence makes is machine-readable."""
    print("\n[safety/pct] embedding-distance estimates at the 99th and 95th percentiles")
    df = _read(TABLES / "safety_embedding_percentile_robustness.csv")
    names = ("safety_embed_p99_2_1", "safety_embed_p95_2_1",
             "safety_embed_p99_3_2", "safety_embed_p95_3_2")
    if df is None or "similarity_percentile" not in df.columns:
        for n in names:
            record(n, None, "pending",
                   "safety_embedding_percentile_robustness.csv absent (emitted by 06c on the run)")
        return
    reported = _read(TABLES / "safety_embedding_distance_estimates.csv")
    for pct, rc, name in ((0.99, "2_1", "safety_embed_p99_2_1"),
                          (0.95, "2_1", "safety_embed_p95_2_1"),
                          (0.99, "3_2", "safety_embed_p99_3_2"),
                          (0.95, "3_2", "safety_embed_p95_3_2")):
        row = df[(df["similarity_percentile"].astype(float) == pct)
                 & (df["reclass_type"].astype(str) == rc)]
        if not len(row):
            record(name, None, "pending", f"no p{pct * 100:g} / {rc} row")
            continue
        est = float(row["estimate"].iloc[0])
        if pct == 0.99 and reported is not None:
            rep = reported[reported.reclass_type.astype(str) == rc]
            target = float(rep["estimate"].iloc[0]) if len(rep) else None
            if target is None:
                record(name, round(est, 4), "pending", "no reported estimate to compare against")
                continue
            print(f"     p99 {rc}: {est:+.3f} (reported table value {target:+.3f})")
            check(name, round(est, 4), ("printed", target, 3),
                  f"{rc} embedding-distance estimate at the reported 99th percentile")
        else:
            # The manuscript's claim about the 95th percentile is qualitative, so what
            # is gated is the CONCLUSION the appendix draws from the table, not a
            # magnitude: a post-Class-II-to-I increase (positive and significant), and
            # "no robust increase" for Class III to II (a confidence interval that
            # contains zero, or a non-positive estimate).
            lo = float(row["ci_lower"].iloc[0])
            hi = float(row["ci_upper"].iloc[0])
            print(f"     p95 {rc}: {est:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            if rc == "2_1":
                ok = est > 0 and lo > 0
                claim = "a significant post-reclassification increase"
            else:
                ok = (est <= 0) or (lo <= 0 <= hi)
                claim = "no robust increase"
            if ok:
                record(name, round(est, 4), "ok",
                       f"95th-percentile estimate {est:+.3f} [{lo:+.3f}, {hi:+.3f}] still shows "
                       f"{claim}, as the manuscript states for the reported 99th percentile")
            else:
                record(name, round(est, 4), "outside_manuscript",
                       f"95th-percentile estimate {est:+.3f} [{lo:+.3f}, {hi:+.3f}] does NOT show "
                       f"{claim}; the manuscript says results are similar at the 95th percentile")


def main():
    print("=" * 70)
    print("In-text derived numbers — reproduction from pipeline outputs")
    print("=" * 70)
    derived_safety_by_asset()        # #4
    derived_cost_benefit()           # #6
    derived_safety_pct_reductions()  # #2 (method + status)
    derived_exp_crossings()          # #7 (~30/~63-year market-age crossings)
    derived_maturity_slopes()        # #7b (Section 6 footnote age slopes)
    derived_headline_innovation()    # headline innovation magnitudes (L210/L387)
    derived_headline_market_price()  # headline market-composition + price magnitudes (L212/L406)
    derived_invention_year_validation()  # GPT-vs-hand invention-year r=0.76 (L500/L1795/L2508)
    derived_case_study_ratios()          # contact-lens case-study ratios (L203)
    derived_breakthrough_distribution()  # III->II breakthrough panel distribution (L1724)
    # --- JPE 2.2 completeness batch: every remaining numeric manuscript claim ---
    derived_event_study_base_rates()     # the twelve printed figure overlays + captions
    derived_alt_control_event_studies()  # the "not shown" intuitive / later-treated ES
    derived_price_expert_concordance()   # human-expert concordance price robustness
    derived_price_sample_construction()  # 56 device types / ~17,400 codes / ~181,700 obs
    derived_class_structure()            # 41% / 90% / 56% / 2% class shares; >5,000 types
    derived_spinal_entrant_audit()       # 20 sampled spinal-implant entrants (proficiency footnote)
    derived_case_study_patent_value()    # KPSS value of the case-study patent, 2019 dollars
    derived_maude_universe()             # ~9.7M MAUDE reports; hand-linked manufacturers
    derived_patent_universe()            # 1.2M (1976-2019) + the three 1996-2015 universes
    derived_safety_term_share()          # ~2% of patents contain a safety term
    derived_dpm_decile()                 # top-decile proxy DPM ~4x the 89th percentile
    derived_recall_numbers()             # recall decline 0.5 / 50%; >200 device types in 2015
    derived_new_entry_2015()             # 11.9 base, ~5 firms/yr, 39%; 1996/8 comparison
    derived_maturity_slope_precision()   # the footnote SEs, p-values and N = 25
    derived_cost_benefit_did()           # the ~$118M total-value DiD point estimate
    derived_adverse_event_levels()       # 1.8 hospitalizations / 0.4 deaths per year
    derived_restricted_sample_shares()   # two-thirds / one-third decomposition
    derived_price_coverage_counts()      # 15 and 3 device types with price coverage
    derived_lbd_tercile_pcts()           # 280% / 65% regulatory-proficiency terciles
    derived_safety_emphasis_pct()        # the ~80% safety-emphasis increase
    derived_breakthrough_pct_zero()      # ~81% zeros in the breakthrough panel

    # JPE 2.2: program-generate the appendix computational tables (D.15/D.11/D.1) from these same
    # outputs, so every computational exhibit is program-generated. Loaded by path (module name starts with a
    # digit). In strict mode a generation failure is fatal (the exhibit would otherwise be missing).
    #
    # THIS MUST RUN BEFORE derived_sample_construction_counts(), which READS the Table D.1 fragment
    # this block writes.
    appendix_ok = True
    try:
        import importlib.util
        _p = Path(__file__).resolve().parent / "10c_generate_appendix_tables.py"
        _spec = importlib.util.spec_from_file_location("gen_appendix_tables", _p)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        # 10c is FAIL-CLOSED: it RETURNS nonzero (does not raise) when a required table is not
        # generated. Check the return code, not just exceptions, or a partial generation reads as OK.
        _rc = _mod.main()
        if _rc:
            appendix_ok = False
            print(f"  [FATAL] appendix-table generation returned nonzero ({_rc}) — a required table was not produced")
    except Exception as e:  # noqa: BLE001
        appendix_ok = False
        print(f"  [FATAL] appendix-table generation raised: {type(e).__name__}: {e}")

    derived_sample_construction_counts()  # Table D.1's 29 / 12 / 17 (reads the fragment just written)
    derived_safety_percentile_robustness()  # the 99th vs 95th similarity threshold

    # COMPLETENESS: any expected name that was never registered is an omission -> record it pending.
    recorded = {r["name"] for r in INTEXT_REPORT}
    for missing_name in sorted(EXPECTED_INTEXT_NAMES - recorded):
        record(missing_name, None, "pending", "NOT REGISTERED (omitted by its function)")

    # Machine-readable report of every registered in-text number (name, value, status).
    report_path = TABLES / "intext_numbers_report.csv"
    try:
        with open(report_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["name", "value", "status", "note"])
            for r in INTEXT_REPORT:
                w.writerow([r["name"], r["value"], r["status"], r["note"]])
        print(f"\nIn-text-number report -> {report_path}")
    except OSError as e:
        print(f"\nFATAL: could not write in-text-number report: {e}")
        return 1

    n_pending = sum(1 for r in INTEXT_REPORT if r["status"] != "ok")
    unexpected_missing = EXPECTED_INTEXT_NAMES - recorded
    strict = os.environ.get("FDA_STRICT_INTEXT") == "1"
    route = os.environ.get("FDA_INTEXT_ROUTE", "real")
    if route not in {"real", "synthetic"}:
        print(f"STRICT: FAILED — invalid FDA_INTEXT_ROUTE={route!r}; expected real or synthetic.")
        return 1

    # Simulated-data estimates DIFFER FROM THE MANUSCRIPT BY CONSTRUCTION, so grading them against
    # the printed values is meaningless: on that route the gate is PRESENCE AND FINITENESS -- every
    # registered scalar must be freshly computed from the simulated inputs, be finite, and be written
    # to the report. An 'outside_manuscript' status is recorded there (the report still shows the
    # comparison) but never counts as a failure. The real-data gate additionally requires manuscript
    # agreement at printed precision.
    by_name = {}
    duplicate_names = set()
    for row in INTEXT_REPORT:
        name = row["name"]
        if name in by_name:
            duplicate_names.add(name)
        by_name[name] = row
    synthetic_bad_values = []
    if route == "synthetic":
        for name in sorted(EXPECTED_INTEXT_NAMES):
            value = by_name.get(name, {}).get("value")
            try:
                finite = value is not None and math.isfinite(float(value))
            except (TypeError, ValueError):
                finite = False
            if not finite:
                synthetic_bad_values.append(name)
    # The two routes report DIFFERENT statuses, because they are graded on different things.
    n_uncomputed = sum(1 for r in INTEXT_REPORT if r["value"] is None)
    n_outside = sum(1 for r in INTEXT_REPORT
                    if r["value"] is not None and r["status"] != "ok")
    if route == "real":
        print(f"STATUS: {'complete' if n_pending == 0 else 'pending'} "
              f"({len(INTEXT_REPORT) - n_pending}/{len(INTEXT_REPORT)} numbers agree with the "
              f"manuscript at printed precision; {n_outside} disagree; {n_uncomputed} not computed; "
              f"{len(_MISSING_INPUTS)} missing input(s); {len(EXPECTED_INTEXT_NAMES)} expected)")
    else:
        print(f"STATUS: {'complete' if not synthetic_bad_values else 'incomplete'} "
              f"({len(INTEXT_REPORT) - n_uncomputed}/{len(INTEXT_REPORT)} numbers computed as finite "
              f"values from the simulated inputs; {len(_MISSING_INPUTS)} missing input(s); "
              f"{len(EXPECTED_INTEXT_NAMES)} expected). Simulated estimates differ from the "
              f"manuscript by construction, so the {n_outside} 'outside_manuscript' row(s) in the "
              f"report are informational on this route, not failures.")
    print("Done. The full crosswalk of every in-text number to its producing program\n"
          "      and output is output/tables/intext_numbers_report.csv.")
    fail_status = n_pending if route == "real" else len(synthetic_bad_values)
    if strict and (fail_status or _MISSING_INPUTS or unexpected_missing or duplicate_names or not appendix_ok):
        # FAIL-CLOSED (certification): in-text magnitudes and/or appendix tables not fully regenerated.
        if route == "real":
            print(f"STRICT: FAILED — {n_pending} number(s) not 'ok' ({n_outside} disagree with the "
                  f"manuscript, {n_uncomputed} not computed), {len(_MISSING_INPUTS)} missing input(s), "
                  f"{len(unexpected_missing)} unregistered expected name(s), "
                  f"{len(duplicate_names)} duplicate name(s), "
                  f"appendix_tables_ok={appendix_ok}.")
        else:
            print(f"STRICT (simulated route): FAILED — {len(synthetic_bad_values)} registered scalar(s) "
                  f"were not computed as finite values, {len(_MISSING_INPUTS)} missing input(s), "
                  f"{len(unexpected_missing)} unregistered expected name(s), "
                  f"{len(duplicate_names)} duplicate name(s), "
                  f"appendix_tables_ok={appendix_ok}. "
                  f"Manuscript agreement is NOT graded on this route.")
            if synthetic_bad_values:
                print("  not computed: " + ", ".join(synthetic_bad_values))
        return 1
    if strict and route == "synthetic":
        print(f"STRICT (simulated route): all {len(EXPECTED_INTEXT_NAMES)} registered manuscript "
              "scalars were freshly computed as finite values; real-data target agreement is not "
              "applicable to simulated estimates. PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
