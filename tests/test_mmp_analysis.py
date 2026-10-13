"""Scientifically defined, deterministic paired-potency checks."""
import math
import pytest
from mmp_optimizer.mmp_analysis import compare_potency_pair


def test_tenfold_shift():
    result = compare_potency_pair(100, 10)
    assert result["p_reference"] == pytest.approx(7.0)
    assert result["p_analogue"] == pytest.approx(8.0)
    assert result["delta_p_activity"] == pytest.approx(1.0)
    assert result["fold_shift"] == pytest.approx(10.0)


def test_equal_and_reverse_shifts():
    assert compare_potency_pair(25, 25)["delta_p_activity"] == pytest.approx(0)
    assert compare_potency_pair(10, 100)["delta_p_activity"] == pytest.approx(-1)


def test_unit_and_endpoint_consistency():
    a = compare_potency_pair(100, 10, "nM", "Ki")
    b = compare_potency_pair(0.1, 0.01, "uM", "Ki")
    assert a["delta_p_activity"] == pytest.approx(b["delta_p_activity"])
    assert a["p_analogue"] == pytest.approx(b["p_analogue"])


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_invalid_values(value):
    with pytest.raises(ValueError):
        compare_potency_pair(value, 10)


@pytest.mark.parametrize("value", [True, "10", None])
def test_non_numeric_values(value):
    with pytest.raises(TypeError):
        compare_potency_pair(10, value)


def test_units_and_endpoints_required():
    with pytest.raises(ValueError):
        compare_potency_pair(10, 1, unit="mg")
    with pytest.raises(ValueError):
        compare_potency_pair(10, 1, endpoint="GI50")


def test_numerical_extremes():
    with pytest.raises(ValueError):
        compare_potency_pair(1e300, 1e-300, unit="M")
