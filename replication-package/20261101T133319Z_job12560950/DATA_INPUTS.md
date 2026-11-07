# Replication Package: External Data Inputs

**Supporting reference; `README.md` governs.** `README.md` is the single documentation point for this
package; this file is the per-file input inventory behind its data-source sections, and
`data_input_manifest.csv` is the same inventory as a table.

Every file below is required by at least one replication script but is **not produced by any other replication script**. Intermediate files (e.g., matched samples from `02_match_samples.py`, safety DID CSVs from `06a`) are excluded.

Each file carries one of two labels:
- **`[GENERATE]`** — built by one of the data generation scripts (see the source column)
- **`[PROVIDE]`** — supplied from outside the pipeline: proprietary, downloaded, manually created, or hand-coded

---

## I. Derived Data (`data/derived/`)

These are processed/merged datasets that feed into the analysis scripts.

| # | File | Source | Used By | Label |
|---|------|--------|---------|-------|
| 1 | `Full_sample.csv` | Master panel: product codes x years with all outcomes and treatment indicators | 02, 03a, 09, 11b, 11d, 11e | `[GENERATE]` |
| 2 | `all_patents_w_xi_oct22_24.csv` | Patent-level data with KPSS market valuations (xi), real 2019$ | 06a-c, 07, 09, 11a, 13, 14 | `[GENERATE]` |
| 3 | `safety_vars_allpats.csv` | Patent-level safety keyword binary indicators | 06a-c, 07 | `[GENERATE]` |
| 5 | `constrained_adv_event_new_sept25.csv` | Adverse event panel (II->I) with constrained matching | 04 | `[GENERATE]` |
| 6 | `constrained_adv_event_new_sept25_3_2.csv` | Adverse event panel (III->II) with constrained matching | 04 | `[GENERATE]` |
| 7 | `RegNum_Factorized_Synth.csv` | Author-built regulation-number crosswalk: FDA classification attributes, reclassification/de-novo metadata, Federal Register change history, top-3 CPC codes and their scheme titles. Byte-identical copy in `data/raw/`; provenance in `certification/PUBLIC_SOURCE_PROVENANCE.csv` | 09, 10c, 11b, 11d | `[PROVIDE]` |
| 8 | `intuitive_2_1_oct22_24.csv` | Intuitive sample panel for II->I | 03b | `[GENERATE]` |
| 9 | `later_treated_2_1_oct22_24.csv` | Later-treated control group for II->I | 03b, 11b, 11e | `[GENERATE]` |
| 10 | `intuitive_3_2_oct22_24_similarity.csv` | Intuitive sample panel for III->II with similarity scores | 03a | `[GENERATE]` |
| 11 | `later_treated_3_2_oct22_24.csv` | Later-treated control group for III->II | 03a | `[GENERATE]` |
| 12 | `intuitive_spillovers_3_2_oct22_24.csv` | Spillover sample for III->II intuitive reclassifications | 03a | `[GENERATE]` |
| 13 | `spillovers_2_1_oct22_24.csv` | Spillover sample for II->I | 03b | `[GENERATE]` |
| 14 | `LBD_ApprovalTime_Both_oct22_24.csv` | Learning-by-doing approval time panel (both reclass types) | 08, 09 | `[GENERATE]` |
| 15 | `data_2_1_full.parquet` | Pre-built full sample for II->I estimation | 03b | `[GENERATE]` |
| 16 | `data_2_1_latertreat.parquet` | Pre-built later-treated sample for II->I | 03b | `[GENERATE]` |
| 17 | `data_2_1_intuitive.parquet` | Pre-built intuitive sample for II->I | 03b | `[GENERATE]` |
| 18 | `data_2_1_spillovers.parquet` | Pre-built spillover sample for II->I | 03b | `[GENERATE]` |
| 19 | `Adverse_fsize_ready_all4_oct22_24.csv` | Adverse events merged with firm size (all 4 event types) | 06a-c, 07 | `[GENERATE]` |
| 20 | `adverse_event_panel_by_PC_full.csv` | Full adverse event panel by product code (summary stats) | 09 | `[GENERATE]` |
| 21 | `Adv_Event_2020_2022.csv` | Adverse event data for 2020-2022 (post-sample extension) | 11b | `[GENERATE]` |
| 22 | `outpatient_combined_censored.csv` | **PROPRIETARY** MarketScan outpatient claims, aggregated at NBER by `code/00_generate_data/gen_00b_marketscan_extraction.py` | 02 (gen_02), 05, 09 | `[PROVIDE]` |

## II. Raw Data (`data/raw/`)

These are externally sourced datasets used directly by analysis scripts.

| # | File | Source | Used By | Label |
|---|------|--------|---------|-------|
| 24 | `501k_all.csv` | FDA 510(k) premarket notification submissions | 09, 11e, **gen** | `[PROVIDE]` |
| 25 | `all_pma_approvals.txt` | FDA PMA (premarket approval) records | 09, **gen** | `[PROVIDE]` |
| 26 | `unique_devices_thr_75.csv` | Unique device types (product codes) with fuzzy dedup | 09 | `[GENERATE]` |
| 27 | `unique_firms_in_PC_thr_75.csv` | Unique firms per product code with fuzzy dedup | 09 | `[GENERATE]` |
| 28 | `unique_firms_thr_75.csv` | Unique firms across device types with fuzzy dedup | 09 | `[GENERATE]` |
| 29 | `KPSS_2019_public.csv` | Kogan-Papanikolaou-Seru-Stoffman patent valuations (public) | 09, **gen** | `[PROVIDE]` |
| 30 | `compustat_firm_data.csv` | Compustat firm-level total assets | 09, **gen** | `[PROVIDE]` |
| 31 | `Applicant_Cites_Only.csv` | Forward citation counts per patent (`USID`, `PRODUCTCODE`, `times_cited`); simulated counterpart at `synthetic_pipeline/simulated_data/synthetic_patents/Applicant_Cites_Only.csv` | 09 | `[PROVIDE]` |
| 32 | `Class2_Exemptions_2017_Grennan.csv` | FDA Class II 510(k) exemptions (2017 deregulation) | 11b | `[PROVIDE]` |
| 33 | `device-recall-0001-of-0001-2.json` | FDA device recall database | 11b | `[PROVIDE]` |
| 34 | `KPST_Breakthrough.csv` | KPSS breakthrough patent classification | 14 | `[PROVIDE]` |
| 35 | `new_patent_analysis/all_device_patents_w_pc.csv` | Device patents matched to FDA product codes | 11a, 13 | `[PROVIDE]` |
| 36 | `FDA_patents_text.csv` | Patent title/abstract text for safety validation | 06b, 06c, **gen** | `[PROVIDE]` |
| 37 | `innovation_year_2_1_FDA_project.csv` | GPT-4o invention years for II->I PCs (293 PCs) | 11d | `[PROVIDE]` |
| 38 | `innovation_year_3_2_FDA_project.csv` | GPT-4o invention years for III->II PCs (25 PCs) | 11d | `[PROVIDE]` |
| 39 | `innovation_year_all_other_FDA_project.csv` | GPT-4o invention years for non-reclassified PCs | 11d | `[PROVIDE]` |
| 40 | `innovation_year_FDA_project.csv` | GPT-4o invention years for III->II PCs, original 25-row output; the only invention-year file that preserves the exact query and the raw model reply (`query`, `response` columns) alongside the hand-coded benchmark year | 12, 15 | `[PROVIDE]` |
| 41 | `2_1_GPT_Price_Links.csv` | **`gpt-5-mini`** linkage: II->I product codes to HCPCS/CPT codes | 05 | `[PROVIDE]` |
| 42 | `3_2_GPT_Price_Links.csv` | **`gpt-5-mini`** linkage: III->II product codes to HCPCS/CPT codes | 05 | `[PROVIDE]` |
| 43 | `spinal_entrant_audit.csv` | Author hand audit of 20 new spinal-implant entrants: the first-time 510(k) applicants under product code MAX, submissions from 2007 onward, with four attributes hand-coded by the author from public web searches (`US_based`, `subsidiary`, `acquired`, `founded`). Backs the regulatory-proficiency footnote; provenance in `certification/PUBLIC_SOURCE_PROVENANCE.csv`, variables in `CODEBOOK.md` | 15 | `[PROVIDE]` |

The four invention-year files (#37–40) come from OpenAI GPT-4o; the two price links (#41–42) come from
OpenAI `gpt-5-mini`. Model, sampling settings, prompts, what is archived and what is not are in
`CODEBOOK.md`, "API-derived fixed inputs", and in `README.md` under "API-derived fixed inputs".

## III. Litigation Data (`data/raw/Liability/`)

*These are Nexis Uni (LexisNexis) search exports; **each filename is the literal Nexis search query**. Search methodology + reproduction: `NEXIS_SEARCH_METHODOLOGY.md`. Excluded from the public package (restricted).*

| # | File | Used By | Label |
|---|------|---------|-------|
| 44 | `Results list for_medical device tort preempt.xlsx` | 11c | `[PROVIDE]` |
| 45 | `Results list for_medical device tort preempt 2006-2007.xlsx` | 11c | `[PROVIDE]` |
| 46 | `Results list for_medical device tort 1985-1995.xlsx` | 11c | `[PROVIDE]` |
| 47 | `Results list for_medical device tort 1996-2000.xlsx` | 11c | `[PROVIDE]` |
| 48 | `Results list for_medical device tort 2001-2004.xlsx` | 11c | `[PROVIDE]` |
| 49 | `Results list for_medical device tort 2005-2007.xlsx` | 11c | `[PROVIDE]` |
| 50 | `Results list for_pharmaceutical tort preempt 1985-1998.xlsx` | 11c | `[PROVIDE]` |
| 51 | `Results list for_pharmaceutical tort preempt 1999-2004.xlsx` | 11c | `[PROVIDE]` |
| 52 | `Results list for_pharmaceutical tort preempt 2005-2007.xlsx` | 11c | `[PROVIDE]` |
| 53 | `medtech/*.xlsx` (bankruptcy filings by year range) | 11c | `[PROVIDE]` |

## IV. Other Files

| # | File | Location | Description | Used By | Label |
|---|------|----------|-------------|---------|-------|
| 54 | `Data_new_latest.png` | `data/raw/` | Author-created chart image (1097x598 PNG), the source asset for Appendix Figure D.2; copied, not regenerated, by `11g`. Provenance in `certification/PUBLIC_SOURCE_PROVENANCE.csv` and `certification/FIGURE_PROVENANCE.md` | 11g | `[PROVIDE]` |
| 55 | `Deregulation_May31_23_Paper.png` | manual | Manually created Figure 2 (regulatory schematic; the contact-lens exhibit is Figure 1) | paper only | `[PROVIDE]` |

## V. R Scripts (`r_scripts/`)

| # | File | Description | Used By | Label |
|---|------|-------------|---------|-------|
| 56 | `preprocess.R` | R preprocessing for DID estimation | estimation module, 11b | `[PROVIDE]` |
| 57 | `did_imputation_topython.R` | BJS DID imputation estimator | estimation module, 11b | `[PROVIDE]` |
| 58 | `did_ES.R` | Event study DID estimation | 11e | `[PROVIDE]` |

---

## VI. Additional Inputs Required by the Data Generation Scripts

These files are **not read by any replication analysis script** but are read by the data-generation
scripts in `code/00_generate_data/` to produce the `[GENERATE]` files above. Paths are the package
paths a replicator uses; the generation scripts resolve them through `config.py`.

| # | File | Package path | Description | Label |
|---|------|--------------|-------------|-------|
| 59 | `RegNums_Final_w_CPC_Desc_sample.csv` | *(not shipped; not read)* | Device-registry entry declared in `config.py` that no shipped program reads; the package does not require it. | `[PROVIDE]` |
| 60 | `revise_for_rescrape_3_2_latest.csv` | `data/raw/pat_search_augment/` | III->II patent search augmentation terms | `[PROVIDE]` |
| 61 | `revise_for_rescrape.csv` | `data/raw/pat_search_augment/` | II->I patent search terms (no prior patents) | `[PROVIDE]` |
| 62 | `revise_for_rescrape_already_had_2_1.csv` | `data/raw/pat_search_augment/` | II->I patent search terms (had prior patents) | `[PROVIDE]` |
| 63 | `FDA_pats_original_firmname.csv` | `data/raw/` | Patent-to-firm-name mapping (from Dimensions; restricted, excluded) | `[PROVIDE]` |
| 64 | `all_pats_wtitlesCPC.csv` | `data/raw/` | Patent titles with CPC codes (from Dimensions; restricted, excluded) | `[PROVIDE]` |
| 65 | `PC_by_year_cites_ApplicantOnly.csv` | `data/raw/` | Citation counts by product code x year, applicant only (Dimensions; restricted, excluded) | `[PROVIDE]` |
| 66 | `PC_by_year_diff_ind_appl_only.csv` | `data/raw/` | Cross-industry citation counts by product code x year (Dimensions; restricted, excluded) | `[PROVIDE]` |
| 67 | `3_2_begin_final_revisions.csv` | `data/raw/` | III->II reclassification cohort: regulatory metadata plus the author's hand-entered invention years and their literature citations. Author-collected primary file; provenance in `certification/PUBLIC_SOURCE_PROVENANCE.csv`, variables in `CODEBOOK.md` | `[PROVIDE]` |
| 68 | `foiclass.txt` | `data/raw/` | FDA FOI device classification (implant flags, life-sustaining flags) | `[PROVIDE]` |
| 69 | `hand_coded_intuitive_3_2.csv` | `data/raw/` | Hand-coded intuitive control matches for III->II | `[PROVIDE]` |
| 70 | `Good_2_1_Control_2_1.txt` | `data/raw/` | Federal Register text of the 2019 premarket-notification exemption rule (84 FR 71794), from which the II->I control regulation numbers were read | `[PROVIDE]` |
| 71 | GRID `types.csv` | `data/raw/GRID/` | GRID organization type classifications (Company, Education, etc.) | `[PROVIDE]` |
| 72 | `MAUDE/masterevent.txt` | `data/raw/MAUDE/` | FDA MAUDE master event records | `[PROVIDE]` |
| 73 | `MAUDE/patient.txt` | `data/raw/MAUDE/` | FDA MAUDE patient outcome data | `[PROVIDE]` |
| 74 | `MAUDE/deviceproblems.txt` | `data/raw/MAUDE/` | FDA MAUDE device problem reports | `[PROVIDE]` |
| 75 | `MAUDE/problemcodedesc.txt` | `data/raw/MAUDE/` | FDA MAUDE problem code descriptions | `[PROVIDE]` |
| 76 | `MAUDE/device_data/*` | `data/raw/MAUDE/device_data/` | FDA MAUDE device-level event files (multiple files by year) | `[PROVIDE]` |
| 77 | Dimensions API key | *(never in the package)* | Required only to re-run the provenance-only Dimensions extraction. Supply it in your own environment as `DIMENSIONS_API_KEY`; no credential file is included in, or may be added to, any package (see `RESTRICTED_DATA_MANIFEST.csv`, "Credentials and secrets") | `[PROVIDE]` |
| 78 | `compustat_firm_data.csv` | `data/raw/` | Compustat firm-year financials with the CRSP PERMNO link (`at`, `LPERMNO`, `fyear`), extracted per `WRDS_EXTRACTION_ROADMAP.md` Query 1. WRDS-licensed; restricted, excluded | `[PROVIDE]` |
| 79 | `CRSPDirectory.csv` | `data/raw/` | CRSP firm directory (firm name → PERMNO); read only by `gen_06b_permno_universe.py` under `RUN_PERMNO_UNIVERSE_BUILD=1`. WRDS-licensed; see `WRDS_EXTRACTION_ROADMAP.md` Query 2 | `[PROVIDE]` |
| 80 | `AllPublicCompanies.csv` | `data/raw/` | Compustat CCM public-company list (firm name → PERMNO); read only by `gen_06b_permno_universe.py` under `RUN_PERMNO_UNIVERSE_BUILD=1`. WRDS-licensed; see `WRDS_EXTRACTION_ROADMAP.md` Query 2 | `[PROVIDE]` |

Items 79–80 are read by a provenance-only script that neither official route runs. On the
simulated route the file that `gen_06b` would produce,
`data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv`, is generated instead by
`synthetic_pipeline/generators/gen_00i_synthetic_maude_linkage_inputs.py`, so the simulated route
needs neither WRDS extract.

---

## Summary

- **55 analysis-script inputs** + **3 R scripts** + **22 generation-script inputs** = **80 total external inputs**
- **22 files are `[GENERATE]`**: #1–3, #5–6, #8–21, #26–28
  - 13 from `code/00_generate_data/gen_01_main_panels.py`: #1–3, #8–13, #20, #26–28
  - 2 from `gen_02_price_matching.py`: #5, #6 (constrained adverse event panels)
  - 1 from `gen_03_lbd.py`: #14 (LBD approval time)
  - 4 from `gen_04_parquets.py`: #15–18 (parquet pre-builds)
  - 1 from `gen_05_adverse_fsize.py`: #19 (adverse event firm size)
  - 1 from `gen_06_adv_2020.py`: #21 (Adv_Event_2020_2022)
- **58 files are `[PROVIDE]`**: #4, #7, #22–25, #29–80
  - 3 are **PROPRIETARY** (MarketScan: #4, #22, #23)
  - 6 are **GPT-generated** (non-deterministic, ship as static: #37–42)
  - 22 are generation-script raw inputs (#59–80), of which #79–80 are read only by the
    provenance-only `gen_06b_permno_universe.py`
- Items marked **gen** in "Used By" column are also read by the generation script itself as raw inputs

---

## Provenance notes — author-created exemption/control inputs

- **`Class2_Exemptions_2017_Grennan.csv`** (#32). Built from public FDA sources (not
  from Grennan — legacy filename only). Base = FDA's final determination listing the
  Class II devices exempted from 510(k) premarket notification under section 3054 of the
  21st Century Cures Act, **82 FR 31976 (11 July 2017)**, keyed by regulation number
  (244 product codes across 138 regulation numbers; full citation in `DATA_SOURCES.md`).
  The build is documented in the original
  construction script `Recall_Analysis_2017_1998_appendix.py`, which is not part of the deposit;
  the shipped `code/11b_recall_analysis.py` carries that construction forward: it left-pads
  `REGULATIONNUMBER` to 8 characters, merges product-code descriptions from the FDA
  classification database (`foiclass.txt`), and sets `Submitted_510k` /
  `Submitted_510k_last10` from the 510(k) database. Used by `11b_recall_analysis.py`
  (Figures D.14-D.15).
- **`hand_coded_intuitive_3_2.csv`** (#69). 12 product codes hand-selected by the
  author as intuitively/clinically similar control device types for the Class
  III->II analysis — the "Intuitive" alternative control group (column (4) in the
  regression tables); descriptions joined from the FDA classification database. Read
  by `gen_01_main_panels.py`. A primary author-coded input (no generating script).
- **`spinal_entrant_audit.csv`** (#43). The 20-firm hand audit behind the
  regulatory-proficiency footnote. Sample: the first-time 510(k) applicants under product
  code MAX (intervertebral body fusion devices), submissions from 2007 onward, taken from
  the de-duplicated applicant list `unique_firms_thr_75.csv`. `APPLICANT`,
  `DATERECEIVED`, `year` and `PRODUCTCODE` are the public FDA 510(k) fields of those
  submissions; `US_based`, `subsidiary`, `acquired` and `founded` were **hand-entered by
  the author** from public web searches on each firm, and are blank where the search
  returned nothing (`acquired` for one firm, `founded` for two). No shipped program writes
  the file. Read by `15_intext_derived_numbers.py`, which tabulates the six registered
  in-text values rather than letting them be typed. Column definitions are in
  `CODEBOOK.md`; the provenance row is in `certification/PUBLIC_SOURCE_PROVENANCE.csv`.
- **`Good_2_1_Control_2_1.txt`** (#70). Raw Federal Register text of FDA's final rule
  "Medical Devices; Exemptions From Premarket Notification for Class I and Class II
  Devices", **84 FR 71794 (30 December 2019)**; the shipped file is a text extraction of
  the amendatory portion, pages 71797–71819 of that issue (full citation in
  `DATA_SOURCES.md`). The author extracted control regulation numbers/product codes for
  the Class II->I analysis from this text. A primary input copied from a public source.
- **`3_2_begin_final_revisions.csv`** (#67). The III->II reclassification cohort, 31
  product codes. Regulatory columns are transcribed from the FDA product-classification
  database and the Federal Register; `yr_invent_or_comm_avail` and `source` were
  **author-collected** from the published medical and technical literature, one
  citation per row (e.g. a journal article with its PMID). No shipped program writes the
  file. It defines the Table D.1 universe and is the hand-coded benchmark for the
  invention-year validation in `15_intext_derived_numbers.py`. Column-by-column
  definitions are in `CODEBOOK.md`; the provenance row is in
  `certification/PUBLIC_SOURCE_PROVENANCE.csv`.
- **`RegNum_Factorized_Synth.csv`** (#7, and the byte-identical `data/raw/` copy).
  Author-built crosswalk, 5,542 rows. Device attributes come from the FDA
  product-classification database; `Reg_Change_List`/`Reg_Change_Text`/`Reg_Title` are
  Federal Register citations, dates and rule titles; `CPC_1..3` are the top three
  Cooperative Patent Classification symbols for the product code's patents and
  `CPC_Desc_1..3` are the public CPC scheme's own hierarchy titles for those symbols. The
  retrieval path for the three description columns is not recorded in the package; the
  strings are scheme titles, not patent text, and carry no restricted content. Both copies
  ship because `09`/`11b`/`11d` read the `data/raw/` path and `10c` reads the
  `data/derived/` path.
- **`Data_new_latest.png`** (#52). An author-created chart image, the source asset for
  Appendix Figure D.2. It is a rendered exhibit, not a dataset: `11g_descriptive_figures.py`
  copies it into `output/figures/` rather than regenerating it. Its underlying numbers are
  not re-derived by any shipped program; see `certification/FIGURE_PROVENANCE.md`.
- **The API-derived inputs** (#37–41). The invention-year files were produced with OpenAI
  GPT-4o at temperature 0; the price-link concordance with OpenAI `gpt-5-mini` at the API
  defaults. Both generating programs ship, carry their prompts verbatim, and refuse to run
  by default. Neither family is regenerated on any route. See `CODEBOOK.md`, "API-derived
  fixed inputs", for the full record including which raw responses are archived.
