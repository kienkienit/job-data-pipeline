"""Persist Discord notified job keys in a local JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from src import config
from src.errors import setup_logging

logger = setup_logging()


def load_notified_keys(path: Path | None = None) -> set[str]:
    state_path = path or config.DISCORD_STATE_PATH
    if not state_path.exists():
        return set()
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return set(data.get("notified_keys") or [])
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read Discord state file: %s", exc)
        return set()


def save_notified_keys(keys: set[str], path: Path | None = None) -> None:
    state_path = path or config.DISCORD_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"notified_keys": sorted(keys)}
    state_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
