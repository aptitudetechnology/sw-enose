# Bio-inspired / neuromorphic signal processing for e-noses and gas-sensor arrays: prior art

Scope: prior work that processes chemical-sensor or odour signals with stages modelled on animal olfaction. The comparison is against the sw-enose chain: (R) virtual receptor array, (C) convergence onto glomeruli, (A) adaptation, (DN) divisive normalisation (Olsen, Bhandawat & Wilson 2010), (KC) sparse random expansion with top-k (Dasgupta et al. 2017), (S) sparse-code recognition.

How much of each source I read is stated for every entry: "full text" means I read the PDF text, "abstract" means abstract or metadata only, and "secondary" means I saw it only through a review's description. Search-engine summaries were used only to find sources. Anything not opened is marked UNVERIFIED.

Summary matrix (built only from the entries below):

| Work | R | C | A | DN | KC expansion | S / readout | Input |
|---|---|---|---|---|---|---|---|
| Imam & Cleland 2020 (Loihi) | no (1 sensor = 1 column) | no | no | no | no (GC lateral inhibition, STDP) | spike-timing attractor, Jaccard | real MOX, Vergara wind-tunnel dataset (72 sensors, 10 gases) |
| Raman & Gutierrez-Osuna 2006 | yes (pseudo-sensors from temperature modulation) | yes (SOM convergence map) | no | yes (shunting / divisive lateral inhibition, PG cells) | no | separability measures / PCA | real temperature-modulated MOX, 3 analytes x 3 concentrations |
| Muezzinoglu et al. NIPS 2008 | no (each of the 16 sensors is treated as a glomerulus) | no | no | no (AL integration + inhibition rate model) | yes (random Bernoulli expansion, threshold neurons, MB gain control) | Hebbian KC-to-output | real MOX, 16 sensors, toluene/acetaldehyde/mixtures |
| Diamond et al. 2016 | yes ("virtual receptors", neural gas) | RN cluster -> PN cluster "glomerulus" | partly (synaptic depletion) | no (soft WTA lateral inhibition) | no (abstracted "association neurons") | plastic PN->AN, WTA | real MOX, FOX e-nose (12 sensors, 4 used), 20 chemicals |
| Schmuker, Pfeil & Nawrot 2014 | yes (virtual receptors) | no | no | no (lateral inhibition) | no | WTA, supervised | "real-world datasets" (type not confirmed from abstract) |
| Pearce et al. 2013 (FPGA) | 2 ORNs | 2 glomeruli x 15 PNs | no | LN inhibition (WTA / winnerless) | no | none (dynamics only) | real SAW polymer sensors plus synthetic pulses |
| Koickal et al. 2006/07 (aVLSI) [secondary] | ORN spiking models | ? | adaptive baseline | lateral inhibition | no | on-chip STDP | 70-element polymer array |
| NEUROCHEM (FP7 216916) | 65,536-element polymer array mimicking the ORN layer | models of OB/cortex | ? | ? | n/a (mammalian) | ? | real conducting polymer |

---

## 1. What did Imam & Cleland (Nature Machine Intelligence 2020) build?

### Takeaway
They built a spiking model of the mammalian olfactory-bulb external plexiform layer (EPL) on Intel Loihi: 72 mitral-cell columns, one per sensor, with granule-cell lateral inhibition learned by STDP, gamma-cycle spike-timing codes and adult neurogenesis. Its input was single-timepoint snapshots of real MOX data (the Vergara et al. wind-tunnel dataset). It does not model glomerular convergence, divisive normalisation, adaptation or a sparse random expansion. A 2024 Matters Arising paper (Dennler, van Schaik & Schmuker) showed that the reported recognition can come from sensor drift. That paper also found the model fails to generalise across separate repetitions of the same gas.

### Cited Findings
- Record: N. Imam & T. A. Cleland, "Rapid online learning and robust recall in a neuromorphic olfactory circuit", *Nature Machine Intelligence* 2(3):181–191 (2020), DOI 10.1038/s42256-020-0159-4; arXiv 1906.07067 (v1 17 Jun 2019, v3 23 Jan 2020). I read the full text of the arXiv v3 PDF. The Nature page redirected to a login, so I did not see the published version. — [arXiv](https://arxiv.org/abs/1906.07067); DOI from the reference list of [Dennler et al.](https://arxiv.org/pdf/2309.11555)
- Architecture: "The structure of the model network ... was based on the circuitry and computational properties of the mammalian MOB, optimized for efficient implementation as a spiking network on the Loihi chip". The listed principles are the learning-dependent lateral inhibitory network of the EPL, gamma-discretised spike timing, MC→GC excitation regardless of distance, GC→MC inhibition expressed as spike delays, permanent GC differentiation with replacement by adult neurogenesis, and neuromodulation. The paper also assumes that "these fine-timescale EPL computations do not meaningfully influence the coarse-timescale computations of the glomerular layer". In other words, the glomerular layer is explicitly not modelled. — [arXiv full text](https://arxiv.org/abs/1906.07067)
- Input: "the 'Gas sensor arrays in open sampling settings' dataset published by Vergara and colleagues ... 72 metal-oxide based chemical sensors distributed across a wind tunnel". They used sensor location L4. Ten odorants were used, with one randomly chosen 180 s plume per odorant. — [arXiv full text](https://arxiv.org/abs/1906.07067)
- Preprocessing and front end: each sensor was "discretized ... into 16 levels of activation" (one level per time bin of the gamma cycle). The 72-dimensional vector "then was sparsened by setting the smallest 50% of the values to zero", and training used the single 90 s timepoint. Each column "received afferent excitation proportional to the activation level of one sensor". The 72 columns were treated "as independent inputs, without crafting the algorithm to combine the responses of duplicate sensor types". So there is no receptor-to-glomerulus convergence. The fixed 50% sparsification is a percentile threshold on the input, not a random expansion. — [arXiv full text](https://arxiv.org/abs/1906.07067)
- Testing: impulse noise replaced a fraction P of the sensor inputs with random values. A separate plume-variance test drew samples from 30–180 s. The paper compares against PCA and a deep autoencoder. — [arXiv full text](https://arxiv.org/abs/1906.07067)
- Critique: N. Dennler, A. van Schaik, M. Schmuker, "Limitations in odour recognition and generalisation in a neuromorphic olfactory circuit", arXiv 2309.11555, Matters Arising "Arising from Imam & Cleland" (full text read from the Hertfordshire repository PDF). Its findings:
  - The data were recorded in gas-specific batches over nine months, and no baseline subtraction was applied.
  - The "same level of 'recognition' of Toluene can be obtained in the absence of gas, using samples obtained at t = 15s".
  - With separate repetitions for training and testing, "gas identity could not be recognised in occluded samples". With baseline subtraction added, recognition "failed even for samples without any noise occlusion".
  - A plain hash table (a Python dictionary) solves the paper's Fig. 4 task.
  — [UH repository PDF](https://uhra.herts.ac.uk/id/eprint/11579/1/Limitations_in_odour_recognition_and_generalisation_in_a_neuromorphic_olfactory_circuit.pdf); [arXiv](https://arxiv.org/pdf/2309.11555)
- The published venue of the critique ("Nature Machine Intelligence 6(12):1451–1453, 2024") comes only from a search-engine summary. I did not open the publisher record, so this is UNVERIFIED. — [UH record](https://uhra.herts.ac.uk/id/eprint/11579/)

### Inferences
- Of the sw-enose stages, Imam & Cleland share only the general "bio-inspired spiking OB" framing and a recognition step. Their circuit models a different stage: mammalian EPL mitral–granule inhibition, not insect AL normalisation or MB expansion. Any novelty claim must still cite it as the best-known neuromorphic olfaction paper on real MOX data.
- The critique is a direct warning for sw-enose's own evaluation. A benchmark on MOX data without baseline subtraction and with non-randomised acquisition can show "recognition" that is really drift. Any test with real data should also train and test on separate repetitions.

### Gaps
- I did not read the supplementary material or Methods sections beyond the arXiv text, or any reply by Imam & Cleland to the Matters Arising, if one exists.

---

## 2. Tim C. Pearce and colleagues: bio-inspired machine olfaction

### Takeaway
Across the sources I opened, Pearce's verified work on processing real sensor data is a 2013 FPGA spiking model of the insect macroglomerular complex (2 ORN types, 2 glomeruli, 30 PNs, 30 LNs), driven by real surface-acoustic-wave polymer sensors and by synthetic pulses. A review also credits his group with ORN→glomerulus convergence-for-hyperacuity theory. NEUROCHEM (FP7 216916, 2008–2011) was coordinated by the Universitat de Barcelona. According to the CORDIS record, its aim was models of the receptor layer, olfactory bulb and cortex, interfaced with a large biomimetic polymer sensor array. None of these, as far as I read, implements divisive normalisation or KC-style sparse random expansion.

### Cited Findings
- T. C. Pearce, S. Karout, Z. Rácz, A. Capurro, J. W. Gardner, M. Cole, "Rapid processing of chemosensor transients in a neuromorphic implementation of the insect macroglomerular complex", *Frontiers in Neuroscience* 7:119 (2013), DOI 10.3389/fnins.2013.00119 (I read the first ~100k characters of the full text).
  - Hardware: a spiking LIF model on a Xilinx Virtex-5 FPGA.
  - Network: 2 ORN types → 2 glomeruli × 15 PNs, with 30 LNs whose probabilistic inhibition gives WTA or winnerless-competition dynamics, and STDP on ORN–LN and LN–LN synapses in one experiment.
  - Input: real SAW resonator chemosensors (PCL and PVK coatings) exposed to 3-methylbutan-1-ol and ethyl acetate in five ratios, plus synthetic square pulses for the FPGA tests.
  — [Frontiers](https://www.frontiersin.org/articles/10.3389/fnins.2013.00119/full)
- Raman & Gutierrez-Osuna (2006) describe earlier Pearce et al. work: "Pearce et al. [9] investigated the issue of concentration hyperacuity by means of massive convergence of ORNs onto GL. Modeling spike trains of individual ORNs as Poisson processes ... an enhancement in sensitivity by a factor √n". This is a model; the review says nothing here about e-nose data. — [Raman & Gutierrez-Osuna 2006 full text](https://psi.engr.tamu.edu/wp-content/uploads/2018/01/raman2006concentration.pdf)
- Raman, Stopfer & Semancik (2011) also describe Pearce et al.'s redundant-copy integration (√n gain) using chemically sensitive microbeads. This is secondary, from the review. — [ACS Chem Neurosci review, PMC3212736](https://pmc.ncbi.nlm.nih.gov/articles/PMC3212736)
- NEUROCHEM, "Biologically inspired computation for chemical sensing", grant 216916, FP7-ICT (Bio-ICT convergence), 1 Jan 2008 – 30 Jun 2011.
  - Coordinator: Universitat de Barcelona. Partners include UPC, UPF, CNRS, INRA, CNR, KTH, University of Leicester and University of Manchester.
  - Objective: computational models of the olfactory receptor layer, olfactory bulb and cortex, abstracted into algorithms. Planned outputs were a demonstrator with a large-scale sensor array mimicking the ORN layer, a full-scale parallel simulation of rat OB and cortex, and an embedded system.
  - The fact sheet reports no results.
  — [CORDIS 216916](https://cordis.europa.eu/project/id/216916)
- The NEUROCHEM array was 65,536 conducting-polymer sensors made from 31 materials (Bernabei et al. 2012, as described by Vanarse et al. 2017; secondary). — [Vanarse et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713038/)
- Koickal et al. (2006/2007), as summarised by Vanarse et al. (2017), is an analogue VLSI chip (AMS 0.6 µm). It includes ORN models producing spikes, projection neurons, lateral inhibition, on-chip STDP and adaptive baseline normalisation, and was built for a 70-element carbon-black polymer array. This is secondary. Whether Pearce is a co-author is UNVERIFIED: the Frontiers 2013 paper cites Koickal et al. but I did not see the author list. — [Vanarse et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713038/)
- A BICS 2004 paper from Pearce's group appeared only in a search snippet: an "olfactory bulb model, a reduced 70 element broadly-tuned chemosensor array (25 different chem-sensor tunings), and details of their silicon implementation". UNVERIFIED (not opened). — [BICS 2004 PDF](https://www.cs.stir.ac.uk/~lss/BICS2004/CD/papers/1099.pdf)
- Guerrero-Rivera & Pearce (2007), an olfactory-bulb attractor model on a spiking FPGA, is known only secondarily via Vanarse et al. The input was not stated in that review. — [Vanarse et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713038/)

### Inferences
- The Pearce and NEUROCHEM line works on mammalian or insect glomerular and OB dynamics, on hardware and large polymer arrays. Neither the 2013 paper nor the CORDIS text describes divisive normalisation (Olsen 2010 form) or a random sparse KC expansion.

### Gaps
- *Handbook of Machine Olfaction* (Pearce, Schiffman, Nagle, Gardner (eds.), Wiley-VCH 2003): I did not open its table of contents or chapters. Its chapter-level content on biological or neuromorphic processing is UNVERIFIED.
- NEUROCHEM outputs: Marco, Gutiérrez-Gálvez et al., SPIE 8763 (2013) "Biologically inspired large scale chemical sensor arrays and embedded data processing" and Microsystem Technologies (2014) appeared only in search results and were not opened. UNVERIFIED.

---

## 3. Fly hashing, mushroom-body/Kenyon-cell expansion and divisive normalisation applied to e-nose data

### Takeaway
- KC-style sparse random expansion on real MOX data: yes, at least since Muezzinoglu, Vergara, Huerta, Nowotny et al. (NIPS 2008). They used a random Bernoulli (p = 0.1) expansion into binary threshold "Kenyon cells" with MB gain control and Hebbian readout, on 16 MOX sensors. That is a fixed threshold plus gain control, not the explicit top-k / winner-take-all of Dasgupta 2017.
- Divisive (shunting) normalisation in glomeruli, after receptor-to-glomerulus convergence, on real MOX data: yes, in Raman & Gutierrez-Osuna (2006).
- The Dasgupta "fly hash" algorithm as such: I found no application to gas-sensor or e-nose data in these searches. That is a search gap, not proof of absence.

### Cited Findings
- B. Raman & R. Gutierrez-Osuna, "Concentration normalization with a model of gain control in the olfactory bulb", *Sensors and Actuators B* 116 (2006) 36–42, DOI 10.1016/j.snb.2005.11.078 (full text read).
  - Pipeline: temperature-modulated MOX sensors, with the response at each temperature set point treated as a "pseudo-sensor" (a virtual receptor population). The pseudo-sensors are clustered by selectivity on a SOM ("a virtual glomerular unit, thereby forming a convergence map"; Fig. 4 shows 3000 pseudo-sensors converging onto a 20×20 SOM).
  - Normalisation: then "a shunting lateral inhibitory network, modeled after the role of periglomerular cells ... is used to compress concentration information". The paper explicitly calls these lateral interactions "of a shunting type (divisive inhibition)".
  - Data: real experimental data, acetone, isopropyl alcohol and ammonia at three concentrations.
  - It has no adaptation stage, no sparse expansion and no sparse-code classifier.
  — [PDF](https://psi.engr.tamu.edu/wp-content/uploads/2018/01/raman2006concentration.pdf)
- M. K. Muezzinoglu, A. Vergara, R. Huerta, T. Nowotny, N. Rulkov, H. Abarbanel, A. Selverston, M. Rabinovich, "Artificial Olfactory Brain for Mixture Identification", NIPS 21 (2008), pp. 1121–1128 (full text read).
  - Input: "16 parallel metal-oxide gas sensors"; "the 16 artificial gas sensors actually correspond to glomeruli (rather than individual ORNs)". So there are no virtual receptors and no convergence.
  - AL stage: a rate model with "integration and inhibition".
  - MB stage: "a nonlinear expansion from the AL representation ... ii) a gain control in the MB to achieve a uniform level of sparse activity [in] the KCs ... iii) ... Hebbian learning rule". KC units are binary McCulloch-Pitts neurons with a Heaviside threshold. The connectivity is "determined randomly by an independent Bernoulli process ... pc = 0.1".
  - Task: pure toluene vs pure acetaldehyde vs mixture.
  — [NeurIPS PDF](https://proceedings.neurips.cc/paper_files/paper/2008/file/8f468c873a32bb0619eaeb2050ba45d1-Paper.pdf)
- A. Diamond, M. Schmuker, A. Z. Berna, S. Trowell, T. Nowotny, "Classifying continuous, real-time e-nose sensor data using a bio-inspired spiking network modelled on the insect olfactory system", *Bioinspiration & Biomimetics* 11(2):026002 (2016), DOI 10.1088/1748-3190/11/2/026002 (publisher page read via fetch summary).
  - Receptor stage: "virtual receptors" (radial-basis encoding, neural gas) drive Poisson RN clusters, which drive PN-cluster "glomeruli".
  - AL stage: "mutual inhibition in a soft winner-take-all (WTA) configuration".
  - MB stage: no KC expansion; the MB is abstracted into one association-neuron cluster per class.
  - Data: a FOX e-nose with 12 MOX sensors, of which 4 were used, and 20 chemicals. Accuracy was about 92% with continuous input; an SVM reached 99%. The network ran on GPU-accelerated SNN software.
  — [IOP](https://iopscience.iop.org/article/10.1088/1748-3190/11/2/026002)
- Raman, Stopfer & Semancik, "Mimicking Biological Design and Computing Principles in Artificial Olfaction", *ACS Chemical Neuroscience* 2(9):487–499 (2011), DOI 10.1021/cn200027r. This is a review; I read about 80% of it. It lists as core principles "Divisive pattern normalization circuits at the input of the olfactory bulb/antennal lobe" and "Neural circuits at the output of the olfactory bulb/antennal lobe decorrelate odor response patterns". — [PMC3212736](https://pmc.ncbi.nlm.nih.gov/articles/PMC3212736)
- Dasgupta, Stevens & Navlakha's fly LSH: 50 PNs → 2000 KCs, each KC sampling about 6 PNs, with about 5% of KCs active. Searches for applications to e-noses found only general-ML follow-ups (Sinha et al., fly Bloom filter / FlyNN; federated FlyNN, AAAI 2022), none on chemical-sensor data. — [Dasgupta et al. PDF](https://courses.csail.mit.edu/6.852/brains/papers/DasguptaStevensNavlakha.pdf); [Sinha (NSF PAR)](https://par.nsf.gov/servlets/purl/10251020); [AAAI 2022](https://cdn.aaai.org/ojs/20775/20775-13-24788-1-2-20220628.pdf) (abstract-level only)

### Inferences
- Several individual sw-enose stages have direct precedents on real MOX data:
  - virtual or pseudo-receptor arrays with convergence onto glomeruli, then divisive / shunting normalisation (Raman & Gutierrez-Osuna 2006);
  - random sparse KC expansion with sparsity control (Muezzinoglu et al. 2008);
  - virtual receptors with lateral inhibition (Schmuker et al. 2014; Diamond et al. 2016).
- In what I read, no single prior work chains all of R → C → A → DN (Olsen form) → KC with top-k → sparse-code recognition. A novelty claim would have to rest on the full chain and its specific forms: Olsen-type divisive normalisation, explicit top-k, and a receptor array that is simulated rather than physical. It cannot rest on any one stage.

### Gaps
- I found no application of Olsen-2010-form divisive normalisation (the specific equation) to e-nose data. The Raman model is a shunting lateral-inhibition network, related to Olsen-2010 normalisation but not the same equation.
- I did not search the Huerta/Nowotny follow-ups on MB-inspired classifiers for the UCSD/Vergara datasets (e.g. inhibitory SVM, drift work). They are likely relevant but UNVERIFIED.

---

## 4. Other bio-inspired e-nose processing: SNN e-noses, neuromorphic chips, antennal-lobe models

### Takeaway
There is a substantial body of spiking and neuromorphic e-nose work: analogue VLSI, CMOS spike-latency chips, FPGA, the Spikey chip, GPU SNNs, SpiNNaker and Loihi. Most of it implements receptor encoding plus lateral inhibition or WTA, and much of it runs on real MOX or polymer arrays.

### Cited Findings
- M. Schmuker, T. Pfeil, M. P. Nawrot, "A neuromorphic network for generic multivariate data classification", *PNAS* (published 27 Jan 2014), DOI 10.1073/pnas.1303053111, PMID 24469794 (abstract read).
  - Pipeline: "real-valued multivariate data are converted into spike trains using 'virtual receptors' ... processed by lateral inhibition and drives a winner-take-all circuit that supports supervised learning". The VRs run in software and the later stages on accelerated neuromorphic hardware (the Spikey chip, per Vanarse et al.). Performance was "on par with a naïve Bayes classifier".
  - The abstract does not say whether the "real-world datasets" were chemical-sensor data. UNVERIFIED.
  — [Crossref/Europe PMC record](https://doi.org/10.1073/pnas.1303053111)
- Vanarse et al. (2017) Table 1 lists further hardware and SNN e-noses on real sensors (all secondary):
  - Ng, Boussaid & Bermak 2011: CMOS spike-latency coding, 4×4 tin-oxide array.
  - Yamani et al. 2012: sensor groups treated as glomeruli, latency coding.
  - Huang & Rabaey 2017: 65 nm CMOS spike front end for 6 MOX sensors.
  - Hassan & Bermak 2016: rank-order codes.
  - Kasap & Schmuker 2013: iSTDP lateral inhibition.
  - Persaud & Dodd 1982: the original three-level receptor/glomerular/cortex analogue.
  The reviewer's table records no Kenyon-cell / MB expansion in the works visible to me.
  — [Vanarse et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713038/)
- SpiNNaker: a GitHub repository runs an odour classifier on a SpiNNaker spiNN-3 board (3 sensors, 30 virtual receptors), derived from A. Diamond's code. I saw this only in a search summary; UNVERIFIED. — [GitHub](https://github.com/iulialexandra/neuromorphic_odour_classifier)
- Other neuromorphic olfaction leads that appeared only in search results and were not opened (UNVERIFIED):
  - Frontiers in Neuroscience 2019 (10.3389/fnins.2019.00656) and 2021 (10.3389/fnins.2021.771480);
  - ISCAS 2024 odour-detection paper (UH);
  - "Fast, Smart Neuromorphic Sensors Based on Heterogeneous Networks and Mixed Encodings" (arXiv 2104.04121);
  - Dennler et al., high-speed miniaturised e-nose (arXiv 2406.01904).
  — [fnins 2019](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00656/pdf); [fnins 2021](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2021.771480/pdf); [ISCAS2024](https://uhra.herts.ac.uk/id/eprint/14545/1/ISCAS2024_OdorDetection.pdf); [arXiv 2104.04121](https://arxiv.org/pdf/2104.04121); [arXiv 2406.01904](https://arxiv.org/pdf/2406.01904)

### Inferences
- In what I read, the dominant hardware-neuromorphic pattern is receptor/latency encoding → lateral inhibition/WTA → learned readout. Sparse random expansion plus divisive normalisation appears much less often.

### Gaps
- I did not open the stage details of the SpiNNaker or Loihi e-nose follow-ups beyond Imam & Cleland. I made no systematic search of IEEE Xplore.

---

## 5. Review articles on bio-inspired / neuromorphic machine olfaction

### Takeaway
At least four reviews exist. Two are the most useful for mining further work: Raman, Stopfer & Semancik 2011, which organises the field by computing principles, and Dennler, True, van Schaik & Schmuker 2025, the most recent and critical. Vanarse et al. 2017 tabulates the spiking/neuromorphic e-noses.

### Cited Findings
- B. Raman, M. Stopfer, S. Semancik, "Mimicking Biological Design and Computing Principles in Artificial Olfaction", *ACS Chem. Neurosci.* 2(9):487–499 (2011), DOI 10.1021/cn200027r (read about 80%). — [PMC3212736](https://pmc.ncbi.nlm.nih.gov/articles/PMC3212736)
- A. Vanarse, A. Osseiran, A. Rassau, "An Investigation into Spike-Based Neuromorphic Approaches for Artificial Olfactory Systems", *Sensors* 17(11):2591 (2017), DOI 10.3390/s17112591, PMC5713038 (read about 80%; the reference list was truncated). — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713038/)
- N. Dennler, A. True, A. van Schaik, M. Schmuker, "Neuromorphic principles for machine olfaction", *Neuromorphic Computing and Engineering* (2025-05-06), DOI 10.1088/2634-4386/add0dc (abstract read via Crossref). It "critically review[s] ... event generation algorithms, information encoding mechanisms, event processing schemes (spiking neural networks), and learning", with a focus on fast and turbulent sensing. — [Crossref DOI](https://doi.org/10.1088/2634-4386/add0dc)
- A. Vanarse, A. Osseiran, A. Rassau, mini review of neuromorphic vision, auditory and olfactory sensors, *Frontiers in Neuroscience* 2016, DOI 10.3389/fnins.2016.00115. I saw this in search results only; not opened. — [Frontiers](https://www.frontiersin.org/articles/10.3389/fnins.2016.00115/full)

### Inferences
- The 2025 Dennler et al. review is the best place to check post-2017 work, including Loihi and SpiNNaker. I read only its abstract.

### Gaps
- I did not read the full text of the 2025 review, so post-2017 work it may cover (for example fly-hash or KC-expansion e-noses) remains unchecked. This is the single most important follow-up for the novelty question.
