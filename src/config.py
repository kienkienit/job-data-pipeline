from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://macbook@localhost:5432/jobs_db")

RAW_CSV = PROJECT_ROOT / os.getenv("RAW_CSV_PATH", "data/data.csv")
PROCESSED_CSV = PROJECT_ROOT / os.getenv( "PROCESSED_CSV_PATH", "data/processed/jobs_clean.csv")
