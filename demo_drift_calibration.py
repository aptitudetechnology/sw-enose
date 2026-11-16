"""Drift compensation from a few labelled reference samples (non-transductive).

demo_drift_mechanisms.py found that recalibrating each batch on its own statistics is the
strongest long-term fix, but that needs a whole batch of unlabelled measurements at once. Here a
batch is instead corrected from a FEW LABELLED reference samples, as an instrument is recalibrated
with calibration gas. The reference samples are then excluded from scoring.

Design fixed before running:
  S1 (all gases): k reference samples of each gas present (k = 1, 3, 5, 10); per-feature affine
     correction a + b*x fitted by least squares mapping the batch's reference-class means onto the
     training-class means (offset only if fewer than two classes).
  S2 (one reference gas): k samples of class 1 only (one of the five gases present in every
     batch; chosen in advance); per-feature offset correction.
  Each with and without adding the corrected reference samples to the training set.
  Comparators: no correction; transductive per-batch standardisation (needs the whole batch).
  Classifiers: logistic regression, 5-NN. Inputs: raw (standardised on training) and Olsen
  front end (standardised on training). Protocol A (train batch 1, test 2-10) and B (k-1 -> k).
  Mean over 5 random draws of the reference samples.
"""
import os
import numpy as np

from sw_enose.bio import BiomimeticNose
from sw_enose.data import synthetic_params
from sw_enose.sensors import OnOffFrontEnd, load_uci_drift

d = load_uci_drift(os.path.join(os.path.dirname(__file__), "data/uci_drift/raw"))
X, y, B = d["X"], d["gas"], d["batch"]
PROTOCOLS = {"A": [(1, k) for k in range(2, 11)], "B": [(k - 1, k) for k in range(2, 11)]}
NOSE = BiomimeticNose(synthetic_params(n_receptors=256, odorants=("A",)), neuron_noise=0.0, seed=0)
REF_GAS = 0
DRAWS = 5


def standardise(Ftr, Fte):
    mu, sd = Ftr.mean(0), Ftr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return (Ftr - mu) / sd, (Fte - mu) / sd


def self_standardise(Z):
    sd = Z.std(0)
    return (Z - Z.mean(0)) / np.where(sd > 0, sd, 1.0)


def knn(Xtr, ytr, Xte, k=5):
    out = np.empty(len(Xte), int)
    for i in range(0, len(Xte), 500):
        dd = ((Xte[i:i + 500, None, :] - Xtr[None]) ** 2).sum(-1)
        nn = np.argpartition(dd, k, axis=1)[:, :k]
        out[i:i + 500] = [np.bincount(ytr[r], minlength=6).argmax() for r in nn]
    return out


def logistic(Xtr, ytr, Xte, l2=1e-4, steps=400, lr=0.5):
    A = np.c_[Xtr, np.ones(len(Xtr))]
    W = np.zeros((A.shape[1], 6))
    Y = np.eye(6)[ytr]
    for _ in range(steps):
        Z = A @ W
        P = np.exp(Z - Z.max(1, keepdims=True))
        P /= P.sum(1, keepdims=True)
        W -= lr * (A.T @ (P - Y) / len(A) + l2 * W)
    return np.argmax(np.c_[Xte, np.ones(len(Xte))] @ W, axis=1)


CLF = {"logreg": logistic, "5-NN": knn}


def raw_features(Xtr, Xte):
    return standardise(Xtr, Xte)


def olsen_features(Xtr, Xte):
    fe = OnOffFrontEnd().fit(Xtr)
    o = lambda Z: np.apply_along_axis(NOSE.normalise, 1, fe.transform(Z))
    return standardise(o(Xtr), o(Xte))


def affine_correction(Fte, ref_idx, ref_y, Ftr, ytr):
    """Per-feature a + b*x mapping the batch's reference-class means onto training-class means."""
    classes = [c for c in np.unique(ref_y) if (ytr == c).any()]
    src = np.array([Fte[ref_idx][ref_y == c].mean(0) for c in classes])
    dst = np.array([Ftr[ytr == c].mean(0) for c in classes])
    if len(classes) < 2:
        return Fte + (dst - src)[0]
    sx, sy = src - src.mean(0), dst - dst.mean(0)
    b = (sx * sy).sum(0) / np.where((sx ** 2).sum(0) > 1e-12, (sx ** 2).sum(0), np.inf)
    b = np.where(np.isfinite(b) & (b > 0), b, 1.0)
    a = dst.mean(0) - b * src.mean(0)
    return a + b * Fte


def offset_correction(Fte, ref_idx, ref_y, Ftr, ytr):
    return Fte + (Ftr[ytr == REF_GAS].mean(0) - Fte[ref_idx].mean(0))


def run(features, scenario, k, augment, rng):
    res = {}
    for pname, pairs in PROTOCOLS.items():
        for cname, clf in CLF.items():
            accs = []
            for tr, te in pairs:
                mtr, mte = B == tr, B == te
                Ftr, Fte = features(X[mtr], X[mte])
                ytr, yte = y[mtr], y[mte]
                for _ in range(DRAWS):
                    if scenario == "none":
                        ref = np.array([], int)
                        G = Fte
                    else:
                        gases = np.unique(yte) if scenario == "S1" else [REF_GAS]
                        ref = np.concatenate([rng.choice(np.flatnonzero(yte == g), size=min(k, (yte == g).sum()),
                                                         replace=False) for g in gases])
                        fix = affine_correction if scenario == "S1" else offset_correction
                        G = fix(Fte, ref, yte[ref], Ftr, ytr)
                    keep = np.setdiff1d(np.arange(len(yte)), ref)
                    Xfit, yfit = (np.r_[Ftr, G[ref]], np.r_[ytr, yte[ref]]) if augment and len(ref) else (Ftr, ytr)
                    accs.append(float((clf(Xfit, yfit, G[keep]) == yte[keep]).mean()))
                    if scenario == "none":
                        break
            res[(pname, cname)] = np.mean(accs)
    return res


def run_transductive(features):
    res = {}
    for pname, pairs in PROTOCOLS.items():
        for cname, clf in CLF.items():
            accs = []
            for tr, te in pairs:
                mtr, mte = B == tr, B == te
                Ftr, Fte = features(X[mtr], X[mte])
                accs.append(float((clf(self_standardise(Ftr), y[mtr], self_standardise(Fte)) == y[mte]).mean()))
            res[(pname, cname)] = np.mean(accs)
    return res


rng = np.random.default_rng(0)
cols = [(p, c) for p in PROTOCOLS for c in CLF]
for fname, features in (("raw features", raw_features), ("Olsen front end", olsen_features)):
    print(f"\n{fname}: mean held-out accuracy (reference samples excluded from scoring)")
    print(f"   {'':44s}" + "".join(f"{p + ' ' + c:>10s}" for p, c in cols))
    rows = {"no correction": run(features, "none", 0, False, rng)}
    for k in (1, 3, 5, 10):
        rows[f"S1 all gases, k={k}, affine"] = run(features, "S1", k, False, rng)
        rows[f"S1 all gases, k={k}, affine + add to training"] = run(features, "S1", k, True, rng)
    for k in (3, 10):
        rows[f"S2 one gas, k={k}, offset"] = run(features, "S2", k, False, rng)
    rows["transductive per-batch standardisation *"] = run_transductive(features)
    for name, r in rows.items():
        print(f"   {name:44s}" + "".join(f"{r[c]:10.3f}" for c in cols))
print("\n* needs the whole unlabelled test batch at once; shown as a reference point, not a deployable method.")


# ------------------------------------------------------------------ control added after the run
# Question raised by the results above: is the OLD training data helping at all? Train on the k
# recent reference samples ALONE (features fitted on them too), score the rest of the batch.
def references_alone(features, k, rng):
    res = {}
    for pname, pairs in PROTOCOLS.items():
        for cname, clf in CLF.items():
            accs = []
            for _, te in pairs:
                mte = B == te
                Xb, yte = X[mte], y[mte]
                for _ in range(DRAWS):
                    ref = np.concatenate([rng.choice(np.flatnonzero(yte == g),
                                                     size=min(k, (yte == g).sum()), replace=False)
                                          for g in np.unique(yte)])
                    keep = np.setdiff1d(np.arange(len(yte)), ref)
                    Fref, Fall = features(Xb[ref], Xb)
                    f = (lambda a, b_, c: knn(a, b_, c, k=min(5, len(a)))) if cname == "5-NN" else clf
                    accs.append(float((f(Fref, yte[ref], Fall[keep]) == yte[keep]).mean()))
            res[(pname, cname)] = np.mean(accs)
    return res


print("\nControl: train on the recent reference samples ALONE (no older data)")
print(f"   {'':24s}" + "".join(f"{p + ' ' + c:>10s}" for p, c in cols))
for fname, features in (("raw", raw_features), ("Olsen", olsen_features)):
    for k in (3, 5, 10):
        r = references_alone(features, k, rng)
        print(f"   {fname:6s} k={k:<2d} per gas      " + "".join(f"{r[c]:10.3f}" for c in cols))
print("""
Reading it: a few labelled reference samples from the current batch transform accuracy, and the
old training data adds nothing -- ten recent samples per gas ALONE match or beat old data plus
the same samples. After months of drift the old data is stale. The practical lesson is to
recalibrate on fresh labelled samples, not to correct old ones. Olsen pre-processing makes that
few-sample learning more efficient (k=3: logreg 0.84 -> 0.91, 5-NN 0.53 -> 0.73). Not yet tested:
whether the generic log-then-L2 recipe, which tied Olsen elsewhere, gives the same gain.
Calibrating with a single reference gas is unreliable: it helps a little on long-term drift and
hurts between neighbouring batches.""")
