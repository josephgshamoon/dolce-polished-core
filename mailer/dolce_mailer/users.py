"""Portal user accounts: salted PBKDF2 password hashes in SQLite.

CLI:
  python -m dolce_mailer.users add <username> <email>      (prints a generated password once)
  python -m dolce_mailer.users set-password <username>     (prompts; or pass --password)
  python -m dolce_mailer.users list
"""
import argparse
import getpass
import hashlib
import os
import secrets

from . import db

_ITER = 240_000


def hash_pw(pw: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, _ITER)
    return salt.hex() + "$" + h.hex()


def verify(pw: str, stored: str) -> bool:
    try:
        salt_hex, h_hex = stored.split("$")
        h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt_hex), _ITER)
        return secrets.compare_digest(h.hex(), h_hex)
    except Exception:
        return False


def get(username: str):
    with db.connect() as con:
        return con.execute("SELECT * FROM users WHERE username=?",
                           (username.lower().strip(),)).fetchone()


def add(username: str, email: str, password: str | None = None) -> str:
    pw = password or secrets.token_urlsafe(9)
    with db.connect() as con:
        con.execute("INSERT OR REPLACE INTO users (username, email, pw_hash) "
                    "VALUES (?,?,?)", (username.lower().strip(), email, hash_pw(pw)))
    return pw


def set_password(username: str, pw: str) -> bool:
    with db.connect() as con:
        cur = con.execute("UPDATE users SET pw_hash=? WHERE username=?",
                          (hash_pw(pw), username.lower().strip()))
        return cur.rowcount > 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("username"); a.add_argument("email")
    sp = sub.add_parser("set-password"); sp.add_argument("username")
    sp.add_argument("--password")
    sub.add_parser("list")
    args = p.parse_args()
    if args.cmd == "add":
        pw = add(args.username, args.email)
        print(f"user '{args.username}' created. TEMPORARY PASSWORD (share once, "
              f"have them change it on the portal): {pw}")
    elif args.cmd == "set-password":
        pw = args.password or getpass.getpass("new password: ")
        print("updated" if set_password(args.username, pw) else "no such user")
    else:
        with db.connect() as con:
            for r in con.execute("SELECT username, email, created_at FROM users"):
                print(dict(r))
