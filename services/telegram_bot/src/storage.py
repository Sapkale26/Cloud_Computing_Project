import json
from pathlib import Path

from config import BASE_DIR

ALERTS_FILE = BASE_DIR / "sent_alerts.json"


def load_sent_alert_ids() -> set:
    if not ALERTS_FILE.exists():
        return set()

    try:
        with open(ALERTS_FILE, "r") as f:
            data = json.load(f)
        return set(data)
    except (json.JSONDecodeError, OSError):
        return set()


def save_sent_alert_ids(alert_ids: set) -> None:
    try:
        with open(ALERTS_FILE, "w") as f:
            json.dump(list(alert_ids), f)
    except OSError as e:
        print(f"Failed to persist sent_alert_ids: {e}")