"""Daily cron: send the birthday template to eligible contacts on their birthday.

Sends at most once per contact per year (kind birthday:<year>). Requires a
birthday template at templates/birthday.html (approved once at setup, like the
welcome) and birthday data on the contact - flag: the Phoenix import needs a
birthday column for this to be useful.
"""
from datetime import date

from . import alerts, config, db, preflight, render, send


def run():
    preflight.check()
    today = date.today()
    kind = f"birthday:{today.year}"
    # one brand-styled email per client; a client in several brands gets the
    # first matching design (dolce > polished > core), never more than one
    templates = {b: render.render_auto(f"birthday:{b}") for b in db.BRAND_KEYS}
    sent = 0
    with db.connect() as con:
        for c in db.eligible_contacts(con):
            b = (c["birthday"] or "")[5:10]  # MM-DD from YYYY-MM-DD
            if b != today.strftime("%m-%d"):
                continue
            if con.execute("SELECT 1 FROM sends WHERE wix_id=? AND kind=?",
                           (c["wix_id"], kind)).fetchone():
                continue
            brand = next(bk for bk in db.BRAND_KEYS
                         if bk in (c["labels"] or ""))
            subject_t, html_template = templates[brand]
            unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
            send.send_email(c["email"], render.render(subject_t, c, plain=True),
                            render.render(html_template, c), unsub)
            con.execute("INSERT INTO sends (wix_id, kind) VALUES (?,?)",
                        (c["wix_id"], kind))
            sent += 1
    print(f"birthday_job: {sent} sent")


if __name__ == "__main__":
    alerts.guard("birthday job", run)
