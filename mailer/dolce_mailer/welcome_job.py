"""Cron entry: sync contacts from Wix, then welcome each new eligible contact ONCE.

Once-only is enforced at two levels: per contact id AND per email address,
so a duplicate contact card for the same person can never trigger a second
welcome. Large batches are throttled to MAX_SENDS_PER_RUN per run."""
import time
from pathlib import Path

from . import alerts, config, db, preflight, render, send, wix_sync

TEMPLATE = Path(__file__).parent / "templates" / "welcome.html"
SUBJECT = "Welcome to Dolce"


def run():
    preflight.check()
    wix_sync.run()
    html_template = TEMPLATE.read_text()
    sent, failures = 0, []
    with db.connect() as con:
        for c in db.eligible_contacts(con):
            done = con.execute(
                """SELECT 1 FROM sends s JOIN contacts c2 ON s.wix_id = c2.wix_id
                   WHERE s.kind='welcome' AND (s.wix_id=? OR c2.email=?)""",
                (c["wix_id"], c["email"]),
            ).fetchone()
            if done:
                continue
            if sent >= config.MAX_SENDS_PER_RUN:
                print(f"welcome_job: reached per-run cap ({config.MAX_SENDS_PER_RUN}); "
                      "the rest go out on the next runs")
                break
            html = render.render(html_template, c)
            unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
            try:
                send.send_email(c["email"], SUBJECT, html, unsub)
            except Exception as e:
                failures.append(f"{c['email']}: {e}")
                continue
            con.execute(
                "INSERT INTO sends (wix_id, kind) VALUES (?, 'welcome')", (c["wix_id"],)
            )
            sent += 1
            time.sleep(config.SEND_DELAY_SECONDS)
    print(f"welcome_job: {sent} welcome email(s) sent")
    if failures:
        alerts.send_alert("[Dolce Mailer] welcome emails failed for some contacts",
                          "These welcome sends failed and will be retried next run:\n\n"
                          + "\n".join(failures))


if __name__ == "__main__":
    alerts.guard("welcome job", run)
