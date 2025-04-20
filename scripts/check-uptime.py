import requests
import csv
import os
from datetime import datetime, timedelta
import smtplib
import time
import pytz

# Constants
SITE_URL = "https://www.ryanabrams.com"
LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "uptime_log.csv")
TIMEZONE = "Asia/Jerusalem"

# Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO = GMAIL_ADDRESS  # Sending email to self; adjust if needed

def ensure_log_directory():
    os.makedirs(LOG_DIR, exist_ok=True)

def get_local_timestamp():
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def send_email_notification(subject, body):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(GMAIL_ADDRESS, EMAIL_TO, message)

def check_site():
    try:
        response = requests.get(SITE_URL, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def log_status(timestamp, status):
    ensure_log_directory()  # Ensures logs directory exists
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp", "status"])
        writer.writerow([timestamp, status])

def trim_logs():
    cutoff = datetime.now(pytz.timezone(TIMEZONE)) - timedelta(days=30)
    if not os.path.exists(LOG_PATH):
        return

    with open(LOG_PATH, "r", newline='') as csvfile:
        rows = list(csv.reader(csvfile))

    header, rows = rows[0], rows[1:]
    filtered_rows = [
        row for row in rows
        if datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone(TIMEZONE)) >= cutoff
    ]

    with open(LOG_PATH, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(filtered_rows)

def main():
    timestamp = get_local_timestamp()
    if check_site():
        log_status(timestamp, "UP")
    else:
        # Wait 2 minutes and recheck
        time.sleep(120)
        if not check_site():
            log_status(timestamp, "DOWN")
            subject = "Website Downtime Alert"
            body = f"{SITE_URL} is DOWN as of {timestamp}."
            send_email_notification(subject, body)
        else:
            log_status(timestamp, "UP (Recovered)")

    trim_logs()

if __name__ == "__main__":
    main()