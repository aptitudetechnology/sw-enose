# Plan: the time-varying pipeline and the wind-tunnel test

Written 16 Nov 2026, before any wind-tunnel data has been inspected for results.

## Why this milestone

On static data the question is answered: the biomimetic stages that help (compression and
normalisation) work equally well in generic form, and the expansion layer does not help on real
sensor data (`demo_drift_mechanisms.py`, `demo_drift_svm.py`). The remaining open question is
time. Synaptic depression and adaptation act on *changes over time*, and on the recorded fly
neurons depression cut the error from 70 to 17 Hz (`demo_depression.py`). The static drift data
has no time course, so it could never show what these stages are for. The wind-tunnel recordings
can.

## The data (UCI 251, Vergara; facts from the UCI page, not yet checked against the files)

- 72 metal-oxide sensors (9 modules × 8), 10 gases, 6 positions downwind of the source (L1
  nearest), 3 fan speeds, heater voltages 4–6 V in 0.5 V steps; recordings of 260 s at 100 Hz;
  plus temperature, humidity, fan and flow channels. Collected December 2010 to April 2012; date
  and time in each file name.
- 7.8 GB zipped text. Read files straight from the zip; do not extract everything.
- The page's licence is CC BY 4.0 but it also says research use only (as with the drift data).
- The page's file count is internally inconsistent (18,000 vs 11 folders × 6 × 300); count the
  files.
- Not on the page: when gas release starts and stops within each recording. Must be found from
  the files (flow-controller channels) or the associated paper, and checked.

## Pitfalls already known (Dennler, van Schaik & Schmuker's critique of Imam & Cleland)

- A single snapshot at a fixed time can be "recognised" before any gas is released, through
  drift and session effects. **Negative control:** a classifier given only the pre-release
  window must score at chance. If it does not, the split is leaking session identity.
- Recognition collapsed when baselines were subtracted and train/test used separate
  repetitions. **Rules:** subtract each recording's own pre-release baseline; never split
  randomly by recording; hold out by date (session), and separately by position and fan speed.

## Questions, fixed now

1. **Early recognition.** Accuracy as a function of time since gas onset, using only data up to
   that time. Hypothesis: stages that emphasise change (depression, adaptation) recognise a gas
   earlier than steady-state features.
2. **Robustness to plume conditions.** Train at some positions or fan speeds, test at others.
   Hypothesis: change-emphasising stages generalise better across turbulence and distance than
   amplitude features do.

Controls, in the style that settled the static question:
- a **generic high-pass filter** (exponential high-pass, matched time constant) as the
  non-biological analogue of depression and adaptation. If it matches them, the conclusion is
  "emphasise change", not "copy the fly";
- **steady-state snapshot features** as the static baseline;
- the **pre-release negative control** above.

Classifiers as before (logistic regression, linear/RBF SVM, 5-NN; tuned inside training data
only; project venv). Decision rules for each question are written into the demo before it runs.

## Architecture

`sw_enose/temporal.py`: a streaming pipeline over (time, channels):
1. front end: subtract the pre-release baseline, scale on training data (ON/OFF as in
   `sensors.py`);
2. optional synaptic depression (`depression.py`, rate form);
3. optional adaptation (stage 3, time constants in seconds);
4. Olsen normalisation at each time step;
5. readout features up to time *t* (current value, running integral).

The static pipeline stays as it is.

## Order of work

1. Inspect the files: column layout, gas-release timing, saturation, missing data, file counts.
   Build a loader that reads from the zip.
2. Tabulate recordings by gas × date × position × heater × fan; write the splits down before
   computing any accuracy.
3. Negative control and static baseline.
4. Temporal stages; questions 1 and 2, with the generic controls.
5. Only then: fold the remaining DM4 items in (depression in the default path, the low peaks).

Compute: 18,000 recordings of 26,000 time steps is large. Start with one heater voltage and a
subset of positions; widen only if results warrant it. GPU (`gpu-to-do.md`) becomes relevant
here, but only if the CPU proves too slow.

## Findings from inspection (16 Nov 2026; no accuracy computed yet)

- Download verified: all 18,151 files pass their CRC check. 107 GB uncompressed; read from zip.
- 18,150 recordings (plus a stray `batch_execution` file). CO_1000 has only 450 recordings on 4
  days; every other gas/concentration folder has 1,500–1,800 on 10–15 days.
- Gas release identical in all 40 recordings sampled: flow on at ~20.2 s, off at ~200.1 s, end at
  260 s. **0–20 s is a clean pre-release baseline.**
- Sampling irregular (≈100 Hz or ≈50 Hz, gaps up to ~1 s); resampled to 10 Hz by time.
- **Gas and day are confounded:** 91 of 111 days hold one gas, 20 hold two. The negative
  control is therefore essential.
- In one recording inspected, only 8% of sensors fell >10% in resistance during gas: responses
  may be weak, especially far downwind.

## Splits, fixed before any accuracy is computed

- **Primary subset:** heater 5.0 V only (3,630 recordings). CO_1000 excluded (4 days only), so
  10 classes, CO meaning CO_4000. Other heater voltages are a later robustness check.
- **Day split (main):** for each gas, sort its recording days; the first 70% of days (rounded
  up) train, the rest test. Every gas appears in both sets; no test day is ever seen in
  training.
- **Position split:** within the day split, train on L1–L3 and test on L4–L6, and the reverse.
- **Fan split:** within the day split, leave one fan set-point out at a time.
- **Negative control:** under the day split, a classifier using only the 0–20 s window (no gas
  yet) must score near chance (0.10). Anything clearly above chance measures day/session leakage
  and is subtracted from how any result is read.
- **Two-gas days:** as a secondary check free of the day confound, compare gases recorded on the
  same day where possible.
