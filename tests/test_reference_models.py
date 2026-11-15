"""Reimplementations of Raman 2006 and Muezzinoglu 2008: check the equations, not the results."""
import numpy as np
import pytest

from sw_enose.reference_models import (MuezzinogluAL, MuezzinogluMB, fisher_j,
                                       raman_connectivity, raman_shunting)


def test_raman_reduces_to_l1_normalisation_with_global_unit_weights_and_no_decay():
    """The paper's Eq. (6): with c_ki = 1 and D = 0, x_i = B G_i / sum_k G_k."""
    G = np.array([1.0, 2.0, 3.0, 4.0])
    x = raman_shunting(G, raman_connectivity(4, "global"), B=1.0, D=0.0)
    assert np.allclose(x, G / G.sum())


def test_raman_steady_state_satisfies_the_differential_equation():
    """Eq. (5) must be a fixed point of Eq. (3)."""
    rng = np.random.default_rng(1)
    G, c, B, D = rng.random(6), raman_connectivity(6, "uniform", rng), 1.0, 0.1
    x = raman_shunting(G, c, B, D)
    dxdt = -D * x + (B - x) * G - x * (G @ c)
    assert np.allclose(dxdt, 0.0, atol=1e-12)


def test_raman_connectivity_has_no_self_connections():
    for mode in ("global", "uniform"):
        assert np.all(np.diag(raman_connectivity(5, mode)) == 0)
    with pytest.raises(ValueError):
        raman_connectivity(3, "lattice")


def test_raman_global_inhibition_removes_concentration():
    G = np.array([0.1, 0.4, 0.2])
    c = raman_connectivity(3, "global")
    lo, hi = raman_shunting(G, c, D=0.0), raman_shunting(10 * G, c, D=0.0)
    assert np.allclose(lo, hi)


def test_fisher_j_rises_with_separation():
    labels = np.array([0] * 5 + [1] * 5)
    noise = np.random.default_rng(2).normal(0, 0.1, (10, 2))
    near = noise + np.where(labels[:, None] == 0, 0.0, 0.2)
    far = noise + np.where(labels[:, None] == 0, 0.0, 2.0)
    assert fisher_j(far, labels) > fisher_j(near, labels)


def test_al_without_connectivity_settles_to_its_driven_value():
    """With gE = gI = 0 each excitatory unit relaxes to K_E * g_inp * scale * S."""
    al = MuezzinogluAL(3, n_e=6, n_i=6, g_e=0.0, g_i=0.0, seed=0)
    G = np.array([[0.2, 0.5, 0.9]])
    x = al.snapshot(G, t_end=40 * float(al.b_e.max()))
    expect = al.k_e * al.g_inp * al.input_scale * G[0, al.src_e]
    assert np.allclose(x[0], expect, rtol=1e-3)


def test_al_covers_every_input_and_inhibition_lowers_activity():
    al = MuezzinogluAL(4, seed=1)
    assert set(al.src_e) | set(al.src_i) == {0, 1, 2, 3}
    G = np.full((1, 4), 0.5)
    free = al.set_conductances(0.0, 0.0).snapshot(G).sum()
    inhibited = al.set_conductances(1e-6, 3e-5).snapshot(G).sum()
    assert inhibited < free


def test_kenyon_layer_keeps_exactly_the_top_fraction():
    mb = MuezzinogluMB(n_in=10, n_classes=2, n_kc=1000, active_fraction=0.2, seed=0)
    mu = mb.kc(np.random.default_rng(3).random((5, 10)))
    assert np.all(mu.sum(axis=1) == 200)
    assert mb.c.sum(axis=0).min() >= 1, "every input must reach at least one Kenyon cell"


def test_kenyon_layer_learns_separable_classes():
    """Tested near the paper's regime (75 inputs). With very few inputs and p_c = 0.1 most cells get
    no input at all and half of each code is ties -- the small-array trap this repo keeps meeting."""
    rng = np.random.default_rng(4)
    protos = rng.random((3, 75))
    X = np.vstack([p + rng.normal(0, 0.05, (20, 75)) for p in protos])
    y = np.repeat([0, 1, 2], 20)
    mb = MuezzinogluMB(75, 3, n_kc=2000, seed=5).train(X[::2], y[::2], epochs=5)
    assert np.mean(mb.predict(X[1::2]) == y[1::2]) > 0.9
