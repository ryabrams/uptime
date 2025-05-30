import os
from datetime import datetime, timedelta

def log_and_prune(logfile, url, timestamp, status, info):
    entry = f"{timestamp} UTC | {url} | {status} | {info}\n"
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    # append new entry
    with open(logfile, 'a') as f:
        f.write(entry)
    # prune entries older than 14 days
    cutoff = datetime.utcnow() - timedelta(days=14)
    kept = []
    with open(logfile) as f:
        for line in f:
            ts_str = line.split('|')[0].strip().replace(" UTC", "")
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                continue
            if ts >= cutoff:
                kept.append(line)
    with open(logfile, 'w') as f:
        f.writelines(kept)
