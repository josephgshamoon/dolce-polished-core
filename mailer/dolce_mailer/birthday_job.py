"""Daily cron: send the birthday template to eligible contacts on their birthday.

Sends at most once per contact per year (kind birthday:<year>). Requires a
birthday template at templates/birthday.html (approved once at setup, like the
welcome) and birthday data on the contact - flag: the Phoenix import needs a
birthday column for this to be useful.
"""
from datetime import date
from pathlib import Path

from . import config, db, preflight, render, send

TEMPLATE = Path(__file__).parent / "templates" / "birthday.html"
SUBJECT = "Happy birthday from Dolce"


def run():
    preflight.check()
    if not TEMPLATE.exists():
        print("birthday_job: no birthday template yet, skipping")
        return
    today = date.today()
    kind = f"birthday:{today.year}"
    html_template = TEMPLATE.read_text()
    sent = 0
    with db.connect() as con:
        for c in db.eligible_contacts(con):
            b = (c["birthday"] or "")[5:10]  # MM-DD from YYYY-MM-DD
            if b != today.strftime("%m-%d"):
                continue
            if con.execute("SELECT 1 FROM sends WHERE wix_id=? AND kind=?",
                           (c["wix_id"], kind)).fetchone():
                continue
            unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
            send.send_email(c["email"], SUBJECT, render.render(html_template, c), unsub)
            con.execute("INSERT INTO sends (wix_id, kind) VALUES (?,?)",
                        (c["wix_id"], kind))
            sent += 1
    print(f"birthday_job: {sent} sent")


if __name__ == "__main__":
    run()
