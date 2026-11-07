"""
10c_generate_appendix_tables.py -- PROGRAM-GENERATE the appendix computational tables, so the
code produces every computational exhibit
(JPE Data Policy 2.2). Each table is written to output/tables/Formatted/ as a complete LaTeX table
the manuscript can \\input{}; running on the simulated data regenerates simulated versions.

Generated here:
  - TableD15_CostBenefit.tex   (cost-benefit; from cost_benefit_total_value_did.csv + the
                                PaperAdverseEvent_{2_1,3_2} estimates + documented cost constants)
  - TableD11_Utilization.tex   (log procedure utilization; from price_utilization_estimates.csv)
  - TableD1_SampleConstruction.tex (treated-sample construction + coverage counts; from the
                                sample-construction counts written by 02_match_samples.py)

The manuscript already \\input{}s all three of these generated files -- TableD1_SampleConstruction.tex
at JPE_submission_v8.tex:2846, TableD11_Utilization.tex at :3608 and TableD15_CostBenefit.tex at
:3887 -- so the .tex carries no separate copy of any of them. A generated cell that
disagrees with the pipeline output is therefore a reproduction failure, not a pending switch-over:
certification/validate_handentered_tables.py recomputes every displayed computed cell from the
underlying output and exits nonzero on any disagreement.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "output" / "tables"
FORMATTED = TABLES / "Formatted"
RAW = ROOT / "data" / "raw"

# Documented cost-benefit constants (also stated in the D.15 table header).
VSL_M = 10.0        # EPA value of a statistical life, $M (2019)
HOSP_M = 0.022      # average inpatient hospitalization, $M ($22,000)
RETENTION = 0.20    # patent-value retention after business-stealing/creative-destruction


def _read(name):
    p = TABLES / name
    if not p.exists():
        raise FileNotFoundError(f"required input for appendix-table generation missing: {p}")
    return pd.read_csv(p)


def _m(x):
    """$-in-millions, manuscript style: negatives as -$X.XM; 2 decimals for small magnitudes so the
    tiny hospitalization figures (~$0.06M) don't collapse to $0.0M."""
    dp = 2 if abs(x) < 1 else 1
    return f"-\\${abs(x):.{dp}f}M" if x < 0 else f"\\${x:.{dp}f}M"


def _m0(x):
    dp = 2 if 0 < abs(x) < 1 else 0
    return f"-\\${abs(x):.{dp}f}M" if x < 0 else f"\\${x:.{dp}f}M"


def _z0(x):
    """$-in-millions rounded to whole millions, manuscript style, with sign-of-zero -> '$0M'."""
    r = int(round(x))
    return "\\$0M" if r == 0 else (f"-\\${abs(r)}M" if r < 0 else f"\\${r}M")


def _h(x):
    """$-in-millions to ONE decimal, sign-aware, for the tiny hospitalization CI bounds
    (~$0.1M) that whole-million rounding (_z0) would collapse to $0M."""
    r = round(x, 1)
    if r == 0:
        return "\\$0M"
    return f"-\\${abs(r):.1f}M" if r < 0 else f"\\${r:.1f}M"


# EXACT manuscript tab:CostBenefits layout. Substantive cells are @@tokens@@ filled from the
# outputs; the negligible hospitalization-dollar cells (Value $0.02M; Total $.06M/-$0.04M and their
# near-zero CIs) and the stated VSL $10M are kept as the manuscript's documented back-of-envelope
# literals -- the hospitalization ESTIMATES and every $M-scale magnitude are still code-computed.
_D15_TEMPLATE = r"""\begin{table}[ht!]
    \centering
    \caption{\textbf{Costs and Benefits of Reclassification}}
\resizebox{\textwidth}{!}{\begin{tabular}{ *8{l}  }
    \midrule \midrule
\multirow{10}{*}{\rotatebox{90}{\textbf{Assumptions}}}
& & &
        &  &  &\\
  & \multicolumn{7}{l}{-Cost of mortality is EPA's VSL of \$10 million (\$2019).} \\
    & \multicolumn{7}{l}{-Average inpatient hospital stay costs \$22,000 \citep{CostsofHospitalStay:2019}. No other costs.} \\
    & \multicolumn{7}{l}{-Attribute 80\% of patent value to business stealing/creative destruction \citep{kogan:2017}.} \\
    & \multicolumn{7}{l}{-Do not consider private firm patent values.} \\

& \multicolumn{7}{l}{-Do not consider scientific value of innovation.} \\
    & \multicolumn{7}{l}{-No value of efficacy information from regulations.} \\
        & \multicolumn{7}{l}{-No value from firm entry (e.g., not considering the value of new jobs).} \\

& & &
        &  &  &\\
    \midrule \midrule



    & & Outcome  & \multicolumn{1}{c}{Estimate} & \multicolumn{1}{c}{95\% C.I.}
        & Value & Total & 95\% C.I. \\
    \midrule

    \multirow{10}{*}{\rotatebox{90}{\textbf{Class III to II}}} & \multirow{5}{*}{\rotatebox{90}{\textbf{Costs}}}
    & Mortality & @@D_EST_32@@& @@D_CI_32@@& @@VSL@@
        & @@D_TOT_32@@& @@D_TOTCI_32@@\\
   & & Hospitalizations& @@H_EST_32@@& @@H_CI_32@@
        & @@HVAL@@ & @@H_TOT_32@@ & @@H_TOTCI_32@@\\
        & & &
        &  &  &\\

     \cmidrule{7-8}

    & &&&&& @@COST_TOT_32@@& @@COST_TOTCI_32@@\\

     \cmidrule{2-8}

   &\multirow{4}{*}{\rotatebox{90}{\textbf{Benefits}}}

    & Patent Value& @@PV_32@@ & @@PVCI_32@@&$/5$
        & @@INNOV_32@@ & @@INNOVCI_32@@\\

          & & &
        &  &  &\\

          & & &
        &  &  &\\
  & & &
        &  &  &\\

    \hline


    \multirow{10}{*}{\rotatebox{90}{\textbf{Class II to I}}} & \multirow{5}{*}{\rotatebox{90}{\textbf{Costs}}}

    & Mortality & @@D_EST_21@@& @@D_CI_21@@
        & @@VSL@@ & @@D_TOT_21@@ &@@D_TOTCI_21@@ \\
   & & Hospitalizations& @@H_EST_21@@& @@H_CI_21@@
        & @@HVAL@@ &  @@H_TOT_21@@ & @@H_TOTCI_21@@\\
        & & &
        &  &  &\\

     \cmidrule{7-8}

    & &&&&& @@COST_TOT_21@@& @@COST_TOTCI_21@@\\

     \cmidrule{2-8}

   &\multirow{4}{*}{\rotatebox{90}{\textbf{Benefits}}}

    & Patent Value & @@PV_21@@ & @@PVCI_21@@
        & $/5$ & @@INNOV_21@@ & @@INNOVCI_21@@\\
          & & &
        &  &  &\\
          & & &
        &  &  &\\
          & & &
        &  &  &\\
    \bottomrule


\end{tabular}}
 \caption*{\footnotesize{Note: The table offers back-of-the-envelope cost-benefit analyses for Class III to II and Class II to I reclassification events, with assumptions outlined in the table header. Patent-value benefits are estimated directly as a difference-in-differences effect on the total market value of public-firm patents per device type per year, using \citet{kogan:2017} patent values deflated to millions of 2019 dollars and the same matched sample as the main analysis. The ``Estimate'' column reports this annual total-value effect; ``$/5$'' in the Value column applies the 20\% retention after netting out business stealing and creative destruction; ``Total'' is the resulting annual benefit. I include 95\% confidence intervals for both costs and benefits, which are annualized and averaged across treated device types. ``Hospital.'' refers to hospitalizations.}}  \label{tab:CostBenefits}
 \end{table}
"""


def generate_d15():
    """Cost-benefit table (tab:CostBenefits): fills the exact manuscript layout with values computed
    from the outputs so \\input renders identically to the previous inline table."""
    cb = {str(r["reclass_type"]): r for _, r in _read("cost_benefit_total_value_did.csv").iterrows()}
    txt = _D15_TEMPLATE
    for rc, sp in (("3_2", ","), ("2_1", ", ")):   # 3_2 estimate-CI has no comma-space; 2_1 does
        d = _read(f"PaperAdverseEvent_{rc}_Estimates_NoLog_xi_latest_oct22_24.csv")
        D = d[d.outcome == "D"].iloc[0]; H = d[d.outcome == "H"].iloc[0]
        r = cb[rc]
        did, cilo, cihi = float(r["did_effect_2019M"]), float(r["ci_lo_2019M"]), float(r["ci_hi_2019M"])
        innov = float(r["innovation_benefit_2019M"])
        mtot, htot = D.Estimate * VSL_M, H.Estimate * HOSP_M
        tag = rc.replace("_", "")
        sub = {
            f"@@D_EST_{tag}@@": f"{D.Estimate:.2f}",
            f"@@D_CI_{tag}@@": f"[{D.lower_CI:.1f}{sp}{D.upper_CI:.1f}]",
            f"@@D_TOT_{tag}@@": _m(mtot),
            f"@@D_TOTCI_{tag}@@": f"[{_z0(D.lower_CI*VSL_M)}, {_z0(D.upper_CI*VSL_M)}]",
            f"@@H_EST_{tag}@@": f"{H.Estimate:.2f}",
            f"@@H_CI_{tag}@@": f"[{H.lower_CI:.1f}{sp}{H.upper_CI:.1f}]",
            # F9: the hospitalization Value/Total/CI + the VSL are now COMPUTED (were literals).
            # Value = per-unit cost constant; Total = estimate x cost; CI = estimate-CI x cost.
            f"@@VSL@@": _m0(VSL_M),                     # per-life cost ($10M, stated assumption)
            f"@@HVAL@@": _m(HOSP_M),                    # per-hospitalization cost ($0.02M)
            f"@@H_TOT_{tag}@@": _m(htot),               # H.Estimate * HOSP_M
            f"@@H_TOTCI_{tag}@@": f"[{_h(H.lower_CI * HOSP_M)}, {_h(H.upper_CI * HOSP_M)}]",
            f"@@COST_TOT_{tag}@@": _m(mtot + htot),
            f"@@COST_TOTCI_{tag}@@": f"[{_z0(D.lower_CI*VSL_M + H.lower_CI*HOSP_M)}, "
                                    f"{_z0(D.upper_CI*VSL_M + H.upper_CI*HOSP_M)}]",
            f"@@PV_{tag}@@": _m(did),
            f"@@PVCI_{tag}@@": f"[{_z0(cilo)}, {_z0(cihi)}]",
            f"@@INNOV_{tag}@@": _m(innov),
            f"@@INNOVCI_{tag}@@": f"[{_m(cilo*RETENTION)}, {_m(cihi*RETENTION)}]",
        }
        for k, v in sub.items():
            txt = txt.replace(k, v)
    if "@@" in txt:
        raise AssertionError(f"D.15 QC: unsubstituted token(s) remain: {txt[txt.find('@@'):][:30]}")
    out = FORMATTED / "TableD15_CostBenefit.tex"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(txt, encoding="utf-8")
    print(f"  Wrote {out.relative_to(ROOT)}")
    return out


def _extract_method_row(texfile, marker):
    """Pull the estimate row + SE row for a method (Conley--Taber / BJS Imputation) out of one of
    05's RegTable_Utilization / DIDimpute_RegTable_Utilization outputs, trimming the two empty
    trailing columns so it fits the 4-column D.11 layout. Returns (estimate_row, se_row) as LaTeX."""
    try:
        lines = Path(texfile).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        # Synthetic-route robustness: 05 does not regenerate a RegTable_Utilization panel when the
        # simulated data lacks that panel's price/GPT-links input (e.g. the 3_2 utilization panel). The
        # cert deletes all shipped exhibits first, so the file is then simply absent. Emit a dash-filled
        # placeholder row so Table D.11 still renders and the step succeeds. This is the synthetic-route
        # placeholder: on the real-data route every such file is regenerated, and
        # certification/validate_handentered_tables.py rejects any dash row there.
        return (f"\\hspace{{6mm}}{marker} & - & - & - \\\\", " & - & - & - \\\\")
    for i, ln in enumerate(lines):
        if marker in ln:
            est = "&".join(ln.split(r"\\")[0].split("&")[:4]).rstrip() + r" \\"
            se = "&".join(lines[i + 1].split(r"\\")[0].split("&")[:4]).rstrip() + r" \\"
            return est, se
    raise ValueError(f"marker {marker!r} not found in {texfile}")


def generate_d11():
    """Table D.11 (Effect on Log Procedure Utilization, tab:Utilization). Assembled from 05's own
    program-generated regression tables: the Conley--Taber rows from RegTable_Utilization_{rc} and
    the BJS rows from DIDimpute_RegTable_Utilization_{rc}; sample sizes from
    price_utilization_estimates.csv. Leaves 05 untouched (reuses its outputs)."""
    pu = _read("price_utilization_estimates.csv")
    panels = {"3_2": "A. Class III to II", "2_1": "B. Class II to I"}
    n_by = {}
    for rc in panels:
        n_by[rc] = {}
        for samp in ("All CPTs", "Matched"):
            # WIRING FIX: price_utilization_estimates.csv also carries the Price (BilledAmt) rows
            # for the SAME (reclass_type, sample) keys, built from a differently-matched panel (the
            # All-CPTs panel is matched on BilledAmt for price vs. proc_count for utilization) --
            # so it can have a DIFFERENT Sample Size. Filtering only by (reclass_type, sample)
            # without an outcome key would let .iloc[0] take whichever row sorts first (Price,
            # since 05 appends price rows before utilization rows). Filter to the log_q
            # (utilization) rows explicitly so the N is never read from the Price rows.
            sub = pu[(pu.reclass_type.astype(str) == rc) & (pu["sample"] == samp)
                     & (pu["outcome"] == "log_q")]
            n_by[rc][samp] = int(sub.iloc[0]["Sample Size"]) if len(sub) else None
    rows = {}
    for rc in panels:
        rows[rc, "ct"] = _extract_method_row(FORMATTED / f"RegTable_Utilization_{rc}_sep25.tex", "Conley--Taber")
        rows[rc, "bj"] = _extract_method_row(FORMATTED / f"DIDimpute_RegTable_Utilization_{rc}_sep25.tex", "BJS Imputation")
    # EXACT reproduction of the manuscript's inline tab:Utilization layout (so \input renders
    # byte-for-byte the same), with the estimate/SE rows and sample sizes filled from the outputs.
    txt = (
        "\\begin{table}[h!]\n\\begin{center}\n"
        "\\caption{\\textbf{Effect of Reclassification on Log Procedure Utilization}}\n"
        "\\resizebox{.9\\textwidth}{!}{\n   \\small\n\\begin{tabular}{lccc}\n\\hline \\hline\n"
        "&   & \\multicolumn{2}{c}{DiD Estimates}\\\\\n\\cmidrule{3-4}\n"
        " & Pre-mean & All CPTs & Matched \\\\\n"
        " & \\multicolumn{1}{c}{(1)}  & \\multicolumn{1}{c}{(2)}&\\multicolumn{1}{c}{(3)}\\\\\n"
        " \\addlinespace\n\n\\midrule\n\\addlinespace\n"
        "\\textbf{A. Class III to II} & & & \\\\\n\\addlinespace\n"
        f"{rows['3_2','ct'][0]}\n{rows['3_2','ct'][1]}\n\\addlinespace\n"
        f"{rows['3_2','bj'][0]}\n{rows['3_2','bj'][1]}\n\\addlinespace\n\\cmidrule{{2-4}}\n"
        f"\\hspace{{6mm}}Sample Size &  & {n_by['3_2']['All CPTs']} & {n_by['3_2']['Matched']} \\\\\n\n"
        "\\addlinespace\n\\hline\n\\addlinespace\n\n"
        "\\textbf{B. Class II to I} & & & \\\\\n\\addlinespace\n"
        f"{rows['2_1','ct'][0]}\n{rows['2_1','ct'][1]}\n\\addlinespace\n"
        f"{rows['2_1','bj'][0]}\n{rows['2_1','bj'][1]}\n\\addlinespace\n\\cmidrule{{2-4}}\n"
        f"\\hspace{{6mm}}Sample Size &  & {n_by['2_1']['All CPTs']} & {n_by['2_1']['Matched']} \\\\\n\\addlinespace\n\n"
        "\\bottomrule\n\\end{tabular}}\n\n"
        "\\caption*{ \\begin{footnotesize}Note: The table reports estimates from Equation \\ref{eq:OLS}, "
        "a DiD OLS model. The outcome is log annual procedure counts (utilization) from MarketScan "
        "claims data (1996--2013). Column (1) reports 5-year pre-event means for treated device types. "
        "Columns (2)--(3) show DiD estimates using controls that match on (2) baseline procedure counts "
        "across all procedure codes and (3) device outcomes. For each panel, the first row reports "
        "Conley--Taber stacked DiD estimates and the second row reports BJS imputation estimates. "
        "† Pre-mean is unlogged, while estimates are in logs. Confidence intervals use "
        "Conley--Taber inference. +, *, **, and *** denote statistical significance at 0.10, 0.05, "
        "0.01, and 0.001 levels, respectively.\n\\end{footnotesize} }\n\\label{tab:Utilization}\n"
        "\\end{center}\n\\end{table}"
    )
    out = FORMATTED / "TableD11_Utilization.tex"
    out.write_text(txt, encoding="utf-8")
    # STRUCTURAL QC (fail-closed) -- does NOT assert equality to real manuscript values, so a
    # synthetic run producing different estimates still passes. Checks: both method rows in both
    # panels; every displayed estimate/SE cell parses to a finite number; sample sizes are positive.
    import re as _re
    for panel in ("Class III to II", "Class II to I"):
        if panel not in txt:
            raise AssertionError(f"D.11 QC: panel {panel!r} missing")
    # Count the ROW-LABEL form (indented \hspace{6mm}<label>), which appears exactly once per panel.
    # The bare terms also occur in the footnote prose, so match the row label, not the plain word.
    for label in ("Conley--Taber", "BJS Imputation", "Sample Size"):
        marker = "\\hspace{6mm}" + label
        if txt.count(marker) != 2:
            raise AssertionError(f"D.11 QC: expected 2 '{label}' rows, found {txt.count(marker)}")
    for rc in panels:
        for meth, e_se in (("ct", rows[rc, "ct"]), ("bj", rows[rc, "bj"])):
            # FAIL-CLOSED FIX: the old version of this loop only iterated over whatever decimal
            # tokens HAPPENED to be present, so it vacuously passed when _extract_method_row()'s
            # dash-placeholder fallback fired (its "- & - & -" row contains zero decimal tokens,
            # so the loop body never ran and nothing raised). Each estimate row is required to show
            # 3 populated data cells -- pre-mean, All-CPTs estimate, Matched estimate -- and the SE
            # row 3 populated SEs; require that many decimal-format numbers are actually present
            # BEFORE checking their finiteness, so an all-dash (or partially-dash) row is caught
            # here instead of silently reaching the shipped table.
            est_nums = _re.findall(r"[-+]?\d+\.\d+", e_se[0])
            se_nums = _re.findall(r"[-+]?\d+\.\d+", e_se[1])
            if len(est_nums) < 3:
                raise AssertionError(
                    f"D.11 QC: {rc}/{meth} estimate row has {len(est_nums)} populated numeric "
                    f"cell(s), expected 3 (pre-mean, All CPTs, Matched) -- placeholder/dash cell(s) "
                    f"reached the table: {e_se[0]!r}"
                )
            if len(se_nums) < 3:
                raise AssertionError(
                    f"D.11 QC: {rc}/{meth} SE row has {len(se_nums)} populated numeric cell(s), "
                    f"expected 3 -- placeholder/dash cell(s) reached the table: {e_se[1]!r}"
                )
            for cell in est_nums + se_nums:
                if not _isfinite_str(cell):
                    raise AssertionError(f"D.11 QC: non-finite value {cell!r} in {rc}/{meth}")
        for samp in ("All CPTs", "Matched"):
            if not (isinstance(n_by[rc][samp], int) and n_by[rc][samp] > 0):
                raise AssertionError(f"D.11 QC: sample size for {rc}/{samp} not a positive int: {n_by[rc][samp]}")
    print(f"  Wrote {out.relative_to(ROOT)}")
    return out


def _isfinite_str(s):
    try:
        import math
        return math.isfinite(float(s))
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------------------------------
# Table D.1 (Treated Sample Construction and Coverage, tab:SampleConstruction)
# ---------------------------------------------------------------------------------------------------
# Documented Federal-Register institutional constants. These are NOT computed from data: the II->I
# reclassification universe is not enumerated in any shipped file, and the two atypical III->II
# exclusions are a documented adjudication named in the table's own footnote a. Provenance: the FDA
# Federal Register reclassification record + manuscript tab:SampleConstruction footnote a.
D1_UNIVERSE_2_1 = 356                 # II->I Federal Register reclassified device types
D1_ATYPICAL_3_2 = ("LTT", "HRD")      # III->II atypical cases excluded (footnote a):
#   LTT = antimicrobial susceptibility panels (a preamendment->Class II reclassification, not a
#         genuine III->II event); HRD = soft-lens thermal sterilizer (commercially obsolete, no
#         device submissions after 1983, well before its 1997 reclassification).

# Verbatim note for D.1 (static prose + footnotes a-e; contains no computed values).
_D1_NOTE = (
    r"\caption*{\footnotesize" "\n"
    r"\textit{Note:} Panel~A traces the treated device-type sample from the Federal Register "
    r"reclassification universe to the final analysis sample. Panel~B reports, for each outcome "
    r"group, the number and share of treated device types that enter the corresponding estimating "
    r"sample. Patent counts, forward citations, and safety-emphasis measures are constructed from "
    r"all USPTO grants in the Dimensions patent database, covering both public and private firms. "
    r"In device-type-years with no patenting, these patent outcomes are coded as zero. In "
    r"device-type-years with no reported adverse events, adverse-event counts are coded as zero. "
    r"All such zero-valued observations enter the regressions. Tables~\ref{tab:Combined_DropNoCounts} "
    r"report robustness estimates excluding device types whose outcome sum equals zero over the full "
    r"sample period; because this restriction is applied separately by outcome, sample sizes can "
    r"differ slightly across specifications.\\[3pt]" "\n"
    r"\textsuperscript{a}Two atypical III-to-II cases are excluded: LTT (antimicrobial "
    r"susceptibility panels), a preamendment-to-Class~II reclassification rather than a III-to-II "
    r"reclassification; and HRD (soft-lens thermal sterilizer), a commercially obsolete product with "
    r"no device submissions after 1983, well before its 1997 reclassification.\\" "\n"
    r"\textsuperscript{b}Patent market values follow \citet{kogan:2017} and are observed only for "
    r"publicly traded assignees. Device-type-years in which patenting is attributable only to private "
    r"firms are coded as zero rather than excluded, so the device-type sample is identical across "
    r"patent-based outcomes.\\" "\n"
    r"\textsuperscript{c}Class~I devices are generally exempt from premarket submission requirements, "
    r"so device-submission outcomes are not defined for II-to-I reclassifications.\\" "\n"
    r"\textsuperscript{d}Requires linkage to MarketScan claims (1996--2013) and outpatient procedure "
    r"mappings, restricting the sample to post-1996 reclassification events with usable procedure "
    r"links.\\" "\n"
    r"\textsuperscript{e}Uses firm assets from CRSP/Compustat and is the only specification "
    r"restricted to publicly listed firms.}"
)


def _pct(n, base):
    """Percentage exactly as displayed in D.1: round(100*n/base)."""
    return int(round(100.0 * n / base))


def _read_key(csv_path, key_col, key, val_col):
    """Read one integer value from a small emitted counts CSV; raise if absent/malformed."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"D.1 input missing: {csv_path} (emitted by the estimation step; run the pipeline first)")
    df = pd.read_csv(csv_path)
    sub = df[df[key_col].astype(str) == str(key)]
    if not len(sub):
        raise AssertionError(f"D.1 input {csv_path} has no row {key_col}=={key!r}")
    v = sub.iloc[0][val_col]
    if pd.isna(v):
        raise AssertionError(f"D.1 input {csv_path} value for {key} is missing/NaN")
    return int(v)


def generate_d1():
    """Table D.1 (Treated Sample Construction and Coverage). Every count is either COMPUTED from the
    pipeline's data/outputs or a clearly-labeled documented Federal-Register constant:

      * III->II universe (31):        unique PRODUCTCODE in data/raw/3_2_begin_final_revisions.csv
      * III->II excl. atypical (29):  universe minus the 2 documented atypical cases (footnote a)
      * III->II FDA-initiated (12):   FDA_own_accord==1 in innovation_year_3_2 minus atypical present
      * III->II final treated (12):   = FDA-initiated (all have >=1 pre-reclassification patent)
      * II->I universe (356):         documented Federal-Register constant (not in any shipped file)
      * II->I final treated (130):    03b emission output/tables/d1_treated_counts.csv
      * price/utilization cover (3,15): 05 emission output/tables/d1_price_coverage.csv

    Fail-closed: raises if any input is missing or any internal-consistency check fails."""
    # --- III->II construction, computed from shipped raw data ---
    bf = pd.read_csv(RAW / "3_2_begin_final_revisions.csv")
    if "PRODUCTCODE" not in bf.columns:
        raise AssertionError("D.1: 3_2_begin_final_revisions.csv lacks PRODUCTCODE column")
    u32 = int(bf["PRODUCTCODE"].dropna().astype(str).nunique())
    exclA32 = u32 - len(D1_ATYPICAL_3_2)                      # documented 2 atypical exclusions
    inv32 = pd.read_csv(RAW / "innovation_year_3_2_FDA_project.csv")
    fda_all = set(inv32.loc[inv32["FDA_own_accord"] == 1, "PRODUCTCODE"].astype(str))
    fda32 = len(fda_all - set(D1_ATYPICAL_3_2))              # FDA-initiated, excluding atypical
    final32 = fda32                                          # all FDA-initiated have >=1 patent

    # --- II->I: universe is a documented constant; treated count from 03b's emission ---
    u21 = D1_UNIVERSE_2_1
    final21 = _read_key(TABLES / "d1_treated_counts.csv", "reclass_type", "2_1", "n_treated")

    # --- price/utilization coverage from 05's emission ---
    cov32 = _read_key(TABLES / "d1_price_coverage.csv", "reclass_type", "3_2", "n_covered")
    cov21 = _read_key(TABLES / "d1_price_coverage.csv", "reclass_type", "2_1", "n_covered")

    # --- internal-consistency QC (fail-closed; monotonicity of the counts, not equality to manuscript values) ---
    if not (0 < final32 <= fda32 <= exclA32 <= u32):
        raise AssertionError(f"D.1 QC: III->II chain not monotone: final{final32} fda{fda32} "
                             f"exclA{exclA32} univ{u32}")
    if not (0 < final21 <= u21):
        raise AssertionError(f"D.1 QC: II->I final {final21} exceeds universe {u21}")
    if not (0 < cov32 <= final32):
        raise AssertionError(f"D.1 QC: III->II price coverage {cov32} exceeds final treated {final32}")
    if not (0 < cov21 <= final21):
        raise AssertionError(f"D.1 QC: II->I price coverage {cov21} exceeds final treated {final21}")

    na = "n/a"
    # (N_3_2, pct_3_2, N_2_1, pct_2_1) per row; pct base = universe for Panel A, final treated for B.
    txt = (
        "\\begin{table}[h!]\n\\centering\n"
        "\\caption{\\textbf{Treated Sample Construction and Coverage}}\n"
        "\\label{tab:SampleConstruction}\n"
        "\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}{lcccc}\n\\toprule\n"
        "& \\multicolumn{2}{c}{Down-Regulation (III to II)}\n"
        "& \\multicolumn{2}{c}{Deregulation (II to I)} \\\\\n"
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}\n"
        "& $N$ & \\% & $N$ & \\% \\\\\n\\midrule\n"
        "\\multicolumn{5}{l}{\\textbf{A. Construction of treated sample}} \\\\[2pt]\n"
        f"Federal Register reclassified device types\n  & {u32} & {_pct(u32,u32)} & {u21} & {_pct(u21,u21)} \\\\\n"
        f"Excluding atypical reclassifications\\textsuperscript{{a}}\n  & {exclA32} & {_pct(exclA32,u32)} & {na} & {na} \\\\\n"
        f"FDA-initiated only (excluding petition-driven cases)\n  & {fda32} & {_pct(fda32,u32)} & {na} & {na} \\\\\n"
        f"With $\\geq$1 pre-reclassification patent\n  & {final32} & {_pct(final32,u32)} & {final21} & {_pct(final21,u21)} \\\\\n"
        f"Final treated device-type sample\n  & {final32} & {_pct(final32,u32)} & {final21} & {_pct(final21,u21)} \\\\\n"
        "\\\\[-2pt]\n"
        "\\multicolumn{5}{l}{\\textbf{B. Estimation-sample coverage by outcome}} \\\\[2pt]\n"
        f"Patent counts, forward citations, safety emphasis\n  & {final32} & {_pct(final32,final32)} & {final21} & {_pct(final21,final21)} \\\\\n"
        f"Patent market value\\textsuperscript{{b}}\n  & {final32} & {_pct(final32,final32)} & {final21} & {_pct(final21,final21)} \\\\\n"
        f"Device submissions\\textsuperscript{{c}}\n  & {final32} & {_pct(final32,final32)} & {na} & {na} \\\\\n"
        f"Adverse events\n  & {final32} & {_pct(final32,final32)} & {final21} & {_pct(final21,final21)} \\\\\n"
        f"Price and utilization\\textsuperscript{{d}}\n  & {cov32} & {_pct(cov32,final32)} & {cov21} & {_pct(cov21,final21)} \\\\\n"
        f"Public-firm heterogeneity\\textsuperscript{{e}}\n  & {final32} & {_pct(final32,final32)} & {final21} & {_pct(final21,final21)} \\\\\n"
        "\\bottomrule\n\\end{tabular}}\n\n\\vspace{3mm}\n\n"
        + _D1_NOTE + "\n\\end{table}"
    )
    out = FORMATTED / "TableD1_SampleConstruction.tex"
    out.write_text(txt, encoding="utf-8")
    print(f"  Wrote {out.relative_to(ROOT)}  "
          f"[III->II {u32}/{exclA32}/{fda32}/{final32}, cov {cov32}; II->I {u21}/{final21}, cov {cov21}]")
    return out


# JPE 1.4 note: the device-experience coefficient tables (output/tables/model_*_est_*.csv) are
# written in non-proprietary form by the step that fits the models, code/11d_reg_design.py (see
# write_model_coefficient_csv there). No shipped step reads a pickle.


# Every table this step MUST generate. main() is FAIL-CLOSED: if any is not produced (missing
# input, generator error), it exits nonzero so appendix generation cannot silently succeed.
# D.1 counts come from computed shipped raw data + two emitted counts files (03b's d1_treated_counts
# for the II->I treated total; 05's d1_price_coverage for the MarketScan price/utilization coverage)
# + two documented Federal-Register constants (II->I universe 356; the 2 atypical III->II exclusions).
REQUIRED_GENERATORS = (generate_d15, generate_d11, generate_d1)


def main():
    FORMATTED.mkdir(parents=True, exist_ok=True)
    generated, failed = [], []
    for gen in REQUIRED_GENERATORS:
        try:
            generated.append(gen())
        except Exception as e:  # noqa: BLE001
            print(f"  [FAIL] {gen.__name__}: {type(e).__name__}: {e}")
            failed.append(gen.__name__)
    print(f"Generated {len(generated)}/{len(REQUIRED_GENERATORS)} appendix table(s).")
    if failed:
        print(f"FATAL: {len(failed)} required appendix table(s) NOT generated: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
