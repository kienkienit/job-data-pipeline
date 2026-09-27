# Free cloud run (GitHub Actions + Neon)

Run crawl + Discord **without keeping your Mac on**.

## 1. Create free Postgres (Neon)

1. Sign up at https://neon.tech (free)
2. Create a project → copy the connection string
3. Change scheme to SQLAlchemy form and keep SSL:

```text
postgresql+psycopg2://USER:PASSWORD@HOST/DB?sslmode=require
```

(Replace `postgresql://` with `postgresql+psycopg2://` if Neon gives the plain form.)

## 2. Add GitHub secrets

Repo → **Settings → Secrets and variables → Actions → Secrets**:

| Secret | Value |
|--------|--------|
| `DB_URL` | Neon URL above |
| `DISCORD_WEBHOOK_URL` | Your Discord webhook |

Optional **Variables** (same page → Variables):

| Variable | Default in workflow | Meaning |
|----------|---------------------|---------|
| `CRAWL_MAX_PAGES` | `20` | Pages per crawl (~1000 newest jobs) |
| `CRAWL_PAGE_SIZE` | `50` | Jobs per page |
| `DISCORD_MAX_MESSAGES` | `20` | Max DE messages per run |

## 3. Commit + push

Push `main` (includes `.github/workflows/daily.yml`). Do **not** commit `.env`.

## 4. Test

**Actions → ETL + Discord → Run workflow**

Cron: every 2 hours UTC (`0 */2 * * *`), at 00:00, 02:00, 04:00, and so on. GitHub may start a few minutes late.

## Notes

- Actions uses `DISCORD_STATE_BACKEND=db` so notified keys survive between runs (table `discord_notified`).
- Local Mac can keep `DISCORD_STATE_BACKEND=file` (default) and local Postgres.
- Private repos: free Actions minutes are limited. Twelve short runs a day usually stay inside the monthly quota.
