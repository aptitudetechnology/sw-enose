"""The biomimetic nose with REAL human receptor EC50s from M2OR. Still MODELLED: efficacy is assumed,
untested pairs are treated as no response, and the circuit numbers are from flies."""
import os, numpy as np
from sw_enose import BiomimeticNose, SparseMemory
from sw_enose.m2or import build_params

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
ODOURS = ("butanoic acid", "cinnamaldehyde", "Geranyl acetate", "cis-3-hexanol", "Androstenone",
          "isovaleric acid", "coumarin", "L-Carvone", "D-Carvone")
p = build_params(CSV, ODOURS)
k = p.known
print(f"{len(p.receptors)} human receptors x {len(ODOURS)} odorants; tested pairs {k.sum()} of {k.size} "
      f"({100*k.mean():.0f}%); measured agonist pairs {int((p.efficacy > 0).sum())}")
print("provenance:", p.provenance, "\n")

nose = BiomimeticNose(p, neuron_noise=0.05, seed=3)
conc = 100.0   # uM, in liquid (the assays are in cultured cells, not air)
vec = lambda j: np.eye(len(ODOURS))[j] * conc

print("Receptors responding to each odorant (measured agonists):")
for j, o in enumerate(ODOURS):
    print(f"  {o:16s} {', '.join(r for i, r in enumerate(p.receptors) if p.efficacy[i, j] > 0)}")

mem = SparseMemory()
for j, o in enumerate(ODOURS):
    mem.learn(o, [nose.sniff(vec(j), adapt=False) for _ in range(10)])
conf = {o: {} for o in ODOURS}
for j, o in enumerate(ODOURS):
    for _ in range(20):
        g = mem.recognise(nose.sniff(vec(j), adapt=False))[0]
        conf[o][g] = conf[o].get(g, 0) + 1
print("\nRecognition (20 trials each; MODELLED, not a result about human smell):")
for o in ODOURS:
    print(f"  {o:16s} -> {conf[o]}")

# Honesty check: with untested pairs set to "no response", two odorants can look different only because
# different labs tested different receptors. Compare L- and D-carvone using only receptors tested on both.
iL, iD = ODOURS.index("L-Carvone"), ODOURS.index("D-Carvone")
both = k[:, iL] & k[:, iD]
print(f"\nReceptors tested on BOTH carvones: {both.sum()} of {len(p.receptors)}")
for i in np.where(both)[0]:
    f = lambda j: f"EC50 {p.affinity[i, j]:.0f} uM" if p.efficacy[i, j] > 0 else "no response"
    print(f"  {p.receptors[i]:8s} L: {f(iL):16s} D: {f(iD)}")
only = (k[:, iL] ^ k[:, iD]).sum()
print(f"Receptors tested on only one of the two: {only}. Differences there reflect what was tested, not biology.")
