# Dolce master email template - build spec

## Platform note (standard practice)
Wix Email Marketing builds campaigns in its own drag-and-drop editor and does
not import custom HTML. The HTML file in this folder is therefore:
  1. the visual reference to recreate in the Wix editor (10-15 min), and
  2. a ready-to-use HTML template if the programme ever moves to an ESP
     that accepts HTML (Brevo, Mailchimp, Klaviyo).

## Recreate in Wix Email Marketing - block by block
1. Background: #f6f2ee. Content card: white, max width.
2. Logo block: upload the real Dolce logo (swap for the "D O L C E" text
   placeholder). Alt text: "Dolce Aesthetic Clinic".
3. Heading text block: Georgia or closest serif, ~24px, #2b2b2b.
4. Body text block: Arial 15px, #4a4a4a. One message, under 150 words.
5. Button: background #b08d57, white uppercase text, link to
   https://wa.me/9647509000200 with pre-filled text. ONE button per email.
6. Divider, then footer text block: address, phone, hello@dolceclinic.com,
   social links in #b08d57. Wix appends its own unsubscribe automatically —
   verify it appears in the test send.
7. Sender settings per campaign: From name "Dolce Aesthetic Clinic",
   from/reply-to hello@dolceclinic.com. Subject sentence case, no ALL CAPS,
   no emoji spam. Preheader: one calm sentence.

## Colour tokens (swap when brand palette is confirmed)
- Ink: #2b2b2b   - Body: #4a4a4a   - Champagne gold (from logo): #c2a273 (logo script ~#d8b98a on mauve)
- Card: #ffffff  - Page: #f5eff0   - Hairline: #ead9dc   - Brand mauve (from logo): #9d8184
Placeholder palette based on the aesthetic-clinic positioning; confirm
against the actual logo/brand colours before first real send.

## Rules baked into the layout
- One message, one CTA per email. WhatsApp is the CTA (bookings happen there).
- No before/after imagery, no results/safety claims. Any email naming
  treatments needs doctor sign-off before scheduling.
- Footer identity + unsubscribe on every send, no exceptions.

## Copy variants that drop into the same shell
1. Welcome (in the HTML) - sign-off not required as long as no treatments named.
2. Consultation invitation (Dolce) - NEEDS DOCTOR SIGN-OFF.
3. Seasonal services note - NEEDS DOCTOR SIGN-OFF.
4. Monthly newsletter - sign-off if treatments mentioned.
5. We-miss-you (90 days inactive) - generic wording, no sign-off needed.

## Approval log
- 30 Aug 2026 - Master template design APPROVED by client (white banner,
  real logo embedded, single WhatsApp CTA, blush/champagne palette).
  Approval gate for sends: every campaign is test-sent to
  dolce.erbil@gmail.com (+ jshamoon30@gmail.com) and waits for an explicit
  "approved" before any real send. Automations are approved once at setup
  via the same test-send, before activation.
