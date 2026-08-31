"""Web endpoints: campaign approve/reject, one-click unsubscribe, Brevo webhook."""
import html as html_mod
import re
import secrets as pysecrets
import traceback
from datetime import date, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from . import alerts, campaigns, config, db, render, send, users

basic = HTTPBasic()


def _admin(creds: HTTPBasicCredentials = Depends(basic)):
    row = users.get(creds.username)
    if row and users.verify(creds.password, row["pw_hash"]):
        return row["username"]
    if config.ADMIN_PASSWORD:  # legacy env credential still works as fallback
        ok = (pysecrets.compare_digest(creds.username, config.ADMIN_USER)
              and pysecrets.compare_digest(creds.password, config.ADMIN_PASSWORD))
        if ok:
            return creds.username
    raise HTTPException(401, "Wrong login", headers={"WWW-Authenticate": "Basic"})

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

STATUS_COLORS = {"draft": "#8a8a8a", "pending": "#c9a227", "approved": "#5aa860",
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
  .card{max-width:900px;margin:40px auto;background:var(--card);border-radius:12px;
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
      <a href="/admin/auto" style="font-size:12px;color:var(--gold);text-decoration:none;">Automatic emails</a>
      <a href="/admin/password" style="font-size:12px;color:var(--muted);text-decoration:none;">Password</a>
      <a href="/admin/logout" style="font-size:12px;color:var(--muted);text-decoration:none;">Log out</a>
    </div>
    <div class="head">
      %%LOGO%%
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
      <input type="hidden" name="return_action" value="%%ACTION%%">
      <label>Subject line</label>
      <input name="subject" required placeholder="e.g. A little something special for our clients" value="%%V_SUBJECT%%">
      <div class="hint">This is what appears in their inbox - keep it warm and short.</div>
      <label>Heading</label>
      <input name="heading" required placeholder="e.g. An autumn treat, just for you" value="%%V_HEADING%%">
      <div class="hint">The large title inside the email.</div>
      <label>Message</label>
      <div style="margin:0 0 8px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <span style="font-size:12px;color:var(--faint);">Insert:</span>
        <button type="button" onclick="insertPh('{{first_name}}')"
          style="all:unset;cursor:pointer;font-size:12px;color:var(--gold);
                 border:1px solid var(--gold);border-radius:999px;padding:4px 12px;">
          + client's first name</button>
        <span style="font-size:11.5px;color:var(--faint);">inserts into whichever
          field you last clicked (subject, heading or message) - becomes each
          client's own name</span>
      </div>
      <textarea name="body" rows="9" required
        placeholder="Write naturally, like a note to a client.&#10;&#10;Leave a blank line to start a new paragraph. Every email automatically starts with the client's name and ends with the WhatsApp button and your clinic details.">%%V_BODY%%</textarea>
      <label>Send time <span style="color:#b5a7a9;text-transform:none;letter-spacing:0;">(optional)</span></label>
      <input type="datetime-local" name="schedule_local" value="%%V_SCHED%%">
      <div class="hint">Leave empty to send right after approval. Times are Erbil time -
        after approval the campaign waits until this moment.</div>
      <div style="display:flex;gap:12px;margin-top:30px;">
        <button type="submit" formaction="/admin/preview"
          style="margin-top:0;background:transparent;border:1px solid var(--gold);
                 color:var(--gold);">PREVIEW FIRST</button>
        <button type="submit" formaction="/admin/draft"
          style="margin-top:0;background:transparent;border:1px solid var(--faint);
                 color:var(--muted);">SAVE AS DRAFT</button>
        <button type="submit" style="margin-top:0;">%%BUTTON%%</button>
      </div>
      <script>
        var phTarget=document.querySelector("textarea[name=body]");
        ["subject","heading","body"].forEach(function(n){
          var el=document.querySelector("[name="+n+"]");
          if(el){ el.addEventListener("focus",function(){ phTarget=el; }); }
        });
        function insertPh(t){
          var el=phTarget||document.querySelector("textarea[name=body]");
          var a=el.selectionStart||el.value.length, b=el.selectionEnd||a;
          el.value=el.value.slice(0,a)+t+el.value.slice(b);
          el.focus(); el.selectionStart=el.selectionEnd=a+t.length;
        }
      </script>
    </form>
%%BIRTHDAYS_SECTION%%
    <div class="recent">
      <h2>%%RECENT_TITLE%% %%ARCHTOGGLE%%</h2>
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


SINGLE_BRAND = False  # tabs visible; Dolce is the default tab

BRANDS = [("dolce", "Dolce"), ("polished", "Polished"), ("core", "Core")]
BRAND_TITLES = {"dolce": "Dolce (clinic)", "polished": "Polished (salon)",
                "core": "Core (studio)", "all": "Everyone"}


def _render_admin(action="/admin/create", title="New campaign",
                  button="CREATE CAMPAIGN", values=None, brand="dolce",
                  show_archived=False):
    v = values or {}
    tabs = "" if SINGLE_BRAND else "".join(
        f"<a class='tab{' active' if key == brand else ''}' "
        f"href='/admin?brand={key}'>{label}</a>" for key, label in BRANDS)
    with db.connect() as con:
        rows = con.execute(
            "SELECT id, name, status, created_at FROM campaigns "
            "WHERE COALESCE(audience,'all') = ? AND COALESCE(archived,0) = ? "
            "ORDER BY id DESC LIMIT 10",
            (brand, 1 if show_archived else 0)).fetchall()
        n_archived = con.execute(
            "SELECT COUNT(*) FROM campaigns WHERE COALESCE(audience,'all') = ? "
            "AND COALESCE(archived,0) = 1", (brand,)).fetchone()[0]
        sent_counts = {r["id"]: con.execute(
            "SELECT COUNT(*) FROM sends WHERE kind=?",
            (f"campaign:{r['id']}",)).fetchone()[0] for r in rows}
    if rows:
        parts = []
        for r in rows:
            fg = STATUS_COLORS.get(r["status"], "#8a8a8a")
            actions = ""
            if r["status"] == "draft":
                actions = (f"<a href='/admin/edit/{r['id']}' style='color:#c2a273;"
                           f"font-size:12px;margin-right:8px;'>edit</a>"
                           f"<form method='post' action='/admin/submit/{r['id']}' "
                           f"style='display:inline;margin-right:8px;'><button style='all:unset;"
                           f"color:#5aa860;font-size:12px;cursor:pointer;'>submit for approval"
                           f"</button></form>"
                           f"<form method='post' action='/admin/delete/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>delete</button></form>")
            elif r["status"] == "pending":
                actions = (f"<a href='/admin/edit/{r['id']}' style='color:#c2a273;"
                           f"font-size:12px;margin-right:8px;'>edit</a>"
                           f"<form method='post' action='/admin/delete/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>delete</button></form>")
            elif r["status"] == "approved":
                actions = (f"<a href='/admin/edit/{r['id']}' style='color:#c2a273;"
                           f"font-size:12px;margin-right:8px;'>edit</a>"
                           f"<form method='post' action='/admin/cancel/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>cancel send</button></form>")
            elif r["status"] == "sent":
                verb = "unarchive" if show_archived else "archive"
                actions = (f"<form method='post' action='/admin/{verb}/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;"
                           f"color:#a08d63;font-size:12px;cursor:pointer;'>{verb}"
                           f"</button></form>")
            elif r["status"] == "rejected":
                actions = (f"<form method='post' action='/admin/delete/{r['id']}' "
                           f"style='display:inline'><button style='all:unset;color:#c96060;"
                           f"font-size:12px;cursor:pointer;'>delete</button></form>")
            parts.append(
                f"<div class='row'><span><a href='/admin/view/{r['id']}' "
                f"style='color:inherit;text-decoration:none;border-bottom:1px dotted "
                f"var(--gold);'>{html_mod.escape(r['name'])}</a></span>"
                f"<span>{actions}</span>"
                f"<span class='pill' style='color:{fg}'>{r['status']}</span>"
                f"<span class='when'>{sent_counts[r['id']]} sent &middot; "
                f"{r['created_at'][:16]}</span></div>")
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
    logo_html = ('<a href="/admin"><img src="/static/dolce-logo.png" '
                 'alt="Dolce Aesthetic Clinic" '
                 'style="width:190px;max-width:70%;"></a>' if brand == "dolce" else "")
    if show_archived:
        recent_title = "Archived campaigns"
        arch_toggle = (f"<a href='/admin?brand={brand}' style='font-size:12px;"
                       f"color:var(--gold);text-decoration:none;'>back to recent</a>")
    else:
        recent_title = "Recent campaigns"
        arch_toggle = (f"<a href='/admin?brand={brand}&archived=1' style='font-size:12px;"
                       f"color:var(--faint);text-decoration:none;'>archived ({n_archived})</a>"
                       if n_archived else "")
    page = (ADMIN_PAGE.replace("%%LOGO%%", logo_html)
                      .replace("%%RECENT_TITLE%%", recent_title)
                      .replace("%%ARCHTOGGLE%%", arch_toggle)
                      .replace("%%BIRTHDAYS_SECTION%%", bd_section)
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
                      .replace("%%V_SCHED%%", html_mod.escape(v.get("schedule_local", ""), quote=True))
                      .replace("%%V_BODY%%", html_mod.escape(v.get("body", ""))))
    return HTMLResponse(page)


_FORM_CSS = """
<style>
  :root{--page:#f5eff0;--card:#fff;--ink:#2b2b2b;--body:#4a4a4a;--gold:#c2a273;
        --faint:#a99a9c;--line:#ead9dc;--field:#fdfbfb;--fb:#e2d3d6;}
  @media (prefers-color-scheme: dark){
    :root{--page:#191516;--card:#231e1f;--ink:#f0e9e6;--body:#cfc5c2;
          --gold:#d0b285;--faint:#877b7d;--line:#3a3132;--field:#2b2526;--fb:#463c3d;}}
  body{margin:0;background:var(--page);font-family:Arial,sans-serif;color:var(--body);}
  .card{max-width:440px;margin:9vh auto;background:var(--card);border-radius:10px;
        padding:36px 32px;}
  h2{font-family:Georgia,serif;font-weight:normal;color:var(--ink);margin:0 0 18px;}
  label{display:block;font-size:11px;letter-spacing:2px;color:var(--gold);
        text-transform:uppercase;margin:16px 0 6px;}
  input{width:100%;box-sizing:border-box;border:1px solid var(--fb);border-radius:8px;
        padding:12px;font-size:15px;background:var(--field);color:var(--ink);}
  button{width:100%;margin-top:24px;background:var(--gold);color:#fff;border:0;
        border-radius:8px;padding:14px;font-size:14px;letter-spacing:1px;cursor:pointer;}
</style>"""


AUTO_LABELS = {"welcome:dolce": "Welcome email - Dolce",
               "welcome:polished": "Welcome email - Polished",
               "welcome:core": "Welcome email - Core",
               "birthday": "Birthday email (sent automatically on each client's birthday)"}


@app.get("/admin/auto")
def auto_list(user: str = Depends(_admin)):
    with db.connect() as con:
        rows = {r["key"]: r for r in con.execute("SELECT * FROM auto_templates")}
    items = "".join(
        f"<div class='row'><span><a href='/admin/auto/{k.replace(':', '-')}' "
        f"style='color:inherit;text-decoration:none;border-bottom:1px dotted var(--gold);'>"
        f"{label}</a></span>"
        f"<span class='when'>updated {(rows[k]['updated_at'] or '')[:16] if k in rows else '-'}</span></div>"
        for k, label in AUTO_LABELS.items())
    page = f"""<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Automatic emails</title>
<link rel='icon' type='image/png' href='/static/dolce-logo.png'>{_FORM_CSS}
<body><div class='card' style='max-width:640px;'>
<p><a href='/admin' style='color:var(--gold);text-decoration:none;font-size:13px;'>&larr; Back to campaigns</a></p>
<h2>Automatic emails</h2>
<p style='font-size:13.5px;color:var(--faint);'>These send themselves - welcomes when
a client is added with a brand label, the birthday email on each client's birthday.
Edits apply to everyone who receives them <b>from now on</b>; people who already
got one are never re-sent.</p>
<style>.row{{display:flex;justify-content:space-between;gap:10px;padding:12px 0;
border-bottom:1px solid var(--line);font-size:14.5px;}}
.when{{color:var(--faint);font-size:12px;white-space:nowrap;}}</style>
{items}
</div></body>"""
    return HTMLResponse(page)


def _auto_key(slug: str) -> str | None:
    key = slug.replace("-", ":", 1) if slug.startswith("welcome-") else slug
    return key if key in AUTO_LABELS else None


@app.get("/admin/auto/{slug}")
def auto_edit_form(slug: str, user: str = Depends(_admin)):
    key = _auto_key(slug)
    if not key:
        return _page("Unknown automatic email.")
    with db.connect() as con:
        r = con.execute("SELECT * FROM auto_templates WHERE key=?", (key,)).fetchone()
    if not r:
        return _page("Template not initialised - run the database setup once.")
    page = f"""<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{AUTO_LABELS[key]}</title>
<link rel='icon' type='image/png' href='/static/dolce-logo.png'>{_FORM_CSS}
<body><div class='card' style='max-width:640px;'>
<p><a href='/admin/auto' style='color:var(--gold);text-decoration:none;font-size:13px;'>&larr; All automatic emails</a></p>
<h2>{AUTO_LABELS[key]}</h2>
<form method='post' action='/admin/auto/{slug}'>
  <label>Subject</label>
  <input name='subject' required value="{html_mod.escape(r['subject'], quote=True)}">
  <label>Heading</label>
  <input name='heading' required value="{html_mod.escape(r['heading'], quote=True)}">
  <label>Message <span style='color:var(--faint);text-transform:none;letter-spacing:0;'>(blank line = new paragraph; {{{{first_name}}}} becomes the client's name)</span></label>
  <textarea name='body' rows='11' required
    style='width:100%;box-sizing:border-box;border:1px solid var(--fb);border-radius:8px;
    padding:12px;font-size:15px;background:var(--field);color:var(--ink);font-family:inherit;'
    >{html_mod.escape(r['body_raw'])}</textarea>
  <button>SAVE - GOES LIVE FOR FUTURE SENDS</button>
</form>
<p style='font-size:12.5px;color:var(--faint);margin-top:14px;'>On save, a test copy
lands in {config.APPROVER_EMAIL} so you can see exactly what future clients will
receive. Clients who already received this email are never re-sent.</p>
</div></body>"""
    return HTMLResponse(page)


@app.post("/admin/auto/{slug}")
def auto_edit_save(slug: str, user: str = Depends(_admin), subject: str = Form(...),
                   heading: str = Form(...), body: str = Form(...)):
    key = _auto_key(slug)
    if not key:
        return _page("Unknown automatic email.")
    with db.connect() as con:
        con.execute("UPDATE auto_templates SET subject=?, heading=?, body_raw=?, "
                    "updated_at=CURRENT_TIMESTAMP WHERE key=?",
                    (subject, heading, body, key))
    sample = {"first_name": "Maya", "unsub_token": "preview"}
    subj_t, html_t = render.render_auto(key)
    try:
        send.send_email(config.APPROVER_EMAIL,
                        f"[TEST - automatic email] {render.render(subj_t, sample)}",
                        render.render(html_t, sample))
    except Exception:
        pass
    return _page(f"<b>{AUTO_LABELS[key]}</b> updated - live for all future sends. "
                 f"A test copy is on its way to {config.APPROVER_EMAIL}. "
                 "Nobody who already received it will get it again.")


@app.get("/admin/password")
def password_form(user: str = Depends(_admin)):
    return HTMLResponse(f"""<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Change password</title>{_FORM_CSS}
<body><div class='card'><h2>Change password</h2>
<form method='post' action='/admin/password'>
  <label>Current password</label><input type='password' name='current' required>
  <label>New password</label><input type='password' name='new1' required minlength='10'>
  <label>New password again</label><input type='password' name='new2' required minlength='10'>
  <button>CHANGE PASSWORD</button>
</form>
<p style='font-size:12.5px;color:var(--faint);margin-top:16px;'>At least 10
characters. After changing, your browser will ask you to log in again.</p>
</div></body>""")


@app.post("/admin/password")
def password_change(user: str = Depends(_admin), current: str = Form(...),
                    new1: str = Form(...), new2: str = Form(...)):
    row = users.get(user)
    if not row or not users.verify(current, row["pw_hash"]):
        return _page("Current password is wrong - nothing changed.")
    if new1 != new2:
        return _page("The two new passwords don't match - nothing changed.")
    if len(new1) < 10:
        return _page("New password must be at least 10 characters - nothing changed.")
    users.set_password(user, new1)
    return _page("Password changed. Your browser will ask for the new login "
                 "next time you open the portal.")


@app.get("/admin/forgot")
def forgot_form():
    return HTMLResponse(f"""<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Reset password</title>{_FORM_CSS}
<body><div class='card'><h2>Forgot password</h2>
<form method='post' action='/admin/forgot'>
  <label>Username</label><input name='username' required>
  <button>EMAIL ME A RESET LINK</button>
</form></div></body>""")


@app.post("/admin/forgot")
def forgot_submit(username: str = Form(...)):
    row = users.get(username)
    if row:
        token = db.new_token()
        with db.connect() as con:
            con.execute("DELETE FROM reset_tokens WHERE expires < datetime('now')")
            con.execute("INSERT INTO reset_tokens (token, username, expires) "
                        "VALUES (?,?,datetime('now','+1 hour'))",
                        (token, row["username"]))
        link = f"{config.APP_BASE_URL}/admin/reset/{token}"
        try:
            send.send_email(row["email"], "Reset your Dolce portal password",
                f"<div style='font-family:Arial;padding:20px;'>"
                f"<p>A password reset was requested for the Dolce campaigns portal "
                f"account <b>{row['username']}</b>.</p>"
                f"<p><a href='{link}' style='background:#c2a273;color:#fff;"
                f"padding:12px 24px;text-decoration:none;border-radius:6px;'>"
                f"SET A NEW PASSWORD</a></p>"
                f"<p style='color:#888;font-size:12px;'>The link works once and "
                f"expires in 1 hour. If you didn't request this, ignore it - "
                f"nothing changes.</p></div>")
        except Exception:
            pass
    return _page("If that account exists, a reset link is on its way to its "
                 "email address. The link expires in 1 hour.")


@app.get("/admin/reset/{token}")
def reset_form(token: str):
    with db.connect() as con:
        row = con.execute("SELECT username FROM reset_tokens WHERE token=? "
                          "AND expires > datetime('now')", (token,)).fetchone()
    if not row:
        return _page("This reset link is invalid or has expired. Request a new "
                     "one from the portal's Forgot password page.")
    return HTMLResponse(f"""<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>New password</title>{_FORM_CSS}
<body><div class='card'><h2>Set a new password</h2>
<form method='post' action='/admin/reset/{token}'>
  <label>New password</label><input type='password' name='new1' required minlength='10'>
  <label>New password again</label><input type='password' name='new2' required minlength='10'>
  <button>SET PASSWORD</button>
</form></div></body>""")


@app.post("/admin/reset/{token}")
def reset_submit(token: str, new1: str = Form(...), new2: str = Form(...)):
    with db.connect() as con:
        row = con.execute("SELECT username FROM reset_tokens WHERE token=? "
                          "AND expires > datetime('now')", (token,)).fetchone()
        if not row:
            return _page("This reset link is invalid or has expired.")
        if new1 != new2 or len(new1) < 10:
            return _page("Passwords must match and be at least 10 characters - "
                         "go back and try again.")
        con.execute("DELETE FROM reset_tokens WHERE token=?", (token,))
    users.set_password(row["username"], new1)
    return _page("Password set. Open the portal and log in with it.")


@app.get("/admin/logout")
def admin_logout():
    return HTMLResponse(
        "<div style='font-family:Arial;max-width:420px;margin:14vh auto;"
        "text-align:center;color:#4a4a4a;'><h3>Logged out</h3>"
        "<p>You can close this tab. Visiting the admin page again will ask "
        "for the login.</p></div>",
        status_code=401, headers={"WWW-Authenticate": 'Basic realm="dolce"'})


@app.get("/admin")
def admin_form(user: str = Depends(_admin), brand: str = "dolce",
               archived: int = 0):
    if brand not in ("dolce", "polished", "core"):
        brand = "dolce"
    return _render_admin(title=f"New campaign - {BRAND_TITLES[brand]}", brand=brand,
                         show_archived=bool(archived))


@app.get("/admin/edit/{cid}")
def admin_edit_form(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT * FROM campaigns WHERE id=?", (cid,)).fetchone()
    if not r or r["status"] not in ("draft", "pending", "approved"):
        return _page("Sent campaigns can't be edited - open the campaign and use "
                     "Duplicate instead.")
    keys = r.keys()
    aud = (r["audience"] if "audience" in keys else "all") or "all"
    vals = {"name": r["name"], "subject": r["subject"],
            "heading": r["heading"] or "", "body": r["body_raw"] or "",
            "audience": aud,
            "schedule_local": _sched_to_local(
                r["scheduled_at"] if "scheduled_at" in keys else None)}
    return _render_admin(action=f"/admin/edit/{cid}",
                         title=f"Edit campaign - {BRAND_TITLES.get(aud, aud)}",
                         button="SAVE &amp; RESEND FOR APPROVAL", values=vals,
                         brand=aud)


@app.post("/admin/edit/{cid}")
def admin_edit(cid: int, user: str = Depends(_admin), name: str = Form(...),
               subject: str = Form(...), heading: str = Form(...),
               body: str = Form(...), audience: str = Form("all"),
               return_action: str = Form(None), schedule_local: str = Form("")):
    try:
        stayed_draft = campaigns.update_campaign(
            cid, name, subject, _campaign_html(heading, body), heading, body,
            audience=audience, scheduled_at=_sched_to_utc(schedule_local))
    except ValueError as e:
        return _page(str(e))
    if stayed_draft:
        return _page(f"Draft <b>{html_mod.escape(name)}</b> updated. Still a draft - "
                     "no emails sent. Submit it for approval when ready.")
    return _page(f"Campaign <b>{html_mod.escape(name)}</b> updated and paused for "
                 f"re-approval. A fresh test copy and approval email are on their way "
                 f"to {config.APPROVER_EMAIL}; the previous approval links no longer "
                 "work. Anyone who already received it will NOT get it again - after "
                 "you approve, sending resumes with the new version for the rest.")


@app.get("/admin/view/{cid}")
def admin_view(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT * FROM campaigns WHERE id=?", (cid,)).fetchone()
    if not r:
        return _page("Campaign not found.")
    keys = r.keys()
    aud = (r["audience"] if "audience" in keys else "all") or "all"
    preview_html = render.render(r["html"], {"first_name": "Maya",
                                             "unsub_token": "preview"})
    m = re.search(r"<body[^>]*>(.*)</body>", preview_html, re.S)
    inner = m.group(1) if m else preview_html
    st = r["status"]
    with db.connect() as con:
        recipients = con.execute(
            """SELECT s.sent_at, c.first_name, c.email FROM sends s
               LEFT JOIN contacts c ON c.wix_id = s.wix_id
               WHERE s.kind = ? ORDER BY s.sent_at""",
            (f"campaign:{cid}",)).fetchall()
        planned = len(db.eligible_contacts(con, aud)) if st in ("pending", "approved") else None
    n_sent = len(recipients)
    if recipients:
        rec_rows = "".join(
            f"<div style='display:flex;justify-content:space-between;gap:10px;"
            f"padding:7px 0;border-bottom:1px solid var(--line);font-size:13.5px;'>"
            f"<span>{html_mod.escape(rc['first_name'] or '')}</span>"
            f"<span style='color:var(--faint)'>{html_mod.escape(rc['email'] or 'contact removed')}</span>"
            f"<span style='color:var(--faint);white-space:nowrap'>{(rc['sent_at'] or '')[:16]}</span></div>"
            for rc in recipients)
        delivery = (f"<details style='margin-top:14px;'><summary style='cursor:pointer;"
                    f"color:var(--gold);font-size:14px;'>Sent to {n_sent} client(s) - "
                    f"see who</summary><div style='margin-top:10px;'>{rec_rows}</div></details>")
    else:
        delivery = ""
    sched_line = ""
    sl = _sched_to_local(r["scheduled_at"] if "scheduled_at" in keys else None)
    if sl and st in ("draft", "pending", "approved"):
        sched_line = (f"<p style='font-size:13.5px;color:var(--faint);margin:10px 0 0;'>"
                      f"Scheduled send: {sl.replace('T', ' ')} (Erbil time)</p>")
    if planned is not None:
        remaining = planned - n_sent
        plan_line = (f"<p style='font-size:13.5px;color:var(--faint);margin:10px 0 0;'>"
                     f"Audience: {planned} consented client(s)"
                     + (f" &middot; {n_sent} already sent, {remaining} remaining"
                        if n_sent else "") + "</p>")
    else:
        plan_line = ""
    btn = ("display:inline-block;padding:10px 22px;border-radius:8px;"
           "text-decoration:none;font-size:13px;letter-spacing:1px;")
    acts = []
    if st in ("draft", "pending", "approved"):
        acts.append(f"<a href='/admin/edit/{cid}' style='{btn}background:#c2a273;"
                    f"color:#fff;'>EDIT</a>")
    if st == "draft":
        acts.append(f"<form method='post' action='/admin/submit/{cid}' "
                    f"style='display:inline'><button style='{btn}background:#5aa860;"
                    f"color:#fff;border:0;cursor:pointer;'>SUBMIT FOR APPROVAL"
                    f"</button></form>")
    if st == "approved":
        acts.append(f"<form method='post' action='/admin/cancel/{cid}' "
                    f"style='display:inline'><button style='{btn}background:#c96060;"
                    f"color:#fff;border:0;cursor:pointer;'>CANCEL SEND</button></form>")
    acts.append(f"<a href='/admin/duplicate/{cid}' style='{btn}background:transparent;"
                f"border:1px solid #c2a273;color:#c2a273;'>DUPLICATE</a>")
    if st == "sent":
        arch = bool(r["archived"]) if "archived" in keys else False
        verb = "unarchive" if arch else "archive"
        acts.append(f"<form method='post' action='/admin/{verb}/{cid}' "
                    f"style='display:inline'><button style='{btn}background:transparent;"
                    f"border:1px solid #a08d63;color:#a08d63;cursor:pointer;'>"
                    f"{verb.upper()}</button></form>")
    note = ""
    if st == "sent":
        note = ("<p style='color:#a99a9c;font-size:12.5px;'>Sent campaigns are kept "
                "as history and can't be edited - use Duplicate to reuse it as a "
                "new draft.</p>")
    fg = STATUS_COLORS.get(st, "#8a8a8a")
    return HTMLResponse(f"""
<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{html_mod.escape(r['name'])}</title>
<link rel='icon' type='image/png' href='/static/dolce-logo.png'>
<style>
  :root{{--page:#f5eff0;--card:#fff;--ink:#2b2b2b;--body:#4a4a4a;--gold:#c2a273;
        --faint:#a99a9c;--line:#ead9dc;}}
  @media (prefers-color-scheme: dark){{
    :root{{--page:#191516;--card:#231e1f;--ink:#f0e9e6;--body:#cfc5c2;
          --gold:#d0b285;--faint:#877b7d;--line:#3a3132;}}}}
  body{{margin:0;background:var(--page);font-family:Arial,sans-serif;color:var(--body);}}
</style>
<body>
  <div style="max-width:660px;margin:30px auto;padding:0 14px;">
    <p><a href="/admin" style="color:var(--gold);text-decoration:none;
       font-size:13px;">&larr; Back to campaigns</a></p>
    <div style="background:var(--card);border-radius:12px;padding:26px 30px;">
      <h1 style="font-family:Georgia,serif;font-weight:normal;font-size:23px;
          color:var(--ink);margin:0 0 6px;">{html_mod.escape(r['name'])}</h1>
      <p style="font-size:13.5px;color:var(--faint);margin:0 0 18px;">
        Subject: {html_mod.escape(r['subject'])} &nbsp;&middot;&nbsp;
        <span style="color:{fg};text-transform:uppercase;font-size:11px;
        letter-spacing:1px;border:1px solid currentColor;border-radius:999px;
        padding:3px 10px;">{st}</span> &nbsp;&middot;&nbsp; {r['created_at'][:16]}</p>
      <p style="margin:0 0 8px;">{''.join(acts)}</p>
      {note}{sched_line}{plan_line}{delivery}
    </div>
    <p style="font-family:Georgia,serif;color:var(--ink);font-size:16px;
       margin:24px 0 8px;">How it looks to clients:</p>
    <div style="border:1px solid var(--line);border-radius:10px;overflow:hidden;
         background:#f5eff0;">{inner}</div>
  </div>
</body>""")


@app.get("/admin/duplicate/{cid}")
def admin_duplicate(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT * FROM campaigns WHERE id=?", (cid,)).fetchone()
    if not r:
        return _page("Campaign not found.")
    keys = r.keys()
    aud = (r["audience"] if "audience" in keys else "all") or "all"
    vals = {"name": f"{r['name']} (copy)", "subject": r["subject"],
            "heading": (r["heading"] if "heading" in keys else "") or "",
            "body": (r["body_raw"] if "body_raw" in keys else "") or "",
            "audience": aud}
    return _render_admin(action="/admin/create", title="Duplicate campaign",
                         button="CREATE CAMPAIGN", values=vals, brand=aud)


@app.post("/admin/delete/{cid}")
def admin_delete(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT status, name FROM campaigns WHERE id=?", (cid,)).fetchone()
        if not r:
            return _page("Campaign not found.")
        if r["status"] not in ("draft", "pending", "rejected"):
            return _page("Sent campaigns stay in the history and approved ones must be "
                         "cancelled first.")
        con.execute("DELETE FROM campaigns WHERE id=?", (cid,))
    return _page(f"Campaign <b>{html_mod.escape(r['name'])}</b> deleted. Nothing was sent.")


@app.post("/admin/archive/{cid}")
def admin_archive(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT status, name FROM campaigns WHERE id=?",
                        (cid,)).fetchone()
        if not r or r["status"] != "sent":
            return _page("Only sent campaigns can be archived.")
        con.execute("UPDATE campaigns SET archived=1 WHERE id=?", (cid,))
    return _page(f"<b>{html_mod.escape(r['name'])}</b> archived - hidden from the "
                 "recent list, kept in history. Find it under 'archived' on the "
                 "campaigns page.")


@app.post("/admin/unarchive/{cid}")
def admin_unarchive(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT name FROM campaigns WHERE id=?", (cid,)).fetchone()
        if not r:
            return _page("Campaign not found.")
        con.execute("UPDATE campaigns SET archived=0 WHERE id=?", (cid,))
    return _page(f"<b>{html_mod.escape(r['name'])}</b> restored to the recent list.")


@app.post("/admin/cancel/{cid}")
def admin_cancel(cid: int, user: str = Depends(_admin)):
    with db.connect() as con:
        r = con.execute("SELECT status, name FROM campaigns WHERE id=?", (cid,)).fetchone()
        if not r or r["status"] != "approved":
            return _page("Only approved-but-not-yet-sent campaigns can be cancelled.")
        con.execute("UPDATE campaigns SET status='rejected' WHERE id=?", (cid,))
    return _page(f"Campaign <b>{html_mod.escape(r['name'])}</b> cancelled before sending.")


from datetime import datetime as _dt, timedelta as _td


def _sched_to_utc(schedule_local: str | None) -> str | None:
    """Erbil local (UTC+3, no DST) datetime-local value -> UTC ISO, or None."""
    if not schedule_local:
        return None
    try:
        return (_dt.fromisoformat(schedule_local) - _td(hours=3)).strftime(
            "%Y-%m-%dT%H:%M:00")
    except ValueError:
        return None


def _sched_to_local(scheduled_at: str | None) -> str:
    if not scheduled_at:
        return ""
    try:
        return (_dt.fromisoformat(scheduled_at) + _td(hours=3)).strftime(
            "%Y-%m-%dT%H:%M")
    except ValueError:
        return ""


def _safe_return_action(action: str) -> str:
    if action == "/admin/create" or re.fullmatch(r"/admin/edit/\d+", action or ""):
        return action
    return "/admin/create"


def _hidden_fields(name, subject, heading, body, audience, return_action,
                   schedule_local=""):
    f = ""
    for k, v in (("name", name), ("subject", subject), ("heading", heading),
                 ("body", body), ("audience", audience),
                 ("return_action", return_action),
                 ("schedule_local", schedule_local)):
        f += (f"<input type='hidden' name='{k}' "
              f"value=\"{html_mod.escape(v or '', quote=True)}\">")
    return f


@app.post("/admin/preview")
def admin_preview(user: str = Depends(_admin), name: str = Form(...),
                  subject: str = Form(...), heading: str = Form(...),
                  body: str = Form(...), audience: str = Form("dolce"),
                  return_action: str = Form("/admin/create"),
                  schedule_local: str = Form("")):
    return_action = _safe_return_action(return_action)
    sample = {"first_name": "Maya", "unsub_token": "preview"}
    preview_html = render.render(_campaign_html(heading, body), sample)
    m = re.search(r"<body[^>]*>(.*)</body>", preview_html, re.S)
    inner = m.group(1) if m else preview_html
    subject_display = render.render(subject, sample) if "{{" in subject else subject
    confirm_label = ("LOOKS GOOD - CREATE" if return_action == "/admin/create"
                     else "LOOKS GOOD - SAVE")
    hidden = _hidden_fields(name, subject, heading, body, audience, return_action,
                            schedule_local)
    btn = ("padding:14px 26px;border-radius:8px;font-size:14px;letter-spacing:1px;"
           "cursor:pointer;")
    return HTMLResponse(f"""
<!doctype html><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Preview - {html_mod.escape(name)}</title>
<link rel='icon' type='image/png' href='/static/dolce-logo.png'>
<style>
  :root{{--page:#f5eff0;--card:#fff;--ink:#2b2b2b;--body:#4a4a4a;--gold:#c2a273;
        --faint:#a99a9c;--line:#ead9dc;}}
  @media (prefers-color-scheme: dark){{
    :root{{--page:#191516;--card:#231e1f;--ink:#f0e9e6;--body:#cfc5c2;
          --gold:#d0b285;--faint:#877b7d;--line:#3a3132;}}}}
  body{{margin:0;background:var(--page);font-family:Arial,sans-serif;color:var(--body);}}
</style>
<body>
  <div style="max-width:700px;margin:30px auto;padding:0 14px;">
    <p style="margin:0 0 12px;"><a href="/admin" style="color:var(--gold);
       text-decoration:none;font-size:13px;">&larr; Home - campaigns</a>
       <span style="font-size:12px;color:var(--faint);">(leaving discards this
       unsaved draft - use Keep editing to go back with your text)</span></p>
    <div style="background:var(--card);border-radius:12px;padding:22px 26px;">
      <h1 style="font-family:Georgia,serif;font-weight:normal;font-size:21px;
          color:var(--ink);margin:0 0 4px;">Preview - nothing is created yet</h1>
      <p style="font-size:13.5px;color:var(--faint);margin:0 0 16px;">
        Subject: {html_mod.escape(subject_display)}</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <form method="post" action="/admin/compose" style="margin:0;">{hidden}
          <button style="{btn}background:transparent;border:1px solid var(--gold);
            color:var(--gold);">KEEP EDITING</button></form>
        <form method="post" action="{return_action}" style="margin:0;">{hidden}
          <button style="{btn}background:var(--gold);border:0;color:#fff;">
            {confirm_label}</button></form>
      </div>
    </div>
    <p style="font-family:Georgia,serif;color:var(--ink);font-size:16px;
       margin:22px 0 8px;">How it will look to clients:</p>
    <div style="border:1px solid var(--line);border-radius:10px;overflow:hidden;
         background:#f5eff0;">{inner}</div>
  </div>
</body>""")


@app.post("/admin/compose")
def admin_compose(user: str = Depends(_admin), name: str = Form(...),
                  subject: str = Form(...), heading: str = Form(...),
                  body: str = Form(...), audience: str = Form("dolce"),
                  return_action: str = Form("/admin/create"),
                  schedule_local: str = Form("")):
    return_action = _safe_return_action(return_action)
    title = "New campaign" if return_action == "/admin/create" else "Edit campaign"
    button = "CREATE CAMPAIGN" if return_action == "/admin/create" else "SAVE &amp; RESEND FOR APPROVAL"
    vals = {"name": name, "subject": subject, "heading": heading,
            "body": body, "audience": audience, "schedule_local": schedule_local}
    brand = audience if audience in ("dolce", "polished", "core") else "dolce"
    return _render_admin(action=return_action, title=title, button=button,
                         values=vals, brand=brand)


@app.post("/admin/create")
def admin_create(user: str = Depends(_admin), name: str = Form(...),
                 subject: str = Form(...), heading: str = Form(...),
                 body: str = Form(...), audience: str = Form("all"),
                 return_action: str = Form(None), schedule_local: str = Form("")):
    campaigns.create_from_html(name, subject, _campaign_html(heading, body),
                               heading=heading, body_raw=body, audience=audience,
                               scheduled_at=_sched_to_utc(schedule_local))
    extra = (" It is scheduled - after approval it waits for the send time."
             if schedule_local else "")
    return _page(f"Your campaign <b>{html_mod.escape(name)}</b> is created.<br><br>"
                 f"Now check <b>{config.APPROVER_EMAIL}</b> - the approval email is on its "
                 f"way. Nothing sends until you press Approve there.{extra}")


@app.post("/admin/draft")
def admin_draft(user: str = Depends(_admin), name: str = Form(...),
                subject: str = Form(...), heading: str = Form(...),
                body: str = Form(...), audience: str = Form("all"),
                return_action: str = Form(None), schedule_local: str = Form("")):
    campaigns.create_from_html(name, subject, _campaign_html(heading, body),
                               heading=heading, body_raw=body, audience=audience,
                               as_draft=True,
                               scheduled_at=_sched_to_utc(schedule_local))
    return _page(f"Draft <b>{html_mod.escape(name)}</b> saved. No emails were sent - "
                 "find it under Recent campaigns to keep editing, or press "
                 "'submit for approval' when it's ready.")


@app.post("/admin/submit/{cid}")
def admin_submit(cid: int, user: str = Depends(_admin)):
    try:
        campaigns.submit_draft(cid)
    except ValueError as e:
        return _page(str(e))
    return _page(f"Submitted. Check <b>{config.APPROVER_EMAIL}</b> for the test copy "
                 "and the approval email - nothing sends until Approve is pressed.")
