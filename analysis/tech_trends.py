from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analysis.data_loader import ensure_figures_dir, load_jobs

TECH_KEYWORDS = [
    "machine learning",
    "react native",
    "node.js",
    "nodejs",
    "node js",
    "full stack",
    "fullstack",
    "full-stack",
    "front end",
    "frontend",
    "front-end",
    "back end",
    "backend",
    "back-end",
    "spring boot",
    ".net",
    "dotnet",
    "c#",
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "angular",
    "vue",
    "php",
    "laravel",
    "golang",
    "kotlin",
    "swift",
    "flutter",
    "android",
    "ios",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "devops",
    "embedded",
    "unity",
]


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword.lower())
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


def count_tech_mentions(titles: pd.Series) -> Counter:
    patterns = [(kw, _keyword_pattern(kw)) for kw in TECH_KEYWORDS]
    counter: Counter = Counter()

    for title in titles.dropna().astype(str):
        lower = title.lower()
        matched_canonical: set[str] = set()
        for kw, pattern in patterns:
            if pattern.search(lower):
                label = _canonical_label(kw)
                if label not in matched_canonical:
                    matched_canonical.add(label)
                    counter[label] += 1
    return counter


def _canonical_label(keyword: str) -> str:
    aliases = {
        "node.js": "nodejs",
        "node js": "nodejs",
        "nodejs": "nodejs",
        "full stack": "fullstack",
        "full-stack": "fullstack",
        "fullstack": "fullstack",
        "front end": "frontend",
        "front-end": "frontend",
        "frontend": "frontend",
        "back end": "backend",
        "back-end": "backend",
        "backend": "backend",
        "dotnet": ".net",
        ".net": ".net",
        "c#": "c#",
    }
    return aliases.get(keyword.lower(), keyword.lower())


def plot_tech_trends(
    df: pd.DataFrame,
    out_path: Path,
    *,
    top_n: int = 15,
) -> Path:
    counts = count_tech_mentions(df["job_title"])
    if not counts:
        raise ValueError("No tech keywords found in job titles")

    top = counts.most_common(top_n)
    labels = [k for k, _ in top][::-1]
    values = [v for _, v in top][::-1]

    plt.figure(figsize=(10, 6))
    plt.barh(labels, values, color="steelblue")
    plt.xlabel("Number of job titles mentioning the tech")
    plt.ylabel("Technology")
    plt.title(f"Hot technologies in job titles (top {top_n})")
    plt.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main() -> None:
    df = load_jobs()
    out = ensure_figures_dir() / "tech_trends.png"
    path = plot_tech_trends(df, out)
    counts = count_tech_mentions(df["job_title"])
    print(f"Saved → {path}")
    print("Top 10:", counts.most_common(10))


if __name__ == "__main__":
    main()
