# Dolce Mailer - self-hosted lifecycle email service

Small VPS-hosted service that:
1. Syncs contacts (name, email, labels, birthday) from Wix Contacts on a schedule.
2. Sends the approved welcome template ONCE to each new contact labeled `consented`.
3. Runs campaigns (offers, birthdays, news): each campaign is drafted, then an
   approval email with Approve/Reject links goes to the approver
   (dolce.erbil@gmail.com). Only an approved campaign is sent to the list.
4. Handles unsubscribes (one-click, per-contact token) and a suppression list.

## Hard rules baked in
- Email is delivered via a transactional API (Brevo by default), NEVER via the
  VPS's own SMTP - a raw VPS IP has no reputation and lands in spam.
- Only contacts labeled `consented`, not unsubscribed, not suppressed, are ever
  emailed. The welcome sends at most once per contact (tracked in the sends table).
- Every outgoing email carries List-Unsubscribe headers (Gmail requires this
  for bulk senders) and a visible unsubscribe link.

## Deploy (Kaev)
1. Python 3.11+, `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env`, fill in:
   - WIX_API_KEY (scoped to Contacts read-only; deliver via password manager,
     never chat), WIX_SITE_ID (ac025ae4-2e2b-4897-896e-e82bdfefb96b)
   - BREVO_API_KEY (create free Brevo account; verify dolceclinic.com there and
     add its DKIM/SPF DNS records in Wix, same routine as Google's)
   - APP_BASE_URL (public HTTPS URL of this service for approve/unsubscribe links)
   - APPROVER_EMAIL=dolce.erbil@gmail.com, FROM_EMAIL=hello@dolceclinic.com
3. `python -m dolce_mailer.db` to create the SQLite database.
4. Run the web app (approval + unsubscribe endpoints) behind HTTPS:
   `uvicorn dolce_mailer.server:app --port 8080` (reverse-proxy with TLS).
5. Cron (see cron.example): sync+welcome every 15 min, campaign queue every
   5 min, birthdays daily.

## Creating a campaign
`python -m dolce_mailer.campaigns create --name "Sept offer" --subject "..." --html path.html`
-> stores draft, emails the approver a preview with Approve/Reject links.
Approved campaigns are picked up by the queue cron and sent to the eligible list.

## Status: SCAFFOLD for Kaev engineering review
Working structure and logic; before production: add error alerting, Brevo
bounce/complaint webhook wiring (endpoint exists), rate limiting on sends,
and a test pass against a seeded database. Birthday campaigns require a
birthday column in the Phoenix import (flagged to client).
