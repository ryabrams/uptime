import requests
import csv
import os
import sys
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def ensure_log_directory():
    os.makedirs(LOG_DIR, exist_ok=True)

def get_local_timestamp():
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def send_email_notification(subject, body):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(GMAIL_ADDRESS, EMAIL_TO, message)
        logging.info("Email notification sent.")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {e}")

def check_site():
    try:
        response = requests.get(SITE_URL, timeout=(5, 10))
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return False

def log_status(timestamp, status):
    ensure_log_directory()
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline='') as csvfile:
        fieldnames = ['timestamp', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'timestamp': timestamp, 'status': status})
    logging.info(f"Logged status: {status} at {timestamp}")

def trim_logs():
    cutoff = datetime.now(pytz.timezone(TIMEZONE)) - timedelta(days=30)
    if not os.path.exists(LOG_PATH):
        return

    with open(LOG_PATH, "r", newline='') as csvfile:
        rows = list(csv.DictReader(csvfile))

    filtered_rows = [
        row for row in rows
        if datetime.fromisoformat(row['timestamp']) >= cutoff
    ]

    with open(LOG_PATH, "w", newline='') as csvfile:
        fieldnames = ['timestamp', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)
    logging.info("Trimmed logs to retain the past 30 days.")

def main():
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logging.error("GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables must be set.")
        sys.exit(1)

    timestamp = get_local_timestamp()
    if check_site():
        log_status(timestamp, "UP")
    else:
        logging.warning("Initial check failed. Waiting 2 minutes before rechecking.")
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