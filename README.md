# Uptime Checker

A simple website uptime monitor that runs on GitHub Actions every 30 minutes. When your site goes down, it notifies you via **email**, **Telegram**, or both — configure whichever channels you want.

## How It Works

1. GitHub Actions runs `check_uptime.py` on a schedule (`*/30 * * * *`).
2. The script makes an HTTP GET request to `SITE_URL`.
3. A non-2xx status code or connection failure is treated as **down**.
4. Every check (up or down) is logged to `logs/log.csv` with timestamp, status, detail, and response time.
5. When down: sends an alert on every configured channel (email and/or Telegram).
6. When up: prints a success message and does nothing else.

## Setup

### 1. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**.

`SITE_URL` is always required. Beyond that, you choose your notification
channels: configure the **email** group, the **Telegram** group, or both. You
must enable **at least one** channel, and each channel must be configured
**completely** — if you set some of a channel's variables but not all, the run
fails with an error listing what's missing.

**Always required**

| Secret | Description |
|---|---|
| `SITE_URL` | Full URL to monitor, e.g. `https://example.com` |

**Email channel** (set all six to enable, or omit all to skip)

| Secret | Description |
|---|---|
| `SMTP_HOST` | SMTP server, e.g. `smtp.gmail.com` |
| `SMTP_PORT` | `587` for STARTTLS, `465` for SSL |
| `SMTP_USERNAME` | SMTP login username |
| `SMTP_PASSWORD` | SMTP password or App Password |
| `EMAIL_FROM` | Sender address shown in the From header |
| `EMAIL_TO` | Recipient address(es), comma-separated for multiple |

**Telegram channel** (set both to enable, or omit both to skip)

| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Chat ID to send alerts to (see below) |

### 2. Test Manually

Once secrets are configured, trigger the workflow manually to verify everything works:

**Actions tab → Uptime Check → Run workflow**

Check the run logs to confirm each notification channel succeeded.

### 3. Let It Run

The workflow runs automatically every 30 minutes. No further action needed.

---

## Gmail Setup

Google requires an **App Password** for SMTP — your regular account password won't work.

1. Enable 2-Step Verification on your Google account.
2. Go to **Google Account → Security → App Passwords**.
3. Generate a password for "Mail" and use it as `SMTP_PASSWORD`.
4. Set `SMTP_HOST` = `smtp.gmail.com` and `SMTP_PORT` = `587`.

## Telegram Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot` to create a bot.
2. Copy the token it gives you → use as `TELEGRAM_BOT_TOKEN`.
3. Send any message to your new bot, then open this URL in a browser (replace `<TOKEN>` with your token):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. Find `"chat": {"id": ...}` in the response → use that number as `TELEGRAM_CHAT_ID`.

For a group chat or channel, add the bot as an admin and use the group/channel ID instead.

---

## Troubleshooting

- **Check the Actions run log** — each channel (`[email]`, `[telegram]`) logs success or the exact error independently.
- **Missing secrets** — the script will list all missing secrets and exit with a non-zero code, which marks the workflow run as failed.
- **Wrong SMTP port** — port `587` uses STARTTLS; port `465` uses implicit SSL. Make sure your provider matches.
- **Telegram `chat not found`** — you must send at least one message to the bot before it can message you back.
