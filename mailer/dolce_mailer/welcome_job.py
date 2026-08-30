"""Cron entry: sync contacts, then send each brand's welcome ONCE per contact
per brand. A client who later joins a second brand receives that brand's
welcome at that point. Once-only is enforced per contact id AND per email
address within each brand. Batches are throttled to MAX_SENDS_PER_RUN."""
import time
from pathlib import Path

from . import alerts, config, db, preflight, render, send, wix_sync

TPL_DIR = Path(__file__).parent / "templates"
BRANDS = ("dolce", "polished", "core")
SUBJECTS = {"dolce": "Welcome to Dolce", "polished": "Welcome to Polished",
            "core": "Welcome to Core"}


def run():
    preflight.check()
    wix_sync.run()
    sent, failures, capped = 0, [], False
    with db.connect() as con:
        for brand in BRANDS:
            tpl = TPL_DIR / f"welcome-{brand}.html"
            if capped or not tpl.exists():
                continue
            html_template = tpl.read_text()
            kind = f"welcome:{brand}"
            for c in db.eligible_contacts(con, brand):
                done = con.execute(
                    """SELECT 1 FROM sends s JOIN contacts c2 ON s.wix_id = c2.wix_id
                       WHERE s.kind = ? AND (s.wix_id = ? OR c2.email = ?)""",
                    (kind, c["wix_id"], c["email"])).fetchone()
                if done:
                    continue
                if sent >= config.MAX_SENDS_PER_RUN:
                    print(f"welcome_job: reached per-run cap "
                          f"({config.MAX_SENDS_PER_RUN}); the rest go out next runs")
                    capped = True
                    break
                html = render.render(html_template, c)
                unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
                try:
                    send.send_email(c["email"], SUBJECTS[brand], html, unsub)
                except Exception as e:
                    failures.append(f"{brand} / {c['email']}: {e}")
                    continue
                con.execute("INSERT INTO sends (wix_id, kind) VALUES (?,?)",
                            (c["wix_id"], kind))
                sent += 1
                time.sleep(config.SEND_DELAY_SECONDS)
    print(f"welcome_job: {sent} welcome email(s) sent")
    if failures:
        alerts.send_alert("[Dolce Mailer] welcome emails failed for some contacts",
                          "These welcome sends failed and will be retried next run:\n\n"
                          + "\n".join(failures))


if __name__ == "__main__":
    alerts.guard("welcome job", run)
