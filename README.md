# Website Uptime Checker

A simple uptime checker for your website ([https://www.ryanabrams.com](https://www.ryanabrams.com)). Uses GitHub Actions to periodically verify your website is running and sends email notifications via Gmail when downtime is detected.

## Features
- Checks website uptime every 30 minutes.
- Confirms downtime by re-checking after 2 minutes.
- Logs uptime status into a CSV file, retaining logs for the past 30 days.
- Sends Gmail notifications upon confirmed downtime.

---

## Setup Instructions

### 1. Clone repository and commit provided files
- Copy provided files into your repository.
- Push to GitHub.

### 2. Configure GitHub Secrets
Set the following GitHub repository secrets:
- `GMAIL_ADDRESS`: Your Gmail address used for sending notifications.
- `GMAIL_APP_PASSWORD`: Generate a Gmail [App Password](https://support.google.com/accounts/answer/185833) for SMTP use.

### 3. Activate GitHub Actions
- Actions will automatically run every 30 minutes.
- To manually trigger an uptime check, use the "Run workflow" button in GitHub Actions.

---

## Usage and Monitoring

### Viewing Logs
- Check logs in the repository at `logs/uptime_log.csv`.

### Email Notifications
- Receive email notifications at your configured Gmail address if downtime is detected.

---

## Dependencies
- Python packages: `requests`, `pytz`

---

## Timezone
- Timestamps reflect Israel local time (Asia/Jerusalem).