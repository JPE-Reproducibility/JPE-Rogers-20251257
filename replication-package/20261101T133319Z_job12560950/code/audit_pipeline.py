# -*- coding: utf-8 -*-
"""
Replication Package Audit & Manuscript-vs-Replication Comparison
================================================================

Three deliverables:
  A. Verify every manuscript figure/table has a producing replication script
  B. Verify every non-source derived data file has a generating script
  C. Generate a side-by-side HTML comparing manuscript outputs vs replication outputs

Usage:
    cd replication_package && python code/audit_pipeline.py
    open output/replication_audit.html

The pipeline runs audit_pipeline_current.py, a thin wrapper over this module; it
is what run_all.py executes as step 36.
"""

import os
import re
import sys
import hashlib
import base64
from pathlib import Path
from collections import OrderedDict
import difflib

# ============================================================================
# Path setup
# ============================================================================

# The replication package root is one level up from code/
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

# Key directories
REPL_FIGURES = ROOT_DIR / "output" / "figures"
REPL_TABLES_FMT = ROOT_DIR / "output" / "tables" / "Formatted"
REPL_TABLES = ROOT_DIR / "output" / "tables"
DERIVED_DIR = ROOT_DIR / "data" / "derived"
RAW_DIR = ROOT_DIR / "data" / "raw"

# Manuscript paths. Default resolution is package-relative so the audit is
# portable for clean-room reviewers. The v4 wrapper (audit_pipeline_v4.py)
# overrides MS_TEX to the active manuscript inside paper/.
PROJECT_ROOT = ROOT_DIR.parent
MS_FIGURES = ROOT_DIR / "output" / "figures"
MS_TABLES_FMT = ROOT_DIR / "output" / "tables" / "Formatted"
MS_TEX = ROOT_DIR / "paper" / "JPE_submission_v4.tex"

# Written inside the package, not /tmp: the report is a package output, and /tmp is shared and
# not writable in every container. audit_pipeline_current.py sets the same path explicitly.
OUTPUT_HTML = ROOT_DIR / "output" / "replication_audit.html"


# ============================================================================
# Known discrepancy notes (displayed in HTML when status is DIFFERS)
# ============================================================================
# filename -> note shown next to a DIFFERS status; empty, no table currently carries a note.
KNOWN_NOTES = {}


# ============================================================================
# Part A: Figure/Table → Script Mapping
# ============================================================================

# Every active (uncommented) figure referenced in the manuscript,
# mapped to the replication script that produces it.
FIGURE_SCRIPT_MAP = OrderedDict([
    # --- Main text ---
    # Fig 1
    ("Deregulation_May31_23_Paper.png",          "11g_descriptive_figures.py (copy from data/raw/)"),
    # Fig 2 panels (overpic composites + standalone)
    ("3_2_nolog_real_pats_oct22_24.png",          "04_event_studies.py"),
    ("3_2_nolog_dev_count_oct22_24.png",          "04_event_studies.py"),
    ("2_1_nolog_real_pats_oct22_24.png",          "04_event_studies.py"),
    ("2_1_nolog_dev_count_solo.png",              "04_event_studies.py"),
    # Fig 3 panels
    ("3_2_nolog_unique_firms_solo_CTs.png",       "04_event_studies.py"),
    ("2_1_nolog_unique_firms_oct22_24.png",        "04_event_studies.py"),
    ("3_2_nolog_Price_solo_CTs_sept20_25.png",    "05_price_analysis.py"),
    ("2_1_nolog_Price_solo_CTs_sept20_25.png",    "05_price_analysis.py"),
    # Fig 4 panels (adverse events event study)
    ("3_2_nolog_v_serious_oct22_24.png",          "04_event_studies.py"),
    ("2_1_nolog_v_serious_oct22_24.png",          "04_event_studies.py"),
    # Fig 5 panels (safety by asset tercile)
    ("2_1_Safety_Top_Decile_Present_oct22_24.png", "07_firm_heterogeneity.py"),
    ("2_1_Deaths_Top_Decile_oct22_24.png",         "07_firm_heterogeneity.py"),
    # --- Appendix ---
    # Fig D.1
    ("Distribution_of_3_2_over_years.png",        "11f_reg_background.py"),
    ("Distribution_of_2_1_over_years.png",        "11f_reg_background.py"),
    # Fig D.2
    ("Data_new_latest.png",                       "11g_descriptive_figures.py (copy from data/raw/)"),
    # Fig D.5
    ("variety_3_2.png",                           "11a_product_variety.py"),
    ("variety_2_1.png",                           "11a_product_variety.py"),
    # Fig D.6
    ("LBDEstimation.png",                         "08_lbd_simulation.py"),
    # Fig D.7
    ("3_2_smallvlarge.png",                       "07_firm_heterogeneity.py"),
    ("2_1_smallvlarge.png",                       "07_firm_heterogeneity.py"),
    # Fig D.8
    ("Safety_emphasis_raw_trends.png",            "06a_safety_analysis.py"),
    ("2_1_nolog_safety_prop_oct22_24.png",        "04_event_studies.py"),
    # Fig D.9
    ("2_1_nolog_v_serious_normalizable_oct22_24.png", "04_event_studies.py"),
    ("2_1_nolog_v_serious_restrict_oct22_24.png",     "04_event_studies.py"),
    # Fig D.10
    ("cases_preemption.png",                      "11c_liability.py"),
    ("Bankruptcy_1996_raw_trend.png",             "11c_liability.py"),
    # Fig D.11
    ("exp_vs_impact_v_serious_est_3_2.png",       "11d_reg_design.py"),
    ("exp_vs_impact_patent_est_3_2.png",          "11d_reg_design.py"),
    ("exp_vs_impact_v_serious_est_2_1.png",       "11d_reg_design.py"),
    ("exp_vs_impact_patent_est_2_1.png",          "11d_reg_design.py"),
    # Fig D.12
    ("Distribution_of_3_over_years.png",          "11d_reg_design.py"),
    ("Distribution_of_2_over_years.png",          "11d_reg_design.py"),
    # Fig D.13
    ("3_2_nolog_patents_pats_nodrugs_oct22_24.png", "04_event_studies.py"),
    # Fig D.14
    ("Recalls_1996_raw_trend.png",                "11b_recall_analysis.py"),
    ("Recalls_1996_raw_trend_intuitive.png",      "11b_recall_analysis.py"),
    ("2_1_no_log_recalls_1996.png",               "11b_recall_analysis.py"),
    # Fig D.15
    ("2_1_no_logv_serious_2016_oct22_24.png",     "11b_recall_analysis.py"),
    ("Recalls_2017.png",                          "11b_recall_analysis.py"),
    ("Recalls_2017_raw_trends.png",               "11b_recall_analysis.py"),
    # Fig D.16
    ("NewFirmsPatenting_2017.png",                "11e_new_entry_2015.py"),
    # Fig D.17
    ("2_1_nolog_v_serious_voluntary_oct22_24.png", "04_event_studies.py"),
    ("2_1_nolog_v_serious_manuf_oct22_24.png",     "04_event_studies.py"),
])

# Every active (uncommented) \input table in the manuscript
TABLE_SCRIPT_MAP = OrderedDict([
    # --- Main text (Table 1-3) ---
    ("PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex",          "10_table_formatting.py"),
    ("PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex",          "10_table_formatting.py"),
    ("RegTable_Prices_3_2_sep25.tex",                            "05_price_analysis.py"),
    ("PaperRegTable3_2_MarketComposition_NoLog_oct22_24.tex",   "10_table_formatting.py"),
    ("RegTable_Prices_2_1_sep25.tex",                            "05_price_analysis.py"),
    ("PaperRegTable2_1_MarketComposition_NoLog_oct22_24.tex",   "10_table_formatting.py"),
    ("PaperRegTableSafety_IIItoII_NoLog.tex",                   "06a_safety_analysis.py"),
    ("PaperRegTable3_2_AdverseEvent_NoLog_oct22_24.tex",        "10_table_formatting.py"),
    ("PaperRegTableSafety_IItoI_NoLog.tex",                     "06a_safety_analysis.py"),
    ("PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex",        "10_table_formatting.py"),
    # --- Appendix: BJS imputation ---
    ("DIDimpute_PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex",          "10_table_formatting.py"),
    ("DIDimpute_PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex",          "10_table_formatting.py"),
    ("DIDimpute_PaperRegTable3_2_MarketComposition_NoLog_oct22_24.tex",   "10_table_formatting.py"),
    ("DIDimpute_PaperRegTable2_1_MarketComposition_NoLog_oct22_24.tex",   "10_table_formatting.py"),
    ("DIDimpute_PaperRegTable3_2_AdverseEvent_NoLog_oct22_24.tex",        "10_table_formatting.py"),
    ("DIDimpute_PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex",        "10_table_formatting.py"),
    # --- Appendix: Log ---
    ("PaperRegTable3_2_Main_Panel_Log_oct22_24.tex",            "10_table_formatting.py"),
    ("PaperRegTable2_1_Main_Panel_Log_oct22_24.tex",            "10_table_formatting.py"),
    ("PaperRegTable3_2_MarketComposition_Log_oct22_24.tex",     "10_table_formatting.py"),
    ("PaperRegTable2_1_MarketComposition_Log_oct22_24.tex",     "10_table_formatting.py"),
    ("PaperRegTable3_2_AdverseEvent_Log_oct22_24.tex",          "10_table_formatting.py"),
    ("PaperRegTable2_1_AdverseEvent_Log_oct22_24.tex",          "10_table_formatting.py"),
    # --- Appendix: Poisson ---
    ("PaperRegTable3_2_Main_Panel_NoLog_poisson_oct22_24.tex",          "10_table_formatting.py"),
    ("PaperRegTable2_1_Main_Panel_NoLog_poisson_oct22_24.tex",          "10_table_formatting.py"),
    ("PaperRegTable3_2_MarketComposition_NoLog_poisson_oct22_24.tex",   "10_table_formatting.py"),
    ("PaperRegTable2_1_MarketComposition_NoLog_poisson_oct22_24.tex",   "10_table_formatting.py"),
    ("PaperRegTable3_2_AdverseEvent_NoLog_poisson_oct22_24.tex",        "10_table_formatting.py"),
    ("PaperRegTable2_1_AdverseEvent_NoLog_poisson_oct22_24.tex",        "10_table_formatting.py"),
    # --- Appendix: Nozero ---
    ("PaperRegTable3_2_Main_Panel_NoLog_No0_oct22_24.tex",          "10_table_formatting.py"),
    ("PaperRegTable2_1_Main_Panel_NoLog_No0_oct22_24.tex",          "10_table_formatting.py"),
    ("PaperRegTable3_2_MarketComposition_NoLog_No0_oct22_24.tex",   "10_table_formatting.py"),
    ("PaperRegTable2_1_MarketComposition_NoLog_No0_oct22_24.tex",   "10_table_formatting.py"),
    ("PaperRegTable3_2_AdverseEvent_NoLog_No0_oct22_24.tex",        "10_table_formatting.py"),
    ("PaperRegTable2_1_AdverseEvent_NoLog_No0_oct22_24.tex",        "10_table_formatting.py"),
    # --- Appendix: Price DID impute ---
    ("DIDimpute_RegTable_Prices_3_2_sep25.tex",                  "05_price_analysis.py"),
    ("DIDimpute_RegTable_Prices_2_1_sep25.tex",                  "05_price_analysis.py"),
    # --- Appendix: Spillovers ---
    ("PaperRegTableSpillovers_3_2_Spillovers_NoLog.tex",        "10_table_formatting.py"),
    ("PaperRegTableSpillovers_2_1_Spillovers_NoLog.tex",        "10_table_formatting.py"),
])

# Additional replication-produced tables NOT \input'd but relevant
# (written by programs, as .tex or .csv)
EXTRA_REPL_TABLES = OrderedDict([
    ("Table_1_summary_stats.tex",            "09_summary_stats.py"),
    ("Table_1_summary_stats.csv",            "09_summary_stats.py"),
    ("Table_D14_summary_stats_by_class.tex", "09_summary_stats.py"),
    ("Table_D14_summary_stats_by_class.csv", "09_summary_stats.py"),
    ("TableD11a_DeviceExperience_3_2.tex",   "11d_reg_design.py"),
    ("TableD11b_DeviceExperience_2_1.tex",   "11d_reg_design.py"),
    ("TableD12_SafetyRobustness.tex",        "10b_format_remaining_tables.py"),
    ("TableD15_RestrictedSamples.tex",       "13_restricted_samples.py"),
    ("TableD16_BreakthroughPatents.tex",     "14_breakthrough_patents.py"),
    ("Table_D11_reg_design.tex",             "11d_reg_design.py"),
    ("Table_D12_petitioned_vs_fda.tex",      "11d_reg_design.py"),
    # Program-generated computational appendix tables (verified producer: 10c generate_*)
    ("TableD1_SampleConstruction.tex",       "10c_generate_appendix_tables.py"),
    ("TableD11_Utilization.tex",             "10c_generate_appendix_tables.py"),
    ("TableD15_CostBenefit.tex",             "10c_generate_appendix_tables.py"),
])

# Mapping of extra replication tables to their \label in the manuscript .tex.
# The script extracts the \begin{table}...\end{table} block containing this label.
# "body_only" = True means the replication output is just the body rows (no table env).
INLINE_TABLE_LABELS = {
    "Table_1_summary_stats.tex":            {"label": "tab:SummaryStatistics",            "body_only": False},
    "Table_D14_summary_stats_by_class.tex": {"label": "tab:SummaryStatistics_AllClasses_Reorg", "body_only": False},
    "TableD11a_DeviceExperience_3_2.tex":   {"label": "tab:impacts_vs_exp_3_2",          "body_only": False},
    "TableD11b_DeviceExperience_2_1.tex":   {"label": "tab:impacts_vs_exp_2_1",          "body_only": False},
    "TableD12_SafetyRobustness.tex":        {"label": "tab:ProbabilitySafetyMentionEffects_Robustness", "body_only": True},
    "TableD15_RestrictedSamples.tex":       {"label": "tab:Innovation_nodrugs_A61only",  "body_only": True},
    "TableD16_BreakthroughPatents.tex":     {"label": "tab:BreakthroughPatentsEffects",  "body_only": True},
}

# Additional replication figures not directly \includegraphics'd but produced
EXTRA_REPL_FIGURES = OrderedDict([
    ("Figure_D6_lbd_simulation.pdf",            "08_lbd_simulation.py"),
    ("Figure_D6b_experience_curves.pdf",        "08_lbd_simulation.py"),
    ("Figure_D14_recall_2015_L.png",            "11b_recall_analysis.py"),
    ("Figure_D14_recall_2015_H.png",            "11b_recall_analysis.py"),
    ("Figure_D14_recall_2015_D.png",            "11b_recall_analysis.py"),
    ("Event_to_RegScrutiny.png",                "11g_descriptive_figures.py"),
    # Figure 1 contact-lens case study (verified producer: writes ContactLens_*.png)
    ("ContactLens_patents.png",                 "12_contact_lens_case_study.py"),
    ("ContactLens_submissions.png",             "12_contact_lens_case_study.py"),
    ("ContactLens_firms.png",                   "12_contact_lens_case_study.py"),
    # Event-study coefplots: 04 builds "<reclass>_nolog_<outcome>_oct22_24.png" (see 04:727-810)
    ("3_2_nolog_real_pats_petitioned_oct22_24.png",  "04_event_studies.py"),
    ("3_2_nolog_absnew_firm_count_oct22_24.png",     "04_event_studies.py"),
    ("3_2_nolog_firm_expansion_oct22_24.png",        "04_event_studies.py"),
    ("2_1_nolog_firm_expansion_patents_oct22_24.png","04_event_studies.py"),
    ("3_2_nolog_firm_expansion_patents_oct22_24.png","04_event_studies.py"),
    # LBD product-count estimation figure
    ("LBDEstimation_ProductCount.png",          "08_lbd_simulation.py"),
])


# ============================================================================
# Producer resolution + content validation (F10)
# ============================================================================

def figure_producer(fname):
    """Generating script for a manuscript figure, consulting BOTH the primary and the
    EXTRA maps. 'UNKNOWN' means no known producer -> a provenance gap (main() fails)."""
    return FIGURE_SCRIPT_MAP.get(fname) or EXTRA_REPL_FIGURES.get(fname) or "UNKNOWN"


def table_producer(fname):
    """Generating script for a manuscript table (primary + EXTRA maps). 'UNKNOWN' = gap."""
    return TABLE_SCRIPT_MAP.get(fname) or EXTRA_REPL_TABLES.get(fname) or "UNKNOWN"


_IMAGE_MAGIC = (b"\x89PNG\r\n\x1a\n", b"%PDF", b"\xff\xd8\xff", b"GIF8")
# Raster exhibits are decoded and must show real content (size and magic bytes
# alone are not sufficient). Calibration (2026-09-15, the 58 shipped PNGs, on a
# 512-px thumbnail): the smallest share of pixels differing from the dominant colour was 3.76% and the fewest
# distinct colours 379; an all-white or all-black image scores 0% and 1 colour, a single dark pixel 0.001%.
_MIN_NONBACKGROUND_SHARE = 0.005
_MIN_DISTINCT_COLOURS = 16
_MIN_PDF_PAINT_OPS = 10


def _raster_content_problem(path):
    """None if the image shows real content, else why not (blank, near-blank, or undecodable)."""
    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        return f"cannot validate image content without Pillow and numpy ({e})"
    try:
        with Image.open(path) as im:
            im = im.convert("RGBA")
            flat = Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im).convert("RGB")
        flat.thumbnail((512, 512))
        px = np.asarray(flat).reshape(-1, 3).astype(np.int16)
    except Exception as e:  # truncated or undecodable image data
        return f"undecodable image ({e})"
    colours, counts = np.unique(px, axis=0, return_counts=True)
    background = colours[counts.argmax()]
    share = float((np.abs(px - background).max(axis=1) > 24).mean())
    if share < _MIN_NONBACKGROUND_SHARE or len(colours) < _MIN_DISTINCT_COLOURS:
        return (f"blank or near-blank image: {share:.3%} of pixels differ from the background colour, "
                f"{len(colours)} distinct colours")
    return None


def _pdf_content_problem(path):
    """None if the PDF's content streams paint something, else why not. No PDF exhibit ships today."""
    import re
    import zlib
    ops = 0
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", path.read_bytes(), re.S):
        body = m.group(1)
        try:
            body = zlib.decompress(body)
        except zlib.error:
            pass
        ops += len(re.findall(rb"(?<![A-Za-z])(?:re|l|c|v|y|Tj|TJ|Do)(?![A-Za-z])", body))
    return None if ops >= _MIN_PDF_PAINT_OPS else f"blank or near-blank PDF: {ops} painting operators"


def figure_content_ok(path):
    """A present figure must show real content: not a zero-byte stub, a truncated or placeholder file, or a
    valid but blank or near-blank image. Content validation: existence is not validity.
    Returns (ok, reason_if_not)."""
    try:
        size = path.stat().st_size
        if size < 128:
            return False, f"only {size} bytes (stub/placeholder)"
        with open(path, "rb") as fh:
            head = fh.read(8)
    except OSError as e:
        return False, f"unreadable: {e}"
    if not any(head.startswith(m) for m in _IMAGE_MAGIC):
        return False, "no PNG/PDF/JPG/GIF magic bytes (corrupt or not an image)"
    problem = _pdf_content_problem(path) if head.startswith(b"%PDF") else _raster_content_problem(path)
    return (False, problem) if problem else (True, None)


def table_content_ok(path):
    """A present table exhibit must carry actual tabular content, not an empty stub.
    .tex/fragment: an alignment '&' or row break '\\\\' AND at least one digit.
    .csv: >= 2 non-empty lines. Returns (ok, reason_if_not)."""
    try:
        if path.stat().st_size == 0:
            return False, "zero-byte file"
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return False, f"unreadable: {e}"
    if path.suffix.lower() == ".csv":
        rows = [ln for ln in text.splitlines() if ln.strip()]
        return (True, None) if len(rows) >= 2 else (False, "fewer than 2 non-empty rows")
    has_struct = ("&" in text) or ("\\\\" in text)
    has_num = any(c.isdigit() for c in text)
    if has_struct and has_num:
        return True, None
    return False, "no tabular rows/numbers (empty or placeholder table)"


# ============================================================================
# Part B: Derived Data → Script Mapping
# ============================================================================

# Map derived data files to their generating scripts.
# Categories: GENERATED, PROPRIETARY, PRE-TRAINED, RAW-INPUT, GAP
DERIVED_FILE_MAP = {
    # --- Generated by gen_01 ---
    "Full_sample.csv":                              ("GENERATED", "gen_01_main_panels.py"),
    "intuitive_2_1_oct22_24.csv":                   ("GENERATED", "gen_01_main_panels.py"),
    "intuitive_3_2_oct22_24_similarity.csv":        ("GENERATED", "gen_01_main_panels.py"),
    "later_treated_2_1_oct22_24.csv":               ("GENERATED", "gen_01_main_panels.py"),
    "later_treated_3_2_oct22_24.csv":               ("GENERATED", "gen_01_main_panels.py"),
    "spillovers_2_1_oct22_24.csv":                  ("GENERATED", "gen_01_main_panels.py"),
    "intuitive_spillovers_3_2_oct22_24.csv":        ("GENERATED", "gen_01_main_panels.py"),
    "all_patents_w_xi_oct22_24.csv":                ("GENERATED", "gen_01_main_panels.py"),
    "safety_vars_allpats.csv":                      ("GENERATED", "gen_01_main_panels.py"),
    "safety_vars_allpats_v2.csv":                   ("GENERATED", "gen_01_main_panels.py"),
    "safety_vars_allpats_updated_v2.csv":           ("GENERATED", "gen_01_main_panels.py"),
    "safety_tagged_patents.csv":                    ("GENERATED", "gen_01_main_panels.py"),
    # --- Generated by 02_match_samples.py (Mahalanobis match loop) ---
    "matched_sample_2_1_onepat.csv":                ("GENERATED", "02_match_samples.py"),
    "matched_sample_2_1_onepat_innovation.csv":     ("GENERATED", "02_match_samples.py"),
    "matched_sample_2_1_onepat_innovation_quality.csv": ("GENERATED", "02_match_samples.py"),
    "matched_sample_3_2_onepat.csv":                ("GENERATED", "02_match_samples.py"),
    "matched_sample_3_2_onepat_innovation.csv":     ("GENERATED", "02_match_samples.py"),
    "matched_sample_3_2_onepat_innovation_quality.csv": ("GENERATED", "02_match_samples.py"),
    "matched_sample_3_2_onepat_innovation_petitioned.csv": ("GENERATED", "02_match_samples.py"),
    "matched_pairs_intuitive_2_1.csv":              ("GENERATED", "gen_01_main_panels.py"),
    # --- Generated by gen_03 / gen_03b ---
    "LBD_ApprovalTime_Both_oct22_24.csv":           ("GENERATED", "gen_03_lbd.py"),
    "AD_data_applicant_df_oct22_24.csv":            ("GENERATED", "gen_03b_lbd_clusters.py"),
    "AD_data_applicant_df2_oct22_24.csv":           ("GENERATED", "gen_03b_lbd_clusters.py"),
    # Written by gen_01 phase 2a; gen_03/gen_03b are its READERS, not its producers.
    "Applicant_Device_data.csv":                    ("GENERATED", "gen_01_main_panels.py"),
    # --- Generated by gen_04 ---
    "data_2_1_full.parquet":                        ("GENERATED", "gen_04_parquets.py"),
    "data_2_1_latertreat.parquet":                  ("GENERATED", "gen_04_parquets.py"),
    "data_2_1_intuitive.parquet":                   ("GENERATED", "gen_04_parquets.py"),
    "data_2_1_spillovers.parquet":                  ("GENERATED", "gen_04_parquets.py"),
    # --- Generated by gen_05 ---
    "Adverse_fsize_ready_all4_oct22_24.csv":        ("GENERATED", "gen_05_adverse_fsize.py"),
    # --- Generated by gen_06 ---
    "adverse_event_panel_by_PC_full.csv":           ("GENERATED", "gen_06_adv_2020.py"),
    "constrained_adv_event_new_sept25.csv":         ("GENERATED", "gen_06_adv_2020.py"),
    "constrained_adv_event_new_sept25_3_2.csv":     ("GENERATED", "gen_06_adv_2020.py"),
    "Adv_Event_2020_2022.csv":                      ("GENERATED", "gen_06_adv_2020.py"),
    # --- Generated by gen_07 ---
    "all_adv_events_w_permno5.csv":                 ("GENERATED", "gen_07_adverse_permno.py"),
    "All_Adverse_Event_Manufacturers_Deduped.csv":  ("GENERATED", "gen_07_adverse_permno.py"),
    # --- Generated by 02_match_samples ---
    # (matched samples are also generated by gen_02; listing gen_02 as primary)
    # --- Generated by 06a ---
    "safety_did_analysis.csv":                      ("GENERATED", "06a_safety_analysis.py"),
    "safety_did_analysis_3_2.csv":                  ("GENERATED", "06a_safety_analysis.py"),
    # --- Generated by 11a ---
    "frequency_df_2to1_variety.csv":                ("GENERATED", "11a_product_variety.py"),
    "frequency_df_3to2_variety.csv":                ("GENERATED", "11a_product_variety.py"),
    # --- Proprietary (MarketScan) ---
    "outpatient_combined_censored.csv":             ("PROPRIETARY", "MarketScan (proprietary)"),
    # --- Raw inputs (not generated by pipeline) ---
    "RegNum_Factorized_Synth.csv":                  ("RAW-INPUT", "External/pre-computed"),
    # --- Pre-trained models ---
    "word2vec_patent_corpus.model":                 ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "word2vec_patent_corpus.model.syn1neg.npy":     ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "word2vec_patent_corpus.model.wv.vectors.npy":  ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_2to1.model":                               ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_3to2.model":                               ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_bigram_2to1.model":                        ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_bigram_3to2.model":                        ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_trigram_2to1.model":                       ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_trigram_3to2.model":                       ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_dictionary_2to1.dict":                     ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    "lda_dictionary_3to2.dict":                     ("PRE-TRAINED", "11a_product_variety.py (pre-trained artifact)"),
    # --- Dedupe settings (pre-trained) ---
    "dedupe_settings/dedupe_dataframe_learned_settings":         ("PRE-TRAINED", "gen_03b_lbd_clusters.py (pre-trained)"),
    "dedupe_settings/dedupe_dataframe_training.json":            ("PRE-TRAINED", "gen_03b_lbd_clusters.py (pre-trained)"),
    "dedupe_settings/adverse_events/dedupe_dataframe_learned_settings": ("PRE-TRAINED", "gen_07_adverse_permno.py (pre-trained)"),
    "dedupe_settings/adverse_events/dedupe_dataframe_training.json":    ("PRE-TRAINED", "gen_07_adverse_permno.py (pre-trained)"),
    "dedupe_settings_applicant/dedupe_dataframe_learned_settings":      ("PRE-TRAINED", "gen_03b_lbd_clusters.py (pre-trained)"),
    "dedupe_settings_applicant/dedupe_dataframe_training.json":         ("PRE-TRAINED", "gen_03b_lbd_clusters.py (pre-trained)"),
}


# ============================================================================
# Staleness detection: script -> input data dependencies
# ============================================================================
# For each analysis script, list the derived/raw data files it reads.
# An output is STALE if *any* of these inputs (or the script itself) is newer.

SCRIPT_DATA_DEPS = {
    "04_event_studies.py": [
        # Matched samples (main input)
        "derived/matched_sample_3_2_onepat.csv",
        "derived/matched_sample_3_2_onepat_innovation.csv",
        "derived/matched_sample_3_2_onepat_innovation_quality.csv",
        "derived/matched_sample_3_2_onepat_innovation_petitioned.csv",
        "derived/matched_sample_2_1_onepat.csv",
        "derived/matched_sample_2_1_onepat_innovation.csv",
        "derived/matched_sample_2_1_onepat_innovation_quality.csv",
        # Intuitive/later-treated/spillover samples
        "derived/intuitive_2_1_oct22_24.csv",
        "derived/intuitive_3_2_oct22_24_similarity.csv",
        "derived/later_treated_2_1_oct22_24.csv",
        "derived/later_treated_3_2_oct22_24.csv",
        "derived/spillovers_2_1_oct22_24.csv",
        "derived/intuitive_spillovers_3_2_oct22_24.csv",
    ],
    "05_price_analysis.py": [
        "derived/matched_sample_3_2_onepat.csv",
        "derived/matched_sample_2_1_onepat.csv",
        "derived/outpatient_combined_censored.csv",
    ],
    "06a_safety_analysis.py": [
        "derived/safety_vars_allpats.csv",
        "derived/all_patents_w_xi_oct22_24.csv",
        "derived/Full_sample.csv",
    ],
    "06b_validate_safety.py": [
        "derived/safety_did_analysis.csv",
        "derived/safety_did_analysis_3_2.csv",
    ],
    "06c_validate_safety_embed.py": [
        "derived/safety_did_analysis.csv",
        "derived/safety_did_analysis_3_2.csv",
    ],
    "07_firm_heterogeneity.py": [
        "derived/Adverse_fsize_ready_all4_oct22_24.csv",
        "derived/all_adv_events_w_permno5.csv",
        "derived/safety_vars_allpats.csv",
        "derived/Full_sample.csv",
    ],
    "08_lbd_simulation.py": [
        "derived/LBD_ApprovalTime_Both_oct22_24.csv",
    ],
    "09_summary_stats.py": [
        "derived/Full_sample.csv",
        "derived/matched_sample_3_2_onepat.csv",
        "derived/matched_sample_2_1_onepat.csv",
        "derived/all_patents_w_xi_oct22_24.csv",
        "derived/Adverse_fsize_ready_all4_oct22_24.csv",
        "derived/LBD_ApprovalTime_Both_oct22_24.csv",
    ],
    "10_table_formatting.py": [
        # Reads CSV estimate files from output/tables/
        # Those are produced by 03a/03b estimation scripts
        # We check against script mtime as proxy
    ],
    "10b_format_remaining_tables.py": [],
    "11a_product_variety.py": [
        "derived/Full_sample.csv",
        "derived/all_patents_w_xi_oct22_24.csv",
        "derived/safety_tagged_patents.csv",
    ],
    "11b_recall_analysis.py": [
        "derived/matched_sample_2_1_onepat.csv",
        "derived/Full_sample.csv",
    ],
    "11c_liability.py": [
        "derived/Full_sample.csv",
    ],
    "11d_reg_design.py": [
        "derived/Full_sample.csv",
        "derived/matched_sample_3_2_onepat.csv",
        "derived/matched_sample_2_1_onepat.csv",
        "derived/Adverse_fsize_ready_all4_oct22_24.csv",
    ],
    "11e_new_entry_2015.py": [
        "derived/Full_sample.csv",
    ],
    "11f_reg_background.py": [
        "derived/Full_sample.csv",
    ],
    "11g_descriptive_figures.py": [],
    "13_restricted_samples.py": [
        "derived/matched_sample_3_2_onepat.csv",
        "derived/matched_sample_2_1_onepat.csv",
    ],
    "14_breakthrough_patents.py": [
        "derived/matched_sample_3_2_onepat.csv",
        "derived/matched_sample_2_1_onepat.csv",
        "derived/all_patents_w_xi_oct22_24.csv",
    ],
}


def check_staleness(output_path, script_name):
    """Check if output_path is stale relative to its script and data inputs.

    Returns (is_stale, newest_input_name, newest_input_mtime, output_mtime).
    """
    if not output_path.exists():
        return False, None, None, None

    output_mtime = output_path.stat().st_mtime

    # Check script itself
    script_path = SCRIPT_DIR / script_name.split(" ")[0]  # strip any "(copy ...)" suffix
    if not script_path.exists():
        # Try in 00_generate_data/
        script_path = SCRIPT_DIR / "00_generate_data" / script_name.split(" ")[0]

    newest_name = None
    newest_mtime = 0

    if script_path.exists():
        smtime = script_path.stat().st_mtime
        if smtime > newest_mtime:
            newest_mtime = smtime
            newest_name = script_name.split(" ")[0]

    # Check config.py (affects all scripts)
    config_path = ROOT_DIR / "config.py"
    if config_path.exists():
        cmtime = config_path.stat().st_mtime
        if cmtime > newest_mtime:
            newest_mtime = cmtime
            newest_name = "config.py"

    # Check data dependencies
    base_script = script_name.split(" ")[0]
    deps = SCRIPT_DATA_DEPS.get(base_script, [])
    data_dir = ROOT_DIR / "data"
    for dep in deps:
        dep_path = data_dir / dep
        if dep_path.exists():
            dmtime = dep_path.stat().st_mtime
            if dmtime > newest_mtime:
                newest_mtime = dmtime
                newest_name = dep

    is_stale = newest_mtime > output_mtime
    return is_stale, newest_name, newest_mtime, output_mtime


def format_mtime(ts):
    """Format a timestamp as a readable date string."""
    if ts is None:
        return "-"
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%b %d %H:%M")


# ============================================================================
# Helper functions
# ============================================================================

def md5(path):
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def file_to_base64(path):
    """Read a PNG/PDF file and return base64 data URI for HTML embedding."""
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf",
    }.get(suffix, "application/octet-stream")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"


def read_text(path):
    """Read text file, return contents or None if missing."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, IsADirectoryError):
        return None


def extract_table_by_label(tex_text, label, body_only=False):
    """Extract a \\begin{table}...\\end{table} block containing the given \\label.

    If body_only=True, strip the table environment and return only the data rows
    between \\midrule/\\hline and \\bottomrule/\\end{tabular}.
    """
    lines = tex_text.splitlines()
    # Find the line with \label{<label>}
    label_idx = None
    for i, line in enumerate(lines):
        if "\\label{" + label + "}" in line:
            label_idx = i
            break
    if label_idx is None:
        return None

    # Search backwards for \begin{table}
    start_idx = label_idx
    for i in range(label_idx, -1, -1):
        if "\\begin{table}" in lines[i]:
            start_idx = i
            break

    # Search forwards for \end{table}
    end_idx = label_idx
    for i in range(label_idx, len(lines)):
        if "\\end{table}" in lines[i]:
            end_idx = i
            break

    full_table = "\n".join(lines[start_idx:end_idx + 1])

    if not body_only:
        return full_table

    # Extract body rows: content between the header rule and \bottomrule
    table_lines = lines[start_idx:end_idx + 1]
    body_lines = []
    in_body = False
    # Find start of data: after the last \hline or \midrule before data
    # Find end: \bottomrule or \end{tabular}
    hline_count = 0
    for line in table_lines:
        stripped = line.strip()
        if stripped in ("\\hline", "\\midrule", "\\hline \\hline", "\\hline\\hline"):
            hline_count += 1
            if hline_count >= 2:  # After column headers
                in_body = True
                continue
        if in_body:
            if "\\bottomrule" in stripped or "\\end{tabular}" in stripped:
                break
            # Skip \caption, \label, \begin/\end commands
            if any(cmd in stripped for cmd in ("\\caption", "\\label",
                                               "\\begin{", "\\end{",
                                               "\\resizebox", "\\centering")):
                continue
            body_lines.append(line)

    return "\n".join(body_lines) if body_lines else full_table


def html_diff(text_a, text_b, label_a="Manuscript", label_b="Replication"):
    """Generate a side-by-side HTML table with green (match) / red (differ) rows."""
    import html as html_mod
    if text_a is None:
        return '<span class="missing">Manuscript file missing</span>'
    if text_b is None:
        return '<span class="missing">Replication file missing</span>'
    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    # Pad to equal length
    max_len = max(len(lines_a), len(lines_b))
    lines_a += [""] * (max_len - len(lines_a))
    lines_b += [""] * (max_len - len(lines_b))

    rows = []
    for i, (la, lb) in enumerate(zip(lines_a, lines_b), 1):
        if la == lb:
            bg = "#d4edda"  # green — match
        else:
            bg = "#f8d7da"  # red — differ
        esc_a = html_mod.escape(la)
        esc_b = html_mod.escape(lb)
        rows.append(
            f'<tr style="background:{bg}">'
            f'<td style="text-align:right;color:#888;width:30px">{i}</td>'
            f'<td>{esc_a}</td>'
            f'<td>{esc_b}</td>'
            f'</tr>'
        )

    return (
        f'<table class="diff-table" style="table-layout:fixed;width:100%">'
        f'<colgroup><col style="width:40px"><col style="width:50%"><col style="width:50%"></colgroup>'
        f'<thead><tr><th>#</th><th>{label_a}</th><th>{label_b}</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def compare_status(ms_path, repl_path):
    """Return (status, detail) comparing two files."""
    ms_exists = ms_path.exists() if ms_path else False
    repl_exists = repl_path.exists() if repl_path else False
    if not ms_exists and not repl_exists:
        return "BOTH-MISSING", "Neither file found"
    if not ms_exists:
        return "MS-MISSING", "Manuscript file missing"
    if not repl_exists:
        return "REPL-MISSING", "Replication file missing"
    if md5(ms_path) == md5(repl_path):
        return "MATCH", "Byte-identical"
    return "DIFFERS", "Files differ"


# ============================================================================
# Part A: Parse manuscript .tex
# ============================================================================

def parse_manuscript():
    """Parse the manuscript .tex for active \\includegraphics and \\input refs."""
    tex = MS_TEX.read_text(encoding="utf-8", errors="replace")
    lines = tex.split("\n")

    figures_found = []
    tables_found = []

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        # Figures: \includegraphics[...]{path} or inside \begin{overpic}[...]{path}
        for m in re.finditer(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}', line):
            figures_found.append((i, m.group(1)))
        for m in re.finditer(r'\\begin\{overpic\}\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}', line):
            figures_found.append((i, m.group(1)))
        # Tables: \input{path}
        for m in re.finditer(r'\\input\{([^}]+)\}', line):
            path = m.group(1)
            # Skip the \newcommand definition line
            if "\\newcommand" in line:
                continue
            tables_found.append((i, path))

    return figures_found, tables_found


def resolve_replication_table_path(tex_path, fname):
    """Resolve a manuscript table input to its replication-package output path.

    Most table fragments live in output/tables/Formatted/, but Table 1 and the
    by-class summary-stat table live directly in output/tables/. Use the actual
    manuscript \\input path when it points into output/ to avoid false missing
    flags.
    """
    parts = list(Path(tex_path).parts)
    if "output" in parts:
        return ROOT_DIR.joinpath(*parts[parts.index("output"):])

    root_candidate = REPL_TABLES / fname
    if root_candidate.exists():
        return root_candidate
    return REPL_TABLES_FMT / fname


def resolve_manuscript_table_path(tex_path, fname):
    """Resolve the table path used by the manuscript source."""
    candidate = (MS_TEX.parent / tex_path).resolve()
    if candidate.exists():
        return candidate
    root_candidate = PROJECT_ROOT / "Tables" / fname
    if root_candidate.exists():
        return root_candidate
    return MS_TABLES_FMT / fname


# ============================================================================
# Part B: Scan derived directory
# ============================================================================

def scan_derived():
    """Scan data/derived/ for all files, classify each."""
    results = []
    if not DERIVED_DIR.exists():
        return results

    for root, dirs, files in os.walk(DERIVED_DIR):
        # Skip _generated backup dir
        rel_root = Path(root).relative_to(DERIVED_DIR)
        if str(rel_root).startswith("_generated"):
            continue
        for fname in sorted(files):
            if fname == ".DS_Store":
                continue
            rel_path = str(rel_root / fname) if str(rel_root) != "." else fname
            # Also skip .bak files
            if rel_path.endswith(".bak"):
                continue
            # Skip gensim auxiliary files (.npy for lda, .state for lda)
            if any(rel_path.endswith(ext) for ext in [
                ".expElogbeta.npy", ".id2word", ".state",
            ]):
                continue
            if rel_path in DERIVED_FILE_MAP:
                cat, script = DERIVED_FILE_MAP[rel_path]
                results.append((rel_path, cat, script))
            else:
                results.append((rel_path, "GAP", "No generating script identified"))

    return results


# ============================================================================
# Part C: HTML comparison builder
# ============================================================================

STATUS_BADGE = {
    "MATCH":        '<span class="badge match">MATCH</span>',
    "DIFFERS":      '<span class="badge differs">DIFFERS</span>',
    "MS-MISSING":   '<span class="badge missing">MS MISSING</span>',
    "REPL-MISSING": '<span class="badge missing">REPL MISSING</span>',
    "BOTH-MISSING": '<span class="badge missing">BOTH MISSING</span>',
}

CAT_BADGE = {
    "GENERATED":    '<span class="badge match">GENERATED</span>',
    "PROPRIETARY":  '<span class="badge proprietary">PROPRIETARY</span>',
    "PRE-TRAINED":  '<span class="badge pretrained">PRE-TRAINED</span>',
    "RAW-INPUT":    '<span class="badge rawinput">RAW-INPUT</span>',
    "GAP":          '<span class="badge missing">GAP</span>',
}


def build_html(figures_tex, tables_tex, derived_scan):
    """Build the full HTML audit report."""

    # ----- Header -----
    html_parts = ["""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Replication Package Audit</title>
<style>
body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 20px; background: #f8f9fa; color: #222; }
h1 { border-bottom: 3px solid #333; padding-bottom: 8px; }
h2 { color: #444; margin-top: 40px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
h3 { color: #555; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 13px; }
th { background: #f0f0f0; }
tr:nth-child(even) { background: #fafafa; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; color: white; }
.badge.match { background: #28a745; }
.badge.differs { background: #fd7e14; }
.badge.missing { background: #dc3545; }
.badge.proprietary { background: #6f42c1; }
.badge.pretrained { background: #17a2b8; }
.badge.rawinput { background: #6c757d; }
.badge.stale { background: #e83e8c; }
.stale-row { background: #fff3cd !important; }
.fig-compare { display: flex; gap: 20px; align-items: flex-start; margin: 10px 0; }
.fig-compare .panel { flex: 1; text-align: center; }
.fig-compare img { max-width: 100%; border: 1px solid #ddd; background: white; }
.fig-compare .label { font-weight: bold; font-size: 12px; color: #555; margin-bottom: 4px; }
.summary-box { background: white; border: 1px solid #ddd; border-radius: 6px; padding: 16px; margin: 16px 0; }
.summary-box h3 { margin-top: 0; }
.diff-table { font-family: monospace; font-size: 11px; }
.diff-table td { white-space: pre-wrap; word-break: break-all; }
details { margin: 6px 0; }
summary { cursor: pointer; font-weight: bold; padding: 4px; }
summary:hover { background: #e9ecef; }
.section-nav { background: white; padding: 12px; border: 1px solid #ddd; border-radius: 6px; margin: 12px 0; }
.section-nav a { margin-right: 12px; text-decoration: none; color: #007bff; font-size: 13px; }
.section-nav a:hover { text-decoration: underline; }
</style>
</head>
<body>
<h1>Replication Package Audit Report</h1>
<p><em>Generated: """ + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M") + """</em></p>

<div class="section-nav">
<strong>Jump to:</strong>
<a href="#part-a-fig">A1. Figure Coverage</a>
<a href="#part-a-tab">A2. Table Coverage</a>
<a href="#part-b">B. Data Pipeline</a>
<a href="#part-c-fig">C1. Figure Comparison</a>
<a href="#part-c-tab">C2. Table Comparison</a>
</div>
"""]

    # ===== PART A: Figure coverage =====
    html_parts.append('<h2 id="part-a-fig">Part A1: Manuscript Figure Coverage</h2>')

    # Tally
    fig_found = 0
    fig_missing_repl = 0
    fig_stale = 0
    fig_rows = []

    for line_no, tex_path in figures_tex:
        fname = Path(tex_path).name
        script = figure_producer(fname)
        repl_path = REPL_FIGURES / fname
        ms_path = MS_FIGURES / fname
        repl_exists = repl_path.exists()
        ms_exists = ms_path.exists()

        if repl_exists:
            fig_found += 1
            # Check staleness
            is_stale, stale_dep, dep_mtime, out_mtime = check_staleness(repl_path, script)
            if is_stale:
                fig_stale += 1
                badge = (f'<span class="badge stale">STALE</span> '
                         f'<small>output {format_mtime(out_mtime)}, '
                         f'{stale_dep} {format_mtime(dep_mtime)}</small>')
                row_class = ' class="stale-row"'
            else:
                badge = '<span class="badge match">CURRENT</span>'
                row_class = ''
        else:
            fig_missing_repl += 1
            badge = '<span class="badge missing">REPL MISSING</span>'
            row_class = ''

        fig_rows.append(f"<tr{row_class}><td>L{line_no}</td><td>{fname}</td><td>{script}</td>"
                        f"<td>{'Y' if ms_exists else 'N'}</td>"
                        f"<td>{badge}</td></tr>")

    html_parts.append(f"""
<div class="summary-box">
<h3>Summary</h3>
<p>Total active figure references in manuscript: <strong>{len(figures_tex)}</strong></p>
<p>Replication output found: <strong>{fig_found}</strong> &nbsp;|&nbsp;
   Replication missing: <strong>{fig_missing_repl}</strong> &nbsp;|&nbsp;
   <span style="color:#e83e8c;font-weight:bold">Stale (input newer than output): {fig_stale}</span></p>
</div>
<table>
<tr><th>MS Line</th><th>Filename</th><th>Producing Script</th><th>MS Exists</th><th>Status</th></tr>
{"".join(fig_rows)}
</table>
""")

    # ===== PART A: Table coverage =====
    html_parts.append('<h2 id="part-a-tab">Part A2: Manuscript Table Coverage</h2>')

    tab_found = 0
    tab_missing_repl = 0
    tab_stale = 0
    tab_rows = []

    for line_no, tex_path in tables_tex:
        fname = Path(tex_path).name
        script = table_producer(fname)
        repl_path = resolve_replication_table_path(tex_path, fname)
        ms_path = resolve_manuscript_table_path(tex_path, fname)
        repl_exists = repl_path.exists()
        ms_exists = ms_path.exists()

        if repl_exists:
            tab_found += 1
            is_stale, stale_dep, dep_mtime, out_mtime = check_staleness(repl_path, script)
            if is_stale:
                tab_stale += 1
                badge = (f'<span class="badge stale">STALE</span> '
                         f'<small>output {format_mtime(out_mtime)}, '
                         f'{stale_dep} {format_mtime(dep_mtime)}</small>')
                row_class = ' class="stale-row"'
            else:
                badge = '<span class="badge match">CURRENT</span>'
                row_class = ''
        else:
            tab_missing_repl += 1
            badge = '<span class="badge missing">REPL MISSING</span>'
            row_class = ''

        tab_rows.append(f"<tr{row_class}><td>L{line_no}</td><td>{fname}</td><td>{script}</td>"
                        f"<td>{'Y' if ms_exists else 'N'}</td>"
                        f"<td>{badge}</td></tr>")

    # Also report extra replication tables
    extra_tab_rows = []
    for fname, script in EXTRA_REPL_TABLES.items():
        # These live in tables/ root (not Formatted/)
        repl_path = REPL_TABLES / fname
        if not repl_path.exists():
            repl_path = REPL_TABLES_FMT / fname
        exists = repl_path.exists()
        badge = ('<span class="badge match">FOUND</span>' if exists
                 else '<span class="badge missing">MISSING</span>')
        extra_tab_rows.append(
            f"<tr><td>-</td><td>{fname}</td><td>{script}</td><td>-</td><td>{badge}</td></tr>"
        )

    html_parts.append(f"""
<div class="summary-box">
<h3>Summary</h3>
<p>Total active \\input table references: <strong>{len(tables_tex)}</strong></p>
<p>Replication output found: <strong>{tab_found}</strong> &nbsp;|&nbsp;
   Replication missing: <strong>{tab_missing_repl}</strong> &nbsp;|&nbsp;
   <span style="color:#e83e8c;font-weight:bold">Stale: {tab_stale}</span></p>
</div>
<table>
<tr><th>MS Line</th><th>Filename</th><th>Producing Script</th><th>MS Exists</th><th>Status</th></tr>
{"".join(tab_rows)}
</table>

<h3>Additional Replication Tables (written by programs but not \\input'd by the manuscript)</h3>
<table>
<tr><th>MS Line</th><th>Filename</th><th>Producing Script</th><th>MS Exists</th><th>Replication</th></tr>
{"".join(extra_tab_rows)}
</table>
""")

    # ===== PART B: Data pipeline =====
    html_parts.append('<h2 id="part-b">Part B: Data Pipeline Coverage</h2>')

    cat_counts = {}
    data_rows = []
    for rel_path, cat, script in derived_scan:
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        badge = CAT_BADGE.get(cat, cat)
        data_rows.append(f"<tr><td>{rel_path}</td><td>{badge}</td><td>{script}</td></tr>")

    summary_parts = []
    for cat in ["GENERATED", "PROPRIETARY", "PRE-TRAINED", "RAW-INPUT", "GAP"]:
        if cat in cat_counts:
            summary_parts.append(f"{cat}: <strong>{cat_counts[cat]}</strong>")

    html_parts.append(f"""
<div class="summary-box">
<h3>Summary</h3>
<p>Total derived files (excl. _generated/, .bak, .DS_Store): <strong>{len(derived_scan)}</strong></p>
<p>{" &nbsp;|&nbsp; ".join(summary_parts)}</p>
</div>
<table>
<tr><th>File</th><th>Category</th><th>Script / Source</th></tr>
{"".join(data_rows)}
</table>
""")

    # ===== PART C: Side-by-side figure comparison =====
    html_parts.append('<h2 id="part-c-fig">Part C1: Figure Comparison (Manuscript vs Replication)</h2>')

    for fname, script in FIGURE_SCRIPT_MAP.items():
        ms_path = MS_FIGURES / fname
        repl_path = REPL_FIGURES / fname
        status, detail = compare_status(ms_path, repl_path)
        badge = STATUS_BADGE.get(status, status)

        # Also check staleness
        is_stale, stale_dep, dep_mtime, out_mtime = check_staleness(repl_path, script)
        stale_badge = ""
        if is_stale:
            stale_badge = (f' <span class="badge stale">STALE</span>'
                           f' <small>output {format_mtime(out_mtime)}, '
                           f'{stale_dep} {format_mtime(dep_mtime)}</small>')

        html_parts.append(f"""
<details>
<summary>{fname} {badge}{stale_badge} <small>({script})</small></summary>
<div class="fig-compare">
""")
        # Manuscript panel
        html_parts.append('<div class="panel"><div class="label">Manuscript</div>')
        if ms_path.exists() and ms_path.suffix.lower() in (".png", ".jpg", ".jpeg"):
            html_parts.append(f'<img src="{file_to_base64(ms_path)}" alt="ms {fname}">')
        elif ms_path.exists():
            html_parts.append(f"<p><em>{ms_path.suffix} file (not embeddable)</em></p>")
        else:
            html_parts.append("<p><em>File not found</em></p>")
        html_parts.append("</div>")

        # Replication panel
        html_parts.append('<div class="panel"><div class="label">Replication</div>')
        if repl_path.exists() and repl_path.suffix.lower() in (".png", ".jpg", ".jpeg"):
            html_parts.append(f'<img src="{file_to_base64(repl_path)}" alt="repl {fname}">')
        elif repl_path.exists():
            html_parts.append(f"<p><em>{repl_path.suffix} file (not embeddable)</em></p>")
        else:
            html_parts.append("<p><em>File not found</em></p>")
        html_parts.append("</div>")

        html_parts.append(f"</div><p><em>Status: {detail}</em></p></details>")

    # ===== PART C: Side-by-side table comparison =====
    html_parts.append('<h2 id="part-c-tab">Part C2: Table Comparison (Manuscript vs Replication)</h2>')

    for fname, script in TABLE_SCRIPT_MAP.items():
        ms_path = MS_TABLES_FMT / fname
        repl_path = REPL_TABLES_FMT / fname
        status, detail = compare_status(ms_path, repl_path)
        badge = STATUS_BADGE.get(status, status)

        ms_text = read_text(ms_path)
        repl_text = read_text(repl_path)

        html_parts.append(f"""
<details>
<summary>{fname} {badge} <small>({script})</small></summary>
""")
        if status == "MATCH":
            diff_html = html_diff(ms_text, repl_text)
            html_parts.append(f'<p><em>Files are byte-identical (all green).</em></p>')
            html_parts.append(f'<div class="diff-table">{diff_html}</div>')
        else:
            if fname in KNOWN_NOTES:
                html_parts.append(
                    f'<p style="background:#fff3cd;padding:6px 10px;border-radius:4px;">'
                    f'<strong>Note:</strong> {KNOWN_NOTES[fname]}</p>')
            diff_html = html_diff(ms_text, repl_text)
            html_parts.append(f'<div class="diff-table">{diff_html}</div>')
        html_parts.append("</details>")

    # Extra tables comparison
    # Three sources for manuscript counterparts:
    #   1. Separate .tex files in Tables/ or Tables/Formatted/
    #   2. Inline in the manuscript .tex (extracted by \label)
    #   3. No counterpart (replication-only)
    MS_TABLES_ROOT = PROJECT_ROOT / "Tables"
    ms_tex_text = read_text(MS_TEX)  # full manuscript for inline extraction

    html_parts.append('<h3>Additional Replication Tables</h3>')
    for fname, script in EXTRA_REPL_TABLES.items():
        repl_path = REPL_TABLES / fname
        if not repl_path.exists():
            repl_path = REPL_TABLES_FMT / fname

        repl_exists = repl_path.exists()
        repl_text = read_text(repl_path) if repl_exists else None

        # Try to find a manuscript counterpart
        ms_text = None
        ms_source = None

        # Source 1: Separate .tex file in Tables/ or Tables/Formatted/
        for ms_candidate in [MS_TABLES_ROOT / fname, MS_TABLES_FMT / fname]:
            if ms_candidate.exists():
                ms_text = read_text(ms_candidate)
                ms_source = str(ms_candidate)
                break

        # Source 2: Inline in the manuscript .tex (extract by label)
        if ms_text is None and fname in INLINE_TABLE_LABELS and ms_tex_text:
            info = INLINE_TABLE_LABELS[fname]
            extracted = extract_table_by_label(
                ms_tex_text, info["label"], body_only=info["body_only"]
            )
            if extracted:
                ms_text = extracted
                ms_source = f"inline in {MS_TEX.name} (\\label{{{info['label']}}})"

        has_ms = ms_text is not None
        if repl_exists and has_ms:
            if ms_text.strip() == repl_text.strip():
                badge = STATUS_BADGE.get("MATCH", "MATCH")
                detail = "Content matches"
            else:
                badge = STATUS_BADGE.get("DIFFERS", "DIFFERS")
                detail = f"Content differs (ms from {ms_source})"
        elif repl_exists:
            badge = '<span class="badge match">EXISTS</span>'
            detail = "Replication only (no manuscript counterpart found)"
        else:
            badge = '<span class="badge missing">MISSING</span>'
            detail = "Not found"

        html_parts.append(f"""
<details>
<summary>{fname} {badge} <small>({script})</small></summary>
""")
        if repl_exists and has_ms:
            # Side-by-side diff with green/red highlighting
            html_parts.append(f'<p><em>Manuscript source: {ms_source}</em></p>')
            if ms_text.strip() == repl_text.strip():
                html_parts.append('<p><em>Content matches (all green).</em></p>')
            elif fname in KNOWN_NOTES:
                html_parts.append(
                    f'<p style="background:#fff3cd;padding:6px 10px;border-radius:4px;">'
                    f'<strong>Note:</strong> {KNOWN_NOTES[fname]}</p>')
            diff_html = html_diff(ms_text, repl_text)
            html_parts.append(f'<div class="diff-table">{diff_html}</div>')
        elif repl_exists:
            text = repl_text
            if text:
                preview = "\n".join(text.splitlines()[:50])
                html_parts.append(f"<p><em>{detail}</em></p>")
                html_parts.append(f"<pre>{__import__('html').escape(preview)}</pre>")
            else:
                html_parts.append("<p><em>Empty file</em></p>")
        else:
            html_parts.append("<p><em>File not found in replication output</em></p>")
        html_parts.append("</details>")

    # ----- Footer -----
    html_parts.append("""
</body>
</html>
""")

    return "".join(html_parts)


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("REPLICATION PACKAGE AUDIT")
    print("=" * 70)

    # --- Part A: Parse manuscript ---
    print("\n[Part A] Parsing manuscript .tex ...")
    if not MS_TEX.exists():
        print(f"  WARNING: Manuscript not found at {MS_TEX}")
        figures_tex, tables_tex = [], []
    else:
        figures_tex, tables_tex = parse_manuscript()
        print(f"  Found {len(figures_tex)} active figure references")
        print(f"  Found {len(tables_tex)} active table references")

    # Check coverage + staleness
    print("\n  --- Figure Coverage ---")
    fig_ok, fig_miss, fig_stale_count = 0, 0, 0
    stale_figures = []
    fig_unknown, fig_badcontent = [], []
    for line_no, tex_path in figures_tex:
        fname = Path(tex_path).name
        repl_path = REPL_FIGURES / fname
        script = figure_producer(fname)
        if script == "UNKNOWN":
            fig_unknown.append(fname)
        if repl_path.exists():
            fig_ok += 1
            content_ok, why = figure_content_ok(repl_path)
            if not content_ok:
                fig_badcontent.append((fname, why))
                print(f"  INVALID CONTENT: {fname}  ({why})")
            is_stale, stale_dep, dep_mtime, out_mtime = check_staleness(repl_path, script)
            if is_stale:
                fig_stale_count += 1
                stale_figures.append((fname, script, stale_dep,
                                      format_mtime(out_mtime), format_mtime(dep_mtime)))
        else:
            fig_miss += 1
            print(f"  MISSING: {fname}  (script: {script})")
    print(f"  Figures: {fig_ok} found, {fig_miss} missing, "
          f"{fig_stale_count} STALE")
    if stale_figures:
        print("\n  --- Stale Figures (need re-run) ---")
        for fname, script, dep, out_t, dep_t in stale_figures:
            print(f"    {fname}")
            print(f"      script: {script}")
            print(f"      output: {out_t}  |  newest input: {dep} @ {dep_t}")

    print("\n  --- Table Coverage ---")
    tab_ok, tab_miss, tab_stale_count = 0, 0, 0
    stale_tables = []
    tab_unknown, tab_badcontent = [], []
    for line_no, tex_path in tables_tex:
        fname = Path(tex_path).name
        repl_path = resolve_replication_table_path(tex_path, fname)
        script = table_producer(fname)
        if script == "UNKNOWN":
            tab_unknown.append(fname)
        if repl_path.exists():
            tab_ok += 1
            content_ok, why = table_content_ok(repl_path)
            if not content_ok:
                tab_badcontent.append((fname, why))
                print(f"  INVALID CONTENT: {fname}  ({why})")
            is_stale, stale_dep, dep_mtime, out_mtime = check_staleness(repl_path, script)
            if is_stale:
                tab_stale_count += 1
                stale_tables.append((fname, script, stale_dep,
                                     format_mtime(out_mtime), format_mtime(dep_mtime)))
        else:
            tab_miss += 1
            print(f"  MISSING: {fname}")
    print(f"  Tables: {tab_ok} found, {tab_miss} missing, "
          f"{tab_stale_count} STALE")
    if stale_tables:
        print("\n  --- Stale Tables (need re-run) ---")
        for fname, script, dep, out_t, dep_t in stale_tables:
            print(f"    {fname}")
            print(f"      script: {script}")
            print(f"      output: {out_t}  |  newest input: {dep} @ {dep_t}")

    # --- Part B: Data pipeline ---
    print("\n[Part B] Scanning data/derived/ ...")
    derived_scan = scan_derived()
    cat_counts = {}
    gaps = []
    for rel_path, cat, script in derived_scan:
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        if cat == "GAP":
            gaps.append(rel_path)
    for cat in ["GENERATED", "PROPRIETARY", "PRE-TRAINED", "RAW-INPUT", "GAP"]:
        if cat in cat_counts:
            print(f"  {cat}: {cat_counts[cat]}")
    if gaps:
        print(f"\n  --- GAP files (no generating script identified) ---")
        for g in gaps:
            print(f"    {g}")

    # --- Part C: HTML comparison ---
    print("\n[Part C] Building HTML comparison ...")
    html = build_html(figures_tex, tables_tex, derived_scan)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  Written to {OUTPUT_HTML}")
    print(f"  File size: {OUTPUT_HTML.stat().st_size / 1024:.0f} KB")

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Manuscript figures: {len(figures_tex)} refs, {fig_ok} covered, "
          f"{fig_miss} missing, {len(fig_unknown)} unknown-producer, "
          f"{len(fig_badcontent)} content-invalid, {fig_stale_count} stale")
    print(f"  Manuscript tables:  {len(tables_tex)} refs, {tab_ok} covered, "
          f"{tab_miss} missing, {len(tab_unknown)} unknown-producer, "
          f"{len(tab_badcontent)} content-invalid, {tab_stale_count} stale")
    print(f"  Derived data files: {len(derived_scan)} total, "
          f"{cat_counts.get('GAP', 0)} gaps")
    print(f"\n  HTML report: {OUTPUT_HTML}")
    print(f"  Open with: open {OUTPUT_HTML}")

    # FAIL-CLOSED: a missing manuscript exhibit (or a derived-file provenance gap) must make this
    # audit exit NONZERO, so "audit completed" can never mask a missing figure/table or an
    # Also fail if the manuscript was not located/parsed at all: a 0-reference audit is meaningless
    # and must NOT pass as "OK" (it would trivially report zero missing exhibits).
    total_refs = len(figures_tex) + len(tables_tex)
    if total_refs == 0:
        print(f"\nAUDIT FAILED: manuscript not found/parsed at {MS_TEX} (0 figure/table references) "
              f"-- cannot certify exhibit completeness. Exiting nonzero.")
        return 1
    n_gaps = cat_counts.get("GAP", 0)
    n_unknown = len(fig_unknown) + len(tab_unknown)
    n_badcontent = len(fig_badcontent) + len(tab_badcontent)
    # F10: every manuscript exhibit must have a KNOWN producer (provenance) and VALID
    # content (not an empty stub / corrupt file) -- "exists" is not "certified".
    if fig_unknown or tab_unknown:
        print("\n  --- Exhibits with UNKNOWN producer (no generating script mapped) ---")
        for f in fig_unknown:
            print(f"    figure: {f}")
        for t in tab_unknown:
            print(f"    table:  {t}")
    if fig_badcontent or tab_badcontent:
        print("\n  --- Exhibits present but content-invalid (empty / stub / corrupt) ---")
        for f, why in fig_badcontent:
            print(f"    figure: {f}  ({why})")
        for t, why in tab_badcontent:
            print(f"    table:  {t}  ({why})")
    problems = fig_miss + tab_miss + n_gaps + n_unknown + n_badcontent
    if problems:
        print(f"\nAUDIT FAILED: {fig_miss} missing figure(s), {tab_miss} missing table(s), "
              f"{n_gaps} derived-file provenance gap(s), {n_unknown} exhibit(s) with UNKNOWN "
              f"producer, {n_badcontent} content-invalid exhibit(s). Exiting nonzero.")
        return 1
    print(f"\nAUDIT OK: all {len(figures_tex)} figures and {len(tables_tex)} tables referenced by "
          f"the manuscript are present, content-validated (non-empty/well-formed), and attributed "
          f"to a known producer; no derived-file gaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
