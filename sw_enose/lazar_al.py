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


ALL_KEYS = ("osn", "pn", "pre_ln", "post_eln", "post_iln", "I_osn_axt", "I_post_eln",
            "I_post_iln")


def _rowwise(xp, value, B):
    """A parameter that is either one number for every row, or one number per batch row."""
    a = xp.asarray(value, dtype=float)
    if a.ndim == 0:
        return a
    if a.shape != (B,):
        raise ValueError(f"per-row parameter must have shape ({B},), got {a.shape}")
    return a.reshape(B, 1)


def simulate(stimulus, affinity, dt, record_every=10, params=None, otp=None, keys=ALL_KEYS,
             receptor=None, xp=np):
    """Run the circuit on concentration waveforms.

    stimulus: (B, T) odorant concentration in ppm, one waveform per row.
    affinity: (N,) binding-rate affinity of this odorant for each of N receptor types.
    dt: integration step in seconds (the recordings' sample interval, 1e-4 s).
    record_every: keep every n-th step (rates are averaged over each block of n steps).
    params: overrides for CIRCUIT, e.g. {"postiln-to-pn": {"gmax": 50.0}}. Any value may be a
        length-B array instead of a number, giving every batch row its own parameter set; that is
        how `sweep` runs many configurations at once.
    otp: overrides for OTP_DEFAULTS, scalars or length-B arrays.
    keys: which quantities to record (see ALL_KEYS). receptor: record only this receptor index,
        which keeps memory small in large sweeps.
    xp: the array module, numpy (default) or cupy for a GPU. The maths is identical.

    Returns a dict of numpy arrays shaped (B, T // record_every, N), or (B, T // record_every) if
    `receptor` is given: firing rates in Hz, currents in the circuit's units.
    """
    stim = xp.atleast_2d(xp.asarray(stimulus, dtype=float))
    aff = xp.asarray(affinity, dtype=float)
    B, T = stim.shape
    N = aff.size
    p = {name: dict(vals) for name, vals in CIRCUIT.items()}
    for name, over in (params or {}).items():
        if name not in p:
            raise KeyError(f"unknown circuit block {name!r}")
        p[name].update(over)
    p = {name: {k: _rowwise(xp, v, B) for k, v in vals.items()} for name, vals in p.items()}
    o = dict(OTP_DEFAULTS, dr=DISSOCIATION_RATE)
    o.update(otp or {})
    o = {k: _rowwise(xp, v, B) for k, v in o.items()}
    br = o["dr"] * aff                               # notebook: br = dr * aff
    unknown = set(keys) - set(ALL_KEYS)
    if unknown:
        raise KeyError(f"unknown keys {sorted(unknown)}")

    z = lambda: xp.zeros((B, N))
    x1, x2, x3, v, uh, duh = z(), z(), z(), z(), z(), z()
    axt, pre_syn, x_pre, a2p = z(), z(), z(), z()
    pe1, pe2, pe3 = z(), z(), xp.ones((B, N))        # PostLNSyn x3 starts at 1.0
    pe2p = z()
    pi1, pi2, pi3 = z(), z(), xp.ones((B, N))
    pi2p = z()

    n_rec = T // record_every
    width = N if receptor is None else 1
    sel = slice(None) if receptor is None else slice(receptor, receptor + 1)
    rec = {k: xp.zeros((B, n_rec, width)) for k in keys}
    acc = {k: xp.zeros((B, width)) for k in keys}
    to_rate = 1.0 / (record_every * dt)

    def ionsyn(x, u, q):
        """IonSyn: I from the pre-update x, then Euler, then clip x to [0, 1]."""
        I = x * q["gmax"]
        x = xp.clip(x + dt * (q["a1"] * u * (1.0 - x) - q["b1"] * x), 0.0, 1.0)
        return x, I

    def postlnsyn(a, b, c, u, q):
        I = a * q["gmax"]
        da = q["a1"] * b * (1.0 - a) - q["b1"] * a - q["k"] * a * c
        db = q["a2"] * u * (1.0 - b) - q["b2"] * b
        dc = q["a3"] * u * (1.0 - c) - q["b3"] * c
        return (xp.clip(a + dt * da, 0, 1), xp.clip(b + dt * db, 0, 1),
                xp.clip(c + dt * dc, 0, 1), I)

    def poly(coeffs, I):
        out = xp.zeros_like(I)
        for c in reversed(coeffs):
            out = out * I + c
        return out

    for i in range(T):
        s = stim[:, i:i + 1]                         # broadcast to every receptor (Repeat)
        # --- OSN-OTP, in the notebook's ode order
        d_x1 = br * v * (1.0 - x1) - o["dr"] * x1
        f = xp.cbrt(x2 * x2) * xp.cbrt(x3 * x3)
        d_x2 = o["a2"] * x1 * (1.0 - x2) - o["b2"] * x2 - o["kappa"] * f
        d_x3 = o["a3"] * x2 - o["b3"] * x3
        I_otp = o["Imax"] * x2 / (x2 + o["c"])
        d_uh = duh
        d_duh = -2.0 * o["a1"] * o["b1"] * duh + o["a1"] ** 2 * (s - uh)
        v = uh + o["gamma"] * duh
        x1 = xp.clip(x1 + dt * d_x1, 0, 1)
        x2 = xp.clip(x2 + dt * d_x2, 0, 1)
        x3 = xp.clip(x3 + dt * d_x3, 0, 1000)
        uh = xp.clip(uh + dt * d_uh, 0, 1e9)
        duh = duh + dt * d_duh
        v = xp.clip(v, 0, 1e9)
        # --- OSN-BSG (PoissonCSN, unbounded x)
        x_osn = dt * poly(CSN_OSN, I_otp)
        # --- OSN axon terminal (dDNP), inhibited by LAST step's Pre-LN
        q = p["osn_axt"]
        axt = xp.clip(axt + dt * (q["a1"] * x_osn * (1.0 - axt) - q["b1"] * axt
                                  - q["k"] * axt * x_pre), 0, 1)
        # --- Pre-LN: synapse, global sum (broadcast back to every unit), Poisson generator
        pre_syn, pre_syn_I = ionsyn(pre_syn, axt, p["osn-to-preln"])
        pre_in = xp.broadcast_to(pre_syn_I.sum(axis=1, keepdims=True), (B, N))
        x_pre = xp.clip(dt * poly(CSN_LN, pre_in), 0, 1)
        # --- OSN axon terminal -> PN
        a2p, a2p_I = ionsyn(a2p, axt, p["osn_axt-to-pn"])
        # --- Post-eLN
        pe1, pe2, pe3, pe_I = postlnsyn(pe1, pe2, pe3, x_osn, p["osn-to-posteln"])
        x_pe = xp.clip(dt * poly(CSN_LN, pe_I), 0, 1)
        pe2p, pe2p_I = ionsyn(pe2p, x_pe, p["posteln-to-pn"])
        # --- Post-iLN
        pi1, pi2, pi3, pi_I = postlnsyn(pi1, pi2, pi3, x_osn, p["osn-to-postiln"])
        x_pi = xp.clip(dt * poly(CSN_LN, pi_I), 0, 1)
        pi2p, pi2p_I = ionsyn(pi2p, x_pi, p["postiln-to-pn"])
        # --- PN dendrite (Add) and PN generator
        x_pn = xp.clip(dt * poly(CSN_PN, a2p_I + pe2p_I + pi2p_I), 0, 1)

        now = {"osn": x_osn, "pn": x_pn, "pre_ln": x_pre, "post_eln": x_pe, "post_iln": x_pi,
               "I_osn_axt": a2p_I, "I_post_eln": pe2p_I, "I_post_iln": pi2p_I}
        for k in keys:
            acc[k] += now[k][:, sel]
        if (i + 1) % record_every == 0:
            j = (i + 1) // record_every - 1
            if j < n_rec:
                for k in keys:
                    rec[k][:, j] = acc[k] * (1.0 / record_every if k.startswith("I_") else to_rate)
                    acc[k][:] = 0.0
    to_np = (lambda a: a.get()) if hasattr(xp, "asnumpy") else (lambda a: a)
    return {k: (to_np(rv)[:, :, 0] if receptor is not None else to_np(rv)) for k, rv in rec.items()}


def sweep(stimulus, affinity, dt, param_sets, otp_sets=None, **kw):
    """Run many circuit configurations at once, every one on every stimulus waveform.

    param_sets: list of `params` override dicts (as for `simulate`), one per configuration.
    otp_sets: optional list of `otp` override dicts, same length.
    Returns a dict of arrays shaped (n_configs, n_stimuli, T // record_every[, N]).
    """
    stim = np.atleast_2d(np.asarray(stimulus, float))
    S, C = stim.shape[0], len(param_sets)
    otp_sets = otp_sets or [{}] * C
    if len(otp_sets) != C:
        raise ValueError("otp_sets must match param_sets in length")

    def stack(dicts, defaults):
        names = {(blk, k) for d in dicts for blk, vals in d.items() for k in vals} if defaults is CIRCUIT \
            else {k for d in dicts for k in d}
        out = {}
        if defaults is CIRCUIT:
            for blk, k in names:
                col = [d.get(blk, {}).get(k, CIRCUIT[blk][k]) for d in dicts]
                out.setdefault(blk, {})[k] = np.repeat(col, S)
        else:
            base = dict(OTP_DEFAULTS, dr=DISSOCIATION_RATE)
            for k in names:
                out[k] = np.repeat([d.get(k, base[k]) for d in dicts], S)
        return out

    r = simulate(np.tile(stim, (C, 1)), affinity, dt, params=stack(param_sets, CIRCUIT),
                 otp=stack(otp_sets, None), **kw)
    return {k: v.reshape(C, S, *v.shape[1:]) for k, v in r.items()}
