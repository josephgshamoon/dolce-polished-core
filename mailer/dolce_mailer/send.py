"""Delivery via Brevo's transactional API - never raw SMTP from the VPS.

Every send carries List-Unsubscribe headers (required by Gmail for bulk mail).
"""
import httpx

from . import config

API = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, html: str, unsub_url: str | None = None):
    payload = {
        "sender": {"name": config.FROM_NAME, "email": config.FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
    }
    if unsub_url:
        payload["headers"] = {
            "List-Unsubscribe": f"<{unsub_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }
    r = httpx.post(API, json=payload, timeout=30,
                   headers={"api-key": config.BREVO_API_KEY,
                            "Content-Type": "application/json"})
    r.raise_for_status()
    return r.json()
