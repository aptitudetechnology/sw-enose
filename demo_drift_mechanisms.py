"""Why does Olsen normalisation help against sensor drift, and what else compensates drift?

Follow-up to demo_drift.py, where Olsen pre-processing beat a trivial L2 normalisation on
long-term drift (protocol A). Both experiments below were designed before running.

PART 1. Which ingredient of Olsen's equation carries the gain?
    PN = Rmax * x**n / (x**n + s**n + sigma**n),  x = activation * rate,
    s = m * (mean over channels of x) * 24 / 190   (lateral pooling; Olsen et al. 2010)
  Knock-outs, one at a time: no lateral pooling (m = 0); linear exponent (n = 1); no floor
  (sigma = 0); pooling only (n = 1, sigma = 0, i.e. x / (x + s)). Controls: per-channel log
  compression; per-sample L2. If "no lateral pooling" matches full Olsen, the gain is per-channel
  compression, not cross-channel normalisation.
  Also: does the expansion layer help when given Olsen-normalised (and standardised) input?

PART 2. Drift compensation.
  - Ratio to a reference sensor (as in the SpiroNose pipeline): log of each sensor's |dR| over a
    reference sensor's |dR|. The reference is chosen from the TRAINING batch only: the sensor
    whose |dR| has the smallest within-gas coefficient of variation.
  - Per-batch recalibration: standardise every batch with its OWN mean and sd (no labels used).
    This is transductive: it needs a batch of unlabelled measurements at once, and batches hold
    different mixes of gases, which can bias it. Flagged as such.
  - Olsen followed by per-batch recalibration.
Classifiers and protocols as in demo_drift.py. MODELLED processing on real sensor data.
"""
import os
import numpy as np

from sw_enose.bio import BiomimeticNose, SparseMemory
from sw_enose.data import synthetic_params
from sw_enose.sensors import OnOffFrontEnd, load_uci_drift

d = load_uci_drift(os.path.join(os.path.dirname(__file__), "data/uci_drift/raw"))
X, y, B = d["X"], d["gas"], d["batch"]
PROTOCOLS = {"A": [(1, k) for k in range(2, 11)], "B": [(k - 1, k) for k in range(2, 11)]}


def standardise(Xtr, Xte):
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return (Xtr - mu) / sd, (Xte - mu) / sd


def self_standardise(Z):
    sd = Z.std(0)
    return (Z - Z.mean(0)) / np.where(sd > 0, sd, 1.0)


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


CLF = {"NC": nearest_centroid, "5-NN": knn, "logreg": logistic}
NOSE = BiomimeticNose(synthetic_params(n_receptors=256, odorants=("A",)), neuron_noise=0.0, seed=0)


def olsen_variant(A, n=1.5, sigma=12.0, m=10.63, rate=250.0):
    orn = np.clip(A, 0, None) * rate
    s = m * orn.mean(1, keepdims=True) * 24 / 190.0
    x = orn ** n
    return 165.0 * x / (x + s ** n + sigma ** n)


_A = OnOffFrontEnd().fit(X[B == 1]).transform(X[B == 1][:5])
assert np.allclose(olsen_variant(_A), np.array([NOSE.normalise(a) for a in _A]))


def evaluate(make, classifiers=CLF):
    """make(Xtr, Xte) -> (Ftr, Fte) already in final form; returns {(protocol, clf): mean acc}."""
    out = {}
    for pname, pairs in PROTOCOLS.items():
        for cname, f in classifiers.items():
            accs = []
            for tr, te in pairs:
                mtr, mte = B == tr, B == te
                Ftr, Fte = make(X[mtr], X[mte])
                accs.append(float((f(Ftr, y[mtr], Fte) == y[mte]).mean()))
            out[(pname, cname)] = np.mean(accs)
    return out


def via_front_end(transform):
    def make(Xtr, Xte):
        fe = OnOffFrontEnd().fit(Xtr)
        return standardise(transform(fe.transform(Xtr)), transform(fe.transform(Xte)))
    return make


def table(title, rows):
    print(f"\n{title}")
    print(f"   {'':34s}" + "".join(f"{p + ' ' + c:>9s}" for p in PROTOCOLS for c in CLF))
    for name, r in rows.items():
        print(f"   {name:34s}" + "".join(f"{r[(p, c)]:9.3f}" for p in PROTOCOLS for c in CLF))


# ------------------------------------------------------------------ PART 1
l2n = lambda A: A / np.maximum(np.linalg.norm(A, axis=1, keepdims=True), 1e-12)
part1 = {
    "full Olsen": via_front_end(olsen_variant),
    "no lateral pooling (m = 0)": via_front_end(lambda A: olsen_variant(A, m=0.0)),
    "linear exponent (n = 1)": via_front_end(lambda A: olsen_variant(A, n=1.0)),
    "no floor (sigma = 0)": via_front_end(lambda A: olsen_variant(A, sigma=0.0)),
    "pooling only, x/(x+s)": via_front_end(lambda A: olsen_variant(A, n=1.0, sigma=0.0)),
    "control: log compression": via_front_end(lambda A: np.log1p(250.0 * A)),
    "control: L2 per sample": via_front_end(l2n),
    "control: log compression, then L2": via_front_end(lambda A: l2n(np.log1p(250.0 * A))),
    "control: front end only": via_front_end(lambda A: A),
}
table("PART 1: Olsen knock-outs (mean held-out accuracy; inputs standardised on training batch)",
      {k: evaluate(v) for k, v in part1.items()})


def expansion_memory(Ftr, ytr, Fte):
    H_tr, H_te = Ftr @ NOSE.W.T, Fte @ NOSE.W.T
    k = max(1, int(NOSE.sparsity * H_tr.shape[1]))
    code = lambda H: np.put_along_axis(np.zeros_like(H), np.argpartition(H, -k, 1)[:, -k:], 1.0, 1) or None
    def sparse(H):
        out = np.zeros_like(H)
        np.put_along_axis(out, np.argpartition(H, -k, axis=1)[:, -k:], 1.0, axis=1)
        return out
    Ctr, Cte = sparse(H_tr), sparse(H_te)
    mem = SparseMemory()
    for c in np.unique(ytr):
        mem.learn(c, Ctr[ytr == c])
    return np.array([mem.recognise(c)[0] for c in Cte])


exp_rows = {}
for name, make in (("Olsen -> expansion + memory", via_front_end(olsen_variant)),):
    exp_rows[name] = {}
    for pname, pairs in PROTOCOLS.items():
        accs = []
        for tr, te in pairs:
            mtr, mte = B == tr, B == te
            Ftr, Fte = make(X[mtr], X[mte])
            accs.append(float((expansion_memory(Ftr, y[mtr], Fte) == y[mte]).mean()))
        exp_rows[name][pname] = np.mean(accs)
print("\n   Expansion layer fed Olsen-normalised, standardised input: "
      + ", ".join(f"protocol {p} {v:.3f}" for p, v in exp_rows[name].items())
      + "  (compare 5-NN on the same input above)")

# ------------------------------------------------------------------ PART 2
ABS_DR = np.arange(1, 128, 8)                     # |dR| feature of each of the 16 sensors


def reference_ratio(Xtr, Xte):
    Rtr = np.abs(Xtr[:, ABS_DR]) + 1e-9
    gas_tr = y[np.flatnonzero(B == B[np.argmax(np.all(X == Xtr[0], axis=1))])][: len(Xtr)]
    return Rtr, Xte


def make_ratio(ytr_lookup):
    def make(Xtr, Xte):
        Rtr, Rte = np.abs(Xtr[:, ABS_DR]) + 1e-9, np.abs(Xte[:, ABS_DR]) + 1e-9
        ytr = ytr_lookup(Xtr)
        cv = np.mean([Rtr[ytr == c].std(0) / Rtr[ytr == c].mean(0) for c in np.unique(ytr)], axis=0)
        ref = int(np.argmin(cv))
        keep = [i for i in range(len(ABS_DR)) if i != ref]
        f = lambda R: np.log(R[:, keep] / R[:, [ref]])
        return standardise(f(Rtr), f(Rte))
    return make


def labels_of(Xtr):
    for b in range(1, 11):
        m = B == b
        if m.sum() == len(Xtr) and np.array_equal(X[m], Xtr):
            return y[m]
    raise RuntimeError("training batch not found")


def per_batch(transform):
    def make(Xtr, Xte):
        fe = OnOffFrontEnd().fit(Xtr)
        return self_standardise(transform(fe.transform(Xtr))), self_standardise(transform(fe.transform(Xte)))
    return make


part2 = {
    "baseline: raw, train-standardised": lambda Xtr, Xte: standardise(Xtr, Xte),
    "Olsen (from Part 1)": via_front_end(olsen_variant),
    "ratio to reference sensor": make_ratio(labels_of),
    "raw, per-batch recalibration *": lambda Xtr, Xte: (self_standardise(Xtr), self_standardise(Xte)),
    "Olsen + per-batch recalibration *": per_batch(olsen_variant),
}
table("PART 2: drift compensation  (* = transductive: uses the unlabelled test batch's statistics)",
      {k: evaluate(v) for k, v in part2.items()})
