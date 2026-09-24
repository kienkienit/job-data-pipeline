"""Tests for the scheduler wiring (no long-running loop)."""

from unittest.mock import patch

import pytest

from jobs.scheduler import create_scheduler, scheduled_discord_job, scheduled_etl_job
from src.errors import LoadError


def test_create_interval_scheduler():
    scheduler = create_scheduler(schedule_type="interval", interval_minutes=30)
    job = scheduler.get_job("job_etl")
    assert job is not None
    assert job.trigger.interval.total_seconds() == 30 * 60
    discord = scheduler.get_job("job_discord_de")
    assert discord is not None


def test_create_cron_scheduler():
    scheduler = create_scheduler(schedule_type="cron", cron_hour=8, cron_minute=30)
    job = scheduler.get_job("job_etl")
    assert job is not None
    fields = {f.name: str(f) for f in job.trigger.fields}
    assert fields["hour"] == "8"
    assert fields["minute"] == "30"


def test_rejects_bad_schedule_type():
    with pytest.raises(ValueError, match="Unknown SCHEDULE_TYPE"):
        create_scheduler(schedule_type="weekly")


def test_rejects_bad_interval():
    with pytest.raises(ValueError, match="> 0"):
        create_scheduler(schedule_type="interval", interval_minutes=0)


def test_rejects_bad_cron_hour():
    with pytest.raises(ValueError, match="HOUR"):
        create_scheduler(schedule_type="cron", cron_hour=24, cron_minute=0)


def test_scheduled_etl_swallows_pipeline_error():
    with patch("jobs.scheduler.run_pipeline", side_effect=LoadError("db down")):
        scheduled_etl_job()


def test_scheduled_etl_calls_pipeline():
    with patch("jobs.scheduler.run_pipeline") as mock_run:
        scheduled_etl_job()
        mock_run.assert_called_once_with(skip_load=False)


def test_scheduled_discord_skips_without_webhook():
    with patch("jobs.scheduler.config.DISCORD_WEBHOOK_URL", ""):
        with patch("jobs.scheduler.notify_new_de_jobs") as mock_notify:
            scheduled_discord_job()
            mock_notify.assert_not_called()
