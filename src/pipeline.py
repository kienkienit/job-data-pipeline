from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src import config
from src.errors import PipelineError, setup_logging
from src.extract import extract
from src.load import load_to_db
from src.transform_batch import transform

logger = setup_logging()


def run_extract_transform(
    raw_csv: Path = config.RAW_CSV,
    output_csv: Path = config.PROCESSED_CSV,
    *,
    source: str | None = None,
) -> pd.DataFrame:
    """Extract (csv or crawl) → Transform → write processed CSV."""
    raw = extract(source=source, raw_csv=raw_csv)
    cleaned = transform(raw)

    try:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(output_csv, index=False)
    except OSError as exc:
        raise PipelineError(f"Cannot write processed CSV to {output_csv}: {exc}") from exc

    logger.info("Wrote %s rows → %s", len(cleaned), output_csv)
    return cleaned


def run_pipeline(
    *,
    skip_load: bool = False,
    raw_csv: Path = config.RAW_CSV,
    output_csv: Path = config.PROCESSED_CSV,
    db_url: str | None = None,
    source: str | None = None,
) -> pd.DataFrame:
    try:
        cleaned = run_extract_transform(
            raw_csv=raw_csv,
            output_csv=output_csv,
            source=source,
        )

        if skip_load:
            logger.info("skip_load=True — skipped database write")
        else:
            load_to_db(cleaned, db_url or config.DB_URL)

        logger.info("Pipeline finished successfully")
        return cleaned
    except PipelineError:
        logger.exception("Pipeline failed with a known error")
        raise
    except Exception:
        logger.exception("Pipeline failed with an unexpected error")
        raise


if __name__ == "__main__":
    try:
        run_pipeline(skip_load=False)
    except PipelineError as exc:
        logger.error("Aborted: %s", exc)
        sys.exit(1)
