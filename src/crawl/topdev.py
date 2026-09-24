"""Crawl IT jobs from TopDev public API (step 1 prototype).
Uses the same JSON API that topdev.vn frontend calls: GET https://api.topdev.vn/td/v2/jobs
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests

from src.errors import ExtractError, setup_logging

logger = setup_logging()

API_URL = "https://api.topdev.vn/td/v2/jobs"
USER_AGENT = "JobDataPipeline/0.1 (+educational; contact: local-dev)"

JOB_FIELDS = (
    "id,title,salary,slug,detail_url,addresses,skills_str,"
    "job_types_str,job_levels_str,status_display,contract_types_str,"
    "opened,closed,company,skills,experiences_str,refreshed"
)
COMPANY_FIELDS = "id,display_name,slug,image_logo"


def _parse_date_dmy(value: str | None) -> str | None:
    """Convert '24-09-2026' → '2026-09-24'."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def format_salary(salary: dict[str, Any] | None) -> str:
    if not salary:
        return "Thoả thuận"

    if salary.get("is_negotiable") in (1, True, "1"):
        # Still prefer estimate range when API provides one
        mn = salary.get("min_estimate") or salary.get("min_filter")
        mx = salary.get("max_estimate") or salary.get("max_filter")
        currency = (salary.get("currency_estimate") or salary.get("currency") or "VND").upper()
        if mn and mx and mn not in (0, "0", "*") and mx not in (0, "0", "*"):
            return _range_text(float(mn), float(mx), currency)
        return "Thoả thuận"

    currency = (salary.get("currency") or "VND").upper()
    raw_min, raw_max = salary.get("min"), salary.get("max")

    def _num(v: Any) -> float | None:
        if v is None or v in ("*", "", 0, "0"):
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    mn = _num(raw_min) or _num(salary.get("min_estimate")) or _num(salary.get("min_filter"))
    mx = _num(raw_max) or _num(salary.get("max_estimate")) or _num(salary.get("max_filter"))

    if mn is None and mx is None:
        return "Thoả thuận"
    if mn is not None and mx is not None:
        return _range_text(mn, mx, currency)
    if mn is not None:
        return _above_text(mn, currency)
    return _upto_text(mx, currency)  # type: ignore[arg-type]


def _range_text(mn: float, mx: float, currency: str) -> str:
    if currency == "VND":
        return f"{mn / 1_000_000:g} - {mx / 1_000_000:g} triệu"
    return f"{mn:g} - {mx:g} {currency}"


def _above_text(mn: float, currency: str) -> str:
    if currency == "VND":
        return f"Trên {mn / 1_000_000:g} triệu"
    return f"Trên {mn:g} {currency}"


def _upto_text(mx: float, currency: str) -> str:
    if currency == "VND":
        return f"Tới {mx / 1_000_000:g} triệu"
    return f"Tới {mx:g} {currency}"


def format_address(addresses: dict[str, Any] | None) -> str:
    """Best-effort address string for parse_address.

    TopDev often returns 'Quận Hà Đông, Hà Nội' — convert to 'Hà Nội: Quận Hà Đông'
    when possible.
    """
    if not addresses:
        return ""

    sort_addr = (addresses.get("sort_addresses") or "").strip(" ,")
    region = (addresses.get("address_region_list") or "").strip()
    city = region.replace("Thành phố ", "").replace("Tỉnh ", "").strip()

    if sort_addr and "," in sort_addr:
        left, right = [p.strip() for p in sort_addr.rsplit(",", 1)]
        if right:
            return f"{right}: {left}"
        return sort_addr

    # City-only (e.g. sort_addresses == "Hồ Chí Minh")
    if city and (not sort_addr or sort_addr == city or city in sort_addr):
        if sort_addr and sort_addr != city and city not in sort_addr:
            return f"{city}: {sort_addr}"
        return city or sort_addr

    return sort_addr or city or region


def map_job_to_row(job: dict[str, Any]) -> dict[str, Any]:
    """Map one API job → columns compatible with data/data.csv."""
    company = job.get("company") or {}
    refreshed = job.get("refreshed") or {}
    closed = job.get("closed") or {}

    created = _parse_date_dmy(refreshed.get("date")) or _parse_date_dmy(
        (job.get("opened") or {}).get("date") if isinstance(job.get("opened"), dict) else None
    )

    return {
        "created_date": created,
        "job_title": job.get("title") or "",
        "company": company.get("display_name") or company.get("name") or "",
        "salary": format_salary(job.get("salary")),
        "address": format_address(job.get("addresses")),
        "time": closed.get("since") or refreshed.get("since") or "",
        "link_description": job.get("detail_url") or "",
        "source_id": job.get("id"),
        "skills_str": job.get("skills_str") or "",
    }


def fetch_jobs_page(
    page: int = 1,
    page_size: int = 20,
    *,
    session: requests.Session | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Fetch one page from TopDev jobs API."""
    params = {
        "page": page,
        "page_size": page_size,
        "fields[job]": JOB_FIELDS,
        "fields[company]": COMPANY_FIELDS,
    }
    sess = session or requests.Session()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Origin": "https://topdev.vn",
        "Referer": "https://topdev.vn/",
    }
    url = f"{API_URL}?{urlencode(params)}"
    try:
        resp = sess.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        raise ExtractError(f"TopDev API request failed (page={page}): {exc}") from exc


def crawl_topdev(
    *,
    max_pages: int = 3,
    page_size: int = 20,
    delay_seconds: float = 1.0,
) -> pd.DataFrame:
    if max_pages <= 0:
        raise ExtractError("max_pages must be > 0")

    session = requests.Session()
    rows: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        payload = fetch_jobs_page(page=page, page_size=page_size, session=session)
        data = payload.get("data") or []
        meta = payload.get("meta") or {}
        logger.info(
            "TopDev page %s/%s — got %s jobs (total≈%s)",
            page,
            max_pages,
            len(data),
            meta.get("total"),
        )
        if not data:
            break
        rows.extend(map_job_to_row(job) for job in data)

        last_page = int(meta.get("last_page") or page)
        if page >= last_page:
            break
        if page < max_pages and delay_seconds > 0:
            time.sleep(delay_seconds)

    if not rows:
        raise ExtractError("TopDev crawl returned no jobs")

    df = pd.DataFrame(rows)
    # Drop duplicates by source link / id
    if "source_id" in df.columns:
        df = df.drop_duplicates(subset=["source_id"], keep="first")
    logger.info("Crawled %s unique jobs from TopDev", len(df))
    return df


def save_crawl_csv(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Wrote crawl CSV → %s", path)
    return path


if __name__ == "__main__":
    from src import config

    out = config.PROJECT_ROOT / "data" / "raw" / "topdev_sample.csv"
    frame = crawl_topdev(max_pages=5, page_size=20, delay_seconds=1.0)
    save_crawl_csv(frame, out)
    print(frame[["job_title", "company", "salary", "address"]].head(5).to_string(index=False))
    print(f"\nSaved {len(frame)} rows → {out}")
