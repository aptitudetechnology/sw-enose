import numpy as np
import pytest
from sw_enose import ReceptorArray, Pipeline, ReceptorParams, synthetic_params, load_params


def test_provenance_required():
    p = synthetic_params()
    with pytest.raises(ValueError):
        ReceptorParams(p.affinity, p.efficacy, 1.0, p.odorants, "trust me")


def test_loader_refuses_missing_provenance(tmp_path):
    f = tmp_path / "x.json"
    f.write_text('{"affinity": [[1.0]], "efficacy": [[1.0]], "hill_n": 1, "odorants": ["A"]}')
    with pytest.raises(ValueError):
        load_params(f)


def test_response_rises_with_concentration():
    arr = ReceptorArray(synthetic_params(seed=3))
    assert arr.clean_response([5, 0, 0, 0]).sum() > arr.clean_response([0.1, 0, 0, 0]).sum()


def test_distinct_odorants_classified_above_chance():
    p = synthetic_params(n_receptors=24, odorants=("A", "B", "C"), seed=4)
    arr = ReceptorArray(p, noise=0.02, seed=5)
    pipe = Pipeline().fit_baseline(arr.stream([[0, 0, 0]] * 20))
    mixes = {"A": [2, 0, 0], "B": [0, 2, 0], "C": [0, 0, 2]}
    pipe.fit({n: [arr.stream([c] * 10) for _ in range(5)] for n, c in mixes.items()})
    ok = sum(pipe.predict(arr.stream([c] * 10))[0] == n for n, c in mixes.items() for _ in range(20))
    assert ok / 60 > 0.9


def test_indistinguishable_odorants_stay_indistinguishable():
    """Two odorants whose receptor columns are identical cannot be separated, however good the pipeline."""
    base = synthetic_params(n_receptors=24, odorants=("A", "B", "C"), seed=6)
    aff, eff = base.affinity.copy(), base.efficacy.copy()
    aff[:, 1], eff[:, 1] = aff[:, 0], eff[:, 0]          # B looks exactly like A to every receptor
    p = ReceptorParams(aff, eff, 1.0, base.odorants, "synthetic:identical-columns")
    arr = ReceptorArray(p, noise=0.0, drift_per_step=0.0, seed=7)
    assert np.allclose(arr.clean_response([2, 0, 0]), arr.clean_response([0, 2, 0]))
    pipe = Pipeline().fit_baseline(arr.stream([[0, 0, 0]] * 5))
    pipe.fit({"A": [arr.stream([[2, 0, 0]] * 5)], "B": [arr.stream([[0, 2, 0]] * 5)]})
    _, d = pipe.predict(arr.stream([[2, 0, 0]] * 5))
    assert abs(d["A"] - d["B"]) < 1e-9


def test_label_says_modelled():
    assert "MODELLED" in ReceptorArray(synthetic_params()).label
