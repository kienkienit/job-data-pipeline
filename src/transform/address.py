from __future__ import annotations

import math
from typing import Any

_KNOWN_PROVINCES = {
    "hà nội",
    "hồ chí minh",
    "đà nẵng",
    "hải phòng",
    "cần thơ",
    "toàn quốc",
    "nước ngoài",
    "bình dương",
    "đồng nai",
    "nghệ an",
    "thừa thiên huế",
    "khánh hoà",
    "thanh hoá",
    "bắc ninh",
    "hải dương",
    "vĩnh phúc",
    "long an",
    "đồng tháp",
}


def _empty_result(*, is_multi_location: bool = False) -> dict[str, Any]:
    return {
        "city": None,
        "district": None,
        "is_multi_location": is_multi_location,
    }


def parse_address(raw: Any) -> dict[str, Any]:
    if raw is None:
        return _empty_result()

    if isinstance(raw, float) and math.isnan(raw):
        return _empty_result()

    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return _empty_result()

    if ":" not in text:
        return {
            "city": text,
            "district": None,
            "is_multi_location": False,
        }

    city, district = text.split(":", 1)
    city = city.strip() or None
    district = district.strip() or None

    colon_count = text.count(":")
    district_looks_like_province = (
        district is not None and district.lower() in _KNOWN_PROVINCES
    )
    is_multi = colon_count >= 2 or district_looks_like_province

    return {
        "city": city,
        "district": district,
        "is_multi_location": is_multi,
    }
