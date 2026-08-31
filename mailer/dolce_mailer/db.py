import secrets
import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    wix_id      TEXT PRIMARY KEY,
    email       TEXT NOT NULL,
    first_name  TEXT DEFAULT '',
    last_name   TEXT DEFAULT '',
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
    scheduled_at TEXT,            -- UTC ISO; approved campaigns wait for this
    archived    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    decided_at  TEXT,
    sent_at     TEXT
);
CREATE TABLE IF NOT EXISTS auto_templates (
    key         TEXT PRIMARY KEY,        -- welcome:dolce|welcome:polished|welcome:core|birthday
    subject     TEXT NOT NULL,
    heading     TEXT NOT NULL,
    body_raw    TEXT NOT NULL,           -- plain text, blank line = paragraph
    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS users (
    username    TEXT PRIMARY KEY,
    email       TEXT NOT NULL,
    pw_hash     TEXT NOT NULL,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reset_tokens (
    token       TEXT PRIMARY KEY,
    username    TEXT NOT NULL,
    expires     TEXT NOT NULL
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
        ccols = [r[1] for r in con.execute("PRAGMA table_info(contacts)")]
        if "last_name" not in ccols:
            con.execute("ALTER TABLE contacts ADD COLUMN last_name TEXT DEFAULT ''")
        cols = [r[1] for r in con.execute("PRAGMA table_info(campaigns)")]
        if "heading" not in cols:
            con.execute("ALTER TABLE campaigns ADD COLUMN heading TEXT DEFAULT ''")
            con.execute("ALTER TABLE campaigns ADD COLUMN body_raw TEXT DEFAULT ''")
        if "audience" not in cols:
            con.execute("ALTER TABLE campaigns ADD COLUMN audience TEXT DEFAULT 'all'")
        if "scheduled_at" not in cols:
            con.execute("ALTER TABLE campaigns ADD COLUMN scheduled_at TEXT")
        if "archived" not in cols:
            con.execute("ALTER TABLE campaigns ADD COLUMN archived INTEGER DEFAULT 0")
        con.execute("UPDATE sends SET kind='welcome:dolce' WHERE kind='welcome'")
        _seed_auto_templates(con)
        # bootstrap: seed the first portal user from the legacy env credential
        if not con.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            if config.ADMIN_PASSWORD:
                from . import users as _users
                con.execute(
                    "INSERT INTO users (username, email, pw_hash) VALUES (?,?,?)",
                    (config.ADMIN_USER.lower(), config.APPROVER_EMAIL,
                     _users.hash_pw(config.ADMIN_PASSWORD)))
                print(f"seeded portal user '{config.ADMIN_USER}' from .env password")


def new_token():
    return secrets.token_urlsafe(24)


BRAND_KEYS = ("dolce", "polished", "core")


def eligible_contacts(con, audience="all"):
    """Who can actually be emailed. Two keys are always required:
      1. consent  - the `consented` label (permission to contact at all)
      2. membership - at least one brand label (dolce/polished/core)
    `consented` alone sends NOTHING. audience="all" means everyone who
    belongs to at least one brand; a brand audience narrows to that brand."""
    rows = con.execute(
        """SELECT c.* FROM contacts c
           WHERE c.consented = 1 AND c.unsubscribed = 0
             AND c.email NOT IN (SELECT email FROM suppression)"""
    ).fetchall()
    if audience and audience != "all":
        return [r for r in rows if audience in (r["labels"] or "")]
    return [r for r in rows
            if any(b in (r["labels"] or "") for b in BRAND_KEYS)]


AUTO_SEEDS = {
    "welcome:dolce": ("Welcome to Dolce", "Welcome to Dolce",
        "Welcome to Dolce. We're so happy to have you with us.\n\n"
        "We'll be sharing what's new at Dolce Aesthetic Clinic - from new treatments "
        "and services to clinic updates, special events, and exclusive offers created "
        "for our clients.\n\n"
        "Whether you're looking to refresh your skin, explore a new treatment, or "
        "simply have a question, our team is always here to help.\n\n"
        "Ready to book or have a question?\n"
        "Message us on WhatsApp and our team will be happy to assist you."),
    "welcome:polished": ("Welcome to Polished", "Welcome to Polished",
        "Welcome to Polished. We're so happy to have you with us.\n\n"
        "We'll be sharing what's new at Polished by Dolce Salon - from hair, nails "
        "and beauty services to salon updates, special events, and exclusive offers "
        "created for our clients.\n\n"
        "Whether you're booking your next appointment or simply have a question, "
        "our team is always here to help.\n\n"
        "Ready to book or have a question?\n"
        "Message us on WhatsApp and our team will be happy to assist you."),
    "welcome:core": ("Welcome to Core", "Welcome to Core",
        "Welcome to Core. We're so happy to have you with us.\n\n"
        "We'll be sharing what's new at Core Yoga & Pilates Studio - from classes "
        "and schedules to studio updates, special events, and exclusive offers "
        "created for our members.\n\n"
        "Whether you're booking your next class or simply have a question, our team "
        "is always here to help.\n\n"
        "Ready to book or have a question?\n"
        "Message us on WhatsApp and our team will be happy to assist you."),
    "birthday:dolce": ("Happy birthday from Dolce", "Happy birthday, {{first_name}}!",
        "All of us at Dolce wish you a wonderful birthday and a beautiful year "
        "ahead.\n\n"
        "Thank you for being part of the Dolce family - we look forward to seeing "
        "you at the clinic soon."),
    "birthday:polished": ("Happy birthday from Polished", "Happy birthday, {{first_name}}!",
        "All of us at Polished wish you a wonderful birthday and a beautiful year "
        "ahead.\n\n"
        "Thank you for being part of the Polished family - we look forward to "
        "seeing you at the salon soon."),
    "birthday:core": ("Happy birthday from Core", "Happy birthday, {{first_name}}!",
        "All of us at Core wish you a wonderful birthday and a wonderful year "
        "ahead.\n\n"
        "Thank you for being part of the Core family - we look forward to seeing "
        "you at the studio soon."),
}


def _seed_auto_templates(con):
    # one-time migration: the old single 'birthday' copy becomes the Dolce one,
    # keeping any edits made in the portal
    old = con.execute("SELECT * FROM auto_templates WHERE key='birthday'").fetchone()
    if old:
        con.execute("INSERT OR IGNORE INTO auto_templates "
                    "(key, subject, heading, body_raw) VALUES (?,?,?,?)",
                    ("birthday:dolce", old["subject"], old["heading"],
                     old["body_raw"]))
        con.execute("DELETE FROM auto_templates WHERE key='birthday'")
    for key, (subject, heading, body) in AUTO_SEEDS.items():
        con.execute("INSERT OR IGNORE INTO auto_templates "
                    "(key, subject, heading, body_raw) VALUES (?,?,?,?)",
                    (key, subject, heading, body))


if __name__ == "__main__":
    init()
    print("database initialised")

