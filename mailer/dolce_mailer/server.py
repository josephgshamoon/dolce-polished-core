"""Web endpoints: campaign approve/reject, one-click unsubscribe, Brevo webhook."""
import html as html_mod
import secrets as pysecrets
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from . import campaigns, config, db

basic = HTTPBasic()


def _admin(creds: HTTPBasicCredentials = Depends(basic)):
    if not config.ADMIN_PASSWORD:
        raise HTTPException(503, "Admin page disabled: set ADMIN_PASSWORD in .env")
    ok = (pysecrets.compare_digest(creds.username, config.ADMIN_USER)
          and pysecrets.compare_digest(creds.password, config.ADMIN_PASSWORD))
    if not ok:
        raise HTTPException(401, "Wrong login", headers={"WWW-Authenticate": "Basic"})
    return creds.username

app = FastAPI(title="Dolce Mailer")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


def _page(msg: str) -> HTMLResponse:
    return HTMLResponse(
        f"<div style='font-family:Arial;max-width:480px;margin:80px auto;"
        f"text-align:center'><h2>Dolce Mailer</h2><p>{msg}</p></div>")


@app.get("/approve/{token}")
def approve(token: str):
    with db.connect() as con:
        row = con.execute(
            "SELECT id, status FROM campaigns WHERE token=?", (token,)).fetchone()
        if not row:
            return _page("Unknown campaign link.")
        if row["status"] != "pending":
            return _page(f"Campaign already {row['status']}.")
        con.execute(
            "UPDATE campaigns SET status='approved', decided_at=CURRENT_TIMESTAMP "
            "WHERE id=?", (row["id"],))
    return _page("Approved. The campaign will send on the next queue run (within 5 minutes).")


@app.get("/reject/{token}")
def reject(token: str):
    with db.connect() as con:
        row = con.execute(
            "SELECT id, status FROM campaigns WHERE token=?", (token,)).fetchone()
        if not row:
            return _page("Unknown campaign link.")
        if row["status"] != "pending":
            return _page(f"Campaign already {row['status']}.")
        con.execute(
            "UPDATE campaigns SET status='rejected', decided_at=CURRENT_TIMESTAMP "
            "WHERE id=?", (row["id"],))
    return _page("Rejected. Nothing was sent.")


@app.get("/unsubscribe/{token}")
@app.post("/unsubscribe/{token}")  # RFC 8058 one-click POST
def unsubscribe(token: str):
    with db.connect() as con:
        row = con.execute(
            "SELECT wix_id FROM contacts WHERE unsub_token=?", (token,)).fetchone()
        if not row:
            return _page("Unknown unsubscribe link.")
        con.execute("UPDATE contacts SET unsubscribed=1 WHERE unsub_token=?", (token,))
    return _page("You are unsubscribed and will not receive further emails from Dolce.")


@app.post("/webhooks/brevo")
async def brevo_webhook(request: Request):
    """Hard bounces and complaints go straight to the suppression list."""
    body = await request.json()
    event = body.get("event", "")
    email = body.get("email", "")
    if email and event in ("hard_bounce", "spam", "complaint", "blocked", "invalid_email"):
        with db.connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO suppression (email, reason) VALUES (?,?)",
                (email, event))
    return {"ok": True}


CAMPAIGN_SHELL = Path(__file__).parent / "templates" / "campaign.html"

ADMIN_FORM = """
<div style='font-family:Arial;max-width:560px;margin:40px auto;'>
  <h2>Dolce Mailer - new campaign</h2>
  <p style='color:#666'>Fill this in and press Create. You will receive an
  approval email at {approver} - nothing sends until you click Approve there.</p>
  <form method='post' action='/admin/create'>
    <p><label>Campaign name (internal)<br>
      <input name='name' required style='width:100%%;padding:8px'></label></p>
    <p><label>Subject line<br>
      <input name='subject' required style='width:100%%;padding:8px'></label></p>
    <p><label>Heading (shown in the email)<br>
      <input name='heading' required style='width:100%%;padding:8px'></label></p>
    <p><label>Message (plain text; blank line = new paragraph)<br>
      <textarea name='body' rows='10' required style='width:100%%;padding:8px'></textarea></label></p>
    <p><button type='submit' style='background:#c2a273;color:#fff;border:0;
      padding:12px 28px;font-size:15px'>Create campaign</button></p>
  </form>
  <hr><h3>Recent campaigns</h3>{recent}
</div>"""


@app.get("/admin")
def admin_form(user: str = Depends(_admin)):
    with db.connect() as con:
        rows = con.execute(
            "SELECT name, status, created_at FROM campaigns ORDER BY id DESC LIMIT 10"
        ).fetchall()
    recent = "".join(
        f"<p>{html_mod.escape(r['name'])} - <b>{r['status']}</b> ({r['created_at']})</p>"
        for r in rows) or "<p>None yet.</p>"
    return HTMLResponse(ADMIN_FORM.format(approver=config.APPROVER_EMAIL, recent=recent))


@app.post("/admin/create")
def admin_create(user: str = Depends(_admin), name: str = Form(...),
                 subject: str = Form(...), heading: str = Form(...),
                 body: str = Form(...)):
    paragraphs = [html_mod.escape(p.strip()).replace("\n", "<br>")
                  for p in body.replace("\r", "").split("\n\n") if p.strip()]
    body_html = "<br><br>\n".join(paragraphs)
    shell = CAMPAIGN_SHELL.read_text()
    campaign_html = (shell.replace("{{heading}}", html_mod.escape(heading))
                          .replace("{{body}}", body_html))
    campaigns.create_from_html(name, subject, campaign_html)
    return _page(f"Campaign '{html_mod.escape(name)}' created. "
                 f"Check {config.APPROVER_EMAIL} for the approval email - "
                 "it sends only after Approve is clicked there.")
