from webhook import send_pushcut_alert

send_pushcut_alert(
    title="Test Alert",
    body="If you're seeing this, the API key and notification are working.",
    url="https://www.target.com/co-cart"
)
