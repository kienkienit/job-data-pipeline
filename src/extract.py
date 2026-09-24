"""Extract step: load jobs from CSV or TopDev crawl."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import config
from src.errors import ExtractError, setup_logging

logger = setup_logging()

REQUIRED_COLUMNS = {"salary", "address", "job_title"}


def extract_from_csv(csv_path: Path | str) -> pd.DataFrame:
    path = Path(csv_path)

    if not path.exists():
        raise ExtractError(f"CSV not found: {path}")

    if not path.is_file():
        raise ExtractError(f"CSV path is not a file: {path}")

    if path.stat().st_size == 0:
        raise ExtractError(f"CSV file is empty: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ExtractError(f"Failed to read CSV (corrupt or invalid): {path}") from exc

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ExtractError(f"CSV missing required columns: {sorted(missing)}")

    if df.empty:
        raise ExtractError(f"CSV has headers but no data rows: {path}")

    logger.info("Extracted %s rows from %s", len(df), path)
    return df


def extract_from_crawl(
    *,
    max_pages: int | None = None,
    page_size: int | None = None,
    delay_seconds: float | None = None,
    save_raw_csv: Path | None = None,
) -> pd.DataFrame:
    from src.crawl.topdev import crawl_topdev, save_crawl_csv

    df = crawl_topdev(
        max_pages=max_pages if max_pages is not None else config.CRAWL_MAX_PAGES,
        page_size=page_size if page_size is not None else config.CRAWL_PAGE_SIZE,
        delay_seconds=(
            delay_seconds if delay_seconds is not None else config.CRAWL_DELAY_SECONDS
        ),
    )

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ExtractError(f"Crawl result missing columns: {sorted(missing)}")
    if df.empty:
        raise ExtractError("Crawl returned an empty DataFrame")

    out_path = save_raw_csv if save_raw_csv is not None else config.CRAWL_RAW_CSV
    save_crawl_csv(df, out_path)
    logger.info("Extracted %s rows from TopDev crawl", len(df))
    return df


def extract(
    source: str | None = None,
    *,
    raw_csv: Path | None = None,
) -> pd.DataFrame:
    mode = (source or config.EXTRACT_SOURCE).strip().lower()
    if mode == "csv":
        return extract_from_csv(raw_csv or config.RAW_CSV)
    if mode == "crawl":
        return extract_from_crawl()
    raise ExtractError(f"Unknown EXTRACT_SOURCE={mode!r}. Use 'csv' or 'crawl'.")
