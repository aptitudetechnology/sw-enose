# Audit of `reports/Carboxylic-Acid-Olfactory-Model-Parameters.md` (16 Nov 2026)

Deep-research result for `research_prompts/03_acid_partitioning_and_thresholds.md`, run on Gemini
by the project owner. By its own account it closed **no** gap with a verified value: most leads were
secondary tables, truncated excerpts or failed extractions. Nothing here was re-fetched (an earlier
automated search for these values in this project was stopped by a safeguard).

## What it returned, and how it is used

| Item | Status in the report | Used? |
|---|---|---|
| pKa C3–C10: 4.80–4.90 | UNVERIFIED, two secondary tables, consistent | Only for an analytic bound: if all pKa lie within 0.1 units, ionisation changes the threshold benchmark's spread by at most ~0.1 log units at ANY mucus pH. No pKa value enters the model. |
| log Kow octanoic 3.05, decanoic 4.09 | UNVERIFIED (Sangster 1989 excerpt) | Only to show the Scott-implied water value for C8; not used in the model |
| Scott et al. 2014 table, log10 air/mucus β: hexanoic −5.0868, heptanoic −5.4656, octanoic −5.7213, nonanoic −5.693 | Read from the opened paper, but table values not re-checked here | Yes, for a sensitivity run of the threshold benchmark only; labelled UNVERIFIED |
| Scott's β formula | Report says not captured | Already in this repo from an earlier full-text read: log β = log β_water − (log P − 1) × 0.524 (research_notes/.../air_mucus_models.md) |
| Wise et al. 2007 | Opened: tested C2, C4, C6, C8 only; reports psychometric functions, no single thresholds | No new thresholds |
| Human nasal / olfactory-cleft mucus pH | Not found (one extraction failed) | Not needed for the spread test (see pKa row) |
| Measured Henry constants C8–C10 | Not found | Gap remains |

## What the sensitivity run showed (see README, "Human detection thresholds")

Using Scott's air/mucus values for C6 and C8 (C4 has none; left on air–water, assuming its log P
near 1 makes the correction small) widens the spread of activation at threshold from 0.85 to 1.40
log units and breaks the C4/C6 agreement (0.08 → 0.73). The run mixes sources (Scott's values rest
on EPA EPI Suite; ours on Sander), so it is not a clean test either. The conclusion drawn is that the
benchmark is limited by the partition step: reasonable treatments move it by 0.5–1.2 log units, as
much as the effect it measures.
