# Audit of `reports/Drosophila-PN-Transience-Mechanisms.md` (16 Nov 2026)

Deep-research result for `research_prompts/02_projection_neuron_transients.md`, run on Gemini by
the project owner. I checked the two papers the modelling relies on against their full texts
(PubMed Central) through separate fetches; the rest of the report was read but not re-checked.

## Checked against the source

| Claim in the report | Verdict | What the source says |
|---|---|---|
| Nagel, Hong & Wilson 2015 (PMID 25485755) fit a depression model with f = 0.78, τ = 893 ms | **Correct, with context the report omits** | The values are in the Fig. 1c legend only. They were fitted to EPSCs from 10 Hz *electrical stimulation of the antennal nerve*, PNs in DM6 and VM2 (n = 19), not to odour responses, not in DM4, with no held-out evaluation. |
| The depression fit spans DM6, VM2, VM7 and DL5 | **Partly wrong** | The nerve-stimulation fit is DM6 and VM2 only. Odour recordings pooled DM6, VM2 and VM7; DL5 was used for identification. |
| Nagel's equations were unavailable | **Wrong** | The Methods give a spike-driven form (Eq. 1) and a firing-rate form (Eq. 3: dA/dt = −r·s·A + (1−A)/τ_A, r = 1 − f), which `sw_enose/depression.py` implements. Also a fast component, f = 0.77, τ = 1006 ms. |
| Kim, Lazar & Slutskiy 2015 (PMID 25974217) predicted DM4 output with a 2D LN model | **Correct** | z = f(y, dy/dt), with f a nonparametric surface from 2D ridge regression. Reported RMSE about 25 spikes/s (100 ms bins); one held-out waveform (the step). |
| The staircase data were first published in Kim et al. 2015 | **Plausible, not confirmed** | The paper shows 17 acetone waveforms with Or59b and DM4 responses, recorded in "two separate assays", but does not say whether any appeared in its 2011 predecessor. |
| Olsen 2010's fitted constants (Rmax, σ, m) were not found | **Wrong** | They are in the full text and already in this repo (165, 12, 10.63), read when stage 4 was built. |

## Useful and accepted as leads

- Short-term depression at ORN→PN synapses (Kazama & Wilson 2008; Nagel et al. 2015) is the
  leading central mechanism. GABA_A/B presynaptic inhibition and ORN rate-of-change encoding also
  contribute; the report gives no quantitative split, and neither does Nagel et al.
- The "case against" holds up and is now partly confirmed by our own fit: the OSN and PN
  recordings are unpaired; Olsen's constants come from other glomeruli; and overlapping timescales
  make mechanisms hard to separate. Fitting depression to the DM4 data pins down its depth, not its
  time constant (see `demo_depression.py`).

## Not checked

Kazama & Wilson 2008, Olsen et al. 2010 GABA-antagonist details, Lazar, Liu & Yeh 2023 (PLOS Comput
Biol) equations, and every source the report itself marks UNVERIFIED.
