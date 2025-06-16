import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def send_pushcut_notification(message: str, deep_link: str):
    """
    Sends a Pushcut notification using the Webhook URL.
    The webhook must already be set up in the Pushcut app.
    """
    url = os.getenv("PUSHCUT_WEBHOOK_URL")
    if not url:
        print("[Pushcut] ERROR: Missing PUSHCUT_WEBHOOK_URL in environment.")
        return

    payload = {
        "title": message,
        "text": "Tap to view in cart.",
        "defaultAction": {
            "url": deep_link
        }
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[Pushcut] ✅ Notification sent: {message}")
        else:
            print(f"[Pushcut] ❌ ERROR {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Pushcut] ❌ Exception: {e}")
