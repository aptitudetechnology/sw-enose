"""The fatty-acid series: the first panel in this project with real joint receptor coverage.

The six-odorant panel used elsewhere was chosen to be evocative and has essentially no joint
coverage (see demo_uncertainty.py section 3). This one was chosen by searching M2OR for the odorant
set with the best coverage, and every pair in it was measured. MODELLED throughout; the receptor
EC50s and most of the Henry constants are measured.
"""
import os
import numpy as np

from sw_enose.air import T_BODY, T_REF, load_henry_csv, ppb_for_liquid
from sw_enose.coverage import describe, restrict_to_tested, support
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_CARBONS, ACID_MEASURED_HENRY, ACID_SERIES, EVOCATIVE_PANEL

HERE = os.path.dirname(__file__)
p_all = build_params(os.path.join(HERE, "data/m2or/repo/M2OR_20230428.csv"), ACID_SERIES)
p = restrict_to_tested(p_all, ACID_SERIES)
h = load_henry_csv(os.path.join(HERE, "data/henry/sander_v5_subset.csv"),
                   "measured:Sander, Compilation of Henry's law constants v5.0.0, Atmos. Chem. Phys. "
                   "23, 10901-12440 (2023); transcribed per compound, see data/henry/README.md")
C = [ACID_CARBONS[a] for a in p.odorants]

print("=" * 78)
print("COVERAGE, against the panel this replaces")
print("=" * 78)
old = build_params(os.path.join(HERE, "data/m2or/repo/M2OR_20230428.csv"), EVOCATIVE_PANEL)
print(f"  evocative panel: {describe(old)}")
print(f"  acid series:     {describe(p)}")
s = support(p)
print(f"\n  {s['fully_tested']} of {s['receptors']} receptors tested against all "
      f"{len(p.odorants)} acids, {s['pairs_tested']} of {s['pairs_total']} pairs measured.")
print("  The measured non-responses are the point: a dash below is a result, not a gap.")

print("\n" + "=" * 78)
print("THE TUNING MAP: EC50 in uM, '-' = tested and no response")
print("=" * 78)
print("   receptor  " + "".join(f"{'C' + str(c):>7s}" for c in C))
for i, r in enumerate(p.receptors):
    cells = "".join(f"{p.affinity[i, j]:7.0f}" if p.efficacy[i, j] > 0 else f"{'-':>7s}"
                    for j in range(len(p.odorants)))
    print(f"   {str(r):10s}{cells}")

print("\nPer-receptor tuning: the chain length each receptor answers most strongly (lowest EC50),")
print("and the span it responds to at all.")
for i, r in enumerate(p.receptors):
    j = np.where(p.efficacy[i] > 0)[0]
    if not len(j):
        continue
    best = j[np.argmin(p.affinity[i, j])]
    print(f"   {str(r):10s} best C{C[best]:<2d} at {p.affinity[i, best]:6.0f} uM, "
          f"responds C{min(C[k] for k in j)}-C{max(C[k] for k in j)} ({len(j)} of {len(C)})")
print("\n  Read the map, not the medians: an OR51 group answers the short acids and OR52B2/OR56A5")
print("  the long ones. OR56A5 in particular falls monotonically from C6 to C10 (427 -> 32 uM),")
print("  which is a measured tuning curve and the kind of shape a model should have to reproduce.")

print("\n" + "=" * 78)
print("AIR CONCENTRATION NEEDED, and why it is quoted at 298.15 K")
print("=" * 78)
print("Only 6 of the 8 acids have a published temperature coefficient. Correcting those 6 to body")
print("temperature while leaving C9 and C10 at their 298.15 K values would make part of the")
print("ordering an artefact of which compound happened to have a coefficient. So the series is")
print("compared at 298.15 K, where every value is on the same footing, and body temperature is")
print("shown alongside only to say how large that gap is.\n")
print(f"  {'':4s} {'EC50':>9s} {'H^cp 298K':>10s} {'ppb @298K':>11s} {'ppb @body':>11s}  Henry constant")
for j, a in enumerate(p.odorants):
    col = p.efficacy[:, j] > 0
    if not col.any():
        continue
    ec = float(np.median(p.affinity[col, j]))
    kind = "measured" if a in ACID_MEASURED_HENRY else "ESTIMATE ONLY"
    print(f"  C{C[j]:<3d} {ec:7.1f}uM {h.h_cp_at(a, T_REF):10.2f} "
          f"{ppb_for_liquid(h, a, ec, temp_k=T_REF):11,.0f} "
          f"{ppb_for_liquid(h, a, ec, temp_k=T_BODY):11,.0f}  {kind}")

print("\n  Two things stop this being an ordered prediction yet:")
print("  - C8 to C10 have NO measured Henry constant. C8's estimates span a factor of 73 and its")
print("    policy value does not continue the measured C3-C7 decline, which is why C8 needs")
print("    thousands of ppb here while its neighbours need hundreds. Treat C8-C10 as unresolved.")
print("  - The medians above are taken over each acid's own agonist receptors, which are different")
print("    receptors for different acids. That makes the column a mixture of tuning and coverage,")
print("    not a clean function of chain length. The per-receptor curves above do not have this")
print("    problem, and are where a comparison with real data should be made.")

print(f"""
What this panel unlocks. Chain length is a single ordered covariate that drives receptor tuning
(measured above), water solubility (measured for C3-C7), and human detection threshold (measured in
the psychophysics literature, not yet fetched here). That makes the next test a real one: does the
model reproduce the ORDER across eight compounds, and the SHAPE of each receptor's tuning curve?
Passing that by luck is far harder than passing a pairwise discrimination.

What is needed first: a measured Henry constant for C8, C9 and C10, since that is exactly where the
long-chain receptors OR52B2 and OR56A5 are tuned and exactly where our constants are weakest; and
published human detection thresholds in air for C3-C10.""")
