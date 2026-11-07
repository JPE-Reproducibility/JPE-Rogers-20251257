"""
Central configuration for the replication package.

All paths, parameters, and constants are defined here. The user sets ROOT_DIR
once; every other path derives from it.

Inputs: None (user edits ROOT_DIR)
Outputs: Importable namespace used by every analysis script
"""

from pathlib import Path

# ============================================================================
# ROOT — Set this to the top-level replication_package directory on your machine
# ============================================================================
ROOT_DIR = Path(__file__).resolve().parent

# ============================================================================
# Directory structure
# ============================================================================
CODE_DIR = ROOT_DIR / "code"
MODULES_DIR = CODE_DIR / "modules"
R_SCRIPTS_DIR = ROOT_DIR / "r_scripts"
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DERIVED_DATA_DIR = DATA_DIR / "derived"
OUTPUT_DIR = ROOT_DIR / "output"
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"
LOGS_DIR = OUTPUT_DIR / "logs"

# output/logs/ is deliberately EXCLUDED from the public package (run logs are not deposited), but
# every step module configures a logging FileHandler into it AT IMPORT TIME while only creating the
# directory later, inside main(). In the author's working tree the directory already exists so this
# is invisible; in a FRESH EXTRACTION of the deposited archive it does not, so simply IMPORTING a
# shipped step (as certification/preflight_apimode.py does for 06c) raised FileNotFoundError.
# run_all.py creates it before running anything, so full pipeline runs were never affected -- only
# importing/running a single step standalone, which a reviewer may well do. Creating it here fixes
# every module at one point, since they all import config. Guarded so a read-only checkout can still
# be imported for inspection.
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

# ============================================================================
# Reproducibility
# ============================================================================
RANDOM_SEED = 12345

# ============================================================================
# CPI deflator (base year 2019)
# ============================================================================
CPI_DEFLATOR_2019 = 0.3891444146542998

# ============================================================================
# Color palette
# ============================================================================
COLORS = {
    "downreg_line": "#984c2a",   # III→II regression/trend line
    "downreg_dot": "#31303a",    # III→II scatter dots
    "dereg_line": "#2a9d8f",     # II→I regression/trend line
    "dereg_dot": "#264653",      # II→I scatter dots
    "error": "#313c2c",          # error bars (both)
}

# ============================================================================
# Anticipation windows (years before reclassification that posttreat = 1)
# ============================================================================
ANTICIPATION = {
    # For adverse events, market structure outcomes: no anticipation
    "no_anticipation": ["L", "H", "D", "v_serious", "very_serious",
                        "firm_expansion", "absnew_firm_count",
                        "firm_count",
                        "PaidAmt", "BilledAmt", "q", "dev_count"],
    # Innovation outcomes: firms anticipate reclassification
    "3_2": 2,   # posttreat starts 2 years before reclassification
    "2_1": 1,   # posttreat starts 1 year before reclassification
}

# ============================================================================
# Outcome variable definitions by panel
# ============================================================================
OUTCOME_DICTS = {
    "MainPanel": {
        "2_1": {
            "default": {
                "real_pats": "Patenting Rate",
                "times_cited": "Citations-Per-Patent Rate",
                "xi_real_2019": "Average Patent Value",
            },
            "nodrugs_A61": {
                "patents_pats_nodrugs": "Patenting Rate",
                "times_cited": "Citations-Per-Patent Rate",
                "xi_real_2019": "Average Patent Value",
            },
        },
        "3_2": {
            "default": {
                "real_pats": "Patenting Rate",
                "dev_count": "Device Submission Rate",
                "times_cited": "Citations-Per-Patent Rate",
                "xi_real_2019": "Average Patent Value",
            },
            "nodrugs_A61": {
                "patents_pats_nodrugs": "Patenting Rate",
                "times_cited": "Citations-Per-Patent Rate",
                "xi_real_2019": "Average Patent Value",
            },
        },
    },
    "AdverseEvent": {
        "2_1": {
            "default": {
                "L": "Life-Threatening Event Rate",
                "H": "Hospitalization Rate",
                "D": "Mortality Rate",
            },
        },
        "3_2": {
            "default": {
                "L": "Life-Threatening Event Rate",
                "H": "Hospitalization Rate",
                "D": "Mortality Rate",
            },
        },
    },
    "MarketComposition": {
        "2_1": {
            "default": {
                "firm_expansion_patents": "Incumb. Entry (pat.)",
                "unique_firms": "New Entry (pat.)",
            },
        },
        "3_2": {
            "default": {
                "firm_expansion": "Incumb. Entry (dev.)",
                "absnew_firm_count": "New Entry  (dev.)",
                "firm_expansion_patents": "Incumb. Entry (pat.)",
                "unique_firms": "New Entry (pat.)",
            },
        },
    },
    "Spillovers": {
        "2_1": {
            "default": {
                "real_pats": "Patenting Rate",
            },
        },
        "3_2": {
            "default": {
                "real_pats": "Patenting Rate",
                "dev_count": "Device Submission Rate",
            },
        },
    },
}


def get_outcome_dict(outcome_type, reclass_type, nodrugs_A61=False):
    """Return the appropriate outcome variable → label mapping."""
    spec = "nodrugs_A61" if nodrugs_A61 else "default"
    panel = OUTCOME_DICTS[outcome_type][reclass_type]
    return panel.get(spec, panel["default"])


# ============================================================================
# Adverse event year restrictions
# ============================================================================
ADVERSE_EVENT_MIN_YEAR = 1991
ADVERSE_EVENT_MIN_RECLASS_YEAR = 1993

# ============================================================================
# Conley-Taber defaults
# ============================================================================
CT_NUMBSIM = 5000
CT_COUNTMAX = 10e6
CT_TOL = 10e-3
CT_GAMMA = 0.3

# ============================================================================
# Data file names (within DERIVED_DATA_DIR)
# ============================================================================
FULL_SAMPLE = "Full_sample.csv"
MATCHED_SAMPLES = {
    "2_1_onepat": "matched_sample_2_1_onepat.csv",
    "2_1_onepat_innovation": "matched_sample_2_1_onepat_innovation.csv",
    "2_1_onepat_innovation_quality": "matched_sample_2_1_onepat_innovation_quality.csv",
    "3_2_onepat": "matched_sample_3_2_onepat.csv",
    "3_2_onepat_innovation": "matched_sample_3_2_onepat_innovation.csv",
    "3_2_onepat_innovation_quality": "matched_sample_3_2_onepat_innovation_quality.csv",
    "3_2_onepat_innovation_petitioned": "matched_sample_3_2_onepat_innovation_petitioned.csv",
}

# Source data files (expected in DERIVED_DATA_DIR or RAW_DATA_DIR)
SOURCE_FILES = {
    "spillovers_2_1": "spillovers_2_1_oct22_24.csv",
    "later_treated_2_1": "later_treated_2_1_oct22_24.csv",
    "intuitive_2_1": "intuitive_2_1_oct22_24.csv",
    "intuitive_spillovers_3_2": "intuitive_spillovers_3_2_oct22_24.csv",
    "later_treated_3_2": "later_treated_3_2_oct22_24.csv",
    "intuitive_3_2": "intuitive_3_2_oct22_24_similarity.csv",
    "safety_vars": "safety_vars_allpats.csv",
    "all_patents": "all_patents_w_xi_oct22_24.csv",
    "constrained_adv_event": "constrained_adv_event_new_sept25.csv",
    "constrained_adv_event_3_2": "constrained_adv_event_new_sept25_3_2.csv",
    "synth_number": "RegNum_Factorized_Synth.csv",
}

# Parquet files for 2→1 samples (pre-built)
PARQUET_FILES = {
    "data_2_1_full": "data_2_1_full.parquet",
    "data_2_1_latertreat": "data_2_1_latertreat.parquet",
    "data_2_1_intuitive": "data_2_1_intuitive.parquet",
    "data_2_1_spillovers": "data_2_1_spillovers.parquet",
}

# Safety analysis outputs
SAFETY_FILES = {
    "safety_did_2_1": "safety_did_analysis.csv",
    "safety_did_3_2": "safety_did_analysis_3_2.csv",
}

# Invention / commercial availability year files (in RAW_DATA_DIR)
INVENTION_YEAR_FILES = {
    "2_1": "innovation_year_2_1_FDA_project.csv",
    "3_2": "innovation_year_3_2_FDA_project.csv",
    "all_other": "innovation_year_all_other_FDA_project.csv",
}

# ============================================================================
# Generation script inputs (raw files needed by 00_generate_data/)
# ============================================================================
GEN_RAW_FILES = {
    # FDA regulatory data
    "501k_all": "501k_all.csv",
    "all_pma_approvals": "all_pma_approvals.txt",
    "foiclass": "foiclass.txt",
    "3_2_begin_final_revisions": "3_2_begin_final_revisions.csv",
    "good_2_1_controls": "Good_2_1_Control_2_1.txt",
    "hand_coded_intuitive_3_2": "hand_coded_intuitive_3_2.csv",
    "regnums_master": "RegNums_Final_w_CPC_Desc_sample.csv",
    # Patent data
    "fda_patents_text": "FDA_patents_text.csv",
    "all_device_patents": "new_patent_analysis/all_device_patents_w_pc.csv",
    # External economic data
    "kpss_2019": "KPSS_2019_public.csv",
    "compustat_firm_data": "compustat_firm_data.csv",
    "applicant_cites": "Applicant_Cites_Only.csv",
    "kpst_breakthrough": "KPST_Breakthrough.csv",
    "cpi_deflator": "CPI_deflator.csv",
    # GPT-generated linkage files
    "gpt_price_links_2_1": "2_1_GPT_Price_Links.csv",
    "gpt_price_links_3_2": "3_2_GPT_Price_Links.csv",
    # 2017 deregulation data
    "class2_exemptions": "Class2_Exemptions_2017_Grennan.csv",
    "device_recalls": "device-recall-0001-of-0001-2.json",
    # Pre-scraped patent data (from Dimensions API)
    "all_pc_pats": "all_PC_pats.csv",
    "expanded_3_2_pats": "expanded_3_2_pats.csv",
    "missed_2_1_pats": "missed_2_1_pats.csv",
    "expanded_2_1_pats": "expanded_2_1_pats.csv",
    "fda_pats_firmname": "FDA_pats_original_firmname.csv",
    "all_pats_titles_cpc": "all_pats_wtitlesCPC.csv",
    # Pre-built citation data
    "pc_by_year_cites": "PC_by_year_cites_ApplicantOnly.csv",
    "pc_by_year_cites_outside": "PC_by_year_diff_ind_appl_only.csv",
    # GRID organization types
    "grid_types": "GRID/types.csv",
}

GEN_DERIVED_FILES = {
    # Fuzzy matching intermediates (pre-built, from interactive pandas_dedupe)
    "ad_data_applicant": "AD_data_applicant_df_oct22_24.csv",
    "ad_data_applicant2": "AD_data_applicant_df2_oct22_24.csv",
    "applicant_device_data": "Applicant_Device_data.csv",
    "adv_events_permno": "all_adv_events_w_permno5.csv",
}

# ============================================================================
# Table formatting — significance stars
# ============================================================================
STAR_LEVELS = {
    0.001: "***",
    0.01: "**",
    0.05: "*",
    0.10: "+",
}

# ============================================================================
# Specification variants for the estimation loop
# ============================================================================
SPEC_VARIANTS = [
    {"name": "nozero", "nozero": True, "df_imput": False, "nodrugs_A61": False, "poisson": False, "logged": "NoLog"},
    {"name": "did_impute", "nozero": False, "df_imput": True, "nodrugs_A61": False, "poisson": False, "logged": "NoLog"},
    {"name": "poisson", "nozero": False, "df_imput": False, "nodrugs_A61": False, "poisson": True, "logged": "NoLog"},
    {"name": "log", "nozero": False, "df_imput": False, "nodrugs_A61": False, "poisson": False, "logged": "Log"},
    {"name": "baseline", "nozero": False, "df_imput": False, "nodrugs_A61": False, "poisson": False, "logged": "NoLog"},
]

# ============================================================================
# Helper: build output CSV filename for estimate tables
# ============================================================================

def estimate_csv_path(outcome_type, reclass_type, logged_type, sample,
                      nozero=False, df_imput=False, nodrugs_A61=False,
                      poisson=False):
    """Build a standardized filename for estimate CSVs."""
    parts = []
    if df_imput:
        parts.append("DIDimpute")
    parts.append(f"Paper{outcome_type}")
    parts.append(reclass_type)

    if sample == "Full":
        parts.append("FullSample")

    parts.append("Estimates")
    parts.append(logged_type)

    if sample == "Later":
        parts.append("LaterTreat")
    elif sample == "Intuitive":
        parts.append("Intuitive")
    elif sample == "Matched":
        # nodrugs_A61 does not include xi_latest in original filenames
        if not nodrugs_A61:
            parts.append("xi_latest")
    elif sample == "Full":
        parts.append("Fuzzy")

    if nodrugs_A61:
        parts.append("nodrugs_A61")
    elif poisson:
        parts.append("poisson")
    elif nozero:
        parts.append("No0")

    parts.append("oct22_24")
    return TABLES_DIR / ("_".join(parts) + ".csv")
