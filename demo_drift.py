"""sw-enose on real gas-sensor recordings: the UCI drift dataset, held out by time.

Data: 16 metal-oxide sensors, 6 gases, 13,910 measurements in 10 batches over 36 months (see
sw_enose/sensors.py for licence and citations; fetch with scripts/fetch_uci_drift.sh). Sensors age
and drift, so a model trained early must still work months later: the standard test for this
dataset, and the failure the Sterk-group and hobby e-nose work both ran into.

Design fixed BEFORE running:
  Protocol A: train on batch 1, test on each of batches 2-10.
  Protocol B: train on batch k-1, test on batch k, for k = 2..10.
  Score: accuracy per test batch, and the mean over test batches.
  Plain baselines on standardised features (mean/sd from the training batch only): nearest
    centroid; 5-nearest-neighbours; multinomial logistic regression (L2 1e-4, 400 steps of
    full-batch gradient descent, step 0.5). Written in numpy: scikit-learn is not installed, so
    the usual SVM baseline is absent.
  sw-enose: OnOffFrontEnd (95th percentile scaling from the training batch; ON/OFF channels; 256
    channels in [0, 1]) -> Olsen normalisation (stage 4) -> sparse expansion with the current
    defaults (graded lognormal weights, fan-in scaled, top 5%, 2,000 cells) -> SparseMemory.
    Ablations: front end alone; + Olsen; + expansion without Olsen. No setting is tuned on any
    test batch.
"""
import os
import numpy as np

from sw_enose.bio import BiomimeticNose, SparseMemory
from sw_enose.data import synthetic_params
from sw_enose.sensors import DRIFT_GASES, OnOffFrontEnd, load_uci_drift

d = load_uci_drift(os.path.join(os.path.dirname(__file__), "data/uci_drift/raw"))
X, y, B = d["X"], d["gas"], d["batch"]


def standardise(Xtr, Xte):
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return (Xtr - mu) / sd, (Xte - mu) / sd


def nearest_centroid(Xtr, ytr, Xte):
    labels = np.unique(ytr)
    C = np.array([Xtr[ytr == c].mean(0) for c in labels])
    return labels[np.argmin(((Xte[:, None, :] - C[None]) ** 2).sum(-1), axis=1)]


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


NOSE = BiomimeticNose(synthetic_params(n_receptors=256, odorants=("A",)), neuron_noise=0.0, seed=0)


def olsen(A):
    return np.apply_along_axis(NOSE.normalise, 1, A)


def sparse(A):
    """NOSE.sparse_code for many rows at once (same top-k rule)."""
    H = A @ NOSE.W.T
    k = max(1, int(NOSE.sparsity * H.shape[1]))
    out = np.zeros_like(H)
    np.put_along_axis(out, np.argpartition(H, -k, axis=1)[:, -k:], 1.0, axis=1)
    return out


def memory(Ctr, ytr, Cte):
    mem = SparseMemory()
    for c in np.unique(ytr):
        mem.learn(c, Ctr[ytr == c])
    return np.array([mem.recognise(c)[0] for c in Cte])


def methods(Xtr, ytr, Xte):
    S_tr, S_te = standardise(Xtr, Xte)
    fe = OnOffFrontEnd().fit(Xtr)
    A_tr, A_te = fe.transform(Xtr), fe.transform(Xte)
    O_tr, O_te = olsen(A_tr), olsen(A_te)
    return {
        "nearest centroid (standardised)": nearest_centroid(S_tr, ytr, S_te),
        "5-nearest neighbours (standardised)": knn(S_tr, ytr, S_te),
        "logistic regression (standardised)": logistic(S_tr, ytr, S_te),
        "sw-enose front end + nearest centroid": nearest_centroid(A_tr, ytr, A_te),
        "sw-enose front end + Olsen + nearest centroid": nearest_centroid(O_tr, ytr, O_te),
        "sw-enose front end + expansion + memory": memory(sparse(A_tr), ytr, sparse(A_te)),
        "sw-enose full: + Olsen + expansion + memory": memory(sparse(O_tr), ytr, sparse(O_te)),
    }


assert np.array_equal(sparse(olsen(OnOffFrontEnd().fit(X[:50]).transform(X[:3]))),
                      np.array([NOSE.sparse_code(NOSE.normalise(a)) for a in
                                OnOffFrontEnd().fit(X[:50]).transform(X[:3])]))

for name, pairs in (("A: train on batch 1, test on batch k", [(1, k) for k in range(2, 11)]),
                    ("B: train on batch k-1, test on batch k", [(k - 1, k) for k in range(2, 11)])):
    table = {}
    for tr, te in pairs:
        mtr, mte = B == tr, B == te
        for m, pred in methods(X[mtr], y[mtr], X[mte]).items():
            table.setdefault(m, []).append(float((pred == y[mte]).mean()))
    print(f"\nProtocol {name}")
    print(f"   {'':46s}" + "".join(f"{te:>6d}" for _, te in pairs) + "    mean")
    for m, accs in table.items():
        print(f"   {m:46s}" + "".join(f"{a:6.2f}" for a in accs) + f"   {np.mean(accs):.3f}")
