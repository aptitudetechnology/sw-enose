# Human odour detection thresholds in air, straight-chain carboxylic acids C2-C10

Compiled 2026-11-15. All values are copied as printed. No unit conversion was done.
"Not tested" means the source did not include that acid.

## PRIMARY SOURCE: Cometto-Muñiz & Abraham 2010 (full text read)

Record, copied from PubMed E-utilities (PMID 20931179) and the PMC XML:
- Authors: Cometto-Muñiz, J. Enrique; Abraham, Michael H.
- Title: "Structure-activity relationships on the odor detectability of homologous carboxylic acids by humans."
- Journal: Experimental Brain Research 207(1-2):75-84, Nov 2010 (epub 2010-10-08)
- DOI 10.1007/s00221-010-2430-0; PMCID PMC2964470; NIHMS248431. Open access, CC BY-NC.
- Full text read from the PMC XML: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=2964470 (https://pmc.ncbi.nlm.nih.gov/articles/PMC2964470)
- Supplementary Figs S1-S5 (individual functions) not opened.

### Acids tested
"Formic (95%, Food Chemical Codex, FCC), acetic (≥99.5%, FCC), butyric (≥99%, FCC), hexanoic (98+%, FCC), and octanoic (98+%, FCC) acids."
So C3, C5, C7, C9 and C10 were NOT TESTED.

### Method (quoted)
- Delivery: "Vapors were delivered by air dilution olfactometry, using a three-alternative forced-choice procedure against carbon-filtered air, and an ascending concentration approach." The device is the "8-station vapor delivery device (VDD8)" (Schmidt and Cain 2010). "Delivered concentrations increased by a factor of two from the lowest (in station 8) to the highest (in station 1)." "All participants completed 35 rounds with the same acid".
- Analytics: "During each testing session (day) the concentration of acid in the odor line of the VDD8 ... was repeatedly measured via gas chromatography (flame ionization detection, FID) ... at the rate of 2–4 samples per hour. Readings from the chromatograph were converted into vapor concentrations (parts per billion by volume, ppb) via a calibration curve for mass, specific for each carboxylic acid". Coefficient of variation across days: "38% for formic, 60% for acetic, 28% for butyric, 24% for hexanoic, and 29% for octanoic acid."
- Range tested: "37–4,754 ppb for formic, 0.72–92 ppb for acetic, 0.037–4.7 ppb for butyric, 0.13–16 ppb for hexanoic, and 0.049–6.3 ppb for octanoic acid."
- Threshold definition: chance correction P = (m·p(c) − 1)/(m − 1) with m = 3, then a logistic fit P = Pmax/(1+e^(−(x−C)/D)) with x in log ppb. "C is the value of x when P = 0.5, that is, when detection probability is half-way (P = 0.5) between chance (P = 0.0) and perfect (P = 1.0) detection. C was taken as the odor detection threshold (ODT) expressed in log ppb."
- Subjects: young (19–37 years), nonsmoker, normosmic participants; 33 recruited, with subgroups of 14 to 18 per acid.

### Table 2, upper part (group psychometric function, all subjects), quoted rows
Columns: n | ODT (ppb) | C (log ppb) | SE (C) | D | SE (D) | R²
- Formic acid 18 | 514 | 2.711 | 0.062 | 0.30 | 0.06 | 0.954
- Acetic acid 16 | 5.2 | 0.716 | 0.021 | 0.25 | 0.02 | 0.994
- Butyric acid 14 | 0.26 | −0.584 | 0.019 | 0.16 | 0.02 | 0.994
- Hexanoic acid 18 | 1.0 | 0.008 | 0.023 | 0.22 | 0.02 | 0.993
- Octanoic acid 14 | 0.86 | −0.066 | 0.026 | 0.20 | 0.02 | 0.990

Table 2, lower part (the 3 subjects tested with all five acids): Formic 485 ppb (C 2.686); Acetic 5.7 (0.759); Butyric 0.23 (−0.630); Hexanoic 1.1 (0.024); Octanoic 1.1 (0.042).

### Table 3 (individual fits): average and SE across subjects of individual C (log ppb)
- Formic (n=18): C average 2.60, SE 0.15 (D 0.26, SE 0.05)
- Acetic (n=16): C average 0.73, SE 0.09 (D 0.18, SE 0.02)
- Butyric (n=14): C average −0.58, SE 0.05 (D 0.12, SE 0.02)
- Hexanoic (n=18): C average 0.005, SE 0.07 (D 0.14, SE 0.02)
- Octanoic (n=14): C average −0.18, SE 0.18 (D 0.19, SE 0.08)
The (C, D) column alignment of these Average/SE rows was checked cell by cell in the PMC XML table markup. The average C values are bold in the C column, and the R² cells are empty.

Spread between the least and most sensitive subject (quoted): "the ratio equaled 636 for formic, 25 for acetic, 5.2 for butyric, 17 for hexanoic and 667 for octanoic." The large formic and octanoic ratios "were due to just one, and the same, very sensitive subject (S29)" (octanoic individual C = −2.41, R² 0.24).

Gender: "No significant effects of gender on odor detectability were observed."

Fig. 6 plots Devos et al. 1990, van Gemert 2003, Nagata 2003 and Wise et al. 2007 values for comparison. I did not read the numbers off the figure.

## SECONDARY SOURCES (cross-check only, not merged with the primary)

### S1. Nagata, "Measurement of Odor Threshold by Triangle Odor Bag Method" (full text read)
- Author: Yoshio Nagata (Japan Environmental Sanitation Center). Hosted by the Japan Ministry of the Environment in the "Odor Measurement Review" (PDF metadata title; created 2003), pp. 118-127.
- URL: https://www.env.go.jp/content/900450144.pdf (an identical table is in https://www.env.go.jp/content/900450159.pdf)
- Method (quoted): primary odour sample prepared in a polyester bag in nitrogen. Concentration "measured by gas chromatography (FID, FPD, FTD)". Threshold = "the concentration of primary odor sample/odor concentration" (ppm, v/v), using the triangle odor bag method. "An odor panel consists of 6 panelists", aged 20 to 50, trained and screened with the T&T olfactometer. Measurements made 1976-1988. For fatty acids "their thresholds were corrected by their recovery rate" (Table 1 recovery: n-butyric acid 40%). "About the odorants of which the thresholds were measured repeatedly, the geometric mean of each observed value was taken as the threshold". No per-acid SD is given.
- Table 2, "Odor thresholds measured by the triangle odor bag method (ppm,v/v)", quoted rows:
  - Acetic acid 0.0060
  - Propionic acid 0.0057
  - n-Butyric acid 0.00019
  - n-Valeric acid 0.000037
  - n-Hexanoic acid 0.00060
  - (Isobutyric acid 0.0015; Isovaleric acid 0.000078; Isohexanoic acid 0.00040 are branched acids, shown for context)
  - Heptanoic, octanoic, nonanoic and decanoic acid: not in Table 2 (grep found no entry). NOT TESTED in this list.

### S2. Wise, Miyazawa, Gallagher, Preti 2007 (abstract only)
- "Human odor detection of homologous carboxylic acids and their binary mixtures." Chemical Senses 32:475-82. PMID 17488748, DOI 10.1093/chemse/bjm016.
- Tested C2, C4, C6 and C8. Psychometric functions. Vapour concentrations "measured by a combination of solid-phase micro extraction and gas chromatography/mass spectrometry".
- Full text is paywalled (OUP returned 403 / "You do not currently have access"; not in Europe PMC OA). The abstract has no threshold numbers. VALUES UNVERIFIED / NOT OBTAINED.
- Related: Miyazawa et al. 2009, J Agric Food Chem 57:9895-901 (PMID 19817417, DOI 10.1021/jf901453r). C2/C4/C6/C8, 2-of-5 forced choice, GC-MS calibration. Abstract only, no threshold numbers.

### S3. Devos et al. 1990, "Standardized Human Olfactory Thresholds"; van Gemert 2003 compilation
- These are books. I did not open them and obtained NO VALUES. They appear only graphically in Cometto-Muñiz & Abraham Fig. 6 (left), which I did not digitise.

## Coverage gaps
- C7 (heptanoic), C9 (nonanoic), C10 (decanoic): no measured, analytically verified human threshold found in any source I opened.
- C3 (propanoic), C5 (pentanoic): only Nagata (secondary).
- Unattributed web compilations (e.g. a Scribd "Thresholds table") came up in search. I did not use them.
