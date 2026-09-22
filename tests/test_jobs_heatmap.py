"""Tests for jobs heatmap helpers."""

import pandas as pd

from analysis.jobs_heatmap import build_count_matrix, prepare_heatmap_frame


def test_prepare_drops_multi_and_nationwide():
    df = pd.DataFrame(
        {
            "city": ["Hà Nội", "Hà Nội", "Toàn Quốc", "Hồ Chí Minh"],
            "job_group": ["Software Engineer", "QA / Tester", "Other", "Software Engineer"],
            "is_multi_location": [False, True, False, False],
        }
    )
    out = prepare_heatmap_frame(df)
    assert set(out["city"]) == {"Hà Nội", "Hồ Chí Minh"}
    assert len(out) == 2


def test_build_count_matrix():
    df = pd.DataFrame(
        {
            "city": ["Hà Nội"] * 5 + ["Hồ Chí Minh"] * 5,
            "job_group": ["Software Engineer"] * 3
            + ["QA / Tester"] * 2
            + ["Software Engineer"] * 4
            + ["Business Analyst"] * 1,
        }
    )
    matrix = build_count_matrix(df)
    assert matrix.loc["Hà Nội", "Software Engineer"] == 3
    assert "Hồ Chí Minh" in matrix.index
