# Status and next steps - end of day, 30 August 2026

## What is live and running (no attention needed)
- hello@dolceclinic.com on Google Workspace; SPF/DKIM/DMARC all passing.
- Self-hosted mailer on the VPS (145.223.88.35), systemd + nginx + Let's
  Encrypt at mailer.dolceclinic.com, cron: welcomes every 15 min, campaign
  queue every 5 min, birthdays daily 07:00 UTC.
- Welcome automation proven on the production path (new contact -> labeled
  consented -> welcomed once, RGBA logo correct in Gmail light/dark).
- Owner portal at mailer.dolceclinic.com/admin (user maya): create / edit /
  delete / cancel campaigns, audience dropdown (all/dolce/polished/core),
  [TEST] copy + inline preview + Approve/Reject via dolce.erbil@gmail.com,
  upcoming-birthdays panel, light/dark theme, logout.
- Safety rails: consented-label gating, once-only sends (per contact AND per
  email), throttling (150/run), resumable campaigns, suppression via webhook,
  one-click unsubscribe, pre-send preflight (blocks sends if assets break).
- Current consented list: Joseph, Maya, Kawa (3). The other ~39 Wix contacts
  are unlabeled = unreachable by the system.

## Targeting model (final, live)
- TWO KEYS required for any send: `consented` (permission) + at least one
  brand label (`dolce`/`polished`/`core` = membership). consented alone
  sends NOTHING. Labels stack for multi-business clients.
- Portal tabs: Dolce (default, only tab with the logo) / Polished / Core.
  No Everyone tab - every campaign is brand-specific. Rows are clickable:
  view rendered email, edit (pending), cancel (approved), duplicate (any).
- Per-brand welcomes: welcome-dolce (approved, live), welcome-polished and
  welcome-core (drafts, inert until those brands have labeled clients;
  need owner approval first). Welcomes tracked per brand - joining a
  second brand later triggers that brand's welcome.
- Server deployed and current as of 30 Aug late night. SSH from overseas
  networks may block port 22 - the Hostinger browser console always works.
- Failure alerting: job crashes, per-send failures, portal errors email
  jshamoon30@gmail.com (same-subject alerts muted 6h).

## Tomorrow / next session
1. Maya reviews the 39 in Wix, unticks non-clients, then TWO bulk actions:
   Add Label `consented` AND Add Label `dolce` -> welcomes go out
   automatically. Check ~/dolce/mailer.log and the approval-count habit.
2. Phoenix export -> upload to the working session -> cleaned wave files
   (each wave labeled `consented` + `dolce`, birthdays YYYY-MM-DD)
   -> Wix imports with batch labels.
3. Maya, 10 min, logged in as dolce.erbil@gmail.com:
   - search.google.com/search-console : what properties exist?
   - business.google.com : what profiles exist?
   These two answers restart the ORIGINAL SEO plan (deliverable 02): GBP
   claiming, review programme, local search.
4. Maya marks the campaign email "Not junk" in Outlook + Safe Senders.

## Housekeeping (this week)
- VPS: disk at 86%; Ubuntu 25.10 is EOL -> upgrade to 26.04 LTS.
- Google app password for hello@ (backup transport) once the security delay
  clears; Brevo activation reply = future bulk transport (flip
  MAIL_TRANSPORT=brevo in mailer/.env when desired).
- Consider UptimeRobot on mailer.dolceclinic.com.

## Standing rules
- The `consented` label is a send button; staff apply it only with real consent.
- No purchased lists; unsubscribes honoured automatically; doctor sign-off on
  any content naming treatments with claims.
- The DELETE FROM sends test command is RETIRED - never run it again.
- Deliverability: warm subjects, no exclamation-mark offers; expect
  Promotions tab for marketing (normal); reputation improves with weeks of
  clean sending; tighten DMARC to quarantine after ~4 clean weeks.
