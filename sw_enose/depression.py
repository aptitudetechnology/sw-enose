"""Short-term synaptic depression at the receptor -> projection-neuron synapse.

Source: Nagel, Hong & Wilson, "Synaptic and circuit mechanisms promoting broadband transmission of
olfactory stimulus dynamics", Nat Neurosci 18:56-65 (2015), PMID 25485755, PMC4289142 (author
manuscript; Methods read). Their firing-rate form of the depression model, Eq. 3:

    dA/dt = -r * s(t) * A(t) + (1 - A(t)) / tau_A

A = fraction of synaptic resources available (1 = undepressed), s = presynaptic ORN firing rate in
spikes/ms, r = depression per spike (r = 1 - f in their spike-driven Eq. 1), tau_A = recovery time
constant. Here the transmitted drive is s * A, which then feeds the existing Olsen normalisation.

Their measured values, kept as constants with their provenance:
  f = 0.78, tau = 893 ms  -- Fig. 1c legend; fitted to EPSCs from 10 Hz electrical stimulation of
                             the antennal nerve, PNs in glomeruli DM6 and VM2 (n = 19), not DM4 and
                             not odour responses; no held-out evaluation reported.
  f = 0.77, tau = 1006 ms -- Results/Methods, fast (IMI-resistant) component, same preparation.

What OURS is: using the drive s*A as the INPUT to the Olsen 2010 equation. Olsen's constants were
fitted to real ORN->PN responses, which already contain whatever depression occurs at steady state,
so the measured depression applied in front of it double-counts: on the DM4 recordings the measured
values under-predict sustained firing (mean 25 Hz against 45 recorded), and the depression rate that
fits best is about half the measured one. See demo_depression.py.
"""
import numpy as np

NAGEL_2015_F, NAGEL_2015_TAU_MS = 0.78, 893.0
NAGEL_2015_FAST_F, NAGEL_2015_FAST_TAU_MS = 0.77, 1006.0


def depress(rate_hz, r=1 - NAGEL_2015_F, tau_ms=NAGEL_2015_TAU_MS, dt_ms=1.0):
    """Transmitted drive s*A for a firing-rate time course, by forward Euler.

    rate_hz: array (..., T, N): presynaptic firing rates in Hz, time on axis -2, sampled every
        dt_ms. A starts at 1 (fully recovered).
    Returns an array of the same shape, in Hz.
    """
    rate_hz = np.asarray(rate_hz, float)
    if r < 0 or tau_ms <= 0 or dt_ms <= 0:
        raise ValueError("r must be >= 0, tau_ms and dt_ms > 0")
    s = rate_hz / 1000.0                                   # spikes/ms, as in their equation
    A = np.ones(rate_hz.shape[:-2] + rate_hz.shape[-1:])
    out = np.empty_like(rate_hz)
    for t in range(rate_hz.shape[-2]):
        out[..., t, :] = rate_hz[..., t, :] * A
        A = np.clip(A + dt_ms * (-r * s[..., t, :] * A + (1.0 - A) / tau_ms), 0.0, 1.0)
    return out


def steady_state(rate_hz, r=1 - NAGEL_2015_F, tau_ms=NAGEL_2015_TAU_MS):
    """Fraction of resources available under a constant rate: A* = 1 / (1 + r * s * tau)."""
    return 1.0 / (1.0 + r * (np.asarray(rate_hz, float) / 1000.0) * tau_ms)
