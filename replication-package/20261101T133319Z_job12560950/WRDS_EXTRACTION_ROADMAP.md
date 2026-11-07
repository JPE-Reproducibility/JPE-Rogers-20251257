# WRDS / CRSP-Compustat Extraction Roadmap

**Supporting reference; `README.md` governs.** `README.md` is the single documentation point for this
package; this file is the extraction detail behind its WRDS/CRSP-Compustat entry.

This document specifies the exact WRDS queries used to build the firm-financial
inputs, so that a licensed user (e.g., the JPE Data Editor with University of
Chicago WRDS access) can reproduce the extraction without the author sharing any
data. Per the WRDS and CRSP/Compustat license agreements, the extracted data
cannot be redistributed outside the licensed institution; this roadmap plus the
released code is the supported reproduction path.

No WRDS credentials are included anywhere in this package.

## Outputs produced from these queries

- `data/raw/compustat_firm_data.csv` — Compustat firm-year financials with the
  CRSP PERMNO link (excluded from the public package; restricted).
- Downstream derived files (also restricted): `Adverse_fsize_ready_all4_oct22_24.csv`,
  `all_adv_events_w_permno5.csv`.

These feed `code/00_generate_data/gen_05_adverse_fsize.py` and
`gen_07_adverse_permno.py`, and the firm-size heterogeneity analysis
(`code/07_firm_heterogeneity.py`).

## Query 1 — Compustat Fundamentals Annual via CRSP/Compustat Merged (CCM)

- **WRDS product:** CRSP/Compustat Merged (CCM) — Fundamentals Annual
  (`comp.funda` joined to the CCM link table `crsp.ccmxpf_lnkhist`), which
  attaches `LPERMNO` to each Compustat `GVKEY`.
- **Extraction interface:** the WRDS web query form "CRSP/Compustat Merged –
  Fundamentals Annual," run with the form's default screening settings (these
  defaults produce one record per GVKEY-DATADATE pair).
- **Date variable / range:** Date Variable = `(fyear) Data Year - Fiscal`,
  extracted over the full available history. The released
  `compustat_firm_data.csv` spans fiscal years 1973–2019 (`datadate` 1974-01-31
  to 2019-12-31; 279,347 firm-year records, 47 fiscal years).
- **Screening variables (form defaults, author-confirmed; verified in the data):**
  - Consolidation Level: `C`  (`consol = 'C'`)
  - Industry Format: `INDL`  (`indfmt = 'INDL'`)
  - Data Format: `STD`  (`datafmt = 'STD'`)
  - Population Source: `D`  (`popsrc = 'D'`)
  - Currency: `USD` and `CAD` (both; matches `curcd` in the data)
  - Company Status: Active and Inactive (both)
- **Universe:** entire database (no company-code or SIC restriction at
  extraction; device relevance is established later via the manufacturer→PERMNO
  match, not here).
- **Step 3 Linking Options (author-confirmed defaults):**
  - Link Types: `LC` and `LU`.
  - Fiscal Period / Link Date Requirement: the form default ("Fiscal period end
    date must be within link date range"). (This WRDS form version exposes Link
    Types + the link-date radio; there is no separate LINKPRIM checkbox.)
- **Variables pulled (exact column set in the output file):**
  `GVKEY, LPERMNO, datadate, fyear, indfmt, consol, popsrc, datafmt, conm,
  curcd, act, at, bkvlps, csho, dltt, costat, prcc_c, prcc_f`.
- **Analysis variable:** `at` (total assets) becomes `firm_size` in
  `gen_05_adverse_fsize.py` (then CPI-deflated to real 2019 dollars using
  `data/raw/CPI_deflator.csv`). The other pulled variables are retained for
  reference/robustness.

## Query 2 — CRSP firm-name / PERMNO reference universe (for manufacturer matching)

- **Purpose:** resolve MAUDE adverse-event manufacturer names to CRSP `PERMNO`
  (see `gen_07_adverse_permno.py`), via a two-stage entity-resolution match
  against a pre-built `(firm_name, permno)` reference, followed by the **70**
  manual correction rows in `data/raw/manual_permno_corrections.csv` (restricted,
  not shipped; its columns are defined in `CODEBOOK.md`).
- **How the reference is built:** `code/00_generate_data/gen_06b_permno_universe.py`
  concatenates three sources and deduplicates on `permno`:
  1. CRSP firm directory (`data/raw/CRSPDirectory.csv`) — `NAME OF FIRM` +
     `PERM NO` as `firm_name`/`permno`.
  2. KPSS-merged Dimensions patent file
     (`data/derived/all_patents_w_xi_oct22_24.csv`) — for patent assignees with
     PERMNOs not already in the CRSP directory, `orig_assignee_solo` ->
     `firm_name`.
  3. Compustat `AllPublicCompanies.csv` — for `LPERMNO`s not already covered,
     `conml` -> `firm_name`. (Built from this same CCM Fundamentals Annual pull.)
- **WRDS source for the CRSP directory (author-confirmed):** `CRSPDirectory.csv`
  was produced from the **CRSP/Compustat Merged — Fundamentals Annual** dataset
  (the same CCM product as Query 1). The firm-name and PERMNO columns
  (saved as `NAME OF FIRM` and `PERM NO`) correspond to the CCM company-name
  (`conm`) and `LPERMNO` fields. No separate CRSP Names extract is required —
  the reference universe is built from CCM Fundamentals Annual plus the patent
  assignee and AllPublicCompanies additions documented in
  `gen_06b_permno_universe.py`.

## Reproduction steps for a licensed user

1. Using your own institutional WRDS access, run Query 1 to regenerate
   `compustat_firm_data.csv` with the variables, filters, and date range above.
2. Build the CRSP `(firm_name, permno)` reference (Query 2).
3. Place the files at the documented paths and run the firm-financial steps:
   `gen_05_adverse_fsize.py`, `gen_07_adverse_permno.py`, then
   `07_firm_heterogeneity.py`.
4. Compare the firm-size / safety-by-assets exhibits against the manuscript via
   `code/audit_pipeline_current.py`.

## Notes

- Do not redistribute the extracted CRSP/Compustat data outside your licensed
  institution.
- Entity resolution (`pandas_dedupe`) is stochastic across environments; the
  frozen manufacturer→PERMNO artifacts are retained so the manuscript result is
  reproducible without re-running the dedupe. See the LBD/dedupe notes in the
  README and the main agent handoff.
