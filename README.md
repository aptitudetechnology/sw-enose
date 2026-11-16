# sw-enose: a software-defined electronic nose

A biomimetic, software-defined electronic nose: a virtual receptor array whose signal is processed
the way animal noses process smell. **Everything here is modelled, not measured.**

Why biomimetic: the most capable noses are biological. We copy their architecture, stage by stage,
and say for each stage how well the biology behind it is established.

## How far along it is

| Part | Biomimetic? | Status |
|---|---|---|
| Processing stages (binding, convergence, adaptation, normalisation, sparse code) | Yes, modelled on animal olfaction | Built, tested on synthetic data. Stages 1 and 4 verified in cells or flies; stages 2 and 3 use invented numbers; stage 5 from a modelling paper. See `sources/AUDIT_*.md` |
| Receptors themselves | **Partly**: real human EC50s from M2OR (`sw_enose/m2or.py`, `demo_m2or.py`) | 626 measured agonist pairs across 128 reference receptors. Efficacy assumed, and `demo_uncertainty.py` shows that assumption **changes the answer** near threshold; untested pairs (most of them) treated as no response |
| How much the answers depend on what we don't know | — | Measured (`sw_enose/uncertainty.py`, `sw_enose/coverage.py`, `demo_uncertainty.py`), paired over 12 seeds. Efficacy matters strongly; convergence only at an extreme setting; adaptation marginally |
| Is the pipeline using the information the receptors give it? | — | Measured (`sw_enose/separability.py`, `demo_ceiling.py`, `demo_stage5.py`). It was discarding more than half of it; with graded expansion weights it is now within ~0.02 of an optimal readout |
| Air-to-mucus conversion (ppb in air to uM at the receptor) | Partly | Built and tested (`sw_enose/air.py`, `demo_air.py`). Gas-law and Henry's-law steps are arithmetic; constants for the six demo odorants are **real** (Sander v5.0.0, `data/henry/`), two of the six only as estimates. Equilibrium, mucus composition, uptake and kinetics are all still unmodelled |
| Comparison with any real nose or sensor | No | Not started |

## Status labels (same as the Hygiene Trap pages)

- **ESTABLISHED**: shown by a source we have read and cited.
- **PLAUSIBLE**: follows from known science but has not been shown here.
- **UNTESTED**: nobody we found has tested it.

Current status of the whole project: **PLAUSIBLE as a design tool, UNTESTED as anything about
real breath, water or health.** No output of this code is evidence about a person.

## Rules

1. Every parameter set carries a `provenance` string. `synthetic:...` means invented for testing.
   `measured:<citation>` means taken from a source we have opened. The loader refuses anything else.
2. Every result carries the label `MODELLED` and the provenance of the parameters behind it.
3. Do not quote any number from a synthetic run as a finding.
4. A software model cannot recover information the receptors do not carry. `tests/` includes a test that
   shows two odorants with near-identical affinities stay indistinguishable at any noise level.

## Layout

- `sw_enose/array.py`: the receptor array (Hill-type response), noise, drift, humidity.
- `sw_enose/bio.py`: the biomimetic stages and `BIOLOGY`, which states the evidence for each stage.
- `sw_enose/m2or.py`: human receptor EC50s from M2OR. `sw_enose/singh.py`: our fits of Singh 2019's raw data and a
  held-out mixture check. `sw_enose/mixture.py`: named gas mixtures in, concentration vector out.
- `sw_enose/air.py`: air-to-mucus conversion. ppb in air to uM at the receptor, via the gas law and
  Henry's law, with `AIR_TO_MUCUS` naming everything it leaves out. Invents no constant: it refuses
  any odorant it has no value for. `data/henry/` holds real values for the six demo odorants.
- `sw_enose/panels.py`: the odorant panels. `ACID_SERIES` (C3-C10 straight-chain fatty acids) is the
  reference panel, chosen by coverage; `EVOCATIVE_PANEL` is the old one, kept so earlier demos run.
- `sw_enose/separability.py`: the ceiling. How separable the odorants are in the measured receptor
  space at all, and how much of that separability each stage actually passes on.
- `sw_enose/coverage.py`: which receptor-odorant pairs were actually tested. `support`, `describe`
  and `restrict_to_tested` so a result can state what measurement it rests on.
- `sw_enose/uncertainty.py`: does a conclusion survive what we don't know? Efficacy redrawing from
  the measured spread, stage-parameter sweeps, and a seed-to-seed noise floor to judge them against.
- `sw_enose/reference_models.py`: reimplementations of Raman & Gutierrez-Osuna 2006 (shunting
  normalisation) and Muezzinoglu et al. 2008 (antennal lobe + Kenyon layer), for comparison.
- `sw_enose/lazar_al.py`: NumPy port of the Lazar, Liu & Yeh fly antennal-lobe circuit (BSD-3),
  checked against the original's saved output and run against real Or59b/DM4 recordings.
- `sw_enose/pipeline.py`: a plain (non-biomimetic) baseline pipeline, kept for comparison.
- `sw_enose/data.py`: parameter loading with mandatory provenance.
- `demo.py`: a worked example on synthetic odorants.

## Henry's law constants

Six odorants, transcribed by hand from `henrys-law.org` on 15 Nov 2026 and stored in
`data/henry/sander_v5_subset.csv` with a source note per value. Source: R. Sander, *Compilation of
Henry's law constants (version 5.0.0) for water as solvent*, Atmos. Chem. Phys. **23**, 10901–12440
(2023), doi:10.5194/acp-23-10901-2023 (ACP is CC-BY 4.0). The site states that Sander's 2015
compilation is obsolete; cite 5.0.0. `data/henry/README.md` records which value was chosen for each
compound and why, and what is weak about four of the six.

## Real receptor data

`git clone --depth 1 https://github.com/chemosim-lab/M2OR data/m2or/repo` (Apache-2.0; snapshot 2023-04-28;
Lalis et al., Nucleic Acids Res 2024, PMID 37870437). The data is not stored in this repo.

Limits that matter: the EC50s come from cultured cells with odorants in liquid, not from noses or air; M2OR has
no efficacy values; and most receptor-odorant pairs were never tested. Two odorants can look different only
because different labs tested different receptors, so `demo_m2or.py` compares odorants on receptors tested on both.

## Checks against published work (15 Nov 2026)

- **Mixtures (Singh et al., PNAS 2019).** We refitted their raw dose-response data (osf.io/aj29q; no licence stated, so
  not stored here) and predicted their 21 binary and ternary mixtures from single-odorant fits only. RMSE below 0.1 for
  11 of 18 receptors, median 0.086; at least as good as simple addition for 15 of 18. The paper reports 12 of its 15
  screened receptors. We did not apply their receptor screen or read their appendix, so this is a close check, not an
  exact reproduction. 17 of the 24 human curves do not saturate below the assay ceiling, so efficacy cannot be separated
  from EC50 for them.
- **Normalisation (Olsen et al., Neuron 2010).** Stage 4 now uses their input-gain equations and constants, read from
  the full text. They are fruit-fly numbers; the conversion from receptor activation to firing rate is ours.
- **Breath sulfur gases.** Hydrogen sulfide is not in the M2OR snapshot, methyl mercaptan has single-concentration
  screening hits only, and dimethyl sulfide has no recorded agonist response. The nose refuses to model them.

## Air concentrations needed to reach a measured EC50 (15 Nov 2026)

`demo_air.py` asks what would have to be in the air for a receptor to meet the EC50 the cell assays
measured, using real Henry's law constants (Sander v5.0.0, 2023; see `data/henry/README.md`) at body
temperature. Both ends are now measured and only the chain between them is modelled.

| Odorant | H^cp, mol/(m³·Pa) | Median EC50 | Air needed | Published spread |
|---|---|---|---|---|
| butanoic acid | 11.0 | 100 µM | **90 ppb** | 19–886 ppb |
| isovaleric acid | 13.9 | 100 µM | **71 ppb** | 15–617 ppb |
| cinnamaldehyde | 0.87 | 10 µM | **113 ppb** | 80–160 ppb |
| L-carvone | 0.13 | 18.3 µM | 1.4 ppm | single estimate |
| dimethyl trisulfide | 0.017 | 17.1 µM | 9.9 ppm | 8.0–14.1 ppm |
| octanethiol | 0.0007 | 92.7 µM | 1.3 parts per thousand | 0.7–4.6 ppt |

The compounds split by water solubility, as the physics requires. For the three soluble ones a
measured EC50 is reached at tens to low hundreds of ppb. Fed a breath-like 20/10/2 ppb mixture, peak
modelled receptor activation is 0.69 of maximum, with 10 of 23 receptors above 1% — an upper bound,
since equilibrium partitioning is a ceiling on the liquid concentration.

Whether that leaves a sensitivity gap is **unmeasured**, not resolved. An EC50 is a *half-maximal*
receptor response; a person's detection threshold sits well below it, so landing in "tens of ppb" at
EC50 says nothing yet about whether the chain reaches threshold sensitivity. That needs the human
detection-threshold comparison, which has not been done. (An earlier version of this section said
there was "no sensitivity gap left to explain". That overstated it; see `sonnet-review.md`.)

**Correction to the previous commit.** That commit reported the opposite: ppm-and-above for every
odorant, and 2e-3 activation at breath-like ppb. It had no real constants and swept an invented band
of 1e-4 to 1e0 mol/(m³·Pa). The carboxylic acids actually sit at 10–50, above the top of that band,
so the band was the error. Treat it as a worked example of why rule 3 exists.

For the three poorly soluble compounds the chain still asks for ppm or more. Two of those three
(octanethiol, carvone) have **no measured Henry constant at all**, only estimates, so part of that
may be an artefact of the constant rather than a fact about olfaction. Dimethyl trisulfide's is
measured, which makes it the one genuine discrepancy worth chasing — through odorant-binding
proteins, accumulation away from equilibrium, or amplification after binding.

## The reference panel: C3-C10 fatty acids (15 Nov 2026)

The coverage result below forced a change of panel. The original six odorants were chosen to be
evocative — sour, sulfur, spice, mint — and have **no** joint coverage: of 23 receptors with a
measured agonist among them, none was tested against all six. Searching M2OR for the best-covered
odorant set gives the straight-chain fatty acids C3-C10, where **64 of 64 pairs are measured** and
8 receptors were tested against all eight acids. `demo_acids.py`; `sw_enose/panels.py`.

```
receptor     C3     C4     C5     C6     C7     C8     C9    C10     EC50 µM, - = tested, no response
OR51E1      398     96    110    158    316      -    246      -
OR51E2      341      -      -      -      -      -      -      -
OR51I2        -    316     83    224      -      -      -      -
OR51L1        -      -    363    117      -      -      -      -
OR52B2        -      -      -      -     16    151     83     72
OR52D1        -      -      -      -    260    316      -      -
OR52L1        -      -    891      -      -      -      -      -
OR56A5        -      -      -    427    282     79     36     32
```

The 40 measured non-responses are information, not gaps. The receptors are **chain-length tuned** —
an OR51 group answers short acids, OR52B2 and OR56A5 long ones, and OR56A5 falls monotonically from
C6 to C10 (427 → 32 µM). Those per-receptor tuning curves are measured shapes a model can be asked
to reproduce, and `tests/test_panels.py` pins the OR56A5 curve so a change that breaks it fails.

Why this panel and not another: chain length is a single ordered covariate driving receptor tuning,
water solubility and human detection threshold at once. That turns the outstanding benchmark from
"can it tell two smells apart" into "does it reproduce the order across eight compounds", which is
much harder to pass by luck.

**Two things stop it being an ordered prediction today.** C8-C10 have no measured Henry constant at
all — octanoic's estimates span a factor of 73 and its chosen value does not continue the measured
C3-C7 decline, which is why C8 wants thousands of ppb where its neighbours want hundreds. And only
6 of the 8 acids have a published temperature coefficient, so `demo_acids.py` quotes the series at
298.15 K, where every value is on the same footing, rather than letting the ordering become an
artefact of which compound had a coefficient. Both gaps sit exactly where the long-chain receptors
are tuned.

## How much the answers depend on what we don't know (revised 16 Nov 2026)

`demo_uncertainty.py` changes each unknown and asks whether the answer moves. It uses a hard task
— a 0.07 µM sulfur trace under strong sour, chance 0.50 — because the easy four-smell task sits
at 1.00 and cannot show an effect in either direction.

**How it is measured, and why that was revised.** On the hard task a single random seed scores
anywhere from about 0.4 to 1.0: the seed fixes the expansion wiring, and that wiring is most of
the variance. The first version compared seed-averaged results against the min–max range of three
single seeds. That yardstick was too small with three seeds, and grows without limit as seeds are
added, so its verdicts flipped between runs and between weighting schemes. Every comparison is now
**paired**: each condition runs on the same 12 seeds as its baseline, and the mean per-seed
difference is judged against its own standard error. An effect "matters" above 2 paired SE and
0.02; about 20 comparisons are made, so one result near 2–3 SE is marginal.

**Conclusions are sensitive to efficacy, which is unknown.** M2OR records no efficacy, so `m2or.py`
assumes 1.0. Our fits of Singh et al.'s raw curves give relative efficacy among agonists at the same
receptor of 0.03–1.0, median 0.43 — but that spread is weak evidence. **17 of the 24 underlying curves
do not saturate**, and for those only `A/EC50` is pinned down, so `A` itself is not identifiable and
part of the spread may be fit degeneracy. Dividing by each receptor's largest `A` also puts exactly
one 1.0 in the sample per receptor by construction. The 6 saturated curves alone give a median of
0.22, so the spread is not *purely* artefact, but six curves from one assay cannot show that
efficacy = 1 is wrong. What they can do is supply a plausible range to stress-test against.
Redrawing from it,
12 draws move seed-averaged recognition between 0.48 and 0.90 around a baseline of 0.70. The
spread between draws (SD 0.150) is four times the precision of each draw's average (SE 0.036), and
8 of 12 draws shift recognition beyond 2 paired SE, by −0.22 to +0.20. This is the firm result:
**which plausible efficacies are drawn decides whether a near-threshold discrimination works.**
Even when it works, a sizeable fraction of a code's active cells move (overlap 0.54–0.85 with the
efficacy = 1 code, against 0.09 between different smells), so the nose can report **that** two
smells differ but not **which** code belongs to which.

**Coverage is worse than the headline figure suggests.** Of 23 receptors with a measured agonist
among the six demo odorants, **none** was tested against all six, and only two odorant pairs have two
or more receptors tested against both. The recognition scores in `demo_mixture.py` are therefore
mostly not a measured difference between odorants but a difference in which receptors each odorant
was screened against. `demo_mixture.py` now prints that caveat beside its own results.

**Of the invented stage parameters, only an extreme convergence ratio clearly matters.**
- *Convergence:* one neuron per receptor type costs about 0.10–0.14 (−0.137 ± 0.054 with binary
  weights; −0.096 ± 0.051 with graded, just short of 2 SE). Above about 20 per type nothing is
  detectable. Stage 2 acts only by averaging neuron noise, so the invented ratio is load-bearing
  only if set very low.
- *Adaptation:* at most about 0.06, detectable with graded weights (+0.058 ± 0.022 at
  `adapt_tau` 100; +0.061 ± 0.023 at strength 0) and not with binary weights (nothing beyond
  ±0.04–0.05). Marginal. On a static presentation adaptation can only subtract signal, so this is a
  small cost; a changing-background task is needed to see what adaptation is for.
- *`recover_tau`:* no verdict at all. Recovery acts only once an odour is removed, and this task
  never removes one.

*Superseded:* two earlier versions of this section reported, in turn, that adaptation did not
matter and that it did. Both rested on the three-seed yardstick described above; neither should be
cited.

## The ceiling, and whether we reach it (15 Nov 2026)

Rule 4 says a software model cannot recover information the receptors do not carry. That is a hard
bound, and `demo_ceiling.py` measures both where it is and whether the pipeline reaches it.

**Where it is — and it depends on noise.** Only *identical* activation profiles are inseparable at
any noise level. Similar ones are a distance, and whether that distance can be resolved depends on
how much noise sits on top of it. `separability.noise_tolerance` measures, per pair, the largest
neuron noise at which two-way accuracy stays at or above 0.95:

| pair | cosine | accuracy at noise 0.1 | 0.8 | 1.6 | 3.2 |
|---|---|---|---|---|---|
| C9 vs C10 | 0.926 | 1.00 | 0.96 | 0.81 | 0.66 |
| C8 vs C10 | 0.920 | 1.00 | 0.98 | 0.78 | 0.62 |
| C4 vs C5 | 0.879 | 1.00 | 0.96 | 0.83 | 0.64 |

Similarity does predict *which* pairs fail first: the most similar ones go first. But **every pair
separates at 0.95 or better up to noise 0.8**, about eight times the 0.05–0.1 the demos run at. So
at this model's operating noise the receptor data is **not** the binding limit on the acid panel.
Whether it binds in a real nose depends on real neural noise, and that number is invented here.

(An earlier version said the array "cannot" separate C9 from C10 because their cosine is 0.926. That
conflated similar with identical; `sonnet-review.md` caught it with the measurement above.)

**Whether we reach it — and a bug this found.** Noise enters at the glomerular stage and every later
stage is a deterministic function of it, so the best readout of the glomerular vector bounds any
later readout. The pipeline was scoring **0.458 against a bound of 0.993** — discarding more than
half the separability the receptors provided.

The cause was stage 5. Dasgupta et al. model each expansion cell as sampling about 6 of ~50
projection neurons: a **ratio** of 12%, not an absolute 6. Carried across as a literal `fan_in=6`,
on an 8-glomerulus array every cell reads 75% of the input, so all 2,000 cells see nearly the same
thing and none can be odorant-selective. `bio.default_fan_in` now scales the ratio instead, giving 2
here and reproducing Dasgupta's own 6 at his own array size of 50.

| | sparse-code accuracy | gap to bound |
|---|---|---|
| absolute `fan_in=6` | 0.458 | +0.539 |
| ratio-scaled (now default) | 0.903 | +0.095 |

What remained with binary weights grew with noise (+0.06 at noise 0.05, +0.19 at 0.40). **Graded
expansion weights, adopted later, closed it to about +0.02 at every noise level** (`demo_stage5.py`). Small enough that further architecture work has little left to give at these noise
levels; what limits the nose beyond that is unmeasured, not shown to be the receptor data.

This was invisible to every other check here: the stage's numbers were cited, its tests passed, and
recognition on the easy four-smell panel was a perfect 1.00. Only comparing against the best
possible readout of the same input exposed it. Note also that "ceiling" is the best of the readouts
tried, so it is a **lower bound** — a cleverer classifier would make the real gap larger, never
smaller.

## Comparison with prior systems (15 Nov 2026)

`reports/Biomimetic software nose prior art.md` found no published system with the full sw-enose
chain, but prior art for every stage. None of the closest papers released code, so
`demo_reference.py` reimplements two of them from the papers, behind the same receptor front end:

- **Stage 4:** Raman 2006's shunting inhibition and the Olsen 2010 equation agree within about
  0.01 and both reach the ceiling. The Olsen form gives no advantage here.
- **Stage 5 is now sw-enose's main loss.** Muezzinoglu 2008's Kenyon layer scores 0.97 / 0.94 /
  0.83 at noise 0.1 / 0.4 / 0.8, against sw-enose's 0.91 / 0.75 / 0.55. Ablation puts most of the
  gap on the active fraction: 5% (the fly's figure, from about 50 glomeruli) against 20%. With
  8 glomeruli and fan-in 2 a 5% code is mostly ties. **That did not survive a held-out test**
  (`demo_heldout.py`). On two M2OR panels sharing no odorant with the acids, 20% was worse than
  5% on one, and the winner there (50%) lost on the acids. By a rule fixed before running, the
  default stays at 5%. The jumpy curves come from duplicate cells: 8 glomeruli at fan-in 2 allow
  only 28 distinct wirings. The fix is to make cells differ, not to tune the fraction.

`demo_lazar.py` runs the Lazar antennal-lobe circuit, ported to NumPy, against recorded fly
neurons, the first recorded data anywhere in this repo. The port reproduces the original
notebook's saved output to plot precision (`tests/test_lazar_al.py`). Its receptor stage tracks the
Or59b recordings in shape (r 0.88–0.95), but its projection-neuron stage does not match DM4
(r 0.40–0.61; it peaks near 65 Hz against 150–190 Hz recorded). The data file also stores one PN
recording three times.

**Neither sw-enose's stage 4 nor the Lazar circuit reproduces the DM4 recordings, and they fail in
opposite ways** (revised 16 Nov 2026). The Olsen 2010 equation was fitted on fly ORN→PN data pooled
over 24 receptor types, and this circuit has exactly 24, so it takes the OSN rates in Hz with
nothing invented or fitted.

| DM4, 5 unique recordings | recorded | Olsen (sw-enose stage 4) | Lazar circuit, published |
|---|---|---|---|
| peak, Hz | 148–191 | 139–146 | 57–69 |
| mean firing, Hz | 45.5 | 107.4 | about the recorded level |
| firing with no odour, Hz | 6.9 | 29.2 | — |
| correlation r (mean) | — | 0.57 | 0.47 |
| RMSE, Hz | — | 69.9 | 25.9 |

Olsen gets the peaks and timing roughly right but holds about 2.3× the recorded level for as long
as the odour lasts; the Lazar circuit gets the average level but never reaches the peaks. Both
miss the same thing: the **transient** burst at each concentration step that then subsides, which
a steady-state equation cannot produce. *An earlier version of this paragraph, judging on peaks
and correlation alone, said sw-enose's stage 4 "does better" and "reproduces the firing
magnitude". It does not.* Adaptation fitted on one recording improves correlation on the four
held-out ones only modestly (r +0.01 to +0.09).

**Fitting the Lazar circuit does not help** (`demo_lazar_sweep.py`). The PN's three input gains and
the pre-synaptic feedback strength were each swept from 0.25× to 4× their published values, 625
configurations. With the best configuration chosen on four recordings and scored on the fifth, the
held-out error is 27.1 Hz against 25.9 for the published configuration, r 0.47 for both, and no
configuration's peak gets above about 90 Hz. Within this range the output barely responds to these
parameters.

**Short-term synaptic depression closes most of the gap** (`demo_depression.py`,
`sw_enose/depression.py`; 16 Nov 2026). A literature search (`reports/Drosophila-PN-Transience-Mechanisms.md`,
audited in `sources/AUDIT_Drosophila-PN-Transience-Mechanisms.md`) pointed to depression at the
ORN→PN synapse. Nagel, Hong & Wilson 2015's rate-form depression model, placed between the receptor
input and the Olsen equation:

| DM4, 5 recordings | RMSE, Hz | r | mean, Hz | peak, Hz |
|---|---|---|---|---|
| recorded | — | — | 45.5 | 167 |
| Olsen alone | 69.9 | 0.57 | 107 | 143 |
| + depression, Nagel's measured values, nothing fitted | 27.6 | 0.77 | 25 | 72 |
| + depression, fitted leave-one-recording-out | **17.0** (held-out) | 0.76 | 46.5 | 106 |
| published Lazar circuit | 25.9 | 0.47 | — | ~65 |

The measured values come from other glomeruli and from nerve stimulation, yet with nothing fitted
they cut the error by 60%. They over-correct: Olsen's constants already contain steady-state
depression, so stacking the measured amount double-counts, and the best-fitting rate is about half.
Fitted, held-out error is 17 Hz with the mean level right, below the Lazar circuit and below the
~25 spikes/s Kim et al. 2015 report for their own model (different binning). **Caveats:** the data
fix the depth of depression, not its speed (a valley of (r, τ) pairs score within a few Hz), so
landing on Nagel's τ is not independent confirmation; peaks remain low (106 against 167 Hz); this
is one glomerulus, one odorant, and modelled OSN input. Depression is not yet in the default
pipeline.

## Human detection thresholds (15 Nov 2026)

`demo_thresholds.py` asks whether the model's receptor activation at each acid's measured human
detection threshold is roughly constant across the series, as a fixed detection criterion would
predict. The only source found with analytically verified vapour concentrations (Cometto-Muñiz &
Abraham 2010, PMC2964470) tested just C4, C6 and C8 from the panel; `data/thresholds/` records it
plus a secondary compilation. Nothing measured was found for C7, C9 or C10.

- C4 and C6, whose Henry constants are measured, sit at almost the same activation at threshold
  (0.75% and 0.91% on the 8 fully-tested receptors, 0.08 log units apart). Two points: a weak
  pass, not a result.
- With C8 (estimated Henry constant) the spread is about 0.9–1.1 log units; the secondary set
  scatters by about 1.9.
- Detection sits at roughly 0.1–1% of maximal receptor activation, far below EC50.
- **Not applied:** mucus-vs-water and acid-ionisation corrections. The search for the values they
  need (log P, pKa, nasal mucus pH) was stopped by an automated safeguard; they still need sourcing.

Verdict: underpowered and inconclusive. See `to-do.md`.

**Revisited 16 Nov 2026: the benchmark cannot give a verdict with the inputs that exist.**
- *Ionisation does not matter for this test.* All eight acids have pKa within 4.80–4.90 in every
  source found (unverified, but consistent), so ionisation scales them alike: it moves the spread
  by at most ~0.1 log units at any mucus pH. It shifts only the overall level.
- *The mucus correction matters a great deal.* Scott et al. 2014's corrected air/mucus values for
  hexanoic and octanoic acid widen the spread from 0.85 to 1.40 log units and break the C4/C6
  agreement (0.08 → 0.73). That run mixes sources, so it is not clean either.
- So the earlier "weak pass" for C4 and C6 holds only under one partition treatment.
  Reasonable treatments move the result by 0.5–1.2 log units, as much as the effect being tested.
  Without measured air–mucus partition values for fatty acids, which two searches did not find,
  this benchmark is limited by its inputs, not by the model. Audit:
  `sources/AUDIT_Carboxylic-Acid-Olfactory-Model-Parameters.md`.

## Stage 5 fixed: graded expansion weights (15 Nov 2026)

`demo_stage5.py`. With binary weights and fan-in 2, 8 glomeruli allow only 28 distinct expansion
cells, so 2,000 cells were duplicates of 28. Giving each connection a random strength makes every
cell distinct. Four candidates were judged against a rule fixed before running: replace the default
only if a candidate beats it on every panel, the acids and two held-out panels.

| mean accuracy over noise 0.1/0.4/0.8 | acids | held-out A | held-out B |
|---|---|---|---|
| binary weights (old default) | 0.772 | 0.758 | 0.908 |
| graded lognormal weights (**new default**) | 0.923 | 0.889 | 0.993 |
| ceiling | 0.942 | 0.896 | 0.997 |

Uniform weights did as well (the rule picked lognormal by 0.008, within noise), so the finding is
"graded weights", not the distribution. The gap to the ceiling on the acids is now about 0.02 at
every noise level and every fan-in tested: graded weights also defuse the absolute-fan-in trap.
Against Muezzinoglu et al.'s Kenyon layer the pipeline now scores 0.98 / 0.95 / 0.83 against
their 0.97 / 0.94 / 0.83.

Attribution (part 2 of the demo): the readout rule does not matter (Hebbian counts and sw-enose's
memory agree within about 0.01). Muezzinoglu's advantage came from Bernoulli wiring and more cells,
which give more distinct cells; graded weights alone do better than either.

**Caveat found on the way.** On the separate sulfur-trace task, results swing from about 0.5 to
1.0 with the random seed alone, under every weighting (7 seeds at the faintest trace: binary
0.74, uniform 0.72, lognormal 0.71, no real difference). That exposed a flaw in how
`demo_uncertainty.py` judged its verdicts; it now uses a paired 12-seed analysis (see "How much the
answers depend on what we don't know").

## First test on real gas-sensor data (16 Nov 2026)

`demo_drift.py` runs sw-enose's stages on real metal-oxide sensor recordings: the UCI Gas Sensor
Array Drift dataset (16 sensors, 6 gases, 13,910 measurements in 10 batches over 36 months;
licence and citations in `sw_enose/sensors.py`; fetch with `scripts/fetch_uci_drift.sh`).
`sw_enose/sensors.py` adds a front end that turns recorded features into the non-negative channel
activations the stages expect (ON/OFF split, scaled on training data only), so the same
processing now runs on simulated receptors or real sensors. Batches are held out by time; the
design was fixed before running.

| mean accuracy on held-out batches | A: train batch 1 only | B: train previous batch |
|---|---|---|
| logistic regression (plain) | **0.442** | **0.753** |
| 5-nearest neighbours (plain) | 0.365 | 0.668 |
| nearest centroid (plain) | 0.330 | 0.574 |
| front end + nearest centroid | 0.323 | 0.560 |
| front end + Olsen normalisation + nearest centroid | 0.426 | 0.684 |
| front end + expansion + memory (no Olsen) | 0.409 | 0.690 |
| full sw-enose pipeline | 0.363 | 0.655 |

- **A plain classifier wins.** The full biomimetic pipeline does not beat logistic regression on
  real sensor data, as the bio-inspired e-nose literature led us to expect.
- **Olsen normalisation is the stage that clearly helps:** with the same classifier before and
  after, +0.10 to +0.12 on both protocols. It makes patterns more robust to the gain and
  concentration changes that drift produces.
- **The expansion layer adds nothing on top of it here;** the full pipeline is slightly worse
  than Olsen plus a simple classifier.
- **Drift overwhelms every method:** trained on batch 1, all fall to 0.06–0.25 on batch 8.
- Caveats: fixed, untuned baselines; no SVM (scikit-learn not installed); one random seed for the
  expansion; published results on this dataset use other protocols and are not compared.
- The UCI pages disagree about which class code is which gas; the code→gas order kept here is
  the one the data's concentration maxima support best. Accuracy is unaffected; per-gas
  statements are not made.

## Not done yet

Published human detection thresholds in air for C3-C10, which is the next piece and the one the
acid panel was chosen to enable. A measured Henry constant for C8, C9 and C10, plus temperature
coefficients for C9 and C10. Per-pair efficacy bounds carried through the stages (the spread is
measured, but the model still takes a single efficacy per pair). A presentation with a blank period so adaptation recovery can be
tested at all, and one with a changing background so adaptation can show a benefit rather than only
a cost. A measured convergence ratio, now that it is known to
matter. Nasal uptake and deposition. Sequence-to-receptor steps from genome data (the hard, unsolved
step), and any comparison with real sensor or gas-chromatography recordings.

Run: `python3 demo.py`, `python3 demo_bio.py`, `python3 demo_m2or.py`, `python3 demo_mixture.py`,
`python3 demo_air.py`, `python3 demo_uncertainty.py`, `python3 demo_acids.py` and
`python3 -m pytest -q`.
