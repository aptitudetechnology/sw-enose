"""Stage 5 active fraction, chosen on panels it was NOT tuned on.

demo_reference.py found that raising the Kenyon-layer active fraction from 5% to 20% recovered most
of sw-enose's stage-5 loss on the acid panel -- but that was tuned and scored on one task. Here
the same sweep runs on two held-out M2OR panels sharing no odorant with the acids.

This analyses the BINARY-weight expansion that was the default at the time, and is pinned to it
(kc_weights="binary"). Graded weights, adopted later (demo_stage5.py), make the question moot.

Rule fixed BEFORE running: change the default only if one candidate has the best mean accuracy
across noise levels on the held-out panels AND beats 5% on the acids. Result: none qualifies, so
the default stays at 5%. MODELLED throughout.
"""
import os
import numpy as np

from sw_enose.coverage import restrict_to_tested
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_SERIES
from sw_enose.separability import stage_accuracies

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
PANELS = {
    "acids C3-C10 (tuning panel)": ACID_SERIES,
    "held-out A": ("coumarin", "Acetophenone", "L-Carvone", "4-chromanone", "D-Carvone", "Octanol",
                   "Dihydrojasmone"),
    "held-out B": ("coumarin", "Acetophenone", "L-Carvone", "4-chromanone"),
}
FRACS = (0.02, 0.05, 0.1, 0.2, 0.3, 0.5)
NOISES = (0.1, 0.4, 0.8)

for name, od in PANELS.items():
    t = restrict_to_tested(build_params(CSV, od), od)
    print(f"\n{name}: {t.affinity.shape[0]} receptors x {len(t.odorants)} odorants, "
          f"chance {1 / len(t.odorants):.3f}")
    print(f"   {'active':>8s}" + "".join(f"  noise {n:<5}" for n in NOISES) + "    mean")
    ceil = [stage_accuracies(t, noise=n, n_train=40, n_test=80)["ceiling"] for n in NOISES]
    print(f"   {'ceiling':>8s}" + "".join(f"  {c:<11.3f}" for c in ceil) + f"  {np.mean(ceil):.3f}")
    for f in FRACS:
        a = [stage_accuracies(t, noise=n, n_train=40, n_test=80, sparsity=f,
                             kc_weights="binary")["sparse_memory"]
             for n in NOISES]
        print(f"   {f:>8.0%}" + "".join(f"  {x:<11.3f}" for x in a) + f"  {np.mean(a):.3f}")

print("""
Reading it: 20% wins on the acids but is clearly worse than 5% on held-out A; 50% wins both
held-out panels but loses to 5% on the acids. No candidate passes the rule, so 5% stays.
The jumpy curves show why tuning it is pointless here: with fan-in 2, 8 glomeruli allow only 28
distinct wirings (4 allow 6), so the 2,000 cells are a few large groups of exact duplicates and
top-k switches whole groups on or off. The fix is to make the cells differ: graded weights,
tested and adopted in demo_stage5.py.""")
