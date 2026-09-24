from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://macbook@localhost:5432/jobs_db")

RAW_CSV = PROJECT_ROOT / os.getenv("RAW_CSV_PATH", "data/data.csv")
PROCESSED_CSV = PROJECT_ROOT / os.getenv(
    "PROCESSED_CSV_PATH", "data/processed/jobs_clean.csv"
)

# "csv" | "crawl" — where Extract reads data from
EXTRACT_SOURCE = os.getenv("EXTRACT_SOURCE", "csv").strip().lower()

# TopDev crawl settings (used when EXTRACT_SOURCE=crawl)
CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "10"))
CRAWL_PAGE_SIZE = int(os.getenv("CRAWL_PAGE_SIZE", "50"))
CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY_SECONDS", "1.0"))
CRAWL_RAW_CSV = PROJECT_ROOT / os.getenv(
    "CRAWL_RAW_CSV_PATH", "data/raw/topdev_latest.csv"
)

# "interval" | "cron"
SCHEDULE_TYPE = os.getenv("SCHEDULE_TYPE", "cron").strip().lower()

# interval mode
PIPELINE_INTERVAL_MINUTES = int(os.getenv("PIPELINE_INTERVAL_MINUTES", "60"))

# cron mode — daily at hour:minute
PIPELINE_CRON_HOUR = int(os.getenv("PIPELINE_CRON_HOUR", "2"))
PIPELINE_CRON_MINUTE = int(os.getenv("PIPELINE_CRON_MINUTE", "0"))

FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
