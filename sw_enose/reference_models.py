"""Reimplementations of two published bio-inspired e-nose models, for comparison with sw-enose.

Neither paper released code (checked 15 Nov 2026), so these are written from the papers alone.
Each function names the equation it implements. Where the paper is ambiguous or leaves a detail
to supplementary material we do not have, the choice made here is marked OURS and is part of
what is being compared, not a property of the original.

Both models are driven by the SAME front end as sw-enose -- measured receptor EC50s, competitive
binding, and same-type convergence (`BiomimeticNose.glomeruli`) -- so the comparison isolates the
downstream processing. That is not how either paper was run: both took metal-oxide (MOX) sensor
signals directly. Results here say how their processing behaves on this input, not how well
their systems performed on their own data.

1. Raman & Gutierrez-Osuna, "Concentration normalization with a model of gain control in the
   olfactory bulb", Sensors and Actuators B 116 (2006) 36-42, doi:10.1016/j.snb.2005.11.078.
   Full text read.

2. Muezzinoglu, Vergara, Huerta, Nowotny, Rulkov, Abarbanel, Selverston & Rabinovich,
   "Artificial Olfactory Brain for Mixture Identification", NIPS 21 (2008) 1121-1128.
   Full text read; supplementary material (which holds MB implementation details and the
   sample network topology) NOT available.
"""
import numpy as np


# --------------------------------------------------------------------------- Raman 2006

def raman_connectivity(n, mode="global", rng=None):
    """Lateral shunting weights c_ki, self-connections disabled (c_ii = 0).

    The paper's Eq. (4) draws c_ki ~ U(0,1) for units within a lattice distance sqrt(M)/r of each
    other on a 20x20 SOM, and 0 otherwise; its "global" case (small r) connects every pair, and
    its Fig. 7 analysis uses c_ki = 1 for all k, i. sw-enose glomeruli have no lattice -- with 8
    receptor types there is nothing for a SOM to arrange -- so only the global cases transfer:
      mode="global":   c_ki = 1 for all k != i            (the paper's Fig. 7 setting)
      mode="uniform":  c_ki ~ U(0,1) for all k != i       (Eq. 4 with r small enough to be global)
    """
    if mode == "global":
        c = np.ones((n, n))
    elif mode == "uniform":
        rng = np.random.default_rng(0) if rng is None else rng
        c = rng.uniform(0.0, 1.0, (n, n))
    else:
        raise ValueError("mode must be 'global' or 'uniform'")
    np.fill_diagonal(c, 0.0)
    return c


def raman_shunting(G, c, B=1.0, D=0.1):
    """Steady state of Grossberg shunting lateral inhibition, the paper's Eq. (5):

        x_i = B * G_i / (D + G_i + sum_{k != i} c_ki * G_k)

    B = 1 and D = 0.1 are the values given for the paper's Fig. 5. G may be (n,) or (samples, n).
    With c_ki = 1 and D = 0 this reduces to the L1 normalisation B * G_i / sum_k G_k (Eq. 6).
    """
    G = np.clip(np.asarray(G, float), 0.0, None)
    lateral = G @ c                               # sum_k c_ki G_k, indexed by i (c[k, i])
    return B * G / (D + G + lateral)


def fisher_j(X, labels):
    """The paper's separability measure, Eq. (6): J = trace(S_B) / trace(S_W).

    Note the paper's S_B (Eq. 8) is NOT weighted by class size; that is kept here.
    """
    X = np.asarray(X, float)
    labels = np.asarray(labels)
    mu = X.mean(axis=0)
    sw = sb = 0.0
    for q in np.unique(labels):
        Xq = X[labels == q]
        mq = Xq.mean(axis=0)
        sw += float(((Xq - mq) ** 2).sum())
        sb += float(((mq - mu) ** 2).sum())
    return sb / sw if sw > 0 else float("inf")


# --------------------------------------------------------------------------- Muezzinoglu 2008

class MuezzinogluAL:
    """Wilson-Cowan-like antennal-lobe rate model, the paper's Section 2.2:

        beta_E dx_i/dt = K_E * Theta(-sum_j w^EI_ij y_j + g_inp S^E_i) - x_i + mu^E_i
        beta_I dy_i/dt = K_I * Theta( sum_j w^IE_ij x_j + g_inp S^I_i) - y_i + mu^I_i

    with Theta the unit ramp, Bernoulli connectivity w^XY = g_Y with probability p^XY, and each
    unit driven by exactly one input chosen at random so that every input is covered.

    Values from the paper: N_E = N_I = 75, g_inp = 1e-2, p^IE = p^EI = 0.5, (g_E, g_I) tuned per
    problem by brute-force sweep (their best pairs were near (1e-6, 9e-6) for resistance inputs of
    order 1e4-1e5 ohms), a readout "snapshot" of the excitatory population x at a chosen time.

    OURS, because the paper is ambiguous or the detail is in its unavailable supplement:
      - "drawn from exponential distributions with lambda_K = 7.5 and lambda_beta = 0.5" is read
        as MEAN 7.5 and MEAN 0.5 (the reading under which time constants are shorter than the 1 s
        odour period). Read as rates the means would be 0.13 and 2.
      - beta is floored at `beta_floor` so that explicit Euler is stable; the paper used adaptive
        Runge-Kutta 5(6) at tolerance 1e-15 and needed no floor.
      - the AL noise term (variance 1e-4) is omitted: it is negligible against inputs of this
        scale and the glomerular stage already supplies noise.
      - inputs are static (sw-enose has no time course), so the snapshot is taken after
        `t_end` seconds of constant input. The paper's AL is designed to exploit sensor
        TRANSIENTS; a static task cannot show that benefit, and this comparison does not.
      - `input_scale` maps glomerular activity (0..~1) onto the paper's resistance-like range.
    """

    def __init__(self, n_inputs, n_e=75, n_i=75, g_inp=1e-2, p=0.5, g_e=1e-6, g_i=9e-6,
                 mean_k=7.5, mean_beta=0.5, beta_floor=0.01, input_scale=1e5, seed=0):
        rng = np.random.default_rng(seed)
        self.n_e, self.n_i, self.g_inp, self.input_scale = n_e, n_i, g_inp, input_scale
        self.k_e = rng.exponential(mean_k, n_e)
        self.k_i = rng.exponential(mean_k, n_i)
        self.b_e = np.maximum(rng.exponential(mean_beta, n_e), beta_floor)
        self.b_i = np.maximum(rng.exponential(mean_beta, n_i), beta_floor)
        self.mask_ei = rng.random((n_e, n_i)) < p          # I -> E
        self.mask_ie = rng.random((n_i, n_e)) < p          # E -> I
        # each unit gets exactly one input, assigned so that every input is used
        def assign(n):
            idx = np.concatenate([rng.permutation(n_inputs),
                                  rng.integers(0, n_inputs, max(0, n - n_inputs))])[:n]
            return rng.permutation(idx)
        self.src_e, self.src_i = assign(n_e), assign(n_i)
        self.set_conductances(g_e, g_i)

    def set_conductances(self, g_e, g_i):
        self.g_e, self.g_i = float(g_e), float(g_i)
        self.w_ei = self.mask_ei * self.g_i                 # weight from I units onto E units
        self.w_ie = self.mask_ie * self.g_e                 # weight from E units onto I units
        return self

    def snapshot(self, G, t_end=1.0, dt=None):
        """Excitatory activity after t_end seconds of constant input G, shape (samples, n_e)."""
        G = np.atleast_2d(np.asarray(G, float)) * self.input_scale
        s_e, s_i = G[:, self.src_e], G[:, self.src_i]
        dt = dt if dt is not None else 0.2 * float(min(self.b_e.min(), self.b_i.min()))
        x = np.zeros((G.shape[0], self.n_e))
        y = np.zeros((G.shape[0], self.n_i))
        relu = lambda u: np.maximum(u, 0.0)
        for _ in range(int(np.ceil(t_end / dt))):
            dx = (self.k_e * relu(-(y @ self.w_ei.T) + self.g_inp * s_e) - x) / self.b_e
            dy = (self.k_i * relu(x @ self.w_ie.T + self.g_inp * s_i) - y) / self.b_i
            x, y = x + dt * dx, y + dt * dy
        return x


class MuezzinogluMB:
    """Mushroom-body classifier, the paper's Section 3:

      - Kenyon cells: mu_j = Heaviside(sum_i c_ji x_i - theta), c_ji ~ Bernoulli(p_c = 0.1);
        gain control admits only the top n_KC = N_KC / 5 most-excited cells.
      - Output units: z_l = Heaviside(sum_j w_lj mu_j - theta_LB), winner-take-all.
      - Learning: weights start at random integers in [0, 10]; for a training input with label l
        the correct output is forced on and w_lj is incremented by 1 for every active KC.

    Paper values: N_KC = 10,000, p_c = 0.1, top N_KC/5 active, p+ = p- = 1. Their check that the
    input-to-KC mapping is "bijective" is not specified further; here we only ensure every input
    feeds at least one KC. The printed update rule reads "w + 1 when z = 1, mu = 1; and 0,
    otherwise", which taken literally would reset weights to zero; we read it (OURS) as "w
    otherwise", the standard form of this rule.
    """

    def __init__(self, n_in, n_classes, n_kc=10_000, p_c=0.1, active_fraction=0.2, seed=0):
        rng = np.random.default_rng(seed)
        self.c = (rng.random((n_kc, n_in)) < p_c).astype(float)
        for i in np.where(self.c.sum(axis=0) == 0)[0]:     # every input reaches some KC
            self.c[rng.integers(n_kc), i] = 1.0
        self.k = max(1, int(round(active_fraction * n_kc)))
        self.w = rng.integers(0, 11, (n_classes, n_kc)).astype(float)

    def kc(self, X):
        h = np.atleast_2d(X) @ self.c.T
        out = np.zeros_like(h)
        top = np.argpartition(h, -self.k, axis=1)[:, -self.k:]
        np.put_along_axis(out, top, 1.0, axis=1)
        return out

    def train(self, X, labels, epochs=1):
        mu = self.kc(X)
        for _ in range(epochs):
            for m, l in zip(mu, labels):
                self.w[l] += m
        return self

    def predict(self, X):
        return np.argmax(self.kc(X) @ self.w.T, axis=1)
