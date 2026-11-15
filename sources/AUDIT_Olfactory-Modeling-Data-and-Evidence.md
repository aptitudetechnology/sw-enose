# Audit of `Olfactory-Modeling-Data-and-Evidence.md` (15 Nov 2026)

Deep-research result for `research_prompts/01_receptors_and_biomimetic_stages.md`.
I checked the identifiers against PubMed and Crossref and checked two key numbers against the abstracts.
I did not read the full texts myself.

## Identifiers checked (PubMed esummary; title, first author, year, journal, DOI all match)

| PMID | Paper | Note |
|---|---|---|
| 37870437 | Lalis M, M2OR, Nucleic Acids Res | PubMed year 2024 (issue), report says 2023 (online). Abstract confirms "75,050 bioassay experiments for 51 395 distinct OR-molecule pairs". |
| 23024602 | Niimura Y, Curr Genomics 2012 | Matches. |
| 31000595 | Singh V, PNAS 2019 | Abstract confirms "to within 15%" for mixtures of up to 12 odorants. |
| 20435004 | Olsen SR, Neuron 2010 | Matches. |
| 29123069 | Dasgupta S, Science 2017 | Matches. |
| 36922591 | Billesbølle CB, Nature 2023 | Real; report listed it as UNVERIFIED metadata. Content still not read. |
| 32620767 | Zak JD, Nat Commun 2020 | Real; title "Antagonistic odor interactions in olfactory sensory neurons are widespread in freely breathing mice". Content not read. |
| DOI 10.64898/2026.03.07.710286 | Crossref: "Computed atlas of the human GPCR-G protein signaling complexes", openRxiv | Real preprint, not peer reviewed. |

## Equations (decoded from the embedded images)

- Singh 2019: F({c_i}) = F_max · Σ(e_i c_i / EC50_i) / (1 + Σ c_i / EC50_i). This is the model already in `bio.py` `receptor_activation` with hill_n = 1 and F_max = 1.
- Olsen 2010 (as shown): PN = R_max · ORN^1.5 / (ORN^1.5 + σ^1.5). This is the private-odour form only. The report does not give the cross-glomerular (lateral) term or fitted values of R_max and σ.

## Problems in the report

1. **Error:** section 7 says *Drosophila* receptors are "homotetrameric ion channels". The homotetramer in the cited structure (MhOR5) is from a jumping bristletail. *Drosophila* odorant receptors are, to my knowledge, heteromers with the co-receptor Orco. Not checked against a source here; do not repeat the report's sentence.
2. **Stretch:** "divisive normalization has exponent 1.5" presents a curve-fitting exponent as the strength of normalisation. The lateral-inhibition strength was not reported.
3. **Stage 5 numbers are from a modelling paper** (Dasgupta 2017), which cites anatomy. "50 PNs" is the model's simplification. Use the numbers as "as used in Dasgupta 2017", not as measurements.
4. **Coverage 5.4%** is the report's own arithmetic across 11 species; a crude figure.
5. **Not found, and important:** the fraction of human receptors with a known agonist. The one lead (Saito 2009: 4% of human and 23% of mouse receptors responded to at least one of 93 odorants, quoted via a review) is UNVERIFIED and worth reading at source.
6. Stage 2 convergence ratios and Stage 3 adaptation time constants: not found. Mammalian piriform sparsity: not found.

## What this means for sw-enose

| Stage | Status now | Parameters we may use |
|---|---|---|
| 1 Competitive binding | ESTABLISHED for 12 of 15 receptors in heterologous cells (Singh 2019) | Model form; real EC50 and efficacy from M2OR / Singh data once downloaded and read |
| 2 Convergence | Biology textbook-level; ratios not verified | Invented; keep marked |
| 3 Adaptation | Phenomenon accepted; constants not found | Invented; keep marked |
| 4 Normalisation | ESTABLISHED in the fruit-fly antennal lobe (Olsen 2010); our formula differs | Exponent 1.5 (fit); R_max, σ and lateral weight invented |
| 5 Sparse expansion | Modelling paper (Dasgupta 2017) citing fly anatomy | 2,000 cells, ~6 inputs each, top 5% (already our defaults) |

Mixing mammalian receptors with fly circuit numbers is a cross-species model and must be labelled as such.

Next reading, in order: M2OR data files and licence; Singh 2019 deposited data; Saito 2009 (deorphanisation rate); Zak 2020 (antagonism in vivo); Olsen 2010 full model with the lateral term.
