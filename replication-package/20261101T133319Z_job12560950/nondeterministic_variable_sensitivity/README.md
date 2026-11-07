# Non-deterministic variable sensitivity — evidence archive

Raw material behind `NONDETERMINISTIC_VARIABLE_SENSITIVITY_MEMO.md`, which is included here and
also sits at the root of the package. Section 9 of that document describes every directory below
and gives the commands that regenerate each of its tables from this archive, with no API calls.

Nothing in this archive is read by the replication pipeline. It is evidence for the sensitivity
statements in the memo, retained because the language-model snapshots that produced the paper's
two model-generated inputs are withdrawn on a vendor timetable: once they are gone, these responses
are the only record of what the instrument returned.

## Contents

| Path | What it holds |
|---|---|
| `price_links_full/` | 3,370 responses — 337 product codes x 10 draws of the price-link concordance |
| `price_links/` | a 200-response pilot, superseded by the census above |
| `invention_years/` | 125 responses — the 25 archived validation queries x 5 draws |
| `invention_years_2_1/` | 2,930 responses — 293 Class II->I codes x 10 draws, the ten substituted input files, and the market-age regression output for each |
| `invention_years_band/` | 3,360 responses — 672 codes x 5 draws, sampled on the 60-year maturity threshold |
| `invention_years_outofband/` | 1,500 responses — the 300-code out-of-band control |
| `price_pipeline_runs/` | the price estimate table for the deposited concordance and for each of the ten draws |
| `lda_seed_runs/` | ten topic-model refits: the coherence sweeps, selected counts and topic effects |
| `validation_invention_years/` | a hand-coding sheet and protocol, drawn up but not used |

## One file needs a warning

`price_pipeline_runs/run_price_h.sh` runs `05_harness.py`, a variant of the deposited
`code/05_price_analysis.py` used only for this exercise. **It is not a replacement for the
deposited step and should not be used to reproduce the paper.** It differs in error handling
only: a price panel with no usable treated-control pairs is skipped and logged rather than ending
the run, and an uncomputable Conley-Taber estimate is reported as unavailable. Section 6.1 of the
memo records the two checks that establish the variant is inert wherever the deposited script
succeeds -- it reproduces the deposited estimate table byte for byte on the deposited concordance,
and on draws where both run to completion the two tables are identical.

## Format

One JSON object per line, one line per API call:

    productcode / pc    the FDA product code queried
    draw                0-based draw index
    model               the dated model snapshot, e.g. gpt-4o-2024-08-06
    raw_response        the reply, verbatim and unparsed
    usage               prompt and completion token counts
    deposited           the value in the deposited input, for comparison

No credential appears anywhere in this archive. The prompts are reproduced verbatim from the
deposited generation scripts; the queries are rebuilt from deposited inputs.
