"""How much do this nose's answers depend on what we do not know?

Three unknowns, three measurements. All MODELLED; the point is to bound the model, not extend it.

 2. Efficacy. M2OR has no efficacy values, so every agonist is assumed to act at full strength.
 3. Coverage. Most receptor-odorant pairs were never tested, and an untested pair is stored as "no
    response" because there is no other array to build.
 4. The invented stage parameters: convergence ratio and the adaptation time constants.

The method throughout: change the unknown, and see whether the answer moves by more than reseeding
the same model moves it. Anything smaller than that is not an effect.
"""
import os
import numpy as np

from sw_enose import BiomimeticNose
from sw_enose.coverage import comparable_odorants, describe, restrict_to_tested, support
from sw_enose.m2or import build_params
from sw_enose.mixture import concentration_vector
from sw_enose.uncertainty import (SINGH_RELATIVE_EFFICACY, between_smell_overlap,
                                  efficacy_sensitivity, seed_floor, stage_sensitivity,
                                  sweep_summary, verdict)

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
ODOURS = ("butanoic acid", "isovaleric acid", "Dimethyl trisulfide", "Octanethiol",
          "cinnamaldehyde", "L-Carvone")
SEEDS = (1, 5, 9)
TRIALS = 50

p = build_params(CSV, ODOURS)
cv = lambda d: concentration_vector(p, d)
print(p.provenance, "\n")

# ---------------------------------------------------------------- 3. coverage
print("=" * 78)
print("3. COVERAGE: what measurement is behind a comparison")
print("=" * 78)
print(describe(p))
print("\nOdorant pairs that CAN be compared on measured ground (receptors tested against both):")
for a, b, n in comparable_odorants(p, min_receptors=2):
    print(f"  {a:22s} vs {b:22s} {n:2d} receptors")
missing = [(a, b) for i, a in enumerate(ODOURS) for b in ODOURS[i + 1:]
           if not any({a, b} == {x, y} for x, y, _ in comparable_odorants(p, min_receptors=2))]
print(f"  ...and {len(missing)} pairs with fewer than 2, which cannot honestly be compared at all:")
for a, b in missing[:4]:
    print(f"    {a} vs {b}")

print("\nRestricting the array to receptors tested against ALL six odorants:")
try:
    tight = restrict_to_tested(p, ODOURS)
    print(f"  {tight.affinity.shape[0]} receptors survive")
except Exception as e:
    print(f"  refused: {e}")
pair = ("butanoic acid", "isovaleric acid")
tight = restrict_to_tested(p, pair)
print(f"\nFor the one well-covered pair {pair}: {tight.affinity.shape[0]} of "
      f"{p.affinity.shape[0]} receptors were tested against both.")
print(" ", describe(tight, pair))
print("  Any claim that these two smell different rests on those receptors, not on the full array.")

# ---------------------------------------------------------------- the task
print("\n" + "=" * 78)
print("THE TASK the next two sections are measured on")
print("=" * 78)
easy = {"sour": cv({"butanoic acid": 100, "isovaleric acid": 100}),
        "sulfur": cv({"Dimethyl trisulfide": 50, "Octanethiol": 50}),
        "spice": cv({"cinnamaldehyde": 100}),
        "mint": cv({"L-Carvone": 100})}
hard = {"sour": cv({"butanoic acid": 100, "isovaleric acid": 100}),
        "sour+trace": cv({"butanoic acid": 100, "isovaleric acid": 100,
                          "Dimethyl trisulfide": 0.07, "Octanethiol": 0.07})}
e_floor = seed_floor(p, easy, seeds=SEEDS, trials=TRIALS, neuron_noise=0.05)
h_floor = seed_floor(p, hard, seeds=SEEDS, trials=TRIALS, neuron_noise=0.05)
print(f"  four clearly different smells: recognition {e_floor['mean']:.2f} "
      f"(seeds {e_floor['min']:.2f}-{e_floor['max']:.2f})")
print(f"  0.07 uM sulfur trace under strong sour: recognition {h_floor['mean']:.2f} "
      f"(seeds {h_floor['min']:.2f}-{h_floor['max']:.2f}), chance 0.50")
print("  The easy task is at ceiling, so it cannot show an effect in either direction. Everything")
print("  below is measured on the hard one, where there is room to fall and room to improve.")

ctrl = between_smell_overlap(p, easy, seed=SEEDS[0], neuron_noise=0.05)
print(f"\n  CONTROL for reading overlap: codes for DIFFERENT smells overlap {ctrl['mean']:.3f} "
      f"on average (worst pair {ctrl['max']:.3f}), chance {ctrl['chance']:.3f}.")
print("  So the codes are near orthogonal, and an overlap of 0.6 below means 'the same smell with")
print("  a large minority of its cells moved', not 'barely related'.")

# ---------------------------------------------------------------- 2. efficacy
print("\n" + "=" * 78)
print("2. EFFICACY: M2OR assumes every agonist acts at full strength")
print("=" * 78)
s = np.asarray(SINGH_RELATIVE_EFFICACY)
print(f"Our fits of Singh et al.'s raw curves give relative efficacy among agonists at the same")
print(f"receptor: n={len(s)}, range {s.min():.3f} to {s.max():.3f}, median {np.median(s):.3f}.")
print("So the assumed 1.0 is not a mild simplification: a typical agonist acts at under half the")
print("strength of the best agonist at its receptor. Redrawing from that measured spread:\n")
eff = efficacy_sensitivity(p, hard, draws=12, seeds=SEEDS, trials=TRIALS, neuron_noise=0.05)
print(f"  recognition over {eff['draws']} draws: {eff['recognition'][0]:.2f} to "
      f"{eff['recognition'][2]:.2f}, median {eff['recognition'][1]:.2f}")
print(f"  baseline (efficacy=1): {eff['baseline']['mean']:.2f}, seeds "
      f"{eff['baseline']['min']:.2f}-{eff['baseline']['max']:.2f}")
print(f"  code overlap with the efficacy=1 nose: {eff['overlap'][0]:.2f} to {eff['overlap'][2]:.2f}, "
      f"median {eff['overlap'][1]:.2f}  (different smells: {ctrl['mean']:.3f})")
print(" ", verdict(eff["recognition"], eff["baseline"], "near-threshold discrimination"))
print("\n  Read it as two separate facts. Discrimination sometimes collapses to chance (0.50) and")
print("  sometimes beats the baseline, purely with which efficacies were drawn. And even when it")
print("  holds, a third to two thirds of the code's active cells move. So this nose can report THAT")
print("  two smells differ, but not WHICH code belongs to a smell, and near threshold not even that.")

# ---------------------------------------------------------------- 4. stages
print("\n" + "=" * 78)
print("4. THE INVENTED STAGE PARAMETERS")
print("=" * 78)
grid = {"neurons_per_type": [1, 5, 20, 50, 200, 500],
        "adapt_tau": [1, 4, 8, 30, 100],
        "adapt_strength": [0.0, 0.3, 0.6, 0.9, 0.95],
        "recover_tau": [1, 4, 20, 100]}
st = stage_sensitivity(p, hard, grid, seeds=SEEDS, trials=TRIALS, neuron_noise=0.05,
                       steps=5, adapt=True)
b = st["baseline"]
print(f"baseline {b['mean']:.2f}, reseeding alone moves it {b['spread']:.2f} "
      f"({b['min']:.2f}-{b['max']:.2f}). A sweep must beat that to mean anything.\n")
for key, rows in st["sweeps"].items():
    summ = sweep_summary(rows, b, key)
    print(f"  {key} (BIOLOGY says: numbers invented)")
    print("    " + "  ".join(f"{r['value']}:{r['recognition']:.2f}" for r in rows))
    print(f"    code overlap with baseline stays {min(r['overlap'] for r in rows):.2f}"
          f"-{max(r['overlap'] for r in rows):.2f}")
    print(f"    {summ['verdict']}")

print("""
What this retires and what it does not. The two adaptation constants that the task does exercise
move the answer less than reseeding does, so those invented numbers are not load-bearing here and
can stay invented without weakening a result. Convergence is different: recognition trends with it
in rank order across the sweep, because stage 2 acts only by averaging neuron noise away, so the
invented convergence ratio IS load-bearing near threshold and wants a real number.

recover_tau gets no verdict at all, and that is the right answer rather than a gap: recovery only
does anything once an odour is taken away, and this task never removes one. Testing it needs a
presentation with a blank period in it, which is not built. Reporting it as "does not matter" would
have been a false reassurance.

The efficacy assumption is the serious one. It is not an invented stage constant that happens not to
matter; it is a value the data we already hold contradicts, and it decides whether a near-threshold
discrimination works at all. Nothing in this repo should claim a near-threshold result from M2OR
parameters until efficacy is measured or bounded per pair.""")
