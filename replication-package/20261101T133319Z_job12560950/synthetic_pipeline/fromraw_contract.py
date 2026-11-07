"""Machine-readable contract for the official synthetic-from-raw route.

Paths are package-relative. Acquisition inputs are supplied by the public
simulator or public source files; transformation outputs must be absent before
the run and present after their generating step has executed.
"""

ACQUISITION_DERIVED = (
    "data/derived/outpatient_combined_censored.csv",
)

TRANSFORMATION_OUTPUTS = {
    1: (
        "data/raw/unique_firms_thr_75.csv",
        "data/raw/unique_firms_in_PC_thr_75.csv",
        "data/raw/unique_devices_thr_75.csv",
        "data/derived/all_patents_w_xi_oct22_24.csv",
        "data/derived/adverse_event_panel_by_PC_full.csv",
        "data/derived/safety_vars_allpats.csv",
        "data/derived/Full_sample.csv",
        "data/derived/matched_pairs_intuitive_2_1.csv",
        "data/derived/intuitive_2_1_oct22_24.csv",
        "data/derived/intuitive_3_2_oct22_24_similarity.csv",
        "data/derived/later_treated_2_1_oct22_24.csv",
        "data/derived/later_treated_3_2_oct22_24.csv",
        "data/derived/intuitive_spillovers_3_2_oct22_24.csv",
        "data/derived/spillovers_2_1_oct22_24.csv",
        # 510(k) + PMA submission compilation: gen_01 phase 2 writes it, gen_03/gen_03b read it.
        "data/derived/Applicant_Device_data.csv",
    ),
    3: (
        "data/derived/AD_data_applicant_df_oct22_24.csv",
        "data/derived/AD_data_applicant_df2_oct22_24.csv",
    ),
    4: ("data/derived/LBD_ApprovalTime_Both_oct22_24.csv",),
    5: (
        "data/derived/data_2_1_full.parquet",
        "data/derived/data_2_1_latertreat.parquet",
        "data/derived/data_2_1_intuitive.parquet",
        "data/derived/data_2_1_spillovers.parquet",
    ),
    6: ("data/derived/Adverse_fsize_ready_all4_oct22_24.csv",),
    7: ("data/derived/Adv_Event_2020_2022.csv",),
    8: (
        "data/derived/all_adv_events_w_permno5.csv",
        # Manufacturer-cluster transparency intermediate. Both branches of gen_07 now write it,
        # so it must be cleared before the run like every other transformation output.
        "data/derived/All_Adverse_Event_Manufacturers_Deduped.csv",
    ),
    9: (
        "data/derived/matched_sample_2_1_onepat.csv",
        "data/derived/matched_sample_2_1_onepat_innovation.csv",
        "data/derived/matched_sample_2_1_onepat_innovation_quality.csv",
        "data/derived/matched_sample_3_2_onepat.csv",
        "data/derived/matched_sample_3_2_onepat_innovation.csv",
        "data/derived/matched_sample_3_2_onepat_innovation_quality.csv",
        "data/derived/matched_sample_3_2_onepat_innovation_petitioned.csv",
    ),
    37: (
        "data/derived/constrained_adv_event_new_sept25.csv",
        "data/derived/constrained_adv_event_new_sept25_3_2.csv",
    ),
}


def all_transformation_outputs():
    """Return a stable, duplicate-free tuple of all contracted writes."""
    paths = tuple(path for step in sorted(TRANSFORMATION_OUTPUTS)
                  for path in TRANSFORMATION_OUTPUTS[step])
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate path in TRANSFORMATION_OUTPUTS")
    return paths
