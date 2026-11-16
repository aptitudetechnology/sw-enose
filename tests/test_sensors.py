from pathlib import Path

import numpy as np
import pytest

from sw_enose.sensors import DRIFT_BATCH_SIZES, OnOffFrontEnd, load_uci_drift

RAW = Path(__file__).resolve().parent.parent / "data" / "uci_drift" / "raw"


def test_front_end_is_non_negative_bounded_and_doubles_the_channels():
    rng = np.random.default_rng(0)
    Xtr, Xte = rng.normal(0, 3, (50, 4)), rng.normal(0, 30, (10, 4))
    fe = OnOffFrontEnd().fit(Xtr)
    A = fe.transform(Xte)
    assert A.shape == (10, 8) and fe.n_channels == 8
    assert A.min() >= 0.0 and A.max() <= 1.0


def test_on_and_off_channels_never_fire_together():
    fe = OnOffFrontEnd().fit(np.array([[1.0, -1.0], [-2.0, 2.0]]))
    A = fe.transform(np.array([[0.5, -0.5]]))
    on, off = A[:, :2], A[:, 2:]
    assert np.all((on == 0) | (off == 0))
    assert on[0, 0] > 0 and off[0, 1] > 0


def test_scaling_comes_from_training_data_only():
    fe = OnOffFrontEnd(percentile=100).fit(np.array([[2.0], [-1.0]]))
    assert fe.scale[0] == pytest.approx(2.0)
    assert fe.transform(np.array([[1.0]]))[0, 0] == pytest.approx(0.5)


def test_transform_before_fit_is_refused():
    with pytest.raises(RuntimeError):
        OnOffFrontEnd().transform(np.zeros((1, 2)))


@pytest.mark.skipif(not (RAW / "batch1.dat").exists(), reason="UCI drift data not fetched")
def test_loader_matches_the_published_batch_sizes():
    d = load_uci_drift(RAW)
    assert d["X"].shape == (13910, 128)
    assert [int((d["batch"] == b).sum()) for b in range(1, 11)] == list(DRIFT_BATCH_SIZES)
    assert set(np.unique(d["gas"])) == set(range(6))
    assert not np.isnan(d["X"]).any()
