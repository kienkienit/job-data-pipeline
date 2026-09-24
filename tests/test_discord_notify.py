"""Tests for Discord DE notify helpers (no live webhook)."""

from pathlib import Path

import pandas as pd

from src.notify.discord import (
    filter_new_de_jobs,
    is_data_engineer_job,
)
from src.notify.state import load_notified_keys, save_notified_keys



def test_is_data_engineer_job():
    assert is_data_engineer_job("Senior Data Engineer") is True
    assert is_data_engineer_job("Data Eng (Spark)") is True
    assert is_data_engineer_job("Kỹ sư dữ liệu") is True
    assert is_data_engineer_job("Java Developer") is False
    assert is_data_engineer_job("Data Analyst") is False
    assert is_data_engineer_job("AI Engineer") is False


def test_filter_new_de_jobs_dedupe():
    df = pd.DataFrame(
        {
            "job_title": ["Data Engineer", "Java Developer", "Senior Data Engineer"],
            "company": ["A", "B", "C"],
            "source_id": [1, 2, 3],
            "link_description": ["u1", "u2", "u3"],
            "salary": ["x", "y", "z"],
            "city": ["HN", "HCM", "HN"],
        }
    )
    already = {"id:1"}
    out = filter_new_de_jobs(df, already)
    assert list(out["source_id"]) == [3]


def test_save_and_load_notified_keys(tmp_path: Path):
    path = tmp_path / "state.json"
    save_notified_keys({"id:1", "id:2"}, path=path)
    assert load_notified_keys(path=path) == {"id:1", "id:2"}
