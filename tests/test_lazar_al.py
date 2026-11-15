"""The NumPy port of the Lazar, Liu & Yeh circuit, pinned to the original's own output."""
import csv
from pathlib import Path

import numpy as np
import pytest

from sw_enose.lazar_al import CSN_OSN, _poly, simulate

REPO = Path(__file__).resolve().parent.parent / "data" / "lazar2022" / "repo" / "data"
HAVE = (REPO / "staircase.npz").exists() and (REPO / "estimated_affinity.csv").exists()


def test_poly_matches_the_notebooks_power_series():
    I = np.array([0.0, 1.0, 7.5, 40.0])
    expect = sum(c * I ** k for k, c in enumerate(CSN_OSN))
    assert np.allclose(_poly(CSN_OSN, I), expect)


def test_no_odour_gives_only_spontaneous_activity_and_is_deterministic():
    stim = np.zeros((1, 2000))
    a = simulate(stim, np.full(4, 1e-3), 1e-4, record_every=100)
    b = simulate(stim, np.full(4, 1e-3), 1e-4, record_every=100)
    assert np.array_equal(a["pn"], b["pn"])
    assert np.allclose(a["osn"][0, -1], CSN_OSN[0], rtol=1e-6), "OSN rest rate is the I=0 rate"


def test_more_odour_drives_the_matching_receptor_harder():
    stim = np.vstack([np.full(5000, 10.0), np.full(5000, 100.0)])
    r = simulate(stim, np.array([1e-5, 2e-3]), 1e-4, record_every=100)
    assert r["osn"][1, -1, 1] > r["osn"][0, -1, 1] > r["osn"][0, -1, 0]


@pytest.mark.skipif(not HAVE, reason="Lazar 2022 data not fetched; see demo_lazar.py")
def test_port_reproduces_the_original_notebooks_saved_figure():
    """The original example_circuit notebook ships with its rendered output for pn_input[2]:
    colour-bar maxima of about 63 Hz (PN), 65 Hz (Post-eLN), 14.5 Hz (Post-iLN) and 12.5 uA (OSN
    axon-terminal current), all at receptor 59b, sampled every 1000th step. The port must match."""
    rows = list(csv.reader(open(REPO / "estimated_affinity.csv")))
    receptors = rows[0][1:]
    aff = {r[0]: np.array(r[1:], float) for r in rows[1:]}
    d = np.load(REPO / "staircase.npz", allow_pickle=False)
    dt = float(d["t"][1] - d["t"][0])
    r = simulate(d["pn_input"][2:3], aff["acetone"], dt, record_every=1)
    expected = {"pn": 63.0, "post_eln": 65.0, "post_iln": 14.5, "I_osn_axt": 12.5}
    for key, val in expected.items():
        sampled = r[key][0, ::1000]
        assert sampled.max() == pytest.approx(val, rel=0.03), key
        assert receptors[int(np.argmax(sampled.max(axis=0)))] == "59b", key
