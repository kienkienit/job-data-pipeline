from __future__ import annotations

import sys

from src import config
from src.errors import PipelineError, setup_logging
from src.notify.discord import notify_new_de_jobs

logger = setup_logging()


def main(*, dry_run: bool = False) -> None:
    if not dry_run and not config.DISCORD_WEBHOOK_URL:
        logger.error(
            "DISCORD_WEBHOOK_URL is not set.\n"
            "1) Discord → Channel → Edit channel → Integrations → Webhooks → New Webhook\n"
            "2) Copy URL into .env as DISCORD_WEBHOOK_URL=..."
        )
        sys.exit(1)
    try:
        n = notify_new_de_jobs(dry_run=dry_run)
        logger.info("Finished — %s notification(s)", n)
    except PipelineError as exc:
        logger.error("Aborted: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(dry_run=dry)
