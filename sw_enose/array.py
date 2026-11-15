"""A virtual receptor array: concentrations in, a stream of responses out. All MODELLED."""
import numpy as np
from .data import ReceptorParams


class ReceptorArray:
    def __init__(self, params: ReceptorParams, noise=0.02, drift_per_step=0.0005, humidity_gain=0.3, seed=0):
        self.p = params
        self.noise, self.drift_per_step, self.humidity_gain = noise, drift_per_step, humidity_gain
        self.rng = np.random.default_rng(seed)
        self.t = 0
        # slow baseline drift per receptor, a random walk with a bias
        self._drift = np.zeros(params.affinity.shape[0])
        self._drift_dir = self.rng.choice([-1.0, 1.0], size=self._drift.shape)

    def clean_response(self, conc):
        """Noise-free response of each receptor to a concentration vector (length n_odorants).
        Each odorant drives a receptor through a Hill function; the receptor reports the strongest drive,
        capped at 1. This is a simple model, not a claim about real receptor mixtures."""
        conc = np.asarray(conc, float)
        x = (conc[None, :] / self.p.affinity) ** self.p.hill_n
        per = self.p.efficacy * x / (1.0 + x)
        return np.minimum(1.0, per.max(axis=1))

    def read(self, conc, humidity=0.0):
        """One reading: clean response + humidity offset + drift + noise. humidity in 0..1."""
        r = self.clean_response(conc)
        self._drift += self.drift_per_step * self._drift_dir + self.rng.normal(0, self.drift_per_step * 0.2, self._drift.shape)
        self.t += 1
        out = r + self.humidity_gain * humidity + self._drift + self.rng.normal(0, self.noise, r.shape)
        return out

    def stream(self, conc_series, humidity_series=None):
        """Readings for a sequence of concentration vectors. Returns array (T, n_receptors)."""
        T = len(conc_series)
        h = np.zeros(T) if humidity_series is None else np.asarray(humidity_series, float)
        return np.vstack([self.read(c, h[i]) for i, c in enumerate(conc_series)])

    @property
    def label(self):
        return "MODELLED; parameters " + self.p.provenance
