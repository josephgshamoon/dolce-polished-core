# Dolce / Polished / Core — Response 2: The full plan

Prepared by Kaev, 30 August 2026. This plan proceeds on the assumptions stated in Response 1: no verified Google Business Profiles, no GA4, contacts unconsented and scattered, bookings via Instagram/WhatsApp, no email platform, English first, one person at ~4 hours/week, no budget beyond free tiers. Anything that depends on an assumption is marked **conditional**. Every action carries: owner · effort · platform dependency · expected outcome, and a confidence tag — **verified** (we saw it), **standard practice** (how these platforms normally behave), or **needs testing** (confirm before relying on it).

Two owners appear throughout: **Kaev** (us) and **Client** (your one person, ~4h/week). Where an action mentions a medical claim, the page or message needs **doctor sign-off** before publishing — these are flagged.

---

## 1. Technical foundation

### Search Console and GA4 ownership

- **Recover or re-establish Dolce Search Console.** A verification tag is on the site (verified), so a property likely exists. Try "request access" from a Google account you control; if the owner is unreachable, add a new verification via Wix's SEO dashboard or a DNS TXT record on dolceclinic.com and verify a fresh property — Google allows multiple owners. *Kaev · 1h · Wix native, free · Outcome: you own your own search data · standard practice.*
- **Create Search Console for Core.** Verify by DNS TXT record on coreyogapilatesstudio.com (cleanest) or a meta tag in the Shopify theme. Submit the sitemap. *Kaev · 30m · Shopify native, free · standard practice.*
- **GA4 on both sites.** Shopify: install the free Google & YouTube channel app and connect a GA4 property — native, free. Wix: connecting Google Analytics requires a Wix premium plan with a connected domain; the site runs on its own domain so this is probably already the case — **needs testing** in week 1. Create one GA4 account, two properties (one per site). *Kaev · 2h · Shopify native free; Wix likely native on existing paid plan · Outcome: baseline traffic numbers exist for the first monthly report.*

### Sitemaps, robots, indexing

- Both robots.txt files and sitemaps are healthy platform defaults (**verified**). No action beyond submitting both sitemaps in Search Console and, in week 1, recording how many of each site's five pages Google has indexed. Current index status: **to be measured in week 1**.

### Fix list — Dolce (Wix)

All native Wix, no apps, no code, no extra cost (standard practice) unless noted.

1. **Rename the four blank slugs.** `/blank-4` → `/dermatology-non-invasive`, `/blank-2` → `/plastic-surgery`, `/blank-3` → `/wellness`, `/blank-1` → `/contact`. Wix offers an automatic 301 redirect when a slug changes — accept it every time so nothing breaks. *Kaev · 1h · Outcome: URLs that say what the page is, to Google and to anyone reading a link.*
2. **Write a unique title and meta description per page.** Pattern: "Service | Dolce Aesthetic Clinic | Erbil" plus a 150-character description naming the service and the location. The home page has a title but no description (**verified**). Draft: Kaev; **doctor sign-off** on any wording about procedures. *Kaev + Client · 2h.*
3. **Header hierarchy.** One H1 per page naming the service ("Dermatology & Non-Invasive Treatments in Erbil"), H2s per treatment. Current state beyond the home H1: **to be measured in week 1**. *Kaev · 2h.*
4. **Alt text** on every image, descriptive not decorative ("Dolce clinic treatment room, Park View Erbil"). *Client · 2h.*
5. **Internal links.** Each service page should link to Contact and to its sibling services in body text, not only the nav. *Kaev · 1h.*
6. **Add a Polished by Dolce page and a Core cross-link page.** Polished currently has no page anywhere (**verified**). One page at `/polished-salon` with services, address, phone gives the salon a landing page for its Business Profile and its schema. Add a short `/core-studio` page that links out to coreyogapilatesstudio.com. *Kaev · 3h · Outcome: every brand has a canonical page.*
7. **Update the 2022 footer.** *Client · 10m.*

### Fix list — Core (Shopify)

1. **Fix the booking dead end — the single most important action in this plan.** The Classes page has a "BOOK YOUR CLASSES NOW!" banner and no way to book (**verified**). Add, natively in the theme editor: the weekly timetable as a simple table or image, a WhatsApp click-to-chat button (`https://wa.me/9647509000200?text=...` pre-filled "I'd like to book a class"), and the phone number. *Kaev · 2h · Shopify native, free · Outcome: a visitor can act. Conditional on WhatsApp being the real booking channel.*
2. **Decide what the cart is for.** Checkout is live but the catalogue is empty (**verified**), so the cart is dead weight. Either create products for class passes and memberships (native, and Shopify's payment options for Iraq need checking — **needs testing**; cash/"manual payment" on delivery-at-studio works natively) or hide cart and account links until there is something to sell. *Client decides, Kaev implements · 1–3h.*
3. **Fix the duplicated title tag.** In Shopify admin → preferences, set the home title to "Core Yoga & Pilates Studio | The Boulevard, Erbil" and write a real meta description; then unique titles/descriptions per page. The duplication comes from the theme appending the store name — check the page-title setting first. *Kaev · 1h · native · standard practice.*
4. **Put the address and phone on the site.** Neither appears anywhere (**verified**). Footer block: "The Boulevard, Erbil, Kurdistan Region, Iraq · +964 750 900 0200". *Kaev · 30m · native.*
5. **Alt text, header hierarchy, internal links** — same treatment as Dolce. *Client · 2h.*

### Schema plan (JSON-LD)

All four blocks below are plain JSON-LD in a `<script type="application/ld+json">` tag. Injection: on **Wix**, each page's SEO settings has an advanced "structured data markup" field — native, free, no code file edits (standard practice). On **Shopify**, add a snippet in the theme (`theme.liquid`) — a one-time code edit, free, no app (standard practice). Google may or may not show rich results; the markup's job is making the businesses machine-readable — tag the visible effect **needs testing**.

- **Dolce home page:** `MedicalClinic` — name, address (Park View, Erbil), phone, URL, `medicalSpecialty`, opening hours, `sameAs` for Instagram/Facebook.
- **Polished page:** `HealthAndBeautyBusiness` — its own name, same address and phone.
- **Core home page:** `ExerciseGym` — name, The Boulevard address, phone, `sameAs` for Instagram/TikTok.
- **FAQPage** on Dolce service pages and Core's Yoga/Pilates pages — only once real FAQ content exists (section 6), never before. FAQ answers about procedures need **doctor sign-off**.

*Kaev · 4h total · Outcome: Google can connect each brand, address and profile.*

---

## 2. Keyword targets

English first. The Kurdish (Sorani) and Arabic columns are deliberately left for you to validate with staff and patients — we will not guess at medical vocabulary in languages we can't verify. Intent: **T** = transactional (wants to book), **I** = informational. Current rankings for all terms: **to be measured in week 1**.

### Dolce (mapped to the renamed pages)

| # | Keyword (EN) | Intent | Page | Kurdish | Arabic |
|---|---|---|---|---|---|
| 1 | dermatologist erbil | T | /dermatology-non-invasive | *validate* | *validate* |
| 2 | skin clinic erbil | T | home | | |
| 3 | botox erbil | T | /dermatology-non-invasive | | |
| 4 | dermal fillers erbil | T | /dermatology-non-invasive | | |
| 5 | laser hair removal erbil | T | /dermatology-non-invasive | | |
| 6 | facial treatment erbil | T | /dermatology-non-invasive | | |
| 7 | mesotherapy erbil | T | /dermatology-non-invasive | | |
| 8 | hair loss treatment erbil | T | /dermatology-non-invasive | | |
| 9 | plastic surgery erbil | T | /plastic-surgery | | |
| 10 | plastic surgeon kurdistan | T | /plastic-surgery | | |
| 11 | iv therapy erbil | T | /wellness | | |
| 12 | vitamin drip erbil | T | /wellness | | |
| 13 | blood test clinic erbil | T | /wellness | | |
| 14 | aesthetic clinic park view erbil | T | home | | |
| 15 | how long does botox last | I | future FAQ (doctor sign-off) | | |

### Core

| # | Keyword (EN) | Intent | Page | Kurdish | Arabic |
|---|---|---|---|---|---|
| 1 | pilates erbil | T | /pages/pilates | *validate* | *validate* |
| 2 | yoga erbil | T | /pages/yoga | | |
| 3 | pilates studio erbil | T | home | | |
| 4 | yoga classes erbil | T | /pages/classes | | |
| 5 | yoga studio near me (Erbil GBP) | T | GBP + home | | |
| 6 | reformer pilates erbil | T | /pages/pilates (only if offered — validate) | | |
| 7 | pilates the boulevard erbil | T | home | | |
| 8 | beginner yoga classes erbil | T | /pages/classes | | |
| 9 | yoga for women erbil | T | /pages/classes (validate positioning) | | |
| 10 | pilates class prices erbil | T | /pages/classes | | |
| 11 | yoga kurdistan | I/T | home | | |
| 12 | what is pilates | I | /pages/pilates | | |
| 13 | yoga vs pilates for beginners | I | future blog/FAQ | | |

*Kaev drafts page mapping into titles/H1s in weeks 2–3 · Outcome: each priority page targets one cluster instead of none.*

---

## 3. Local search

### Google Business Profiles — three profiles, two addresses

Create or claim **three separate profiles** (conditional on our assumption that none exist; if any does, claim rather than duplicate — a duplicate gets suspended):

1. **Dolce Aesthetic Clinic** — Park View. Primary category: *Skin care clinic*; secondary: *Medical clinic*, *Plastic surgery clinic*.
2. **Polished by Dolce Salon** — Park View. Primary: *Beauty salon*; secondary: *Hair salon*, *Nail salon* (match to real services).
3. **Core Yoga & Pilates Studio** — The Boulevard. Primary: *Pilates studio*; secondary: *Yoga studio*.

Two businesses at one Park View address is fine as long as names, categories and entrances are distinct (standard practice). Verification may be by postcard, phone, video or live call — Google decides; in Iraq expect video verification and allow up to two weeks (**needs testing**). *Client (must be the owner's Google account) with Kaev on the call · 2h setup + wait.*

**Completion checklist per profile:** exact name (no keyword stuffing — "Dolce Aesthetic Clinic", not "Dolce Clinic Botox Erbil"), address, pin placed correctly on the map, hours including holiday hours, phone, website link to the brand's own page (Polished → the new /polished-salon page), services list with short plain descriptions (clinic service descriptions: **doctor sign-off**), attributes (women-owned/accessibility as applicable — validate), opening date, booking link (the WhatsApp link until a real booking tool exists).

**Photo plan:** 10+ per profile at launch — exterior with signage, reception, treatment/studio rooms, team (with consent). Then 2–4 fresh photos per month. Phone photos are fine; consistency beats polish. *Client · 2h launch, 30m/month.*

**Posting cadence:** one Google post per profile per week — the same content as section 6, repurposed. *Client · 30m/week.*

### NAP consistency

One phone number serves three brands (**verified**). That's workable if it's *identical everywhere*: pick one format — `+964 750 900 0200` — and use it on both sites, all three profiles, Instagram bios, Facebook and TikTok. Same for addresses: "Park View, Erbil, Kurdistan Region, Iraq" and "The Boulevard, Erbil, Kurdistan Region, Iraq", spelled the same way every time. If budget ever allows, a separate WhatsApp Business number per brand removes the shared-line ambiguity — optional, not required. *Kaev audits, Client fixes bios · 1h.*

### Citations — Iraq and Kurdistan only

The formal directory ecosystem in Iraq is thin, and we will not pad this list with Western directories nobody in Erbil uses. The citations that actually matter:

1. **Google Business Profile** (above) — the only one that moves rankings materially. *Standard practice.*
2. **Apple Business Connect** — free; Apple Maps usage in Erbil is real on iPhones. *Kaev · 1h · standard practice.*
3. **Facebook pages** with full address/phone/hours for all three brands (Dolce's exists — **verified**; complete it; create Polished's and Core's or consolidate deliberately).
4. **Instagram business profiles** with address and contact buttons — all three exist (**verified**); ensure category and contact info are set.
5. **Bing Places** — 15 minutes, minor upside. *Optional.*
6. **The Boulevard's own tenant directory** (for Core) and any **Park View compound directory** (for Dolce/Polished) — whether these exist and accept listings: **needs testing** in week 4; ask the mall/compound management directly.
7. **Local aggregator apps** (e.g. Erbil-based super-apps and delivery/services platforms that list venues): audit which currently list any of the three brands and correct them — inventory **to be measured in week 4**.

---

## 4. Review programme

Rules that hold regardless of anything else: no incentives or discounts for reviews, no filtering unhappy customers away from the public link, no staff or family reviews, requests sent one-to-one from the customer's own visit — never bulk from one device. Ask everyone or ask by a neutral rule (e.g. every new customer), not only the happy ones.

**Channel:** WhatsApp, one message per customer, sent within a few hours of the visit. Conditional on WhatsApp being your active channel (our assumption). Each GBP profile has a short review link — grab it from the profile dashboard in week 3.

**Clinic flow (Dolce/Polished):** visit ends → reception logs the visit in the tracking sheet → same-day WhatsApp request → one reminder after 3 days if no response → stop. Never mention the treatment received in the message — the patient may not want it in writing.

> **Request:** "Hi [name], thank you for visiting Dolce today. If you have a minute, a Google review helps others in Erbil find us: [link]. Either way, we're glad you came in."
>
> **Reminder (once, day 3):** "Hi [name], just a gentle nudge — if you'd like to share your experience at Dolce, here's the link: [link]. No worries if not!"

**Studio flow (Core):** ask after a member's *third* class (first-timers haven't formed a view), then never re-ask someone who has been asked twice.

> "Hi [name], great having you at Core this week! If you're enjoying the classes, a quick Google review means a lot to a small studio: [link]."

**Response templates** — reply to every review within 48h:

> **Positive:** "Thank you, [name]! It's a pleasure having you at [brand]. See you next time." (Vary the wording; never confirm what treatment a clinic patient had.)
>
> **Negative:** "Thank you for telling us, [name] — we're sorry this was your experience. We'd like to understand what happened and put it right: please call us on +964 750 900 0200 or message this number. — [manager name]" (No arguing, no clinical details, take it offline.)

**Tracking sheet** (until a CRM exists — Google Sheet, one tab per brand): date of visit · name · phone · request sent (date) · reminder sent (date) · review received (Y/N) · rating · responded (date). *Client · 15m/day of visits · Outcome: review counts move from their current baseline — **to be measured in week 3** — with a clean audit trail.*

---

## 5. Email programme

### First, the sender

Three gmail.com addresses are the current identity (**verified**). Free-mailbox senders can't carry proper authentication and read as unofficial. Set up domain mailboxes on **dolceclinic.com** — e.g. `hello@dolceclinic.com`, `core@dolceclinic.com` — via Zoho Mail's free tier or Google Workspace (~$6/user/month; the one place we'd suggest spending). Keep the gmail addresses as forwarding aliases so nothing is lost. *Kaev · 2h · conditional on budget choice · standard practice.*

**Deliverability, on the sending domain:** SPF record including your mailbox provider and email platform; DKIM keys from both; DMARC starting at `p=none` with a reporting address, tightened to `p=quarantine` after 4+ clean weeks. All are DNS records — 1h of work, then monitoring. *Kaev · standard practice.*

**Platform:** with no budget, **Shopify Email** covers Core natively (free tier, sends from the store) and a free-tier ESP (Brevo or Mailchimp — current free limits **needs testing**) covers Dolce/Polished. One ESP for everything is cleaner if a small budget appears. *Conditional on budget answer.*

### Consolidating the 5,000+ — permission first

Under our assumption the list has no recorded consent, so **we do not import and mail it.** The standard we follow everywhere: explicit opt-in, one-click unsubscribe, no purchased lists, opt-outs honoured within 24 hours — and the platform policies of Google, Meta and the ESP as binding rules.

1. Export every source (WhatsApp contacts, Instagram, spreadsheets, any Shopify signups) into one master sheet: name · phone · email · brand · source · consent evidence. *Client · 3h.*
2. Contacts with real consent evidence (e.g. the Shopify "subscribe to our emails" form — **verified** it exists) import directly.
3. Everyone else gets **one** re-permission invitation through the channel they already use — WhatsApp: "We're starting a monthly email from Dolce with offers and openings. Want in? Tap to join: [signup link]" — plus a QR code at both receptions and a link-in-bio on all three Instagram accounts. No response = not on the list. Expect a small fraction to convert; a 500-person opted-in list outperforms 5,000 cold. *Client · ongoing, weeks 5–8.*

### Segmentation

Tag at signup, don't guess later: **brand** (Dolce / Polished / Core), **location** (Park View / Boulevard), **service interest** (clinic: dermatology / surgery / wellness; studio: yoga / pilates). One monthly email per brand maximum at this capacity.

### Evergreen templates (drafts by Kaev; every clinic email: **doctor sign-off**)

1. **Welcome** (per brand) — what to expect, hours, how to book, one CTA.
2. **New-patient consultation invitation** (Dolce) — books a consult; no outcome claims.
3. **Seasonal services note** (Dolce/Polished) — what's relevant now; facts, not promises.
4. **First class free / intro offer** (Core) — conditional on the studio actually running one; if not, "bring a friend week".
5. **Class schedule update** (Core) — monthly timetable.
6. **We-miss-you** (any brand) — to subscribers inactive 90+ days, one send, then stop.

*Outcome: a small, clean, authenticated list that lands in inboxes. Open/click baselines: to be measured from the first sends.*

---

## 6. Content — 90 days

Capacity assumption: ~4 client hours/week, some consumed by GBP posts and reviews. So: **one content piece per week**, alternating brands, each reused three ways (web page → GBP post → Instagram caption). Kaev drafts, Client supplies photos and local facts, doctor signs off anything clinical.

**Weeks 1–4 (foundations double as content):** rewritten service-page copy for Dolce's three service pages, the new Polished page, Core's Pilates and Yoga page copy with the timetable.

**Weeks 5–8 (people):** one doctor profile (credentials and approach — sign-off), one instructor profile for Core, "your first visit at Dolce" explainer, "your first class at Core" explainer.

**Weeks 9–12 (FAQs, then their schema):** 6–8 real questions per business, sourced from what reception and instructors actually get asked. Clinic answers: what a treatment is, what a visit involves, how to prepare — never results or safety claims; **doctor sign-off**. Publish, then add FAQPage schema (section 1).

**Weeks 13 (day 90) onward:** one local page per site — "Visiting Dolce in Park View" / "Finding Core at The Boulevard" with directions, parking, landmarks. Kurdish/Arabic versions of the top 3 pages **only if** the language answer and translation budget say yes — machine translation of medical content is a reputation risk we won't take (conditional).

---

## 7. Measurement

**KPI set (small on purpose):** indexed pages per site · GBP actions per profile (calls + direction requests + website clicks) · total reviews and average rating per profile · WhatsApp booking messages per week (ask "how did you find us?") · opted-in email subscribers · email open rate. All baselines: **to be measured in week 1** (or week 3 for GBP, post-verification).

**Weekly 15-minute check (Client, same day each week):** Search Console — any errors, indexed count. GBP — new reviews (respond), post published. Tracking sheet — requests sent vs. reviews in. Note WhatsApp booking count. One line in a log: "anything odd?"

**Monthly report (Kaev, 1 page):** the six KPIs vs. last month · what shipped · what didn't and why · next month's three priorities · the rubric below.

**Rubric — score 0–5 each, monthly:**

| Area | 0 | 3 | 5 |
|---|---|---|---|
| Technical health | blank slugs, no analytics | slugs/titles/schema live, GA4 + SC reporting | all pages indexed, errors at zero for 2+ months |
| Local visibility | no verified GBP | 3 profiles verified and complete | weekly posts + photos sustained, GBP actions rising 3 straight months |
| Reviews | no flow | flow running, responses within 48h | steady monthly review flow, rating ≥ 4.5, zero unanswered |
| Email | gmail sender, no consented list | domain sender authenticated, opted-in list growing | monthly sends per brand, complaints ~0, opens above provider benchmark |

---

## 8. Quick wins — top 10 by impact vs. effort

| # | Action | Time | Why first |
|---|---|---|---|
| 1 | WhatsApp booking button + timetable on Core's Classes page | 2h | Converts existing visitors today; the site currently can't take a booking (**verified**) |
| 2 | Fix Core's duplicated title + write meta description | 45m | Every search impression looks broken right now |
| 3 | Rename Dolce's four blank slugs with 301s | 1h | Highest SEO value per minute on either site |
| 4 | Titles + meta descriptions on all Dolce pages | 2h | Same |
| 5 | Claim/verify 3 Google Business Profiles | 2h + wait | Nothing local moves without them |
| 6 | Core footer: address + phone | 30m | Site currently has neither (**verified**) |
| 7 | Search Console both sites, submit sitemaps | 1h | Can't measure anything without it |
| 8 | GA4 both sites | 2h | Same |
| 9 | Domain mailboxes + SPF/DKIM/DMARC | 2h | Unblocks the whole email programme |
| 10 | Review request template + tracking sheet live | 1h | Compounds weekly from week 3 |

---

## 12-week plan

| Week | Dolce (+ Polished) tasks | Core tasks | Milestone |
|---|---|---|---|
| 1 | Recover/verify Search Console; GA4; record indexing + baselines; audit NAP everywhere | Search Console + GA4; baseline record; fix duplicated title + meta | Both sites measurable; baselines logged |
| 2 | Rename blank slugs with 301s; new titles/metas all pages | WhatsApp booking button + timetable on Classes; footer address/phone | A Core visitor can book; Dolce URLs readable |
| 3 | Start GBP claims (clinic + salon); begin service-page copy rewrite (doctor sign-off) | GBP claim (studio); decide cart: class-pass products or hide | GBP verifications in progress |
| 4 | Finish GBP profiles: services, photos, booking link; header/alt-text pass | Same for studio profile; Pilates/Yoga page copy | 3 complete profiles (pending Google verification) |
| 5 | Build /polished-salon page; JSON-LD on Dolce + Polished | JSON-LD (ExerciseGym); alt-text/header pass | Schema live on both sites |
| 6 | Domain mailboxes; SPF/DKIM/DMARC; pick ESP | Shopify Email connected; signup form checked | Authenticated domain sender exists |
| 7 | Review flow live at clinic reception; tracking sheet | Review flow live (3rd-class rule) | First review requests sent |
| 8 | Contact consolidation: export, dedupe, tag consent | Same for studio sources | Master contact sheet done |
| 9 | Re-permission push: WhatsApp invite, reception QR, bio links | Same + timetable email to consented subscribers | Opt-in list growing; first Core send |
| 10 | Welcome + consultation emails drafted (doctor sign-off); doctor profile published | Welcome + intro-offer emails; instructor profile published | Welcome flows live per brand |
| 11 | FAQ content (sign-off) → FAQPage schema | FAQ content → FAQPage schema | FAQs live with schema |
| 12 | First monthly report: KPIs + rubric; citations audit (Boulevard/Park View directories, aggregators); "first visit" explainer | In same report; "first class" explainer; Apple Business Connect all brands | Month-1 report delivered; 90-day content plan rolling |

---

*Everything in this document that touches procedure descriptions, treatment explanations or patient communications requires doctor review before it goes live. Nothing here promises rankings, review counts or revenue — the baselines get measured in week 1 and the monthly report tracks movement honestly from there.*

---

## 9. WhatsApp booking automation (added at client request)

Two tiers exist, and it matters which you buy into:

**Tier 1 — WhatsApp Business app (free, on now, week 2).** The free app gives you: a greeting message when someone first messages, an away message outside hours, and quick replies (canned answers triggered by shortcuts). That is the ceiling — it cannot hold a conversation, show a class list, or confirm a slot by itself. But configured well it does half the job: a greeting that says "Reply 1 for Dolce Clinic appointments, 2 for Polished Salon, 3 for Core class bookings" with staff finishing each thread manually is a real improvement over an unstructured inbox, costs nothing, and takes an hour. *Client + Kaev · 1h · free · standard practice.*

**Tier 2 — WhatsApp Business Platform (Cloud API) for true automation.** A real booking bot — client messages, bot offers the class schedule or consultation slots, client picks, bot confirms and logs it — requires the WhatsApp Business API, accessed through a Business Solution Provider (examples: Twilio, 360dialog, Wati, respond.io). Facts to hold onto:

- The API number **cannot simultaneously use the normal WhatsApp app** — the number is dedicated to the platform. Since one number currently serves all three brands, moving it to the API affects everyone at once. A safer path is a **new dedicated booking number** on the API, with the existing number kept for human conversation. *Standard practice.*
- Costs are real: BSP subscription fees plus Meta's per-conversation/per-message charges. Exact current pricing for Iraq and which BSPs onboard Iraqi businesses smoothly: **needs testing — we will price 2–3 providers in writing before you commit.** This is **conditional on budget**, which our assumptions say is zero — so Tier 2 is a decision point, not a default.
- The bot also needs something to book *into*. A bot without a schedule behind it just moves the manual work later. So the order is: pick a booking backend first (Shopify class-pass products with a simple timetable, or a dedicated booking tool), then automate the conversation in front of it.
- Meta's Business and Commerce policies apply fully — opt-in before proactive messages, no message blasts to the unconsented 5,000, human handoff always available. Medical conversations deserve extra caution: the bot should book consultations, never give treatment advice (**doctor sign-off** on all bot scripts touching clinic services).

**Recommended sequence:** week 2 — Tier 1 configured (greeting, away, quick replies, the wa.me links from section 1 all point at it). Week 6 — Kaev delivers a written Tier 2 comparison (2–3 BSPs, real prices, Iraq onboarding confirmed, booking-backend options). Week 8+ — if you approve the budget, build the Core class-booking flow first (simple, repetitive, low risk), clinic consultation booking second. *Outcome: structured booking immediately at zero cost, with a priced, honest path to full automation instead of a premature tool purchase.*
