"""Web endpoints: campaign approve/reject, one-click unsubscribe, Brevo webhook."""
import html as html_mod
import secrets as pysecrets
import traceback
from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from . import alerts, campaigns, config, db

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


@app.exception_handler(Exception)
async def _unhandled(request, exc):
    alerts.send_alert("[Dolce Mailer] portal error",
                      f"URL: {request.url}\n\n"
                      + "".join(traceback.format_exception(exc)))
    return _page("Something went wrong on our side. The team has been alerted "
                 "automatically - please try again in a few minutes.")


app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


def _page(msg: str) -> HTMLResponse:
    return HTMLResponse(f"""
<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Dolce</title>
<link rel='icon' type='image/png' href='/static/dolce-logo.png'>
<style>
  :root{{--page:#f5eff0;--card:#fff;--body:#4a4a4a;--gold:#c2a273;
        --shadow:0 8px 30px rgba(157,129,132,.18);}}
  @media (prefers-color-scheme: dark){{
    :root{{--page:#191516;--card:#231e1f;--body:#cfc5c2;--gold:#d0b285;
          --shadow:0 8px 30px rgba(0,0,0,.5);}}}}
  body{{margin:0;background:var(--page);font-family:Georgia,serif;}}
  .card{{max-width:480px;margin:9vh auto;background:var(--card);border-radius:10px;
        padding:44px 36px;text-align:center;box-shadow:var(--shadow);}}
  .card img{{width:170px;max-width:70%;}}
  .msg{{font-size:17px;line-height:1.6;color:var(--body);margin-top:28px;}}
  .foot{{font-family:Arial;font-size:11px;letter-spacing:2px;color:var(--gold);
        margin-top:32px;}}
</style>
<body><div class="card">
  <img src="/static/dolce-logo.png" alt="Dolce Aesthetic Clinic">
  <p class="msg">{msg}</p>
  <p class="foot">DOLCE AESTHETIC CLINIC</p>
</div></body>""")


@app.get("/favicon.ico")
def favicon():
    return FileResponse(Path(__file__).parent / "static" / "dolce-logo.png",
                        media_type="image/png")


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

STATUS_COLORS = {"pending": "#c9a227", "approved": "#5aa860",
                 "sent": "#a08d63", "rejected": "#c96060"}

ADMIN_PAGE = """
<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Dolce Campaigns</title>
<link rel='icon' type='image/png' href='/static/dolce-logo.png'>
<style>
  :root{
    --page:#f5eff0; --card:#ffffff; --ink:#2b2b2b; --body:#4a4a4a;
    --muted:#8a8a8a; --faint:#a99a9c; --line:#ead9dc; --line-soft:#f3eaec;
    --field:#fdfbfb; --field-border:#e2d3d6; --chipbg:#faf6f7; --chip:#ffffff;
    --gold:#c2a273; --gold-hover:#b3925f;
    --shadow:0 8px 30px rgba(157,129,132,.18);
  }
  @media (prefers-color-scheme: dark){
    :root{
      --page:#191516; --card:#231e1f; --ink:#f0e9e6; --body:#cfc5c2;
      --muted:#9a8f90; --faint:#877b7d; --line:#3a3132; --line-soft:#322a2b;
      --field:#2b2526; --field-border:#463c3d; --chipbg:#2a2425; --chip:#231e1f;
      --gold:#d0b285; --gold-hover:#c2a273;
      --shadow:0 8px 30px rgba(0,0,0,.5);
    }
  }
  body{margin:0;background:var(--page);font-family:Arial,Helvetica,sans-serif;color:var(--body);}
  .card{max-width:620px;margin:40px auto;background:var(--card);border-radius:12px;
        box-shadow:var(--shadow);overflow:hidden;}
  .head{padding:36px 40px 24px;text-align:center;border-bottom:1px solid var(--line);}
  .head img{width:190px;max-width:70%;}
  h1{font-family:Georgia,serif;font-weight:normal;font-size:26px;color:var(--ink);
     margin:26px 0 6px;}
  .sub{color:var(--muted);font-size:14px;margin:0;}
  .tabs{display:flex;gap:6px;justify-content:center;padding:16px 20px 0;
        flex-wrap:wrap;background:var(--card);}
  .tab{padding:8px 18px;border-radius:999px;font-size:13px;text-decoration:none;
        color:var(--muted);border:1px solid var(--line);}
  .tab.active{background:var(--gold);color:#fff;border-color:var(--gold);}
  .steps{display:flex;gap:8px;justify-content:center;padding:18px 20px;
         background:var(--chipbg);border-bottom:1px solid var(--line);flex-wrap:wrap;}
  .step{font-size:12.5px;color:var(--muted);background:var(--chip);
        border:1px solid var(--line);border-radius:999px;padding:7px 14px;}
  .step b{color:var(--gold);}
  form{padding:30px 40px 40px;}
  label{display:block;font-size:11px;letter-spacing:2px;color:var(--gold);
        text-transform:uppercase;margin:22px 0 7px;}
  label:first-of-type{margin-top:0;}
  select{width:100%;box-sizing:border-box;border:1px solid var(--field-border);
        border-radius:8px;padding:13px 14px;font-size:15px;font-family:inherit;
        color:var(--ink);background:var(--field);}
  select:focus{outline:none;border-color:var(--gold);}
  input,textarea{width:100%;box-sizing:border-box;border:1px solid var(--field-border);
        border-radius:8px;padding:13px 14px;font-size:15px;font-family:inherit;
        color:var(--ink);background:var(--field);transition:border .15s;}
  input:focus,textarea:focus{outline:none;border-color:var(--gold);}
  input::placeholder,textarea::placeholder{color:var(--faint);}
  .hint{font-size:12.5px;color:var(--faint);margin-top:6px;}
  button{width:100%;margin-top:30px;background:var(--gold);color:#fff;border:0;
        border-radius:8px;padding:16px;font-size:15px;letter-spacing:1.5px;cursor:pointer;}
  button:hover{background:var(--gold-hover);}
  .recent{padding:26px 40px 36px;border-top:1px solid var(--line);}
  .recent h2{font-family:Georgia,serif;font-weight:normal;font-size:19px;
        color:var(--ink);margin:0 0 14px;}
  .row{display:flex;justify-content:space-between;align-items:center;
        padding:10px 0;border-bottom:1px solid var(--line-soft);font-size:14px;gap:10px;}
  .row:last-child{border-bottom:0;}
  .pill{font-size:11px;letter-spacing:1px;border-radius:999px;padding:4px 12px;
        text-transform:uppercase;white-space:nowrap;border:1px solid currentColor;
        background:transparent;}
  .when{color:var(--faint);font-size:12px;white-space:nowrap;}
  @media(max-width:640px){form,.recent{padding-left:22px;padding-right:22px;}}
</style>
<body>
  <div class="card">
    <div style="display:flex;justify-content:flex-end;gap:14px;padding:12px 16px 0;">
      <a href="/admin" style="font-size:12px;color:var(--muted);text-decoration:none;">&#8635; Refresh</a>
      <a href="/admin/logout" style="font-size:12px;color:var(--muted);text-decoration:none;">Log out</a>
    </div>
    <div class="head">
      <img src="/static/dolce-logo.png" alt="Dolce Aesthetic Clinic">
      <h1>%%FORM_TITLE%%</h1>
      <p class="sub">Write it here - approve it from your inbox - we send it carefully.</p>
    </div>
    <div class="tabs">%%TABS%%</div>
    <div class="steps">
      <span class="step"><b>1</b> Write &amp; create</span>
      <span class="step"><b>2</b> Approve from %%APPROVER%%</span>
      <span class="step"><b>3</b> Sent to consented clients only</span>
    </div>
    <form method="post" action="%%ACTION%%">
      <label>Campaign name <span style="color:#b5a7a9;text-transform:none;letter-spacing:0;">(just for you)</span></label>
      <input name="name" required placeholder="e.g. September glow offer" value="%%V_NAME%%">
      <input type="hidden" name="audience" value="%%AUD%%">
      <label>Subject line</label>
      <input name="subject" required placeholder="e.g. A little something special for our clients" value="%%V_SUBJECT%%">
      <div class="hint">This is what appears in their inbox - keep it warm and short.</div>
      <label>Heading</label>
      <input name="heading" required placeholder="e.g. An autumn treat, just for you" value="%%V_HEADING%%">
      <div class="hint">The large title inside the email.</div>
      <label>Message</label>
      <textarea name="body" rows="9" required
        placeholder="Write naturally, like a note to a client.&#10;&#10;Leave a blank line to start a new paragraph. Every email automatically starts with the client's name and ends with the WhatsApp button and your clinic details.">%%V_BODY%%</textarea>
      <button type="submit">%%BUTTON%%</button>
    </form>
%%BIRTHDAYS_SECTION%%
    <div class="recent">
      <h2>Recent campaigns</h2>
      %%RECENT%%
    </div>
  </div>
</body>"""


def _campaign_html(heading: str, body: str) -> str:
    paragraphs = [html_mod.escape(pp.strip()).replace("\n", "<br>")
                  for pp in body.replace("\r", "").split("\n\n") if pp.strip()]
    body_html = "<br><br>\n".join(paragraphs)
    shell = CAMPAIGN_SHELL.read_text()
    return (shell.replace("{{heading}}", html_mod.escape(heading))
                 .replace("{{body}}", body_html))


SINGLE_BRAND = True  # Dolce-only for now; set False to show all brand tabs

BRANDS = [("dolce", "Dolce"), ("polished", "Polished"),
          ("core", "Core"), ("all", "Everyone")]
BRAND_TITLES = {"dolce": "Dolce (clinic)", "polished": "Polished (salon)",
                "core": "Core (studio)", "all": "Everyone"}


def _render_admin(action="/admin/create", title="New campaign",
                  button="CREATE CAMPAIGN", values=None, brand="dolce"):
    v = values or {}
    tabs = "" if SINGLE_BRAND else "".join(
        f"<a class='tab{' active' if key == brand else ''}' "
        f"href='/admin?brand={key}'>{label}</a>" for key, label in BRANDS)
    with db.connect() as con:
        rows = con.execute(
            "SELECT id, name, status, created_at FROM campaigns "
            "WHERE COALESCE(audience,'all') = ? ORDER BY id DESC LIMIT 10",
            (brand,)).fetchall()
    if rows:
        parts = []
        for r in rows:
            fg = STATUS_COLORS.get(r["status"], "#8a8a8a")
            actions = ""
            if r["status"] == "pending":
                actions = (f"<a href='/admin/edit/{r['id']}' style='color:#c2a273;"
                           f"font-size:12px;margin-right:8px;'>edit</a>"
                           f"<form method='post' action='/admin/delete/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>delete</button></form>")
            elif r["status"] == "approved":
                actions = (f"<form method='post' action='/admin/cancel/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>cancel send</button></form>")
            elif r["status"] == "rejected":
                actions = (f"<form method='post' action='/admin/delete/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>delete</button></form>")
            parts.append(
                f"<div class='row'><span>{html_mod.escape(r['name'])}</span>"
                f"<span>{actions}</span>"
                f"<span class='pill' style='color:{fg}'>{r['status']}</span>"
                f"<span class='when'>{r['created_at'][:16]}</span></div>")
        recent = "".join(parts)
    else:
        recent = ("<p style='color:#a99a9c;font-size:14px;'>No "
                  f"{BRAND_TITLES[brand]} campaigns yet.</p>")
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
        bd_section = ('<div class="recent"><h2>Upcoming birthdays '
                      '<span style="font-size:12px;color:#b5a7a9;">(next 30 days)</span></h2>'
                      + bd + '</div>')
    else:
        bd_section = ""
    page = (ADMIN_PAGE.replace("%%BIRTHDAYS_SECTION%%", bd_section)
                      .replace("%%TABS%%", tabs)
                      .replace("%%AUD%%", brand)
                      .replace("%%APPROVER%%", config.APPROVER_EMAIL)
                      .replace("%%RECENT%%", recent)
                      .replace("%%ACTION%%", action)
                      .replace("%%FORM_TITLE%%", title)
                      .replace("%%BUTTON%%", button)
                      .replace("%%V_NAME%%", html_mod.escape(v.get("name", ""), quote=True))
                      .replace("%%V_SUBJECT%%", html_mod.escape(v.get("subject", ""), quote=True))
                      .replace("%%V_HEADING%%", html_mod.escape(v.get("heading", ""), quote=True))
                      .replace("%%V_BODY%%", html_mod.escape(v.get("body", ""))))
    return HTMLResponse(page)


@app.get("/admin/logout")
def admin_logout():
    return HTMLResponse(
        "<div style='font-family:Arial;max-width:420px;margin:14vh auto;"
        "text-align:center;color:#4a4a4a;'><h3>Logged out</h3>"
        "<p>You can close this tab. Visiting the admin page again will ask "
        "for the login.</p></div>",
        status_code=401, headers={"WWW-Authenticate": 'Basic realm="dolce"'})


@app.get("/admin")
def admin_form(user: str = Depends(_admin), brand: str = "dolce"):
    if SINGLE_BRAND:
        # All current clients are Dolce clients; campaigns reach every
        # consented contact until the other brands launch.
        return _render_admin(title="New campaign - Dolce", brand="all")
    if brand not in BRAND_TITLES:
        brand = "dolce"
    return _render_admin(title=f"New campaign - {BRAND_TITLES[brand]}", brand=brand)


@app.get("/admin/edit/{cid}")
def admin_edit_form(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT * FROM campaigns WHERE id=?", (cid,)).fetchone()
    if not r or r["status"] != "pending":
        return _page("Only campaigns still waiting for approval can be edited.")
    keys = r.keys()
    aud = (r["audience"] if "audience" in keys else "all") or "all"
    vals = {"name": r["name"], "subject": r["subject"],
            "heading": r["heading"] or "", "body": r["body_raw"] or "",
            "audience": aud}
    return _render_admin(action=f"/admin/edit/{cid}",
                         title=f"Edit campaign - {BRAND_TITLES.get(aud, aud)}",
                         button="SAVE &amp; RESEND FOR APPROVAL", values=vals,
                         brand=aud)


@app.post("/admin/edit/{cid}")
def admin_edit(cid: int, user: str = Depends(_admin), name: str = Form(...),
               subject: str = Form(...), heading: str = Form(...),
               body: str = Form(...), audience: str = Form("all")):
    try:
        campaigns.update_campaign(cid, name, subject,
                                  _campaign_html(heading, body), heading, body,
                                  audience=audience)
    except ValueError as e:
        return _page(str(e))
    return _page(f"Campaign <b>{html_mod.escape(name)}</b> updated. A fresh test copy "
                 f"and approval email are on their way to {config.APPROVER_EMAIL}; "
                 "the previous approval links no longer work.")


@app.post("/admin/delete/{cid}")
def admin_delete(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT status, name FROM campaigns WHERE id=?", (cid,)).fetchone()
        if not r:
            return _page("Campaign not found.")
        if r["status"] not in ("pending", "rejected"):
            return _page("Sent campaigns stay in the history and approved ones must be "
                         "cancelled first.")
        con.execute("DELETE FROM campaigns WHERE id=?", (cid,))
    return _page(f"Campaign <b>{html_mod.escape(r['name'])}</b> deleted. Nothing was sent.")


@app.post("/admin/cancel/{cid}")
def admin_cancel(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT status, name FROM campaigns WHERE id=?", (cid,)).fetchone()
        if not r or r["status"] != "approved":
            return _page("Only approved-but-not-yet-sent campaigns can be cancelled.")
        con.execute("UPDATE campaigns SET status='rejected' WHERE id=?", (cid,))
    return _page(f"Campaign <b>{html_mod.escape(r['name'])}</b> cancelled before sending.")


@app.post("/admin/create")
def admin_create(user: str = Depends(_admin), name: str = Form(...),
                 subject: str = Form(...), heading: str = Form(...),
                 body: str = Form(...), audience: str = Form("all")):
    campaigns.create_from_html(name, subject, _campaign_html(heading, body),
                               heading=heading, body_raw=body, audience=audience)
    return _page(f"Your campaign <b>{html_mod.escape(name)}</b> is created.<br><br>"
                 f"Now check <b>{config.APPROVER_EMAIL}</b> - the approval email is on its "
                 "way. Nothing sends until you press Approve there.")
