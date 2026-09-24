from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests

from analysis.data_loader import load_jobs
from src import config
from src.errors import PipelineError, setup_logging
from src.notify.state import load_notified_keys, save_notified_keys

logger = setup_logging()

# Title patterns that mean Data Engineer (not every "Data / AI" role)
_DE_PATTERNS = [
    re.compile(r"data\s*engineer", re.I),
    re.compile(r"data\s*eng\b", re.I),
    re.compile(r"kỹ\s*sư\s*dữ\s*liệu", re.I),
    re.compile(r"ky\s*su\s*du\s*lieu", re.I),
    re.compile(r"\betl\s*engineer\b", re.I),
    re.compile(r"\bde\b(?=.*\b(data|spark|airflow|warehouse)\b)", re.I),
]


class NotifyError(PipelineError):
    """Raised when Discord notification fails."""


def is_data_engineer_job(title: Any) -> bool:
    if title is None or (isinstance(title, float) and pd.isna(title)):
        return False
    text = str(title).strip()
    if not text:
        return False
    return any(p.search(text) for p in _DE_PATTERNS)


def job_key(row: pd.Series) -> str:
    if "source_id" in row.index and pd.notna(row.get("source_id")):
        return f"id:{row['source_id']}"
    link = row.get("link_description")
    if pd.notna(link) and str(link).strip():
        return f"url:{link}"
    return f"title:{row.get('job_title')}|{row.get('company')}"


def filter_new_de_jobs(df: pd.DataFrame, already: set[str]) -> pd.DataFrame:
    if df.empty:
        return df
    mask = df["job_title"].apply(is_data_engineer_job)
    de = df.loc[mask].copy()
    if de.empty:
        return de
    de["_key"] = de.apply(job_key, axis=1)
    return de.loc[~de["_key"].isin(already)].copy()


def build_discord_content(row: pd.Series) -> dict[str, Any]:
    title = str(row.get("job_title") or "Untitled")
    company = str(row.get("company") or "N/A")
    salary = str(row.get("salary") or "N/A")
    city = str(row.get("city") or row.get("address") or "N/A")
    link = str(row.get("link_description") or "")
    skills = str(row.get("skills_str") or "")

    description_parts = [
        f"**Company:** {company}",
        f"**Salary:** {salary}",
        f"**Location:** {city}",
    ]
    if skills and skills != "nan":
        description_parts.append(f"**Skills:** {skills[:200]}")
    if link and link != "nan":
        description_parts.append(f"[View job]({link})")

    return {
        "embeds": [
            {
                "title": f"🆕 DE: {title[:200]}",
                "description": "\n".join(description_parts),
                "color": 5814783,
            }
        ]
    }


def send_discord_webhook(webhook_url: str, payload: dict[str, Any]) -> None:
    if not webhook_url or not webhook_url.strip():
        raise NotifyError("DISCORD_WEBHOOK_URL is empty — set it in .env")
    try:
        resp = requests.post(webhook_url, json=payload, timeout=30)
        if resp.status_code >= 400:
            raise NotifyError(
                f"Discord webhook failed ({resp.status_code}): {resp.text[:300]}"
            )
    except requests.RequestException as exc:
        raise NotifyError(f"Discord webhook request error: {exc}") from exc


def notify_new_de_jobs(
    *,
    webhook_url: str | None = None,
    dry_run: bool = False,
    max_messages: int | None = None,
) -> int:
    url = webhook_url if webhook_url is not None else config.DISCORD_WEBHOOK_URL
    limit = config.DISCORD_MAX_MESSAGES if max_messages is None else max_messages
    df = load_jobs()
    already = load_notified_keys()
    new_jobs = filter_new_de_jobs(df, already)

    if new_jobs.empty:
        logger.info("No new Data Engineer jobs to notify")
        return 0

    if "created_date" in new_jobs.columns:
        new_jobs = new_jobs.sort_values("created_date", ascending=False)

    to_send = new_jobs.head(limit)
    sent_keys: set[str] = set()

    for _, row in to_send.iterrows():
        payload = build_discord_content(row)
        key = row["_key"]
        if dry_run:
            logger.info("[dry-run] Would notify: %s", row.get("job_title"))
        else:
            send_discord_webhook(url, payload)
            logger.info("Notified Discord: %s", row.get("job_title"))
        sent_keys.add(key)

    if not dry_run and sent_keys:
        # File backend needs full set; DB backend upserts (ON CONFLICT DO NOTHING).
        save_notified_keys(already | sent_keys)

    logger.info("Discord notify done — sent %s job(s)", len(sent_keys))
    return len(sent_keys)
