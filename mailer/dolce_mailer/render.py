"""Merge-field rendering and automatic-template assembly."""
import html as html_mod
from pathlib import Path

from . import config

TPL_DIR = Path(__file__).parent / "templates"
AUTO_FILES = {"welcome:dolce": "welcome-dolce.html",
              "welcome:polished": "welcome-polished.html",
              "welcome:core": "welcome-core.html",
              "birthday:dolce": "birthday.html",
              "birthday:polished": "birthday-polished.html",
              "birthday:core": "birthday-core.html"}


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


def render(html: str, contact, plain: bool = False) -> str:
    """Merge contact fields into html (or, with plain=True, into a plain-text
    string such as a subject line, where HTML-escaping must not apply)."""
    first = (contact["first_name"] or "").strip() or "there"
    if not plain:
        first = html_mod.escape(first)
    unsub = f"{config.APP_BASE_URL}/unsubscribe/{contact['unsub_token']}"
    base = config.APP_BASE_URL
    return (html.replace("{{first_name}}", first)
                .replace("{{unsubscribe_url}}", unsub)
                .replace("{{logo_url}}", f"{base}/static/dolce-logo.png?v=2")
                .replace("{{logo_url_polished}}", f"{base}/static/polished-logo.png")
                .replace("{{logo_url_core_dark}}", f"{base}/static/core-logo-dark.png?v=3")
                .replace("{{logo_url_core}}", f"{base}/static/core-logo.png"))
