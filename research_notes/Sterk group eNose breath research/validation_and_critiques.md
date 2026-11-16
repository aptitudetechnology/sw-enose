# Validation evidence for, and critiques of, the Sterk group's eNose breath analysis (Cyranose 320, SpiroNose / Breathomix), and the wider eNose breathomics methodology critique

Scope note: methodology only, no clinical advice. Bibliographic metadata below was copied from Europe PMC REST API records (which mirror PubMed) unless stated otherwise. PubMed pages themselves refused automated fetches, so the PubMed links are built from the PMIDs in those records. "Abstract" means only the abstract was read. "Full text" means the article body was read. A lead list supplied by the user (/home/chris/sw-enose/reports/20260202-V33-Breathomix-List-of-Publications.pdf, Breathomix, 2 Feb 2026) was used only to find leads. Each paper taken from it was confirmed from its own record.

## Q1. Per-study validation design and held-out performance (Sterk group and multicentre efforts)

### Takeaway
The early Cyranose 320 studies (2007–2009) reported only cross-validated accuracy on small case-control samples (n=40–90). Training/validation splits and "external" validation in newly recruited patients started around 2011. SpiroNose studies after 2019 report independent validation sets, and the strongest designs (multicentre prospective lung cancer, 2025; international ILD, 2026) show the expected loss of performance from training to external data. For example, lung cancer AUC was 0.92 in the original target population (COPD) but 0.80 in the broader population. ILD subtype AUCs were 0.88–0.92 in training versus 0.75–0.95 at external centres.

### Cited Findings

**Summary table (all from abstracts unless noted)**

| Study | Device | n | Validation design | Held-out metric | Training → held-out |
|---|---|---|---|---|---|
| Dragonieri 2007, JACI | Cyranose 320 | 40 (4 groups × 10) | Cross-validation only (single set) | CVV 100% mild asthma vs young controls; 90% severe asthma vs old controls; 65% mild vs severe | n/a |
| Fens 2009, AJRCCM | Cyranose 320 | 90 | Cross-validation only | Accuracy 96% asthma vs COPD | n/a |
| Fens 2011, Clin Exp Allergy | Cyranose 320 | 100 new patients | "External" = newly recruited patients tested on an earlier, independent training set | Fixed asthma vs COPD: accuracy 88%, AUC 0.95; classic asthma vs COPD: accuracy 83%, AUC 0.93 | Training figures not in abstract |
| de Vries 2015, J Breath Res | SpiroNose | 60 healthy (technical); 144 clinical (37 asthma, 31 COPD, 31 lung cancer, 45 controls) | Two-centre case-control, cross-validation only | Cross-validation 78–88% | n/a |
| Brinkman 2019, JACI (U-BIOPRED) | Assembly of eNoses, central analysis | 78 severe asthma | Unsupervised clustering; "internal validation" by alternative clustering methods; 12–18 month follow-up for stability | 3 clusters (26/33/19); no supervised held-out metric | n/a |
| de Vries 2019, Ann Oncol (anti-PD-1) | MOS eNose at pneumotachograph (SpiroNose-type) | 143 (training 92, validation 51) | Split training/validation, same programme | Validation AUC 0.85 (CI 0.75–0.96) | 0.89 → 0.85 |
| de Vries 2021 preprint (COVID, public test sites) | Cloud-connected eNose (SpiroNose) | 4510 | Training, validation, "replication" and asymptomatic sets | AUC 0.957 (validation, n=904), 0.937 (replication, n=1948), 0.909 (asymptomatic, n=754) | 0.947 → 0.909–0.957 |
| Moor 2021, ERJ (ILD; Erasmus MC) | SpiroNose | 322 ILD + 48 controls | 2:1 training/validation split in larger subgroups, single centre | ILD vs controls AUC 1.00; IPF vs other ILD validation AUC 0.87 | IPF: 0.91 → 0.87 |
| Buma 2025, Ann Oncol (lung cancer) | SpiroNose | 364 | Prospective, 2 sites; external validation of a published model + new model with training/validation cohorts | Original model AUC 0.92 in COPD, 0.80 in all; new model validation AUC 0.83 | See below |
| Formsma 2026, AJRCCM (fibrotic ILD) | SpiroNose | 587 | 5 international centres; trained on some centres, externally validated on others | Subtype vs other ILD AUC 0.75–0.95 (validation) | 0.88–0.92 → 0.75–0.95; subtypes 0.95–0.98 → 0.83–0.93 |

**Detail and quotes**

- Dragonieri S, Schot R, Mertens BJ, ... Bel EH, Sterk PJ. "An electronic nose in the discrimination of patients with asthma and controls." J Allergy Clin Immunol 2007. PMID 17658592, DOI 10.1016/j.jaci.2007.05.043 (abstract). Each of the four groups had 10 subjects. Breath was collected into Tedlar bags after 5 min of breathing VOC-filtered air and read on a Cyranose 320. Results: "mild asthma were fully separated from young controls (CVV, 100%...)"; "Patients with mild and severe asthma could be less well discriminated (CVV, 65%...)"; and "the 2 control groups were indistinguishable (CVV, 50%)". — [PubMed 17658592](https://pubmed.ncbi.nlm.nih.gov/17658592/)
- Fens N, Zwinderman AH, van der Schee MP, ... Bel EH, Sterk PJ. "Exhaled breath profiling enables discrimination of chronic obstructive pulmonary disease and asthma." Am J Respir Crit Care Med 2009. PMID 19713445, DOI 10.1164/rccm.200906-0939oc (abstract). There were 90 subjects: 30 COPD, 20 asthma, 20 non-smoking controls and 20 smoking controls. Reported cross-validated accuracy was asthma vs COPD 96%, asthma vs non-smoking controls 95% and asthma vs smoking controls 92.5%. COPD breath profiles "partially overlapped with those of asymptomatic smok[ers]". Repeatability was checked by measuring samples in duplicate on two devices. — [PubMed 19713445](https://pubmed.ncbi.nlm.nih.gov/19713445/)
- Fens N, Roldaan AC, van der Schee MP, Boksem RJ, Zwinderman AH, Bel EH, Sterk PJ. "External validation of exhaled breath profiling using an electronic nose in the discrimination of asthma with fixed airways obstruction and chronic obstructive pulmonary disease." Clin Exp Allergy 2011. PMID 21732998, DOI 10.1111/j.1365-2222.2011.03800.x (abstract). "External validity in newly recruited patients (validation sets) was tested using a previous and independent training set." Results: "88% accuracy for distinguishing fixed asthma from COPD (AUC 0.95, 95% CI 0.84-1.00, sensitivity 85%, specificity 90%) and 83% for classic asthma (AUC 0.93...)". "Discriminative accuracy was not confounded by current smoking." "External" here means a later-recruited set from the same group, not another centre or another group. — [PubMed 21732998](https://pubmed.ncbi.nlm.nih.gov/21732998/)
- de Vries R, Brinkman P, van der Schee MP, Fens N, Dijkers E, Bootsma SK, de Jongh FH, Sterk PJ. "Integration of electronic nose technology with spirometry: validation of a new approach for exhaled breath analysis." J Breath Res 2015;9(4):046001. PMID 26469298, DOI 10.1088/1752-7155/9/4/046001 (abstract). The device has five identical MOS sensor arrays: "three arrays monitoring exhaled breath and two reference arrays monitoring ambient air". Flow correlated with raw sensor deflection (R² = 0.84, n=60 healthy). "No correlation was found between sensor readings and exhaled volume, humidity and temperature." After environment correction, readings were reproducible (Cohen's kappa 0.81–0.94). The clinical part was two-centre and case-control, with "cross-validation values ranging between 78-88%". "Validation" in the title refers to technical validation, not external clinical validation. — [PubMed 26469298](https://pubmed.ncbi.nlm.nih.gov/26469298/)
- Brinkman P, Wagener AH, Hekking PP, ... (U-BIOPRED). "Identification and prospective stability of electronic nose (eNose)-derived inflammatory phenotypes in patients with severe asthma." J Allergy Clin Immunol 2019. PMID 30529449, DOI 10.1016/j.jaci.2018.10.058 (abstract). Data came from 78 subjects in an "unselected subset" of U-BIOPRED. Samples were "analyzed centrally by using an assembly of eNoses". "For internal validation, partitioning around medoids and topological data analysis were applied." There were three clusters (n = 26/33/19), which differed in blood eosinophils (P = .045), neutrophils (P = .017) and oral corticosteroid use (P = .035). Within-patient cluster stability was associated with changes in sputum eosinophils (P = .045). No external cohort was used. — [PubMed 30529449](https://pubmed.ncbi.nlm.nih.gov/30529449/)
- de Vries R, Muller M, van der Noort V, ... "Prediction of response to anti-PD-1 therapy in patients with non-small-cell lung cancer by electronic nose analysis of exhaled breath." Ann Oncol 2019. PMID 31529107, DOI 10.1093/annonc/mdz279 (abstract). "143 NSCLC patients (training: 92, validation: 51)"; "ROC-area under the curve (AUC) of 0.89 [CI 0.82-0.96]. This AUC was confirmed in the validation set: 0.85 (CI 0.75-0.96)." The validation set came from the same programme. Feature selection was "independent t-tests followed by linear discriminant" analysis. — [PubMed 31529107](https://pubmed.ncbi.nlm.nih.gov/31529107/)
- de Vries R, Vigeveno RM, Mulder S, ... Sterk PJ, in 't Veen JCCM ... "Ruling out SARS-CoV-2 infection using exhaled breath analysis by electronic nose in a public health setting." medRxiv preprint 2021, DOI 10.1101/2021.02.14.21251712 (abstract). There were 4510 individuals. The training set had only 35 SARS-CoV-2-positive people (versus 869 negative), with training AUC 0.947. Results: "confirmed in the validation set (0.957; ... n=904) and externally validated in the replication set (0.937; ... n=1948) and the asymptomatic set (0.909; ... n=754)". At cut-off 0.30, sensitivity/specificity was "100/78, >99/84, 98/82%". I did not find a peer-reviewed version of this paper in these searches (UNVERIFIED whether one exists). — [medRxiv DOI](https://doi.org/10.1101/2021.02.14.21251712)
- Moor CC, Oppenheimer JC, Nakshbandi G, Aerts JGJV, Brinkman P, Maitland-van der Zee AH, Wijsenbeek MS. "Exhaled breath analysis by use of eNose technology: a novel diagnostic tool for interstitial lung disease." Eur Respir J 2021. PMID 32732331, DOI 10.1183/13993003.02042-2020 (abstract). The study included 322 ILD patients and only 48 healthy controls. ILD vs controls had "AUC of 1.00 in the training and validation sets". IPF vs other ILD gave training AUC 0.91 and validation AUC 0.87. Subgroups were split 2:1 into training and validation at a single centre. — [PubMed 32732331](https://pubmed.ncbi.nlm.nih.gov/32732331/)
- Buma AIG, Muntinghe-Wagenaar MB, van der Noort V, de Vries R, Schuurbiers MMF, Sterk PJ, Schipper SPM, Meurs J, Cristescu SM, Hiltermann TJN, van den Heuvel MM. "Lung cancer detection by electronic nose analysis of exhaled breath: a multicentre prospective external validation study." Ann Oncol 2025 (36(7):786-795 per Breathomix lead list; volume and pages not checked against the record). PMID 40174676, DOI 10.1016/j.annonc.2025.03.013 (abstract).
  - The authors state: "prospective external validation studies are lacking."
  - Design: 364 participants from two Dutch thoracic oncology clinics, March 2019 to November 2023.
  - Original published model: "ROC-AUC of 0.92 [95% CI 0.85-0.99] in COPD patients (n = 98/116; 84%) and 0.80 (95% CI 0.75-0.85) in all participants". At 95% sensitivity, specificity was 72% (COPD) and 51% (all).
  - New model: on its validation cohort (n = 72/121 with cancer, 60%) it gave "ROC-AUC of 0.83 ..., sensitivity of 94%, specificity of 63%".
  - Performance falls when the model is moved from its original target population (COPD) to a broader one. Disease prevalence in the cohort was 59–84%, far above a screening setting.
  - Three letters to the editor were published, by Liu et al. (PMID 40368170), Rocco (PMID 40368168) and Szarpak et al., with an author reply (PMID 40461382). Their content was not read; the records have no abstract (gap).
  - Breathomix-affiliated author de Vries and Sterk are co-authors. Sterk is listed on the Breathomix lead list; his formal affiliation in this paper is not verified. — [PubMed 40174676](https://pubmed.ncbi.nlm.nih.gov/40174676/); letters [40368170](https://pubmed.ncbi.nlm.nih.gov/40368170/), [40368168](https://pubmed.ncbi.nlm.nih.gov/40368168/), reply [40461382](https://pubmed.ncbi.nlm.nih.gov/40461382/)
- Formsma BJ, Van Der Sar IG, Yazbeck L, Kreuter M, Cottin V, Polke M, Corte TJ, Tran M, Molyneaux PL, Moor CC, Wijsenbeek MS. "International validation of electronic nose technology as a diagnostic tool for fibrotic interstitial lung diseases." Am J Respir Crit Care Med 2026. PMID 41738130, DOI 10.1093/ajrccm/aamaf085 (abstract). The study covered 5 international ILD expert centres and 587 patients. "Models were trained on data from a selection of centers and externally validated in other centers." Subtype vs all other ILD: AUC "0.88 to 0.92 in the training set and 0.75 to 0.95 in the validation set". Between subtypes: "0.95 to 0.98 in the training set and 0.83 to 0.93 in the validation set". There is no healthy-control comparison, which avoids the easy AUC 1.00 contrast of the 2021 study. — [PubMed 41738130](https://pubmed.ncbi.nlm.nih.gov/41738130/)

### Inferences
- Over time the field moved from cross-validation on n≈40–90 to center-held-out validation on n≈600. The best-designed studies (Buma 2025, Formsma 2026) show the largest and most honest drops, which supports the view that the early 90–100% figures were inflated by design.
- "External validation" in the group's papers often means a later set from the same programme or centre (Fens 2011; de Vries 2019). Only Formsma 2026 holds out whole centres, and only Buma 2025 tests a frozen, previously published model on prospective data.
- Healthy controls inflate AUCs. Moor 2021 reports ILD vs healthy AUC 1.00 with 48 controls. Comparisons between clinically confusable groups (ILD subtypes; suspected vs confirmed lung cancer) are lower and more meaningful.
- The COVID preprint trained on 35 positive cases. Its very high validation AUCs did not hold up in GGD field use (see Q2), a clear example of the difference between validation in a study and verification in real use.

### Gaps
- The training-set AUC of the original COPD lung cancer model that Buma 2025 validated was not found; the original paper is not identified in these searches.
- The content of the Ann Oncol 2025 letters (Liu, Rocco, Szarpak) and the reply was not read.
- U-BIOPRED: no supervised eNose diagnostic model with an external cohort was found beyond Brinkman 2019 clustering.
- Full texts were not read for any primary study, so calibration, confidence intervals at fixed thresholds and per-centre breakdowns are unknown.

## Q2. Independent replication (groups not affiliated with Sterk/Breathomix)

### Takeaway
No fully independent replication was confirmed. SpiroNose work outside Amsterdam (Erasmus MC ILD and transplant, Leiden COVID follow-up) uses the Breathomix device and its analysis platform and often shares co-authors. The most independent real-world test, Dutch government verification at GGD test sites in 2021, found the device did not meet agreed sensitivity and specificity, and the contract was terminated.

### Cited Findings
- **Dutch COVID-19 deployment: evidence against field performance**
  - Ministry answer to parliamentary questions (Aanhangsel Handelingen TK 2021-2022, nr. 1818; answer by Minister Kuipers received 22 Feb 2022; full text read).
    - The ministry leased "1800 apparaten" (1800 devices) to 1 July 2022.
    - The breath test was "medio februari tijdelijk stopgezet naar aanleiding van een aantal mogelijke foute uitslagen" (temporarily halted in mid-February [2021] after a number of possibly incorrect results).
    - "uit de robuuste verificatie gebleken dat de afgesproken sensitiviteit niet werd behaald. Ook op de specificiteit bleef de ademtest achter" (robust verification showed the agreed sensitivity was not achieved, and specificity also fell short).
    - On 6 September 2021 the OMT advised against using the test "in de huidige vorm" (in its current form).
    - On data sharing: "Aan Breathomix is herhaaldelijk gevraagd om alle beschikbare data te delen, maar deze heeft Breathomix niet verstrekt" (Breathomix was repeatedly asked to share all available data but did not).
    - The answer gives no sensitivity or specificity numbers.
    - — [officielebekendmakingen ah-tk-20212022-1818](https://zoek.officielebekendmakingen.nl/ah-tk-20212022-1818.odt)
  - Landelijk Expertteam Ademtest letter (WOO release, undated, responding to an email of 2 March [2021]; full text read via pdftotext).
    - The validation study had reported "sensitiviteit ... 0.996 in de replicatie; 95% betrouwbaarheidsinterval 0.98 tot 1.00".
    - The team expected "de sensitiviteit bij verificatie in een reéle gebruiksomgeving lager zal zijn dan in de validatiestudie" (sensitivity in a real setting would be lower than in the validation study).
    - Targets were set at ≥0.95 with 0.90 as the floor, with double testing until at least 100 RT-PCR positives were included; no more than 4 false negatives were allowed to show sensitivity ≥0.90.
    - "de prestaties van de ademtest in Venray en Amsterdam erg uiteen liepen" (performance differed greatly between Venray and Amsterdam).
    - About 30% of results were "onduidelijk" (indeterminate). The team also asked for reporting on failed analyses and samples with too-high alcohol readings.
    - — [open.minvws.nl WOO document](https://open.minvws.nl/dossier/VWS-WOO/3551818-1045128-pdo/file/download/document/1ee84816-1426-6ccc-afa6-5d6a8657aabd)
  - Press report: DutchNews (15 July 2021, citing Volkskrant) said checks at three test centres found "For the vast majority of people, the results were so unreliable that they had to do another test". No figures were given; secondary source. — [DutchNews](https://www.dutchnews.nl/2021/07/coronavirus-breath-test-system-is-not-delivering-desired-results-volkskrant)
- **Leiden COVID follow-up: SpiroNose, not fully independent.** van Raaij BFM, Veltman JD, Hameete JF, Stöger JL, Geelhoed JJM. "Diagnostic performance of eNose technology in COVID-19 patients after hospitalization." BMC Pulm Med 2023. PMID 37081422, DOI 10.1186/s12890-023-02407-6, PMC10117233 (abstract). There were 135 post-COVID patients and 174 healthy controls, with leave-one-out cross-validation and AUC 0.893. "There was no difference in VOCs patterns in subgroups ... based on diffusion capacity or chest CT." Geelhoed is also a co-author of the de Vries COVID preprint, so the groups are linked. — [PubMed 37081422](https://pubmed.ncbi.nlm.nih.gov/37081422/)
- **Erasmus MC (Wijsenbeek group), ILD: SpiroNose.** Moor 2021 includes Amsterdam UMC co-authors (Brinkman, Maitland-van der Zee). Formsma 2026 has no Sterk or de Vries in its author list, but uses SpiroNose; any Breathomix analysis role or COI is UNVERIFIED. — [PubMed 32732331](https://pubmed.ncbi.nlm.nih.gov/32732331/); [PubMed 41738130](https://pubmed.ncbi.nlm.nih.gov/41738130/)
- **Other SpiroNose users, all cross-sectional single-centre feasibility studies with no external validation stated in their abstracts:**
  - Wijbenga et al., Erasmus MC lung transplant bacterial colonization. Transplant Direct 2023, PMID 37745948. — [PubMed 37745948](https://pubmed.ncbi.nlm.nih.gov/37745948/)
  - Heart-transplant glucose metabolism. Cardiovasc Diabetol 2025, PMID 41214692. — [PubMed 41214692](https://pubmed.ncbi.nlm.nih.gov/41214692/)
  - melaNose feasibility trial. Front Immunol 2025, PMID 40248699. — [PubMed 40248699](https://pubmed.ncbi.nlm.nih.gov/40248699/)
- **Bari group (Dragonieri, a former Sterk-group fellow), Cyranose-style eNose.** IPF vs autoimmune UIP, n=60, leave-one-out cross-validated accuracy 73.3%. A modest result, reported honestly. Sensors (Basel) 2026, PMID 42122346. — [PubMed 42122346](https://pubmed.ncbi.nlm.nih.gov/42122346/)

### Inferences
- The national COVID rollout is the clearest evidence in this field that high internal and "replication" AUCs (0.937; sensitivity 0.996) did not carry over to new sites and operators. Site-to-site variation (Venray vs Amsterdam), a high indeterminate rate and operator effects (the test being "not used properly") were the reported failure modes. These are exactly the risks an open-source e-nose project faces.
- Because the data were not shared (per the ministry), outsiders cannot check the failure.

### Gaps
- No peer-reviewed publication of the GGD robust-verification results was found, and no numbers were found.
- No group without Breathomix device or analytics involvement that replicated a specific Sterk-group model was found in these searches. This is a gap, not proof that none exists.
- Independent replication of Cyranose asthma/COPD models (Fens 2009/2011) by other centres was not found.

## Q3. Systematic reviews and meta-analyses

### Takeaway
Reviews in cancer, COPD and COVID report high pooled accuracy (sensitivity/specificity around 83–92%). They also consistently judge the evidence to be feasibility-level, with high risk of bias, very high heterogeneity, probable publication bias and rare external validation. An earlier review co-authored by the Sterk group found only 7 of 46 eNose studies used external validation, and re-analysis showed AUC losses of up to 0.38 from in-sample performance to external performance.

### Cited Findings
- **Scheepers MHMC, Al-Difaie Z, Brandts L, Peeters A, van Grinsven B, Bouvy ND.** "Diagnostic Performance of Electronic Noses in Cancer Diagnoses Using Exhaled Breath: A Systematic Review and Meta-analysis." JAMA Netw Open 2022;5(6):e2219372. DOI 10.1001/jamanetworkopen.2022.19372, PMC9244610 (full text, first ~100k characters).
  - Scope: 52 studies, 3677 patients with cancer. "All studies were feasibility studies."
  - Pooled accuracy: sensitivity 90% (88–92%), specificity 87% (81–92%), AUC 94%. Cyranose 320 subgroup: sensitivity 93%, specificity 89%.
  - QUADAS-2: index-test domain at high risk in 83% (43 studies), mainly from lack of standardization and reproducibility. Flow and timing at high risk in 54%, from "insufficient consideration of endogenous and exogenous factors". Patient selection at high risk in 40%.
  - Heterogeneity: I² 76.41% (sensitivity) and 95.53% (specificity). Device subgrouping did not reduce it.
  - Publication bias: the Deeks funnel test was significant (P = .02).
  - Confounder control: only 58% of studies reported fasting, 46% smoking cessation and 10% a rest period.
  - "Adequately powered external validation studies to confirm the results of these feasibility studies are rarely conducted."
  - de Vries 2015 SpiroNose is included (AUC 95%, accuracy 88%, lung cancer).
  - — [PMC9244610](https://pmc.ncbi.nlm.nih.gov/articles/PMC9244610/)
- **Leopold JH, Bos LDJ, Sterk PJ, Schultz MJ, Fens N, Horvath I, Bikov A, Montuschi P, Di Natale C, Yates DH, Abu-Hanna A.** "Comparison of classification methods in breath analysis by electronic nose." J Breath Res 2015. PMID 26669708, DOI 10.1088/1752-7155/9/4/046002 (abstract). This is the key overfitting evidence, co-authored by the Sterk group.
  - "From forty-six reviewed articles only seven applied external validation in an independent dataset, mostly with a case-control design." Four of the seven datasets could be obtained for re-analysis.
  - "Internal validation resulted in a decrease in ROC-AUCs compared to in-set performance: -0.15,-0.14,-0.1,-0.11".
  - "External validation resulted in lower ROC-AUC compared to internal validation in dataset 1 (-0.23) and 3 (-0.09)"; there was no decrease in datasets 2 (+0.07) and 4 (+0.04).
  - "No single combination of dimension reduction and classification methods gave consistent results between internal and external validation sets."
  - "Risk of bias was high in most studies due to non-random selection of patients."
  - — [PubMed 26669708](https://pubmed.ncbi.nlm.nih.gov/26669708/)
- **Chai Y et al.** "Exhaled breath VOCs detection methods: GC-MS versus eNose in COPD diagnosis." BMC Pulm Med 2025. PMID 41316246, PMC12860002 (abstract). Of 39 studies, 18 were meta-analysed. Pooled sensitivity was 83% and specificity 78%; eNose specificity was 0.87. QUADAS-2 was used. — [PubMed 41316246](https://pubmed.ncbi.nlm.nih.gov/41316246/)
- **COVID-19.**
  - Subali AD et al., Diagn Microbiol Infect Dis 2022, PMID 34879323 (abstract): 6 studies, 4093 samples, pooled sensitivity 98.2% and specificity 74.3%. — [PubMed 34879323](https://pubmed.ncbi.nlm.nih.gov/34879323/)
  - Long GA et al., Diagn Microbiol Infect Dis 2024, PMID 38692202 (abstract): 29 papers, sensitivity 0.92 and specificity 0.90, with lower sensitivity for Omicron and Delta. — [PubMed 38692202](https://pubmed.ncbi.nlm.nih.gov/38692202/)
  - Neither abstract mentions the failed Dutch field verification (see Q2), which shows the gap between published and real-world results.
- **Neugut EJ, Neugut AI.** "eNose technologies in the detection of cancer: a systematic review and meta-analysis." Oncologist 2026. PMID 41604309, PMC12923108 (abstract). 37 studies; pooled sensitivity 85.9% and specificity 83.6%. — [PubMed 41604309](https://pubmed.ncbi.nlm.nih.gov/41604309/)
- **Colorectal cancer breath VOC review (Frontiers in Oncology 2024, 10.3389/fonc.2024.1397259).** Search snippet only, not opened: "modest sample size, absence of standardized collection methods, lack of external validation, and a notable risk of bias" (UNVERIFIED, not opened). — [Frontiers](https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2024.1397259/full)
- **Bikov A, Lázár Z, Horvath I.** "Established methodological issues in electronic nose research: how far are we from using these instruments in clinical settings of breath analysis?" J Breath Res 2015;9(3):034001. PMID 26056127, DOI 10.1088/1752-7155/9/3/034001. Abstract only; it gives no specific conclusions. — [PubMed 26056127](https://pubmed.ncbi.nlm.nih.gov/26056127/)

### Inferences
- High pooled accuracy combined with I² above 90% for specificity, significant funnel asymmetry and near-universal case-control designs means the pooled figures are upper bounds, not expected field performance.
- Leopold 2015 gives a usable rule of thumb from real eNose data: expect AUC to fall by roughly 0.1–0.15 going from in-sample to cross-validated performance, and possibly by a further ~0.1–0.2 on external data. The size of the external drop is not predictable.

### Gaps
- No Cochrane review of eNose breath analysis was found.
- No review pooling only externally validated studies was found.
- The Steenhuis et al. lung cancer review (ERJ Open Res 2025, DOI 10.1183/23120541.00723-2024) appeared in search results but its findings were not read.
- No asthma-specific meta-analysis with risk-of-bias data was opened.

## Q4. Confounders and technical problems, and how the group addressed them

### Takeaway
The group's main technical counter-measures are: inspiratory VOC filters with a 5-minute washout and Tedlar bags (Cyranose era); then ambient-air reference sensor arrays with "alveolar gradient" environment correction and flow linked through the pneumotachograph (SpiroNose); plus checks of smoking as a confounder. Sensor drift, device-to-device transfer, operator effects and site effects remain weakly documented in what was read, and the COVID rollout showed that site and operator effects can dominate.

### Cited Findings
- **Ambient and room air.** SpiroNose uses "two reference arrays monitoring ambient air" with "environment correction based on alveolar gradients". After correction, reproducibility was kappa 0.81–0.94 (de Vries 2015). The Cyranose studies used 5 min of tidal breathing "through an inspiratory VOC filter" before collection into Tedlar bags (Dragonieri 2007; Fens 2009). — [PubMed 26469298](https://pubmed.ncbi.nlm.nih.gov/26469298/); [PubMed 17658592](https://pubmed.ncbi.nlm.nih.gov/17658592/); [PubMed 19713445](https://pubmed.ncbi.nlm.nih.gov/19713445/)
- **Flow, humidity and temperature.** Flow strongly drives raw signal (R² = 0.84). The group reports no correlation with volume, humidity or temperature in 60 healthy subjects (de Vries 2015). This is the group's own claim; independent confirmation was not found. Bikov and colleagues reported that "expiratory flow, breath hold and dead space influence exhaled volatile compound pattern assessed with electronic nose" (from a search summary of a BMC Pulm Med 2014 paper, 10.1186/1471-2466-14-202; not opened, UNVERIFIED). — [PubMed 26469298](https://pubmed.ncbi.nlm.nih.gov/26469298/)
- **Smoking.** "Discriminative accuracy was not confounded by current smoking" (Fens 2011). In Fens 2009, COPD breathprints partially overlapped with those of asymptomatic smokers. — [PubMed 21732998](https://pubmed.ncbi.nlm.nih.gov/21732998/); [PubMed 19713445](https://pubmed.ncbi.nlm.nih.gov/19713445/)
- **Medication.** In U-BIOPRED, eNose clusters differed in oral corticosteroid use (P = .035). Medication is therefore entangled with the phenotype signal rather than removed as a confounder. — [PubMed 30529449](https://pubmed.ncbi.nlm.nih.gov/30529449/)
- **Age and selection.** In Dragonieri 2007, groups were defined by both age and disease (young mild vs older severe asthma). In de Vries 2015, asthma patients and controls had mean ages of about 41, while COPD and lung cancer patients were about 63–66, so age is a potential confounder in the cross-validated separations. — [PubMed 17658592](https://pubmed.ncbi.nlm.nih.gov/17658592/); [PubMed 26469298](https://pubmed.ncbi.nlm.nih.gov/26469298/)
- **Alcohol, failed and indeterminate measurements (field).** The Expertteam asked for results broken down by failed analyses, unassessable analyses and "analyses bij te hoge alcoholwaarden" (too-high alcohol values). About 30% of results were indeterminate. — [WOO document](https://open.minvws.nl/dossier/VWS-WOO/3551818-1045128-pdo/file/download/document/1ee84816-1426-6ccc-afa6-5d6a8657aabd)
- **Sensor drift (independent, Amsterdam UMC paediatric/GI group, Cyranose 320, faecal samples).** Bosch S et al. "Electronic Nose Sensor Drift Affects Diagnostic Reliability and Accuracy of Disease-Specific Algorithms." Sensors 2022. PMID 36501947, PMC9740993 (abstract). "Sensor drift is a well-known disadvantage of electronic nose (eNose) technology ... Correction for this phenomenon is not routinely performed." "Sensor data displayed associations with date of measurement, which was reproducible across all samples." — [PubMed 36501947](https://pubmed.ncbi.nlm.nih.gov/36501947/)
- **Between-device variability.** Fens 2009 measured samples "in duplicate by two devices". U-BIOPRED used central analysis on one "assembly of eNoses" to avoid site-to-device variation. No SpiroNose calibration-transfer study was found. — [PubMed 19713445](https://pubmed.ncbi.nlm.nih.gov/19713445/); [PubMed 30529449](https://pubmed.ncbi.nlm.nih.gov/30529449/)
- **Diet and fasting across the field.** In the JAMA review, fasting was reported in only 58% of cancer eNose studies. — [PMC9244610](https://pmc.ncbi.nlm.nih.gov/articles/PMC9244610/)

### Inferences
- The reference-array design (measuring ambient air at the same time as breath) is the group's most transferable idea for an open-source build. However, the evidence that it removes room or hospital air effects is the group's own reproducibility data, not an across-site test, and the across-site COVID data did not support robustness.
- For drift, the independent Bosch 2022 finding that sensor data track measurement date argues for randomizing case and control measurement order and date, logging timestamps and testing date as a covariate.

### Gaps
- No full-text details were read on how SpiroNose handles sensor ageing, replacement, firmware or calibration over years, or how models transfer between the 1800 leased devices.
- No dedicated diet or medication challenge study for SpiroNose was found.
- The hospital-air effect was not quantified in the sources read.

## Q5. Standardisation: ERS technical standard and reporting guidance

### Takeaway
The ERS Task Force technical standard (Horváth et al., 2017; Sterk is a co-author) states that, unlike FeNO and EBC, there were no official standardised procedures for exhaled VOCs. It provides consensus recommendations for sampling, analysis and reporting. Its detailed eNose recommendations could not be read here (full text blocked). No breathomics-specific reporting guideline was confirmed beyond STARD/QUADAS-2 use in reviews.

### Cited Findings
- Horváth I, Barnes PJ, Loukides S, Sterk PJ, Högman M, Olin AC, Amann A, Antus B, Baraldi E, Bikov A, Boots AW, Bos LD, Brinkman P, ... "A European Respiratory Society technical standard: exhaled biomarkers in lung disease." Eur Respir J 2017. PMID 28446552, DOI 10.1183/13993003.00965-2016 (abstract only). The ERS article number is 1600965.
  - "For EBC and for FeNO, official recommendations for standardised procedures are more than 10 years old and there is none for exhaled VOCs and particles."
  - "Recommendations for standardisation of sampling, analysing and reporting of data and suggestions for research to cover gaps in the evidence have been created and summarised."
  - "This report is not intended to provide clinical guidance."
  - — [PubMed 28446552](https://pubmed.ncbi.nlm.nih.gov/28446552/)
- In practice, reviews use QUADAS-2 for risk of bias, some with modifications for external validation and for including benign conditions and healthy controls (Scheepers 2022). — [PMC9244610](https://pmc.ncbi.nlm.nih.gov/articles/PMC9244610/)
- The Dutch Expertteam's verification protocol is a concrete field-validation standard: pre-set sensitivity floor 0.90 and target ≥0.95; RT-PCR reference; at least 100 positives; an exact binomial test allowing at most 4 false negatives; verification at a second site; and reporting of failed and indeterminate rates. — [WOO document](https://open.minvws.nl/dossier/VWS-WOO/3551818-1045128-pdo/file/download/document/1ee84816-1426-6ccc-afa6-5d6a8657aabd)

### Inferences
- For an open-source e-nose project, a rigorous-validation checklist can be assembled from these sources:
  - Pre-register a frozen model and threshold.
  - Hold out whole sites, devices and time periods (Formsma 2026 design).
  - Include clinically confusable comparators rather than healthy controls (Buma 2025; Formsma 2026).
  - Report in-sample, cross-validated and external AUCs side by side (Leopold 2015).
  - Power the study on the lower confidence bound of sensitivity (Expertteam).
  - Report failed and indeterminate rates.
  - Log and test date/drift (Bosch 2022).
  - Share data (the ministry's complaint).

### Gaps
- The ERS 2017 full-text recommendations specific to eNoses were not read (publisher returned 403 / DNS failure). These include inspiratory filtering, breath-hold, dead space, ambient air sampling, drift and calibration, and data-analysis or validation recommendations. Specific recommendation wording is therefore UNVERIFIED and should be obtained from the full text.
- No dedicated breathomics reporting guideline (for example an extension of STARD or TRIPOD for eNose) was confirmed in these searches.
- The Bikov 2015 methodological review's specific conclusions were not available beyond its abstract.
