import os
import smtplib
import requests

def send_email(service, to, subject, body):
    service = service.lower()
    if service == 'gmail':
        _send_gmail(to, subject, body)
    elif service == 'sendgrid':
        _send_sendgrid(to, subject, body)
    elif service == 'mailgun':
        _send_mailgun(to, subject, body)
    else:
        raise ValueError(f"Unknown email service: {service}")

def _send_gmail(to, subject, body):
    user = os.getenv('GMAIL_EMAIL')
    pwd  = os.getenv('GMAIL_PASSWORD')
    if not user or not pwd:
        raise RuntimeError("GMAIL_EMAIL and GMAIL_PASSWORD must be set")
    msg = f"Subject: {subject}\n\n{body}"
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(user, pwd)
        s.sendmail(user, to, msg)

def _send_sendgrid(to, subject, body):
    key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('RECIPIENT_EMAIL')
    if not key or not from_email:
        raise RuntimeError("SENDGRID_API_KEY and RECIPIENT_EMAIL must be set")
    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        json={
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
    )
    resp.raise_for_status()

def _send_mailgun(to, subject, body):
    key    = os.getenv('MAILGUN_API_KEY')
    domain = os.getenv('MAILGUN_DOMAIN')
    if not key or not domain:
        raise RuntimeError("MAILGUN_API_KEY and MAILGUN_DOMAIN must be set")
    resp = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", key),
        data={
            "from":    f"Uptime Monitor <monitor@{domain}>",
            "to":      [to],
            "subject": subject,
            "text":    body
        }
    )
    resp.raise_for_status()
