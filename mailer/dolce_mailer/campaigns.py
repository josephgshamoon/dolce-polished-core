"""Campaigns: draft -> approval email to the approver -> approved -> mass send.

CLI:
  python -m dolce_mailer.campaigns create --name X --subject S --html file.html
  python -m dolce_mailer.campaigns send-approved      (cron entry)
"""
import argparse
import time
from pathlib import Path

from . import config, db, preflight, render, send


def create(name: str, subject: str, html_path: str):
    html = Path(html_path).read_text()
    token = db.new_token()
    with db.connect() as con:
        cur = con.execute(
            "INSERT INTO campaigns (name, subject, html, token) VALUES (?,?,?,?)",
            (name, subject, html, token),
        )
        campaign_id = cur.lastrowid
        n = len(db.eligible_contacts(con))
    approve = f"{config.APP_BASE_URL}/approve/{token}"
    reject = f"{config.APP_BASE_URL}/reject/{token}"
    notice = f"""
      <div style="font-family:Arial,sans-serif; padding:16px;">
        <h2>Campaign approval needed: {name}</h2>
        <p>Subject: <b>{subject}</b> - would send to <b>{n}</b> consented contacts.</p>
        <p>
          <a href="{approve}" style="background:#2e7d32;color:#fff;padding:12px 24px;
             text-decoration:none;border-radius:4px;">APPROVE &amp; SEND</a>
          &nbsp;&nbsp;
          <a href="{reject}" style="background:#c62828;color:#fff;padding:12px 24px;
             text-decoration:none;border-radius:4px;">REJECT</a>
        </p>
        <p>Preview below (placeholders shown unmerged):</p>
        <hr>{html}
      </div>"""
    send.send_email(config.APPROVER_EMAIL, f"[APPROVAL NEEDED] {name}", notice)
    print(f"campaign {campaign_id} created; approval email sent to {config.APPROVER_EMAIL}")


def send_approved():
    preflight.check()
    with db.connect() as con:
        rows = con.execute("SELECT * FROM campaigns WHERE status='approved'").fetchall()
        for camp in rows:
            kind = f"campaign:{camp['id']}"
            sent, remaining = 0, 0
            for c in db.eligible_contacts(con):
                if con.execute("SELECT 1 FROM sends WHERE wix_id=? AND kind=?",
                               (c["wix_id"], kind)).fetchone():
                    continue
                if sent >= config.MAX_SENDS_PER_RUN:
                    remaining += 1
                    continue
                unsub = f"{config.APP_BASE_URL}/unsubscribe/{c['unsub_token']}"
                send.send_email(c["email"], camp["subject"],
                                render.render(camp["html"], c), unsub)
                con.execute("INSERT INTO sends (wix_id, kind) VALUES (?,?)",
                            (c["wix_id"], kind))
                sent += 1
                time.sleep(config.SEND_DELAY_SECONDS)
            if remaining:
                print(f"campaign {camp['id']} ({camp['name']}): {sent} sent this run, "
                      f"{remaining} remaining - continues next run")
            else:
                con.execute(
                    "UPDATE campaigns SET status='sent', sent_at=CURRENT_TIMESTAMP WHERE id=?",
                    (camp["id"],))
                print(f"campaign {camp['id']} ({camp['name']}): complete, {sent} sent this run")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("--name", required=True)
    c.add_argument("--subject", required=True)
    c.add_argument("--html", required=True)
    sub.add_parser("send-approved")
    args = p.parse_args()
    if args.cmd == "create":
        create(args.name, args.subject, args.html)
    else:
        send_approved()
