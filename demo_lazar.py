"""The Lazar, Liu & Yeh fly antennal-lobe circuit, ported to NumPy, against real recordings.

This is the first time anything in this repo has been compared with recorded neural activity.
The recordings ship with the original code (github.com/TK-21st/AntennalLobeLLY22, BSD-3):
acetone concentration staircases (ppm) with the response of an Or59b olfactory receptor neuron
(OSN) and, in separate experiments, of a DM4 projection neuron (PN), as PSTHs in Hz.

Fetch:  git clone --depth 1 https://github.com/TK-21st/AntennalLobeLLY22 data/lazar2022/repo

The port is checked against the original's own saved output in `tests/test_lazar_al.py`. What it
is NOT is our model: it is their circuit with their parameters, run unchanged.
"""
import csv
import os
import numpy as np

from sw_enose.lazar_al import simulate

HERE = os.path.dirname(__file__)
REPO = os.path.join(HERE, "data/lazar2022/repo/data")
RECORD_EVERY = 10                                   # 1 ms bins

rows = list(csv.reader(open(os.path.join(REPO, "estimated_affinity.csv"))))
receptors = rows[0][1:]
affinity = {r[0]: np.array(r[1:], float) for r in rows[1:]}
k = receptors.index("59b")                          # DM4 glomerulus is fed by Or59b OSNs
d = np.load(os.path.join(REPO, "staircase.npz"), allow_pickle=False)   # plain arrays only
dt = float(d["t"][1] - d["t"][0])

print("Data checks:")
for key in ("osn_input", "osn_output", "pn_input", "pn_output"):
    dup = [(a, b) for a in range(7) for b in range(a + 1, 7) if np.array_equal(d[key][a], d[key][b])]
    print(f"   {key:11s} {d[key].shape}  identical rows: {dup or 'none'}")
print("   So PN recordings 3, 5 and 6 are one recording stored three times, and the OSN stimuli")
print("   0 and 1 are the same waveform. Treat the PN set as 5 recordings, not 7.\n")

stim = np.vstack([d["osn_input"], d["pn_input"]])
r = simulate(stim, affinity["acetone"], dt, record_every=RECORD_EVERY)


def block(x):
    return x[:, : (x.shape[1] // RECORD_EVERY) * RECORD_EVERY].reshape(x.shape[0], -1, RECORD_EVERY).mean(2)


def smooth(x, w=50):
    ker = np.ones(w) / w
    return np.array([np.convolve(row, ker, mode="same") for row in x])


for name, model, data, rows_ in (("Or59b OSN", r["osn"][:7, :, k], block(d["osn_output"]), range(7)),
                                 ("DM4 PN", r["pn"][7:, :, k], block(d["pn_output"]), (0, 1, 2, 3, 4))):
    n = min(model.shape[1], data.shape[1])
    m, y = smooth(model[:, :n]), smooth(data[:, :n])
    print(f"{name}: model vs recording, 50 ms smoothing")
    print("   rec   r      RMSE Hz   mean model  mean data   peak model  peak data")
    for i in rows_:
        print(f"   {i}   {np.corrcoef(m[i], y[i])[0, 1]:6.3f}   {np.sqrt(np.mean((m[i] - y[i]) ** 2)):6.1f}"
              f"     {m[i].mean():7.1f}    {y[i].mean():7.1f}     {m[i].max():7.1f}    {y[i].max():7.1f}")
    print()

# ---------------------------------------------------------------- sw-enose's own stages
# Olsen 2010's equation was fitted on fly ORN -> PN data pooled over 24 receptor types, and this
# circuit has exactly 24. So sw-enose's stage 4 can take the Lazar OSN rates in Hz unchanged:
# max_orn_rate=1 makes the activation a rate, and 24 types make the pool rescaling the identity.
from sw_enose.bio import BiomimeticNose
from sw_enose.data import synthetic_params
import itertools

U = [0, 1, 2, 3, 4]                                  # unique PN recordings
osn = r["osn"][7:][U]                                # OSN rates for the PN experiments' stimuli
data = block(d["pn_output"][U])
n = min(data.shape[1], osn.shape[1])
y = [smooth(data[i:i + 1, :n])[0] for i in range(5)]


def swenose_pn(i, tau=1.0, rec=1.0, strength=0.0):
    nose = BiomimeticNose(synthetic_params(n_receptors=24, odorants=("A",)), max_orn_rate=1.0,
                          neuron_noise=0.0, adapt_tau=tau, recover_tau=rec, adapt_strength=strength)
    out = np.empty(n)
    for s_ in range(n):
        g = osn[i, s_]
        if strength > 0:
            g = nose.adapt(g, dt=dt * RECORD_EVERY)   # stage 3, time constants in seconds
        out[s_] = nose.normalise(g)[k]               # stage 4, Olsen
    return smooth(out[None])[0]


rr = lambda m, i: float(np.corrcoef(m, y[i])[0, 1])
lazar_pn = [smooth(r["pn"][7:][i:i + 1, :n, k])[0] for i in U]
olsen = [swenose_pn(i) for i in range(5)]
print("DM4 PN: sw-enose stage 4 (Olsen 2010, fly constants, nothing fitted) vs Lazar's PN stage")
print("   rec   Lazar r  peak   |  sw-enose r  peak   |  recorded peak")
for i in range(5):
    print(f"   {U[i]}     {rr(lazar_pn[i], i):5.2f}  {lazar_pn[i].max():5.0f}   |  {rr(olsen[i], i):6.2f}    "
          f"{olsen[i].max():5.0f}  |  {y[i].max():6.0f}")

grid = list(itertools.product((0.1, 0.3, 1.0, 3.0), (0.1, 0.3, 1.0, 3.0), (0.2, 0.4, 0.6, 0.8)))
fit = max(grid, key=lambda g: rr(swenose_pn(0, *g), 0))
print(f"\nAdding stage 3 (adaptation): constants fitted on recording 0 only -> tau {fit[0]} s, "
      f"recovery {fit[1]} s, strength {fit[2]}; both time constants landed on the grid's edges.")
for i in range(1, 5):
    a = swenose_pn(i, *fit)
    print(f"   held-out rec {U[i]}: Olsen only r {rr(olsen[i], i):.2f} -> with adaptation r {rr(a, i):.2f}")
print()

print("""What this shows.
 - The receptor-neuron stage tracks the recordings closely in shape (r about 0.9 in every
   recording) but under-predicts the rate in recordings 3-5 by about half. Its transduction
   parameters were very probably fitted to Or59b data of this kind, so this is consistency, not
   independent validation. UNVERIFIED: which recordings, if any, they were fitted to.
 - The projection-neuron stage does not match: r about 0.4-0.6, and it peaks near 65 Hz where
   the recordings peak at 150-190 Hz. The port reproduces the original notebook's own output to
   plot precision, so this is the example circuit as published, not a porting error. The paper
   explores many circuit configurations; this notebook is one of them.
 - sw-enose's stage 4, the Olsen 2010 equation with its published fly constants and nothing fitted,
   gets the PEAKS into the recorded range (about 140 Hz against 148-191 Hz, where the published
   circuit reaches about 65 Hz) and tracks timing somewhat better (mean r 0.57 against 0.47).
   But it fires far too much between peaks: mean 107 Hz against 45 Hz recorded, and 29 Hz
   against 7 Hz with no odour, so its overall error is much WORSE (RMSE about 70 Hz against 26
   for the published circuit; demo_lazar_sweep.py). Recorded DM4 responses are transient bursts
   on a modest sustained level; a steady-state equation cannot produce that. An earlier version
   of this text, judging on peaks alone, said stage 4 "reproduces the DM4 firing magnitude". It
   does not.
 - Adaptation fitted on one recording helps the four held-out ones only modestly.""")
