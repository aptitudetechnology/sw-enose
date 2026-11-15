"""Does a conclusion survive what we do not know?

Two unknowns in this project are large enough to invalidate results if they matter, and harmless if
they do not. This module measures which:

 1. **Efficacy.** M2OR records no efficacy, so `m2or.build_params` assumes 1.0 for every agonist.
    Our fits of Singh et al.'s raw curves say that is wrong: relative efficacy among agonists at the
    same receptor runs from about 0.03 to 1.0, median 0.43. `efficacy_sensitivity` redraws efficacies
    from that measured spread and asks whether the nose still tells the same odorants apart, and
    whether it still reports the same code for each.

 2. **The invented stage parameters.** Convergence ratio and the adaptation time constants
    (`BIOLOGY["convergence"]`, `BIOLOGY["adaptation"]`) have no measured values behind them.
    `stage_sensitivity` sweeps them and reports how much the output moves.

A conclusion that survives both sweeps does not depend on the invented numbers. One that does not
survive is not a conclusion yet. Nothing here makes the model more accurate; it says how far to
trust it.
"""
from dataclasses import replace
import numpy as np

from .bio import BiomimeticNose, SparseMemory
from .data import ReceptorParams

# Relative efficacy (fitted A divided by the largest A at the same receptor) from OUR fits of the
# raw dose-response data of Singh, Murphy, Balasubramanian & Mainland, PNAS 2019 (PMID 31000595),
# osf.io/aj29q: 8 human receptors x 3 odorants, dropping 2 of 24 that sit below 2% of the receptor's
# best agonist (at that level a "response" is not distinguishable from none). Recompute with
# `relative_efficacy_sample(path)` when the raw file is present; a test checks the two agree.
#
# Health warning: 3 odorants, 8 receptors, one paper, one assay. 18 of these 24 curves do not
# saturate below the assay ceiling, and for those the fitted A is poorly constrained. Treat the
# spread as an order-of-magnitude statement, not a distribution.
SINGH_RELATIVE_EFFICACY = (
    0.416, 1.000, 0.954, 0.111, 0.169, 1.000, 0.044, 0.268, 1.000, 0.359, 1.000,
    0.256, 1.000, 1.000, 0.290, 0.107, 0.510, 1.000, 0.451, 0.031, 1.000, 0.355,
)
SINGH_EFFICACY_SOURCE = ("measured:relative efficacy spread from OUR fits of Singh et al., PNAS 2019 "
                         "(PMID 31000595) raw data, 8 receptors x 3 odorants")
MIN_RELATIVE_EFFICACY = 0.02


def relative_efficacy_sample(dr_path, receptors=None, min_relative=MIN_RELATIVE_EFFICACY) -> tuple:
    """Recompute the relative-efficacy sample from Singh's raw dose-response file."""
    from .singh import HUMAN, ODORANTS, fit_all
    fits = fit_all(dr_path)
    out = []
    for r in (HUMAN if receptors is None else receptors):
        if not all((r, o) in fits for o in ODORANTS):
            continue
        a = {o: fits[(r, o)]["A"] for o in ODORANTS}
        top = max(a.values())
        if top <= 0:
            continue
        out += [round(a[o] / top, 3) for o in ODORANTS if a[o] / top > min_relative]
    return tuple(out)


def resample_efficacy(params: ReceptorParams, rng, sample=SINGH_RELATIVE_EFFICACY) -> ReceptorParams:
    """Replace every agonist's efficacy with a draw from the measured relative-efficacy spread.

    Pairs with efficacy 0 (tested and no response, or never tested) stay 0: this changes how
    strongly an agonist acts, never whether it is one.
    """
    eff = np.array(params.efficacy, float, copy=True)
    agonist = eff > 0
    if agonist.any():
        eff[agonist] = np.asarray(rng.choice(np.asarray(sample, float), size=int(agonist.sum())))
    return replace(params, efficacy=eff,
                   provenance=params.provenance + "; efficacy REDRAWN from " + SINGH_EFFICACY_SOURCE)


def code_overlap(a, b) -> float:
    """Fraction of a sparse code's active cells that the other code also has active, 0..1."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(a @ b) / max(1.0, float(a.sum()))


def panel_codes(nose: BiomimeticNose, panel: dict, steps=1, adapt=False) -> dict:
    """One sparse code per smell in the panel, each from a fresh adaptation state."""
    out = {}
    for name, conc in panel.items():
        nose.reset()
        out[name] = nose.sniff(conc, steps=steps, adapt=adapt)
    return out


def panel_recognition(nose: BiomimeticNose, panel: dict, trials=20, repeats=10, steps=1,
                      adapt=False) -> float:
    """Learn each smell from the sparse code, then re-present it. Returns accuracy 0..1."""
    mem = SparseMemory()
    for name, conc in panel.items():
        codes = []
        for _ in range(repeats):
            nose.reset()
            codes.append(nose.sniff(conc, steps=steps, adapt=adapt))
        mem.learn(name, codes)
    ok = 0
    for name, conc in panel.items():
        for _ in range(trials):
            nose.reset()
            ok += mem.recognise(nose.sniff(conc, steps=steps, adapt=adapt))[0] == name
    return ok / (len(panel) * trials)


def _quiet(params, seed, nose_kw):
    """The same nose with neuron noise switched off, so codes are deterministic and comparable."""
    return BiomimeticNose(params, seed=seed, **{**nose_kw, "neuron_noise": 0.0})


def seed_floor(params: ReceptorParams, panel: dict, seeds=(0, 1, 2, 3, 4), trials=20, steps=1,
               adapt=False, **nose_kw) -> dict:
    """Recognition across several random seeds with nothing else changed.

    This is the noise floor of every sweep below. A parameter has only been shown to matter if its
    effect is bigger than the spread here, which is pure run-to-run variation.
    """
    r = [panel_recognition(BiomimeticNose(params, seed=s, **nose_kw), panel, trials=trials,
                           steps=steps, adapt=adapt) for s in seeds]
    return {"seeds": tuple(seeds), "mean": float(np.mean(r)), "min": float(np.min(r)),
            "max": float(np.max(r)), "spread": float(np.max(r) - np.min(r))}


def between_smell_overlap(params: ReceptorParams, panel: dict, seed=0, **nose_kw) -> dict:
    """Overlap between the codes of DIFFERENT smells: the control for reading any overlap number.

    Without this, an overlap of 0.6 cannot be judged. If different smells overlap at 0.0, then 0.6
    means the code is recognisably the same smell with a third of its cells moved. If different
    smells already overlap at 0.5, it means almost nothing.
    """
    codes = panel_codes(_quiet(params, seed, nose_kw), panel)
    names = list(panel)
    vals = [code_overlap(codes[a], codes[b]) for i, a in enumerate(names) for b in names[i + 1:]]
    k = float(np.mean([c.mean() for c in codes.values()]))
    return {"pairs": len(vals), "mean": float(np.mean(vals)) if vals else float("nan"),
            "max": float(np.max(vals)) if vals else float("nan"), "chance": k}


def efficacy_sensitivity(params: ReceptorParams, panel: dict, draws=20, seeds=(0, 1, 2), trials=20,
                         steps=1, adapt=False, sample=SINGH_RELATIVE_EFFICACY, **nose_kw) -> dict:
    """Redraw efficacies from the measured spread and see what moves.

    Two different questions, reported separately, because they can disagree:
      `recognition`  -- can the nose still tell the panel apart, in its own redrawn world?
      `overlap`      -- is the code it reports for a smell still the code the efficacy=1 nose gave?

    High recognition with low overlap means discrimination is safe but the identity of any particular
    code is not: a claim of the form "odorant X produces code Y" would not survive. Read `overlap`
    against `between_smell_overlap`, never on its own.
    """
    rng = np.random.default_rng(seeds[0])
    floor = seed_floor(params, panel, seeds=seeds, trials=trials, steps=steps, adapt=adapt, **nose_kw)
    ref = {s: panel_codes(_quiet(params, s, nose_kw), panel, steps=steps, adapt=adapt) for s in seeds}
    rec, ovl = [], []
    for _ in range(draws):
        q = resample_efficacy(params, rng, sample)
        rec.append(float(np.mean([panel_recognition(BiomimeticNose(q, seed=s, **nose_kw), panel,
                                                    trials=trials, steps=steps, adapt=adapt)
                                  for s in seeds])))
        per_seed = []
        for s in seeds:
            codes = panel_codes(_quiet(q, s, nose_kw), panel, steps=steps, adapt=adapt)
            per_seed.append(np.mean([code_overlap(ref[s][n], codes[n]) for n in panel]))
        ovl.append(float(np.mean(per_seed)))
    return {"baseline": floor, "draws": draws,
            "recognition": (float(np.min(rec)), float(np.median(rec)), float(np.max(rec))),
            "overlap": (float(np.min(ovl)), float(np.median(ovl)), float(np.max(ovl))),
            "sample_median": float(np.median(sample)),
            "sample_range": (float(min(sample)), float(max(sample)))}


#: Sweeping these changes the random expansion matrix, so sparse codes stop being comparable
#: between runs and `overlap` becomes meaningless. Recognition is still valid.
RESHAPES_CODE = ("n_expansion", "fan_in", "sparsity", "seed")


def stage_sensitivity(params: ReceptorParams, panel: dict, grid: dict, seeds=(0, 1, 2), trials=20,
                      steps=1, adapt=False, **nose_kw) -> dict:
    """Sweep stage parameters one at a time; report recognition and overlap against the baseline.

    grid: {keyword: [values]}, each keyword a BiomimeticNose argument. Each value is averaged over
    `seeds`, and `baseline` gives the spread across those same seeds with nothing changed, which is
    what a sweep's spread has to beat to mean anything.

    Convergence (`neurons_per_type`) acts ONLY by averaging away neuron noise: with noise at zero the
    glomerular output does not depend on it at all. So its overlap column is 1.0 by construction and
    only the recognition column carries information. That is a property of the model, not a bug.
    """
    floor = seed_floor(params, panel, seeds=seeds, trials=trials, steps=steps, adapt=adapt, **nose_kw)
    ref = {s: panel_codes(_quiet(params, s, nose_kw), panel, steps=steps, adapt=adapt) for s in seeds}
    out = {"baseline": floor, "sweeps": {}}
    for key, values in grid.items():
        rows = []
        for v in values:
            kw = {**nose_kw, key: v}
            rec = float(np.mean([panel_recognition(BiomimeticNose(params, seed=s, **kw), panel,
                                                   trials=trials, steps=steps, adapt=adapt)
                                 for s in seeds]))
            if key in RESHAPES_CODE:
                ov = float("nan")
            else:
                ov = float(np.mean([
                    np.mean([code_overlap(ref[s][n], c[n]) for n in panel])
                    for s in seeds
                    for c in [panel_codes(_quiet(params, s, kw), panel, steps=steps, adapt=adapt)]]))
            rows.append({"value": v, "recognition": rec, "overlap": ov})
        out["sweeps"][key] = rows
    return out


def verdict(recognition_values, baseline: dict, label="the answer") -> str:
    """Did a sweep move the result by more than reseeding the same model does?

    Compares the sweep's spread with the baseline seed-to-seed spread. A sweep that moves things less
    than reseeding has not been shown to matter; one that drops recognition below the baseline's
    worst seed has.
    """
    lo, hi = float(np.min(recognition_values)), float(np.max(recognition_values))
    spread = hi - lo
    if lo < baseline["min"] - max(0.05, baseline["spread"]):
        return (f"MATTERS: recognition falls to {lo:.2f}, below the baseline's worst seed "
                f"{baseline['min']:.2f} by more than its own spread {baseline['spread']:.2f}")
    if spread <= max(baseline["spread"], 0.02):
        return (f"DOES NOT MATTER for {label}: spread {spread:.2f} over the whole sweep, "
                f"against {baseline['spread']:.2f} from reseeding alone")
    return (f"UNCLEAR: sweep spread {spread:.2f} vs {baseline['spread']:.2f} from reseeding; "
            f"worst {lo:.2f} against baseline worst {baseline['min']:.2f}")


def _rank_correlation(y) -> float:
    """Spearman correlation between position in the sweep and the result. Needs ascending values."""
    y = np.asarray(y, float)
    if len(y) < 3 or np.ptp(y) == 0:
        return 0.0
    ry = np.argsort(np.argsort(y)).astype(float)
    rx = np.arange(len(y), dtype=float)
    return float(np.corrcoef(rx, ry)[0, 1])


TREND_RHO = 0.8


def sweep_summary(rows, baseline: dict, label="") -> dict:
    """Spread, trend and verdict for one swept parameter. Grid values must be in ascending order.

    A sweep whose recognition trends consistently with the parameter, by more than reseeding moves
    it, is a real effect even when no single value drops below the baseline: run-to-run noise does
    not arrive in rank order. A sweep with no spread at all has not tested anything, which is
    reported as such rather than as an absence of effect.
    """
    rec = [r["recognition"] for r in rows]
    spread = float(np.max(rec) - np.min(rec))
    if spread <= 1e-9:
        return {"spread": 0.0, "rho": 0.0, "trend": "none",
                "verdict": (f"NOT EXERCISED: every value gives the same recognition ({rec[0]:.2f}), "
                            f"so this task does not test {label or 'this parameter'} at all. "
                            "An absence of effect here is an absence of evidence, not evidence of "
                            "absence")}
    rho = _rank_correlation(rec)
    trend = "increasing" if rho >= TREND_RHO else "decreasing" if rho <= -TREND_RHO else "none"
    v = verdict(rec, baseline, label)
    if trend != "none" and spread > baseline["spread"] and not v.startswith("MATTERS"):
        v = (f"MATTERS: recognition trends {trend} with the parameter (rank correlation "
             f"{rho:+.2f}), {min(rec):.2f} to {max(rec):.2f}, a spread of {spread:.2f} against "
             f"{baseline['spread']:.2f} from reseeding; an ordered trend is not reseeding noise")
    return {"spread": spread, "rho": rho, "trend": trend, "verdict": v}


# ---------------------------------------------------------------------------------------------
# Paired analysis. Added 16 Nov 2026 after finding that the sulfur-trace task swings from about
# 0.5 to 1.0 with the random seed alone: the seed fixes the expansion wiring, and that wiring is
# most of the variance. `verdict` above compares the spread of seed-AVERAGED accuracies against
# the min-max range of INDIVIDUAL seeds, a yardstick that grows as seeds are added, so with many
# seeds everything would read "does not matter". The functions below compare conditions WITHIN
# each seed and test the mean paired difference against its own standard error, which cancels the
# wiring luck instead of letting it swamp the comparison.

def paired_stage_sweep(params: ReceptorParams, panel: dict, grid: dict, seeds=tuple(range(1, 13)),
                       trials=50, steps=1, adapt=False, **nose_kw) -> dict:
    """For each swept value and each seed, recognition; differences are taken against the
    baseline nose (nose_kw alone) with the SAME seed.

    Returns {"baseline": per-seed array, "sweeps": {key: [{"value", "acc" (per seed),
    "diff_mean", "diff_se"}]}}.
    """
    seeds = tuple(seeds)
    rec = lambda kw, s: panel_recognition(BiomimeticNose(params, seed=s, **kw), panel,
                                          trials=trials, steps=steps, adapt=adapt)
    base = np.array([rec(nose_kw, s) for s in seeds])
    out = {"baseline": base, "seeds": seeds, "sweeps": {}}
    for key, values in grid.items():
        rows = []
        for v in values:
            acc = np.array([rec({**nose_kw, key: v}, s) for s in seeds])
            d = acc - base
            rows.append({"value": v, "acc": acc, "diff_mean": float(d.mean()),
                         "diff_se": float(d.std(ddof=1) / np.sqrt(len(d)))})
        out["sweeps"][key] = rows
    return out


def paired_verdict(rows, min_effect=0.02, z=2.0, label="this parameter") -> str:
    """MATTERS if some value shifts recognition by more than `z` paired standard errors AND by at
    least `min_effect` in absolute terms; otherwise report the smallest effect the data could
    have detected, so "no effect found" is never mistaken for "no effect"."""
    sig = [r for r in rows if abs(r["diff_mean"]) > max(z * r["diff_se"], min_effect)]
    if sig:
        worst = max(sig, key=lambda r: abs(r["diff_mean"]))
        return (f"MATTERS: {label}={worst['value']} shifts recognition by {worst['diff_mean']:+.3f} "
                f"(paired SE {worst['diff_se']:.3f}, {len(worst['acc'])} seeds)")
    detectable = max(max(z * r["diff_se"], min_effect) for r in rows)
    if all(r["diff_se"] == 0 and r["diff_mean"] == 0 for r in rows):
        return (f"NOT EXERCISED: every value gives identical recognition on every seed, so this task "
                f"does not test {label} at all")
    return (f"NO EFFECT DETECTED for {label}: every shift is within {z:.0f} paired SE; effects "
            f"smaller than about {detectable:.3f} could not have been seen")


def paired_efficacy(params: ReceptorParams, panel: dict, draws=12, seeds=tuple(range(1, 13)),
                    trials=50, steps=1, adapt=False, sample=SINGH_RELATIVE_EFFICACY, **nose_kw) -> dict:
    """Recognition for each efficacy redraw on each seed, paired against efficacy=1 on that seed.

    Answers two questions: does a redraw shift recognition beyond paired noise (per draw), and is
    the spread BETWEEN draws larger than the precision of each draw's seed-average.
    """
    seeds = tuple(seeds)
    rng = np.random.default_rng(seeds[0])
    rec = lambda q, s: panel_recognition(BiomimeticNose(q, seed=s, **nose_kw), panel, trials=trials,
                                         steps=steps, adapt=adapt)
    base = np.array([rec(params, s) for s in seeds])
    per_draw = []
    for _ in range(draws):
        q = resample_efficacy(params, rng, sample)
        acc = np.array([rec(q, s) for s in seeds])
        d = acc - base
        per_draw.append({"acc": acc, "diff_mean": float(d.mean()),
                         "diff_se": float(d.std(ddof=1) / np.sqrt(len(d)))})
    means = np.array([p["acc"].mean() for p in per_draw])
    typical_se = float(np.median([p["acc"].std(ddof=1) / np.sqrt(len(seeds)) for p in per_draw]))
    return {"baseline": base, "seeds": seeds, "draws": per_draw, "draw_means": means,
            "between_draw_sd": float(means.std(ddof=1)), "typical_se": typical_se}
