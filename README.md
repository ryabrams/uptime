# Uptime Checker

A GitHub-hosted, Python-powered website uptime monitor.  
– Pings your site every 30 minutes  
– Confirms downtime after a 2 min retry  
– Sends email alerts on downtime & recovery  
– Logs every check (2-week rolling history)  
– Supports Gmail, SendGrid, Mailgun via GitHub Secrets  

---

## Features
- **Automated Pings**: HTTP GET every 30 minutes  
- **Downtime Confirmation**: 2 min retry before alert  
- **Recovery Alerts**: Notifies when site is back up  
- **Multiple Email Services**: Gmail SMTP, SendGrid API, Mailgun API  
- **Rolling Logs**: Keeps past 14 days of scan history  
- **Stateful**: Remembers last status across runs  

---

## Repository Structure
```
.
├── .github/
│   └── workflows/uptime-checker.yml
├── main.py
├── notifier.py
├── logger.py
├── state.json
├── logs/checks.log
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

1. **Clone repo**  
   ```bash
   git clone https://github.com/youruser/uptime-monitor.git
   cd uptime-monitor
   ```

2. **Create GitHub Secrets** (`Settings → Secrets → Actions`):
   - `TARGET_URL` – URL to monitor (e.g. `https://example.com`)
   - `RECIPIENT_EMAIL` – your alert email
   - `EMAIL_SERVICE` – one of `gmail`, `sendgrid`, `mailgun`
   - **Gmail**:  
     - `GMAIL_EMAIL` – Gmail address  
     - `GMAIL_PASSWORD` – App password  
   - **SendGrid**:  
     - `SENDGRID_API_KEY`  
   - **Mailgun**:  
     - `MAILGUN_API_KEY`  
     - `MAILGUN_DOMAIN`  

3. **Push first commit**  
   ```bash
   git add .
   git commit -m "Initial setup"
   git push
   ```

4. **Enable Actions** – go to **Actions** tab, approve the workflow.

---

## How It Works

1. **Ping**: `main.py` does an HTTP GET.  
2. **Pending Confirmation**: On first failure, logs “PENDING CONFIRMATION,” waits 2 minutes.  
3. **Confirm**: If still failing, logs “DOWN,” sends downtime alert, updates `state.json`.  
4. **Recovery**: On next success after “down,” logs “UP,” sends recovery alert, computes downtime.  
5. **Logs**: Appends events to `logs/checks.log`, then prunes entries older than 14 days.  
6. **Persistence**: `state.json` is committed back so the next run knows last status.

---

## Accessing Logs

Open `logs/checks.log` in the repo to view a history like:  
```
2025-05-29T14:00:00 UTC | https://example.com | DOWN | 502
```

---

## Troubleshooting

- **No emails?**  
  - Verify your API key / SMTP credentials.  
  - Check Actions logs for errors.
- **Workflow not running?**  
  - Ensure Actions is enabled.  
  - Validate cron syntax.
- **Commit errors?**  
  - Make sure `contents: write` permission is set.

---

## Contributing

1. Fork the repo  
2. Create feature branch (`git checkout -b feature/xyz`)  
3. Commit & push  
4. Open a Pull Request

---

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
