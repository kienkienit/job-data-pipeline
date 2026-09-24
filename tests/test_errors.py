from pathlib import Path

import pandas as pd
import pytest

from src.errors import ExtractError, LoadError, TransformError
from src.extract import extract_from_csv
from src.load import load_to_db
from src.pipeline import run_pipeline
from src.transform_batch import transform


def test_extract_file_not_found(tmp_path: Path):
    with pytest.raises(ExtractError, match="not found"):
        extract_from_csv(tmp_path / "missing.csv")


def test_extract_empty_file(tmp_path: Path):
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ExtractError, match="empty"):
        extract_from_csv(empty)


def test_extract_missing_columns(tmp_path: Path):
    bad = tmp_path / "bad.csv"
    bad.write_text("created_date,company\n2023-01-01,ACME\n", encoding="utf-8")
    with pytest.raises(ExtractError, match="missing required columns"):
        extract_from_csv(bad)


def test_extract_header_only(tmp_path: Path):
    header_only = tmp_path / "header.csv"
    header_only.write_text(
        "created_date,job_title,company,salary,address,time,link_description\n",
        encoding="utf-8",
    )
    with pytest.raises(ExtractError, match="no data rows"):
        extract_from_csv(header_only)


def test_transform_empty_dataframe():
    with pytest.raises(TransformError, match="empty"):
        transform(pd.DataFrame())


def test_load_empty_dataframe():
    with pytest.raises(LoadError, match="empty"):
        load_to_db(pd.DataFrame(), "sqlite:///:memory:")


def test_load_empty_db_url():
    df = pd.DataFrame({"job_title": ["x"]})
    with pytest.raises(LoadError, match="DB_URL"):
        load_to_db(df, "")


def test_load_bad_connection_message():
    df = pd.DataFrame({"job_title": ["x"]})
    with pytest.raises(LoadError, match="(?i)connect|database|failed"):
        load_to_db(df, "postgresql+psycopg2://macbook@localhost:1/jobs_db")


def test_pipeline_propagates_extract_error(tmp_path: Path):
    with pytest.raises(ExtractError):
        run_pipeline(
            skip_load=True,
            source="csv",
            raw_csv=tmp_path / "nope.csv",
            output_csv=tmp_path / "out.csv",
        )
