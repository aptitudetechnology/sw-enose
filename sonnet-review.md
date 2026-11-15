# Review of the sw-enose work (Sonnet 5.5, 15 Nov 2026)

Scope: the commits from `b4245e8` (air-to-mucus) to `291e262` (ceiling and sparse-coding fix), all on
`main`. I checked repo state, ran the tests, spot-checked transcribed data against the fetch agents'
reports, and tested two headline claims directly. I did not re-derive every number or re-read every
source page.

## State

- Seven commits, all merged to `main`, working tree clean.
- 100 tests pass (about 5 s).
- Eight demos run.

## What holds up

- **Provenance discipline.** I spot-checked the Henry constants against the fetch agents' reports. The
  geometric means, low/high spreads and notes match. The temperature coefficient has the right sign:
  `H(T) = H_ref * exp(c * (1/T - 1/T_ref))` with positive `c` makes a compound less soluble when warmer.
- **Honest self-correction.** Several mistakes were found and fixed rather than left in:
  - an invented Henry band that produced a wrong "ppm for every odorant" headline;
  - a stale 2015 citation that the source site says is obsolete;
  - a ceiling estimate that was not actually a ceiling, because normalisation scored above it.
- **The `fan_in` fix is real.** Sparse-code accuracy on the acid panel went from 0.46 to 0.90. The
  ratio rule reproduces Dasgupta's own value of 6 at 50 glomeruli, and a test asserts that.
- **Refusals instead of guesses.** `air.py`, `coverage.py` and `restrict_to_tested` raise rather than
  invent a value. The `narrow_odorants` fix removed a real source of mislabelled columns.

## Problems

### 1. "This array cannot separate C9 from C10" is contradicted by the repo's own data

`demo_ceiling.py` and the README present a cosine similarity of 0.926 between nonanoic and decanoic
acid as a hard ceiling: "a real nose separates C9 from C10; this array cannot... more software would
not [help]". That does not follow.

- Rule 4 makes only *identical* profiles (cosine 1.0) indistinguishable at any noise level. A
  similarity of 0.93 is a distance, and whether it can be resolved depends on noise.
- I ran C9 against C10 as a two-way nearest-centroid problem at 200 uM:

  | neuron noise | accuracy |
  |---|---|
  | 0.02 to 0.40 | 1.000 |
  | 0.80 | 0.968 |

- The overall ceiling of 0.998 reported by `demo_ceiling.py` already implied this, since it includes
  those pairs.

So the paragraph about "where the bound is" overstates what the receptor data forbids. Similarity
becomes limiting only when noise is large relative to the gap. The section should be rewritten around
a noise-dependent statement: how much noise each pair tolerates before accuracy falls.

### 2. The efficacy conclusion is weaker than the README says

The README says the data "contradicts the assumption" that efficacy is 1.0. The supporting spread
comes from Singh curves where:

- **17 of 24 do not saturate** below the assay ceiling. For those, only `A/EC50` is pinned down and `A`
  itself is not identifiable, so some of the 0.03 to 1.0 spread may be fit degeneracy.
- Dividing by the largest `A` at each receptor forces one value of exactly 1.0 per receptor, so a
  third of the sample is 1.0 by construction.
- The sample covers 8 receptors, 3 odorants, one paper and one assay.

`uncertainty.py` hedges this correctly ("an order-of-magnitude statement, not a distribution"). The
README does not. What the work shows is that conclusions are sensitive to efficacy across a plausible
range. It does not show that efficacy = 1 is wrong.

### 3. "No sensitivity gap left to explain" is premature

For the water-soluble acids the README says there is no sensitivity gap, because half-maximal EC50s
are reached at tens to hundreds of ppb, "the range noses work in".

- An EC50 is a half-maximal receptor response. A detection threshold lies well below that.
- The same README says nothing has been compared with human detection thresholds.

Those two statements cannot both stand. The accurate version is that the earlier ppm-everywhere
conclusion was an artefact of invented constants, and that the gap is now unmeasured rather than
resolved.

### 4. Smaller points

- **~400 intact human receptors** is used for the "24% of the repertoire" figure. The audit file says
  repertoire counts were not verified at source, so this number is unsourced in the repo.
- **Adaptation conclusion:** "matters" was defined as an ordered trend above the reseeding floor, and
  both trends have a spread of only 0.08 to 0.11 against a floor of 0.07. That is thin, and on a
  static presentation adaptation can only subtract signal. The README says this, but "all three
  testable stage parameters matter" reads stronger than the evidence.
- **Heptanoic temperature coefficient:** 8500 K is taken from a type-V row, while C5 and C6 use
  measured values near 6000 to 6900 K. That is a visible jump in an otherwise smooth series.
- **The `fan_in` choice** came from a scan against the same synthetic task it was then scored on. The
  improvement is large enough that this is unlikely to change the conclusion, but it is not held-out.

## Recommended follow-up

One commit that:

1. rewrites the C9/C10 and "ceiling" wording to match the measurement above, ideally with a
   noise-tolerance table per pair;
2. qualifies the efficacy section, and says how many of the underlying curves are unconstrained;
3. replaces "no sensitivity gap left to explain" with "unmeasured pending threshold data";
4. marks the 400-receptor figure as unverified.

The human detection-threshold comparison remains the one check that could change the overall verdict.
