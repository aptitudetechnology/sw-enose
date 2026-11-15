"""Air-to-mucus conversion: from an odorant concentration in air to the concentration at the receptor.

Why this exists: every receptor number in this project is a concentration in LIQUID (micromolar),
because the assays behind it bathe cultured cells in odorant solution. Every real-world measurement
of a smell is a concentration in AIR (ppb or ppm). Without a conversion the nose cannot take a real
input at all, and `mixture.py` says so.

What here is arithmetic and what is a measurement:
 - ppb in air -> moles per cubic metre of air: arithmetic, from the gas constant.
 - Henry's law is a definition; the van 't Hoff temperature correction is standard algebra.
 - The Henry's law constant OF A COMPOUND is a measurement and needs a source. **This module ships
   no compound constants.** Load them with `load_henry_csv` (provenance mandatory), or build a
   `HenryTable` directly. `synthetic_henry_table` invents them for testing the machinery only.

Constants are held as H^cp, the solubility form: H^cp = c_aqueous / p_gas, in mol/(m^3 Pa). Published
values come in several forms; `h_cp_from_*` convert the common ones.

Everything this model leaves out, each of which makes it a CEILING rather than a prediction, is listed
in `AIR_TO_MUCUS`. Read that before using a number from here.
"""
import csv
from dataclasses import dataclass
import numpy as np

from .mixture import UnknownOdorant, concentration_vector

R_GAS = 8.314462618          # Pa m^3 / (mol K)
P_STANDARD = 101325.0        # Pa, one standard atmosphere
T_REF = 298.15               # K (25 C), the reference temperature of most tabulated Henry constants
T_BODY = 310.15              # K (37 C). The nasal mucosa is cooler than core and swings through the
                             # breathing cycle; that variation is not modelled. See AIR_TO_MUCUS.
UM_PER_MOL_PER_M3 = 1000.0   # 1 mol/m^3 = 1 mmol/L = 1000 umol/L = 1000 uM
L_PER_M3 = 1000.0

AIR_TO_MUCUS = {
    "equilibrium_only": (
        "The mucus is assumed to reach equilibrium with the air being breathed in.",
        "UNTESTED here, and an upper bound: how much of an odorant actually crosses into mucus "
        "depends on flow rate, residence time and solubility. A soluble odorant is absorbed in the "
        "front of the nose, so epithelium further back meets less of it than the inhaled air carries. "
        "None of that is modelled: treat the output as the most the receptor could see, not what it does see"),
    "mucus_is_not_water": (
        "Tabulated Henry constants are for air and pure water; the receptor sits in mucus.",
        "UNTESTED: mucus carries mucins, lipids and odorant-binding proteins, so partitioning differs, "
        "probably in favour of hydrophobic odorants. `mucus_water_ratio` is a knob for this with no "
        "measured value behind it; it defaults to 1.0, meaning 'assume mucus behaves as water'"),
    "temperature": (
        "Constants are corrected from the table's reference temperature with van 't Hoff.",
        "The algebra is standard; the correction is only as good as the table's temperature coefficient, "
        "and a single temperature stands in for the real gradient along the airway"),
    "no_kinetics": (
        "Steady state only: one air concentration in, one liquid concentration out.",
        "UNTESTED: a sniff is a transient, and the rise and fall of concentration at the receptor is "
        "not modelled here. Adaptation in `bio.py` acts on time steps, but those steps carry no transport"),
    "no_binding_proteins": (
        "Odorant-binding proteins are not modelled.",
        "They are thought to help carry hydrophobic odorants through mucus; omitting them likely "
        "understates how much of such an odorant reaches a receptor"),
}


class MissingHenryConstant(KeyError):
    """The odorant is in the table but the source gave no Henry constant for it."""


@dataclass(frozen=True)
class HenryTable:
    """Henry's law solubility constants for named odorants. Provenance is mandatory.

    h_cp: mol/(m^3 Pa) at temp_ref_k. NaN means the source has no value: asking for it raises
    rather than returning a guess.
    temp_dep: d ln(H^cp) / d(1/T) in kelvin, as compilations tabulate it. NaN or 0 = no correction.
    """
    odorants: tuple
    h_cp: np.ndarray
    provenance: str
    temp_dep: np.ndarray = None
    temp_ref_k: float = T_REF
    notes: tuple = ()
    h_cp_low: np.ndarray = None    # lowest and highest value any source in the compilation gives,
    h_cp_high: np.ndarray = None   # so the spread between labs stays visible. NaN where unknown.

    def __post_init__(self):
        if not (self.provenance.startswith("synthetic:") or self.provenance.startswith("measured:")):
            raise ValueError("provenance must start with 'synthetic:' or 'measured:'")
        if len(self.odorants) != len(self.h_cp):
            raise ValueError("one Henry constant per odorant name")
        for name in ("temp_dep", "h_cp_low", "h_cp_high"):
            v = getattr(self, name)
            if v is not None and len(v) != len(self.h_cp):
                raise ValueError(f"one {name} value per odorant name")
        for name in ("h_cp", "h_cp_low", "h_cp_high"):
            v = getattr(self, name)
            if v is None:
                continue
            v = np.asarray(v, float)
            if np.any(v[np.isfinite(v)] <= 0):
                raise ValueError(f"{name}: Henry constants must be positive")
        if self.temp_ref_k <= 0:
            raise ValueError("reference temperature must be positive")

    def bracket(self, name, temp_k=T_BODY):
        """(low, chosen, high) Henry constant at `temp_k`. low/high are NaN where the source gives
        only one value; the temperature correction is applied to all three alike."""
        j = self.index(name)
        chosen = self.h_cp_at(name, temp_k)
        scale = chosen / float(self.h_cp[j])
        def side(arr):
            if arr is None:
                return float("nan")
            return float(arr[j]) * scale
        return side(self.h_cp_low), chosen, side(self.h_cp_high)

    @property
    def modelled(self) -> bool:
        return self.provenance.startswith("synthetic:")

    @property
    def missing(self) -> tuple:
        """Odorants listed with no constant, so the nose must refuse them."""
        return tuple(o for o, h in zip(self.odorants, self.h_cp) if not np.isfinite(h))

    def index(self, name) -> int:
        low = [o.lower() for o in self.odorants]
        try:
            return low.index(str(name).lower())
        except ValueError:
            raise UnknownOdorant(
                f"{name!r} has no Henry's law constant in this table ({self.provenance.split(':')[0]}); "
                "refusing to guess how much of it reaches the receptor") from None

    def h_cp_at(self, name, temp_k=T_BODY) -> float:
        """Henry constant in mol/(m^3 Pa) at `temp_k`, van 't Hoff corrected from temp_ref_k."""
        j = self.index(name)
        h = float(self.h_cp[j])
        if not np.isfinite(h):
            raise MissingHenryConstant(
                f"{name!r} is in the table but has no measured Henry's law constant; refusing to guess")
        if self.temp_dep is not None:
            c = float(self.temp_dep[j])
            if np.isfinite(c) and c != 0.0:
                h *= float(np.exp(c * (1.0 / temp_k - 1.0 / self.temp_ref_k)))
        return h

    def k_aw(self, name, temp_k=T_BODY) -> float:
        """Dimensionless air-water partition coefficient, c_air / c_water. Large = stays in the air."""
        return 1.0 / (self.h_cp_at(name, temp_k) * R_GAS * temp_k)


# --- converting published forms into H^cp, mol/(m^3 Pa). Pure algebra. ---

def h_cp_from_atm_m3_per_mol(h):
    """H in atm m^3/mol (the volatility form used by US compilations) -> H^cp."""
    return 1.0 / (np.asarray(h, float) * P_STANDARD)


def h_cp_from_m_per_atm(kh):
    """K_H in M/atm = mol/(L atm) (the solubility form) -> H^cp."""
    return np.asarray(kh, float) * L_PER_M3 / P_STANDARD


def h_cp_from_dimensionless(k_aw, temp_k=T_REF):
    """Dimensionless air-water partition coefficient c_air/c_water -> H^cp, at the stated temperature."""
    return 1.0 / (np.asarray(k_aw, float) * R_GAS * temp_k)


# --- the conversion itself ---

def air_molar(ppb, temp_k=T_BODY, pressure_pa=P_STANDARD):
    """Concentration of an odorant present at `ppb` parts per billion by volume, in uM OF AIR.

    This is the gas phase only: it is not what the receptor sees. Use `air_to_liquid` for that.
    """
    ppb = np.asarray(ppb, float)
    if np.any(ppb < 0):
        raise ValueError("ppb must be >= 0")
    return ppb * 1e-9 * pressure_pa / (R_GAS * temp_k) * UM_PER_MOL_PER_M3


def air_to_liquid(table: HenryTable, mixture_ppb: dict, temp_k=T_BODY, pressure_pa=P_STANDARD,
                  mucus_water_ratio=1.0, uptake_fraction=1.0) -> dict:
    """{odorant: ppb in air} -> {odorant: uM in the liquid at the receptor}, at equilibrium.

    mucus_water_ratio: concentration in mucus divided by concentration in water at the same air
        concentration. 1.0 assumes mucus behaves as water. No measured value; see AIR_TO_MUCUS.
    uptake_fraction: 0..1, a blunt stand-in for incomplete transfer. 1.0 is full equilibrium, the
        ceiling. Any other value is invented unless you have a source for it.

    The result is MODELLED and is an upper bound. Pair it with `table.provenance` wherever it is shown.
    """
    if not 0 < uptake_fraction <= 1:
        raise ValueError("uptake_fraction must be in (0, 1]")
    if mucus_water_ratio <= 0:
        raise ValueError("mucus_water_ratio must be positive")
    if temp_k <= 0 or pressure_pa <= 0:
        raise ValueError("temperature and pressure must be positive")
    out = {}
    for name, ppb in mixture_ppb.items():
        if ppb < 0:
            raise ValueError(f"{name!r}: ppb must be >= 0")
        p_partial = float(ppb) * 1e-9 * pressure_pa                      # Pa
        c_aq = table.h_cp_at(name, temp_k) * p_partial                   # mol/m^3 in water
        out[name] = c_aq * UM_PER_MOL_PER_M3 * mucus_water_ratio * uptake_fraction
    return out


def ppb_for_liquid_at(h_cp, target_um, pressure_pa=P_STANDARD, mucus_water_ratio=1.0,
                      uptake_fraction=1.0) -> float:
    """As `ppb_for_liquid`, but for a Henry constant given directly, already at the temperature of
    interest. Useful for sweeping the spread a compilation reports across labs."""
    if target_um < 0:
        raise ValueError("target_um must be >= 0")
    if not 0 < uptake_fraction <= 1 or mucus_water_ratio <= 0:
        raise ValueError("uptake_fraction must be in (0, 1] and mucus_water_ratio positive")
    if not np.isfinite(h_cp) or h_cp <= 0:
        raise ValueError("h_cp must be finite and positive")
    c_aq = target_um / (UM_PER_MOL_PER_M3 * mucus_water_ratio * uptake_fraction)   # mol/m^3
    return c_aq / (h_cp * 1e-9 * pressure_pa)


def ppb_for_liquid(table: HenryTable, name, target_um, temp_k=T_BODY, pressure_pa=P_STANDARD,
                   mucus_water_ratio=1.0, uptake_fraction=1.0) -> float:
    """The air concentration in ppb that would put `target_um` uM of `name` at the receptor.

    The inverse of `air_to_liquid`, and the question worth asking of a measured EC50: what would have
    to be in the air for the receptor to see its half-maximal concentration. Because `air_to_liquid`
    is a ceiling, this is a FLOOR: the real air concentration needed would be higher.
    """
    return ppb_for_liquid_at(table.h_cp_at(name, temp_k), target_um, pressure_pa,
                             mucus_water_ratio, uptake_fraction)


def concentration_vector_from_air(params, table: HenryTable, mixture_ppb: dict, **kw):
    """Air concentrations in ppb straight to the vector the receptor array wants (uM in liquid).

    Refuses an odorant the Henry table does not cover, and then again if the receptor parameters
    do not cover it.
    """
    return concentration_vector(params, air_to_liquid(table, mixture_ppb, **kw))


# --- building tables ---

def synthetic_henry_table(odorants=("A", "B", "C", "D"), seed=0) -> HenryTable:
    """Invented Henry constants for testing the machinery. Not chemistry.

    Spread over 1e-4 .. 1e1 mol/(m^3 Pa), roughly the range real odorants occupy, so that the
    machinery is exercised across volatilities. The individual numbers mean nothing.
    """
    rng = np.random.default_rng(seed)
    h = 10 ** rng.uniform(-4, 1, size=len(odorants))
    return HenryTable(tuple(odorants), h, f"synthetic:seed={seed}",
                      temp_dep=np.full(len(odorants), 5000.0))


HENRY_CSV_COLUMNS = ("odorant", "h_cp_mol_per_m3_Pa", "temp_dep_K", "h_cp_low", "h_cp_high", "source")

# Sign convention of the temperature coefficient, written down because it is easy to get backwards
# and the source does not state it. henrys-law.org heads the column "d ln Hs cp / d (1/T)" with no
# minus sign and prints positive values (butanoic acid 7100 K). Used directly as the coefficient in
# `h_cp_at`, a positive value makes a compound LESS soluble as it warms, which is the right direction
# for an exothermic dissolution, as these are. If a future source heads the column "-d ln H / d(1/T)",
# negate its values before putting them in the file.
TEMP_DEP_CONVENTION = "d ln(H^cp) / d(1/T) in K, positive = less soluble when warmer"


def load_henry_csv(path, provenance, temp_ref_k=T_REF) -> HenryTable:
    """Load a curated CSV of Henry constants. `provenance` is mandatory and must name the source.

    Columns: odorant, h_cp_mol_per_m3_Pa, and optionally temp_dep_K, h_cp_low, h_cp_high and source.
    A blank constant means the source has no value for that odorant, which is kept as NaN so the
    nose refuses it instead of guessing. Use the `h_cp_from_*` helpers to convert published units
    before writing the file, and record in `source` which form each value came from. The temperature
    coefficient must follow TEMP_DEP_CONVENTION.
    """
    cols = {k: [] for k in ("h_cp_mol_per_m3_Pa", "temp_dep_K", "h_cp_low", "h_cp_high")}
    names, notes = [], []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "odorant" not in reader.fieldnames:
            raise ValueError(f"{path}: needs a header with at least {HENRY_CSV_COLUMNS[:2]}")
        if "h_cp_mol_per_m3_Pa" not in reader.fieldnames:
            raise ValueError(f"{path}: no 'h_cp_mol_per_m3_Pa' column; refusing to interpret the numbers")
        for row in reader:
            name = (row["odorant"] or "").strip()
            if not name or name.startswith("#"):
                continue
            for k in cols:
                raw = (row.get(k) or "").strip()
                cols[k].append(float(raw) if raw else (0.0 if k == "temp_dep_K" else float("nan")))
            names.append(name)
            notes.append((row.get("source") or "").strip())
    if not names:
        raise ValueError(f"{path}: no odorants found")
    return HenryTable(tuple(names), np.array(cols["h_cp_mol_per_m3_Pa"], float), provenance,
                      temp_dep=np.array(cols["temp_dep_K"], float), temp_ref_k=temp_ref_k,
                      notes=tuple(notes), h_cp_low=np.array(cols["h_cp_low"], float),
                      h_cp_high=np.array(cols["h_cp_high"], float))
