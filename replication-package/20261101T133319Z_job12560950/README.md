# README for "Regulating the Innovators: Approval Costs and Innovation in Medical Technologies"

## Overview

**Paper.** Parker Rogers, "Regulating the Innovators: Approval Costs and Innovation in Medical
Technologies."

**Author.** Parker Rogers, Indiana University, Kelley School of Business. Contact: parkerrogers2@gmail.com.

**Package version.** 2026-10 (revision after the JPE compliance audit).

**What this package is.** It contains every program used to build the analysis data, estimate the
results, and draw every figure and table in the paper and its appendices; all of the public and
author-created data those programs read; a complete simulated replacement for the four restricted data
sources I am not allowed to redistribute; the reference outputs that simulated replacement produces;
the manuscript source and the program that compiles it; and the documentation and checking programs
described below.

**What this package does not contain.** It contains no MarketScan claims, no Dimensions patent records
or patent text, no CRSP/Compustat firm financials, no Nexis Uni exports, and no file derived from any of
them. Those four sources are licensed to me and cannot be redistributed. The analysis panels built from
them are excluded on the same ground and are rebuilt by the code at run time rather than shipped. Every
excluded file is listed by name, with its simulated counterpart, under "Confidential raw input files the
code reads" below.

**The three routes.** The *simulated-data route* runs all 36 pipeline steps end to end
on the simulated data that ships in `synthetic_pipeline/simulated_data/`, and must reproduce the 283 reference outputs in `output-simulated/`
byte-for-byte; this is the route a replicator without licensed data runs, and it checks that the code is
complete and deterministic, not that it reproduces the paper's numbers. The *real-data route* runs the
same code on the licensed inputs inside an authorized environment and compares against the manuscript's
own outputs, which ship in `output/`; it is the route that checks the published estimates, and only a
researcher who holds the licences can run it. That route starts from the derived analysis files, which
ship. The *real-data route from raw* rebuilds those derived files from the licensed raw extracts first and
then runs the same analysis on what it has rebuilt, so it needs every raw input rather than only the
derived panels; it reaches the same published numbers, and the files that differ are set out under
"Route 3 — the real-data route from raw".

**Expected effort.** Installing the environment takes under ten minutes. The simulated-data route takes
about nine hours of wall clock on the machine described under "Memory, runtime and storage"; the
real-data route takes about an hour and a quarter, and the real-data route from raw a little over two
hours. Allow at least 30 GB of free disk.

**Suggested citation of this package.**

> Rogers, Parker. 2026. "Replication package for: Regulating the Innovators: Approval Costs and
> Innovation in Medical Technologies." *Journal of Political Economy* Dataverse.
> (Package version 2026-10.)

**In a hurry?** The reproducibility check is "Route 1 — the simulated-data route" under
[Instructions to replicators](#instructions-to-replicators): install the Python environment, empty
`output/figures` and `output/tables`, run three commands, and compare with `output-simulated/`.

**Contents.**

1. Overview (this section)
2. Data Availability and Provenance Statements — the Statement about Rights, the licence, what is and is
   not public, every data source with its version and access cost, the complete list of confidential
   input files with their simulated counterparts, and the dataset list
3. Computational requirements — software, the Python environment, the reference container, R, LaTeX,
   controlled randomness, and memory/runtime/storage
4. Description of programs/code — the package layout, the 36-step pipeline, the simulation programs, and
   the checking programs
5. Instructions to replicators — all three routes, the comparison, and the scope of each check
6. List of tables and figures — every exhibit, its program and its output file, including the exhibits no
   program produces, and the in-text numbers
7. References — the data citations
8. Acknowledgements, preservation and contact

---

# Data Availability and Provenance Statements

## Statement about Rights

- [x] I certify that the author(s) of the manuscript have legitimate access to and permission to use the data used in this manuscript.
- [x] I certify that the author(s) of the manuscript have documented permission to redistribute/publish the data contained within this replication package. Appropriate permission are documented in the LICENSE.txt file.

The per-member evidence behind the second certification is
`certification/DEPOSITED_FILE_RIGHTS.csv`: one row for every file in the deposit, each naming the
concrete basis on which I may redistribute it (U.S. Government public domain, CC0, author-created,
third-party academic data published openly by its authors with a citation request, or a third-party
model licence). `certification/PUBLIC_SOURCE_PROVENANCE.csv` carries the
per-file provenance for the public inputs, and `certification/COMMITTED_PARAMETER_RIGHTS.csv` carries
the rights determination for the two restricted-derived simulator parameter files.
`synthetic_pipeline/_synthetic_source_internal/simulation_parameters.json` and
`simulation_schema_contract.json` are author-created abstractions of the restricted corpus (rounded
cardinalities, rounded dimensions and schema, smoothed distribution parameters, and no restricted
record or value), and their redistribution rests on my own representation to that effect — not on a
provider's permission and not on an independently verified legal opinion — recorded in
`certification/COMMITTED_PARAMETER_RIGHTS.csv`, evidenced per file in
`certification/rights_evidence/*.rights.json`, reviewed in
`certification/COMMITTED_PARAMETER_RIGHTS_REVIEW.md`, and stated in `LICENSE.txt` section 2a.

## License for Data and Code

The package is released under the terms in `LICENSE.txt`, which covers my own code and documentation,
the simulated data in `synthetic_pipeline/simulated_data/`, the reference outputs in
`output-simulated/`, the public data I redistribute, and the third-party sentence-transformer model in
`models/`. Third-party components keep their own terms, which `LICENSE.txt` reproduces: the MiniLM model
is Apache-2.0 (`models/all-MiniLM-L6-v2/MODEL_CARD.md`), GRID is CC0, the FDA databases are U.S.
Government works in the public domain, and the KPSS and KPST patent datasets are redistributed on the
basis that their authors publish them openly and ask that the accompanying paper be cited.

## Summary of Availability

- [ ] All data **are** publicly available.
- [x] Some data **cannot be made** publicly available.
- [ ] **No data can be made** publicly available.

- [x] Confidential data used in this paper and not provided as part of the public replication package will be preserved for **five** years after publication, in accordance with journal policies.

Four data sources cannot be made public: MarketScan, Dimensions, WRDS/CRSP-Compustat and Nexis Uni. A
fully simulated counterpart of each ships in this package, so every program runs without them. All other
inputs — the FDA 510(k), PMA, product-classification, MAUDE and recall databases, GRID, the KPSS and
KPST patent datasets, the CPI deflator series, the two Federal Register documents I use as data, and
every file I created myself — ship in `data/`.

**One of those four cannot be re-obtained even with a licence, and I want to be explicit about it.**
Dimensions is a live, versioned database, and my patent extract is a 2020 snapshot of it. The provider
does not allow querying a prior API version or a historical database snapshot, and the full-text
retrieval layer that selects patents for a search phrase has been revised repeatedly since my pull —
including corrections to how phrase queries match patent text, some of which I reported to Digital
Science myself and which they fixed. I have no visibility into the full revision history, and others
have very likely been found and corrected in the years since. So a replicator with a current Dimensions
licence, running my extraction program with my search phrases, will not obtain the patent set this paper
was built on, and the patent-based estimates from such a re-pull would differ. This is a property of the
live database, not of my code. It is why the 2020 extract is treated as a frozen, hash-pinned input
rather than something the pipeline rebuilds, and it is set out in full under *Dimensions patent records*
below and in the header of `code/00_generate_data/gen_00_dimensions_patent_extraction.py`.

## Details on each Data Source

### Public sources, included in the package

**Access restrictions (JPE Data and Code Policy).** None of the public sources below requires
registration, a login, an application or a data-use agreement: each is a direct download or an open
API, and each row records the cost and the time to obtain it. The two openFDA endpoints accept an
optional free API key that raises rate limits; this package neither uses nor needs one at the volumes
it downloads. The restricted sources, whose access requirements are substantial, are in the next
subsection.

**U.S. FDA / CDRH, 510(k) Premarket Notification Database.** Downloadable files at
<https://www.fda.gov/medical-devices/510k-clearances/downloadable-510k-files> (record search at
<https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm>). Public domain. Format: pipe-delimited
text saved as `.csv`. File: `data/raw/501k_all.csv`. Downloaded 2020-02-07. Free, no registration, minutes
to obtain.

**U.S. FDA / CDRH, Premarket Approval (PMA) Database.** Downloadable files from the FDA Medical Device
Databases page above (record search at
<https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm>; API at
<https://open.fda.gov/apis/device/pma/>). Public domain. Format: delimited text. File:
`data/raw/all_pma_approvals.txt`. Downloaded 2019-11-04. Free, minutes.

**U.S. FDA / CDRH, Product Classification Database.** Download page:
<https://www.fda.gov/medical-devices/classify-your-medical-device/download-product-code-classification-files>.
Public domain. Format: delimited text. File: `data/raw/foiclass.txt`. Downloaded 2019-11-04. Free, minutes.

**U.S. FDA / CDRH, MAUDE (Manufacturer and User Facility Device Experience).** MDR data files at
<https://www.fda.gov/medical-devices/medical-device-reporting-mdr-how-report-medical-device-problems/mdr-data-files>.
Public domain. Format: delimited text. Files: `data/raw/MAUDE/` (original pull, 2019–2020) and
`data/raw/MAUDE_2020/` (refreshed pull, 2023, covering events through 2022) — the masterevent, patient,
device-problem, problem-code-description and device-data tables. These are the two largest components of
the deposit (about 13 GB together). Free; the download itself takes hours on a normal connection.

**U.S. FDA / CDRH, Medical Device Recall Database (openFDA export).**
<https://www.fda.gov/medical-devices/medical-device-recalls>; data via
<https://open.fda.gov/apis/device/recall/>. Public domain. Format: JSON. File:
`data/raw/device-recall-0001-of-0001-2.json`. Downloaded 2020. Free, minutes.

**Kogan, Papanikolaou, Seru and Stoffman (KPSS) patent values, public extended release.** From the
authors' repository,
<https://github.com/KPSS2017/Technological-Innovation-Resource-Allocation-and-Growth-Extended-Data>.
Format: `.csv`. File: `data/raw/KPSS_2019_public.csv`. Downloaded 2020-08-10. Free, minutes. The
repository carries a citation request and no licence file, so no broader licence is claimed; this package
makes the requested citation. Note that `KPSS_2019_public.csv` contains a `permno` column: those PERMNOs
are part of KPSS's own public release — the variable appears in their repository's published variable
table — and are not an extract from my WRDS licence. That is why this file ships while my own
CRSP-derived crosswalk `data/raw/manual_permno_corrections.csv` (70 rows), whose PERMNOs do come from a
licensed WRDS extract, is excluded.

**Kelly, Papanikolaou, Seru and Taddy (KPST) breakthrough-patent measures.** Extended data at
<https://github.com/KPSS2017/Measuring-Technological-Innovation-Over-the-Long-Run-Extended-Data>; the
replication project is openICPSR 119043 (<https://www.openicpsr.org/openicpsr/project/119043>). Format:
`.csv`. File: `data/raw/KPST_Breakthrough.csv`. Downloaded 2023-09-12. Free, minutes. Same basis as KPSS:
an open release with a citation request and no licence file.

**Digital Science, Global Research Identifier Database (GRID), release 2019-10-06.** <https://www.grid.ac/>.
CC0. Format: `.csv`. File: `data/raw/GRID/types.csv`. Free, minutes.

**Annual price deflator, 1834–2019.** File: `data/raw/CPI_deflator.csv`. This series is tied to the KPSS
patent-value data rather than to an independent BLS download: the pipeline computes the deflator as
`xi_real / xi_nominal` from KPSS (`code/00_generate_data/gen_01_main_panels.py`), and the file's 2019
value agrees with the KPSS-implied 2019 deflator to eight significant figures -- the file carries
0.3891444268900899 and `config.CPI_DEFLATOR_2019` is 0.3891444146542998, a relative difference of
3.1e-8 that moves no reported figure -- and
tracks the KPSS real/nominal ratio within about 10 percent year by year. It does **not** match BLS CPI-U
(the 2000→2019 factor here is about 1.38 against CPI-U's 1.48). Cite it through the KPSS source.

**Two Federal Register documents used as data.** Both are U.S. Government works in the public domain and
are cited in full under "References" below. 84 FR 71794 (2019) is the source of
`data/raw/Good_2_1_Control_2_1.txt`, a text extraction of the amendatory portion of the rule; 82 FR 31976
(2017) is the basis of `data/raw/Class2_Exemptions_2017_Grennan.csv` (244 product codes across 138
regulation numbers).

**Download dates.** They are author-recalled and accurate to the month. The shipped copies were
re-staged in February 2026, so file modification times do **not** corroborate them; where a download date
was not recorded, `certification/PUBLIC_SOURCE_PROVENANCE.csv` says so explicitly, per file.

### Author-created inputs, included in the package

These files have no external source. `certification/PUBLIC_SOURCE_PROVENANCE.csv` records how each was
built and what evidence dates it; `CODEBOOK.md` defines their variables.

- `data/raw/3_2_begin_final_revisions.csv` (31 rows) — Class III→II reclassification metadata: event
  dates, whether the event was petitioned or FDA-initiated, and author-collected invention years with one
  literature citation per row in the `source` column.
- `data/raw/RegNum_Factorized_Synth.csv` (5,542 rows) and its byte-identical copy in `data/derived/` — a
  regulation-number-to-product-code crosswalk I built from the FDA classification database, the Federal
  Register, and the public CPC scheme titles.
- `data/raw/hand_coded_intuitive_3_2.csv` (12 product codes) — my domain-knowledge selection of
  intuitively similar control device types for the Class III→II analysis, read by
  `code/00_generate_data/gen_01_main_panels.py`.
- `data/raw/spinal_entrant_audit.csv` (20 rows) — the hand audit of new spinal-implant entrants behind
  the regulatory-proficiency footnote. The sample is the first-time 510(k) applicants under product code
  MAX (intervertebral body fusion devices), submissions from 2007 onward, taken from
  `data/raw/unique_firms_thr_75.csv`; the applicant name, submission date and product code are the public
  FDA 510(k) fields, and `US_based`, `subsidiary`, `acquired` and `founded` are attributes I entered by
  hand from public web searches, left blank where the search settled nothing. Read by
  `code/15_intext_derived_numbers.py`, which tabulates the six quoted statistics rather than letting them
  be typed.
- `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv` — an FDA-product-code-to-HCPCS/CPT crosswalk produced for me by
  a certified medical coder; deliverable received 2024-01-17. It is public and ships, and the real-data
  route reads it as it is. The simulated-data route replaces it with a fake-keyed twin
  (`synthetic_price_links/FDA_HCPCS_Xwalk_Moazzam.csv`), because it carries real HCPCS codes and the
  simulated claims are generated over a synthetic procedure-code domain; without the twin the expert
  robustness sample in step 14 would have almost nothing to estimate on.
- `data/raw/Class2_Exemptions_2017_Grennan.csv` — built from 82 FR 31976 plus the FDA classification and
  510(k) databases (the regulation numbers are left-padded, product-code descriptions merged from
  `foiclass.txt`, and 510(k)-submission history flagged). "Grennan" in the filename is a legacy label
  only; I created the file. Created 2021-10-11. Used by `code/11b_recall_analysis.py`.
- `data/raw/Data_new_latest.png` — the data-catalog diagram I drew, reproduced as Appendix Figure D.2 and
  copied (not regenerated) into `output/figures/` by step 28.
- `data/raw/pat_search_augment/*.csv` (3 files) — patent-search augmentation lists I assembled.
- `data/raw/innovation_year_*.csv` and `data/raw/{2_1,3_2}_GPT_Price_Links.csv` — API-derived fixed
  inputs; see "API-derived fixed inputs" below.
- `data/raw/unique_devices_thr_75.csv`, `unique_firms_in_PC_thr_75.csv`, `unique_firms_thr_75.csv`, and
  `data/raw/adverse_event_panel_by_PC_full.csv` — product-code-level aggregates I computed from the
  public FDA registries and MAUDE and ship directly, so that the summary-statistics step does not have to
  rebuild them.

### Restricted sources, excluded from the package

Access cost and time below are approximate and should be confirmed against current provider terms. All
four sources are excluded under exemptions; the exemption status of each is stated in its row.

**MarketScan claims (Merative, formerly IBM Watson Health), obtained through the NBER data enclave.**

| | |
|---|---|
| Used for | Price, utilization, and utilization-normalized safety analyses |
| Provider URL | <https://www.merative.com/real-world-evidence>; access route <https://www.nber.org/research/data> |
| Version / vintage | Commercial Claims and Encounters Database; my extract spans claim years **1996–2013**. No provider release label is recorded. Evidence: the year loop `range(1996, 2014)` in the recovered extraction program `code/00_generate_data/gen_00b_marketscan_extraction.py`, and the coverage of the extract itself. |
| My date of access | **Not recorded.** |
| Exemption status | No new exemption requested; excluded under the original restricted-data disclosure. The extraction program is deposited (`gen_00b_marketscan_extraction.py`), so no policy 2.1 exemption is needed for it; the two-significant-figure rounded row counts published below require the Data Editor's written acceptance. |
| Monetary cost | Free to researchers at NBER-affiliated institutions through the NBER enclave; otherwise a commercial licence, typically tens of thousands of USD per year |
| Time cost | Roughly 2–6 weeks for the NBER application, data-use agreement and onboarding |

The program that reads the raw MarketScan outpatient claims tables and aggregates them into
`data/derived/outpatient_combined_censored.csv` is `code/00_generate_data/gen_00b_marketscan_extraction.py`.
It is the original program I ran at NBER, recovered by NBER IT from my former account there and released
to me through their output-review process; the deposited file is that program, with only a module
docstring and three block headers added. It is not invoked by `run_all.py` — the raw claims never leave
NBER — but a researcher with MarketScan access can run it unchanged there, and NBER IT has offered to
execute it on request. **The name and address of the NBER contact, together with the institutional
data-core address, are supplied to the Data Editor directly on request rather than published in this
package, so that no individual's contact details are redistributed with the deposit.**

**Dimensions patent records, metadata and full text (Digital Science & Research Solutions).**

| | |
|---|---|
| Used for | Patent outcomes, patent values, citations, safety text, product variety, restricted patent samples, breakthrough-patent robustness |
| Provider URL | <https://www.dimensions.ai/> |
| Version / vintage | Dimensions DSL API **v1.24, week of 2020-05-11**, with the query bound by `date_inserted <= "2020-05-18"`. Evidence: the script header of `code/00_generate_data/gen_00_dimensions_patent_extraction.py:14,43`. The later device-patent classification file `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` came from a separate pull whose date is **not recorded**. |
| My date of access | Main patent pull: the week of **2020-05-11**. Device-patent classification file: **not recorded**. |
| Exemption status | Excluded under a third-party licence (Indiana University institutional subscription). The provider's reply permits the documented confidential review of Dimensions-derived files; the reply is retained outside the public deposit. |
| Monetary cost | Free for some non-commercial research through the Dimensions Analytics API programme, but full patent-text and metadata extraction generally requires an institutional subscription (commercial pricing on request) |
| Time cost | Days to a few weeks, depending on the institutional agreement |

The 2020 extract cannot be re-pulled identically, and the reason is worth stating precisely because it
bounds what any replicator can check. Dimensions is a live database: the corpus grows, and the full-text
retrieval layer that decides which patents a search phrase returns has itself been revised repeatedly
since v1.24. Those revisions include **corrections** — defects in how phrase queries matched patent text,
some of which I identified and reported to Digital Science and which they then fixed. I have no visibility
into the provider's full revision history, and I assume others have been found and corrected by other
users over the years. The provider does not allow pinning a DSL version or querying a historical
snapshot, so there is no way to reconstruct the retrieval behaviour my pull saw.

`gen_00_dimensions_patent_extraction.py` measures the consequence against the shipped extract. Product
codes with a hand-curated search phrase reproduce at roughly 99–100 percent recall: a specific phrase
selects the same specific patents under either the old relevance ranking or the current stricter phrase
match. Product codes with a generic device phrase do not reproduce at all, because the 2020 query behaved
as a broad relevance-ranked full-text search over title and abstract and today's does not; neither a
stricter phrase nor an explicit OR of the terms recovers that set. Hand-curated phrases cover 20 of the 30
III→II treated product codes and 11 of 31 plus 14 of 24 on the II→I side, so the non-reproducing part is
not a corner case.

**What follows for the results.** A replicator who rebuilds the patent inputs from a fresh pull will have
a materially different patent panel for the generic-phrase product codes, and the patent outcomes — and
therefore the patent-based estimates — will not be numerically identical to the published ones. I cannot
bound that difference, because doing so would require re-running the whole pipeline on a fresh extract
under licence. What I can do, and have done, is make the archived 2020 extract the authoritative input,
pin every derived input built from it by SHA-256 (`certification/EXPECTED_CONFIDENTIAL_REAL_INPUT_HASHES.csv`,
the real-input closure the confidential lane verifies), ship the exact search phrases so the selection rule is inspectable (`data/raw/pat_search_augment/`), ship the
extraction program itself for transparency rather than as a turnkey re-run, and offer the extract for
confidential verification to the Data Editor or to a replicator holding a Dimensions licence
(`RESTRICTED_DATA_VERIFICATION_MEMO.md`). Verifying this paper's patent results means verifying that my
pipeline reproduces them **from that archived extract**, which it does, byte for byte; it cannot mean
re-deriving the extract.

**WRDS / CRSP-Compustat firm financials.**

| | |
|---|---|
| Used for | Firm assets, public-firm matching, firm-size heterogeneity |
| Provider URL | <https://wrds-www.wharton.upenn.edu/> (CRSP: University of Chicago Booth; Compustat: S&P Global Market Intelligence) |
| Version / vintage | CRSP/Compustat Merged, Fundamentals Annual; my extract spans **fiscal years 1973–2019** (`datadate` 1974-01-31 to 2019-12-31). No provider vintage label is recorded. Evidence: the extract itself, recorded at `WRDS_EXTRACTION_ROADMAP.md:36-37`. |
| My date of access | **Not recorded.** |
| Exemption status | Excluded under a third-party licence (institutional WRDS subscription); verification runs in the licensed environment. |
| Monetary cost | Institutional WRDS subscription; annual fees vary widely, commonly thousands to tens of thousands USD per year |
| Time cost | Same-day to about one week once an institutional WRDS account exists |

`WRDS_EXTRACTION_ROADMAP.md` gives the exact WRDS web-form settings (`consol=C`, `indfmt=INDL`,
`datafmt=STD`, `popsrc=D`, link types `LC` and `LU`) and the exact column list, so a licensed user can
reproduce my extract.

**Nexis Uni (LexisNexis) legal-search exports.**

| | |
|---|---|
| Used for | Liability and legal-mechanism analyses (Appendix Figure D.9) |
| Provider URL | <https://www.lexisnexis.com/en-us/professional/academic/nexis-uni.page> |
| Version / vintage | Nexis Uni **Cases** content type; exports span **2023-07-25 to 2024-08-27**. Evidence: the internal workbook timestamps of the `.xlsx` exports, recorded at `NEXIS_SEARCH_METHODOLOGY.md:47-57`. |
| My date(s) of access | Tort and preemption searches **2023-07-25/26**, with three later files **2023-08-22**, **2023-08-23** and **2023-11-06**; bankruptcy searches **2024-08-27**. |
| Exemption status | **Exemption granted by the handling editor.** |
| Monetary cost | Commercial legal-database subscription; pricing is account-specific |
| Time cost | Days to weeks; some exports may be restricted by vendor redistribution terms |

`NEXIS_SEARCH_METHODOLOGY.md` reproduces every search: each export's filename *is* the literal query, and
the file gives the export settings and a per-file expected hit count.

### Where an authorized researcher places the restricted files

An authorized researcher who obtains a source places the files at exactly these paths. MarketScan row
counts are the approximations — two significant figures, set one rounding step above the nearest two-significant-figure value, so the real extract is smaller by half a step to one and a half steps — published in
`synthetic_pipeline/_synthetic_source_internal/simulation_schema_contract.json`; exact restricted extract
sizes are not published, and a single real record moves a published count by at most one step.

**MarketScan** — supply the first file (the output of `gen_00b_marketscan_extraction.py`); the last two
are produced from it by step 2/37.

| Destination | Columns | Rows (approximation) |
|---|---|---|
| `data/derived/outpatient_combined_censored.csv` | 9: `proc1, year, coins, copay, netpay, qty, pay, proc_count, enrolid_count` | ~190,000 |
| `data/derived/constrained_adv_event_new_sept25.csv` | 16 (see the schema contract) | ~16,000 |
| `data/derived/constrained_adv_event_new_sept25_3_2.csv` | 17 (see the schema contract) | ~280 |

**Dimensions** — destinations and their column sets:

| Destination | Columns |
|---|---|
| `data/raw/all_PC_pats.csv`, `data/raw/expanded_2_1_pats.csv`, `data/raw/expanded_3_2_pats.csv`, `data/raw/missed_2_1_pats.csv` | `id, year, PRODUCTCODE, filing_status, times_cited, title` |
| `data/raw/FDA_pats_original_firmname.csv` | `id, original_assignee_names, original_assignees, inventor_names` |
| `data/raw/all_pats_wtitlesCPC.csv` | `PRODUCTCODE, GRID, orig_assignee_solo, original_assignee_names, original_assignees, id, inventor_names, patents, year, type`, plus the eight GRID assignee-type indicator columns |
| `data/raw/FDA_patents_text.csv` | `id, input` (patent title plus abstract text) |
| `data/raw/Applicant_Cites_Only.csv` | `USID, PRODUCTCODE, times_cited` |
| `data/raw/PC_by_year_cites_ApplicantOnly.csv`, `data/raw/PC_by_year_diff_ind_appl_only.csv` | `year, PRODUCTCODE, times_cited` |
| `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` | patent-level device classification; 13 leading columns beginning `patent_id, patent_abstract, patent_type, patent_date, patent_title` |

**WRDS / CRSP-Compustat**:

| Destination | Columns | Expected shape |
|---|---|---|
| `data/raw/compustat_firm_data.csv` | 18: `GVKEY, LPERMNO, datadate, fyear, indfmt, consol, popsrc, datafmt, conm, curcd, act, at, bkvlps, csho, dltt, costat, prcc_c, prcc_f` | 279,347 firm-year records across 47 fiscal years (1973–2019) |
| `data/raw/CRSPDirectory.csv` | firm name and PERMNO, saved as `NAME OF FIRM` and `PERM NO` | one row per firm in the CCM company universe |
| `data/raw/AllPublicCompanies.csv` | `conml`, `LPERMNO` | one row per public company in the same CCM pull |

The last two are read only by `code/00_generate_data/gen_06b_permno_universe.py`, which is gated behind
`RUN_PERMNO_UNIVERSE_BUILD=1` and runs on neither route. Query 2 of `WRDS_EXTRACTION_ROADMAP.md` is the
only route to them; I cannot supply them.

**Nexis Uni** — the tort and preemption exports go in `data/raw/Liability/` and the bankruptcy exports in
`data/raw/Liability/medtech/`, with a lowercase `.xlsx` extension. Every tort and preemption Results-list
export carries the seven columns `CASE NAME, CITE, SUMMARY, JURISDICTION, COURT, DATE DECIDED, YEAR`; the
fourteen bankruptcy exports under `medtech/` carry the 26 columns of the Nexis company-news export
(the simulated counterparts show the exact headers).

### Analysis data (JPE Data Policy 1.3)

The real analysis panels are excluded from the deposit. `data/derived/Full_sample.csv` is not shipped in
any form: shipping it reduced to a public column subset was rejected, because column-stripping a master
panel built from mixed restricted sources is not sanitization — row membership, ordering and missingness
remain disclosure surfaces. It is instead created at run time by the pipeline, from simulated inputs on
the simulated-data route and from the real inputs in an authorized route. The matched, intuitive,
later-treated and spillover panels (`matched_sample_*`, `intuitive_*`, `later_treated_*`, `spillovers_*`,
`data_2_1_*.parquet`), the patent-level files (`all_patents_w_xi_oct22_24.csv`, `safety_vars_allpats*`),
the firm-size panel (`Adverse_fsize_ready_all4_oct22_24.csv`) and the MarketScan-constrained panels
(`constrained_adv_event_*`) are excluded on the same
restricted-lineage ground. Fully simulated counterparts of all of them ship in
`synthetic_pipeline/simulated_data/`, so the analysis runs end to end without any restricted byte.

### Confidential raw input files the code reads

The table below lists every restricted file that a program in this package reads, grouped by source, with
the pipeline step that reads it and the simulated file that takes its place. It is generated from
`RESTRICTED_FILE_INVENTORY.csv` (the classification of every input) and
`certification/MATERIALIZE_DESTINATIONS.tsv` (the simulated-file-to-destination map that
`synthetic_pipeline/materialize_simulation.py` executes). Step numbers refer to the pipeline table under
"Description of programs/code".

<!-- BEGIN CONFIDENTIAL-INPUT TABLE -->
**MarketScan** — 3 files

| File the code reads | Kind | Read at | Simulated counterpart under `synthetic_pipeline/simulated_data/` |
|---|---|---|---|
| `data/derived/constrained_adv_event_new_sept25.csv` | derived | step 2, 13, 37 | `synthetic_marketscan/constrained_adv_event_new_sept25.csv` |
| `data/derived/constrained_adv_event_new_sept25_3_2.csv` | derived | step 2, 37 | `synthetic_marketscan/constrained_adv_event_new_sept25_3_2.csv` |
| `data/derived/outpatient_combined_censored.csv` | derived | step 2, 14, 20, 37 | `synthetic_marketscan/outpatient_combined_censored.csv` |

**Dimensions** — 26 files

| File the code reads | Kind | Read at | Simulated counterpart under `synthetic_pipeline/simulated_data/` |
|---|---|---|---|
| `data/derived/lda_2to1.model` | derived | step 22 | none — note (b) |
| `data/derived/lda_3to2.model` | derived | step 22 | none — note (b) |
| `data/derived/lda_bigram_2to1.model` | derived | companion file of the step-22 LDA models | none — note (b) |
| `data/derived/lda_bigram_3to2.model` | derived | companion file of the step-22 LDA models | none — note (b) |
| `data/derived/lda_dictionary_2to1.dict` | derived | companion file of the step-22 LDA models | none — note (b) |
| `data/derived/lda_dictionary_3to2.dict` | derived | companion file of the step-22 LDA models | none — note (b) |
| `data/derived/lda_trigram_2to1.model` | derived | companion file of the step-22 LDA models | none — note (b) |
| `data/derived/lda_trigram_3to2.model` | derived | companion file of the step-22 LDA models | none — note (b) |
| `data/derived/safety_tagged_patents.csv` | derived | step 17 | `synthetic_patents/safety_tagged_patents.csv` |
| `data/derived/safety_vars_allpats.csv` | derived | step 1, 15, 16, 18 | `synthetic_patents/safety_vars_allpats.csv` |
| `data/derived/safety_vars_allpats_updated_v2.csv` | derived | step 16 | `synthetic_patents/safety_vars_allpats_updated_v2.csv` |
| `data/derived/safety_vars_allpats_v2.csv` | derived | step 16 | `synthetic_patents/safety_vars_allpats_v2.csv` |
| `data/derived/word2vec_patent_corpus.model` | derived | step 16 | none — note (b) |
| `data/derived/word2vec_patent_corpus.model.syn1neg.npy` | derived | companion file of the step-16 Word2Vec model | none — note (b) |
| `data/derived/word2vec_patent_corpus.model.wv.vectors.npy` | derived | companion file of the step-16 Word2Vec model | none — note (b) |
| `data/raw/Applicant_Cites_Only.csv` | raw | step 20 | `synthetic_patents/Applicant_Cites_Only.csv` |
| `data/raw/FDA_patents_text.csv` | raw | step 1, 16, 17; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/FDA_patents_text.csv` |
| `data/raw/FDA_pats_original_firmname.csv` | raw | step 1; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/FDA_pats_original_firmname.csv` |
| `data/raw/PC_by_year_cites_ApplicantOnly.csv` | raw | step 1 | `synthetic_patents/PC_by_year_cites_ApplicantOnly.csv` |
| `data/raw/PC_by_year_diff_ind_appl_only.csv` | raw | step 1 | `synthetic_patents/PC_by_year_diff_ind_appl_only.csv` |
| `data/raw/all_PC_pats.csv` | raw | step 1; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/all_PC_pats.csv` |
| `data/raw/all_pats_wtitlesCPC.csv` | raw | step 1, 29; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/all_pats_wtitlesCPC.csv` |
| `data/raw/expanded_2_1_pats.csv` | raw | step 1; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/expanded_2_1_pats.csv` |
| `data/raw/expanded_3_2_pats.csv` | raw | step 1; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/expanded_3_2_pats.csv` |
| `data/raw/missed_2_1_pats.csv` | raw | step 1; `code/00_generate_data/gen_00_dimensions_patent_extraction.py` | `synthetic_patents/missed_2_1_pats.csv` |
| `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` | raw | step 22, 29; `code/modules/match_mahal.py` | `synthetic_patents/new_patent_analysis/all_device_patents_w_pc.csv` |

**Dimensions and WRDS/CRSP-Compustat combined** — 24 files

| File the code reads | Kind | Read at | Simulated counterpart under `synthetic_pipeline/simulated_data/` |
|---|---|---|---|
| `data/derived/Full_sample.csv` | derived | step 1, 5, 9, 11, 20, 23, 25, 26, 29, 32, 35; `code/modules/match_mahal.py` | `synthetic_dimensions_wrds/Full_sample.csv` |
| `data/derived/all_patents_w_xi_oct22_24.csv` | derived | step 1, 15, 16, 17, 18, 20, 22, 29, 30, 34; `code/00_generate_data/gen_06b_permno_universe.py` | `synthetic_dimensions_wrds/all_patents_w_xi_oct22_24.csv` |
| `data/derived/data_2_1_full.parquet` | derived | step 5 | `synthetic_dimensions_wrds/data_2_1_full.parquet` |
| `data/derived/data_2_1_intuitive.parquet` | derived | step 5 | `synthetic_dimensions_wrds/data_2_1_intuitive.parquet` |
| `data/derived/data_2_1_latertreat.parquet` | derived | step 5 | `synthetic_dimensions_wrds/data_2_1_latertreat.parquet` |
| `data/derived/data_2_1_spillovers.parquet` | derived | step 5 | `synthetic_dimensions_wrds/data_2_1_spillovers.parquet` |
| `data/derived/frequency_df_2to1_variety.csv` | derived | step 22 | `synthetic_dimensions_wrds/frequency_df_2to1_variety.csv` |
| `data/derived/frequency_df_3to2_variety.csv` | derived | step 22 | `synthetic_dimensions_wrds/frequency_df_3to2_variety.csv` |
| `data/derived/intuitive_2_1_oct22_24.csv` | derived | step 1, 5, 23 | `synthetic_dimensions_wrds/intuitive_2_1_oct22_24.csv` |
| `data/derived/intuitive_3_2_oct22_24_similarity.csv` | derived | step 1 | `synthetic_dimensions_wrds/intuitive_3_2_oct22_24_similarity.csv` |
| `data/derived/intuitive_spillovers_3_2_oct22_24.csv` | derived | step 1 | `synthetic_dimensions_wrds/intuitive_spillovers_3_2_oct22_24.csv` |
| `data/derived/later_treated_2_1_oct22_24.csv` | derived | step 1, 5, 26 | `synthetic_dimensions_wrds/later_treated_2_1_oct22_24.csv` |
| `data/derived/later_treated_3_2_oct22_24.csv` | derived | step 1 | `synthetic_dimensions_wrds/later_treated_3_2_oct22_24.csv` |
| `data/derived/matched_pairs_intuitive_2_1.csv` | derived | step 1 | `synthetic_dimensions_wrds/matched_pairs_intuitive_2_1.csv` |
| `data/derived/matched_sample_2_1_onepat.csv` | derived | step 2, 13, 14, 15, 16, 17, 18, 23, 27, 33, 37; `code/12b_gpt_price_links_generation.py` | none — note (b) |
| `data/derived/matched_sample_2_1_onepat_innovation.csv` | derived | step 13, 14, 18, 22, 34 | none — note (b) |
| `data/derived/matched_sample_2_1_onepat_innovation_quality.csv` | derived | inventoried by `code/audit_pipeline.py` | none — note (b) |
| `data/derived/matched_sample_3_2_onepat.csv` | derived | step 2, 13, 14, 15, 16, 17, 25, 27, 37; `code/12b_gpt_price_links_generation.py` | none — note (b) |
| `data/derived/matched_sample_3_2_onepat_innovation.csv` | derived | step 13, 14, 18, 19, 22, 34 | none — note (b) |
| `data/derived/matched_sample_3_2_onepat_innovation_petitioned.csv` | derived | step 25 | none — note (b) |
| `data/derived/matched_sample_3_2_onepat_innovation_quality.csv` | derived | step 13 | none — note (b) |
| `data/derived/safety_did_analysis.csv` | derived | step 13, 15 | `synthetic_dimensions_wrds/safety_did_analysis.csv` |
| `data/derived/safety_did_analysis_3_2.csv` | derived | step 13, 15 | `synthetic_dimensions_wrds/safety_did_analysis_3_2.csv` |
| `data/derived/spillovers_2_1_oct22_24.csv` | derived | step 1, 5 | `synthetic_dimensions_wrds/spillovers_2_1_oct22_24.csv` |

**WRDS/CRSP-Compustat** — 8 files

| File the code reads | Kind | Read at | Simulated counterpart under `synthetic_pipeline/simulated_data/` |
|---|---|---|---|
| `data/derived/Adverse_fsize_ready_all4_oct22_24.csv` | derived | step 6, 15, 16, 17, 18, 20 | `synthetic_dimensions_wrds/Adverse_fsize_ready_all4_oct22_24.csv` |
| `data/derived/all_adv_events_w_permno5.csv` | derived | step 6, 8 | none — note (b) |
| `data/raw/AllPublicCompanies.csv` | raw | `code/00_generate_data/gen_06b_permno_universe.py` | none — note (b) |
| `data/raw/CRSPDirectory.csv` | raw | `code/00_generate_data/gen_06b_permno_universe.py` | none — note (b) |
| `data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv` | derived | step 8; `code/00_generate_data/gen_06b_permno_universe.py` | `synthetic_maude_linkage/all_permnos_fname_adverse_events_oct22_24.csv` |
| `data/raw/MAUDE/link_dataframes_learned_settings` | raw | step 8 | none — note (b) |
| `data/raw/compustat_firm_data.csv` | raw | step 6, 20 | `synthetic_dimensions_wrds/compustat_firm_data.csv` |
| `data/raw/manual_permno_corrections.csv` | raw | step 8, 35 | `synthetic_maude_linkage/manual_permno_corrections.csv` |

**Nexis Uni** — 24 files (10 tort and preemption exports plus the 14 bankruptcy exports under `medtech/`)

| File the code reads | Kind | Read at | Simulated counterpart under `synthetic_pipeline/simulated_data/` |
|---|---|---|---|
| `data/raw/Liability/NEXIS_FORMAT_MIRROR_HASHES.csv` | raw | `code/00_generate_data/convert_nexis_to_csv.py` | none — note (b) |
| `data/raw/Liability/medtech/Results list for__medical device_ AND _Chapter 11_ AND bankruptcy AND date _YYYY AND date _ YYYY.xlsx` (14 files, windows 1989–1991 … 2002–2004) | raw | step 24 | `synthetic_nexis/medtech/` (same 14 names) |
| `data/raw/Liability/Results list for_medical device tort 1985-1995.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_medical device tort 1985-1995.xlsx` |
| `data/raw/Liability/Results list for_medical device tort 1996-2000.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_medical device tort 1996-2000.xlsx` |
| `data/raw/Liability/Results list for_medical device tort 2001-2004.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_medical device tort 2001-2004.xlsx` |
| `data/raw/Liability/Results list for_medical device tort 2005-2007.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_medical device tort 2005-2007.xlsx` |
| `data/raw/Liability/Results list for_medical device tort preempt 2006-2007.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_medical device tort preempt 2006-2007.xlsx` |
| `data/raw/Liability/Results list for_medical device tort preempt.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_medical device tort preempt.xlsx` |
| `data/raw/Liability/Results list for_pharmaceutical tort preempt 1985-1998.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_pharmaceutical tort preempt 1985-1998.xlsx` |
| `data/raw/Liability/Results list for_pharmaceutical tort preempt 1999-2004.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_pharmaceutical tort preempt 1999-2004.xlsx` |
| `data/raw/Liability/Results list for_pharmaceutical tort preempt 2005-2007.xlsx` | raw | step 24 | `synthetic_nexis/Results list for_pharmaceutical tort preempt 2005-2007.xlsx` |
<!-- END CONFIDENTIAL-INPUT TABLE -->

Notes.

(a) `RESTRICTED_FILE_INVENTORY.csv` also classifies restricted files that no program in this package
reads: working copies and notebooks in my local `data/raw/MAUDE/` tree, and a staging mirror under
`data/derived/_generated/` that holds a second copy of eighteen of the files above, written by
`code/00_generate_data/gen_02_price_matching.py --staging`. The inventory is deliberately exhaustive, so
that a reader can tell a file withheld because it is restricted from one omitted by oversight. None of
them ships and none is an additional input.

(b) A row has no simulated counterpart for one of three reasons. Either the pipeline creates the file
itself at run time on every route — this is true of every `matched_sample_*` panel, which step 9 builds
— or it is a frozen model artifact that only the real-data route uses (the LDA and Word2Vec models; see
"Scope of the real-data check"), or it belongs to a provenance-only program that neither route runs
(`data/raw/CRSPDirectory.csv`, `data/raw/AllPublicCompanies.csv`,
`data/raw/Liability/NEXIS_FORMAT_MIRROR_HASHES.csv`).

(c) `data/raw/MAUDE/` is a public FDA dataset and ships in full; the two restricted entries under that
path are a firm-name-to-PERMNO linkage table and a dedupe settings blob that steps 6 and 8 write and read,
not MAUDE records.

### API-derived fixed inputs (JPE Data Policy 4.3)

Two families of inputs were produced by querying a commercial language model. **Neither is regenerated on
any route.** Both generating programs ship, carry their prompts verbatim, and refuse to run without an
explicit environment variable, so a replicator cannot accidentally overwrite the shipped files — and
could not reproduce them if they tried, because the model responses are not deterministic.

| | Invention years | Price-link concordance |
|---|---|---|
| Files | `data/raw/innovation_year_2_1_FDA_project.csv`, `innovation_year_3_2_FDA_project.csv`, `innovation_year_all_other_FDA_project.csv`, `innovation_year_FDA_project.csv` | `data/raw/2_1_GPT_Price_Links.csv`, `data/raw/3_2_GPT_Price_Links.csv` |
| Program (run guard) | `code/12_invention_year_generation.py` (`RUN_GPT_INVENTION_YEARS`) | `code/12b_gpt_price_links_generation.py` (`RUN_GPT_PRICE_LINKS`) |
| Model | OpenAI `gpt-4o` | OpenAI `gpt-5-mini` (**not** GPT-4o) |
| Sampling | `temperature=0`, 60 requests per minute | API defaults; no temperature, top-p or seed is set |
| Prompt | verbatim in the script: two system prompts with three to four few-shot examples | verbatim in the script (`INSTRUCTIONS`) |
| Run date | **2024-09-09** for the III→II and II→I files and **2024-12-03** for `innovation_year_all_other_FDA_project.csv`, from the pre-staging originals I still hold outside the package. The shipped copies' modification times are February 2026 re-staging dates. | **2025-09-22.** Same evidence: the pre-staging originals. The source notebook is named for 2025-09-25, which is when I saved it, not when the queries ran. |
| Raw responses archived | Partly: the 25 Class III→II raw replies and their exact queries ship inside `innovation_year_FDA_project.csv` (`response`, `query` columns); the 293 Class II→I and 2,784 other replies were not retained. | No: the program writes a JSONL of raw replies at run time, but that file is not a package member. |

On the simulated-data route, step 10 validates the shipped invention-year files against the simulated
panel rather than calling the API; that is one of the three substitutions listed under "Scope of the
simulated-data check".

### The concordance accuracy comparison — a non-scripted validation exercise (JPE Data Policy 4.3)

The paper's price section reports six accuracy figures comparing the two device-type-to-procedure
concordances. They come from a hand-tabulated exercise, not from a program in this package, and this
section states exactly what I did so that a reader can judge it and, if they wish, repeat it.

**What I did.** Two concordances exist: the `gpt-5-mini` one generated by
`code/12b_gpt_price_links_generation.py` and shipped as `data/raw/2_1_GPT_Price_Links.csv` and
`data/raw/3_2_GPT_Price_Links.csv`, and an independently produced crosswalk from two AAPC-certified
medical coders with third-coder reconciliation, shipped as `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv`. I put
the two side by side and asked three chatbot models — GPT-5 Thinking, Gemini 2.5 Pro and Claude Sonnet 4.5
— to apply the same linkage rules and to choose the better mapping, in blinded A/B comparisons. Two of the
three returned their verdicts as counts over 100 device-type–procedure items. I tallied the verdicts by
hand.

**What came out.** Claude Sonnet 4.5's estimated accuracy (correct links over links provided) was 80 % for
`gpt-5-mini` against 75 % for the expert coders; GPT-5 Thinking judged `gpt-5-mini` correct on 78 of 100
items against 43 of 100 for the expert coders; Gemini 2.5 Pro judged 85 of 100 against 48 of 100. All
three favoured the `gpt-5-mini` concordance, which is why it is the baseline and the expert-coder
concordance is the robustness check.

**What this means for reproducibility.** Chatbot outputs are not deterministic, and I did not retain the
session records, the item lists or the per-item verdicts. **These six figures therefore cannot be
regenerated by this package, and they are deliberately not part of the in-text number check** — no program
here produces them and no gate asserts them. They are disclosed here under policy 4.3 rather than
presented as a reproducible result. The manuscript footnote that reports the six figures makes no claim
that they are regenerated by this package; this section is the disclosure, and it is the right place for
it, because what a replicator needs is the method and the two shipped concordances, not a caveat in the
paper.

**What can be repeated.** Both concordances ship, so the comparison itself can be run again by anyone,
with whatever judges they prefer. More importantly, nothing in the paper's estimates rests on the
comparison: step 14 (`code/05_price_analysis.py`) estimates the price results on **each** concordance and
writes both to `output/tables/price_utilization_estimates.csv`, the expert-coder estimates under
`sample="Expert"` and `sample="Expert Matched"`. A replicator can therefore see directly what the choice
was between and what it would have changed.

A third model-derived variable, the "GPT-4o identified devices" patent classification used by
`code/13_restricted_samples.py`, lives inside the restricted Dimensions file
`data/raw/new_patent_analysis/all_device_patents_w_pc.csv` and ships on neither route.

## Dataset list

Every data file in the deposit, by family. `CODEBOOK.md` defines the variables of every shipped
`data/` member — all 108 of them, either by name or through an explicit delegation table that points the
five FDA databases at the agency's own record layouts and names the columns the code reads.
`certification/DATA_DICTIONARY.csv` is the machine-generated per-column dictionary for the simulated
payload: file, column, dtype, description, units, non-null rate, missing-value meaning, distinct-value
count, and allowed values or coarse range for every column of all 116 simulated files. It is regenerated
with the payload by `certification/generate_data_dictionary.py`, which fails if the file set differs, so
its row count always tracks the payload rather than a number printed here.

| Data name | Files in the package | Location | Provided | Citation key |
|---|---|---|---|---|
| FDA 510(k) Premarket Notification | `501k_all.csv` | `data/raw/` | Yes | FDA (2020a) |
| FDA Premarket Approval (PMA) | `all_pma_approvals.txt` | `data/raw/` | Yes | FDA (2019a) |
| FDA Product Classification | `foiclass.txt` | `data/raw/` | Yes | FDA (2019b) |
| FDA MAUDE, original pull | 58 files (masterevent, patient, device problems, problem-code descriptions, device data) | `data/raw/MAUDE/` | Yes | FDA (2020b) |
| FDA MAUDE, 2023 refresh | 7 files | `data/raw/MAUDE_2020/` | Yes | FDA (2020b) |
| FDA Medical Device Recalls (openFDA) | `device-recall-0001-of-0001-2.json` | `data/raw/` | Yes | FDA (2020c) |
| KPSS patent values | `KPSS_2019_public.csv` | `data/raw/` | Yes | Kogan et al. (2017) |
| KPST breakthrough measures | `KPST_Breakthrough.csv` | `data/raw/` | Yes | Kelly et al. (2021) |
| GRID institution identifiers | `GRID/types.csv` | `data/raw/` | Yes | Digital Science (2019) |
| Price deflator (KPSS-implied) | `CPI_deflator.csv` | `data/raw/` | Yes | Kogan et al. (2017) |
| Federal Register 84 FR 71794 text | `Good_2_1_Control_2_1.txt` | `data/raw/` | Yes | FDA (2019c) |
| Class II exemption list from 82 FR 31976 | `Class2_Exemptions_2017_Grennan.csv` | `data/raw/` | Yes | FDA (2017) |
| Author-created inputs | 9 files (the reclassification metadata, two crosswalks, the hand-coded control list, the 20-firm spinal-entrant audit, the data-catalog image and three patent-search augmentation lists) | `data/raw/`, `data/raw/pat_search_augment/` | Yes | — (author-created) |
| API-derived fixed inputs | 6 files (4 invention-year, 2 price-link) | `data/raw/` | Yes | — (author-created) |
| Shipped public aggregates | `unique_devices_thr_75.csv`, `unique_firms_in_PC_thr_75.csv`, `unique_firms_thr_75.csv`, `adverse_event_panel_by_PC_full.csv` | `data/raw/` | Yes | — (author-created) |
| Shipped derived intermediates | 14 files (the applicant-device panel, the approval-time panel, the adverse-event panels, the manufacturer clusters, a copy of the regulation-number crosswalk, and the dedupe settings) | `data/derived/` | Yes | — (author-created) |
| MarketScan claims and aggregates | 3 files | `data/derived/` | **No** — simulated counterpart provided | Merative (2013) |
| Dimensions patent records, metadata, text | 26 files | `data/raw/`, `data/derived/` | **No** — simulated counterpart provided | Digital Science (2020) |
| Analysis panels built from Dimensions and WRDS together | 24 files | `data/derived/` | **No** — rebuilt at run time | Digital Science (2020); CRSP (2019); S&P Global (2019) |
| WRDS / CRSP-Compustat firm financials | 8 files | `data/raw/`, `data/derived/` | **No** — simulated counterpart provided | CRSP (2019); S&P Global (2019) |
| Nexis Uni legal exports | 24 files (10 tort/preemption, 14 bankruptcy) | `data/raw/Liability/`, `data/raw/Liability/medtech/` | **No** — simulated counterpart provided | LexisNexis (2024) |
| Simulated data for all four restricted sources | 116 files in eight subtrees | `synthetic_pipeline/simulated_data/` | Yes | — (generated by this package) |
| Reference outputs of the simulated run | 283 files | `output-simulated/` | Yes | — (generated by this package) |
| Manuscript outputs (real data) | 283 files | `output/` | Yes | — (generated by this package) |

---

# Computational requirements

## Software requirements

I ran everything on x86_64 Linux and macOS. The pipeline needs four things: Python 3.9.13, R 4.1.3, a
LaTeX distribution, and about 30 GB of free disk. The reference environment in which the deposited
outputs are byte-reproducible is a single container image; see "Obtaining or rebuilding the reference
container".

| Component | Version | Notes |
|---|---|---|
| Python | 3.9.13 | pins in `requirements.txt`; numpy must be 1.26.4 |
| R | 4.1.3 in the reference image (4.0.1 on the machine where the outputs were first computed) | `fixest` 0.10.4 and 0.12.1 respectively; see "R packages" |
| LaTeX | TeX Live 2019 in the reference image | only needed to rebuild the manuscript PDF |
| Disk | ≥ 30 GB free | the package is about 22 GB unzipped |
| Memory | ≥ 64 GB for the simulated-data route; ≥ 12 GB for the real-data route | see "Memory, runtime and storage" |

The two operating systems, by release: the reference container is Debian-based, built from
`rocker/r-ver:4.1.3` (Ubuntu 20.04 "focal" userland), running x86_64 Linux; the machine on which the
manuscript's committed outputs were first computed ran macOS on Apple silicon with an x86_64 Python 3.9.13
and an x86_64 R 4.0.1 under Rosetta. `certification/SIF_PROVENANCE.json` records the container's own
version report; `r_requirements-lock.txt` records that machine's R library.

## Installing the Python environment

Create a clean Python 3.9.13 environment and install the pinned direct dependencies:

```bash
python3.9 -m venv fda-env
fda-env/bin/python -m pip install --upgrade pip
fda-env/bin/python -m pip install -r requirements.txt
fda-env/bin/python -m nltk.downloader punkt punkt_tab stopwords wordnet omw-1.4
```

On a macOS x86_64 machine this took 3 minutes 48 seconds and installed 98 distributions. Confirm the pin
that matters most:

```bash
fda-env/bin/python -c "import numpy; assert numpy.__version__ == '1.26.4'; print('ok')"
```

numpy must be 1.26.4. This is load-bearing for the whole pipeline, not for one step: the matched-sample
safety exhibit reproduces the manuscript value (`safety_did = 48,703`) only under numpy 1.26.4, while
numpy 2.0.x yields 52,767 — 4,064 more, about 8.3 percent, a material difference. `run_all.py` launches
every step with `sys.executable`, so all steps inherit this one interpreter; there is no separate numpy
sub-environment anywhere in this package.

The key package versions are `pandas==2.3.3`, `numpy==1.26.4`, `scipy==1.13.1`, `matplotlib==3.9.4`,
`scikit-learn==1.6.1`, `statsmodels==0.14.6`, `rpy2==3.6.4`, `pyhdfe==0.2.0`, `gensim==4.4.0`,
`flashtext==2.7`, `nltk==3.9.2`, `sentence-transformers==5.1.2`, `torch==2.2.2`, `pyarrow==21.0.0`.

Two notes on the other requirement files in the package:

* `requirements-lock.txt` is the complete transitive freeze of the machine that produced the outputs, and
  it is kept byte-identical to the copy the reference image was built from. **It cannot be installed with
  a plain `pip install -r`**: it pins `PySimpleGUI==4.47.0`, which has been withdrawn from PyPI; it pins
  the Linux CUDA build of torch; and pip's resolver rejects the (self-consistent) set. The reference image
  installs it like this, and so should you if you want the exact transitive environment rather than the
  direct pins:

  ```bash
  grep -viE '^(PySimpleGUI|pyreadstat)[=<>]' requirements-lock.txt > reqs.txt
  fda-env/bin/python -m pip install --no-deps -r reqs.txt
  fda-env/bin/python -m pip install --no-deps torch==2.2.2 \
      --index-url https://download.pytorch.org/whl/cpu   # Linux only; on macOS the PyPI wheel is CPU
  ```

  Neither filtered package is imported by the pipeline: `PySimpleGUI` is a dependency of the interactive
  labeller inside `pandas_dedupe`, and `pyreadstat` is unused. This route completed in 4 minutes 27
  seconds and installed 177 distributions when I tested it.

* Two programs in `code/` document how third-party data were acquired and are not part of any reproduction
  route. They need `openai` and `dimcli` respectively, which `requirements.txt` therefore does not install.
  Neither can be re-run in any case: the Dimensions queries ran against a database version the vendor no
  longer serves, and the model calls are not deterministic.

`pandas_dedupe` is needed only by the real-data route's entity-resolution steps; the simulated-data route
imports it nowhere, because both call sites are inside `if not SYNTHETIC_MODE:`. It is pinned anyway, so
that one installation covers every route.

## Obtaining or rebuilding the reference container

The reference environment is one container image. Its identity is:

| | |
|---|---|
| `.sif` SHA-256 | `b9f9ee2aea02c556475487668cf21fcccff0ef07cafd9369ce9100752b4d41a8` (also in `certification/EXPECTED_SIF_SHA`) |
| Base image | `rocker/r-ver@sha256:96be237557b98e5d34957ed4fcbf386999981119086cd4b4cfbafd5c2a47a3f4` (= `rocker/r-ver:4.1.3`) |

**To obtain it.** The certified image file `fda_np126.sif` (5.85 GB; 5.4 GiB) is deposited with this
package, alongside the archive rather than inside it. It is the image every certified run used, and it is
the only copy whose hash can be checked against the anchor:

```bash
sha256sum fda_np126.sif    # must equal certification/EXPECTED_SIF_SHA
```

The byte-identity guarantee for the deposited outputs is made for that file, and for no other copy.
It was converted with Apptainer 1.3.6 from an OCI image built from an immutable source commit;
`certification/SIF_PROVENANCE.json` records that conversion together with the SHA-256 of each of the four
recipe files the image was built from, so the deposited image can be tied back to the recipe that ships
here. If you cannot run the deposited image, the recipe below rebuilds the same software, but a rebuilt
image is not covered by the byte-identity claim.

**To rebuild it** from the recipe in this package, pinning the base image by digest:

```bash
docker build \
  --build-arg BASE_REF=rocker/r-ver@sha256:96be237557b98e5d34957ed4fcbf386999981119086cd4b4cfbafd5c2a47a3f4 \
  -f docker/Dockerfile -t fda-repro .
docker save fda-repro -o fda-repro.tar
apptainer build fda_np126.sif docker-archive://fda-repro.tar
```

The first build takes roughly 30 to 40 minutes: it compiles CPython 3.9.13 from source, installs
`texlive-full`, and installs about 200 R packages. `docker/Dockerfile`'s `BASE_REF` defaults to the mutable
tag `rocker/r-ver:4.1.3`, so always pass the digest.

**A rebuilt image is not byte-identical to the certified one, and I do not claim it will be.** The recipe
is not hermetic: every R package except `fixest`, `didimputation` and `did2s` is installed without a
version request from live CRAN, TeX Live and the system libraries come from Debian mirrors, CPython is
downloaded from python.org, and the NLTK corpora are downloaded during the build. The byte-identity of the
deposited outputs is therefore guaranteed only inside the exact image whose `.sif` hashes to
`b9f9ee2a…`. In any other environment, including a rebuilt image, I expect the numerical results to agree
and the rendered PNGs to differ at the sub-pixel level; compare figures with
`certification/compare_exhibit_fidelity.py` in that case, and treat only the CSV and TeX outputs as
byte-exact. `docker/DOCKER_GUIDE.md` has the full detail.

## R packages

*Note:* the header comments in `docker/install_r_packages.R` and `docker/Dockerfile` that describe the
image as a cross-check with a 0.1–0.6 percent discrepancy predate certification and are superseded by
this section; those files are hash-bound to the image and are kept byte-identical.

R is required: several estimation steps call R through `rpy2`. The reference image has R 4.1.3 with
`fixest` 0.10.4; the machine on which the deposited outputs were first computed had R 4.0.1 with `fixest`
0.12.1, recorded in `r_requirements-lock.txt`. In a controlled
test on the real data, the Class III→II estimation step reproduced all 50 committed formatted tables
byte-for-byte under both `fixest` versions.

I want to be precise about what is and is not pinned. `docker/install_r_packages.R` version-asserts exactly
three packages at build time — `fixest 0.10.4`, `didimputation 0.3.0`, `did2s 0.4.0` — and stops the build
if any of them is wrong. Every other R package is installed from the base image's repository, or from CRAN
as a dependency, without a version request. **The R library is not restored from `docker/renv.lock`**;
nothing in this package calls `renv::restore()`, and the comment in `docker/Dockerfile` that says otherwise
is inaccurate (that file is kept byte-identical to the copy the image was built from, so I correct it here
rather than editing it).

Two comments in `docker/install_r_packages.R` need the same correction. Its header (lines 3–7) calls this
image "a clean-room cross-check, not the authoritative env" and names the original macOS machine as the
reference; line 11 repeats a 0.1–0.6 percent cross-environment discrepancy. Both were written before I
decided to certify the deposit inside this image, and both are superseded by this README: the environment
in which the deposited outputs are byte-reproducible is the image whose `.sif` hashes to `b9f9ee2a…`, and
the 0.1–0.6 percent figure was an artifact of running the image under x86_64 emulation (see "Expected
numerical differences across environments"). `docker/install_r_packages.R` is one of the four files whose
hashes are bound to the image in `certification/SIF_PROVENANCE.json`, so editing it would break the
identity between the recipe and the certified image; it is kept byte-identical and corrected here instead.
The supporting record its header points at, `certification/ENVIRONMENT_EVIDENCE.txt`, ships with the
package.

What the image's R library actually contains is recorded in `docker/container_r_library.tsv`, listed from
inside the built image: 226 packages. It mixes the base image's 2022 package snapshot (`tidyverse 1.3.1`,
`ggplot2 3.3.5`, `Matrix 1.4-0`, `data.table 1.14.2`) with current CRAN releases pulled in as dependencies
of the two pinned installs (`dplyr 1.2.1`, `BH 1.90.0-1`, `tibble 3.3.1`). That is why the authoritative
pin on the R environment is the image hash, not a lock file.

The estimation-critical packages, for reference:

| Package | Reference image | Original author machine |
|---|---|---|
| R | 4.1.3 | 4.0.1 |
| `fixest` | 0.10.4 | 0.12.1 |
| `didimputation` | 0.3.0 | 0.3.0 |
| `did2s` | 0.4.0 | 0.4.0 |
| `did` | 2.1.1 | 2.0.0 |
| `data.table` | 1.14.2 | 1.17.2 |

To install the estimation packages into an existing R outside the container:

```r
install.packages("remotes")
remotes::install_version("fixest",        version = "0.10.4")
remotes::install_version("did",           version = "2.1.1")
remotes::install_version("did2s",         version = "0.4.0")
remotes::install_version("didimputation", version = "0.3.0")
install.packages(c("data.table", "tidyverse", "extrafont", "sandwich",
                   "broom", "lmtest", "BMisc", "Rcpp", "RcppArmadillo"))
```

**On macOS, three settings are required** because `rpy2` loads R in-process.

1. The R build must match the Python interpreter's architecture. This package was verified with an
   x86_64 Python 3.9.13 and an x86_64 R. On Apple silicon machines where the default R is an arm64 build,
   `rpy2` fails to load `libR.dylib` with an "incompatible architecture" error; point `R_HOME` at a
   matching x86_64 R, for example
   `R_HOME=/Library/Frameworks/R.framework/Versions/4.0/Resources`.
2. Preload `libR` so `rpy2` uses stable API mode. Without this, `rpy2`'s C extension cannot resolve
   `_R_BaseEnv` in the flat namespace and falls back to ABI mode, where a single R error corrupts the
   session for the rest of the process — the cause of intermittent step-12 failures. Set, alongside
   `R_HOME`:

   ```bash
   export DYLD_INSERT_LIBRARIES="$R_HOME/lib/libR.dylib"
   ```

3. Several steps also spawn a subprocess `Rscript` (for example `code/05_price_analysis.py` and the
   Conley–Taber calls). If the system `Rscript` resolves to a different R than `R_HOME`, those steps fail.
   Put a shim first on `PATH`:

   ```bash
   export R_HOME=/Library/Frameworks/R.framework/Versions/4.0/Resources
   export R_LIBS_USER="$HOME/Library/R/4.0/library:$R_HOME/library"
   mkdir -p "$HOME/r_shim" && cat > "$HOME/r_shim/Rscript" <<'SH'
   #!/bin/bash
   f="${@: -1}"; exec arch -x86_64 "$R_HOME/bin/exec/R" --no-save --no-restore --no-echo --file="$f"
   SH
   chmod +x "$HOME/r_shim/Rscript"
   export PATH="$HOME/r_shim:$PATH"
   ```

   The shim reads `$R_HOME`, so it follows that setting; drop `arch -x86_64` on non-macOS. Where `Rscript`
   already resolves to the correct R, the shim is a harmless no-op.

`run_all.py` copies the environment into each step's subprocess, so exporting these once before the run
covers the whole pipeline. On Linux, and inside the reference container, none of the three is needed.

## LaTeX

LaTeX is needed only to rebuild the manuscript PDF; no analysis step uses it. To compile, run from
`paper/`:

```bash
python3 build_manuscript.py JPE_submission_v8.tex
```

That script requires `pdflatex` and `bibtex` on `PATH` and exits with an error if either is missing. The
manuscript uses `\bibliographystyle{aer}`, and `aer.bst` comes from the TeX Live package `economic`, which
a minimal installation does not include (`tlmgr install economic`, or Debian's
`texlive-bibtex-extra`) — it is the one prerequisite that is easy to miss. The reference image has
**TeX Live 2019** (`pdfTeX 3.14159265-2.6-1.40.20`); `docker/DOCKER_GUIDE.md` lists the full LaTeX
installation.

A compile outside the reference image produces the same 110-page document but not a byte-identical PDF,
because TeX Live versions differ (verified on macOS with TeX Live 2026). The deposited
`paper/JPE_submission_v8_build.pdf` is the one built in the reference image.

## Controlled randomness

Every source of randomness in this package is seeded, and the seed is a constant, never a timestamp.

| Where | Seed | Set at |
|---|---|---|
| Every pipeline step's Python hash seed | `PYTHONHASHSEED=0` | `run_all.py`, function `build_child_env` — the driver sets it for every child process, so nothing has to be exported by hand |
| Every analysis step's NumPy global RNG | `config.RANDOM_SEED = 12345` | `config.py:49`, applied by `np.random.seed(config.RANDOM_SEED)` at the top of each step (for example `code/02_match_samples.py:24`, `code/04_event_studies.py:60`, `code/11a_product_variety.py:67-68`) |
| Mahalanobis matching (step 9) | `config.RANDOM_SEED` | `code/02_match_samples.py:24`, via `code/modules/match_mahal.py` |
| Conley–Taber permutation inference | `config.RANDOM_SEED` | passed explicitly at 16 of the 21 call sites: `code/03a_estimation_3to2.py`, `code/03b_estimation_2to1.py`, `code/04_event_studies.py`, `code/05_price_analysis.py` (two), `code/06a_safety_analysis.py`, `code/06b_validate_safety.py`, `code/06c_validate_safety_embed.py`, `code/07_firm_heterogeneity.py` (three), `code/08_lbd_simulation.py`, `code/13_restricted_samples.py`, `code/14_breakthrough_patents.py` (two), `code/16_total_patent_value_did.py`. The remaining five — `code/11a_product_variety.py:451,593` and `code/11d_reg_design.py:222,1056,1595` — pass no seed of their own and draw from the module's global stream, seeded on the same constant at `11a:68` and `11d:62`; see the note below |
| Word2Vec training (step 16) | `config.RANDOM_SEED`, single-threaded | `code/06b_validate_safety.py:528-530` (`workers=1, seed=config.RANDOM_SEED`); a single worker is required because gensim's parallel training is not order-deterministic |
| LDA topic models (step 22) | `random_state=42` | `code/11a_product_variety.py:212,236` |
| The data simulation | `PUBLIC_SEED = 20260803` | `synthetic_pipeline/build_simulation.py:59`, at the top of the file, echoed as the first line of the build log and cross-checked fail-closed against `synthetic_pipeline/generators/independent_universe.py`. `FDA_SYNTHETIC_SEED_OFFSET` perturbs it for robustness testing; leave it unset to reproduce the deposited payload. |

**The five Conley–Taber calls that take the global stream.** `code/11a_product_variety.py:451,593`
and `code/11d_reg_design.py:222,1056,1595` do not pass `seed=`; they draw from the NumPy global
stream, which both modules seed on `config.RANDOM_SEED` at import. Nothing is drawn from entropy, so
each script reproduces itself, but those five draws depend on how many draws were taken before them
in the same process — that is, on the number and order of Conley–Taber calls, which a caught-and-
skipped product code or topic would change. What this does and does not reach:

- the Conley–Taber **point estimate** does not depend on the draw at all. It is ordinary least
  squares on the residualized data, and it is identical to ten decimal places across different
  streams. So the Section 6 footnote's maturity-gradient slopes, standard errors and p-values
  (`output/tables/maturity_gradient_slopes.csv`) are fully determined: they are a cross-sectional
  regression of the per-product-code **point estimates** on product-code age, and the Conley–Taber
  interval does not enter them;
- the **permutation interval** does depend on the draw, by roughly two percent of the bound at the
  shipped 5,000 simulations. Three outputs carry such an interval from these five sites: the standard
  errors in `output/tables/Table_D12_petitioned_vs_fda.tex`, and the confidence bands in
  `output/figures/variety_3_2.png` and `variety_2_1.png` (Figure D.5). No in-text number is among
  them.

A replicator re-running these two steps in the reference environment reproduces all of it; the point
is to say plainly which part of it rests on the call order rather than on an explicit seed.

The driver also pins the linear-algebra thread count to one
(`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=VECLIB_MAXIMUM_THREADS=MKL_NUM_THREADS=NUMEXPR_NUM_THREADS=1`),
forces the non-interactive matplotlib backend (`MPLBACKEND=Agg`), points the matplotlib, XDG and NLTK
caches at `output/_cache/` inside the package, and scrubs `PYTHONPATH`, `PYTHONSTARTUP`, `R_PROFILE_USER`
and `R_ENVIRON_USER` from the child environment so that nothing on the host machine can change a result.

## Memory, runtime and storage

The figures below were measured once, on an AMD EPYC 7742 node of Indiana University's Quartz cluster.
Treat them as the order of magnitude to plan for, not as a guarantee.

**Simulated-data route (36 steps).** About **9 hours 5 minutes** of wall clock on 12 cores with a 150 GB
memory allocation. The time is concentrated in a handful of steps:

| Step | Program | Time |
|---|---|---|
| 17 | `code/06c_validate_safety_embed.py` (sentence-transformer embeddings, single-threaded) | ≈ 5 h 07 min |
| 12 | `code/03b_estimation_2to1.py` | ≈ 1 h 49 min |
| 22 | `code/11a_product_variety.py` (topic models) | ≈ 30 min |
| 1 | `code/00_generate_data/gen_01_main_panels.py` | ≈ 24 min |
| 16 | `code/06b_validate_safety.py` (Word2Vec) | ≈ 9 min |
| all others | | under 5 min each |

**A second measurement of the same route, on very different hardware.** I also ran the simulated-data
route end to end on my own laptop on 18 September 2026 — an Apple-silicon Mac running the x86_64 build of
Python 3.9.13 under Rosetta, with x86_64 R 4.0.1 — and it took **2 hours 4 minutes** of wall clock (23:49
to 01:53) for the 34 steps that ran, with step 12 at about **47 minutes** and step 17 at about
**11 minutes**. Both figures were measured once. They differ from the cluster figures above by much more
than I would put down to clock speed, and the difference is concentrated in exactly those two steps; I
have not established why, so plan for the larger of the two. Step 35 then failed on that run because two
simulated inputs were missing from the payload it used; with those inputs present the route finishes
`36 succeeded / 0 failed / 0 skipped`.

**Real-data route** (`--skip-gen --force-estimation --strict-cert`): **1 hour 17 minutes** on 8 cores, with
a peak resident set of about **9.8 GB**.

**Memory.** Run the simulated-data route on a machine with at least **64 GB**. I ran it with a 150 GB
allocation and it did not fail; the scheduler's own peak figure for that run is about 150 GB, but that
accounting double-counts shared pages, so I do not offer it as a requirement. The real-data route's
estimation steps are much lighter and run comfortably in 12 GB.

**Storage.** The package is about **22 GB** unzipped.
`synthetic_pipeline/materialize_simulation.py --for-gen-run` copies a further about **6.5 GB** into
`data/` before the run starts. Allow at least **32 GB** free.

The archive is 4.6 GB compressed and about 22 GB unpacked, and it is accompanied by the 5.4 GB reference
image, so the delivery is of the size at which the JPE Data and Code Policy asks for a method agreed with
the Data Editor in advance; it is delivered by the method the Data Editor specifies rather than by upload
alone. Almost all of the bulk is the FDA MAUDE tables under `data/raw/` and the simulated
payload; the code, documentation and outputs together are a small fraction of it.

Rebuilding the simulated payload from scratch (optional; see "The simulation programs") takes about
**10 minutes** and writes about **6.5 GB**.

---

# Description of programs/code

## Package layout

```text
README.md                  this file — the single documentation point for the package
LICENSE.txt                licence and rights statement
run_all.py                 the driver: runs the whole pipeline in dependency order
config.py                  shared paths, constants and the analysis random seed
requirements.txt           pinned direct Python dependencies
requirements-lock.txt      full transitive freeze of the environment (see the install notes)
r_requirements-lock.txt    snapshot of the R library on the original author machine
code/                      all analysis and data-construction programs
  00_generate_data/          raw-to-derived construction (steps 1-8) and acquisition provenance
  modules/                   shared estimation and matching modules
r_scripts/                 R helpers the Python steps source through rpy2
data/                      all shipped inputs
  raw/                       public and author-created raw inputs, incl. the FDA MAUDE tables
  derived/                   shipped derived intermediates and dedupe settings
synthetic_pipeline/        the simulation: generators, driver, contracts, and the simulated data
  simulated_data/            116 simulated files in eight subtrees — the restricted-data replacement
  generators/                the Stage A and Stage B generator programs
  _synthetic_source_internal/  the four committed artifacts the simulation is built from
output/                    the manuscript's own outputs (figures, tables, formatted LaTeX tables)
output-simulated/          the 283 reference outputs of the simulated-data run
certification/             manifests, provenance records and the checking programs (see below)
docker/                    the recipe for the reference container and its guide
models/                    the sentence-transformer model step 17 uses, offline, with its model card
manual_figures/            the author-drawn Figure 2, as PNG and as its editable draw.io master
paper/                     the manuscript source, bibliography, built PDF and its build program
```

The supporting documents are `CODEBOOK.md` (variable definitions for every shipped data file),
`DATA_INPUTS.md` and `data_input_manifest.csv` (the per-file input inventory, in prose and as a table),
`DATA_SOURCES.md` (per-source notes), `RESTRICTED_DATA_MANIFEST.csv` and `RESTRICTED_FILE_INVENTORY.csv`
(what is excluded and why), `RESTRICTED_DATA_VERIFICATION_MEMO.md` (the provider routes),
`WRDS_EXTRACTION_ROADMAP.md` and `NEXIS_SEARCH_METHODOLOGY.md` (how to reproduce those two extracts),
`DATA_POLICY_COMPLIANCE.md` (the policy-by-policy compliance record),
`MANUSCRIPT_EXHIBIT_PROGRAMS.md` and `MANUSCRIPT_EXHIBIT_DATA_DEPENDENCIES.md` (the working copies behind
the exhibit table below, and which restricted source each exhibit needs),
`synthetic_pipeline/DGP_DESIGN.md` (how the simulated data are built) and
`docker/DOCKER_GUIDE.md` (the container in detail). Each of them carries the header "Supporting reference;
`README.md` governs"; nothing a replicator must do is documented only in one of them. `.dockerignore` at
the root is a build-time file for the container recipe and is not used by either route.

Five further reference documents sit beside the checking programs in `certification/`, and carry the same
header: `THREAT_MODEL.md` (what the simulation is designed to prevent, and what it does not),
`COMMITTED_PARAMETER_RIGHTS_REVIEW.md` (the rights review of the two restricted-derived committed
artifacts), `GEN_PROGRAM_AUTHENTICITY.md` (whether each generating program that ships is the original),
`FIGURE_PROVENANCE.md` (how each figure in the manuscript is produced) and
`EXPECTED_OUTPUT_HASHES_NOTES.md` (how the output manifests are declared and refreshed).
`manual_figures/NOTES.md` and `models/MODEL_PROVENANCE.md` document the one hand-drawn figure and the
shipped embedding model in place.

### Non-deterministic inputs, and what is deposited about them

Two inputs are produced by a language model and the topic models behind Appendix Figure D.5 are
fitted from a random seed, so none of the three is reproducible by running it again: the same
prompt returns different answers, and the same corpus fits differently under a different seed. The
package handles this by freezing each of them as a hash-pinned input, so the deposited outputs are
reproducible from the deposited artifacts rather than from a fresh call or a refit.

`NONDETERMINISTIC_VARIABLE_SENSITIVITY_MEMO.md` measures what that costs. It traces where each
input reaches the manuscript, reports how far the published quantities move across ten
re-draws — or ten seeds for the topic models — and states what the exercise does not establish.
`nondeterministic_variable_sensitivity.zip` is the evidence behind it: 11,485 raw model responses
with their prompts and model identifiers, the analysis scripts, and the per-draw outputs. Nothing
in that archive is read by either route, and section 9 of the memo gives the command that
regenerates each of its tables. It ships as one archive rather than as its individual members
because it is evidence rather than input; it is hashed as a single object.

**What the exercise found.** Each classification was repeated ten times, and each fresh draw was
carried through to the published estimates rather than compared only at the item level.

*Procedure-code price links* (337 codes, ten draws, 3,370 calls, no errors). The link decision is
unanimous across all ten draws for 70% of codes and mixed for 30%; mean pairwise agreement is
0.866. Ten draws reproduce the deposited decision for 234 of 337 codes (69%). Carried through, the
headline Class II→I billed-amount decline averages −0.297 with a standard deviation of 0.109
against −0.32 in the deposit, and is negative in every draw; the matched-sample version averages
−0.235 (SD 0.076) against −0.23. The Class III→II all-procedure estimate is the fragile one: it is
available in seven of ten draws and ranges from −0.11 to +0.23 against a deposited +0.06, so its
sign is not stable. The eight estimates built on the independently expert-coded crosswalk have a
standard deviation of exactly zero across all ten draws, which is the control.

*Device invention years* (293 codes, ten draws). The returned year moves for 113 of 293 codes
(39%), with a median movement of 7 years and a maximum of 139. The published Class II→I market-age
slope stays negative and insignificant in all ten draws (mean −0.001312, SD 0.000122; p-values .19
to .35), and the implied maturity crossing lands between 60.6 and 64.2 years against a deposited
61.1, consistent with the manuscript’s “roughly 60 years”. Two things belong alongside that: the
deposited slope is larger in magnitude than the slope in every one of the ten draws, and these
invention years have no independent hand-coded benchmark, so the exercise establishes stability
rather than accuracy. The count of Class II codes above the 60-year threshold runs 647 to 656
(SD 3.20) against a deposited 651, out of a population of 2,235. The Class III→II rows use
hand-coded years and have a standard deviation of exactly zero.

*Topic models for Appendix Figure D.5* (ten seeds). Refitting selects anywhere from 10 to 25
topics, which moves the number of topic effects from 20 to 35 (mean 26.0, SD 5.4); one seed in ten
gives the deposited 30, and the share of effects whose confidence interval excludes zero runs 54%
to 80%. No main result depends on this figure.

One caution for anyone repeating this design: the share of items on which N draws agree unanimously
falls mechanically as N rises, so it is not an estimate of a fixed quantity and is not comparable
across exercises run at different N. Mean pairwise agreement is the stable summary. Ten draws
should be treated as a lower bound on what is needed to characterise these distributions.

The topic count for the LDA fits is stated in the code rather than selected by maximising
coherence: `code/11a_product_variety.py` sets `PINNED_TOPIC_COUNT = 15`, the value the fourteen
frozen model artifacts carry in both samples. Coherence does not identify a count here, and the
comment at the selection site gives the evidence. The selection runs only on a refit; on both
routes the figures come from the frozen artifacts.

If this deposit carries a `confidential-data-do-not-publish/` folder, that folder is outside the
scope of `certification/PUBLIC_PACKAGE_ALLOWLIST.txt` and of
`certification/DEPOSITED_FILE_RIGHTS.csv`. Both enumerate the files authorized for publication, and
both are the authority on what may be published; the archive will therefore contain more members
than either lists. The restricted sources behind that folder, and the route by which each can be
verified, are set out in `RESTRICTED_DATA_VERIFICATION_MEMO.md`. That folder carries its own
manifest, which states for each source what is included and the permission that inclusion
rests on; for a source the folder does not carry, the route in the verification memo is the
one that applies.

## The pipeline: 36 steps

`run_all.py` runs the steps below in this order and stops at the first failure. Steps 1–8 build derived
data from raw inputs; steps 9–10 construct samples; steps 11–12 estimate the static difference-in-differences
models through R; steps 13–34 produce the figures and tables; step 35 computes the in-text numbers; step 36
audits the manuscript's exhibit coverage.

| Step | Program (under `code/`) | Phase | What it produces |
|---|---|---|---|
| 1 | `00_generate_data/gen_01_main_panels.py` | data generation | The master product-code-by-year panel `Full_sample.csv`, the patent panel, the intuitive/later-treated/spillover control frames, and the applicant-device panel |
| 2 | `00_generate_data/gen_02_price_matching.py` | data generation | Price-matched claims panels `constrained_adv_event_new_sept25{,_3_2}.csv` (needs MarketScan) |
| 3 | `00_generate_data/gen_03b_lbd_clusters.py` | data generation | Entity-resolution clusters for the learning-by-doing panel |
| 4 | `00_generate_data/gen_03_lbd.py` | data generation | The learning-by-doing approval-time panel `LBD_ApprovalTime_Both_oct22_24.csv` |
| 5 | `00_generate_data/gen_04_parquets.py` | data generation | The pre-stacked Class II→I panels `data_2_1_*.parquet` |
| 6 | `00_generate_data/gen_05_adverse_fsize.py` | data generation | The adverse-event-by-firm-size panel `Adverse_fsize_ready_all4_oct22_24.csv` |
| 7 | `00_generate_data/gen_06_adv_2020.py` | data generation | The 2020–2022 adverse-event panel `Adv_Event_2020_2022.csv` |
| 8 | `00_generate_data/gen_07_adverse_permno.py` | data generation | The MAUDE-manufacturer-to-PERMNO linkage and its deduplicated manufacturer list |
| 9 | `02_match_samples.py` | samples | The Mahalanobis-matched treated/control samples `matched_sample_*` |
| 10 | `12_invention_year_generation.py` | samples | Validates the invention-year inputs (see "API-derived fixed inputs") |
| 37 | `00_generate_data/gen_02_price_matching.py` | samples | The deferred price-matching run — see the note below |
| 11 | `03a_estimation_3to2.py` | estimation | Static DiD estimates, Class III→II (about 50 estimate CSVs) |
| 12 | `03b_estimation_2to1.py` | estimation | Static DiD estimates, Class II→I (about 50 estimate CSVs) |
| 13 | `04_event_studies.py` | analysis | Event-study figures, their coefficient CSVs and the printed base rates (27 specifications) |
| 14 | `05_price_analysis.py` | analysis | Price and utilization estimates and figures |
| 15 | `06a_safety_analysis.py` | analysis | Safety-emphasis DiD panels and figures |
| 16 | `06b_validate_safety.py` | analysis | Safety robustness by refined keywords (trains Word2Vec) |
| 17 | `06c_validate_safety_embed.py` | analysis | Safety robustness by embedding distance (sentence-transformer) |
| 18 | `07_firm_heterogeneity.py` | analysis | Firm-size heterogeneity figures and tables |
| 19 | `08_lbd_simulation.py` | analysis | Learning-by-doing simulation and calibration figures |
| 20 | `09_summary_stats.py` | analysis | Table 1 and Table D.16, the summary statistics |
| 21 | `10_table_formatting.py` | formatting | The main formatted LaTeX tables (32 tables) |
| 22 | `11a_product_variety.py` | appendix | Product-variety LDA analysis, Figure D.5 |
| 23 | `11b_recall_analysis.py` | appendix | Recall analyses, Figures D.13 and D.14 |
| 24 | `11c_liability.py` | appendix | Liability and bankruptcy trends, Figure D.9 |
| 25 | `11d_reg_design.py` | appendix | Device-experience regressions, Figures D.10–D.11 and the model caches step 31 reads |
| 26 | `11e_new_entry_2015.py` | appendix | New-firm entry after the 2015 event, Figure D.15 |
| 27 | `11f_reg_background.py` | appendix | Reclassification-event distributions, Figure D.1 |
| 28 | `11g_descriptive_figures.py` | appendix | Copies the data-catalog diagram into `output/figures/`, Figure D.2 |
| 29 | `13_restricted_samples.py` | appendix | Restricted patent-sample robustness, Table D.17 |
| 30 | `14_breakthrough_patents.py` | appendix | Breakthrough-patent effects, Table D.18 |
| 31 | `10b_format_remaining_tables.py` | formatting | The remaining formatted tables (needs step 25's caches and steps 16–17's CSVs) |
| 32 | `12_contact_lens_case_study.py` | exhibits | The contact-lens case-study figures, Figure 1 |
| 33 | `15b_event_study_HD_coefficients.py` | exhibits | Event-study half-distance coefficients that feed the in-text safety percentage |
| 34 | `16_total_patent_value_did.py` | exhibits | The total-patent-value DiD behind the cost-benefit table |
| 35 | `15_intext_derived_numbers.py` | exhibits | Every derived number quoted in the text, plus the computational appendix tables |
| 36 | `audit_pipeline_current.py` | audit | Checks that every manuscript figure and table reference resolves, and writes the HTML comparison report |

**The deferred step (why the step table has 37 entries and 36 run).** `gen_02_price_matching.py` is a
data-generation transformation that reads the matched sample produced at step 9, so it cannot run at its
step-2 position on a route that builds the matched sample from scratch. On either route that runs the
generation phase — the simulated-data route and the real-data route from raw — the step-2 position
is skipped and the same program is executed after step 9 as table entry 37, on that route's MarketScan
claims, its price links and the fresh step-9 matched sample. On Route 2 the generation phase does not run
at all, so entry 37 is not scheduled. Exactly one of the two positions is scheduled on
any route, which is why every route schedules 36 steps and the progress counter reads
`Step N/36 (step table #M)`.

## The simulation programs

The simulation replaces all four restricted sources. It has two stages.

**Stage A** runs on my side, in the authorized environment, and is not part of any replication route.
`synthetic_pipeline/generators/gen_00a_extract_parameters.py` is the only program that ever reads
restricted data; `gen_00b_pc_effects.py` uses public design inputs. Together they emit the four artifacts
that ship in `synthetic_pipeline/_synthetic_source_internal/`:

* `simulation_parameters.json` — rounded cardinalities, smoothed size families, and the public product-code
  list;
* `simulation_schema_contract.json` — the aggregate-interface paths, columns, coarse types, the rounded
  per-column cardinalities of the Nexis files, and row-count approximations — two significant figures, set one rounding step above the nearest two-significant-figure value, so the real extract is smaller by half a step to one and a half steps;
* `pc_effects.parquet` — synthetic random effects drawn from fixed distributions conditioned on the public
  FDA and Federal Register design;
* `public_master_skeleton.parquet` — the public columns of the master panel.

Both programs ship, so the Data Editor can read exactly what was extracted. The first two are the only
restricted-derived artifacts in the deposit; `certification/COMMITTED_PARAMETER_RIGHTS.csv` and
`certification/rights_evidence/` record their rights determination.

**Stage B** reads no real data. `synthetic_pipeline/build_simulation.py` drives the generators
`gen_00c`–`gen_00i` (simulated MarketScan, Dimensions/WRDS, patents, Nexis, patent text, de-identified
patent values and the MAUDE linkage inputs), each seeded from `PUBLIC_SEED = 20260803`, and writes the
116-file payload. To regenerate it:

```bash
PYTHONHASHSEED=0 python3 synthetic_pipeline/build_simulation.py --output-dir /path/outside/the/package
```

The output directory must be outside the package and must not already exist. The build takes about 10
minutes and writes about 6.5 GB, and two clean builds are byte-identical.
`certification/compare_simulated_payloads.py` compares two builds.
`certification/regen_determinism/verify_simulated_data_manifest.py` takes no arguments and checks the
payload shipped at `synthetic_pipeline/simulated_data/` against the file list and per-file SHA-256 values
in `certification/regen_determinism/`; to check a build of your own, materialize it over the shipped one
in a fresh extraction first. The payload that ships is the one authorized by the author-signed migration record
`certification/regen_determinism/PAYLOAD_MIGRATION_RECORD.json`, which `verify_payload_migration.py` in the same
directory checks (the build refuses an unsigned record).

`synthetic_pipeline/materialize_simulation.py` copies the payload into `data/` at the destinations
recorded in `certification/MATERIALIZE_DESTINATIONS.tsv`. With `--for-gen-run` it places only the
acquisition-stage inputs and deletes every derived transformation output, so the run really does start
from raw. `--list-destinations` and `--list-for-gen-destinations` print the two destination sets without
copying anything, and `--source-dir <dir>` materializes a payload you rebuilt yourself instead of the
shipped one. `synthetic_pipeline/preflight_from_raw.py` then checks, fail-closed, that every required
input is present and every transformation output is absent.

Every generated file has a signed row in `certification/GENERATION_LINEAGE.csv`, the lineage ledger: for
each column of each simulated file it records the public or synthesized source the column comes from and
the name of the reviewer who signed that determination. `certification/verify_generation_lineage.py`
checks the ledger against the payload and reports any row that is not signed.

How the simulated data are built, and the disclosure limits they respect, are documented in
`synthetic_pipeline/DGP_DESIGN.md`. In short: the data are drawn from an independent universe rather than
de-identified from the real data; restricted values, identifiers, per-code patent counts, matched-control
structure, and firm, safety and price outcomes are all synthetic draws; only documented public FDA product
codes and the Federal Register reclassification design are retained. Non-key entity co-membership — which
rows share a firm, assignee or inventor — is regenerated, and per-column missingness is redrawn.
Restricted-derived cardinalities are rounded and group sizes are drawn from smoothed families rather than
preserving the real distributions. Merge keys belong to an independent synthetic identifier domain and stay
consistent across the simulated files, which the run-time joins require, but no real-to-simulated identifier
map exists anywhere. `synthetic_pipeline/audit_simulated_data.py` is a fail-closed test of those properties.
On the deposit as it stands (no restricted data present) run it with
`--defer-restricted-counterparts`; without that flag it fails closed because the real counterparts are
absent, which is the intended behaviour in the authorized environment.

## Checking programs that ship

These are in `certification/`. A replicator needs the first two; the rest are there so that any claim this
README makes can be checked on the extracted archive rather than taken on trust.

The archive also carries the record of its own build: `PUBLIC_PACKAGE_BUILD_REPORT.txt`,
`certification/BUILD_CERTIFICATION.txt` and one `certification/build_evidence/<check>.report.txt` per build
check (the command, its exit code and its full output, with the builder's directories replaced by
`<source>` and `<package>`). `BUILD_CERTIFICATION.txt` lists the SHA-256 of each report, so the evidence
cannot be altered without the certificate disagreeing. A replicator does not need these files to run anything.

| Program | What it checks |
|---|---|
| `compare_output_simulated.py` | The simulated run against the 283 reference members in `output-simulated/`; SHA-256 identity. **This is the Data Editor's acceptance check.** |
| `compare_exhibit_fidelity.py` | Figures, semantically, when byte identity is not expected because the run was outside the reference image |
| `compare_all_numbers.py` | Every cell of the 152 estimate and in-text-backing CSVs listed in `COMPARATOR_INVENTORY.txt`, against the committed values; byte identity by default, and `--allow-numeric-equal` accepts numerically equal cells that differ only in formatting |
| `certify_fromraw_route.sh` | The whole simulated-data route inside the reference container, with network and host mounts denied (see "Instructions to replicators") |
| `run_fromraw_analysis_only.sh` | The analysis half of that harness, used inside the container |
| `verify_candidate_zip.py` | The archive's SHA-256 and that its member list matches the reviewed inventory |
| `verify_immutable_tree.py` | That the extracted code did not change during a run |
| `compare_simulated_payloads.py` | Two independent simulation builds against each other |
| `validate_payload_contract.py` | The simulated MarketScan and Nexis files against the committed schema contract: file set, rows, ordered columns, types and cardinalities |
| `regen_determinism/verify_simulated_data_manifest.py` | The shipped simulated payload against its file list and per-file SHA-256 values (no arguments) |
| `regen_determinism/verify_payload_migration.py` | That the shipped simulated payload is the one the signed migration record `regen_determinism/PAYLOAD_MIGRATION_RECORD.json` authorizes: the manifest SHA-256, the file counts and the exact added/removed file set; the `--final` build refuses an unsigned record |
| `verify_generation_lineage.py` | That every column of every simulated file has a recorded lineage back to a public or synthesized source |
| `verify_intext_report.py` | That the in-text-number report is complete for the route that produced it |
| `validate_handentered_tables.py` | That the three generated appendix tables (D.1, D.11, D.15) display the numbers the analysis programs computed, and that the manuscript `\input`s the generated file rather than a stale inline copy |
| `verify_public_source_provenance.py` | That every shipped public input has a provenance row and matches its pinned hash |
| `gen_deposited_file_rights.py` | Regenerates the per-member rights matrix and fails if any member lacks an affirmative row |
| `generate_data_dictionary.py` | Regenerates `certification/DATA_DICTIONARY.csv` and fails if the file set differs from the reviewed payload inventory |
| `refresh_expected_output_hashes.py` | That the declared output manifests agree with the canonical inventory and with the files on disk. `--write` re-pins the SAME set of outputs and names every one whose content changed; changing WHICH outputs are governed needs `--write --allow-path-set-change`, which names every path it adds or removes |
| `hash_manuscript_closure.py` | That the shipped manuscript is byte-identical to the authoritative copy |

## License for code

All code in this package is mine and is licensed under the terms in `LICENSE.txt`, which permits access
and use for replication and any other purpose, asking only for attribution and subject to the third-party
terms reproduced there for the MiniLM model and the redistributed public datasets.

---

# Instructions to replicators

Three routes are supported. **Route 1 is the reproducibility check** and needs no licensed data. Routes 2
and 3 are for a researcher who holds the four licences: Route 2 starts from the derived analysis files
that ship, and Route 3 rebuilds those from the licensed raw extracts first.

A bare `python3 run_all.py` is not a reproduction command, and the driver says so: it names no route, so
the driver exits before step 1, writes nothing, and prints the three routes below. It refuses this way on
every tree, including a complete one, because a run that names no route must not be able to start the
generation phase and overwrite a derived file.

## Route 1 — the simulated-data route

### (a) Unpack

Extract the archive into an empty directory and work there. If you received the archive with a `.sha256`
sidecar, check it first:

```bash
SHA=$(cut -d' ' -f1 <archive>.zip.sha256)
python3 certification/verify_candidate_zip.py --zip <archive>.zip --sha256 "$SHA"
```

Use a fresh extraction for each route, and never materialize simulated data over a tree that holds
licensed real data.

### (b) Install

Follow "Installing the Python environment" above, and use the reference image `fda_np126.sif`
if you want byte-identical figures (see "Obtaining or rebuilding the reference container"; a rebuild from
the recipe is the same software but is not covered by the byte-identity claim). Outside that image the
analysis still runs and the numbers still agree; only the PNG bytes may differ.

Every command below is written as `python3`. If you installed into the virtual environment above, either
activate it (`source fda-env/bin/activate`) or substitute `fda-env/bin/python` for `python3` throughout —
what matters is that the interpreter running `run_all.py` is the one with numpy 1.26.4, because the driver
launches every step with `sys.executable`. On macOS, export the three R settings from "R packages" in the
same shell before you start.

### (c) Empty the output directories

**Delete everything under `output/figures/` and `output/tables/` before the run, or pass `--clean-output`
and let the driver do it.** The deposited `output/` tree holds the manuscript's real-data exhibits. If it
is left in place, a step that silently produced nothing would leave the previous file behind and the run
would still report success. The simulated-data route refuses to start while either directory contains a
file, and tells you which files to remove. `output/logs/` and `output/_cache/` are not touched.

### (d) Run

```bash
python3 synthetic_pipeline/materialize_simulation.py --for-gen-run
python3 synthetic_pipeline/preflight_from_raw.py
python3 run_all.py --synthetic-from-raw --clean-output \
    --regenerate-safety-keywords --regenerate-safety-embeddings
```

The first command places the 94 simulated acquisition inputs into `data/` and removes every derived
transformation output. The second checks that state and fails closed if anything is missing or left over.
The third runs all 36 steps.

**No environment variable needs to be exported.** `run_all.py` sets, for every step it launches:
`PYTHONHASHSEED=0`; `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`,
`MKL_NUM_THREADS` and `NUMEXPR_NUM_THREADS` all `=1`; `MPLBACKEND=Agg`; `MPLCONFIGDIR`, `XDG_CACHE_HOME`
and `NLTK_DATA` under `output/_cache/`; `FDA_STRICT_INTEXT=1`; `FDA_INTEXT_ROUTE=synthetic`;
`FORCE_ESTIMATION=1` (implied by `--synthetic-from-raw`, so the estimate CSVs are always recomputed rather
than reused); `FDA_SYNTHETIC_MODE=1`; and `FDA_FORCE_SAFETY_KEYWORDS=1` when
`--regenerate-safety-keywords` is passed. It also scrubs `PYTHONPATH`, `PYTHONSTARTUP`, `R_PROFILE_USER`
and `R_ENVIRON_USER`, and it scrubs the package's own override variables
(`FDA_SKIP_MARKETSCAN_PANEL`, `FDA_SAFETY_SIMILARITY_PERCENTILE`,
`FDA_SAFETY_SIMILARITY_PERCENTILES_ROBUST`, `FDA_FORCE_SAFETY_*`, `FDA_SYNTHETIC_MODE`) so that a value
left in your shell cannot change what a driver-run reproduction means; it logs each one it ignores. The
only variables a replicator may need to set are the three macOS R settings under "R packages".

The safety-tagging threshold a run actually applied is recorded twice, so no estimate is silent about
the specification that produced it: in `output/tables/safety_embedding_percentile_used.txt` (one line,
`similarity_percentile=0.99`) and, per percentile, in the `similarity_percentile` column of
`output/tables/safety_embedding_percentile_robustness.csv`, whose first block is that same reported
threshold and whose remaining block is the 95th-percentile robustness the appendix refers to.

The one optional variable is `FDA_SKIP_MARKETSCAN_PANEL=1`, which omits Panel III of Table 1 and skips
the whole price and utilization analysis, printing a banner that says the result is not a complete
reproduction. It exists only for a reader running neither route, and it only has effect when
`code/05_price_analysis.py` or `code/09_summary_stats.py` is invoked DIRECTLY: `run_all.py` removes it
from every step it launches. Without it, step 14 exits non-zero rather than skipping quietly.

**Acceptance.** The run must end with the three tally lines `Succeeded: 36`, `Failed:    0`,
`Skipped:   0` and exit 0. The progress
counter reads `Step N/36 (step table #M)`; see the note on the deferred step above. Each step's combined
standard output and error is kept under `output/logs/`, whether the step succeeded or failed, so a failure
can be diagnosed without re-running the pipeline. `--clean-output` does not touch `output/logs/` or
`output/_cache/`.

### (e) The same route inside the container

To run it exactly as I do, in a network-denied container with no host mounts, use the shipped harness:

```bash
bash certification/certify_fromraw_route.sh \
  --zip /path/to/archive.zip \
  --zip-sha256 <64-lowercase-hex> \
  --image /path/to/fda_np126.sif \
  --image-sha256 <64-lowercase-hex> \
  --workdir /fresh/empty/workdir
```

The harness works on the archive, not on an extracted tree: it needs the `.zip` and its SHA-256 so that
everything it records is bound to one artifact. If you have only an extracted directory, run the commands
in (d) instead; they produce the same outputs.

That is the whole command. `--embed-python-container` is optional and defaults to the image's own
`python3`, resolved inside the container; nothing is bound in from the host for it. (`--apptainer <path>`
overrides the launcher.) The image is self-contained: its own `python3` is the pinned numpy 1.26.4
interpreter that every step, including the safety-embedding step, runs under, so no interpreter has to be
supplied or bound in from the host. The harness itself requires the exact image digest, disables the
network and automatic host mounts, uses empty home, cache and temporary directories, rejects
credential-like environment variables and forbidden mounts, and records the container's mount namespace.

What it does, in order: it verifies the archive's SHA-256 and its member inventory; generates the complete
simulation **twice**, each time with empty read-only mounts hiding both deposited reference trees
(`synthetic_pipeline/simulated_data/` and `output-simulated/`) from the generators, and requires both
generations to match the shipped payload byte-for-byte; empties `output/figures` and `output/tables`
itself; runs the 36 steps in a container that receives neither the archive nor `output-simulated/`; and
only after the analysis has exited does host-side code restore the reference tree and compare. It then
requires all of:

- `36 succeeded / 0 failed / 0 skipped` and process exit 0;
- 52 of 52 figures and 48 of 48 tables present;
- the complete set of finite in-text scalars (see "In-text numbers");
- every step log present with return code 0, and no fallback to an ABI-mode R session or to a remote
  model cache;
- all 283 reference members regenerated byte-identically, with no extra file under `output/figures` or
  `output/tables`;
- the extracted code and the other immutable members unchanged during the run.

A run outside this harness is perfectly valid as a reproduction — it produces the same outputs — but it
produces none of the isolation evidence, which is why the harness exists.

### (f) Compare with `output-simulated/`

`output-simulated/` contains the expected outputs of the simulated run — in this deposit **283 files**,
laid out as `figures/`, `tables/`, `tables/event_study_coefficients/` and `tables/Formatted/`. It is
regenerated together with the deposit, so treat the tree itself, not the count, as the reference.
The simulated run writes into `output/`; compare the two with:

```bash
python3 certification/compare_output_simulated.py --root . --report output/compare_report.txt
```

**The criterion is SHA-256 identity for every member of `output-simulated/`** — 283 of them in this
deposit; the comparator reads the reference tree's own member list rather than a fixed number. The report must print
`missing=0`, `differing=0`, `excused_figures=0`, `unapproved_extra=0` and `missing_required_cache=0`
(the summary spans two lines) and the command must exit 0. No file
other than the 283 members may appear under `output/figures` or `output/tables` after a run: nothing the
pipeline writes there is exempt from the comparison. (Step logs and the NLTK corpus cache go to
`output/logs/` and `output/_cache/`, which the comparator does not read.)

### (g) Figures

Byte identity for the 66 PNGs among those 283 members holds **inside the reference image**, whose `.sif`
hashes to `b9f9ee2a…`. It is not promised anywhere else: outside that image, font and renderer differences
can change PNG bytes while the plotted content is identical. If you run outside the image and the
comparator reports differing PNGs, re-run it in its outside-the-image mode:

```bash
python3 certification/compare_output_simulated.py --root . \
  --report output/compare_report.txt --outside-reference-image
```

That flag changes the criterion for PNG members only: a differing PNG is accepted if it is
pixel-identical, or if it differs within the sub-visual anti-aliasing bound the program documents and
prints per accepted file. Every non-PNG member stays byte-strict, so treat the CSV and TeX members as
byte-exact either way. This is the one place where the acceptance criterion depends on the environment,
and it is why the harness in (e) pins the image by hash. (`certification/compare_exhibit_fidelity.py` is
the corresponding tool on the real-data route; it is bound to the manuscript's own exhibit closure and is
documented under Route 2.)

## Scope of the simulated-data check

Every one of the 36 steps executes on this route, from the first cleaning script to the last output script,
and no script is skipped. Three steps nevertheless run a different implementation than they do on real
data, because the real implementation depends on an external service or on a licensed corpus. They are
listed here so that nothing about this route is implied rather than stated.

| Step | Program | What runs on the simulated data instead | Why |
|---|---|---|---|
| 3 | `code/00_generate_data/gen_03b_lbd_clusters.py` | A deterministic clustering branch; `pandas_dedupe` is not imported and the interactive entity-resolution model is not exercised | The dedupe model is trained on real applicant names; on simulated names it would learn nothing, and its output is not reproducible across environments |
| 8 | `code/00_generate_data/gen_07_adverse_permno.py` | An exact manufacturer-name-to-PERMNO join; the NLTK keyword processing, the fuzzy linkage and the 70 manual CRSP corrections do not run | The manual corrections are a licensed WRDS-derived crosswalk and cannot be redistributed; the simulated names match exactly by construction. The deduplicated manufacturer list `data/derived/All_Adverse_Event_Manufacturers_Deduped.csv` is still written on this route, with one row per distinct manufacturer and confidence 1.0 |
| 10 | `code/12_invention_year_generation.py` | Validation of the shipped invention-year files against the simulated panel; the three generation functions are not called | The invention years are fixed API-derived inputs that no route regenerates — see "API-derived fixed inputs" |

Two exhibits are copied rather than computed, on every route, because they are hand-drawn schematics with
no underlying data: Figure 2 is copied from `manual_figures/Deregulation_May31_23_Paper.png` by
`run_all.py`, and Figure D.2 is copied from `data/raw/Data_new_latest.png` by step 28. Both are documented
under "Exhibits not produced by code" below.

**And the plain statement that matters most: the simulated route verifies only that the code is complete,
runs, and produces every exhibit and in-text number. Its values differ from the published ones by
construction, so no result in the paper or its appendices is checked for reproducibility by that route.**
The published estimates are checked only by the real-data route below.

## Route 2 — the real-data route

For a researcher who holds the MarketScan, Dimensions, WRDS/CRSP-Compustat and Nexis Uni licences.

1. Place the licensed files at the paths given under "Where an authorized researcher places the restricted
   files", in a fresh extraction that has never had simulated data materialized into it.
2. Empty `output/figures/` and `output/tables/`, **except** for the five frozen step-16/17 output tables
   listed under "The frozen output tables" below (`safety_refined_keywords_estimates.csv`,
   `safety_term_share.csv`, `safety_embedding_distance_estimates.csv`,
   `safety_embedding_percentile_robustness.csv`, `safety_embedding_percentile_used.txt`), which must be
   restored from the archive; the driver checks them against `certification/EXPECTED_INTERMEDIATE_HASHES.csv`
   before the run.
3. Run:

   ```bash
   python3 run_all.py --skip-gen --force-estimation --strict-cert
   ```

   `run_all.py` sets `FDA_STRICT_INTEXT=1`, `FDA_INTEXT_ROUTE=real`, `FORCE_ESTIMATION=1` and the
   determinism variables itself. `--strict-cert` turns every frozen-artifact check into a hard failure
   rather than a warning.
4. Of the 36 steps, 25 execute and 11 are skipped — steps 1–8, 10, 16 and 17, for the reasons in "Scope of
   the real-data check" below. **Every executing step succeeds**, including step 35, and the run finishes
   `25 succeeded / 0 failed / 11 skipped`. Step 35 compares each of the 117 in-text scalars with the value
   the manuscript prints, at the precision it prints it, and all 117 agree: see "How the
   manuscript and the package were brought into agreement" below for what moved on each side. A scalar
   that stops agreeing fails the step and takes the run's exit code with it, which is the point of the
   gate.

   `--no-strict-intext` exists for diagnosis only: it makes step 35 record a divergence instead of failing
   on it, and it also stops a missing or non-finite scalar from being fatal. It is not an acceptance run
   and must not be used as the criterion.
5. Compare against the manuscript's own outputs, which ship in `output/`. The first three commands need a
   second, untouched extraction of the same archive to compare against, because the run has overwritten
   `output/` in place; `$REF` below is the root of that untouched extraction.

   ```bash
   python3 certification/compare_all_numbers.py --regen output --committed "$REF/output" \
     --inventory certification/COMPARATOR_INVENTORY.txt --out output/compare_numbers.txt
   python3 certification/compare_exhibit_fidelity.py --regen-root . --reference-root "$REF" \
     --out output/exhibit_fidelity.txt
   python3 certification/verify_intext_report.py --root . --route real
   python3 certification/validate_handentered_tables.py \
     --manuscript paper/JPE_submission_v8.tex --output-dir output/tables
   python3 code/audit_pipeline_current.py
   cd paper && python3 build_manuscript.py JPE_submission_v8.tex
   ```

   A missing, extra, unreadable, shape-changed or numerically different output fails the check. The
   semantic comparison uses a fixed numeric tolerance of 1e-9, and any structural difference — shape,
   columns, strings — fails regardless of tolerance. `compare_exhibit_fidelity.py` is the exhibit gate:
   it takes its reference set from `certification/MANUSCRIPT_CLOSURE.sha256`, so it covers exactly the
   tables and figures the manuscript displays — all 48 table fragments and all 52 figure panels,
   counting both the `\includegraphics` figures and the panels drawn with `\begin{overpic}`; it
   compares tables byte-for-byte and figures
   pixel-for-pixel, and its last line is `EXHIBIT_FIDELITY_FAILURES=0` on a clean run.
   `verify_intext_report.py --route real` exits 0 on a clean run and exits 1 if any scalar in the report
   is missing, non-finite or outside the value the manuscript prints — the same finding as step 35's,
   reported after the fact.

Run each provider's data in the environment its licence permits. MarketScan acquisition runs at NBER;
Nexis follows the granted exemption route; Dimensions and WRDS follow their documented provider routes. Do
not consolidate restricted sources onto one machine unless every licence permits it.

`certification/compare_all_numbers.py` is the cell-by-cell comparison over the 152 CSVs listed in
`certification/COMPARATOR_INVENTORY.txt`. It requires byte identity by default; `--allow-numeric-equal`
accepts cells that are numerically equal but formatted differently, and any numeric difference fails it.
It refuses to run against an inventory of any other length, so the two cannot drift apart. Outside the
reference image small floating-point differences (of order 1e-14 in some event-study CSVs) are expected,
so a FAIL from this comparator outside the image is informative rather than disqualifying; the
tolerance-based semantic comparison that gates certification runs inside the authorized certification
harness and is not part of the deposit.

## Route 3 — the real-data route from raw

For the same researcher as Route 2, when the question is whether the derived analysis files themselves
rebuild from the licensed raw extracts. Route 2 starts from those derived files, which ship; this route
rebuilds them first and then runs the same analysis on what it has rebuilt, so it executes the generation
phase (steps 1–8) that Route 2 skips. It therefore needs every licensed **raw** extract behind the derived
panels, not only the panels themselves, at the paths given under "Where an authorized researcher places
the restricted files".

1. Start from a fresh extraction holding the licensed raw inputs, as in Route 2, and empty
   `output/figures/` and `output/tables/` except for the five frozen step-16/17 tables listed under "The
   frozen output tables", which must be restored from the archive.
2. Remove the three fuzzy-dedup outputs that ship under `data/raw/` — `unique_firms_thr_75.csv`,
   `unique_firms_in_PC_thr_75.csv` and `unique_devices_thr_75.csv` — so that the second phase of step 1
   rebuilds them instead of reusing them. Left in place, that phase refuses and names them, for the reason
   under "Reuse of the shipped dedup artifacts on a from-raw run"; `FDA_REUSE_FROZEN_DEDUP=1` reuses them
   deliberately instead. Rebuilding them takes hours.
3. `data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv` is omitted from the package for size rather than
   rights, and step 8 rebuilds it from the 23 public MAUDE files that do ship, verifying the digest before
   it proceeds. Nothing has to be done by hand; see "One input is omitted for size, not for rights".
4. Run:

   ```bash
   python3 run_all.py --real-from-raw --force-estimation --strict-cert
   ```

   The flag is mutually exclusive with `--skip-gen` and with `--synthetic-from-raw`, and the driver
   refuses either combination rather than guessing. As on Route 2, `run_all.py` sets
   `FDA_INTEXT_ROUTE=real`, `FDA_STRICT_INTEXT=1`, `FORCE_ESTIMATION=1` and the determinism variables
   itself.
5. Of the 36 steps, 31 execute and 5 are skipped — steps 3, 4, 10, 16 and 17, each of which prints its own
   reason when it is skipped. These are the default frozen artifacts described under "Why four artifacts
   are frozen rather than regenerated": the two entity-resolution artifacts, the invention-year files, and
   the two high-memory text models. `--regenerate-lbd`, `--regenerate-safety-keywords` and
   `--regenerate-safety-embeddings` run them, each at a cost of hours. **Every executing step succeeds**
   and the run finishes `31 succeeded / 0 failed / 5 skipped`. Step 35 compares each of the 117 in-text
   scalars with the value the manuscript prints, at the precision it prints it, and all 117 agree — the
   same criterion as Route 2, and a scalar that stops agreeing fails the step and takes the run's exit
   code with it.
6. Compare with the same commands as Route 2, against a second untouched extraction. One comparison is
   worth adding here, because this is the only route that writes to `data/`: take

   ```bash
   find data output -type f -print0 | sort -z | xargs -0 sha256sum
   ```

   before the run and again after it, and compare the two listings. Use the null-delimited form. Sixty-nine
   of the files under `data/raw/` have spaces in their names, and a plain `find | xargs sha256sum` splits
   on those, dropping them from the listing and hashing fragments in their place — so the ordinary
   pipeline reports a clean comparison over a set that quietly excludes them.

**What this route reproduces.** Every number the manuscript prints, at the precision it prints it. Of the
files, 358 of the 363 under `data/` and 259 of the 283 under `output/` come back byte-identical. The five
under `data/` are the three dedup artifacts and their extra `DECISIONDATE` column, the deposited
`Applicant_Device_data.csv` — which had been round-tripped through a spreadsheet program before deposit,
so the rebuilt copy is the more faithful of the two — and the dedupe `confidence` column of
`All_Adverse_Event_Manufacturers_Deduped.csv`, whose manufacturer names and cluster assignments are
byte-identical. All three are stated precisely under "Why a few bytes still differ, stated precisely".
Of the 24 under `output/`, 19 are tables differing only in the trailing digits of their floating-point
fields, the largest absolute difference anywhere being 1.6e-13, and four are figures of identical
dimensions differing by antialiasing on lines that moved by those quantities — between 29 and 316 bytes
of some 30 million decompressed image bytes, which is why a byte count on the compressed file says
nothing useful here.

The twenty-fourth is `output/tables/intext_numbers_report.csv`, and it differs because it records the
tree it was produced in, which is also why it is not among the hash-pinned exhibits. It holds 117 rows
here rather than 118: the row the program emits only when the restricted Class II sample is absent is not
emitted on a route that rebuilds that sample. Three of its values move within the precision the
manuscript prints — two entry quantities that count distinct entering firms, and one standard error
whose point estimate does not move — and nine of its note strings differ in wording. No status changes:
all 117 agree.

## Expected numerical differences across environments

What I have measured, so that a replicator can tell an expected difference from a defect:

- **On the original macOS environment** (x86_64 R 4.0.1, `fixest` 0.12.1, numpy 1.26.4, Accelerate BLAS),
  a forced full re-estimation — deleting the roughly 100 estimate CSVs so they are recomputed from the
  derived data rather than reused — reproduces the estimation outputs **byte-for-byte**: point-estimate
  maximum absolute difference 0.0000, and no sign or significance change anywhere.
- **On native x86_64 Linux with the container recipe** (R 4.1.3, `fixest` 0.10.4, OpenBLAS), all 50
  formatted manuscript tables also reproduced byte-for-byte. The only non-identical committed CSVs were 15
  full-precision intermediate files differing in the last floating-point digits (maximum absolute
  difference 7.2e-14); no formatted table is affected.
- **Inside the reference image**, a full real-data run from empty outputs reproduced all 50 formatted
  tables byte-identically, and the strict byte comparator matched 120 of the 130 files then under
  comparison. The other 10 were
  event-study coefficient CSVs within 4.44e-14 of the committed values, with no sign or significance
  change — numerical equivalence rather than byte identity. The semantic comparison passed.
- **An earlier ~0.1–0.6 percent discrepancy** that a previous version of this README reported came from
  running the container under x86_64 emulation on an Apple-silicon Mac. It does not occur on native x86_64
  Linux, where every formatted table was byte-identical and the level utilization estimate is 959,632.322
  in both environments. Do not run the container under emulation for a reproduction.
- **Limits.** All of these tests ran on one CPU family. Forcing five different OpenBLAS kernels, including
  SSE-only ones, and the reference BLAS, left the Class III→II estimation step byte-identical, which
  suggests other x86_64 CPUs behave the same; I have not tested one.
- Mahalanobis matching can in principle select a slightly different control set across platforms, through
  floating-point tie-breaks in without-replacement selection. In the native-Linux run, every formatted
  table built on the matched samples was byte-identical.

## Two hand-coded adjustments to the MarketScan claims extract

`code/05_price_analysis.py:load_claims_data()` applies two corrections to the outpatient claims
extract before any price panel is built, and `code/00_generate_data/gen_02_price_matching.py` applies
the same two to the panels it exports. Both are deliberate and both are visible in the code; they are
set out here because a replicator rebuilding the extract will not reproduce the published price
estimates without them.

1. **CPT 52336 → 52352.** CPT 52336 (cystourethroscopy with ureteroscopy) was retired and replaced by
   52352 during the sample period: in the extract, 52336's claims run 1996–2002 and 52352's begin in
   2001. Claims billed under 52336 before 2001 are relabelled 52352, and all remaining 52336 rows are
   dropped, so one procedure is not split across two codes at an arbitrary point in the panel.

2. **Product code MLM's 1996 cell is carried back from 1997.** The procedure the concordance maps to
   MLM, CPT 80197 (tacrolimus assay), has no 1996 claims in the extract; its claims begin in 1997.
   MLM's 1996 cell is therefore filled with its 1997 values, the same backfill rule the panel applies
   to interior gaps. MLM was reclassified in 2002, so the carried-back cell sits at event time −6, in
   the pre-period. The source row is selected by minimum year, not by position in the input file.

   This row matters, which is why it is stated here rather than left in a comment. It is not the
   same as the panel's own backfill: the carried-back claims row enters the procedure-level price
   matching and the sample-construction counts before any panel is built, and MLM is one of only
   three treated product codes in the III→II price panel. Measured on the real data, without it the
   III→II price sample and matched controls change and so do the III→II rows of
   `output/tables/price_utilization_estimates.csv`, including the expert-concordance estimate the
   price section reports (−0.09, which would be −0.08 without the row). The II→I results, including
   the 32 percent II→I price decline, do not depend on it: MLM is a III→II product code.

   Note also that 742 other procedure codes in the extract first appear in 1997 and 9,279 first
   appear later still, so a procedure code whose claims begin after 1996 is ordinary; MLM is carried
   back because it is a treated unit in a three-unit panel, not because its gap is unusual.

## Scope of the real-data check (JPE Policy 2.2 and 4.3)

The real-data check is narrower than the simulated one: it is a partial check in the sense of JPE policy
2.2. It runs `run_all.py --skip-gen --force-estimation --strict-cert` on the authorized real data,
regenerates every estimate, figure, table and in-text number (25 steps), and compares each with the
committed outputs in `output/`. It takes the following as given instead of regenerating them from the
licensed source data:

- **The derived real data built by steps 1–8** (`code/00_generate_data/gen_*.py`: the analysis panels, the
  price matching, the learning-by-doing dedupe clusters and approval-time panel, and the adverse-event firm
  links). This route starts from their outputs, which are hash-bound in its authorized-overlay manifest.
  Running these raw-to-derived transformations on the real data belongs to the per-provider real-data
  routes, where each provider's raw data stay in its licensed environment and MarketScan's claim-level data
  never leave NBER. The learning-by-doing dedupe output is frozen in any case, because `pandas_dedupe` is
  not guaranteed to reproduce it across environments. One of these outputs,
  `data/derived/Applicant_Device_data.csv`, is written by step 1 from the two public FDA registries, so a
  replicator does not supply it.
- **Step 10, the invention-year files.** They are static API-derived inputs; the program is kept for
  provenance and is not run.
- **Steps 16–17, the safety robustness checks** (refined keywords with Word2Vec, and embedding distance
  with a sentence-transformer). They read the restricted patent texts, which cannot be redistributed, so
  their outputs ship as precomputed artifacts: the three data files and two output tables listed below.
  The programs ship and can be rerun with `--regenerate-safety-keywords` and
  `--regenerate-safety-embeddings`. Both reproduce on the restricted inputs; what a rerun gives is
  recorded under "What a rerun of steps 16, 17 and 22 gives".
- **Step 22's LDA topic models (14 files).** LDA fitting is not bitwise portable across environments, so a
  retrain, even with the same seed, is not guaranteed to reproduce the shipped models or Figure D.5; the
  cached models are frozen inputs (see "Why four artifacts are frozen rather than regenerated").

The frozen real-data inputs, which `run_all.py` checks against
`certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv` before any step runs — a changed file is fatal, and
so is a missing one under `--strict-cert`:

```text
data/derived/safety_tagged_patents.csv
data/derived/safety_vars_allpats_v2.csv
data/derived/safety_vars_allpats_updated_v2.csv
data/derived/lda_2to1.model
data/derived/lda_2to1.model.expElogbeta.npy
data/derived/lda_2to1.model.id2word
data/derived/lda_2to1.model.state
data/derived/lda_3to2.model
data/derived/lda_3to2.model.expElogbeta.npy
data/derived/lda_3to2.model.id2word
data/derived/lda_3to2.model.state
data/derived/lda_bigram_2to1.model
data/derived/lda_bigram_3to2.model
data/derived/lda_dictionary_2to1.dict
data/derived/lda_dictionary_3to2.dict
data/derived/lda_trigram_2to1.model
data/derived/lda_trigram_3to2.model
```

The frozen output tables, restored after clearing `output/` and checked against
`certification/EXPECTED_INTERMEDIATE_HASHES.csv`:

```text
output/tables/safety_refined_keywords_estimates.csv         (step 16)
output/tables/safety_term_share.csv                         (step 16)
output/tables/safety_embedding_distance_estimates.csv       (step 17)
output/tables/safety_embedding_percentile_robustness.csv    (step 17)
output/tables/safety_embedding_percentile_used.txt          (step 17)
```

The set is defined once, as `FROZEN_SAFETY_OUTPUT_TABLES` in `run_all.py`; the certification harness reads it
from there.

### One input is omitted for size, not for rights

`data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv` is not in the package. It is 306 MB, and it is a
plain two-column projection (`MDR_REPORT_KEY`, `MANUFACTURER_D_NAME`) of the 23 public FDA MAUDE device
files that *are* in the package, under `data/raw/MAUDE/device_data/`. Nothing in it is restricted; I left
it out only to keep the archive to a reasonable size, and I note it here as an omission under policy 4.3.

Unlike the frozen inputs above, this one does not have to be taken on trust. To rebuild and check it:

```bash
python3 certification/verify_maude_manufacturer_rebuild.py --root .
# or, to rebuild it in place before a from-raw run:
python3 code/00_generate_data/gen_07_adverse_permno.py --rebuild-manufacturer-list
```

The rebuild reproduces the file I used **byte for byte**: 9,238,809 rows, 305,836,795 bytes, SHA-256
`8833a9a01599c145f84274cfabdf9d9d87ac8ddd897115d7a428ed28dd768f19`. The verifier first confirms all 23
source files against `certification/PUBLIC_INPUT_HASHES.csv`, then rebuilds and compares the digest, and
exits non-zero if either check fails. `gen_07_adverse_permno.py` runs the same rebuild automatically if
the file is absent, and raises rather than proceeding if the result does not match the digest.

Two details are worth stating, because they are why this needs a manifest rather than a one-line loop.
The source files must be concatenated in the order recorded in
`certification/MAUDE_MFR_SOURCE_ORDER.txt`, which is *not* alphabetical: the file was written by a
program that iterated the directory without sorting it, so the row order is the order that machine
returned. And the order is load-bearing rather than cosmetic, because `gen_07` takes
`drop_duplicates("MANUFACTURER_D_NAME")`, which keeps the first occurrence, before handing the names to
`pandas_dedupe`. A rebuild in a different order holds exactly the same 9,238,809 rows but can cluster
them differently, so the order is pinned and verified instead of normalised. Reading the files in the
pinned order under the pinned `pandas` 2.3.3 is fully deterministic; the parse discards 37,397 malformed
source lines, which is what `on_bad_lines="skip"` is there for.

**What each route re-derives (policy 4.3).** The simulated-data route runs the whole pipeline, steps 1–36,
from raw simulated inputs: nothing is taken as given there. Route 2 is a partial check in the
sense of policy 2.2: its command passes `--skip-gen`, so it starts from the derived real data
and takes as given the raw-to-derived construction (steps 1–8), the invention-year files (step 10), the
safety robustness artifacts (steps 16–17) and the LDA topic models. Every estimate, figure, table and
in-text number built on them is regenerated on the real data and compared with the published outputs.
Route 3 moves that boundary: it runs steps 1—8 on the licensed raw extracts, so the raw-to-derived
construction is re-derived by a documented command rather than taken as given. What stays frozen there is
narrower — the two entity-resolution artifacts, the invention-year files and the two high-memory text
models, five skipped steps in all.
The reason Route 2 is the documented default is practical rather than evidentiary: the MarketScan
claim-level data never leave NBER, the fuzzy dedup takes hours, and the two API-derived inputs cannot be
re-queried. The
programs themselves all ship, and each has been verified on the real data — see below.

**Steps 1–8 are not, however, unexamined — every one of the seven `gen_*` programs has been run on the
real data and its outputs compared.** I did this two ways, because they answer different questions.

*Per program.* Each of `gen_01` through `gen_07` was run on its own against the authorized inputs inside
the reference image, and every file it declares was compared byte for byte with the authorized copy
(8 cores, `PYTHONHASHSEED=0`):

| program | outcome |
|---|---|
| `gen_02_price_matching.py` | both panels byte-identical |
| `gen_03_lbd.py` | `LBD_ApprovalTime_Both_oct22_24.csv` byte-identical |
| `gen_04_parquets.py` | all four `data_2_1_*.parquet` byte-identical |
| `gen_05_adverse_fsize.py` | `Adverse_fsize_ready_all4_oct22_24.csv` byte-identical (1.2 GB) |
| `gen_06_adv_2020.py` | `Adv_Event_2020_2022.csv` byte-identical |
| `gen_07_adverse_permno.py` | `all_adv_events_w_permno5.csv` byte-identical (9.1 M rows); `All_Adverse_Event_Manufacturers_Deduped.csv` differs by 82 bytes of floating-point noise in the dedupe confidence column, which nothing downstream reads |
| `gen_03b_lbd_clusters.py` | identical clustering — 147,691 and 32,087 clusters, the same records in the same groups, and every column byte-equal except the arbitrary integer `cluster id` labels and `confidence` at the eighth decimal |
| `gen_01_main_panels.py` | 14 of its 15 outputs byte-identical; with the fuzzy dedup forced to re-derive rather than reuse, the three `unique_*_thr_75.csv` reproduce their row counts exactly (14,092 / 68,515 / 107,501) and `unique_firms_thr_75.csv` is identical in every shared cell |

*As a chain.* Steps 1–8 have also been run end to end from the raw extracts on the real data, in the
reference image. This is what Route 3 does, and it runs as a documented command rather than as a test
harness. Twenty-nine of the thirty-eight derived files the chain regenerates came back byte-identical to
the authorized copies. Of the nine that did not, three are the fuzzy-dedup artifacts carrying the extra
`DECISIONDATE` column and one is step 17's intermediate — both accounted for below — and the remaining
five were an artifact of an early test that had excluded one of its own inputs: with that input present
`gen_07`'s output is byte-identical and the chain returns `safety_did` = **48,703** patents over 9,856
rows, the manuscript's figures exactly. Run as Route 3 over the whole pipeline rather than over steps
1–8 alone, 358 of the 363 files under `data/` and 259 of the 283 under `output/` come back
byte-identical and all 117 in-text scalars agree with the values the manuscript prints.

**Why a few bytes still differ, stated precisely.** Three residuals survive, and none of them is the
pipeline behaving unpredictably:

1. The three fuzzy-dedup artifacts — `data/raw/unique_firms_thr_75.csv`, `unique_firms_in_PC_thr_75.csv`
   and `unique_devices_thr_75.csv` — ship as files. Re-deriving them from the deposited input reproduces
   the clustering **exactly**: identical row counts (14,092 / 68,515 / 107,501), the same records in the
   same groups, and the same number of clusters, so no firm or device count moves. The re-derived files
   carry one additional column, `DECISIONDATE`, which no program reads from them. Dropping that column
   makes `unique_firms_thr_75.csv` byte-identical to the deposited copy. The other two still differ in
   seven `DEVICENAME` strings in total — three cells of 616,635 in `unique_firms_in_PC_thr_75.csv` and
   four of 967,509 in `unique_devices_thr_75.csv` — and the reason is worth stating. The deposited copies
   were built from a version of `Applicant_Device_data.csv` that had been round-tripped through a
   spreadsheet program, which dropped an internal space from a few device names; step 1 now rebuilds that
   input from the two public FDA registries and keeps the registry spelling, so on this point the
   regenerated files are the more faithful of the two. `DEVICENAME` is one of the three dedup keys, so a
   changed string is not cosmetic in principle. Here it changed nothing: the groups, the number of
   clusters and all three counts step 9 reports from these files are identical either way.
2. `gen_03b_lbd_clusters.py` numbers its clusters differently from run to run while grouping the same
   records identically; `cluster id` is an arbitrary label, and no downstream step depends on its value.
3. `gen_07`'s `All_Adverse_Event_Manufacturers_Deduped.csv` differs in the dedupe confidence column at
   about 5e-07, which does not propagate.

The fuzzy dedup is the one place worth a caution rather than a result: it runs multi-process on the
real-data path (`n_jobs=-1`, `gen_01_main_panels.py:356`) over a sort with many date ties, so the
reproduction above is evidence at eight cores in the reference image and not a guarantee at every core
count. That is why the three artifacts ship and are reused by default rather than rebuilt, and why
`FDA_REUSE_FROZEN_DEDUP=1` has to be set deliberately.

**What a rerun of steps 16, 17 and 22 gives.** All three have been rerun on the restricted inputs in the
reference container, and the answer differs by step.

Step 16, the refined-keyword check, reproduces: both frozen data files and both output tables come back
byte-identical to the shipped copies. Its Word2Vec call uses four worker threads and no seed, so the
fitted model itself is not reproducible run to run, but that jitter reaches neither the tagged output nor
any published number.

Step 17, the embedding-distance check, reproduces: all three output tables come back byte-identical. Its
intermediate `data/derived/safety_tagged_patents.csv` differs in the last digits of `safety_similarity`
(largest absolute difference 4.9e-07 across 1,248,292 rows) and in no `safety_tag` at all — both copies
tag the same 12,483 patents. The sentence-transformer is not an unpinned external dependency: the model
snapshot ships in `models/all-MiniLM-L6-v2/` and is loaded offline.

Both steps therefore ship precomputed because they read restricted patent texts I cannot redistribute,
which is a limit on access rather than on reproducibility.

The step-22 LDA models are the genuine exception: they retrain, but fitting is not bitwise portable
across environments, so a retrain even with the same seed is not guaranteed to reproduce the shipped
models or Figure D.5. They are frozen and hash-pinned for that reason.

One further set of numbers is outside the reproducibility check entirely: the **six concordance-accuracy
figures** in the paper's price-data footnote (80 % against 75 %; 78/100 against 43/100; 85/100 against
48/100). They come from a hand-tabulated comparison of the two shipped concordances judged by three
chatbot models, whose outputs are not deterministic and whose session records I did not retain. No program
in this package produces them, they are not in
`certification/INTEXT_NUMBER_INVENTORY.txt`, and no gate asserts them. The exercise is described in full
under "The concordance accuracy comparison" above; the price estimates themselves are computed on both
concordances and are checked like every other estimate.

## What the driver refuses to do, and why

1. No route flag on a tree without the restricted derived data: it exits before step 1 and prints the two
   routes, because a bare `python3 run_all.py` is not a reproduction command.
2. `--synthetic-from-raw` while `output/figures` or `output/tables` holds any file: it tells you to delete
   them or pass `--clean-output`.
3. `--synthetic-from-raw` together with `--skip-gen`, or with `--from-step`: that route must run complete.
4. `--from-step N` where N is not a step the selected route executes: it lists the valid numbers.
5. A frozen artifact that exists but is unmanifested or hash-mismatched — and, under `--strict-cert`, a
   pinned frozen artifact that is MISSING and that this run does not regenerate.
6. `--clean-output` when it would delete any of the five frozen step-16/17 output tables without the
   matching `--regenerate-safety-keywords` / `--regenerate-safety-embeddings`: they are pinned frozen
   artifacts, steps 16 and 17 are skipped as precomputed without the flags, and the deleted file could
   not be rebuilt. The simulated-data route passes both flags, so this only affects a real-data
   `--clean-output` run.

`--continue-on-fail` exists for development and must not be used for a reproduction: it hides exactly the
failures the run is meant to surface. The same is true of `--no-strict-intext`, `--skip-estimation`,
`--audit-only`, `--from-step` and `--regenerate-lbd`, all of which the driver's own help labels
development-only.

## How the routes relate

The simulated-data route establishes that all of the code executes and that every exhibit and in-text
number in the paper regenerates without any restricted data. Route 2 establishes that the paper's
estimates reproduce from the derived data. Route 3 establishes that the derived data themselves rebuild
from the licensed raw extracts, so that the construction behind the estimates is checked rather than
assumed. A separate audit, which needs the restricted counterparts and therefore runs
only in an authorized environment, establishes that the simulated release discloses nothing:
`python3 synthetic_pipeline/audit_simulated_data.py` is the fail-closed real-versus-simulated test for
value copies, exact statistics, preserved co-membership and preserved missingness. The four answer
different questions and none substitutes for another.

---

# List of tables and figures

The manuscript references 52 figure files and 48 table files, produced by the programs below. Step 36
(`code/audit_pipeline_current.py`) re-checks this mapping at the end of every run: it resolves every
`\includegraphics` and `\input` in `paper/JPE_submission_v8.tex` against `output/`, names the producing
program for each, and exits non-zero if any reference is missing or has no known producer. Its HTML report
lands at `output/replication_audit.html`. On a completed run it prints `52 refs, 52 covered, 0 missing`
for figures and `48 refs, 48 covered, 0 missing` for tables.

Figures are written to `output/figures/`; formatted tables are written to `output/tables/Formatted/` and
`\input` into the manuscript, except the two summary-statistics tables, which are written to
`output/tables/`. `{2_1, 3_2}` denotes the Class II→I and Class III→II panels.

## Figures

| Fig. | Title | Program(s) (step) | Output file(s) in `output/figures/` |
|---|---|---|---|
| 1 | Contact Lens Case Study | `12_contact_lens_case_study.py` (32) | `ContactLens_patents.png`, `ContactLens_submissions.png`, `ContactLens_firms.png` |
| 2 | Background on Medical Device Regulations | *not script-generated* — copied by `run_all.py` from `manual_figures/` | `Deregulation_May31_23_Paper.png` |
| 3 | Effect of Reclassification on Innovation | `04_event_studies.py` (13) | `3_2_nolog_real_pats_oct22_24.png`, `3_2_nolog_dev_count_oct22_24.png`, `2_1_nolog_real_pats_oct22_24.png`, `2_1_nolog_dev_count_solo.png` |
| 4 | Effects of Reclassification on Market Structure | `04_event_studies.py` (13) for firms; `05_price_analysis.py` (14) for prices | `3_2_nolog_unique_firms_solo_CTs.png`, `2_1_nolog_unique_firms_oct22_24.png`, `3_2_nolog_Price_solo_CTs_sept20_25.png`, `2_1_nolog_Price_solo_CTs_sept20_25.png` |
| 5 | Effects of Reclassification on Product Safety | `04_event_studies.py` (13) | `3_2_nolog_v_serious_oct22_24.png`, `2_1_nolog_v_serious_oct22_24.png`, `2_1_nolog_v_serious_normalizable_oct22_24.png`, `2_1_nolog_v_serious_restrict_oct22_24.png` |
| 6 | Change in Product Safety by Firm Asset Terciles (II→I) | `07_firm_heterogeneity.py` (18) | `2_1_Safety_Top_Decile_Present_oct22_24.png`, `2_1_Deaths_Top_Decile_oct22_24.png` |
| D.1 | Temporal Distribution of Reclassification Events | `11f_reg_background.py` (27) | `Distribution_of_3_2_over_years.png`, `Distribution_of_2_1_over_years.png` |
| D.2 | Data Catalog | *not script-generated* — copied by `11g_descriptive_figures.py` (28) from `data/raw/Data_new_latest.png` | `Data_new_latest.png` |
| D.3 | Petitioned Down-Regulation Events | `04_event_studies.py` (13) | `3_2_nolog_real_pats_petitioned_oct22_24.png` |
| D.4 | Reclassification and Market Structure (Incumbent and New Entry) | `04_event_studies.py` (13) | `3_2_nolog_absnew_firm_count_oct22_24.png`, `3_2_nolog_firm_expansion_oct22_24.png`, `3_2_nolog_firm_expansion_patents_oct22_24.png`, `2_1_nolog_firm_expansion_patents_oct22_24.png` |
| D.5 | Product Variety, Complexity, and Quality | `11a_product_variety.py` (22) | `variety_3_2.png`, `variety_2_1.png` |
| D.6 | Effects on Innovation by Experience | `08_lbd_simulation.py` (19) | `LBDEstimation.png`, `LBDEstimation_ProductCount.png` |
| D.7 | Patenting Rates by Asset Terciles | `07_firm_heterogeneity.py` (18) | `3_2_smallvlarge.png`, `2_1_smallvlarge.png` |
| D.8 | Impact of Class II→I Events on Safety Emphasis | `06a_safety_analysis.py` (15) for the raw trends; `04_event_studies.py` (13) for panel (b) | `Safety_emphasis_raw_trends.png`, `2_1_nolog_safety_prop_oct22_24.png` |
| D.9 | Evolution of the Medical Device Legal Environment | `11c_liability.py` (24) | `cases_preemption.png`, `Bankruptcy_1996_raw_trend.png` |
| D.10 | How Impacts Vary with Device Market Age | `11d_reg_design.py` (25) | `exp_vs_impact_v_serious_est_3_2.png`, `exp_vs_impact_patent_est_3_2.png`, `exp_vs_impact_v_serious_est_2_1.png`, `exp_vs_impact_patent_est_2_1.png` |
| D.11 | Histogram, Years of Experience With Current Class | `11d_reg_design.py` (25) | `Distribution_of_3_over_years.png`, `Distribution_of_2_over_years.png` |
| D.12 | Class III→II Patenting Rates: Restricted | `04_event_studies.py` (13) | `3_2_nolog_patents_pats_nodrugs_oct22_24.png` |
| D.13 | Device Recall Analysis — Class II→I | `11b_recall_analysis.py` (23) | `Recalls_1996_raw_trend.png`, `Recalls_1996_raw_trend_intuitive.png`, `2_1_no_log_recalls_1996.png` |
| D.14 | Safety and Recalls After Deregulation — Class II→I (2015) | `11b_recall_analysis.py` (23); `04_event_studies.py` (13) | `2_1_no_logv_serious_2016_oct22_24.png`, `Recalls_2017.png`, `Recalls_2017_raw_trends.png` |
| D.15 | Effects of the 2015 Class II→I Event on New Entry | `11e_new_entry_2015.py` (26) | `NewFirmsPatenting_2017.png` |
| D.16 | Serious Adverse Event Changes by Reporter Type | `04_event_studies.py` (13) | `2_1_nolog_v_serious_voluntary_oct22_24.png`, `2_1_nolog_v_serious_manuf_oct22_24.png` |

## Tables

| Table | Title | Program(s) (step) | Output file(s) |
|---|---|---|---|
| 1 | Summary Statistics | `09_summary_stats.py` (20) | `output/tables/Table_1_summary_stats.tex` |
| 2 | Effect of Reclassification on Innovation | `10_table_formatting.py` (21) | `Formatted/PaperRegTable2_1_Main_Panel_NoLog_oct22_24.tex`, `Formatted/PaperRegTable3_2_Main_Panel_NoLog_oct22_24.tex` |
| 3 | Effect of Reclassification on Market Structure | `10_table_formatting.py` (21); `05_price_analysis.py` (14) for the price rows | `Formatted/PaperRegTable{2_1,3_2}_MarketComposition_NoLog_oct22_24.tex`, `Formatted/RegTable_Prices_{2_1,3_2}_sep25.tex` |
| 4 | Effect of Reclassification on Adverse Events | `10_table_formatting.py` (21) | `Formatted/PaperRegTable{2_1,3_2}_AdverseEvent_NoLog_oct22_24.tex`, `Formatted/PaperRegTableSafety_{IItoI,IIItoII}_NoLog.tex` |
| D.1 | Treated Sample Construction and Coverage | `10c_generate_appendix_tables.py` (via step 35) | `Formatted/TableD1_SampleConstruction.tex` |
| D.2 | Class III→II Down-Regulated Device Types | *author-constructed catalog; not script-generated* | inline in the manuscript |
| D.3 | Treated Device Type to Procedure Linkages | *author-constructed catalog; not script-generated* | inline in the manuscript |
| D.4 | Robustness Matrix: Innovation | `10_table_formatting.py` (21) | `Formatted/PaperRegTable{2_1,3_2}_Main_Panel_{Log,NoLog_poisson}_oct22_24.tex`, `Formatted/DIDimpute_PaperRegTable{2_1,3_2}_Main_Panel_NoLog_oct22_24.tex` |
| D.5 | Robustness Matrix: Market Structure | `10_table_formatting.py` (21); `05_price_analysis.py` (14) | `Formatted/PaperRegTable{2_1,3_2}_MarketComposition_{Log,NoLog_poisson}_oct22_24.tex`, `Formatted/DIDimpute_PaperRegTable{2_1,3_2}_MarketComposition_NoLog_oct22_24.tex`, `Formatted/DIDimpute_RegTable_Prices_{2_1,3_2}_sep25.tex` |
| D.6 | Robustness Matrix: Adverse Events | `10_table_formatting.py` (21) | `Formatted/PaperRegTable{2_1,3_2}_AdverseEvent_{Log,NoLog_poisson}_oct22_24.tex`, `Formatted/DIDimpute_PaperRegTable{2_1,3_2}_AdverseEvent_NoLog_oct22_24.tex` |
| D.7 | Reclassification Spillovers (Innovation) | `10_table_formatting.py` (21) | `Formatted/PaperRegTableSpillovers_{2_1,3_2}_Spillovers_NoLog.tex` |
| D.8 | Class III→II Device Types by Broad Category | *author-constructed catalog; not script-generated* | inline in the manuscript |
| D.9 | Class II→I Device Types by Broad Category | *author-constructed catalog; not script-generated* | inline in the manuscript |
| D.10 | Effects Excluding Zero-Count Product Codes | `10_table_formatting.py` (21) | `Formatted/PaperRegTable{2_1,3_2}_{Main_Panel,MarketComposition,AdverseEvent}_NoLog_No0_oct22_24.tex` |
| D.11 | Effect on Log Procedure Utilization | `10c_generate_appendix_tables.py` (via step 35), assembling `05_price_analysis.py` (14) output | `Formatted/TableD11_Utilization.tex` |
| D.12 | Probability of Any Safety Mention | `06b_validate_safety.py` (16); formatted by `10b_format_remaining_tables.py` (31) | `Formatted/TableD12_SafetyRobustness.tex` |
| D.13 | Impacts and Device Experience (III→II) | `11d_reg_design.py` (25); formatted by `10b_format_remaining_tables.py` (31) | `Formatted/TableD11a_DeviceExperience_3_2.tex` |
| D.14 | Impacts and Device Experience (II→I) | `11d_reg_design.py` (25); formatted by `10b_format_remaining_tables.py` (31) | `Formatted/TableD11b_DeviceExperience_2_1.tex` |
| D.15 | Costs and Benefits of Reclassification | `10c_generate_appendix_tables.py` (via step 35), from `16_total_patent_value_did.py` (34) and the adverse-event outputs | `Formatted/TableD15_CostBenefit.tex` |
| D.16 | Summary Statistics by FDA Class | `09_summary_stats.py` (20) | `output/tables/Table_D14_summary_stats_by_class.tex` |
| D.17 | Patenting Rates: Restricted Sample | `13_restricted_samples.py` (29) | `Formatted/TableD15_RestrictedSamples.tex` |
| D.18 | Effect on Breakthrough Patents | `14_breakthrough_patents.py` (30) | `Formatted/TableD16_BreakthroughPatents.tex` |

Several output filenames carry a historical number that no longer matches the manuscript number:
`TableD11a_DeviceExperience_3_2.tex` and `TableD11b_DeviceExperience_2_1.tex` are Tables D.13 and D.14,
`TableD15_RestrictedSamples.tex` is Table D.17, `TableD16_BreakthroughPatents.tex` is Table D.18, and
`Table_D14_summary_stats_by_class.tex` is Table D.16. I have left the filenames as the code writes them
rather than renaming outputs late; the table above is the authoritative map, and step 36 checks it against
the manuscript on every run.

### Outputs that are not manuscript exhibits

The pipeline also writes files that no exhibit `\input`s or `\includegraphics`es. They are the numeric
backing for statements in the text, or diagnostics I keep because they were used in developing the paper.
Almost all of them are inventoried and hash-pinned like every other output, so a run that fails to produce
one fails. Six are not, because their content is route-dependent: `intext_numbers_report.csv` records the
comparison the run itself made, `cost_benefit_total_value_did.csv` and the four `model_*_est_*.csv`
coefficient exports are re-derived on every run. On the simulated-data route all six are members of
`output-simulated/` and are covered byte-for-byte by `compare_output_simulated.py`; on the real-data route
they are checked by `verify_intext_report.py` and by the appendix-table validator rather than by a hash.
The main ones are `output/tables/event_study_base_rates.csv` (the printed base-rate overlays; see below),
`price_sample_construction.csv`, `dpm_decile_ratio.csv`, `recall_event_study_1996.csv`,
`recall_in_text_numbers.csv`, `new_entry_2015_event_study.csv`, `new_entry_2015_in_text.csv`,
`safety_term_share.csv`, `safety_embedding_percentile_robustness.csv`,
`contact_lens_case_study_ratios.csv`, `BreakthroughPanel_distribution.csv`,
`PatentCollectionCounts.csv`, `intext_numbers_report.csv`, the 28 event-study coefficient files under
`output/tables/event_study_coefficients/`, and four diagnostic event-study figures the manuscript does not
print (`output/figures/{2_1,3_2}_nolog_{D,H}_oct22_24.png`). Four further figures are written under
`output/figures/unreported/` — the alternative-control event studies a footnote describes as "not shown"
— placed in their own directory so they cannot be mistaken for printed exhibits.

## Exhibits not produced by code

Six exhibits are not produced by any program. JPE policy 2.3 asks for step-by-step instructions for these,
so they are here rather than in a separate file.

**Figure 2, "Background on Medical Device Regulations."** A hand-drawn conceptual schematic of the FDA's
three device risk classes, the approval time and cost associated with each, and the two reclassification
policies the paper studies. It plots no estimate, so there is nothing to regenerate from data. To
reproduce or edit it:

1. Open `manual_figures/Deregulation_May31_23_Paper.drawio` — plain XML — at <https://app.diagrams.net>
   (or in the draw.io desktop application) with *File → Open From → Device*.
2. Edit if you wish; the per-class approval time and cost figures shown are class averages from Makower et
   al. (2010), cited in the figure note, and the device examples are illustrative cases drawn from the FDA
   reclassification record.
3. Export with *File → Export as → PNG*, with *Zoom* 100%, *Border width* 0, *Selection only* unchecked,
   *Transparent background* unchecked, and *Appearance* Light. Save as `Deregulation_May31_23_Paper.png`.
4. Place the PNG at `manual_figures/Deregulation_May31_23_Paper.png`. `run_all.py` copies it into
   `output/figures/` on every run, so the figure is restored even after `output/figures/` is emptied.

The `.drawio` master lives in `manual_figures/` rather than `output/` because `output/` holds only what a
run produces and is emptied before a reproduction run. Its SHA-256 is pinned in
`certification/EXPECTED_MODEL_ARTIFACT_HASHES.csv`, and
`certification/FIGURE_PROVENANCE.md` records the figure's full provenance.

**Figure D.2, "Data Catalog."** A schematic that catalogs the study's data sources and how they link — a
reference diagram, not a data plot. It is a pre-made image: step 28 (`code/11g_descriptive_figures.py`)
copies `data/raw/Data_new_latest.png` into `output/figures/` and does not generate it. **No editable source
survives**: there is no `.drawio` or `.svg` master for this image anywhere in my records, and I disclose
that rather than imply one exists. The figure can therefore be reproduced only by copying the shipped PNG,
which is what the pipeline does. It contains no restricted data — source names and links only — and step 28
fails loudly if the PNG is missing rather than silently producing nothing.

**Tables D.2, D.3, D.8 and D.9.** These are catalogs of device types, typed directly into the manuscript
as LaTeX, not produced by a program and not read from `output/`. They contain no estimates: D.2 lists the
Class III→II down-regulated device types with their Federal Register citations, D.3 lists the treated
device-type-to-procedure linkages, and D.8 and D.9 group the Class III→II and Class II→I device types into
broad categories. Every entry is copied from the public FDA product-classification database and from the
Federal Register notices cited in the table notes, so they are reproduced by re-reading those two public
sources; the product codes themselves also appear in `data/raw/foiclass.txt` and
`data/raw/Class2_Exemptions_2017_Grennan.csv`, which ship.

Every computational table is generated by a program. Tables **D.1**, **D.11** and **D.15** are
generated by `code/10c_generate_appendix_tables.py` (run as part of step 35) and
`\input` from `output/tables/Formatted/`. `certification/validate_handentered_tables.py` remains as a
guard: it reads the values out of the compiled `.tex` and checks each against the program output that
should produce it, so a stale number fails the run rather than surviving into print.

## In-text numbers

Every number quoted in the text that is derived from the data — the cost-benefit figures, the
safety-by-asset percentages, the Class II counts, the case-study ratios and the rest — is computed by step
35, `code/15_intext_derived_numbers.py`, and written to `output/tables/intext_numbers_report.csv`.

`certification/INTEXT_NUMBER_INVENTORY.txt` is the closed inventory of those scalars: **117** rows, one per
value, by name. The gate is strict on every route. `run_all.py` sets `FDA_STRICT_INTEXT=1` and the route
(`FDA_INTEXT_ROUTE=synthetic` or `real`) for step 35 itself, and under that setting the step fails — and
takes the whole run's exit code with it — if any inventoried scalar is missing or non-finite, if the
registered set and the inventory file disagree, or if a computational appendix table could not be
generated. Without it, a run could report success having produced neither, which is exactly the failure
this gate exists to prevent.

On the **real-data** route the gate does more: each scalar is additionally compared with the value the
manuscript prints, at the precision the manuscript prints it. A scalar that does not round to the printed
value fails the step. That is deliberate — it is how a divergence between the paper and the programs
surfaces as a failed run rather than as silence — so an authorized researcher should expect step 35 to
report which scalars agree and which do not, and to exit non-zero if any does not. On the
**simulated-data** route no such comparison is made, and none would be meaningful: the simulated values
differ from the published ones by construction, so the gate there checks only that every scalar is
computed and finite.

`certification/verify_intext_report.py --root . --route <synthetic|real>` re-checks the written report
against the inventory after the fact, and is part of the container harness.

### Why four artifacts are frozen rather than regenerated

Four inputs are shipped or held fixed rather than rebuilt on each run, for two different reasons. Two
were produced by calling a hosted language model, which is not a fixed function, so re-running the
program would not necessarily return the same answer at all. The others were fitted here by a procedure
whose numerical path depends on the environment it runs in, so a refit elsewhere is not guaranteed to
match byte for byte. Neither reason is a gap in the code, so the package pins the artifacts by SHA-256
and regenerates everything downstream of them.

**The two language-model-generated inputs.** `data/raw/{2_1,3_2}_GPT_Price_Links.csv` (the device-type
to procedure concordance, `gpt-5-mini`) and the invention-year files (GPT-4o) were produced by calling
a hosted model. A hosted model is not a fixed function: the provider's weights and serving stack change
without notice, and even at `temperature=0` the arithmetic behind a forward pass is not guaranteed to be
bit-identical across serving hardware, so the same prompt need not return the same completion a year
later. Re-running these scripts would therefore change the concordance, and with it the baseline price
sample. They are frozen inputs and no route calls them.

What stands in for reproduction is **validation and full prompt disclosure**:
`code/12b_gpt_price_links_generation.py` and `code/12_invention_year_generation.py` reproduce their
prompts verbatim, record the model, the sampling settings and what was and was not archived, and the
price section reports the concordance's accuracy against an independently produced human-expert
crosswalk that also ships (`data/raw/FDA_HCPCS_Xwalk_Moazzam.csv`), so the comparison can be repeated
by hand. Neither run's date was recorded, which the scripts say; the invention-year file retains 25
raw replies in `data/raw/innovation_year_FDA_project.csv`.

**The LDA models behind Figure D.5.** `code/11a_product_variety.py` trains a topic model on patent
titles and abstracts and ships the fitted models (`data/derived/lda_*`, 14 files, pinned in
`certification/EXPECTED_FROZEN_INPUT_HASHES_REAL.csv`). The call sets `random_state=42` and runs
single-core, so nothing is left to chance *within* an environment. What `random_state` fixes is the
initialisation, not the floating-point path: with `alpha="auto"` the prior is learned over ten passes,
so tiny numerical differences compound, and the chain from tokens (NLTK lemmatiser and stop-word list)
to dictionary ids (assigned in first-seen order) to topics carries any upstream difference forward.
The shipped models were fitted on macOS under Rosetta, with that machine's BLAS and NLTK and gensim
versions; the reference container is Debian-based with a different stack. Fitting is therefore not
bitwise portable: a retrain in another environment, even with the same seed, is not guaranteed to
reproduce the shipped models, and the topic assignments that Figure D.5 reports can differ with it.
A refit in the reference container shows what this looks like in practice. The fit itself comes back
almost identical — largest absolute difference 3.9e-04 across the topic-word matrix and 8.3e-04 in the
learned `alpha` — and the dictionaries rebuild identically. But the topic count is chosen by maximising
a coherence criterion over a grid, and on one of the two samples two topic counts score within
0.0002 of each other, so the selection tips from one to the other. The saved model files are not
byte-identical in any case, because gensim's pickles record the interpreter and platform that wrote
them.
That is why `11a` loads the fitted models when they are present and `run_all.py --strict-cert`
refuses to run the real-data route when they are not, rather than retraining silently.

Variational inference on text is a stochastic, environment-sensitive procedure; this is expected
behaviour for topic models and not a defect in the pipeline. No number the manuscript prints depends
on the topic count -- the text states only that the number of topics was chosen by maximising a
coherence criterion -- but the content of Figure D.5 does, so the models are pinned and travel with the
restricted data rather than being rebuilt.

### Which event time the recall magnitude is read at

The recall paragraph states that recalls show "no divergence at event times 4-6 when data exist, and
a significant decline beginning around year 7 that grows thereafter", and then quotes "the decline of
about 0.45 recalls per device-type-year". That quoted figure is the decline **where it begins, at
event time 7** -- not the larger effects it grows into over the following decade. The constant is
`RECALL_DECLINE_ONSET_ET = 7` in `code/11b_recall_analysis.py`.

The alternative reading -- the mean effect over the whole post-divergence window -- is nearly twice
as large, and both are emitted in `output/tables/recall_in_text_numbers.csv` so a reader can see
them without rerunning the estimation:

| reading | effect | as a share of the control mean (0.854 recalls per device-type-year) |
|---|---|---|
| at event time 7, where the decline begins (**the quoted figure**) | −0.4475 | 52.4 % — the manuscript's "roughly a 50 percent reduction" |
| mean over event times ≥ 7 (alternative) | −0.8769 | 102.7 % |

The paper quotes the smaller, conservative reading. The window mean exceeds the control group's own
mean recall rate, which is why the onset effect is the one registered and stated.

### Two price confidence intervals are not permutation intervals

`code/modules/conley_taber.py` cannot compute its permutation interval when `feols` removes
observations during residualization, because the estimator needs a balanced cluster-by-year layout.
In that case it reports the `feols` point estimate with a **clustered-SE normal-approximation**
95 % interval instead. In `output/tables/price_utilization_estimates.csv` the `method` column names
the estimator and the `ci_method` column records which interval each row carries:
`permutation (Conley-Taber)`, `clustered-SE normal approximation (feols; permutation CI undefined)`,
or, for the BJS rows, `clustered-SE normal approximation (did_imputation)`.

On the real data this happens for two rows, both II→I `BilledAmt` on the human-expert concordance:

| reclass | sample | `ci_method` | estimate | interval | removed by feols |
|---|---|---|---|---|---|
| II→I | Expert | clustered-SE normal approximation | −0.184 | [−0.314, −0.054] | 8 of 118,414 |
| II→I | Expert Matched | clustered-SE normal approximation | −0.075 | [−0.204, 0.055] | 8 of 79,714 |

**No number the manuscript prints is among them.** The price footnote's expert-concordance figures
(−0.18 with SE 0.07 for deregulation, −0.09 with SE 0.03 for down-regulation) are the
`BJS_imputation` rows, which are estimated through `code/modules/estimation.py` and never touch this
code path. The two rows above are robustness rows in the shipped table.

Every substitution is written to `output/logs/inference_method_fallbacks.csv` as it happens, with
the estimator, the outcome, the method substituted, how many observations were removed and which
route the run was on. That file is under `output/logs/`, which the simulated-route comparator does
not read, precisely because it exists only when a substitution occurs.

### Reuse of the shipped dedup artifacts on a from-raw run

`code/00_generate_data/gen_01_main_panels.py` phase 2 fuzzy-deduplicates firm and device names and
writes `data/raw/unique_firms_thr_75.csv`, `unique_firms_in_PC_thr_75.csv` and
`unique_devices_thr_75.csv`. All three **ship** in `data/raw`, and in a non-staging run that is also
where phase 2 writes, so the "outputs already exist, skipping" branch always fired on a real
from-raw run and the dedup never executed — while `synthetic_pipeline/fromraw_contract.py` lists
those same three paths as step-1 transformation outputs a from-raw run is expected to produce.

Phase 2 refuses in that situation, as it does on the simulated route, and names the
three files. To reuse the deposited artifacts deliberately, set `FDA_REUSE_FROZEN_DEDUP=1`; the run
then says so in its log and the firm- and device-count outcomes derive from the shipped artifacts
rather than from raw. This affects only Route 3: Route 2's command passes `--skip-gen`, so steps
1–8 do not execute. Regenerating the three files takes hours. In the reference image it has
reproduced the deposited clustering exactly — identical row counts, identical row order, and the seven
differing `DEVICENAME` cells stated under "Why a few bytes still differ, stated precisely" — at eight
cores and again at twelve. Those are two observations rather than a guarantee: the pass is greedy and
first-wins over a sort with many date ties and runs multi-process on the real-data path
(`n_jobs=-1`), so its result can in principle depend on row order and process scheduling. That is why
the three artifacts ship and are reused unless a replicator removes them deliberately.

### How the two safety-reduction magnitudes are derived

Two of the 117 scalars are summaries rather than single estimates, and a reader reconstructing them
from the deposited coefficients needs to know which horizon and which summary they are, so both are
stated here. The paper's sentence is: "Magnitudes imply an approximately 77% reduction in annual
hospitalizations and a suggestive 40-70% decline in deaths (pre-mean: 0.2 deaths/yr), relative to
counterfactual levels."

**Method.** For each post-event year *h*, `code/15_intext_derived_numbers.py` reads the effect and
the treated level from `output/tables/event_study_coefficients/ES_coefs_2_1_{H,D}.csv` and forms

    counterfactual_level(h) = treated_mean(h) - Effect(h)
    reduction(h)            = |Effect(h)| / counterfactual_level(h)

The control group in this stacked design is pooled (never-treated, all at event time 0), so there is
no control-group event-time slope to project; the counterfactual is the model-implied treated level
absent the effect. The alternative method (project the control slope from the treated pre-level) is
kept in the same file as `counterfactual_pct_reduction()` and is **not** what these two numbers use.

**Horizon.** The reported figure is the central reduction over the long-run window **event years 10
to 15**, set as `H_LO, H_HI = 10, 15` in that script. Year-by-year over that window the
hospitalization reductions are 58.6, 71.9, 71.7, 80.9, 90.7 and 77.5 percent, and the death
reductions 56.9, 36.4, 47.3, 66.1, 72.0 and 62.0 percent. The window matters: taken over the whole
post-period (event years 1–15) the hospitalization figure is 53 percent rather than 77, so the
quoted magnitude is a statement about the second post-reclassification decade, not about the average
post-period year.

**Summary statistic.** The script records `sorted(reductions)[len // 2]`, which for an even-length
window is the upper of the two middle values: 77.5 percent for hospitalizations and 62.0 for
deaths. The conventional median over the same six values is 74.7 and 59.4, and the mean 75.2 and
56.8. All of them fall inside the registered ranges, and the recorded value is the one in
`output/tables/intext_numbers_report.csv`.

**Why the gate registers a range.** The magnitudes in Table 4, Panel B are DiD estimates across
control comparisons; the quantity computed here is the event-study central over a fixed long-run
window -- a related but distinct lens on the same effect. The in-text gate therefore checks that the
event-study figure lands in the range the manuscript states (72-82 percent for hospitalizations,
the printed 40-70 for deaths) rather than asserting an exact printed value, and a figure outside
that range is recorded as `outside_manuscript_range` and fails the step. These are the only two scalars in the
inventory whose registered relation is a range, for that reason, and it is why they are documented
here rather than left to the script.

### How the in-text numbers are checked, and what the composite ones mean

All **117** inventoried scalars agree with the manuscript at the precision the manuscript prints, and
step 35 (`code/15_intext_derived_numbers.py`) exits 0 on the real-data route. The crosswalk from each
scalar to the program and output file it comes from is emitted on every run to
`output/tables/intext_numbers_report.csv`; `certification/INTEXT_NUMBER_INVENTORY.txt` is the closed
inventory. Six of the 117 are not a single number read off a single file, so what the gate compares is
set out here.

**The maturity threshold.** The fitted II→I zero-crossing is 61.1 years with a 95 % confidence interval
of [22, 100], and the figure itself is annotated "Zero Crossing ~ 61 Years". The text states the benchmark
as "roughly 60 years", and the gate reads a hedged benchmark the way it reads the hedged "roughly 30
years" for III→II: rounded to the nearest ten. `MANUSCRIPT_MATURITY_THRESHOLD_YEARS` in
`code/15_intext_derived_numbers.py` is therefore 60, and the companion counts are registered at that
threshold — 651 of 2,235 Class II device types with invention-year data, 29.1 %, exceed it.

**The expert-concordance price footnote.** These come from the human-expert device-type-to-procedure
crosswalk in `data/raw/FDA_HCPCS_Xwalk_Moazzam.csv`, which identifies 52 treated device types: 43
deregulated plus 9 down-regulated. Holding the control construction at the baseline it gives −0.18
(SE 0.07) for deregulation and −0.09 (SE 0.03) for down-regulation, and the down-regulation price effect
is not consistently signed across concordances — which is what the two control constructions in
`output/tables/price_utilization_estimates.csv` (`sample="Expert"` and `sample="Expert Matched"`) show.
The GPT-assisted concordance remains the baseline, as the adjudication footnote explains.

**The top-300 manufacturer linkage.** `code/modules/manufacturer_linkage_coverage.py` emits the
reconciliation to `output/tables/manufacturer_linkage_coverage.csv`: of the 300 largest MAUDE reporters,
which account for 83.9 % of all reports, 88 are private firms with no public-firm match and 32 were
already linked by the dedupe and CRSP merge, so 180 carry a hand-coded assignment. The 70 substring
patterns in `data/raw/manual_permno_corrections.csv` reach 209 of the 300 names, because one pattern
catches every variant of a firm's name (`medtronic` alone matches 23). The pattern count is a diagnostic
in that report and is deliberately not compared against the 300: they are different quantities.

**The case-study patent value.** `xi_real` for patent 6478423 is 295.66147 in `KPSS_2019_public.csv`, and
295.66147 ÷ `config.CPI_DEFLATOR_2019` (0.3891444, the 2019 row of `data/raw/CPI_deflator.csv`) is 759.77
— the \$760 million the text reports, in the 2019 dollars the rest of the paper uses.

**The spinal-entrant audit.** `data/raw/spinal_entrant_audit.csv` carries the six statistics the footnote
quotes: 20 firms, one subsidiary, a median founding year of 2011, a mean of 2010.94, two firms later
acquired, 80 % U.S.-based. The two statistics over the founding year are computed on the 18 firms whose
founding year the sheet records; it is blank for the other two.

**One scalar is printed but not graded.** `class_II_product_codes`, the Class II product-code universe, is
computed and printed by step 35 for context but is not an inventoried manuscript claim, because the
manuscript prints no such count anywhere — it states shares ("About 56\% of product codes are Class II").
A scalar whose target the paper never prints cannot be graded against it. That is why the inventory is 117
rather than 118.

**The twelve printed base rates.** Twelve event-study figures carry a "Base rate" annotation in their
caption or panel, and a thirteenth value appears in a caption in the same form. These are not typed: step
13 writes every one of them to `output/tables/event_study_base_rates.csv`, keyed by figure, and the writer
is fail-closed in two directions — a specification whose figure carries a manuscript overlay raises if its
outcome, event-time or treatment columns are missing or its pre-event window is empty, and the writer
raises if any figure in its completeness set has no row. A run that produced none of these values can no
longer exit 0. The figures concerned are the innovation, market-structure, safety, petitioned-subsample,
entry and firm-expansion event studies (Figures 3, 4, 5, D.3, D.4) and the restricted serious-event panel.

---

# References

## Data citations

U.S. Food and Drug Administration, Center for Devices and Radiological Health. 2020a. "510(k) Premarket
Notification Database [dataset]." <https://www.fda.gov/medical-devices/510k-clearances/downloadable-510k-files>.
Public domain. Downloaded 2020-02-07.

U.S. Food and Drug Administration, Center for Devices and Radiological Health. 2019a. "Premarket Approval
(PMA) Database [dataset]." <https://open.fda.gov/apis/device/pma/>. Public domain. Downloaded 2019-11-04.

U.S. Food and Drug Administration, Center for Devices and Radiological Health. 2019b. "Product
Classification Database [dataset]."
<https://www.fda.gov/medical-devices/classify-your-medical-device/download-product-code-classification-files>.
Public domain. Downloaded 2019-11-04.

U.S. Food and Drug Administration, Center for Devices and Radiological Health. 2020b. "Manufacturer and
User Facility Device Experience (MAUDE) Database [dataset]."
<https://www.fda.gov/medical-devices/medical-device-reporting-mdr-how-report-medical-device-problems/mdr-data-files>.
Public domain. Original pull 2019–2020; refreshed pull 2023.

U.S. Food and Drug Administration, Center for Devices and Radiological Health. 2020c. "Medical Device
Recall Database (openFDA) [dataset]." <https://open.fda.gov/apis/device/recall/>. Public domain.
Downloaded 2020.

U.S. Food and Drug Administration. 2019c. "Medical Devices; Exemptions From Premarket Notification for
Class I and Class II Devices." Final rule. *Federal Register* 84 (249), December 30, 2019: 71794–71819.
Docket Nos. FDA-2017-N-1129 and FDA-2017-N-1610; document 2019-27394.
<https://www.federalregister.gov/documents/2019/12/30/2019-27394/medical-devices-exemptions-from-premarket-notification-for-class-i-and-class-ii-devices>.
Public domain. Source of `data/raw/Good_2_1_Control_2_1.txt`, a text extraction of the amendatory portion
(pages 71797–71819).

U.S. Food and Drug Administration. 2017. "Medical Devices; Exemptions From Premarket Notification: Class II
Devices." Notice of final determination under section 3054 of the 21st Century Cures Act. *Federal
Register* 82, July 11, 2017: 31976–32002. Docket No. FDA-2017-N-1129; document 2017-14453.
<https://www.federalregister.gov/documents/2017/07/11/2017-14453/medical-devices-exemptions-from-premarket-notification-class-ii-devices>.
Public domain. Basis of `data/raw/Class2_Exemptions_2017_Grennan.csv` (244 product codes across 138
regulation numbers). This notice is FDA's final determination on the list proposed on March 14, 2017
(82 FR 13609); the 2019 rule above later codified the exemptions in 21 CFR.

*Both Federal Register items are cited in this README and in `DATA_SOURCES.md`, and are being added to the
manuscript's own bibliography and to its data `\nocite` in the same form as the three reclassification
rules it already cites.*

Merative. 2013. "Merative MarketScan Commercial Claims and Encounters Database [dataset]." Merative L.P.
(formerly IBM Watson Health). Claims years 1996–2013; accessed through the NBER data enclave. Restricted
access.

Digital Science. 2020. "Dimensions Patent Database [dataset]." Digital Science & Research Solutions. US
utility patent records, metadata and full text. Accessed through the Dimensions DSL API v1.24, week of
2020-05-11, with the query bound by `date_inserted <= "2020-05-18"`. The later device-patent
classification file `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` came from a separate pull
whose date is not recorded. Restricted access through an Indiana University subscription.

Center for Research in Security Prices. 2019. "CRSP US Stock Database [dataset]." CRSP, University of
Chicago Booth School of Business. Security and firm identifiers through 2019, used for PERMNO linkage;
accessed through WRDS. Restricted access.

S&P Global Market Intelligence. 2019. "Compustat North America [dataset]." Firm financials through fiscal
year 2019; accessed through WRDS. Restricted access.

LexisNexis. 2024. "Nexis Uni [dataset]." Legal case-law search exports: medical-device and pharmaceutical
tort and preemption pulled July–November 2023, bankruptcy pulled August 2024. Restricted access through an
Indiana University subscription.

Kogan, Leonid, Dimitris Papanikolaou, Amit Seru, and Noah Stoffman. 2019. "Firm-Level Patent Values (KPSS),
public release [dataset]."
<https://github.com/KPSS2017/Technological-Innovation-Resource-Allocation-and-Growth-Extended-Data>. Public
patent-value data accompanying Kogan, Papanikolaou, Seru and Stoffman (2017), *Quarterly Journal of
Economics* 132(2): 665–712. File `data/raw/KPSS_2019_public.csv`; downloaded 2020-08-10.

Kelly, Bryan, Dimitris Papanikolaou, Amit Seru, and Matt Taddy. 2021. "Breakthrough Patent Measures
[dataset]." Patent-similarity and breakthrough indicators released with "Measuring Technological Innovation
over the Long Run," *American Economic Review: Insights* 3(3): 303–320. openICPSR project 119043 and
<https://github.com/KPSS2017/Measuring-Technological-Innovation-Over-the-Long-Run-Extended-Data>. File
`data/raw/KPST_Breakthrough.csv`; downloaded 2023-09-12.

Digital Science. 2019. "Global Research Identifier Database (GRID), release 2019-10-06 [dataset]."
<https://www.grid.ac/>. CC0. File `data/raw/GRID/types.csv`.

Every one of these datasets is also cited in the manuscript's own reference section:
`paper/JPE_submission_v8.tex` `\nocite`s the `data_*` entries of `paper/FDAPaperv1.bib`.

## Other references cited above

Kogan, Leonid, Dimitris Papanikolaou, Amit Seru, and Noah Stoffman. 2017. "Technological Innovation,
Resource Allocation, and Growth." *Quarterly Journal of Economics* 132(2): 665–712.

Kelly, Bryan, Dimitris Papanikolaou, Amit Seru, and Matt Taddy. 2021. "Measuring Technological Innovation
over the Long Run." *American Economic Review: Insights* 3(3): 303–320.

Makower, Josh, Aabed Meer, and Lyn Denend. 2010. *FDA Impact on U.S. Medical Technology Innovation: A
Survey of Over 200 Medical Technology Companies.* Stanford University. (Source of the per-class approval
time and cost figures shown in Figure 2.)

---

# Acknowledgements, preservation and contact

## Preservation and assistance commitment (JPE Data Policy 4.1)

Because this package relies on restricted-data exemptions for MarketScan, Dimensions, WRDS/CRSP-Compustat
and Nexis Uni, I commit to preserving the data and code underlying the results for no less than five years
following publication, in the authorized and licensed environments where the restricted inputs reside. I
will also provide reasonable assistance to requests for clarification and replication.

## Contact

For questions about this package, and for restricted-data verification, contact me at
parkerrogers2@gmail.com. `RESTRICTED_DATA_VERIFICATION_MEMO.md` and
`RESTRICTED_DATA_MANIFEST.csv` identify the appropriate verification route for each restricted source, and
the NBER contact for executing `gen_00b_marketscan_extraction.py` on the raw MarketScan tables is supplied to the Data Editor directly on request.

## Pre-registration

Not applicable. This is a retrospective observational study of administrative records and is not
pre-registered.

## Human subjects

This study collects no primary data from human subjects. Every input is a public administrative database, a
licensed third-party research database, or my own desk coding of published documents. There is accordingly
no IRB approval, consent procedure or ethics documentation to deposit, and no survey instrument or
experimental protocol.

## Acknowledgements

The sentence-transformer model in `models/all-MiniLM-L6-v2/` is third-party work redistributed under
Apache-2.0; its model card and licence text ship with it. The simulated Nexis, MarketScan, patent and firm
data in `synthetic_pipeline/simulated_data/` are generated by the programs in this package and are not
derived from any provider's data.
