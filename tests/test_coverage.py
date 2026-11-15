import numpy as np
import pytest

from sw_enose import synthetic_params
from sw_enose.coverage import (NoCoverageInformation, comparable_odorants, describe,
                               restrict_to_tested, support)
from sw_enose.data import ReceptorParams


def params(known):
    """Receptors x odorants with a hand-written coverage mask; agonist wherever tested."""
    known = np.array(known, bool)
    return ReceptorParams(np.full(known.shape, 10.0), np.where(known, 1.0, 0.0), 1.0,
                          ("A", "B", "C"), "measured:test fixture", known,
                          tuple(f"r{i}" for i in range(known.shape[0])))


def test_support_counts_what_was_tested():
    p = params([[1, 1, 1], [1, 1, 0], [0, 0, 0]])
    s = support(p)
    assert s["receptors"] == 3 and s["fully_tested"] == 1
    assert s["partly_tested"] == 1 and s["untested"] == 1
    assert s["pairs_tested"] == 5 and s["pairs_total"] == 9


def test_support_narrows_to_the_odorants_being_compared():
    p = params([[1, 1, 0], [1, 1, 0], [0, 0, 1]])
    assert support(p, ("A", "B"))["fully_tested"] == 2
    assert support(p, ("A", "C"))["fully_tested"] == 0


def test_describe_states_the_numbers():
    text = describe(params([[1, 1, 1], [0, 0, 0]]))
    assert "3 of 6" in text and "1 of 2 receptors" in text


def test_restrict_keeps_only_fully_tested_receptors_and_says_so():
    p = params([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    t = restrict_to_tested(p, ("A", "B"))
    assert t.affinity.shape[0] == 2
    assert t.receptors == ("r0", "r2")
    assert "RESTRICTED" in t.provenance and t.provenance.startswith("measured:")


def test_restrict_any_is_looser_than_all():
    p = params([[1, 0, 0], [1, 1, 0], [0, 0, 1]])
    assert restrict_to_tested(p, ("A", "B"), how="any").affinity.shape[0] == 2
    assert restrict_to_tested(p, ("A", "B"), how="all").affinity.shape[0] == 1
    with pytest.raises(ValueError):
        restrict_to_tested(p, ("A", "B"), how="sideways")


def test_restrict_refuses_to_return_an_empty_array():
    p = params([[1, 0, 0], [1, 0, 0]])
    with pytest.raises(NoCoverageInformation):
        restrict_to_tested(p, ("A", "B"))


def test_invented_parameters_have_no_coverage_to_report():
    """synthetic_params carries no mask, so coverage questions must be refused, not answered with 0."""
    p = synthetic_params(n_receptors=4, odorants=("A", "B"))
    assert p.known is None
    for call in (lambda: support(p), lambda: describe(p), lambda: restrict_to_tested(p)):
        with pytest.raises(NoCoverageInformation):
            call()


def test_unknown_odorant_is_refused():
    with pytest.raises(KeyError):
        support(params([[1, 1, 1]]), ("A", "Z"))


def test_comparable_odorants_respects_the_threshold_and_sorts_by_support():
    p = params([[1, 1, 1], [1, 1, 0], [1, 1, 0]])
    got = comparable_odorants(p, min_receptors=2)
    assert got[0][:2] == ("A", "B") and got[0][2] == 3
    assert ("A", "C") not in [(a, b) for a, b, _ in got]        # only 1 receptor tested on both
    assert comparable_odorants(p, min_receptors=4) == []


def test_restriction_narrows_odorant_columns_so_headers_match_values():
    """Without this, column j of the result still means params.odorants[j], which silently
    produces tables whose headers and numbers disagree."""
    p = params([[1, 1, 1], [0, 1, 1]])
    t = restrict_to_tested(p, ("B", "C"))
    assert t.odorants == ("B", "C")
    assert t.affinity.shape == (2, 2) and t.known.shape == (2, 2)
    # the kept columns must be B and C, not A and B
    p2 = ReceptorParams(np.array([[1.0, 2.0, 3.0]]), np.ones((1, 3)), 1.0, ("A", "B", "C"),
                        "measured:ordered", np.ones((1, 3), bool), ("r0",))
    assert list(restrict_to_tested(p2, ("B", "C")).affinity[0]) == [2.0, 3.0]
    assert list(restrict_to_tested(p2, ("C", "A")).affinity[0]) == [3.0, 1.0]


def test_narrowing_can_be_turned_off_but_then_keeps_every_column():
    p = params([[1, 1, 1], [0, 1, 1]])
    t = restrict_to_tested(p, ("B", "C"), narrow_odorants=False)
    assert t.odorants == ("A", "B", "C") and t.affinity.shape[1] == 3


def test_restriction_does_not_mutate_the_original():
    p = params([[1, 1, 1], [1, 0, 1]])
    before = p.affinity.shape
    restrict_to_tested(p, ("A", "B"))
    assert p.affinity.shape == before and p.known.shape == before
