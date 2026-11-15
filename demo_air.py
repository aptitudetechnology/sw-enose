"""Air to mucus: what would have to be in the air for a measured EC50 to be reached?

This joins the two halves of the project that did not meet before: receptor EC50s measured in
MICROMOLAR IN LIQUID (M2OR) and odorant concentrations in AIR in ppb (what any real instrument
reports). Both halves are now measured; the chain between them is MODELLED.

CORRECTION. An earlier version of this demo had no real Henry's law constants and swept an invented
band of 1e-4 to 1e0 mol/(m^3 Pa), concluding that reaching a measured EC50 always needs ppm in air.
That was wrong. The real constants for the carboxylic acids are 10 to 50 mol/(m^3 Pa), above the top
of that band, and their EC50s are reached at tens of ppb. The invented band was the error, not the
measurements. What follows uses data/henry/sander_v5_subset.csv.
"""
import os
import numpy as np

from sw_enose import BiomimeticNose
from sw_enose.air import (AIR_TO_MUCUS, T_BODY, T_REF, air_molar, air_to_liquid,
                          concentration_vector_from_air, load_henry_csv, ppb_for_liquid,
                          ppb_for_liquid_at)
from sw_enose.m2or import build_params

HERE = os.path.dirname(__file__)
CSV = os.path.join(HERE, "data/m2or/repo/M2OR_20230428.csv")
HENRY = os.path.join(HERE, "data/henry/sander_v5_subset.csv")
ODOURS = ("butanoic acid", "isovaleric acid", "Dimethyl trisulfide", "Octanethiol",
          "cinnamaldehyde", "L-Carvone")

p = build_params(CSV, ODOURS)
h = load_henry_csv(HENRY, "measured:Sander, Compilation of Henry's law constants v5.0.0, "
                          "Atmos. Chem. Phys. 23, 10901-12440 (2023), doi:10.5194/acp-23-10901-2023; "
                          "transcribed per compound, see data/henry/README.md")
print("receptors:", p.provenance)
print("partitioning:", h.provenance, "\n")

print("What the conversion still leaves out (so every number below is a ceiling on the liquid")
print("concentration, and a floor on the air concentration needed):")
for key, (what, status) in AIR_TO_MUCUS.items():
    print(f"  {key}: {what}\n      {status}")

print(f"\nThe gas-law step alone, at {T_BODY:.2f} K: 1 ppb of anything is {air_molar(1.0):.3g} uM of air.")

print("\nAir concentration needed to put the median measured EC50 at the receptor, at body")
print("temperature, assuming mucus behaves as water. The bracket spans every value the")
print("compilation lists for that compound, estimates included.\n")
print(f"  {'odorant':22s} {'H^cp':>8s} {'EC50':>9s} {'ppb needed':>12s}   {'bracket from the published spread':34s}")


def fmt(ppb):
    if ppb >= 1e6:
        return f"{ppb / 1e6:,.1f} parts per thousand"
    return f"{ppb / 1e3:,.1f} ppm" if ppb >= 1e3 else f"{ppb:,.0f} ppb"


rows = {}
for j, o in enumerate(ODOURS):
    ec = float(np.median(p.affinity[p.efficacy[:, j] > 0, j]))
    lo_h, mid_h, hi_h = h.bracket(o, temp_k=T_BODY)
    mid = ppb_for_liquid(h, o, ec, temp_k=T_BODY)
    # a bigger Henry constant means more dissolves, so it needs LESS in the air: the sides swap
    band = ""
    if np.isfinite(lo_h) and np.isfinite(hi_h):
        band = f"{fmt(ppb_for_liquid_at(hi_h, ec))} to {fmt(ppb_for_liquid_at(lo_h, ec))}"
    else:
        band = "no range published (single estimate)"
    rows[o] = (ec, mid)
    print(f"  {o:22s} {mid_h:8.3g} {ec:6.1f}uM {fmt(mid):>12s}   {band:34s}")

print("\nThe compounds split in two, and the split follows water solubility exactly as the physics")
print("says it must:")
soluble = [o for o, (_, ppb) in rows.items() if ppb < 1e3]
stubborn = [o for o, (_, ppb) in rows.items() if ppb >= 1e3]
print(f"  reachable at ppb:  {', '.join(soluble)}")
print(f"  needs ppm or more: {', '.join(stubborn)}")
print("  And note the data quality: two of the three that need ppm (octanethiol, carvone) have no")
print("  measured Henry constant at all, only estimates. Dimethyl trisulfide's is measured, so that")
print("  one is a real discrepancy; the other two may partly be artefacts of an estimated constant.")

print(f"\nTemperature matters where a coefficient exists. Butanoic acid, 298.15 K vs {T_BODY:.2f} K:")
for t in (T_REF, T_BODY):
    print(f"  {t:7.2f} K: H^cp {h.h_cp_at('butanoic acid', t):7.2f}, "
          f"EC50 reached at {fmt(ppb_for_liquid(h, 'butanoic acid', rows['butanoic acid'][0], temp_k=t))}")
print("  Warmer means less soluble, so a warm nose needs more in the air. Four of the six compounds")
print("  have no published coefficient, so for them this correction is silently skipped.")

print("\nA breath-like mixture at low ppb, through the whole nose:")
nose = BiomimeticNose(p, neuron_noise=0.0, seed=5)
breath_ppb = {"butanoic acid": 20.0, "isovaleric acid": 10.0, "Octanethiol": 2.0}
liquid = air_to_liquid(h, breath_ppb, temp_k=T_BODY)
for o, ppb in breath_ppb.items():
    print(f"  {o:22s} {ppb:6.1f} ppb -> {liquid[o]:10.4g} uM in liquid")
v = concentration_vector_from_air(p, h, breath_ppb, temp_k=T_BODY)
act = nose.receptor_activation(v)
print(f"  peak receptor activation {act.max():.3f} of 1.0 across {len(act)} receptors, "
      f"{int((act > 0.01).sum())} above 1%")
print("  With real constants the acids do drive the array at breath-like ppb. The earlier version of")
print("  this demo reported 2e-3 here, purely because its invented constants were too small.")

print("""
Where that leaves the sensitivity question. For water-soluble odorants there is no longer a gap to
explain: equilibrium partitioning plus cultured-cell EC50s land in the tens of ppb, which is the
range noses work in. For the poorly soluble ones -- the thiol above all -- the chain still asks for
ppm, and that is where to keep looking: at odorant-binding proteins, at accumulation away from
equilibrium, and at the fact that two of those three Henry constants are estimates rather than
measurements. Getting a measured constant for octanethiol would do more than any modelling here.""")

print("\nAn odorant the table does not cover is still refused, not guessed:")
try:
    air_to_liquid(h, {"hydrogen sulfide": 5.0})
except KeyError as e:
    print("  ", e.args[0])
