from __future__ import annotations

from pathlib import Path

import pandas as pd

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
