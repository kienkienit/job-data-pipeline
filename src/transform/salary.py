from __future__ import annotations

import math
import re
from typing import Any

# Numbers like 10, 2,000, 4.6, 0.0
_NUMBER_RE = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")


def _empty_result(*, is_negotiable: bool = False) -> dict[str, Any]:
    return {
        "min_salary": None,
        "max_salary": None,
        "salary_unit": None,
        "is_negotiable": is_negotiable,
    }


def _extract_numbers(text: str) -> list[float]:
    values: list[float] = []
    for match in _NUMBER_RE.findall(text):
        normalized = match.replace(",", "")
        values.append(float(normalized))
    return values


def parse_salary(raw: Any) -> dict[str, Any]:
    """Normalize a salary string into structured fields.
    Returns
    -------
    dict with keys:
        min_salary, max_salary, salary_unit ("VND"|"USD"|None), is_negotiable
    """
    if raw is None:
        return _empty_result()

    if isinstance(raw, float) and math.isnan(raw):
        return _empty_result()

    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return _empty_result()

    lower = text.lower()

    if "thoả thuận" in lower:
        return _empty_result(is_negotiable=True)

    if "usd" in lower or "$" in text:
        unit = "USD"
    elif "triệu" in lower:
        unit = "VND"
    else:
        unit = None

    numbers = _extract_numbers(text)
    if not numbers:
        return {
            "min_salary": None,
            "max_salary": None,
            "salary_unit": unit,
            "is_negotiable": False,
        }

    if all(n == 0 for n in numbers):
        return _empty_result()

    if unit == "VND":
        numbers = [n * 1_000_000 for n in numbers]

    if "trên" in lower:
        return {
            "min_salary": numbers[0],
            "max_salary": None,
            "salary_unit": unit,
            "is_negotiable": False,
        }

    if "tới" in lower:
        return {
            "min_salary": None,
            "max_salary": numbers[0],
            "salary_unit": unit,
            "is_negotiable": False,
        }

    if len(numbers) >= 2:
        return {
            "min_salary": numbers[0],
            "max_salary": numbers[1],
            "salary_unit": unit,
            "is_negotiable": False,
        }

    return {
        "min_salary": numbers[0],
        "max_salary": numbers[0],
        "salary_unit": unit,
        "is_negotiable": False,
    }


def is_salary_suspicious(
    min_salary: float | None,
    max_salary: float | None,
    salary_unit: str | None,
    *,
    usd_max_reasonable: float = 20_000,
    vnd_max_reasonable: float = 200_000_000,
) -> bool:
    if salary_unit is None:
        return False

    candidates = [v for v in (min_salary, max_salary) if v is not None]
    if not candidates:
        return False

    peak = max(candidates)
    if salary_unit == "USD" and peak > usd_max_reasonable:
        return True
    if salary_unit == "VND" and peak > vnd_max_reasonable:
        return True
    if min_salary is not None and max_salary is not None and min_salary > max_salary:
        return True
    return False
