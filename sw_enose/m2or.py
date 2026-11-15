"""Build receptor parameters from the M2OR database (Lalis et al., Nucleic Acids Res 2024, PMID 37870437).

Data: chemosim-lab/M2OR on GitHub, snapshot M2OR_20230428.csv, Apache-2.0 licence.
Fetch with:  git clone --depth 1 https://github.com/chemosim-lab/M2OR data/m2or/repo

What is measured and what is assumed (carried into the provenance string):
- EC50 values: MEASURED (dose-response rows, parameter 'ec50', in cultured cells; mostly luciferase assays).
- Tested non-agonists (EC50 'n.d'): MEASURED as no response up to the highest concentration tested.
- Efficacy: NOT in M2OR. Assumed 1 for every agonist. This is an assumption, not data.
- Pairs never tested: UNKNOWN. Set to no response in the arrays, and marked False in `known`.
- Reference receptors only (no 'Mutation' entry and no variant suffix such as OR7D4_R88W_T133M); mixtures excluded; EC50 outside 1e-3..1e5 uM excluded as likely unit errors.
"""
import csv
import math
from collections import defaultdict
import numpy as np
from .data import ReceptorParams

SOURCE = "M2OR_20230428 (Lalis et al., Nucleic Acids Res 2024, PMID 37870437; Apache-2.0)"
EC50_RANGE_UM = (1e-3, 1e5)


def _ec50_um(row):
    try:
        x = float(row["Value"])
    except ValueError:
        return None
    u = row["Unit"]
    if u == "Log(M)":
        return 10 ** x * 1e6
    if u == "uM":
        return x
    if u == "M":
        return x * 1e6
    return None


def read_pairs(path, species="homo sapiens"):
    """Return {(receptor, molecule_name): ('agonist', ec50_uM) or ('none', max_tested_uM or None)}.
    Several measurements of one pair: agonist wins; its EC50 is the geometric mean."""
    ag, neg, names = defaultdict(list), set(), {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["species"] != species or r["Parameter"] != "ec50" or r["Mixture"] == "mixture" or r["Mutation"]:
                continue
            rec = (r["Gene ID"] or r["Uniprot ID"]).strip()
            rec = rec[1:] if rec.startswith("hOR") else rec
            mol = r["InChI Key"]
            if not rec or not mol or "_" in rec:   # names like OR7D4_R88W_T133M are variants; keep the reference receptor only
                continue
            names[mol] = r["Name"] or mol
            if r["Responsive"] == "1":
                v = _ec50_um(r)
                if v is not None and EC50_RANGE_UM[0] <= v <= EC50_RANGE_UM[1]:
                    ag[(rec, mol)].append(v)
            elif r["Unit"] == "n.d":
                neg.add((rec, mol))
    pairs = {}
    for k in neg:
        pairs[k] = ("none", None)
    for k, vs in ag.items():
        pairs[k] = ("agonist", math.exp(sum(math.log(v) for v in vs) / len(vs)))
    return {(rec, names[mol]): v for (rec, mol), v in pairs.items()}


def build_params(path, odorants, receptors=None, species="homo sapiens", min_agonists=1):
    """Receptor parameters for the chosen odorant names. Receptors default to all with at least
    `min_agonists` measured agonists among those odorants."""
    pairs = read_pairs(path, species)
    odorants = tuple(odorants)
    if receptors is None:
        count = defaultdict(int)
        for (rec, mol), (kind, _) in pairs.items():
            if mol in odorants and kind == "agonist":
                count[rec] += 1
        receptors = sorted(r for r, n in count.items() if n >= min_agonists)
    receptors = tuple(receptors)
    nR, nO = len(receptors), len(odorants)
    affinity = np.full((nR, nO), 1e6)   # placeholder K for no response (efficacy is 0 there anyway)
    efficacy = np.zeros((nR, nO))
    known = np.zeros((nR, nO), bool)
    for i, rec in enumerate(receptors):
        for j, mol in enumerate(odorants):
            v = pairs.get((rec, mol))
            if v is None:
                continue
            known[i, j] = True
            if v[0] == "agonist":
                affinity[i, j], efficacy[i, j] = v[1], 1.0
    prov = (f"measured:{SOURCE}; EC50 in uM from cultured-cell assays; ASSUMED efficacy=1 for agonists; "
            f"untested pairs set to no response ({int((~known).sum())} of {known.size} pairs untested)")
    return ReceptorParams(affinity, efficacy, 1.0, odorants, prov, known, receptors)
