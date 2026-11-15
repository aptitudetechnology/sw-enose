"""Stage 5 on small arrays: make the Kenyon cells differ, and find what made Muezzinoglu's better.

Background (demo_heldout.py): with fan-in 2, 8 glomeruli allow only 28 distinct binary cells, so
sw-enose's 2,000 expansion cells are a few large groups of exact duplicates, and tuning the active
fraction does not help on held-out panels. Two fixes are tested here, plus an attribution.

PART 1. Rule fixed BEFORE running. Candidates, all at the default 5% active:
    graded weights U(0,1); graded weights lognormal(0,1); Bernoulli wiring p=0.1 (binary);
    Bernoulli wiring p=0.1 with U(0,1) weights.
A candidate replaces the default only if it beats the default's mean accuracy (over noise
0.1/0.4/0.8) on EVERY panel -- the acid panel and two held-out panels; among those that do, the
best average across panels is chosen.

PART 2. Attribution on the acid panel: Muezzinoglu et al.'s Kenyon layer beat sw-enose's, and
differs in wiring (Bernoulli p=0.1 vs fixed fan-in), cell count, and readout (Hebbian counts from
random integer weights in [0,10] vs sw-enose's mean-code overlap). Full factorial at 5% active.

Same front end everywhere; concentration varies 20-2000 uM so only the pattern identifies the
odorant; 40 train / 80 test samples per odorant. MODELLED throughout.
"""
import itertools
import os
import numpy as np

from sw_enose import BiomimeticNose, SparseMemory
from sw_enose.coverage import restrict_to_tested
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_SERIES

CSV = os.path.join(os.path.dirname(__file__), "data/m2or/repo/M2OR_20230428.csv")
PANELS = {
    "acids": ACID_SERIES,
    "held-out A": ("coumarin", "Acetophenone", "L-Carvone", "4-chromanone", "D-Carvone", "Octanol",
                   "Dihydrojasmone"),
    "held-out B": ("coumarin", "Acetophenone", "L-Carvone", "4-chromanone"),
}
NOISES = (0.1, 0.4, 0.8)
SEED = 1


def glomerular_data(t, noise):
    """Train/test glomerular vectors. The expansion options draw from a separate stream, so these
    are identical whatever the stage-5 configuration -- every configuration sees the same samples."""
    nose = BiomimeticNose(t, neuron_noise=noise, seed=SEED)
    rng = np.random.default_rng(SEED + 99)
    n_od = len(t.odorants)
    out = []
    for n in (40, 80):
        G, y = [], []
        for j in range(n_od):
            for _ in range(n):
                c = np.zeros(n_od)
                c[j] = 10 ** rng.uniform(np.log10(20), np.log10(2000))
                G.append(nose.glomeruli(c))
                y.append(j)
        out += [np.array(G), np.array(y)]
    return out


def codes(t, noise, G, **kw):
    nose = BiomimeticNose(t, neuron_noise=noise, seed=SEED, **kw)
    return np.array([nose.sparse_code(nose.normalise(g)) for g in G])


def read_memory(Ctr, ytr, Cte, yte):
    mem = SparseMemory()
    for k in np.unique(ytr):
        mem.learn(k, Ctr[ytr == k])
    return float(np.mean([mem.recognise(c)[0] == y for c, y in zip(Cte, yte)]))


def read_hebbian(Ctr, ytr, Cte, yte, seed=4):
    """Muezzinoglu et al. 2008's readout: integer weights from [0, 10], +1 per active cell for the
    correct output, winner-take-all."""
    rng = np.random.default_rng(seed)
    w = rng.integers(0, 11, (len(np.unique(ytr)), Ctr.shape[1])).astype(float)
    for c, l in zip(Ctr, ytr):
        w[l] += c
    return float(np.mean(np.argmax(Cte @ w.T, axis=1) == yte))


data = {}
for name, od in PANELS.items():
    t = restrict_to_tested(build_params(CSV, od), od)
    data[name] = (t, {n: glomerular_data(t, n) for n in NOISES})

# ------------------------------------------------------------------ PART 1
CANDIDATES = {
    "default (fixed fan-in, binary)": {},
    "graded weights U(0,1)": {"kc_weights": "uniform"},
    "graded weights lognormal": {"kc_weights": "lognormal"},
    "Bernoulli wiring p=0.1": {"kc_connectivity": "bernoulli"},
    "Bernoulli wiring + U(0,1)": {"kc_connectivity": "bernoulli", "kc_weights": "uniform"},
}
part1 = {}
print("PART 1: sw-enose readout, 5% active. Mean accuracy over noise 0.1/0.4/0.8 "
      "(per-noise values in brackets)\n")
print(f"   {'':34s}" + "".join(f"{p:>27s}" for p in PANELS))
for cname, kw in CANDIDATES.items():
    row = {}
    for pname, (t, by_noise) in data.items():
        accs = []
        for n in NOISES:
            Gtr, ytr, Gte, yte = by_noise[n]
            accs.append(read_memory(codes(t, n, Gtr, **kw), ytr, codes(t, n, Gte, **kw), yte))
        row[pname] = accs
    part1[cname] = row
    print(f"   {cname:34s}" + "".join(
        f"{np.mean(a):9.3f} ({' '.join(f'{x:.2f}' for x in a)})" for a in row.values()))

base = {p: np.mean(v) for p, v in part1["default (fixed fan-in, binary)"].items()}
qualify = {c: np.mean([np.mean(v) for v in row.values()]) for c, row in part1.items()
           if c != "default (fixed fan-in, binary)" and all(np.mean(row[p]) > base[p] for p in PANELS)}
print("\n   Rule: replace the default only if a candidate beats it on every panel.")
if qualify:
    best = max(qualify, key=qualify.get)
    print(f"   Qualify: {', '.join(f'{c} ({v:.3f})' for c, v in qualify.items())}")
    print(f"   -> CHOSEN: {best}")
else:
    print("   No candidate qualifies; the default stands.")

# ------------------------------------------------------------------ PART 2
print("\nPART 2: what made Muezzinoglu's Kenyon layer better? Acid panel, 5% active.\n")
t, by_noise = data["acids"]
print(f"   {'wiring':10s} {'weights':8s} {'cells':>6s} {'readout':9s}" + "".join(f"  noise {n:<5}" for n in NOISES) + "   mean")
for wiring, weights, cells, readout in itertools.product(("fixed", "bernoulli"), ("binary", "uniform"),
                                                         (2000, 10000), ("memory", "hebbian")):
    kw = {"kc_connectivity": wiring, "kc_weights": weights, "n_expansion": cells}
    accs = []
    for n in NOISES:
        Gtr, ytr, Gte, yte = by_noise[n]
        Ctr, Cte = codes(t, n, Gtr, **kw), codes(t, n, Gte, **kw)
        accs.append((read_memory if readout == "memory" else read_hebbian)(Ctr, ytr, Cte, yte))
    tag = "   <- sw-enose default" if (wiring, weights, cells, readout) == ("fixed", "binary", 2000, "memory") \
        else ("   <- Muezzinoglu's combination" if (wiring, weights, cells, readout) == ("bernoulli", "binary", 10000, "hebbian") else "")
    print(f"   {wiring:10s} {weights:8s} {cells:6d} {readout:9s}" + "".join(f"  {a:<11.3f}" for a in accs) + f"  {np.mean(accs):.3f}{tag}")
