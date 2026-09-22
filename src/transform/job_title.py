"""Normalize free-text job titles into coarse groups."""

from __future__ import annotations

import math
import re
from typing import Any

DEFAULT_GROUPS: list[dict[str, Any]] = [
    {
        "name": "BrSE / Comtor",
        "keywords": ["brse", "comtor", "bridge engineer"],
    },
    {
        "name": "Business Analyst",
        "keywords": [
            "business analyst",
            "phân tích nghiệp vụ",
            "chuyên viên phân tích",
        ],
    },
    {
        "name": "Project Manager",
        "keywords": [
            "project manager",
            "scrum master",
            "quản lý dự án",
            "product owner",
            "product manager",
        ],
    },
    {
        "name": "QA / Tester",
        "keywords": [
            "tester",
            "kiểm thử",
            "quality assurance",
            "automation test",
            "manual test",
        ],
    },
    {
        "name": "Data / AI",
        "keywords": [
            "data analyst",
            "data engineer",
            "data scientist",
            "machine learning",
            "ai engineer",
            "deep learning",
        ],
    },
    {
        "name": "DevOps / Infra",
        "keywords": [
            "devops",
            "system admin",
            "system administrator",
            "sre",
            "cloud engineer",
            "it helpdesk",
            "it support",
            "network admin",
        ],
    },
    {
        "name": "Design",
        "keywords": [
            "ui/ux",
            "ui ux",
            "ux/ui",
            "ui designer",
            "ux designer",
            "product designer",
            "thiết kế ui",
            "thiết kế ux",
        ],
    },
    {
        "name": "Software Engineer",
        "keywords": [
            "software engineer",
            "developer",
            "lập trình",
            "programmer",
            "frontend",
            "front-end",
            "front end",
            "backend",
            "back-end",
            "back end",
            "fullstack",
            "full-stack",
            "full stack",
            ".net",
            "nodejs",
            "node.js",
            "node js",
            "react",
            "angular",
            "vue",
            "java",
            "python",
            "php",
            "golang",
            "flutter",
            "android",
            "ios",
            "mobile",
            "embedded",
            "unity",
        ],
    },
]

_WORD_KEYWORDS: dict[str, str] = {
    r"\bqa\b": "QA / Tester",
    r"\bba\b": "Business Analyst",
    r"\bpm\b": "Project Manager",
}


def normalize_job_title(
    raw: Any,
    groups: list[dict[str, Any]] | None = None,
) -> str:
    if raw is None:
        return "Other"
    if isinstance(raw, float) and math.isnan(raw):
        return "Other"

    title = str(raw).strip().lower()
    if not title or title == "nan":
        return "Other"

    for pattern, group_name in _WORD_KEYWORDS.items():
        if re.search(pattern, title):
            return group_name

    rules = groups if groups is not None else DEFAULT_GROUPS
    for group in rules:
        name = group.get("name", "Other")
        for kw in group.get("keywords") or []:
            if kw.lower() in title:
                return name

    return "Other"
