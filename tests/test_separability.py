"""The ceiling, and whether the pipeline reaches it."""
from pathlib import Path

import numpy as np
import pytest

from sw_enose import synthetic_params
from sw_enose.bio import DASGUPTA_FAN_IN_RATIO, MIN_FAN_IN, BiomimeticNose, default_fan_in
from sw_enose.coverage import restrict_to_tested
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_SERIES
from sw_enose.separability import (activation_profiles, describe_gap, nearest_centroid_accuracy,
                                   pairwise_similarity, stage_accuracies)

M2OR = Path(__file__).resolve().parent.parent / "data" / "m2or" / "repo" / "M2OR_20230428.csv"


def acids():
    return restrict_to_tested(build_params(M2OR, ACID_SERIES), ACID_SERIES)


# --- the fan-in rule, which is where the bug was ---

def test_fan_in_rule_reproduces_dasgupta_at_dasgupta_s_array_size():
    """~6 of ~50 is the published figure; the rule must give 6 back at 50."""
    assert default_fan_in(50) == 6
    assert DASGUPTA_FAN_IN_RATIO == pytest.approx(0.12)


def test_fan_in_scales_down_instead_of_reading_most_of_a_small_array():
    assert default_fan_in(8) == MIN_FAN_IN
    assert default_fan_in(8) < 6, "an absolute 6 would read 75% of an 8-glomerulus array"
    assert default_fan_in(24) == 3
    for n in range(2, 60):
        f = default_fan_in(n)
        assert f <= max(1, n - 1), "a cell must not read every glomerulus"
        # the floor of MIN_FAN_IN applies unless that cap forces it lower, as it does at n=2
        assert f >= MIN_FAN_IN or f == max(1, n - 1)
    assert default_fan_in(2) == 1, "with two glomeruli a cell can only read one of them"


def test_nose_uses_the_scaled_rule_by_default_and_honours_an_explicit_value():
    p = synthetic_params(n_receptors=8, odorants=("A", "B", "C"))
    assert BiomimeticNose(p).fan_in == default_fan_in(8)
    assert BiomimeticNose(p, fan_in=6).fan_in == 6
    assert BiomimeticNose(p, fan_in=6).W.sum(axis=1).max() == 6


# --- separability: where the bound is ---

def test_identical_odorant_columns_are_indistinguishable():
    """Rule 4, as a measurement: duplicate a column and the pair must score cosine 1.0."""
    p = synthetic_params(n_receptors=10, odorants=("A", "B"), seed=2)
    aff = np.column_stack([p.affinity[:, 0], p.affinity[:, 0]])
    eff = np.column_stack([p.efficacy[:, 0], p.efficacy[:, 0]])
    from sw_enose.data import ReceptorParams
    twin = ReceptorParams(aff, eff, 1.0, ("A", "A_copy"), "synthetic:twin columns")
    assert pairwise_similarity(twin)[0][0] == pytest.approx(1.0)


def test_disjoint_odorants_are_orthogonal():
    from sw_enose.data import ReceptorParams
    aff = np.array([[1.0, 1e6], [1e6, 1.0]])
    eff = np.array([[1.0, 0.0], [0.0, 1.0]])
    p = ReceptorParams(aff, eff, 1.0, ("A", "B"), "synthetic:disjoint")
    assert pairwise_similarity(p)[0][0] == pytest.approx(0.0)


def test_similarity_is_sorted_hardest_first_and_covers_every_pair():
    p = synthetic_params(n_receptors=8, odorants=("A", "B", "C", "D"), seed=4)
    sim = pairwise_similarity(p)
    assert len(sim) == 6
    assert [c for c, _, _ in sim] == sorted([c for c, _, _ in sim], reverse=True)


def test_activation_profiles_cover_every_odorant():
    p = synthetic_params(n_receptors=6, odorants=("A", "B"))
    prof = activation_profiles(p, conc_um=100.0)
    assert set(prof) == {"A", "B"} and all(len(v) == 6 for v in prof.values())


# --- the classifier helper ---

def test_nearest_centroid_is_perfect_on_separated_classes_and_chance_on_identical_ones():
    tr = {"a": np.array([[0.0, 1.0]] * 5), "b": np.array([[1.0, 0.0]] * 5)}
    assert nearest_centroid_accuracy(tr, tr, "euclid") == pytest.approx(1.0)
    same = {"a": np.array([[1.0, 1.0]] * 5), "b": np.array([[1.0, 1.0]] * 5)}
    assert nearest_centroid_accuracy(same, same, "euclid") <= 0.5
    with pytest.raises(ValueError):
        nearest_centroid_accuracy(tr, tr, "cosine")


# --- the gap itself ---

@pytest.mark.skipif(not M2OR.exists(), reason="M2OR snapshot not fetched")
def test_the_scaled_fan_in_closes_most_of_the_gap():
    """The regression this module exists to prevent: an absolute fan_in of 6 on a small array
    throws away more than half the separability the receptors provided."""
    t = acids()
    bad = stage_accuracies(t, noise=0.1, vary_conc=True, fan_in=6, n_train=30, n_test=60)
    good = stage_accuracies(t, noise=0.1, vary_conc=True, n_train=30, n_test=60)
    assert bad["gap"] > 0.35, "expected the old default to lose a lot"
    assert good["gap"] < 0.20, "expected the scaled rule to recover most of it"
    assert good["sparse_memory"] > bad["sparse_memory"] + 0.3


@pytest.mark.skipif(not M2OR.exists(), reason="M2OR snapshot not fetched")
def test_ceiling_is_a_lower_bound_never_below_a_later_stage():
    a = stage_accuracies(acids(), noise=0.1, vary_conc=True, n_train=30, n_test=60)
    assert a["ceiling_is_lower_bound"] is True
    for key in ("glomeruli", "glomeruli_l2", "normalised"):
        assert a["ceiling"] >= a[key] - 1e-9
    assert a["gap"] == pytest.approx(a["ceiling"] - a["sparse_memory"])
    assert a["chance"] == pytest.approx(1 / 8)


def test_describe_gap_distinguishes_the_two_verdicts():
    assert "AT THE ESTIMATED CEILING" in describe_gap({"gap": 0.01, "ceiling": 0.99,
                                                       "sparse_memory": 0.98})
    assert "BELOW THE CEILING" in describe_gap({"gap": 0.4, "ceiling": 0.99,
                                                "sparse_memory": 0.59})
