# Investedia Pro — Phase 1 review pack (Stripe TEST mode only)

Branch `premium-preview` (local, not pushed). Production Worker keeps `PRO_ENABLED = "false"`; nothing here charges anyone.

## 1. Supabase migration — security implications
Files: `supabase/migrations/20261105_pro_subscriptions.sql` (up) and `.down.sql` (rollback).
- `subscriptions` holds one row per user: Stripe customer/subscription ids, status, plan, trial and period dates. No card data, no
  addresses, no amounts (Stripe keeps those). Primary key = `auth.users.id`; `on delete cascade` removes the row when an account is
  deleted (GDPR erasure). Accounting records (invoices) stay in Stripe, which Belgian bookkeeping rules require you to keep.
- RLS is enabled on both tables. Signed-in users can SELECT only their own subscription row; nobody with the public (anon) or user
  token can INSERT, UPDATE or DELETE anything, and nobody can read `stripe_events`.
- Writes come only from the Worker using the Supabase service-role key, which BYPASSES RLS and has full database access. It is stored
  only as a Cloudflare Worker secret on the sandbox Worker. Risk: if that key leaks, the whole database is exposed. Hardening options
  (recommended before live): (a) a dedicated Postgres role `billing_writer` with INSERT/UPDATE on these two tables only, used through
  a custom-signed JWT; or (b) two SECURITY DEFINER functions (`upsert_subscription`, `claim_stripe_event`) callable only by that role.
- `stripe_events` grows by ~5 rows per subscriber per month; add a monthly cleanup of rows older than 90 days.
- Client code never decides access: the site asks `/v1/pro/me`, and every Pro data endpoint re-checks the subscription server-side.

## 2. Verification results (41 Worker tests, all passing; Stripe mocked — real test-mode runs come after deployment)
| Area | What is enforced | Test |
|---|---|---|
| Webhook authentication | HMAC-SHA256 over `timestamp.payload` with the webhook secret, constant-time compare, 5-minute tolerance; bad/stale/tampered signatures → 400 | signature: valid, tampered, stale |
| Idempotency | every event id recorded once (`stripe_events`); duplicates acknowledged without re-applying | webhook: duplicate |
| Ordering | events older than the last applied one (`event.created`) are ignored | webhook: out-of-order |
| Linking | subscription events before the checkout link return 409 so Stripe retries | webhook: link |
| Lifecycle | trialing → active → canceled; `customer.subscription.deleted` ends access | webhook lifecycle |
| Failed payment | first `past_due` starts a 3-day grace (not restarted by later failed retries); recovery to `active` clears it; `unpaid`/`canceled` end access | failed payment test |
| Trial reuse | a customer whose row already has a `trial_end` gets no trial; trialing/active users cannot open a second checkout (409) | trial reuse test |
| Flags | all routes 404 unless `PRO_ENABLED`; `sk_live_` keys refused unless `PRO_LIVE` | flag tests |
| VAT | checkout refuses to run until `VAT_MODE` is `registered` or `exempt`; exempt disables Stripe Tax and VAT-ID collection | VAT test |
Known gap: a person can open a NEW account with another email and start another trial. Optional fix before live: on
`checkout.session.completed`, read the payment method's card fingerprint and end the trial immediately if that fingerprint already
had one (needs a small `trial_fingerprints` table). Trial reminder email: Stripe sends `customer.subscription.trial_will_end` 3 days
before the end; sending the email itself is Phase 2 (or use Stripe's built-in "trial ending" reminder in Billing settings).

## 3. EU withdrawal right (Belgian Code of Economic Law, Book VI; Directive 2011/83/EU as amended)
- Pro is a **digital service** (continuous access and alerts), not one-off digital content. For services, starting at the consumer's
  request does **not** remove the 14-day withdrawal right; if the consumer withdraws, the trader may charge only for the service
  actually supplied (pro rata), and only if the consumer expressly asked for an early start.
- The earlier draft wording ("I understand that I lose my 14-day withdrawal right") was wrong for this product and has been removed.
- New checkout text: "Your 7-day free trial starts now; we charge €11.99 (monthly) or €109 (yearly) when it ends unless you cancel.
  You may withdraw within 14 days of subscribing for a full refund of any amount charged, and cancel anytime after that."
  (Full refund is more generous than the law requires and keeps support simple.)
- Still required before live: confirmation email on a durable medium with the terms, the withdrawal information and the model
  withdrawal form; a "Withdraw" option in the account page (cancel + refund via Stripe); Terms of Use Pro section and the Stripe
  terms-of-service URL (Checkout now requires ToS consent). **Have a Belgian lawyer confirm the wording.**

## 4. VAT and "price includes VAT" (depends on your actual VAT status — please confirm)
| Your status | What the customer pays | What you receive | Stripe settings | Page wording |
|---|---|---|---|---|
| **Small-enterprise exemption** (vrijstellingsregeling, Belgian turnover ≤ €25,000/yr) and EU cross-border e-services ≤ €10,000/yr | €11.99 | €11.99 minus fees (no VAT) | `VAT_MODE=exempt` (Stripe Tax off) | "€11.99/month" + invoice mention "Bijzondere vrijstellingsregeling kleine ondernemingen"; do NOT write "incl. VAT" |
| **VAT-registered**, cross-border EU e-services ≤ €10,000/yr | €11.99 everywhere in the EU | €9.91 (BE 21% VAT inside the price) | `VAT_MODE=registered`, price `tax_behavior=inclusive`, Stripe Tax registration: Belgium | "€11.99/month incl. VAT" |
| **VAT-registered**, cross-border > €10,000/yr | €11.99 everywhere | varies: net = 11.99 / (1 + customer-country VAT), e.g. €9.91 BE, €10.07 DE (19%), €9.99 FR (20%) | as above + OSS registration in Stripe Tax; file OSS quarterly | "€11.99/month incl. VAT" |
Exempt small enterprises crossing the €10,000 EU threshold must charge the customer country's VAT (OSS) or use the EU SME scheme —
decide with your accountant. The live preview currently says "incl. VAT"; it will follow whichever status you confirm.

## 5. Stripe test products — exact steps (Dashboard, **Test mode** switch ON)
1. Developers → toggle **Test mode** (top right). Every step below must show the orange "Test data" banner.
2. Product catalog → **Add product**: Name "Investedia Pro"; description "Alerts, research notes and tools. Not investment advice."
   - Price 1: Recurring, **€11.99 EUR**, Monthly, *Include tax in price* = Yes (registered) — if exempt, leave tax behaviour inclusive (no tax will be added).
   - Price 2: Recurring, **€109.00 EUR**, Yearly, same tax setting.
   - Copy both **price IDs** (`price_...`) — not secret; send them to me or paste into `[env.sandbox.vars]`.
3. Settings → Billing → **Customer portal**: allow cancel (at period end), switch plans between the two prices, update payment method, invoice history. Save.
4. Settings → **Tax** (only if VAT-registered): add registration Belgium; default tax behaviour "inclusive".
5. Settings → Public details: add Terms of Service URL (`https://investedia.com/terms.html`) — required because Checkout now collects ToS consent.
6. Developers → **Webhooks** → Add endpoint: `https://investedia-live-sandbox.<your-subdomain>.workers.dev/v1/pro/webhook`;
   events: `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`,
   `customer.subscription.trial_will_end`, `invoice.paid`, `invoice.payment_failed`. Copy the **signing secret** (`whsec_...`).
7. Developers → API keys: copy the **test secret key** (`sk_test_...`). Never the live key.

## 6. Configure the sandbox Worker securely (you do this; never paste keys in chat or commit them)
- Cloudflare dashboard → Workers & Pages → `investedia-live-sandbox` (exists after the first sandbox deploy) → Settings → Variables and
  Secrets → **Add → Secret** (type "Secret", not "Text"):
  `STRIPE_SECRET_KEY` = `sk_test_...` · `STRIPE_WEBHOOK_SECRET` = `whsec_...` · `SUPABASE_SERVICE_KEY` = Supabase service-role key.
- Or from your computer: `cd workers/live && npx wrangler secret put STRIPE_SECRET_KEY --env sandbox` (repeat for the other two).
- Never add these secrets to the production Worker `investedia-live`.

## 7. Test-mode deployment plan (each step needs your approval)
1. **Approve migration** → run `20261105_pro_subscriptions.sql` in Supabase SQL editor (or `supabase db push`). Check: tables exist, RLS enabled, policy present.
2. **Approve sandbox deploy** → push branch `premium-preview` (not merged), run workflow "Pro sandbox" with `SANDBOX`. It runs the 41 tests, refuses placeholder price ids, and deploys only `investedia-live-sandbox`.
3. Add the three secrets (step 6); create the webhook (step 5.6).
4. Test-mode runs with a test page or curl: checkout with test card 4242…, then Stripe **test clocks**: trial → first charge; cancel during trial; renewal; failed renewal (card 4000 0000 0000 0341) → past_due → grace → recovery/unpaid; plan switch monthly ↔ yearly; refund; webhook replay from the dashboard; out-of-order replay.
5. Report results; production stays untouched (`PRO_ENABLED=false`, no Stripe secrets).

## 8. Rollback
| What | How | Effect |
|---|---|---|
| Stop the sandbox | Cloudflare → `investedia-live-sandbox` → Settings → set `PRO_ENABLED` to `false`, or delete the Worker | all Pro routes 404 |
| Stop webhooks | Stripe test dashboard → Webhooks → disable endpoint | no events delivered |
| Revoke keys | Stripe → API keys → roll test key; delete Worker secrets | old keys useless |
| Remove database objects | run `20261105_pro_subscriptions.down.sql` | drops both tables (test data only) |
| Code | branch is not merged; nothing to revert on `main` | production unchanged |
The production Worker cannot be affected: it has `PRO_ENABLED=false`, no Stripe secrets, and the sandbox is a separate Worker with no crons and no KV.
