"""Unit tests for address parsing."""

from src.transform.address import parse_address


def test_none_and_empty():
    assert parse_address(None) == {
        "city": None,
        "district": None,
        "is_multi_location": False,
    }
    assert parse_address("")["city"] is None
    assert parse_address("   ")["city"] is None


def test_city_only():
    assert parse_address("Hà Nội") == {
        "city": "Hà Nội",
        "district": None,
        "is_multi_location": False,
    }
    assert parse_address("Toàn Quốc")["city"] == "Toàn Quốc"
    assert parse_address("Nước Ngoài")["district"] is None


def test_city_and_district():
    assert parse_address("Hà Nội: Cầu Giấy") == {
        "city": "Hà Nội",
        "district": "Cầu Giấy",
        "is_multi_location": False,
    }
    assert parse_address("Hồ Chí Minh: Quận 1") == {
        "city": "Hồ Chí Minh",
        "district": "Quận 1",
        "is_multi_location": False,
    }


def test_district_with_commas_still_single_city():
    result = parse_address("Hà Nội: Cầu Giấy, Hai Bà Trưng")
    assert result["city"] == "Hà Nội"
    assert result["district"] == "Cầu Giấy, Hai Bà Trưng"
    assert result["is_multi_location"] is False


def test_multi_colon_locations():
    result = parse_address("Hà Nội: Ba Đình: Hồ Chí Minh: Tân Bình")
    assert result["city"] == "Hà Nội"
    assert result["district"] == "Ba Đình: Hồ Chí Minh: Tân Bình"
    assert result["is_multi_location"] is True


def test_noisy_province_as_district():
    result = parse_address("Hà Nội: Hồ Chí Minh")
    assert result["city"] == "Hà Nội"
    assert result["district"] == "Hồ Chí Minh"
    assert result["is_multi_location"] is True
