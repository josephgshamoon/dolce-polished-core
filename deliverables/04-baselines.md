# Week-1 baselines — recorded 30 August 2026

Source: Wix dashboard screenshot provided by client (last 30 days), plus live checks.

## Dolce (dolceclinic.com)
- Site sessions, 30 days: 217 (down 11%)
- Unique visitors, 30 days: 184 (down 15%)
- Clicks to contact, 30 days: 8 (down 33%) — the number the whole plan exists to move
- Queries on AI surfaces, 30 days: 636 (down 63%) — worth watching; AI answers appear to be a real discovery channel here
- Wix plan: Combo (paid) — GA4 connection should be available natively
- Business email: none connected (confirmed in dashboard)
- Wix Inbox: 39 unread messages — triage these; some may be booking enquiries
- Slug state at check time: /blank-1 … /blank-4 all still live (200), new slugs not yet created

## Core (coreyogapilatesstudio.com)
- To be measured once Search Console and GA4 are connected

## Milestone — 30 August 2026, sender infrastructure complete
- hello@dolceclinic.com live on Google Workspace Starter (purchased via Wix)
- Domain verified in Google Workspace; Gmail activated
- DNS confirmed live globally (checked externally): SPF, DKIM (google._domainkey),
  DMARC (p=none, rua to hello@), full Google MX set
- Test send hello@ -> jshamoon30@gmail.com: delivered to INBOX in 12s,
  SPF PASS / DKIM PASS (d=dolceclinic.com) / DMARC PASS
- Remaining for email launch: Wix Email Marketing test campaign (verify Wix-side
  sender auth), master template approval, Phoenix contact import with consent
  labels, welcome automation
- Still open from week 1: Search Console + Google Business Profile lookups under
  dolce.erbil@gmail.com

## Milestone - 30 August 2026, evening: custom mailer LIVE
- Self-hosted mailer on VPS (145.223.88.35) sent its first production emails:
  welcome_job: 2 welcome email(s) sent (test contacts Maya + Joseph)
- Transport: Google Workspace SMTP relay (IP-authenticated, TLS), from
  hello@dolceclinic.com. Brevo activation pending as future bulk transport.
- Full chain proven: Wix Contacts sync -> consent label gating -> once-only
  welcome -> first-name personalization -> authenticated delivery.

## Milestone - 30 August 2026, late evening: system COMPLETE end to end
- Root cause of missing logo: APP_BASE_URL placeholder never saved in .env;
  fixed, verified by new pre-send preflight (refuses to send if the asset
  URL is unreachable - wired into welcome, campaign, and birthday paths).
- Welcome email confirmed rendering with logo in Gmail.
- Full production stack live: nginx vhost + Let's Encrypt at
  mailer.dolceclinic.com, systemd service, Wix sync, consent gating,
  once-only welcome, personalization, unsubscribe endpoint.
- Remaining to switch on: cron entries; first campaign through the
  dolce.erbil@gmail.com approval flow.
- Still pending from client: Phoenix export; Search Console and
  business.google.com lookups; Brevo activation (future bulk transport).
