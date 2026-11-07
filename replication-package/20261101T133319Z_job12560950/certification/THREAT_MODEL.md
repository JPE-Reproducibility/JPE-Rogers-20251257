# Synthetic-data privacy threat model + parameter-disclosure review (frozen before generation)

**Supporting reference; `README.md` governs.**

**Final package freeze:** 2026-08-26, before the clean generations. Earlier development generations do not
count as certification evidence. **Amendments after the freeze (dated, so that the record is honest):**
on 2026-09-28 the T2 audit rules gained lineage-driven counterpart lookup, a label-vocabulary exemption
(≤ 12 symbols), a date-span baseline and a published-row-count exemption; on 2026-09-29/30 the T6 bar was
restated from "any change of a committed value under one-record removal fails" to "a change of more than
one rounding step fails" (bounded influence), and the committed parameters and the schema contract were
re-generated under rounding rules that satisfy it. The thresholds in §3–§5 are otherwise unchanged. Numerical thresholds below are the predetermined pass/fail bars for this package; results
are reported as **"passed the predetermined disclosure-risk tests,"** never "proves non-disclosure."

## 1. Protected facts (what must NOT be inferable from the shipped synthetic data)
Restricted sources: **MarketScan** (CCAE claims), **Dimensions** (patents), **WRDS/CRSP-Compustat** (firm
financials), **Nexis** (legal records). Protected:
- P1 — **Membership:** whether a specific real entity (firm/permno/gvkey, assignee/inventor, patent, enrollee-derived
  cell) is present in the restricted data.
- P2 — **Values:** any real restricted value (a firm's financials, a patent's citations/xi, a claim cell's payments).
- P3 — **Linkage / co-membership:** which real rows belong to the same real entity (firm↔patents, assignee↔inventor),
  and cross-file joins that reveal the real relational graph.
- P4 — **Rare groups:** the identity or composition of small/unique cells (a product-code with one firm; a rare
  procedure×year cell), which are re-identifying even without exact values.
- P5 — **Missingness structure:** a real per-row missingness mask that fingerprints a real record.

## 2. Assumed adversary knowledge
- A1 — Has the **complete shipped public deposit** (all generator code + the generated synthetic data + the public
  seed). **Factual note:** the committed artifacts — `simulation_parameters.json`
  (rounded cardinalities + smoothed size families + public product codes), the structural contract
  (columns/types/formats + rounded row-count approximations), the theta table `pc_effects.parquet`
  (synthetic random effects drawn from FIXED distributions), and `public_master_skeleton.parquet` (Full_sample's
  PUBLIC columns) — **are shipped**, so a Data Editor can **re-generate the entire synthetic universe** from
  scratch by running `synthetic_pipeline/build_simulation.py` (JPE confidential.html step 6). This does **not** weaken
  privacy only if: (i) every shipped parameter is rounded/smoothed/public, receives affirmative file-level
  publication-rights review, and passes the fail-closed
  `gen_00a.disclosure_review` (no exact count, no stored size multiset, no un-rounded rate); and (ii) this model was
  frozen before the final confidential test suite ran. Publication-rights review is a separate human/legal gate; a privacy PASS does not
  establish permission to publish a restricted-derived parameter.
- A2 — May have the relevant identifier universes through public sources or lawful external access, including firm,
  patent, FDA-device, and organization identifiers. This is deliberately stronger than assuming obscurity of an id.
- A3 — May hold **auxiliary public data** on the real entities (public firm financials, public patent metadata).
- A4 — May run the shipped Stage-B generators (`build_simulation.py`) and inspect every intermediate. This is the
  intended Data-Editor workflow, not just a conservative hypothetical: the Stage-B generators read only the shipped
  committed artifacts + the public seed. Stage A runs author-side; `gen_00a` reads licensed inputs while `gen_00b`
  uses public design inputs. Stage A is not part of the public rerunnable path. Its outputs ship only after separate
  privacy and publication-rights approval. Final byte-identical regeneration remains an acceptance gate.
- **Implication:** any deterministic function FROM a real public id TO a synthetic value is invertible by
  enumeration (this is exactly the 2026-08-03 finding). The design must contain **no real→synthetic mapping at all.**

## 3. Predetermined pass/fail thresholds (per test)
Run in the CONFIDENTIAL layer (needs the real originals; authorized environment; only a bound report retained),
EXCEPT the structural/inverse-mapping tests which are PUBLIC.

| # | Test | Layer | Threshold (FAIL if exceeded) |
|---|---|---|---|
| T1 | **Inverse-mapping (structural):** any deterministic formula in shipped code maps a real id → a synthetic value/id. | PUBLIC | **> 0** such mappings present → FAIL. Target: 0. |
| T2 | **Value/statistic-copy disclosure:** high-entropy restricted identifiers/strings are searched directly and after canonicalization, relocation, reversal, or numeric truncation; row-aligned restricted columns are tested for near-copying; exact real row counts, distinct counts, group-size multisets, and missing-value counts are prohibited (except a size the package itself publishes, e.g. the 70-row correction crosswalk). Public taxonomies and ordinary low-entropy support values are classified explicitly. This test does **not** claim an exhaustive arbitrary-tuple or sequence attack. | CONF | any restricted high-entropy corpus hit, prohibited exact statistic, or >90% row-aligned restricted-column copy → FAIL; sensitive non-date strings have zero-overlap tolerance; label vocabularies (a real column of at most 12 symbols, e.g. 0/1 flags) are classified explicitly rather than treated as sensitive strings, and date columns are held to a coincidence bound anchored on the independence baseline (real distinct dates over the calendar span), never below 30%. |
| T3 | **Membership inference:** adversary advantage distinguishing in-sample vs out-of-sample real entities from the synthetic data. | CONF | advantage **> 0.05** over random (0.5 AUC baseline → **> 0.55**) → FAIL. |
| T4 | **Co-membership overlap:** fraction of real same-entity row-pairs that remain same-entity in the synthetic partition, vs the chance rate. | CONF | overlap **> chance + 0.02** → FAIL (independent universe ⇒ ≈ chance). |
| T5 | **Rare-group representation:** committed parameters must not contain a real group-size multiset, value list, exact rare-cell table, or exact restricted cardinality. Synthetic conditioned cells must have support sufficient for every estimator. | CONF | any forbidden raw representation or exact restricted count → FAIL privacy; any required synthetic conditioned cell with zero support → FAIL functionality. This is a representation/support test, not a formal k-anonymity guarantee. |
| T6 | **Single-record influence (parameter-level):** removal of one real record at each relevant worst-case boundary is applied to every restricted-derived Stage-A row count, schema-contract rounded dimension, id cardinality/size-family field, and numeric missingness rate; the published (rounded) parameter must not move by more than one of its own rounding steps (a count by more than its rounding base, a rate by more than 10^-3, a size-family moment by more than one unit in its last significant figure), so no parameter reveals more than its declared granularity. A rounding function necessarily has boundary values at which one record shifts the rounded value by exactly one step; that shift is the granularity itself, not a disclosure, and is permitted. | CONF | any published parameter moving by more than one rounding step after the tested one-record removal, or either restricted-derived committed artifact differing from authorized-input recomputation, → FAIL. No differential-privacy claim is made. |
| T7 | **Missingness mask:** row-level overlap of a synthetic mask with a real mask; rare-mask uniqueness; cross-file mask co-occurrence; missingness-based linkage. | CONF | any restricted (non-public-determined) mask row-identical to real, or a mask-based linkage advantage **> 0.05** → FAIL. |

## 4. Cumulative-disclosure test (aggregate risk across all tests)
Individual tests passing is necessary but not sufficient — combined leakage can exceed any single test. Predetermined
cumulative rule: T2 and T5/T6 must have **zero findings**, and the sum of the measured T3, T4, and T7
membership/linkage advantages must be **≤ 0.05**. If the aggregate exceeds 0.05, the run FAILS regardless of
the individual thresholds. This is a combined threshold over the implemented attacks; it is not a universal
reconstruction guarantee.

## 5. Parameter-disclosure + licensing review (some committed parameters are restricted-derived)
Every committed parameter that drives generation is inventoried BEFORE generation with: source, granularity,
derivation, licensing basis, privacy status, and its T5/T6 threshold. Rules:
- **Do NOT commit exact real group-size distributions, rare-cell counts, or any parameter that fails T5/T6.** Prefer
  parameterized/smoothed families (fitted distributions, capped/rounded marginals) that satisfy the structural-
  fidelity gate (rounded rows, exact columns/types/formats, support, and ≥1 observation per conditioned cell)
  without carrying a re-identifying real signature. Written Data Editor acceptance is required for the rounded-row
  deviation from the formal same-row-count instruction.
- Each parameter's **licensing basis** must permit publication (aggregate/derived-and-cleared, or public). A
  parameter derived from a restricted source that its license forbids publishing is not committed.
- The parameter inventory + its per-parameter T5/T6 results are frozen here and re-verified against the exact
  package members in the authorized environment. Publication-rights approval is recorded separately and must be
  affirmative for every committed artifact before build promotion.

## 6. Reporting language (mandatory)
Report outcomes as **"passed the predetermined disclosure-risk tests (T1–T7 + cumulative), final package thresholds
frozen 2026-08-26 and amended as dated above."** Never "proves non-disclosure." The confidential-layer report binds the restricted-input hashes,
parameter hashes, thresholds, audit-code hash, environment digest, raw log, exit status, and the package ZIP SHA
(Phase 8, §EVIDENCE_INDEX).
