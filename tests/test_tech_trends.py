"""Tests for tech trend counting."""

import pandas as pd

from analysis.tech_trends import count_tech_mentions


def test_counts_keywords_once_per_title():
    titles = pd.Series(
        [
            "Senior Java Developer",
            "Java Spring Boot Engineer",
            "React Native Developer",
            "Nhân viên hành chính",
        ]
    )
    counts = count_tech_mentions(titles)
    assert counts["java"] == 2
    assert counts["react native"] == 1
    assert "python" not in counts


def test_nodejs_aliases_merge():
    titles = pd.Series(["Node.js Developer", "Nodejs Engineer", "Node JS Intern"])
    counts = count_tech_mentions(titles)
    assert counts["nodejs"] == 3
