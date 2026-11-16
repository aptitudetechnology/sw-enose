"""Loader for the UCI wind-tunnel gas sensor dataset (UCI 251), read straight from the zip.

Vergara, A. (2013). Gas sensor arrays in open sampling settings [Dataset]. UCI Machine Learning
Repository. https://doi.org/10.24432/C5JP5N. The page says CC BY 4.0 and also "exclusively for
research purposes"; see temporal-plan.md. Fetch with `scripts/fetch_uci_windtunnel.sh` into
data/uci_windtunnel/ (gitignored). The zip is 8.4 GB and 107 GB uncompressed, so recordings are
streamed from it one at a time and never extracted.

Verified from the files (16 Nov 2026), not from the page:
  - 18,150 recordings (plus one stray `batch_execution` file); 10 gases, CO at two
    concentrations; positions L1..L6 (filename codes p1, p3, ..., p11); heater 4.0-6.0 V in
    0.5 V steps; fan set-points 000/060/100; 111 days, 7 Dec 2010 to 25 Sep 2011.
  - Columns (92): 0 time (ms); 1 fan set-point; 2 fan reading; 3-5 mass-flow set-points (%);
    6-8 mass-flow readings (%); 9 temperature (C); 10 relative humidity (%); then 9 boards of
    [marker "1", 8 sensor resistances (kOhm)].
  - Gas release is the same in every recording sampled: flow set-point on at ~20.2 s, off at
    ~200.1 s; recordings run to 260 s. So 0-20 s is a clean-air baseline.
  - Sampling is irregular (median 10 or 20 ms, gaps up to ~1 s), so recordings are resampled
    onto a uniform grid using the time column.
  - Gas and day are heavily confounded: 91 of the 111 days hold a single gas.
"""
import re
import zipfile
from dataclasses import dataclass

import numpy as np

GAS_ON_S, GAS_OFF_S, DURATION_S = 20.2, 200.1, 260.0
SENSOR_COLS = np.array([12 + 9 * b + s for b in range(9) for s in range(8)])   # 72 sensor columns
assert len(SENSOR_COLS) == 72 and SENSOR_COLS[-1] == 91

_NAME = re.compile(
    r"WTD_upload/(?P<folder>(?P<gas>[^/_]+)_(?P<ppm>\d+))/(?P<loc>L\d)/(?P<dt>\d{12})"
    r"_board_setPoint_(?P<heater>\d+)V_fan_setPoint_(?P<fan>\d+)_mfc_setPoint_[^/]+_p(?P<p>\d+)$")


@dataclass(frozen=True)
class Recording:
    name: str          # path inside the zip
    gas: str
    ppm: int
    folder: str        # gas_ppm folder, e.g. "CO_4000"
    position: int      # 1..6 (L1 nearest the source)
    day: str           # YYYYMMDD
    time: str          # hhmm
    heater_v: float    # board heater set-point in volts
    fan: int           # fan set-point code: 0, 60, 100


def inventory(zip_path):
    """Every recording's metadata, from file names alone (no file is read)."""
    out = []
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            m = _NAME.match(info.filename)
            if not m:
                continue
            out.append(Recording(name=info.filename, gas=m["gas"], ppm=int(m["ppm"]),
                                 folder=m["folder"], position=int(m["loc"][1]),
                                 day=m["dt"][:8], time=m["dt"][8:], heater_v=int(m["heater"]) / 100,
                                 fan=int(m["fan"])))
    return out


def read_recording(zf, name, rate_hz=10.0):
    """One recording, resampled onto a uniform grid by averaging within bins.

    zf: an open zipfile.ZipFile. Returns dict: t (s, bin centres), sensors (T, 72) kOhm,
    temperature, humidity, mfc_set (T, 3), mfc_read (T, 3). Bins with no samples are filled by
    carrying the previous bin forward. Pure text parsing; nothing in the file is executed.
    """
    A = np.loadtxt(zf.open(name), dtype=float)
    t = A[:, 0] / 1000.0
    n_bins = int(round(DURATION_S * rate_hz))
    # integer bin index: float bin edges put a sample at exactly 20.2 s into the previous bin
    idx = np.clip(np.floor(t * rate_hz + 1e-6).astype(int), 0, n_bins - 1)
    edges = np.arange(n_bins + 1) / rate_hz
    counts = np.bincount(idx, minlength=n_bins)
    sums = np.zeros((n_bins, A.shape[1]))
    np.add.at(sums, idx, A)
    M = np.full_like(sums, np.nan)
    ok = counts > 0
    M[ok] = sums[ok] / counts[ok, None]
    for i in range(1, n_bins):               # carry forward over empty bins
        if not ok[i]:
            M[i] = M[i - 1]
    if not ok[0]:
        first = np.flatnonzero(ok)[0]
        M[:first] = M[first]
    return {"t": edges[:-1] + 0.5 / rate_hz, "sensors": M[:, SENSOR_COLS],
            "temperature": M[:, 9], "humidity": M[:, 10], "mfc_set": M[:, 3:6], "mfc_read": M[:, 6:9]}
