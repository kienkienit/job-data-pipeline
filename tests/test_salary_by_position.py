"""Tests for salary-by-position analysis helpers."""

import pandas as pd

from analysis.salary_by_position import compute_avg_salary, prepare_salary_frame


def test_compute_avg_salary_both_sides():
    df = pd.DataFrame({"min_salary": [10.0, 5.0], "max_salary": [20.0, None]})
    avg = compute_avg_salary(df)
    assert avg.iloc[0] == 15.0
    assert avg.iloc[1] == 5.0


def test_prepare_filters_negotiable_and_suspicious():
    df = pd.DataFrame(
        {
            "job_group": ["Software Engineer", "Software Engineer", "QA / Tester", "QA / Tester", "QA / Tester", "Other"],
            "min_salary": [10e6, None, 8e6, 9e6, 7e6, 1e6],
            "max_salary": [20e6, None, 12e6, 11e6, 10e6, 2e6],
            "salary_unit": ["VND"] * 6,
            "is_negotiable": [False, True, False, False, False, False],
            "salary_suspicious": [False, False, False, False, False, True],
        }
    )
    out = prepare_salary_frame(df)
    # negotiable + suspicious dropped; Other has only 1 row (<3) dropped
    assert set(out["job_group"]) == {"QA / Tester"}
    assert len(out) == 3
