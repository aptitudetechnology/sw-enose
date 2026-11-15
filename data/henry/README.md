# Henry's law constants: six odorants, transcribed 15 Nov 2026

`sander_v5_subset.csv` holds Henry's law solubility constants for the six odorants the demos use.
Unlike everything else under `data/`, this file is **in the repo**: it is six hand-transcribed values
with their attributions, not a bulk download.

## Source

R. Sander, *Compilation of Henry's law constants (version 5.0.0) for water as solvent*, Atmospheric
Chemistry and Physics **23**, 10901–12440 (2023), doi:10.5194/acp-23-10901-2023. Read through the
per-compound pages at `https://henrys-law.org/henry/casrn/<CAS>` on 15 Nov 2026. ACP publishes under
CC-BY 4.0; the six values are reproduced with attribution, and each row's `source` column names the
original study behind it.

Note the version: the site states that Sander's 2015 compilation is **obsolete** and superseded by
version 5.0.0 (2023). An earlier draft of this repo cited the 2015 paper. Do not reintroduce it.

## Quantity and units

`h_cp_mol_per_m3_Pa` is H^cp, the *solubility* form of the constant — aqueous concentration divided
by gas partial pressure — in mol/(m³·Pa), at the reference temperature 298.15 K. That is the form the
compilation tabulates, so no unit conversion was applied to any value here. `sw_enose/air.py` has
`h_cp_from_atm_m3_per_mol`, `h_cp_from_m_per_atm` and `h_cp_from_dimensionless` for sources that use
the other conventions.

`temp_dep_K` follows `air.TEMP_DEP_CONVENTION`: d ln(H^cp) / d(1/T) in kelvin, **positive meaning
less soluble when warmer**. The compilation heads this column `d ln Hs cp / d (1/T)` with no minus
sign and prints positive values, and taking them at face value gives the physically right direction
for the exothermic dissolution these compounds undergo. The source does not state the convention
explicitly, so this is reasoned, not quoted. Blank means no coefficient is published, which the
loader turns into no correction at all — so those compounds are effectively treated as if their
298.15 K value held at body temperature, which it does not.

## How a value was chosen

1. Prefer **measured** rows (the compilation's type `M`). Where several exist, take their
   **geometric mean**, matching how `sw_enose/m2or.py` combines repeated EC50 measurements.
2. With no measured rows, fall back to vapour-pressure/solubility (`V`), then QSPR (`Q`), and say so
   in the row's `source`.
3. `h_cp_low` and `h_cp_high` span **every** listed type, including estimates, so the disagreement
   between labs stays visible rather than being hidden behind a single number. Butanoic acid spans a
   factor of about 46 this way.

No row in the compilation is flagged recommended or preferred; rows are merely sorted by reliability.
The choice above is therefore ours, and is the main thing to challenge if a number here looks wrong.

## What is weak

- **Octanethiol** and **L-carvone** have no measured value at all — only estimates, one of them built
  on a water solubility that was itself calculated from a boiling point. Any conclusion resting on
  these two rests on a model, not a measurement.
- **Cinnamaldehyde** has no measured value either, and the source names no isomer.
- **Carvone's** stereochemistry is unspecified in the source while the receptor data is for
  L-carvone. Enantiomers should partition alike, so this is a nominal rather than a real mismatch.
- Only **butanoic acid** and **cinnamaldehyde** have a temperature coefficient. For the other four,
  the body-temperature correction is silently skipped.
- All of it is air-to-**water**. The receptor sits in mucus. See `AIR_TO_MUCUS` in `sw_enose/air.py`.
