from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analysis.data_loader import ensure_figures_dir, load_jobs


def compute_avg_salary(df: pd.DataFrame) -> pd.Series:
    return df[["min_salary", "max_salary"]].mean(axis=1, skipna=True)


def prepare_salary_frame(
    df: pd.DataFrame,
    *,
    salary_unit: str = "VND",
) -> pd.DataFrame:
    out = df.copy()
    out["avg_salary"] = compute_avg_salary(out)

    negotiable = out["is_negotiable"].fillna(False).astype(bool)
    suspicious = out["salary_suspicious"].fillna(False).astype(bool)

    filtered = out.loc[
        out["avg_salary"].notna()
        & ~negotiable
        & ~suspicious
        & (out["salary_unit"] == salary_unit)
        & out["job_group"].notna()
    ].copy()

    counts = filtered["job_group"].value_counts()
    keep = counts[counts >= 3].index
    return filtered[filtered["job_group"].isin(keep)]


def plot_salary_by_position(
    df: pd.DataFrame,
    out_path: Path,
    *,
    salary_unit: str = "VND",
) -> Path:
    plot_df = prepare_salary_frame(df, salary_unit=salary_unit)
    if plot_df.empty:
        raise ValueError("No rows left after salary filters — cannot plot")

    order = (
        plot_df.groupby("job_group")["avg_salary"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    plt.figure(figsize=(12, 6))
    sns.boxplot(
        data=plot_df,
        x="job_group",
        y="avg_salary",
        order=order,
    )
    plt.xticks(rotation=25, ha="right")
    ylabel = "Average salary (VND)" if salary_unit == "VND" else f"Average salary ({salary_unit})"
    plt.ylabel(ylabel)
    plt.xlabel("Job group")
    plt.title(f"Salary distribution by job group ({salary_unit})")
    plt.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main() -> None:
    df = load_jobs()
    out = ensure_figures_dir() / "salary_by_position.png"
    path = plot_salary_by_position(df, out)
    print(f"Saved → {path}")
    print(f"Rows plotted: {len(prepare_salary_frame(df))}")


if __name__ == "__main__":
    main()
