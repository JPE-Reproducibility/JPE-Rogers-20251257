# Coding protocol — invention-year validation sample

## Files

- `coding_sheet_BLIND.csv` — 300 product codes in random order. **Contains no model output.** Give
  this to coders.
- `sample_KEY.csv` — stratum, design weight `pi`, and the model's year per row. **Withhold until
  coding and adjudication are complete.**
- `definition_invention_year.md` — the rubric. Read it before coding.
- `score_validation.py` — computes the error table and the signed-bias test once coding is in.

## Sampling design (already executed, seed 20260803)

Drawn from the 2,784 Class II/III product codes that carry a model year and merge to the FDA
classification file. Stratified on submission type and on distance from the sixty-year maturity
boundary, oversampling the near-threshold band because that is where a classification error moves a
published number.

| stratum | N | n | pi |
|---|---|---|---|
| 510(K), within ±6 yr of 1959 | 588 | 173 | 0.2942 |
| 510(K), further out | 2,066 | 114 | 0.0552 |
| PMA, within ±6 yr of 1959 | 24 | 7 | 0.2917 |
| PMA, further out | 106 | 6 | 0.0566 |

Every estimate computed from this sample must use design weights `1/pi`. Unweighted means are not
estimates of anything.

## Procedure

1. **Two coders, independently and blind.** Coders must not see the model's year, each other's
   labels, or `sample_KEY.csv`. Device domain knowledge is required; a general research assistant
   applying this rubric is not a valid coder.
2. Each coder fills `coder_year` (four digits, or blank for undeterminable), `coder_source` (the
   study or patent relied on), `coder_confidence_1to5`, and `coder_notes`. Save as
   `coding_sheet_coder1.csv` and `coding_sheet_coder2.csv`.
3. **Adjudicate every disagreement explicitly** and keep all three columns — coder 1, coder 2, and
   the adjudicated label. Inter-coder disagreement is the ceiling on measurable model accuracy and
   belongs in the write-up.
4. Run `score_validation.py`. It reports, with design weights: the share of codes where the model's
   year differs from the adjudicated year by more than a tolerance you choose; the signed mean error
   `E[model - hand]`, which is the bias in the units of the measure; the share misclassified across
   the sixty-year boundary, which is the quantity that moves the published count; and all of these
   by stratum.

## What a coder should not do

Do not look up what the model said. Do not resolve a hard case by majority vote with a chatbot —
agreement among models is correlated error, not evidence. Leave it blank and note it.
