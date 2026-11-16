# SpiroNose (Sterk group / Amsterdam UMC / Breathomix) and predecessor eNoses: engineering design and signal-processing methods

Scope: engineering and methods only, for someone building a low-cost MOS e-nose (e.g. a BME688 with heater profiles). Nothing here is clinical advice.

Sources actually opened (full text unless marked otherwise):
- **[JBR2015]** de Vries R, Brinkman P, van der Schee MP, Fens N, Dijkers E, Bootsma SK, de Jongh FH, Sterk PJ. "Integration of electronic nose technology with spirometry: validation of a new approach for exhaled breath analysis." *J Breath Res* 2015;9(4):046001. PMID 26469298. DOI 10.1088/1752-7155/9/4/046001. Open-access PDF read in full: https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf (also Chapter 3 of the de Vries thesis).
- **[ERJ2018]** de Vries R, Dagelet YWF, Spoor P, et al. "Clinical and inflammatory phenotyping by breathomics in chronic airway diseases irrespective of the diagnostic label." *Eur Respir J* 2018;51(1):1701817. PMID 29326334. DOI 10.1183/13993003.01817-2017. The ERJ site returned 403. I read the full text plus the online supplement as reproduced in Chapter 4 of the de Vries PhD thesis: https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf
- **[Thesis2022]** de Vries R. "eNose analysis of exhaled breath for diagnosing and phenotyping respiratory diseases." PhD thesis, University of Amsterdam, 2022. Record: https://dare.uva.nl/id/f288f245-af56-4efc-9d6e-d389c708aa2d. I read the Chapter 8 general discussion in full: https://pure.uva.nl/ws/files/86066334/Chapter_8.pdf
- **[Brinkman2019]** Brinkman P. "Biomedical engineering for breathomics: towards clinical application in respiratory diseases." PhD thesis, University of Amsterdam, 2019. Record: https://dare.uva.nl/id/de70b6de-4d95-4eca-acf5-d0305b973b34. PDF: https://pure.uva.nl/ws/files/42598554/Thesis.pdf. pdftotext reported an xref error but extracted text. I searched it by keyword; I did not read it end to end.
- **[Chest2023]** de Vries R, et al. "Prospective Detection of Early Lung Cancer in Patients With COPD in Regular Care by Electronic Nose Analysis of Exhaled Breath." *Chest* 2023;164(5):1315–1324. DOI 10.1016/j.chest.2023.04.050. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10635840/
- **[Chest2021]** van der Sar IG, Moor CC, Oppenheimer JC, et al. "Diagnostic Performance of Electronic Nose Technology in Sarcoidosis." *Chest* 2022;161(3):738–747 (online 2021). DOI 10.1016/j.chest.2021.10.025. Full text, but the supplement (mmc1.pdf) was not read: https://pmc.ncbi.nlm.nih.gov/articles/PMC8941620/
- **[RespRes2023]** van der Sar IG, Wijsenbeek MS, Braunstahl GJ, et al. "Differentiating interstitial lung diseases from other respiratory diseases using electronic nose technology." *Respir Res* 2023;24:271. DOI 10.1186/s12931-023-02575-3. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10626662/
- **[BMC2023]** van Raaij BFM, Veltman JD, Hameete JF, Stöger JL, Geelhoed JJM. "Diagnostic performance of eNose technology in COVID-19 patients after hospitalization." *BMC Pulm Med* 2023;23:134. DOI 10.1186/s12890-023-02407-6. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10117233/
- **[JBR2023-sarc]** van der Sar IG, van Jaarsveld N, Spiekerman IA, et al. "Evaluation of different classification methods using electronic nose data to diagnose sarcoidosis." *J Breath Res* 2023;17(4). PMID 37595574. DOI 10.1088/1752-7163/acf1bf. Abstract only, via the Europe PMC record.
- **[AnnOnc2025]** Buma AIG, Muntinghe-Wagenaar MB, van der Noort V, de Vries R, et al. "Lung cancer detection by electronic nose analysis of exhaled breath: a multicentre prospective external validation study." *Ann Oncol* 2025;36(7):786–795. PMID 40174676. DOI 10.1016/j.annonc.2025.03.013. Abstract only, via Europe PMC.
- **[Lazar2010]** Lazar Z, Fens N, van der Maten J, et al. "Electronic nose breathprints are independent of acute changes in airway caliber in asthma." *Sensors* 2010;10:9127. PMID 22163399. DOI 10.3390/s101009127. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC3230982/
- **[Dragonieri2007]** Dragonieri S, Schot R, Mertens BJA, et al. "An electronic nose in the discrimination of patients with asthma and controls." *J Allergy Clin Immunol* 2007. PMID 17658592. DOI 10.1016/j.jaci.2007.05.043. Abstract only.
- **[Leopold2015]** Leopold JH, Bos LDJ, Sterk PJ, et al. "Comparison of classification methods in breath analysis by electronic nose." *J Breath Res* 2015. PMID 26669708. DOI 10.1088/1752-7155/9/4/046002. Abstract only.
- Breathomix web pages, used as leads and manufacturer claims only: product page https://www.breathomix.com/?p=554 and development timeline https://breathomix.com/?p=1853
- Breathomix publication list (user-supplied, /home/chris/sw-enose/reports/20260202-V33-Breathomix-List-of-Publications.pdf). I used it only as a lead list and confirmed each entry I cite from its own record.

---

## 1. Sensors: number, type, manufacturer, arrangement, operating temperature

### Takeaway
The sensor hardware changed across versions.
- **2015 prototype:** 5 identical arrays of 4 Figaro (Japan) thick-film SnO2 MOS sensors. 3 arrays sat in the breath path and 2 outside the tube as ambient references.
- **2018 onward:** 7 different MOS sensor types. Each type appears in duplicate on both the breath side and the reference side, which gives 28 sensors.
- **Description conflict:** ERJ2018 describes the 28 sensors as 8 arrays (4 breath, 4 reference). Breathomix describes them as "four sets of seven" (2 breath, 2 ambient). My reading is that both describe the same 28 sensors.
- **Not published in what I read:** the manufacturer and model of the 7 later sensors, and any heater temperature or heater modulation.

### Cited Findings
- **2015 hardware.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), Methods, verbatim: "The SpiroNose consists of five separate sensor arrays, each comprising four metal oxide semiconductor (MOS) sensors (Figaro, Japan). The choice of Figaro-type MOS sensors was based on their good long-term performance and stability [20]. Two of the sensor arrays were used as reference arrays to detect the ambient VOCs and three sensor arrays were used to monitor the VOCs in exhaled breath (figure 1). All sensor arrays are identical and consist of four different MOS sensors with operating temperatures ranging between −40 °C and +70 °C. Using thick film techniques, the sensor material is printed on electrodes onto an alumina substrate. The four MOS sensors all used tin dioxide (SnO2) as the main sensing material of the sensor element."
  - Ref [20] is Romain AC, Nicolas J, "Long term stability of metal oxide-based gas sensors for e-nose environmental applications: an overview," *Sensors Actuators B* 146:502–6 (2010).
- **2015 geometry.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), Fig. 1 caption: "three arrays of MOS sensors placed inside the tube for exhaled breath analysis ... two arrays of MOS sensors placed at the outside of the tube, used for environment correction." The arrays sit "at the rear end of a pneumotachograph" (abstract).
- **2015 device and data path.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf):
  - Co-developed by AMC Amsterdam and Comon Invent BV, Delft.
  - Output was "changes in electrical voltage," sent in real time by a GSM module to a Comon Invent server.
- **2018 hardware.** [ERJ2018 supplement, via thesis Ch. 4](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf), verbatim: "The SpiroNose consists of 8 separate sensor arrays, 4 reference sensor arrays to monitor environmental air and 4 sensor arrays used to monitor the VOCs in exhaled breath (Figure 4.2). In total, the SpiroNose contains 7 different metal oxide semiconductor (MOS) sensors and each sensor is present in duplicate in both the reference and breath-monitoring sensor arrays."
  - Fig. 4.2 caption: "The four central sensor arrays monitor exhaled breath; the four reference sensor arrays monitor ambient volatile organic compounds."
  - The same paper analyses "the original 14 sensor peaks and the 14 peak/BH ratios (28 variables in total)." That is 14 breath sensors, i.e. 7 types × 2.
- **Later descriptions.**
  - [Chest2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10635840/): "seven different cross-reactive metal-oxide semiconductor sensors (sensors 1-7)"; "Another set of the same sensors sampled ambient air for background correction."
  - [BMC2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10117233/): "duplicate sensors positioned on the outside of the device."
  - [RespRes2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10626662/): "seven different metaloxide semiconductor sensors in various arrays."
- **Manufacturer claim (Breathomix product page).** [Breathomix](https://www.breathomix.com/?p=554): "equipped with 28 sensors arranged in four sets of seven. Two sets focus on capturing the VOCs present in exhaled breath," and the other two "monitor the VOCs in the surrounding air."
- **Prototype history (Breathomix timeline).** [Breathomix timeline](https://breathomix.com/?p=1853):
  - Prototype I (2014): 2 USB sensors.
  - Prototype II (2015): 6 MOS sensors.
  - Prototype III (2016): 7 MOS sensors.
  - Prototype IV: connected to the BreathBase cloud.
  - Conflict: JBR2015 describes 4 sensor types × 5 arrays. The "6 MOS sensors" for Prototype II does not match the published paper.
- **Predecessor MOS module.** [Brinkman2019](https://pure.uva.nl/ws/files/42598554/Thesis.pdf), U-BIOPRED composite platform: "Common Invent eNose using metal oxide semiconductor sensors [33] [8 sensors]," alongside Cyranose C320, Tor Vergata QMB and Owlstone Lonestar FAIMS.

### Inferences
- **The −40 to +70 °C figure.** It almost certainly comes from a Figaro datasheet ambient operating range, not a heater set-point. No heater temperature or heater profile is reported. That suggests constant-temperature (datasheet default) operation, but this is UNVERIFIED.
- **Readout.** The design uses resistance read out as voltage, followed by temporal waveform analysis. It does not use temperature-modulated feature extraction.
- **Relevance to a BME688 build.** The SpiroNose gets its discrimination from about 7 sensor chemistries × 2 replicates plus temporal/manoeuvre features. A BME688 heater profile gives up to 10 heater steps per sensor, which is a different route to pseudo-sensor diversity. This is an inference, not from the sources.

### Gaps
- **Sensor identity (7-sensor generation).** Manufacturer and model are not found in these searches. Figaro TGS-series is plausible but UNVERIFIED for post-2015 devices.
- **Heater and thermal design.** Heater voltage, temperature, sampling rate, ADC resolution, and the tube/array geometry dimensions were not found.
- **Patents.** I did not search Google Patents for a SpiroNose or Comon Invent patent, so this remains open.
- **[Chest2021] supplement.** e-Appendix 1 on sensor processing (mmc1.pdf) was not read.

---

## 2. Ambient correction method

### Takeaway
Ambient correction is reference-signal subtraction, described as "alveolar gradients" (expiratory minus inspiratory concentration). The steps are:
1. Low-pass Butterworth filter the reference signals.
2. Remove linear trends from them by least-squares fit.
3. Average them.
4. Time-align the averaged reference to each breath signal by cross-correlation.
5. Subtract it from the low-pass-filtered breath signal.
6. Remove residual linear trends and offsets.

No ratio or regression model is used for this step. Normalisation to a reference sensor comes afterwards, as a separate feature step (section 4).

### Cited Findings
- **2015 Methods, "Environment correction".** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), verbatim:
  - "The environment correction was based on the calculation of alveolar gradients [21–23]. Alveolar gradients were obtained by subtracting inspiratory (reference signal) from expiratory VOC concentrations (patient signal) [22, 23]."
  - "Reference sensor signals were filtered using a low-pass Butterworth filter to extract the overall shape of the signal, followed by linear trend removal based on a least squares fit. Subsequently, both reference signals were averaged."
  - "Cross-correlation was used to obtain the highest correlation between reference and patient signal, as both showed a similar but delayed pattern."
  - "Finally, the patient sensor signals were filtered using a low-pass Butterworth filter before subtracting the processed and averaged reference signal. Following this environment correction, linear trends and offsets were removed from the patient signals. The three processed and corrected patient signals were not averaged."
  - Refs [21–23] are Phillips 1997 and 1999 (alveolar gradient) and Miekisch 2004.
- **2018 Methods (supplement).** [ERJ2018 supplement](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf), verbatim. It is the same method plus one added first step:
  - "The processing of the sensor signals started with the removal of the SpiroNose's eigenfrequency. Subsequently, reference sensor signals were averaged after they were filtered using a low-pass Butterworth filter followed by linear trend removal based on a least squares fit. The patient sensor signals were also filtered with a low-pass Butterworth filter."
  - "Cross-correlation was used to obtain the highest correlation between reference and patient signal, as both showed a similar but delayed pattern. The environment correction was based on the calculation of alveolar gradients (4-6). Patient sensor signals were subtracted by the processed and averaged reference signal. Finally, linear trends and offsets were removed from the 2 patient signals."
- **Effect on array-to-array agreement.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf):
  - Before processing, the three in-tube arrays differed significantly "for sensor 1 (p < 0.001) and sensor 3 (p < 0.05)," even though they sampled the same breath.
  - After processing and ambient correction there were no significant differences. Reproducibility was "Cohen's kappa results ranging from 0.81 to 0.94."
  - Discussion: "in retrospect this strategy [two reference arrays] might have been overly cautious" because "of the large similarity of responses between sensor arrays."
- **Rationale versus a VOC filter on inhalation.** [Thesis2022 Ch. 8](https://pure.uva.nl/ws/files/86066334/Chapter_8.pdf):
  - The group proposes "an 'ambient correction method' based on multiple sensor arrays that measure environmental VOCs real-time before and during the actual breath measurement," as "a different approach than the 'wash-out' method."
  - They note that with VOC filters "it is not known how long such a wash-out period should last."
  - They report that correction "significantly improved" discrimination and "the time needed for an individual patient measurement was significantly reduced."
- **Later papers describe the step only briefly.** Examples: "Sensor readings are corrected for VOCs in ambient air" ([BMC2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10117233/)); "data correction for ambient air" ([RespRes2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10626662/)). Breathomix states correction is done in the BreathBase platform ([Breathomix](https://www.breathomix.com/?p=554)).

### Inferences
- **Meaning of "eigenfrequency".** Removing the "SpiroNose's eigenfrequency" probably means a notch or band-stop filter at a device-specific oscillation, such as a mechanical, electrical or sampling artefact. Neither the method nor the frequency is given (UNVERIFIED).
- **Why the lag correction matters.** Reference sensors outside the tube see room air with a lag relative to the in-line sensors. Cross-correlation alignment compensates for this. A BME688 build with a second, ambient-exposed sensor could copy the pipeline directly: low-pass filter, detrend, cross-correlation lag, then subtract.

### Gaps
- **Filter parameters.** Butterworth order and cutoff frequency, sampling rate, and the cross-correlation lag search window are not reported in what I read.
- **Current algorithm.** Whether the BreathBase production algorithm still matches the 2015/2018 description is not found.

---

## 3. Breath sampling manoeuvre and spirometry integration

### Takeaway
The SpiroNose sits in series behind a pneumotachograph, with a mouthpiece, nose clip and viral/bacterial filter. There is no VOC filter on inhalation; ambient correction replaces it.

Manoeuvre:
- **2015:** 10 tidal breaths, then inspiratory capacity to TLC, a 5 s breath hold, and slow exhalation (<0.4 L/s) of a vital capacity. Done in duplicate, 2 min apart, after mouth rinsing ×3.
- **2018 onward:** 5 tidal breaths instead of 10. Exhalation is slow (<0.4 L/s) to residual volume.

Flow mattered:
- Raw sensor deflection tracked expiratory flow (R² = 0.84).
- Sensor ratios were less flow-dependent.
- The authors recommend 0.19–0.38 L/s.

No dead-space discard is described. The breath-hold point is used as a feature anchor instead.

### Cited Findings
- **Measurement setup.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf): "a soft bite mouthpiece, nose clamp and viral/bacterial filter (Lemon Medical GmbH) attached to a Masterscreen™ PFT system (Masterscreen, Jaeger, Care Fusion) and the SpiroNose." ERJ2018 adds the Vmax Encore PFT system ([Ch. 4](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf)).
- **2015 manoeuvre.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf): "All patients were instructed to start the measurement by performing 10 tidal breaths. After a single deep inspiratory capacity maneuver and a 5 s breath hold the patient exhaled, with an expiratory flow <0.4 L s−1, a vital capacity volume into the measurement setup."
  - Measurements were "performed right before regular spirometry."
  - Patients "rinse their mouth thoroughly three times with water"; analysis "in duplicate with a 2 min interval."
- **2018 manoeuvre.** [ERJ2018](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf): "5 tidal breaths followed by a single inspiratory capacity maneuver up to total lung capacity, a 5 second breath hold and slow (<0.4 L/s) maximal expiration towards residual volume." The same protocol appears in [Chest2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10635840/) and [Chest2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8941620/).
- **Signal features of the manoeuvre.** [ERJ2018](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf), Fig. S4.1: the inspiratory capacity manoeuvre appears as a "drop in sensor signal"; the breath hold is the "red triangle"; and the slow expiration runs to the "green star" (the peak).
- **Flow, volume, humidity and temperature.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf):
  - "Expiratory flow showed a significant linear correlation with raw sensor deflections (R² = 0.84) ... No correlation was found between sensor readings and exhaled volume, humidity and temperature."
  - Discussion: "our data suggest that expiratory flow rates between 0.19 and 0.38 L s−1 are suitable." Also: "it is not possible to regulate expiratory flow by means of a resistor. The expiratory flow can only be influenced by instructing the patient ... e.g. visual feedback from pneumotachograph measurements."
  - The authors suggest MOS sensors "likely become saturated" in that flow range.
- **Effect on spirometry.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf): three FVC set-ups were compared (normal calibration; calibration before adding the SpiroNose; calibration after adding it). Spirometry was not affected (p > 0.5).
- **Bacterial filter.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf): measurements were compared with and without the filter in 10 asthma patients and 10 controls. Discrimination was retained with the filter (abstract fragment: "CVV 78%) a bacterial filter").
- **Duration claim.** [Breathomix](https://www.breathomix.com/?p=554): "Exhaled breath is measured in approximately 30 seconds." This is a manufacturer claim; no paper I read states the duration.
- **Predecessor (Cyranose) sampling.** [Lazar2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC3230982/), full text:
  - Subjects "inhaled VOC-filtered air (A2, North Safety, Middelburg, Netherlands)" for "5 min of equilibration with tidal breathing."
  - Then a "maximal inspiratory capacity maneuver and the full expiratory capacity volume was collected into a 10-L Tedlar bag." "Bags were sampled within ten minutes." A room-air bag was sampled in parallel.
  - [Dragonieri2007](https://doi.org/10.1016/j.jaci.2007.05.043) (abstract) uses the same approach.

### Inferences
- **Moving from bags to on-line sensing.** The SpiroNose replaced a 5-minute filtered wash-in and bag collection with direct on-line sensing plus ambient subtraction. That shortened the test and removed bag storage.
- **Flow control.** For a hobby build without a pneumotach, flow is a major confound. A flow sensor or a fixed resistor is worth considering. The SpiroNose relied on coaching instead.

### Gaps
- **Dead space.** No explicit dead-space discard or CO2-gated sampling is described in what I read.
- **Flow-out-of-range rejection.** No automatic rejection rule is published. RespRes2023 mentions removal for "wrong breathing technique" without criteria.

---

## 4. Signal processing and features ("breathprints")

### Takeaway
Pipeline:
1. Eigenfrequency removal (2018).
2. Butterworth low-pass filtering.
3. Ambient subtraction.
4. Detrend and offset removal.
5. Automatic peak detection (Matlab local-maxima finder).

Features per breath sensor:
- **Peak:** the highest peak of the duplicate measurements, normalised to one reference sensor. Sensor 4 ("most sensitive") was used in 2015; sensor 2 ("most stable") from 2018.
- **Peak/breath-hold ratio** (from 2018).

With 14 breath sensors, that gives 28 variables. Later work drops the reference sensor's own normalised peak, which is constant, leaving 13 values. The group deliberately uses sensor-to-sensor ratios rather than absolute values, to cancel inter-array and inter-device gain differences.

### Cited Findings
- **2015 peak features.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), verbatim:
  - "Peak values of the sensor signals were detected using an automatic peak detection algorithm implemented in Matlab for both measurements. This algorithm automatically finds the local maxima in a vector (patient signal)."
  - "In order to create exhaled breathprints, the highest sensor peak of both measurements for each sensor signal was selected and normalized with respect to the most sensitive sensor (range: 1–30 ppm) with the highest corrected sensor values, sensor 4. The study focused on sensor-to-sensor ratios rather than absolute sensor values, to minimize inter-array differences."
- **Ratios and flow.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), Results: absolute values tracked flow, but "absolute sensor values were not significantly influenced by the expiratory flow rate (p > 0.5)" within the tested range. Ratios S2/S4 and S3/S4 are examined against flow (text fragmentary in extraction). Ratio features were explicitly adopted to suppress such effects.
- **2018 features.** [ERJ2018 supplement](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf), verbatim:
  - "The highest sensor peak of both measurements for each sensor signal was selected and normalized with respect to the most stable sensor, sensor 2, to minimize the inter-array differences. Finally, ratios between the sensor peak and the breath hold (BH) point were calculated and used as extra variable within the exhaled breath analysis (Figure S4.1)."
  - "Both variables have discriminative power. There is a relationship between both variables, however, the peak/BH ratio is influenced to a larger extend by the sensor signal obtained during the previous 5 tidal breaths."
- **Later papers.**
  - [Chest2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10635840/): "Signal processing included signal detrending, filtering, ambient air correction, automatic peak detection"; variables are "the highest sensor peak normalized to the most stable sensor, sensor 2," and "the ratio between the sensor peak and the breath hold point."
  - [RespRes2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10626662/): "the peak value and the ratio between peak value and breath hold"; the most stable sensor's peak is excluded, "resulting in 13 values per measurement."
  - [BMC2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10117233/): "each measurement generated 13 principal components" (sic, as reported).
- **Data-quality checks.** [RespRes2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10626662/): measurements removed for "wrong breathing technique or unstable ambient air." Outliers defined by Q1/Q3 ± 1.5 × IQR, with sensitivity analysis excluding them.
- **Drift handling.** [Thesis2022 Ch. 8](https://pure.uva.nl/ws/files/86066334/Chapter_8.pdf): "Processed sensor values that were corrected for ambient VOCs showed no sensor drift during the different studies using this QC gas." Also: "Because sensor drift is not entirely deterministic, it is challenging to separate drift from noise."
  - No algorithmic drift compensation (e.g. component correction) is described beyond detrending and ratios.
  - Ch. 8 also shows 48 months of daily single-subject data smoothed "by using a moving average filter," with "changes in the ratios between the various sensors" visible.
- **Predecessor processing (Cyranose).** [Lazar2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC3230982/): sensor value = "the relative change in electrical resistance"; "Savitzky-Golay filtering and baseline correction"; "the first measurement was disregarded at each session (first sniff effect)."

### Inferences
- **The feature set is very compact.** It is about 2 scalars per sensor, with no full curve-shape descriptors such as rise time or area. Its strength comes from a standardised manoeuvre that makes the peak and breath-hold landmarks comparable across subjects.
- **Transfer to a BME688 build.** The analogous approach is to anchor features to manoeuvre events (e.g. end of breath-hold, end of exhalation) and use ratios to one stable heater step or sensor.

### Gaps
- **Peak-finder details.** Exact parameters (e.g. Matlab findpeaks prominence) and how the breath-hold point is timed are not given. The pneumotach timing is probably used, but this is UNVERIFIED.
- **Current pipeline.** Whether BreathBase's current pipeline extracts more features is not found.

---

## 5. Classifiers and statistics

### Takeaway
The house standard, from Cyranose work through the SpiroNose, is:
- PCA, retaining components with eigenvalue >1 (Kaiser criterion).
- Univariate tests (ANOVA or t-tests) on PCs to pick discriminative components, validated by bootstrap.
- Linear (canonical) discriminant analysis with leave-one-out cross-validation, plus ROC.
- From 2018, a random 2:1 train/validation split.

PCs are fitted on the training set only (ERJ2018). Later studies add PLS-DA, gradient boosting, adaptive LASSO, sPLS-DA, and random forest with nested CV and hyperparameter optimisation. Hyperparameter values are generally not reported.

### Cited Findings
- **2015 statistics.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), verbatim:
  - "Pre-processed exhaled breath data were restructured by PCA from the original 12 sensors monitoring exhaled breath (three sensor arrays of four MOS sensors) to four principal components according the Kaiser criterion [24]. The obtained PCA factors were used to perform a univariate ANOVA analysis to select the principal components that were discriminative between groups. Breathprints were internally validated by multiple iterations of bootstrap."
  - "Subsequently, linear canonical discriminant analysis was performed ... Cross-validation using the leave-one-out method was used to calculate the cross-validated accuracy value (CVV, %)."
  - Software: Matlab 2014 and SPSS 20.
  - Results: cross-validated accuracy 78–88% across group pairs (abstract).
- **2018 statistics.** [ERJ2018](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf):
  - The 28 variables were reduced "to 4 PCs that captured 91.2% of the variance." "PCs were constructed for all subjects (training and validation set), based on eNose data from subjects within the training set."
  - Unsupervised analysis: Ward hierarchical clustering with SIMPROF, repeated 10 times on 70% subsamples.
  - Supervised analysis: stepwise multiple linear regression.
  - Validation set "half the size of the training set," citing Broadhurst & Kell 2006.
- **Chest2023.** [Chest2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10635840/):
  - Kaiser criterion; random 2:1 split; t-tests "validated internally by 1,000 bootstrap iterations"; LDA with LOOCV; ROC.
  - Plus "gradient boosting machine, adaptive LASSO, and sparse PLS-DA." Hyperparameters were not reported.
- **Other ILD and post-COVID papers.**
  - [Chest2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8941620/): PLS-DA (mixOmics) with GLM prediction and ROC; 2:1 split.
  - [RespRes2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10626662/): PLS-DA with 1–2 components "to avoid model overfitting."
  - [BMC2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10117233/): PCA (scree plus Kaiser), then LDA with LOOCV.
- **Classifier comparison.** [JBR2023-sarc](https://doi.org/10.1088/1752-7163/acf1bf) (abstract): "Various methods of dimensionality reduction and multiple hyperparameter optimised classifiers were tested"; "Nested cross-validation was applied." "A classification model with feature selection and random forest (RF) classifier showed the highest accuracy" (87.1% accuracy, AUC 91.2%; n = 224 sarcoidosis vs 317 other ILD).
- **The group's own caution about overfitting.** [Thesis2022 Ch. 8](https://pure.uva.nl/ws/files/86066334/Chapter_8.pdf): "In many studies, including most of our own ... conclusions are based on a single classification model. This approach can be prone to bias and overfitting." Also: "when selected variables from the same sensor overlap in information as is the case for the SpiroNose, machine learning models will be more likely to overfit."
- **External validation (lung cancer).** [AnnOnc2025](https://doi.org/10.1016/j.annonc.2025.03.013) (abstract): two Dutch sites. The "original eNose model" achieved ROC-AUC 0.92, and a new model was trained and validated "targeting 95% sensitivity."
- **Cyranose-era methods review.** [Leopold2015](https://doi.org/10.1088/1752-7155/9/4/046002) (abstract): a review of 46 eNose studies' dimension-reduction and classification approaches, noting reliance on LOOCV as internal validation.

### Inferences
- **Low model capacity by design.** It is a direct response to small n and highly collinear features. For a BME688 build with many heater-step features, the same discipline applies: dimensionality reduction fit on training data only, held-out validation, and few components.

### Gaps
- **Hyperparameters and feature selection.** Values and grids for GBM, LASSO, sPLS-DA and RF are not available (JBR2023-sarc full text not read).
- **AnnOnc2025 model.** The algorithm and whether the original model was locked are not confirmed (abstract only).

---

## 6. Sensor selection (how the 7 types were chosen)

### Takeaway
I found no published, data-driven description of how the 7 sensor types were selected. The claim that they are "the sensors with the highest ability to distinguish between different (lung) diseases" appears only on the Breathomix product page. Whether selection was done independently of the validation data is not found. The only published selection rationale is the 2015 choice of Figaro MOS sensors for long-term stability, citing a literature review.

### Cited Findings
- **Manufacturer claim.** [Breathomix](https://www.breathomix.com/?p=554): "The selection of the SpiroNose® sensors was guided by extensive research," "selecting only the sensors with the highest ability to distinguish between different (lung diseases and their subtypes." No data or reference is given.
- **2015 rationale.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf): "The choice of Figaro-type MOS sensors was based on their good long-term performance and stability [20]" (Romain & Nicolas 2010 review). Discussion: "with this small number of MOS sensors comparable accuracy levels were achieved ... increasing the sensor array number does not necessarily improve eNose classification performance as that could amplify the noise and/or generate redundancy."
- **Stability rationale for the normalising sensor.** [ERJ2018](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf): sensor 2 was chosen as "the most stable sensor." No criterion is given for "most stable."
- **Prototype progression.** [Breathomix timeline](https://breathomix.com/?p=1853): Prototype I tested "the most optimal position of the sensors" and ambient influence. This is a manufacturer page with no data.

### Inferences
- **The selection claim is not independent evidence.** It should be treated as UNVERIFIED marketing. Any selection done on clinical data that later served as validation would bias performance estimates, but there is no evidence either way.

### Gaps
- **Published selection study.** None found (Brinkman 2019 thesis searched by keyword only; patents not searched).

---

## 7. Earlier devices, cross-device/site comparisons, drift, calibration and QC

### Takeaway
Predecessors:
- **Cyranose 320:** 32 carbon black–polymer chemiresistors, with VOC-filtered 5-minute tidal wash-in and Tedlar-bag sampling.
- **U-BIOPRED composite platform:** Cyranose plus Comon Invent MOS (8 sensors) plus a Tor Vergata QMB and an Owlstone FAIMS, used on thermally desorbed Tenax samples.

SpiroNose QC: a daily flush with standard pulmonary-diffusion test gas (0.3% each acetylene, CO and CH4 in air). This was used to verify the absence of drift and to estimate signal-to-noise (effect size 5.2–7.4× sensor variability).

Cross-device consistency is attributed to:
- the ambient correction and ratio normalisation;
- Breathomix's "cloud-based calibration," which is undocumented in what I read.

No published method for calibrating many SpiroNose units to each other was found.

### Cited Findings
- **QC gas protocol.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf), verbatim: "SpiroNose sensor stability was verified using a test gas (Lindegas, for the measurement of pulmonary diffusion capacity) as quality control (QC) gas before every session. This QC gas is a standard mixture of acetylene (0.300 ± 0.015%), carbon monoxide (0.300 ± 0.015%), methane (0.300 ± 0.015%), oxygen (20.7 ± 1.0%) and nitrogen ... the gas mixture was flushed for 5 s with a mean flow of 3 L s−1 through the SpiroNose."
  - The authors concede that it "would have been most optimal to determine sensor stability with a flow <0.4 L s−1."
- **QC continued in 2018.** [ERJ2018](https://pure.uva.nl/ws/files/86066326/Chapter_4.pdf): stability was verified "using the standard test gas for pulmonary diffusion capacity measurements as quality control gas every morning before patient measurements."
- **QC results and limits.** [Thesis2022 Ch. 8](https://pure.uva.nl/ws/files/86066334/Chapter_8.pdf):
  - QC-gas and breath data were processed with the same algorithm, giving a "5.2 to 7.4-fold higher effect size indicating a good signal-to-noise ratio."
  - "the next step should be the creation of a specific QC gas that mimics the exhaled breath."
  - "there have been doubts as to whether the implementation of eNose technology is hampered by limited sensor stability, the inability to calibrate devices simultaneously, and the difficulty of mass-producing identical sensors."
- **Portability claim.** [Thesis2022 Ch. 8](https://pure.uva.nl/ws/files/86066334/Chapter_8.pdf), conclusions: "advanced signal processing, including a new background correction method, ensures sufficient reproducibility and portability of algorithms between devices." The evidence cited is chapter 3 (JBR2015), which compared arrays within one device and between two sites.
- **Repeatability and site comparison.** [JBR2015](https://iopscience.iop.org/article/10.1088/1752-7155/9/4/046001/pdf): within-day and between-day (2-week) repeatability was assessed in 10 asthma patients and 10 controls. Asthma breathprints were compared between two sites (AMC vs MST) "to investigate whether the used data sampling and analysis techniques are appropriate for multi-center purposes."
- **Manufacturer claims.**
  - [Breathomix timeline](https://breathomix.com/?p=1853): Prototype II's study confirmed "transferability of algorithms between devices." Current work focuses on "optimizing calibration methods."
  - [Breathomix product page](https://www.breathomix.com/?p=554): "The SpiroNose® employs cloud-based calibration to ensure consistent, standardized data across all devices," correcting "for sensor variability." No method is given; UNVERIFIED.
- **Cyranose 320 details.** [Lazar2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC3230982/): "32 carbon black polymer sensors"; the same unit was used throughout; first sniff discarded; Savitzky-Golay plus baseline correction; PCA (4 factors, 95.6% variance). A control study found "no significant temporal change" over repeated analyses.
- **U-BIOPRED composite platform.** [Brinkman2019](https://pure.uva.nl/ws/files/42598554/Thesis.pdf): Tenax-sampled breath was thermally desorbed into Tedlar bags with N2 and analysed by "1) Cyranose C320 using carbon black-polymer sensors ... 2) Tor Vergata eNose using quartz crystal microbalances (QMB) covered with metalloporphyrins ... 3) Common Invent eNose using metal oxide semiconductor sensors ... 4) Owlstone Lonestar." The combined output was 158 signals ("Comon Invent = 8, Cyranose = 32, Lonestar = 110, Tor Vegata = 8"). In one chapter "two [Cyranose] instruments were included."
- **Multi-site lung cancer validation.** [AnnOnc2025](https://doi.org/10.1016/j.annonc.2025.03.013): two sites; a prior model was applied to a new cohort and retrained. Device-to-device analysis is not stated in the abstract.

### Inferences
- **The group's calibration strategy is mostly differential.** It relies on two things. First, subtraction of a co-located reference array of the same sensor types. Second, normalisation of features to one stable sensor, which turns gain differences into ratios. The diffusion gas checks sensor function but is not used to compute per-device correction factors in the published methods.
- **Fit for a BME688.** This approach suits a BME688 build: a second BME688 on ambient air, and ratios to a stable heater step.

### Gaps
- **Unit-to-unit calibration.** No published method for calibrating many SpiroNose units to each other (transfer standards, direct standardisation, etc.) was found. "Cloud-based calibration" is undocumented.
- **Sensor replacement.** Sensor replacement intervals and lifetime are not found.
- **Not read:**
  - the de Vries thesis Ch. 2 and Ch. 7 methods in detail;
  - the Brinkman thesis (keyword search only);
  - Fens 2009/2011 full texts;
  - the Moor 2020 ERJ ILD paper (paywalled, DOI 10.1183/13993003.02042-2020);
  - the de Vries 2019 *Ann Oncol* anti-PD-1 paper (DOI 10.1093/annonc/mdz279, subscription).
  - These could hold more device or calibration detail.
- **Patents.** Not searched.
