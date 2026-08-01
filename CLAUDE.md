# CLAUDE.md

## Project overview

Simple website uptime monitor. A single Python script (`check_uptime.py`) runs every 30 minutes via GitHub Actions, checks a URL, logs the result to `logs/log.csv`, and sends alerts (email and/or Telegram) when the site is down.

## Architecture

- `check_uptime.py` — entire application; no modules, no classes, just functions
  - `validate_env()` — requires `SITE_URL` plus at least one fully configured notification channel; returns which channels are enabled
  - `check_site()` — single HTTP GET; 2xx = up, anything else (or a connection error/timeout) = down; also measures response time
  - `send_email()` / `send_telegram()` — one function per channel; failures are logged, never raised (a broken channel must not crash the run)
  - `log_check()` — appends one row to `logs/log.csv`, writing the header if the file is new
- `.github/workflows/uptime.yml` — scheduled workflow (`*/30 * * * *`) that runs the check, then commits the updated `logs/log.csv` back to the repo. Runs from the **default branch (`main`)** and needs `permissions: contents: write` to push the log commit.
- `logs/log.csv` — append-only check history (`timestamp,url,status,detail,response_time_ms`)
- `requirements.txt` — sole dependency is `requests` (pinned)

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

- `SITE_URL` (required) — URL to check; must start with `http://` or `https://`
- Email channel: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `EMAIL_TO`
- Telegram channel: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

Each channel is all-or-nothing: set **every** var in a group to enable it, or none to skip it. A partially configured channel exits with an error. At least one full channel must be configured or the script exits with an error.

## Git workflow

### Branches

- **`dev`** — the working/integration branch. All development happens here.
- **`main`** — the production/default branch. GitHub Actions runs the scheduled workflow from `main`, and the CI bot pushes `log: uptime check ...` commits to `logs/log.csv` on `main` every 30 minutes. As a result, **`main` continuously gains log commits that `dev` does not have.**

### Rules

1. **Always work on `dev`.** Create and commit every change on `dev`. Never commit source changes directly to `main`.
2. **Always ask before pushing to `main`.** Never push or merge to `main` without explicit user approval — ask first, every time.
3. **Always keep `main` and `dev` in sync.** They diverge by design (CI appends logs to `main`; features land on `dev`), so "in sync" means **neither branch is missing the other's commits for any tracked file except `logs/log.csv`**, whose CI appends on `main` are expected to run ahead between syncs.

### Sync procedure (after an approved merge to `main`)

Once the user approves releasing `dev` to `main`:

```bash
# 1. Merge dev into main and push
git checkout main && git pull origin main
# WARNING: this is a MERGE COMMIT, not a fast-forward (CI adds log: commits to
# main that dev lacks). NEVER add --ff-only here — it aborts. See Gotchas below.
git merge dev --no-edit
git push origin main            # only after user approval
# Then confirm the ref actually moved: git log -1 --oneline origin/main

# 2. Merge main back into dev (pulls the CI log commits + the merge) and push
git checkout dev
git merge main --no-edit
git push origin dev

# 3. Verify they are in sync (source identical; only logs/log.csv may differ)
git diff origin/main origin/dev -- . ':!logs/log.csv'   # expect no output
```

Before starting new work, first sync `dev` with the latest `main`
(`git checkout dev && git merge origin/main`) so you build on current logs and released code.

### Gotchas (learned the hard way)

- **The `dev → main` merge is normally a merge commit, not a fast-forward.**
  Because CI keeps appending `log:` commits to `main`, `main` and `dev` each
  get ahead of the other between syncs (main on logs, dev on features). Neither
  is an ancestor of the other, so a plain `git merge dev` must create a merge
  commit. **Do not force `--ff-only` on step 1** — it will abort with
  "Not possible to fast-forward". (Step 1's merge only fast-forwards if step 2
  already ran, making `dev` a descendant of `main`.)
- **Verify the ref actually moved; don't trust command output.** After
  `git push origin main`, confirm with `git log -1 --oneline origin/main` (or the
  step-3 diff). Piping a git command through `head`/`tail` masks its exit code,
  so a failed merge can look like it succeeded — always check the end state.

## Key conventions

- Python 3.12, no type annotations, no tests, no linter config
- Single-file script — keep it that way; avoid splitting into modules
- `logs/log.csv` is committed by the CI bot; don't gitignore it
- Notifications only fire on failure (down), not on recovery
