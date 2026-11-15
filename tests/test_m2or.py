import os
import numpy as np
import pytest
from sw_enose.m2or import build_params, read_pairs

CSV = os.path.join(os.path.dirname(__file__), "..", "data", "m2or", "repo", "M2OR_20230428.csv")
pytestmark = pytest.mark.skipif(not os.path.exists(CSV), reason="M2OR data not downloaded (see sw_enose/m2or.py)")


def test_provenance_says_measured_and_states_assumptions():
    p = build_params(CSV, ("L-Carvone", "D-Carvone"))
    assert p.provenance.startswith("measured:M2OR")
    assert "ASSUMED efficacy=1" in p.provenance and "untested" in p.provenance


def test_reference_receptors_only():
    assert not any("_" in rec for rec, _ in read_pairs(CSV))


def test_known_mask_matches_data():
    p = build_params(CSV, ("L-Carvone", "D-Carvone"))
    assert p.known.shape == p.affinity.shape
    assert np.all(p.efficacy[~p.known] == 0)          # untested pairs carry no response
    assert np.all(p.known[p.efficacy > 0])            # every agonist pair was tested


def test_ec50_values_in_plausible_range():
    vals = [v for kind, v in read_pairs(CSV).values() if kind == "agonist"]
    assert min(vals) >= 1e-3 and max(vals) <= 1e5
