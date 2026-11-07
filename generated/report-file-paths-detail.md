## Filepaths Analysis Details

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00h_synthetic_patent_text.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 10, unix : route 06b/06c run on synthetic text and Table D.12 is regenerated rather than reused from the real
- Line 14, unix : `simulated_data/synthetic_patents/all_pats_wtitlesCPC.csv` (synthetic ids + PRODUCTCODE) and the
- Line 16, unix : `simulated_data/synthetic_patents/FDA_patents_text.csv`, which materialize_simulation.py then
- Line 17, unix : routes to `data/raw/FDA_patents_text.csv`.
- Line 46, unix : # code/06b_validate_safety.py). Injecting these into synthetic abstracts gives 06b/06c real
- Line 47, unix : # (synthetic) safety/cost/quality signal instead of an all-zero column.
- Line 85, unix : # safety-keyword injection rate CLUSTERS by product code via theta.p_safety; cost/quality

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11c_liability.py**

- Line 1, unix : #!/usr/bin/env python
- Line 13, unix : data/raw/Liability/Results list for_medical device tort preempt.xlsx
- Line 14, unix : data/raw/Liability/Results list for_medical device tort preempt 2006-2007.xlsx
- Line 15, unix : data/raw/Liability/Results list for_medical device tort 1985-1995.xlsx
- Line 16, unix : data/raw/Liability/Results list for_medical device tort 1996-2000.xlsx
- Line 17, unix : data/raw/Liability/Results list for_medical device tort 2001-2004.xlsx
- Line 18, unix : data/raw/Liability/Results list for_medical device tort 2005-2007.xlsx
- Line 19, unix : data/raw/Liability/Results list for_pharmaceutical tort preempt 1985-1998.xlsx
- Line 20, unix : data/raw/Liability/Results list for_pharmaceutical tort preempt 1999-2004.xlsx
- Line 21, unix : data/raw/Liability/Results list for_pharmaceutical tort preempt 2005-2007.xlsx
- Line 22, unix : data/raw/Liability/medtech/ (bankruptcy Excel files)
- Line 25, unix : output/figures/cases_preemption.png
- Line 26, unix : output/figures/Bankruptcy_1996_raw_trend.png

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py**

- Line 50, unix : # Every substitution is therefore RECORDED, per call, to output/logs/inference_method_fallbacks.csv,
- Line 80, unix : # output/logs/, NOT output/tables/: this file only exists when a substitution happens, and
- Line 81, unix : # the simulated-route comparator requires the fixed reference set under output/tables to
- Line 83, unix : # output/logs is explicitly outside what the comparator reads.
- Line 101, unix : # tidyverse/didimputation/fixest/did dozens of times within one process -- a known rpy2 memory-churn
- Line 256, unix : # into a hard process exit (SIGSEGV/SIGABRT) mid-feols. An explicit gc() bounds that. No effect on
- Line 282, unix : # output/logs/inference_method_fallbacks.csv. No manuscript number is affected: the price
- Line 364, unix : # output/logs/inference_method_fallbacks.csv (see the note at the top of this file; the sidecar
- Line 431, unix : # `eta[df[...].index]` uses df's full positional index, so a shorter residual would raise/misalign
- Line 438, unix : # output/logs/inference_method_fallbacks.csv.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R**

- Line 8, unix : # threaded is deterministic and stable (see run_all.build_child_env, which also pins OMP/BLAS).
- Line 25, unix : # observation (singleton/collinear FE level, or NA outcome). The Python caller (conley_taber.py)
- Line 28, unix : # values/order -- so deposited (real-data) estimates are unchanged.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py**

- Line 32, unix : # output/logs/ is deliberately EXCLUDED from the public package (run logs are not deposited), but
- Line 36, unix : # shipped step (as certification/preflight_apimode.py does for 06c) raised FileNotFoundError.
- Line 38, unix : # importing/running a single step standalone, which a reviewer may well do. Creating it here fixes

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/convert_nexis_to_csv.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 17, unix : Run: `python3 code/00_generate_data/convert_nexis_to_csv.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/05_price_analysis.py**

- Line 1, unix : #!/usr/bin/env python
- Line 22, unix : data/derived/outpatient_combined_censored.csv
- Line 23, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 24, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 25, unix : data/derived/matched_sample_2_1_onepat_innovation.csv
- Line 26, unix : data/derived/matched_sample_3_2_onepat_innovation.csv
- Line 29, unix : output/figures/3_2_nolog_Price_solo_CTs_sept20_25.png
- Line 30, unix : output/figures/2_1_nolog_Price_solo_CTs_sept20_25.png
- Line 31, unix : output/tables/price_utilization_estimates.csv
- Line 32, unix : output/tables/price_sample_construction.csv
- Line 33, unix : output/tables/Formatted/RegTable_Prices_3_2_sep25.tex
- Line 34, unix : output/tables/Formatted/RegTable_Prices_2_1_sep25.tex
- Line 35, unix : output/tables/Formatted/DIDimpute_RegTable_Prices_3_2_sep25.tex
- Line 36, unix : output/tables/Formatted/DIDimpute_RegTable_Prices_2_1_sep25.tex
- Line 37, unix : output/tables/Formatted/RegTable_Utilization_3_2_sep25.tex
- Line 38, unix : output/tables/Formatted/RegTable_Utilization_2_1_sep25.tex
- Line 39, unix : output/tables/Formatted/DIDimpute_RegTable_Utilization_3_2_sep25.tex
- Line 40, unix : output/tables/Formatted/DIDimpute_RegTable_Utilization_2_1_sep25.tex
- Line 151, unix : Returns a claims DataFrame with proc1/HCPCS, year, pay, proc_count, BilledAmt.
- Line 246, unix : # HCPCS/CPT code corrections for retired and replaced procedure codes.
- Line 270, unix : (JPE Policy 2.2 in-text numbers) to output/tables/price_sample_construction.csv.
- Line 389, unix : coders with third-coder reconciliation (data/raw/FDA_HCPCS_Xwalk_Moazzam.csv,
- Line 392, unix : estimates it produces are written to output/tables/price_utilization_estimates.csv
- Line 396, unix : 'HCCPS Category Code' column, stripped, is the HCPCS/CPT code, and the
- Line 676, unix : # Balance the panel via unstack/stack
- Line 686, unix : # Forward/backward fill the sentinel values. FDA_own_accord is a per-product-code constant;
- Line 764, unix : Run static DiD estimation for a single price/utilization outcome.
- Line 780, unix : output/logs/inference_method_fallbacks.csv;
- Line 1180, unix : # price/utilization estimating sample -- i.e., treated device types whose linked procedures are
- Line 1295, unix : code/10c_generate_appendix_tables.py's _extract_method_row() reads (it locates the row by its
- Line 1368, unix : certification/test_price_exhibit_guard.py, which checks that each clause binds by
- Line 1631, unix : # needs -- Conley-Taber/All-CPTs, BJS/All-CPTs, Conley-Taber/Matched, BJS/Matched -- are
- Line 1670, unix : # Level utilization (q): retained All-CPTs/Conley-Taber only, matching prior

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py**

- Line 10, unix : data/derived/Full_sample.csv
- Line 11, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 12, unix : data/derived/safety_vars_allpats.csv
- Line 13, unix : data/derived/intuitive_2_1_oct22_24.csv
- Line 14, unix : data/derived/later_treated_2_1_oct22_24.csv
- Line 15, unix : data/derived/intuitive_3_2_oct22_24_similarity.csv
- Line 16, unix : data/derived/later_treated_3_2_oct22_24.csv
- Line 17, unix : data/derived/intuitive_spillovers_3_2_oct22_24.csv
- Line 18, unix : data/derived/spillovers_2_1_oct22_24.csv
- Line 19, unix : data/derived/adverse_event_panel_by_PC_full.csv
- Line 20, unix : data/raw/unique_devices_thr_75.csv
- Line 21, unix : data/raw/unique_firms_in_PC_thr_75.csv
- Line 22, unix : data/raw/unique_firms_thr_75.csv
- Line 24, unix : Source: my_paper/analysis/code/Replication_Gather_and_Compile_Data.py
- Line 141, windows : text = re.sub(r'[^\w\s]', ' ', text)
- Line 189, unix : # Columns and their order in data/derived/Applicant_Device_data.csv, exactly as the deposited
- Line 240, unix : # PHASE 2: Fuzzy deduplication of firms/devices
- Line 257, unix : # All three of these files SHIP in data/raw (see RESTRICTED_FILE_INVENTORY.csv, disposition
- Line 259, unix : # branch is always reached; synthetic_pipeline/fromraw_contract.py lists these same three
- Line 274, windows : f"{OUT_RAW}:\n"
- Line 314, unix : 'Change Design/Components/Specifications/Material')]
- Line 862, unix : # code's U/D/P/M reporter convention, and guarantee expected columns exist.
- Line 1021, unix : # --- Treatment/control indicators ---
- Line 1336, windows : if re.search(r"\d\d\d+\.+\d", s):
- Line 1337, windows : if re.search(r"\d\d\d+\.+9", s):
- Line 1785, unix : # Phase 2a: compile the 510(k)+PMA submission table gen_03/gen_03b read.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_07_adverse_permno.py**

- Line 5, unix : data/derived/all_adv_events_w_permno5.csv
- Line 10, unix : held in data/raw/manual_permno_corrections.csv.
- Line 27, unix : data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv
- Line 28, unix : data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv
- Line 29, unix : data/derived/dedupe_settings/adverse_events/dedupe_dataframe_learned_settings
- Line 30, unix : data/raw/MAUDE/link_dataframes_learned_settings
- Line 36, unix : data/derived/all_adv_events_w_permno5.csv
- Line 37, unix : data/derived/All_Adverse_Event_Manufacturers_Deduped.csv (intermediate)
- Line 251, unix : # (data/raw/manual_permno_corrections.csv), shipped only in the restricted archive.
- Line 365, unix : # data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv is a two-column projection of the
- Line 366, unix : # 23 public FDA MAUDE device files that ship under data/raw/MAUDE/device_data/. It is
- Line 368, unix : # and certification/verify_maude_manufacturer_rebuild.py checks that this rebuild
- Line 375, unix : # it. The order is therefore pinned in certification/MAUDE_MFR_SOURCE_ORDER.txt rather than
- Line 458, unix : # assembled file give identical STRINGS but a different int/str object mix in
- Line 536, unix : # Save intermediate deduped file for comparison/transparency
- Line 633, unix : # Left-join permno/stock_name from matched rows

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/materialize_from_universe.py**

- Line 4, unix : as a VIEW/SUBSET of the SAME universe, so cross-file joins resolve WITHOUT any real id.
- Line 19, unix : pass the real SCHEMA (column names/order) and any PUBLIC columns explicitly. Self-test uses
- Line 63, unix : # drawn independently). Replaces reading a real identity column (GRID/assignee/inventor/...).

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/gen_deposited_file_rights.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 12, unix : 1. `certification/PUBLIC_SOURCE_PROVENANCE.csv:redistribution_basis` -- the per-file provenance
- Line 21, unix : Usage: python3 certification/gen_deposited_file_rights.py [--root .]   (exit 0 = every member has a basis)
- Line 29, unix : RIGHTS_SCHEMA = 'artifact_rights/v1'
- Line 38, unix : 'code/00_generate_data/ from public-domain FDA sources (the 510(k) and PMA '
- Line 43, unix : 'reviewed byte-by-byte in certification/NONTABULAR_DATA_AUTHORITY.csv')
- Line 45, unix : 'data/raw/unique_devices_thr_75.csv': _FDA_DERIVED,
- Line 46, unix : 'data/raw/unique_firms_thr_75.csv': _FDA_DERIVED,
- Line 47, unix : 'data/raw/unique_firms_in_PC_thr_75.csv': _FDA_DERIVED,
- Line 48, unix : 'data/raw/adverse_event_panel_by_PC_full.csv': _FDA_DERIVED,
- Line 49, unix : 'data/derived/adverse_event_panel_by_PC_full.csv': _FDA_DERIVED,
- Line 50, unix : 'data/derived/Applicant_Device_data.csv': _FDA_DERIVED,
- Line 51, unix : 'data/derived/AD_data_applicant_df_oct22_24.csv': _FDA_DERIVED,
- Line 52, unix : 'data/derived/AD_data_applicant_df2_oct22_24.csv': _FDA_DERIVED,
- Line 53, unix : 'data/derived/LBD_ApprovalTime_Both_oct22_24.csv': _FDA_DERIVED,
- Line 54, unix : 'data/derived/Adv_Event_2020_2022.csv': _FDA_DERIVED,
- Line 55, unix : 'data/derived/All_Adverse_Event_Manufacturers_Deduped.csv': _FDA_DERIVED,
- Line 58, unix : ('data/derived/dedupe_settings', _DEDUPE_ARTIFACT),
- Line 97, unix : PRIVACY audit and from Data-Editor TECHNICAL acceptance (external-audit R2 F1/F2/F9). The evidence
- Line 100, unix : certification/rights_evidence/ within root (rejects the abs / '../' escape the prior token allowed);
- Line 101, unix : - is a versioned JSON evidence document (schema 'artifact_rights/v1') that carries an affirmative
- Line 104, unix : Fails closed on a bad path, missing/unreadable/malformed doc, wrong schema, non-PASS determination, an
- Line 105, unix : artifact_sha256 that does not equal the actual committed artifact bytes, an empty reviewer/role/date/
- Line 106, unix : basis/seal, an invalid date, or a reviewer_role that is the Data Editor (who grants technical, not
- Line 165, unix : # R3 F8: rights are an AUTHOR REPRESENTATION unless an independent provider/licensing review is cited.
- Line 196, unix : if m.startswith('synthetic_pipeline/_synthetic_source_internal/'):
- Line 204, unix : # Restricted-derived committed parameters (rounded/smoothed DGP params; restricted
- Line 209, unix : # derived committed inputs (public design/skeleton) keep the status-only basis.
- Line 222, unix : # data files: the inventory says WHETHER it ships; the ledger/table says ON WHAT RIGHT.
- Line 235, unix : if m.startswith('synthetic_pipeline/simulated_data/'):
- Line 243, unix : # output/figures/, which would misclassify it as a pipeline product).
- Line 264, unix : return ('author-doc/config', 'redistributable',
- Line 276, unix : return ('author-doc/config', 'redistributable', 'author-authored doc/config/manifest')
- Line 283, unix : ap.add_argument('--out', default='certification/DEPOSITED_FILE_RIGHTS.csv')
- Line 285, unix : members = load_allowlist(os.path.join(root, 'certification/PUBLIC_PACKAGE_ALLOWLIST.txt'))
- Line 288, unix : os.path.join(root, 'certification/COMMITTED_PARAMETER_RIGHTS.csv'))
- Line 290, unix : os.path.join(root, 'certification/PUBLIC_SOURCE_PROVENANCE.csv'))

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/synthetic_universe.py**

- Line 18, unix : Because both universes are generated (not mapped from real rows), the real firm/patent
- Line 88, unix : # Deterministic support contract for matched/event-study samples. Sampling weights

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00b_marketscan_extraction.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 8, unix : This is the Python program I ran on the NBER MarketScan server (/homes/nber/parogers/mktscan)
- Line 9, unix : to aggregate the raw Merative/IBM MarketScan Commercial Claims and Encounters (CCAE) outpatient
- Line 12, unix : data/derived/outpatient_combined_censored.csv
- Line 26, unix : date) summing coins/copay/netpay/qty/pay, then sum to (proc1, year); proc_count is

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00g_deidentify_patents.py**

- Line 9, unix : synthetic identifiers consistently across files, creates synthetic KPSS/KPST
- Line 17, unix : synthetic domain is a fatal upstream/privacy error.
- Line 21, unix : synthetic per-code patenting level, with floored weights for reclass/control codes so the
- Line 133, unix : # assignment was already RESIMULATED from theta in gen_00d/gen_00e (weight-proportional
- Line 134, unix : # with floored weights for reclass/control codes), so the per-code counts are synthetic
- Line 193, unix : synthetic D/M/YYYY dates (gen_01 parses `year = filing_date.split('/')[2]`). So the from-raw
- Line 267, unix : # 2) validate/preserve every already-synthetic patent number consistently.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/16_total_patent_value_did.py**

- Line 11, unix : Δ patents/yr (4) × value per patent ($27M) × retention (0.20) ≈ $22M/yr.
- Line 12, unix : That decomposition assumes the marginal/induced patents are worth the AVERAGE
- Line 27, unix : baseline (NoLog) estimation steps from 03a/03b (class_by_episode construction,
- Line 31, unix : RUN_TOTAL_VALUE_DID=1 python3 code/16_total_patent_value_did.py
- Line 96, unix : # class_by_episode (03a/03b lines 146-150)
- Line 123, unix : exact estimator + plotter. Saves a figure to output/figures/.
- Line 218, unix : # FAIL-CLOSED (certification): a swallowed estimate/event-study failure leaves the cost-benefit

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py**

- Line 4, unix : (JPE Data Policy 2.2). Each table is written to output/tables/Formatted/ as a complete LaTeX table
- Line 18, unix : certification/validate_handentered_tables.py recomputes every displayed computed cell from the
- Line 34, unix : RETENTION = 0.20    # patent-value retention after business-stealing/creative-destruction
- Line 72, unix : # outputs; the negligible hospitalization-dollar cells (Value $0.02M; Total $.06M/-$0.04M and their
- Line 85, unix : & \multicolumn{7}{l}{-Attribute 80\% of patent value to business stealing/creative destruction \citep{kogan:2017}.} \\
- Line 186, unix : # F9: the hospitalization Value/Total/CI + the VSL are now COMPUTED (were literals).
- Line 219, unix : # simulated data lacks that panel's price/GPT-links input (e.g. the 3_2 utilization panel). The
- Line 223, unix : # certification/validate_handentered_tables.py rejects any dash row there.
- Line 259, unix : # byte-for-byte the same), with the estimate/SE rows and sample sizes filled from the outputs.
- Line 267, windows : " \\addlinespace\n\n\\midrule\n\\addlinespace\n"
- Line 272, windows : "\\addlinespace\n\\hline\n\\addlinespace\n\n"
- Line 293, unix : # panels; every displayed estimate/SE cell parses to a finite number; sample sizes are positive.
- Line 412, unix : pipeline's data/outputs or a clearly-labeled documented Federal-Register constant:
- Line 438, unix : # --- price/utilization coverage from 05's emission ---
- Line 463, windows : "& $N$ & \\% & $N$ & \\% \\\\\n\\midrule\n"
- Line 489, unix : # written in non-proprietary form by the step that fits the models, code/11d_reg_design.py (see

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/08_lbd_simulation.py**

- Line 1, unix : #!/usr/bin/env python
- Line 13, unix : data/derived/LBD_ApprovalTime_Both_oct22_24.csv
- Line 14, unix : data/derived/matched_sample_3_2_onepat_innovation.csv
- Line 17, unix : output/figures/LBDEstimation.png
- Line 18, unix : output/figures/LBDEstimation_ProductCount.png  (robustness: product count measure)
- Line 19, unix : output/tables/lbd_tercile_estimation.csv
- Line 20, unix : output/tables/lbd_tercile_estimation_product_count.csv

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py**

- Line 1, unix : #!/usr/bin/env python
- Line 17, unix : data/derived/matched_sample_{reclass}_onepat_innovation_quality.csv
- Line 18, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 19, unix : data/raw/KPST_Breakthrough.csv
- Line 22, unix : output/tables/BreakthroughPatents_estimates.csv
- Line 23, unix : output/tables/Formatted/TableD16_BreakthroughPatents.tex
- Line 58, unix : # KPST Breakthrough data: expected in data/raw/
- Line 147, unix : Run one estimation specification (poisson/linear/logged).
- Line 362, unix : # code/15_intext_derived_numbers.py:derived_breakthrough_distribution() (kept in

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/estimation.py**

- Line 45, unix : rpy2 heap accumulation), which is why 03a/03b/06a survived. gc() only reclaims memory and does not enter

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03a_estimation_3to2.py**

- Line 1, unix : #!/usr/bin/env python
- Line 10, unix : data/derived/ (matched samples, Full_sample.csv, parquet files, spillovers)
- Line 12, unix : output/tables/ (estimate CSVs for Tables 2-4, III→II columns)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/docker/generate_renv_lock.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 3, unix : generate_renv_lock.py -- write docker/renv.lock as a RECORD of an R library.
- Line 11, unix : WHAT THIS FILE IS NOT. The resulting docker/renv.lock is NOT restored anywhere.
- Line 12, unix : docker/install_r_packages.R -- the only R install step the image runs -- never
- Line 20, unix : the R library is the image hash in certification/EXPECTED_SIF_SHA, and the
- Line 21, unix : record of what that image contains is docker/container_r_library.tsv. See the
- Line 30, unix : Base/recommended R packages that ship with R itself are excluded -- they are
- Line 34, unix : python3 docker/generate_renv_lock.py            # writes docker/renv.lock
- Line 107, windows : header = fh.readline()  # "Package\tVersion"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/sanitize_public_data.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 9, unix : listed public variables (FDA registry/MAUDE outcomes + public reclassification
- Line 18, unix : Restricted-lineage selected/matched panels and Dimensions-derived files are
- Line 23, unix : Emits certification/SANITIZER_REPORT.csv (pre/post sha256, rows, cols, dropped).
- Line 32, unix : # non-tabular sidecars (docs/images) are allowlisted by extension so their
- Line 43, windows : ".png": [b"\x89PNG\r\n\x1a\n"], ".jpg": [b"\xff\xd8\xff"], ".jpeg": [b"\xff\xd8\xff"],
- Line 81, windows : # a bare `\bnpi\b` false-positived on public FDA device MODELS like "NPI-200" (3-4 digits). MarketScan
- Line 89, unix : # Excludes ALL patent/firm-size columns AND the patent-derived membership flags
- Line 93, unix : # EMPTY BY DESIGN. The only schema target was data/derived/Full_sample.csv --
- Line 114, unix : # carry ONLY public FDA 510(k)/MAUDE fields (APPLICANT/KNUMBER/DEVICENAME/PRODUCTCODE) and learned
- Line 115, unix : # dedup weights -- never a restricted (Dimensions/WRDS/MarketScan/Nexis) source. We do NOT skip them
- Line 147, unix : # Irregular/large JSON (e.g. the openFDA recall dump {meta, results:[...]}, which
- Line 155, unix : # structured parse fails (irregular/quoted public FDA dumps: MAUDE masterevent/patient/device_data,
- Line 214, unix : #    unknown/unsupported extension, or a symlink is a HARD FAILURE (never a
- Line 233, unix : # F4: a sidecar accepted by extension must actually BE that format (magic/UTF-8), else it

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/lda_seed_runs/analyze_selection.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 15, windows : EST = re.compile(r"Topic (\d+): est=([-\d.eE]+), CI=\[([-\d.eE]+), ([-\d.eE]+)\]")
- Line 22, windows : print("Coherence sweeps and selections\n")

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py**

- Line 13, windows : pat = re.compile(r"sk-[A-Za-z0-9_\-]{20,}")
- Line 18, unix : # ---- the deposited prompt, verbatim from code/12b_gpt_price_links_generation.py ----
- Line 23, windows : return ("Device candidate:\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py**

- Line 1, unix : #!/usr/bin/env python
- Line 24, unix : data/derived/Full_sample.csv
- Line 25, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 26, unix : data/derived/matched_sample_3_2_onepat_innovation_petitioned.csv
- Line 27, unix : data/raw/RegNum_Factorized_Synth.csv
- Line 30, unix : output/figures/exp_vs_impact_v_serious_est_3_2.png
- Line 31, unix : output/figures/exp_vs_impact_patent_est_3_2.png
- Line 32, unix : output/figures/exp_vs_impact_v_serious_est_2_1.png
- Line 33, unix : output/figures/exp_vs_impact_patent_est_2_1.png
- Line 34, unix : output/figures/Distribution_of_3_over_years.png
- Line 35, unix : output/figures/Distribution_of_2_over_years.png
- Line 36, unix : output/tables/Table_D11_reg_design.tex
- Line 37, unix : output/tables/Table_D12_petitioned_vs_fda.tex
- Line 38, unix : output/tables/model_{v_serious,patent}_est_{2_1,3_2}.csv
- Line 39, unix : (the fitted coefficient tables Table D.11a/D.11b are typeset from, in plain CSV)
- Line 65, unix : # line above: the five Conley-Taber calls in 11a/11d pass no `seed=` of their own, unlike
- Line 110, windows : "CLINICAL CHEMISTRY AND CLINICAL TOXICOLOGY DEVICES\n": "OTHER DEVICES",
- Line 112, windows : "HEMATOLOGY AND PATHOLOGY DEVICES\n": "OTHER DEVICES",
- Line 183, unix : and the DPM/experience score vector.
- Line 275, unix : # Load regulation-number crosswalk for PART/SUBPART descriptions
- Line 344, unix : # Merge SUBPART for matching (drop existing to avoid _x/_y suffixes)
- Line 448, unix : to output/tables/dpm_decile_ratio.csv.
- Line 452, unix : over the 1996/1998 Class II universe -- the same score the burden analysis
- Line 521, unix : Uses the 63 FR 59 and 61 FR 111/112 reclassifications as treated units,
- Line 573, unix : # Control pool: Class I/II devices not reclassified
- Line 677, unix : # LAST 1998 treated PC's part_desc/subpart_desc -- an original-code quirk)
- Line 774, unix : # Experience years from manually researched invention/commercial availability dates
- Line 811, unix : file Tables D.11a/D.11b are typeset from; it is written here, by the step that fits the model,
- Line 893, unix : # D.11a/D.11b. A pickle is a Python- and library-version-specific format, so the .csv is
- Line 939, unix : # Output-only in-text provenance (does not affect the plot/estimate).
- Line 1395, unix : # have invention year data -- not just the matched/treated sample.
- Line 1799, windows : f"  {labels[key]}:\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py**

- Line 5, windows : KEY=re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/validation_invention_years/score_validation.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 11, unix : Every estimate uses design weights 1/pi. Unweighted means estimate nothing.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD1_SampleConstruction.tex**

- Line 17, unix : & 29 & 94 & n/a & n/a \\
- Line 19, unix : & 12 & 39 & n/a & n/a \\
- Line 31, unix : & 12 & 100 & n/a & n/a \\
- Line 49, unix : \textsuperscript{e}Uses firm assets from CRSP/Compustat and is the only specification restricted to publicly listed firms.}

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py**

- Line 10, unix : writes, plus the 06b/06c estimate CSVs). Does NOT re-run any regressions, and does not read
- Line 260, windows : "\\textquotedblleft---\\textquotedblright\\ indicates variables "
- Line 292, windows : "\\textquotedblleft---\\textquotedblright\\ indicates variables "

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15b_event_study_HD_coefficients.py**

- Line 16, unix : treated/control level means to:
- Line 18, unix : output/tables/event_study_coefficients/ES_coefs_2_1_{v_serious,H,D}.csv
- Line 39, unix : RUN_ES_HD=1 python3 code/15b_event_study_HD_coefficients.py

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline_current.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 10, unix : bibliography, and figure/table comparison paths relative to the package root,
- Line 15, unix : location in my_paper/paper/). This wrapper rewrites that resolution so both
- Line 51, unix : audit's purpose here is to confirm every figure/table referenced by the

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py**

- Line 5, unix : `DPM2_1_1997/for_gpt_2_1_invention_dates.csv`. That file holds exactly the 293 product codes of
- Line 61, windows : print("\n--- system prompt ---\n" + SYSTEM)
- Line 68, windows : KEY = re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00b_pc_effects.py**

- Line 51, unix : _MIN_ELIGIBLE_WEIGHT = 0.35   # floor on the patent sampling weight for reclass/control PCs
- Line 121, windows : if (re.search(r"\d\d\d+\.+\d", value)
- Line 122, windows : and not re.search(r"\d\d\d+\.+9", value)):
- Line 268, unix : # exact real NaN count -- which the re-audit showed leaks restricted structure. gen_00d/gen_00e now

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 6, unix : analysis, table/figure production, and final audit.
- Line 17, unix : python3 synthetic_pipeline/materialize_simulation.py --for-gen-run
- Line 18, unix : python3 synthetic_pipeline/preflight_from_raw.py
- Line 23, unix : #     restricted derived data are present. Starts from data/derived/:
- Line 33, unix : PYTHONHASHSEED=0, single-threaded BLAS/OpenMP, package-owned matplotlib/XDG/NLTK
- Line 38, unix : --skip-estimation      reuse existing estimate CSVs in output/tables/
- Line 49, unix : estimation (steps 11-12): Estimation (static DiD, requires R/fixest via rpy2)
- Line 51, unix : formatting (step 31):     Final table formatting (depends on 06b/06c + 11d)
- Line 61, unix : steps 16-17 (06b/06c safety CSVs) and step 25 (11d coefficient tables).
- Line 68, unix : conley_taber_stacked in 03a/03b/04/05/06a/etc.). A few pieces are frozen
- Line 78, unix : - GPT/API invention-year CSVs (step 10): derived from data via an external
- Line 79, unix : LLM/API call that cannot be re-executed deterministically inside the
- Line 88, unix : These are DERIVED FROM DATA by shipped code and seeded/frozen only because
- Line 100, unix : 11g_descriptive_figures.py from data/raw/.
- Line 102, unix : script; every result-bearing figure is generated from data by 04/05/06a/11a/etc.
- Line 121, unix : EXECUTION RELIABILITY (rpy2/R): the R bridge (rpy2) occasionally cannot import in
- Line 122, unix : API mode and falls back to ABI mode, in which a single R/feols error can corrupt
- Line 125, unix : output shows a transient R/rpy2 marker (a fresh process recovers with byte-identical
- Line 186, unix : # EXECUTED on that route's MarketScan claims (data/derived/outpatient_combined_censored.csv --
- Line 198, unix : # Phase 3: Estimation (static DiD via R/fixest)
- Line 252, unix : # Phase 6: Final formatting (MUST follow 06b/06c + 11d)
- Line 369, unix : # The step-16/17 OUTPUT tables that the real-data route takes as given (steps 16 and 17 are skipped
- Line 405, unix : run_all reuses precomputed safety artifacts (steps 16/17) instead of regenerating them (the
- Line 410, unix : certification/EXPECTED_INTERMEDIATE_HASHES.csv (the two output/tables estimate files) or
- Line 411, unix : certification/EXPECTED_FROZEN_INPUT_HASHES.csv (the three data/derived frozen inputs) is a HARD
- Line 414, unix : audit's own caveat: an artifact that WILL be overwritten before use (its step 16/17 is being
- Line 432, unix : a HARD FAILURE (SystemExit), not a warning/skip. Certification must verify every frozen artifact
- Line 575, unix : # before a run, and the same two the output comparison reads. output/logs and output/_cache are
- Line 590, windows : "  (1) Simulated-data route -- no restricted data, runs every step:\n"
- Line 591, windows : "        python3 synthetic_pipeline/materialize_simulation.py --for-gen-run\n"
- Line 592, windows : "        python3 synthetic_pipeline/preflight_from_raw.py\n"
- Line 594, windows : "            --regenerate-safety-keywords --regenerate-safety-embeddings\n"
- Line 596, windows : "  (2) Real-data route -- only where the licensed inputs and the restricted derived\n"
- Line 597, windows : "      data are present:\n"
- Line 598, windows : "        python3 run_all.py --skip-gen --force-estimation --strict-cert\n"
- Line 600, windows : "  (3) Real-data route FROM RAW -- as (2), but rebuilding the derived data first. Needs\n"
- Line 601, windows : "      every licensed raw input, not only the derived panels, and does not reproduce every\n"
- Line 602, windows : "      shipped file byte-for-byte (see README.md, \"Route 3\"):\n"
- Line 603, windows : "        python3 run_all.py --real-from-raw --force-estimation --strict-cert\n"
- Line 627, unix : leaves the run with no way to produce it again -- steps 16/17 are skipped as precomputed
- Line 642, windows : "regenerate:\n"
- Line 712, unix : `manual_figures/Deregulation_May31_23_Paper.png` so it can be restored even
- Line 713, unix : after output/figures/ is cleared for a from-scratch run. The editable
- Line 714, unix : draw.io master, `manual_figures/Deregulation_May31_23_Paper.drawio`, ships
- Line 727, unix : generated from data by 04/05/06a/11a/etc. See the REPRODUCIBILITY POLICY block
- Line 757, unix : step self-manages sys.path via config.MODULES_DIR/ROOT inserts),
- Line 758, unix : PYTHONSTARTUP, and USER-level R profile/environ files -- so a developer's
- Line 773, unix : The frozen-env reproduction legitimately sets R_HOME/R_LIBS_USER/NLTK_DATA (see
- Line 785, unix : #        FDA_SKIP_MARKETSCAN_PANEL   -- would drop the price/utilization exhibits (step 14) and
- Line 815, unix : # /opt/nltk_data and sets NLTK_DATA to it; a bare host falls back to the package
- Line 818, unix : # Deterministic Python hashing so dict/set-ordering-sensitive steps reproduce
- Line 841, unix : # API mode it falls back to ABI mode, in which a single feols/R error can corrupt
- Line 873, unix : rpy2/ABI-mode failure (see _R_TRANSIENT_MARKERS and the REPRODUCIBILITY
- Line 923, unix : # Up to two automatic retries for transient R/rpy2 (ABI-mode) failures. Heavy
- Line 924, unix : # steps make many feols calls per run (11a ~1/topic, 14/04 several), so the
- Line 948, unix : # a log-write failure is FATAL — a missing/partial log invalidates the evidence.
- Line 958, windows : _fh.write("# ---- stdout ----\n")
- Line 960, windows : _fh.write("\n# ---- stderr ----\n")
- Line 974, unix : # the interpreter, which leaves EMPTY stdout/stderr -- so no marker string matches. Detect that
- Line 1003, windows : "stderr (last 2000):\n%s",
- Line 1059, unix : python3 synthetic_pipeline/materialize_simulation.py --for-gen-run
- Line 1060, unix : python3 synthetic_pipeline/preflight_from_raw.py
- Line 1068, unix : single-threaded BLAS/OpenMP, package-owned caches, FDA_STRICT_INTEXT=1 and
- Line 1260, unix : # rewrote data/derived/Applicant_Device_data.csv before gen_01 stopped it. Refusing here
- Line 1308, unix : # STRICT/final-cert mode: no skip, no cross-route fallback -- a missing or wrong-route manifest
- Line 1329, unix : # Estimation is FORCED on both reported routes. 03a/03b skip any estimate CSV that already

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_intext_report.py**

- Line 1, unix : #!/usr/bin/env python3

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/cmp_price.py**

- Line 4, unix : output/tables/price_utilization_estimates.csv byte for byte; each draw run substitutes one

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD15_CostBenefit.tex**

- Line 11, unix : & \multicolumn{7}{l}{-Attribute 80\% of patent value to business stealing/creative destruction \citep{kogan:2017}.} \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py**

- Line 5, unix : `DPM2_1_1997/for_gpt_2_1_invention_dates.csv`. That file holds exactly the 293 product codes of
- Line 59, windows : print("\n--- system prompt ---\n" + SYSTEM)
- Line 66, windows : KEY = re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py**

- Line 1, unix : #!/usr/bin/env python
- Line 19, unix : data/derived/matched_sample_{reclass}_onepat_innovation.csv
- Line 20, unix : data/derived/Full_sample.csv  (via match_mahal for GPT-4o re-matching)
- Line 21, unix : data/raw/new_patent_analysis/all_device_patents_w_pc.csv
- Line 22, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 25, unix : output/tables/RestrictedSamples_estimates.csv
- Line 26, unix : output/tables/Formatted/TableD15_RestrictedSamples.tex
- Line 355, unix : to a NEW CSV (output/tables/PatentCollectionCounts.csv). Guarded so a missing

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/refresh_expected_output_hashes.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 4, unix : certification/EXPECTED_EXHIBIT_HASHES.csv        (figures + tables)
- Line 5, unix : certification/EXPECTED_INTERMEDIATE_HASHES.csv   (intermediate CSVs)
- Line 6, unix : certification/EXPECTED_MODEL_ARTIFACT_HASHES.csv (model artifacts)
- Line 22, unix : that live under data/derived/ (the three precomputed safety artifacts reused on the real-data route)
- Line 23, unix : is kept in a SEPARATE manifest, certification/EXPECTED_FROZEN_INPUT_HASHES.csv, verified by
- Line 24, unix : run_all.verify_frozen_artifact_integrity -- NOT by this script. Keeping data/derived paths out of the
- Line 43, unix : python3 certification/refresh_expected_output_hashes.py            # verify; exit 1 on any issue
- Line 44, unix : python3 certification/refresh_expected_output_hashes.py --write    # re-pin the SAME output set
- Line 45, unix : python3 certification/refresh_expected_output_hashes.py --write --allow-path-set-change
- Line 68, unix : # unsafe/out-of-tree, exactly as before -- this only says WHICH directory, per manifest.
- Line 182, unix : # CANONICAL PATH SET must match exactly (catches swapped/added/removed paths at fixed count).
- Line 258, windows : # "\r\n" would rewrite every byte of every manifest on the first --write.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 17, unix : `data/raw/manual_permno_corrections.csv` is the author's hand-coded
- Line 20, unix : `data/raw/manual_permno_corrections.csv` at all, and step 35
- Line 63, unix : # both state it, and code/00_generate_data/gen_07_adverse_permno.py's own docstring names it. It is

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/docker/install_r_packages.R**

- Line 1, unix : #!/usr/bin/env Rscript
- Line 7, unix : # section and certification/ENVIRONMENT_EVIDENCE.txt). This image instead uses
- Line 8, unix : # fixest 0.10.4 because rocker/r-ver:4.1.3 ships it as a binary in its default
- Line 11, unix : # conflicts. 0.10.4 cross-checks the deposit to within 0.1-0.6% (a platform/BLAS
- Line 19, unix : # container matches certification/ENVIRONMENT_EVIDENCE.txt exactly, not because any
- Line 23, unix : # (see certification/ENVIRONMENT_EVIDENCE.txt). data.table is used for data
- Line 34, unix : # 0.12.1, see the package README); data.table/Matrix/did to the compatible
- Line 60, windows : cat(sprintf("  %-14s %s%s\n", p, v, flag))

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_pipeline_runs/run_one.sh**

- Line 1, unix : #!/bin/bash
- Line 7, unix : B=${FDA_TREE:-$W/base}
- Line 19, unix : --env HOME=/tmp,PYTHONHASHSEED=0,MPLCONFIGDIR=/tmp/mpl \

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py**

- Line 1, unix : #!/usr/bin/env python
- Line 19, unix : data/derived/Full_sample.csv
- Line 20, unix : data/derived/RegNum_Factorized_Synth.csv          (product-code-to-class crosswalk)
- Line 21, unix : data/derived/all_patents_w_xi_oct22_24.csv         (patent-level data with xi values)
- Line 22, unix : data/derived/adverse_event_panel_by_PC_full.csv    (adverse events by product code)
- Line 23, unix : data/derived/LBD_ApprovalTime_Both_oct22_24.csv    (firm regulatory proficiency)
- Line 24, unix : data/raw/501k_all.csv                              (510(k) submissions)
- Line 25, unix : data/raw/all_pma_approvals.txt                     (PMA submissions)
- Line 26, unix : data/raw/unique_devices_thr_75.csv                 (unique device count)
- Line 27, unix : data/raw/unique_firms_in_PC_thr_75.csv             (firms per product code)
- Line 28, unix : data/raw/unique_firms_thr_75.csv                   (unique entrant firms)
- Line 29, unix : data/raw/Adverse_fsize_ready_all4_oct22_24.csv     (adverse-event firm sizes)
- Line 30, unix : data/raw/KPSS_2019_public.csv                      (patent value data)
- Line 31, unix : data/raw/compustat_firm_data.csv                   (firm total assets from Compustat)
- Line 32, unix : data/raw/Applicant_Cites_Only.csv                  (forward citations per patent)
- Line 33, unix : data/derived/outpatient_combined_censored.csv       (MarketScan outpatient claims, proprietary)
- Line 42, unix : output/tables/Table_1_summary_stats.csv
- Line 43, unix : output/tables/Table_1_summary_stats.tex
- Line 44, unix : output/tables/Table_D14_summary_stats_by_class.csv
- Line 45, unix : output/tables/Table_D14_summary_stats_by_class.tex
- Line 76, unix : # synthetic_pipeline/materialize_simulation.py places it at the path this module reads).
- Line 231, unix : # Use these directly rather than re-merging from raw KPSS/Compustat,
- Line 232, unix : # which causes column collisions (xi_real_x/xi_real_y).
- Line 401, unix : # A. PMA/510(k) Submissions
- Line 965, unix : Input is in MILLIONS for Assets/Valuation rows.
- Line 1243, unix : Panel A, currency formatting for asset/valuation rows, and LaTeX-safe commas.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06a_safety_analysis.py**

- Line 1, unix : #!/usr/bin/env python
- Line 12, unix : data/derived/safety_vars_allpats.csv
- Line 13, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 14, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 15, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 16, unix : data/derived/Adverse_fsize_ready_all4_oct22_24.csv
- Line 18, unix : data/derived/safety_did_analysis.csv
- Line 19, unix : data/derived/safety_did_analysis_3_2.csv
- Line 20, unix : output/tables/ (safety table rows)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py**

- Line 9, unix : This script documents how the invention-year CSVs in data/raw/ were generated.
- Line 43, unix : data/raw/innovation_year_FDA_project.csv (column `response`),
- Line 51, unix : Outputs produced (now in data/raw/):
- Line 58, unix : - code/11d_reg_design.py  (calculates experience years = year_reclassified - invention year;
- Line 69, unix : # The source CSV contained hand-coded invention/commercial-availability years
- Line 75, unix : # GPT-4o was queried using a separate prompt with 3 few-shot examples (Lens/Contact,
- Line 88, unix : #     code/15_intext_derived_numbers.py::derived_invention_year_validation.
- Line 91, unix : #     PRODUCTCODE/year_reclassified/FDA_own_accord, so corr(its years, hand) = 1.0. Do NOT use this file to
- Line 143, unix : Two of the three inputs ship in data/raw/; the third does not, and this says so
- Line 188, windows : "along with the relevant source.\n\n"
- Line 189, windows : "Here are a few examples:\n\n"
- Line 275, unix : # The 1996/1998 reclassification batch:
- Line 295, windows : "along with the relevant source.\n\n"
- Line 296, windows : "Here are a few examples:\n\n"
- Line 365, unix : # to produce Figures D.11a/b (distribution of device experience years for all
- Line 372, unix : #   4. Send each query to GPT-4o with the same prompt/instructions as Part 2
- Line 407, windows : "along with the relevant source.\n\n"
- Line 408, windows : "Here are a few examples:\n\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/preflight_apimode.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 9, unix : DYLD_INSERT_LIBRARIES=$R_HOME/lib/libR.dylib preload forces API mode.)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_public_source_provenance.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 3, unix : (certification/PUBLIC_SOURCE_PROVENANCE.csv), external-audit R5 F7. Before R5 the ledger existed but NO
- Line 8, unix : source URL/DOI, a version/access date, and a provider checksum, plus a completed review status. Every
- Line 9, unix : such field must be populated (no PENDING/TBD/TODO/empty) for the ledger to pass.
- Line 191, unix : # R7 F8: prose-as-checksum and a dated phrase without reviewer/disposition must FAIL.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/regen_determinism/verify_payload_migration.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 21, unix : - the declared added/removed file sets EXACTLY equal the actual presence delta.
- Line 22, unix : Any mismatch -- or a record still marked PENDING_REGEN -- fails closed, so a silent/unreviewed drift
- Line 41, unix : Determinism (gen1 == gen2), the reviewed inventory match, and the contract/privacy gates are enforced
- Line 42, unix : separately in stage 1 (steps A1/A3); this verifier adds the reviewed-target/migration-record authority.
- Line 61, unix : (synthetic_pipeline/simulated_data/...), the fresh manifest, and the inventory (simulated_data/...)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/run_fromraw_analysis_only.sh**

- Line 1, unix : #!/bin/bash
- Line 82, unix : # run_all sets PYTHONHASHSEED, the single-threaded BLAS/OpenMP pins, FDA_STRICT_INTEXT=1 and
- Line 84, unix : # output/figures or output/tables holds a file (the block above emptied them). The values are still
- Line 106, unix : python3 synthetic_pipeline/preflight_from_raw.py --post-run \
- Line 112, unix : python3 certification/validate_handentered_tables.py \

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD15_CostBenefit.tex**

- Line 11, unix : & \multicolumn{7}{l}{-Attribute 80\% of patent value to business stealing/creative destruction \citep{kogan:2017}.} \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/universe_backend.py**

- Line 2, unix : universe_backend.py -- the shared bridge the entity generators (gen_00d/00e/00g) call instead of
- Line 4, unix : ONCE (from the committed Stage-A parameters + theta), caches them, and hands out firm/patent ids
- Line 165, unix : # patent-owning subset ~ the adverse/patent firm cardinality (committed, rounded)
- Line 216, unix : independent co-membership (drop-in for `_link_remap` on a permno/LPERMNO column). The permnos

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_1_summary_stats.tex**

- Line 14, unix : \textit{A. PMA/510(k) Submissions} & 0.169M & - & - & -\\
- Line 49, unix : \textit{Note}: Table \ref{tab:SummaryStatistics_AllClasses_Reorg} provides summary statistics for each class independently. See \citet{kogan:2017} for more information on the patent market valuation data, which was merged into the patent dataset. The CRSP/Compustat database was used to derive the total assets of firms applying for patent protection as a proxy for firm size. Market values and applicant assets are only available for patents filed by publicly traded firms, representing roughly 30\% of the total sample of patents. Missing observations account for discrepancies between (i) the total FDA device types (5,542) and the number represented in device submissions, adverse event reports, and patents (many device types have no associated patents); (ii) the total number of patents and the number with market valuations and applicant assets; and (iii) the total number of claims and those containing amounts paid. \dag``Regulatory proficiency'' indicates the total number of days a firm has experienced approval delays across all its submitted devices.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_00_dimensions_patent_extraction.py**

- Line 16, unix : does not allow pinning or querying against a prior DSL/version or a historical
- Line 31, unix : certification/EXPECTED_CONFIDENTIAL_REAL_INPUT_HASHES.csv, and the patent-based
- Line 94, unix : as a STRICTER term/phrase match returning far fewer records. Consequently:
- Line 96, unix : the IVD/antigen tests) reproduce the shipped Grant set at ~99-100% recall --
- Line 121, unix : data/raw/pat_search_augment/):
- Line 133, unix : off-target patent sets), so additional/sharper keywords were written for those
- Line 278, unix : is not byte-identical). One rich query per product code; the text/cpc/assignee inputs used

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06_adv_2020.py**

- Line 6, unix : data/raw/MAUDE_2020/masterevent.txt
- Line 7, unix : data/raw/MAUDE_2020/patient.txt
- Line 8, unix : data/raw/MAUDE_2020/deviceproblems.txt
- Line 9, unix : data/raw/MAUDE_2020/problemcodedesc.txt
- Line 12, unix : data/derived/Adv_Event_2020_2022.csv

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex**

- Line 4, unix : % Compustat, Nexis Uni, FDA MAUDE/510(k)/PMA/classification/recall, GRID), so the
- Line 8, unix : % Version 6 (2026-06-10): packaging/reproduction pass. Two table values change
- Line 11, unix : % associated means/SDs updated to the freshly regenerated replication-package
- Line 24, unix : % replication-package values. See my_paper/MANUSCRIPT_CHANGE_LOG.md and the
- Line 124, windows : \newcommand\norm[1]{\left\lVert#1\right\rVert}
- Line 279, unix : I build a two-stage model (formal details in Appendix~\ref{sec:AppendixConcept}) in which firms first invent and finance development, then commercialize and choose safety effort. Reclassification shifts three primitives that govern these choices: the approval delay, the mandated safety level, and effective exposure to tort. Under Class~III/II (regulated), firms face positive approval delays, must meet a mandated level of safety effort, and enjoy a regulatory-compliance safe harbor in tort that lowers expected liability. Under Class~I (deregulated), firms avoid approval delays, choose safety effort to maximize profits, and lose the compliance defense, raising expected liability.
- Line 293, unix : This framework delivers three predictions borne out in the data: (i) both forms of reclassification increase innovation and entry via the delay/finance channel, especially among smaller and inexperienced firms; (ii) safety improves after deregulation (II to I) because expected liability rises when the compliance defense disappears, with larger effects at better-capitalized firms; and (iii) these safety gains are most pronounced for mature device types, where the informational value of premarket review is lower.
- Line 301, unix : \textit{FDA Device Submissions (PMA and 510(k) Databases).} I derive a primary dataset from FDA administrative data on the universe of medical devices submitted for approval/clearance. These data are drawn from the FDA's PMA and 510(k) databases, covering both Class III and II devices. Submissions include the submitting company name, device brand name, medical device type, and submission and approval dates. I use fuzzy matching to form three measures of market dynamics and innovation. First, I measure ``new entry'' by identifying firms submitting approval documents for the first time. Second, I form a measure of ``incumbent entry'' by locating firms that have filed prior approval documents but are starting to submit for approval in a given device type. Third, I isolate the first occurrence of unique device brand names within a device type to form the ``unique device submissions'' measure. These variables are aggregated to the device-type-year level. To measure each firm's regulatory proficiency, I calculate the total approval delays (in days) the submitting firm has experienced up to the date of each submission.
- Line 305, unix : \textit{FDA Adverse Event Reports (MAUDE).} The FDA’s Manufacturer and User Facility Device Experience (MAUDE) database contains roughly 9.2 million device-related reports. I construct a device-type-by-year series of adverse event reports from 1992 to 2019. I focus on “serious” outcomes---deaths, hospitalizations, and life-threatening events---for which manufacturers face mandatory reporting obligations enforced through criminal liability \citep{bragg_florence_chan_2018}. To study heterogeneity by firm size, I link MAUDE-reporting manufacturers to CRSP/Compustat to obtain asset totals for public firms, working down the report-count ranking: the 300 largest reporters account for 84\% of all reports, of which 88 are private firms with no public-firm match and the remainder are linked by automated name clustering with hand-coded corrections. I construct three complementary safety measures, each suited to a different purpose in the analysis. First, simple annual counts of serious events retain the full treated sample and avoid denominator noise; I use these for baseline event-study figures as a benchmark, while acknowledging that levels are sensitive to utilization and reporting intensity (see Appendix \ref{appendix:safety} for more details and robustness checks). Second, where reliable procedure mappings exist, I normalize by exposure---serious events per linked procedure---so that estimates reflect risk conditional on use rather than shifts in volume or case mix; these exposure-adjusted rates serve as a robustness check for treated groups that have linked procedures. Third, I report a “severity share”---serious events divided by total MAUDE reports---which absorbs broad shifts in reporting intensity and utilization to the extent they affect both numerator and denominator. Because reductions in serious events must outpace reductions in overall reports to manifest as product safety improvements, this is a conservative metric that I deploy for cross-device-type comparisons (e.g., by device age) to maintain the full treated sample while aiming to account for utilization. Across these measures, the conclusions are consistent.
- Line 313, unix : \textit{Patent and Patent Applicant Characteristics.} I enrich the patent data with measures of innovation quality and applicant characteristics. Patent quality is assessed using forward citations from other patents and patent market value.\footnotemark \footnotetext{I exclude examiner citations and assign zero values to patent citations and market values when no patents were filed in a given device-type-year.} Market values, derived from \citet{kogan:2017}, are expressed in millions of 2019 dollars (CPI-deflated) and are based on the increase in a patent assignee’s stock price following a USPTO issuance announcement, making them available only for publicly traded firms. I also construct \textit{emphasis on safety}---a device-type-year indicator equal to one if at least one patent filed that year explicitly references safety features---following \citet{clemens2020demand}.\footnotemark \footnotetext{Explicit safety mentions are rare, so I code the measure as binary. See Appendix~\ref{appendix:safety} for details and robustness checks.} This measure allows me to assess how reclassification influences inventors' focus on improving device safety, complementing the adverse event analyses. Lastly, to examine how reclassification affects innovation across firms of different sizes, I link patent applicants to total firm asset holdings from the CRSP/Compustat database.
- Line 317, unix : \footnotetext{Additional guardrails included: (i) outpatient-only scope; (ii) analyte-specific mappings for in vitro diagnostics; and (iii) hard exclusions for E/M, visit/collection/handling, and unlisted/miscellaneous HCPCS families (e.g., 992\textit{xx}). Each proposed linkage required a brief rationale and supporting source(s).}
- Line 366, unix : \footnotetext{Implementation details: For each treated product code, I compute 5-year pre-event means (relative to its reclassification year) and select the two nearest-neighbor controls from the treated group's pre/post regimes (III to II: 510(k)/PMA; II to I: 510(k)/510(k)-exempt). All matched units have at least one pre-period patent. Distance metrics and covariate sets are: (i) \emph{Adverse-event analysis}---Mahalanobis distance on standardized pre-event means of all considered outcomes; using all outcomes guards against noise in pre-event adverse-event rates. (ii) \emph{Innovation/market-structure analyses}---squared Euclidean distance on raw pre-event means of patent counts and new firms patenting, augmented with device-submission counts for Class III to II. (iii) \emph{Patent-quality analysis}---squared Euclidean distance on raw pre-event means of forward-citation rates and real patent-value measures.} Although I do not find evidence of spillovers, I exclude device types that treat the same indications as the treated code. Because many outcomes (e.g., patenting) naturally trend upward over time, aligning pre-event levels via matching improves comparability; accordingly, this matched design is my preferred specification, though results are similar under alternative control groups.\footnotemark \footnotetext{Each event panel contains one treated group and its own matched controls; controls can reappear across panels. In inference, I account for such reuse when clustering standard errors.}
- Line 387, unix : Table \ref{tab:Innovation}, Panel A indicates that down-regulation led to statistically significant increases in patenting rates, unique device submissions, forward citations per patent, and patent market values. The matched-control estimates imply approximately 140--350\% more patents and device submissions per device-type-year (baseline means: 8 patents/yr; 1 submission/yr). Post-event patents receive nearly three times as many forward citations and exhibit double the market value. Panel B reports smaller but economically meaningful responses for deregulation: patenting increased by 62\%, forward citations by 87\%, and market value increased modestly, though these effects are not statistically significant under the matched-control specification.
- Line 406, unix : Panel~A shows that down-regulation (Class III to II) leads to a sharp rise in both new and incumbent entry. New-firm entry significantly increases by 600\% in the FDA submissions data (baseline: 0.1 firms/yr) and by 164\% in the patent data. Incumbents also expand into newly down-regulated device types, though less than the inflow of new entrants.
- Line 453, unix : By contrast, Table \ref{tab:AdverseEvent}, Panel B shows that deregulation (Class~II to I) is associated with marked safety improvements: hospitalization rates, life-threatening incidents, and fatalities fall significantly under most control comparisons, and safety-focused innovation rises. Magnitudes imply an approximately 77\% reduction in annual hospitalizations and a suggestive 40--70\% decline in deaths (pre-mean: 0.2 deaths/yr), relative to counterfactual levels. The probability that any patent emphasizes safety increases by about 80\%, and this effect is robust to alternative measurement approaches (Appendix~\ref{appendix:safety}; Table~\ref{tab:ProbabilitySafetyMentionEffects_Robustness}), mirroring the pattern in FDA adverse‐event data.\footnotemark \footnotetext{Inventors also show a heightened focus on quality in patent texts post-deregulation, implying that removing regulatory controls on efficacy and quality does not diminish quality.}
- Line 605, mixed : \includegraphics[trim=0cm 0cm 0cm 0.5cm, clip, width=0.49\textwidth]{../replication_package/output/figures/ContactLens_patents.png}
- Line 608, mixed : \includegraphics[trim=0cm 0cm 0cm 0.5cm, clip, width=0.49\textwidth]{../replication_package/output/figures/ContactLens_submissions.png}
- Line 614, mixed : \includegraphics[trim=0cm 0cm 0cm 0.5cm, clip, width=0.49\textwidth]{../replication_package/output/figures/ContactLens_firms.png}
- Line 628, unix : \includegraphics[trim=0cm 0cm 0cm 0cm,scale = .49]{../replication_package/output/figures/Deregulation_May31_23_Paper.png}
- Line 646, unix : %   \centering \begin{overpic}[trim=0cm 0cm 0cm 0cm,scale=0.4]{../Figures/Spinal_Firms.png}
- Line 647, unix : %      \put(13,22){\includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.35]{../Figures/SpinalFusion.png}}
- Line 652, unix : %   \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.4]{../Figures/Spinal_Firms_Adv.png}
- Line 665, unix : % \centering \includegraphics[trim=8cm 0cm 0cm 6cm,scale=0.25]{../Figures/3_2_logged_Main_Panel.png}
- Line 677, unix : \subfloat[Patenting Rate, Down-Regulation (Class III to II)]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_real_pats_oct22_24.png}
- Line 678, unix : \put(13,60){\tiny Base rate: 6.3 patents/yr}
- Line 681, unix : \subfloat[Device Submission Rate, Down-Regulation]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_dev_count_oct22_24.png}
- Line 682, unix : \put(13,60){\tiny Base rate: 0.9 dev/yr}
- Line 687, unix : \subfloat[Patenting Rate, Deregulation (Class II to I)]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_real_pats_oct22_24.png}
- Line 688, unix : \put(13,60){\tiny Base rate: 14.8 patents/yr}
- Line 692, unix : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_dev_count_solo.png}
- Line 703, unix : %   \includegraphics[scale = .35]{../Figures/3_2_nolog_absnew_firm_count_solo_CTs.png}
- Line 706, unix : %   \includegraphics[scale = .35]{../Figures/3_2_nolog_firm_expansion_solo_CTs.png}
- Line 718, unix : %   \includegraphics[scale = .35]{../Figures/2_1_nolog_real_pats_solo_CTs.png}
- Line 721, unix : %   \includegraphics[scale = .35]{../replication_package/output/figures/2_1_nolog_dev_count_solo.png}
- Line 726, unix : %   \includegraphics[scale = .35]{../Figures/2_1_nolog_times_cited_solo_CTs.png}
- Line 729, unix : %   \includegraphics[scale = .35]{../Figures/2_1_nolog_xi_real_solo_CTs.png}
- Line 744, unix : \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_unique_firms_solo_CTs.png}
- Line 745, unix : \put(13,60){\tiny Base rate: 3.0 firms/yr}
- Line 748, unix : \subfloat[New Firms Patenting, Deregulation (Class II to I)]{ \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_unique_firms_oct22_24.png}
- Line 749, unix : \put(13,60){\tiny Base rate: 6.8 firms/yr}
- Line 755, unix : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.365]{../replication_package/output/figures/3_2_nolog_Price_solo_CTs_sept20_25.png}
- Line 758, unix : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.365]{../replication_package/output/figures/2_1_nolog_Price_solo_CTs_sept20_25.png}
- Line 771, unix : %  \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.28]{../replication_package/output/figures/3_2_nolog_unique_firms_solo_CTs.png}
- Line 772, unix : %      \put(13,60){\tiny Base rate: 3.0 firms/yr}
- Line 776, unix : %  \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.28]{../Figures/3_2_nolog_absnew_firm_count_solo_CTs.png}
- Line 777, unix : %      \put(13,60){\tiny Base rate: 1 firm/10 yrs}
- Line 781, unix : %  \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.28]{../Figures/2_1_nolog_unique_firms_solo_CTs.png}
- Line 782, unix : %      \put(13,60){\tiny Base rate: 7 firms/yr}
- Line 790, unix : %   \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/IIItoIIPrices_latest.png}
- Line 793, unix : %   \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/IItoIPrices_latest.png}
- Line 813, unix : \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_v_serious_oct22_24.png}
- Line 814, unix : \put(55,60){\tiny Base rate: 0.6 events/yr}
- Line 818, unix : \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_v_serious_oct22_24.png}
- Line 819, unix : \put(40,60){\tiny Base rate: 0.5 events/yr}
- Line 825, unix : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_v_serious_normalizable_oct22_24.png}
- Line 828, unix : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_v_serious_restrict_oct22_24.png}
- Line 847, unix : \includegraphics[trim=0cm 0cm 0cm 1.7cm,clip,scale=0.42]{../replication_package/output/figures/2_1_Safety_Top_Decile_Present_oct22_24.png}
- Line 851, unix : \includegraphics[trim=0cm 0cm 0cm 1.7cm,clip,scale=0.42]{../replication_package/output/figures/2_1_Deaths_Top_Decile_oct22_24.png}
- Line 868, mixed : %   \includegraphics[width=0.5\linewidth]{../Figures/2_1_logged_Main_Panel_real_pats.png}
- Line 872, mixed : %   \includegraphics[width=0.5\linewidth]{../Figures/2_1_logged_Main_Panel_times_cited.png}
- Line 878, mixed : %   \includegraphics[width=0.5\linewidth]{../Figures/2_1_logged_Main_Panel_xi_real.png}
- Line 899, unix : %     \subfloat{{\includegraphics[trim=30cm 35cm 30cm 35cm,scale=0.3]{../Figures/IIItoIICostsBenefits.png} }}%
- Line 905, unix : %     \subfloat{{\includegraphics[trim=30cm 35cm 30cm 35cm,scale=0.3]{../Figures/IItoICostsBenefits.png} }}%
- Line 916, unix : \input{../replication_package/output/tables/Table_1_summary_stats.tex}
- Line 1050, unix : %         \hspace{6mm} Applicant Assets (CRSP/Compustat) & 377,465 &  \$26.68B &       \$54.82B	\\
- Line 1106, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex}
- Line 1113, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex}
- Line 1153, unix : \input{../replication_package/output/tables/Formatted/RegTable_Prices_3_2_sep25.tex}
- Line 1159, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_MarketComposition_NoLog_oct22_24.tex}
- Line 1173, unix : \input{../replication_package/output/tables/Formatted/RegTable_Prices_2_1_sep25.tex}
- Line 1180, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_MarketComposition_NoLog_oct22_24.tex}
- Line 1212, unix : \hspace{-1mm}\input{../replication_package/output/tables/Formatted/PaperRegTableSafety_IIItoII_NoLog.tex}
- Line 1213, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_AdverseEvent_NoLog_oct22_24.tex}
- Line 1220, unix : \hspace{-1mm}\input{../replication_package/output/tables/Formatted/PaperRegTableSafety_IItoI_NoLog.tex}
- Line 1221, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex}
- Line 1298, unix : \textit{Rationale.} This action formed part of the Food and Drug Administration Modernization Act (FDAMA, 1997) follow-through on legacy (pre-1976) Class~III types with substantial clinical history. FDAMA~\S515(i) directed the agency to resolve the status of pre-amendment Class~III devices lacking final regulations or PMA requirements. The reclassification was therefore deadline- and process-driven, leveraging long-run safety/effectiveness experience rather than recent technological advances.
- Line 1332, unix : Two agency actions---in 1996 and 1998---removed 510(k) requirements for selected Class~II devices. The 1996 action was part of a resource-reallocation strategy to focus review on higher-risk submissions \citep{FR58:37378,FR60:38903}. To prioritize candidates, the FDA used an internal \emph{Device Priority Model} (DPM) that combined injury frequencies (deaths, serious, less-serious) with expected use, health benefit, and effectiveness \citep{FR60:38903}. Injury components increased the score; higher benefit/effectiveness or lower use reduced it. Because exact cutoffs and some inputs were not public, I proxy the DPM with a weighted index of average annual adverse-event counts,
- Line 1342, unix : The 1998 deregulation implemented FDAMA~\S510(m)(1) (1997), which directed the FDA to list Class~II devices no longer needing 510(k) \citep{FR63:3142}. Internal scoring was paired with four criteria: (i) no reported deaths in prior years; (ii) well-understood characteristics for safe/effective performance; (iii) device changes are either readily detectable by users or unlikely to raise risk; and (iv) modifications are unlikely to create a new device type. These criteria did not hinge on short-run technological improvements or outcome trends, and the agency did not publish exact scores.
- Line 1348, unix : \textbf{Class~I (low risk).} Subject to general controls.\footnotemark \footnotetext{``Low risk'' refers to devices that do not support/sustain life and do not present unreasonable risk (e.g., tongue depressors).}~About 41\% of product codes are Class~I, and roughly 90\% of those are exempt from premarket submissions beyond facility registration. New devices may be Class~I if intended use and key characteristics match an existing Class~I type; novel intended use or technology can trigger a new device type requiring review.\footnotemark \footnotetext{Manufacturers can also seek a De Novo classification when appropriate; see \citet{fda:CFR}.}
- Line 1365, unix : I model R\&D as a two-stage process: development and commercialization. First, firms invent and patent a new product, improve its safety profile, and raise capital to cover commercialization. Second, firms bring their products to market by attaining regulatory approval/clearance, forming distribution networks, etc. The model builds on that of \citet{budish2015firms}, who formalize the impacts of commercialization lags on innovation. For comparability, I follow their notation closely wherever possible. I introduce into their framework two alternative policy regimes (i.e., regulation and litigation) that differ in commercialization lags, liability risk, and financing costs.
- Line 1507, windows : \quad\Longrightarrow\quad
- Line 1700, unix : Primary CPC: A61L12/08
- Line 1708, unix : Primary CPC: A61K48/0058
- Line 1715, unix : Although suggested product codes are often inaccurate, the device/not-device flag is informative. Restricting to patents flagged as devices narrows the sample to 302{,}140 patents during 1996–2015. I also use this screened set to calibrate the patent-topic model so that non-device patents do not drive topics.
- Line 1724, unix : I use the novelty/radicalness index of \citet{KellySeru:2021} to proxy for “breakthrough” patents. The indicator identifies patents that are textually novel relative to prior art and similar to subsequent patents. The distribution is highly skewed in the device-type-year panel (1{,}584 observations): $\approx$81\% zeros; right tail up to 51; mean 0.66; s.d. 3.20. DiD estimates in Table~\ref{tab:BreakthroughPatentsEffects} broadly mirror the main patent‐quality results: breakthrough counts rise post‐reclassification, especially for Class~III to II. Quasi‐Poisson estimates are similar but imprecise because Conley–Taber standard errors are unavailable for non‐linear models and treated units are few; linear specifications with Conley–Taber errors yield tighter intervals.
- Line 1757, unix : Recalls directly address serious defects, are supervised/mandated by the FDA, are less sensitive to utilization, and are difficult to conceal. Recall data begin in 2000, whereas the primary II to I events occur in 1996 and 1998, so I focus on long-run dynamics. Administrative recall data by device type from 2000–2022 show patterns consistent with the adverse-event and safety‐text analyses. To contextualize the timing, Figure~\ref{fig:InnovationES}, panel (b), shows an immediate rise in available technologies after reclassification; Figure~\ref{fig:ESProductSafety} shows a small, immediate decline in serious events (with hospitalizations significantly lower), followed by a larger decline five to seven years later as patents in Figure~\ref{fig:InnovationES}, panel (c), diffuse.
- Line 1764, unix : More than 200 Class~II device types were reclassified in 2015 without materially altering tort exposure, while removing 510(k) requirements.\footnotemark \footnotetext{The 2015 event was the first major Class II reclassification since the 1996/8 events analyzed in the main specification.} Before \citetalias{MedtronicvLohr:1996}, 510(k) often preempted state tort claims \citep{flaherty2008defending}; \citetalias{MedtronicvLohr:1996} weakened preemption for Class~II; later, \citetalias{RiegelVMedtronic:2008} restored some protection, but primarily where the FDA imposed device-specific special controls \citep{Costello:2016}.\footnotemark \footnotetext{See, for example, \citetalias{KelseyVAlcon:2019}, involving a contact-lens disinfectant subject to special controls; the court found preemption barred design-defect claims. Similar outcomes have been found for latex gloves, contact lenses, tampons, condoms, angioplasty catheters, wound dressings, tissue adhesive with wound-closure devices, a hemorrhoid-prevention wedge, and electrical-stimulation devices \citep{Munford_2018}.} Most 2015 Class II devices lacked such controls and thus remained exposed to tort liability.\footnotemark \footnotetext{Special controls are typically issued for Class III to II reclassifications.} Using the main matching/estimation strategy, I find no significant changes in hospitalizations, life‐threatening events, deaths, or the composite serious‐events measure (Figure~\ref{fig:SafetyRecalls_IItoI_2015}, Panel (a)); recalls likewise do not change meaningfully for up to eight years (Figure~\ref{fig:SafetyRecalls_IItoI_2015}, Panels (b)--(c)). These null results support liability exposure---not market structure or innovation alone---as the driver of the earlier safety gains. Notably, entry and patenting responses appear larger in 2015 (Figure~\ref{fig:Innovation_2_1_2017}): new‐entrant patenting rises by roughly 39\% within two years (base 11.9 entrants/yr), versus a statistically insignificant 13.0\% rise within two years after the 1996/8 events.\footnotemark \footnotetext{Data limit the horizon to two years post-policy. The 2015 event adds about five new firms per year relative to pre-event means; the 1996/8 events add about one.} Because the 2015 event reduced regulatory costs without raising litigation exposure, innovation benefits may be larger than they were historically.
- Line 1799, windows : \noindent\itshape
- Line 1838, unix : %    \includegraphics[trim=0cm 0cm 0cm 0cm, scale = .65]{../Figures/LiabilityFunction.png}
- Line 1853, unix : % \centering \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.6]{../Figures/Liability3_2.png}
- Line 1865, unix : \subfloat[Down-Regulation Events]{\includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, scale=0.45]{../replication_package/output/figures/Distribution_of_3_2_over_years.png}}
- Line 1867, unix : \subfloat[Deregulation Events]{\includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, scale=0.45]{../replication_package/output/figures/Distribution_of_2_1_over_years.png}}
- Line 1883, unix : \centering \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.57]{../replication_package/output/figures/Data_new_latest.png}
- Line 1901, unix : \begin{overpic}[trim=0cm 0cm 0cm 0cm,scale=0.50]{../replication_package/output/figures/3_2_nolog_real_pats_petitioned_oct22_24.png}
- Line 1902, unix : \put(15,60){\footnotesize Base rate: 7.5 patents/yr}
- Line 1914, mixed : %     \centering\includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../Figures/Event_to_RegScrutiny.png}
- Line 1948, unix : %   \includegraphics[scale = .4]{../Figures/3_2_nolog_times_cited_oct22_24.png}
- Line 1951, unix : %   \includegraphics[scale = .4]{../Figures/3_2_nolog_xi_real_2019_oct22_24.png}
- Line 1970, unix : %   \includegraphics[scale = .4]{../Figures/2_1_nolog_times_cited_oct22_24.png}
- Line 1973, unix : %   \includegraphics[scale = .4]{../Figures/2_1_nolog_xi_real_2019_oct22_24.png}
- Line 2000, unix : % \centering \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../Figures/3_2_nolog_q_solo_CTs.png}
- Line 2015, unix : %   \includegraphics[width = \textwidth]{../Figures/3_2_nolog_PaidAmt_solo_CTs.png}
- Line 2020, unix : % %   \includegraphics[scale = .39]{../Figures/3_2_nolog_BilledAmt_solo_CTs.png}
- Line 2045, unix : \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_absnew_firm_count_oct22_24.png}
- Line 2046, unix : \put(15,60){\tiny Base rate: 0.1 firms/yr}
- Line 2049, unix : \subfloat[Incumbent Entry (Device Data), Down-Regulation]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_firm_expansion_oct22_24.png}
- Line 2050, unix : \put(15,60){\tiny Base rate: 0.3 firms/yr}
- Line 2055, unix : \subfloat[Incumbent Entry (Patent Data), Deregulation (II to I)]{ \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/2_1_nolog_firm_expansion_patents_oct22_24.png}
- Line 2056, unix : \put(15,60){\tiny Base rate: 2.2 firms/yr}
- Line 2059, unix : \subfloat[Incumbent Entry (Patent Data), Down-Regulation]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../replication_package/output/figures/3_2_nolog_firm_expansion_patents_oct22_24.png}
- Line 2060, unix : \put(15,60){\tiny Base rate: 1.5 firms/yr}
- Line 2078, unix : %   \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/3_2_nolog_patents_incumbent_oct22_24.png}
- Line 2079, unix : %      \put(15,60){\tiny Base rate: 6.3 pats/yr}
- Line 2082, unix : %   \subfloat[Entrant Patenting, Down-Regulation]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/3_2_nolog_patents_entrants_oct22_24.png}
- Line 2083, unix : %      \put(15,60){\tiny Base rate: 0 pats/yr}
- Line 2088, unix : %  \subfloat[Incumbent Patenting, Deregulation (II to I)]{ \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/2_1_nolog_patents_incumbent_oct22_24.png}
- Line 2089, unix : %      \put(15,60){\tiny Base rate: 14.8 pats/yr}
- Line 2092, unix : %   \subfloat[Entrant Patenting, Deregulation]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/2_1_nolog_patents_entrants_oct22_24.png}
- Line 2093, unix : %      \put(15,60){\tiny Base rate: 0 pats/yr}
- Line 2113, unix : %   \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.45]{../Figures/2_1_nolog_Price_labs_solo_CTs.png}
- Line 2117, unix : % %   \subfloat[Logged Price Event Study, DME]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.35]{../Figures/2_1_nolog_Price_DME_solo_CTs.png}
- Line 2123, unix : %  \subfloat[Logged Price Raw Trends, Labs]{ \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.45]{../Figures/2_1_labs_price_raw_trends.png}
- Line 2127, unix : %   % \subfloat[Logged Price Raw Trends, DME]{\begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.32]{../Figures/2_1_DME_price_raw_trends.png}
- Line 2144, unix : %     \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../Figures/mkt_structure_interactions.png}
- Line 2158, unix : %     \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../Figures/Initial_Competition_Innovation.png}
- Line 2171, unix : \subfloat[Change in Patent Topics, Down-Regulation]{\includegraphics[trim=0cm 0cm 0cm 0.8cm,clip,scale=.45]{../replication_package/output/figures/variety_3_2.png}}
- Line 2173, unix : \subfloat[Change in Patent Topics, Deregulation]{\includegraphics[trim=0cm 0cm 0cm 0.8cm,clip,scale=.45]{../replication_package/output/figures/variety_2_1.png}}
- Line 2192, mixed : \includegraphics[width = 0.48\textwidth]{../replication_package/output/figures/LBDEstimation.png}
- Line 2195, mixed : \includegraphics[width = 0.48\textwidth]{../replication_package/output/figures/LBDEstimation_ProductCount.png}
- Line 2210, unix : %         \includegraphics[width=\textwidth]{../Figures/Simulation.png} % first figure itself
- Line 2218, unix : %         \includegraphics[width=\textwidth]{../Figures/LBDsimulationIIItoII.png} % second figure itself
- Line 2236, mixed : %     \centering\includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.65]{../Figures/LBDEstimation_Separated.png}
- Line 2250, unix : %   \includegraphics[scale = .39]{../Figures/2_1_nolog_unique_firms_solo_CTs.png}
- Line 2255, unix : %   \includegraphics[scale = .39]{../Figures/2_1_nolog_firm_expansion_patents_solo_CTs.png}
- Line 2268, unix : %     \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../Figures/LBDGammaSim.png}
- Line 2291, mixed : \includegraphics[width = 0.48\textwidth]{../replication_package/output/figures/3_2_smallvlarge.png}
- Line 2294, mixed : \includegraphics[width = 0.48\textwidth]{../replication_package/output/figures/2_1_smallvlarge.png}
- Line 2299, unix : %  \includegraphics[scale = .3]{../Figures/FirmSizesimulationIIItoII.png}
- Line 2302, unix : %  \includegraphics[scale = .3]{../Figures/FirmSizesimulationIItoI.png}
- Line 2310, unix : %     \includegraphics[width=\textwidth]{../Figures/3_2_SideGig_smallvlarge.png} % first figure itself
- Line 2318, unix : %     \includegraphics[width=\textwidth]{../Figures/2_1_SideGig_smallvlarge.png} % second figure itself
- Line 2349, unix : %   \includegraphics[scale = .35]{../Figures/3_2_nolog_L_oct22_24.png}
- Line 2352, unix : %   \includegraphics[scale = .35]{../Figures/3_2_nolog_H_oct22_24.png}
- Line 2357, unix : %   \includegraphics[scale = .35]{../Figures/3_2_nolog_D_oct22_24.png}
- Line 2360, unix : %   \includegraphics[scale = .35]{../replication_package/output/figures/3_2_nolog_v_serious_oct22_24.png}
- Line 2375, unix : %   \includegraphics[scale = .35]{../Figures/2_1_nolog_L_oct22_24.png}
- Line 2378, unix : %   \includegraphics[scale = .35]{../Figures/2_1_nolog_H_oct22_24.png}
- Line 2383, unix : %   \includegraphics[scale = .35]{../Figures/2_1_nolog_D_oct22_24.png}
- Line 2386, unix : %   \includegraphics[scale = .35]{../replication_package/output/figures/2_1_nolog_v_serious_oct22_24.png}
- Line 2402, mixed : \subfloat[Safety Emphasis, Raw Trends]{\includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,width = 0.68\textwidth]{../replication_package/output/figures/Safety_emphasis_raw_trends.png}}
- Line 2404, mixed : \subfloat[Safety Emphasis, Event Study]{\includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,width = 0.7\textwidth]{../replication_package/output/figures/2_1_nolog_safety_prop_oct22_24.png}}
- Line 2432, mixed : \includegraphics[width=0.65\textwidth]{../replication_package/output/figures/cases_preemption.png}
- Line 2439, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, width=0.65\textwidth]{../replication_package/output/figures/Bankruptcy_1996_raw_trend.png}
- Line 2464, unix : \includegraphics[scale = .32]{../replication_package/output/figures/exp_vs_impact_v_serious_est_3_2.png}
- Line 2467, unix : \includegraphics[scale = .32]{../replication_package/output/figures/exp_vs_impact_patent_est_3_2.png}
- Line 2472, unix : \includegraphics[scale = .32]{../replication_package/output/figures/exp_vs_impact_v_serious_est_2_1.png}
- Line 2475, unix : \includegraphics[scale = .32]{../replication_package/output/figures/exp_vs_impact_patent_est_2_1.png}
- Line 2498, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, width=0.7\textwidth]{../replication_package/output/figures/Distribution_of_3_over_years.png}
- Line 2503, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, width=0.7\textwidth]{../replication_package/output/figures/Distribution_of_2_over_years.png}
- Line 2521, unix : %   \begin{overpic}[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.50]{../Figures/Denovos_stability.png}
- Line 2535, mixed : %    \includegraphics[width = .9\textwidth]{../Figures/Safety_Effort_Theory.png}
- Line 2566, mixed : %   \includegraphics[width=0.49\linewidth]{../Figures/DPM_Deaths.png}
- Line 2570, mixed : %   \includegraphics[width=0.49\linewidth]{../Figures/DPM_LifeThreat.png}
- Line 2575, mixed : %   \includegraphics[width=0.49\linewidth]{../Figures/DPM_Hospital.png}
- Line 2591, unix : %   \centering \begin{overpic}[trim=0cm 0cm 0cm 0cm,scale=0.5]{../Figures/Contact_Firms.png}
- Line 2592, unix : %      \put(15,30){\includegraphics[scale=0.27]{../FDA_Presentation_Latest/cooperVision}}
- Line 2593, unix : %      \put(60,20){\includegraphics[scale=0.25 ]{../FDA_Presentation_Latest/dailies}}
- Line 2614, unix : \centering \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../replication_package/output/figures/3_2_nolog_patents_pats_nodrugs_oct22_24.png}
- Line 2631, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, width=0.49\textwidth]{../replication_package/output/figures/Recalls_1996_raw_trend.png}
- Line 2634, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, width=0.49\textwidth]{../replication_package/output/figures/Recalls_1996_raw_trend_intuitive.png}
- Line 2641, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm, clip, width=0.65\textwidth]{../replication_package/output/figures/2_1_no_log_recalls_1996.png}
- Line 2668, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,width=.9\linewidth]{../replication_package/output/figures/2_1_no_logv_serious_2016_oct22_24.png}
- Line 2674, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,width=.9\linewidth]{../replication_package/output/figures/Recalls_2017.png}
- Line 2684, mixed : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,width=0.5\textwidth]{../replication_package/output/figures/Recalls_2017_raw_trends.png}
- Line 2704, unix : \centering \includegraphics[trim=0cm 0cm 0cm 0cm,scale=0.5]{../replication_package/output/figures/NewFirmsPatenting_2017.png}
- Line 2720, unix : %   \begin{overpic}[trim=0cm 0cm 0cm 0cm,scale=0.50]{../Figures/Hospital_bed.png}
- Line 2721, unix : %      \put(40,60){\footnotesize Base rate: 50 events/yr}
- Line 2737, unix : \subfloat[Serious Adverse Events, Excluding Manufacturers]{\includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.4]{../replication_package/output/figures/2_1_nolog_v_serious_voluntary_oct22_24.png}}
- Line 2739, unix : \subfloat[Serious Adverse Events, Manufacturers]{\includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.4]{../replication_package/output/figures/2_1_nolog_v_serious_manuf_oct22_24.png}}
- Line 2766, unix : %      \centering{\includegraphics[scale=0.2]{../Figures/Patent_Citation_Dist.png} }
- Line 2783, unix : % \centering \includegraphics[trim=0cm 0cm 0cm 0cm ,scale=0.2]{../Figures/LBDResidPlot.png}
- Line 2793, unix : %      \centering {\includegraphics[scale=0.5]{../Figures/Event_Estimation_3_2.png} }
- Line 2846, unix : \input{../replication_package/output/tables/Formatted/TableD1_SampleConstruction.tex}
- Line 2903, unix : Hip joint metal/polymer constrained prosthesis. & Orthopedic Devices & 2001 & OSMA & 67 FR 21173 \\
- Line 2944, unix : CFJ & NAD Reduction/NADH Oxidation, Lactate Dehydrogenase & 83615 &  & Lactate dehydrogenase (LDH) quantitative assay. \\
- Line 2948, unix : FNM & Mattress, Air Flotation, Alternating Pressure &  & E0277 & Powered pressure-reducing air mattress (alternating/low air loss) furnished as DME. \\
- Line 2953, unix : JGQ & Turbidimetric, Total Protein & 84155 &  & Total protein; quantitative assay (serum/plasma) -- turbidimetric method. \\
- Line 2982, windows : \centering\footnotesize
- Line 2991, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex}
- Line 3002, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_Main_Panel_Log_oct22_24.tex}
- Line 3013, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_poisson_oct22_24.tex}
- Line 3019, windows : \centering\footnotesize
- Line 3028, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex}
- Line 3039, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_Main_Panel_Log_oct22_24.tex}
- Line 3050, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_Main_Panel_NoLog_poisson_oct22_24.tex}
- Line 3084, windows : \centering\scriptsize
- Line 3094, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_RegTable_Prices_3_2_sep25.tex}
- Line 3107, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_PaperRegTable3_2_MarketComposition_NoLog_oct22_24.tex}
- Line 3120, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_MarketComposition_Log_oct22_24.tex}
- Line 3133, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_MarketComposition_NoLog_poisson_oct22_24.tex}
- Line 3139, windows : \centering\scriptsize
- Line 3150, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_RegTable_Prices_2_1_sep25.tex}
- Line 3163, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_PaperRegTable2_1_MarketComposition_NoLog_oct22_24.tex}
- Line 3176, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_MarketComposition_Log_oct22_24.tex}
- Line 3189, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_MarketComposition_NoLog_poisson_oct22_24.tex}
- Line 3225, windows : \centering\footnotesize
- Line 3234, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_PaperRegTable3_2_AdverseEvent_NoLog_oct22_24.tex}
- Line 3245, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_AdverseEvent_Log_oct22_24.tex}
- Line 3256, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_AdverseEvent_NoLog_poisson_oct22_24.tex}
- Line 3262, windows : \centering\footnotesize
- Line 3271, unix : \input{../replication_package/output/tables/Formatted/DIDimpute_PaperRegTable2_1_AdverseEvent_NoLog_oct22_24.tex}
- Line 3282, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_AdverseEvent_Log_oct22_24.tex}
- Line 3293, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_poisson_oct22_24.tex}
- Line 3326, unix : \input{../replication_package/output/tables/Formatted/PaperRegTableSpillovers_3_2_Spillovers_NoLog.tex}
- Line 3333, unix : \input{../replication_package/output/tables/Formatted/PaperRegTableSpillovers_2_1_Spillovers_NoLog.tex}
- Line 3367, unix : Vascular graft prosthesis---Synthetic/Biologic Composite  &  Cardiovascular Devices---Cardiovascular Prosth... &          1 &            1 \\
- Line 3419, unix : Clinical Chemistry/Toxicology---Test Systems & 6 & 0 & 6 & 0 \\
- Line 3420, unix : Clinical Chemistry/Toxicology---Laboratory Instruments & 3 & 0 & 3 & 0 \\
- Line 3487, windows : \centering\footnotesize
- Line 3496, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_No0_oct22_24.tex}
- Line 3502, windows : \centering\footnotesize
- Line 3511, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_Main_Panel_NoLog_No0_oct22_24.tex}
- Line 3525, windows : \centering\footnotesize
- Line 3534, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_MarketComposition_NoLog_No0_oct22_24.tex}
- Line 3540, windows : \centering\footnotesize
- Line 3549, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_MarketComposition_NoLog_No0_oct22_24.tex}
- Line 3563, windows : \centering\footnotesize
- Line 3572, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_AdverseEvent_NoLog_No0_oct22_24.tex}
- Line 3578, windows : \centering\footnotesize
- Line 3587, unix : \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_No0_oct22_24.tex}
- Line 3608, unix : \input{../replication_package/output/tables/Formatted/TableD11_Utilization.tex}
- Line 3632, unix : % \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_No0_oct22_24.tex}
- Line 3639, unix : % \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_Main_Panel_NoLog_No0_oct22_24.tex}
- Line 3679, unix : % % \input{../Tables/Formatted/RegTable_Prices_3_2.tex}
- Line 3685, unix : % \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_MarketComposition_NoLog_No0_oct22_24.tex}
- Line 3699, unix : % % \input{../Tables/Formatted/RegTable_Prices_2_1.tex}
- Line 3706, unix : % \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_MarketComposition_NoLog_No0_oct22_24.tex}
- Line 3739, unix : % % \hspace{-1mm}\input{../replication_package/output/tables/Formatted/PaperRegTableSafety_IIItoII_NoLog.tex}
- Line 3740, unix : % \input{../replication_package/output/tables/Formatted/PaperRegTable3_2_AdverseEvent_NoLog_No0_oct22_24.tex}
- Line 3747, unix : % % \hspace{-1mm}\input{../replication_package/output/tables/Formatted/PaperRegTableSafety_IItoI_NoLog.tex}
- Line 3748, unix : % \input{../replication_package/output/tables/Formatted/PaperRegTable2_1_AdverseEvent_NoLog_No0_oct22_24.tex}
- Line 3859, unix : \input{../replication_package/output/tables/Formatted/TableD12_SafetyRobustness.tex}
- Line 3875, unix : \input{../replication_package/output/tables/Formatted/TableD11a_DeviceExperience_3_2.tex}
- Line 3880, unix : \input{../replication_package/output/tables/Formatted/TableD11b_DeviceExperience_2_1.tex}
- Line 3887, unix : \input{../replication_package/output/tables/Formatted/TableD15_CostBenefit.tex}
- Line 3896, unix : \input{../replication_package/output/tables/Table_D14_summary_stats_by_class.tex}
- Line 3919, unix : %      5 &          0 &  Vascular graft prosthesis---w/o coating&   Prosthetic  &               Cardiovascular &            \checkmark &                                 \\
- Line 3962, unix : \input{../replication_package/output/tables/Formatted/TableD15_RestrictedSamples.tex}
- Line 3987, unix : \input{../replication_package/output/tables/Formatted/TableD16_BreakthroughPatents.tex}
- Line 4056, unix : % \input{../Tables/Corr_Size_Experience.tex} %from Corr_Size_Experience.do
- Line 4081, unix : % \input{../Tables/Formatted/PaperRegTable3_2_Main_Panel_NoLog_NoDrugs_A61_oct22_24.tex}
- Line 4088, unix : % \input{../Tables/Formatted/PaperRegTable2_1_Main_Panel_NoLog_NoDrugs_A61_oct22_24.tex}
- Line 4114, unix : % \input{../Tables/LBDGammaEst_oct22_24.tex}

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_immutable_tree.py**

- Line 1, unix : #!/usr/bin/env python3

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_candidate_zip.py**

- Line 1, unix : #!/usr/bin/env python3

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_06b_permno_universe.py**

- Line 20, unix : data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv
- Line 22, unix : package because it carries CRSP/KPSS/Compustat-derived PERMNOs).
- Line 24, unix : Source logic: `my_paper/analysis/code/Dedupe_Manuf_firm_size_adverse_events.py`

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03b_lbd_clusters.py**

- Line 5, unix : data/derived/AD_data_applicant_df_oct22_24.csv   (device-level clusters)
- Line 6, unix : data/derived/AD_data_applicant_df2_oct22_24.csv  (applicant-level clusters)
- Line 28, unix : data/derived/Applicant_Device_data.csv
- Line 29, unix : data/raw/501k_all.csv
- Line 30, unix : data/raw/all_pma_approvals.txt
- Line 31, unix : data/derived/dedupe_settings/dedupe_dataframe_learned_settings
- Line 32, unix : data/derived/dedupe_settings/dedupe_dataframe_training.json
- Line 35, unix : data/derived/AD_data_applicant_df_oct22_24.csv
- Line 36, unix : data/derived/AD_data_applicant_df2_oct22_24.csv

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_11d.sh**

- Line 1, unix : #!/bin/bash
- Line 4, unix : # market-age regression step. Only data/raw/innovation_year_2_1_FDA_project.csv
- Line 31, unix : --env HOME=/tmp,PYTHONHASHSEED=0,MPLCONFIGDIR=/tmp/mpl \

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10_table_formatting.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 6, unix : pre-treatment means/SDs from the matched sample data, and assembles
- Line 18, unix : data/derived/ (matched sample CSVs for pre-treatment means)
- Line 21, unix : output/tables/Formatted/
- Line 227, unix : For MainPanel/MarketComposition: use the _onepat_innovation matched sample.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_05_adverse_fsize.py**

- Line 5, unix : to CRSP/Compustat identifiers via pandas_dedupe. The manufacturer→permno
- Line 10, unix : data/raw/MAUDE/masterevent.txt
- Line 11, unix : data/raw/MAUDE/patient.txt
- Line 12, unix : data/raw/MAUDE/deviceproblems.txt
- Line 13, unix : data/raw/MAUDE/problemcodedesc.txt
- Line 14, unix : data/derived/all_adv_events_w_permno5.csv  (pre-built manufacturer→permno mapping)
- Line 15, unix : data/raw/compustat_firm_data.csv           (Compustat total assets)
- Line 16, unix : data/raw/CPI_deflator.csv                  (CPI deflator for real dollars)
- Line 19, unix : data/derived/Adverse_fsize_ready_all4_oct22_24.csv

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py**

- Line 13, windows : pat = re.compile(r"sk-[A-Za-z0-9_\-]{20,}")
- Line 18, unix : # ---- the deposited prompt, verbatim from code/12b_gpt_price_links_generation.py ----
- Line 23, windows : return ("Device candidate:\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11g_descriptive_figures.py**

- Line 1, unix : #!/usr/bin/env python
- Line 6, unix : from the raw-data directory into output/figures/.
- Line 11, unix : data/raw/Data_new_latest.png                   (pre-made data catalog)
- Line 14, unix : output/figures/Data_new_latest.png
- Line 47, unix : copies it into output/figures/. It is a required manuscript exhibit, so a

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_simulated_payloads.py**

- Line 1, unix : #!/usr/bin/env python3

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/07_firm_heterogeneity.py**

- Line 1, unix : #!/usr/bin/env python
- Line 29, unix : data/derived/safety_vars_allpats.csv
- Line 30, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 31, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 32, unix : data/derived/matched_sample_2_1_onepat_innovation.csv
- Line 33, unix : data/derived/matched_sample_3_2_onepat_innovation.csv
- Line 34, unix : data/derived/Adverse_fsize_ready_all4_oct22_24.csv
- Line 39, unix : output/figures/2_1_Safety_Top_Decile_Present_oct22_24.png
- Line 40, unix : output/figures/2_1_Deaths_Top_Decile_oct22_24.png
- Line 41, unix : output/tables/firm_heterogeneity_k_est.csv
- Line 42, unix : output/tables/firm_heterogeneity_k_pct.csv
- Line 88, unix : Used for safety/adverse event figures (D.7a-b).
- Line 242, unix : # matched every treated unit (92/92, 88/88, 104/104 and 130/130 x3), so this raises only if
- Line 279, unix : k_pct: list of estimate/baseline ratios by tercile
- Line 513, unix : # k_pct stores estimate/baseline
- Line 836, unix : k_pct: list of estimate/baseline ratios by tercile
- Line 960, unix : # k_pct stores estimate/baseline

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_all_numbers.py**

- Line 1, unix : #!/usr/bin/env python3.9
- Line 7, unix : NONZERO if ANY inventory file is missing, unreadable, shape/column-changed,
- Line 49, unix : any governed output carrying a True/False column (the `reproduces` flag in
- Line 50, unix : output/tables/PatentCollectionCounts.csv). Casting to float64 makes a boolean
- Line 51, unix : column compare as 0.0/1.0, so a flag that FLIPS is reported as a difference
- Line 69, unix : # certified numeric CSVs. Passing a different/short/../ inventory cannot trivially pass.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_exhibit_fidelity.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 5, unix : shows. The reference set is the package's own manuscript closure (certification/MANUSCRIPT_CLOSURE.sha256):
- Line 24, unix : # Figures no analysis step computes: 11g_descriptive_figures.py copies them from data/raw/ (the producer map in
- Line 25, unix : # code/audit_pipeline.py says so). They are checked against their pins, not compared as computations.
- Line 80, windows : ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/match_mahal.py**

- Line 7, unix : Inputs: Full_sample.csv from data/derived/

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py**

- Line 4, unix : Stage A is the only real-data READ that produces committed params; gen_00d/gen_00e now read NO
- Line 18, unix : a rounded N cannot single out a rare group -- T5/T6), never the exact count;
- Line 25, unix : `_selftest()` (runs WITHOUT real data) checks the smoothing/rounding logic fails closed.
- Line 54, unix : # INTERLOCK CONTRACT (Stage A writes it here; gen_00d/gen_00e consume EXACTLY this shape).
- Line 70, unix : #                                                                      exact distinct-count/multiset)
- Line 74, unix : # The role classifier below MIRRORS gen_00d's column routing so id/num statistics land on the
- Line 75, unix : # columns that consume them; gen_00e overrides its special columns (patnum/PC/year/cpc/text/...) by
- Line 239, unix : # INTERLOCK per-file specs: assert every committed statistic is rounded/smoothed (no raw stat).
- Line 312, unix : # Per-file, per-column spec extraction (the INTERLOCK payload for gen_00d/gen_00e).
- Line 335, unix : (the pandas dtype string) is PUBLIC structural metadata kept so gen_00d/gen_00e reproduce the
- Line 442, unix : # INTERLOCK: per-file schema + rounded/smoothed column specs for every gen_00d/gen_00e file.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00e_synthetic_patents.py**

- Line 31, unix : # DERIVED/RAW retained ONLY so gen_00a (Stage A) can resolve this generator's real-file paths when
- Line 58, unix : # --- synthetic CPC vocabulary (A61-family SHAPED so the device/drug A61-vs-A61P filter works) ---
- Line 98, unix : committed cardinality + independent co-membership -- no real grid/firm/name survives, and the
- Line 141, unix : # This is the forward-citation lookup `code/09_summary_stats.py` merges onto the patent panel
- Line 158, unix : # treats type/format fidelity as required and as non-disclosive); the VALUES are fully simulated.
- Line 182, unix : # (gen_00g's fake-domain gate covers id/patnum/patent_id columns, not this one.)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py**

- Line 1, unix : #!/usr/bin/env python
- Line 14, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 15, unix : data/derived/matched_sample_2_1_onepat_innovation.csv
- Line 16, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 17, unix : data/derived/matched_sample_3_2_onepat_innovation.csv
- Line 18, unix : data/derived/matched_sample_3_2_onepat_innovation_quality.csv
- Line 19, unix : data/derived/safety_did_analysis.csv            (from 06a_safety_analysis.py)
- Line 20, unix : data/derived/safety_did_analysis_3_2.csv        (from 06a_safety_analysis.py)
- Line 21, unix : data/derived/constrained_adv_event_new_sept25.csv
- Line 22, unix : data/derived/constrained_adv_event_new_sept25_3_2.csv
- Line 29, unix : output/tables/event_study_base_rates.csv
- Line 174, unix : # v_serious Adverse_Events specs above (same panel/reclass/window/matched_file, outcome column only
- Line 175, unix : # differs; the matched-sample df already carries L/H/D/S columns -- see load_matched_sample /
- Line 177, unix : # (treated/control means by event time) feed 15_intext_derived_numbers.py's counterfactual
- Line 178, unix : # hospitalization/death % reductions and the H=-1.77/yr, D=-0.43/yr level estimates. They are
- Line 265, unix : # figures to output/figures/unreported/ (they are not manuscript exhibits).
- Line 377, unix : These are the same pools 03a/03b use for their pooled DiD columns; here they
- Line 401, unix : # The 2_1 parquets already carry the stacked FE column built in 02/03b.
- Line 469, unix : adverse/utilization: ET = year - year_reclass_ET
- Line 472, unix : adverse/utilization: ET = year - year_reclass_ET
- Line 664, unix : + (D_P + S_P + H_P + L_P)      (voluntary/patient)
- Line 890, unix : # writes extra CSVs to output/tables/event_study_coefficients/ so that derived
- Line 900, unix : The treated/control means are the raw outcome means by event time, from
- Line 944, unix : # (certification/COMPARATOR_INVENTORY.txt). A failed export ABORTS the step.
- Line 957, unix : # output/tables/event_study_base_rates.csv, and checked by step 35 against the
- Line 963, unix : # (FDA_own_accord, adverse-event year cut, utilization/normalizable restriction,
- Line 971, unix : # writes ONE new CSV (output/tables/event_study_base_rates.csv) once at the end
- Line 989, unix : # (paper/JPE_submission_v8.tex, lines 678, 682, 688, 745, 749, 814, 819, 1902,
- Line 1085, unix : output/tables/event_study_base_rates.csv with columns

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_1_summary_stats.tex**

- Line 14, unix : \textit{A. PMA/510(k) Submissions} & 0.169M & - & - & -\\
- Line 49, unix : \textit{Note}: Table \ref{tab:SummaryStatistics_AllClasses_Reorg} provides summary statistics for each class independently. See \citet{kogan:2017} for more information on the patent market valuation data, which was merged into the patent dataset. The CRSP/Compustat database was used to derive the total assets of firms applying for patent protection as a proxy for firm size. Market values and applicant assets are only available for patents filed by publicly traded firms, representing roughly 100\% of the total sample of patents. Missing observations account for discrepancies between (i) the total FDA device types (5,542) and the number represented in device submissions, adverse event reports, and patents (many device types have no associated patents); (ii) the total number of patents and the number with market valuations and applicant assets; and (iii) the total number of claims and those containing amounts paid. \dag``Regulatory proficiency'' indicates the total number of days a firm has experienced approval delays across all its submitted devices.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/manufacturer_linkage_coverage.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 25, unix : output/tables/manufacturer_linkage_coverage.csv -- one row per metric:
- Line 30, unix : Manufacturer names and report counts come from MAUDE, which is public. The CRSP/Compustat
- Line 36, unix : data/derived/all_adv_events_w_permno5.csv   (clean_name, permno, manually_encoded)
- Line 37, unix : data/raw/manual_permno_corrections.csv      (the hand-coded `contains` patterns)
- Line 40, unix : code/00_generate_data/gen_07_adverse_permno.py exactly: `contains` is a JSON string or a

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00d_synthetic_dimensions_wrds.py**

- Line 2, unix : gen_00d_synthetic_dimensions_wrds.py -- SYNTHETIC Dimensions + WRDS/CRSP-Compustat
- Line 9, unix : per-column role (public/key/id/num/date) with only ROUNDED cardinalities, SMOOTHED size
- Line 45, unix : # DERIVED/RAW are retained ONLY so gen_00a (Stage A) can resolve this generator's real-file paths
- Line 158, unix : here is public by construction (FDA/Federal-Register design + calendar + MAUDE taxonomy).
- Line 245, unix : # skeleton; patent/firm/safety values are theta-conditioned synthetic DRAWS; patent-derived flags
- Line 498, unix : # within its FE/stack class. A random (PC,year) CELL sample (the generic sampler) fragments each PC's
- Line 500, unix : # code/00_generate_data/gen_04_parquets.py (+ gen_01) with proper event-time windows; this reproduces
- Line 517, unix : # 04_event_studies reads them PRE-STACKED and uses their posttreat/ET directly -- if no treated unit
- Line 527, unix : # unstacked whole-PC one, so their committed FE/class_by_episode/posttreat/ET are a live DiD contrast.
- Line 537, unix : stacked permutation estimator (code/modules/conley_taber.py::_gen_matrix) requires. An off-grid PC
- Line 606, unix : reproducing code/00_generate_data/gen_04_parquets.py::_stack_FE: one stack per treated PC, each
- Line 609, unix : _public_column emits as the `FE` column. This is the structure 03b/07 need: fixest absorbs
- Line 634, unix : # are derived from the committed n_rows + public n_years ALONE, so no real treated/control count is
- Line 764, unix : (PRODUCTCODE, year) and pivot stacked-DiD on (FE/class_by_episode, year), so a panel must NOT carry
- Line 767, unix : grid permutation across ceil(n/N) stacks and returns a per-row `episode` (stack index), so the panel is a

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_output_simulated.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 4, unix : Reads every file under output/figures and output/tables and requires that set to equal
- Line 20, unix : numpy 1.26.4): the plotted estimates are bit-identical, but the dashed pre/post trend lines the
- Line 156, unix : # No file under output/figures or output/tables is exempt: anything the run writes there

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11b_recall_analysis.py**

- Line 1, unix : #!/usr/bin/env python
- Line 17, unix : data/raw/device-recall-0001-of-0001-2.json
- Line 18, unix : data/raw/Class2_Exemptions_2017_Grennan.csv
- Line 19, unix : data/derived/Full_sample.csv
- Line 20, unix : data/derived/Adv_Event_2020_2022.csv
- Line 21, unix : data/derived/RegNum_Factorized_Synth.csv
- Line 22, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 23, unix : data/derived/intuitive_2_1_oct22_24.csv
- Line 24, unix : r_scripts/preprocess.R
- Line 25, unix : r_scripts/did_imputation_topython.R
- Line 28, unix : output/figures/Recalls_2017.png
- Line 29, unix : output/figures/Recalls_2017_raw_trends.png
- Line 30, unix : output/figures/2_1_no_logv_serious_2016_oct22_24.png
- Line 31, unix : output/figures/2_1_no_log_recalls_1996.png
- Line 32, unix : output/figures/Recalls_1996_raw_trend.png
- Line 33, unix : output/figures/Recalls_1996_raw_trend_intuitive.png
- Line 34, unix : output/tables/recall_event_study_1996.csv       (in-text: the recall decline)
- Line 35, unix : output/tables/recall_in_text_numbers.csv        (in-text: decline, % of control
- Line 275, unix : # Pre/post trend lines
- Line 336, unix : output/tables/recall_event_study_1996.csv -- the per-event-time effects and
- Line 338, unix : output/tables/recall_in_text_numbers.csv -- the derived magnitudes:

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py**

- Line 7, unix : A. Verify every manuscript figure/table has a producing replication script
- Line 12, unix : cd replication_package && python code/audit_pipeline.py
- Line 13, unix : open output/replication_audit.html
- Line 64, unix : # Part A: Figure/Table → Script Mapping
- Line 257, windows : _IMAGE_MAGIC = (b"\x89PNG\r\n\x1a\n", b"%PDF", b"\xff\xd8\xff", b"GIF8")
- Line 326, unix : .tex/fragment: an alignment '&' or row break '\\\\' AND at least one digit.
- Line 377, unix : # Written by gen_01 phase 2a; gen_03/gen_03b are its READERS, not its producers.
- Line 431, unix : # For each analysis script, list the derived/raw data files it reads.
- Line 444, unix : # Intuitive/later-treated/spillover samples
- Line 488, unix : # Reads CSV estimate files from output/tables/
- Line 489, unix : # Those are produced by 03a/03b estimation scripts
- Line 773, unix : Most table fragments live in output/tables/Formatted/, but Table 1 and the
- Line 774, unix : by-class summary-stat table live directly in output/tables/. Use the actual
- Line 1139, unix : #   1. Separate .tex files in Tables/ or Tables/Formatted/
- Line 1158, unix : # Source 1: Separate .tex file in Tables/ or Tables/Formatted/
- Line 1195, unix : # Side-by-side diff with green/red highlighting
- Line 1354, unix : # Also fail if the manuscript was not located/parsed at all: a 0-reference audit is meaningless

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/preflight_from_raw.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 5, unix : The simulated-data route runs every transformation on synthetic/public inputs. gen_02 is deferred until
- Line 7, unix : acquired invention-year inputs. The scripts read several inputs from data/raw/ with NO existence guard --
- Line 9, unix : clear PRESENT/MISSING/OPTIONAL table, exiting nonzero if any REQUIRED input is absent, so a coverage
- Line 12, unix : Run AFTER `python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` and BEFORE
- Line 31, unix : # gen-phase I/O map surfaced). REQUIRED = crashes if absent; OPTIONAL = the script guards/skips. ---
- Line 32, unix : PUBLIC_RAW = [   # shipped FDA/public inputs (must be present in a deposited package)
- Line 162, unix : # Exact Phase-4 replacement/filter order from gen_01_main_panels.py.
- Line 264, windows : if (re.search(r"\d\d\d+\.+\d", value)
- Line 265, windows : and not re.search(r"\d\d\d+\.+9", value)):
- Line 390, windows : "output is absent. Next:\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/independent_universe.py**

- Line 17, unix : (which real rows are the same firm/patent), which is exactly the disclosure to remove.
- Line 47, unix : # Generic fake domain for NON-merge NUMERIC identity columns (not permno/gvkey/patnum, so not
- Line 63, unix : # 1. Fresh entity ids -- replaces _link_remap (permno/gvkey) and build_map (patnum).
- Line 195, unix : rounded/smoothed marginal rate -- never the exact real NaN count). Breaks both the per-row

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_generation_lineage.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 4, unix : (synthetic_pipeline/simulated_data/, the files listed in MATERIALIZE_DESTINATIONS.tsv) is generated from a
- Line 14, unix : non-ISO review_date, or empty reviewer/transformation. A declaration alone is not a proof; these

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/analyze_pooled.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 7, unix : invention_years_band/raw_responses.jsonl        (612 codes within 6 years of 1959)
- Line 8, unix : invention_years_outofband/raw_responses.jsonl   (360 codes drawn further out)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/02_match_samples.py**

- Line 1, unix : #!/usr/bin/env python
- Line 9, unix : Inputs: data/derived/Full_sample.csv

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/certify_fromraw_route.sh**

- Line 1, unix : #!/bin/bash
- Line 8, unix : # The certified image is self-contained: it carries ONE Python (3.9.13 at /usr/local/bin/python3,
- Line 37, unix : # container. Existence/executability is checked in the container itself, once the image hash is
- Line 53, unix : # container. Remove every user-controlled implicit bind/environment injection;
- Line 101, unix : # container. Dedicated home/tmp/cache paths contain no host credentials.
- Line 166, unix : # Delete output/figures and output/tables BEFORE the run so the regeneration is provably from empty.
- Line 168, unix : # container), so a silent no-op inside the container cannot hide a stale/reused exhibit.
- Line 172, unix : for sub in output/figures output/tables; do
- Line 178, unix : for sub in output/figures output/tables; do
- Line 190, unix : # image installs; see docker/Dockerfile and certification/SIF_PROVENANCE.json). It was resolved and
- Line 192, unix : # below remains the package tree, the evidence directory and the isolated home/tmp/cache.
- Line 206, unix : # Re-verify the exact 36/0/0 tally from the host, independent of the analysis container's own exit
- Line 211, unix : # Require 36 distinct successful per-step logs, none swallowed/nonzero/ABI-fallback.
- Line 218, unix : for sub in output/figures output/tables; do
- Line 228, unix : # missing=0/differing=0/extras=0 (nothing under output/figures or output/tables is exempt) against whatever is
- Line 237, unix : # Manuscript compile/identity check: hash_manuscript_closure.py enumerates and hashes the full
- Line 242, unix : # this writes into the evidence directory and leaves certification/MANUSCRIPT_CLOSURE.sha256 -- an

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/verify_maude_manufacturer_rebuild.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 4, unix : data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv is a two-column projection of the 23
- Line 5, unix : public FDA MAUDE device files under data/raw/MAUDE/device_data/. It is omitted from the
- Line 15, unix : python3 certification/verify_maude_manufacturer_rebuild.py --root .
- Line 16, unix : python3 certification/verify_maude_manufacturer_rebuild.py --root . --inputs-only

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_02_price_matching.py**

- Line 13, unix : data/derived/outpatient_combined_censored.csv     (PROPRIETARY MarketScan)
- Line 14, unix : data/raw/2_1_GPT_Price_Links.csv                  (GPT-generated)
- Line 15, unix : data/raw/3_2_GPT_Price_Links.csv                  (GPT-generated)
- Line 16, unix : data/derived/matched_sample_3_2_onepat.csv        (from 02_match_samples)
- Line 17, unix : data/derived/matched_sample_2_1_onepat.csv        (from 02_match_samples)
- Line 20, unix : data/derived/constrained_adv_event_new_sept25.csv
- Line 21, unix : data/derived/constrained_adv_event_new_sept25_3_2.csv
- Line 173, unix : # Forward/backward fill
- Line 324, unix : # object/string, but the synthetic MarketScan uses all-numeric synthetic HCPCS (90000+), which pandas

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py**

- Line 21, unix : Inputs (all are aggregate pipeline OUTPUTS already in output/tables/, plus the
- Line 23, unix : - output/tables/PaperAdverseEvent_2_1_Estimates_NoLog_xi_latest_oct22_24.csv
- Line 25, unix : - output/tables/firm_heterogeneity_k_est.csv  (tercile level estimates)
- Line 26, unix : - output/tables/firm_heterogeneity_k_pct.csv  (tercile ratios; #4 = 1.612)
- Line 27, unix : - output/tables/PaperMainPanel_2_1_Estimates_NoLog_xi_latest_oct22_24.csv
- Line 28, unix : - output/tables/cost_benefit_total_value_did.csv  (written by run_all step 34 =
- Line 31, unix : - data/raw/foiclass.txt  (Class II product-code universe, #6 counts)
- Line 41, unix : python3 code/15_intext_derived_numbers.py
- Line 268, unix : # fitted zero-crossing (output/tables/exp_impact_zero_crossings.csv) differs;
- Line 396, unix : # Register the hospitalization (H) and mortality/death (D) central reductions so their absence
- Line 500, unix : sample data/derived/matched_sample_{reclass_type}_onepat_innovation.csv, and return
- Line 548, unix : citations 87%, market value 'increased modestly' (~+18%, n.s.). Baselines '8 patents/yr,
- Line 684, unix : # --- headline magnitudes (Results L210/L387/L212/L406) ---
- Line 836, unix : GPT-4o responses + parsed years ship in data/raw/innovation_year_FDA_project.csv (yr_invent_or_comm_avail
- Line 838, unix : checkable. NOTE: data/raw/innovation_year_3_2_FDA_project.csv is the DOWNSTREAM age-calc file whose
- Line 909, unix : output/tables/event_study_base_rates.csv.
- Line 966, unix : from data/raw/FDA_HCPCS_Xwalk_Moazzam.csv and writes its estimates with
- Line 1034, unix : 1982 dollars, data/raw/KPSS_2019_public.csv) converted to 2019 dollars with the same deflator the rest
- Line 1060, unix : data/raw/spinal_entrant_audit.csv lists the 20 sampled 510(k) applicants (public FDA records,
- Line 1128, unix : pipeline reads (data/raw/MAUDE/masterevent.txt, read by
- Line 1129, unix : code/00_generate_data/gen_01_main_panels.py). It is counted by streaming the file,
- Line 1137, unix : code/modules/manufacturer_linkage_coverage.py (which gen_07 writes to
- Line 1138, unix : output/tables/manufacturer_linkage_coverage.csv). The 70 rows of
- Line 1142, windows : print("\n[MAUDE] adverse-event universe (manuscript: ~9.2 million reports; the top 300\n"
- Line 1163, unix : # numbers (code/modules/manufacturer_linkage_coverage.py).
- Line 1167, unix : # it as one made the strict gate fail on the analysis-only real route although 118/118 numbers
- Line 1306, unix : two years (base 11.9 entrants/yr), versus a statistically insignificant 13.7%
- Line 1308, unix : adds about five new firms per year relative to pre-event means; the 1996/8 events
- Line 1310, unix : 1996/8 comparison is the matched-control new-entry event study's two-year
- Line 1334, unix : # 1996/8 comparison: the same two-year horizon on the matched-control new-entry
- Line 1525, unix : output/tables/Formatted/PaperRegTableSafety_IItoI_NoLog.tex (written by
- Line 1678, unix : derived_headline_innovation()    # headline innovation magnitudes (L210/L387)
- Line 1679, unix : derived_headline_market_price()  # headline market-composition + price magnitudes (L212/L406)
- Line 1680, unix : derived_invention_year_validation()  # GPT-vs-hand invention-year r=0.76 (L500/L1795/L2508)
- Line 1696, unix : derived_new_entry_2015()             # 11.9 base, ~5 firms/yr, 39%; 1996/8 comparison
- Line 1706, unix : # JPE 2.2: program-generate the appendix computational tables (D.15/D.11/D.1) from these same
- Line 1797, windows : print("Done. The full crosswalk of every in-text number to its producing program\n"
- Line 1801, unix : # FAIL-CLOSED (certification): in-text magnitudes and/or appendix tables not fully regenerated.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/fromraw_contract.py**

- Line 28, unix : # 510(k) + PMA submission compilation: gen_01 phase 2 writes it, gen_03/gen_03b read it.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/materialize_simulation.py**

- Line 7, unix : acquisition-level simulated inputs, verifies that transformation outputs/caches
- Line 11, unix : python3 synthetic_pipeline/preflight_from_raw.py
- Line 16, unix : to data/raw) so 06b/06c run on synthetic text. Steps 16/17 regenerate the safety estimate CSVs and
- Line 28, unix : synthetic_pipeline/generators/gen_00g_deidentify_patents.py),
- Line 56, unix : # Patent-subtree members whose reader resolves them under data/raw/ even though their basename
- Line 57, unix : # matches one of the data/derived/ prefixes below. Applicant_Cites_Only.csv is read by
- Line 59, unix : # (and is listed under data/raw/ in RESTRICTED_FILE_INVENTORY.csv), so the generic
- Line 63, unix : # MAUDE-linkage members that do NOT live under data/raw/MAUDE/. The synthetic twin of the
- Line 65, unix : # data/raw/manual_permno_corrections.csv (and by gen_07's REAL branch at the same path), so the
- Line 84, unix : # data/raw/ with no existence guard, so they must land in raw for the simulated-data route.
- Line 115, unix : # code/00_generate_data/gen_00b_marketscan_extraction.py, run at NBER).
- Line 129, unix : map: the certification harness reads certification/MATERIALIZE_DESTINATIONS.tsv (each destination
- Line 247, unix : # remove trained LDA/word2vec models so 11a retrains on the simulated text
- Line 291, windows : epilog=("Simulated-data route:\n"
- Line 292, windows : "  python3 synthetic_pipeline/materialize_simulation.py --for-gen-run\n"
- Line 293, windows : "  python3 synthetic_pipeline/preflight_from_raw.py\n"
- Line 295, windows : "      --regenerate-safety-keywords --regenerate-safety-embeddings\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11e_new_entry_2015.py**

- Line 1, unix : #!/usr/bin/env python
- Line 11, unix : data/derived/Full_sample.csv
- Line 12, unix : data/derived/later_treated_2_1_oct22_24.csv
- Line 13, unix : data/raw/501k_all.csv
- Line 14, unix : r_scripts/did_ES.R
- Line 17, unix : output/figures/NewFirmsPatenting_2017.png
- Line 18, unix : output/tables/new_entry_2015_event_study.csv   (in-text: 2015 new-entry effects)
- Line 19, unix : output/tables/new_entry_2015_in_text.csv       (in-text: base 11.9, ~5 firms/yr, ~39%)
- Line 124, unix : output/tables/new_entry_2015_event_study.csv -- the per-year effects and
- Line 126, unix : output/tables/new_entry_2015_in_text.csv -- the derived magnitudes:
- Line 128, unix : event year's pre-period year (manuscript: base 11.9 entrants/yr)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py**

- Line 20, windows : pat = re.compile(r"sk-[A-Za-z0-9_\-]{20,}")
- Line 23, unix : # ---- the deposited prompt, verbatim from code/12b_gpt_price_links_generation.py ----
- Line 28, windows : return ("Device candidate:\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/03b_estimation_2to1.py**

- Line 1, unix : #!/usr/bin/env python
- Line 9, unix : data/derived/ (matched samples, parquet files, spillovers)
- Line 11, unix : output/tables/ (estimate CSVs for Tables 2-4, II→I columns)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06b_validate_safety.py**

- Line 1, unix : #!/usr/bin/env python
- Line 7, unix : FROM DATA. It is memory/compute heavy, so run_all treats its outputs as
- Line 16, unix : output/tables/safety_refined_keywords_estimates.csv) are the frozen ones the
- Line 30, unix : data/raw/FDA_patents_text.csv          (patent title+abstract text)
- Line 31, unix : data/derived/safety_vars_allpats.csv   (baseline safety flags from 06a)
- Line 32, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 33, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 34, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 35, unix : data/derived/Adverse_fsize_ready_all4_oct22_24.csv
- Line 38, unix : data/derived/safety_vars_allpats_v2.csv           (keyword-only flags)
- Line 39, unix : data/derived/safety_vars_allpats_updated_v2.csv   (refined keyword flags)
- Line 40, unix : data/derived/word2vec_patent_corpus.model          (trained Word2Vec model)
- Line 41, unix : output/tables/safety_refined_keywords_estimates.csv  (incl. the n_obs column
- Line 43, unix : output/tables/safety_term_share.csv   (in-text: the ~2% safety-term share)
- Line 89, windows : text = re.sub(r"[^\w\s]", " ", text)
- Line 370, unix : the safety terms, to output/tables/safety_term_share.csv.
- Line 374, unix : per-patent flags ship (data/derived/safety_vars_allpats_v2.csv, written above
- Line 452, unix : # Read as text so the existing estimate/CI/baseline cells are written back
- Line 682, unix : # Table D.12 (safety robustness) is formatted by code/10b_format_remaining_tables.py, which runs
- Line 685, unix : # output/tables/Formatted/TableD12_SafetyRobustness.tex is 10b_format_remaining_tables.py.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py**

- Line 44, unix : Outputs produced (now bundled in data/raw/):
- Line 49, unix : - code/00_generate_data/gen_02_price_matching.py (whose docstring notes the
- Line 52, unix : - code/05_price_analysis.py (manual HCPCS corrections at lines 854-899)
- Line 98, unix : You are an expert on FDA medical devices and outpatient HCPCS/CPT procedures.
- Line 100, unix : TASK: Given a specific device description (or FDA product code), return the single best outpatient procedure mapping IF AND ONLY IF the device is a nontrivial driver of the outpatient episode (e.g., the core implant/kit that defines the surgery, or the assay/test system in a lab test), not a trivial supply. If no suitable outpatient procedure exists—or the device is only a trivial component—return a structured 'no_link' result.
- Line 105, unix : - LINK if the device/implant/test system is the defining component or drives a nontrivial share of payment (e.g., IOL in cataract surgery; a specific in vitro diagnostic assay kit; an ambulatory infusion pump).
- Line 106, unix : - NO LINK if the item is a generic tool/consumable, if mapping is diffuse (many-to-many across unrelated procedures), or if the code is primarily an evaluation/visit/collection/handling/service code.
- Line 114, unix : 5) Lab/test linking guardrails:
- Line 122, unix : 8) Sources: Provide ≥1 high-quality source (FDA Product Classification page, CMS/AMA descriptor, relevant specialty society guidance, or manufacturer IFU/clinical overview). If a reliable source can’t be identified, respond with no_link.
- Line 127, unix : - Reject mappings that rely solely on visit/collection/handling/service or unlisted codes (rule 6).
- Line 192, unix : - Regulation: 862.1215; Creatine phosphokinase/creatine kinase or isoenzymes test system.
- Line 261, unix : # verified a more accurate HCPCS/CPT than the model returned. Same set the
- Line 313, windows : "Device candidate:\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_contact_lens_case_study.py**

- Line 1, unix : #!/usr/bin/env python
- Line 12, unix : data/derived/Full_sample.csv
- Line 15, unix : output/figures/ContactLens_CaseStudy.png
- Line 136, windows : "Reclassification\n(1994)",
- Line 177, windows : "Reclassification\n(1994)",
- Line 187, unix : # ── Additive emitter: write the intro case-study pre/post ratios ──

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/plotting.py**

- Line 8, unix : Outputs: Formatted figures saved to output/figures/
- Line 107, unix : add_trend_lines: whether to fit pre/post linear trends

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py**

- Line 2, unix : audit_simulated_data.py -- FAIL-CLOSED certification that synthetic_pipeline/simulated_data/
- Line 60, unix : # patent files, KPST/KPSS) are GENERATED as views over a fresh synthetic
- Line 61, unix : # firm/patent universe drawn from committed public parameters -- their rows do NOT correspond to real
- Line 73, unix : # above every real permno/gvkey). Verified by DOMAIN, not a row-equality threshold.
- Line 78, unix : # join keys (Explore code-map: firm linking is entirely via permno/LPERMNO), so a synthetic RELABEL
- Line 80, unix : # firm/inventor) would survive. permno/LPERMNO/gvkey/id/patnum are the allowlisted merge-key
- Line 102, unix : # PUBLIC = genuinely public code/label/design columns that may equal real BY DESIGN. Kept
- Line 103, unix : # DELIBERATELY narrow: FDA product codes + descriptors, public reclassification design, CPT/HCPCS
- Line 107, unix : # Nexis Class/Preempted flags) are NOT here -- they are TESTED against real so a future
- Line 116, unix : # F1/F3 rebuild: the former re-identifying tuple columns (cpc/jurisdiction/type/dates/datadate/
- Line 119, unix : # re-identification risk is STRUCTURAL (the (year,type,cpc,jur) SET/tuple, the MarketScan skeleton,
- Line 167, unix : # (certification/GENERATION_LINEAGE.csv, column materialized_destination). That is the authoritative
- Line 170, unix : # data/raw/ rather than the family's usual folder.)
- Line 300, unix : # EXPLICIT constant handling (no blanket exemption): a numeric constant (0/1/a count)
- Line 313, unix : # restricted-value column: fully compare to real (must not be a verbatim/shuffled copy) ---
- Line 331, unix : # A column whose REAL vocabulary is a handful of symbols (0/1 flags, Yes/No, a code set) is a
- Line 335, unix : # (Confidential run 2026-09-28: 0/1 flags stored as strings tripped the zero-overlap rule.)
- Line 377, unix : return                                       # not patent-level: rows/code = panel skeleton
- Line 502, unix : # No minimum-row threshold (fail-closed): if EVERY master-null/panel-value row equals
- Line 521, unix : Merge keys (permno/LPERMNO/gvkey/id/patnum) are intentionally NOT checked here -- they keep a
- Line 522, unix : consistent map by design (the runtime `.isin` firm/device gates need it); that residual is a
- Line 587, unix : continue                              # trivial masks (all/near present or absent) can coincide
- Line 633, unix : firms/patents lack a value) equals NONE of these, so this exemption is NON-VACUOUS: it fires only
- Line 656, unix : # (3) pre-/post-event structure from public year + public reclassification years.
- Line 673, unix : #     (patent_sum_2_1/3_2 are NaN precisely where no at-or-earlier PC row is a pre-event row; this
- Line 674, unix : #     reconstructs that mask from PUBLIC year/reclass/PC + row order -- see gen_00d._rederive_full_sample).
- Line 747, unix : count. These are STRONG indicators -- a smoothed/independent draw essentially never reproduces a
- Line 748, unix : real multiset or a non-rounded size, so the old resample_identity/redraw_missingness outputs trip
- Line 749, unix : them and the rounded/smoothed independent-universe outputs pass.
- Line 797, unix : #     draw from the committed rounded rate. (i) exempts control/pre-event/never-reclassified/
- Line 798, unix : #     public-column/patent-sum-ffill structure. (ii) exempts a coincidental genuine draw whose
- Line 800, unix : #     committed rate would NOT predict (a preserved/injected exact count with a mismatched rate)
- Line 802, unix : #     is unavailable, it falls back to round(real_nan/real_n, 3) = gen_00a's committed definition.
- Line 860, windows : fh.write("file,column,kind,status\n")
- Line 910, unix : # PUBLIC allowlist from any value check -- so a restricted value under a RENAMED/new column, a value
- Line 911, unix : # RELOCATED to a different column, or a REVERSED/TRUNCATED numeric copy all evade. This backstop is
- Line 913, unix : # (company/assignee/inventor/name/title/legal-text strings + high-entropy numeric IDs, EXCLUDING the
- Line 917, unix : # Genuinely-PUBLIC value columns: real values here MAY appear in synthetic (public taxonomies/codes,
- Line 920, unix : # uniqueness/linkage attack suite, not a value-leak matter).
- Line 926, unix : # F1/F3 rebuild: cpc/jurisdiction/patent_type/dates/datadate/fyear/filing_status etc. are NO
- Line 1023, unix : # false positives come from continuous VALUE columns (pay/netpay/coins/financials, stored as
- Line 1067, unix : # ROOT/PARENT-SYMLINK guard: os.walk(followlinks=False) still traverses when SIM itself is a
- Line 1116, unix : # e.g. data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv, which is public MAUDE-derived but is
- Line 1160, unix : # /external/restricted.csv -- would be dereferenced by the builder's copy and ship external
- Line 1198, unix : # (name-independent) so a renamed/relocated/reversed/truncated restricted value cannot evade.
- Line 1286, unix : audit_exact_statistics(sim_df, real_df, rel, findings)   # §6: no EXACT distinct/multiset/NaN/rows
- Line 1288, unix : # or 'public', so a renamed/relocated/reversed restricted value cannot slip through).
- Line 1298, unix : # its own pass/fail, so a structural failure is visible in the file rather than only in exit(1).
- Line 1355, unix : # written, the audit must NOT report success -- refuse to exit 0 with a missing/stale report.
- Line 1378, windows : f"{_ns} not-shipped member(s)) whose real\n"
- Line 1379, windows : f"  counterpart is a reviewed RESTRICTED input absent from this clean-room source by\n"
- Line 1380, windows : f"  construction. Their real-vs-synthetic comparison is MANDATORY in\n"
- Line 1381, windows : f"  the author's confidential certification run (real data bound read-only, this script hash-bound\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD1_SampleConstruction.tex**

- Line 17, unix : & 29 & 94 & n/a & n/a \\
- Line 19, unix : & 12 & 39 & n/a & n/a \\
- Line 31, unix : & 12 & 100 & n/a & n/a \\
- Line 49, unix : \textsuperscript{e}Uses firm assets from CRSP/Compustat and is the only specification restricted to publicly listed firms.}

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py**

- Line 1, unix : #!/usr/bin/env python3.9
- Line 7, unix : code/10c_generate_appendix_tables.py into output/tables/Formatted/ and pulled into the manuscript
- Line 20, unix : Table D.1 (treated-sample construction/coverage) IS program-generated:
- Line 21, unix : code/10c_generate_appendix_tables.py writes output/tables/Formatted/TableD1_SampleConstruction.tex,
- Line 24, unix : and its price/utilization coverage cells are read from output/tables/d1_price_coverage.csv; the
- Line 28, unix : code/15_intext_derived_numbers.derived_sample_construction_counts().
- Line 73, unix : # hospitalization Value/Total/CI and VSL cells. Kept in sync with the generator by construction; a
- Line 114, unix : # Confidence-interval bounds, checked so a generator/source drift is caught at the
- Line 119, unix : # The hospitalization Value/Total/CI cells and the VSL are COMPUTED (Value = per-unit
- Line 141, unix : its upstream RegTable_Utilization/DIDimpute_RegTable_Utilization source is missing) cannot
- Line 203, unix : Rationale: code/10c_generate_appendix_tables.py's _extract_method_row() falls back to exactly

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_04_parquets.py**

- Line 9, unix : data/derived/Full_sample.csv
- Line 10, unix : data/derived/later_treated_2_1_oct22_24.csv
- Line 11, unix : data/derived/intuitive_2_1_oct22_24.csv
- Line 12, unix : data/derived/spillovers_2_1_oct22_24.csv
- Line 15, unix : data/derived/data_2_1_full.parquet
- Line 16, unix : data/derived/data_2_1_latertreat.parquet
- Line 17, unix : data/derived/data_2_1_intuitive.parquet
- Line 18, unix : data/derived/data_2_1_spillovers.parquet

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/regen_determinism/verify_simulated_data_manifest.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 3, unix : (`certification/regen_determinism/simulated_data_sha256.txt`).
- Line 9, unix : - every `.csv` / `.parquet` / `.xlsx` under `synthetic_pipeline/simulated_data/` is present
- Line 16, unix : python3 certification/regen_determinism/verify_simulated_data_manifest.py
- Line 26, unix : # package root = two levels up from certification/regen_determinism/
- Line 37, unix : Shipped alongside the manifest so an empty/shrunk/inflated simulation fails against a FIXED
- Line 100, unix : # ROOT/PARENT-SYMLINK guard: os.walk(followlinks=False) still traverses when the START dir is
- Line 151, unix : # so a shrunk/empty/inflated simulation fails against a canonical expectation.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_simulation_schema_contract.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 9, unix : simulator and must pass the rights/privacy review before publication.
- Line 78, unix : # generated by gen_00c on its own synthetic HCPCS/PRODUCTCODE construction and does NOT consume

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/analyze_correlation.py**

- Line 1, unix : #!/usr/bin/env python3

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/build_simulation.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 4, unix : Regenerates the entire publishable `synthetic_pipeline/simulated_data/` tree from the shipped,
- Line 5, unix : reviewed committed parameters -- WITHOUT reading any real/restricted data. This is the
- Line 11, unix : synthetic_pipeline/_synthetic_source_internal/simulation_parameters.json  (rounded/smoothed params;
- Line 13, unix : synthetic_pipeline/_synthetic_source_internal/pc_effects.parquet          (theta: synthetic random
- Line 15, unix : synthetic_pipeline/_synthetic_source_internal/public_master_skeleton.parquet (Full_sample PUBLIC cols)
- Line 21, unix : gen_00e  synthetic patents (fresh patnum/permno/PC, KPSS values)
- Line 26, unix : gen_00h  synthetic patent title/abstract text
- Line 34, unix : PYTHONHASHSEED=0 python3 synthetic_pipeline/build_simulation.py --output-dir /path/outside/pkg
- Line 36, unix : python3 synthetic_pipeline/materialize_simulation.py --source-dir /path/outside/pkg --for-gen-run
- Line 37, unix : # The official analysis route is certification/certify_fromraw_route.sh.
- Line 54, unix : # generators/independent_universe.py turns it into one numpy Generator per (file, column) tag
- Line 60, unix : # Optional public perturbation control (generators/synthetic_seed.py). Leave unset for the
- Line 88, windows : sys.stderr.write("build_simulation: FATAL: %s\n" % msg)
- Line 170, windows : "  You gave: %s\n"
- Line 171, windows : "  Use, for example:\n"
- Line 173, windows : "--output-dir /path/outside/the/package\n"
- Line 174, windows : "  and then consume it with:\n"
- Line 205, unix : g00a.disclosure_review(params)          # raises SystemExit on any un-rounded/raw statistic

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_payload_contract.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 30, unix : Run from the package root:  python3 certification/validate_payload_contract.py
- Line 41, unix : # Reuse the contract generator's kind/reader so the validator's inference matches how the contract
- Line 53, unix : kind -- JPE's confidential.html column-type-fidelity requirement (values stay fake; type/format
- Line 57, unix : other kind change -- including a committed date/number/integer column shipping as a bare string,

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_03_lbd.py**

- Line 34, unix : data/derived/Applicant_Device_data.csv                 (compiled 510k+PMA submissions)
- Line 35, unix : data/derived/AD_data_applicant_df_oct22_24.csv         (device-level clusters)
- Line 36, unix : data/derived/AD_data_applicant_df2_oct22_24.csv        (applicant-level clusters)
- Line 37, unix : data/raw/501k_all.csv                                  (FDA 510(k) submissions)
- Line 38, unix : data/raw/all_pma_approvals.txt                         (FDA PMA approvals)
- Line 41, unix : data/derived/LBD_ApprovalTime_Both_oct22_24.csv

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00f_synthetic_nexis.py**

- Line 15, unix : confidential-data-not-for-publication/synthetic_nexis/. Deterministic (seeded).
- Line 27, unix : # pandas/openpyxl embed the current wall-clock time in docProps/core.xml (created/modified) and in
- Line 62, unix : # certification/validate_payload_contract.py uses to cross-check the shipped payload against
- Line 76, unix : # column/type/format schemas are committed structural metadata, pending the Data Editor's written
- Line 108, unix : # Class/Device/Preempted ship as a STRING-kind column in some Nexis files (real cells were
- Line 113, unix : # pd.read_csv (the same reader the contract/validator use) infers int64 right back -- use a
- Line 114, unix : # non-numeric-parseable token (Yes/No) so the column is unambiguously string on read-back.
- Line 132, unix : # date_bounds=(lo, hi); this branch is the fallback for a date-kind/date-named column with too
- Line 153, unix : contract's column_kinds) to actually carry that STRUCTURAL kind -- integer/number/date/
- Line 154, unix : string, per `_contract_kind()` (== certification/generate_simulation_schema_contract.py's
- Line 155, unix : `_kind()`, the same classifier certification/validate_payload_contract.py cross-checks the
- Line 213, unix : # Same-stem xlsx/csv pairs use the same seed and therefore the same values.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/06c_validate_safety_embed.py**

- Line 1, unix : #!/usr/bin/env python
- Line 26, unix : data/raw/FDA_patents_text.csv            (patent title+abstract text)
- Line 27, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 28, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 29, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 30, unix : data/derived/Adverse_fsize_ready_all4_oct22_24.csv
- Line 33, unix : data/derived/safety_tagged_patents.csv
- Line 34, unix : output/tables/safety_embedding_distance_estimates.csv
- Line 35, unix : output/tables/safety_embedding_percentile_robustness.csv
- Line 38, unix : output/tables/safety_embedding_percentile_used.txt
- Line 87, windows : text = re.sub(r"[^\w\s]", " ", text)
- Line 120, unix : # output/tables/safety_embedding_percentile_used.txt and into every row of
- Line 121, unix : # output/tables/safety_embedding_percentile_robustness.csv, so no estimate can be silent about
- Line 150, unix : (`models/all-MiniLM-L6-v2/`, Apache-2.0, redistributable) so a clean-room reviewer needs no
- Line 613, unix : output/tables/safety_embedding_percentile_used.txt, a single
- Line 631, unix : output/tables/safety_embedding_percentile_robustness.csv.
- Line 633, unix : Reads data/derived/safety_tagged_patents.csv (id, safety_similarity,
- Line 640, unix : python3 code/06c_validate_safety_embed.py --percentile-robustness-only

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/docker/entrypoint.sh**

- Line 1, unix : #!/usr/bin/env bash
- Line 42, unix : if [ -e data/raw/MAUDE ] && [ ! -e data/raw/MAUDE/. ]; then

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py**

- Line 5, windows : KEY=re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py**

- Line 1, unix : #!/usr/bin/env python
- Line 13, unix : data/raw/new_patent_analysis/all_device_patents_w_pc.csv
- Line 14, unix : data/derived/all_patents_w_xi_oct22_24.csv
- Line 15, unix : data/derived/matched_sample_3_2_onepat_innovation.csv
- Line 16, unix : data/derived/matched_sample_2_1_onepat_innovation.csv
- Line 19, unix : output/figures/variety_3_2.png
- Line 20, unix : output/figures/variety_2_1.png
- Line 25, unix : synthetic-data run, where synthetic_pipeline/materialize_simulation.py deletes the models
- Line 26, unix : on purpose -- the pipeline cleans the text, trains the bigram/trigram phrasers
- Line 33, unix : certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv before any step runs and,
- Line 71, unix : # line above: the five Conley-Taber calls in 11a/11d pass no `seed=` of their own, unlike
- Line 153, unix : Full LDA pipeline: clean text, train bigram/trigram, optimize topics,
- Line 163, unix : frequency_df (topic-level pre/post change stats),
- Line 240, unix : # (certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv) and the branch above loads them, so
- Line 242, unix : # certification/EXPECTED_EXHIBIT_HASHES.csv. A forced refit at this count selects 15 in
- Line 265, unix : # Frequency before/after reclassification
- Line 318, unix : 3) Build stacked treated/control panel.
- Line 514, unix : # Synthetic-route robustness: a topic can end up without a text label (NaN/float) when its LDA
- Line 516, unix : # y-axis in barplot/errorbar) rejects non-str values with a TypeError, aborting the exhibit. Coerce

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/generate_data_dictionary.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 10, unix : what the leakage/structure audit enforces.
- Line 12, unix : Output: certification/DATA_DICTIONARY.csv with JPE 1.5 per-column metadata:
- Line 15, unix : Stats are computed over the FULL column (not a sample) so ranges/allowed values are exact.
- Line 19, unix : the reviewed payload inventory in certification/regen_determinism/simulated_data_expected_files.txt,
- Line 126, unix : # rewrites certification/DATA_DICTIONARY.csv (the generator reads the whole simulated payload).
- Line 143, unix : df = _read_full(p)                              # FULL column stats (exact ranges/allowed values)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/table_format.py**

- Line 5, unix : row/panel assembly for booktabs-style tables.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py**

- Line 6, windows : KEY = re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py**

- Line 8, unix : verification is provider-/enclave-run). The three other restricted sources
- Line 9, unix : (Dimensions, WRDS/CRSP-Compustat, Nexis) have confidential temporary-access routes,
- Line 16, unix : end-to-end and produces price/utilization exhibits of the correct shape (with synthetic
- Line 30, unix : Writes into  confidential-data-not-for-publication/synthetic_marketscan/ :
- Line 34, unix : data/derived/ (in a throwaway working copy). See the confidential-data README.
- Line 38, unix : python3 code/00_generate_data/gen_00c_synthetic_marketscan.py
- Line 54, unix : import gen_00b_pc_effects as pcmod   # shared PC-level design/theta (PUBLIC product-code universe)
- Line 57, unix : # certification/validate_payload_contract.py uses to cross-check the shipped payload against
- Line 71, unix : # them to data/raw/ (OVERRIDING the real crosswalk) on the simulated routes (like the synthetic KPST/KPSS).
- Line 81, unix : # public data/raw/FDA_HCPCS_Xwalk_Moazzam.csv on the synthetic routes only. The real file is public
- Line 105, unix : #     (data/raw/FDA_HCPCS_Xwalk_Moazzam.csv), and the disclosure audit flagged the overlap.
- Line 114, unix : #     synthetic_pipeline/audit_simulated_data.py, which is run before the package is built.
- Line 117, unix : #     05_price_analysis.py (85002/84155/80197/83010/52352/52336), and keeps the shipped proc1 column
- Line 124, unix : #         data/raw/2_1_GPT_Price_Links.csv data/raw/3_2_GPT_Price_Links.csv
- Line 190, unix : Why this exists (price 'Matched' panel): the shipped 2_1/3_2_GPT_Price_Links.csv are a FROZEN real
- Line 194, unix : universe, so its treated/control codes no longer coincide with that frozen crosswalk. The price
- Line 206, unix : so whatever treated/control codes the synthetic matching selects have price data and both price
- Line 209, unix : simulated_data/synthetic_price_links/ and materialize routes it to data/raw/ (overriding the real
- Line 211, unix : 05_price's crosswalk stay HCPCS-consistent for the derived inputs too. gen_00c never writes data/raw, so
- Line 275, unix : `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv` is PUBLIC and ships, so it is not restricted --
- Line 276, unix : but it carries REAL HCPCS/CPT codes, while the simulated MarketScan claims live entirely
- Line 299, unix : over data/raw/FDA_HCPCS_Xwalk_Moazzam.csv on the simulated route only, so the restricted-data
- Line 391, unix : contract's column_kinds) to actually carry that STRUCTURAL kind -- integer/number/date/
- Line 392, unix : string, per `_contract_kind()` (== certification/generate_simulation_schema_contract.py's
- Line 393, unix : `_kind()`, the same classifier certification/validate_payload_contract.py cross-checks the
- Line 485, unix : No file under ``data/raw`` or ``data/derived`` is read. The contract contains only
- Line 585, unix : # skeleton/sentinels), over the PUBLIC product-code universe from theta (loaded above).

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11f_reg_background.py**

- Line 1, unix : #!/usr/bin/env python
- Line 9, unix : data/derived/matched_sample_2_1_onepat.csv
- Line 10, unix : data/derived/matched_sample_3_2_onepat.csv
- Line 13, unix : output/figures/Distribution_of_2_1_over_years.png
- Line 14, unix : output/figures/Distribution_of_3_2_over_years.png

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/build_manuscript.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 20, unix : for editing/version control; only the build copy is spliced.
- Line 46, unix : #   - deposit tree: paper/../replication_package/output  is absent, but paper/../output holds the
- Line 48, unix : #                   ../replication_package/output/ prefix, so rewrite it to ../output/ in the build
- Line 141, unix : #   (3) require the resulting PDF to be FRESHLY created (mtime at/after this run's start) and
- Line 148, unix : # (all expected before bibtex/later passes resolve them), and a bibtex pass with a
- Line 191, unix : # under a unique name rather than the fixed path /tmp/_bm.log: /tmp is not writable (or not
- Line 201, unix : # by later passes). Because ALL passes' logs are retained (to catch bibtex/earlier errors),
- Line 215, unix : # Require a FRESHLY-created, non-empty PDF -- not a pre-existing/stale one (see the gate note above).
- Line 217, unix : # file; the size/mtime checks are belt-and-suspenders against a tool that leaves behind a

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/hash_manuscript_closure.py**

- Line 1, unix : #!/usr/bin/env python3
- Line 8, unix : existing file) -- a missing/extra target fails the freeze. Emits a stable MANUSCRIPT_CLOSURE.sha256
- Line 16, unix : code/audit_pipeline.py and fails the freeze if the two scanners disagree on the set of figure
- Line 20, unix : Usage:  python3 certification/hash_manuscript_closure.py [--tex paper/JPE_submission_v8.tex] [--root .]
- Line 29, unix : # \includegraphics (code/audit_pipeline.py collects both).
- Line 103, unix : ap.add_argument('--tex', default='paper/JPE_submission_v8.tex')
- Line 105, unix : ap.add_argument('--out', default='certification/MANUSCRIPT_CLOSURE.sha256')

