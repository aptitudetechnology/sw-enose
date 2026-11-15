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

# Dasgupta, Stevens & Navlakha, Science 2017 (PMID 29123069) model each of ~2000 expansion cells as
# sampling ~6 of ~50 projection neurons: a RATIO of about 12%, not an absolute count of 6. Carrying
# the 6 across to a smaller array is a mistake that quietly destroys the code: with 8 glomeruli a
# cell sampling 6 of them reads 75% of the input, so every cell sees nearly the same thing and none
# can be odorant-selective. Measured on the 8-receptor acid panel, an absolute fan_in of 6 scored
# 0.46 where the scaled rule scores 0.95, against a ceiling of 1.00 (sw_enose/separability.py).
DASGUPTA_FAN_IN_RATIO = 6 / 50
MIN_FAN_IN = 2          # OURS: below 2 a cell combines nothing, it just relabels one glomerulus.
# Not held out: on the 8-glomerulus acid panel this floor is what sets fan_in, and 2 is also where a
# scan on that same task peaked. The 12% ratio is Dasgupta's; the floor is a judgement call.


def default_fan_in(n_types: int) -> int:
    """Dasgupta's sampling ratio scaled to this array, floored at MIN_FAN_IN."""
    return int(min(max(round(DASGUPTA_FAN_IN_RATIO * n_types), MIN_FAN_IN), max(1, n_types - 1)))


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
                         "Science 2017, PMID 29123069): 2,000 cells, about 6 of ~50 inputs each, top 5% active. "
                         "We carry their SAMPLING RATIO (12%), not the absolute 6, because on a small array a "
                         "fan-in of 6 makes every cell read most of the input and the code stops discriminating"),
}


class BiomimeticNose:
    def __init__(self, params: ReceptorParams, neurons_per_type=50, neuron_noise=0.1,
                 adapt_tau=8.0, adapt_strength=0.6, recover_tau=4.0,
                 norm_sigma=0.1, n_expansion=2000, fan_in=None, sparsity=0.05, seed=0,
                 normalisation="olsen", max_orn_rate=250.0, kc_weights="lognormal",
                 kc_connectivity="fixed", kc_p=0.1):
        self.p = params
        self.rng = np.random.default_rng(seed)
        self.n_types = params.affinity.shape[0]
        self.neurons_per_type, self.neuron_noise = neurons_per_type, neuron_noise
        self.adapt_tau, self.adapt_strength, self.recover_tau = adapt_tau, adapt_strength, recover_tau
        self.norm_sigma = norm_sigma
        self.normalisation, self.max_orn_rate = normalisation, max_orn_rate
        self.sparsity = sparsity
        self.fan_in = default_fan_in(self.n_types) if fan_in is None else int(fan_in)
        # each expansion cell samples a few glomeruli at random (binary weights)
        W = np.zeros((n_expansion, self.n_types))
        for i in range(n_expansion):
            W[i, self.rng.choice(self.n_types, size=min(self.fan_in, self.n_types), replace=False)] = 1.0
        # Options for small arrays, where binary fixed fan-in makes most cells exact duplicates (8
        # glomeruli at fan-in 2 allow only 28 distinct cells). Their draws come from a SEPARATE
        # stream, so the default is bit-for-bit unchanged and an option alters only the wiring or
        # weights, never the noise that follows.
        #   kc_connectivity="bernoulli": each glomerulus-cell link exists independently with
        #       probability kc_p (Muezzinoglu et al. 2008 used 0.1); fan-in then varies by cell.
        #   kc_weights="uniform" / "lognormal": graded synaptic strengths, U(0,1) or
        #       lognormal(0, 1), instead of 1. Real Kenyon-cell claws differ in strength, and
        #       Litwin-Kumar et al. 2017 show the weight distribution matters; these exact
        #       distributions are OURS.
        if kc_connectivity not in ("fixed", "bernoulli") or kc_weights not in ("binary", "uniform", "lognormal"):
            raise ValueError("kc_connectivity must be 'fixed' or 'bernoulli'; "
                             "kc_weights 'binary', 'uniform' or 'lognormal'")
        alt = np.random.default_rng([seed, 1])
        if kc_connectivity == "bernoulli":
            W = (alt.random((n_expansion, self.n_types)) < kc_p).astype(float)
        if kc_weights == "uniform":
            W = W * alt.uniform(0.0, 1.0, W.shape)
        elif kc_weights == "lognormal":
            W = W * alt.lognormal(0.0, 1.0, W.shape)
        self.kc_weights, self.kc_connectivity, self.kc_p = kc_weights, kc_connectivity, kc_p
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
