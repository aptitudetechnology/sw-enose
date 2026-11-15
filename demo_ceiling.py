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
from sw_enose.separability import describe_gap, pairwise_similarity, stage_accuracies

t = restrict_to_tested(build_params(
    os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv"), ACID_SERIES),
    ACID_SERIES)
short = lambda a: f"C{ACID_CARBONS[a]}"

print("=" * 76)
print("1. WHERE THE BOUND IS: separability in the measured receptor space")
print("=" * 76)
print("Cosine between activation profiles. 1.00 means indistinguishable by ANY processing, at any")
print("noise level: no stage, memory or classifier can separate them.\n")
sim = pairwise_similarity(t)
for cos, a, b in sim[:5]:
    print(f"   {short(a):>4s} vs {short(b):<4s} {cos:.3f}   <-- hardest")
print("   ...")
for cos, a, b in sim[-3:]:
    print(f"   {short(a):>4s} vs {short(b):<4s} {cos:.3f}")
print(f"\n   {sum(1 for c, _, _ in sim if c > 0.85)} of {len(sim)} pairs are above 0.85.")
print("   Adjacent chain lengths share the same two or three receptors at similar EC50s. A real")
print("   nose separates C9 from C10; this array cannot, and that is a fact about the 8 measured")
print("   columns rather than about the code. More receptors would move it. More software will not.")

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
old = stage_accuracies(t, noise=0.1, vary_conc=True, fan_in=6)
print(f"  Before the fix, fan_in=6 absolute:  {old['sparse_memory']:.3f}  (gap {old['gap']:+.3f})")
print(f"  After, Dasgupta's ratio scaled:     {a['sparse_memory']:.3f}  (gap {a['gap']:+.3f})")
print(f"""
  Dasgupta et al. model each expansion cell as sampling about 6 of ~50 projection neurons: a
  ratio of {DASGUPTA_FAN_IN_RATIO:.0%}, not an absolute 6. Carried across as a literal 6, on an array of
  {len(t.odorants)} glomeruli every cell reads {6 / len(t.odorants):.0%} of the input, so all 2,000 cells see nearly the
  same thing and none can be odorant-selective. Scaling the ratio instead gives
  fan_in={default_fan_in(len(t.odorants))} here, and recovers almost everything that was being thrown away.

  This was invisible to every other check in the repo. The stage looked right, its numbers were
  cited, its tests passed, and recognition on the easy four-smell panel was a perfect 1.00. Only
  asking "how does this compare with the best possible readout of the same input" exposed it.""")

print("""
  What remains is the honest cost of the stage: binarising to a sparse code loses a little, and
  loses more as noise rises (+0.06 at noise 0.05, +0.19 at 0.40), because top-k selection is
  brittle where a real-valued readout degrades gracefully. That residue is the price of the
  biomimetic representation, and it is now small enough that the receptor data, not the
  architecture, is again what limits this nose.

  Caveat on the word ceiling: it is the best of the readouts tried, so it is a LOWER BOUND. A
  cleverer classifier might beat it, which would mean the real gap is larger, never smaller.""")
