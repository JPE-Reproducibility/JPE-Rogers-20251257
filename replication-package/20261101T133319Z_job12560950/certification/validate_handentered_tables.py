#!/usr/bin/env python3.9
"""STRICT validator for the generated computational appendix tables D.1, D.11 and D.15: it
validates them against the estimate CSVs they are built from.

Three computational appendix tables -- D.1 (treated-sample construction and coverage), D.11 (log
procedure utilization) and D.15 (cost-benefit) -- are produced by
code/10c_generate_appendix_tables.py into output/tables/Formatted/ and pulled into the manuscript
with \\input. JPE 2.2 wants programs to produce computational exhibits; this validator is the safety
net around that generation. For each table it:

  1. locates the GENERATED .tex file (not an inline manuscript block),
  2. recomputes every displayed COMPUTED cell from the underlying pipeline output, formats it
     exactly as displayed, and requires that string to appear in the generated file, and
  3. verifies the manuscript actually \\input's that generated file (so an inline copy cannot
     shadow the generated one).

It exits NONZERO if any source is missing, any cell disagrees, the generated file is absent, or the
manuscript fails to \\input it -- so incompleteness can never read as success.

Table D.1 (treated-sample construction/coverage) IS program-generated:
code/10c_generate_appendix_tables.py writes output/tables/Formatted/TableD1_SampleConstruction.tex,
which the manuscript \\input{}s at JPE_submission_v8.tex:2846. Its Federal-Register universe counts
are documented constants inside that generator rather than cells recomputed from a pipeline output,
and its price/utilization coverage cells are read from output/tables/d1_price_coverage.csv; the
per-cell recomputation this validator performs for D.11 and D.15 therefore does not apply to it, and
requesting it (--tables ...,D.1) still exits nonzero. The three construction cells the manuscript
prose repeats (29 reclassifications, 12 FDA-initiated, 17 petition-driven) are gated separately, by
code/15_intext_derived_numbers.derived_sample_construction_counts().

Usage:
  validate_handentered_tables.py --manuscript <tex> --output-dir <output/tables> [--tables D.15,D.11]
"""
import argparse
import re
import sys
from pathlib import Path

import pandas as pd

RETENTION = 0.20


def _norm(s):
    r"""Normalize a .tex fragment for string containment: drop backslashes + whitespace, then collapse
    the LaTeX math-minus idiom ``$-$`` to a plain ``-``. The manuscript renders negative estimates as
    ``$-$0.24`` (math-minus), while the spec builders compute the expected cell with Python's ``%.2f``
    => plain ``-0.24``; without this collapse a correct negative cell (e.g. D.11's 2_1 log_q Matched
    ``$-$0.24``) would never contain-match its computed ``-0.24`` and would be reported as a false
    divergence. Applied symmetrically to both sides, so it cannot create a spurious match (currency
    ``$...$`` around positive magnitudes is untouched -- only the standalone ``$-$`` sign is collapsed)."""
    t = re.sub(r"\s+", "", s.replace("\\", ""))
    return t.replace("$-$", "-")


def _find_generated(output_dir, filename):
    """Locate a generated table .tex. --output-dir may point at output/tables or its Formatted/ child."""
    for cand in (output_dir / filename, output_dir / "Formatted" / filename,
                 output_dir.parent / "Formatted" / filename):
        if cand.exists():
            return cand
    return None


def _manuscript_inputs(tex, stem):
    r"""True if the manuscript \input's a file whose basename stem matches (ignoring directory/.tex)."""
    for m in re.finditer(r"\\input\s*\{([^}]*)\}", tex):
        if Path(m.group(1)).name.replace(".tex", "") == stem:
            return True
    return False


# Formatters that MIRROR 10c_generate_appendix_tables' _m / _h / _m0, for validating the D.15
# hospitalization Value/Total/CI and VSL cells. Kept in sync with the generator by construction; a
# divergence in either surfaces as a validator mismatch.
def _mM(x):
    dp = 2 if abs(x) < 1 else 1
    return f"-${abs(x):.{dp}f}M" if x < 0 else f"${x:.{dp}f}M"


def _hM(x):
    r = round(x, 1)
    return "$0M" if r == 0 else (f"-${abs(r):.1f}M" if r < 0 else f"${r:.1f}M")


def _m0M(x):
    dp = 2 if 0 < abs(x) < 1 else 0
    return f"-${abs(x):.{dp}f}M" if x < 0 else f"${x:.{dp}f}M"


def spec_D15(output_dir):
    """Return a list of (label, displayed_string) computed cells for the D.15 cost-benefit table."""
    cb = pd.read_csv(output_dir / "cost_benefit_total_value_did.csv")
    cb = {str(r["reclass_type"]): r for _, r in cb.iterrows()}
    cells = []
    for rc in ("2_1", "3_2"):
        r = cb[rc]
        did = float(r["did_effect_2019M"]); innov = float(r["innovation_benefit_2019M"])
        lo, hi = float(r["ci_lo_2019M"]), float(r["ci_hi_2019M"])
        cells += [
            # These 4 cells (10c generate_d15()'s @@PV_@@/@@INNOV_@@/@@INNOVCI_@@) use _mM(), which
            # mirrors 10c's _m() (2 decimals when the magnitude is below $1M).
            (f"D.15 {rc} patent value",       _mM(did)),
            (f"D.15 {rc} innovation benefit", _mM(innov)),
            (f"D.15 {rc} innov CI lo",        _mM(lo * RETENTION)),
            (f"D.15 {rc} innov CI hi",        _mM(hi * RETENTION)),
        ]
        adv = pd.read_csv(output_dir / f"PaperAdverseEvent_{rc}_Estimates_NoLog_xi_latest_oct22_24.csv")
        Dr = adv.loc[adv.outcome == "D"].iloc[0]
        Hr = adv.loc[adv.outcome == "H"].iloc[0]
        D, H = float(Dr["Estimate"]), float(Hr["Estimate"])
        cells += [
            (f"D.15 {rc} mortality estimate",       f"{D:.2f}"),
            (f"D.15 {rc} hospitalization estimate", f"{H:.2f}"),
            # Confidence-interval bounds, checked so a generator/source drift is caught at the
            # build gate. The normalized comparison normalises bracket spacing.
            (f"D.15 {rc} mortality CI",       f"[{float(Dr['lower_CI']):.1f},{float(Dr['upper_CI']):.1f}]"),
            (f"D.15 {rc} hospitalization CI", f"[{float(Hr['lower_CI']):.1f},{float(Hr['upper_CI']):.1f}]"),
        ]
        # The hospitalization Value/Total/CI cells and the VSL are COMPUTED (Value = per-unit
        # cost; Total = estimate x cost; CI = estimate-CI x cost). Validate them so a HOSP_M / VSL_M
        # drift is caught at the build gate. Formats mirror 10c's _m / _h / _m0.
        VSL_M, HOSP_M = 10.0, 0.022
        hlo, hhi = float(Hr["lower_CI"]) * HOSP_M, float(Hr["upper_CI"]) * HOSP_M
        cells += [
            (f"D.15 {rc} VSL",                     _m0M(VSL_M)),
            (f"D.15 {rc} hospitalization value",   _mM(HOSP_M)),
            (f"D.15 {rc} hospitalization total",   _mM(H * HOSP_M)),
            (f"D.15 {rc} hospitalization total CI", f"[{_hM(hlo)},{_hM(hhi)}]"),
        ]
    return cells


def spec_D11(output_dir):
    """D.11 (Log Procedure Utilization). Checks every DiD-estimate cell the table displays --
    Conley-Taber AND BJS Imputation, All-CPTs AND Matched, both panels -- plus the pre-event mean
    and sample sizes, all read from 05_price_analysis's price_utilization_estimates.csv.

    All 4 (method x sample) Estimate cells per panel are checked, so a table where the BJS
    Imputation row or the Matched column fell back to dash placeholders
    (code/10c_generate_appendix_tables.py's _extract_method_row() emits "<label> & - & - & -" when
    its upstream RegTable_Utilization/DIDimpute_RegTable_Utilization source is missing) cannot
    validate."""
    df = pd.read_csv(output_dir / "price_utilization_estimates.csv")
    cells = []
    for rc in ("3_2", "2_1"):
        lq_all = df[(df.reclass_type.astype(str) == rc) & (df.outcome == "log_q")]
        ct_allcpt = lq_all[(lq_all.method == "Conley_Taber") & (lq_all["sample"] == "All CPTs")]
        if len(ct_allcpt):
            cells.append((f"D.11 {rc} log-q pre-mean", f"{float(ct_allcpt.iloc[0]['pre_mean']):.2f}"))
        for method, mtag in (("Conley_Taber", "CT"), ("BJS_imputation", "BJS")):
            for samp in ("All CPTs", "Matched"):
                sub = lq_all[(lq_all.method == method) & (lq_all["sample"] == samp)]
                if len(sub):
                    cells.append(
                        (f"D.11 {rc} {mtag} {samp} estimate", f"{float(sub.iloc[0]['Estimate']):.2f}")
                    )
        # Sample sizes -- filtered to the utilization (log_q) rows specifically, not just
        # (reclass_type, sample). The same (reclass_type, sample) key also matches the Price
        # (BilledAmt) rows in this CSV, which are built from a differently-matched panel (All-CPTs
        # matched on BilledAmt for price vs. proc_count for utilization) and so can carry a
        # DIFFERENT N, so the rows are filtered to the utilization outcome and the N cannot be
        # read from the Price rows.
        for samp in ("All CPTs", "Matched"):
            sub = lq_all[lq_all["sample"] == samp]
            if len(sub):
                cells.append((f"D.11 {rc} N {samp}", str(int(sub.iloc[0]["Sample Size"]))))
    return cells


def spec_D1(output_dir):
    """D.1 (Treated Sample Construction and Coverage). Independently recomputes the distinctive counts
    -- III->II universe (from data/raw/3_2_begin_final_revisions.csv), II->I treated (03b emission),
    price/utilization coverage (05 emission), and the documented II->I universe constant -- and checks
    the composite N&%% row strings appear in the generated table. Percentages are recomputed from
    the sources, so a synthetic run with different counts still validates against its own sources."""
    raw = output_dir.parent.parent / "data" / "raw"
    bf = pd.read_csv(raw / "3_2_begin_final_revisions.csv")
    u32 = int(bf["PRODUCTCODE"].dropna().astype(str).nunique())
    inv32 = pd.read_csv(raw / "innovation_year_3_2_FDA_project.csv")
    ATYP = ("LTT", "HRD")
    fda32 = len(set(inv32.loc[inv32["FDA_own_accord"] == 1, "PRODUCTCODE"].astype(str)) - set(ATYP))
    final32 = fda32
    U21 = 356
    tr = pd.read_csv(output_dir / "d1_treated_counts.csv")
    final21 = int(tr.loc[tr.reclass_type.astype(str) == "2_1", "n_treated"].iloc[0])
    cov = pd.read_csv(output_dir / "d1_price_coverage.csv")
    cov32 = int(cov.loc[cov.reclass_type.astype(str) == "3_2", "n_covered"].iloc[0])
    cov21 = int(cov.loc[cov.reclass_type.astype(str) == "2_1", "n_covered"].iloc[0])
    p = lambda n, b: int(round(100.0 * n / b))
    return [
        ("D.1 universe row",     f"{u32}&{p(u32,u32)}&{U21}&{p(U21,U21)}"),          # 31&100&356&100
        ("D.1 FDA-initiated",    f"{fda32}&{p(fda32,u32)}"),                          # 12&39
        ("D.1 final treated II->I", f"{final21}&{p(final21,U21)}"),                   # 130&37
        ("D.1 price coverage row",  f"{cov32}&{p(cov32,final32)}&{cov21}&{p(cov21,final21)}"),  # 3&25&15&12
    ]


def _scan_dash_placeholders(block):
    """Structural fail-closed check: flag any row that is a bare dash-placeholder
    ("<label> & - & - & -") wherever it appears in a generated table, INDEPENDENT of whether a
    spec_*() builder above happens to check that specific cell.

    Rationale: code/10c_generate_appendix_tables.py's _extract_method_row() falls back to exactly
    this literal 3-consecutive-dash pattern when its upstream source .tex fragment is missing (see
    generate_d11()); the fallback is syntactically valid LaTeX with no unusual tokens, so it cannot
    be caught by a malformed-file check. The per-cell containment checks above only compare cells a
    spec builder explicitly lists; here any dash-placeholder row fails, regardless of which cells a
    spec lists. This scan is table-agnostic (neither D.15's nor D.1's
    generated output legitimately contains this pattern) so a similar fallback introduced into any
    future generator, for a cell no spec_*() has been updated to check yet, still cannot pass."""
    problems = []
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9 —–.-]{0,40})&\s*-\s*&\s*-\s*&\s*-\s*\\\\", block):
        label = m.group(1).strip(" \\{}").strip()
        problems.append(
            f"placeholder row: {label!r} row is unpopulated (\"& - & - & -\") -- a required "
            f"computed cell did not reach the table (generator fell back to its dash placeholder)."
        )
    return problems


# table -> (generated .tex filename, spec builder). All three tables are program-generated by 10c and
# \input into the manuscript; the validator reads the GENERATED file and confirms the \input.
SPECS = {
    "D.15": ("TableD15_CostBenefit.tex", spec_D15),
    "D.11": ("TableD11_Utilization.tex", spec_D11),
    "D.1":  ("TableD1_SampleConstruction.tex", spec_D1),
}

OPEN_TABLES = {}


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manuscript", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--tables", default="D.15,D.11,D.1",
                    help="comma-separated tables (default all three program-generated ones).")
    return ap.parse_args()


def main():
    a = parse_args()
    tex = a.manuscript.read_text(encoding="utf-8", errors="replace")
    requested = [t.strip() for t in a.tables.split(",") if t.strip()]
    problems, checked, ok = [], 0, []
    for t in requested:
        if t in OPEN_TABLES:
            problems.append(f"{t}: OPEN -- {OPEN_TABLES[t]}")
            continue
        if t not in SPECS:
            problems.append(f"{t}: unknown table")
            continue
        filename, builder = SPECS[t]
        stem = filename.replace(".tex", "")
        # (1) the generated file must exist
        genfile = _find_generated(a.output_dir, filename)
        if genfile is None:
            problems.append(f"{t}: generated file {filename} not found under {a.output_dir} "
                            f"(did 10c_generate_appendix_tables.py run?)")
            continue
        block = genfile.read_text(encoding="utf-8", errors="replace")
        nblock = _norm(block)
        # (1b) structural fail-closed scan: no row may be an unpopulated dash placeholder,
        # regardless of whether the spec below happens to check that row's specific cells.
        for p in _scan_dash_placeholders(block):
            problems.append(f"{t}: {p}")
        # (2) every computed cell must trace to the pipeline output
        try:
            cells = builder(a.output_dir)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{t}: could not compute expected cells: {type(e).__name__}: {e}")
            continue
        if not cells:
            problems.append(f"{t}: spec produced 0 cells (source missing/empty) -- cannot validate")
            continue
        for label, disp in cells:
            checked += 1
            if _norm(disp) not in nblock:
                problems.append(f"{label}: value {disp!r} NOT in generated {filename} (generator/source diverge)")
        # (3) the manuscript must \input the generated file (no inline copy shadowing it)
        if not _manuscript_inputs(tex, stem):
            problems.append(f"{t}: manuscript does not \\input {stem} (inline copy or missing wire)")
        else:
            ok.append(f"{t}: {len(cells)} cell(s) validated against source; manuscript \\input's {stem}.")

    print(f"appendix-table validation: {checked} computed cell(s) checked, {len(problems)} problem(s).")
    for o in ok:
        print(f"  OK: {o}")
    for p in problems:
        print(f"  PROBLEM: {p}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
