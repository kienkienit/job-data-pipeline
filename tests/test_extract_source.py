"""Tests for extract source dispatch (csv | crawl)."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.errors import ExtractError
from src.extract import extract
from src.pipeline import run_pipeline


def test_extract_unknown_source():
    with pytest.raises(ExtractError, match="Unknown EXTRACT_SOURCE"):
        extract(source="ftp")


def test_extract_crawl_uses_topdev(tmp_path: Path):
    fake = pd.DataFrame(
        {
            "created_date": ["2026-09-24"],
            "job_title": ["Data Engineer"],
            "company": ["ACME"],
            "salary": ["20 - 40 triệu"],
            "address": ["Hà Nội"],
            "time": ["x"],
            "link_description": ["https://topdev.vn/x"],
            "source_id": [1],
            "skills_str": ["Python"],
        }
    )
    with patch("src.crawl.topdev.crawl_topdev", return_value=fake) as mock_crawl:
        with patch("src.crawl.topdev.save_crawl_csv") as mock_save:
            with patch("src.config.CRAWL_RAW_CSV", tmp_path / "raw.csv"):
                df = extract(source="crawl")
    assert len(df) == 1
    assert df.loc[0, "job_title"] == "Data Engineer"
    mock_crawl.assert_called_once()
    mock_save.assert_called_once()


def test_pipeline_crawl_skip_load(tmp_path: Path):
    fake = pd.DataFrame(
        {
            "created_date": ["2026-09-24"],
            "job_title": ["Java Developer"],
            "company": ["ACME"],
            "salary": ["10 - 20 triệu"],
            "address": ["Hà Nội: Cầu Giấy"],
            "time": ["x"],
            "link_description": ["https://topdev.vn/x"],
        }
    )
    out = tmp_path / "clean.csv"
    with patch("src.crawl.topdev.crawl_topdev", return_value=fake):
        with patch("src.crawl.topdev.save_crawl_csv"):
            df = run_pipeline(
                skip_load=True,
                source="crawl",
                output_csv=out,
            )
    assert out.exists()
    assert df.loc[0, "job_group"] == "Software Engineer"
