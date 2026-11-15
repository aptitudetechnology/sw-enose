import os
import numpy as np
import pytest
from sw_enose.singh import fit_all, fit_curve, validate_on_mixtures, params_from_singh, ODORANTS

D = os.path.join(os.path.dirname(__file__), "..", "data", "singh2019", "raw")
DR, MIX = os.path.join(D, "MultiPlateDRResults.csv"), os.path.join(D, "BinaryTernary.csv")
need_data = pytest.mark.skipif(not os.path.exists(DR), reason="Singh 2019 raw data not downloaded (see sw_enose/singh.py)")


def test_fit_recovers_known_curve():
    c = np.array([4e-7, 1.2e-6, 3.7e-6, 1.11e-5, 3.33e-5, 1e-4, 3e-4])
    y = 0.8 * (c / 2e-5) / (1 + c / 2e-5)
    f = fit_curve(c, y, np.full_like(c, 0.02))
    assert abs(f["A"] - 0.8) < 0.05 and 1.5e-5 < f["EC50_M"] < 2.7e-5 and not f["unconstrained"]


def test_non_saturating_curve_is_flagged():
    c = np.array([4e-7, 1.2e-6, 3.7e-6, 1.11e-5, 3.33e-5, 1e-4, 3e-4])
    assert fit_curve(c, 100 * c, np.full_like(c, 0.001))["unconstrained"]


@need_data
def test_competitive_model_predicts_unseen_mixtures():
    """Fits use single odorants only; mixtures are held out. Loose bounds around what we observed."""
    v = validate_on_mixtures(DR, MIX)
    rmse = [d["rmse"] for d in v.values()]
    assert len(v) == 18
    assert np.median(rmse) < 0.15
    assert sum(d["rmse"] <= d["sum_rmse"] + 1e-9 for d in v.values()) >= 12   # at least as good as simple addition


@need_data
def test_params_state_what_is_unconstrained():
    p = params_from_singh(DR)
    assert p.provenance.startswith("measured:Singh") and "do not saturate" in p.provenance
    assert p.affinity.shape == (len(p.receptors), len(ODORANTS)) and p.known.all()
