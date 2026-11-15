from pathlib import Path

import numpy as np
import pytest

from sw_enose import BiomimeticNose, synthetic_params
from sw_enose.uncertainty import (RESHAPES_CODE, SINGH_RELATIVE_EFFICACY, _rank_correlation,
                                  between_smell_overlap, code_overlap, efficacy_sensitivity,
                                  panel_codes, panel_recognition, relative_efficacy_sample,
                                  resample_efficacy, seed_floor, stage_sensitivity, sweep_summary,
                                  verdict)

SINGH_RAW = Path(__file__).resolve().parent.parent / "data" / "singh2019" / "raw" / "MultiPlateDRResults.csv"


def small():
    return synthetic_params(n_receptors=12, odorants=("A", "B", "C"), seed=3)


def panel(p):
    return {"a": [3.0, 0.0, 0.0], "b": [0.0, 3.0, 0.0]}


# --- the measured efficacy spread ---

def test_stored_efficacy_sample_matches_a_recomputation_from_the_raw_data():
    """The stored sample is a transcription; this is the check that it is the right one."""
    if not SINGH_RAW.exists():
        pytest.skip("Singh raw data not fetched; see sw_enose/singh.py for the URL")
    assert sorted(relative_efficacy_sample(SINGH_RAW)) == sorted(SINGH_RELATIVE_EFFICACY)


def test_efficacy_spread_is_wide_enough_to_contradict_the_assumed_one():
    s = np.asarray(SINGH_RELATIVE_EFFICACY)
    assert s.min() < 0.1 and s.max() == pytest.approx(1.0)
    assert np.median(s) < 0.6, "if the median were near 1.0, assuming 1.0 would be harmless"


# --- redrawing efficacy ---

def test_resample_changes_agonists_but_never_creates_one():
    p = small()
    q = resample_efficacy(p, np.random.default_rng(0))
    agonist = p.efficacy > 0
    assert np.array_equal(q.efficacy == 0, p.efficacy == 0), "a non-agonist must stay a non-agonist"
    assert np.any(q.efficacy[agonist] != p.efficacy[agonist])
    assert np.all(q.efficacy[agonist] > 0) and np.all(q.efficacy <= 1.0)


def test_resample_records_itself_in_the_provenance_and_leaves_the_original_alone():
    p = small()
    before = p.efficacy.copy()
    q = resample_efficacy(p, np.random.default_rng(0))
    assert "REDRAWN" in q.provenance and q.provenance.startswith(p.provenance.split(":")[0])
    assert np.array_equal(p.efficacy, before)


# --- the metrics ---

def test_code_overlap_is_one_for_itself_and_zero_for_disjoint():
    a = np.array([1.0, 1.0, 0.0, 0.0])
    assert code_overlap(a, a) == pytest.approx(1.0)
    assert code_overlap(a, np.array([0.0, 0.0, 1.0, 1.0])) == pytest.approx(0.0)
    assert code_overlap(a, np.array([1.0, 0.0, 1.0, 0.0])) == pytest.approx(0.5)


def test_recognition_is_perfect_on_different_smells_and_chance_on_identical_ones():
    p = small()
    n = BiomimeticNose(p, neuron_noise=0.0, seed=1)
    assert panel_recognition(n, panel(p), trials=5, repeats=3) == pytest.approx(1.0)
    same = {"x": [3.0, 0.0, 0.0], "y": [3.0, 0.0, 0.0]}
    assert panel_recognition(n, same, trials=10, repeats=3) <= 0.75


def test_different_smells_give_near_orthogonal_codes():
    """The control that makes any overlap number readable."""
    p = small()
    c = between_smell_overlap(p, panel(p), seed=1)
    assert c["mean"] < 0.25 and c["chance"] < 0.25


def test_panel_codes_are_sparse_and_reset_between_smells():
    p = small()
    n = BiomimeticNose(p, neuron_noise=0.0, seed=1)
    codes = panel_codes(n, panel(p), steps=3, adapt=True)
    assert set(codes) == {"a", "b"}
    assert all(0 < c.mean() <= 0.06 for c in codes.values())
    # presenting in the other order must give the same codes, which only holds if state is reset
    again = panel_codes(n, {k: panel(p)[k] for k in ("b", "a")}, steps=3, adapt=True)
    assert np.array_equal(codes["a"], again["a"])


def test_seed_floor_reports_a_spread():
    f = seed_floor(small(), panel(small()), seeds=(0, 1), trials=5, neuron_noise=0.2)
    assert f["min"] <= f["mean"] <= f["max"] and f["spread"] == pytest.approx(f["max"] - f["min"])


# --- the verdicts ---

def test_rank_correlation_detects_order():
    assert _rank_correlation([1, 2, 3, 4]) == pytest.approx(1.0)
    assert _rank_correlation([4, 3, 2, 1]) == pytest.approx(-1.0)
    assert _rank_correlation([1, 1, 1]) == 0.0


def test_a_sweep_with_no_spread_is_reported_as_untested_not_as_no_effect():
    base = {"min": 0.7, "max": 0.8, "spread": 0.1, "mean": 0.75}
    s = sweep_summary([{"value": v, "recognition": 0.73, "overlap": 1.0} for v in (1, 2, 3)],
                      base, "recover_tau")
    assert "NOT EXERCISED" in s["verdict"]
    assert "absence of evidence" in s["verdict"]


def test_an_ordered_trend_bigger_than_reseeding_is_called_out():
    base = {"min": 0.70, "max": 0.80, "spread": 0.10, "mean": 0.75}
    rows = [{"value": v, "recognition": r, "overlap": 1.0}
            for v, r in zip((1, 5, 20, 50), (0.55, 0.70, 0.72, 0.85))]
    s = sweep_summary(rows, base, "neurons_per_type")
    assert s["trend"] == "increasing" and s["verdict"].startswith("MATTERS")


def test_a_small_unordered_wobble_does_not_count():
    base = {"min": 0.70, "max": 0.80, "spread": 0.10, "mean": 0.75}
    rows = [{"value": v, "recognition": r, "overlap": 1.0}
            for v, r in zip((1, 2, 3, 4), (0.75, 0.73, 0.76, 0.74))]
    assert sweep_summary(rows, base, "x")["verdict"].startswith("DOES NOT MATTER")


def test_verdict_flags_a_collapse_below_the_baseline():
    base = {"min": 0.70, "max": 0.80, "spread": 0.10, "mean": 0.75}
    assert verdict([0.50, 0.60, 0.75], base).startswith("MATTERS")
    assert verdict([0.74, 0.75, 0.76], base).startswith("DOES NOT MATTER")


# --- the two sensitivity runs, kept small ---

def test_efficacy_sensitivity_reports_both_questions_against_a_baseline():
    p = small()
    r = efficacy_sensitivity(p, panel(p), draws=3, seeds=(0, 1), trials=5, neuron_noise=0.1)
    assert len(r["recognition"]) == 3 and len(r["overlap"]) == 3
    assert r["recognition"][0] <= r["recognition"][1] <= r["recognition"][2]
    assert 0.0 <= r["overlap"][0] <= 1.0
    assert set(r["baseline"]) >= {"min", "max", "spread", "mean"}


def test_stage_sensitivity_sweeps_and_skips_overlap_where_the_code_is_reshaped():
    p = small()
    s = stage_sensitivity(p, panel(p), {"neurons_per_type": [1, 20], "sparsity": [0.05, 0.1]},
                          seeds=(0,), trials=5, neuron_noise=0.1)
    assert [r["value"] for r in s["sweeps"]["neurons_per_type"]] == [1, 20]
    assert all(np.isfinite(r["overlap"]) for r in s["sweeps"]["neurons_per_type"])
    assert "sparsity" in RESHAPES_CODE
    assert all(np.isnan(r["overlap"]) for r in s["sweeps"]["sparsity"]), \
        "changing the expansion layer makes codes incomparable, so overlap must not be reported"


# --- the paired analysis ---

from sw_enose.uncertainty import paired_efficacy, paired_stage_sweep, paired_verdict


def _rows(diffs, ses, values=None):
    values = values or list(range(len(diffs)))
    return [{"value": v, "acc": np.zeros(5), "diff_mean": d, "diff_se": s}
            for v, d, s in zip(values, diffs, ses)]


def test_paired_verdict_needs_both_significance_and_size():
    assert paired_verdict(_rows([0.10], [0.01])).startswith("MATTERS")
    assert paired_verdict(_rows([0.10], [0.08])).startswith("NO EFFECT DETECTED"), "within 2 SE"
    assert paired_verdict(_rows([0.01], [0.001])).startswith("NO EFFECT DETECTED"), "too small to matter"
    assert paired_verdict(_rows([0.0, 0.0], [0.0, 0.0])).startswith("NOT EXERCISED")


def test_no_effect_verdict_states_what_could_have_been_detected():
    v = paired_verdict(_rows([0.03], [0.04]))
    assert "could not have been seen" in v and "0.080" in v


def test_paired_sweep_cancels_seed_luck():
    """Two seeds with very different baselines; a parameter that does nothing must show zero
    paired difference on every seed."""
    p = small()
    r = paired_stage_sweep(p, panel(p), {"recover_tau": [1.0, 100.0]}, seeds=(0, 1, 2), trials=5,
                           neuron_noise=0.0)
    for row in r["sweeps"]["recover_tau"]:
        assert row["diff_mean"] == 0.0 and row["diff_se"] == 0.0


def test_paired_efficacy_reports_between_and_within_draw_spread():
    p = small()
    r = paired_efficacy(p, panel(p), draws=3, seeds=(0, 1), trials=5, neuron_noise=0.1)
    assert len(r["draws"]) == 3 and len(r["draw_means"]) == 3
    assert r["between_draw_sd"] >= 0 and r["typical_se"] >= 0
