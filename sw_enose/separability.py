"""How much of the discriminable information survives each stage?

Rule 4 of this project says a software model cannot recover information the receptors do not carry.
That sets a ceiling. This module measures two different things against it:

 1. `pairwise_similarity`: how separable the odorants are in the MEASURED receptor space at all.
    Two odorants whose activation profiles have cosine 1.0 are indistinguishable by any processing,
    at any noise level. No stage, memory or classifier can move that.

 2. `stage_accuracies`: how much of the available separability the pipeline actually uses. Noise
    enters at the glomerular stage and every later stage is a deterministic function of it, so
    optimal classification OF THE GLOMERULAR VECTOR is the ceiling and each later readout can only
    lose. Comparing them localises the loss.

A ceiling is not the same as sitting at it. A large gap means the stages are discarding signal that
the receptors did provide, which is a software problem and fixable. A small gap means further
architecture work is pointless and only better receptor data will help.

Classification is nearest-centroid, which is close to Bayes-optimal for the roughly isotropic
Gaussian noise the glomerular stage produces, and is the same rule `pipeline.Pipeline` uses.
"""
import itertools

import numpy as np

from .bio import BiomimeticNose, SparseMemory
from .data import ReceptorParams


def _l2(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def nearest_centroid_accuracy(train: dict, test: dict, metric="euclid") -> float:
    """train/test: {label: array of feature vectors}. Returns accuracy 0..1."""
    cent = {k: np.mean(v, axis=0) for k, v in train.items()}
    ok = n = 0
    for label, vectors in test.items():
        for v in vectors:
            if metric == "euclid":
                pred = min(cent, key=lambda k: float(np.linalg.norm(v - cent[k])))
            elif metric == "inner":
                pred = max(cent, key=lambda k: float(v @ cent[k]))
            else:
                raise ValueError("metric must be 'euclid' or 'inner'")
            ok += pred == label
            n += 1
    return ok / max(1, n)


def activation_profiles(params: ReceptorParams, conc_um=200.0) -> dict:
    """Noise-free receptor activation for each odorant presented alone."""
    nose = BiomimeticNose(params, neuron_noise=0.0, seed=0)
    out = {}
    for j, a in enumerate(params.odorants):
        c = np.zeros(len(params.odorants))
        c[j] = conc_um
        out[a] = nose.receptor_activation(c)
    return out


def pairwise_similarity(params: ReceptorParams, conc_um=200.0) -> list:
    """[(cosine, odorant_a, odorant_b), ...] most similar first.

    Only a cosine of exactly 1.0 is a hard ceiling: identical profiles cannot be told apart at any
    noise level. Anything below 1.0 is a distance, and whether it can be resolved depends on how much
    noise sits on top of it. Use `noise_tolerance` for that question; similarity alone does not
    answer it.
    """
    prof = activation_profiles(params, conc_um)
    rows = []
    for a, b in itertools.combinations(params.odorants, 2):
        u, v = prof[a], prof[b]
        nu, nv = float(np.linalg.norm(u)), float(np.linalg.norm(v))
        rows.append((float(u @ v / nu / nv) if nu and nv else float("nan"), a, b))
    return sorted(rows, reverse=True)


def stage_accuracies(params: ReceptorParams, noise=0.1, vary_conc=True, conc_um=200.0,
                     conc_range=(20.0, 2000.0), n_train=60, n_test=150, seed=1, **nose_kw) -> dict:
    """Accuracy of an optimal readout taken at four points along the pipeline.

    vary_conc: draw each presentation's concentration log-uniformly from `conc_range`, so that
        intensity is a nuisance variable and only the PATTERN identifies the odorant. This is the
        job divisive normalisation exists to do, so it is the fairer test of it. With vary_conc
        False every presentation is at `conc_um` and intensity alone carries information.

    Keys: `glomeruli`, `glomeruli_l2`, `normalised`, `sparse`, `sparse_memory` (the pipeline's own
    readout, for comparison with an optimal readout of the same code), plus `ceiling`, `gap` and
    `chance`. `ceiling` is the best of the pre-sparse readouts: a LOWER BOUND on what is achievable,
    since a cleverer classifier might beat all of them, so `gap` is a lower bound on the real loss.
    """
    nose = BiomimeticNose(params, neuron_noise=noise, seed=seed, **nose_kw)
    rng = np.random.default_rng(seed + 99)
    n_od = len(params.odorants)
    keys = ("glomeruli", "glomeruli_l2", "normalised", "sparse")
    data = {k: ({}, {}) for k in keys}
    for split, n in ((0, n_train), (1, n_test)):
        for j, a in enumerate(params.odorants):
            for k in keys:
                data[k][split].setdefault(a, [])
            for _ in range(n):
                c = np.zeros(n_od)
                c[j] = (10 ** rng.uniform(*np.log10(conc_range))) if vary_conc else conc_um
                g = nose.glomeruli(c)
                pn = nose.normalise(g)
                data["glomeruli"][split][a].append(g)
                data["glomeruli_l2"][split][a].append(_l2(g))
                data["normalised"][split][a].append(_l2(pn))
                data["sparse"][split][a].append(nose.sparse_code(pn))
    out = {}
    for k in keys:
        tr = {n: np.array(v) for n, v in data[k][0].items()}
        te = {n: np.array(v) for n, v in data[k][1].items()}
        out[k] = max(nearest_centroid_accuracy(tr, te, "euclid"),
                     nearest_centroid_accuracy(tr, te, "inner"))
    mem = SparseMemory()
    for a in params.odorants:
        mem.learn(a, data["sparse"][0][a])
    hits = sum(mem.recognise(v)[0] == a for a in params.odorants for v in data["sparse"][1][a])
    out["sparse_memory"] = hits / max(1, n_od * n_test)
    # Every pre-sparse readout here is a deterministic function of the glomerular vector, so each is
    # one particular classifier of it and the best of them is a valid LOWER BOUND on the true
    # ceiling. It is not the ceiling itself: a better classifier may exist, so `gap` understates.
    # `normalised` beating the raw readouts is exactly this -- removing the intensity nuisance makes
    # a nearest-centroid rule work better, which says the raw readout was not optimal.
    out["ceiling"] = max(out["glomeruli"], out["glomeruli_l2"], out["normalised"])
    out["ceiling_is_lower_bound"] = True
    out["gap"] = out["ceiling"] - out["sparse_memory"]
    out["chance"] = 1.0 / n_od
    return out


def describe_gap(acc: dict, tol=0.05) -> str:
    """A verdict on whether architecture work has anything left to give."""
    if acc["gap"] <= tol:
        return (f"AT THE ESTIMATED CEILING (gap {acc['gap']:+.3f}, and the ceiling is a lower "
                "bound so the real gap may be larger): the pipeline uses nearly all the "
                "separability these receptors provide. Further stage work has little to give; "
                "better receptor data is what would help")
    return (f"BELOW THE CEILING (gap {acc['gap']:+.3f}): an optimal readout of the glomerular "
            f"vector scores {acc['ceiling']:.3f} where the pipeline scores "
            f"{acc['sparse_memory']:.3f}, so the stages are discarding signal the receptors did "
            "provide. That is a software problem, not a data one")


NOISE_GRID = (0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2)


def pair_accuracy(params: ReceptorParams, a, b, noise, conc_um=200.0, n_train=60, n_test=150,
                  seed=1) -> float:
    """Two-way nearest-centroid accuracy on the glomerular vector for one pair, at one noise level."""
    nose = BiomimeticNose(params, neuron_noise=noise, seed=seed)
    idx = {o: j for j, o in enumerate(params.odorants)}

    def draw(name, n):
        c = np.zeros(len(params.odorants))
        c[idx[name]] = conc_um
        return np.array([nose.glomeruli(c) for _ in range(n)])

    tr = {a: draw(a, n_train), b: draw(b, n_train)}
    te = {a: draw(a, n_test), b: draw(b, n_test)}
    return nearest_centroid_accuracy(tr, te, "euclid")


def noise_tolerance(params: ReceptorParams, conc_um=200.0, grid=NOISE_GRID, threshold=0.95,
                    **kw) -> list:
    """For every odorant pair, the largest neuron noise at which it is still told apart.

    Returns [(tolerance, cosine, a, b, {noise: accuracy}), ...], least tolerant first. `tolerance`
    is the highest grid value with accuracy >= threshold, 0.0 if none, or inf if every grid value
    passes. This is the statement that replaces "similar profiles cannot be separated": similar
    profiles can be, until the noise is large enough to close the distance between them.
    """
    sim = {(x, y): c for c, x, y in pairwise_similarity(params, conc_um)}
    rows = []
    for (x, y), cos in sim.items():
        accs = {n: pair_accuracy(params, x, y, n, conc_um=conc_um, **kw) for n in grid}
        passing = [n for n in grid if accs[n] >= threshold]
        tol = float("inf") if len(passing) == len(grid) else (max(passing) if passing else 0.0)
        rows.append((tol, cos, x, y, accs))
    return sorted(rows, key=lambda r: (r[0], -r[1]))
