import requests
import smtplib
from email.mime.text import MIMEText
import os
import time
from datetime import datetime
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (INFO, WARNING, ERROR, DEBUG)
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output to console
        # logging.FileHandler("website_monitor.log"), # Optionally log to a file
    ],
)
# Constants
TIMEOUT_SECONDS = 10
RETRY_DELAY_SECONDS = 120
MAX_RETRIES = 2
SUCCESS_STATUS_CODES = range(200, 300)

def check_website_status(url):
    """
    Checks the HTTP status of a website with retry logic and improved error handling.

    Args:
        url (str): The URL of the website to check.

    Returns:
        int: The HTTP status code of the website, or None if the check fails after retries.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()  # Raise exception for bad status codes
            logging.info(f"Attempt {attempt + 1}: {url} is up (Status Code: {response.status_code})")
            return response.status_code
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Error checking {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                logging.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logging.error(f"Max retries reached.  Failed to check status for {url}")
                return None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

def send_email(subject, body):
    """
    Sends an email using Gmail's SMTP server with error handling.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    sender_email = os.environ.get("GMAIL_EMAIL")
    sender_password = os.environ.get("GMAIL_PASSWORD")
    receiver_email = os.environ.get("RECIPIENT_EMAIL")

    if not sender_email or not sender_password or not receiver_email:
        logging.error("Error: Email credentials or recipient email are not set in environment variables.")
        return

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def main():
    """
    Main function to check website status, handle downtime/recovery, and send emails.
    """
    url = os.environ.get("WEBSITE_URL")
    if not url:
        logging.error("Error: WEBSITE_URL is not set in environment variables.")
        return

    status_code = check_website_status(url)
    if status_code is None:
        logging.error(f"Failed to check status for {url} after retries. Exiting.")
        return

    if status_code in SUCCESS_STATUS_CODES:
        logging.info(f"{url} is up (Status Code: {status_code})")
        if os.environ.get("PREVIOUSLY_DOWN") == "true":
            send_email(
                subject=f"✅ {url} is back up!",
                body=f"Hooray! {url} is back online.\nRecovery Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )
            os.environ["PREVIOUSLY_DOWN"] = "false"
            logging.info("Recovery email sent.")
        else:
            logging.info("Website was already up.")
    else:
        logging.warning(f"{url} is down or returned an error (Status Code: {status_code})")
        send_email(
                subject=f"🚨 {url} is DOWN!",
                body=f"Oh no! {url} appears to be down.\nDowntime detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nStatus Code: {status_code}",
            )
        os.environ["PREVIOUSLY_DOWN"] = "true"
        logging.info("Downtime email sent.")

if __name__ == "__main__":
    main()
