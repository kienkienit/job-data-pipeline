"""Persist Discord notified job keys (local file or Postgres)."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from src import config
from src.errors import setup_logging

logger = setup_logging()

TABLE_NAME = "discord_notified"

_CREATE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    job_key TEXT PRIMARY KEY,
    notified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""


def load_notified_keys(
    path: Path | None = None,
    *,
    backend: str | None = None,
) -> set[str]:
    mode = (backend or config.DISCORD_STATE_BACKEND).strip().lower()
    if mode == "db":
        return _load_from_db()
    return _load_from_file(path or config.DISCORD_STATE_PATH)


def save_notified_keys(
    keys: set[str],
    path: Path | None = None,
    *,
    backend: str | None = None,
) -> None:
    mode = (backend or config.DISCORD_STATE_BACKEND).strip().lower()
    if mode == "db":
        _save_to_db(keys)
        return
    _save_to_file(keys, path or config.DISCORD_STATE_PATH)


def _load_from_file(state_path: Path) -> set[str]:
    if not state_path.exists():
        return set()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return set(data.get("notified_keys") or [])
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read Discord state file: %s", exc)
        return set()


def _save_to_file(keys: set[str], state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"notified_keys": sorted(keys)}
    state_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _load_from_db() -> set[str]:
    if not config.DB_URL or not str(config.DB_URL).strip():
        logger.warning("DISCORD_STATE_BACKEND=db but DB_URL empty — no keys loaded")
        return set()
    try:
        engine = create_engine(config.DB_URL)
        with engine.begin() as conn:
            conn.execute(text(_CREATE_SQL))
            rows = conn.execute(text(f"SELECT job_key FROM {TABLE_NAME}"))
            return {r[0] for r in rows}
    except SQLAlchemyError as exc:
        logger.warning("Could not load Discord state from DB: %s", exc)
        return set()


def _save_to_db(keys: set[str]) -> None:
    if not keys:
        return
    if not config.DB_URL or not str(config.DB_URL).strip():
        raise RuntimeError("DISCORD_STATE_BACKEND=db but DB_URL is empty")
    engine = create_engine(config.DB_URL)
    with engine.begin() as conn:
        conn.execute(text(_CREATE_SQL))
        for key in sorted(keys):
            conn.execute(
                text(
                    f"""
                    INSERT INTO {TABLE_NAME} (job_key)
                    VALUES (:job_key)
                    ON CONFLICT (job_key) DO NOTHING
                    """
                ),
                {"job_key": key},
            )
    logger.info("Saved %s Discord notified key(s) to DB", len(keys))
