"""Front ends for real sensor data: turn recorded sensor features into the non-negative channel
activations sw-enose's downstream stages expect, so the same biomimetic processing can run on
real gas-sensor recordings as well as on simulated receptors.

UCI Gas Sensor Array Drift at Different Concentrations (dataset 270):
  Vergara, A. (2012). Gas Sensor Array Drift at Different Concentrations [Dataset]. UCI Machine
  Learning Repository. https://doi.org/10.24432/C5MK6M. Licence on the page: CC BY 4.0, while the
  same page also says "exclusively for research purposes. Commercial purposes are fully
  excluded." The page asks that two papers be cited as well: Vergara et al., "Chemical gas sensor
  drift compensation using classifier ensembles"; and Rodriguez-Lujan, Fonollosa, Vergara, Homer &
  Huerta (2014), Chemometrics and Intelligent Laboratory Systems 130. The data are NOT stored in
  this repo: fetch with `scripts/fetch_uci_drift.sh` into data/uci_drift/ (gitignored).

  16 metal-oxide sensors, 6 gases, 13,910 measurements in 10 batches spanning 36 months. Only
  extracted features are distributed, 8 per sensor in this order: dR (steady-state resistance
  change), |dR| (normalised), EMA rising transient at alpha 0.001, 0.01, 0.1, EMA decaying
  transient at alpha 0.001, 0.01, 0.1. Decaying-transient features are negative.
"""
import os
import numpy as np

# Class codes 1..6 -> gas, as documented on UCI page 224. CAUTION: the per-batch count table on
# UCI page 270 is inconsistent with this order (its "Acetone" column matches code 1), and neither
# page's per-gas concentration ranges match the data exactly. The maximum concentration per code
# (600, 300, 1000, 300, 1000, 230 ppmv) matches this order for 4 of 6 gases and the count-table
# order for fewer, so this order is kept. Classification accuracy does not depend on the names;
# any statement about a SPECIFIC gas inherits this uncertainty.
DRIFT_GASES = ("Ethanol", "Ethylene", "Ammonia", "Acetaldehyde", "Acetone", "Toluene")
DRIFT_FEATURES = ("dR", "|dR|", "EMAi0.001", "EMAi0.01", "EMAi0.1", "EMAd0.001", "EMAd0.01",
                  "EMAd0.1")
DRIFT_N_SENSORS = 16
# Measurements per batch, from the UCI 270 page (sum 13,910); the loader checks against these.
DRIFT_BATCH_SIZES = (445, 1244, 1586, 161, 197, 2300, 3613, 294, 470, 3600)


def load_uci_drift(directory):
    """Parse batch1.dat .. batch10.dat (libsvm-like: 'gas;conc idx:value ...').

    Returns dict with X (n, 128) float, gas (n,) int 0..5, conc (n,) ppmv, batch (n,) int 1..10.
    Pure text parsing; nothing in the files is executed.
    """
    X, gas, conc, batch = [], [], [], []
    for b in range(1, 11):
        path = os.path.join(directory, f"batch{b}.dat")
        n_before = len(X)
        with open(path, encoding="ascii") as f:
            for line in f:
                parts = line.split()
                if not parts:
                    continue
                g, c = parts[0].split(";")
                row = np.zeros(128)
                for item in parts[1:]:
                    i, v = item.split(":")
                    row[int(i) - 1] = float(v)
                X.append(row)
                gas.append(int(g) - 1)
                conc.append(float(c))
                batch.append(b)
        got = len(X) - n_before
        if got != DRIFT_BATCH_SIZES[b - 1]:
            raise ValueError(f"batch {b}: {got} rows, the UCI page says {DRIFT_BATCH_SIZES[b - 1]}")
    return {"X": np.array(X), "gas": np.array(gas), "conc": np.array(conc),
            "batch": np.array(batch)}


class OnOffFrontEnd:
    """Recorded features -> non-negative channel activations in [0, 1].

    Each feature is divided by a robust scale (the `percentile` of its absolute value in the
    TRAINING data only) and split into an ON channel (positive part) and an OFF channel (negative
    part), like ON and OFF cells, then clipped to [0, 1]. 128 features -> 256 channels. Choices
    (95th percentile, ON/OFF split, clipping) are OURS and were fixed before any evaluation.
    """

    def __init__(self, percentile=95.0):
        self.percentile = percentile
        self.scale = None

    def fit(self, X):
        s = np.percentile(np.abs(np.asarray(X, float)), self.percentile, axis=0)
        self.scale = np.where(s > 0, s, 1.0)
        return self

    def transform(self, X):
        if self.scale is None:
            raise RuntimeError("fit the front end on training data first")
        z = np.asarray(X, float) / self.scale
        return np.clip(np.concatenate([z, -z], axis=-1), 0.0, 1.0)

    @property
    def n_channels(self):
        return 2 * len(self.scale)
