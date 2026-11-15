# Prompt 3: Physical chemistry and human thresholds for the C3–C10 fatty acids

Paste everything below the line into a deep-research tool. Use the strongest model you have.

---

## Role

You are a careful analyst in physical chemistry and human olfactory psychophysics. The aim is to collect sourced, measured values for a computational model, not to argue for any conclusion. Report values as printed, with units, and say when something was not found.

## Context

We are building an open-source, software-only model of an olfactory system. It converts an odorant's concentration in air (ppb) to its concentration in the liquid at the receptor using equilibrium Henry's-law partitioning, with constants from R. Sander, *Compilation of Henry's law constants (version 5.0.0) for water as solvent*, Atmos. Chem. Phys. 23, 10901–12440 (2023). It then predicts receptor activation from measured receptor EC50 values. We test it against **measured human odour detection thresholds** for the homologous series of straight-chain saturated carboxylic acids from propanoic (C3) to decanoic (C10) acid.

Three gaps limit that test:

1. **Air–water vs air–mucus.** Scott, Sherrill, Jiang & Zhao, J Neurosci 2014 (PMC3913860), used a correction for mucus that depends on the octanol–water partition coefficient. We need measured log Kow values to apply it.
2. **Ionisation.** These are weak acids. At mucus pH the ionised form adds to the dissolved total, so an effective Henry's constant depends on pKa and mucus pH.
3. **Missing measurements.** We have analytically verified human thresholds only for butanoic, hexanoic and octanoic acid (Cometto-Muñiz & Abraham, Exp Brain Res 2010, PMC2964470). The Henry's law compilation has no measured value for octanoic, nonanoic or decanoic acid, only estimates, and octanoic's estimates span a factor of 73.

"Not found in these searches" means a gap in the search, not evidence that something doesn't exist.

## Find

1. **Measured octanol–water partition coefficients (log Kow)** for C3–C10 straight-chain acids, from primary measurements or authoritative compilations (for example Hansch, Leo & Hoekman 1995, or Sangster). Distinguish measured from calculated values.
2. **Measured pKa in water** (about 25 °C) for C3–C10, with source. Note any measured temperature dependence.
3. **pH of human nasal mucus and airway surface liquid**, especially in or near the **olfactory region** as opposed to respiratory mucosa, from primary studies: value, method, subjects.
4. **The exact form of Scott et al. 2014's mucus correction.** Quote the equation verbatim, define every symbol as the paper does (air/mucus vs mucus/air, dimensionless or not, log base), say what data it was calibrated on, and quote anything about ionisable odorants or pH. Identify the original source if it comes from Kurtz et al. 2004 or elsewhere.
5. **Measured air–water partition / Henry's law constants for octanoic (C8), nonanoic (C9) and decanoic (C10) acid,** from any primary measurement: the value, temperature, method and source. These are the most important gap.
6. **Measured human odour detection thresholds** for propanoic (C3), pentanoic (C5), heptanoic (C7), nonanoic (C9) and decanoic (C10) acid, preferably with vapour concentrations verified analytically (for example by gas chromatography). Include Wise, Miyazawa, Gallagher & Preti, Chem Senses 2007 (PMID 17488748), which measured C2–C8 by SPME-GC-MS: extract its actual threshold values. Give the threshold measure used (for example 50% detection above chance), the spread, the number of subjects and the method.
7. Any study that directly relates human detection thresholds of carboxylic acids to their air–mucus partitioning or ionisation.

## Rules

1. Rank sources by strength of evidence: primary measurements and authoritative data compilations first, then reviews, then everything else. **Anything that carries a conclusion needs a PMID, a DOI or, for databases and datasets, a stable URL, and you must have opened it.** Say whether you read the full text or only the abstract.
2. Copy titles, authors, year and journal from the record, never from memory. Quote the sentence or table row for each number, with its units, **as printed; do not convert units**. If you can't confirm a value, mark it UNVERIFIED and leave it out of your conclusions.
3. Keep measured and estimated values apart, and say which is which. Do not average values from different sources.
4. **Do not stretch.** If you found nothing for an acid, write "not found in these searches".

## Output

1. **Direct answer** (100 words): which gaps can now be filled with measured values, and which remain open.
2. **Partition and ionisation table:** acid | log Kow (measured) | source | pKa | source | measured Henry's law constant (C8–C10 only) | units | temperature | source.
3. **Mucus pH table:** value | region (olfactory / respiratory / unspecified) | method | subjects | source.
4. **Scott et al. 2014 correction:** the equation verbatim, symbol definitions, calibration data, and any statement on ionisable odorants.
5. **Threshold table:** acid | threshold as printed | units | measure | spread | n subjects | method (analytically verified?) | source.
6. **Verification table:** identifier | title | first author | year | full text or abstract.
