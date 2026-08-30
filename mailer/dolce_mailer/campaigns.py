"""Campaigns: draft -> approval email to the approver -> approved -> mass send.

CLI:
  python -m dolce_mailer.campaigns create --name X --subject S --html file.html
  python -m dolce_mailer.campaigns send-approved      (cron entry)
"""
import argparse
import re
import time
from pathlib import Path

from . import config, db, preflight, render, send


def create(name: str, subject: str, html_path: str):
    return create_from_html(name, subject, Path(html_path).read_text())


def create_from_html(name: str, subject: str, html: str,
                     heading: str = "", body_raw: str = "", audience: str = "all"):
    token = db.new_token()
    with db.connect() as con:
        con.execute(
            "INSERT INTO campaigns (name, subject, html, token, heading, body_raw, audience) "
            "VALUES (?,?,?,?,?,?,?)",
            (name, subject, html, token, heading, body_raw, audience))
        n = len(db.eligible_contacts(con, audience))
    _send_review(name, subject, html, token, n, audience)
    print(f"campaign '{name}' created; approval email sent to {config.APPROVER_EMAIL}")


def update_campaign(cid: int, name: str, subject: str, html: str,
                    heading: str, body_raw: str, audience: str = "all"):
    """Edit a pending campaign: new content, fresh token (old links die),
    back to pending, review emails re-sent."""
    token = db.new_token()
    with db.connect() as con:
        row = con.execute("SELECT status FROM campaigns WHERE id=?", (cid,)).fetchone()
        if not row or row["status"] != "pending":
            raise ValueError("only pending campaigns can be edited")
        con.execute(
            "UPDATE campaigns SET name=?, subject=?, html=?, token=?, heading=?, "
            "body_raw=?, audience=?, status='pending' WHERE id=?",
            (name, subject, html, token, heading, body_raw, audience, cid))
        n = len(db.eligible_contacts(con, audience))
    _send_review(name, subject, html, token, n, audience)


AUDIENCE_LABELS = {"all": "All clients", "dolce": "Dolce (clinic)",
                   "polished": "Polished (salon)", "core": "Core (studio)"}


def _send_review(name, subject, html, token, n, audience="all"):
    approve = f"{config.APP_BASE_URL}/approve/{token}"
    reject = f"{config.APP_BASE_URL}/reject/{token}"
    preview_contact = {"first_name": "Maya", "unsub_token": "preview"}
    preview_html = render.render(html, preview_contact)
    send.send_email(config.APPROVER_EMAIL, f"[TEST] {subject}", preview_html)
    m = re.search(r"<body[^>]*>(.*)</body>", preview_html, re.S)
    preview_inner = m.group(1) if m else preview_html
    notice = f"""
      <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
        <h2 style="font-family:Georgia,serif;font-weight:normal;color:#2b2b2b;">
          Approve campaign: {name}</h2>
        <p style="color:#4a4a4a;">Subject: <b>{subject}</b><br>
           Audience: <b>{AUDIENCE_LABELS.get(audience, audience)}</b><br>
           Recipients: <b>{n}</b> consented client(s).</p>
        <p style="color:#4a4a4a;">A test copy of the exact email was just sent to this
           inbox with the subject "[TEST] {subject}" - open it first and check how it looks.</p>
        <p style="margin:28px 0;">
          <a href="{approve}" style="background:#2e7d32;color:#fff;padding:14px 26px;
             text-decoration:none;border-radius:6px;">APPROVE &amp; SEND</a>
          &nbsp;&nbsp;
          <a href="{reject}" style="background:#c62828;color:#fff;padding:14px 26px;
             text-decoration:none;border-radius:6px;">REJECT</a>
        </p>
        <p style="color:#a99a9c;font-size:12px;">Nothing sends until you press Approve.
           Approved campaigns go out within 5 minutes, in gentle batches.</p>
        <p style="font-family:Georgia,serif;color:#2b2b2b;font-size:17px;
           margin:32px 0 10px;">Preview - exactly what clients receive:</p>
      </div>
      <div style="max-width:660px;margin:0 auto;border:1px solid #ead9dc;
           border-radius:10px;overflow:hidden;">{preview_inner}</div>"""
    send.send_email(config.APPROVER_EMAIL, f"[APPROVAL NEEDED] {name}", notice)


def send_approved():
    preflight.check()
    with db.connect() as con:
        rows = con.execute("SELECT * FROM campaigns WHERE status='approved'").fetchall()
        for camp in rows:
            kind = f"campaign:{camp['id']}"
            sent, remaining = 0, 0
            keys = camp.keys()
            camp_audience = camp["audience"] if "audience" in keys else "all"
            for c in db.eligible_contacts(con, camp_audience):
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
