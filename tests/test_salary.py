"""Unit tests for salary parsing helpers."""

import math

from src.transform.salary import is_salary_suspicious, parse_salary


def test_none_and_empty():
    assert parse_salary(None) == {
        "min_salary": None,
        "max_salary": None,
        "salary_unit": None,
        "is_negotiable": False,
    }
    assert parse_salary("")["min_salary"] is None
    assert parse_salary("   ")["min_salary"] is None


def test_nan_float_and_string():
    assert parse_salary(float("nan"))["min_salary"] is None
    assert parse_salary("nan")["min_salary"] is None
    assert math.isnan(float("nan"))


def test_negotiable():
    result = parse_salary("Thoả thuận")
    assert result["is_negotiable"] is True
    assert result["min_salary"] is None
    assert result["max_salary"] is None
    assert result["salary_unit"] is None


def test_range_vnd():
    result = parse_salary("10 - 20 triệu")
    assert result == {
        "min_salary": 10_000_000,
        "max_salary": 20_000_000,
        "salary_unit": "VND",
        "is_negotiable": False,
    }


def test_range_vnd_decimal():
    result = parse_salary("7.5 - 14 triệu")
    assert result["min_salary"] == 7_500_000
    assert result["max_salary"] == 14_000_000
    assert result["salary_unit"] == "VND"


def test_tren_vnd():
    result = parse_salary("Trên 10 triệu")
    assert result["min_salary"] == 10_000_000
    assert result["max_salary"] is None
    assert result["salary_unit"] == "VND"


def test_toi_vnd():
    result = parse_salary("Tới 35 triệu")
    assert result["min_salary"] is None
    assert result["max_salary"] == 35_000_000
    assert result["salary_unit"] == "VND"


def test_toi_vnd_decimal():
    result = parse_salary("Tới 4.6 triệu")
    assert result["max_salary"] == 4_600_000
    assert result["salary_unit"] == "VND"


def test_range_usd_with_thousand_comma():
    result = parse_salary("1,000 - 2,000 USD")
    assert result == {
        "min_salary": 1000.0,
        "max_salary": 2000.0,
        "salary_unit": "USD",
        "is_negotiable": False,
    }


def test_tren_usd():
    result = parse_salary("Trên 1,000 USD")
    assert result["min_salary"] == 1000.0
    assert result["max_salary"] is None
    assert result["salary_unit"] == "USD"


def test_toi_usd():
    result = parse_salary("Tới 2,000 USD")
    assert result["min_salary"] is None
    assert result["max_salary"] == 2000.0
    assert result["salary_unit"] == "USD"


def test_zero_placeholder_invalid():
    assert parse_salary("0.0 - 0.0 triệu") == {
        "min_salary": None,
        "max_salary": None,
        "salary_unit": None,
        "is_negotiable": False,
    }
    assert parse_salary("Trên 0.0 triệu")["min_salary"] is None


def test_suspicious_usd_outlier():
    assert is_salary_suspicious(84_000, None, "USD") is True
    assert is_salary_suspicious(None, 30_000_000, "USD") is True
    assert is_salary_suspicious(10_000_000, 14_000_000, "USD") is True


def test_suspicious_normal_values():
    assert is_salary_suspicious(1000, 2000, "USD") is False
    assert is_salary_suspicious(10_000_000, 20_000_000, "VND") is False
    assert is_salary_suspicious(None, 35_000_000, "VND") is False


def test_suspicious_negotiable_or_missing():
    assert is_salary_suspicious(None, None, None) is False
    assert is_salary_suspicious(None, None, "USD") is False


def test_suspicious_min_greater_than_max():
    assert is_salary_suspicious(20_000_000, 10_000_000, "VND") is True
