# sw-enose: a software-defined electronic nose

A biomimetic, software-defined electronic nose: a virtual receptor array whose signal is processed
the way animal noses process smell. **Everything here is modelled, not measured.**

Why biomimetic: the most capable noses are biological. We copy their architecture, stage by stage,
and say for each stage how well the biology behind it is established.

## How far along it is

| Part | Biomimetic? | Status |
|---|---|---|
| Processing stages (binding, convergence, adaptation, normalisation, sparse code) | Yes, modelled on animal olfaction | Built, tested on synthetic data. Stages 1 and 4 verified in cells or flies; stages 2 and 3 use invented numbers; stage 5 from a modelling paper. See `sources/AUDIT_*.md` |
| Receptors themselves | **Partly**: real human EC50s from M2OR (`sw_enose/m2or.py`, `demo_m2or.py`) | 626 measured agonist pairs across 128 reference receptors. Efficacy assumed; untested pairs (most of them) treated as no response |
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
measured EC50 is reached at tens to low hundreds of ppb — the range noses work in — so **there is no
sensitivity gap left to explain for them**. Fed a breath-like 20/10/2 ppb mixture, peak modelled
receptor activation is 0.69 of maximum, with 10 of 23 receptors above 1%.

**Correction to the previous commit.** That commit reported the opposite: ppm-and-above for every
odorant, and 2e-3 activation at breath-like ppb. It had no real constants and swept an invented band
of 1e-4 to 1e0 mol/(m³·Pa). The carboxylic acids actually sit at 10–50, above the top of that band,
so the band was the error. Treat it as a worked example of why rule 3 exists.

For the three poorly soluble compounds the chain still asks for ppm or more. Two of those three
(octanethiol, carvone) have **no measured Henry constant at all**, only estimates, so part of that
may be an artefact of the constant rather than a fact about olfaction. Dimethyl trisulfide's is
measured, which makes it the one genuine discrepancy worth chasing — through odorant-binding
proteins, accumulation away from equilibrium, or amplification after binding.

## Not done yet

A measured Henry constant for octanethiol and carvone (both currently estimates), temperature
coefficients for four of the six compounds, nasal uptake and deposition, comparison against measured
human detection thresholds in air, sequence-to-receptor steps from genome data (the hard, unsolved
step), and any comparison with real sensor or gas-chromatography recordings.

Run: `python3 demo.py`, `python3 demo_bio.py`, `python3 demo_m2or.py`, `python3 demo_mixture.py`,
`python3 demo_air.py` and `python3 -m pytest -q`.
