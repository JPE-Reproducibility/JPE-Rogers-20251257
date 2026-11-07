"""
10b_format_remaining_tables.py

Produce formatted LaTeX tables for:
  - Table D.11a: Device Experience (III→II)
  - Table D.11b: Device Experience (II→I)
  - Safety Robustness: combined Embedding Distance + "Safety" Only

Reads from existing replication output (the plain-CSV coefficient tables 11d_reg_design.py
writes, plus the 06b/06c estimate CSVs). Does NOT re-run any regressions, and does not read
any Python pickle.
"""

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = ROOT / "output" / "tables"
FORMATTED_DIR = TABLES_DIR / "Formatted"
FORMATTED_DIR.mkdir(parents=True, exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────

def _stars(pval):
    if pval < 0.001:
        return "***"
    if pval < 0.01:
        return "**"
    if pval < 0.05:
        return "*"
    if pval < 0.10:
        return "+"
    return ""


def _stars_from_ci(est, ci_lo, ci_hi):
    """Compute significance stars from CI bounds (for safety tables)."""
    se = (est - ci_lo) / 1.96 if est > 0 else abs(est - ci_hi) / 1.96
    if se == 0:
        return "", 0.0
    tstat = abs(est / se)
    if tstat > scipy.stats.norm.ppf(0.9995):
        return "***", se
    if tstat > scipy.stats.norm.ppf(0.995):
        return "**", se
    if tstat > scipy.stats.norm.ppf(0.975):
        return "*", se
    if tstat > scipy.stats.norm.ppf(0.95):
        return "+", se
    return "", se


# ── variable display names ───────────────────────────────────────────────────

CORE_VAR_NAMES = {
    "constant": "Intercept",
    "exp_years": "Device Experience (years)",
    "v_serious_event": "Baseline Serious Adverse Events",
    "FDA_own_accord": "FDA's Own Accord",
    "DPM": "Device Priority Model Score",
    "patents_allpats": "Baseline Patent Count",
}

def _display_name(var):
    """Title-case device category names; use mapping for core vars."""
    if var in CORE_VAR_NAMES:
        return CORE_VAR_NAMES[var]
    # Device category: stored as UPPER CASE, display as Title Case
    return var.strip().title().replace("\n", " ")


# ── D.11 formatting ─────────────────────────────────────────────────────────

class _ModelEstimates:
    """The three coefficient vectors and the sample size of one fitted model.

    Read from the plain-CSV coefficient table `11d_reg_design.py` writes. It exposes the same
    attribute names (params, bse, pvalues, nobs) as a statsmodels results object, which is
    what the formatting code below expects.
    """

    __slots__ = ("params", "bse", "pvalues", "nobs")

    def __init__(self, params, bse, pvalues, nobs):
        self.params, self.bse, self.pvalues, self.nobs = params, bse, pvalues, nobs


def _load_model(name):
    """Load one model's coefficients from its non-proprietary .csv copy.

    `name` is the `model_<estimate>_<reclass>` stem; the .csv is what is read. A pickle is a
    Python- and library-version-specific format: copies written under one numpy raise
    `ModuleNotFoundError: No module named 'numpy._core.numeric'` under the pinned numpy 1.26.4,
    so no pickle is read here. The CSV carries
    exactly what these tables need (term, coef, std_err, pvalue, and a `# nobs,<N>` line).
    """
    path = TABLES_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found: the device-experience coefficients are written by "
            "code/11d_reg_design.py (step 25 of run_all.py). Run that step before this one.")
    body, nobs = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            key, _, value = line.lstrip("# ").partition(",")
            if key.strip() == "nobs" and value.strip():
                nobs = float(value)
            continue
        if line.strip():
            body.append(line)
    df = pd.read_csv(io.StringIO("\n".join(body) + "\n"))
    missing = {"term", "coef", "std_err", "pvalue"} - set(df.columns)
    if missing:
        raise KeyError(
            f"{path.name} is missing column(s) {sorted(missing)}: rerun "
            "code/11d_reg_design.py to rewrite the coefficient tables.")
    if nobs is None:
        raise KeyError(
            f"{path.name} carries no '# nobs,<N>' line, so Table D.11's sample size cannot be "
            "printed: rerun code/11d_reg_design.py to rewrite the coefficient tables.")
    idx = pd.Index(df["term"].astype(str))
    return _ModelEstimates(
        params=pd.Series(df["coef"].to_numpy(), index=idx),
        bse=pd.Series(df["std_err"].to_numpy(), index=idx),
        pvalues=pd.Series(df["pvalue"].to_numpy(), index=idx),
        nobs=nobs,
    )


def _shared_nobs(*models):
    """Read the sample size from each model's .nobs (fail-closed) and assert every column agrees,
    so the displayed N is read from the model objects. Raises if a model lacks .nobs or the
    columns disagree."""
    ns = []
    for m in models:
        if not hasattr(m, "nobs"):
            raise AssertionError(f"model {type(m).__name__} has no .nobs attribute")
        ns.append(int(round(float(m.nobs))))
    if len(set(ns)) != 1:
        raise AssertionError(f"D.11 columns disagree on sample size (model.nobs = {ns}); "
                             f"cannot display a single N -- investigate the regression samples")
    return ns[0]


def _format_d11_table(model_sae, model_pat, *, caption, label,
                       has_fda_own_accord, has_dpm, footnote, use_resizebox=False):
    """
    Format a single D.11 table (III→II or II→I) as a complete LaTeX table.
    Two columns: (1) Serious-Event Estimate, (2) Patenting Estimate.
    """
    # Determine variable ordering: core vars first, then FEs, then patents_allpats
    # N read from the model objects (fail-closed, asserts both columns agree).
    n_obs = _shared_nobs(model_sae, model_pat)
    core_order = ["exp_years", "constant", "v_serious_event"]
    if has_fda_own_accord:
        core_order.append("FDA_own_accord")
    if has_dpm:
        core_order.append("DPM")

    # Collect FE names (everything not in core + patents_allpats)
    all_params = set(model_sae.params.index) | set(model_pat.params.index)
    skip = set(core_order) | {"patents_allpats"}
    fe_vars = sorted([v for v in all_params if v not in skip])

    # Full variable order
    var_order = core_order + fe_vars + ["patents_allpats"]

    lines = []
    lines.append("\\begin{table}[h!]")
    lines.append("\\centering")
    lines.append(f"\\caption{{\\textbf{{{caption}}}}}")
    lines.append(f"\\label{{{label}}}")

    if use_resizebox:
        lines.append("\\resizebox{.62\\textwidth}{!}{\\begin{tabular}{lcc}")
    else:
        lines.append("\\begin{tabular}{lcc}")

    lines.append("\\hline")
    lines.append("\\hline")
    lines.append("\\textbf{Variable} & \\textbf{(1)} & \\textbf{(2)} \\\\")
    lines.append("\\midrule")

    for var in var_order:
        display = _display_name(var)

        # Serious events column
        if var in model_sae.params.index and var != "patents_allpats":
            coef_sae = model_sae.params[var]
            se_sae = model_sae.bse[var]
            pval_sae = model_sae.pvalues[var]
            est_str_sae = f"{coef_sae:.4f}{_stars(pval_sae)}"
            se_str_sae = f"({se_sae:.4f})"
        elif var == "patents_allpats":
            est_str_sae = "---"
            se_str_sae = "---"
        else:
            est_str_sae = ""
            se_str_sae = ""

        # Patents column
        if var in model_pat.params.index:
            coef_pat = model_pat.params[var]
            se_pat = model_pat.bse[var]
            pval_pat = model_pat.pvalues[var]
            est_str_pat = f"{coef_pat:.4f}{_stars(pval_pat)}"
            se_str_pat = f"({se_pat:.4f})"
        else:
            est_str_pat = ""
            se_str_pat = ""

        lines.append(f"{display} & {est_str_sae} & {est_str_pat} \\\\")
        lines.append(f" & {se_str_sae} & {se_str_pat} \\\\")

    lines.append("\\midrule")
    lines.append(f"N & {n_obs} & {n_obs} \\\\")
    lines.append("Serious-Event Estimate & Yes & No \\\\")
    lines.append("Patenting Estimate & No & Yes \\\\")
    lines.append("\\bottomrule")
    lines.append("")

    if use_resizebox:
        lines.append("\\end{tabular}}")
    else:
        lines.append("\\end{tabular}")

    lines.append("\\caption*{")
    lines.append("\\begin{footnotesize}" + footnote + "")
    lines.append("\\end{footnotesize}")
    lines.append("}")
    lines.append("\\end{table}")

    return "\n".join(lines)


def format_d11_tables():
    """Produce Table D.11a (III→II) and D.11b (II→I)."""
    # III→II
    m_sae_32 = _load_model("model_v_serious_est_3_2")
    m_pat_32 = _load_model("model_patent_est_3_2")

    tex_32 = _format_d11_table(
        m_sae_32, m_pat_32,
        caption="Relationship Between Impacts and Device Experience (III to II)",
        label="tab:impacts_vs_exp_3_2",
        has_fda_own_accord=True,
        has_dpm=False,
        footnote=(
            "Note: The regression relates device-level DiD estimates for "
            "(1) serious adverse events and (2) patenting activity to each "
            "device type's market age (FDA years of experience) and other "
            "covariates, including baseline patenting rates. "
            "\\textquotedblleft---\\textquotedblright\\ indicates variables "
            "excluded from a given specification. Due to limited data, fixed "
            "effects are included only for higher-risk device categories "
            "(each with $\\geq$ 2 observations); cardiovascular devices are "
            "the omitted group. To increase power, FDA-initiated "
            "reclassifications (own accord = 0) are included with a "
            "corresponding fixed effect. +, *, **, *** denote significance "
            "at 0.10, 0.05, 0.01, 0.001 levels."
        ),
    )

    path_32 = FORMATTED_DIR / "TableD11a_DeviceExperience_3_2.tex"
    with open(path_32, "w") as f:
        f.write(tex_32)
    print(f"  Wrote {path_32}")

    # II→I
    m_sae_21 = _load_model("model_v_serious_est_2_1")
    m_pat_21 = _load_model("model_patent_est_2_1")

    tex_21 = _format_d11_table(
        m_sae_21, m_pat_21,
        caption="Relationship Between Impacts and Device Experience (II to I)",
        label="tab:impacts_vs_exp_2_1",
        has_fda_own_accord=False,
        has_dpm=True,
        use_resizebox=True,
        footnote=(
            "Note: The regression relates device-level DiD estimates for "
            "(1) serious adverse events and (2) patenting activity to each "
            "device type's market age (FDA years of experience) and other "
            "covariates, including baseline patenting rates. "
            "\\textquotedblleft---\\textquotedblright\\ indicates variables "
            "excluded from a given specification. To increase power, all "
            "deregulated device types with at least one submission are "
            "included. Fixed effects for part descriptions are included, "
            "with anesthesiology devices as the omitted group. "
            "+, *, **, *** denote significance at 0.10, 0.05, 0.01, 0.001 levels."
        ),
    )

    path_21 = FORMATTED_DIR / "TableD11b_DeviceExperience_2_1.tex"
    with open(path_21, "w") as f:
        f.write(tex_21)
    print(f"  Wrote {path_21}")


# ── Safety Robustness formatting ─────────────────────────────────────────────

def format_safety_robustness_table():
    """
    Produce the Safety Robustness table by reading 06b + 06c CSV outputs.
    Output: a LaTeX fragment for \\input inside the manuscript table wrapper.
    """
    kw_path = TABLES_DIR / "safety_refined_keywords_estimates.csv"
    embed_path = TABLES_DIR / "safety_embedding_distance_estimates.csv"

    kw_df = pd.read_csv(kw_path) if kw_path.exists() else None
    embed_df = pd.read_csv(embed_path) if embed_path.exists() else None

    if kw_df is None:
        print("  WARNING: No 06b output found. Skipping safety robustness table.")
        return

    lines = []
    panel_labels = {"2_1": "A. Class II to I", "3_2": "B. Class III to II"}

    for reclass_type in ["2_1", "3_2"]:
        lines.append(f"\\textbf{{{panel_labels[reclass_type]}}} & & & \\\\")
        lines.append("\\addlinespace")

        # Embedding Distance row (from 06c)
        if embed_df is not None:
            row = embed_df[embed_df.reclass_type == reclass_type]
            if len(row) == 1:
                r = row.iloc[0]
                est = r["estimate"]
                stars, se = _stars_from_ci(est, r["ci_lower"], r["ci_upper"])
                lines.append(
                    f"\\hspace{{6mm}}Pr of any Safety Mention & Embedding Distance "
                    f"& {r['baseline_mean']:.3f} & {est:.3f}{stars} \\\\"
                )
                lines.append(
                    f" &  & ({r['baseline_std']:.3f}) & ({abs(se):.3f}) \\\\"
                )
                lines.append("\\addlinespace")

        # "Safety" Only row (from 06b)
        row = kw_df[kw_df.reclass_type == reclass_type]
        if len(row) == 1:
            r = row.iloc[0]
            est = r["estimate"]
            stars, se = _stars_from_ci(est, r["ci_lower"], r["ci_upper"])
            lines.append(
                f"\\hspace{{6mm}}Pr of any Safety Mention & ``Safety'' Only "
                f"& {r['baseline_mean']:.3f} & {est:.3f}{stars} \\\\"
            )
            lines.append(
                f" &  & ({r['baseline_std']:.3f}) & ({abs(se):.3f}) \\\\"
            )
        lines.append("\\addlinespace")

        # Sample Size row (JPE 2.2): the manuscript caption states one N per panel. It is
        # printed from the estimating panel's own observation count, emitted by
        # 06b_validate_safety.emit_safety_panel_sizes().
        if "n_obs" not in kw_df.columns:
            raise KeyError(
                "safety_refined_keywords_estimates.csv has no 'n_obs' column: rerun "
                "code/06b_validate_safety.py so the panel sample sizes are emitted "
                "(they back the safety-robustness table caption)")
        row = kw_df[kw_df.reclass_type == reclass_type]
        if len(row) == 1 and pd.notna(row.iloc[0]["n_obs"]):
            lines.append(
                f"\\hspace{{6mm}}Sample Size &  &  & {int(row.iloc[0]['n_obs']):,} \\\\"
            )
            lines.append("\\addlinespace")
        lines.append("")

    tex_content = "\n".join(lines) + "\n"
    tex_path = FORMATTED_DIR / "TableD12_SafetyRobustness.tex"
    with open(tex_path, "w") as f:
        f.write(tex_content)
    print(f"  Wrote {tex_path}")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Formatting Tables D.11 and D.12 from the estimate CSVs...")
    print()
    print("=== Table D.11 (Device Experience) ===")
    format_d11_tables()
    print()
    print("=== Safety Robustness Table ===")
    format_safety_robustness_table()
    print()
    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
