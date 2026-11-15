# Air-to-mucus odorant transport models and their coupling to receptor/perception models

Scope note: sw-enose converts air ppb to liquid concentration at the receptor by equilibrium Henry's-law partitioning (air-water constants, Sander 2023 compilation), then applies receptor EC50 models. These notes cover prior work on air-to-mucus uptake, how sophisticated it is, and whether anyone chained it to receptor or perception predictions.

Method: PubMed E-utilities searches and record retrieval (esearch/esummary/efetch), plus one PMC full-text read. Titles, authors, years and venues below come from the PubMed records retrieved in this session. "Abstract" means only the PubMed abstract was read. "Full text" means the article body was read. All searches were PubMed only. Google Scholar, Crossref and publisher pages were not searched, so anything "not found" here is a gap in the search, not evidence that it does not exist.

---

## Q1. Classic nasal odorant uptake / chromatographic sorption theory (Mozell; Hahn, Scherer & Mozell; Keyhani, Scherer & Mozell; Zhao, Kurtz et al. CFD)

### Takeaway
There is a 60-year line of work on this. Mozell's experimental "chromatographic/sorption" theory (1964-1974) led to Hahn, Scherer & Mozell's 1994 analytical mass-transport model. That model runs from inspired air through sorption at the air-mucus interface and diffusion through mucus to interaction with receptors. Keyhani, Scherer & Mozell then built a 3-D finite-element CFD model in 1997, followed by CT-based patient-specific human, rat and canine CFD models (Zhao, Yang, Craven, Lawson; 2004-2019). All of these are flow and mass-transfer (kinetic) models. The mucus enters as a wall boundary condition built from solubility (the air/mucus partition coefficient), diffusivity and layer thickness. None is a pure equilibrium partition model like the one in sw-enose. The chromatographic theory itself has been challenged experimentally: two mouse EOG+CFD studies, in 2017 and 2019, failed to support it.

### Cited Findings
- **Mozell MM (1964).** "Evidence for sorption as a mechanism of the olfactory analysis of vapours." *Nature* 203:1181. DOI 10.1038/2031181a0. Record metadata only, abstract not read. — [PubMed 14213677](https://pubmed.ncbi.nlm.nih.gov/14213677/)
- **Mozell MM (1970).** "Evidence for a chromatographic model of olfaction." *J Gen Physiol* 56(1):46. DOI 10.1085/jgp.56.1.46. Record metadata only. — [PubMed 5514160](https://pubmed.ncbi.nlm.nih.gov/5514160/)
- **Mozell MM, Jagodowicz M (1973).** "Chromatographic separation of odorants by the nose: retention times measured across in vivo olfactory mucosa." *Science* 181(4106):1247-9. DOI 10.1126/science.181.4106.1247. Abstract: the column of a gas chromatograph was replaced with an in vivo frog olfactory sac. The wide range of relative retention times for 15 odorants "supports the concept of a chromatographic separation along the mucosa". — [PubMed 4542192](https://pubmed.ncbi.nlm.nih.gov/4542192/)
- **Hornung DE, Mozell MM (1977).** "Factors influencing the differential sorption of odorant molecules across the olfactory mucosa." *J Gen Physiol* 69(3):343. DOI 10.1085/jgp.69.3.343. Record metadata only. — [PubMed 300427](https://pubmed.ncbi.nlm.nih.gov/300427/)
- **Mozell MM, Sheehe PR, Hornung DE, Kent PF (1987).** "'Imposed' and 'inherent' mucosal activity patterns. Their composite representation of olfactory stimuli." *J Gen Physiol* 90(5):625. DOI 10.1085/jgp.90.5.625. Record metadata only. This paper is the source of the "imposed" (sorption-driven) vs "inherent" (receptor-sensitivity) patterning distinction used in later CFD work. — [PubMed 3500998](https://pubmed.ncbi.nlm.nih.gov/3500998/)
- **Hahn I, Scherer PW, Mozell MM (1994).** "A mass transport model of olfaction." *J Theor Biol* 167(2):115-28. DOI 10.1006/jtbi.1994.1057. Abstract. The model includes "(i) convective bulk flow ... (ii) lateral transport ... onto the olfactory mucus surface, (iii) sorption of odorant molecules into the mucus at the air-mucus interface, (iv) diffusion of odorant molecules through the mucus layer, and (v) interaction of odorant molecules with the olfactory receptor cells". It yields "the olfactory response" as a function of flow rate, mass transfer coefficient, inlet concentration, mucosa length and thickness, and "the air-mucus partitioning (or solubility in the mucus)". The model predicts that higher flow increases perceived intensity for highly soluble odorants (carvone) and decreases it for insoluble ones (octane). It "show[s] good agreement with various experimental data obtained from both psychophysical and electrophysiological studies". The abstract does not specify the functional form of the receptor-interaction step. — [PubMed 8207942](https://pubmed.ncbi.nlm.nih.gov/8207942/)
- **Keyhani K, Scherer PW, Mozell MM (1995).** "Numerical simulation of airflow in the human nasal cavity." *J Biomech Eng* 117(4):429-41. DOI 10.1115/1.2794204. Record metadata only. This is the airflow companion to the 1997 paper. — [PubMed 8748525](https://pubmed.ncbi.nlm.nih.gov/8748525/)
- **Keyhani K, Scherer PW, Mozell MM (1997).** "A numerical model of nasal odorant transport for the analysis of human olfaction." *J Theor Biol* 186(3):279-301. DOI 10.1006/jtbi.1996.0347. This confirms the title and venue in the prompt. Abstract:
  - It is an anatomically correct 3-D finite-element model with steady laminar flow and an uncoupled steady convective-diffusion equation.
  - "The mass-transfer boundary condition used at the nasal cavity wall included the effects of solubility and diffusivity of odorants in the mucosal lining, and the thickness of the mucus layer."
  - About 10% of the volumetric flow passes through the olfactory airway.
  - The model computes "total olfactory flux of odorants, that is highly correlated with perceived odor intensity".
  - It also computes spatial flux patterns ("imposed patterning") and the post-airflow decay of flux (time constants under 0.5 s).
  - The abstract does not say that a receptor-response model is attached. Perception is related through flux as a proxy. — [PubMed 9219668](https://pubmed.ncbi.nlm.nih.gov/9219668/)
- **Zhao K, Scherer PW, Hajiloo SA, Dalton P (2004).** "Effect of anatomy on human nasal air flow and odorant transport patterns: implications for olfaction." *Chem Senses* 29(5):365-79. DOI 10.1093/chemse/bjh033. Abstract: a method to convert patient CT scans to 3-D CFD nasal models in under a few days, predicting "airflow and odorant transport, which may ultimately determine olfactory sensitivity". — [PubMed 15201204](https://pubmed.ncbi.nlm.nih.gov/15201204/)
- **Kurtz DB, Zhao K, Hornung DE, Scherer P (2004).** "Experimental and numerical determination of odorant solubility in nasal and olfactory mucosa." *Chem Senses* 29(9):763-73. DOI 10.1093/chemse/bjh079. Abstract. It combines human in vivo measurement of the fraction absorbed (η) with CFD, using odorant blown through one nostril and out the other during velopharyngeal closure, measured by PID at 3.33 and 10 L/min. This is the main source of human mucosal solubility estimates; see Q2. — [PubMed 15574812](https://pubmed.ncbi.nlm.nih.gov/15574812/)
- **Zhao K, Dalton P, Yang GC, Scherer PW (2006).** "Numerical modeling of turbulent and laminar airflow and odorant transport during sniffing in the human and rat nose." *Chem Senses* 31(2):107-18. DOI 10.1093/chemse/bjj008. Abstract: essentially no difference in predicted olfactory odorant flux between turbulent and laminar flow (300-1000 ml/s). The reason is that "the much higher resistance to lateral odorant mass transport in the mucosal nasal airway wall than in the air phase". In rats, deposition "was highly dependent on solubility and correlated with the locations of different types of receptors." — [PubMed 16354744](https://pubmed.ncbi.nlm.nih.gov/16354744/)
- **Zhao K, Pribitkin EA, Cowart BJ, Rosen D, Scherer PW, Dalton P (2006).** "Numerical modeling of nasal obstruction and endoscopic surgical intervention: outcome to airflow and olfaction." *Am J Rhinol* 20(3):308-16. DOI 10.2500/ajr.2006.20.2848. Record metadata only. — [PubMed 16871935](https://pubmed.ncbi.nlm.nih.gov/16871935/)
- **Yang GC, Scherer PW, Zhao K, Mozell MM (2007).** "Numerical modeling of odorant uptake in the rat nasal cavity." *Chem Senses* 32(3):273-84. DOI 10.1093/chemse/bjl056. Abstract. It computes mucosal flux for 3 odorants of differing mucus solubility and compares the flux maps with receptor gene-expression zones. Soluble odorants are absorbed dorsally and medially, insoluble ones peripherally. The maps "agreed in general" with EOG and voltage-sensitive dye data. — [PubMed 17220517](https://pubmed.ncbi.nlm.nih.gov/17220517/)
- **Lawson MJ, Craven BA, Paterson EG, Settles GS (2012).** "A computational study of odorant transport and deposition in the canine nasal cavity: implications for olfaction." *Chem Senses* 37(6):553-66. DOI 10.1093/chemse/bjs039. Abstract: steady inspiration CFD in a reconstructed dog nose. Highly soluble odorants are deposited in front of the olfactory recess, while moderately soluble and insoluble ones deposit more uniformly. "ORNs that are sensitive to a particular class of odorants are located in regions where that class of odorants is deposited." This is a qualitative correspondence, not a response model. — [PubMed 22473924](https://pubmed.ncbi.nlm.nih.gov/22473924/)
- **Rygg AD, Van Valkenburgh B, Craven BA (2017).** "The Influence of Sniffing on Airflow and Odorant Deposition in the Canine Nasal Cavity." *Chem Senses* 42(8):683-698. DOI 10.1093/chemse/bjx053. Abstract: unsteady sniffing CFD (coyote). "A quasi-steady approximation is, therefore, justified for simulating time-averaged olfactory function." Sniffing gives 2.5-3x more uptake of highly and moderately soluble odorants per unit time. — [PubMed 28981825](https://pubmed.ncbi.nlm.nih.gov/28981825/)
- **Challenges to the chromatographic theory.**
  - **Coppola DM, Ritchie BE, Craven BA (2017).** "Tests of the sorption and olfactory 'fovea' hypotheses in the mouse." *J Neurophysiol* 118(5):2770-2788. DOI 10.1152/jn.00455.2017. Abstract: "sorption simulation patterns along individual nasal turbinates for particular odorants did not correlate with their EOG response gradients." — [PubMed 28877965](https://pubmed.ncbi.nlm.nih.gov/28877965/)
  - **Coppola DM, Fitzwater E, Rygg AD, Craven BA (2019).** "Tests of the chromatographic theory of olfaction with highly soluble odors: a combined electro-olfactogram and computational fluid dynamics study in the mouse." *Biol Open* 8(10):bio047217. DOI 10.1242/bio.047217. Abstract: "Results showed no relationship between local odor sorption patterns and EOG response maps", which casts "further doubt on the viability of this classical odor coding mechanism." — [PubMed 31649069](https://pubmed.ncbi.nlm.nih.gov/31649069/)

### Inferences
- Compared with this literature, the sw-enose equilibrium step is the simplest possible limit. It assumes mucus at the receptor is in equilibrium with the inlet air concentration. That ignores upstream depletion by anterior nasal mucosa, which matters most for highly soluble odorants. It also ignores mucus-side diffusion resistance, which Zhao et al. 2006 identify as the dominant resistance, and time-to-equilibrium. Keyhani 1997 reports fast decay after airflow stops (time constants under 0.5 s), but that is air-phase decay, not mucus equilibration.
- The prior models deliberately output flux (mass per area per time), not an equilibrium liquid concentration. The equilibrium concentration Cair/H is an upper bound on the steady mucus concentration at the interface, not necessarily the concentration at the cilia.

### Gaps
- Full texts of Hahn 1994 and Keyhani 1997 were not read, so the exact boundary-condition equations and partition values used were not checked.
- Mozell 1964/1970 and Hornung & Mozell 1977: only record metadata was read.
- The "Kurtz, Zhao et al. CFD models" named in the prompt are confirmed only as Kurtz et al. 2004 (above). Any other Kurtz-led CFD paper was not found in these searches.

---

## Q2. Mucus-air partition coefficients: measured or assumed equal to air-water? Effect of odorant-binding proteins

### Takeaway
Mucus/air partition has been measured, but only for a handful of odorants:
- frog (bullfrog) mucosa with radiolabelled odorants in the 1980s;
- human in vivo, estimated indirectly by fitting CFD to measured nasal absorption, for about 12 odorants (Kurtz et al. 2004).

Kurtz 2004 found that mucosal solubility departs from water solubility in an odorant-specific way. Lipophilic, less water-soluble odorants are *more* soluble in mucosa than water solubility alone predicts. Scott et al. (2014) turned this into an empirical correction of the air/water coefficient by log P, and it measurably improved prediction of receptor-epithelium responses. In the literature checked here, the usual CFD practice is the air/water value plus that kind of correction, not air/water alone. OBPs have been shown experimentally and computationally to change uptake: about 50,000-fold accumulation in OBP films, and a lower free-energy barrier to uptake. Neither OBP effect is captured by Henry's law.

### Cited Findings
- **Hornung DE, Youngentob SL, Mozell MM (1987).** "Olfactory mucosa/air partitioning of odorants." *Brain Res* 413(1):147-54. DOI 10.1016/0006-8993(87)90163-6. Abstract: measured mucosa/air partition coefficients in bullfrog using radioactive odorants, comparing intact mucosa with mucosa whose receptor cells had degenerated after nerve section. "For the more water-soluble odorants (butanol and isobutyric acid), both sides sorbed the same amount of odorant, suggesting that the mucosal uptake mostly reflects uptake by the water in the mucosa. For the less water soluble odorants (octane and amyl acetate), the uncut side did sorb significantly more odorant than the cut side." In other words, receptor-cell tissue adds sorption capacity for hydrophobic odorants. — [PubMed 3496142](https://pubmed.ncbi.nlm.nih.gov/3496142/)
- **Kurtz et al. (2004)**, Chem Senses 29:763, abstract: "the increase in diffusive resistance of the mucosal layer over that of a thin layer of water seemed to be general and non-odorant-specific; however, the mucosa solubility was odorant specific and usually followed the trend that odorants with lower water solubility were more soluble in the mucosa than would be predicted from water solubility alone." The abstract also says mucosal solubility "in the bullfrog mucus has been experimentally determined for a few odorants." — [PubMed 15574812](https://pubmed.ncbi.nlm.nih.gov/15574812/)
- **Scott JW, Sherrill L, Jiang J, Zhao K (2014).** "Tuning to odor solubility and sorption pattern in olfactory epithelial responses." *J Neurosci* 34(6):2025-36. DOI 10.1523/JNEUROSCI.3736-13.2014. Full text read via PMC3913860 (first ~100k of 107k characters).
  - The CFD wall boundary uses the air/mucus partition coefficient β, estimated as **log(β) = log(β_water) − (log P − 1) × 0.524**.
  - Both inputs come from US EPA EPI Suite.
  - The correction was calibrated on 12 odorants from Kurtz et al. 2004, based on a "strong linear relationship (R2 = 0.81)" between log P and the mucus-vs-water difference.
  - Using β instead of β_water raised the response-prediction correlation from r = 0.66 to r = 0.86.
  - Source: [PMC3913860](https://pmc.ncbi.nlm.nih.gov/articles/PMC3913860/); [PubMed 24501345](https://pubmed.ncbi.nlm.nih.gov/24501345/)
- **Shen J, Harada Y, Nakamura S (2024).** "Prediction on Air-Nasal Mucus Partition Coefficients of Odor Compounds." *ACS Omega* 9(29):31328-31334. DOI 10.1021/acsomega.3c07722. Abstract: a deep neural network using COSMO-RS σ-profiles predicts air-mucus partition coefficients. It states that "in vivo determination of the air-mucus partition coefficient is a technical challenge." The training data source was not checked. — [PubMed 39072110](https://pubmed.ncbi.nlm.nih.gov/39072110/)
- **Rygg AD, van Duin AC, Craven BA (2013).** "Molecular dynamics simulations of water/mucus partition coefficients for feeding stimulants in fish and the implications for olfaction." *PLoS One* 8(9):e72271. DOI 10.1371/journal.pone.0072271. Abstract: MD with a simplified mucus (mucin) model. It notes that air/mucus partition coefficients "can span up to six orders of magnitude" in terrestrial species. — [PubMed 24023732](https://pubmed.ncbi.nlm.nih.gov/24023732/)
- **OBP effect, experimental.** **Yabuki M, Scott DJ, Briand L, Taylor AJ (2011).** "Dynamics of odorant binding to thin aqueous films of rat-OBP3." *Chem Senses* 36(7):659-71. DOI 10.1093/chemse/bjr037. Abstract: gaseous odorants were passed through a capillary coated with aqueous rat-OBP3 film and monitored by APCI-MS. "All 5 odorants were quantitatively bound by rat-OBP3, which resulted in an effective concentration of the odorants in the aqueous layer (about 50 000-fold)." Release "was governed by the dissociation constant of the complex and the flow rate". — [PubMed 21536621](https://pubmed.ncbi.nlm.nih.gov/21536621/)
- **OBP effect, computational.** **Paesani M, Goetzee AG, Abeln S, Mouhib H (2025).** "Odorant Binding Proteins Facilitate the Gas-Phase Uptake of Odorants Through the Nasal Mucus." *Chemistry (Chem Eur J)* 31(2):e202403058. DOI 10.1002/chem.202403058. Abstract: in multi-scale simulation, carvone inside porcine OBP explores a conformational space "much closer to the gas than the aqueous phase", and "pOBP effectively manages to transport odorants by lowering the free energy barrier of odorant uptake." — [PubMed 39509459](https://pubmed.ncbi.nlm.nih.gov/39509459/)
- **Abraham et al. (2002).** "A model for odour thresholds", abstract: the residual not explained by "selective transport" includes "a specific size effect, that might involve odour-binding proteins". — [PubMed 11839607](https://pubmed.ncbi.nlm.nih.gov/11839607/)

### Inferences
- Using air-water Henry constants as the air-to-mucus step has precedent as a *starting point* (β_water in Scott 2014). The CFD/EOG literature found, however, that it under-predicts mucosal uptake for lipophilic odorants, and Scott 2014 quantified how much air-water partitioning loses as a predictor (r 0.66 vs 0.86).
- Applying the Scott 2014 correction illustratively, sw-enose's air-water assumption under-predicts mucus concentration by roughly 0.52 log units per log P unit above 1. For a log P of 3 that is about 1 log unit, i.e. 10x. This is my extrapolation from the Scott formula, not a published estimate for these compounds. The C3-C10 fatty acid panel in recent commits spans a wide log P range, so the bias would grow along the homologous series. The formula's validity range (12 odorants) was not checked, and it may not hold for ionizable acids at mucus pH.
- OBP binding can raise total (bound + free) mucus odorant by orders of magnitude in vitro. A receptor EC50 is presumably defined on *free* ligand concentration, so how OBPs affect free concentration at the receptor is not settled by these sources.

### Gaps
- Full Kurtz 2004 table of human mucosal solubility values: not read.
- Whether any measured human mucus/air coefficients exist for short-chain fatty acids specifically: not found in these searches.
- Effect of mucus pH on partitioning of carboxylic acids (ionization lowers apparent volatility): not searched. This is relevant to the fatty acid panel.

---

## Q3. Has any study coupled a nasal uptake model to receptor activation, a receptor-array model, or predicted detection thresholds?

### Takeaway
Yes, at the level of the whole epithelium and of perceived intensity or threshold, but not at the level of individual cloned olfactory receptors and their EC50s.
- The closest precedent is Scott, Sherrill, Jiang & Zhao (2014). They chained CFD-derived mucosal concentration (using a corrected air/mucus β) into a logistic concentration-response function and fit rat EOG responses for 66 odorants (r = 0.86).
- Hahn et al. 1994 included a receptor-interaction step and compared with psychophysical and electrophysiological data.
- Zhao/Dalton-lab studies correlate CFD flow features with measured human odour detection thresholds, but by correlation rather than a mechanistic threshold prediction.
- No study was found that chains an uptake model to a receptor-array model built from heterologous OR EC50 data.

### Cited Findings
- **Scott et al. (2014)**, J Neurosci, full text via PMC:
  - The response model is logistic, sigmoidal in log concentration. The authors note it is mathematically equivalent to a Hill form, but "the logistic equation is easier to fit in the absence of reliable estimates of the maximum response."
  - The intrinsic (open-preparation, no airflow) EOG response "were used as a multiplier of the log(odorant concentration)", and only the inflection parameter was fit separately for medial vs lateral sites.
  - "combining the intrinsic response with the mucosal concentration estimated by CFD in nonlinear regression successfully accounts for the measured retronasal and orthonasal EOG response at all flow rates and positions" (abstract).
  - The set is 66 odorants, 35 of them in open-preparation experiments.
  - The Results report r = 0.86, p < 0.01, while the Figure 6 legend says p < 0.001, a discrepancy within the paper.
  - The exact equation is an image and was not transcribed.
  - Source: [PMC3913860](https://pmc.ncbi.nlm.nih.gov/articles/PMC3913860/); [PubMed 24501345](https://pubmed.ncbi.nlm.nih.gov/24501345/)
- **Hahn, Scherer & Mozell (1994)** include "(v) interaction of odorant molecules with the olfactory receptor cells" and solve for "the olfactory response". The abstract claims "good agreement" with psychophysical and electrophysiological data. — [PubMed 8207942](https://pubmed.ncbi.nlm.nih.gov/8207942/)
- **Keyhani et al. (1997)** use total olfactory flux as the quantity "highly correlated with perceived odor intensity". This is a proxy; no receptor model appears in the abstract. — [PubMed 9219668](https://pubmed.ncbi.nlm.nih.gov/9219668/)
- **Li C, Jiang J, Kim K, Otto BA, Farag AA, Cowart BJ, Pribitkin EA, Dalton P, Zhao K (2018).** "Nasal Structural and Aerodynamic Features That May Benefit Normal Olfactory Sensitivity." *Chem Senses* 43(4):229-237. DOI 10.1093/chemse/bjy013. Abstract: 22 subjects, with CT-based CFD and unilateral ODTs for l-carvone, PEA and d-limonene. Vortex size correlated with the l-carvone ODT (r = 0.31). "ODT of d-limonene, a low mucosal soluble odor, does not correlate with any of the anatomical or aerodynamic variables." — [PubMed 29474516](https://pubmed.ncbi.nlm.nih.gov/29474516/)
- **Zhao K, Jiang J, Pribitkin EA, Dalton P, et al. (2014).** "Conductive olfactory losses in chronic rhinosinusitis? A computational fluid dynamics study of 29 patients." *Int Forum Allergy Rhinol* 4(4):298-308. DOI 10.1002/alr.21272. Record metadata only. — [PubMed 24449655](https://pubmed.ncbi.nlm.nih.gov/24449655/)
- **Yang et al. (2007)** and **Lawson et al. (2012)** compare CFD deposition maps with receptor zonal expression (rat) and ORN organization (dog) qualitatively. — [PubMed 17220517](https://pubmed.ncbi.nlm.nih.gov/17220517/); [PubMed 22473924](https://pubmed.ncbi.nlm.nih.gov/22473924/)
- **Coppola et al. 2017/2019** compare CFD sorption maps with EOG maps and found no local correspondence (see Q1). — [PubMed 28877965](https://pubmed.ncbi.nlm.nih.gov/28877965/); [PubMed 31649069](https://pubmed.ncbi.nlm.nih.gov/31649069/)
- **Takeuchi H, Ishida H, Hikichi S, Kurahashi T (2009).** "Mechanism of olfactory masking in the sensory cilia." *J Gen Physiol* 133(6):583-601. DOI 10.1085/jgp.200810085. Abstract. Ringer's solution pre-exposed to odorant-laden air suppressed single-cell currents, "suggesting that odorant suppression occurs after the evaporation and air/water partition of the odorant chemicals at the olfactory mucus." This is an experimental air-to-liquid-to-cell chain, not a model. — [PubMed 19433623](https://pubmed.ncbi.nlm.nih.gov/19433623/)

### Inferences
- An "air concentration → mucus concentration (partition) → sigmoidal dose-response" chain has direct published precedent in Scott et al. 2014. That paper is the nearest methodological ancestor of the sw-enose pipeline and worth citing. It differs from sw-enose in three ways: it uses CFD (not equilibrium), a corrected β (not air-water H), and fitted whole-epithelium EOG (not per-OR EC50s).
- Combining nasal-uptake modelling with a receptor-array model built from per-OR in vitro EC50s appears unexplored in the sources found. This is a search gap, not proven novelty.

### Gaps
- The prompt's "Zhao & Dalton" threshold work: no paper was found here that mechanistically predicts ODTs from simulated uptake. Only correlational studies (Li 2018) were found, plus record titles (Zhao 2014 CRS, Zhao 2006 Am J Rhinol) whose content was not read.
- Hahn 1994's receptor-interaction formulation (e.g. whether it is Langmuir/Hill-type binding) was not checked; full text was not read.
- Whether anyone used OR deorphanization EC50s (HEK293/Hana3A luciferase assays) together with a partition step to predict thresholds: no paper found in these PubMed searches. Google Scholar was not searched.

---

## Q4. Relating human odour detection thresholds to physicochemical properties including air-water partition (Abraham, Sánchez-Moreno, Cometto-Muñiz, Cain)

### Takeaway
Abraham, Cometto-Muñiz and Cain built linear free-energy relationship (LFER) models of human ODTs using Abraham solvation descriptors. The 2002 model frames thresholds as mostly "selective transport" from the gas phase, about 77% of the variance. The remainder is attributed to specific effects such as size (possibly OBPs) and aldehyde/acid potency. The 2012 model fits 353 ODTs with R² ≈ 0.76 and SD ≈ 0.82 log units. These are statistical transport-plus-specific-effect models, not mechanistic uptake models. Whether the air-water partition coefficient (log Kw) enters directly as a predictor, rather than through the descriptors from which log Kw is computed, could not be confirmed (full texts not accessible).

### Cited Findings
- **Abraham MH, Gola JM, Cometto-Muniz JE, Cain WS (2002).** "A model for odour thresholds." *Chem Senses* 27(2):95-104. DOI 10.1093/chemse/27.2.95. Abstract: ODTs "analysed by a general equation for selective transport ... such selective transport can account for some 77% of the total effect. The remainder is due to a specific size effect, that might involve odour-binding proteins, and a specific effect for aldehydes and carboxylic acids. Our analysis raises the question of whether selective transport is physically separable from the specific effects of receptor activation. The model predicts a chemical cut-off in odour detection along any homologous series." — [PubMed 11839607](https://pubmed.ncbi.nlm.nih.gov/11839607/)
- **Abraham MH, Sánchez-Moreno R, Cometto-Muñiz JE, Cain WS (2012).** "An algorithm for 353 odor detection thresholds in humans." *Chem Senses* 37(3):207-18. DOI 10.1093/chemse/bjr094. Abstract:
  - 193 Nagata ODTs fit with R² = 0.748 and SD = 0.830 log units, against an estimated 0.66 log-unit self-consistency of the data.
  - Indicator variables for aldehydes, acids, unsaturated esters and mercaptans.
  - Combined with Cometto-Muñiz/Cain, Cometto-Muñiz/Abraham and Hellman & Small data: 353 ODTs, R² = 0.759, SD = 0.819.
  - Source: [PubMed 21976369](https://pubmed.ncbi.nlm.nih.gov/21976369/). The PMC full text (PMC3278675) was blocked by a CAPTCHA and is not open access in Europe PMC, so it was not read.
- **Abraham MH, Acree WE Jr, Cometto-Muñiz JE (2020).** "Descriptors for terpene esters from chromatographic and partition measurements: Estimation of human odor detection thresholds." *J Chromatogr A* 1609:460428. DOI 10.1016/j.chroma.2019.460428. Abstract: derives descriptors "includ[ing] the air-water partition coefficient, as log Kw, for which no experimental values are available for any terpene ester". It constructs "another equation for the calculation of these thresholds". This shows the group treats log Kw and ODT as outputs of the same descriptor set. — [PubMed 31402107](https://pubmed.ncbi.nlm.nih.gov/31402107/)
- **Abraham MH et al. (2007).** "A quantitative structure activity analysis on the relative sensitivity of the olfactory and the nasal trigeminal chemosensory systems." *Chem Senses*. DOI 10.1093/chemse/bjm038. Record metadata only. — [PubMed 17573355](https://pubmed.ncbi.nlm.nih.gov/17573355/)
- **Abraham MH et al. (2010).** "The biological and toxicological activity of gases and vapors." *Toxicol In Vitro*. DOI 10.1016/j.tiv.2009.11.009. Record metadata only. — [PubMed 19913608](https://pubmed.ncbi.nlm.nih.gov/19913608/)
- **Cometto-Muñiz homologous-series psychometric (concentration-detection) functions.** These are the threshold datasets underlying the models. All record metadata only:
  - n-alcohols, Pharmacol Biochem Behav 2008 — [PubMed 18258288](https://pubmed.ncbi.nlm.nih.gov/18258288/)
  - n-acetate esters, Physiol Behav 2008 — [PubMed 18950650](https://pubmed.ncbi.nlm.nih.gov/18950650/)
  - 2-ketones, Behav Brain Res 2009 — [PubMed 19428635](https://pubmed.ncbi.nlm.nih.gov/19428635/)
  - n-alkylbenzenes, Neuroscience 2009 — [PubMed 19303922](https://pubmed.ncbi.nlm.nih.gov/19303922/)
  - aldehydes, Chem Senses 2010 — [PubMed 20190010](https://pubmed.ncbi.nlm.nih.gov/20190010/)
  - **"Structure-activity relationships on the odor detectability of homologous carboxylic acids by humans"**, Exp Brain Res 2010, DOI 10.1007/s00221-010-2430-0. This one is directly relevant to the sw-enose C3-C10 fatty acid panel. — [PubMed 20931179](https://pubmed.ncbi.nlm.nih.gov/20931179/)
  - dose-response compilation, Chem Senses 2016, DOI 10.1093/chemse/bjv060 — [PubMed 26476441](https://pubmed.ncbi.nlm.nih.gov/26476441/)

### Inferences
- There is precedent for treating ODT as "transport (partition) term + receptor-specific term". Abraham 2002 explicitly asks whether the two are "physically separable". The sw-enose decomposition (Henry partition, then receptor EC50) is a mechanistic version of that same split, and Abraham et al. are the natural comparison.
- The Cometto-Muñiz carboxylic acid ODT series (2010) is probably the best human threshold dataset to compare against sw-enose fatty-acid EC50-derived predictions. Its values were not extracted here.
- Abraham's own framing predicts a homologous-series "cut-off" from transport alone. A pure Henry's-law step would not produce one, because larger acids are less water-soluble and are therefore pushed out of water into air less, not more. This is my inference; check it against the 2002 full text.

### Gaps
- UNVERIFIED: whether log Kw (air-water partition) appears explicitly in the Abraham ODT equations, and how equation coefficients compare with those for air-water partition. Full texts of the 2002 and 2012 papers were not read.
- The carboxylic acid ODT values (Cometto-Muñiz 2010) were not extracted.

---

## Q5. E-nose / machine-olfaction work modelling a liquid or mucus layer over sensors

### Takeaway
The Warwick group (Gardner, Covington, Pearce) built hardware "artificial olfactory mucosa" / "electronic mucosa" devices. These are polymer-coated retentive channels over sensor arrays that emulate the chromatographic effect, i.e. a partitioning *stationary phase*, not an aqueous mucus. More recent work proposes OBP-based biomimetic sensors and canine-turbinate-shaped sensor substrates studied with CFD. No software e-nose was found that models an aqueous mucus layer by Henry's law ahead of receptor models.

### Cited Findings
- **Covington JA, Gardner JW, Hamilton A, Pearce TC, Tan SL (2007).** "Towards a truly biomimetic olfactory microsystem: an artificial olfactory mucosa." *IET Nanobiotechnol* 1(2):15-21. DOI 10.1049/iet-nbt:20060015. Abstract: an integrated channel "coated with a polymer to mimic the partitioning mucous layer, which is positioned directly over a sensor array". There are 80 carbon black/polymer chemoresistors. "Temporal chemical retention period of up to 170 s", with improved discrimination. — [PubMed 17428120](https://pubmed.ncbi.nlm.nih.gov/17428120/)
- **Che Harun FK, Covington JA, Gardner JW (2012).** "Mimicking the biological olfactory system: a Portable electron
ic Mucosa." *IET Nanobiotechnol* 6(2):45-51. DOI 10.1049/iet-nbt.2010.0032. Abstract: three arrays of 576 sensors with 24 coatings. The nasal chromatographic effect is "mimicked here using two-coated retentive channels ... coated with polar and non-polar compounds". — [PubMed 22559706](https://pubmed.ncbi.nlm.nih.gov/22559706/)
- **Persaud KC (2013).** "Engineering Aspects of Olfaction." In: *Neuromorphic Olfaction*, CRC Press, Ch. 1. Abstract/excerpt: "Odorant molecules need to partition from air into water before they can reach the transduction sites ... Soluble odorant binding proteins ... may have an odorant carrier and preconcentration role." — [PubMed 26042329](https://pubmed.ncbi.nlm.nih.gov/26042329/)
- **Paesani et al. (2025)** motivate OBP-based "protein-based biomimetic sensor units that can serve as artificial noses". — [PubMed 39509459](https://pubmed.ncbi.nlm.nih.gov/39509459/)
- **Liu Y, Tian F, Covington JA, et al. (2025).** "Bioinspired Substrate Structures for High-Performance Room-Temperature Chemiresistive Gas Sensors." *ACS Sens* 10(6):4045-4050. DOI 10.1021/acssensors.5c00028. Abstract: canine-turbinate-shaped sensor substrates studied with CFD. This is about the flow field, not a liquid layer. — [PubMed 40380944](https://pubmed.ncbi.nlm.nih.gov/40380944/)
- **Staymates ME et al. (2016).** "Biomimetic Sniffing Improves the Detection Performance of a 3D Printed Nose of a Dog and a Commercial Trace Vapor Detector." *Sci Rep*. DOI 10.1038/srep36876. Record metadata only. — [PubMed 27906156](https://pubmed.ncbi.nlm.nih.gov/27906156/)

### Inferences
- In hardware, the biomimetic "mucus" is a polymer stationary phase whose role is temporal separation (retention time). sw-enose uses the mucus step only as a static concentration transform. The two are different functional abstractions of the same biological layer.

### Gaps
- Bio-hybrid sensors with aqueous layers (OR- or OBP-functionalized FETs, QCM or SPR operating with a liquid film) were not systematically searched. PubMed "artificial mucosa" returned 118 hits, mostly irrelevant, and only the Covington-linked ones were examined.
- No software or computational e-nose with an explicit Henry's-law mucus step was found in these searches. Not searched: IEEE Xplore, Google Scholar, ISOEN proceedings.

---

## Overall gaps and caveats
- Searches were PubMed-only. Google Scholar, Crossref, IEEE and publisher sites were not used. PMC full text was obtained for only one paper (Scott 2014); the PMC page for Abraham 2012 returned a CAPTCHA.
- Most findings rest on abstracts. Boundary-condition details for Hahn 1994, Keyhani 1997 and Kurtz 2004 need full-text checks before being quoted as exact equations.
