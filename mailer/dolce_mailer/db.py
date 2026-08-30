import secrets
import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    wix_id      TEXT PRIMARY KEY,
    email       TEXT NOT NULL,
    first_name  TEXT DEFAULT '',
    labels      TEXT DEFAULT '',          -- comma-separated wix labels
    birthday    TEXT DEFAULT '',          -- YYYY-MM-DD if known
    consented   INTEGER DEFAULT 0,
    unsubscribed INTEGER DEFAULT 0,
    unsub_token TEXT NOT NULL,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sends (
    id          INTEGER PRIMARY KEY,
    wix_id      TEXT NOT NULL,
    kind        TEXT NOT NULL,            -- 'welcome' | 'birthday' | 'campaign:<id>'
    sent_at     TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wix_id, kind)
);
CREATE TABLE IF NOT EXISTS campaigns (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    subject     TEXT NOT NULL,
    html        TEXT NOT NULL,
    status      TEXT DEFAULT 'pending',   -- pending | approved | rejected | sent
    token       TEXT NOT NULL,            -- approval link token
    heading     TEXT DEFAULT '',
    body_raw    TEXT DEFAULT '',
    audience    TEXT DEFAULT 'all',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    decided_at  TEXT,
    sent_at     TEXT
);
CREATE TABLE IF NOT EXISTS suppression (
    email       TEXT PRIMARY KEY,
    reason      TEXT,                     -- bounce | complaint | manual
    added_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def connect():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init():
    with connect() as con:
        con.executescript(SCHEMA)
        cols = [r[1] for r in con.execute("PRAGMA table_info(campaigns)")]
        if "heading" not in cols:
            con.execute("ALTER TABLE campaigns ADD COLUMN heading TEXT DEFAULT ''")
            con.execute("ALTER TABLE campaigns ADD COLUMN body_raw TEXT DEFAULT ''")
        if "audience" not in cols:
            con.execute("ALTER TABLE campaigns ADD COLUMN audience TEXT DEFAULT 'all'")


def new_token():
    return secrets.token_urlsafe(24)


def eligible_contacts(con, audience="all"):
    """Contacts we are allowed to email: consented, not unsubscribed, not
    suppressed - optionally narrowed to a brand audience (a Wix label)."""
    rows = con.execute(
        """SELECT c.* FROM contacts c
           WHERE c.consented = 1 AND c.unsubscribed = 0
             AND c.email NOT IN (SELECT email FROM suppression)"""
    ).fetchall()
    if audience and audience != "all":
        rows = [r for r in rows if audience in (r["labels"] or "")]
    return rows


if __name__ == "__main__":
    init()
    print("database initialised")
