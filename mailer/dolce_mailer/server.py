"""Web endpoints: campaign approve/reject, one-click unsubscribe, Brevo webhook."""
import html as html_mod
import secrets as pysecrets
from datetime import date, timedelta
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
    return HTMLResponse(f"""
<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Dolce</title>
<body style="margin:0;background:#f5eff0;font-family:Georgia,serif;">
  <div style="max-width:480px;margin:9vh auto;background:#fff;border-radius:10px;
              padding:44px 36px;text-align:center;
              box-shadow:0 8px 30px rgba(157,129,132,.18);">
    <img src="/static/dolce-logo.jpg" alt="Dolce Aesthetic Clinic"
         style="width:170px;max-width:70%%;">
    <p style="font-size:17px;line-height:1.6;color:#4a4a4a;margin-top:28px;">{msg}</p>
    <p style="font-family:Arial;font-size:11px;letter-spacing:2px;color:#c2a273;
              margin-top:32px;">DOLCE AESTHETIC CLINIC</p>
  </div>
</body>""")


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

STATUS_COLORS = {"pending": ("#8a6d1a", "#faf3d9"), "approved": ("#2e6b32", "#e2f2e3"),
                 "sent": ("#6b5b3e", "#f1e9dc"), "rejected": ("#8a2626", "#f7e0e0")}

ADMIN_PAGE = """
<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Dolce Campaigns</title>
<style>
  body{margin:0;background:#f5eff0;font-family:Arial,Helvetica,sans-serif;color:#4a4a4a;}
  .card{max-width:620px;margin:40px auto;background:#fff;border-radius:12px;
        box-shadow:0 8px 30px rgba(157,129,132,.18);overflow:hidden;}
  .head{padding:36px 40px 24px;text-align:center;border-bottom:1px solid #ead9dc;}
  .head img{width:190px;max-width:70%;}
  h1{font-family:Georgia,serif;font-weight:normal;font-size:26px;color:#2b2b2b;
     margin:26px 0 6px;}
  .sub{color:#8a8a8a;font-size:14px;margin:0;}
  .steps{display:flex;gap:8px;justify-content:center;padding:18px 20px;
         background:#faf6f7;border-bottom:1px solid #ead9dc;flex-wrap:wrap;}
  .step{font-size:12.5px;color:#7a6a6c;background:#fff;border:1px solid #ead9dc;
        border-radius:999px;padding:7px 14px;}
  .step b{color:#c2a273;}
  form{padding:30px 40px 40px;}
  label{display:block;font-size:11px;letter-spacing:2px;color:#c2a273;
        text-transform:uppercase;margin:22px 0 7px;}
  label:first-of-type{margin-top:0;}
  input,textarea{width:100%;box-sizing:border-box;border:1px solid #e2d3d6;
        border-radius:8px;padding:13px 14px;font-size:15px;font-family:inherit;
        color:#2b2b2b;background:#fdfbfb;transition:border .15s;}
  input:focus,textarea:focus{outline:none;border-color:#c2a273;background:#fff;}
  .hint{font-size:12.5px;color:#a99a9c;margin-top:6px;}
  button{width:100%;margin-top:30px;background:#c2a273;color:#fff;border:0;border-radius:8px;padding:16px;
        font-size:15px;letter-spacing:1.5px;cursor:pointer;}
  button:hover{background:#b3925f;}
  .recent{padding:26px 40px 36px;border-top:1px solid #ead9dc;}
  .recent h2{font-family:Georgia,serif;font-weight:normal;font-size:19px;
        color:#2b2b2b;margin:0 0 14px;}
  .row{display:flex;justify-content:space-between;align-items:center;
        padding:10px 0;border-bottom:1px solid #f3eaec;font-size:14px;gap:10px;}
  .row:last-child{border-bottom:0;}
  .pill{font-size:11px;letter-spacing:1px;border-radius:999px;padding:4px 12px;
        text-transform:uppercase;white-space:nowrap;}
  .when{color:#b5a7a9;font-size:12px;white-space:nowrap;}
  @media(max-width:640px){form,.recent{padding-left:22px;padding-right:22px;}}
</style>
<body>
  <div class="card">
    <div class="head">
      <img src="/static/dolce-logo.jpg" alt="Dolce Aesthetic Clinic">
      <h1>New campaign</h1>
      <p class="sub">Write it here - approve it from your inbox - we send it carefully.</p>
    </div>
    <div class="steps">
      <span class="step"><b>1</b> Write &amp; create</span>
      <span class="step"><b>2</b> Approve from %%APPROVER%%</span>
      <span class="step"><b>3</b> Sent to consented clients only</span>
    </div>
    <form method="post" action="/admin/create">
      <label>Campaign name <span style="color:#b5a7a9;text-transform:none;letter-spacing:0;">(just for you)</span></label>
      <input name="name" required placeholder="e.g. September glow offer">
      <label>Subject line</label>
      <input name="subject" required placeholder="e.g. A little something special for our clients">
      <div class="hint">This is what appears in their inbox - keep it warm and short.</div>
      <label>Heading</label>
      <input name="heading" required placeholder="e.g. An autumn treat, just for you">
      <div class="hint">The large title inside the email.</div>
      <label>Message</label>
      <textarea name="body" rows="9" required
        placeholder="Write naturally, like a note to a client.&#10;&#10;Leave a blank line to start a new paragraph. Every email automatically starts with the client's name and ends with the WhatsApp button and your clinic details."></textarea>
      <button type="submit">CREATE CAMPAIGN</button>
    </form>
    <div class="recent">
      <h2>Upcoming birthdays <span style="font-size:12px;color:#b5a7a9;">(next 30 days)</span></h2>
      %%BIRTHDAYS%%
    </div>
    <div class="recent">
      <h2>Recent campaigns</h2>
      %%RECENT%%
    </div>
  </div>
</body>"""


@app.get("/admin")
def admin_form(user: str = Depends(_admin)):
    with db.connect() as con:
        rows = con.execute(
            "SELECT name, status, created_at FROM campaigns ORDER BY id DESC LIMIT 10"
        ).fetchall()
    if rows:
        parts = []
        for r in rows:
            fg, bg = STATUS_COLORS.get(r["status"], ("#666", "#eee"))
            parts.append(
                f"<div class='row'><span>{html_mod.escape(r['name'])}</span>"
                f"<span class='pill' style='color:{fg};background:{bg}'>{r['status']}</span>"
                f"<span class='when'>{r['created_at'][:16]}</span></div>")
        recent = "".join(parts)
    else:
        recent = "<p style='color:#a99a9c;font-size:14px;'>Nothing yet - your first campaign will appear here.</p>"
    today = date.today()
    upcoming = []
    with db.connect() as con:
        for c in db.eligible_contacts(con):
            b = (c["birthday"] or "")[5:10]
            if len(b) != 5:
                continue
            try:
                nxt = date(today.year, int(b[:2]), int(b[3:]))
            except ValueError:
                continue
            if nxt < today:
                nxt = date(today.year + 1, int(b[:2]), int(b[3:]))
            days = (nxt - today).days
            if days <= 30:
                upcoming.append((days, nxt, c["first_name"] or c["email"]))
    upcoming.sort()
    if upcoming:
        bd = "".join(
            f"<div class='row'><span>{html_mod.escape(str(nm))}</span>"
            f"<span class='when'>{d.strftime('%d %b')}"
            f"{' - today!' if days == 0 else f' (in {days}d)'}</span></div>"
            for days, d, nm in upcoming)
        bd += ("<p style='color:#a99a9c;font-size:12.5px;margin-top:10px;'>Each of them "
               "automatically receives the birthday email on the day - nothing to do.</p>")
    else:
        bd = ("<p style='color:#a99a9c;font-size:14px;'>No birthdays in the next 30 days. "
              "Birthday dates come from the client list - once the full list is imported, "
              "they appear here.</p>")
    page = (ADMIN_PAGE.replace("%%APPROVER%%", config.APPROVER_EMAIL)
                      .replace("%%RECENT%%", recent)
                      .replace("%%BIRTHDAYS%%", bd))
    return HTMLResponse(page)


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
    return _page(f"Your campaign <b>{html_mod.escape(name)}</b> is created.<br><br>"
                 f"Now check <b>{config.APPROVER_EMAIL}</b> - the approval email is on its "
                 "way. Nothing sends until you press Approve there.")
