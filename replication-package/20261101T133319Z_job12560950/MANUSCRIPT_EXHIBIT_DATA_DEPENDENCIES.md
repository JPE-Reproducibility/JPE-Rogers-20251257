# Manuscript Exhibit Data Dependencies

**Supporting reference; `README.md` governs.** This file records which restricted source each
manuscript exhibit depends on. What ships, what does not, and how to run either route are in
`README.md`.

Current manuscript source:

```text
paper/JPE_submission_v8.tex
```

This file identifies the data-access status of the main manuscript exhibits and
the major appendix exhibits: which restricted source each one depends on, and
which are reproducible from public and author-created data alone.

## Status Legend

- `public`: Reproducible from redistributable public or author-created data.
- `restricted-dimensions`: Requires Dimensions patent records, metadata, patent
  text, or derived patent-level data.
- `restricted-marketscan`: Requires MarketScan claims or derived claims files.
- `restricted-wrds`: Requires WRDS/CRSP-Compustat firm data or firm-level derived
  assets/PERMNO matches.
- `restricted-legal`: Requires legal database exports or derived legal-search
  encodings whose redistribution rights require confirmation.
- `mixed`: Uses both public and restricted inputs.

## Main Text Tables

| Exhibit | Manuscript Label | Output/Input | Status | Notes |
|---|---|---|---|---|
| Table 1 | `tab:SummaryStatistics` | `output/tables/Table_1_summary_stats.tex` | mixed | Includes public FDA/MAUDE data plus restricted patent, WRDS, and MarketScan components. Public README should identify which panels cannot be reproduced from public data alone. |
| Table 2 | `tab:Innovation` | `PaperRegTable*_Main_Panel_NoLog_oct22_24.tex` | restricted-dimensions | Patent outcomes require Dimensions-derived data; FDA device submission rows are public/source-FDA based. |
| Table 3 | `tab:MarketComposition` | price and market-composition tables | mixed | Entry and product variety use Dimensions/FDA inputs; price rows require MarketScan. |
| Table 4 | `tab:AdverseEvent` | safety emphasis and adverse-event tables | mixed | MAUDE adverse-event counts are public/source-FDA based; safety patent emphasis requires Dimensions patent text; firm-size safety components require WRDS. |

## Main Text Figures

| Exhibit | Manuscript Label | Output/Input | Status | Notes |
|---|---|---|---|---|
| Contact lens case study | `fig:ContactLensCaseStudy` | `ContactLens_patents.png`, `ContactLens_submissions.png`, `ContactLens_firms.png` | mixed | Patent and firm patenting panels require Dimensions-derived data; FDA submission panel is public/source-FDA based. |
| Background on regulation | `pic:DeviceDeregulation` | `Deregulation_May31_23_Paper.png` | public | Manually created figure; include source note and original editable source if available. |
| Innovation event studies | `fig:InnovationES` | `*_real_pats*`, `*_dev_count*` | mixed | Patent panels require Dimensions; FDA submission panel is public/source-FDA based. |
| Market structure | `fig:MarketStructure` | price event-study figures | restricted-marketscan | Requires MarketScan claims and device-procedure links. |
| Product safety | `fig:ESProductSafety` | adverse-event and normalized safety figures | mixed | Raw MAUDE panels are public/source-FDA based; utilization-normalized panels require MarketScan-derived utilization. |
| Safety by assets | `fig:SafetybyAsset` | `2_1_Safety_Top_Decile*`, `2_1_Deaths_Top_Decile*` | restricted-wrds | Requires firm asset data from WRDS/CRSP-Compustat merged to safety outcomes. |

## Appendix and Online Appendix Tables

| Exhibit | Manuscript Label | Status | Notes |
|---|---|---|---|
| Sample construction | `tab:SampleConstruction` | mixed | Contains sample counts by outcome; patent rows require Dimensions, price/utilization rows require MarketScan, firm-size rows require WRDS. |
| Device-to-procedure linkages | `tab:DeviceToProcedureLinkages` | mixed | Linkage files are author-created, but the linked price/utilization evidence requires MarketScan. |
| Innovation robustness | `tab:Robustness_Innovation` | restricted-dimensions | Patent robustness tables require Dimensions-derived patent outcomes. |
| Market structure robustness | `tab:Robustness_MarketStructure` | mixed | Price robustness requires MarketScan; patent-based entry requires Dimensions; FDA submission-based entry is public/source-FDA based. |
| Adverse-event robustness | `tab:Robustness_Adverse` | public or mixed | MAUDE count robustness is public/source-FDA based; any utilization-normalized or firm-size components are restricted. |
| Spillovers | `tab:Innovation_Spillovers` | mixed | Patent spillovers require Dimensions; device-submission spillovers are public/source-FDA based. |
| Drop positive-count robustness | `tab:Combined_DropNoCounts` | mixed | Status follows the underlying outcome: patent rows require Dimensions, price rows require MarketScan, firm-size rows require WRDS. |
| Utilization | `tab:Utilization` | restricted-marketscan | Requires MarketScan claims. |
| Safety patent robustness | `tab:ProbabilitySafetyMentionEffects_Robustness` | restricted-dimensions | Requires patent text or patent-level safety classifications. |
| Cost-benefit | `tab:CostBenefits` | mixed | Patent value components require Dimensions/KPSS and public-firm data; safety components use MAUDE; price/utilization assumptions may depend on MarketScan. |
| Restricted patent samples | `tab:Innovation_nodrugs_A61only` | restricted-dimensions | Requires patent-level classifications and Dimensions-derived sample construction. |
| Breakthrough patents | `tab:BreakthroughPatentsEffects` | restricted-dimensions | Requires patent-level sample and breakthrough patent indicators. |

## Appendix and Online Appendix Figures

| Exhibit | Manuscript Label | Status | Notes |
|---|---|---|---|
| Event distribution | `fig:event_distribution` | public | Based on FDA/Federal Register reclassification data. |
| Data catalog | `fig:DataCatalog` | public | Descriptive figure; include source/editable file if available. |
| Petitioned III-to-II | `fig:Petitioned_IIItoII` | mixed | Patent outcome requires Dimensions; petition metadata is public/source-FDA based. |
| Product variety | `fig:ProductVariety` | restricted-dimensions | Requires patent text and LDA artifacts. |
| Firm experience heterogeneity | `fig:FirmExperienceHeteroSimulation` | mixed | FDA approval/submission history is public/source-FDA based; any patent-based components require Dimensions. |
| Firm size heterogeneity | `fig:FirmSizeHetero` | restricted-wrds | Requires public-firm assets merged to patent outcomes. |
| Safety emphasis | `fig:Safety_IItoI` | restricted-dimensions | Requires patent text or patent-level safety classifications. |
| Legal environment | `fig:DeviceTortCasesOverTime` | restricted-legal | Requires legal-search exports or derived legal encodings. |
| Impact by experience | `fig:Impact_by_experience` | mixed | Safety component uses MAUDE; patent component requires Dimensions; experience-year inputs are author-created. |
| Current device experience | `fig:DeviceExperienceCurrent` | public | Based on FDA/product-code and invention-year inputs; confirm author-created invention-year files are included. |
| Recall analyses | `fig:Recall_Analysis`, `fig:SafetyRecalls_IItoI_2015` | public or mixed | FDA recall/adverse-event components are public/source-FDA based; any patent/new-entry panel requires Dimensions. |
| New entry 2015 | `fig:Innovation_2_1_2017` | restricted-dimensions | New-firm patenting requires Dimensions-derived patent data. |
| Reporter-type adverse events | `fig:AdvEvent_by_Reporter` | public | Based on MAUDE reporter categories. |

## What this means for reproduction

This package includes all of my code and all of the data I may redistribute. The simulated-data route runs
every pipeline step on clearly labelled simulated substitutes for the restricted inputs, so every code path
is exercised and every exhibit above is produced — with simulated values. Exact reproduction of the
MarketScan, Dimensions, WRDS/CRSP-Compustat and legal-database exhibits requires the restricted-data route.
`README.md` describes both routes and the scope of each check; `RESTRICTED_DATA_MANIFEST.csv` lists what is
excluded per source.
