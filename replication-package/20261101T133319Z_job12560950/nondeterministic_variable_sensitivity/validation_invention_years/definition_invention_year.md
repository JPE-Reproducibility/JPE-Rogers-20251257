# Measurement definition — device-type invention year

⚠ **Written retrospectively.** The classifier ran in September and December 2024; this document
reconstructs the definition from the prompt deposited verbatim in
`code/12_invention_year_generation.py`. It is therefore a record of what the instrument was asked to
do, not a specification frozen before measurement. State that plainly in any write-up.

## The definition proper

For a medical device **type** (an FDA product code, not an individual product), the invention year is
the earliest year in which a device of that type was introduced, established by whichever of the
following came first:

- the earliest academic study presenting the device, or
- the first patent filed by its inventor.

A domain expert should be able to apply this without seeing any model output.

## Unit of observation and input shown

One FDA product code. The text shown to the instrument is the concatenation of `DEVICENAME` and
`DESCRIPTION_OF_REGNUM` from the FDA product classification file — nothing else. No regulation
history, no submission dates, no patent corpus. Coders are shown the same three fields so that the
comparison is like for like.

## Output format

A four-digit year plus a source, returned as `['Year: YYYY', 'source: ...']`.

## ⚠ The definition conflates two distinct objects

The analysis variable is named `yr_invent_or_comm_avail` — *invention or commercial availability*.
These are different dates and can differ by many years. The prompt asks for invention (first study or
first patent filing); the variable name admits commercial availability. **Coders must code invention
as defined above**, and any write-up should acknowledge the ambiguity rather than paper over it.

## Adjacent objects this must be distinguished from

| Not this | Why it differs |
|---|---|
| First FDA clearance or approval year | Regulatory milestone, typically years after invention |
| First commercial availability | Market entry, after invention; see the conflation note above |
| Year the product code was created | An FDA administrative act, unrelated to invention |
| Year of the reclassification being studied | The treatment date, not a device characteristic |

## Boundary cases, resolved in advance

1. **Device type predates modern medicine** (sutures, forceps, scalpels). Code the earliest
   documented instrument of recognisably the same type. Centuries-old years are legitimate; the
   deposited data contains eight codes before 1800.
2. **Type is defined by a reagent or assay target.** Code the first assay for that analyte, not the
   first analyser platform.
3. **Type is a kit or system combining older components.** Code the first appearance of the
   *combination* as a recognised device type.
4. **Patent filing and academic study in the same year.** Either is acceptable; record which.
5. **Genuinely undeterminable from the three fields shown.** Leave `coder_year` blank and write
   `undeterminable` in `coder_notes`. Do not guess — a blank is information.

## What the measure is used for

Nothing in the paper's estimation. The years feed two descriptive objects only: the correlation
against hand-coded years on 25 treated Class III→II codes, and the Class II / Class III
device-experience distribution figures with the associated over-60-year maturity count. The
classification that matters for the count is binary — device age above or below sixty years in 2019,
i.e. invention year before or after 1959 — which is why the sample oversamples codes near that
boundary.
