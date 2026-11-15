import numpy as np
from sw_enose import BiomimeticNose, SparseMemory, synthetic_params, BIOLOGY


def nose(**kw):
    return BiomimeticNose(synthetic_params(n_receptors=40, odorants=("A", "B", "C"), seed=11), seed=12, **kw)


def test_every_stage_states_its_evidence():
    for name, (what, status) in BIOLOGY.items():
        assert status.split(":")[0].split(" ")[0] in {"ESTABLISHED", "PLAUSIBLE", "UNTESTED"}, name


def test_mixture_is_not_the_sum():
    n = nose()
    a, b, ab = n.receptor_activation([3, 0, 0]), n.receptor_activation([0, 3, 0]), n.receptor_activation([3, 3, 0])
    assert np.all(ab <= a + b + 1e-12) and np.any(ab < a + b - 1e-3)


def test_convergence_reduces_noise():
    few, many = nose(neurons_per_type=1), nose(neurons_per_type=200)
    sd = lambda n: np.std([n.glomeruli([2, 0, 0]) for _ in range(200)], axis=0).mean()
    assert sd(many) < sd(few) / 4


def test_adaptation_fades_and_recovers():
    n = nose(neuron_noise=0.0)
    first = n.adapt(n.glomeruli([3, 0, 0])).sum()
    for _ in range(40):
        late = n.adapt(n.glomeruli([3, 0, 0])).sum()
    assert late < 0.7 * first
    for _ in range(40):
        n.adapt(n.glomeruli([0, 0, 0]))
    assert n.adapt(n.glomeruli([3, 0, 0])).sum() > 0.9 * first


def test_normalisation_keeps_pattern_across_strength():
    n = nose(neuron_noise=0.0)
    lo, hi = n.normalise(n.glomeruli([1, 0, 0])), n.normalise(n.glomeruli([10, 0, 0]))
    cos = lo @ hi / np.linalg.norm(lo) / np.linalg.norm(hi)
    assert cos > 0.9


def test_sparse_code_recognises_smells():
    n = nose()
    mem = SparseMemory()
    for name, c in {"A": [2, 0, 0], "B": [0, 2, 0], "C": [0, 0, 2]}.items():
        mem.learn(name, [n.sniff(c, adapt=False) for _ in range(10)])
    ok = sum(mem.recognise(n.sniff(c, adapt=False))[0] == name
             for name, c in {"A": [2, 0, 0], "B": [0, 2, 0], "C": [0, 0, 2]}.items() for _ in range(20))
    assert ok / 60 > 0.9


def test_sparse_code_is_sparse():
    code = nose().sniff([2, 0, 0], adapt=False)
    assert 0 < code.mean() <= 0.06


def test_olsen_normalisation_matches_paper_equation():
    """Equation (2) with s from Equation (6), checked by hand for one input."""
    n = nose(neuron_noise=0.0)
    g = np.zeros(n.n_types); g[0] = 0.2            # one glomerulus at 50 spikes/s, the rest silent
    orn = 50.0
    s_ = 10.63 * (orn / n.n_types * 24) / 190.0
    expect = 165.0 * orn ** 1.5 / (orn ** 1.5 + s_ ** 1.5 + 12.0 ** 1.5)
    assert abs(n.normalise(g)[0] - expect) < 1e-9


def test_lateral_input_suppresses_a_weak_response():
    """Olsen 2010: activity in other glomeruli reduces a glomerulus's output (input gain control)."""
    n = nose(neuron_noise=0.0)
    alone = np.zeros(n.n_types); alone[0] = 0.1
    crowd = np.full(n.n_types, 0.6); crowd[0] = 0.1
    assert n.normalise(crowd)[0] < 0.5 * n.normalise(alone)[0]
