from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src import config


def load_jobs(*, prefer_db: bool = True) -> pd.DataFrame:
    if prefer_db:
        try:
            engine = create_engine(config.DB_URL)
            df = pd.read_sql("SELECT * FROM jobs", engine)
            if not df.empty:
                return df
        except Exception:
            pass

    if not config.PROCESSED_CSV.exists():
        raise FileNotFoundError(
            f"No data found in DB or {config.PROCESSED_CSV}. "
            "Run: PYTHONPATH=. python -m src.pipeline"
        )
    return pd.read_csv(config.PROCESSED_CSV)


def ensure_figures_dir() -> Path:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return config.FIGURES_DIR
