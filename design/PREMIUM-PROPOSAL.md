# Investedia Premium — audit, proposal and plan (preview stage, 2026-11-05)

Status: design preview only (`premium-preview` branch, page `premium.html`). No payment provider connected, nothing pushed or deployed.

## 1. Audit (what exists today)
| Area | Finding | Implication for Premium |
|---|---|---|
| Hosting | Static site on GitHub Pages (`docs/`), built by `build.py`. Everything in `docs/` is public. | Premium content must never be published to Pages; it has to be served by a server that checks entitlement. |
| Server | Cloudflare Worker `investedia-live` (KV `PRICES`): `/v1/prices`, `/v1/news`, `/v1/calls`, ingest endpoints with bearer tokens. Free plan. | Natural place for billing webhooks, checkout sessions and gated `/v1/premium/*` endpoints. |
| Accounts | Supabase Auth (email/password + Google) in the browser; watchlist synced to Supabase; publishable key in `ui.js`. Sign-up modal also auto-opens after 4 s for new visitors. | Reuse Supabase as the identity provider; the Worker verifies Supabase JWTs. Retire the 4-second sign-up pop-up when Premium launches (it conflicts with "no aggressive prompts"). |
| Market Views / Priority Insights | Produced by V5; same content for everyone; Priority = a V5 tier, not a statistically validated stronger subset (V6/V7 research). | Do not sell Priority Insights as "more accurate". Sell depth (full note, context), speed (alerts) and tools. |
| Track Record | Public, frozen calls, methodology documented; research engine panel prepared on `v7-product`. | Keep 100% free (also a trust and regulatory requirement). |
| Legal | Terms contain a "Future Pro service — placeholder"; operator is a Belgian eenmanszaak; owner placeholders (address, KBO/VAT) still unfilled; disclaimer says not FSMA-authorised. | Before charging: fill company details, Pro terms, withdrawal-right wording, privacy (payment processor), invoicing. Legal review of whether paid directional content is "investment recommendation/advice" (see §9). |
| Existing teasers | Asset sheet: "Live analysis is coming to Investedia Pro"; dashboard meta says "premium". | Rename to Premium consistently; link to the landing page. |

## 2. Free / Premium matrix
| Feature | Free | Premium | Upgrade trigger |
|---|---|---|---|
| News, globe, market and company pages | ✓ | ✓ | — |
| Market Views (direction, horizon, evidence, risk) | ✓ (same as Premium) | ✓ | — |
| Track Record, methodology, every past call | ✓ | ✓ | never gated |
| Priority Insights | headline + summary | full research note (evidence, counterarguments, scenarios, key risk) | "Read the full note" at the summary end |
| Long-Term Outlooks | direction + thesis | + historical analog context (count, median, range, limits) | blurred context block |
| Watchlist | 10 assets | unlimited | adding the 11th asset |
| Alerts | daily email digest | real-time per asset (SEC filing, earnings, unusual move, new call) | "Alert me instantly" toggle |
| Company event history | last 30 days | full verified history with reactions | "Show older events" |
| Charts | standard | full chart + indicators | opening indicators |
| CSV export | — | watchlist + calls | export button |

Limits are enforced on the server (Worker), never only in the browser.

## 3. Price and trial
- €11.99/month **including** 21% Belgian VAT → €9.91 net for a Belgian consumer (other EU countries: their VAT rate via OSS). Positioning vs common retail research tools (approximate public list prices; verify before launch): TradingView paid tiers ~$13–60/mo, Simply Wall St ~€10–20/mo, Seeking Alpha Premium ~$299/yr, Morningstar Investor ~$35/mo. €11.99 sits at the accessible end — appropriate while the engine has no demonstrated predictive edge.
- Add an annual plan: €99/year (≈31% off) to reduce churn and payment fees.
- Trial: a **3-day** trial is short for a research product (one market week is ~5 sessions; alerts need time to prove value). Recommendation: **7-day trial with card**, reminder email 24 h before charging, one-click cancel. If you keep 3 days, start it on any weekday but extend to the next Monday close if it would end on a weekend.
- EU consumer rules: 14-day withdrawal right for digital services unless the consumer explicitly requests immediate start and acknowledges losing the right; collect that consent at checkout. Show total price incl. VAT before payment.

## 4. Conversion journey
Free research (article / Market View / company page) → contextual gate at a real limit (full note, 11th asset, older events, real-time alert) → Premium landing (`premium.html`: value, comparison, price, FAQ) → sign in / create account (Supabase; skip if signed in) → hosted checkout (provider page, VAT, consent) → webhook grants entitlement → trial (welcome email + "what's unlocked" checklist; reminder day N-1) → subscription → account page (plan, next charge, invoices, change payment method, switch yearly, cancel = provider portal). Measure each step (privacy-friendly event counter already exists in `ui.js`).

## 5. Payment providers (Belgian eenmanszaak, B2C digital subscriptions; verify current terms before choosing)
| | Stripe Billing (+ Stripe Tax) | Mollie | Paddle (merchant of record) | Lemon Squeezy (MoR) |
|---|---|---|---|---|
| Who is seller of record | You | You | Paddle | Lemon Squeezy |
| EU VAT / OSS filing | You file (Stripe Tax calculates) | You (no tax engine) | Paddle collects & remits | LS collects & remits |
| Bancontact | yes (first payment; recurring via SEPA mandate) | yes, strong in BE | limited | limited |
| Hosted checkout + customer portal | yes | checkout yes, portal no (build yourself) | yes | yes |
| Webhooks with signatures | yes | yes | yes | yes |
| Typical fee at €11.99 (indicative) | ~1.5%+€0.25 card + ~0.7% Billing + ~0.5% Tax ≈ €0.55 | ~€0.30–0.45 + build effort | ~5%+$0.50 ≈ €1.05 | ~5%+$0.50 ≈ €1.05 |
| Fit | best long-term, more admin | best Belgian payment mix, most build | least admin at launch | similar to Paddle |
Recommendation: launch with a **merchant of record (Paddle)** to avoid OSS filing and invoicing work while volumes are small; revisit Stripe Billing + Stripe Tax once revenue justifies the admin (or if an accountant already files OSS). Discuss the VAT small-business exemption (Belgian €25k regime) with an accountant: it interacts with OSS and cross-border sales.

## 6. Entitlement architecture (GitHub Pages + Cloudflare Workers + Supabase)
- Identity: Supabase Auth (existing). Browser sends the Supabase access token to the Worker.
- Worker routes (new): `POST /v1/billing/checkout` (creates provider checkout for the signed-in user, user id in metadata), `POST /v1/billing/webhook` (verifies provider signature, idempotent by event id, writes `subscriptions` row: user_id, status, plan, current_period_end, provider ids), `POST /v1/billing/portal` (returns provider customer-portal URL), `GET /v1/me/entitlements`, `GET /v1/premium/*` (full notes, analog context, history, export).
- Checks: Worker verifies the Supabase JWT (JWKS, issuer, expiry), then reads entitlement (Supabase table via service role key stored as a Worker secret; cached 60 s in KV). Premium responses are `Cache-Control: private, no-store`; free responses stay edge-cached.
- Data: Premium JSON is produced by GitHub Actions and uploaded to Cloudflare R2/KV through the existing token-protected ingest pattern — never committed to `docs/`. Free pages keep working if the Worker is down; Premium shows "temporarily unavailable" (fail closed).
- Secrets: provider secret key and webhook secret as Worker secrets; never in the repo or browser.
- Row-level security on `subscriptions` (users read only their own row; only the service role writes).

## 7. Connecting News, Outlooks, Priority Insights and Track Record
- Each article shows the outlooks it produced (or "No View" with the reason) and links to their Track Record rows once resolved.
- Each Market View card links to its source article and, after resolution, to its outcome; each Track Record row links back to the article and the call.
- Company pages show: recent verified events → outlooks → outcomes timeline, plus descriptive historical context.
- Track Record gets per-category and per-horizon views and the live/shadow/research separation panel (prepared on `v7-product`).

## 8. Costs (monthly, indicative)
| Item | Launch (<1k users) | Growth |
|---|---|---|
| Cloudflare Workers | €0 (free 100k req/day) | ~€5 (Workers Paid) |
| Supabase | €0 (free tier) | ~€25 (Pro) |
| R2 / KV | €0 | <€5 |
| Transactional email (reminders) | €0 (free tier) | ~€20 |
| Payment fees | ~4.6% (Stripe) or ~9% (MoR) of revenue | same |
| One-off | accountant setup, legal review of Pro terms & regulatory status | — |

## 9. Risks to settle before charging
1. Regulatory: selling directional calls (Long/Short) may qualify as investment recommendations under MAR/FSMA rules even with disclaimers. Keeping Market Views free and identical for all users, and making Premium about tools/depth, lowers but does not remove the risk. Get Belgian legal advice.
2. Honesty: no accuracy claims for Premium; Priority Insights must not be marketed as stronger until prospectively validated.
3. Company details placeholders in Terms must be filled; Pro terms drafted and reviewed.

## 10. Phased plan
- Phase 0 (now): this preview; decide provider, trial length, matrix.
- Phase 1 (1–2 weeks): Worker entitlement layer + Supabase `subscriptions` table + RLS; tests with provider sandbox; premium endpoints behind a feature flag.
- Phase 2 (1 week): gates in the UI (full note, watchlist limit, history, alerts), landing + account pages, emails; sandbox end-to-end tests (trial, renewal, failed payment, cancel, refund, webhook replay).
- Phase 3: legal/terms/privacy updates, accountant VAT setup, soft launch to a small group, then public.
Each phase: preview → approval → implement → test; no live payments without approval.
