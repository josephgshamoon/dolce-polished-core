"""Merge-field rendering and automatic-template assembly."""
import html as html_mod
from pathlib import Path

from . import config

TPL_DIR = Path(__file__).parent / "templates"
AUTO_FILES = {"welcome:dolce": "welcome-dolce.html",
              "welcome:polished": "welcome-polished.html",
              "welcome:core": "welcome-core.html",
              "birthday": "birthday.html"}


def paragraphs_to_html(body: str) -> str:
    paragraphs = [html_mod.escape(p.strip()).replace("\n", "<br>")
                  for p in body.replace("\r", "").split("\n\n") if p.strip()]
    return "<br><br>\n".join(paragraphs)


def render_auto(key: str):
    """Return (subject, html_template) for an automatic email: the design shell
    from disk, with the owner-editable subject/heading/body from the database.
    Escaped body text keeps {{first_name}} intact for per-recipient rendering."""
    from . import db
    with db.connect() as con:
        row = con.execute("SELECT * FROM auto_templates WHERE key=?",
                          (key,)).fetchone()
    shell = (TPL_DIR / AUTO_FILES[key]).read_text()
    if not row:
        raise RuntimeError(f"auto template '{key}' missing - run: python -m dolce_mailer.db")
    html = (shell.replace("{{heading}}", html_mod.escape(row["heading"]))
                 .replace("{{body}}", paragraphs_to_html(row["body_raw"])))
    return row["subject"], html


def render(html: str, contact) -> str:
    first = (contact["first_name"] or "").strip() or "there"
    unsub = f"{config.APP_BASE_URL}/unsubscribe/{contact['unsub_token']}"
    logo = f"{config.APP_BASE_URL}/static/dolce-logo.png?v=2"
    return (html.replace("{{first_name}}", first)
                .replace("{{unsubscribe_url}}", unsub)
                .replace("{{logo_url}}", logo))
