"""Baseline correction, normalisation and a nearest-centroid classifier."""
import numpy as np


class Pipeline:
    def __init__(self):
        self.baseline = None
        self.centroids = {}

    def fit_baseline(self, blank_stream):
        """Blank (no-odorant) readings. Subtracting their mean removes the offset."""
        self.baseline = np.asarray(blank_stream, float).mean(axis=0)
        return self

    def features(self, stream):
        s = np.asarray(stream, float)
        if self.baseline is not None:
            s = s - self.baseline
        s = s.mean(axis=0) if s.ndim == 2 else s
        n = np.linalg.norm(s)
        return s / n if n > 0 else s   # shape of the pattern, not its size

    def fit(self, labelled):
        """labelled: dict name -> list of streams."""
        for name, streams in labelled.items():
            self.centroids[name] = np.mean([self.features(s) for s in streams], axis=0)
        return self

    def predict(self, stream):
        f = self.features(stream)
        d = {n: float(np.linalg.norm(f - c)) for n, c in self.centroids.items()}
        best = min(d, key=d.get)
        return best, d
