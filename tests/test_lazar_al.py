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


@pytest.mark.skipif(not HAVE, reason="Lazar 2022 data not fetched; see demo_lazar.py")
def test_swenose_olsen_stage_reaches_the_recorded_dm4_magnitude():
    """sw-enose's stage 4, given the Lazar OSN rates in Hz and nothing fitted, peaks near 140 Hz on
    recording 2 (recorded 148 Hz); the published example circuit peaks near 65 Hz."""
    from sw_enose.bio import BiomimeticNose
    from sw_enose.data import synthetic_params
    rows = list(csv.reader(open(REPO / "estimated_affinity.csv")))
    receptors = rows[0][1:]
    aff = {r[0]: np.array(r[1:], float) for r in rows[1:]}
    d = np.load(REPO / "staircase.npz", allow_pickle=False)
    dt = float(d["t"][1] - d["t"][0])
    k = receptors.index("59b")
    r = simulate(d["pn_input"][2:3], aff["acetone"], dt, record_every=10)
    nose = BiomimeticNose(synthetic_params(n_receptors=24, odorants=("A",)), max_orn_rate=1.0)
    pn = np.array([nose.normalise(g)[k] for g in r["osn"][0]])
    smoothed = np.convolve(pn, np.ones(50) / 50, mode="same")
    assert 120 < smoothed.max() < 165
    assert smoothed.max() > 1.8 * np.convolve(r["pn"][0, :, k], np.ones(50) / 50, mode="same").max()


def test_sweep_equals_running_each_configuration_separately():
    from sw_enose.lazar_al import sweep
    rng = np.random.default_rng(0)
    stim = rng.uniform(0, 200, (2, 3000))
    aff = rng.uniform(1e-5, 2e-3, 5)
    sets = [{}, {"postiln-to-pn": {"gmax": 300.0}}, {"osn_axt": {"k": 3e5}, "posteln-to-pn": {"gmax": 5.0}}]
    otps = [{}, {"kappa": 5000.0}, {}]
    batched = sweep(stim, aff, 1e-4, sets, otps, record_every=10)
    for c, (ps, ot) in enumerate(zip(sets, otps)):
        alone = simulate(stim, aff, 1e-4, record_every=10, params=ps, otp=ot)
        for key in ("osn", "pn"):
            assert np.allclose(batched[key][c], alone[key], rtol=1e-12, atol=1e-12), (c, key)


def test_recording_one_receptor_matches_the_full_recording():
    stim = np.full((1, 2000), 50.0)
    aff = np.array([1e-5, 2e-3, 5e-4])
    full = simulate(stim, aff, 1e-4, record_every=10)
    one = simulate(stim, aff, 1e-4, record_every=10, keys=("pn",), receptor=1)
    assert set(one) == {"pn"} and one["pn"].shape == full["pn"].shape[:2]
    assert np.allclose(one["pn"], full["pn"][:, :, 1])


def test_bad_parameter_shapes_and_names_are_refused():
    stim = np.zeros((2, 100))
    with pytest.raises(ValueError):
        simulate(stim, np.ones(3) * 1e-4, 1e-4, params={"osn_axt": {"k": np.ones(3)}})
    with pytest.raises(KeyError):
        simulate(stim, np.ones(3) * 1e-4, 1e-4, params={"no-such-block": {"k": 1.0}})
