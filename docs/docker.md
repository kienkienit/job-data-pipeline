# Run scheduler with Docker

Keeps crawl + Discord running while your Mac is awake (sleep still stops the container).

## 1. Prepare `.env`

```env
EXTRACT_SOURCE=crawl
SCHEDULE_TYPE=interval
PIPELINE_INTERVAL_MINUTES=120
DISCORD_INTERVAL_HOURS=2
DISCORD_WEBHOOK_URL=...
DB_URL=postgresql+psycopg2://macbook@host.docker.internal:5432/jobs_db
```

Use `host.docker.internal` so the container can reach Postgres on your Mac.

## 2. Start

```bash
docker compose up -d --build
```

## 3. Logs / stop

```bash
docker compose logs -f scheduler
docker compose down
```

On start, the scheduler runs ETL + Discord once, then every 2 hours (with the `.env` above).
