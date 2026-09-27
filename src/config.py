from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def use_psycopg2(db_url: str) -> str:
    """Point Postgres URLs at psycopg2 (the driver this project installs).

    Newer SQLAlchemy treats a bare ``postgresql://`` URL as psycopg v3.
    Neon/Supabase connection strings usually omit the driver name.
    """
    url = (db_url or "").strip()
    if url.startswith("postgresql+psycopg2://"):
        return url
    for prefix in ("postgresql+psycopg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix) :]
    return url


DB_URL = use_psycopg2(
    os.getenv("DB_URL", "postgresql+psycopg2://macbook@localhost:5432/jobs_db")
)

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

# Discord: new Data Engineer jobs
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
DISCORD_INTERVAL_HOURS = int(os.getenv("DISCORD_INTERVAL_HOURS", "2"))
DISCORD_STATE_PATH = PROJECT_ROOT / os.getenv(
    "DISCORD_STATE_PATH", "data/state/discord_notified.json"
)
# "file" (local) | "db" (GitHub Actions / shared Postgres)
DISCORD_STATE_BACKEND = os.getenv("DISCORD_STATE_BACKEND", "file").strip().lower()
DISCORD_MAX_MESSAGES = int(os.getenv("DISCORD_MAX_MESSAGES", "10"))

