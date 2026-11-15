"""The acid series is the project's reference panel; these pin what makes it one."""
from pathlib import Path

import numpy as np
import pytest

from sw_enose.air import load_henry_csv
from sw_enose.coverage import restrict_to_tested, support
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_CARBONS, ACID_MEASURED_HENRY, ACID_SERIES, EVOCATIVE_PANEL

ROOT = Path(__file__).resolve().parent.parent
M2OR = ROOT / "data" / "m2or" / "repo" / "M2OR_20230428.csv"
HENRY = ROOT / "data" / "henry" / "sander_v5_subset.csv"


def test_panel_metadata_is_consistent():
    assert set(ACID_CARBONS) == set(ACID_SERIES)
    assert [ACID_CARBONS[a] for a in ACID_SERIES] == list(range(3, 11)), "C3..C10 in order"
    assert set(ACID_MEASURED_HENRY) <= set(ACID_SERIES)


def test_every_panel_member_has_a_henry_constant():
    t = load_henry_csv(HENRY, "measured:Sander v5.0.0 (2023)")
    for a in ACID_SERIES:
        assert np.isfinite(t.h_cp_at(a)), a
    assert t.missing == ()


def test_the_measured_henry_constants_run_out_at_c7():
    """C8-C10 are estimates only. Recorded as a test so the gap cannot be forgotten, since that is
    exactly where the long-chain receptors are tuned."""
    assert tuple(ACID_MEASURED_HENRY) == ACID_SERIES[:5]
    assert [ACID_CARBONS[a] for a in ACID_MEASURED_HENRY] == [3, 4, 5, 6, 7]


def test_solubility_falls_across_the_measured_part_of_the_series():
    t = load_henry_csv(HENRY, "measured:Sander v5.0.0 (2023)")
    h = [t.h_cp_at(a, t.temp_ref_k) for a in ACID_SERIES[:4]]      # C3..C6, all measured
    assert h == sorted(h, reverse=True), "longer chain should be less water-soluble"


@pytest.mark.skipif(not M2OR.exists(), reason="M2OR snapshot not fetched")
def test_acid_panel_has_the_joint_coverage_the_old_panel_lacked():
    p = build_params(M2OR, ACID_SERIES)
    t = restrict_to_tested(p, ACID_SERIES)
    s = support(t)
    assert s["pairs_tested"] == s["pairs_total"], "every pair in the restricted panel is measured"
    assert s["fully_tested"] >= 8
    assert support(build_params(M2OR, EVOCATIVE_PANEL))["fully_tested"] == 0


@pytest.mark.skipif(not M2OR.exists(), reason="M2OR snapshot not fetched")
def test_panel_carries_short_and_long_chain_receptors():
    """The panel is only useful if different receptors answer different chain lengths."""
    t = restrict_to_tested(build_params(M2OR, ACID_SERIES), ACID_SERIES)
    best = {}
    for i, r in enumerate(t.receptors):
        j = np.where(t.efficacy[i] > 0)[0]
        if len(j):
            best[str(r)] = ACID_CARBONS[t.odorants[j[np.argmin(t.affinity[i, j])]]]
    assert min(best.values()) <= 4 and max(best.values()) >= 9, \
        "need receptors tuned to both ends, or the panel cannot discriminate chain length"


@pytest.mark.skipif(not M2OR.exists(), reason="M2OR snapshot not fetched")
def test_or56a5_tuning_curve_is_monotone_in_chain_length():
    """A measured tuning curve, pinned: EC50 falls from C6 to C10. This is the shape a model has
    to reproduce, so a change that breaks it should fail here."""
    t = restrict_to_tested(build_params(M2OR, ACID_SERIES), ACID_SERIES)
    i = [str(r) for r in t.receptors].index("OR56A5")
    j = np.where(t.efficacy[i] > 0)[0]
    carbons = [ACID_CARBONS[t.odorants[k]] for k in j]
    ec50 = [t.affinity[i, k] for k in j]
    assert carbons == sorted(carbons)
    assert ec50 == sorted(ec50, reverse=True), f"expected a falling curve, got {list(zip(carbons, ec50))}"
