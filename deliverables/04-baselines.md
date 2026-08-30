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
