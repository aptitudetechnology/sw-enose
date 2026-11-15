"""NumPy port of the Lazar, Liu & Yeh fly antennal-lobe example circuit.

Source: github.com/TK-21st/AntennalLobeLLY22, notebooks/example_circuit.py (last commit
28 Feb 2022), code for "The Functional Logic of Odor Information Processing in the Drosophila
Antennal Lobe" (Lazar, Liu & Yeh; bioRxiv Feb 2022). The original runs on NVIDIA CUDA only
(pycuda, scikit-cuda, and the in-house `neural` package, branch `al`). This port reproduces the
same equations, parameters, update order and clipping on the CPU, so that the circuit can be run
and checked against the recordings that ship with it.

What the port reproduces, taken from `neural`'s own stepping code rather than assumed:
  - forward Euler at the data's sample interval;
  - inside each model, `ode` assignments happen in program order (so `I = x1*gmax` uses the
    pre-update x1, and OTP's binding term uses the previous step's v), then the Euler update, then
    clipping of every state that has bounds;
  - across models, components update in the order the notebook adds them and read the newest
    value of their inputs, so the one feedback edge (Pre-LN onto the OSN axon terminal) sees the
    previous step;
  - every coupling uses the Poisson generators' per-step firing probability x = rate*dt, never
    the random spikes, so the circuit is deterministic and spikes are not simulated here.

Not reproduced: the random spike trains themselves (they affect nothing downstream) and the
`spike_rate`/`cx`/`y` bookkeeping states, which are never read.

Licence of the original code, which this port is derived from:

    BSD 3-Clause License
    Copyright (c) 2022, Tingkai Liu
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification, are
    permitted provided that the following conditions are met:
    1. Redistributions of source code must retain the above copyright notice, this list of
       conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of
       conditions and the following disclaimer in the documentation and/or other materials
       provided with the distribution.
    3. Neither the name of the copyright holder nor the names of its contributors may be used
       to endorse or promote products derived from this software without specific prior written
       permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
    OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
    IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import numpy as np

# ---------------------------------------------------------------- parameters, as in the notebook

OTP_DEFAULTS = dict(br=1.0, dr=1.0, gamma=0.215, b1=0.8, a1=45.0, a2=146.1, b2=117.2, a3=2.539,
                    b3=0.9096, kappa=8841.0, p=1.0, c=0.06546, Imax=85.0)
DISSOCIATION_RATE = 10.0            # notebook: "dr = 10. # dissociation rate fixed"

# Frequency-current polynomials of the noisy Connor-Stevens neurons, coefficient of I**k at [k].
CSN_OSN = (5.11085315, 3.44246777, 1.94672932e-01, -7.79496241e-03, 1.25880567e-04,
           -9.55636291e-07, 2.79621009e-09)                                    # PoissonCSN
CSN_LN = (-1.36299580e02, 2.25636389e01, -6.79691186e-01, 1.34591675e-02, -1.61863859e-04,
          1.14814892e-06, -4.41125703e-09, 7.06672200e-12)                     # PoissonCSN0
CSN_PN = (8.95839969e-01, -6.90178752e-01, 8.87442880e-01, -4.88554093e-02, 1.38994273e-03,
          -2.30971695e-05, 2.24914051e-07, -1.18820316e-09, 2.62834699e-12)    # PoissonCSN1

CIRCUIT = {
    "osn_axt": dict(a1=101.6, b1=3.12, k=1e5),
    "osn-to-preln": dict(a1=1.06, b1=15.5, gmax=3232.6),
    "osn-to-posteln": dict(a1=2.858053089117711, b1=1.4540529550164887, k=323039.26691518247,
                           a2=1.5028414134309191, b2=98.82274646620965, a3=8.583048572622092,
                           b3=5.9266873782378555, gmax=6.791877e+07),
    "osn-to-postiln": dict(a1=12.537946628371419, b1=3.5533912946105644, k=850654.7752613979,
                           a2=64.39457099988905, b2=14.7847156711102, a3=4.946413745118113,
                           b3=23.05951238421643, gmax=2.463306e+04),
    "osn_axt-to-pn": dict(a1=1.0, b1=100.0, gmax=1.273e5),
    "posteln-to-pn": dict(a1=1.0, b1=100.0, gmax=20.85),
    "postiln-to-pn": dict(a1=1.0, b1=100.0, gmax=89.5),
}


def _poly(coeffs, I):
    """Horner evaluation of sum_k coeffs[k] * I**k (same polynomial as the notebook's loop)."""
    out = np.zeros_like(I)
    for c in reversed(coeffs):
        out = out * I + c
    return out


def simulate(stimulus, affinity, dt, record_every=10, params=None):
    """Run the circuit on concentration waveforms.

    stimulus: (B, T) odorant concentration in ppm, one waveform per row.
    affinity: (N,) binding-rate affinity of this odorant for each of N receptor types.
    dt: integration step in seconds (the recordings' sample interval, 1e-4 s).
    record_every: keep every n-th step (rates are averaged over each block of n steps).

    Returns a dict of (B, T // record_every, N) arrays: firing rates in Hz for "osn", "pn",
    "pre_ln", "post_eln", "post_iln", and the three PN input currents.
    """
    stim = np.atleast_2d(np.asarray(stimulus, float))
    aff = np.asarray(affinity, float)
    B, T = stim.shape
    N = aff.size
    p = {**CIRCUIT, **(params or {})}
    o = dict(OTP_DEFAULTS, dr=DISSOCIATION_RATE)
    br = DISSOCIATION_RATE * aff                    # notebook: br=dr*aff, dr=dr

    z = lambda: np.zeros((B, N))
    # OTP states
    x1, x2, x3, v, uh, duh, I_otp = z(), z(), z(), z(), z(), z(), z()
    x_osn = z()                                     # OSN-BSG probability per step
    axt = z()                                       # OSN axon-terminal dDNP x1
    pre_syn, pre_syn_I = z(), z()
    x_pre = z()
    a2p, a2p_I = z(), z()
    pe1, pe2, pe3, pe_I = z(), z(), np.ones((B, N)), z()   # PostLNSyn x3 starts at 1.0
    x_pe = z()
    pe2p, pe2p_I = z(), z()
    pi1, pi2, pi3, pi_I = z(), z(), np.ones((B, N)), z()
    x_pi = z()
    pi2p, pi2p_I = z(), z()
    x_pn = z()

    n_rec = T // record_every
    keys = ("osn", "pn", "pre_ln", "post_eln", "post_iln", "I_osn_axt", "I_post_eln", "I_post_iln")
    rec = {k: np.zeros((B, n_rec, N)) for k in keys}
    acc = {k: z() for k in keys}

    def ionsyn(x, u, q):
        """IonSyn: I from the pre-update x, then Euler, then clip x to [0, 1]."""
        I = x * q["gmax"]
        x = np.clip(x + dt * (q["a1"] * u * (1.0 - x) - q["b1"] * x), 0.0, 1.0)
        return x, I

    def postlnsyn(a, b, c, u, q):
        I = a * q["gmax"]
        da = q["a1"] * b * (1.0 - a) - q["b1"] * a - q["k"] * a * c
        db = q["a2"] * u * (1.0 - b) - q["b2"] * b
        dc = q["a3"] * u * (1.0 - c) - q["b3"] * c
        return (np.clip(a + dt * da, 0, 1), np.clip(b + dt * db, 0, 1),
                np.clip(c + dt * dc, 0, 1), I)

    for i in range(T):
        s = stim[:, i:i + 1]                        # broadcast to every receptor (Repeat)
        # --- OSN-OTP, in the notebook's ode order
        d_x1 = br * v * (1.0 - x1) - o["dr"] * x1
        f = np.cbrt(x2 * x2) * np.cbrt(x3 * x3)
        d_x2 = o["a2"] * x1 * (1.0 - x2) - o["b2"] * x2 - o["kappa"] * f
        d_x3 = o["a3"] * x2 - o["b3"] * x3
        I_otp = o["Imax"] * x2 / (x2 + o["c"])
        d_uh = duh
        d_duh = -2.0 * o["a1"] * o["b1"] * duh + o["a1"] ** 2 * (s - uh)
        v = uh + o["gamma"] * duh
        x1 = np.clip(x1 + dt * d_x1, 0, 1)
        x2 = np.clip(x2 + dt * d_x2, 0, 1)
        x3 = np.clip(x3 + dt * d_x3, 0, 1000)
        uh = np.clip(uh + dt * d_uh, 0, 1e9)
        duh = duh + dt * d_duh
        v = np.clip(v, 0, 1e9)
        # --- OSN-BSG (PoissonCSN, unbounded x)
        x_osn = dt * _poly(CSN_OSN, I_otp)
        # --- OSN axon terminal (dDNP), inhibited by LAST step's Pre-LN
        q = p["osn_axt"]
        axt = np.clip(axt + dt * (q["a1"] * x_osn * (1.0 - axt) - q["b1"] * axt
                                  - q["k"] * axt * x_pre), 0, 1)
        # --- Pre-LN: synapse, global sum, Poisson generator
        pre_syn, pre_syn_I = ionsyn(pre_syn, axt, p["osn-to-preln"])
        pre_in = np.repeat(pre_syn_I.sum(axis=1, keepdims=True), N, axis=1)
        x_pre = np.clip(dt * _poly(CSN_LN, pre_in), 0, 1)
        # --- OSN axon terminal -> PN
        a2p, a2p_I = ionsyn(a2p, axt, p["osn_axt-to-pn"])
        # --- Post-eLN
        pe1, pe2, pe3, pe_I = postlnsyn(pe1, pe2, pe3, x_osn, p["osn-to-posteln"])
        x_pe = np.clip(dt * _poly(CSN_LN, pe_I), 0, 1)
        pe2p, pe2p_I = ionsyn(pe2p, x_pe, p["posteln-to-pn"])
        # --- Post-iLN
        pi1, pi2, pi3, pi_I = postlnsyn(pi1, pi2, pi3, x_osn, p["osn-to-postiln"])
        x_pi = np.clip(dt * _poly(CSN_LN, pi_I), 0, 1)
        pi2p, pi2p_I = ionsyn(pi2p, x_pi, p["postiln-to-pn"])
        # --- PN dendrite (Add) and PN generator
        x_pn = np.clip(dt * _poly(CSN_PN, a2p_I + pe2p_I + pi2p_I), 0, 1)

        acc["osn"] += x_osn
        acc["pn"] += x_pn
        acc["pre_ln"] += x_pre
        acc["post_eln"] += x_pe
        acc["post_iln"] += x_pi
        acc["I_osn_axt"] += a2p_I
        acc["I_post_eln"] += pe2p_I
        acc["I_post_iln"] += pi2p_I
        if (i + 1) % record_every == 0:
            j = (i + 1) // record_every - 1
            if j < n_rec:
                for k in keys:
                    scale = 1.0 / (record_every * dt) if not k.startswith("I_") else 1.0 / record_every
                    rec[k][:, j] = acc[k] * scale
                    acc[k][:] = 0.0
    return rec
