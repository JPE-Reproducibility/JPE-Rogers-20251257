# Expected-Output Manifests — Procedure

**Supporting reference; `README.md` governs.**

The three strict manifests cover the fixed real-data output inventory:

- `EXPECTED_EXHIBIT_HASHES.csv`;
- `EXPECTED_INTERMEDIATE_HASHES.csv`;
- `EXPECTED_MODEL_ARTIFACT_HASHES.csv`.

They are refreshed only from a real-data output tree that has been reviewed and frozen, never from a
simulated run:

```bash
python3 certification/refresh_expected_output_hashes.py --write
python3 certification/refresh_expected_output_hashes.py
```

The verifier requires fixed row counts, strict schema/path syntax, unique safe paths, readable files,
and matching SHA-256/byte/line counts. The package build's `--final` mode runs verify mode and aborts on
any mismatch or missing verifier. A manifest may not be refreshed from an uncertified source tree or
from the same synthetic output it is intended to test.

## Adding an output to a manifest

The canonical path inventories (`EXPECTED_EXHIBIT_PATHS.txt`, `EXPECTED_INTERMEDIATE_PATHS.txt`,
`EXPECTED_MODEL_ARTIFACT_PATHS.txt`) are the declaration; the `*_HASHES.csv` files are derived from
them. To add (or remove) a governed output, edit the PATHS file and re-run `--write`, which now
regenerates each manifest FROM its canonical inventory rather than from the manifest's own existing
rows. A sha256 column is never hand-edited. `--write` writes LF line endings, matching the shipped
manifests, so a no-op refresh leaves them byte-identical.

Which manifest a new output belongs to:

- `EXPECTED_EXHIBIT_PATHS.txt` — `output/figures/*.png` and the standalone / `Formatted` `.tex`
  tables the manuscript prints.
- `EXPECTED_INTERMEDIATE_PATHS.txt` — `output/tables/**/*.csv`: every estimate and every CSV that
  backs an in-text number.
- `EXPECTED_MODEL_ARTIFACT_PATHS.txt` — the editable source assets under `manual_figures/`.

**2026-09-17 refresh.** 29 outputs were added: the four adverse-event subtype panels
(`{2_1,3_2}_nolog_{D,H}_oct22_24.png`) and the four "not shown" alternative-control panels under
`output/figures/unreported/` to the exhibit inventory; and 21 CSVs to the intermediate inventory —
`event_study_base_rates.csv` (the twelve base-rate overlays the manuscript prints on its
event-study figures), `contact_lens_case_study_ratios.csv`, `BreakthroughPanel_distribution.csv`,
`PatentCollectionCounts.csv`, `price_sample_construction.csv`, `dpm_decile_ratio.csv`,
`recall_event_study_1996.csv`, `recall_in_text_numbers.csv`, `new_entry_2015_event_study.csv`,
`new_entry_2015_in_text.csv`, `safety_term_share.csv`,
`safety_embedding_percentile_robustness.csv`, and nine `event_study_coefficients/ES_coefs_*.csv`
that the pipeline writes but the deposited tree lacked. Three existing rows changed by design:
`price_utilization_estimates.csv` (rows for the human-expert concordance sample),
`safety_refined_keywords_estimates.csv` (an `n_obs` column), and
`Formatted/TableD12_SafetyRobustness.tex` (a program-generated Sample Size row per panel).

The manifests in this deposit were refreshed from the real-data outputs that ship in `output/`, and
`certification/refresh_expected_output_hashes.py` (verify mode, no arguments) re-checks them against that
tree at any time.
