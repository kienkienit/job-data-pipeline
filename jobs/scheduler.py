from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler

from src import config
from src.errors import PipelineError, setup_logging
from src.pipeline import run_pipeline

logger = setup_logging()


def scheduled_job() -> None:
    logger.info("Scheduled pipeline run started")
    try:
        run_pipeline(skip_load=False)
        logger.info("Scheduled pipeline run finished OK")
    except PipelineError as exc:
        logger.error("Scheduled pipeline run failed: %s", exc)
    except Exception:
        logger.exception("Scheduled pipeline run failed unexpectedly")


def create_scheduler(
    schedule_type: str | None = None,
    *,
    interval_minutes: int | None = None,
    cron_hour: int | None = None,
    cron_minute: int | None = None,
) -> BlockingScheduler:
    mode = (schedule_type or config.SCHEDULE_TYPE).strip().lower()
    scheduler = BlockingScheduler()
    common = {"id": "job_etl", "max_instances": 1, "coalesce": True}

    if mode == "interval":
        minutes = (
            config.PIPELINE_INTERVAL_MINUTES
            if interval_minutes is None
            else interval_minutes
        )
        if minutes <= 0:
            raise ValueError("PIPELINE_INTERVAL_MINUTES must be > 0")
        scheduler.add_job(
            scheduled_job,
            trigger="interval",
            minutes=minutes,
            **common,
        )
    elif mode == "cron":
        hour = config.PIPELINE_CRON_HOUR if cron_hour is None else cron_hour
        minute = config.PIPELINE_CRON_MINUTE if cron_minute is None else cron_minute
        if not (0 <= hour <= 23):
            raise ValueError("PIPELINE_CRON_HOUR must be between 0 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("PIPELINE_CRON_MINUTE must be between 0 and 59")
        scheduler.add_job(
            scheduled_job,
            trigger="cron",
            hour=hour,
            minute=minute,
            **common,
        )
    else:
        raise ValueError(
            f"Unknown SCHEDULE_TYPE={mode!r}. Use 'interval' or 'cron'."
        )

    return scheduler


def _describe_schedule() -> str:
    if config.SCHEDULE_TYPE == "interval":
        return f"every {config.PIPELINE_INTERVAL_MINUTES} minute(s)"
    return f"daily at {config.PIPELINE_CRON_HOUR:02d}:{config.PIPELINE_CRON_MINUTE:02d}"


def main() -> None:
    scheduler = create_scheduler()
    logger.info(
        "Scheduler started — %s (%s) (Ctrl+C to stop)",
        config.SCHEDULE_TYPE,
        _describe_schedule(),
    )

    if config.SCHEDULE_TYPE == "interval":
        scheduled_job()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
