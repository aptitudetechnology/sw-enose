"""Odorant panels, chosen for what has actually been measured about them.

Why this exists. The project's first panel was picked to be evocative -- sour, sulfur, spice, mint --
and `sw_enose/coverage.py` then showed it has essentially no joint receptor coverage: of 23 receptors
with a measured agonist among those six odorants, NONE was tested against all six, and only two of
the fifteen odorant pairs have two or more receptors tested against both. Comparisons on that panel
mostly reflect which laboratory screened which receptor.

ACID_SERIES was found by searching M2OR for the odorant set with the best joint coverage, and it is
better on every count that matters:

 - Coverage: 8 receptors tested against all 8 acids, 75 of 104 pairs measured. Measured
   non-responses are information, and most of the matrix is one.
 - Structure: the receptors are chain-length tuned. An OR51 group answers the short acids, OR52B2
   and OR56A5 the long ones, with a monotone shift between. The pattern is a measurement, not an
   artefact of screening.
 - One ordered covariate: chain length drives both the Henry's law constant (solubility falls as the
   chain grows) and the human detection threshold. So the model makes an ORDERED prediction across
   eight compounds, which is much harder to satisfy by luck than a pairwise discrimination.

Names are spelled as M2OR spells them, including the capital in "Heptanoic acid". Lookups elsewhere
in this package are case-insensitive.
"""

#: Straight-chain saturated fatty acids, C3 to C10. The reference panel for anything quantitative.
ACID_SERIES = ("propanoic acid", "butanoic acid", "pentanoic acid", "hexanoic acid",
               "Heptanoic acid", "octanoic acid", "nonanoic acid", "decanoic acid")

#: Carbon count per member, the ordered covariate the panel exists to exploit.
ACID_CARBONS = {"propanoic acid": 3, "butanoic acid": 4, "pentanoic acid": 5, "hexanoic acid": 6,
                "Heptanoic acid": 7, "octanoic acid": 8, "nonanoic acid": 9, "decanoic acid": 10}

#: Members whose Henry's law constant is MEASURED. For C8-C10 the compilation has no measured row
#: at all, only estimates, and octanoic's estimates span a factor of 73 (see data/henry/README.md).
#: Any air-concentration claim about C8-C10 rests on an estimate, which is awkward because that is
#: exactly where the long-chain receptors OR52B2 and OR56A5 are tuned.
ACID_MEASURED_HENRY = ("propanoic acid", "butanoic acid", "pentanoic acid", "hexanoic acid",
                       "Heptanoic acid")

#: The original panel, kept so earlier demos still run. Not fit for a quantitative comparison:
#: see the module docstring and `demo_uncertainty.py` section 3.
EVOCATIVE_PANEL = ("butanoic acid", "isovaleric acid", "Dimethyl trisulfide", "Octanethiol",
                   "cinnamaldehyde", "L-Carvone")
