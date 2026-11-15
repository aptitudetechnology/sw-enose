"""Which receptor-odorant pairs were actually tested, kept as a first-class fact.

The problem this solves. `m2or.build_params` sets an untested pair to "no response", because that is
the only array it can build. But a receptor that nobody tested against an odorant is not a receptor
that fails to respond to it, and most pairs in M2OR were never tested. Comparing two odorants across
all receptors therefore mixes a real difference in binding with an accident of which lab screened
which receptor. `demo_m2or.py` worked around this by hand; the logic belongs here.

Nothing in this module invents a response. It either narrows the array to pairs that were measured,
or reports how much measurement a given comparison actually rests on.
"""
from dataclasses import replace
import numpy as np

from .data import ReceptorParams


class NoCoverageInformation(ValueError):
    """These parameters do not record which pairs were tested, so coverage cannot be reported."""


def _indices(params, odorants):
    low = [o.lower() for o in params.odorants]
    out = []
    for name in odorants:
        try:
            out.append(low.index(str(name).lower()))
        except ValueError:
            raise KeyError(f"{name!r} is not in these receptor parameters") from None
    return out


def _known(params):
    if params.known is None:
        raise NoCoverageInformation(
            "these parameters carry no `known` mask, so every value in them is invented; "
            "coverage is only meaningful for measured parameters")
    return params.known


def support(params: ReceptorParams, odorants=None) -> dict:
    """How much measurement stands behind a comparison between `odorants` (default: all of them).

    `fully_tested` is the number that matters: only a receptor tested against EVERY odorant in the
    comparison can distinguish them on measured ground. The rest contribute a difference that may be
    nothing more than which pair someone happened to assay.
    """
    known = _known(params)
    odorants = tuple(params.odorants) if odorants is None else tuple(odorants)
    cols = _indices(params, odorants)
    sub = known[:, cols]
    fully = int(np.all(sub, axis=1).sum())
    return {
        "odorants": odorants,
        "receptors": int(known.shape[0]),
        "fully_tested": fully,
        "partly_tested": int((np.any(sub, axis=1) & ~np.all(sub, axis=1)).sum()),
        "untested": int((~np.any(sub, axis=1)).sum()),
        "pairs_tested": int(sub.sum()),
        "pairs_total": int(sub.size),
        "agonist_pairs": int((params.efficacy[:, cols] > 0).sum()),
    }


def describe(params: ReceptorParams, odorants=None) -> str:
    """One sentence fit to print beside a result, so a reader knows what it rests on."""
    s = support(params, odorants)
    return (f"rests on {s['pairs_tested']} of {s['pairs_total']} possible receptor-odorant pairs "
            f"actually tested ({s['agonist_pairs']} of them agonists); "
            f"{s['fully_tested']} of {s['receptors']} receptors were tested against all "
            f"{len(s['odorants'])} odorants, {s['untested']} against none")


def restrict_to_tested(params: ReceptorParams, odorants=None, how="all") -> ReceptorParams:
    """Drop receptors that were not tested against the odorants being compared.

    how="all": keep a receptor only if every listed odorant was tested on it. This is the honest
        array for comparing those odorants, and it is usually much smaller.
    how="any": keep a receptor tested against at least one of them.

    The returned parameters carry the restriction in their provenance, so a result made with them
    cannot be mistaken for one made on the full array.
    """
    known = _known(params)
    odorants = tuple(params.odorants) if odorants is None else tuple(odorants)
    cols = _indices(params, odorants)
    sub = known[:, cols]
    keep = np.all(sub, axis=1) if how == "all" else np.any(sub, axis=1)
    if how not in ("all", "any"):
        raise ValueError("how must be 'all' or 'any'")
    if not keep.any():
        raise NoCoverageInformation(
            f"no receptor was tested against {how} of {odorants}; refusing to return an empty array")
    rec = tuple(np.asarray(params.receptors, object)[keep]) if len(params.receptors) else ()
    note = (f"; RESTRICTED to the {int(keep.sum())} of {known.shape[0]} receptors tested against "
            f"{how} of {odorants}")
    return replace(params, affinity=params.affinity[keep], efficacy=params.efficacy[keep],
                   known=known[keep], receptors=rec, provenance=params.provenance + note)


def comparable_odorants(params: ReceptorParams, min_receptors=3) -> list:
    """Pairs of odorants with at least `min_receptors` receptors tested against both.

    Any other pair cannot be compared on measured ground, however different their arrays look.
    """
    known = _known(params)
    out = []
    for i in range(len(params.odorants)):
        for j in range(i + 1, len(params.odorants)):
            n = int((known[:, i] & known[:, j]).sum())
            if n >= min_receptors:
                out.append((params.odorants[i], params.odorants[j], n))
    return sorted(out, key=lambda t: -t[2])
