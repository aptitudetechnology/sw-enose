"""Mixtures through the nose, on REAL receptor EC50s (M2OR). MODELLED; illustrative concentrations in liquid."""
import os, numpy as np
from sw_enose import BiomimeticNose, SparseMemory
from sw_enose.m2or import build_params
from sw_enose.mixture import concentration_vector, coverage, BREATH_SULFUR_COVERAGE, UnknownOdorant

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
ODOURS = ("butanoic acid", "isovaleric acid", "Dimethyl trisulfide", "Octanethiol", "cinnamaldehyde", "L-Carvone")
p = build_params(CSV, ODOURS)
nose = BiomimeticNose(p, neuron_noise=0.05, seed=5)
print(p.provenance, "\n")

profiles = {
    "sour (two acids)":       {"butanoic acid": 100, "isovaleric acid": 100},
    "sulfur (trisulfide+thiol)": {"Dimethyl trisulfide": 50, "Octanethiol": 50},
    "sour + sulfur":          {"butanoic acid": 100, "isovaleric acid": 100, "Dimethyl trisulfide": 50, "Octanethiol": 50},
    "spice + mint":           {"cinnamaldehyde": 100, "L-Carvone": 100},
}
for name, mix in profiles.items():
    print(f"{name}: " + "; ".join(f"{o} tested on {v['receptors_tested']}/{v['of']} receptors, agonist for {v['agonist_for']}"
                                  for o, v in coverage(p, mix).items()))

from sw_enose.coverage import comparable_odorants, describe
print("\nWhat these comparisons rest on:")
print(" ", describe(p))
print("  odorant pairs with 2+ receptors tested against both:",
      ", ".join(f"{a}/{b} ({n})" for a, b, n in comparable_odorants(p, 2)) or "none")
print("  So the recognition scores below are mostly NOT a measured difference between these")
print("  odorants: they are the difference between which receptors each odorant happened to be")
print("  screened against. See demo_uncertainty.py section 3.")

mem = SparseMemory()
for name, mix in profiles.items():
    mem.learn(name, [nose.sniff(concentration_vector(p, mix), adapt=False) for _ in range(10)])
print("\nRecognition, 20 trials each (a check of the machinery, NOT of the chemistry):")
for name, mix in profiles.items():
    hits = sum(mem.recognise(nose.sniff(concentration_vector(p, mix), adapt=False))[0] == name for _ in range(20))
    print(f"  {name:26s} {hits}/20")

print("\nA sulfur trace under a strong sour smell (does the model still tell them apart?):")
for trace in (50, 5, 0.5):
    mix = {"butanoic acid": 100, "isovaleric acid": 100, "Dimethyl trisulfide": trace, "Octanethiol": trace}
    got = [mem.recognise(nose.sniff(concentration_vector(p, mix), adapt=False))[0] for _ in range(20)]
    print(f"  sulfur at {trace:>4} uM: called 'sour + sulfur' {got.count('sour + sulfur')}/20, 'sour (two acids)' {got.count('sour (two acids)')}/20")

print("\nThe breath-meter gases cannot be modelled from measured data yet:")
for gas, why in BREATH_SULFUR_COVERAGE.items():
    print(f"  {gas}: {why}")
try:
    concentration_vector(p, {"hydrogen sulfide": 1.0})
except UnknownOdorant as e:
    print("  asking anyway ->", e.args[0])
