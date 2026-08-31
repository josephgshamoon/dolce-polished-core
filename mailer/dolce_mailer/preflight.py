"""Pre-send safety checks. Sending is refused when they fail, so a
misconfigured APP_BASE_URL or a down web endpoint can never produce a batch
of emails with broken images or dead unsubscribe links."""
import httpx

from . import config


def check():
    base = config.APP_BASE_URL
    if "example" in base or not base.startswith("https://"):
        raise SystemExit(
            f"PREFLIGHT FAILED: APP_BASE_URL is '{base}' - still a placeholder "
            "or not https. Fix .env before sending.")
    for name in ("dolce-logo.png", "polished-logo.png", "core-logo.png",
                 "core-logo-dark.png"):
        url = f"{base}/static/{name}"
        try:
            r = httpx.get(url, timeout=15, follow_redirects=True)
        except Exception as e:
            raise SystemExit(
                f"PREFLIGHT FAILED: cannot fetch {url} ({e}). The web service or "
                "nginx is down - emails would carry broken images. Fix, then rerun.")
        ct = r.headers.get("content-type", "")
        if r.status_code != 200 or not ct.startswith("image/"):
            raise SystemExit(
                f"PREFLIGHT FAILED: {url} returned {r.status_code} ({ct or 'no type'}). "
                "Emails would carry broken images. Fix, then rerun.")
    print("preflight ok: all brand logos serving")
