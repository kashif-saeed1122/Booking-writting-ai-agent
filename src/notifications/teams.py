import os

import requests


TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")


def send_teams_message(text: str) -> None:
    """
    Send a simple text message to MS Teams via incoming webhook.
    If TEAMS_WEBHOOK_URL is not set, this is a no-op.
    """
    if not TEAMS_WEBHOOK_URL:
        return

    try:
        requests.post(TEAMS_WEBHOOK_URL, json={"text": text}, timeout=10)
    except Exception:
        # Fail silently for now – keep the core flow running
        pass

