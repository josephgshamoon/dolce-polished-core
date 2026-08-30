"""Delivery via Brevo's transactional API - never raw SMTP from the VPS.

Every send carries List-Unsubscribe headers (required by Gmail for bulk mail).
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import httpx

from . import config

API = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, html: str, unsub_url: str | None = None):
    if config.MAIL_TRANSPORT == "smtp":
        return _send_smtp(to_email, subject, html, unsub_url)
    return _send_brevo(to_email, subject, html, unsub_url)


def _send_smtp(to_email: str, subject: str, html: str, unsub_url: str | None = None):
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((config.FROM_NAME, config.FROM_EMAIL))
    msg["To"] = to_email
    msg["Subject"] = subject
    if unsub_url:
        msg["List-Unsubscribe"] = f"<{unsub_url}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
        server.starttls()
        if config.SMTP_PASS:  # Google SMTP relay authenticates by allowed IP; no login needed
            server.login(config.SMTP_USER, config.SMTP_PASS)
        server.send_message(msg)
    return {"transport": "smtp", "to": to_email}


def _send_brevo(to_email: str, subject: str, html: str, unsub_url: str | None = None):
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
    if r.status_code >= 400:
        raise RuntimeError(f"Brevo refused the send ({r.status_code}): {r.text[:500]}")
    return r.json()
