import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText

import requests

SMTP_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
]

TELEGRAM_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]


def _channel_state(name, variables):
    """Return whether a notification channel is fully configured.

    A channel counts as enabled only when all of its variables are set. If
    some — but not all — are set, that's a misconfiguration and we exit.
    """
    present = [v for v in variables if os.environ.get(v)]
    if not present:
        return False
    if len(present) != len(variables):
        missing = [v for v in variables if not os.environ.get(v)]
        print(
            f"ERROR: {name} is partially configured. Missing: {', '.join(missing)}"
        )
        sys.exit(1)
    return True


def validate_env():
    if not os.environ.get("SITE_URL"):
        print("ERROR: Missing required environment variable: SITE_URL")
        sys.exit(1)
    url = os.environ["SITE_URL"]
    if not url.startswith("http://") and not url.startswith("https://"):
        print(f"ERROR: SITE_URL must start with http:// or https:// (got: {url!r})")
        sys.exit(1)

    email_enabled = _channel_state("SMTP/email", SMTP_VARS)
    telegram_enabled = _channel_state("Telegram", TELEGRAM_VARS)

    if not email_enabled and not telegram_enabled:
        print(
            "ERROR: No notification channel configured. Set the SMTP/email "
            f"variables ({', '.join(SMTP_VARS)}) and/or the Telegram variables "
            f"({', '.join(TELEGRAM_VARS)})."
        )
        sys.exit(1)

    return email_enabled, telegram_enabled


def check_site(url):
    try:
        resp = requests.get(url, timeout=15, allow_redirects=True)
        if 200 <= resp.status_code < 300:
            return True, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        return False, "Connection timed out after 15s"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def send_email(subject, body):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]
    from_addr = os.environ["EMAIL_FROM"]
    to_addrs = [a.strip() for a in os.environ["EMAIL_TO"].split(",")]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)

    try:
        ctx = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ctx) as smtp:
                smtp.login(username, password)
                smtp.sendmail(from_addr, to_addrs, msg.as_string())
        else:
            with smtplib.SMTP(host, port) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ctx)
                smtp.login(username, password)
                smtp.sendmail(from_addr, to_addrs, msg.as_string())
        print(f"  [email] Sent to {to_addrs}")
    except Exception as e:
        print(f"  [email] FAILED: {e}")


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=15,
        )
        if resp.status_code == 200:
            print("  [telegram] Sent")
        else:
            print(f"  [telegram] FAILED: HTTP {resp.status_code} — {resp.text}")
    except Exception as e:
        print(f"  [telegram] FAILED: {e}")


def main():
    email_enabled, telegram_enabled = validate_env()

    site_url = os.environ["SITE_URL"]
    is_up, detail = check_site(site_url)

    if not is_up:
        print(f"DOWN: {site_url} — {detail}")
        if email_enabled:
            send_email(
                subject=f"[ALERT] {site_url} is DOWN",
                body=f"Your site appears to be down.\n\nURL: {site_url}\nDetail: {detail}",
            )
        if telegram_enabled:
            send_telegram(
                f"<b>ALERT</b>: <a href='{site_url}'>{site_url}</a> is <b>DOWN</b>\n"
                f"Detail: {detail}"
            )
    else:
        print(f"UP: {site_url} — {detail}")


if __name__ == "__main__":
    main()
