# Codebook

**Supporting reference; `README.md` governs.** `README.md` is the single documentation point for this
package; this file is the per-variable detail behind its dataset list.

Variable documentation for the main analysis files in this replication package
(JPE Data Policy 1.5). For raw-input provenance and the file-to-script map, see
`DATA_INPUTS.md` and `DATA_SOURCES.md`.

**Metadata coverage (how the three 1.5 artifacts divide the work).** No single file carries every
variable's semantics; together they cover the deposit:
- **`certification/DATA_DICTIONARY.csv`** is auto-generated over the shipped SYNTHETIC payload
  (`synthetic_pipeline/simulated_data/`) and records, per column, its **privacy class + provenance**
  (public / synthetic-value / derived / scrambled-identity / merge-key-id) plus units, ranges, and
  missingness. Its `description` field states that provenance/privacy class by design — it is NOT the
  per-variable economic definition.
- **This CODEBOOK.md** carries the per-variable **semantics** for the main analysis files (the
  adverse-event / innovation / market / price panels below).
- **Shipped REAL inputs** — section "Shipped input files" at the end of this codebook defines every
  shipped `data/` file that is not an FDA public file. The five FDA public databases
  (MAUDE, 510(k), PMA, product classification, device recall) are **delegated by name** to the agency's
  own published record layouts, which are cited in the bibliography (`data_maude`, `data_fda510k`,
  `data_fdapma`, `data_fdaclass`, `data_fdarecall`) and listed again under "FDA public files
  (delegated)" below; for those files this codebook names the columns the code actually reads rather
  than restating the agency dictionary.

Unit of observation for the panel files is the **product code x year**
(`PRODUCTCODE` x `year`), unless noted otherwise. "PC" = FDA product code.
Reclassification directions: **II->I** (file tag `2_1`, a deregulation) and
**III->II** (file tag `3_2`, a down-regulation).

---

## Adverse-event variable scheme

Adverse-event counts come from FDA MAUDE. Two encodings appear:

- **Aggregate outcome flags** (single letters): `D`, `L`, `H`, `S`, `R`. These
  are MAUDE patient-outcome codes parsed from `SEQUENCE_NUMBER_OUTCOME`:
  - `D` = Death / mortality event count
  - `L` = Life-threatening event count
  - `H` = Hospitalization event count
  - `S` = Disability / serious-injury event count
  - `R` = Required-intervention event count
- **`v_serious`** = `D + L + H + S` (the paper's "serious adverse events"
  measure).
- **Reporter-disaggregated counts** (letter + suffix, e.g. `L_M`, `H_U`): the
  same outcome letter split by MAUDE `REPORT_SOURCE_CODE`, suffixes
  `M`/`U`/`D`/`P` (manufacturer / user-facility / distributor / other-reporter,
  per the MAUDE report-source codes). Additional outcome letters appear in the
  disaggregated set (`C`, `O`, `U`, `I`, `A`) and follow MAUDE's outcome-code
  values; consult the FDA MAUDE data dictionary for the full code list.
- `event_count` = number of MAUDE event records contributing to the PC-year.

MAUDE is treated as reliable from 1992 onward; post-1991 missing counts are set
to 0 during panel construction.

---

## Common panel columns

These columns are shared by `Full_sample.csv`, `matched_sample_*.csv`,
`intuitive_*_oct22_24.csv`, `later_treated_*_oct22_24.csv`,
`spillovers_*_oct22_24.csv`, and the `data_2_1_*.parquet` files. Per-file
sections below list only the columns added on top of this common set.

Identifiers and device metadata:

- `PRODUCTCODE` — FDA product code (string). Primary device-type identifier.
- `year` — calendar year of the observation (integer).
- `REGULATIONNUMBER` — CFR regulation number governing the product code.
- `DEVICECLASS` — FDA device class (I, II, III).
- `DEVICENAME` — FDA device name string.
- `DESCRIPTION_OF_REGNUM` — text description of the regulation number.
- `SUBPART_DESCRIPTION` / `PART_DESCRIPTION` — CFR subpart / part description.
- `SUBMISSION_TYPE_ID` — premarket pathway (e.g. `510(K)`, `510(K) Exempt`, PMA).
- `use_case` — internal sample-construction tag for the reclassification pathway.
- `Reg_Change_List` — list/marker of regulation-change events for the PC.

Treatment / reclassification:

- `year_reclassified_2_1` — year the PC was reclassified II->I (NaN if never).
- `year_reclassified_3_2` — year the PC was reclassified III->II (NaN if never).
- `FDA_own_accord` / `FDA_own_accord_3_2` — 1 if reclassification was
  FDA-initiated (vs. petition/de novo); for the II->I and III->II events resp.
- `controls` — 1 if the PC is an eligible control device type.
- `*_3_2` suffixed columns (`DESCRIPTION_OF_REGNUM_3_2`, `PART_DESCRIPTION_3_2`,
  `REGULATIONNUMBER_3_2`, `date_proposed_3_2`, `Petition_DeNovo_Filing_Date_3_2`,
  `SUBMISSION_TYPE_ID_3_2`, `SUBPART_DESCRIPTION_3_2`) — III->II-specific copies
  of the corresponding metadata fields.

Patenting / innovation outcomes:

- `patents_allpats` — patent count assigned to the PC (all assignee types).
- `patents_newfirm`, `patents_newfirmPC` — patent counts attributed to new
  firms (overall and within-PC entrants).
- `<Type>_allpats` / `<Type>_newfirm` / `<Type>_newfirmPC` — patent counts by
  GRID assignee type, where `<Type>` in {`Archive`, `Company`, `Education`,
  `Facility`, `Government`, `Healthcare`, `Nonprofit`, `Other`} (GRID
  organization classifications).
- `patents_pats_nodrugs` — patent count excluding drug (A61K-type) patents.
- `times_cited` — forward citations to the PC's patents.
- `times_cited_outside_ind` — forward citations originating outside the device's
  own industry.
- `xi_real` — KPSS patent market value aggregated to the PC, in **millions of 1982 USD**
  (the base year of the KPSS public release; see `KPSS_2019_public.csv` below). The
  2019-dollar outcome used in estimation is `xi_real_2019` = `xi_real` /
  `config.CPI_DEFLATOR_2019` (= 0.3891444146542998), created in `03a`/`03b`/`04`/`10`/`11d`.

Firm-structure outcomes:

- `dev_count` — count of device submissions (submission rate) in the PC-year.
- `firm_count` — number of firms active in the PC.
- `absnew_firm_count` — count of absolutely-new firms entering the PC.
- `firm_size` — firm size (assets) measure merged in for the PC (restricted
  WRDS-derived; absent in public package).

Patent-eligibility bookkeeping (used for sample selection):

- `patent_sum_2_1`, `patent_sum_3_2` — pre-period patent sums used to flag
  patenting PCs for the II->I and III->II samples.
- `total_pat_sum` — total patent sum across the window.
- `one_pat_atleast` — 1 if the PC has at least one patent (sample filter).
- `use_2_1_treat`, `use_3_2_treat` — 1 if the PC is a treated unit in the
  respective sample.
- `PRODUCTCODE_COUNT` — number of records for the PC (bookkeeping).

Adverse-event columns: see "Adverse-event variable scheme" above
(`D`, `H`, `L`, `S`, `R`, `v_serious`, `event_count`, and the
`{D,L,H,S,C,R,O,U,I,A}_{U,D,P,M}` reporter-disaggregated set).

---

## Full_sample.csv

Master product-code x year panel feeding sample construction and estimation
(used by steps 02, 03a, 09, 11b, 11d, 11e). Columns: the common panel set
above. This is the unmatched universe; treated and control PCs are selected
downstream into the matched/intuitive/later-treated/spillover files.

## matched_sample_2_1_onepat.csv / matched_sample_3_2_onepat.csv

Mahalanobis-matched estimation samples (treated + matched controls), II->I and
III->II respectively. Common panel set plus estimation columns:

- `treatment` — 1 if the PC is a treated (reclassified) unit, 0 if matched
  control.
- `year_reclassified` — the operative reclassification year for the unit in this
  sample (direction-specific).
- `posttreat` — 1 in years on/after the unit's effective treatment year
  (with the outcome-specific anticipation window applied in config).
- `factorized` — integer PC identifier (categorical code) for fixed effects.
- `FE` — fixed-effect grouping key used in estimation.
- `event_time` (where present) — year relative to reclassification.
- Outcome aliases used by the estimator: `real_pats` (patent count outcome),
  `unique_firms`, `unique_firmsPC`, `firm_expansion`, `firm_expansion_patents`,
  `xi_real_2019` (real 2019 USD patent value), `v_serious`.
- `*_innovation`, `*_innovation_quality`, `*_petitioned` filename variants carry
  the same schema, restricted to the innovation/quality/petitioned subsamples.

## intuitive_*_oct22_24.csv

"Intuitive" control samples (hand-/similarity-selected comparison PCs), II->I
(`intuitive_2_1_oct22_24.csv`) and III->II
(`intuitive_3_2_oct22_24_similarity.csv`). Common panel set plus `treatment`,
`year_reclassified`, `posttreat`, `factorized`, `v_serious`, and (3_2)
similarity scores.

## later_treated_*_oct22_24.csv

Not-yet-treated ("later-treated") control samples used as a clean control group.
Common panel set plus `treatment`, `posttreat`, `factorized`.

## spillovers_*_oct22_24.csv / intuitive_spillovers_3_2_oct22_24.csv

Spillover samples that retain MAUDE event-record detail (manufacturer/distributor
address fields, `DEVICE_EVENT_KEY`, `PATIENT_SEQUENCE_NUMBER`,
`NUMBER_PATIENTS_IN_EVENT`) in addition to the common panel set, plus
`treatment`, `year_reclassified`, `posttreat`, `factorized`, `v_serious`.

## data_2_1_full / _intuitive / _latertreat / _spillovers.parquet

Pre-stacked II->I estimation inputs in Parquet (same schema as the
corresponding CSV samples), produced by `gen_04_parquets.py` for fast loading by
`03b_estimation_2to1.py`.

---

## safety_did_analysis.csv / safety_did_analysis_3_2.csv

Patent-safety DiD panel (II->I and III->II), produced by
`06a_safety_analysis.py`. PC x year.

- `PRODUCTCODE`, `year` — identifiers.
- `patents` — patent count in the PC-year.
- `safety` — count of safety-related patents (keyword-classified).
- `safety_prop` — safety patents as a share of patents (`safety / patents`).
- `treatment` — treated indicator; `treatment_final` — finalized treatment flag
  after episode assignment.
- `year_reclassified`, `year_reclassfinal` — reclassification year (raw and
  finalized).
- `event_time`, `ET`, `year_reclass_ET` — event-time (years to reclassification)
  helpers.
- `factorized` — integer PC id for fixed effects; `FE` — fixed-effect key.
- `class_by_episode` — episode-level class grouping.
- `posttreat` — post-treatment indicator.
- `baseline_event_count` — pre-period baseline used for normalization.

## constrained_adv_event_new_sept25.csv / _3_2.csv

MarketScan-constrained adverse-event / utilization panel (II->I and III->II)
used by the event-study step (04). PC x year.

- `PRODUCTCODE`, `year` — identifiers.
- `proc_count` — procedure count (MarketScan utilization).
- `pay`, `coins`, `BilledAmt`, `PaidAmt` — payment/utilization amounts
  (MarketScan-derived; restricted).
- `treatment`, `posttreat`, `factorized`, `FE` — estimation columns (as above).
- `event_time` — years relative to reclassification.
- `class_by_episode` — episode-level class grouping.
- `2_1`, `year_reclassified_2_1` (in the II->I file) / `year_reclassified` —
  reclassification timing.
- `Unnamed: 0` — pandas index artifact (ignore).

## LBD_ApprovalTime_Both_oct22_24.csv

Learning-by-doing approval-time panel (both reclassification types), produced by
`gen_03_lbd.py`; consumed by `08_lbd_simulation.py` and `09_summary_stats.py`.

- `cluster id app` — applicant cluster id (entity-resolved firm).
- `cluster id` — device cluster id (entity-resolved device).
- `PRODUCTCODE`, `year` — identifiers.
- `Days_take_approve` — days from submission to approval (approval time).
- `cumsum_time_t1` — cumulative experience (running approval-time sum) used as
  the proficiency / learning measure.

## RegNum_Factorized_Synth.csv

Regulation-number crosswalk with reclassification metadata and CPC technology
descriptions; used by steps 09, 11b, 11d.

- `PRODUCTCODE` (and `PRODUCTCODE_x`, `PRODUCTCODE_y` merge artifacts),
  `sub_prod_code` — product-code identifiers.
- `REGULATIONNUMBER`, `DESCRIPTION_OF_REGNUM`, `Reg_Title`, `Reg_Change_List`,
  `Reg_Change_Text` — regulation identity and change history.
- `DEVICECLASS`, `DEVICENAME`, `PART_DESCRIPTION`, `SUBPART_DESCRIPTION`,
  `SUBMISSION_TYPE_ID` — device metadata.
- `FDA_own_accord` — FDA-initiated reclassification flag.
- `De_Novo`, `DENOVO_DATERECEIVED`, `DENOVO_APPLICANT`,
  `Petition_DeNovo_Filing_Date`, `Petition_DeNovo_Firm_Name` — de novo /
  petition metadata.
- `year_reclassified`, `reclass_years`, `auto_year`, `auto_categorize` —
  reclassification timing and auto-classification helpers.
- `CPC_1`, `CPC_2`, `CPC_3` and `CPC_Desc_1..3` — top CPC technology codes and
  descriptions for the device's patents.
- `use_case`, `sample_size`, `factorized`, `0` (index artifact) — bookkeeping.

---

## Notes

- Restricted-data columns (e.g. `firm_size`, MarketScan payment fields, and
  patent-level Dimensions inputs) are present in the schema but their source
  files are excluded from the public package; see `RESTRICTED_DATA_MANIFEST.csv`.
- `Unnamed: 0` / `0` columns are pandas index artifacts and are not analysis
  variables.
- For the precise script that produces each file, see `DATA_INPUTS.md`
  (GENERATE vs. PROVIDE labels).
- For per-column metadata (dtype, units, non-null rate, missing-value meaning,
  distinct-value count, and allowed values/coarse range) over the full
  116-file synthetic payload, see `certification/DATA_DICTIONARY.csv`, which
  is machine-generated and content-validated from the built synthetic tree at
  package-build time.


---

# Author-created / modified datasets (JPE Policy 1.5)

This section documents the author-**generated** datasets (the **21** `[GENERATE]`
files in `DATA_INPUTS.md` — see its Summary, item #130 — and `data_input_manifest.csv`).
Column semantics not obvious from the name are given; full column lists are in each
file's header and the producing script (`00_generate_data/`).

**`gpt-5-mini` procedure-code price links** (`2_1_GPT_Price_Links.csv`, 301 rows;
`3_2_GPT_Price_Links.csv`, 36 rows) — these are **not** key→value maps; each is a
15-column structured model output linking an FDA product code to a billing code.
The model is OpenAI **`gpt-5-mini`** (`code/12b_gpt_price_links_generation.py:67`), not
GPT-4o; the invention-year files below are the GPT-4o ones. Full generation facts
(model, prompt, sampling settings, what is and is not archived) are in "API-derived
fixed inputs" at the end of this codebook.

| Column | Description |
|---|---|
| `row_index` | Source row index in the input device list |
| `productcode` | FDA 3-letter product code |
| `devicename` | FDA device name |
| `regulationnumber` | FDA regulation (21 CFR) number |
| `description_of_regnum` | Text description of the regulation |
| `subpart_description` | CFR subpart description |
| `status` | Device regulatory status |
| `decision` | Whether a billing-code link was identified |
| `mapping_quality` | GPT-assessed quality of the HCPCS/CPT mapping |
| `hcpcs_cpt` | Matched HCPCS/CPT procedure code |
| `hcpcs_level_2` | Matched HCPCS Level II code, if applicable |
| `procedure_desc` | Description of the matched procedure |
| `rationale` | GPT rationale for the mapping |
| `alternates` | Other codes considered for the same device type |
| `confidence` | GPT confidence score for the link |

Other author-created **`[PROVIDE]`** inputs are static artifacts documented (with
their provenance) in `DATA_INPUTS.md`: the GPT-4o invention-year files
(`innovation_year_*`) and the hand-coded control inputs (`hand_coded_intuitive_3_2.csv`
— 12 author-selected intuitively-similar control product codes for the III->II
"Intuitive" control group; `spinal_entrant_audit.csv` — the 20-firm hand audit of new
spinal-implant entrants behind the regulatory-proficiency footnote;
`Good_2_1_Control_2_1.txt` — raw FDA Federal Register
exemption-rule text from which II->I control regulation numbers were extracted);
their provenance is detailed in `DATA_INPUTS.md` ("Provenance notes").

**Public package vs provider-authorized routes:** in the public Dataverse package the *real* `Full_sample.csv`
is **not shipped at all**. Shipping it reduced to a 71-column public schema would not be
sanitization: column-stripping a mixed restricted master leaves row membership, ordering and
missingness as disclosure surfaces. `data/derived/Full_sample.csv` is instead
created at RUNTIME on a fresh extraction (see the synthetic counterpart described just below), the real
master is on no shipping inventory (`certification/PUBLIC_PACKAGE_ALLOWLIST.txt` is the sole list of what
the package may contain), and its materialization precondition is `ABSENT`. The *real* matched/intuitive/spillover panels
below are **excluded** (restricted-lineage) and are reproduced only in the provider-authorized
verification routes (there is no separate editor package). However, the
public package also ships **fully synthetic counterparts** of these panels in the simulated payload
(`synthetic_pipeline/simulated_data/`): `materialize_simulation.py` supplies a
110-column synthetic `Full_sample.csv`, and step 9 (`02_match_samples.py`) regenerates the
matched samples from it, so the analysis runs end-to-end on synthetic data (see
`synthetic_pipeline/DGP_DESIGN.md`). The synthetic panels contain no real restricted data.

## Matched-sample panels (shared schema)
`intuitive_2_1_*`, `later_treated_2_1_*`, `spillovers_2_1_*`, `intuitive_3_2_*`,
`later_treated_3_2_*`, `intuitive_spillovers_3_2_*` and the pre-built parquet
equivalents (`data_2_1_full/intuitive/latertreat/spillovers.parquet`) all share a
product-code × year panel schema (≈111 columns), the same family as
`Full_sample.csv`. Key columns:
- `PRODUCTCODE` — FDA device product code (panel unit). `year` — calendar year.
- `REGULATIONNUMBER`, `DEVICECLASS`, `SUBMISSION_TYPE_ID`, `DEVICENAME`,
  `SUBPART_DESCRIPTION` — FDA device-registry attributes.
- `dev_count`, `firm_count`, `absnew_firm_count` — device-submission and firm
  counts (outcomes). `patents_allpats` and the GRID-type splits
  (`Company_allpats`, `Education_allpats`, `Facility_allpats`, `Government_allpats`,
  `Healthcare_allpats`, `Nonprofit_allpats`, `Other_allpats`, `Archive_allpats`) —
  patent counts overall and by assignee organization type.
- `treatment`/`posttreat`/`event_time`/`year_reclassified` — DiD treatment timing.
`use_case` and `Reg_Change_List` flag the reclassification group (intuitive vs
later-treated control vs spillover).

## `all_patents_w_xi_oct22_24.csv` — patent-level (25 cols)
Patent-level file with market valuations. `id`/`patnum` — patent identifiers;
`PRODUCTCODE` — linked FDA product code; `GRID` + `original_assignee_*` —
assignee org; `year`, `type`; assignee-type flags (`Company`…`Other`);
`xi_real`/`xi_nominal` — KPSS patent market value (millions of 1982$ / millions of
nominal $); `cites` —
forward citations; `CPI`; `permno` — CRSP firm identifier; `firm_size` — firm total
assets. (Upstream patent records are Dimensions; valuations are public KPSS.)

## `safety_vars_allpats.csv` — patent safety indicators (4 cols)
`id` — patent id; `safety`, `cost`, `quality` — binary indicators of
safety/cost/quality-related language (keyword classifier; see `06b`).

## `constrained_adv_event_new_sept25*.csv` — utilization-constrained AE panels (17 cols)
Product-code × year panel for the price/utilization analyses. `pay`, `BilledAmt`,
`PaidAmt`, `proc_count`, `coins` — MarketScan billing/utilization aggregates;
`treatment`/`posttreat`/`event_time`/`year_reclassified(_2_1)` — DiD timing;
`class_by_episode`, `factorized`, `FE` — fixed-effect / grouping helpers; `2_1`
flags the II→I sample. (`_3_2` is the III→II counterpart.)

## `adverse_event_panel_by_PC_full.csv` — MAUDE AE panel (73 cols)
Product-code × year adverse-event panel built from FDA MAUDE. Includes
`NUMBER_PATIENTS_IN_EVENT`, manufacturer/distributor identity and address fields,
`REPORT_TO_MANUFACTURER`, and event/device attributes; used for summary statistics.

## `unique_devices_thr_75.csv`, `unique_firms_thr_75.csv`, `unique_firms_in_PC_thr_75.csv`
510(k)/PMA registry rows after fuzzy de-duplication (threshold 0.75). Columns:
`KNUMBER` (510(k) number), `PRODUCTCODE`, `APPLICANT`, `DEVICENAME`,
`COUNTRY_CODE`, `year`, `DATERECEIVED`, `PMANUMBER`, `TRADENAME`. Used for
device/firm counts in summary statistics.

## `LBD_ApprovalTime_Both_oct22_24.csv`, `Adverse_fsize_ready_all4_oct22_24.csv`, `Adv_Event_2020_2022.csv`
Generated intermediate panels: learning-by-doing approval-time panel (by
reclassification type), adverse events merged with firm size (4 event types), and
the 2020–2022 adverse-event extension, respectively. See producing scripts in
`00_generate_data/` and the `used_by` column of `data_input_manifest.csv`.

---

# Shipped input files — variable documentation (JPE Policy 1.5)

This section documents every file shipped under `data/` that is **not** one of the five FDA
public databases delegated below. Row and column counts are the shipped files, measured with
pandas; "allowed values" are stated where the column is categorical or an indicator.

## FDA public files (delegated to the agency record layouts)

For these files the authoritative variable documentation is the agency's own published record
layout, cited in `paper/FDAPaperv1.bib` and in the README "Data References". They are
redistributed byte-for-byte, so restating FDA's dictionary here would only risk drift.

| Shipped file(s) | Agency dictionary | Columns the shipped code reads |
|---|---|---|
| `data/raw/501k_all.csv` (22 cols) | FDA 510(k) downloadable-files record layout (`data_fda510k`) | `KNUMBER`, `PRODUCTCODE`, `APPLICANT`, `DEVICENAME`, `COUNTRY_CODE`, `DATERECEIVED`, `DECISIONDATE` |
| `data/raw/all_pma_approvals.txt` (22 cols, pipe-delimited) | FDA PMA downloadable-files record layout (`data_fdapma`) | `PMANUMBER`, `PRODUCTCODE`, `APPLICANT`, `TRADENAME`, `DATERECEIVED`, `DECISIONDATE` |
| `data/raw/foiclass.txt` (18 cols, pipe-delimited) | FDA Product Classification (`foiclass`) record layout (`data_fdaclass`) | `PRODUCTCODE`, `REGULATIONNUMBER`, `DEVICECLASS`, `DEVICENAME`, `SUBMISSION_TYPE_ID`, `IMPLANT_FLAG`, `LIFE_SUSTAIN_SUPPORT_FLAG` |
| `data/raw/device-recall-0001-of-0001-2.json` | openFDA device-recall API fields (`data_fdarecall`) | `product_code`, `event_date_initiated`, `recalling_firm` |
| `data/raw/MAUDE/**`, `data/raw/MAUDE_2020/**` (65 files — 58 in `MAUDE/` and 7 in `MAUDE_2020/`: `masterevent.txt`, `patient.txt`, `deviceproblems.txt`, `problemcodedesc.txt`, `device_data/foidev*.txt`, `device_data/MDR/mdr*.txt`, `device_data/ASR/ASR_*.csv`, `device_data/DEVICE20*.txt`) | FDA MDR data-files record layouts (`data_maude`) | `MDR_REPORT_KEY`, `DEVICE_REPORT_PRODUCT_CODE`, `DATE_RECEIVED`, `SEQUENCE_NUMBER_OUTCOME`, `REPORT_SOURCE_CODE`, `MANUFACTURER_D_NAME`, `NUMBER_PATIENTS_IN_EVENT` |

The MAUDE outcome and reporter codes parsed out of `SEQUENCE_NUMBER_OUTCOME` and
`REPORT_SOURCE_CODE` are defined in "Adverse-event variable scheme" at the top of this codebook.

## `data/raw/KPST_Breakthrough.csv` — KPST patent similarity / breakthrough panel

11,474,838 rows x 12 columns; one row per patent, 1836–2022. Source: the Kelly–Papanikolaou–Seru–Taddy
extended-data release (see `certification/PUBLIC_SOURCE_PROVENANCE.csv`). Definitions below are taken
from that release's own README (retrieved 2026-09-17), which is the source documentation for this file.

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `patent_num` | integer | USPTO patent number | Patent ID number (merge key to the device-patent file). |
| `issue_year` | integer | year, `yyyy` | Year the patent was issued. |
| `filed_year` | integer | year, `yyyy` | Year the patent was filed. |
| `fsim01` | float | similarity index, >= 0, unitless | Forward 1-year aggregate patent similarity. |
| `fsim25` | float | similarity index, >= 0, unitless | Forward 2–5 year aggregate patent similarity. |
| `fsim610` | float | similarity index, >= 0, unitless | Forward 6–10 year aggregate patent similarity. |
| `bsim5` | float | similarity index, >= 0, unitless | Backward 5-year aggregate patent similarity. |
| `lqsim05` | float | log ratio (can be negative) | 5-year patent importance: log(fsim5 / bsim5). Missing after 2016 by construction (truncation). |
| `lqsim010` | float | log ratio (can be negative) | 10-year patent importance: log(fsim10 / bsim5). Missing after 2011 by construction (truncation). |
| `bk_p90_alqsim05` | float indicator | {0, 1}, missing after 2016 | Breakthrough indicator based on the 5-year importance measure (top decile). **This is the outcome the package uses** (`code/14_breakthrough_patents.py:62`). |
| `bk_p90_alqsim010` | float indicator | {0, 1}, missing after 2011 | Breakthrough indicator based on the 10-year importance measure. |
| `fcitALL` | integer | count, >= 0 | Total forward citations through 2022. |

`code/14_breakthrough_patents.py` reads only `patent_num` and `bk_p90_alqsim05`. The truncation
windows above are the KPST authors' own caveat and are why the breakthrough sample ends before the
patent panel does.

## `data/raw/KPSS_2019_public.csv` — KPSS patent market values

2,950,305 rows x 7 columns; one row per patent, issue years 1926–2019. Source: the
Kogan–Papanikolaou–Seru–Stoffman extended-data release (2019 vintage). Definitions are the release
README's own (retrieved 2026-09-17).

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `patent_num` | integer | USPTO patent number | Patent ID number. |
| `xi_real` | float | **millions of 1982 USD** | Value of innovation (xi), deflated to 1982 dollars with the CPI: `xi_real = xi_nominal / CPI * 100`. |
| `xi_nominal` | float | millions of nominal USD | Value of innovation in the dollars of the patent's issue year. |
| `cites` | integer | count, >= 0 | Forward citations to the patent in the KPSS release. |
| `permno` | integer | CRSP PERMNO (5-digit) | CRSP firm identifier of the patent's assignee, **as published by KPSS in their own public release**. See `LICENSE.txt` §3 for why this column ships while the author's own CRSP-derived crosswalk does not. |
| `issue_date` | string | date text as published | Patent issue date as distributed. A minority of early-year values are malformed in the upstream release (e.g. an impossible month/day pair); the column is **not read** by any shipped program. |
| `filing_date` | string | date text as published | Filing date as distributed; same caveat, also not read. |

`gen_01_main_panels.py:584` reads this file and uses `patent_num`, `permno`, `xi_real`,
`xi_nominal` and `cites`; `09_summary_stats.py` uses it for the patent-value summary row.

No per-column contract governs this file — unlike its sibling `KPST_Breakthrough.csv` — and that
asymmetry is deliberate, not an omission. A column contract governs the members the pipeline
regenerates, which is KPST's class. `KPSS_2019_public.csv` instead ships as a pinned public
download: its bytes are listed in `certification/PUBLIC_INPUT_HASHES.csv` and must equal the
approved public download exactly, which is a stricter control than a per-column role.

## `data/raw/CPI_deflator.csv` — price deflator to 1982 dollars

119 rows x 2 columns, years 1834–2019 (not every year in that span is present; 67 years are absent,
mostly pre-1900).

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `year` | integer | year, `yyyy` | Calendar year. |
| `CPI` | float | deflation **factor**, 0.389–7.63 | Multiply a nominal dollar amount in `year` by this factor to express it in 1982 dollars. It is `100 / CPI-U(year)`, recovered as `xi_real / xi_nominal` from the KPSS release (`gen_01_main_panels.py:591` recomputes exactly this ratio), **not** an independently downloaded BLS series. The 2019 value, 0.38914, is `config.CPI_DEFLATOR_2019`. |

Read by `gen_05_adverse_fsize.py:116` to put Compustat total assets in real dollars.

## `data/raw/GRID/types.csv` — GRID organization types

95,064 rows x 2 columns. GRID release 2019-10-06 (CC0).

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `grid_id` | string | `grid.NNNN.N` | GRID organization identifier. |
| `type` | string | exactly one of `Company` (27,824), `Education` (18,700), `Healthcare` (12,290), `Nonprofit` (11,876), `Facility` (8,281), `Other` (7,772), `Government` (5,627), `Archive` (2,694) | GRID organization classification. These eight values are the `<Type>_allpats` / `<Type>_newfirm` / `<Type>_newfirmPC` column families in the analysis panels. |

## `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv` — product code to HCPCS/CPT crosswalk

7,953 rows covering 5,541 distinct product codes, 4 columns. Hand-coded by a paid certified medical
coder engaged by the author (work for hire); received 2024-01-17.

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `PRODUCTCODE` | string | 3-letter FDA product code | Device type being linked. |
| `HCPCS Level 1 (CPT Code)` | string | Python-literal list of 5-digit CPT codes, e.g. `['82040']`; `['']` when none | HCPCS Level I (CPT) procedure codes the coder judged to be the outpatient procedure(s) in which the device type is used. |
| `HCPCS Level 2` | string | Python-literal list of alphanumeric HCPCS Level II codes; `['']` when none | HCPCS Level II (device/supply) codes. |
| `HCCPS Category Code` | string | first listed code, or missing (23% missing) | Convenience single-code field; spelling of the header is as delivered. |

**Coding protocol as recorded in the package.** The instruction set given to the coder was not
retained in writing, so the link rule cannot be restated verbatim here; what is verifiable is the
deliverable (one or more HCPCS/CPT codes per product code, empty lists where the coder found no
procedure) and its receipt date. This crosswalk is the "expert" comparator behind the concordance
footnote in the manuscript; no shipped program currently reads it.

## `data/raw/Class2_Exemptions_2017_Grennan.csv` — 2017 Class II 510(k) exemption list

244 rows (244 product codes, 138 regulation numbers) x 9 columns. Author-built from the FDA
Federal Register final determination of 11 July 2017 (82 FR 31976; see `DATA_SOURCES.md`), merged
with `foiclass.txt` descriptions and 510(k)-submission flags. "Grennan" is a legacy filename label
only.

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `Unnamed: 0` | integer | — | pandas index artifact; not an analysis variable. |
| `REGULATIONNUMBER` | float | 21 CFR section, e.g. `862.1020` | Regulation exempted. |
| `Device type` | string | — | FDA device-type name as printed in the FR list. |
| `PRODUCTCODE` | string | 3-letter FDA product code | Exempted device type. |
| `DESCRIPTION_OF_REGNUM` | string | — | Regulation text description (from `foiclass.txt`). |
| `SUBPART_DESCRIPTION` | string | — | CFR subpart description (from `foiclass.txt`). |
| `PART_DESCRIPTION` | string | — | CFR part description (from `foiclass.txt`). |
| `Submitted_510k` | integer indicator | {0, 1} | 1 if the product code has any 510(k) submission in the FDA 510(k) database. |
| `Submitted_510k_last10` | integer indicator | {0, 1} | 1 if the product code has a 510(k) submission in the ten years before the exemption. |

Read by `code/11b_recall_analysis.py` as the treated-device list for Figures D.14–D.15.

## `data/raw/hand_coded_intuitive_3_2.csv` — hand-selected III→II control device types

12 rows x 4 columns: `PRODUCTCODE`, `DESCRIPTION_OF_REGNUM`, `SUBPART_DESCRIPTION`,
`PART_DESCRIPTION` (all strings; the three description fields are joined from `foiclass.txt`). The
product codes are the author's domain-knowledge selection of clinically similar, never-reclassified
device types that form the "Intuitive" control group for the Class III→II analysis. Read by
`gen_01_main_panels.py`. No column is an estimated or model-derived value.

## `data/raw/spinal_entrant_audit.csv` — hand audit of 20 new spinal-implant entrants

20 rows x 8 columns; one row per sampled firm. A primary author-coded file: no shipped program
writes it. The sample is the first-time 510(k) applicants under product code MAX (intervertebral
body fusion devices) with submissions from 2007 onward, drawn from the de-duplicated applicant list
`data/raw/unique_firms_thr_75.csv`. `APPLICANT`, `DATERECEIVED`, `year` and `PRODUCTCODE` are the
public FDA 510(k) fields of those submissions; the four attribute columns were hand-entered by the
author from public web searches on each firm, and are blank where the search returned nothing. No
column is an estimated or model-derived value.

| Column | Type | Units / allowed values | Definition and how it was coded |
|---|---|---|---|
| `APPLICANT` | string | lower-cased firm name | The 510(k) applicant name as published in the FDA 510(k) database, lower-cased as everywhere else in the pipeline. Taken from the registry, not hand-entered. |
| `DATERECEIVED` | date | `YYYY-MM-DD`, 2007-12-07 to 2018-09-20 | Date FDA received the firm's first 510(k) submission under this product code. Taken from the registry. |
| `year` | integer | 2007–2018 | Calendar year of `DATERECEIVED`. Derived from the registry field. |
| `PRODUCTCODE` | string | `max` | FDA product code for intervertebral body fusion devices; constant by construction of the sample. |
| `US_based` | integer indicator | {0, 1}; complete (20/20) | 1 if the firm is headquartered in the United States, else 0. Hand-coded by the author from the firm's own website or a public company profile. |
| `subsidiary` | integer indicator | {0, 1}; complete (20/20) | 1 if the firm was a subsidiary of another company at the time of the submission, else 0. Hand-coded by the author from the parent company's or the firm's own public disclosures. |
| `acquired` | float indicator | {0, 1}; **missing for 1 of 20** | 1 if the firm was later acquired, 0 if no acquisition was found. Hand-coded by the author from public acquisition announcements. Blank for `corelink llc`, where the search returned nothing conclusive. |
| `founded` | float | calendar year, 2000–2016; **missing for 2 of 20** | Year the firm was founded. Hand-coded by the author from the firm's own website or a public company profile. Blank for `corelink llc` and `spinemed ges.m.b.h`, where no founding year could be established. |

Read by `code/15_intext_derived_numbers.py` (step 35), which tabulates the six registered in-text
values quoted in the regulatory-proficiency footnote: the number of firms, the number that are
subsidiaries, the median and mean founding year, the number later acquired, and the U.S.-based
share. The two statistics over `founded` are computed on the 18 firms with a recorded year, and
`acquired` is summed treating the one blank as not acquired; both conventions are stated in the
program and in the report's `note` column.

## `data/raw/3_2_begin_final_revisions.csv` — III→II reclassification cohort with hand-entered invention years

31 rows x 38 columns; one row per III→II-reclassified product code. This is a primary
author-collected file: no shipped program writes it. Its regulatory fields are transcribed from the
FDA product-classification database and the Federal Register; its `yr_invent_or_comm_avail` and
`source` columns were hand-entered by the author from the published medical and technical
literature. It defines the 31-product-code III→II universe used in Table D.1 and is the hand-coded
benchmark for the GPT-versus-hand invention-year validation.

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `0`, `Unnamed: 26`, `Unnamed: 37` | float | all-missing | Spreadsheet artifacts; not analysis variables. |
| `Unnamed: 36` | float | sparse (6% populated) | Spreadsheet artifact; not read by any program. |
| `PRODUCTCODE`, `PRODUCTCODE_x`, `PRODUCTCODE_y` | string | 3-letter FDA product code | Product-code identifier (three merge-artifact copies with identical content). |
| `sub_prod_code` | string | free text, 84% populated | Author adjudication note about the row (e.g. a remark that a code's effective reclassification differs from the listed one). Not a code. |
| `DEVICENAME`, `DESCRIPTION_OF_REGNUM`, `PART_DESCRIPTION`, `SUBPART_DESCRIPTION`, `SUBMISSION_TYPE_ID` | string | — | FDA classification-database attributes. |
| `DEVICECLASS` | integer | constant `2` | Post-reclassification device class. |
| `REGULATIONNUMBER` | float | 21 CFR section, 862.124–892.172 | Regulation governing the product code. |
| `year_reclassified` | integer | year, 1982–2015 | Year the III→II reclassification took effect. |
| `date_proposed` | integer | year, 1980–2014 | Year the reclassification was proposed. |
| `Post-Amendment` | integer indicator | {0, 1} | 1 if the device type is post-1976-Amendments. |
| `FDA_own_accord` | float indicator | {0, 1} | 1 if FDA initiated the reclassification; 0 if it followed a petition or de novo request. |
| `Petition_DeNovo_Filing_Date` | string | date or `None`, 55% populated | Filing date of the petition / de novo request. |
| `Petition_DeNovo_Firm_Name` | string | firm name or `None`, 55% populated | Petitioner. |
| `De_Novo` | float indicator | constant `0` where populated | De novo flag. |
| `yr_invent_or_comm_avail` | string | a 4-digit year, `0`, or the literal `Too early for adverse events` | **Hand-entered** year the device type was invented or first commercially available. The two non-year values are exclusion markers, dropped before use. |
| `source` | string | free text, 84% populated | **Hand-entered** citation supporting `yr_invent_or_comm_avail` — a journal article with PMID, a patent, or a regulatory document. |
| `Search Phrase` | string | Dimensions query text | Patent-search phrase used for the product code. |
| `Reg_Change_List` | string | list of Federal Register citations, e.g. `[’47 FR 5817]` | Regulation-change events for the product code. |
| `Reg_Change_Text` | string | free text | Federal Register citation with date. |
| `Reg_Title` | string | free text, 65% populated | Title of the Federal Register rule. |
| `CPC_1`, `CPC_2`, `CPC_3` | string | CPC symbol, e.g. `A61K38/00`, 94% populated | Top three Cooperative Patent Classification codes for the product code's patents. |
| `CPC_Desc_1..3` | string | CPC scheme title text, 94% populated | Titles of the CPC hierarchy for the corresponding code. |
| `auto_year` | float | year, 1989–2015, 87% populated | Automated reclassification-year guess retained for comparison. |
| `auto_categorize` | float | all-missing | Unused. |
| `use_case` | string | `reclass_3_2` (29), `reclass_0_2` (1), `reclass_3_2/class_importance` (1) | Sample-construction tag. |
| `sample_size` | float | count, 0–84,492 | Number of patents retrieved for the product code. |

**Hand-coding rule as recorded in the package.** The author recorded, for each product code, the
earliest year at which the device type was either described in the scientific literature or
commercially available, together with the citation used, in the `source` column; rows where no such
year could be placed before the adverse-event data begin are marked `Too early for adverse events`
and dropped. The per-row citation in `source` is the auditable record of the search. A written
search protocol beyond this was not retained, and none is invented here.

## `data/raw/RegNum_Factorized_Synth.csv` (and its byte-identical copy `data/derived/RegNum_Factorized_Synth.csv`)

5,542 rows (5,541 distinct product codes) x 34 columns. An author-built regulation-number crosswalk:
FDA product-classification attributes, reclassification/de novo metadata, Federal Register change
history, and the top three CPC technology codes with their scheme titles. No shipped program writes
it. The per-column semantics are given in the "RegNum_Factorized_Synth.csv" section earlier in this
codebook; the additions here are the sources of the three column families that are not FDA fields:

- `Reg_Change_List`, `Reg_Change_Text`, `Reg_Title` — Federal Register citations, dates and rule
  titles for the regulation's change history, transcribed from the Federal Register.
- `CPC_1..3` — Cooperative Patent Classification symbols of the product code's patents, from the
  patent extract.
- `CPC_Desc_1..3` — the public CPC scheme's own hierarchy titles for those symbols (the CPC scheme
  is published jointly by the EPO and the USPTO and is freely available). The retrieval path for
  these three description columns is **not recorded anywhere in the package**; the strings are
  scheme titles, not patent text, and carry no restricted content.

The two copies are byte-identical (sha256 `2b4ab207…`); both ship because `09`/`11b`/`11d` read the
`data/raw/` path and `10c` reads the `data/derived/` path.

## `data/raw/innovation_year_*.csv` — GPT-4o device-introduction years

Four files, all produced by `code/12_invention_year_generation.py` (OpenAI GPT-4o, temperature 0).

| File | Rows x cols | Contents |
|---|---|---|
| `innovation_year_2_1_FDA_project.csv` | 293 x 2 | `PRODUCTCODE` (string); `years` (integer year, 1714–2002) — model-estimated year the device type was first introduced. |
| `innovation_year_3_2_FDA_project.csv` | 25 x 4 | `PRODUCTCODE`; `years` (integer year, 1953–1999) — **note**: in this downstream file the `years` column was replaced with the hand-coded values, so it is not the GPT series; `year_reclassified` (integer year, 1982–2015); `FDA_own_accord` (indicator {0,1}). |
| `innovation_year_all_other_FDA_project.csv` | 2,784 x 3 | `PRODUCTCODE`; `years` (integer year, 1550–2019); `source` (free text — the model's stated source for the year). Covers all 510(k) and PMA product codes outside the two reclassification cohorts. |
| `innovation_year_FDA_project.csv` | 25 x 7 | The original III→II output, and the only file that preserves the raw model responses: `DEVICENAME`, `DESCRIPTION_OF_REGNUM` (the query inputs); `yr_invent_or_comm_avail` (integer year — the **hand-coded** benchmark); `source` (the hand-coded citation); `query` (the exact user message sent); `response` (the **raw model reply string**, e.g. `['Year: 1978', 'source: …']`); `years` (integer year parsed from `response`). The manuscript's invention-year validation correlation is `corr(yr_invent_or_comm_avail, years)` on this file. |

## `data/raw/{2_1,3_2}_GPT_Price_Links.csv` — `gpt-5-mini` product-code → HCPCS/CPT concordance

301 x 15 and 36 x 15. Column definitions are in the table earlier in this codebook. Value domains:

- `row_index` (integer) — row position in the input device list; not a device identifier.
- `productcode` (string, 3 letters); `devicename`, `description_of_regnum`, `subpart_description`
  (strings, copied from the input); `regulationnumber` (float, 21 CFR section).
- `status` (string) — device regulatory status as supplied in the prompt.
- `decision` (string) — whether the model returned a link or a structured `no_link`.
- `mapping_quality` (string) — the model's own quality label for the mapping.
- `hcpcs_cpt` (string, 5-digit CPT; populated for 24% / 25% of rows) — the matched procedure code.
- `hcpcs_level_2` (string; populated for 4% / 0% of rows) — matched HCPCS Level II code.
- `procedure_desc` (string; 28% / 25%) — the model's **paraphrase** of the procedure. These are not
  verbatim AMA CPT descriptors: the same CPT code appears with different wordings across rows.
- `rationale` (string, always populated) — the model's justification.
- `alternates` (string; 14% / 11%) — other codes considered for the same device type.
- `confidence` (float, 0.35–0.92 / 0.41–0.90) — the model's self-reported confidence, unitless.

## `data/raw/pat_search_augment/*.csv` — patent-search phrases

Three files, 4 columns each (`DESCRIPTION_OF_REGNUM`, `DEVICENAME`, `PRODUCTCODE_x`,
`Search_Phrase`; all strings). Author-created inputs to the Dimensions patent extraction
(`gen_00_dimensions_patent_extraction.py`). `Search_Phrase` is a hand-curated query written for
product codes whose automatic device-name query proved too broad; it is missing where the automatic
phrase was used. Coverage: `revise_for_rescrape.csv` 31 rows, 11 hand-curated;
`revise_for_rescrape_already_had_2_1.csv` 24 rows, 14 hand-curated;
`revise_for_rescrape_3_2_latest.csv` 30 rows, 20 hand-curated.

## `data/raw/Good_2_1_Control_2_1.txt` — Federal Register rule text

853 lines / 86,629 bytes of plain text: a text extraction of the amendatory portion of the FDA
final rule "Medical Devices; Exemptions From Premarket Notification for Class I and Class II
Devices", 84 FR 71794 (30 December 2019), pages 71797–71819 of that issue as shown by the running
heads inside the file. It is unstructured text, not a table: the author read the affected 21 CFR
section numbers out of it to build the II→I control regulation list. Because the extraction is
page-based, a small amount of text from an unrelated rule printed in the same columns of the same
pages is interleaved; it contains no device regulation numbers and does not affect the extraction.

## `data/raw/Data_new_latest.png` — source asset for Appendix Figure D.2

A 1,097 x 598 RGBA PNG (233,314 bytes): the author's hand-drawn **data-catalog diagram**, exported
from draw.io. It is a diagram, not a dataset — it has no variables and no underlying data table. It
has no surviving editable source, so it is copied, not regenerated, into `output/figures/` by
`code/11g_descriptive_figures.py:74`. Its embedded draw.io source chunk has been decoded and
reviewed: it contains only data-source names and layout coordinates, no values. See
`certification/FIGURE_PROVENANCE.md` and `certification/NONTABULAR_DATA_AUTHORITY.csv`.

## `data/raw/manual_permno_corrections.csv` — hand-coded firm-name → PERMNO corrections (RESTRICTED, not shipped)

70 data rows x 7 columns. **Defined here for completeness only; the file is classified RESTRICTED
and is excluded from the public package** because its `permno` column holds licensed CRSP
identifiers drawn from the author's own WRDS extract.

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `contains` | string | lower-case substring | Manufacturer-name substring that triggers the correction. |
| `not_contains` | string | lower-case substring or empty | Substring that must be absent for the correction to apply. |
| `permno` | integer | CRSP PERMNO | Correct PERMNO for the matched manufacturer. |
| `stock_name` | string | — | Correct firm name. |
| `manual_stock` | indicator | {0, 1} | 1 if the row sets the firm name as well as the PERMNO. |
| `no_guard` | indicator | {0, 1} | 1 to bypass the default name guard. |
| `undo` | indicator | {0, 1} | 1 if the row removes a previously assigned PERMNO instead of setting one. |

Applied by `code/00_generate_data/gen_07_adverse_permno.py`.

## `data/raw/unique_{devices,firms,firms_in_PC}_thr_75.csv` — de-duplicated 510(k)/PMA registry rows

Three files with the same 9 columns; 107,501 / 14,092 / 68,515 rows. Produced by
`gen_01_main_panels.py` from the FDA 510(k) and PMA databases by fuzzy de-duplication at a 0.75
similarity threshold (hence the `_thr_75` suffix), then read back by `09_summary_stats.py` for the
device-count, firm-count and entrant statistics. They are **regenerated** on the from-raw route
(`synthetic_pipeline/fromraw_contract.py` step 1).

| Column | Type | Units / allowed values | Definition |
|---|---|---|---|
| `KNUMBER` | string | FDA 510(k) number, or empty for PMA rows | Submission identifier. |
| `PRODUCTCODE` | string | 3-letter FDA product code | Device type. |
| `APPLICANT` | string | — | Submitting firm name as filed. |
| `DEVICENAME` | string | — | Device trade/common name. |
| `COUNTRY_CODE` | string | ISO-like country code as filed | Applicant country. |
| `year` | integer | year | Year of the submission. |
| `DATERECEIVED` | string | date as filed | Date FDA received the submission. |
| `PMANUMBER` | string | FDA PMA number, or empty for 510(k) rows | Submission identifier for PMA rows. |
| `TRADENAME` | string | — | Trade name for PMA rows. |

The three differ only in the de-duplication unit: `unique_devices` keeps one row per distinct
device, `unique_firms` one per distinct firm, `unique_firms_in_PC` one per distinct firm within a
product code.

## `data/raw/adverse_event_panel_by_PC_full.csv` and `data/derived/adverse_event_panel_by_PC_full.csv`

Product-code x year MAUDE adverse-event panels, 119,219 rows each. The two copies are **not**
identical: the `data/raw/` copy has 48 columns and the `data/derived/` copy 53. Both carry
`PRODUCTCODE` (string), `year` (integer), `event_count` (integer count of MAUDE records in the
cell), the 40 reporter-disaggregated counts `{D,L,H,S,C,R,O,U,I,A}_{U,D,P,M}` (integer counts), and
aggregate outcome counts; the `data/derived/` copy additionally carries the aggregate columns
`C`, `O`, `U`, `I`, `A`, while the `data/raw/` copy carries only `D`, `H`, `L`, `S`, `R`. All
outcome letters and reporter suffixes are defined in "Adverse-event variable scheme" above.
`09_summary_stats.py` reads the `data/raw/` copy; the `data/derived/` copy is the panel regenerated
on the from-raw route (`fromraw_contract.py` step 1).

## `data/derived/Applicant_Device_data.csv` — applicant x device submission rows

196,676 rows x 7 columns: `APPLICANT`, `DATERECEIVED`, `DEVICENAME`, `KNUMBER`, `PMANUMBER`,
`PRODUCTCODE`, `year` — the same field meanings as the `unique_*_thr_75` table above, before
entity resolution. It is the input to the learning-by-doing clustering
(`gen_03_lbd.py`, `gen_03b_lbd_clusters.py`). The file is written with a UTF-8 BOM, so the first
column name reads `﻿APPLICANT` unless the reader is told `encoding="utf-8-sig"`.

## `data/derived/AD_data_applicant_df{,2}_oct22_24.csv` — entity-resolved applicant clusters

170,471 and 32,709 rows x 12 columns. `Applicant_Device_data.csv`'s columns plus
`DECISIONDATE_x` / `DECISIONDATE_y` (dates merged from the 510(k) and PMA registries), `cluster id`
(integer — the `pandas_dedupe` entity-resolution cluster the row was assigned to) and `confidence`
(float in [0,1] — the clustering confidence for that assignment). Written by
`gen_03b_lbd_clusters.py`; the `2` variant is the second (PMA-side) pass.

## `data/derived/All_Adverse_Event_Manufacturers_Deduped.csv` — de-duplicated MAUDE manufacturers

48,897 rows x 7 columns: `MDR_REPORT_KEY` (integer MAUDE report key), `MANUFACTURER_D_NAME`
(string, as filed in MAUDE), `group` / `clean_name` / `clean_name_group` (strings — normalization
stages of the firm name), `cluster id` (integer) and `confidence` (float in [0,1]) from the same
`pandas_dedupe` clustering. Written by `gen_07_adverse_permno.py`. The firm names and the report
keys are verbatim public-domain FDA MAUDE fields.

## `data/derived/Adv_Event_2020_2022.csv` — 2020–2022 adverse-event extension

7,119 rows x 13 columns: `PRODUCTCODE`, `year`, the aggregate outcome counts
`L, H, S, C, R, O, U, I, A, D` (integer counts, defined in the adverse-event scheme above) and
`event_count`. Built by `gen_06_adv_2020.py` from the `MAUDE_2020/` pull; used by
`11b_recall_analysis.py` for the post-sample extension.

## `data/derived/dedupe_settings*/` — frozen entity-resolution artifacts

Six files in three directories (`dedupe_settings/`, `dedupe_settings/adverse_events/`,
`dedupe_settings_applicant/`). Each directory holds a `dedupe_dataframe_learned_settings` (a binary
`pandas_dedupe` model: the learned blocking predicates and field weights) and a
`dedupe_dataframe_training.json` (the labelled record pairs used to train it). They are **model
artifacts, not data**: they contain field-comparison weights and the labelled name pairs, and are
reviewed byte-by-byte in `certification/NONTABULAR_DATA_AUTHORITY.csv`. They ship frozen because
`pandas_dedupe` active learning is interactive and not reproducible in a batch run; the pipeline
loads them instead of retraining.

## API-derived fixed inputs (JPE Policy 4.3)

Two shipped input families were produced by calls to a third-party language-model API. **Neither is
regenerated on any route** — not the synthetic route, not the from-raw route, not the provider
routes. The generating programs ship for transparency and both refuse to run unless an explicit
environment variable is set.

| | Invention years | Price-link concordance |
|---|---|---|
| Files | `data/raw/innovation_year_2_1_FDA_project.csv`, `data/raw/innovation_year_3_2_FDA_project.csv`, `data/raw/innovation_year_all_other_FDA_project.csv`, `data/raw/innovation_year_FDA_project.csv` | `data/raw/{2_1,3_2}_GPT_Price_Links.csv` |
| Program | `code/12_invention_year_generation.py` (guard: `RUN_GPT_INVENTION_YEARS`) | `code/12b_gpt_price_links_generation.py` (guard: `RUN_GPT_PRICE_LINKS`) |
| Provider / model | OpenAI, **`gpt-4o`** (`12_invention_year_generation.py:152, 261, 375`) | OpenAI, **`gpt-5-mini`** (`12b_gpt_price_links_generation.py:67`) |
| Sampling settings | `temperature=0`; 60 requests/minute | API defaults (no `temperature` or `top_p` is set at `12b:363`) |
| Prompts | Reproduced verbatim in the program (system instructions plus three or four few-shot examples, one prompt per cohort) | Reproduced verbatim in the program (`INSTRUCTIONS`, `12b:73`) |
| Date of the run | **Not recorded.** The only evidence in the package is the source-notebook name `OpenAI_Upwork.ipynb`, which carries no date. Shipped-file modification times (2026-02-18 to 2026-02-20) are re-staging dates, not generation dates. | **Not recorded.** The source-notebook name `Query_Prices_GPT_New_Price_Analysis_9_25_25.ipynb` (`12b:18`) indicates 25 September 2025; shipped-file modification times (2026-02-24) are re-staging dates. |
| Raw responses archived? | **Partly.** The 25 III→II raw replies ship in `innovation_year_FDA_project.csv` (`response` column). The 293 II→I and 2,784 all-other raw replies were not retained; only the parsed year (and, for the all-other file, the parsed `source` string) ship. | **No.** The program writes a JSONL of raw replies at run time (`12b:376`), but that file is not part of the deposit. |
| Why frozen | Model replies are not deterministic and the provider does not allow replay against a frozen snapshot, so byte-identical re-extraction is impossible. | Same. |

A third model-derived variable, the device-patent classification behind the "GPT-4o Identified
Devices" robustness column (`code/13_restricted_samples.py`), is carried inside the restricted
Dimensions file `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` and therefore ships in
neither route.
