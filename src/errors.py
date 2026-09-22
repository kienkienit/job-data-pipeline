"""Pipeline errors and logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path


class PipelineError(Exception):
    """Base error for the ETL pipeline."""


class ExtractError(PipelineError):
    """Raised when reading the source CSV fails."""


class TransformError(PipelineError):
    """Raised when cleaning / transforming data fails."""


class LoadError(PipelineError):
    """Raised when writing to the database fails."""


def setup_logging(log_dir: Path | None = None) -> logging.Logger:
    """Console logger; optionally also write to logs/pipeline.log."""
    logger = logging.getLogger("pipeline")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_dir is None:
        log_dir = Path(__file__).resolve().parents[1] / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not create log file under %s", log_dir)

    return logger
