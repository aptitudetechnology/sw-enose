# Prompt 2: What makes fly projection-neuron responses transient, and with what parameters

Paste everything below the line into a deep-research tool. Use the strongest model you have.

---

## Role

You are a careful analyst in insect olfactory neurophysiology and computational modelling. The aim is to find measured mechanisms and parameters that can go into a software model, not to promote any model or method. Report evidence against as readily as evidence for.

## Context

We are building an open-source, software-only model of an olfactory system. One stage maps olfactory receptor neuron (ORN) firing to projection neuron (PN) firing in the *Drosophila* antennal lobe using the divisive-normalisation equation of Olsen, Bhandawat & Wilson (Neuron 2010, PMID 20435004), with their published constants. We tested it against public recordings: **acetone concentration staircases (ppm) with the response of an Or59b ORN and, in separate experiments, of a DM4 PN**, distributed with the code for Lazar, Liu & Yeh, "The Functional Logic of Odor Information Processing in the Drosophila Antennal Lobe" (bioRxiv, Feb 2022; github.com/TK-21st/AntennalLobeLLY22).

What we found:

- **The recorded DM4 PN responses are transient.** They are bursts of 150–190 Hz at each concentration step on a modest sustained level, with a mean of about 45 Hz during odour and about 7 Hz without odour.
- **The steady-state Olsen equation gets the peaks and timing roughly right** (peaks about 140 Hz, r about 0.57). But it holds about 2.3× the recorded level for as long as the odour lasts (mean 107 Hz, and 29 Hz without odour).
- **The published Lazar example circuit gets the average level roughly right but never exceeds about 70 Hz.**
- **Sweeping its PN input gains and pre-synaptic feedback strength from 0.25× to 4× did not help** on held-out recordings.

Neither model produces the transient. We want to know which mechanisms produce PN transients and what their measured parameters are, so we can add the right one and test it on held-out recordings. "Not found in these searches" means a gap in the search, not evidence that something doesn't exist.

## Find

1. **Mechanisms.** Which mechanisms are shown experimentally to make *Drosophila* PN responses transient or to emphasise changes in odour concentration? Candidates include:
   - short-term synaptic depression at ORN→PN synapses;
   - presynaptic inhibition of ORN terminals (GABA_A and GABA_B);
   - ORN firing adaptation;
   - intrinsic PN properties;
   - lateral excitation or inhibition from local neurons.

   For each, give the primary studies, the preparation (in vivo or explant; whole-cell, extracellular or imaging), the glomeruli studied, and how large its contribution to PN transience is, quantitatively where reported.
2. **Measured parameters for modelling, with units.** These include:
   - depression magnitude (paired-pulse or steady-state ratio), recovery time constant and release probability at ORN→PN synapses;
   - time course and strength of GABA_B presynaptic inhibition;
   - ORN adaptation time constants;
   - PN membrane time constant and input resistance;
   - any fitted rate-model or dynamical-model parameters.

   Quote the sentence or table each number comes from.
3. **Models that reproduce PN transients.** Published equations, ideally rate models, that map an ORN firing-rate time course to a PN firing-rate time course and reproduce responses to concentration steps or fluctuating stimuli. For each: the equation, its parameters, what data it was fitted to, and how it was validated (held-out stimuli or recordings?).
4. **The Lazar group's work on these recordings.** Aurel A. Lazar and co-workers (including Tingkai Liu, Chung-Heng Yeh, Anmo J. Kim and Yevgeniy B. Slutskiy) have published on Or59b/DM4 responses to concentration waveforms, including whether PNs encode concentration contrast, or the rate or acceleration of change. Identify every such paper, with identifiers. What do they conclude about which mechanism produces PN transients? Which circuit configuration or parameters in the 2022 "Functional Logic" paper (and any later published version) best reproduce the DM4 recordings, and how well (with any quantitative fit)? Who recorded the staircase data, and in which paper was it first published?
5. **Datasets.** Any other public datasets with simultaneous or matched ORN and PN recordings to time-varying odour concentrations, with concentrations measured (for example by photoionisation detector). Give the licence and download location.
6. **The best case against** adding any one mechanism: evidence that the transience in such recordings comes mainly from the stimulus delivery, from ORN dynamics already, or from a combination that cannot be separated.

## Rules

1. Rank sources by strength of evidence: primary experimental studies in *Drosophila* first, then other insects (label the species clearly), then modelling papers, then everything else. **Anything that carries a conclusion needs a PMID, a DOI or, for datasets, a stable URL, and you must have opened it.** Say whether you read the full text or only the abstract.
2. Copy titles, authors, year and journal from the record, never from memory. Quote the sentence or table for each key number, with its units. If you can't, mark it UNVERIFIED and leave it out of your conclusions.
3. State the species, glomerulus, preparation and recording method for every parameter. Values from different glomeruli, species or preparations must not be merged into one number.
4. **Do not stretch.** A result in one glomerulus or one lab is not general. If you found nothing, write "not found in these searches".

## Output

1. **Direct answer** (150 words): which mechanism or mechanisms most plausibly produce PN transients like those described, how strong the evidence is for each (**established**, **plausible**, **untested**), and the strongest argument against.
2. **Mechanism table:** mechanism | evidence of a role in PN transience | species / glomeruli | preparation | effect size | source (identifier; full text or abstract).
3. **Parameter table:** parameter | value | units | species / glomerulus | preparation | how measured | source.
4. **Model table:** model | equation (verbatim) | parameters | fitted to | validated on held-out data? | source.
5. **Lazar group papers on Or59b/DM4:** paper | identifier | what it concludes about mechanism | quantitative fit to recordings | where the staircase data was first published.
6. **Datasets:** dataset | contents | concentrations measured how | licence | URL.
7. **The case against.**
8. **Verification table:** identifier | title | first author | year | full text or abstract.
