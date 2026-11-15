"""Short-term synaptic depression ahead of Olsen normalisation, against the recorded DM4 neurons.

Olsen 2010 alone gets DM4's peaks and timing but fires about 2.3x too much between them (RMSE
~70 Hz). The literature (reports/Drosophila-PN-Transience-Mechanisms.md, audited in
sources/AUDIT_Drosophila-PN-Transience-Mechanisms.md) points to short-term depression at the
ORN->PN synapse. Here Nagel et al. 2015's depression model (sw_enose/depression.py) sits between
the receptor input and the Olsen equation, tested three ways:
  1. their MEASURED values, nothing fitted (from other glomeruli and nerve stimulation);
  2. their fast-component values;
  3. depression rate r and recovery tau FITTED, leave one recording out, scored on the fifth.
Input is the Lazar OSN stage's rates for all 24 receptor types (the Or59b stage tracks the OSN
recordings with r ~0.9); output is compared with the 5 unique DM4 recordings, 50 ms smoothing.
Fetch the data as described in demo_lazar.py. MODELLED throughout.
"""
import csv
import itertools
import os
import numpy as np

from sw_enose.bio import BiomimeticNose
from sw_enose.data import synthetic_params
from sw_enose.depression import (NAGEL_2015_F, NAGEL_2015_FAST_F, NAGEL_2015_FAST_TAU_MS,
                                 NAGEL_2015_TAU_MS, depress)
from sw_enose.lazar_al import simulate

REPO = os.path.join(os.path.dirname(__file__), "data/lazar2022/repo/data")
rows = list(csv.reader(open(os.path.join(REPO, "estimated_affinity.csv"))))
k = rows[0][1:].index("59b")
aff = {r[0]: np.array(r[1:], float) for r in rows[1:]}["acetone"]
d = np.load(os.path.join(REPO, "staircase.npz"), allow_pickle=False)
dt = float(d["t"][1] - d["t"][0])
RE, U = 10, [0, 1, 2, 3, 4]
osn = simulate(d["pn_input"][U], aff, dt, record_every=RE, keys=("osn",))["osn"]
data = d["pn_output"][U][:, : (d["pn_output"].shape[1] // RE) * RE].reshape(5, -1, RE).mean(2)
n = min(data.shape[1], osn.shape[1])
osn, data = osn[:, :n], data[:, :n]
smooth = lambda x: np.apply_along_axis(lambda r: np.convolve(r, np.ones(50) / 50, mode="same"), -1, x)
y = smooth(data)
nose = BiomimeticNose(synthetic_params(n_receptors=24, odorants=("A",)), max_orn_rate=1.0)


def olsen(orn):
    """sw-enose's stage 4 (BiomimeticNose.normalise), vectorised over time."""
    return np.apply_along_axis(nose.normalise, -1, orn)


def score(pn):
    p = smooth(pn[..., k])
    rm = np.sqrt(((p - y) ** 2).mean(-1))
    rr = np.array([np.corrcoef(p[i], y[i])[0, 1] for i in range(len(U))])
    return rm, rr, p


def line(name, pn):
    rm, rr, p = score(pn)
    print(f"   {name:46s} {rm.mean():6.1f}  {rr.mean():5.2f}  {p.mean():6.1f}  {p.max(-1).mean():5.0f}")


print(f"   {'':46s} {'RMSE':>6s}  {'r':>5s}  {'mean':>6s}  {'peak':>5s}   (Hz)")
print(f"   {'recorded DM4':46s} {'':6s}  {'':5s}  {y.mean():6.1f}  {y.max(-1).mean():5.0f}")
print(f"   {'published Lazar circuit (demo_lazar_sweep.py)':46s} {25.9:6.1f}  {0.47:5.2f}")
line("Olsen alone (sw-enose stage 4 today)", olsen(osn))
line(f"+ depression, measured f={NAGEL_2015_F} tau={NAGEL_2015_TAU_MS:.0f} ms", olsen(depress(osn)))
line(f"+ depression, fast f={NAGEL_2015_FAST_F} tau={NAGEL_2015_FAST_TAU_MS:.0f} ms",
     olsen(depress(osn, 1 - NAGEL_2015_FAST_F, NAGEL_2015_FAST_TAU_MS)))

R_, T_ = (0.003, 0.01, 0.03, 0.1, 0.22, 0.5), (50, 150, 300, 893, 2000, 5000)
grid = {(r, t): score(olsen(depress(osn, r, t)))[0] for r, t in itertools.product(R_, T_)}
print("\nFitted leave one recording out (chosen on four, scored on the fifth):")
held = []
for i in range(len(U)):
    best = min(grid, key=lambda g: np.mean([grid[g][j] for j in range(len(U)) if j != i]))
    held.append(grid[best][i])
    print(f"   held-out rec {U[i]}: r={best[0]}, tau={best[1]} ms -> RMSE {grid[best][i]:.1f}")
print(f"   mean held-out RMSE {np.mean(held):.1f}")
b = min(grid, key=lambda g: grid[g].mean())
line(f"   that configuration on all five (r={b[0]}, tau={b[1]})", olsen(depress(osn, *b)))

print("\nRMSE surface (mean over 5 recordings); rows r, columns tau in ms:")
print("   r \\ tau " + "".join(f"{t:>7d}" for t in T_))
for r in R_:
    print(f"   {r:8.3f} " + "".join(f"{grid[(r, t)].mean():7.1f}" for t in T_))

print("""
Reading it:
 - Nagel's MEASURED depression, from other glomeruli and nerve stimulation, with nothing fitted,
   cuts the error from ~70 to ~28 Hz and lifts correlation from 0.57 to 0.77.
 - It over-corrects (mean ~25 Hz against 45): Olsen's constants were fitted to real ORN->PN
   responses that already contain steady-state depression, so stacking the measured amount on
   top double-counts. The best-fitting depression rate is about half the measured one.
 - Fitted leave-one-out, held-out error is ~17 Hz with the mean level right: below the published
   Lazar circuit (25.9) and below the ~25 spikes/s Kim et al. 2015 report for their own model
   (different binning, so that comparison is approximate).
 - The recordings constrain HOW MUCH depression, not HOW FAST: a diagonal valley of (r, tau)
   pairs score within a few Hz of the best. That the best grid point sits at Nagel's tau is not
   independent confirmation. This is the non-identifiability the literature report warned of.
 - Peaks are still low (~106 Hz against ~167). Something else adds to the onset burst.""")
