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
from sw_enose.uncertainty import (paired_efficacy, paired_stage_sweep, paired_verdict,
                                  SINGH_RELATIVE_EFFICACY, between_smell_overlap,
                                  efficacy_sensitivity, seed_floor, stage_sensitivity,
                                  sweep_summary, verdict)

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
ODOURS = ("butanoic acid", "isovaleric acid", "Dimethyl trisulfide", "Octanethiol",
          "cinnamaldehyde", "L-Carvone")
SEEDS = tuple(range(1, 13))       # 12 seeds; see the paired analysis below
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
print(f"""
  HOW TO READ WHAT FOLLOWS. On the hard task a single seed can score anywhere from about 0.4 to
  1.0: the seed fixes the expansion wiring, and that wiring is most of the variance. So every
  comparison below is PAIRED: each condition is run on the same {len(SEEDS)} seeds as its
  baseline, and the mean of the per-seed differences is judged against its own standard error.
  (An earlier version compared seed-averaged results with the min-max range of single seeds, a
  yardstick that grows as seeds are added; its verdicts are superseded by these.) An effect
  "MATTERS" when it exceeds 2 paired SE and 0.02; about 20 comparisons are made, so a single
  result near 2-3 SE is marginal.""")

ctrl = between_smell_overlap(p, easy, seed=SEEDS[0], neuron_noise=0.05)
print(f"\n  CONTROL for reading overlap: codes for DIFFERENT smells overlap {ctrl['mean']:.3f} "
      f"on average (worst pair {ctrl['max']:.3f}), chance {ctrl['chance']:.3f}.")

# ---------------------------------------------------------------- 2. efficacy
print("\n" + "=" * 78)
print("2. EFFICACY: M2OR assumes every agonist acts at full strength")
print("=" * 78)
s_ = np.asarray(SINGH_RELATIVE_EFFICACY)
print(f"Our fits of Singh et al.'s raw curves give relative efficacy among agonists at the same")
print(f"receptor: n={len(s_)}, range {s_.min():.3f} to {s_.max():.3f}, median {np.median(s_):.3f}. That spread is")
print("weak evidence (17 of the 24 curves behind it do not saturate, so their efficacy is not")
print("identifiable), but it is a plausible range to stress-test against. Redrawing from it:\n")
eff = paired_efficacy(p, hard, draws=12, seeds=SEEDS, trials=TRIALS, neuron_noise=0.05)
sig = [d for d in eff["draws"] if abs(d["diff_mean"]) > max(2 * d["diff_se"], 0.02)]
print(f"  baseline (efficacy=1), mean over seeds: {eff['baseline'].mean():.3f}")
print(f"  12 redraws, each averaged over the same seeds: {eff['draw_means'].min():.3f} to "
      f"{eff['draw_means'].max():.3f}")
print(f"  spread BETWEEN draws (SD {eff['between_draw_sd']:.3f}) against the precision of one draw's "
      f"average (SE {eff['typical_se']:.3f})")
print(f"  draws shifting recognition beyond 2 paired SE: {len(sig)} of {len(eff['draws'])} "
      f"(shifts {min(d['diff_mean'] for d in sig):+.2f} to {max(d['diff_mean'] for d in sig):+.2f})"
      if sig else "  no draw shifts recognition beyond 2 paired SE")
old = efficacy_sensitivity(p, hard, draws=12, seeds=SEEDS[:3], trials=TRIALS, neuron_noise=0.05)
print(f"  code overlap with the efficacy=1 nose: {old['overlap'][0]:.2f} to {old['overlap'][2]:.2f}, "
      f"median {old['overlap'][1]:.2f}  (different smells: {ctrl['mean']:.3f})")
print("""
  Efficacy MATTERS, and this is the firm result of the section: which plausible efficacies are
  drawn moves near-threshold recognition by up to about 0.2 either way, several times the
  precision of the measurement. And even when discrimination holds, a sizeable fraction of a
  code's active cells move. So this nose can report THAT two smells differ, but not WHICH code
  belongs to a smell, and near threshold not even that, until efficacy is known.""")

# ---------------------------------------------------------------- 4. stages
print("\n" + "=" * 78)
print("4. THE INVENTED STAGE PARAMETERS (paired, %d seeds)" % len(SEEDS))
print("=" * 78)
grid = {"neurons_per_type": [1, 5, 20, 50, 200, 500],
        "adapt_tau": [1, 4, 8, 30, 100],
        "adapt_strength": [0.0, 0.3, 0.6, 0.9, 0.95],
        "recover_tau": [1, 4, 20, 100]}
for w in ("lognormal", "binary"):
    st = paired_stage_sweep(p, hard, grid, seeds=SEEDS, trials=TRIALS, neuron_noise=0.05,
                            steps=5, adapt=True, kc_weights=w)
    b = st["baseline"]
    print(f"\n  [{w} expansion weights{' -- current default' if w == 'lognormal' else ''}] baseline "
          f"{b.mean():.3f}; shifts from it, mean +/- paired SE:")
    for key, rows in st["sweeps"].items():
        print(f"    {key:16s} " + "  ".join(f"{r['value']}:{r['diff_mean']:+.3f}+/-{r['diff_se']:.3f}"
                                           for r in rows))
        print(f"    {'':16s} {paired_verdict(rows, label=key)}")

print("""
What this retires and what it does not.
 - Convergence matters only at the extreme: one neuron per receptor type costs about 0.1-0.14,
   because stage 2 acts only by averaging neuron noise. Above about 20 neurons per type no effect
   is detectable. The invented ratio is load-bearing only if it is set very low.
 - The adaptation constants move recognition by at most about 0.06, detectably with graded
   weights and not with binary ones. On a static presentation adaptation can only subtract
   signal, so this is a small cost, not a benefit; a task with a changing background is needed to
   see what adaptation is for.
 - recover_tau gets no verdict at all: recovery only acts once an odour is removed, and this task
   never removes one. Reporting it as "does not matter" would be a false reassurance.
 - Efficacy is the serious unknown. Nothing in this repo should claim a near-threshold result
   from M2OR parameters until efficacy is measured or bounded per pair.""")
