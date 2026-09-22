from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analysis.data_loader import ensure_figures_dir, load_jobs

_EXCLUDE_CITIES = {"toàn quốc", "nước ngoài"}


def prepare_heatmap_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    multi = out["is_multi_location"].fillna(False).astype(bool)

    filtered = out.loc[
        ~multi
        & out["city"].notna()
        & (out["city"].astype(str).str.strip() != "")
        & out["job_group"].notna()
    ].copy()

    filtered = filtered[
        ~filtered["city"].astype(str).str.strip().str.lower().isin(_EXCLUDE_CITIES)
    ]
    return filtered


def build_count_matrix(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.groupby(["city", "job_group"], dropna=False)
        .size()
        .unstack(fill_value=0)
    )
    city_totals = counts.sum(axis=1).sort_values(ascending=False)
    keep_cities = city_totals[city_totals >= 5].index
    counts = counts.loc[keep_cities]
    col_order = counts.sum(axis=0).sort_values(ascending=False).index
    return counts[col_order]


def plot_jobs_heatmap(df: pd.DataFrame, out_path: Path) -> Path:
    plot_df = prepare_heatmap_frame(df)
    if plot_df.empty:
        raise ValueError("No rows left after heatmap filters — cannot plot")

    matrix = build_count_matrix(plot_df)
    if matrix.empty:
        raise ValueError("Count matrix is empty — cannot plot")

    height = max(6, 0.35 * len(matrix))
    plt.figure(figsize=(12, height))
    sns.heatmap(matrix, cmap="YlOrRd", linewidths=0.3, linecolor="white")
    plt.title("Job count heatmap: city × job group")
    plt.xlabel("Job group")
    plt.ylabel("City")
    plt.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main() -> None:
    df = load_jobs()
    out = ensure_figures_dir() / "jobs_heatmap.png"
    path = plot_jobs_heatmap(df, out)
    filtered = prepare_heatmap_frame(df)
    print(f"Saved → {path}")
    print(f"Rows used: {len(filtered)}")


if __name__ == "__main__":
    main()
