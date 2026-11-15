"""Gas-mixture input: name the odorants and their concentrations, get the vector the nose needs.

Concentrations are in micromolar IN LIQUID, because the receptor data come from cultured cells bathed
in odorant solution. Converting an air concentration (ppb) to the concentration at a receptor needs a
model of air-to-mucus partitioning, which is NOT implemented. Treat every profile as illustrative.
"""
import numpy as np

# What the data can and cannot say about the three sulfur gases measured by breath meters.
# Checked against M2OR_20230428 on 15 Nov 2026 (see sources/AUDIT_*.md).
BREATH_SULFUR_COVERAGE = {
    "hydrogen sulfide": "not in the M2OR snapshot: no human receptor data found",
    "methyl mercaptan (methanethiol)": "screened once against about 500 human receptors at 10-100 uM (Mainland et al. 2015 "
                                       "data set); 7 receptor entries responded, 1 of them a genetic variant; no EC50, so it "
                                       "cannot be given measured parameters",
    "dimethyl sulfide": "tested on 6 human receptors, no agonist response recorded; no EC50",
}


class UnknownOdorant(KeyError):
    pass


def concentration_vector(params, mixture):
    """mixture: {odorant name: concentration in uM}. Names must be odorants the parameters cover."""
    idx = {o.lower(): j for j, o in enumerate(params.odorants)}
    c = np.zeros(len(params.odorants))
    for name, conc in mixture.items():
        if name.lower() not in idx:
            raise UnknownOdorant(f"{name!r} is not in these receptor parameters; refusing to guess a response")
        if conc < 0:
            raise ValueError("concentration must be >= 0")
        c[idx[name.lower()]] = conc
    return c


def coverage(params, mixture):
    """For each odorant in the mixture: how many receptors were actually tested with it, and how many respond."""
    out = {}
    for name in mixture:
        j = [o.lower() for o in params.odorants].index(name.lower())
        tested = int(params.known[:, j].sum()) if params.known is not None else 0
        out[name] = {"receptors_tested": tested, "agonist_for": int((params.efficacy[:, j] > 0).sum()),
                     "of": params.affinity.shape[0]}
    return out
