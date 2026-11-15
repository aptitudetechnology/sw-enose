"""Receptor parameters. Provenance is mandatory so a made-up number can never pass as a measurement."""
from dataclasses import dataclass
import json
import numpy as np


@dataclass(frozen=True)
class ReceptorParams:
    affinity: np.ndarray      # (n_receptors, n_odorants): half-saturation concentration K (arbitrary units); smaller = binds more strongly
    efficacy: np.ndarray      # (n_receptors, n_odorants): maximum response 0..1 (0 = no response)
    hill_n: float             # Hill coefficient
    odorants: tuple           # names, length n_odorants
    provenance: str           # "synthetic:<note>" or "measured:<citation>"
    known: np.ndarray = None  # (n_receptors, n_odorants) bool: True where the pair was actually tested; None = all invented
    receptors: tuple = ()     # receptor names, if known

    def __post_init__(self):
        if not (self.provenance.startswith("synthetic:") or self.provenance.startswith("measured:")):
            raise ValueError("provenance must start with 'synthetic:' or 'measured:'")
        if self.affinity.shape != self.efficacy.shape:
            raise ValueError("affinity and efficacy must have the same shape")
        if self.affinity.shape[1] != len(self.odorants):
            raise ValueError("one odorant name per column")
        if np.any(self.affinity <= 0):
            raise ValueError("affinity (K) must be positive")

    @property
    def modelled(self) -> bool:
        return self.provenance.startswith("synthetic:")


def synthetic_params(n_receptors=24, odorants=("A", "B", "C", "D"), seed=0) -> ReceptorParams:
    """Invented parameters for testing the machinery. Not chemistry."""
    rng = np.random.default_rng(seed)
    k = len(odorants)
    affinity = 10 ** rng.uniform(-1, 1, size=(n_receptors, k))
    efficacy = np.where(rng.random((n_receptors, k)) < 0.4, rng.uniform(0.3, 1.0, (n_receptors, k)), 0.0)
    return ReceptorParams(affinity, efficacy, 1.0, tuple(odorants), f"synthetic:seed={seed}")


def load_params(path) -> ReceptorParams:
    """Load a JSON file with keys affinity, efficacy, hill_n, odorants, provenance. Refuses missing provenance."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    if "provenance" not in d:
        raise ValueError("file has no provenance; refusing to load")
    return ReceptorParams(np.array(d["affinity"], float), np.array(d["efficacy"], float),
                          float(d["hill_n"]), tuple(d["odorants"]), d["provenance"])
