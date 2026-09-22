from __future__ import annotations

import pandas as pd

from src.errors import TransformError, setup_logging
from src.transform.address import parse_address
from src.transform.job_title import normalize_job_title
from src.transform.salary import is_salary_suspicious, parse_salary

logger = setup_logging()


def transform(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise TransformError("Cannot transform an empty DataFrame")
    try:
        out = df.copy()
        salary = out["salary"].apply(parse_salary).apply(pd.Series)
        address = out["address"].apply(parse_address).apply(pd.Series)
        out["min_salary"] = salary["min_salary"]
        out["max_salary"] = salary["max_salary"]
        out["salary_unit"] = salary["salary_unit"]
        out["is_negotiable"] = salary["is_negotiable"]
        out["salary_suspicious"] = [
            is_salary_suspicious(row.min_salary, row.max_salary, row.salary_unit)
            for row in salary.itertuples(index=False)
        ]

        out["city"] = address["city"]
        out["district"] = address["district"]
        out["is_multi_location"] = address["is_multi_location"]

        out["job_group"] = out["job_title"].apply(normalize_job_title)
        logger.info("Transformed %s rows", len(out))
        return out
    except TransformError:
        raise
    except KeyError as exc:
        raise TransformError(f"Missing expected column during transform: {exc}") from exc
    except Exception as exc:
        raise TransformError(f"Transform failed: {exc}") from exc
