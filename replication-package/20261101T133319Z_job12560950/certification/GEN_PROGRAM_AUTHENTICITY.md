# Data-generation program authenticity audit (JPE §2.1)

**Supporting reference; `README.md` governs.**

Audit date 2026-10-06. Checks **every** `gen_*` program
for whether it is the *actual* transformation code that produced the deposited derived data, or a
reconstruction / approximation / placeholder. Method: keyword scan (reconstruct / approximate /
placeholder / not-original / stub / to-do) plus manual review of each hit.

| Program | Verdict | Notes |
|---|---|---|
| `gen_00_dimensions_patent_extraction.py` | **Authentic (provenance)** | The actual Dimensions extraction code; ships as provenance (reads the licensed Dimensions source, not runnable publicly). |
| `code/00_generate_data/gen_00b_marketscan_extraction.py` | **Authentic (provenance)** | The original MarketScan claims-aggregation program I ran at NBER, recovered by NBER IT from my former account there and released to me through their output-review process. The deposited file is that program, with only a module docstring and three block headers added (the docstring records the provenance; the aggregation code is unedited). Ships as provenance: it reads the raw CCAE outpatient tables at NBER and writes `outpatient_combined_censored.csv`, the one provider-held input. |
| `gen_01_main_panels.py` | Authentic | actual panel-construction code. |
| `gen_02_price_matching.py` | Authentic | actual MarketScan price-matching. |
| `gen_03_lbd.py` | Authentic | the two "reconstruct" hits refer to rebuilding the panel with cluster IDs in memory — normal processing, not a lost-program reconstruction. |
| `gen_03b_lbd_clusters.py` | Authentic | actual LBD clustering. |
| `gen_04_parquets.py` | Authentic | actual parquet materialization. |
| `gen_05_adverse_fsize.py` | Authentic | actual adverse-event / firm-size join. |
| `gen_06_adv_2020.py` | Authentic | actual 2020 adverse-event build. |
| `gen_06b_permno_universe.py` | Authentic (provenance) | actual PERMNO-universe build (reads WRDS-linked source). |
| `gen_07_adverse_permno.py` | Authentic | the "reconstruct" hits refer to rebuilding an exact list-of-dicts data structure — normal code, not a lost-program reconstruction. |

**Conclusion:** every `gen_*` program that ships is authentic author code, including the MarketScan
extraction program. The public synthetic route generates the aggregate MarketScan-shaped interface
independently; the real-data route runs the deposited extraction program at NBER (raw claims do not
leave NBER) and then the deposited transformations. The one MarketScan-derived input is RESTRICTED/EXCLUDED
with a synthetic substitute for the public route, disclosed in the Data Availability Statement and under
§4.3. Evidence from a provider-side run of the extraction program is not claimed here.
