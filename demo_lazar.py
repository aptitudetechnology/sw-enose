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

print("""What this shows.
 - The receptor-neuron stage tracks the recordings closely in shape (r about 0.9 in every
   recording) but under-predicts the rate in recordings 3-5 by about half. Its transduction
   parameters were very probably fitted to Or59b data of this kind, so this is consistency, not
   independent validation. UNVERIFIED: which recordings, if any, they were fitted to.
 - The projection-neuron stage does not match: r about 0.4-0.6, and it peaks near 65 Hz where
   the recordings peak at 150-190 Hz. The port reproduces the original notebook's own output to
   plot precision, so this is the example circuit as published, not a porting error. The paper
   explores many circuit configurations; this notebook is one of them.
 - For sw-enose: this is a recorded benchmark that its own adaptation and normalisation stages
   (stages 3 and 4) could be run against, which has not been done yet.""")
