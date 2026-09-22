from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from src.errors import LoadError, setup_logging

logger = setup_logging()

TABLE_NAME = "jobs"


def _friendly_db_message(exc: BaseException) -> str:
    msg = str(exc).lower()
    if "could not connect" in msg or "connection refused" in msg:
        return (
            "Cannot connect to database — is PostgreSQL running? "
            f"(brew services list). Details: {exc}"
        )
    if "password authentication failed" in msg:
        return f"Database authentication failed — check user/password in DB_URL. Details: {exc}"
    if "does not exist" in msg and "database" in msg:
        return f"Database not found — create it first (CREATE DATABASE jobs_db;). Details: {exc}"
    if "nodename nor servname" in msg or "name or service not known" in msg:
        return f"Database host not reachable — check host in DB_URL. Details: {exc}"
    return f"Failed to load data into DB: {exc}"


def load_to_db(
    df: pd.DataFrame,
    db_url: str,
    table_name: str = TABLE_NAME,
    *,
    if_exists: str = "replace",
) -> None:
    if df.empty:
        raise LoadError("Cannot load an empty DataFrame")

    if not db_url or not str(db_url).strip():
        raise LoadError("DB_URL is empty — set it in .env (see .env.example)")

    try:
        engine = create_engine(db_url)
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))

        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        logger.info("Loaded %s rows into table '%s'", len(df), table_name)
    except LoadError:
        raise
    except OperationalError as exc:
        raise LoadError(_friendly_db_message(exc)) from exc
    except SQLAlchemyError as exc:
        raise LoadError(_friendly_db_message(exc)) from exc
    except Exception as exc:
        raise LoadError(_friendly_db_message(exc)) from exc
