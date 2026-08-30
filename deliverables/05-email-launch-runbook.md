# Dolce email programme — launch runbook

Owner-account work is marked [OWNER]; everything else is Kaev via existing access.
Platform choice: Wix Email Marketing + Wix Automations (native, contacts already
live in Wix, no third-party sync to break). Revisit only if send volume or
segmentation outgrows it.

## Phase A — sender foundation [OWNER]
1. Wix Home -> "No business email" -> Connect -> buy hello@dolceclinic.com
   (Google Workspace, cheapest tier, 1 mailbox).
2. Sign into the new mailbox once so it is active.
3. Same sitting: record what exists at search.google.com/search-console and
   business.google.com under dolce.erbil@gmail.com.

## Phase B — authentication (Kaev, after A)
4. Confirm MX + SPF records Wix/Google set automatically.
5. Generate DKIM in Google Admin (Apps -> Google Workspace -> Gmail ->
   Authenticate email) and add the TXT record in the Wix domain DNS panel.
6. Add DMARC TXT: v=DMARC1; p=none; rua=mailto:hello@dolceclinic.com
   (tighten to quarantine after 4+ clean weeks).
7. If Wix Email Marketing offers custom-domain sender authentication for
   campaigns, complete it so campaigns send as dolceclinic.com, not via
   Wix shared identity. Exact panel name varies — the checkpoint is what
   matters: the test email must not show "via" a third-party domain.

## Phase C — the test send
8. Marketing -> Email Marketing -> new campaign.
   From name: Dolce Aesthetic Clinic. From/reply-to: hello@dolceclinic.com.
9. Send test to jshamoon30@gmail.com. In Gmail open it -> three-dot menu ->
   Show original -> confirm SPF: PASS, DKIM: PASS, DMARC: PASS, and that
   the from line has no "via" tag. Screenshot the result.
10. Only proceed to automation when all three pass.

## Phase D — master template (one layout for every email)
- Header: logo on white, nothing else.
- One message per email, 150 words max.
- One button: "Message us on WhatsApp" -> wa.me/9647509000200.
- Footer: Dolce Aesthetic Clinic, Park View, Erbil, Kurdistan Region, Iraq ·
  +964 750 900 0200 · unsubscribe link (Wix inserts automatically — verify
  it is present in the test).
- No prices in images, no before/after photos, no claims about results or
  safety. Any treatment mention: doctor sign-off before the campaign is scheduled.

### Welcome email draft (needs doctor sign-off if service names remain)
Subject: Welcome to Dolce
Hi {first name},
Thanks for joining the Dolce list. Once a month we'll share what's new at the
clinic in Park View — services, openings, and the occasional offer. When you
want to book or ask a question, just message us on WhatsApp and a real person
answers.
[Message us on WhatsApp]
Dolce Aesthetic Clinic · Park View, Erbil

## Phase E — contacts and automation
11. Import internal-platform clients into Wix Contacts with labels:
    source label (e.g. internal-platform) + consented / needs-repermission.
    No treatment data in any field.
12. Wix Automations: trigger = contact added with label "consented" (and all
    new signups) -> send welcome email. That is the only automation at launch.
13. needs-repermission contacts are NOT emailed. They get the one-time
    WhatsApp opt-in invite; a reply/signup moves them to consented.
14. Monthly campaign: drafted by Kaev, approved by client, sent manually to
    consented only. Add further automations (90-day win-back) after two clean
    monthly sends.

## Hard rules
- Consented contacts only, ever. One-click unsubscribe honoured within 24h.
- No purchased lists. No blast to the 5,000 before re-permission.
- Watch the first sends: if spam complaints or bounces spike, stop and review.
