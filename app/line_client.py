import os
import requests


def push_line_text(texts: str) -> None:
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    to = os.getenv("LINE_TO")
    if not token or not to:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN or LINE_TO is not set")

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    # Each request can send up to 5 messages; we keep it simple: 1 per request.
    payload = {"to": to, "messages": [{"type": "text", "text": texts}]}
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    try:
        r.raise_for_status()
    except Exception as ex:
            raise RuntimeError(f"LINE push failed: {r.status_code} {r.text}") from ex
