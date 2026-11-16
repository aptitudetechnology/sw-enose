import io
import zipfile
from pathlib import Path

import numpy as np
import pytest

from sw_enose.windtunnel import SENSOR_COLS, inventory, read_recording

ZIP = Path(__file__).resolve().parent.parent / "data" / "uci_windtunnel" / "windtunnel251.zip"
NAME = ("WTD_upload/CO_4000/L2/201105121600_board_setPoint_500V_fan_setPoint_060_"
        "mfc_setPoint_CO_4000ppm_p3")


def _fake_zip(tmp_path, times_ms):
    rows = []
    for t in times_ms:
        row = [t, 60, 3000, 100 if 20200 <= t < 200100 else 0, 0, 0, 0, 0, 0, 21.0, 50.0]
        for b in range(9):
            row += [1] + [100 + b * 8 + s for s in range(8)]
        rows.append("\t".join(str(v) for v in row))
    p = tmp_path / "fake.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr(NAME, "\n".join(rows))
        z.writestr("WTD_upload/CO_4000/L6/batch_execution", "not data")
    return p


def test_sensor_columns_skip_the_board_markers():
    assert len(SENSOR_COLS) == 72 and SENSOR_COLS[0] == 12 and SENSOR_COLS[8] == 21


def test_inventory_parses_names_and_skips_stray_files(tmp_path):
    inv = inventory(_fake_zip(tmp_path, [0, 10]))
    assert len(inv) == 1
    r = inv[0]
    assert (r.gas, r.ppm, r.position, r.day, r.heater_v, r.fan) == ("CO", 4000, 2, "20110512", 5.0, 60)


def test_resampling_puts_sensors_on_a_uniform_grid_and_fills_gaps(tmp_path):
    times = list(range(0, 260000, 20)) ; times = [t for t in times if not 50000 <= t < 51000]  # a 1 s gap
    p = _fake_zip(tmp_path, times)
    with zipfile.ZipFile(p) as z:
        r = read_recording(z, NAME, rate_hz=10.0)
    assert r["sensors"].shape == (2600, 72)
    assert not np.isnan(r["sensors"]).any()
    assert np.allclose(r["sensors"][0], np.arange(100, 172))   # markers dropped, order kept
    on = r["t"][np.argmax(r["mfc_set"][:, 0] > 0.5)]
    assert on == pytest.approx(20.25, abs=0.06)


@pytest.mark.skipif(not ZIP.exists(), reason="wind-tunnel data not fetched")
def test_real_inventory_matches_what_inspection_found():
    inv = inventory(ZIP)
    assert len(inv) == 18150
    assert {r.position for r in inv} == {1, 2, 3, 4, 5, 6}
    assert {r.fan for r in inv} == {0, 60, 100}
