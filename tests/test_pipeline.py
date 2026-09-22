from pathlib import Path

import pandas as pd
import pytest

from src.errors import ExtractError
from src.extract import extract_from_csv
from src.pipeline import run_extract_transform
from src.transform_batch import transform


def test_extract_missing_file(tmp_path: Path):
    with pytest.raises(ExtractError, match="not found"):
        extract_from_csv(tmp_path / "nope.csv")


def test_transform_adds_columns():
    df = pd.DataFrame(
        {
            "created_date": ["2023-08-01"],
            "job_title": ["Java Developer"],
            "company": ["ACME"],
            "salary": ["10 - 20 triệu"],
            "address": ["Hà Nội: Cầu Giấy"],
            "time": ["x"],
            "link_description": ["http://example.com"],
        }
    )
    out = transform(df)
    assert out.loc[0, "min_salary"] == 10_000_000
    assert out.loc[0, "max_salary"] == 20_000_000
    assert out.loc[0, "salary_unit"] == "VND"
    assert out.loc[0, "city"] == "Hà Nội"
    assert out.loc[0, "district"] == "Cầu Giấy"
    assert out.loc[0, "job_group"] == "Software Engineer"
    assert bool(out.loc[0, "is_multi_location"]) is False
    assert bool(out.loc[0, "salary_suspicious"]) is False


def test_run_extract_transform_writes_csv(tmp_path: Path):
    raw = tmp_path / "raw.csv"
    raw.write_text(
        "created_date,job_title,company,salary,address,time,link_description\n"
        "2023-08-01,Business Analyst,Co,Thoả thuận,Hà Nội,t,http://x\n",
        encoding="utf-8",
    )
    out = tmp_path / "clean.csv"
    cleaned_df = run_extract_transform(raw_csv=raw, output_csv=out)
    assert out.exists()
    assert len(cleaned_df) == 1
    cleaned = pd.read_csv(out)
    assert cleaned.loc[0, "job_group"] == "Business Analyst"
    assert bool(cleaned.loc[0, "is_negotiable"]) is True
