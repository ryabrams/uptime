# CLAUDE.md

## Project overview

Simple website uptime monitor. A single Python script (`check_uptime.py`) runs every 30 minutes via GitHub Actions, checks a URL, logs the result to `logs/log.csv`, and sends alerts (email and/or Telegram) when the site is down.

## Architecture

- `check_uptime.py` — entire application; no modules, no classes, just functions
- `.github/workflows/uptime.yml` — scheduled workflow; commits the updated log CSV back to the repo
- `logs/log.csv` — append-only check history (timestamp, url, status, detail, response_time_ms)
- `requirements.txt` — sole dependency is `requests`

## Running locally

```bash
pip install -r requirements.txt

# Minimum viable run (needs at least one notification channel):
SITE_URL=https://example.com \
TELEGRAM_BOT_TOKEN=... \
TELEGRAM_CHAT_ID=... \
python check_uptime.py
```

## Environment variables

All configuration is via env vars (GitHub Secrets in CI):

- `SITE_URL` (required) — URL to check
- Email channel: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`
- Telegram channel: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

At least one full channel must be configured or the script exits with an error.

## Key conventions

- Python 3.12, no type annotations, no tests, no linter config
- Single-file script — keep it that way; avoid splitting into modules
- `logs/log.csv` is committed by the CI bot; don't gitignore it
- Notifications only fire on failure (down), not on recovery
