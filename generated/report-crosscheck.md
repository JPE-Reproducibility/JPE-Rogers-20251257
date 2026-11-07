### Paper vs. Code/Data Crosscheck

_Generated on 2026-11-07T16:45:33.156_

**Caveats (read before using this report):**
- **Static plausibility only, not a reproducibility check.** No code was executed.
  This cannot catch logic bugs, wrong coefficients, or silently incorrect results.
- **File-level citations only, not line-level.** The model did not see code file
  contents -- only Stage A/B's pre-computed findings and file listings. Any
  "supporting file" below is a plausibility signal, not a verified line reference.
- **Coverage is relative to what Stage C extracted from the paper**, not to the
  paper's true full content. A claim Stage C missed is invisible to this score.

#### Coverage

| Category | Coverage | n claims |
|----------|----------|----------|
| figure | 87.5% | 20 |
| data_source | 66.7% | 12 |
| table | 90.5% | 21 |
| **Overall** | **84.0%** | 53 |

#### Per-Claim Detail

🟡 **data_source: FDA reclassification events (Federal Register, 1980-2015)** — Plausible
- Event-list inputs exist (data/raw/3_2_begin_final_revisions.csv, Class2_Exemptions_2017_Grennan.csv, innovation_year_*_FDA_project.csv, RegNum_Factorized_Synth.csv) and gen_01_main_panels.py / 02_match_samples.py would consume them. I did not see a Stage A trace tying a specific file to the Federal Register events.
- supporting files: `data/raw/3_2_begin_final_revisions.csv`, `data/raw/Class2_Exemptions_2017_Grennan.csv`, `data/raw/RegNum_Factorized_Synth.csv`, `code/00_generate_data/gen_01_main_panels.py`

✅ **data_source: FDA PMA and 510(k) databases** — Matched
- README structure check says data/raw/501k_all.csv is mentioned with URL/DOI and access date nearby. Applicant_Device_data.csv, AD_data_applicant_df_oct22_24.csv and the unique_firms/unique_devices files are the derived firm-name-matched submission data. gen_01_main_panels.py is the likely builder.
- supporting files: `data/raw/501k_all.csv`, `data/derived/Applicant_Device_data.csv`, `data/derived/AD_data_applicant_df_oct22_24.csv`, `data/raw/unique_devices_thr_75.csv`, `data/raw/unique_firms_thr_75.csv`, `code/00_generate_data/gen_01_main_panels.py`

🟡 **data_source: FDA MAUDE adverse event reports** — Plausible
- MAUDE ASR files (data/raw/MAUDE/device_data/ASR/ASR_1999-2018) and adverse_event_panel_by_PC_full.csv are present, plus Adv_Event_2020_2022.csv. gen_05, gen_06 and gen_07 scripts match the construction. Stage B reports the ASR files are not mentioned in the README, and I saw no direct code-reference trace. The files also look like extracts, not the full 1992-2019 set.
- supporting files: `data/raw/MAUDE/device_data/ASR/ASR_2000.csv`, `data/raw/adverse_event_panel_by_PC_full.csv`, `data/derived/Adv_Event_2020_2022.csv`, `code/00_generate_data/gen_05_adverse_fsize.py`, `code/00_generate_data/gen_06_adv_2020.py`, `code/00_generate_data/gen_07_adverse_permno.py`

🟡 **data_source: Dimensions patent grants extract** — Plausible
- gen_00_dimensions_patent_extraction.py references RESTRICTED_DATA_MANIFEST.csv per Stage A, which indicates restricted Dimensions data. The raw patent files are not in the data manifest, only restricted or synthetic stand-ins and patent-search augment lists. The code plausibly implements it.
- supporting files: `code/00_generate_data/gen_00_dimensions_patent_extraction.py`, `RESTRICTED_DATA_MANIFEST.csv`, `data/raw/pat_search_augment/revise_for_rescrape.csv`, `data/raw/GRID/types.csv`

✅ **data_source: Kogan et al. (2017) patent market values** — Matched
- data/raw/KPSS_2019_public.csv is the Kogan et al. public patent value file. Stage B reports it is mentioned in the README with URL/DOI and access date nearby.
- supporting files: `data/raw/KPSS_2019_public.csv`, `code/00_generate_data/gen_01_main_panels.py`, `code/16_total_patent_value_did.py`

🟡 **data_source: CRSP/Compustat firm assets** — Plausible
- gen_06b_permno_universe.py, gen_07_adverse_permno.py, gen_05_adverse_fsize.py and the modules/manufacturer_linkage_coverage.py module match linking manufacturers to PERMNO/assets. The derived All_Adverse_Event_Manufacturers_Deduped.csv exists. No CRSP/Compustat raw file is in the data manifest, which is expected if it is restricted.
- supporting files: `code/00_generate_data/gen_06b_permno_universe.py`, `code/00_generate_data/gen_07_adverse_permno.py`, `code/00_generate_data/gen_05_adverse_fsize.py`, `data/derived/All_Adverse_Event_Manufacturers_Deduped.csv`

🟡 **data_source: Truven MarketScan claims** — Plausible
- gen_00b_marketscan_extraction.py, gen_02_price_matching.py, 05_price_analysis.py and the GPT price-link files (2_1_GPT_Price_Links.csv, 3_2_GPT_Price_Links.csv, FDA_HCPCS_Xwalk_Moazzam.csv) are present. Raw MarketScan data is proprietary and not in the manifest. The package includes only synthetic stand-in generators.
- supporting files: `code/00_generate_data/gen_00b_marketscan_extraction.py`, `code/00_generate_data/gen_02_price_matching.py`, `code/05_price_analysis.py`, `data/raw/2_1_GPT_Price_Links.csv`, `data/raw/3_2_GPT_Price_Links.csv`, `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv`

🟡 **data_source: FDA device recall data** — Plausible
- 11b_recall_analysis.py is present, but no recall data file is visible in the data manifest. It may be built in a script or derived elsewhere.
- supporting files: `code/11b_recall_analysis.py`

✅ **data_source: Nexis Uni case counts** — Matched
- The synthetic_nexis xlsx result lists (tort, preemption, Chapter 11 bankruptcy queries) are in the data manifest. convert_nexis_to_csv.py and 11c_liability.py are the corresponding code. Stage B lists several Nexis files as mentioned in the README.
- supporting files: `code/00_generate_data/convert_nexis_to_csv.py`, `code/11c_liability.py`, `synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt.xlsx`

✅ **data_source: Kelly and Seru (2021) breakthrough index** — Matched
- data/raw/KPST_Breakthrough.csv is present. Stage B says it is mentioned in the README with URL/DOI and access date. 14_breakthrough_patents.py is the consumer.
- supporting files: `data/raw/KPST_Breakthrough.csv`, `code/14_breakthrough_patents.py`

❌ **data_source: Makower et al. (2010) survey** — Missing
- No data file or code file in the listings is plausibly connected to the Makower et al. survey. It may be cited from the text only.

✅ **data_source: GPT-5-mini / GPT-4o constructed data** — Matched
- Generation scripts 12_invention_year_generation.py and 12b_gpt_price_links_generation.py exist. Their outputs (innovation_year_*_FDA_project.csv, for_gpt_2_1_invention_dates.csv, *_GPT_Price_Links.csv, hand_coded_intuitive_3_2.csv) are in the package. 13_restricted_samples.py covers the GPT-4o patent screen.
- supporting files: `code/12_invention_year_generation.py`, `code/12b_gpt_price_links_generation.py`, `code/13_restricted_samples.py`, `data/raw/innovation_year_2_1_FDA_project.csv`, `data/raw/innovation_year_3_2_FDA_project.csv`, `data/raw/2_1_GPT_Price_Links.csv`, `data/raw/3_2_GPT_Price_Links.csv`, `data/raw/hand_coded_intuitive_3_2.csv`

✅ **table: Table 1 (Summary statistics)** — Matched
- 09_summary_stats.py is the likely generator. output/tables/Table_1_summary_stats.tex is in the manifest.
- supporting files: `code/09_summary_stats.py`, `output/tables/Table_1_summary_stats.tex`

✅ **table: Table 2 (Innovation)** — Matched
- Estimation scripts 03a/03b, modules/estimation.py, modules/conley_taber.py and 10_table_formatting.py are present. Formatted outputs PaperRegTable{3_2,2_1}_Main_Panel_* and DIDimpute_* are in the manifest.
- supporting files: `code/03a_estimation_3to2.py`, `code/03b_estimation_2to1.py`, `code/10_table_formatting.py`, `output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex`, `output/tables/Formatted/PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex`

✅ **table: Table 3 (Market structure)** — Matched
- Estimation scripts plus 05_price_analysis.py cover prices. Formatted outputs PaperRegTable*_MarketComposition_* and RegTable_Prices_*_sep25.tex are present.
- supporting files: `code/03a_estimation_3to2.py`, `code/03b_estimation_2to1.py`, `code/05_price_analysis.py`, `output/tables/Formatted/PaperRegTable3_2_MarketComposition_NoLog_oct22_24.tex`, `output/tables/Formatted/RegTable_Prices_3_2_sep25.tex`

✅ **table: Table 4 (Adverse events)** — Matched
- Estimation scripts, 06a_safety_analysis.py and formatted AdverseEvent tables are present.
- supporting files: `code/03a_estimation_3to2.py`, `code/03b_estimation_2to1.py`, `code/06a_safety_analysis.py`, `output/tables/Formatted/PaperRegTable3_2_AdverseEvent_NoLog_oct22_24.tex`, `output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex`

🟡 **table: Appendix Table ClassIIIRegnums_combined** — Plausible
- The Table D12 petitioned_vs_fda output exists. A hand-entered Federal Register table could come from 10c_generate_appendix_tables.py or 10b_format_remaining_tables.py. certification/validate_handentered_tables.py suggests hand-entered tables.
- supporting files: `code/10c_generate_appendix_tables.py`, `output/tables/Table_D12_petitioned_vs_fda.tex`, `certification/validate_handentered_tables.py`

🟡 **table: Appendix Table DeviceToProcedureLinkages** — Plausible
- The GPT price-link files and the 12b generation script exist. The table is likely produced by 10c_generate_appendix_tables.py or 05_price_analysis.py. No direct trace.
- supporting files: `data/raw/3_2_GPT_Price_Links.csv`, `data/raw/2_1_GPT_Price_Links.csv`, `code/12b_gpt_price_links_generation.py`, `code/10c_generate_appendix_tables.py`

✅ **table: Appendix Table Robustness_Innovation** — Matched
- Output estimate files exist for Log, poisson, and DIDimpute (Borusyak) variants of PaperMainPanel. Formatted Log, poisson and DIDimpute tables are in the manifest. did_imputation_topython.R is the imputation code.
- supporting files: `r_scripts/did_imputation_topython.R`, `output/tables/Formatted/PaperRegTable3_2_Main_Panel_Log_oct22_24.tex`, `output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_poisson_oct22_24.tex`, `output/tables/Formatted/DIDimpute_PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex`

✅ **table: Appendix Table Robustness_MarketStructure** — Matched
- Formatted MarketComposition Log, poisson and DIDimpute tables, and DIDimpute price tables, are present.
- supporting files: `output/tables/Formatted/PaperRegTable3_2_MarketComposition_Log_oct22_24.tex`, `output/tables/Formatted/DIDimpute_RegTable_Prices_3_2_sep25.tex`, `output/tables/Formatted/PaperRegTable2_1_MarketComposition_NoLog_poisson_oct22_24.tex`

✅ **table: Appendix Table Robustness_Adverse** — Matched
- Formatted AdverseEvent Log, poisson and DIDimpute tables are present.
- supporting files: `output/tables/Formatted/PaperRegTable3_2_AdverseEvent_Log_oct22_24.tex`, `output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_poisson_oct22_24.tex`, `output/tables/Formatted/DIDimpute_PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex`

✅ **table: Appendix Table Innovation_Spillovers** — Matched
- Spillover output tables exist (PaperRegTableSpillovers_2_1/3_2 and DIDimpute_PaperSpillovers estimate files).
- supporting files: `output/tables/Formatted/PaperRegTableSpillovers_3_2_Spillovers_NoLog.tex`, `output/tables/Formatted/PaperRegTableSpillovers_2_1_Spillovers_NoLog.tex`, `code/03a_estimation_3to2.py`

🟡 **table: Appendix Table ClassIIIRegnumswControls** — Plausible
- No distinctly named output file. It is likely produced by 10c_generate_appendix_tables.py or 10b_format_remaining_tables.py from the hand-coded intuitive controls (hand_coded_intuitive_3_2.csv).
- supporting files: `code/10c_generate_appendix_tables.py`, `code/10b_format_remaining_tables.py`, `data/raw/hand_coded_intuitive_3_2.csv`

🟡 **table: Appendix Table ClassIIRegnumsTreated** — Plausible
- No distinctly named output file. It is likely generated by the appendix-table scripts. Class2_Exemptions_2017_Grennan.csv is a plausible input.
- supporting files: `code/10c_generate_appendix_tables.py`, `data/raw/Class2_Exemptions_2017_Grennan.csv`

✅ **table: Appendix Table Combined_DropNoCounts** — Matched
- Output estimate files with a _No0_ suffix and formatted *_NoLog_No0_* tables are in the manifest.
- supporting files: `output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_No0_oct22_24.tex`, `output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_No0_oct22_24.tex`, `output/tables/Formatted/PaperRegTable2_1_MarketComposition_NoLog_No0_oct22_24.tex`

✅ **table: Appendix Table Utilization (TableD11_Utilization)** — Matched
- TableD11_Utilization.tex and RegTable_Utilization_*_sep25.tex are in the manifest. 05_price_analysis.py is the likely generator.
- supporting files: `output/tables/Formatted/TableD11_Utilization.tex`, `output/tables/Formatted/RegTable_Utilization_3_2_sep25.tex`, `code/05_price_analysis.py`

✅ **table: Appendix Table SampleConstruction (TableD1)** — Matched
- TableD1_SampleConstruction.tex is in the manifest. Probable generators are 11d_reg_design.py or 10c_generate_appendix_tables.py.
- supporting files: `output/tables/Formatted/TableD1_SampleConstruction.tex`, `code/11d_reg_design.py`, `code/10c_generate_appendix_tables.py`

✅ **table: Appendix Table ProbabilitySafetyMentionEffects_Robustness** — Matched
- 06b_validate_safety.py (keyword) and 06c_validate_safety_embed.py (embedding) match the two approaches. TableD12_SafetyRobustness.tex and the PaperRegTableSafety_* tables are present.
- supporting files: `code/06b_validate_safety.py`, `code/06c_validate_safety_embed.py`, `output/tables/Formatted/TableD12_SafetyRobustness.tex`, `output/tables/Formatted/PaperRegTableSafety_IItoI_NoLog.tex`

✅ **table: Appendix Tables impacts_vs_exp_3_2 / impacts_vs_exp_2_1** — Matched
- TableD11a_DeviceExperience_3_2.tex and TableD11b_DeviceExperience_2_1.tex are in the manifest. The sensitivity folder has maturity_gradient_slopes and model_*_est files. 11d_reg_design.py and the invention-year sensitivity scripts are plausible generators.
- supporting files: `output/tables/Formatted/TableD11a_DeviceExperience_3_2.tex`, `output/tables/Formatted/TableD11b_DeviceExperience_2_1.tex`, `code/11d_reg_design.py`, `nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`

✅ **table: Appendix Table Innovation_nodrugs_A61only** — Matched
- TableD15_RestrictedSamples.tex is in the manifest. 13_restricted_samples.py is the generator.
- supporting files: `code/13_restricted_samples.py`, `output/tables/Formatted/TableD15_RestrictedSamples.tex`

✅ **table: Appendix Table BreakthroughPatentsEffects** — Matched
- 14_breakthrough_patents.py, BreakthroughPatents_estimates.csv, and TableD16_BreakthroughPatents.tex are present.
- supporting files: `code/14_breakthrough_patents.py`, `output/tables/Formatted/TableD16_BreakthroughPatents.tex`, `output/tables/BreakthroughPatents_estimates.csv`

✅ **table: Appendix Table CostBenefits (TableD15_CostBenefit)** — Matched
- TableD15_CostBenefit.tex is present. 15_intext_derived_numbers.py and 16_total_patent_value_did.py are likely the sources.
- supporting files: `output/tables/Formatted/TableD15_CostBenefit.tex`, `code/15_intext_derived_numbers.py`, `code/16_total_patent_value_did.py`

✅ **table: Appendix Table Table_D14_summary_stats_by_class** — Matched
- Table_D14_summary_stats_by_class.tex is in the manifest. 09_summary_stats.py is the likely generator.
- supporting files: `output/tables/Table_D14_summary_stats_by_class.tex`, `code/09_summary_stats.py`

✅ **figure: Figure 1 (ContactLensCaseStudy)** — Matched
- 12_contact_lens_case_study.py is directly named for this.
- supporting files: `code/12_contact_lens_case_study.py`

✅ **figure: Figure 3 (InnovationES)** — Matched
- 04_event_studies.py, did_ES.R and modules/plotting.py implement the event-study figures. No figure outputs are listed in the manifest, which includes only tables and csv/tex files.
- supporting files: `code/04_event_studies.py`, `r_scripts/did_ES.R`, `code/modules/plotting.py`

✅ **figure: Figure 4 (MarketStructure)** — Matched
- 04_event_studies.py covers the event studies. 05_price_analysis.py covers the price panels.
- supporting files: `code/04_event_studies.py`, `code/05_price_analysis.py`

✅ **figure: Figure 5 (ESProductSafety)** — Matched
- 04_event_studies.py and 06a_safety_analysis.py. The procedure-normalized panels use price/MarketScan volumes via 05_price_analysis.py.
- supporting files: `code/04_event_studies.py`, `code/06a_safety_analysis.py`, `code/05_price_analysis.py`

✅ **figure: Figure 6 (SafetybyAsset)** — Matched
- 07_firm_heterogeneity.py covers asset terciles. The CRSP linkage scripts support the data.
- supporting files: `code/07_firm_heterogeneity.py`, `code/00_generate_data/gen_05_adverse_fsize.py`

🟡 **figure: Appendix Figure Petitioned_IIItoII** — Plausible
- Table_D12_petitioned_vs_fda.tex shows petitioned-event analysis exists. The figure is likely from 04_event_studies.py or 11d_reg_design.py. No direct trace.
- supporting files: `code/04_event_studies.py`, `code/11d_reg_design.py`, `output/tables/Table_D12_petitioned_vs_fda.tex`

🟡 **figure: Appendix Figure MktCompostition_IIItoII_Patents** — Plausible
- 04_event_studies.py plausibly produces the entry event studies.
- supporting files: `code/04_event_studies.py`

✅ **figure: Appendix Figure ProductVariety** — Matched
- 11a_product_variety.py (LDA topics) is directly named. nondeterministic_variable_sensitivity/lda_seed_runs/analyze_selection.py supports LDA topic selection.
- supporting files: `code/11a_product_variety.py`, `nondeterministic_variable_sensitivity/lda_seed_runs/analyze_selection.py`

✅ **figure: Appendix Figure FirmExperienceHeteroSimulation** — Matched
- 08_lbd_simulation.py with gen_03_lbd and gen_03b_lbd_clusters. The data are LBD_ApprovalTime_Both_oct22_24.csv and AD_data_applicant files.
- supporting files: `code/08_lbd_simulation.py`, `code/00_generate_data/gen_03_lbd.py`, `data/derived/LBD_ApprovalTime_Both_oct22_24.csv`

✅ **figure: Appendix Figure FirmSizeHetero** — Matched
- 07_firm_heterogeneity.py covers firm asset terciles.
- supporting files: `code/07_firm_heterogeneity.py`

✅ **figure: Appendix Figure Safety_IItoI** — Matched
- 06a_safety_analysis.py and the validate-safety scripts.
- supporting files: `code/06a_safety_analysis.py`, `code/06b_validate_safety.py`

✅ **figure: Appendix Figure DeviceTortCasesOverTime** — Matched
- 11c_liability.py with the Nexis result files and convert_nexis_to_csv.py.
- supporting files: `code/11c_liability.py`, `code/00_generate_data/convert_nexis_to_csv.py`

✅ **figure: Appendix Figure Impact_by_experience** — Matched
- 11d_reg_design.py and the invention_years_2_1 sensitivity scripts (maturity_sensitivity.py, model_*_est outputs).
- supporting files: `code/11d_reg_design.py`, `nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`

🟡 **figure: Appendix Figure DeviceExperienceCurrent** — Plausible
- Likely from 11d_reg_design.py or 11g_descriptive_figures.py using GPT invention-date files such as innovation_year_all_other_FDA_project.csv.
- supporting files: `code/11d_reg_design.py`, `code/11g_descriptive_figures.py`, `data/raw/innovation_year_all_other_FDA_project.csv`

✅ **figure: Appendix Figure Innovation_3_2_Nodrugs** — Matched
- 13_restricted_samples.py.
- supporting files: `code/13_restricted_samples.py`

✅ **figure: Appendix Figure Recall_Analysis** — Matched
- 11b_recall_analysis.py is named for this.
- supporting files: `code/11b_recall_analysis.py`

✅ **figure: Appendix Figure SafetyRecalls_IItoI_2015** — Matched
- 11b_recall_analysis.py and 11e_new_entry_2015.py. Adv_Event_2020_2022.csv supports the 2015 event.
- supporting files: `code/11b_recall_analysis.py`, `code/11e_new_entry_2015.py`, `data/derived/Adv_Event_2020_2022.csv`

✅ **figure: Appendix Figure Innovation_2_1_2017** — Matched
- 11e_new_entry_2015.py.
- supporting files: `code/11e_new_entry_2015.py`

🟡 **figure: Appendix Figure AdvEvent_by_Reporter** — Plausible
- No script is named for reporter type. 06a_safety_analysis.py or 04_event_studies.py with MAUDE data are plausible.
- supporting files: `code/06a_safety_analysis.py`, `code/04_event_studies.py`

🟡 **figure: Appendix Figure event_distribution** — Plausible
- 11f_reg_background.py or 11g_descriptive_figures.py are plausible generators of event histograms.
- supporting files: `code/11f_reg_background.py`, `code/11g_descriptive_figures.py`

#### Orphan Code (no traceable connection to any claim)

- `certification/compare_all_numbers.py`
- `certification/compare_exhibit_fidelity.py`
- `certification/compare_output_simulated.py`
- `certification/compare_simulated_payloads.py`
- `certification/gen_deposited_file_rights.py`
- `certification/generate_data_dictionary.py`
- `certification/generate_simulation_schema_contract.py`
- `certification/hash_manuscript_closure.py`
- `certification/preflight_apimode.py`
- `certification/refresh_expected_output_hashes.py`
- `certification/validate_payload_contract.py`
- `certification/verify_candidate_zip.py`
- `certification/verify_generation_lineage.py`
- `certification/verify_immutable_tree.py`
- `certification/verify_intext_report.py`
- `certification/verify_public_source_provenance.py`
- `certification/regen_determinism/verify_payload_migration.py`
- `certification/regen_determinism/verify_simulated_data_manifest.py`
- `certification/certify_fromraw_route.sh`
- `certification/run_fromraw_analysis_only.sh`
- `code/audit_pipeline.py`
- `code/audit_pipeline_current.py`
- `code/00_generate_data/sanitize_public_data.py`
- `docker/install_r_packages.R`
- `docker/generate_renv_lock.py`
- `docker/entrypoint.sh`
- `paper/build_manuscript.py`
- `synthetic_pipeline/audit_simulated_data.py`
- `synthetic_pipeline/build_simulation.py`
- `synthetic_pipeline/fromraw_contract.py`
- `synthetic_pipeline/materialize_simulation.py`
- `synthetic_pipeline/preflight_from_raw.py`
- `synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- `synthetic_pipeline/generators/gen_00b_pc_effects.py`
- `synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- `synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`
- `synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- `synthetic_pipeline/generators/gen_00f_synthetic_nexis.py`
- `synthetic_pipeline/generators/gen_00g_deidentify_patents.py`
- `synthetic_pipeline/generators/gen_00h_synthetic_patent_text.py`
- `synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py`
- `synthetic_pipeline/generators/independent_universe.py`
- `synthetic_pipeline/generators/materialize_from_universe.py`
- `synthetic_pipeline/generators/synthetic_paths.py`
- `synthetic_pipeline/generators/synthetic_seed.py`
- `synthetic_pipeline/generators/synthetic_universe.py`
- `synthetic_pipeline/generators/universe_backend.py`
- `nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- `nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- `nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- `nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
