"""SVM baselines on the drift data, with tuning inside the training data only.

Needs scikit-learn, which the system Python lacks: run with the project venv,
  python3 -m venv .venv && .venv/bin/pip install numpy scipy pytest scikit-learn
  .venv/bin/python demo_drift_svm.py

Design fixed before running:
  Classifiers: linear SVM, RBF SVM, and tuned logistic regression (the earlier demos used fixed
    settings). Hyperparameters by stratified cross-validation INSIDE the training data only:
    linear SVM and logistic regression C in {0.01, 0.1, 1, 10, 100}; RBF SVM C in {1, 10, 100,
    1000} x gamma in {"scale", 0.001, 0.01, 0.1}.
  Inputs (each standardised on the training data): raw features; Olsen front end; generic
    log-compress-then-L2 front end (which tied Olsen in demo_drift_mechanisms.py).
  Settings: protocol A (train batch 1, test 2-10); protocol B (train k-1, test k); and few-sample
    recalibration (train on k labelled samples per gas from the test batch ALONE, k = 3, 5, 10,
    5 random draws, those samples excluded from scoring; CV folds = min(k, 5)).
"""
import os
import warnings
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.svm import SVC, LinearSVC

from sw_enose.bio import BiomimeticNose
from sw_enose.data import synthetic_params
from sw_enose.sensors import OnOffFrontEnd, load_uci_drift

warnings.filterwarnings("ignore")
d = load_uci_drift(os.path.join(os.path.dirname(__file__), "data/uci_drift/raw"))
X, y, B = d["X"], d["gas"], d["batch"]
NOSE = BiomimeticNose(synthetic_params(n_receptors=256, odorants=("A",)), neuron_noise=0.0, seed=0)
PROTOCOLS = {"A": [(1, k) for k in range(2, 11)], "B": [(k - 1, k) for k in range(2, 11)]}


def standardise(Ftr, Fte):
    mu, sd = Ftr.mean(0), Ftr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return (Ftr - mu) / sd, (Fte - mu) / sd


def raw(Xtr, Xte):
    return standardise(Xtr, Xte)


def olsen(Xtr, Xte):
    fe = OnOffFrontEnd().fit(Xtr)
    f = lambda Z: np.apply_along_axis(NOSE.normalise, 1, fe.transform(Z))
    return standardise(f(Xtr), f(Xte))


def log_l2(Xtr, Xte):
    fe = OnOffFrontEnd().fit(Xtr)
    def f(Z):
        L = np.log1p(250.0 * fe.transform(Z))
        return L / np.maximum(np.linalg.norm(L, axis=1, keepdims=True), 1e-12)
    return standardise(f(Xtr), f(Xte))


INPUTS = {"raw": raw, "Olsen": olsen, "log+L2": log_l2}
MODELS = {
    "linear SVM": (LinearSVC(max_iter=20000), {"C": [0.01, 0.1, 1, 10, 100]}),
    "RBF SVM": (SVC(kernel="rbf"), {"C": [1, 10, 100, 1000], "gamma": ["scale", 0.001, 0.01, 0.1]}),
    "logistic (tuned)": (LogisticRegression(max_iter=5000), {"C": [0.01, 0.1, 1, 10, 100]}),
}


def fit_predict(model, grid, Ftr, ytr, Fte, folds):
    folds = max(2, min(folds, np.bincount(ytr)[np.bincount(ytr) > 0].min()))
    g = GridSearchCV(model, grid, cv=StratifiedKFold(folds, shuffle=True, random_state=0), n_jobs=-1)
    g.fit(Ftr, ytr)
    return g.predict(Fte)


def protocol_scores(feat, model, grid):
    out = {}
    for pname, pairs in PROTOCOLS.items():
        accs = []
        for tr, te in pairs:
            mtr, mte = B == tr, B == te
            Ftr, Fte = feat(X[mtr], X[mte])
            accs.append(float((fit_predict(model, grid, Ftr, y[mtr], Fte, 5) == y[mte]).mean()))
        out[pname] = np.mean(accs)
    return out


def few_shot_scores(feat, model, grid, k, rng, draws=5):
    accs = []
    for te in range(2, 11):
        mte = B == te
        Xb, yb = X[mte], y[mte]
        for _ in range(draws):
            ref = np.concatenate([rng.choice(np.flatnonzero(yb == g), size=min(k, (yb == g).sum()),
                                             replace=False) for g in np.unique(yb)])
            keep = np.setdiff1d(np.arange(len(yb)), ref)
            Fref, Fall = feat(Xb[ref], Xb)
            accs.append(float((fit_predict(model, grid, Fref, yb[ref], Fall[keep], min(k, 5))
                               == yb[keep]).mean()))
    return np.mean(accs)


print("Mean held-out accuracy. Hyperparameters tuned by CV inside the training data only.")
print(f"   {'':18s}{'':8s}" + "".join(f"{c:>9s}" for c in ("A", "B", "k=3", "k=5", "k=10")))
for mname, (model, grid) in MODELS.items():
    for iname, feat in INPUTS.items():
        rng = np.random.default_rng(0)
        p = protocol_scores(feat, model, grid)
        f = [few_shot_scores(feat, model, grid, k, rng) for k in (3, 5, 10)]
        print(f"   {mname:18s}{iname:8s}" + "".join(f"{v:9.3f}" for v in (p["A"], p["B"], *f)), flush=True)
print("\n(earlier, untuned numpy logistic regression: raw A 0.442, B 0.753; few-shot raw k=3/10 0.839/0.950,"
      " Olsen 0.906/0.973)")
