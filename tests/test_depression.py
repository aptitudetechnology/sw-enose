import numpy as np
import pytest

from sw_enose.depression import NAGEL_2015_F, NAGEL_2015_TAU_MS, depress, steady_state


def test_constant_input_settles_to_the_analytic_steady_state():
    rate = np.full((5000, 1), 40.0)                      # 40 Hz for 5 s
    out = depress(rate, r=0.22, tau_ms=893.0)
    assert out[-1, 0] / 40.0 == pytest.approx(steady_state(40.0, 0.22, 893.0), rel=1e-3)


def test_response_is_transient_peak_then_sag_then_recovery():
    rate = np.zeros((6000, 1))
    rate[1000:3000] = 50.0                              # a 2 s step
    out = depress(rate)
    assert out[1000, 0] == pytest.approx(50.0)          # undepressed at onset
    assert out[2999, 0] < 0.5 * out[1000, 0]            # sags during the step
    rate2 = rate.copy()
    rate2[5900:] = 50.0                                 # a second step after 2.9 s of rest
    assert depress(rate2)[5900, 0] > 0.9 * 50.0         # mostly recovered (tau ~0.9 s)


def test_no_depression_passes_input_unchanged_and_bad_args_refused():
    rate = np.random.default_rng(0).uniform(0, 80, (300, 3))
    assert np.allclose(depress(rate, r=0.0), rate)
    with pytest.raises(ValueError):
        depress(rate, tau_ms=0)


def test_measured_constants_are_nagels():
    assert (NAGEL_2015_F, NAGEL_2015_TAU_MS) == (0.78, 893.0)
