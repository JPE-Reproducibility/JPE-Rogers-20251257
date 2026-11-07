# Non-deterministic variable sensitivity

**MS 20251257, "Regulating the Innovators"**
Parker Rogers

Two of the paper's inputs are produced by a language model, and the topic models behind Appendix
Figure D.5 are fitted from a random seed. None of the three is reproducible by re-running it: the
same prompt returns different answers, and the same corpus fits differently under a different seed.
This document measures how far the published quantities move as a result.

Five exercises are reported. Each runs at **ten draws**, or ten random seeds for the topic models,
except the two noted in sections 3 and 4, where the quantity is stable enough that further draws
buy nothing. Every raw response, log and estimate table is retained; the final section lists the
archive and the commands that regenerate each table in this document.

What these exercises establish is instability under repetition. Whether the model applies the
paper's measurement definitions *accurately* is a separate question, addressed in section 2 for one
input and left open for the others; section 8 says what that leaves unresolved.

---

## 1. Where the model-generated inputs enter the paper

Before measuring instability I traced every consumer of both inputs through the deposited
code, because the answer determines what the exercise has to cover.

**Invention years** (`12_invention_year_generation.py`, `model="gpt-4o"`, `temperature=0`)
reach the manuscript through three channels:

1. The correlation between the model's years and my own hand-coded years for the 25
   down-regulated Class III→II device types, computed at
   `15_intext_derived_numbers.py:852` and graded by the in-text number gate. The
   manuscript prints it in a footnote, in the body, and in the caption to the market-age
   histograms described next.
2. The two market-age histograms captioned "Histogram, Market Age of Current Class III
   and II Devices" (`fig:DeviceExperienceCurrent`; the files
   `Distribution_of_3_over_years.png` and `Distribution_of_2_over_years.png`), and the
   associated count of Class II device types with more than sixty years of device
   experience. These are built at `11d_reg_design.py:1395-1508` from the broad
   all-product-code file, which the code's own comment flags as "not just the
   matched/treated sample".

3. **Market age for the Class II→I transition, which enters a regression.**
   `12_invention_year_generation.py:330,348-349` writes
   `innovation_year_2_1_FDA_project.csv` (293 product codes) from `model="gpt-4o"`.
   `11d_reg_design.py:775-782` reads it and forms
   `exp_years = year_reclassified - yr_invent`; that variable is a regressor at
   `11d_reg_design.py:859-863`, and its slope, standard error, p-value and fitted
   zero-crossing are all reported. The manuscript states the dependence outright: "I identify
   the introduction year using hand coding supplemented by GPT-4o adjudication for Class II
   devices." Section 5 measures this channel.

The Class III→II age variable is **not** model-generated, which matters for reading section 5.
`innovation_year_3_2_FDA_project.csv` carries the hand-coded years — verified as an exact sorted
multiset match to `yr_invent_or_comm_avail` in the validation file, and not a match to that
file's model `years`. Appendix Table D.1 reads that file only for its FDA-initiated indicator.

**The price-link concordance** (`12b_gpt_price_links_generation.py`, `MODEL = "gpt-5-mini"`,
API defaults) enters the price and utilization estimates through sample construction: it
determines which CPT codes a device's claims are matched to. The manuscript also reports
those estimates under an independent expert-coder concordance, which section 5 uses as a
control.

**One published regression coefficient is a function of a model output:** the Class II→I
market-age slope, through channel 3. The Class II→I decline in billed amounts is a second, less
direct case, estimated on a sample the concordance helps construct. Both are measured — the
market-age slope in section 5, the price estimates in section 6 — and the Class III→II
counterparts of both serve as controls, because they are built from hand-coded years and the
expert crosswalk respectively.

---

## 2. Price-link concordance: decision stability across ten draws

All 337 product codes in the deposited concordance, **ten** independent draws each, against
`gpt-5-mini-2025-08-07` — the snapshot current when the deposited concordance was built on
22 September 2025 — with the deposited prompt reused verbatim. 3,370 calls, no failures. The
model takes no temperature or seed argument in the deposited code, and none was added.

| Link decision across the ten draws | Codes | Share |
|---|---:|---:|
| Unanimous `no_link` | 186 | 55% |
| Unanimous `link` | 51 | 15% |
| Mixed | 100 | 30% |

| Code-set agreement, given a link | Mean pairwise Jaccard |
|---|---:|
| All 337 codes (empty = empty counts as agreement) | 0.866 |
| The 47 codes unanimously linked with a non-empty set | 0.817 |

Of the 51 unanimously linked codes, 30 (59%) return an identical CPT set in all ten draws.

The instability is concentrated at the extensive margin — whether a device links at all —
rather than in which procedure it links to.

Flip rates by direction: 86 of 301 codes (29%) in the Class II→I direction, 14 of 36 (39%)
in the Class III→II direction.

**A caution about how to read these shares.** "Unanimous across N draws" falls mechanically as
N rises: the mixed share was 22% at five draws and is 30% at ten, on the same items and the
same model, because a tenth draw gives every item one more chance to disagree. The two figures
are therefore not comparable across designs, and neither is an estimate of a fixed quantity.
The mean pairwise Jaccard is better behaved — it is 0.866 at both five and ten draws — and a
per-call flip probability would be better still. I report the unanimity shares because they are
interpretable, not because they are stable.

**Against the deposited file.** All ten draws reproduce the deposited decision for 234 of 337
codes (69%). Three codes (1%) are stable across all ten draws yet disagree with the deposited
value — down from eight at five draws, for the same mechanical reason. Those three are the only
ones that could reflect genuine drift in the model between September 2025 and now; the remaining
disagreement is within-draw sampling noise.

**On accuracy, for this input only.** The package ships
`data/raw/FDA_HCPCS_Xwalk_Moazzam.csv`, a crosswalk produced independently by two
AAPC-certified medical coders with third-coder reconciliation. The price step estimates on
both concordances and reports the expert versions under `sample="Expert"` and
`sample="Expert Matched"`. A reader can see directly what the choice of concordance was
between and what it changed. The Class III→II price figures the manuscript prints are the
expert ones.

---

## 3. Invention years: the published correlation

The 25 archived queries for the down-regulated device types, reused verbatim, five draws
each against `gpt-4o-2024-08-06` at `temperature=0`. 125 calls, no failures. This is the one
exercise left at five draws: the quantity is a correlation over 25 fixed items whose spread
across draws is already tight (SD 0.0050), so further draws buy almost nothing.

| | Value |
|---|---:|
| Device types whose returned year changes across draws | 5 of 25 (20%) |
| Mean spread among those, in years | 2.0 (max 6) |
| Device types where all five draws reproduce the archived 2024 year | 17 of 25 (68%) |

Setting temperature to zero does not deliver determinism.

The consequence for the published statistic is larger than the item-level churn suggests,
and I would rather report it than have it found.

| Correlation with my hand-coded years, n = 25 | r |
|---|---:|
| Archived 2024 responses, as deposited | **0.7574** |
| Five fresh draws | **0.5470** (SD 0.0050, range 0.5414–0.5538) |

The manuscript prints 0.76. The deposited value recomputes exactly from the raw responses
shipped in `data/raw/innovation_year_FDA_project.csv`; it does not reproduce from fresh
calls to the same model family.

Most of the gap is attributable to five device types where the 2024 response happened to
match my hand-coded year exactly. Excluding them:

| Excluding the 5 exact matches, n = 20 | r |
|---|---:|
| Archived 2024 responses | 0.7363 |
| Five fresh draws | 0.6776 (SD 0.0014) |

So the published correlation is not a knife-edge artifact of the full sample, but it does
depend materially on five fortunate matches that fresh calls to the model do not return.
The honest summary is that the statistic is reproducible from the deposited archive and is
not reproducible from the live API.

---

## 4. Invention years: the Class II maturity count

The second channel is a count, not a correlation, so instability only matters if it moves
years across the sixty-year threshold applied at `15_intext_derived_numbers.py:70`
(`MANUSCRIPT_MATURITY_THRESHOLD_YEARS = 60`, boundary year 1959).

I sampled on that threshold: all 612 product codes whose deposited year falls within six
years of 1959, plus 360 codes drawn from further out as a control, five draws each. 4,860
calls, no failures. This exercise is also left at five draws, because the published quantity it
feeds turns out to be stable to well under one per cent (below).

| Stratum | n | Year moves | Crosses the threshold | 95% CI on crossing |
|---|---:|---:|---:|---|
| Near-threshold (within 6 years) | 612 | 130 (21.2%) | 47 (7.7%) | [5.8%, 10.1%] |
| Out-of-band control | 360 | 99 (27.5%) | 9 (2.5%) | [1.3%, 4.7%] |

Out-of-band codes cross too, which is why I widened the control rather than assuming the
band contained all threshold movement. The reason is a long revision tail: among the 229
codes whose year moves, the spread is a median of 6 years but a mean of 11.7, a 90th
percentile of 27, and a **maximum of 139** — one code returns 1855 in four draws and 1994
in the fifth.

**The published figure, recomputed under each draw.** Rather than extrapolate, I applied the
figure's own method (`15_intext_derived_numbers.py:234-285`) to each draw: the population is the
510(K)-filtered subset of the invention-year file, merged to `Full_sample.csv`, restricted to the
post-2015 cross-section and deduplicated by product code, which is **2,235** product codes. Each
code's year is replaced by that draw's year where the study drew it and held at the deposited
value otherwise.

| | Count over 60 years | Share |
|---|---:|---:|
| Deposited | **651** | 29.1% |
| Draw 1 | 651 | 29.1% |
| Draw 2 | 655 | 29.3% |
| Draw 3 | 656 | 29.4% |
| Draw 4 | 647 | 28.9% |
| Draw 5 | 653 | 29.2% |

Mean 652.4, standard deviation 3.20, range 647-656 — a spread of 1.38% of the deposited count.
The deposited value of 651 reproduces the manuscript's printed "approximately 650 device types"
and "about 29%".

Coverage is what makes this a measurement rather than an extrapolation: **all 497 codes within
six years of the threshold were drawn**, and those are the only ones a modest revision can move
across it. The 1,449 codes held at their deposited year all sit more than six years out; at the
2.5% out-of-band crossing rate measured above they would contribute on the order of 36 further
crossings, running in both directions, which the table does not include.

---

## 5. Invention years: the Class II→I market-age regression

This is the one published regression coefficient that is a function of a model output, so it gets
the closest treatment.

I re-drew all 293 Class II→I product codes **ten** times against `gpt-4o-2024-08-06` at
`temperature=0`, 2,930 calls with no failures, then substituted each draw's invention-year vector
into the deposited tree and re-ran `11d_reg_design.py` inside the reference container. The
per-code treatment effects do not depend on invention years — only `exp_years` does — so the
substitution changes the regressor and nothing else. Each draw file carries the deposited schema
and row order, and only the years column differs. All ten runs completed.

The queries are not deposited: `innovation_year_2_1_FDA_project.csv` keeps only PRODUCTCODE and
years. They were rebuilt from the project-root input the generator names in its own comment,
`DPM2_1_1997/for_gpt_2_1_invention_dates.csv`, which holds exactly those 293 codes in the same
order as the deposited output. The system prompt is lifted verbatim from Part 2 of the deposited
generator, and the query is built the way Part 2 builds it, by concatenating device name and
regulatory description without a separator. **That input file is not in the package, so the
deposited archive does not currently make these queries reconstructible; it should be added.**

**Item-level instability, 293 codes × 10 draws.** This is the least stable of the three inputs.

| | Value |
|---|---:|
| Codes whose returned year changes across draws | 113 of 293 (39%) |
| Spread among those | median 7 years, mean 16.2, max 161 |
| Codes where all ten draws reproduce the deposited year | 136 of 293 (46%) |

For comparison, 68% of the hand-validated Class III→II codes reproduce their archived year. As in
section 2, the churn share rises with the number of draws (30% at five, 39% at ten) and is not an
estimate of a fixed quantity.

**The baseline control.** Re-running the step on the deposited invention years reproduces
`exp_impact_zero_crossings.csv` byte for byte and all four slope rows to 13-14 significant
figures, the residual being floating-point accumulation order. Movement in the draws is therefore
attributable to the invention years alone.

**The control that should not move does not move.** The Class III→II rows are built from
hand-coded years, and across all ten draws their slopes, standard errors, p-values and crossings
are identical to every printed digit — standard deviation exactly zero.

| Class III→II (hand-coded control) | Slope | s.e. | p | Crossing |
|---|---:|---:|---:|---:|
| Serious events, every run | −0.017012 | 0.008465 | 0.0597 | 28.5 yrs |
| Patents, every run | −0.039626 | 0.013161 | 0.0079 | 42.5 yrs |

**The published Class II→I results, ten draws.**

| | Deposited | Draws (n = 10) |
|---|---:|---|
| Slope, serious events | −0.0014978 | mean −0.001312, SD 0.000122, range [−0.001463, −0.001048] |
| p-value | 0.2182 | 0.1882 to 0.3473 — insignificant in every draw |
| Fitted crossing | 61.1 yrs | mean 62.8, range 60.6 to 64.2 |

The slope is negative in all ten draws, the coefficient remains insignificant throughout, and the
fitted crossing stays between 60.6 and 64.2 years — so the manuscript's "roughly 60 years" holds
under every draw.

The patent slope is near zero in every draw (−0.000004 to +0.000264 against a deposited
+0.000153, p between 0.769 and 0.996), matching the manuscript's "near zero for Class II to I".
One draw returns a very slightly negative value, so the sign is not technically preserved; at four
decimal places the estimate is zero in both directions and I would not read a reversal into it.
Its fitted crossing moves much more, 168.8 years to between 162.5 and 203.4, but that is an
extrapolation far outside the data and the manuscript does not print it.

**One asymmetry worth stating.** The deposited serious-event slope, −0.0014978, is larger in
magnitude than every one of the ten draws, so it sits at the edge of the re-draw distribution
rather than inside it. The gap to the draw mean is 0.00019, about 0.16 of a standard error, which
is immaterial for any inference. It holds across every draw rather than a subset of them, so it is
a property of the deposited value rather than an artifact of how many draws were taken. A reader
should know that rather than infer the deposit was a typical draw.

**What this does not establish.** It measures instability, not accuracy. The 25 hand-coded device
types are all Class III→II, so the Class II→I years — the ones feeding this regression — have no
hand-coded benchmark. Section 8 says what follows from that.

---

## 6. Downstream price and utilization estimates

I substituted each draw's concordance into the deposited pipeline and re-ran the price step inside
the reference container, ten times, then compared all 26 published estimates.

**The baseline control holds exactly.** Re-running on the deposited concordance reproduces
`output/tables/price_utilization_estimates.csv` byte for byte —
`sha256 5770132b78238475b3984fc8addb64901c5662d848d5d073aab69afae63fd1d8`, verified against the
archive member, and re-verified four times over the course of the exercise as the harness below
changed. Any difference in a draw run is therefore attributable to the concordance and nothing
else.

### 6.1 A harness change, and why it does not affect the deposited numbers

Three of the first five draws produced no estimate table at all. The reason is a detail of the
deposited script rather than of the data: it accumulates every estimate in a list and writes the
table once, after the last panel, so an exception raised while building any panel discards the
estimates already computed for the others. Two usable runs out of five was the result.

For this exercise I therefore ran a variant, `05_harness.py`, which differs from the deposited
`05_price_analysis.py` in error handling only. A panel with no usable treated-control pairs raises
a named `PanelUnbuildable` that the caller skips and logs; a Conley–Taber estimate that cannot be
computed is reported as unavailable, which is the same sentinel the deposited function already
returns for a panel with too few product codes. Nothing else is touched.

Two checks establish that this changes no deposited number. First, on the deposited concordance
the variant reproduces the estimate table byte for byte, with no panel skipped — so on the
deposited inputs the guards never fire. Second, on the two draws that produced tables under
**both** the deposited script and the variant, the two tables are identical. The variant is
therefore inert wherever the deposited script succeeds, and the only runs it changes are the ones
whose panels are degenerate. **Ten of ten draws yield estimates.**

### 6.2 Why the Class III→II panel fails, which is a result in itself

The diagnostic the harness adds counts the treated procedures entering each panel, and the
mechanism turns out to be monotone in a single quantity: how many treated device types link to a
procedure code that the claims data observes.

| Treated device types linking, Class III→II | Runs | Consequence |
|---|---|---|
| 0 | draws 3, 4 | no pairs to match — the panel cannot be built |
| 1 | draw 8 | `posttreat` is collinear with the fixed effects — the estimate is **void** |
| 2 to 5 | draws 1, 2, 5, 6, 7, 9, 10 | the panel builds and the estimates are computed |
| **3** | the deposited concordance | the published value |

So the Class III→II price panel rests on a handful of treated device types, the deposited
concordance supplies three, and a re-draw moves that count between zero and five. At one the
estimate is unidentified; at zero the panel does not exist. That is a quantitative statement about
how close this panel sits to the edge.

One explanation is worth ruling out explicitly, because the code invites it: a comment in
`05_price_analysis.py` records that one tacrolimus assay code is among the three treated codes this
panel carries, which makes that code look decisive. It is not. All ten draws decline to link it,
including every draw whose panel built successfully, so its absence cannot distinguish a panel that
builds from one that does not. The count of linking treated codes can.

One draw does not fit the pattern: draw 5 had three treated codes and built the panel, then lost a
single Conley–Taber estimate to a mis-shaped permutation grid. Sparsity is the main driver but not
the only one.

### 6.3 The estimates

| Class II→I billed amounts | Deposited | n | Mean | SD | Range |
|---|---:|---:|---:|---:|---|
| All CPTs, BJS imputation | −0.32 | 10 | −0.297 | 0.109 | −0.46 to −0.16 |
| All CPTs, Conley–Taber | −0.316 | 9 | −0.285 | 0.110 | −0.46 to −0.16 |
| Matched, BJS imputation | −0.23 | 10 | −0.235 | 0.076 | −0.35 to −0.08 |

The ten all-CPT values, sorted: −0.46, −0.43, −0.40, −0.37, −0.30, −0.28, −0.25, −0.16, −0.16,
−0.16. The estimate is negative in every draw and the interpretation never changes, but the
magnitude is pinned only to roughly a factor of three, and three draws sit at half the published
value. The deposited −0.32 falls inside the range and close to the mean.

This is where ten draws mattered. At five the two surviving runs gave −0.30 and −0.43, which made
the deposited −0.32 look like the centre of a tight cluster. It is not; it is a central value in a
wide one.

**Eight of the 26 estimates are invariant across every draw, and they are exactly the eight rows
built from the expert crosswalk** — standard deviation 0.0000 at ten draws, every value identical.
That is the control I would want to see, and it holds without exception.

**The fragile panel behaves as its mechanism predicts.** The Class III→II all-CPTs estimate is
available in seven of ten draws and ranges from −0.11 to +0.23 around a deposited +0.06, flipping
sign. The manuscript prints the expert-crosswalk figures for this pathway, −0.09 and −0.186, and
those do not move at all — which is the right design given what the model-concordance version
does under re-draw.

The utilization and quantity estimates move more, including changes of sign. They are reported in
a compact appendix table and no conclusion in the paper rests on them.

---

## 7. Topic models behind Appendix Figure D.5

The topic models are not model-generated, but they share the relevant property: a refit is not a
reproduction. I refitted them **ten** times inside the reference container, varying only the
random seed.

**The selected topic count is not stable, and the deposited exhibit is the minority outcome.**

| Seed | Class III→II | Class II→I | Topic effects | CI excludes 0 |
|---|---:|---:|---:|---:|
| 42 (deposited seed) | 10 | 15 | 25 | 18 (72%) |
| 1 | 15 | 15 | **30** | 23 (77%) |
| 2 | 20 | 15 | 35 | 24 (69%) |
| 3 | 10 | 25 | 35 | 19 (54%) |
| 4 | 10 | 10 | 20 | 16 (80%) |
| 5 | 10 | 15 | 25 | 17 (68%) |
| 6 | 10 | 15 | 25 | 18 (72%) |
| 7 | 10 | 10 | 20 | 14 (70%) |
| 8 | 10 | 10 | 20 | 14 (70%) |
| 9 | 15 | 10 | 25 | 18 (72%) |

The deposited models carry 15 topics in each sample, so the deposited exhibit has **30** topic
effects. Across ten seeds the count ranges from 20 to 35, mean 26.0 with a standard deviation of
5.4, and **only one seed in ten reproduces the deposited 30**. The share of effects whose
confidence interval excludes zero ranges from 54% to 80%. For the Class III→II sample the
procedure selects 10 topics under seven of the ten seeds, so the deposited 15 is itself the
minority selection.

Two mechanisms produce this. The dominant one is that the coherence surface moves with the seed,
so the maximum moves across the grid `range(10, 31, 5)` rather than sitting at one
value. The second is the tie-break in the selection rule: it takes the smallest topic count whose
coherence falls within `1e-3` of the maximum rather than the arg-max, preferring the smaller
model when the scores are effectively tied. At the deposited seed the Class III→II
scores at 10 and 15 topics are 0.4905 and 0.4907 — two ten-thousandths apart — so the rule selects
10 where an arg-max would select 15. The Class II→I sweep at the same seed sits on the same
boundary, selecting 15 at 0.5020 over an apparent maximum of 0.5030 at 20 topics. **The deposited
seed is on the tie-break boundary in both samples.**

### 7.1 Fixing the topic count

I have pinned the count at 15, the value the deposited models carry, and verified in three ways
that this changes nothing in the certified pipeline.

1. **The deposited code, frozen models present.** `11a_product_variety.py` run against the
   fourteen frozen artifacts reproduces `variety_2_1.png` and `variety_3_2.png` at exactly the
   hashes recorded in `certification/EXPECTED_EXHIBIT_HASHES.csv` (`b90a950d…`, `3f91ce66…`), and
   the log reads `Loading saved LDA model`. The selection code is never reached on the certified
   path, because the models are hash-pinned inputs.
2. **The pinned code, frozen models present.** Same two hashes, unchanged. The pin introduces no
   side effects.
3. **The pinned code, models deleted — a forced refit.** The procedure selects 15 topics in both
   samples and produces exactly 30 topic effects, matching the deposited exhibit's shape, where
   the seed-dependent tie-break gave anywhere from 20 to 35.

So pinning is a code-only change: no deposited number, figure or output hash moves, and a refit
now reproduces the deposited topic count instead of drifting with the seed. The constant is
written as a named `PINNED_TOPIC_COUNT = 15` with the reasoning in a comment, since a replicator
will read it.

One consequence for the deposit: because this edits a deposited code file rather than adding a
new one, it cannot be supplied as a companion upload the way the confidential data can. The
archive is certified against a fixed file manifest, so folding the pin in means a re-certified
build. The change is implemented and verified; when that build happens is a scheduling question,
not a technical one.

A residual remains that pinning cannot remove: a refit on a different platform agrees with the
deposited fit only to within 4e-4 on the topic distributions and 8e-4 on the concentration
parameter, gensim records the saving platform inside the model file, and the refit figures differ
from the deposited ones at the byte level. Freezing the fourteen artifacts as hash-pinned inputs
is what makes the exhibit reproducible; pinning the count is what makes a refit agree about the
exhibit's shape.

**Two conclusions, offered rather than defended.** First, freezing the artifacts is the right
design, and the deposit says so. Second, a coherence-maximising topic count is not identified here
in any useful sense — one seed in ten reproducing the deposited shape is the clearest evidence of
that — and a reader should not take the specific number of topics in Figure D.5 to carry
information it does not. Figure D.5 is an appendix exhibit and no result in the paper depends on
it.

---

## 8. Limitations

**Ten draws give a shape, not a standard error.** Ten is enough to see where a quantity sits and
how wide its spread is. It is not enough to characterize a distribution's tails, and none of the
spreads here should be read as a sampling standard error for an estimator. Where a number is
sensitive to the draw count I have said so on the spot: the unanimity shares in sections 2 and 5
rise mechanically with the number of draws and are not estimates of fixed quantities.

**Ten draws is close to the minimum that characterizes these quantities.** Each of the headline
results reads differently at five. Five draws of the price concordance put the Class II→I decline
in a narrow band near the deposited value; ten show a wide spread with the deposited value near
its centre. Five put the invention-year churn at 30%; ten put it at 39%. Five seeds give the same
20-to-35 range for the topic exhibit, but only ten make it visible that one seed in ten reproduces
the deposited shape. Anyone repeating this design should treat five as a lower bound on what it
takes to see the shape of these distributions, not a sufficient number.

**The original instrument may be unrecoverable.** My scripts named the model by alias rather than
by dated snapshot, so the September 2024 invention-year queries went to whichever snapshot was
then current. Querying `gpt-4o-2024-05-13` to test whether that was the target returns HTTP 404 —
the snapshot is retired, though still listed in the models endpoint. The whole `gpt-4o` family
leaves the API in January 2027. The only reason the published correlation can be reproduced at all
is that the 25 raw responses ship inside the deposit. That seems to me the practical lesson: pin
the snapshot, and archive the raw responses, because the model will be withdrawn long before the
paper stops being read.

**The maturity count is measured, with a stated residual.** Section 4 applies the figure's own
method to each draw over the full 2,235-code population. Every one of the 497 codes within six
years of the threshold was drawn; the 1,449 held at their deposited year all sit further out, and
their residual contribution is stated rather than folded into the table. That exercise is at five
draws, which is defensible only because the quantity moves so little.



**What I have not done.** I have not commissioned additional hand coding, and I have not
re-estimated anything with a correction for classification error. The paper was accepted on its
current evidence; this memo documents variability under re-draw, which is what was asked for.

---

## 9. Archive and reproduction

Held at `LLM_REDRAW_STUDY_20261027/`, **11,485 raw API responses across eight JSONL files**, 19 MB
in total. One JSON line per call, each carrying the model id, the draw index, the prompt inputs,
the full raw response, the parsed value, the deposited value for comparison, and token usage. No
credential appears anywhere in the archive.

| Path | Contents |
|---|---|
| `price_links_full/` | 3,370 responses (337 codes × 10 draws, in `raw_responses.jsonl` for draws 1-5 and `pl_full2/` for 6-10); `analyze_full.py` produces section 2, `build_draw_concordances.py` turns the responses back into the ten substituted concordances |
| `price_links/` | 200-response pilot, superseded by the census above |
| `invention_years/` | 125 responses, 25 archived queries × 5 draws; `analyze_correlation.py` produces section 3 |
| `invention_years_band/` | 3,360 responses, 672 codes × 5 draws; `analyze_pooled.py` produces section 4 |
| `invention_years_outofband/` | 1,500 responses, the 300-code control extension |
| `invention_years_2_1/` | 2,930 responses (293 codes × 10 draws, two batches), the ten substituted input files, six output tables per run, `RESULTS_slopes.txt`, `RESULTS_maturity.txt`; `run_2_1.py`, `run_2_1b.py`, `build_draw_files.py`, `run_11d.sh`, `cmp_11d.py`, `maturity_denom.py`, `maturity_sensitivity.py` produce sections 4 and 5 |
| `price_pipeline_runs/` | Estimate tables under `hresults/`: ten draws plus four baseline runs, the baseline having been re-checked as each guard was added. `results/` holds the runs made with the deposited script unmodified. `cmp_price.py` produces section 6 and `RESULTS_price_10draw.txt`; `run_one.sh` and `run_price_h.sh` are the invocations |
| `lda_seed_runs/` | Ten refits: `coherence_sweeps.txt` (the per-k sweeps and the selected counts) and `results/seed_*/estimates.txt` (the topic effects); `analyze_selection.py` produces section 7 from these. The 45 MB of gensim training logs the sweeps were extracted from are not deposited. The pinned variant and its three verification runs sit alongside |

To regenerate the tables in this memo from the archive, with no API calls:

    python3 price_links_full/analyze_full.py                       # section 2
    python3 invention_years/analyze_correlation.py \
        <package>/data/raw/innovation_year_FDA_project.csv         # section 3
    python3 invention_years_band/analyze_pooled.py                 # section 4
    python3 invention_years_2_1/cmp_11d.py \
        invention_years_2_1/results                                # section 5
    python3 price_pipeline_runs/cmp_price.py \
        price_pipeline_runs/hresults                               # section 6
    python3 lda_seed_runs/analyze_selection.py                     # section 7

Two further scripts rebuild the substituted inputs rather than a table:
`invention_years_2_1/build_draw_files.py` turns the invention-year responses back into the ten
input files, and `price_links_full/build_draw_concordances.py` does the same for the ten
concordances. Each run of the first prints the item-level instability in section 5.

The LDA refits, the price pipeline runs and the market-age regression runs were executed inside
the reference container `fda_np126.sif`; `price_pipeline_runs/run_one.sh` (deposited script),
`price_pipeline_runs/run_price_h.sh` (the section 6.1 variant) and `invention_years_2_1/run_11d.sh`
are the exact invocations. The two maturity scripts reproduce section 4's population and per-draw
counts from the same tree.

**On running the harness.** `05_harness.py` is a sensitivity-exercise variant, not a replacement:
`code/05_price_analysis.py` remains the authoritative step. The variant differs in error handling
only, and section 6.1 records the two checks that establish it is inert where the deposited script
succeeds.

Every table above regenerates from the archive without further API calls, so the exercises can be
extended to more draws, or applied to another exhibit, from the material as deposited.
