# Prompt 1: Real olfactory receptors and the biology behind a biomimetic software nose

Paste everything below the line into a deep-research tool. Use the strongest model you have.

---

## Role

You are a careful analyst in olfactory neuroscience and receptor pharmacology. The goal is to find out what real data exist to build a software model of a biological nose, and how well the biology it copies is established, not to promote any device or method. Report evidence against as readily as evidence for.

## Context

We are building an open-source, software-only model of a nose. It has a virtual array of receptors whose signal passes through five stages copied from animal olfaction: (1) receptor binding with competition in mixtures, (2) convergence of same-type receptor neurons onto glomeruli, (3) adaptation to a constant odour, (4) divisive normalisation across glomeruli, (5) a sparse random expansion (insect mushroom body, mammalian piriform cortex). The processing works on invented parameters. **We now need real receptors and real response data, and primary sources for each stage.** "Not found in these searches" means a gap in the search, not evidence that something doesn't exist.

## Find

1. **Receptor repertoires.** Number of intact olfactory receptor genes and pseudogenes in humans, dogs, mice and the fruit fly, the databases that hold the sequences (for example NCBI, Ensembl, HORDE), and their licences.
2. **Odorant–receptor response data.** Public datasets that link specific receptors to specific odorants with measured responses: what fraction of human receptors have at least one known agonist; for each dataset the number of receptors and odorants, the assay type (for example luciferase reporter in HEK293 cells, calcium imaging, in-vivo recording), whether concentration–response curves (EC50, efficacy) or only yes/no are given, known reproducibility problems, the licence, and how to download it.
3. **Predicting responses.** Methods that predict which odorants activate a receptor from sequence or structure (machine learning, docking, solved structures such as cryo-EM): accuracy on held-out receptors and odorants, not just on training data, and how often predictions were tested in the lab.
4. **Mixtures.** Evidence on how receptors respond to mixtures: competitive binding, antagonism, suppression or enhancement, and whether a simple competitive-binding model fits.
5. **The five stages.** For each stage, the primary studies that show it, the species, and any measured parameters (for example convergence ratios, adaptation time constants, normalisation strength, the fraction of mushroom-body or piriform cells active per odour). We believe these from memory and need them checked: Olsen, Bhandawat & Wilson on normalisation in the fruit-fly antennal lobe (about 2010); Dasgupta, Stevens & Navlakha on the fly olfactory circuit as a similarity-search algorithm (Science, 2017).
6. **Biohybrid and biomimetic noses.** Devices that use real olfactory receptors (cells, nanodiscs, receptor-coated transistors) or insect antennae, and software models of the olfactory system used for gas sensing: what they detected, in what setting, and with what validation in people or real-world samples.
7. **The best case against** building a nose model from receptor data: missing data, poor reproducibility, species differences, or reasons the biology may not transfer to software.

## Rules

1. Rank sources by strength of evidence: systematic reviews, consensus statements and large curated datasets first, then primary experimental studies, then modelling papers, then everything else. **Anything that carries a conclusion needs a PMID, a DOI or, for databases and datasets, a stable URL, and you must have opened it.** Say whether you read the full text or only the abstract. Lower-ranked sources are leads only.
2. Copy titles, authors, year and journal from the record, never from memory. Quote the sentence for each key number. If you can't, mark it UNVERIFIED and leave it out of your conclusions.
3. State the species, the assay and whether results were in cells, tissue or living animals. Company pages, press releases, blogs and AI summaries are leads, never evidence.
4. **Do not stretch.** A result in one species, one assay or one lab is not general. If you found nothing, write "not found in these searches".

## Output

1. **Direct answer** (150 words): can a software nose be built from real receptor data today? What is **established**, **plausible** and **untested**, and the strongest argument against.
2. **Repertoire table:** species | intact genes | pseudogenes | database | licence | source.
3. **Dataset table:** dataset | receptors | odorants | assay | concentration–response or yes/no | licence | download URL | known problems | source.
4. **Prediction methods:** method | input | held-out accuracy | lab-tested? | source.
5. **Stage table:** stage | what it does | species | measured parameters (with units) | source (identifier; full text or abstract).
6. **Biohybrid and biomimetic devices:** device | receptor source | target | setting | validation | source.
7. **The case against.**
8. **Verification table:** identifier | title | first author | year | full text or abstract.

Describe the data and the evidence. Do not suggest diagnoses or treatments for any individual.
