# Virtual noses driven by measured olfactory-receptor response data

Scope: models whose front end is an array of real receptors parameterised from measured receptor-odorant data (EC50s or response matrices), used to predict or discriminate odours or perception. This is checked against sw-enose, which uses human EC50s from M2OR (PMID 37870437) with Singh et al. 2019 competitive binding (PMID 31000595).

Method. PubMed E-utilities (esearch, esummary, efetch), PubMed "cited-in" links for M2OR, Singh 2019 and Kowalewski 2020, and full text from Europe PMC/PMC XML, searched for "Hallem", "DoOR", "Saito", "M2OR", "competitive binding" and "EC50". There were also three web searches and two bioRxiv/arXiv page fetches. Google Scholar "cited by" was not used, so the citation coverage is PubMed's only. That coverage is incomplete, especially for preprints and conference papers.

Key to the access labels: **[FT]** means I checked the full text. **[ABS]** means abstract only. **UNVERIFIED** means I did not confirm it from a source I opened.

## Has M2OR been used as the front end of an odour-processing or perception model?

### Takeaway
I found one M2OR-driven receptor-to-perception model, MolOR (Chithrananda, Amores & Yang, bioRxiv 2024). It does not use M2OR EC50s as a parameterised receptor array. It trains a **binary** responsive/non-responsive molecule-to-OR classifier on M2OR, uses the predicted OR activation profiles as features, and predicts single-molecule percept labels. It has no dose-response, no mixtures and no circuit stage. In these searches I found no work that uses M2OR EC50s with a binding or mixture model to predict perception or discrimination.

### Cited Findings
- **M2OR itself.** Lalis M, Hladiš M, Khalil SA, et al. "M2OR: a database of olfactory receptor–odorant pairs for understanding the molecular mechanisms of olfaction." *Nucleic Acids Res* 2024. [FT]
  - It holds 75,050 bioassay experiments covering 51,395 distinct OR-molecule pairs, 768 molecules and 1,246 OR sequences from 11 species.
  - "M2OR includes either screening concentration or EC50 for all gathered experimental data."
  - [PMID 37870437](https://pubmed.ncbi.nlm.nih.gov/37870437/), DOI 10.1093/nar/gkad886, [PMC10767820](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10767820/)
- **PubMed's 23 citing records.** On 2026-11-15 PubMed listed 23 records citing M2OR.
  - Their titles cover reviews (ectopic ORs, OR structural bioinformatics), other databases (GPCRdb 2025, BitterDB, the Chordata OR database, MORE-Q), OR-ligand docking or ML, an e-nose LSTM paper (Kwon et al., *ACS Sens* 2025, PMID 40388541), olfactory-training odorant selection (PMID 40679176) and a *Drosophila* receptor-response paper (PMID 40062376).
  - Judging by title, none of them is a receptor-array-to-perception model. I did not read most of them past the title.
  - [PubMed cited-in for 37870437](https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=37870437)
- **MolOR.** Chithrananda S, Amores J, Yang KK. "Mapping the combinatorial coding between olfactory receptors and perception with deep learning." bioRxiv, posted 2024-09-16, DOI 10.1101/2024.09.16.613334. [FT, read through a fetch tool; quotes are as the tool returned them]
  - Data: "For molecule-OR data, we use M2OR (14)", and models are trained "using binary cross entropy (BCE) losses". EC50 dose-response screens act only as the "true label" reference in sample-quality weighting.
  - Perception data: the Goodscents-Leffingwell set (5,862 molecules, 152 descriptors).
  - Method: the model "first maps odorant molecules to their respective OR activation profiles and subsequently predicts their odor percepts".
  - Species: human ORs, as the abstract mentions the "human olfactory subgenome". No downstream circuit. Predicts single-molecule percept labels.
  - [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.09.16.613334v1.full)
- **LORAX.** McConachie GD, Duniec E, Guerina F, Younger MA, DePasquale B. "Low rank adaptation of chemical foundation models generates effective odorant representations." bioRxiv 2026 (2025.11.04.686628). [FT]
  - Benchmarks odorant-receptor affinity prediction on Hallem & Carlson 2006, Carey 2010, full M2OR and an "M2OR (EC50)" subset.
  - It compares its learned odour space with a "neural representation" built from receptor responses.
  - It predicts receptor responses only, not perception or discrimination.
  - [PMID 42039378](https://pubmed.ncbi.nlm.nih.gov/42039378/), [PMC13105091](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13105091/)
- **Zanineli et al.** Zanineli P, Lopes EVC, Schleder GR, et al. "Heterogeneous Molecular Signatures of Human Odor Perception." arXiv:2604.09758, April 2026. [ABS]
  - A web search snippet claimed it uses M2OR, but the arXiv abstract page does not mention M2OR.
  - Its models are trained on first-principles molecular descriptors and analyse "odor categories and their associated receptors".
  - Whether it uses M2OR is UNVERIFIED.
  - [arXiv](https://arxiv.org/abs/2604.09758)

### Inferences
- MolOR is the nearest M2OR-based prior art. It differs from sw-enose on three points that matter: binary activation labels rather than EC50 dose-response, no concentration or mixture handling (no competitive binding), and percept-label prediction rather than discrimination by a virtual array.
- An M2OR EC50 array combined with competitive binding for mixtures looks unclaimed in the literature these searches reached. That is not proof of novelty.

### Gaps
- I did not run Google Scholar or Semantic Scholar "cited by" for M2OR. Preprints, conference papers (for example ICLR/NeurIPS workshops) and e-nose engineering papers that cite M2OR are probably under-counted.
- I did not open the full text of the Kwon et al. *ACS Sens* 2025 e-nose paper (PMID 40388541) to see how it uses M2OR.

## Insect analogues: DoOR and Hallem & Carlson 2006 as model front ends

### Takeaway
Feeding measured *Drosophila* receptor response matrices (Hallem & Carlson 2006, or DoOR) into antennal-lobe and mushroom-body models is an established practice, going back at least to 2010. The closest analogue to sw-enose is Lazar et al. 2024. It drives a competitive-binding antenna model from DoOR-derived affinities and feeds that through antennal-lobe and mushroom-body-calyx stages, including for mixtures.

### Cited Findings
- **Data sources:**
  - Hallem EA, Carlson JR. "Coding of odors by a receptor repertoire." *Cell* 2006. [PMID 16615896](https://pubmed.ncbi.nlm.nih.gov/16615896/), DOI 10.1016/j.cell.2006.01.050 (record only).
  - Galizia CG, Münch D, Strauch M, Nissler A. "Integrating heterogeneous odor response data into a common response model: A DoOR to the complete olfactome." *Chem Senses* 2010. [PMID 20530377](https://pubmed.ncbi.nlm.nih.gov/20530377/).
  - Münch D, Galizia CG. "DoOR 2.0—Comprehensive Mapping of Drosophila melanogaster Odorant Responses." *Sci Rep* 2016. [PMID 26912260](https://pubmed.ncbi.nlm.nih.gov/26912260/), DOI 10.1038/srep21841.
- **Lazar AA, Liu T, Yeh CH, Zhou Y.** "Modeling and characterization of pure and odorant mixture processing in the Drosophila mushroom body calyx." *Front Physiol* 2024. [FT]
  - Species and data: *Drosophila*; 110 odorants × 23 ORs from DoOR, converted to affinity vectors by the Lazar & Yeh 2020 algorithm.
  - Front end: the antenna model was extended "to account for competitive binding of a mixture of odorant molecules".
  - Downstream: antenna → antennal lobe → mushroom-body calyx (Kenyon cells), built as cascaded divisive-normalisation processors.
  - Predicts: KC spike codes for pure odorants and mixtures, and their concentration invariance.
  - [PMID 39479309](https://pubmed.ncbi.nlm.nih.gov/39479309/), DOI 10.3389/fphys.2024.1410946
- **Olsen SR, Bhandawat V, Wilson RI.** "Divisive normalization in olfactory population codes." *Neuron* 2010. [FT]
  - Data: "As the input to our model, we used ORN odor responses measured by reference (Hallem and Carlson, 2006), comprising 176 olfactory stimuli and 24 ORN types", which simulated 24 glomeruli.
  - Downstream: projection neurons (PNs) with divisive normalisation by lateral inhibition.
  - Predicts: PN population codes and odour discrimination with perceptron read-outs, including across concentration.
  - [PMID 20435004](https://pubmed.ncbi.nlm.nih.gov/20435004/), DOI 10.1016/j.neuron.2010.04.009
- **Proske JH, Wittmann M, Galizia CG.** "Olfactory sensor processing in neural networks: lessons from modeling the fruit fly antennal lobe." *Front Neuroeng* 2012. [FT]
  - Data: "The input to our model network comes from the DoOR database (Galizia et al., 2010)", a matrix of 22 glomeruli × 137 odours.
  - Downstream: antennal-lobe lateral-inhibition network topologies.
  - Predicts: how well odour representations are separated (discriminability). The paper frames the fly AL explicitly as a model for "artificial olfactory devices".
  - [PMID 22347182](https://pubmed.ncbi.nlm.nih.gov/22347182/), DOI 10.3389/fneng.2012.00002
- **Krishnamurthy K, Hermundstad AM, Mora T, Walczak AM, Balasubramanian V.** "Disorder and the Neural Representation of Complex Odors." *Front Comput Neurosci* 2022. [FT]
  - Data: firing rates of 24 ORN types to 110 odorants (Hallem & Carlson 2006), used as a response matrix R. Mixtures are modelled linearly as y = Rx, explicitly without competitive binding.
  - Downstream: lateral interactions and disordered expansion to a mushroom-body-like layer.
  - Predicts: similarity preservation and odour-valence learning.
  - [PMID 36003684](https://pubmed.ncbi.nlm.nih.gov/36003684/), DOI 10.3389/fncom.2022.917786
- **Giaffar H, Shuvaev S, Rinberg D, Koulakov AA.** "The primacy model and the structure of olfactory space." *PLoS Comput Biol* 2024. [FT]
  - Data: OR-odorant affinities from DoORv2 (156 odours), compared with FlyEM/FAFB OR→KC connectivity.
  - Finding: KCs integrate inputs from high-affinity ("primacy") OR sets.
  - [PMID 39255274](https://pubmed.ncbi.nlm.nih.gov/39255274/), DOI 10.1371/journal.pcbi.1012379
- **Del Castillo JCF, Pashakhanloo F, Murthy VN, Zavatone-Veth JA.** "Convergent motifs of early olfactory processing are recapitulated by layer-wise efficient coding." *PNAS* 2026. [FT]
  - It optimises the receptor matrix W and compares it only qualitatively with Hallem & Carlson ("a qualitative match"). The measured data is not a front end here.
  - [PMID 41875150](https://pubmed.ncbi.nlm.nih.gov/41875150/), DOI 10.1073/pnas.2524661123
- **Kowalewski J, Ray A (2020).** The *Drosophila* section of this paper predicts behavioural valence from "electrophysiologically measured responses" of ORNs. The text cites Hallem & Carlson 2006 and MacWilliam et al. 2018 here. Read-out is machine learning, with no circuit stage. [FT] [PMID 32731170](https://pubmed.ncbi.nlm.nih.gov/32731170/)
- **Inspiration, not measured receptor data.**
  - Schmuker M, Schneider G. "Processing and classification of chemical data inspired by insect olfaction." *PNAS* 2007. Uses "virtual receptors" laid out by a self-organising map on chemical descriptor space. [ABS] [PMID 18077325](https://pubmed.ncbi.nlm.nih.gov/18077325/)
  - Schmuker M, Pfeil T, Nawrot MP. "A neuromorphic network for generic multivariate data classification." *PNAS* 2014. Converts real-valued data to spikes with "virtual receptors". [ABS] [PMID 24469794](https://pubmed.ncbi.nlm.nih.gov/24469794/)
  - Both are olfaction-inspired, but their receptors are not parameterised from measured OR data.
- **Not confirmed as Hallem/DoOR-driven.**
  - Luo SX, Axel R, Abbott LF. "Generating sparse and selective third-order responses in the olfactory system of the fly." *PNAS* 2010. [PMID 20498080](https://pubmed.ncbi.nlm.nih.gov/20498080/). Only the abstract was retrievable and it does not name a data source, so use of Hallem data is UNVERIFIED.
  - Stevens CF. "What the fly's nose tells the fly's brain." *PNAS* 2015. [PMID 26150492](https://pubmed.ncbi.nlm.nih.gov/26150492/). Abstract only; data source UNVERIFIED.
  - Litwin-Kumar A et al. "Optimal Degrees of Synaptic Connectivity." *Neuron* 2017. [PMID 28215558](https://pubmed.ncbi.nlm.nih.gov/28215558/). Full text contains no "Hallem" or "DoOR", so it does not appear to use measured receptor data.
  - Endo K, Tsuchimoto Y, Kazama H. *Neuron* 2020. [PMID 32814018](https://pubmed.ncbi.nlm.nih.gov/32814018/). Full text not available; its abstract describes an "experimentally well-constrained model", data source UNVERIFIED.
- **Community model card, not peer reviewed.** A web search turned up a Hugging Face card, "FlyWire Olfactory SNN". It is described as a connectome-constrained spiking network trained on the DoOR receptor response dataset (about 52 receptors) for odour-identity classification. [Hugging Face](https://huggingface.co/MIRE-org/flywire-olfactory-snn). UNVERIFIED: I did not open the page; the description comes from a search summary.

### Inferences
- For insects, "measured receptor matrix → AL/MB model → discrimination" is well-trodden prior art (Olsen 2010, Proske 2012, Krishnamurthy 2022, Lazar 2024). Lazar 2024 also has competitive binding in front of the circuit. Any novelty claim for sw-enose must therefore rest on human EC50s and the application, not on the architecture.
- Most insect models use single-concentration response matrices. Hallem and DoOR are mostly responses at one dose. They combine mixtures linearly (Krishnamurthy) or through an inferred-affinity binding model (Lazar). They do not fit dose-response curves.

### Gaps
- I did not systematically mine the thousands of papers citing Hallem 2006 or DoOR. There are probably many more circuit models: locust and honeybee spiking models, Nowotny- and Nawrot-lab models, and fly connectome simulations.
- I did not check the Luo 2010 and Stevens 2015 data sources in full text.

## Human/mammal: models using Saito 2009, Mainland 2015 or similar OR screening data to predict perception or discrimination

### Takeaway
The clearest human example is Kowalewski & Ray 2020. Machine learning predicts the activity of 34 human ORs, trained on literature ligand data, and that predicted activity is used to predict 146 perceptual descriptors. It does better than chemical features alone in many cases. I found no human model that drives a dose-response EC50 array through binding and circuit stages to predict perception or discrimination. Mammalian mixture work (Singh 2019, Reddy 2018) predicts receptor or ORN responses, not perception.

### Cited Findings
- **Data sources:**
  - Saito H, Chi Q, Zhuang H, Matsunami H, Mainland JD. "Odor coding by a Mammalian receptor repertoire." *Sci Signal* 2009. [PMID 19261596](https://pubmed.ncbi.nlm.nih.gov/19261596/), DOI 10.1126/scisignal.2000016 (record only).
  - Mainland JD, Li YR, Zhou T, Liu WL, et al. "Human olfactory receptor responses to odorants." *Sci Data* 2015. [PMID 25977809](https://pubmed.ncbi.nlm.nih.gov/25977809/), DOI 10.1038/sdata.2015.2 (record only).
- **Kowalewski J, Ray A.** "Predicting Human Olfactory Perception from Activities of Odorant Receptors." *iScience* 2020. [FT]
  - Species: human. The authors are inventors on related patent applications (conflict-of-interest statement).
  - Data: of 138 ORs with literature ligand data, 34 had enough ligands to train structure-activity models. The literature compiled includes Saito 2009, Mainland 2014 and others.
  - Uses those models to screen about 450,000 compounds.
  - Perception data: Keller & Vosshall 2016 and the 146 ATLAS (Dravnieks) descriptors. "Activity of ORs successfully predicts many of the 146 different perceptual qualities"; "biologically relevant OR activity is often superior" to chemical features.
  - No downstream circuit and no mixtures. The activities are predicted, not measured EC50s.
  - [PMID 32731170](https://pubmed.ncbi.nlm.nih.gov/32731170/), DOI 10.1016/j.isci.2020.101361
- **Kowalewski J, Boyle SM, Arvidson R, Ejercito J, Ray A.** "Machine Learning Based Modelling of Human and Insect Olfaction Screens Millions of compounds to Identify Pleasant Smelling Insect Repellents." bioRxiv 2023, revised 2026. [ABS]
  - Uses chemical-structure ML models for insect valence and the 146 human odour characters, and screens more than 10 million compounds.
  - The abstract describes chemical-structure models, not a receptor-array front end.
  - [PMID 41959424](https://pubmed.ncbi.nlm.nih.gov/41959424/), DOI 10.1101/2023.12.25.573309
- **Haddad R, Weiss T, Khan R, Nadler B, et al. (incl. Sobel N).** "Global features of neural activity in the olfactory system form a parallel code that predicts olfactory behavior and perception." *J Neurosci* 2010. [ABS]
  - Applies dimensionality reduction to neural activity from 12 published studies in seven species ("Four studies reported olfactory receptor activity, seven reported glomerulus activity...").
  - Finds two axes that predict behaviour and perception.
  - It analyses response datasets rather than simulating an array.
  - [PMID 20610736](https://pubmed.ncbi.nlm.nih.gov/20610736/), DOI 10.1523/JNEUROSCI.0398-10.2010
- **Kaneshiro H, Sato M, Tanaka A, et al.** "A Structure-Based Approach for Predicting Odor Similarity of Molecules via Docking Simulations with Human Olfactory Receptors." *ACS Omega* 2025. [FT]
  - Front end: a virtual array of 409 human ORs from AlphaFold2 structures. Each odorant becomes "a 409-dimensional docking score vector".
  - Predicts: odour similarity, validated against ATLAS.
  - This is a virtual human receptor array, but it is **docking-derived, not measured** response data. No circuit and no mixtures.
  - [PMID 40949280](https://pubmed.ncbi.nlm.nih.gov/40949280/), DOI 10.1021/acsomega.5c04324
- **Achebouche R, Tromelin A, Audouze K, et al.** "Application of artificial intelligence to decode the relationships between smell, olfactory receptors and small molecules." *Sci Rep* 2022. [FT]
  - Data: 365 compounds tested on 74 human ORs, from OdorDB, ODORactor, OlfactionDB and the literature.
  - Builds separate compound→odour and ligand→receptor models (GCN etc.) and relates the two.
  - It does not simulate a receptor array to predict perception.
  - [PMID 36335231](https://pubmed.ncbi.nlm.nih.gov/36335231/), [PMC9637086](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9637086/)
- **McCalmon H, Cai G, Tsibouris C, Pashakhanloo F, Chung S, Kapoor V, Murthy VN.** "Sparse input representations explain odor discrimination in complex, concentration-varying mixtures." bioRxiv 2026; updated version in *Cell Rep* 2026, 45(9):117883. [FT preprint]
  - Species: mouse. Method: behavioural discrimination of a target odour in up to 16-component mixtures.
  - Uses "a biophysically grounded model of olfactory bulb glomerular responses" with linear decoding to reproduce behaviour, and cites Singh 2019 and Reddy 2018.
  - The parameterisation I saw (grep for affinity, EC50, receptor model) does not show that it comes from measured per-receptor EC50s. UNVERIFIED.
  - [PMID 41659483](https://pubmed.ncbi.nlm.nih.gov/41659483/)
- **Ravia et al. 2020** ("A measure of smell enables the creation of olfactory metamers", *Nature*) appears in the POM reference list. I did not check it here.

### Inferences
- Human prior art splits into two camps. One uses ML-predicted OR activity profiles as perception features (Kowalewski 2020, MolOR). The other uses virtual receptors built from docking (Kaneshiro 2025). Neither uses measured EC50 dose-response curves as a concentration-dependent array, and neither models mixtures at the receptor level.

### Gaps
- I did not mine the papers citing Saito 2009 or Mainland 2015, which may hold more mouse models. Examples might include bulb models fed with Saito data; Teşileanu et al. *eLife* 2019 (PMID 30806351, title only seen), which may use measured sensitivity matrices but was UNVERIFIED.

## ML receptor-response prediction plus virtual arrays, "digital olfaction" and Osmo/Google's Principal Odor Map

### Takeaway
The Principal Odor Map (Lee et al., *Science* 2023) does not involve receptors. It maps structure straight to perception with a graph neural network trained on perceptual labels. The work that does build virtual receptor arrays from predicted responses comes from other groups: the Ray lab (Boyle 2013 for flies, Kowalewski 2020 for humans), MolOR (Microsoft Research, from M2OR), and Kaneshiro 2025 (docking).

### Cited Findings
- **Lee BK, Mayhew EJ, Sanchez-Lengeling B, Wei JN, et al.** "A principal odor map unifies diverse tasks in olfactory perception." *Science* 2023. [FT, PMC author manuscript]
  - Uses "graph neural networks to generate a principal odor map (POM) that preserves perceptual relationships".
  - Downstream tasks: Dravnieks/DREAM applicability and odour detection thresholds.
  - In full text, "receptor" appears only in passing ("later attempts to incorporate receptor mechanisms") and in references such as Trimmer 2019. Receptors play no part in the model.
  - [PMID 37651511](https://pubmed.ncbi.nlm.nih.gov/37651511/), DOI 10.1126/science.ade4401, [PMC11898014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11898014/)
- **Boyle SM, McInally S, Ray A.** "Expanding the olfactory code by in silico decoding of odor-receptor chemical space." *eLife* 2013. [ABS]
  - A cheminformatics pipeline that predicts *Drosophila* Or-odorant interactions for more than 240,000 compounds, from receptors tested on about 100 odorants.
  - [PMID 24137542](https://pubmed.ncbi.nlm.nih.gov/24137542/), DOI 10.7554/eLife.01120
- **Kowalewski & Ray 2020** and **MolOR 2024**: see the sections above. Both are predicted-receptor-activity → perception pipelines.
- **Pellegrino R, Mayhew EJ, Margolis J, Andres M, Wiltschko AB, Gerkin RC, Mainland JD.** "Odors Smell Like Their Components: A Linear Framework for Predicting Olfactory Mixture Perception." bioRxiv 2026 (Osmo/Mainland authors). [FT]
  - Finds that in a human panel, 432 mixtures of 144 components are "explained by a linear average of their component quality profiles".
  - This is perceptual-level modelling. In full text, Singh 2019 appears only as a reference; there is no receptor front end.
  - [PMID 42465471](https://pubmed.ncbi.nlm.nih.gov/42465471/)
- **Pellegrino R, Samoilova K, Ihara Y, Andres M, Singh V, Gerkin RC, Koulakov A, Mainland JD.** "A quantitative framework for predicting odor intensity across molecule and mixtures." bioRxiv 2025. [ABS]
  - Deep learning models predict the intensity of single molecules and mixtures "from physical properties".
  - Whether a receptor or competitive-binding stage is involved was not stated in the abstract. UNVERIFIED.
  - [PMID 40832259](https://pubmed.ncbi.nlm.nih.gov/40832259/), DOI 10.1101/2025.08.08.668954
- **Kuroda S, Nakaya-Kishi Y, Tatematsu K, Hinuma S.** "Human Olfactory Receptor Sensor for Odor Reconstitution." *Sensors* 2023. [ABS]
  - A review that proposes "human olfactory DX" using physical human-OR sensors (hardware, not a software model).
  - It cites Singh 2019.
  - [PMID 37448013](https://pubmed.ncbi.nlm.nih.gov/37448013/)

### Inferences
- "Digital olfaction" as Osmo and Google have published it (POM, and the Pellegrino 2026 linear mixture model) works at the perceptual level and skips receptors. A receptor-array front end is therefore a genuinely different design from POM, not a re-implementation of it.

### Gaps
- I did not search Osmo's patents or non-PubMed preprints for receptor-based work.
- I did not open the full text of Pellegrino 2025 (intensity), the paper most likely to involve competitive binding, since Singh is a co-author.

## Measured receptor data plus competitive-binding mixture models to predict mixture perception

### Takeaway
I found no published model that takes measured receptor dose-response data, applies competitive binding to mixtures, and predicts *perception*. Singh et al. 2019 stops at receptor responses. Reddy et al. 2018 and Gronowitz et al. 2021 use competitive binding with *synthetic* receptor parameters drawn from distributions, and Reddy's are matched to Saito 2009. Lazar 2024 does this in flies with DoOR-derived affinities, but predicts Kenyon-cell codes, not perception. Fukutani et al. 2023 shows experimentally that receptor antagonism changes human perception, but does not build an array model.

### Cited Findings
- **Singh V, Murphy NR, Balasubramanian V, Mainland JD.** "Competitive binding predicts nonlinear responses of olfactory receptors to complex mixtures." *PNAS* 2019. [FT]
  - Data: dose-response measurements on human and mouse ORs, plus mouse Olfr168 data from Saito 2009 (12 odorants).
  - Predicts receptor responses to mixtures of up to 12 odorants "to within 15% of experimental observations".
  - No perception or circuit stage.
  - [PMID 31000595](https://pubmed.ncbi.nlm.nih.gov/31000595/), DOI 10.1073/pnas.1813230116
- **Reddy G, Zak JD, Vergassola M, Murthy VN.** "Antagonism in olfactory receptor neurons and its implications for the perception of odor mixtures." *eLife* 2018. [FT]
  - Front end: a competitive-binding ORN model, with sensitivities κ⁻¹ drawn from a log-normal "to obtain a six orders of magnitude separation... (Saito et al., 2009)".
  - These are synthetic receptors with statistics matched to the data, not a measured array.
  - Downstream: glomerular code and information transmission. Predicts that antagonism improves mixture coding.
  - [PMID 29687778](https://pubmed.ncbi.nlm.nih.gov/29687778/), DOI 10.7554/eLife.34958
- **Zak JD, Reddy G, Vergassola M, Murthy VN.** "Antagonistic odor interactions in olfactory sensory neurons are widespread in freely breathing mice." *Nat Commun* 2020. [ABS record]
  - Experimental mouse confirmation of OSN antagonism.
  - [PMID 32620767](https://pubmed.ncbi.nlm.nih.gov/32620767/), DOI 10.1038/s41467-020-17124-5
- **Gronowitz ME, Liu A, Qiu Q, Yu CR, Cleland TA.** "A physicochemical model of odor sampling." *PLoS Comput Biol* 2021. [FT]
  - Ligands with receptor-specific affinities and efficacies "compete with one another for dwell time", mapped to glomerular activation.
  - Predicts discrimination sensitivity versus number of receptors and antagonism.
  - Full text has no hits for Hallem, Saito, M2OR or EC50, so it uses **generated** ligand-receptor parameters, not measured ones.
  - [PMID 34115747](https://pubmed.ncbi.nlm.nih.gov/34115747/), DOI 10.1371/journal.pcbi.1009054
- **Fukutani Y, Abe M, Saito H, Eguchi R, Tazawa T, de March CA, Yohda M, Matsunami H.** "Antagonistic interactions between odorants alter human odor perception." *Curr Biol* 2023. [ABS]
  - Identifies human ORs for methanethiol and H₂S and finds antagonists including β-ionone.
  - β-ionone reduced the intensity and unpleasantness of methanethiol in humans, but not when presented to separate nostrils.
  - Experimental link from receptors to perception. No computational array.
  - [PMID 37220745](https://pubmed.ncbi.nlm.nih.gov/37220745/), DOI 10.1016/j.cub.2023.04.072
- **Kim M, Lee J, Park I, et al.** "Stable olfactory receptor activation across odor complexity." *iScience* 2025. [ABS]
  - Mouse phosphoTRAP experiments show mixture receptor patterns mostly match the "linear sum of individual component responses", with some non-linear receptors.
  - Relevant evidence on whether competitive binding is needed in vivo.
  - [PMID 41244577](https://pubmed.ncbi.nlm.nih.gov/41244577/)
- **Lazar et al. 2024**: DoOR-derived affinities with competitive binding for fly mixtures, through to KCs. See the insect section. [PMID 39479309](https://pubmed.ncbi.nlm.nih.gov/39479309/)
- **Singh V, Tchernookov M, Balasubramanian V.** "What the odor is not: Estimation by elimination." *Phys Rev E* 2021. Seen in the Singh 2019 cited-in list by title only. It is a theory paper and its data use was not checked (UNVERIFIED). [PMID 34525542](https://pubmed.ncbi.nlm.nih.gov/34525542/)
- PubMed listed 37 papers citing Singh 2019 on 2026-11-15. By title, the only ones that combine receptor-level competitive binding with downstream modelling are those reviewed above: Reddy 2018, Gronowitz 2021, Krishnamurthy 2022, Lazar 2024 and McCalmon 2026. [PubMed cited-in for 31000595](https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid=31000595)

### Inferences
- The components of sw-enose each have published precedent: a measured receptor array (insects since 2010), competitive binding on measured dose-response data (Singh 2019, receptor level only), and predicted human OR activity → perception (Kowalewski 2020, MolOR 2024).
- The specific combination is human measured EC50s from M2OR, competitive binding for mixtures, and an array used for discrimination. I did not find it in these searches. The fly analogue (Lazar 2024) is the closest.
- There is a counterweight to the premise that receptor-level non-linearity matters for perception. The Mainland/Osmo group's 2026 preprint finds that mixture *perception* is close to linear in component quality profiles, and Kim 2025 finds receptor patterns are mostly linear. These are relevant when claiming value for a competitive-binding front end.

### Gaps
- I did not read the full text of Pellegrino 2025 (intensity, which has Singh as co-author), McCalmon 2026 / *Cell Rep* 2026 (how the bulb model is parameterised) or Teşileanu 2019. Any of them could turn out to use measured receptor parameters with binding to predict perception or behaviour.
- I did not search Google Scholar, Semantic Scholar or patents, and I did not mine the citations of Hallem 2006 or Saito 2009 at scale.
