"""Pull contacts from the Wix Contacts API into the local database.

Wix remains the master client list; this service only mirrors it.
Consent = the contact carries the CONSENT_LABEL in Wix.
"""
import httpx

from . import config, db

API = "https://www.wixapis.com/contacts/v4/contacts"


def _headers():
    return {
        "Authorization": config.WIX_API_KEY,
        "wix-site-id": config.WIX_SITE_ID,
        "Content-Type": "application/json",
    }


def fetch_all():
    contacts, cursor = [], None
    with httpx.Client(timeout=30) as client:
        while True:
            params = {"paging.limit": 100}
            if cursor:
                params["paging.cursor"] = cursor
            r = client.get(API, headers=_headers(), params=params)
            r.raise_for_status()
            data = r.json()
            contacts += data.get("contacts", [])
            cursor = data.get("pagingMetadata", {}).get("cursors", {}).get("next")
            if not cursor:
                return contacts


def upsert(raw_contacts):
    added = 0
    with db.connect() as con:
        for c in raw_contacts:
            info = c.get("info", {})
            emails = info.get("emails", {}).get("items", [])
            email = next((e if isinstance(e, str) else e.get("email")
                          for e in emails if e), None)
            if not email:
                continue
            first = (info.get("name") or {}).get("first", "") or ""
            last = (info.get("name") or {}).get("last", "") or ""
            raw_labels = info.get("labelKeys", {}).get("items", [])
            labels = [l if isinstance(l, str) else l.get("key", "") for l in raw_labels]
            birthday = info.get("birthdate", "") or ""
            consented = int(any(config.CONSENT_LABEL in l for l in labels))
            row = con.execute(
                "SELECT wix_id FROM contacts WHERE wix_id = ?", (c["id"],)
            ).fetchone()
            if row:
                con.execute(
                    """UPDATE contacts SET email=?, first_name=?, last_name=?,
                       labels=?, birthday=?, consented=? WHERE wix_id=?""",
                    (email, first, last, ",".join(labels), birthday, consented,
                     c["id"]),
                )
            else:
                con.execute(
                    """INSERT INTO contacts
                       (wix_id, email, first_name, last_name, labels, birthday,
                        consented, unsub_token)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (c["id"], email, first, last, ",".join(labels), birthday,
                     consented, db.new_token()),
                )
                added += 1
    return added


def run():
    added = upsert(fetch_all())
    print(f"sync complete, {added} new contact(s)")


if __name__ == "__main__":
    run()
