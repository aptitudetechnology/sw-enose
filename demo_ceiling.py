"""How close is the pipeline to the ceiling the receptor data sets?

Rule 4 says a software model cannot recover information the receptors do not carry. That is a hard
bound. Two questions follow, and they have different answers:

  Where is the bound?          -> pairwise separability in the measured receptor space
  Are we at it?                -> compare the pipeline against an optimal readout

The second question found a real bug, which this demo now reports post-fix. MODELLED throughout.
"""
import os
import numpy as np

from sw_enose.bio import DASGUPTA_FAN_IN_RATIO, default_fan_in
from sw_enose.coverage import restrict_to_tested
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_CARBONS, ACID_SERIES
from sw_enose.separability import (NOISE_GRID, describe_gap, noise_tolerance, pairwise_similarity,
                                   stage_accuracies)

t = restrict_to_tested(build_params(
    os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv"), ACID_SERIES),
    ACID_SERIES)
short = lambda a: f"C{ACID_CARBONS[a]}"

print("=" * 76)
print("1. WHERE THE BOUND IS: separability in the measured receptor space")
print("=" * 76)
print("Cosine between activation profiles. Only 1.00 means indistinguishable by ANY processing at any")
print("noise level. Below that it is a distance, and noise decides whether it can be resolved.\n")
sim = pairwise_similarity(t)
for cos, a, b in sim[:5]:
    print(f"   {short(a):>4s} vs {short(b):<4s} {cos:.3f}   <-- hardest")
print("   ...")
for cos, a, b in sim[-3:]:
    print(f"   {short(a):>4s} vs {short(b):<4s} {cos:.3f}")
print(f"\n   {sum(1 for c, _, _ in sim if c > 0.85)} of {len(sim)} pairs are above 0.85.")
print("\n   How much noise does each pair tolerate? Two-way accuracy on the glomerular vector:\n")
tol = noise_tolerance(t)
print("   pair         cos  " + "".join(f"{n:>6}" for n in NOISE_GRID))
for tv, cos, a, b, acc in tol[:5]:
    print(f"   {short(a):>4s} v {short(b):<4s} {cos:.3f} " + "".join(f"{acc[n]:6.2f}" for n in NOISE_GRID))
worst = min(r[0] for r in tol)
print(f"\n   Every pair holds accuracy >= 0.95 up to noise {worst}, about eight times the 0.05-0.1")
print("   these demos run at. The most similar pairs do fail first, so similarity predicts the")
print("   ORDER of failure, but at operating noise the receptor data is not what limits this panel.")
print("   Whether it binds in a real nose depends on real neural noise, which is invented here.")

print("\n" + "=" * 76)
print("2. ARE WE AT IT: pipeline against an optimal readout")
print("=" * 76)
print("Noise enters at the glomerular stage; every later stage is a deterministic function of it.")
print("So the best readout of the glomerular vector bounds what any later readout can reach.")
print("Concentration varies over 20-2000 uM, so only the PATTERN identifies the odorant --")
print("the job divisive normalisation exists to do.\n")
print(f"  {'noise':>6s} {'ceiling':>8s} {'after norm':>11s} {'sparse code':>12s} "
      f"{'SparseMemory':>13s} {'gap':>7s}")
for noise in (0.05, 0.1, 0.2, 0.4):
    a = stage_accuracies(t, noise=noise, vary_conc=True)
    print(f"  {noise:6.2f} {a['ceiling']:8.3f} {a['normalised']:11.3f} {a['sparse']:12.3f} "
          f"{a['sparse_memory']:13.3f} {a['gap']:+7.3f}")
a = stage_accuracies(t, noise=0.1, vary_conc=True)
print(f"\n  chance is {a['chance']:.3f} with {len(t.odorants)} odorants.")
print(" ", describe_gap(a))

print("\n" + "=" * 76)
print("3. WHAT THIS MEASUREMENT FOUND")
print("=" * 76)
hist = [("binary weights, absolute fan_in=6 (original)", dict(fan_in=6, kc_weights="binary")),
        ("binary weights, fan_in scaled to Dasgupta's ratio", dict(kc_weights="binary")),
        ("graded lognormal weights (current default)", {})]
for label, kw in hist:
    h = stage_accuracies(t, noise=0.1, vary_conc=True, **kw)
    print(f"  {label:50s} {h['sparse_memory']:.3f}  (gap {h['gap']:+.3f})")
print(f"""
  Dasgupta et al. model each expansion cell as sampling about 6 of ~50 projection neurons: a
  ratio of {DASGUPTA_FAN_IN_RATIO:.0%}, not an absolute 6. Carried across as a literal 6, on an array of
  {len(t.odorants)} glomeruli every binary cell reads {6 / len(t.odorants):.0%} of the input, so the 2,000 cells see nearly
  the same thing. Scaling the ratio (fan_in={default_fan_in(len(t.odorants))}) recovered most of it -- but with binary
  weights even that leaves only 28 distinct cells. Graded weights make every cell distinct and
  close the remaining gap, at any fan-in (demo_stage5.py).

  This was invisible to every other check in the repo. The stage looked right, its numbers were
  cited, its tests passed, and recognition on the easy four-smell panel was a perfect 1.00. Only
  asking "how does this compare with the best possible readout of the same input" exposed it.""")

print("""
  What remains is small: with graded weights the gap is a few hundredths at every noise level in
  the table above. On this panel the pipeline now uses nearly all the separability its receptors
  provide, so the receptor data -- not the architecture -- is what limits it.

  Caveat on the word ceiling: it is the best of the readouts tried, so it is a LOWER BOUND. A
  cleverer classifier might beat it, which would mean the real gap is larger, never smaller.""")
