"""Human detection thresholds against the model: the benchmark the acid panel was chosen for.

If the chain from air to receptor is right, and detection happens at a fixed level of receptor
drive, then the model's receptor activation AT each acid's measured human threshold should be
roughly the same across the series. Scatter says the chain is wrong somewhere.

Thresholds: data/thresholds/acid_thresholds.csv. Primary: Cometto-Muniz & Abraham 2010, the only
source found with analytically verified vapour concentrations, which tested only C4, C6 and C8
from this panel. Secondary, cross-check only: Nagata's triangle-bag compilation (C3-C6).
Nothing measured was found for C7, C9 or C10.

NOT APPLIED, and why: corrections for mucus differing from water (lipophilic odorants partition
more into mucus; Scott et al. 2014) and for acid ionisation at mucus pH. The sourced values these
need (log P, pKa, nasal mucus pH) were not collected: the search for them was stopped by an
automated safeguard. Ionisation would scale all acids by roughly the same factor (similar pKa), so
it should move the level more than the spread; the lipophilicity correction would raise C8 most.
MODELLED throughout.
"""
import csv
import os
import numpy as np

from sw_enose import BiomimeticNose
from sw_enose.air import T_BODY, T_REF, air_to_liquid, load_henry_csv
from sw_enose.coverage import restrict_to_tested
from sw_enose.m2or import build_params
from sw_enose.panels import ACID_CARBONS, ACID_MEASURED_HENRY, ACID_SERIES

HERE = os.path.dirname(__file__)
h = load_henry_csv(os.path.join(HERE, "data/henry/sander_v5_subset.csv"),
                   "measured:Sander v5.0.0 (2023); see data/henry/README.md")
full = build_params(os.path.join(HERE, "data/m2or/repo/M2OR_20230428.csv"), ACID_SERIES)
tight = restrict_to_tested(full, ACID_SERIES)
thr = {"primary": {}, "secondary": {}}
for row in csv.DictReader(open(os.path.join(HERE, "data/thresholds/acid_thresholds.csv"))):
    if row["odorant"] in ACID_SERIES:
        thr[row["role"]][row["odorant"]] = float(row["threshold_ppb"])


def peak_at_threshold(params, thresholds, temp):
    nose = BiomimeticNose(params, neuron_noise=0.0)
    out = {}
    for a, ppb in thresholds.items():
        c = np.zeros(len(params.odorants))
        c[list(params.odorants).index(a)] = air_to_liquid(h, {a: ppb}, temp_k=temp)[a]
        out[a] = float(nose.receptor_activation(c).max())
    return out


for role, label in (("primary", "PRIMARY (Cometto-Muniz & Abraham 2010)"),
                    ("secondary", "SECONDARY (Nagata, cross-check only)")):
    print(f"\n{label}")
    for pname, p in (("8 fully-tested receptors", tight),
                     (f"all {full.affinity.shape[0]} receptors with an acid agonist", full)):
        for temp in (T_REF, T_BODY):
            pk = peak_at_threshold(p, thr[role], temp)
            line = "  ".join(f"C{ACID_CARBONS[a]} {v:.1e}{'*' if a not in ACID_MEASURED_HENRY else ''}"
                             for a, v in pk.items())
            spread = np.log10(max(pk.values()) / min(pk.values()))
            print(f"   {pname:40s} {temp:6.2f} K  peak activation at threshold: {line}"
                  f"   spread {spread:.2f} log units")
print("   * Henry constant is an estimate, not a measurement")

print("""
Reading it:
 - The two acids with measured Henry constants, C4 and C6, sit at almost the same activation
   at threshold on the 8 fully-tested receptors (0.75% and 0.91% at 298 K, 0.08 log units
   apart): what a fixed detection criterion predicts. Two points are a weak pass, not a result.
 - Adding C8 widens the spread to about 0.9-1.1 log units. Its Henry constant is the suspect
   estimate, and the missing mucus correction would raise it, narrowing the gap.
 - The secondary set scatters by about 1.9 log units (C3 high, C5 low).
 - Detection sits at roughly 0.1-1% of maximal receptor activation: far below EC50.
 - Verdict: underpowered and inconclusive. It needs measured thresholds for C7-C10, measured
   Henry constants for C8-C10, and the mucus and ionisation corrections.""")
