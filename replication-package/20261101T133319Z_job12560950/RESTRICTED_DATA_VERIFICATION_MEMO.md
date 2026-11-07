# Restricted Data Verification Memo

**Supporting reference; `README.md` governs.** `README.md` is the single documentation point for this
package; this file is the detail behind its "Restricted sources, excluded from the package" section.

## Scope

The public ZIP excludes licensed real microdata and restricted-derived analytical files. The exact
deposited code is instead executed in provider/licensed environments, and permitted outputs/evidence
are assembled fail-closed. The public simulation is an additional code-execution route; it does not
replace real-data numerical verification.

Human/legal facts are supported by the confidential external-evidence ledger. Automated checks verify
record presence/hashes but do not interpret licenses or grant approval.

## Per-source facts (version, access date, exemption status, provider)

The evidence for each date is named explicitly. Where the package holds no evidence, the entry says
so rather than estimating. **Shipped-file modification times are NOT evidence of an access date**:
every restricted file in the author's tree carries a February 2026 modification time because the tree
was re-staged then; the earliest acquisitions are years older.

| | MarketScan | Dimensions | WRDS / CRSP-Compustat | Nexis Uni |
|---|---|---|---|---|
| Provider | Merative (formerly IBM Watson Health), accessed through the NBER data enclave | Digital Science & Research Solutions | Wharton Research Data Services (CRSP, University of Chicago Booth; Compustat, S&P Global Market Intelligence) | LexisNexis |
| Provider URL | https://www.merative.com/real-world-evidence ; access route https://www.nber.org/research/data | https://www.dimensions.ai/ | https://wrds-www.wharton.upenn.edu/ | https://www.lexisnexis.com/en-us/professional/academic/nexis-uni.page |
| Dataset version / vintage | Commercial Claims and Encounters Database; the extract spans claim years **1996–2013** (evidence: the coverage of the extract, recorded at `synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py:23,80`). No provider release label is recorded. | Dimensions DSL API **v1.24, week of 2020-05-11**, with the query bound by `date_inserted <= "2020-05-18"` (evidence: script header, `code/00_generate_data/gen_00_dimensions_patent_extraction.py:15–22,44–50`). The later device-patent classification file `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` came from a separate, **undated** pull. | CRSP/Compustat Merged, Fundamentals Annual; the extract spans **fiscal years 1973–2019** (`datadate` 1974-01-31 to 2019-12-31) — evidence: the extract itself, recorded at `WRDS_EXTRACTION_ROADMAP.md:31–34`. No provider vintage label is recorded. | Nexis Uni **Cases** content type; exports span **2023-07-25 to 2024-08-27** (evidence: the internal workbook timestamps of the `.xlsx` exports, `NEXIS_SEARCH_METHODOLOGY.md:47–57`). |
| Author's date(s) of access | **NOT RECORDED.** | Main patent pull: the week of **2020-05-11** (evidence: script header, as above). Device-patent classification file: **NOT RECORDED**. | **NOT RECORDED.** | Tort and preemption searches **2023-07-25/26**, with three later files **2023-08-22**, **2023-08-23** and **2023-11-06**; bankruptcy searches **2024-08-27** (evidence: internal workbook timestamps, as above). |
| Exemption status | No new exemption requested; the source is excluded under the original restricted-data disclosure. The extraction program is deposited (`gen_00b_marketscan_extraction.py`), so no Policy 2.1 exemption is needed for it; the two-significant-figure rounded row counts require the Data Editor's written acceptance. | Excluded under a third-party licence (Indiana University institutional subscription). Digital Science's reply permits the documented confidential review of Dimensions-derived files; the reply and its hash are retained outside the public deposit. | Excluded under a third-party licence (institutional WRDS subscription). Verification runs in the licensed environment. | **Exemption granted by the handling editor.** |
| Verification route | Provider execution at NBER, or a licensed MarketScan environment (see "MarketScan provider-run route" below). | Institutional Dimensions access, a licence-permitted temporary confidential extract, or provider/licensed-environment execution. | The Data Editor's own WRDS access, following `WRDS_EXTRACTION_ROADMAP.md`. | The author supplies the archived raw Results-list exports under confidentiality (primary), or the searches are re-run per `NEXIS_SEARCH_METHODOLOGY.md` (best effort). |

`DATA_POLICY_COMPLIANCE.md` row 1.2 states the same per-source status; the two must be kept in step.

## Destinations and expected shapes for an authorized researcher

An authorized researcher who obtains a restricted source places the files at exactly these paths.
Row counts for MarketScan are approximations — two significant figures, set one rounding step above the nearest two-significant-figure value, so the real extract is smaller by half a step to one and a half steps — published in
`synthetic_pipeline/_synthetic_source_internal/simulation_schema_contract.json`; exact restricted
extract sizes are not published, a single real record moves a published count by at most one step, and
the Data Editor's acceptance of the rounded figures is pending.

**MarketScan** (`simulation_schema_contract.json`, `marketscan_files`):

| Destination | Columns | Rows (approximation) |
|---|---|---|
| `data/derived/outpatient_combined_censored.csv` | 9: `proc1, year, coins, copay, netpay, qty, pay, proc_count, enrolid_count` | ~190,000 |
| `data/derived/constrained_adv_event_new_sept25.csv` | 16 (see the contract) | ~16,000 |
| `data/derived/constrained_adv_event_new_sept25_3_2.csv` | 17 (see the contract) | ~280 |

The last two are produced by `gen_02_price_matching.py` from the first three plus public inputs, so an
authorized researcher supplies only the first three.

**Dimensions.** Destinations and their column sets (the extraction is specified in
`code/00_generate_data/gen_00_dimensions_patent_extraction.py`; row counts are a function of the
author's phrase files and are not published):

| Destination | Columns |
|---|---|
| `data/raw/all_PC_pats.csv`, `expanded_2_1_pats.csv`, `expanded_3_2_pats.csv`, `missed_2_1_pats.csv` | `id, year, PRODUCTCODE, filing_status, times_cited, title` |
| `data/raw/FDA_pats_original_firmname.csv` | `id, original_assignee_names, original_assignees, inventor_names` |
| `data/raw/all_pats_wtitlesCPC.csv` | `PRODUCTCODE, GRID, orig_assignee_solo, original_assignee_names, original_assignees, id, inventor_names, patents, year, type` plus the eight GRID assignee-type indicator columns |
| `data/raw/FDA_patents_text.csv` | `id, input` (patent title + abstract text) |
| `data/raw/Applicant_Cites_Only.csv` | `USID, PRODUCTCODE, times_cited` |
| `data/raw/PC_by_year_cites_ApplicantOnly.csv`, `PC_by_year_diff_ind_appl_only.csv` | `year, PRODUCTCODE, times_cited` |
| `data/raw/new_patent_analysis/all_device_patents_w_pc.csv` | patent-level device classification file; 13 leading columns beginning `patent_id, patent_abstract, patent_type, patent_date, patent_title` |

**WRDS / CRSP-Compustat** (queries in `WRDS_EXTRACTION_ROADMAP.md`):

| Destination | Columns | Expected shape |
|---|---|---|
| `data/raw/compustat_firm_data.csv` | 18: `GVKEY, LPERMNO, datadate, fyear, indfmt, consol, popsrc, datafmt, conm, curcd, act, at, bkvlps, csho, dltt, costat, prcc_c, prcc_f` | 279,347 firm-year records across 47 fiscal years (1973–2019) |
| `data/raw/CRSPDirectory.csv` | firm name + PERMNO, saved as `NAME OF FIRM` and `PERM NO` | one row per firm in the CCM company universe |
| `data/raw/AllPublicCompanies.csv` | `conml`, `LPERMNO` | one row per public company in the same CCM pull |

The last two are read only by `gen_06b_permno_universe.py`, which is gated behind
`RUN_PERMNO_UNIVERSE_BUILD=1` and runs on neither official route.

**Nexis Uni.** Destinations, exact filenames (each filename is the literal search query), export
settings and a per-file expected-hit-count table are in `NEXIS_SEARCH_METHODOLOGY.md`; the
tort/preemption exports go in `data/raw/Liability/` and the bankruptcy exports in
`data/raw/Liability/medtech/`, with a lowercase `.xlsx` extension. Every tort and preemption
Results-list export carries the seven columns `CASE NAME, CITE, SUMMARY, JURISDICTION, COURT, DATE
DECIDED, YEAR`; the fourteen bankruptcy exports under `medtech/` carry the 26 columns of the Nexis
company-news export.

## Analysis data (JPE Data Policy 1.3)

The real analysis panels are excluded from the deposit. The real `data/derived/Full_sample.csv` is not
shipped in any form: shipping it reduced to a public column subset was rejected, because
column-stripping a master panel built from mixed restricted sources is not sanitization — row
membership, ordering and missingness remain disclosure surfaces. It is instead created at run time by
the pipeline, from synthetic inputs on the public route and from the real inputs in an authorized
route, and the package builder is structurally barred from copying the real master. The matched,
intuitive, later-treated and spillover panels (`matched_sample_*`, `intuitive_*`, `later_treated_*`,
`spillovers_*`, `data_2_1_*.parquet`), the patent-level files (`all_patents_w_xi_oct22_24.csv`,
`safety_vars_allpats*`), the firm-size panel (`Adverse_fsize_ready_all4_oct22_24.csv`), the
MarketScan-constrained panels (`constrained_adv_event_*`) are
excluded on the same restricted-lineage ground and are reproduced only in the provider-authorized
routes. Fully synthetic counterparts of all of them ship in
`synthetic_pipeline/simulated_data/`, so the analysis runs end to end without any restricted byte.

## Source routes

### MarketScan via NBER

Raw MarketScan variables remain at NBER. The extraction program that aggregates them into the single
claims extract the package reads is deposited: `code/00_generate_data/gen_00b_marketscan_extraction.py`,
the original program, recovered by NBER IT from my former account there and released to me through their
output-review process. NBER IT has offered to execute it. No raw MarketScan data, proprietary variable dictionary, or real claims-derived file ships
publicly. The public simulation generates independent author-defined aggregate interfaces for the
analysis.

The NBER/provider real-data route is covered by the original restricted-data disclosure, and no new
exemption request is being made. Pending evidence: hash-matched code delivery, NBER environment/input identification
where permitted, commands/logs/return codes, output hashes/comparisons, and Data Editor technical
acceptance.

#### MarketScan provider-run route

*Provider contact.* The name and address of the NBER contact who offered to execute the extraction
program, together with the institutional data-core address, are supplied to the Data Editor directly on
request rather than published in this package, so that no individual's contact details are
redistributed with the deposit.

*What the provider runs.* `code/00_generate_data/gen_00b_marketscan_extraction.py`, unchanged, against
the raw CCAE outpatient tables (`ccaeo1996` … `ccaeo2013`, the 100% level). It is the program I ran at
NBER; its docstring records the recovery. `outpatient_combined_censored.csv` is the only
MarketScan-derived file the package needs: the price analysis is outpatient-only, and the utilization
counts the event studies normalize by come from `constrained_adv_event_*`, which
`gen_02_price_matching.py` builds from the outpatient extract.

*What the provider returns.* Exactly one file, with the columns and approximate row count in the
MarketScan table above:

    data/derived/outpatient_combined_censored.csv

*What happens next.* Place the file at that path in the package and run the price and
utilization steps — `code/00_generate_data/gen_02_price_matching.py`, then `code/05_price_analysis.py`
and `code/04_event_studies.py` — following `README.md`, "Route 2 -- the real-data route". The exhibits to compare
are the price and utilization panels and the utilization-normalized safety checks listed against the
MarketScan row of `RESTRICTED_DATA_MANIFEST.csv`.

### Dimensions

Digital Science's reply permits the documented confidential review of Dimensions-derived files. The
reply and its hash are retained outside the public deposit. Pending evidence: execution bound to the deposited archive,
and output comparison, in the permitted route.

Note for the authorized researcher: the 2020 extract cannot be re-pulled identically. The Dimensions
DSL has been revised repeatedly since v1.24 and the provider does not allow querying a historical
snapshot; `gen_00_dimensions_patent_extraction.py` measures the consequence — product codes with a
specific hand-curated search phrase reproduce at roughly 99–100% recall, while product codes with a
generic device phrase do not reproduce at all, because the 2020 query behaved as a broad
relevance-ranked full-text search and the current one does not. The archived extract is therefore the
authoritative input.

### WRDS/CRSP-Compustat

The Data Editor uses authorized WRDS access or another provider-approved licensed environment following
`WRDS_EXTRACTION_ROADMAP.md`. The author's credentials/extracts are not shared publicly. Pending
evidence: extraction and transformation logs bound to the deposited archive, and output comparison.

### Nexis Uni

The handling editor has granted the Nexis exemption. Technical verification follows the approved
confidential/provider route using the documented search methodology and permitted derived/raw review.
Pending evidence: execution and comparison bound to the deposited archive, and the Data Editor's route-sufficiency record.

## Required evidence per route

Each route records:

1. the deposit archive's, the code's and the manuscript's SHA-256;
2. lawful input version/date and identifiers/hashes where the license permits;
3. environment and software versions;
4. exact command, raw log, return code, and expected writes;
5. output member hashes and transfer/assembly manifest;
6. zero missing, extra, conflicting, or unapproved-different outputs;
7. strict manuscript/output/in-text/exhibit/hand-entered-table comparison result.

Only original source acquisition may be classified N-A on the synthetic route. Every post-acquisition
transformation must execute unless the Data Editor approves a specific technical exception; a policy
deviation, if any, is reported separately and is never counted as an executed step.

## Materials never placed in the public ZIP

- MarketScan raw claims, raw-variable definitions, provider extraction code, and real aggregates;
- Dimensions individual records/text and restricted-derived files;
- WRDS/CRSP-Compustat extracts, credentials, real identifiers/crosswalks, and linked outputs;
- Nexis raw exports or derived records beyond what the granted/approved route permits;
- any confidential provider correspondence or credentials.

## Status

This memo documents the route to each restricted source and the evidence behind each fact it states. It
does not report a completed numerical verification on any provider's real data: no route is described
here as completed, and none should be read as completed, until the evidence from that run exists.
