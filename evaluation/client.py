import os

import requests


BASE_URL = os.getenv("NEXADESK_BASE_URL", "http://localhost:8001")


def send_chat(message: str, session_id: str | None = None) -> dict:
    """Send a chat request to NexaDesk and return its JSON response."""
    payload = {"message": message}

    if session_id:
        payload["session_id"] = session_id

    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()