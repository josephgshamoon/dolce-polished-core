"""Cron entry: sync contacts from Wix, then welcome each new eligible contact ONCE."""
from pathlib import Path

from . import config, db, render, send, wix_sync

TEMPLATE = Path(__file__).parent / "templates" / "welcome.html"
SUBJECT = "Welcome to Dolce"


def run():
    wix_sync.run()
    html_template = TEMPLATE.read_text()
    sent = 0
    with db.connect() as con:
        for c in db.eligible_contacts(con):
            done = con.execute(
                "SELECT 1 FROM sends WHERE wix_id=? AND kind='welcome'", (c["wix_id"],)
            ).fetchone()
            if done:
                continue
            html = render.render(html_template, c)
            unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
            send.send_email(c["email"], SUBJECT, html, unsub)
            con.execute(
                "INSERT INTO sends (wix_id, kind) VALUES (?, 'welcome')", (c["wix_id"],)
            )
            sent += 1
    print(f"welcome_job: {sent} welcome email(s) sent")


if __name__ == "__main__":
    run()
