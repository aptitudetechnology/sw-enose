"""Dose-response fits from Singh, Murphy, Balasubramanian & Mainland, PNAS 2019 (PMID 31000595).

Raw data: Open Science Framework, https://osf.io/aj29q/ (no licence stated there, so the raw files are
not stored in this repo; fetch them into data/singh2019/raw/). The fitted numbers below are OUR fits to
their raw plate readings, following the preprocessing and model in their Materials and Methods:

  ratio      = Firefly / Renilla luminescence per well
  standard   = ratio / (standard receptor at 100 uM nonanedioic acid - standard receptor with no odour), per plate
  response   = standard(odour) - standard(no odour) for the same receptor
  model      = A * (c/EC50) / (1 + c/EC50),  A = F_max * efficacy      (their Eq. 1, single odorant)

We did not read their SI Appendix, so details there (for example their handling of unconstrained
parameters) are not reproduced. A fit is flagged 'unconstrained' when EC50 lies above the highest
concentration tested (0.3 mM): then only the ratio A/EC50 is pinned down by the data.
"""
import csv
from collections import defaultdict
import numpy as np

STANDARD = "MOR42-3"          # Olfr544 in the paper
MAX_CONC = 3e-4               # molar, the assay ceiling
ODORANTS = ("eugenol", "coumarin", "acetophenone")
HUMAN = ("OR2W1", "OR2J2", "OR5P3", "OR2C1", "OR5K1", "OR1A1", "OR2J3", "OR10G4")


def _plate_scale(wells):
    """Per plate: difference between the standard receptor with and without its odorant."""
    hi = [w["ratio"] for w in wells if w["rec"] == STANDARD and w["odor"] == "Nonanedioic acid"]
    lo = [w["ratio"] for w in wells if w["rec"] == STANDARD and w["odor"] == "CD293"]
    return np.mean(hi) - np.mean(lo)


def dose_response(path):
    """Return {(receptor, odorant): (conc[M], mean response, sd)} with baseline already subtracted."""
    plates = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            plates[(r["TransfectionDate"], r["PlateNum"])].append(
                {"rec": r["ReceptorName"], "odor": r["OdorName"], "c": float(r["Odor1Concentration"]),
                 "ratio": float(r["LucData"]) / float(r["RLData"])})
    std = defaultdict(lambda: defaultdict(list))
    for wells in plates.values():
        scale = _plate_scale(wells)
        for w in wells:
            if w["rec"] != STANDARD:
                std[(w["rec"], w["odor"])][w["c"]].append(w["ratio"] / scale)
    out = {}
    for key, byc in std.items():
        zero = [c for c in byc if c <= 1e-11]
        if not zero:
            continue
        base = np.mean(byc[zero[0]])
        cs = sorted(c for c in byc if c > 1e-11)
        out[key] = (np.array(cs), np.array([np.mean(byc[c]) - base for c in cs]),
                    np.array([np.std(byc[c], ddof=1) for c in cs]), base)
    return out


def fit_curve(c, y, sd):
    """Weighted least squares for y = A * x/(1+x), x = c/EC50. EC50 on a log grid; A solved exactly (A >= 0)."""
    w = 1.0 / np.maximum(sd, 0.05 * max(1e-9, np.max(np.abs(y)), np.max(sd))) ** 2
    best = None
    for ec50 in np.logspace(-8, -1, 701):
        g = (c / ec50) / (1 + c / ec50)
        A = max(0.0, float(np.sum(w * g * y) / np.sum(w * g * g)))
        err = float(np.sum(w * (A * g - y) ** 2))
        if best is None or err < best[0]:
            best = (err, A, ec50)
    err, A, ec50 = best
    E = float(np.sqrt(np.mean(((A * (c / ec50) / (1 + c / ec50) - y) / np.maximum(sd, 1e-9)) ** 2)))
    return {"A": A, "EC50_M": ec50, "E": E, "unconstrained": bool(ec50 > MAX_CONC), "max_response": float(np.max(y))}


def fit_all(path):
    dr = dose_response(path)
    fits = {k: dict(fit_curve(c, y, sd), baseline=float(b)) for k, (c, y, sd, b) in dr.items()}
    return fits


def predict_mixture(fits, receptor, concs):
    """Competitive-binding prediction (their Eq. 1) for {odorant: conc in M}."""
    num = den = 0.0
    for o, c in concs.items():
        f = fits[(receptor, o)]
        num += f["A"] * c / f["EC50_M"]
        den += c / f["EC50_M"]
    return num / (1 + den)


def mixture_responses(path):
    """Return {receptor: [({odorant: conc}, mean response, sd), ...]} for the binary/ternary mixtures,
    standardised and baseline-subtracted the same way as the dose-response data."""
    plates = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ratio = float(r["LucData"]) / float(r["RLData"])
            if r["ReceptorName"] == STANDARD:
                plates[(r["TransfectionDate"], r["PlateNum"])].append(
                    {"rec": STANDARD, "odor": r["Odor1Name"], "ratio": ratio})
            else:
                concs = tuple(0.0 if float(r[f"Odor{i}Conc"]) <= 1e-11 else float(r[f"Odor{i}Conc"]) for i in (1, 2, 3))   # 1e-12 codes "no odour"
                names = tuple(r[f"Odor{i}Name"] for i in (1, 2, 3))
                plates[(r["TransfectionDate"], r["PlateNum"])].append(
                    {"rec": r["ReceptorName"], "odor": "mix", "ratio": ratio, "mix": dict(zip(names, concs))})
    vals = defaultdict(lambda: defaultdict(list))
    for wells in plates.values():
        scale = _plate_scale(wells)
        for w in wells:
            if w["rec"] != STANDARD:
                vals[w["rec"]][tuple(sorted(w["mix"].items()))].append(w["ratio"] / scale)
    out = {}
    for rec, bymix in vals.items():
        zero = [m for m in bymix if all(c == 0 for _, c in m)]
        if not zero:
            continue
        base = np.mean(bymix[zero[0]])
        out[rec] = [({o: c for o, c in m if c > 0}, float(np.mean(v) - base), float(np.std(v, ddof=1)))
                    for m, v in bymix.items() if m != zero[0]]
    return out


def validate_on_mixtures(dr_path, mix_path):
    """Predict each mixture from single-odorant fits only. Returns {receptor: rmse, median |response|, n}."""
    fits, mix = fit_all(dr_path), mixture_responses(mix_path)
    res = {}
    for rec, items in mix.items():
        if not all((rec, o) in fits for o in ODORANTS):
            continue
        pred = np.array([predict_mixture(fits, rec, m) for m, _, _ in items])
        obs = np.array([y for _, y, _ in items])
        sd = np.array([s for _, _, s in items])
        res[rec] = {"rmse": float(np.sqrt(np.mean((pred - obs) ** 2))), "n": len(items),
                    "median_obs": float(np.median(np.abs(obs))),
                    "rmse_over_sd": float(np.median(np.abs(pred - obs) / np.maximum(sd, 1e-9))),
                    "sum_rmse": float(np.sqrt(np.mean((np.array([sum(predict_mixture(fits, rec, {o: c}) for o, c in m.items())
                                                                  for m, _, _ in items]) - obs) ** 2)))}
    return res


def params_from_singh(dr_path, receptors=HUMAN):
    """ReceptorParams from our fits: EC50 in uM, and 'efficacy' = A = F_max * efficacy in the paper's
    standardised response units (so it is not capped at 1 and is comparable only within this dataset)."""
    from .data import ReceptorParams
    fits = fit_all(dr_path)
    receptors = tuple(r for r in receptors if all((r, o) in fits for o in ODORANTS))
    aff = np.array([[max(fits[(r, o)]["EC50_M"] * 1e6, 1e-6) for o in ODORANTS] for r in receptors])
    eff = np.array([[fits[(r, o)]["A"] for o in ODORANTS] for r in receptors])
    unc = sum(fits[(r, o)]["unconstrained"] for r in receptors for o in ODORANTS)
    prov = ("measured:Singh et al., PNAS 2019 (PMID 31000595), raw data from osf.io/aj29q; OUR fits of their Eq. 1; "
            "EC50 in uM, efficacy column holds A = F_max*efficacy in standardised units; cultured-cell assay, max 300 uM; "
            f"{unc} of {eff.size} curves do not saturate, so only A/EC50 is constrained for them")
    return ReceptorParams(aff, eff, 1.0, ODORANTS, prov, np.ones_like(eff, bool), receptors)
