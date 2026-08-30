# Dolce / Polished / Core — Response 1: Audit summary, questions, assumptions

Prepared by Kaev. Date of checks: 30 August 2026. All findings below were observed directly in the live sites, their robots.txt and their XML sitemaps on that date.

## What we found

### Dolce Aesthetic Clinic (dolceclinic.com, Wix)

- Five pages exist in total: home plus `/blank-1` (Contact), `/blank-2` (Plastic Surgery), `/blank-3` (Wellness), `/blank-4` (Dermatology & Non-Invasive). The URLs carry no words a search engine can read.
- Title tag on the home page: "Clinic | Dolce Aesthetic Clinic | Erbil". No meta description was returned.
- No structured data (JSON-LD) anywhere. Google cannot read the clinic as a business, an address or a set of services.
- robots.txt and sitemap.xml are healthy Wix defaults. Sitemap last modified 25 June 2025.
- One site carries three brands. Polished and Core have no page of their own on it.
- Footer still says 2022. English only. Three gmail.com addresses used as business contacts.
- A google-site-verification tag is present, so a Search Console property probably exists. We cannot see who owns it.

### Core Yoga & Pilates Studio (coreyogapilatesstudio.com, Shopify)

- Five pages: home, Pilates, Yoga, Classes, Contact, plus a policy page.
- **The Classes page has no way to book.** It shows a "BOOK YOUR CLASSES NOW!" banner and six photographs, and nothing else — no form, no timetable, no phone number, no WhatsApp link, no booking button. The only outbound link on the page goes to Instagram.
- **The store has zero products** (`/products.json` returns an empty list). Cart, checkout and customer accounts are switched on but there is nothing to buy, so no class pass or membership can be sold today.
- Title tag is duplicated: "Core Yoga & Pilates Studio – Core Yoga & Pilates Studio". Meta description is the brand name only.
- No structured data. No Search Console verification tag in the HTML.
- No phone number and no street address anywhere on the site. English only, locale IQ.

The single largest commercial problem across both sites is not ranking. It is that a person who finds Core and wants to book cannot, and a person who finds Dolce lands on pages Google barely understands.

## Questions we need answered before the plan is finalised

1. **Google Business Profile** — does each location have a claimed and verified profile, and who holds the login? Is Core listed separately from Dolce and Polished?
2. **Search Console and GA4** — who owns the existing Dolce verification, and is there any GA4 property on either site?
3. **Client database** — where do the 5,000+ contacts actually live (Shopify customers, Wix contacts, a booking app, WhatsApp, a spreadsheet)? What did people agree to when they were added?
4. **Booking** — what takes bookings today for clinic appointments, and for studio classes? Is it Instagram DM and WhatsApp?
5. **Email platform** — is there a sender already (Shopify Email, Wix, Mailchimp, Klaviyo, none)?
6. **Languages** — should we plan Kurdish (Sorani) and Arabic content, or English only for now?
7. **Regulatory** — are there local advertising restrictions on medical or aesthetic procedures the clinic already works to?
8. **Capacity** — who on your side does the work each week, and how many hours are realistic?
9. **Budget** — is there any spend for paid tools, translation or photography?

## Assumptions we will proceed on if these go unanswered

- No verified Google Business Profile exists for any of the three brands. Claiming them is week 1 work.
- No GA4 exists on either site. Search Console access for Dolce is recoverable but unproven.
- The 5,000+ contacts are spread across WhatsApp, Instagram and a spreadsheet, with no recorded consent. We will treat the whole list as unconsented and re-permission it rather than mail it.
- Bookings run through Instagram DM and WhatsApp for both businesses.
- No email platform is in place.
- English first, with Kurdish and Arabic columns left for you to validate.
- One person on your side, roughly four hours a week.
- No budget beyond the free tiers of Google tools and the existing Wix and Shopify plans.

Every recommendation that depends on one of these will be marked conditional in the plan.
