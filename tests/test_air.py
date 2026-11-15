import numpy as np
import pytest

from sw_enose import synthetic_params
from sw_enose.air import (AIR_TO_MUCUS, HenryTable, MissingHenryConstant, P_STANDARD, R_GAS, T_REF,
                          air_molar, air_to_liquid, concentration_vector_from_air,
                          h_cp_from_atm_m3_per_mol, h_cp_from_dimensionless, h_cp_from_m_per_atm,
                          load_henry_csv, ppb_for_liquid, synthetic_henry_table)
from sw_enose.mixture import UnknownOdorant


# --- the arithmetic, against values computed by hand ---

def test_ideal_gas_step_matches_hand_calculation():
    # n/V = P/RT = 101325 / (8.314462618 * 298.15) = 40.874 mol/m^3 of air.
    # One part per million of that is 4.0874e-5 mol/m^3 = 0.040874 uM.
    assert air_molar(1000.0, temp_k=T_REF) == pytest.approx(0.0408740, rel=1e-4)


def test_air_molar_is_linear_and_falls_with_temperature():
    assert air_molar(200.0) == pytest.approx(2 * air_molar(100.0))
    assert air_molar(100.0, temp_k=310.15) < air_molar(100.0, temp_k=T_REF)


def test_negative_ppb_rejected():
    with pytest.raises(ValueError):
        air_molar(-1.0)


def test_unit_conversions_round_trip():
    # 1 atm m^3/mol, converted and read back as a dimensionless partition coefficient at T_REF.
    h = float(h_cp_from_atm_m3_per_mol(1.0))
    assert h == pytest.approx(1.0 / P_STANDARD)
    t = HenryTable(("x",), np.array([h]), "synthetic:unit check")
    assert t.k_aw("x", temp_k=T_REF) == pytest.approx(P_STANDARD / (R_GAS * T_REF), rel=1e-12)


def test_solubility_and_dimensionless_forms_agree():
    # 1 M/atm is 1000 mol/(m^3 atm); as H^cp that is 1000/101325 mol/(m^3 Pa).
    assert float(h_cp_from_m_per_atm(1.0)) == pytest.approx(1000.0 / P_STANDARD)
    k_aw = 0.03
    h = float(h_cp_from_dimensionless(k_aw, temp_k=T_REF))
    back = HenryTable(("x",), np.array([h]), "synthetic:unit check").k_aw("x", temp_k=T_REF)
    assert back == pytest.approx(k_aw, rel=1e-12)


# --- the partitioning step ---

def test_more_soluble_odorant_reaches_a_higher_liquid_concentration():
    t = HenryTable(("shy", "soluble"), np.array([1e-3, 1e0]), "synthetic:two volatilities")
    got = air_to_liquid(t, {"shy": 100.0, "soluble": 100.0})
    assert got["soluble"] / got["shy"] == pytest.approx(1000.0)


def test_liquid_concentration_is_linear_in_ppb():
    t = synthetic_henry_table(("A",))
    assert air_to_liquid(t, {"A": 50.0})["A"] == pytest.approx(5 * air_to_liquid(t, {"A": 10.0})["A"])


def test_partition_step_matches_henrys_law_by_hand():
    # H^cp = 1e-2 mol/(m^3 Pa), 1 ppm at one atmosphere: p = 1e-6 * 101325 = 0.101325 Pa, so
    # c = 1.01325e-3 mol/m^3 = 1.01325 uM. No temperature coefficient, so temperature does not enter.
    t = HenryTable(("x",), np.array([1e-2]), "synthetic:hand check")
    assert air_to_liquid(t, {"x": 1000.0})["x"] == pytest.approx(1.01325, rel=1e-9)


def test_knobs_scale_the_result_and_reject_nonsense():
    t = synthetic_henry_table(("A",))
    base = air_to_liquid(t, {"A": 10.0})["A"]
    assert air_to_liquid(t, {"A": 10.0}, uptake_fraction=0.25)["A"] == pytest.approx(0.25 * base)
    assert air_to_liquid(t, {"A": 10.0}, mucus_water_ratio=3.0)["A"] == pytest.approx(3.0 * base)
    for bad in ({"uptake_fraction": 0.0}, {"uptake_fraction": 1.5}, {"mucus_water_ratio": 0.0}):
        with pytest.raises(ValueError):
            air_to_liquid(t, {"A": 10.0}, **bad)


def test_van_t_hoff_makes_an_exothermic_dissolution_less_soluble_when_warm():
    t = HenryTable(("x",), np.array([1e-2]), "synthetic:temperature check",
                   temp_dep=np.array([5000.0]), temp_ref_k=T_REF)
    assert t.h_cp_at("x", temp_k=T_REF) == pytest.approx(1e-2)
    assert t.h_cp_at("x", temp_k=310.15) < t.h_cp_at("x", temp_k=T_REF)
    assert t.h_cp_at("x", temp_k=280.0) > t.h_cp_at("x", temp_k=T_REF)


# --- refusals: the point of the module is that it will not guess ---

def test_odorant_absent_from_the_table_is_refused():
    with pytest.raises(UnknownOdorant):
        air_to_liquid(synthetic_henry_table(("A", "B")), {"hydrogen sulfide": 1.0})


def test_odorant_with_no_measured_constant_is_refused_not_guessed():
    t = HenryTable(("known", "untested"), np.array([1e-2, np.nan]), "synthetic:one value missing")
    assert t.missing == ("untested",)
    with pytest.raises(MissingHenryConstant):
        air_to_liquid(t, {"untested": 10.0})


def test_provenance_is_mandatory():
    with pytest.raises(ValueError):
        HenryTable(("A",), np.array([1e-2]), "from memory")


def test_table_shape_and_sign_are_checked():
    with pytest.raises(ValueError):
        HenryTable(("A", "B"), np.array([1e-2]), "synthetic:mismatched")
    with pytest.raises(ValueError):
        HenryTable(("A",), np.array([-1e-2]), "synthetic:negative")
    with pytest.raises(ValueError):
        HenryTable(("A",), np.array([1e-2]), "synthetic:bad dep", temp_dep=np.array([1.0, 2.0]))


def test_ppb_for_liquid_inverts_air_to_liquid():
    t = synthetic_henry_table(("A", "B"), seed=3)
    for name in ("A", "B"):
        ppb = ppb_for_liquid(t, name, 25.0)
        assert air_to_liquid(t, {name: ppb})[name] == pytest.approx(25.0, rel=1e-9)
    # and it inverts the knobs too
    ppb = ppb_for_liquid(t, "A", 25.0, uptake_fraction=0.1, mucus_water_ratio=2.0)
    got = air_to_liquid(t, {"A": ppb}, uptake_fraction=0.1, mucus_water_ratio=2.0)["A"]
    assert got == pytest.approx(25.0, rel=1e-9)


def test_ppb_for_liquid_refuses_a_missing_constant():
    t = HenryTable(("untested",), np.array([np.nan]), "synthetic:no value")
    with pytest.raises(MissingHenryConstant):
        ppb_for_liquid(t, "untested", 1.0)


# --- the bridge to the receptor array ---

def test_air_mixture_becomes_a_concentration_vector_in_parameter_order():
    p = synthetic_params(odorants=("A", "B", "C"))
    t = HenryTable(("A", "B", "C"), np.array([1e-2, 1e-2, 1e-2]), "synthetic:equal")
    v = concentration_vector_from_air(p, t, {"A": 1000.0, "C": 2000.0})
    assert v[1] == 0.0
    assert v[2] == pytest.approx(2 * v[0])
    assert v[0] == pytest.approx(1.01325, rel=1e-9)


def test_odorant_the_receptors_do_not_cover_is_still_refused():
    p = synthetic_params(odorants=("A", "B"))
    t = synthetic_henry_table(("A", "B", "Z"))
    with pytest.raises(UnknownOdorant):
        concentration_vector_from_air(p, t, {"Z": 100.0})


# --- the CSV loader ---

def test_csv_loader_requires_provenance_and_the_constant_column(tmp_path):
    f = tmp_path / "h.csv"
    f.write_text("odorant,h_cp_mol_per_m3_Pa,temp_dep_K,source\nx,1e-2,5000,made up\n", encoding="utf-8")
    t = load_henry_csv(f, "measured:a source we actually opened")
    assert t.h_cp_at("x", temp_k=T_REF) == pytest.approx(1e-2)
    assert t.notes == ("made up",)
    assert not t.modelled
    with pytest.raises(ValueError):
        load_henry_csv(f, "remembered")
    bad = tmp_path / "bad.csv"
    bad.write_text("odorant,henry\nx,1e-2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_henry_csv(bad, "measured:x")


def test_csv_blank_constant_is_kept_as_missing(tmp_path):
    f = tmp_path / "h.csv"
    f.write_text("odorant,h_cp_mol_per_m3_Pa\nx,1e-2\ny,\n", encoding="utf-8")
    t = load_henry_csv(f, "measured:partial table")
    assert t.missing == ("y",)


# --- the module must keep saying what it leaves out ---

def test_caveats_are_documented():
    assert "equilibrium_only" in AIR_TO_MUCUS and "mucus_is_not_water" in AIR_TO_MUCUS
    assert all(len(v) == 2 and v[1] for v in AIR_TO_MUCUS.values())
