"""sw-enose against reimplementations of two published bio-inspired e-noses.

Raman & Gutierrez-Osuna 2006 (shunting-inhibition normalisation) and Muezzinoglu et al. 2008
(Wilson-Cowan antennal lobe + Kenyon-cell layer with Hebbian readout). Neither released code;
see sw_enose/reference_models.py for what was implemented and every interpretation made.

All models get the SAME front end -- measured M2OR EC50s, competitive binding, same-type
convergence -- so only the downstream processing differs. That is not how either paper ran:
both used metal-oxide sensor signals directly. MODELLED throughout.

Task: the 8 fatty acids C3-C10, each alone at a concentration drawn log-uniformly from 20 to
2000 uM, so only the PATTERN identifies the odorant. 40 training and 80 test samples per acid.
"""
import os
import numpy as np

from sw_enose import BiomimeticNose, SparseMemory
from sw_enose.coverage import restrict_to_tested
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_SERIES
from sw_enose.reference_models import (MuezzinogluAL, MuezzinogluMB, fisher_j,
                                       raman_connectivity, raman_shunting)
from sw_enose.separability import nearest_centroid_accuracy as nca

t = restrict_to_tested(build_params(os.path.join(os.path.dirname(__file__),
                                                 "data/m2or/repo/M2OR_20230428.csv"),
                                    ACID_SERIES), ACID_SERIES)
NO = len(t.odorants)
NOISES = (0.1, 0.4, 0.8)


def dataset(noise, n, seed):
    nose = BiomimeticNose(t, neuron_noise=noise, seed=1)
    rng = np.random.default_rng(seed)
    G, y = [], []
    for j in range(NO):
        for _ in range(n):
            c = np.zeros(NO)
            c[j] = 10 ** rng.uniform(np.log10(20), np.log10(2000))
            G.append(nose.glomeruli(c))
            y.append(j)
    return np.array(G), np.array(y)


def acc(Xtr, ytr, Xte, yte):
    tr = {k: Xtr[ytr == k] for k in range(NO)}
    te = {k: Xte[yte == k] for k in range(NO)}
    return max(nca(tr, te, "euclid"), nca(tr, te, "inner"))


def l2(X):
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)


def swenose_full(noise, Gtr, ytr, Gte, yte, **kw):
    nose = BiomimeticNose(t, neuron_noise=noise, seed=1, **kw)
    mem = SparseMemory()
    for k in range(NO):
        mem.learn(k, [nose.sparse_code(nose.normalise(g)) for g in Gtr[ytr == k]])
    return float(np.mean([mem.recognise(nose.sparse_code(nose.normalise(g)))[0] == y
                          for g, y in zip(Gte, yte)]))


def muezzinoglu_al(Gtr, ytr):
    """Tune (gE, gI) on a validation split of the TRAINING data only, as a grid search."""
    al = MuezzinogluAL(NO, seed=3)
    fit, val = np.arange(len(ytr)) % 4 != 0, np.arange(len(ytr)) % 4 == 0
    best = (-1.0, (0.0, 0.0))
    for ge in (0, 1e-6, 3e-6, 1e-5):
        for gi in (0, 1e-6, 3e-6, 9e-6, 3e-5):
            S = al.set_conductances(ge, gi).snapshot(Gtr)
            a = acc(S[fit], ytr[fit], S[val], ytr[val])
            if a > best[0]:
                best = (a, (ge, gi))
    return al.set_conductances(*best[1]), best[1]


results, ablation, fisher = {}, {}, {}
for noise in NOISES:
    Gtr, ytr = dataset(noise, 40, 11)
    Gte, yte = dataset(noise, 80, 22)
    nose = BiomimeticNose(t, neuron_noise=noise, seed=1)
    olsen = lambda X: np.array([nose.normalise(g) for g in X])
    cg, cu = raman_connectivity(NO, "global"), raman_connectivity(NO, "uniform")
    al, gegi = muezzinoglu_al(Gtr, ytr)
    Str, Ste = al.snapshot(Gtr), al.snapshot(Gte)
    r = {
        "ceiling (best readout of the glomerular vector)": max(
            acc(Gtr, ytr, Gte, yte), acc(l2(Gtr), ytr, l2(Gte), yte),
            acc(l2(olsen(Gtr)), ytr, l2(olsen(Gte)), yte)),
        "sw-enose stage 4, Olsen normalisation": acc(olsen(Gtr), ytr, olsen(Gte), yte),
        "Raman 2006 shunting, c = 1": acc(raman_shunting(Gtr, cg), ytr, raman_shunting(Gte, cg), yte),
        "Raman 2006 shunting, c ~ U(0,1)": acc(raman_shunting(Gtr, cu), ytr,
                                               raman_shunting(Gte, cu), yte),
        "sw-enose full pipeline (sparse code + memory)": swenose_full(noise, Gtr, ytr, Gte, yte),
        f"Muezzinoglu AL + nearest centroid": acc(Str, ytr, Ste, yte),
        "Muezzinoglu AL + Kenyon layer (Hebbian)": float(np.mean(
            MuezzinogluMB(al.n_e, NO, seed=4).train(Str, ytr).predict(Ste) == yte)),
    }
    results[noise] = (r, gegi)
    fisher[noise] = {"Olsen": fisher_j(olsen(Gte), yte), "Raman c=1": fisher_j(raman_shunting(Gte, cg), yte)}
    O = lambda X: olsen(X)
    ablation[noise] = {
        "sw-enose default (2,000 cells, top 5%, fan-in 2)": swenose_full(noise, Gtr, ytr, Gte, yte),
        "10,000 cells": swenose_full(noise, Gtr, ytr, Gte, yte, n_expansion=10000),
        "top 20% active": swenose_full(noise, Gtr, ytr, Gte, yte, sparsity=0.2),
        "10,000 cells and top 20%": swenose_full(noise, Gtr, ytr, Gte, yte, n_expansion=10000,
                                                 sparsity=0.2),
        "10,000 cells, top 20%, fan-in 4": swenose_full(noise, Gtr, ytr, Gte, yte,
                                                        n_expansion=10000, sparsity=0.2, fan_in=4),
        "Muezzinoglu Kenyon layer on Olsen output, top 20%": float(np.mean(
            MuezzinogluMB(NO, NO, active_fraction=0.2, seed=4).train(O(Gtr), ytr).predict(O(Gte)) == yte)),
        "Muezzinoglu Kenyon layer on Olsen output, top 5%": float(np.mean(
            MuezzinogluMB(NO, NO, active_fraction=0.05, seed=4).train(O(Gtr), ytr).predict(O(Gte)) == yte)),
    }


def table(title, rows_by_noise):
    keys = list(next(iter(rows_by_noise.values())).keys())
    print(f"\n{title}")
    print(f"   {'':52s}" + "".join(f"noise {n:<6}" for n in NOISES))
    for k in keys:
        print(f"   {k:52s}" + "".join(f"{rows_by_noise[n][k]:<12.3f}" for n in NOISES))


table("1. Comparison", {n: results[n][0] for n in NOISES})
print("   Muezzinoglu (gE, gI) chosen on training data: " +
      ", ".join(f"noise {n}: {results[n][1]}" for n in NOISES))
table("   Fisher J (Raman's own measure, higher = more separable)", fisher)
table("2. What makes the Kenyon layer better? One change at a time", ablation)
print("""
Reading it:
 - Stage 4: Olsen and Raman shunting agree within about 0.01 and both reach the ceiling.
 - Muezzinoglu's antennal lobe is tuned to zero connectivity here: it is built for sensor
   TRANSIENTS and this task has none, so this is not a fair test of it.
 - sw-enose's stage 5 is the main loss. Cell count barely matters; raising the active fraction
   from 5% to 20% recovers most of it. With 8 glomeruli and fan-in 2 there are only 28 distinct
   wirings, so a 5% code is mostly ties and duplicate cells.
 - These were tuned and scored on the same task: not held out.""")
