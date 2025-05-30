import os
import time
import json
from datetime import datetime

from dotenv import load_dotenv
import requests

from notifier import send_email
from logger import log_and_prune

load_dotenv()  # support local .env during development

STATE_FILE = 'state.json'
LOG_FILE = 'logs/checks.log'
TARGET = os.getenv('TARGET_URL')
RECIPIENT = os.getenv('RECIPIENT_EMAIL')
SERVICE = os.getenv('EMAIL_SERVICE', 'gmail').lower()

def load_state():
    if not os.path.isfile(STATE_FILE):
        return {"status": "unknown", "last_change": None}
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def ping(url):
    try:
        resp = requests.get(url, timeout=10)
        return resp.status_code < 300, resp.status_code
    except Exception as e:
        return False, str(e)

def main():
    if not TARGET or not RECIPIENT:
        raise RuntimeError("TARGET_URL and RECIPIENT_EMAIL must be set")

    state = load_state()
    now = datetime.utcnow().isoformat()
    up, code = ping(TARGET)

    if not up:
        # First failure: pending confirmation
        log_and_prune(LOG_FILE, TARGET, now, "PENDING CONFIRMATION", code)
        time.sleep(120)
        up2, code2 = ping(TARGET)
        if not up2:
            # Confirmed down
            if state['status'] != 'down':
                send_email(
                    service=SERVICE,
                    to=RECIPIENT,
                    subject=f"[DOWN] {TARGET}",
                    body=f"Site {TARGET} is DOWN at {now} UTC. Error: {code2}"
                )
                state['status'] = 'down'
                state['last_change'] = now
            log_and_prune(LOG_FILE, TARGET, now, "DOWN", code2)

    else:
        # Site is up
        if state.get('status') == 'down':
            down_since = state.get('last_change')
            start = datetime.fromisoformat(down_since)
            duration = datetime.utcnow() - start
            send_email(
                service=SERVICE,
                to=RECIPIENT,
                subject=f"[RECOVERED] {TARGET}",
                body=(
                    f"Site {TARGET} recovered at {now} UTC.\n"
                    f"Downtime duration: {duration}."
                )
            )
            state['status'] = 'up'
            state['last_change'] = now

        log_and_prune(LOG_FILE, TARGET, now, "UP", code)

    save_state(state)

if __name__ == "__main__":
    main()
