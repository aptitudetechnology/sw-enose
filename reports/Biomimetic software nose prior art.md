# Prior art covers every stage, not the chain

The general idea behind sw-enose is not new. Software and neuromorphic e-noses built on animal olfactory circuits go back at least to 2006–2008. Raman & Gutierrez-Osuna ran virtual receptors, convergence onto glomeruli and divisive normalisation on real metal-oxide (MOX) sensor data in 2006. Muezzinoglu et al. ran a random Kenyon-cell (KC) expansion on MOX data in 2008. Lazar et al. 2024 have already chained measured receptor affinities with competitive binding through antennal-lobe and mushroom-body stages, in flies.

Every individual stage of sw-enose has published precedent, and so does nearly every pairing of stages. What these searches did not find is the specific chain sw-enose runs:

1. measured human EC50s from M2OR,
2. competitive binding for mixtures,
3. a ppb-in-air front end via an equilibrium Henry's-law step,
4. same-type convergence, adaptation, normalisation in the Olsen 2010 form, and Dasgupta-style top-k expansion,

all applied to an engineered virtual nose. A narrow, carefully worded integration claim is defensible on that basis. A claim to a new architecture, a new use of measured receptor data, or a new fan-in insight is not.

Two of sw-enose's own assumptions sit behind the current literature:

- **Air-water partitioning.** The prior work measured mucus partitioning and replaced the air-water value with a corrected one (Scott et al. 2014).
- **Fan-in.** The bug sw-enose found and fixed is what Litwin-Kumar et al. 2017 predict. Dasgupta et al.'s own supplement already scaled fan-in as a fraction of input dimension.

These searches were centred on PubMed and read many papers only at abstract level. The single most important unread source is the 2025 Dennler et al. review. "Not found" below always means a search gap, not evidence of absence.

## Bio-inspired e-nose pipelines have existed since 2006

A whole line of work takes the insect or mammalian olfactory pathway and runs it on chemical-sensor data. Some of these papers match several sw-enose stages.

**Raman & Gutierrez-Osuna (2006), the closest match on the convergence-and-normalisation side.**
- Temperature-modulated MOX responses become "pseudo-sensors", a virtual receptor population.
- A self-organising map clusters the pseudo-sensors into "a virtual glomerular unit, thereby forming a convergence map".
- A "shunting lateral inhibitory network" of the "shunting type (divisive inhibition)" then compresses concentration.
- Data: real data on three analytes at three concentrations.
- No adaptation, expansion or sparse-code classifier.
- Source: ([Raman & Gutierrez-Osuna 2006, DOI 10.1016/j.snb.2005.11.078, full text](https://psi.engr.tamu.edu/wp-content/uploads/2018/01/raman2006concentration.pdf)).

**Muezzinoglu et al. (NIPS 2008), the KC expansion on sensor data.**
- 16 MOX sensors are treated directly as glomeruli.
- They feed an antennal-lobe rate model with integration and inhibition.
- KC stage: random Bernoulli (p = 0.1) expansion into binary threshold "Kenyon cells", with MB gain control holding sparsity uniform.
- Readout: Hebbian.
- Task: toluene vs acetaldehyde vs their mixture.
- Source: ([Muezzinoglu et al. 2008, full text](https://proceedings.neurips.cc/paper_files/paper/2008/file/8f468c873a32bb0619eaeb2050ba45d1-Paper.pdf)).

**The Schmuker/Nowotny line.**
- Schmuker & Schneider 2007: "virtual receptors" followed by correlation-based lateral inhibition and a classifier ([PMID 18077325, abstract](https://pubmed.ncbi.nlm.nih.gov/18077325/)).
- Schmuker, Pfeil & Nawrot 2014: virtual receptors, lateral inhibition and a winner-take-all (WTA) stage on neuromorphic hardware. Whether its "real-world datasets" were chemical-sensor data is UNVERIFIED ([PMID 24469794, abstract](https://pubmed.ncbi.nlm.nih.gov/24469794/)).
- Diamond et al. 2016: virtual receptors drive receptor-neuron clusters, which drive projection-neuron "glomeruli", then soft WTA. Synaptic depletion gives partial adaptation. 92% accuracy on a 12-sensor FOX e-nose using 4 sensors ([PMID 26891474, publisher page via fetch summary](https://iopscience.iop.org/article/10.1088/1748-3190/11/2/026002)).
- Proske, Wittmann & Galizia 2012 drove an antennal-lobe lateral-inhibition model with measured DoOR responses (22 glomeruli × 137 odours) and framed it explicitly as a model for "artificial olfactory devices" ([PMID 22347182, full text](https://pubmed.ncbi.nlm.nih.gov/22347182/)).

**Hardware lineage.**
- Pearce et al. 2013 put an FPGA model of the insect macroglomerular complex on real SAW sensors ([DOI 10.3389/fnins.2013.00119, full text ~100k chars](https://www.frontiersin.org/articles/10.3389/fnins.2013.00119/full)).
- NEUROCHEM (FP7 216916) planned receptor, bulb and cortex models for a 65,536-element polymer array ([CORDIS](https://cordis.europa.eu/project/id/216916)).
- A review tabulates further spiking and VLSI e-noses. None of those visible to the reader has an MB expansion ([Vanarse et al. 2017, PMC5713038, ~80% read](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713038/)).

**Imam & Cleland 2020 is the best-known neuromorphic olfaction paper, and the most cautionary.**
- It models the mammalian bulb's mitral–granule inhibition on Loihi.
- Input: real MOX data from 72 sensors, one per column. The authors explicitly do not combine duplicate sensor types and leave the glomerular layer unmodelled.
- It has no divisive normalisation and no random expansion ([arXiv 1906.07067, full text of v3](https://arxiv.org/abs/1906.07067)).
- Dennler, van Schaik & Schmuker later showed that its "recognition" of toluene could be reproduced "in the absence of gas", because of sensor drift across batches recorded over nine months. They also showed that a plain Python dictionary solves the task ([arXiv 2309.11555, full text](https://uhra.herts.ac.uk/id/eprint/11579/1/Limitations_in_odour_recognition_and_generalisation_in_a_neuromorphic_olfactory_circuit.pdf)). The published venue of this critique is UNVERIFIED.
- The lesson applies directly to any real-data test sw-enose eventually runs. Subtract baselines, and train and test on separate repetitions.

**What has not been found.** These searches found no application of Dasgupta's fly hash itself to gas-sensor data. The only follow-ups found were general machine-learning ones, read at abstract level only ([AAAI 2022](https://cdn.aaai.org/ojs/20775/20775-13-24788-1-2-20220628.pdf)). They also found no use of the specific Olsen 2010 normalisation equation on e-nose data. Raman's shunting network is related to it but is not the same equation.

## Measured receptor data already drives fly circuits, including through competitive binding

On the "real receptors" side, insect modelling is far ahead of human modelling.

**Olsen, Bhandawat & Wilson 2010**, the source of sw-enose's normalisation equations, already fed measured responses into the circuit. The input was Hallem & Carlson's 24 ORN types × 176 stimuli, passed through divisive normalisation to perceptron readouts that discriminate odours across concentration ([PMID 20435004, full text per one note; record only per another](https://pubmed.ncbi.nlm.nih.gov/20435004/)).

**Luo, Axel & Abbott 2010** is the closest whole-pathway fly model. The chain is 20 Hallem & Carlson receptors → normalisation with lateral suppression → 2,500 KCs, each with about 5 random inputs and global inhibition at ~5% sparseness ([PMID 20498080, full text, PMC2890779](https://pmc.ncbi.nlm.nih.gov/articles/PMC2890779/)). The two notes disagree on its data source. One note lists the Hallem input as UNVERIFIED from the abstract alone; the other read the full text and quotes it. The full-text reading should stand.

**Krishnamurthy et al. 2022** use the Hallem matrix with explicitly *linear* mixing into a disordered expansion ([PMID 36003684, full text](https://pubmed.ncbi.nlm.nih.gov/36003684/)).

**Lazar, Liu, Yeh & Zhou 2024 is the single closest analogue to sw-enose anywhere in these notes.**
- Front end: DoOR responses (110 odorants × 23 ORs), converted to affinities, in an antenna model extended "to account for competitive binding of a mixture of odorant molecules".
- Downstream: cascaded divisive-normalisation stages through antennal lobe to mushroom-body calyx KCs.
- It predicts KC codes for pure odorants and mixtures, and their concentration invariance ([PMID 39479309, full text](https://pubmed.ncbi.nlm.nih.gov/39479309/)).
- Relative to sw-enose it differs in species (fly), data type (DoOR-inferred affinities rather than human EC50s), the absence of an air-phase front end, and purpose (characterising biology, not an engineered nose).
- The notes do not record whether it models convergence, adaptation or an explicit top-k.

**The human side is thinner and split into two camps.**

The first camp uses ML-predicted receptor activity as features for predicting perception:
- Kowalewski & Ray 2020 predicted the activity of 34 human ORs and used it to predict 146 perceptual descriptors. They found OR activity "often superior" to chemical features. There is no circuit and no mixtures ([PMID 32731170, full text](https://pubmed.ncbi.nlm.nih.gov/32731170/)).
- MolOR is the only M2OR-driven receptor-to-perception model found. It trains a *binary* responsive/non-responsive classifier on M2OR and maps the predicted OR profiles to single-molecule percept labels. It has no dose-response, no mixtures and no circuit ([bioRxiv 10.1101/2024.09.16.613334, full text via fetch tool](https://www.biorxiv.org/content/10.1101/2024.09.16.613334v1.full)).

The second camp builds a docking-derived virtual human array: 409 AlphaFold2 ORs, each odorant a docking-score vector, validated on odour similarity ([PMID 40949280, full text](https://pubmed.ncbi.nlm.nih.gov/40949280/)).

**Competitive binding on measured human data stops at the receptor.**
- Singh et al. 2019 predict mixture responses "to within 15%", with no downstream stages ([PMID 31000595, full text](https://pubmed.ncbi.nlm.nih.gov/31000595/)).
- Reddy et al. 2018 and Gronowitz et al. 2021 put competitive binding in front of glomerular codes. Both use *synthetic* receptor parameters: Reddy's are log-normal, with statistics matched to Saito 2009, and Gronowitz's are generated ([PMID 29687778, full text](https://pubmed.ncbi.nlm.nih.gov/29687778/); [PMID 34115747, full text](https://pubmed.ncbi.nlm.nih.gov/34115747/)).
- PubMed listed 23 records citing M2OR and 37 citing Singh 2019. By title, none chains measured human EC50s through competitive binding into a circuit ([M2OR cited-in](https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=37870437); [Singh cited-in](https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=31000595)).

**Counterweights to the value of a competitive-binding front end.**
- The Mainland/Osmo group finds human mixture *perception* "explained by a linear average of their component quality profiles" across 432 mixtures ([PMID 42465471, full text](https://pubmed.ncbi.nlm.nih.gov/42465471/)).
- Kim et al. 2025 find mouse receptor mixture patterns mostly match the "linear sum" of the components ([PMID 41244577, abstract](https://pubmed.ncbi.nlm.nih.gov/41244577/)).
- Fukutani et al. 2023 show that receptor antagonism does change human perception, for β-ionone against methanethiol ([PMID 37220745, abstract](https://pubmed.ncbi.nlm.nih.gov/37220745/)).

Competitive binding therefore has experimental grounds, but "it matters for what a nose reports" remains an open claim rather than a given.

**A difference in approach worth stating.** Most of these models fill gaps by predicting the responses of untested pairs, whether by ML, docking or inferred affinities. sw-enose refuses to predict untested pairs. It treats them as no response by default and offers `restrict_to_tested`. That is a real methodological difference. Note, though, that "untested means zero" is itself an assumption and not a neutral one, because it biases toward sparser receptor codes. These searches did not look for prior work on provenance discipline specifically, so no novelty claim can rest on it.

## The air-to-mucus step is the one sw-enose assumption the literature has already corrected

Nasal uptake has been modelled for sixty years. The line runs from Mozell's chromatographic experiments to the following papers:
- Hahn, Scherer & Mozell 1994: an analytical model running from convective flow through sorption, mucus diffusion and "interaction of odorant molecules with the olfactory receptor cells", compared against psychophysics ([PMID 8207942, abstract](https://pubmed.ncbi.nlm.nih.gov/8207942/)).
- Keyhani, Scherer & Mozell 1997: the 3-D finite-element CFD successor ([PMID 9219668, abstract](https://pubmed.ncbi.nlm.nih.gov/9219668/)).
- Zhao, Yang, Lawson and Craven: patient- and species-specific CFD models built on the same approach.

All of these are kinetic flux models in which mucus enters as a wall boundary condition. None is a pure equilibrium partition step like sw-enose's. Zhao et al. 2006 locate the dominant resistance on the mucus side of the airway wall ([PMID 16354744, abstract](https://pubmed.ncbi.nlm.nih.gov/16354744/)). sw-enose's step is therefore the simplest possible limit. Its equilibrium concentration (air concentration divided by H) is an upper bound at the mucus interface, not necessarily the concentration at the cilia, and it ignores depletion by the mucosa upstream.

**Scott, Sherrill, Jiang & Zhao 2014 is the nearest methodological ancestor of sw-enose's front end, and it contradicts sw-enose's partition choice.** Their chain is air concentration → CFD mucosal concentration → logistic (Hill-equivalent) concentration-response. It fits rat electro-olfactogram (EOG) responses for 66 odorants at r = 0.86. That chain used a corrected air/mucus coefficient, **log β = log β_water − (log P − 1) × 0.524**, calibrated on 12 human odorants from Kurtz et al. 2004. Replacing β_water with β raised the prediction correlation from **r = 0.66 to r = 0.86** ([PMID 24501345, full text ~100k of 107k chars, PMC3913860](https://pmc.ncbi.nlm.nih.gov/articles/PMC3913860/)).

Kurtz et al. 2004 found that mucosal solubility departs from water solubility in an odorant-specific way. Lipophilic odorants are *more* soluble in mucosa than water solubility predicts ([PMID 15574812, abstract](https://pubmed.ncbi.nlm.nih.gov/15574812/)). Hornung et al. 1987 measured the same effect in bullfrog mucosa and attributed the extra sorption to receptor-cell tissue ([PMID 3496142, abstract](https://pubmed.ncbi.nlm.nih.gov/3496142/)).

**How large the bias is for sw-enose's acid panel.** Extrapolating the Scott formula, an air-water step under-predicts mucus concentration by about 0.5 log units per log P unit above 1, roughly 10× at log P 3. That bias grows along the C3–C10 fatty-acid series. It is an inference from the notes, not a published estimate for these compounds. The formula's range and its validity for acids that ionise at mucus pH were not checked.

**Effects Henry's law cannot capture.**
- Rat OBP3 films concentrated odorants about 50,000-fold ([PMID 21536621, abstract](https://pubmed.ncbi.nlm.nih.gov/21536621/)).
- Simulations show porcine OBP lowering the uptake barrier ([PMID 39509459, abstract](https://pubmed.ncbi.nlm.nih.gov/39509459/)).
- How either effect changes the *free* concentration that an EC50 refers to is unsettled.

**Two further points cut in different directions.**
- Mouse EOG+CFD studies in 2017 and 2019 found "no relationship between local odor sorption patterns and EOG response maps". That casts doubt on sorption as a spatial coding mechanism, but not on partitioning as a gate on concentration ([PMID 31649069, abstract](https://pubmed.ncbi.nlm.nih.gov/31649069/)).
- Abraham et al. 2002 split human odour thresholds into "selective transport" (~77%) and receptor-specific effects, and ask whether these are "physically separable" ([PMID 11839607, abstract](https://pubmed.ncbi.nlm.nih.gov/11839607/)). sw-enose's Henry-then-EC50 decomposition is a mechanistic version of that exact question. The Cometto-Muñiz carboxylic-acid threshold series is the obvious human benchmark for the acid panel ([PMID 20931179, record only](https://pubmed.ncbi.nlm.nih.gov/20931179/)).

**What appears unexplored.** No study found chains an uptake model into an array built from per-receptor heterologous EC50s. No software e-nose found models an aqueous mucus layer by Henry's law. The Warwick "artificial olfactory mucosa" is a polymer stationary phase in hardware, used for retention time rather than as a concentration transform ([PMID 17428120, abstract](https://pubmed.ncbi.nlm.nih.gov/17428120/)).

## The fan-in failure was predicted in 2017 and avoided in Dasgupta's own supplement

sw-enose found that copying Dasgupta's absolute fan-in of 6 onto an 8-glomerulus array roughly halved the separability the pipeline passed on. It fixed this by scaling Dasgupta's ~12% ratio, floored at 2 (commit 291e262; `sw_enose/bio.py`). This is a real result for the project, but not a new finding.

**Dasgupta's supplement already treats fan-in as a fraction.** It states that "each KC samples from roughly 10% of the PNs (6 out of 50)". The authors tried 1% and 50%, and found 10% "the most consistent" across datasets. So on SIFT, GloVe and MNIST (d = 128–784) fan-in was a fraction of d, not an absolute 6 ([Dasgupta et al. 2017 supplement, PMID 29123069, full text from hosted copy](https://www.its.caltech.edu/~jkenny/nb250c/papers/Dasgupta-2017-supp.pdf)). sw-enose's `default_fan_in` rediscovers that practice.

**Litwin-Kumar et al. 2017 give the theory.** Optimal fan-in "depends on N, f, and the distribution of synaptic weights". With N = 50 and M = 2,000, the combinatorial criterion gives K* = 7. Above the optimum, dimension falls "because of positive average correlations among the mixed-layer neurons" ([PMID 28215558, full text, PMC5379477](https://pmc.ncbi.nlm.nih.gov/articles/PMC5379477/)). Luo et al. 2010 found the best performance at 5–15 inputs per KC from N = 20, which is 25% connectivity rather than 12% ([PMC2890779](https://pmc.ncbi.nlm.nih.gov/articles/PMC2890779/)).

**Why fan-in 6 fails at N = 8.** This is the notes' inference; no paper simulates N = 8.
- Two random KCs with K = 6 of N = 8 share on average 4.5 of their 6 inputs. That is exactly the correlated regime Litwin-Kumar identify as collapsing dimension.
- The fix does not escape the deeper limit. With binary weights and K = 2 there are only C(8,2) = **28** distinct input sets, so sw-enose's 2,000 expansion cells are at most 28 distinct units, each copied many times. This is arithmetic on sw-enose's own code.
- Babadi & Sompolinsky 2014 warn that "the low dimensionality of the input layer ... limit[s] the benefit of expansion" ([PMID 25155954, abstract](https://pubmed.ncbi.nlm.nih.gov/25155954/)).

So for an 8-receptor array, the expansion stage is closer to a re-encoding than a source of discriminative power. That fits sw-enose's own finding that its best case only approaches the separability bound set at the glomerular stage.

**What sw-enose can claim here.** At most, a documented small-N instance consistent with Litwin-Kumar's theory, plus the engineering warning that porting a fly constant without its ratio fails silently. That is useful to report but is not prior-art-free.

## Closest prior work against the sw-enose chain

Stage key:
- **R**: measured receptor front end
- **Mix**: competitive binding in mixtures
- **Air**: air-to-liquid step
- **C**: same-type convergence onto glomeruli
- **A**: adaptation
- **DN**: divisive normalisation
- **X/k**: random sparse expansion with top-k or other sparsening
- **Read**: readout

"?" means the notes do not say.

| Work (identifier, access) | What it includes | What it lacks relative to sw-enose |
|---|---|---|
| Lazar et al. 2024, Front Physiol (PMID 39479309, full text) | R (DoOR-derived fly affinities), Mix (competitive binding), cascaded DN through AL to KCs; mixtures and concentration invariance | Human data, EC50 dose-response, Air; C, A and top-k not recorded; biology characterisation, not an engineered nose |
| Luo, Axel & Abbott 2010, PNAS (PMID 20498080, full text) | R (Hallem & Carlson, 20 receptors), DN with lateral suppression, X (2,500 KCs, ~5 inputs), global-inhibition sparsening, fan-in sweep | Mix, Air, C, A; no learned KC readout; fly |
| Olsen, Bhandawat & Wilson 2010, Neuron (PMID 20435004, full text / record per note) | R (Hallem, 24 ORN types), DN (the equations sw-enose uses), perceptron discrimination across concentration | Mix, Air, C, A, X/k; fly |
| Krishnamurthy et al. 2022, Front Comput Neurosci (PMID 36003684, full text) | R (Hallem), linear mixing, lateral interactions, disordered expansion to MB-like layer | Competitive binding (explicitly linear), Air, C, A; fly |
| Proske, Wittmann & Galizia 2012, Front Neuroeng (PMID 22347182, full text) | R (DoOR, 22 × 137), AL lateral inhibition, discriminability, framed for "artificial olfactory devices" | Mix, Air, C, A, X/k; fly |
| Raman & Gutierrez-Osuna 2006, Sens Actuators B (DOI 10.1016/j.snb.2005.11.078, full text) | Virtual (pseudo-sensor) receptors, C via SOM convergence map, divisive/shunting DN, real MOX data | Measured biological receptors, Mix, Air, A, X/k, sparse-code readout |
| Muezzinoglu et al. 2008, NIPS (full text) | AL inhibition, random Bernoulli KC expansion with gain-controlled sparsity, Hebbian readout, real MOX incl. a mixture | Virtual receptors (sensors = glomeruli), Mix, Air, C, A; explicit top-k |
| Diamond et al. 2016, Bioinspir Biomim (PMID 26891474, publisher-page summary) | Virtual receptors, RN cluster → PN "glomerulus", partial A (synaptic depletion), soft WTA, plastic readout, real MOX | Measured receptors, Mix, Air, DN, KC expansion |
| Schmuker & Schneider 2007; Schmuker, Pfeil & Nawrot 2014, PNAS (PMIDs 18077325, 24469794, abstracts) | Virtual receptors, lateral inhibition / decorrelation, WTA and supervised learning (2014) | Measured receptors, Mix, Air, C, A, KC expansion |
| Imam & Cleland 2020, Nat Mach Intell (DOI 10.1038/s42256-020-0159-4, arXiv v3 full text) | Mammalian bulb mitral–granule inhibition on Loihi, real MOX, online learning | R, Mix, Air, C (explicitly not modelled), A, DN, X/k; recognition challenged as drift |
| Dasgupta, Stevens & Navlakha 2017, Science (PMID 29123069, full text + supplement) | DN (mean-centring), X (2,000 KCs, ~6 inputs, 10% ratio), top-5% WTA | Any chemical data (SIFT/GloVe/MNIST), R, Mix, Air, C, A |
| Singh et al. 2019, PNAS (PMID 31000595, full text) | Measured human/mouse dose-response, Mix (competitive binding, within 15%) | Everything downstream of the receptor; Air |
| Reddy et al. 2018, eLife (PMID 29687778, full text); Gronowitz et al. 2021, PLoS Comput Biol (PMID 34115747, full text) | Competitive binding into glomerular codes, discrimination/information analysis | Measured receptors (synthetic, statistics matched to Saito or generated), Air, A, X/k |
| MolOR 2024, bioRxiv (DOI 10.1101/2024.09.16.613334, full text via fetch) | M2OR-trained human OR profiles → percept labels | EC50 dose-response (binary labels), Mix, Air, any circuit |
| Kowalewski & Ray 2020, iScience (PMID 32731170, full text) | Predicted activity of 34 human ORs → 146 perceptual descriptors | Measured EC50 array, Mix, Air, any circuit |
| Scott et al. 2014, J Neurosci (PMID 24501345, full text) | Air → mucus (CFD, corrected β) → logistic concentration-response, fit to rat EOG for 66 odorants | Per-receptor EC50s, Mix, any circuit; uses kinetic CFD, not equilibrium |
| Hahn, Scherer & Mozell 1994, J Theor Biol (PMID 8207942, abstract) | Flow → sorption → mucus diffusion → receptor interaction → response | Per-receptor array, Mix, circuit; receptor-interaction form UNVERIFIED |

## A narrow integration claim survives; broader ones do not

**What is not new:**
- A biomimetic or software-defined e-nose.
- Using measured receptor data as a circuit front end.
- Competitive binding feeding a normalising, expanding circuit (Lazar 2024, in flies).
- Air-to-mucus partitioning chained to a concentration-response (Scott 2014).
- The insight that fan-in must scale with input dimension.

**What these searches did not find anywhere:**
1. Measured *human* EC50s from M2OR used as a dose-dependent receptor array. MolOR uses M2OR only as binary labels.
2. Competitive binding for mixtures on that array. Singh 2019 stops at the receptor.
3. An equilibrium air-water Henry's-law conversion turning ppb in air into receptor-side concentration ahead of per-receptor EC50s.
4. That human front end driven through same-type convergence, adaptation, Olsen-form normalisation and Dasgupta-style top-k expansion.
5. Olsen-form normalisation, or the fly hash, applied in any e-nose context.

**A defensible wording**, assuming the claim is made at all:

> To our knowledge, based on PubMed-centred literature searches in November 2026 that did not cover Google Scholar, IEEE Xplore or patents, no published system combines measured human olfactory-receptor EC50s (M2OR) with competitive binding for mixtures, an equilibrium air-to-liquid Henry's-law front end, and a fly-derived processing chain (convergence, adaptation, Olsen-form divisive normalisation, sparse random expansion with top-k) in a software electronic nose. Each component, and several pairings of them, has precedent: notably Lazar et al. 2024 (competitive binding through to Kenyon cells, in *Drosophila*), Scott et al. 2014 (air-to-mucus partitioning into a concentration-response model) and Raman & Gutierrez-Osuna 2006 (virtual receptors, convergence and divisive normalisation on sensor data).

**The claim should stop there.** It is an integration claim about an engineered artifact, not evidence of scientific merit. sw-enose has not yet been compared with any real nose or sensor. Its partition step is less accurate than the corrected β already in use. Its 8-receptor arrays sit in the regime where expansion cannot add dimensions. The project should not claim:
- the fan-in fix as a discovery (cite Dasgupta's supplement and Litwin-Kumar instead);
- provenance discipline as a novelty (it was not searched for);
- that competitive binding improves what the nose reports (the 2025–2026 linearity findings cut against it).

## Gaps that could still overturn the verdict

The searches leaned on PubMed, and many key papers were read at abstract level only. The table ranks the remaining gaps by how likely each is to produce a prior system that matches the full chain.

| Gap | Why it could change the verdict |
|---|---|
| Dennler, True, van Schaik & Schmuker 2025 review (DOI 10.1088/2634-4386/add0dc), abstract only | Most recent critical review; the notes call it "the single most important follow-up"; could list post-2017 KC-expansion or fly-hash e-noses |
| No Google Scholar / Semantic Scholar "cited by" for M2OR, Singh 2019, Olsen 2010 or Dasgupta 2017; no IEEE Xplore, ISOEN or patent search (including Osmo) | Engineering e-nose papers and preprints that combine these are systematically under-counted |
| Kwon et al. 2025, ACS Sens (PMID 40388541), an e-nose LSTM paper citing M2OR, title only | The one known e-nose paper that touches M2OR; how it uses it is unknown |
| Lazar et al. 2024 stage details (convergence, adaptation, top-k) not recorded | If present, the fly analogue matches everything except species, data and the air step |
| McCalmon et al. 2026, Cell Rep / bioRxiv (PMID 41659483); Pellegrino et al. 2025 intensity (PMID 40832259, abstract); Teşileanu et al. 2019 (PMID 30806351, title only) | Any could use measured receptor parameters with binding to predict behaviour or perception (all UNVERIFIED) |
| Huerta/Nowotny/Vergara follow-ups on MB classifiers for MOX datasets; NEUROCHEM outputs (Marco, Gutiérrez-Gálvez 2013/2014); *Handbook of Machine Olfaction* 2003 chapters | Likely home of KC-expansion e-noses beyond Muezzinoglu 2008 (UNVERIFIED) |
| Endo et al. 2020 (PMID 32814018, abstract); Senge arXiv 2610.09114 (listing page only); FlyWire Olfactory SNN model card (search summary only) | Whole-pathway or connectome models whose data sources and stages are UNVERIFIED |
| Systematic mining of Hallem 2006, DoOR and Saito 2009 citers; mouse OR-driven bulb→piriform models | Only a handful of the thousands of citers were checked |
| Hahn 1994 receptor-interaction form; Kurtz 2004 solubility table; Abraham 2002/2012 full texts; acid ionisation at mucus pH | These would not change the novelty verdict, but they decide how wrong sw-enose's air-water step is for the acid panel |
| Litwin-Kumar Equation 3 not evaluated at N = 8; no search for small-N fan-in follow-ups | Could turn the N = 8 inference into a computed optimum, or reveal that someone has already published it |

## Conclusion

The literature changes the question from "is this new?" to "what does the integration buy?". Each stage of sw-enose was built in isolation by groups who also knew its limits. Scott corrected air-water partitioning. Litwin-Kumar and Babadi bounded what expansion can do on few inputs. Dennler showed how drift fakes recognition. Pellegrino and Kim question whether mixture nonlinearity reaches perception. sw-enose's distinctive asset is therefore the human, measured, mixture-aware front end, more than the fly-inspired back end. That back end adds little on 8 receptors.

The strongest next step is to test that front end against human data the notes already identify. The candidates are the Cometto-Muñiz carboxylic-acid thresholds, with the Scott-corrected partition step swapped in. That test would show whether the combination does something the simpler prior pipelines cannot. It would also cover the gap no prior work in these notes has filled: an end-to-end prediction from ppb in air, through measured human receptors, to a human measurement.
