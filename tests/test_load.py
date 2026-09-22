"""Tests for the Load step (uses SQLite — no Postgres required)."""

from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from src.errors import LoadError
from src.load import load_to_db
from src.pipeline import run_pipeline


def test_load_rejects_empty():
    with pytest.raises(LoadError, match="empty"):
        load_to_db(pd.DataFrame(), "sqlite:///:memory:")


def test_load_to_sqlite(tmp_path: Path):
    df = pd.DataFrame(
        {
            "job_title": ["Java Developer"],
            "job_group": ["Software Engineer"],
            "city": ["Hà Nội"],
            "min_salary": [10_000_000.0],
            "max_salary": [20_000_000.0],
        }
    )
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path}"
    load_to_db(df, url, table_name="jobs")

    engine = create_engine(url)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
    assert count == 1


def test_run_pipeline_skip_load(tmp_path: Path):
    raw = tmp_path / "raw.csv"
    raw.write_text(
        "created_date,job_title,company,salary,address,time,link_description\n"
        "2023-08-01,Java Developer,Co,10 - 20 triệu,Hà Nội,t,http://x\n",
        encoding="utf-8",
    )
    out = tmp_path / "clean.csv"
    df = run_pipeline(
        skip_load=True,
        raw_csv=raw,
        output_csv=out,
    )
    assert out.exists()
    assert df.loc[0, "job_group"] == "Software Engineer"
