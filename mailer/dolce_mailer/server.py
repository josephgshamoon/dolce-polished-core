"""Web endpoints: campaign approve/reject, one-click unsubscribe, Brevo webhook."""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from . import db

app = FastAPI(title="Dolce Mailer")


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
