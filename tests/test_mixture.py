import numpy as np
import pytest
from sw_enose import synthetic_params
from sw_enose.mixture import concentration_vector, UnknownOdorant, BREATH_SULFUR_COVERAGE


def test_vector_places_concentrations_by_name():
    p = synthetic_params(odorants=("A", "B", "C"))
    assert np.allclose(concentration_vector(p, {"c": 2.0, "A": 1.0}), [1.0, 0.0, 2.0])


def test_unknown_odorant_is_refused_not_guessed():
    with pytest.raises(UnknownOdorant):
        concentration_vector(synthetic_params(odorants=("A", "B")), {"hydrogen sulfide": 1.0})


def test_negative_concentration_rejected():
    with pytest.raises(ValueError):
        concentration_vector(synthetic_params(odorants=("A", "B")), {"A": -1})


def test_breath_gases_documented_as_not_modellable():
    assert set(BREATH_SULFUR_COVERAGE) == {"hydrogen sulfide", "methyl mercaptan (methanethiol)", "dimethyl sulfide"}
