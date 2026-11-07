# Publishable Simulation Design

**Supporting reference; `README.md` governs.** `README.md` is the single documentation point for this
package; this file is the design detail behind its "The simulation programs" section.

This simulation is an independent synthetic universe, not perturbed or relabeled real microdata.

## 1. Public design retained

The simulation may retain documented public FDA product codes, calendar/panel structure, Federal
Register reclassification design, FDA descriptors/taxonomies, and other public inputs listed in the
rights matrix. Public structure is not treated as a privacy claim and is reported separately by the
audit.

## 2. Stage A: authorized parameter extraction

Stage A runs only in the authorized environment:

- `gen_00a_extract_parameters.py` emits rounded cardinalities, smoothed size families, rounded
  missingness rates, file schemas, and the public master skeleton;
- `gen_00b_pc_effects.py` creates seeded product-code random effects from public design inputs.

Four committed artifacts drive Stage B:

1. `simulation_parameters.json`;
2. `simulation_schema_contract.json`;
3. `public_master_skeleton.parquet`;
4. `pc_effects.parquet`.

The first two are restricted-derived. Their file-level publication-rights review is complete — both are
author-signed `APPROVED_TO_SHIP` for redistribution as an author representation (see
`certification/COMMITTED_PARAMETER_RIGHTS.csv` and `certification/rights_evidence/`; not an
independently verified legal opinion), so their inclusion in the final deposit now depends only on the
package passing the confidential T5/T6 disclosure review (privacy) and the Data Editor's separate
technical acceptance of the rounded dimensions. Stage A is not a public clean-room step because it
reads licensed sources.

## 3. Stage B: standalone public generation

`build_simulation.py` invokes `gen_00c` through `gen_00i`. Stage B reads only the four committed
artifacts, documented public inputs, and the public seed (`PUBLIC_SEED = 20260803`, stated at the
top of `build_simulation.py` and turned into per-file generators by
`generators/independent_universe.iu_rng`). It must not read `data/raw`, `data/derived`, host caches,
credentials, APIs, or network resources. It generates the complete fixed 118-file payload covering
Dimensions/patents, WRDS/firm interfaces, MarketScan aggregate interfaces, Nexis, MAUDE linkage
inputs, KPSS/KPST support files, price links, and safety text.

The MarketScan portion is a synthetic implementation of the author-defined aggregate interfaces. It
does not contain or reconstruct NBER's proprietary raw variables or source-acquisition program.

### 3.1 `Applicant_Cites_Only.csv` — a universe-derived file with no committed spec

Almost every simulated file is sized and typed by a committed per-file interlock spec
(`simulation_parameters.json["files"]`). `synthetic_patents/Applicant_Cites_Only.csv` — the
forward-citation lookup `code/09_summary_stats.py` merges onto the patent panel for the
"Citations per Patent" rows of Table 1 and Table D.14 — is generated without one, so that no new
restricted-derived parameter had to be extracted for it. Everything it needs is already fixed by
artifacts that ship:

- **Rows.** Exactly one row per patent in the simulated patent universe, so its row count equals
  `entities.patents.cardinality`, the committed ROUNDED patent cardinality already published for
  the other patent files. The row count is therefore a documented function of the simulated
  universe, not an approximation to a real extract size.
- **Key.** `USID` is that universe's `patnum` — the digit core of the `US-<patnum>-B2` identifiers
  the other patent files carry — so the merge in step 20 resolves for every patent and the key is
  unique by construction. Values lie in the synthetic patent domain (>= 90,000,000); the generator
  refuses to write anything below it.
- **Product code.** The universe's already-resimulated PUBLIC FDA product code.
- **Outcome.** `times_cited ~ Poisson(theta.mu_cite[PRODUCTCODE])`, drawn through `iu_rng` — the
  same seeded product-code random-effects table (`pc_effects.parquet`) the PC-year citation panels
  use.
- **Schema.** Column names, order and kinds are the real file's structural metadata (`USID`
  integer, `PRODUCTCODE` string, `times_cited` integer). No real value is read or retained.

`gen_00e` and `gen_00d` FAIL rather than print `SKIP` when a file listed for generation has no
committed spec and is not on the short, explicit spec-free list, so a payload cannot ship with a
simulated input silently missing.

### 3.2 Two further spec-free twins: the hand-linked manufacturer crosswalk and the expert concordance

Two more payload members are generated without a committed interlock spec, for the same reason: the
only thing either needs from the real file is its HEADER, and taking a header is not an extraction.

**`synthetic_maude_linkage/manual_permno_corrections.csv`** (written by
`generators/gen_00i_synthetic_maude_linkage_inputs.py::write_manual_permno_corrections`, materialized
to `data/raw/manual_permno_corrections.csv`). The real file is the hand-coded
manufacturer-name-to-CRSP-PERMNO crosswalk; CRSP PERMNO is proprietary, so it is excluded from the
deposit. Step 35 counts its rows for the in-text "hand-linked manufacturers" number, so without a
twin that registered scalar was a missing input on the simulated route and the strict in-text gate
could not pass. The twin reproduces the real file's column names and order, its column dtypes and its
row count (70) — the row count being the figure `README.md` and `WRDS_EXTRACTION_ROADMAP.md` already
state publicly — and nothing else. It deliberately does NOT reproduce the real file's per-column fill
pattern: every cell of every column is populated by a fixed rule written in the generator (a
non-boolean truthy token where the real column reads as `object`, a numeric literal where it reads as
`float64`, and a two-element pattern on every tenth `contains` row plus a one-element list on row 5,
so both of `gen_07`'s `json.loads` branches are exercised). Every name in it is a synthetic
manufacturer name this generator itself produced, and every PERMNO comes from the synthetic PERMNO
domain that also backs `compustat_firm_data.csv`. Rows are selected by a fixed stride over that
sorted domain, and the writer draws no random numbers at all, so two clean generations are
byte-identical.
`gen_07`'s synthetic branch does not read the crosswalk, so the twin changes nothing about how the
simulated linkage is built.

**`synthetic_price_links/FDA_HCPCS_Xwalk_Moazzam.csv`** (written by
`generators/gen_00c_synthetic_marketscan.py::_write_synthetic_expert_crosswalk`, materialized OVER
`data/raw/FDA_HCPCS_Xwalk_Moazzam.csv`). The real expert device-to-procedure concordance is public
and keeps shipping for the restricted-data reproduction, but it carries REAL HCPCS/CPT codes while
the simulated MarketScan claims are generated over the synthetic `Y####` procedure-code domain
described just below, which is disjoint from every real code space by construction. Without a twin
the two share no procedure code at all, the expert robustness sample in `05_price_analysis.py`
collapses to a handful of device types, and its four registered in-text scalars come out
non-finite. The twin is built over the public product-code
universe with procedure codes drawn from the SAME synthetic domain the claims are generated for, so
every link the analysis follows has claims behind it; a price-eligible product code draws only from
its own three synthetic codes, so no control code can inherit a treated code's procedure code. It is
deliberately a different concordance from the GPT price-link twins (one code per row over the whole
public universe, against all three codes for every price-eligible code), so the Expert sample stays a
genuinely distinct robustness sample rather than a copy of the baseline. Row count,
rows-per-product-code and the share of rows carrying a procedure code follow the real file's
coverage shape.

### The synthetic procedure-code domain: `Y0000`-`Y9998`

The simulated MarketScan claims (`proc1`), the synthetic GPT price-link twins
(`hcpcs_cpt`/`hcpcs_level_2`) and the synthetic expert concordance (`HCCPS Category Code`) all draw
their procedure codes from one domain, defined once in
`generators/gen_00c_synthetic_marketscan.py` as `SYNTHETIC_CODE_PREFIX = "Y"` plus four digits.

The domain is chosen so that a synthetic code can never coincide with a real one:

- **HCPCS Level II** codes are one letter plus four digits, and the letters in use are
  A, B, C, D, E, G, H, J, K, L, M, P, Q, R, S, T, U and V. `Y` is not among them.
- **CPT Category I** codes are five digits with no letter. **CPT Category II**, **Category III** and
  the Proprietary Laboratory Analyses codes are four digits plus a letter *suffix* (`####F`,
  `####T`, `####U`), so a *leading* letter cannot collide with those either.
- Of the letters HCPCS and CPT never use (I, N, O, W, X, Y, Z), this domain avoids `I` and `O`
  because they read as the digits 1 and 0 in a code column, and `X` because it has been floated for
  temporary Medicare codes. Of the four that remain (N, W, Y, Z), `Y` is the only one that also
  coincides with nothing in the wider value corpus the disclosure audit compares against: that
  corpus pools free-form identifier and address fields from the other inputs, some of which happen
  to take a letter-plus-four-digit shape, and N, W and Z each collide with at least one of them in
  the range this generator uses while `Y` collides with none.
- A letter prefix also keeps the synthetic domain clear of the pure-digit code corrections wired into
  `05_price_analysis.py` (85002, 84155, 80197, 83010, 52352, 52336), and keeps `proc1` from being
  re-inferred as an integer column when the CSV is read back, which would break the committed column
  kind.

Disjointness from the three shipped public procedure-code files is checkable directly:

```
grep -cE '(^|,|")Y[0-9]{4}' data/raw/FDA_HCPCS_Xwalk_Moazzam.csv \
    data/raw/2_1_GPT_Price_Links.csv data/raw/3_2_GPT_Price_Links.csv
```

returns `0` for each. The predecessor domain used an `S` prefix, which *is* a live HCPCS Level II
letter; synthetic codes then coincided with the 97 real Level-II S-codes carried by the public
expert crosswalk, and the disclosure audit flagged the overlap as shared real values in a sensitive
column. Nothing about how the real-data route reads real codes changed.

This is the same override channel the GPT price-link twins already use: both files are staged under
`_synthetic_source_internal/`, published by `gen_00g`'s `synthetic_*` glob, and routed by
`materialize_simulation.py`. Neither generator writes into `data/`, and the real-data reproduction
never runs `materialize_simulation.py`, so it always reads the real files.

## 4. Independence and linkage

- Patent and firm identifiers are generated in disjoint fake domains.
- No real-to-fake map, rank permutation, real identifier hash, exact group-size multiset, or exact
  restricted row-count input is permitted.
- Synthetic keys remain internally consistent where analysis joins require them.
- Entity co-membership, restricted values, and missingness masks are generated anew.
- Downstream restricted-derived fields are recomputed from the synthetic master, not copied from real
  panels or caches.

## 5. Structural fidelity

Every simulated raw file is checked against the committed contract for path, column names/order,
coarse dtypes, formats, units/supports, required keys, cross-file joins, cardinality relationships,
temporal consistency, and estimator-required cells. Restricted row counts are approximations — two significant figures, set one rounding step above the nearest two-significant-figure value, so the real extract is smaller by half a step to one and a half steps — rather than copied exactly. Written JPE Data Editor acceptance of that close-row
implementation is required before deposit.

Structural fidelity is not numerical fidelity: synthetic estimates are expected to differ from the
paper. The design deliberately favors non-degenerate treatment/control/event-time support over matching
real restricted marginals.

## 6. Privacy acceptance

`THREAT_MODEL.md` fixes the T1-T7 adversary, tests, and thresholds before the clean generations.
The public gates test source isolation, identifier domains, deterministic integrity, schemas, and
archive boundaries. The confidential authorized-environment gates compare the exact package members
to real counterparts, test copied values/statistics, membership/co-membership/missingness advantage,
and recompute/perturb every restricted-derived Stage-A parameter.

A PASS means only that the package passed the predetermined disclosure-risk tests. It does not prove
non-disclosure and does not establish redistribution rights.

## 7. Determinism and official route

Two clean Stage-B generations must be byte-identical to each other and to the 118 files shipped in the
package. The simulated-data route then materializes one generated payload and executes:

```bash
python3 run_all.py --synthetic-from-raw --clean-output \
  --regenerate-safety-keywords --regenerate-safety-embeddings
```

`run_all.py` sets the strict in-text gate, the route and the determinism variables for every step itself,
so nothing has to be exported by hand. The archive-bound harness described in `README.md`, not this bare
development command, is the certification route. Acceptance is 36 steps succeeded / 0 failed / 0 skipped,
52/52 and 48/48 in the step-36 audit, all 118 in-text scalars computed and finite, all semantic and
lineage checks passing, and exact output identity with `output-simulated/`. No source acquisition is
simulated as a transformation waiver; every post-acquisition transformation must execute.

## 8. Invalidation rule

Any change to the seed, committed parameters, schema, generator, materializer, analysis code,
environment, manuscript, payload, or reference output invalidates the package and requires two new
generations, privacy review, rebuild, and complete archive certification.
