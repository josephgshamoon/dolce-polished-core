"""Automatic review request - Dolce only for now.

Sends each consented Dolce client ONE review-request email, 3 days after
their Dolce welcome was sent.
Once-only is enforced per contact id AND per email address, like welcomes.
Runs piggybacked on the welcome job's cron entry - no extra crontab line.
Brands are added here only once their Google Business Profile is claimed
(config.REVIEW_LINKS).
"""
import time
from datetime import datetime, timedelta

from . import alerts, config, db, preflight, render, send

DAYS_AFTER_WELCOME = 3


def run():
    preflight.check()
    sent, failures = 0, []
    cutoff = (datetime.utcnow() - timedelta(days=DAYS_AFTER_WELCOME)
              ).strftime("%Y-%m-%d %H:%M:%S")
    with db.connect() as con:
        for brand in config.REVIEW_LINKS:
            kind = f"review:{brand}"
            subject_t, html_template = render.render_auto(kind)
            for c in db.eligible_contacts(con, brand):
                welcomed = con.execute(
                    "SELECT 1 FROM sends WHERE wix_id=? AND kind=? AND sent_at<=?",
                    (c["wix_id"], f"welcome:{brand}", cutoff)).fetchone()
                if not welcomed:
                    continue
                done = con.execute(
                    """SELECT 1 FROM sends s JOIN contacts c2 ON s.wix_id = c2.wix_id
                       WHERE s.kind = ? AND (s.wix_id = ? OR c2.email = ?)""",
                    (kind, c["wix_id"], c["email"])).fetchone()
                if done:
                    continue
                if sent >= config.MAX_SENDS_PER_RUN:
                    print(f"review_job: reached per-run cap "
                          f"({config.MAX_SENDS_PER_RUN}); the rest go out next runs")
                    break
                html = render.render(html_template, c)
                unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
                try:
                    send.send_email(c["email"],
                                    render.render(subject_t, c, plain=True),
                                    html, unsub)
                except Exception as e:
                    failures.append(f"{brand} / {c['email']}: {e}")
                    continue
                con.execute("INSERT INTO sends (wix_id, kind) VALUES (?,?)",
                            (c["wix_id"], kind))
                sent += 1
                time.sleep(config.SEND_DELAY_SECONDS)
    print(f"review_job: {sent} review request(s) sent")
    if failures:
        alerts.send_alert("[Dolce Mailer] review requests failed for some contacts",
                          "These review-request sends failed and will be retried "
                          "next run:\n\n" + "\n".join(failures))


if __name__ == "__main__":
    alerts.guard("review job", run)
