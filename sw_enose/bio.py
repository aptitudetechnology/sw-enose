"""Biomimetic processing stages, modelled on animal olfaction.

Each stage names the biology it copies and how sure we are of that biology. Sources were checked
on 15 Nov 2026; see sources/AUDIT_Olfactory-Modeling-Data-and-Evidence.md.
All outputs are MODELLED.

Stages, in the order a smell travels:
 1. Receptor binding with competition in mixtures (receptor neurons).
 2. Convergence: many neurons of the same receptor type pool onto one glomerulus.
 3. Adaptation: responses fade under a constant smell and recover when it goes.
 4. Divisive normalisation across glomeruli (lateral inhibition).
 5. Sparse expansion: a random projection to many cells, keeping only the most active
    (insect mushroom body / mammalian piriform cortex style).
"""
import numpy as np
from .data import ReceptorParams

BIOLOGY = {
    "competitive_binding": ("Odorants compete for the same binding site, so a mixture is not the sum of its parts.",
                            "ESTABLISHED for 12 of 15 human and mouse receptors in cultured cells; same model form as here "
                            "(Singh et al., PNAS 2019, PMID 31000595). Real EC50 and efficacy values not yet loaded"),
    "convergence": ("Neurons expressing the same receptor converge on one or a few glomeruli, pooling their signal.",
                    "PLAUSIBLE here: the anatomy is textbook, but convergence ratios were not found in verified sources; numbers invented"),
    "adaptation": ("Responses to a constant odour decline over time and recover after it is removed.",
                   "PLAUSIBLE here: the phenomenon is accepted, but no verified time constants were found; numbers invented"),
    "normalisation": ("Glomerular output is divided by total activity across glomeruli (lateral inhibition).",
                      "ESTABLISHED in the fruit-fly antennal lobe (Olsen, Bhandawat & Wilson, Neuron 2010, PMID 20435004); "
                      "we use their input-gain equations and constants (Rmax 165, sigma 12, m 10.63); the conversion from "
                      "receptor activation to firing rate (250 spikes/s) is invented, and these are fly numbers"),
    "sparse_expansion": ("Projection neurons connect randomly to many more cells, and only the most active few fire.",
                         "PLAUSIBLE: numbers as used in a modelling paper citing fly anatomy (Dasgupta, Stevens & Navlakha, "
                         "Science 2017, PMID 29123069): 2,000 cells, about 6 inputs each, top 5% active"),
}


class BiomimeticNose:
    def __init__(self, params: ReceptorParams, neurons_per_type=50, neuron_noise=0.1,
                 adapt_tau=8.0, adapt_strength=0.6, recover_tau=4.0,
                 norm_sigma=0.1, n_expansion=2000, fan_in=6, sparsity=0.05, seed=0,
                 normalisation="olsen", max_orn_rate=250.0):
        self.p = params
        self.rng = np.random.default_rng(seed)
        self.n_types = params.affinity.shape[0]
        self.neurons_per_type, self.neuron_noise = neurons_per_type, neuron_noise
        self.adapt_tau, self.adapt_strength, self.recover_tau = adapt_tau, adapt_strength, recover_tau
        self.norm_sigma = norm_sigma
        self.normalisation, self.max_orn_rate = normalisation, max_orn_rate
        self.sparsity = sparsity
        # each expansion cell samples a few glomeruli at random (binary weights)
        W = np.zeros((n_expansion, self.n_types))
        for i in range(n_expansion):
            W[i, self.rng.choice(self.n_types, size=min(fan_in, self.n_types), replace=False)] = 1.0
        self.W = W
        self.adapt_state = np.zeros(self.n_types)

    # 1. receptor binding, with competition
    def receptor_activation(self, conc):
        c = np.asarray(conc, float)
        x = (c[None, :] / self.p.affinity) ** self.p.hill_n          # occupancy drive per odorant
        return (self.p.efficacy * x).sum(axis=1) / (1.0 + x.sum(axis=1))

    # 2. convergence: many noisy neurons per type, averaged in the glomerulus
    def glomeruli(self, conc):
        a = self.receptor_activation(conc)
        spikes = a[:, None] + self.rng.normal(0, self.neuron_noise, (self.n_types, self.neurons_per_type))
        return np.clip(spikes, 0, None).mean(axis=1)

    # 3. adaptation: a slow variable that follows the input and is subtracted from it
    def adapt(self, g, dt=1.0):
        rising = g > self.adapt_state
        tau = np.where(rising, self.adapt_tau, self.recover_tau)
        self.adapt_state += (g - self.adapt_state) * (dt / tau)
        return np.clip(g - self.adapt_strength * self.adapt_state, 0, None)

    def reset(self):
        self.adapt_state[:] = 0.0

    # 4. divisive normalisation
    # Olsen, Bhandawat & Wilson, Neuron 2010 (PMID 20435004), input-gain model, Equations (2) and (6):
    #   PN = Rmax * ORN^1.5 / (ORN^1.5 + s^1.5 + sigma^1.5),   s = m * (sum of ORN rates over 24 types) / 190
    # with their simulation constants Rmax = 165 spikes/s, sigma = 12 spikes/s, m = 10.63 (fruit fly).
    # OUR assumptions: activation 0..1 is turned into a firing rate by max_orn_rate (invented, 250 spikes/s),
    # and the pool sum is rescaled to their 24 receptor types when our array has a different number.
    OLSEN = {"Rmax": 165.0, "sigma": 12.0, "m": 10.63, "n": 1.5, "pool_types": 24, "lfp_scale": 190.0}

    def normalise(self, g):
        if self.normalisation == "simple":
            return g / (self.norm_sigma + g.mean())
        o = self.OLSEN
        orn = np.clip(g, 0, None) * self.max_orn_rate
        s_ = o["m"] * (orn.mean() * o["pool_types"]) / o["lfp_scale"]
        x = orn ** o["n"]
        return o["Rmax"] * x / (x + s_ ** o["n"] + o["sigma"] ** o["n"])

    # 5. sparse expansion: keep the top fraction of cells active
    def sparse_code(self, pn):
        h = self.W @ pn
        k = max(1, int(self.sparsity * len(h)))
        out = np.zeros_like(h)
        out[np.argpartition(h, -k)[-k:]] = 1.0
        return out

    def sniff(self, conc, steps=1, adapt=True):
        """Present a smell for a number of time steps. Returns the sparse code at the last step."""
        pn = None
        for _ in range(steps):
            g = self.glomeruli(conc)
            if adapt:
                g = self.adapt(g)
            pn = self.normalise(g)
        return self.sparse_code(pn)

    @property
    def label(self):
        return "MODELLED (biomimetic stages); receptor parameters " + self.p.provenance


class SparseMemory:
    """Learn a smell as the set of expansion cells it activates; recognise by overlap (like a fly's mushroom body output)."""
    def __init__(self):
        self.memory = {}

    def learn(self, name, codes):
        self.memory[name] = np.mean(codes, axis=0)

    def recognise(self, code):
        scores = {n: float(code @ m) / max(1.0, code.sum()) for n, m in self.memory.items()}
        return max(scores, key=scores.get), scores
