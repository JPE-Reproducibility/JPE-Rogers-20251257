### Data Dependency Audit

_Generated on 2026-11-07T16:43:19.489_

**Warning**: this audit is a static string search (data file name as a word-bounded
token in the code text), not a trace of actual data loading. It cannot catch filenames
built dynamically at runtime, or data fetched from a URL rather than a local path. Treat
it as a lead for manual review, not as ground truth.


| Data files | Referenced by code | Orphans (no code reference found) |
|------------|---------------------|-------------------------------------|
| 633 | 323 | 310 |

#### Detail

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/RESTRICTED_DATA_MANIFEST.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/RESTRICTED_FILE_INVENTORY.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_public_source_provenance.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/COMMITTED_PARAMETER_RIGHTS.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/DATA_DICTIONARY.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_data_dictionary.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/DATA_MEMBER_COLUMN_CONTRACT.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/DATA_MEMBER_DISPOSITIONS.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/DEPOSITED_FILE_RIGHTS.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_public_source_provenance.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/EXPECTED_EXHIBIT_HASHES.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/refresh_expected_output_hashes.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/EXPECTED_FROZEN_INPUT_HASHES.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/refresh_expected_output_hashes.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/lda_seed_runs/analyze_selection.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/EXPECTED_INTERMEDIATE_HASHES.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/refresh_expected_output_hashes.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/EXPECTED_MODEL_ARTIFACT_HASHES.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/refresh_expected_output_hashes.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/GENERATION_INPUTS.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_generation_lineage.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/GENERATION_LINEAGE.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_generation_lineage.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/NONTABULAR_DATA_AUTHORITY.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/PUBLIC_INPUT_HASHES.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_maude_manufacturer_rebuild.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_public_source_provenance.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/PUBLIC_SOURCE_PROVENANCE.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_public_source_provenance.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/RESTRICTED_CORPUS_INVENTORY.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/SANITIZER_REPORT.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/SIF_PROVENANCE.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/certify_fromraw_route.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/regen_determinism/PAYLOAD_MIGRATION_RECORD.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/regen_determinism/verify_payload_migration.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/rights_evidence/simulation_parameters.rights.json**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/rights_evidence/simulation_schema_contract.rights.json**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/AD_data_applicant_df2_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/AD_data_applicant_df_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/Adv_Event_2020_2022.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06_adv_2020.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/All_Adverse_Event_Manufacturers_Deduped.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/Applicant_Device_data.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/LBD_ApprovalTime_Both_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/RegNum_Factorized_Synth.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_denom.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00b_pc_effects.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/adverse_event_panel_by_PC_full.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/dedupe_settings/adverse_events/dedupe_dataframe_training.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/dedupe_settings/dedupe_dataframe_training.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/derived/dedupe_settings_applicant/dedupe_dataframe_training.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/2_1_GPT_Price_Links.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/build_draw_concordances.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/3_2_GPT_Price_Links.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/build_draw_concordances.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/3_2_begin_final_revisions.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/501k_all.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/CPI_deflator.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_05_adverse_fsize.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/Class2_Exemptions_2017_Grennan.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/FDA_HCPCS_Xwalk_Moazzam.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/GRID/types.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_data_dictionary.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_simulation_schema_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/regen_determinism/verify_simulated_data_manifest.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/02_match_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10_table_formatting.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD11_Utilization.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD11b_DeviceExperience_2_1.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD15_CostBenefit.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD1_SampleConstruction.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_1_summary_stats.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_D14_summary_stats_by_class.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD11_Utilization.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD11b_DeviceExperience_2_1.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD15_CostBenefit.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD1_SampleConstruction.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_1_summary_stats.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_D14_summary_stats_by_class.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00f_synthetic_nexis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/KPSS_2019_public.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00g_deidentify_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/KPST_Breakthrough.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00g_deidentify_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_1999.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2000.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2001.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2002.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2003.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2004.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2005.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2006.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2008.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2009.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2011.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2012.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2013.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2014.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2016.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2017.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/MAUDE/device_data/ASR/ASR_2018.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/RegNum_Factorized_Synth.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_denom.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00b_pc_effects.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/adverse_event_panel_by_PC_full.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/device-recall-0001-of-0001-2.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00b_pc_effects.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/for_gpt_2_1_invention_dates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/hand_coded_intuitive_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/innovation_year_3_2_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/innovation_year_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/innovation_year_all_other_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_denom.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/pat_search_augment/revise_for_rescrape.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/pat_search_augment/revise_for_rescrape_3_2_latest.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/pat_search_augment/revise_for_rescrape_already_had_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/spinal_entrant_audit.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/unique_devices_thr_75.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/unique_firms_in_PC_thr_75.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data/raw/unique_firms_thr_75.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/data_input_manifest.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_data_dictionary.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/models/all-MiniLM-L6-v2/1_Pooling/config.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_05_adverse_fsize.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06_adv_2020.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/02_match_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03a_estimation_3to2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10_table_formatting.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11f_reg_background.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11g_descriptive_figures.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_contact_lens_case_study.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15b_event_study_HD_coefficients.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/16_total_patent_value_did.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/estimation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/match_mahal.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/plotting.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/table_format.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/models/all-MiniLM-L6-v2/config.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_05_adverse_fsize.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06_adv_2020.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/02_match_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03a_estimation_3to2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10_table_formatting.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11f_reg_background.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11g_descriptive_figures.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_contact_lens_case_study.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15b_event_study_HD_coefficients.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/16_total_patent_value_did.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/estimation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/match_mahal.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/plotting.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/table_format.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/models/all-MiniLM-L6-v2/config_sentence_transformers.json**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/models/all-MiniLM-L6-v2/modules.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/models/all-MiniLM-L6-v2/sentence_bert_config.json**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw1/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw10/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw2/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw3/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw4/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw5/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw6/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw7/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw8/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/draw_files/draw9/innovation_year_2_1_FDA_project.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/drawn_years.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/iy_2_1/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/iy_2_1b_raw_responses.jsonl**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/baseline/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/baseline/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/baseline/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/baseline/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/baseline/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/baseline/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw1/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw1/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw1/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw1/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw1/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw1/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw10/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw10/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw10/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw10/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw10/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw10/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw2/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw2/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw2/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw2/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw2/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw2/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw3/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw3/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw3/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw3/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw3/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw3/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw4/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw4/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw4/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw4/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw4/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw4/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw5/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw5/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw5/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw5/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw5/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw5/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw6/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw6/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw6/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw6/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw6/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw6/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw7/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw7/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw7/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw7/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw7/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw7/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw8/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw8/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw8/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw8/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw8/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw8/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw9/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw9/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw9/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw9/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw9/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/results/draw9/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/pl_full2/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/raw_responses.jsonl**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/build_draw_files.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/analyze2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/analyze_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/deposited/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hbaseline/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hbaseline2/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hbaseline3/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hbaseline4/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw1/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw10/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw2/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw3/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw4/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw5/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw6/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw7/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw8/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/hresults/hdraw9/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/results/baseline/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/results/draw1/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/results/draw2/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/validation_invention_years/coding_sheet_BLIND.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/validation_invention_years/score_validation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/validation_invention_years/sample_KEY.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/validation_invention_years/score_validation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/BreakthroughPanel_distribution.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/BreakthroughPatents_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMainPanel_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMainPanel_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMainPanel_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperSpillovers_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/DIDimpute_PaperSpillovers_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMainPanel_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PaperSpillovers_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/PatentCollectionCounts.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_all_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/RestrictedSamples_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_1_summary_stats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_D14_summary_stats_by_class.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/contact_lens_case_study_ratios.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_contact_lens_case_study.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/cost_benefit_total_value_did.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/16_total_patent_value_did.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/d1_price_coverage.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/d1_treated_counts.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/dpm_decile_ratio.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_base_rates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_D.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_H.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_firm_expansion_patents.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_real_pats.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_real_pats_intuitive.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_real_pats_later.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_safety_prop.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_unique_firms.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_v_serious.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_v_serious_manuf.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_v_serious_normalizable.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_v_serious_restrict.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_2_1_v_serious_voluntary.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_D.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_H.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_absnew_firm_count.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_dev_count.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_firm_expansion.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_firm_expansion_patents.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_patents_pats_nodrugs.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_real_pats.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_real_pats_intuitive.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_real_pats_later.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_real_pats_petitioned.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_unique_firms.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_3_2_v_serious.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_price_2_1.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/event_study_coefficients/ES_coefs_price_3_2.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/firm_heterogeneity_k_est.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/firm_heterogeneity_k_pct.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/intext_numbers_report.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_intext_report.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/lbd_tercile_estimation.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/lbd_tercile_estimation_product_count.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/manufacturer_linkage_coverage.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_all_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/manufacturer_linkage_coverage.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/new_entry_2015_event_study.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/new_entry_2015_in_text.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/price_sample_construction.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/recall_event_study_1996.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/recall_in_text_numbers.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/safety_embedding_distance_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/safety_embedding_percentile_robustness.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/safety_refined_keywords_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/safety_term_share.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/BreakthroughPanel_distribution.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/BreakthroughPatents_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMainPanel_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMainPanel_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMainPanel_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperSpillovers_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/DIDimpute_PaperSpillovers_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperAdverseEvent_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMainPanel_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_Log_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_Log_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_Intuitive_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_LaterTreat_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperMarketComposition_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_2_1_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_2_1_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_2_1_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_2_1_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_3_2_Estimates_Log_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_3_2_Estimates_NoLog_xi_latest_No0_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_3_2_Estimates_NoLog_xi_latest_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PaperSpillovers_3_2_Estimates_NoLog_xi_latest_poisson_oct22_24.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/PatentCollectionCounts.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_all_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/RestrictedSamples_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_1_summary_stats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_D14_summary_stats_by_class.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/contact_lens_case_study_ratios.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_contact_lens_case_study.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/cost_benefit_total_value_did.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/16_total_patent_value_did.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/d1_price_coverage.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/d1_treated_counts.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/dpm_decile_ratio.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_base_rates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_D.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_H.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_firm_expansion_patents.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_real_pats.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_real_pats_intuitive.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_real_pats_later.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_safety_prop.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_unique_firms.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_v_serious.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_v_serious_manuf.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_v_serious_normalizable.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_v_serious_restrict.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_2_1_v_serious_voluntary.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_D.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_H.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_absnew_firm_count.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_dev_count.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_firm_expansion.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_firm_expansion_patents.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_patents_pats_nodrugs.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_real_pats.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_real_pats_intuitive.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_real_pats_later.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_real_pats_petitioned.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_unique_firms.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_3_2_v_serious.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_price_2_1.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/event_study_coefficients/ES_coefs_price_3_2.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/exp_impact_zero_crossings.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/firm_heterogeneity_k_est.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/firm_heterogeneity_k_pct.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/intext_numbers_report.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_intext_report.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/lbd_tercile_estimation.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/lbd_tercile_estimation_product_count.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/manufacturer_linkage_coverage.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_all_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/manufacturer_linkage_coverage.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/maturity_gradient_slopes.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/cmp_11d.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/model_patent_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/model_patent_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/model_v_serious_est_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/model_v_serious_est_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/new_entry_2015_event_study.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/new_entry_2015_in_text.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/price_sample_construction.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/price_utilization_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/recall_event_study_1996.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/recall_in_text_numbers.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/safety_embedding_distance_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/safety_embedding_percentile_robustness.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/safety_refined_keywords_estimates.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/safety_term_share.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/_synthetic_source_internal/pc_effects.parquet**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/build_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00b_pc_effects.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/_synthetic_source_internal/public_master_skeleton.parquet**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/build_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/universe_backend.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/_synthetic_source_internal/simulation_parameters.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_generation_lineage.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/build_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/synthetic_universe.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/universe_backend.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/_synthetic_source_internal/simulation_schema_contract.json**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_simulation_schema_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_payload_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/build_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00f_synthetic_nexis.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/Adverse_fsize_ready_all4_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_05_adverse_fsize.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/Full_sample.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/02_match_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03a_estimation_3to2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_contact_lens_case_study.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/match_mahal.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_denom.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/build_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00b_pc_effects.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/universe_backend.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/all_patents_w_xi_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06b_permno_universe.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/16_total_patent_value_did.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00g_deidentify_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/compustat_firm_data.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_05_adverse_fsize.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/data_2_1_full.parquet**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/data_2_1_intuitive.parquet**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/data_2_1_latertreat.parquet**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/data_2_1_spillovers.parquet**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/frequency_df_2to1_variety.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/frequency_df_3to2_variety.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/intuitive_2_1_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/intuitive_3_2_oct22_24_similarity.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/intuitive_spillovers_3_2_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/later_treated_2_1_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/later_treated_3_2_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/matched_pairs_intuitive_2_1.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/safety_did_analysis.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/safety_did_analysis_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_dimensions_wrds/spillovers_2_1_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_kpss/KPSS_2019_public.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00g_deidentify_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_kpst/KPST_Breakthrough.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00g_deidentify_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_marketscan/constrained_adv_event_new_sept25.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_simulation_schema_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_marketscan/constrained_adv_event_new_sept25_3_2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_simulation_schema_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_marketscan/outpatient_combined_censored.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_simulation_schema_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00b_marketscan_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_maude_linkage/All_Adverse_Event_Manufacturers.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_maude_manufacturer_rebuild.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_maude_linkage/all_permnos_fname_adverse_events_oct22_24.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06b_permno_universe.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_maude_linkage/manual_permno_corrections.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/manufacturer_linkage_coverage.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_all_gpt4.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_both.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave1.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave1_gpt4.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave2.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave2_gpt4.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave3_gpt4.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave4_gpt4.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Liability_Encodings_wave5_gpt4.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for__medical device_ _Class II_ tort preempt.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for__medical device_ _Class II_ tort preempt.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for__medical device_ tort _Class II_.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for__medical device_ tort _Class II_.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 1985-1995.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 1985-1995.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 1996-2000.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 1996-2000.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 2001-2004.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 2001-2004.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 2005-2007.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort 2005-2007.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort _hospital bed_ powered.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort _hospital bed_ powered.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt 2006-2007.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt 2006-2007.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt NOT pharma.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt NOT pharma.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt _Class III_.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt _Class III_.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt _Class II_.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt _Class II_.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_medical device tort preempt.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt 1985-1998.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt 1985-1998.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt 1999-2004.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt 1999-2004.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt 2005-2007.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt 2005-2007.xlsx**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt NOT device 1985-2001.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt NOT device 1985-2001.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt NOT device 2002-2007.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/Results list for_pharmaceutical tort preempt NOT device 2002-2007.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1989 AND date _ 1991.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1989 AND date _ 1991.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1990 AND date _ 1992.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1990 AND date _ 1992.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1991 AND date _ 1993.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1991 AND date _ 1993.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1992 AND date _ 1994.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1992 AND date _ 1994.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1993 AND date _ 1995.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1993 AND date _ 1995.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1994 AND date _ 1996.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1994 AND date _ 1996.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1995 AND date _ 1997.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1995 AND date _ 1997.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1996 AND date _ 1998.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1996 AND date _ 1998.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1997 AND date _ 1999.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1997 AND date _ 1999.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1998 AND date _ 2000.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1998 AND date _ 2000.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1999 AND date _ 2001.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _1999 AND date _ 2001.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _2000 AND date _ 2002.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _2000 AND date _ 2002.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _2001 AND date _ 2003.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _2001 AND date _ 2003.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _2002 AND date _ 2004.csv**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_nexis/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _2002 AND date _ 2004.xlsx**

- ⚠️ ORPHAN: no code reference found

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/Applicant_Cites_Only.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/FDA_patents_text.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00h_synthetic_patent_text.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/FDA_pats_original_firmname.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/PC_by_year_cites_ApplicantOnly.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/PC_by_year_diff_ind_appl_only.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/all_PC_pats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/all_pats_wtitlesCPC.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00h_synthetic_patent_text.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/expanded_2_1_pats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/expanded_3_2_pats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/missed_2_1_pats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/new_patent_analysis/all_device_patents_w_pc.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/match_mahal.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/safety_tagged_patents.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/safety_vars_allpats.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/safety_vars_allpats_updated_v2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_patents/safety_vars_allpats_v2.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_price_links/2_1_GPT_Price_Links.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/build_draw_concordances.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_price_links/3_2_GPT_Price_Links.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/build_draw_concordances.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data/synthetic_price_links/FDA_HCPCS_Xwalk_Moazzam.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py`
- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/simulated_data_audit_report.csv**

- referenced by `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py`

