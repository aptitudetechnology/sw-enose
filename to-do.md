# Comparison with prior bio-inspired e-noses, and what to do next

Written 15 Nov 2026. This follows the literature search in
`reports/Biomimetic software nose prior art.md`, which found that no published system has the full
sw-enose chain, but that every stage has precedent. The question here was practical: can we get the
closest prior systems' code and compare it with ours?

## 1. Is the source code available?

None of the four closest papers released code. Checked against the papers' own data and code
statements, plus web searches for repositories.

| Paper | Code? | What exists |
|---|---|---|
| Lazar, Liu, Yeh & Zhou 2024, Front Physiol, doi 10.3389/fphys.2024.1410946 (fly, DoOR affinities, competitive binding, through to Kenyon cells) | No | Data statement says results are in the article and supplement; "further inquiries" to the corresponding author. No repository, no language named. |
| Lazar, Liu & Yeh 2022/23, antennal lobe only (same group) | **Yes** | [github.com/TK-21st/AntennalLobeLLY22](https://github.com/TK-21st/AntennalLobeLLY22), BSD-3, last commit 28 Feb 2022. See section 2. |
| Scott, Sherrill, Jiang & Zhao 2014, J Neurosci, PMC3913860 (air-to-mucus into a dose-response model) | No | Article only. Built on CFD software. |
| Raman & Gutierrez-Osuna 2006, Sens Actuators B 116:36, doi 10.1016/j.snb.2005.11.078 | No | Paper only. Fully specified, so reimplemented (section 3). |
| Muezzinoglu et al. 2008, NIPS 21:1121 | No | Paper only. The metal-oxide sensor datasets and network topology are said to be in its supplementary material, which we do not have. Mostly specified, so reimplemented (section 3). |

## 2. The Lazar antennal-lobe repository

Cloned to the session scratchpad (not into this repo) and read; nothing was executed.

- **Contents:** two jupytext notebooks (`example_circuit`, `data`) and two data files:
  - `estimated_affinity.csv`: estimated affinities for 110 odorants × 24 fly receptors, derived from
    DoOR with the group's own estimation algorithm.
  - `staircase.npz`: **real recordings**: an Or59b olfactory receptor neuron and a DM4 projection
    neuron responding to acetone concentration staircases (ppm), as PSTHs.
- **Model:** a fly antennal-lobe circuit: odorant transduction (an ODE model), pre-synaptic global
  feedback inhibition, local feedforward excitation and inhibition onto PNs, and Poisson spike
  generators with polynomial rate curves. It models one odorant at a time, has no mixtures and no
  Kenyon cells.
- **Why it can't run here as-is:** it uses `pycuda` and `scikit-cuda`, which are NVIDIA CUDA only,
  plus a pinned branch of the in-house `neural` package (github.com/chungheng/neural, branch `al`).
  `neural.Network` supports only `backend="cuda"`, and it writes its CUDA kernels as strings at
  runtime (`neural/codegen/cuda.py`).
- **The AMD GPU (RX 9070):** hipify-perl converts CUDA C/C++ source, but there is none in this repo
  to convert. Running on ROCm would mean replacing pycuda/skcuda with CuPy-on-ROCm or AMD's
  `hip-python`, and hipifying the kernel templates in the code generator. That is a real porting
  project.
- **Recommended instead:** port `example_circuit.py` to plain numpy. Every ODE is visible in the
  file, there are only 24 receptor types, and it uses Euler steps, so a CPU is enough. The port can
  then be checked against the real `staircase.npz` recordings, which no part of sw-enose has ever
  been compared with.

## 3. Reimplementations and comparison

**Code:** `sw_enose/reference_models.py` (in the repo, **uncommitted**). The comparison scripts
are in the session scratchpad (`compare.py`, `ablate.py`) and may not survive a reboot. They should
become `demo_reference.py`.

**Method:** both reimplementations are fed the **same sw-enose front end**: measured M2OR EC50s,
competitive binding, and same-type convergence (`BiomimeticNose.glomeruli`). Only the downstream
processing differs. The task is the 8 fatty acids (C3–C10), one at a time, each at a concentration
drawn log-uniformly from 20 to 2000 µM, so only the pattern identifies the odorant. There are 40
training and 80 test samples per acid, and nearest-centroid readout unless stated.

**This is not how either paper was run.** Both took metal-oxide sensor signals directly. The results
say how their processing behaves on our input, not how well their systems worked on their own
data.

### Fidelity of the reimplementations

- **Raman 2006: faithful for the global case.** Their Eq. (5) steady state is
  `x_i = B·G_i / (D + G_i + Σ_{k≠i} c_ki·G_k)` with B = 1 and D = 0.1, and their Fisher
  separability is Eq. (6). Their self-organising map and lattice-local connectivity were not used,
  because 8 receptor types give nothing to arrange on a lattice and convergence by receptor identity
  is already done upstream. The global variants (c = 1, and c ~ U(0,1)) are implemented.
- **Muezzinoglu 2008: mostly faithful, with interpretations marked OURS in the code:**
  - The exponential parameters "λ_K = 7.5, λ_β = 0.5" are read as means, not rates.
  - Explicit Euler with time constants floored at 0.01 replaces their adaptive Runge–Kutta 5(6).
  - The AL noise term is omitted.
  - The input is static, with a snapshot after 1 s. Their antennal lobe is designed to exploit
    sensor transients, which a static task cannot reward.
  - An input scale factor of 1e5 maps glomerular activity onto their resistance-like range.
  - Their garbled learning rule ("…and 0, otherwise") is read as "w otherwise".
  - Their bijectivity check is reduced to making sure every input reaches at least one Kenyon cell.
  - Conductances (gE, gI) were tuned by grid search on a validation split of the **training** data
    only. They tuned on their classification problem.

### Results: accuracy on the 8-acid task

| | noise 0.1 | 0.4 | 0.8 |
|---|---|---|---|
| ceiling (best readout of the glomerular vector) | 0.997 | 0.959 | 0.859 |
| sw-enose stage 4, Olsen normalisation | 0.992 | 0.945 | 0.853 |
| Raman 2006 shunting, c = 1 | 1.000 | 0.950 | 0.856 |
| Raman 2006 shunting, c ~ U(0,1) | 0.994 | 0.944 | 0.850 |
| **sw-enose full pipeline (sparse code + memory)** | **0.911** | **0.753** | **0.548** |
| Muezzinoglu antennal lobe + nearest centroid | 0.783 | 0.770 | 0.747 |
| **Muezzinoglu antennal lobe + Kenyon layer (Hebbian)** | **0.970** | **0.941** | **0.828** |

On Raman's own Fisher-J measure the two normalisation stages are also close (Olsen 0.19 vs Raman
0.14 at noise 0.1; 0.05 vs 0.06 at noise 0.4; 0.03 each at noise 0.8).

### Ablation: what makes the Kenyon layer better?

Changes to sw-enose's stage 5, one at a time. Muezzinoglu's Kenyon layer is fed the Olsen output for
comparison.

| | noise 0.1 | 0.4 | 0.8 |
|---|---|---|---|
| sw-enose default: 2,000 cells, top 5% active, fan-in 2 | 0.911 | 0.753 | 0.548 |
| 10,000 cells | 0.911 | 0.766 | 0.555 |
| **top 20% active** | **0.967** | **0.839** | **0.716** |
| 10,000 cells and top 20% | 0.964 | 0.841 | 0.711 |
| 10,000 cells, top 20%, fan-in 4 | 0.728 | 0.680 | 0.637 |
| Muezzinoglu Kenyon layer, top 20% | 0.866 | 0.755 | 0.628 |
| Muezzinoglu Kenyon layer, top 5% | 0.973 | 0.886 | 0.759 |

### What the results show

1. **Stage 4 makes no difference on this panel.** Olsen and Raman agree within 0.01 everywhere and
   both reach the ceiling. The Olsen form has no advantage over a simpler two-parameter shunting
   equation here.
2. **Muezzinoglu's antennal lobe adds nothing on a static task.** Tuning chose zero connectivity,
   and it scored below the raw input. That is expected from its design, so it is not a fair test
   of the model.
3. **sw-enose's stage 5 is now the main loss, and the active fraction is the main reason.**
   - The number of cells barely matters.
   - Going from 5% to 20% active recovers +0.06, +0.09 and +0.17 at the three noise levels.
   - It is the same transplant error as the fan-in bug. The fly's 5% belongs to an array of about
     50 glomeruli. With 8 glomeruli and fan-in 2 there are only 28 distinct wirings, so a 5% code
     is dominated by ties and duplicate cells.
4. **Muezzinoglu's layer at 5% does better still, for reasons not yet separated.**
   - With connection probability 0.1 over 8 inputs, most of its cells get 0, 1 or 2 inputs, so its
     effective fan-in distribution is very different from ours.
   - Its readout is also different: summed Hebbian counts over random initial weights.
   - Its own 20% setting does worse on our input. Many of its cells have no input, so ties fill
     the top 20%. Its parameters belong to its 75-input regime, not ours.
5. **These numbers were tuned and scored on the same synthetic task.** That is the "not held out"
   criticism from `sonnet-review.md` again. Any default change made on this basis inherits it.

## 4. To do

**Decisions needed:**

- [ ] **Stage 5 active fraction.** Keep the fly's 5%, adopt a fixed 20%, or scale it with array
  size the way `fan_in` now scales? If it changes, choose it on a held-out panel or task and not
  this one. Every number in `README.md` and the demos that depends on stage 5 would need re-running.
- [ ] **Stage 4.** Keep Olsen (literature-grounded, fly constants) or note that Raman's simpler
  form performs the same? This is documentation only unless something else changes.

**Work:**

- [ ] Package the comparison: `demo_reference.py` reproducing both tables above, tests for
  `reference_models.py` (at minimum that Raman Eq. 6 reduces to L1 normalisation and that the Kenyon
  layer keeps exactly the top fraction), then commit.
- [ ] Separate the remaining Kenyon-layer effect: sweep connection probability (fan-in distribution)
  and readout rule (SparseMemory vs Hebbian counts) independently at 5% active.
- [x] **Done (uncommitted): ported the Lazar antennal-lobe circuit to numpy.** Files:
  `sw_enose/lazar_al.py` (port, with the BSD-3 notice), `demo_lazar.py`, `tests/test_lazar_al.py`.
  The data is cloned to `data/lazar2022/repo/` and gitignored.
  - **The port is faithful.** On the original notebook's own example (acetone, `pn_input[2]`) it
    reproduces all four saved colour-bar maxima: 63.7 / 65.5 / 14.5 Hz and 12.57 µA, against
    about 63 / 65 / 14.5 Hz and 12.5 µA. The same receptors are active and the same transients
    occur. A test pins this. 17.5 s of 14 waveforms runs in about 21 s on the CPU.
  - **The data file has duplicates.** PN recordings 3, 5 and 6 are byte-identical, and so are OSN
    stimuli 0 and 1. The PN set is 5 recordings, not 7.
  - **The Or59b receptor neuron fits well in shape:** r = 0.88–0.95 in every recording. The
    model's rate is about half the recorded rate in recordings 3–5. Its transduction parameters
    were probably fitted to data like this, so this shows consistency rather than independent
    validation (UNVERIFIED).
  - **The DM4 projection neuron does not fit:** r = 0.40–0.61, with the model peaking near 65 Hz
    against 150–190 Hz recorded. Because the port matches the original's output, this belongs to
    the published example configuration, not to the port.
- [ ] Run sw-enose's own stages 3 (adaptation) and 4 (normalisation) against these Or59b/DM4
  recordings. This is the first recorded-data benchmark available to it. It needs a time-varying
  input path, since sw-enose currently has none.
- [ ] Ask the Lazar group which circuit configuration in the paper reproduces the DM4 peaks.
- [ ] Email the Lazar 2024 and Scott 2014 corresponding authors asking for code.
- [ ] Give Muezzinoglu's antennal lobe a fair test: it needs time-varying input (sensor-like
  transients), which sw-enose does not produce yet.

**Still open from earlier:**

- [ ] Human detection-threshold benchmark for C3–C10. Cometto-Muñiz 2010 (PMID 20931179) measured a
  homologous carboxylic-acid series and is the likely data source. This remains the one check that
  could change the overall verdict.
- [ ] Revisit the air-to-mucus step. Scott 2014 and Kurtz 2004 show mucus takes up lipophilic
  odorants more than water does, by about tenfold at log P 3 (extrapolated). This matters most for
  C8–C10.
- [ ] Decide whether to commit `reports/` and `research_notes/`, which are currently untracked.
- [ ] Read the 2025 Dennler et al. neuromorphic machine-olfaction review in full, the largest gap in
  the novelty search.
