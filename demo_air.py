"""Air to mucus: what would have to be in the air for a measured EC50 to be reached?

This joins the two halves of the project that did not meet before: receptor EC50s measured in
MICROMOLAR IN LIQUID (M2OR, real) and odorant concentrations in AIR in ppb (what any real
instrument reports). MODELLED throughout.

The Henry's law constant of each compound is a measurement this repo does not have yet, so instead
of inventing one per odorant the demo sweeps a band covering the range volatile organics occupy.
The conclusion below holds across the whole band, which is why it is worth printing.
"""
import os
import numpy as np

from sw_enose import BiomimeticNose
from sw_enose.air import (AIR_TO_MUCUS, HenryTable, T_BODY, air_molar, air_to_liquid,
                          concentration_vector_from_air, ppb_for_liquid)
from sw_enose.m2or import build_params

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
ODOURS = ("butanoic acid", "isovaleric acid", "Dimethyl trisulfide", "Octanethiol",
          "cinnamaldehyde", "L-Carvone")
# mol/(m^3 Pa): poorly soluble and volatile, middling, very soluble. Bracket, not chemistry.
BAND = (1e-4, 1e-2, 1e0)

p = build_params(CSV, ODOURS)
print("receptors:", p.provenance, "\n")

print("What the conversion leaves out (every number below is therefore a ceiling):")
for key, (what, status) in AIR_TO_MUCUS.items():
    print(f"  {key}: {what}\n      {status}")

print(f"\nThe gas-law step alone, at {T_BODY:.2f} K: 1 ppb of anything is "
      f"{air_molar(1.0):.3g} uM of air. Receptor EC50s here are tens of uM, in liquid.")

print("\nAir concentration needed to put the median measured EC50 at the receptor")
print("(equilibrium, mucus assumed to behave as water; FLOOR, the real figure would be higher):\n")
print(f"  {'odorant':22s} {'agonists':>8s} {'median EC50':>12s} " +
      " ".join(f"{'H=' + format(h, '.0e'):>14s}" for h in BAND))
for j, o in enumerate(ODOURS):
    ec = p.affinity[p.efficacy[:, j] > 0, j]
    med = float(np.median(ec))
    cells = []
    for h in BAND:
        t = HenryTable((o,), np.array([h]), "synthetic:volatility bracket")
        ppb = ppb_for_liquid(t, o, med)
        cells.append(f"{ppb / 1e3:,.0f} ppm" if ppb >= 1e3 else f"{ppb:,.2f} ppb")
    print(f"  {o:22s} {len(ec):8d} {med:9.1f} uM " + " ".join(f"{c:>14s}" for c in cells))

print("\nSo: unless an odorant is at the very soluble end, reaching a concentration these assays")
print("call half-maximal needs air concentrations in the ppm range or above. Breath traces are")
print("usually low ppb. The gap is the finding; it comes from the measured EC50s and the gas law,")
print("not from the invented Henry constants, since it survives the whole band.")

print("\nA breath-like mixture at low ppb, pushed through the nose anyway:")
table = HenryTable(ODOURS, np.full(len(ODOURS), 1e-2), "synthetic:one middling constant for all")
nose = BiomimeticNose(p, neuron_noise=0.0, seed=5)
breath_ppb = {"butanoic acid": 20.0, "isovaleric acid": 10.0, "Octanethiol": 2.0}
liquid = air_to_liquid(table, breath_ppb, temp_k=T_BODY)
for o, ppb in breath_ppb.items():
    print(f"  {o:22s} {ppb:6.1f} ppb -> {liquid[o]:.3e} uM in liquid")
v = concentration_vector_from_air(p, table, breath_ppb, temp_k=T_BODY)
act = nose.receptor_activation(v)
print(f"  peak receptor activation {act.max():.3e} of 1.0 across {len(act)} receptors "
      f"-- indistinguishable from nothing")
print(f"  for comparison, the same odorants at the liquid concentrations demo_mixture.py uses: "
      f"{nose.receptor_activation(np.where(v > 0, 100.0, 0.0)).max():.3f}")

print("""
What that does and does not mean. It is NOT evidence that a nose cannot smell these gases at ppb:
people plainly do smell some odorants at very low air concentrations. It means the chain assembled
here -- cultured-cell EC50s, plus equilibrium air-water partitioning -- does not reach the receptor
sensitivity real olfaction shows. Something in it is wrong or missing: candidates are the assays
reporting far higher EC50s than receptors in a nose need, transport by odorant-binding proteins,
accumulation in mucus away from equilibrium, and amplification in the stages after binding. Which
of those it is, this repo cannot say. Until it can, the nose should not be fed real ppb figures
and expected to behave like a nose.""")

print("\nAn odorant with no Henry constant is refused, not guessed:")
partial = HenryTable(("butanoic acid", "Octanethiol"), np.array([1e-2, np.nan]),
                     "synthetic:one value deliberately absent")
try:
    air_to_liquid(partial, {"Octanethiol": 5.0})
except KeyError as e:
    print("  ", e.args[0])
