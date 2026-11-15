"""Can any configuration of the Lazar antennal-lobe circuit reproduce the recorded DM4 neurons?

The published example configuration does not (demo_lazar.py: r about 0.47, peaks near 65 Hz
against 148-191 Hz recorded). This sweeps the four parameters most likely to set the projection
neuron's response, each at 0.25x, 0.5x, 1x, 2x and 4x its published value: the gains of the PN's
three inputs (OSN axon terminal, post-synaptic excitatory LN, post-synaptic inhibitory LN) and the
strength of pre-synaptic feedback inhibition (`osn_axt` k). 5**4 = 625 configurations.

Design fixed before running:
  - score: RMSE in Hz against the recorded DM4 PSTH, 50 ms smoothing, which penalises both wrong
    shape and wrong magnitude; correlation and peak are reported alongside;
  - data: the 5 unique PN recordings (rows 3, 5 and 6 of pn_output are one recording stored
    three times);
  - held out: leave one recording out -- choose the best configuration on four, score it on the
    fifth, for each of the five. Only held-out numbers are reported as results;
  - benchmarks: the published configuration, and sw-enose's stage 4 (Olsen 2010) with nothing
    fitted.

The 625 x 5 simulations take about 10 minutes on the CPU; results are cached in
data/lazar2022/dm4_sweep.npz (gitignored) and reused if present.
"""
import csv
import itertools
import os
import time
import numpy as np

from sw_enose.bio import BiomimeticNose
from sw_enose.data import synthetic_params
from sw_enose.lazar_al import CIRCUIT, simulate, sweep

HERE = os.path.dirname(__file__)
REPO = os.path.join(HERE, "data/lazar2022/repo/data")
CACHE = os.path.join(HERE, "data/lazar2022/dm4_sweep.npz")
RE = 10
U = [0, 1, 2, 3, 4]
FACTORS = (0.25, 0.5, 1.0, 2.0, 4.0)
SWEPT = (("osn_axt-to-pn", "gmax"), ("posteln-to-pn", "gmax"), ("postiln-to-pn", "gmax"),
         ("osn_axt", "k"))

rows = list(csv.reader(open(os.path.join(REPO, "estimated_affinity.csv"))))
receptors = rows[0][1:]
aff = {r[0]: np.array(r[1:], float) for r in rows[1:]}["acetone"]
k = receptors.index("59b")
d = np.load(os.path.join(REPO, "staircase.npz"), allow_pickle=False)
dt = float(d["t"][1] - d["t"][0])
stim = d["pn_input"][U]
combos = list(itertools.product(FACTORS, repeat=len(SWEPT)))


def config(factors):
    p = {}
    for (blk, key), f in zip(SWEPT, factors):
        p.setdefault(blk, {})[key] = CIRCUIT[blk][key] * f
    return p


if os.path.exists(CACHE):
    pn = np.load(CACHE)["pn"]
    print(f"loaded cached sweep: {pn.shape}")
else:
    t0 = time.time()
    chunks = []
    for i in range(0, len(combos), 125):
        chunks.append(sweep(stim, aff, dt, [config(c) for c in combos[i:i + 125]], record_every=RE,
                            keys=("pn",), receptor=k)["pn"])
        print(f"   {i + len(chunks[-1])} of {len(combos)} configurations done "
              f"({time.time() - t0:.0f} s)", flush=True)
    pn = np.concatenate(chunks)
    np.savez_compressed(CACHE, pn=pn, factors=np.array(combos))
    print(f"ran {len(combos)} configurations x {len(U)} recordings in {time.time() - t0:.0f} s")


def block(x):
    return x[:, : (x.shape[1] // RE) * RE].reshape(x.shape[0], -1, RE).mean(2)


def smooth(x, w=50):
    ker = np.ones(w) / w
    return np.apply_along_axis(lambda r: np.convolve(r, ker, mode="same"), -1, x)


data = block(d["pn_output"][U])
n = min(data.shape[1], pn.shape[2])
y = smooth(data[:, :n])                                      # (5, n)
m = smooth(pn[:, :, :n])                                     # (configs, 5, n)
rmse = np.sqrt(((m - y[None]) ** 2).mean(axis=2))            # (configs, 5)
corr = np.array([[np.corrcoef(m[c, i], y[i])[0, 1] for i in range(len(U))] for c in range(len(combos))])
peak = m.max(axis=2)
default = combos.index((1.0, 1.0, 1.0, 1.0))

# benchmark: sw-enose stage 4, nothing fitted, on the Lazar OSN stage's output
osn = simulate(stim, aff, dt, record_every=RE, keys=("osn",))["osn"][:, :n]
nose = BiomimeticNose(synthetic_params(n_receptors=24, odorants=("A",)), max_orn_rate=1.0)
ols = smooth(np.array([[nose.normalise(g)[k] for g in rec] for rec in osn]))
ols_rmse = np.sqrt(((ols - y) ** 2).mean(axis=1))
ols_r = [np.corrcoef(ols[i], y[i])[0, 1] for i in range(len(U))]

print("\nLeave-one-recording-out: configuration chosen on the other four, scored on this one")
print("   rec |  chosen factors (axt->PN, eLN->PN, iLN->PN, pre-LN k) |  RMSE   r     peak | "
      " published: RMSE  r    peak |  Olsen, unfitted: RMSE  r    peak | recorded peak")
held = []
for i in range(len(U)):
    others = [j for j in range(len(U)) if j != i]
    best = int(np.argmin(rmse[:, others].mean(axis=1)))
    held.append((rmse[best, i], corr[best, i], rmse[default, i], corr[default, i], ols_rmse[i], ols_r[i]))
    print(f"   {U[i]}   |  {str(combos[best]):48s} | {rmse[best, i]:5.1f} {corr[best, i]:5.2f} {peak[best, i]:5.0f} | "
          f"      {rmse[default, i]:5.1f} {corr[default, i]:5.2f} {peak[default, i]:5.0f} |"
          f"            {ols_rmse[i]:5.1f} {ols_r[i]:5.2f} {ols[i].max():5.0f} | {y[i].max():5.0f}")
h = np.array(held)
print(f"   mean held-out:  fitted Lazar RMSE {h[:, 0].mean():.1f}, r {h[:, 1].mean():.2f}  |  "
      f"published RMSE {h[:, 2].mean():.1f}, r {h[:, 3].mean():.2f}  |  "
      f"Olsen unfitted RMSE {h[:, 4].mean():.1f}, r {h[:, 5].mean():.2f}")

print(f"\nWhy Olsen's correlation is higher but its error far worse: mean firing "
      f"{ols.mean():.0f} Hz against {y.mean():.0f} Hz recorded. It holds high levels through the odour;")
print("the recordings are transient bursts on a modest sustained level.")

best_all = int(np.argmin(rmse.mean(axis=1)))
print(f"\nBest on all five (in-sample, for orientation only): {combos[best_all]}, "
      f"RMSE {rmse[best_all].mean():.1f}, r {corr[best_all].mean():.2f}, peaks "
      + " ".join(f"{p:.0f}" for p in peak[best_all]))
on_edge = [SWEPT[j] for j, f in enumerate(combos[best_all]) if f in (FACTORS[0], FACTORS[-1])]
if on_edge:
    print(f"   On the edge of the grid for {on_edge}: the true optimum may lie outside it.")
