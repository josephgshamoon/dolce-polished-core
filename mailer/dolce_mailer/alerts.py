"""Failure alerting: anything that breaks emails ALERT_EMAIL.

Same-subject alerts are suppressed for 6 hours so a repeating cron failure
produces one email, not one every run. Alert delivery is best-effort - if
the mail transport itself is down, the failure still lands in the log.
"""
import html
import traceback

from . import config, db, send


def send_alert(subject: str, body: str) -> bool:
    try:
        with db.connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS alerts "
                        "(subject TEXT PRIMARY KEY, last_sent TEXT)")
            recent = con.execute(
                "SELECT 1 FROM alerts WHERE subject=? "
                "AND last_sent > datetime('now','-6 hours')", (subject,)).fetchone()
            if recent:
                print(f"alert suppressed (sent within 6h): {subject}")
                return False
            con.execute("INSERT OR REPLACE INTO alerts VALUES (?, datetime('now'))",
                        (subject,))
        send.send_email(
            config.ALERT_EMAIL, subject,
            f"<div style='font-family:Arial;padding:16px;'>"
            f"<h3 style='color:#c62828;'>Dolce Mailer alert</h3>"
            f"<pre style='background:#f6f2ee;padding:14px;border-radius:6px;"
            f"white-space:pre-wrap;font-size:13px;'>{html.escape(body)}</pre>"
            f"<p style='color:#888;font-size:12px;'>Server: mailer.dolceclinic.com "
            f"(145.223.88.35). Repeats of this alert are muted for 6 hours.</p></div>")
        print(f"alert sent to {config.ALERT_EMAIL}: {subject}")
        return True
    except Exception:
        print("ALERT DELIVERY FAILED:\n" + traceback.format_exc())
        return False


def guard(name: str, fn):
    """Run a job; on any failure, alert and re-raise."""
    try:
        fn()
    except BaseException:
        send_alert(f"[Dolce Mailer] {name} FAILED",
                   f"{name} failed:\n\n{traceback.format_exc()}")
        raise
