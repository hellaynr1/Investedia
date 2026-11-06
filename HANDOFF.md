# Investedia: project handoff

*Status as of 6 November 2026. Written for a new team member. Read with `AGENTS.md` (the owner's rules), which is the authority if anything here disagrees.*

---

## 0. Read this first: 10 rules that must not be broken

1. **Nothing goes live without the owner's explicit "push" / "go".** Work on a branch, show screenshots (PC 1440 px + phone 390 px), merge to `main` only when told.
2. **No live payments.** Stripe is in **sandbox/test mode only**. Do not enable live Stripe, add live keys, or charge a real customer without the owner's explicit approval.
3. **Never commit or paste secrets** (Stripe keys, Supabase `service_role` key, webhook secrets, Resend key, Google client secret, Anthropic key). Secrets live only in Cloudflare Worker secrets, GitHub Actions secrets or Supabase Vault. The only key allowed in code is the Supabase **publishable** key (in `assets/ui.js`).
4. **Engine V5 stays the production prediction engine.** V7 is research and shadow-only; V7 predictions are disabled on the site.
5. **Track Record and methodology are free and public forever.** Never paywall them.
6. **No invented accuracy claims.** Priority Insights may not be marketed as "more accurate". Any illustrative/mock content must be labelled **ILLUSTRATIVE**.
7. **Real data only**, keep "Not investment advice" visible everywhere.
8. **Never delete files, data, accounts or keys without asking.**
9. **Robots commit to `main` every few minutes:** always `git pull --rebase origin main` before pushing.
10. The owner is not a developer: explain in plain words, give click-by-click steps for anything they must do in a dashboard, and label every design option directly on the image (A/B/C, "Now"/"New", PC/phone).

---

## 1. What Investedia is

- **investedia.com**: *investing media for everyone*. A news-first site: world financial and business news on one live 3D globe, showing what happened, where, and why it matters to your money. Slogan: **"Invest with clarity. / See the world move."**
- Information and education only, never investment advice. Operator: a Belgian sole proprietorship (eenmanszaak); not FSMA-authorised (the disclaimer says so).
- **Direction since Oct 2026:** news first, not a trading/price site. Do not add live tickers, screeners, gainers/losers or TradingView-style pages. Old market pages still exist but are out of the menu; ask before changing them.
- **Audience and voice:** professional, educated investors. Newsroom register (Reuters/Bloomberg), precise vocabulary. Say "article(s)" in visible text, never "story". No "for beginners", no cute copy.
- **Design:** black, dark-first, minimal, Apple-like (whitespace, large type, soft glass, rounded corners, subtle motion). Accent orange `#FF7A1A`; green/red only for up/down, shown as an arrow in a round badge (↑ green, ↓ red, ↔ grey), never the words "Up/Down". Fonts: Inter (text), Geist Mono (numbers).

---

## 2. Architecture overview

```
                 GitHub repo hellaynr1/Investedia (branch main)
                                  │
     ┌────────────────────────────┼─────────────────────────────┐
     │                            │                             │
 GitHub Pages (docs/)     GitHub Actions robots          Cloudflare Workers
 static site built         (news, calendar, engine,       investedia-live  (prod API, KV "PRICES")
 by build.py               registry, prices)              investedia-live-sandbox (Pro test only)
     │                            │                             │
     └──────────── browser ───────┴──────── Supabase (Auth + Postgres, project lfjyoeusblhfpmgwbrhj)
                                                        │
                                                 Stripe (sandbox only)  ·  Resend (email)
```

| Layer | What | Notes |
|---|---|---|
| Hosting | GitHub Pages serves `docs/` | Everything in `docs/` is public. Never put Pro content there. |
| Build | `python3 build.py` | Wraps `src/pages/*.html` (first line is JSON: title, desc, key, scripts) with the shared head, writes root `*.html` **and** mirrors to `docs/`. Always run after editing; commit source + generated files. |
| Shared UI | `assets/ui.js`, `assets/app.css` | Menu (Home · Globe · News · Learn · Tools · About), login popup, footer, analytics, Supabase publishable key, `OWNERS` list. |
| Homepage | `src/pages/index.html`, `assets/home-news.js`, `assets/home-news.css` (`hn-` prefix) | Globe hero, top articles, why it moved, countries, markets open now, upcoming events and earnings. |
| Globe News page | `assets/globe/news.html`, source `tools/globe-news/` | Build: `python3 tools/globe-news/build.py && python3 build.py`. `?embed=1` = globe only (used by homepage). |
| API | Cloudflare Worker `investedia-live` (`workers/live/`) | `/v1/prices`, `/v1/news`, `/v1/calls`, ingest endpoints (bearer tokens), and `/v1/pro/*` (disabled in prod). Deployed by `.github/workflows/cf-worker.yml` on push to `main` touching `workers/live/**`. |
| Auth / DB | Supabase | Google + email/password login. Tables with RLS: `watchlists`, `events` (cookie-free analytics), `subscriptions`, `stripe_events`. |
| Email | Resend, from `info@investedia.com` (DNS at Spaceship) | Templates and setup SQL in `emails/`. Welcome email = DB trigger `on_email_confirmed` reading the Resend key from Supabase Vault. |
| Analytics | `admin.html` (owner-only) | Reads the `events` table; owners in `OWNERS` (ui.js) and the RLS policy. |

Local preview: `cd docs && python3 -m http.server 8765` → http://localhost:8765.

---

## 3. Automated robots (GitHub Actions, `.github/workflows/`)

| Workflow | Schedule | What it does |
|---|---|---|
| `broad-news.yml` | every 30 min | `update_globe_news.py` (GDELT + ECB/Fed/BoE feeds; Gemini selects and summarises; Pixabay topic photos) → `assets/globe/news-live.json`; `update_calendar.py` (ForexFactory events, Nasdaq earnings) → `assets/calendar-live.json`. |
| `priority-news.yml` | every ~10 min (self-chaining; GitHub cron alone averaged ~46 min) | Up to 10 new priority articles per run; pushes to the Worker (fast path), then commits. |
| `engine-v5.yml` | `7,37 * * * *` + triggered after new news | **Production prediction engine V5**: Market Views / calls; delivers to the Worker first, git is the permanent record. |
| `registry.yml` | hourly (`:41`) | Builds and checks the canonical asset registry (ticker ↔ company ↔ country resolver). |
| `update-calendar.yml`, `update-economy.yml` (weekly, World Bank), `update-market.yml`, `update-prices.yml` | various | Calendar, economy data, legacy price data (still used by Tools pages). |
| `native-locales.yml` | — | Translations. |
| `cf-worker.yml` | on push to `main` (workers/live/**) | Deploys the production Worker. |
| `pro-sandbox.yml` | on push to branch `pro-sandbox` | Tests, refuses placeholder price IDs, deploys **sandbox** Worker `investedia-live-sandbox`. |

GitHub secrets in use: `GEMINI_API_KEY`, `PIXABAY_KEY`, Cloudflare deploy token. Brandfetch logo Client ID is public (in `tools/globe-news/page.html`).

News rules: never copy articles or photos; each article keeps source name, link and time; AI summaries labelled "AI-assisted"; topic photos labelled "Illustration"; no Wikimedia images.

---

## 4. Investedia Pro (subscriptions): current main workstream

### 4.1 Decisions made by the owner
| Decision | Value |
|---|---|
| Name | **Investedia Pro** (not "Premium") |
| Provider | **Stripe** (Checkout + Customer Portal + Billing) |
| Price | **€11.99 / month**; **€109 / year** (annual: proposed, pending final approval) |
| Trial | **7 days free, card required**; ends automatically if no payment method |
| Free tier | **All current Free features stay unchanged**; Pro is purely additive |
| Pro feature priority | 1. custom alerts · 2. earnings-day briefs · 3. portfolio view · 4. calendar history |
| VAT | **Pending** (expected within days). No "incl. VAT" wording anywhere until settled. |

### 4.2 What is built (branch `premium-preview`, pushed, **not merged**)
| File | Purpose |
|---|---|
| `src/pages/pro.html`, `assets/pro.css` | Pro landing/preview page: hero, features, Free-vs-Pro comparison, pricing ("final price shown at checkout"), upgrade prompts marked ILLUSTRATIVE, account mock, FAQ. Not on the live site. |
| `design/PRO-PROPOSAL.md` | Audit, Free/Pro matrix, conversion journey, provider comparison, costs, risks, phased plan, Stripe spec (§11), additive features (§12). |
| `design/PRO-PHASE1-REVIEW.md` | Migration security notes, verification table, EU withdrawal analysis, VAT table, Stripe and Worker setup steps, deploy plan, rollback. |
| `workers/live/v1/pro.js` | All billing logic (below). |
| `workers/live/index.js` | Routes `/v1/pro/*` to `handlePro` inside try/catch. In the sandbox (only when the key is `sk_test_`) the 500 response includes an error `detail`. |
| `workers/live/test/pro.test.mjs` | Pro tests; whole Worker suite: **45 pass, 0 fail** (`cd workers/live && node --test test/*.mjs`). |
| `workers/live/wrangler.toml` | Prod `[vars]` `PRO_ENABLED="false"`. `[env.sandbox]`: name `investedia-live-sandbox`, `crons=[]`, no KV, `PRO_ENABLED="true"`, `VAT_MODE="exempt"` (test only), test price IDs. |
| `.github/workflows/pro-sandbox.yml` | Sandbox deploy pipeline. |
| `supabase/migrations/20261105_pro_subscriptions.sql` (+ `.down.sql`) | **Already run in production Supabase** by the owner. |

### 4.3 Worker API (`workers/live/v1/pro.js`)
| Route | Auth | Behaviour |
|---|---|---|
| `GET /v1/pro/me` | Supabase JWT | `{pro, status, plan, trial_end, current_period_end, cancel_at_period_end}` |
| `POST /v1/pro/checkout` `{plan: monthly|yearly}` | Supabase JWT | Creates Stripe Checkout (subscription mode, 7-day trial unless the user already had one, `missing_payment_method=cancel`, `payment_method_collection=always`, ToS consent required, custom withdrawal text, billing address required, Stripe Tax on only if `VAT_MODE=registered`). 409 if already Pro. 500 if `VAT_MODE` not explicitly `registered`/`exempt`. |
| `POST /v1/pro/portal` | Supabase JWT | Stripe Customer Portal session (manage card, cancel). |
| `POST /v1/pro/webhook` | Stripe signature | HMAC-SHA256 verify (5-min tolerance) → claim event id in `stripe_events` (idempotency) → apply → on failure or 409 **release the claim** so Stripe's retry is processed. Out-of-order protection via `last_event_created`. |

Exports: `isPro`, `verifyStripe`, `userFromToken`, `supabaseStore`, `applyEvent`, `handlePro`, `proCors`, `TRIAL_DAYS=7`, `GRACE_DAYS=3`, `WITHDRAWAL_TEXT`.

**Entitlement rule:** `trialing` or `active` → Pro. `past_due` → Pro for a 3-day grace period from `past_due_since`. Anything else → Free.

**Safety switches:** `PRO_ENABLED` must be `"true"` or every Pro route returns 404 (prod is `"false"`). Any `sk_live_` key is refused (503) unless `PRO_LIVE="true"` (not set anywhere).

Webhook events subscribed: `checkout.session.completed`, `customer.subscription.created|updated|deleted|trial_will_end`, `invoice.paid`, `invoice.payment_failed`.

### 4.4 Database (Supabase, RLS on both tables)
- `subscriptions`: `user_id` (PK → `auth.users`, cascade delete), `stripe_customer` (unique), `stripe_subscription`, `status`, `plan` (month/year), `price_id`, `trial_end`, `current_period_end`, `cancel_at_period_end`, `past_due_since`, `last_event_created`, `updated_at`. Policy "read own subscription": authenticated users can only `select` their own row. Writes only by the Worker with the service key.
- `stripe_events`: `id` PK (processed Stripe event ids).
- Rollback: `.down.sql` drops both tables.

### 4.5 Sandbox environment (live and working)
- Worker URL: `https://investedia-live-sandbox.adonaykabeya10.workers.dev`
- Stripe: account "Guidify", **Sandbox**. Product **Investedia Pro**, category SaaS – personal use.
  - Monthly price `price_1UYZjiKyZQALj8qFBhmnZjiZ` (€11.99), yearly `price_1UYZl1KyZQALj8qFLUOzcDlM` (€109).
  - Event destination "investedia sandbox", snapshot payload, API version `2024-12-18.acacia` (keep it: newer versions move `current_period_end`).
  - Public details: ToS `https://investedia.com/terms.html`, privacy `/privacy.html`, support `/contact.html`.
  - Note: live mode also has an "Investedia Pro" product with 2 prices (created by mistake first; harmless, can be reused at launch).
- Cloudflare secrets on `investedia-live-sandbox` (set by the owner): `STRIPE_SECRET_KEY` (sk_test), `STRIPE_WEBHOOK_SECRET`, `SUPABASE_SERVICE_KEY` (service_role/secret key; *the anon key causes "event 401"*).
- Test user: `adonaykabeya10+protest@gmail.com` (Supabase user `955df500-…`). **Delete when testing is finished (ask the owner first).**

### 4.6 Sandbox test results (6 Nov 2026)
| Scenario | Result |
|---|---|
| Unsigned webhook | ✅ 400 bad signature |
| Unauthenticated `/me`, `/checkout`, `/portal` | ✅ 401 |
| Checkout: 7-day trial, €0 today | ✅ |
| Webhook → `trialing`, Pro = true | ✅ (after fixing the service key) |
| Second checkout while subscribed | ✅ 409 |
| Portal opens | ✅ |
| Cancel at period end → keeps Pro until trial end | ✅ |
| Cancel immediately → Pro = false | ✅ |
| Returning user → no second trial, €11.99 due now | ✅ |
| Bug found: event claimed before processing, so retries were lost | ✅ fixed + 2 regression tests |
| Renewal after day 7 (test clock) | ⏳ not yet |
| Failed payment → past_due → 3-day grace → loss of access | ⏳ not yet (test clock, card `4000 0000 0000 0341`) |
| `VAT_MODE=registered` run (Stripe Tax) | ⏳ waits for VAT decision |

### 4.7 Known gaps before any live launch
1. **Almost no Pro features exist yet.** Billing works; gated features are designs. Recommendation: don't charge until at least custom alerts + one more (calendar history is quickest) work.
2. Checkout success/cancel URLs point to `/pro.html`, which is not on the live site (404). Publish the page or point to `profile.html`.
3. Terms page needs a Pro section: price, trial, renewal, cancellation, 14-day refund/withdrawal.
4. Stripe statement descriptor is **DROPLATES**: change to e.g. **INVESTEDIA PRO**. Public business name shows "Guidify".
5. Trial-reminder email 24 h before charging (Phase 2, uses `customer.subscription.trial_will_end`).
6. Multiple trials via new email accounts (optional fix: card fingerprint check, documented).
7. Fill company details in legal pages (address, KBO/VAT number); legal check on whether paid directional content is an "investment recommendation".
8. Retire the 4-second sign-up pop-up when Pro launches.
9. Open decision: the proposal caps Free watchlists at 10. That would take something away from Free; recommendation is to drop the cap.
10. Production launch steps (each needs separate approval): live Stripe product/prices/webhook, live secrets on `investedia-live`, `VAT_MODE`, `PRO_ENABLED=true`, `PRO_LIVE=true`, merge `premium-preview`.

**EU withdrawal wording (verified):** customers get a full refund if they withdraw within 14 days. The text must never say they "lose", "waive" or "forfeit" the right (a test enforces this).

### 4.8 Free vs Pro (target)
| Feature | Free | Pro |
|---|---|---|
| News, globe, market and company pages | ✓ | ✓ |
| Market Views (direction, horizon, evidence, risk) | ✓ same | ✓ |
| Track Record, methodology, every past call | ✓ never gated | ✓ |
| Priority Insights | headline + summary | full note (evidence, counterarguments, scenarios, key risk) |
| Long-Term Outlooks | direction + thesis | + historical analog context |
| Alerts | daily digest | custom real-time (price level, % move, volume, new filing) |
| Company event history | recent | full verified history |
| Charts / export | standard | indicators, CSV export |
| New Pro-only tools (planned) | — | earnings-day briefs, portfolio view, calendar history, SEC filing digest, saved screens, weekly personal report, research workspace, data export/API key |

---

## 5. Prediction engines and research

| Engine | Status | Where |
|---|---|---|
| **V5** | **Production.** Generates the public calls / Market Views; outcomes in the public Track Record. Do not change. | `engine/` (`live_v5.py`, `run.py`, …), `engine-v5.yml` |
| V6 | Research, concluded. PEAD and timing studies: **no edge survives** costs and multiple-testing correction. Deterministic extraction ~48% revenue precision, not usable. | branch `engine-v6` |
| **V7** | **Research + shadow only, predictions disabled.** Full walk-forward evaluation 2023→2026 (784 comparisons, Holm-corrected): **0 model families eligible** → selector outputs "No View", Priority disabled. | branch `engine-v6` (`tools/v7/`, `research/ENGINE-V7-REPORT.md`) |
| V8 | Roadmap proposal only | `research/V8-ROADMAP.md` on `engine-v6` |

**V7 key facts:**
- Unified event DB: **96,299 events** 2022–2026 (66,959 earnings + 8-K items), point-in-time features, outcomes at 1/5/10/20 days, timing provenance (`verified-consistent` / `conflict` / `in-session` / `calendar`).
- Found and fixed a **look-ahead leak** in the V6 timing filter (it compared with the next session's gap). V6 results were negative anyway, so no false claim was published.
- Small-cap "accuracy" of 54–58% was a microstructure artifact; models are restricted to ≥ $20M average daily dollar volume.
- 2023–2026 is spent as development data; no clean holdout remains. V8 principle: no more retrospective parameter search; credibility only through prospective (future) evidence.
- **Shadow job** (branch `v7-shadow-job`, disabled): pre-registered hypotheses H1/H2, frozen H2 model with hash, append-only hash-chained ledger on a separate data branch. Earlier bugs fixed (decisions before session open, wrong filing parse, failed price fetch frozen as No View, H2 refrozen without surprise features).
- **Product components** (branch `v7-product`, unreleased): Market View cards show horizon/evidence/key risk/history; Track Record "engine status" panel separating live / shadow / research.

**Haiku extraction pilot** (`tools/v7/haiku_extract.py` on `engine-v6`): approved at a **hard cap of $0.20** (upper-bound estimate ~$0.17, 300 press releases, Batch API, model `claude-haiku-5-5`, strict JSON schema, every number must have a verbatim quote found in the source or it is rejected). **Blocked:** no Anthropic API key in the environment; the owner must add it as a network secret. Run: `python3 -m tools.v7.haiku_extract --execute --set pilot --approved-usd 0.20`. Gate to pass: revenue precision ≥ 90%, recall ≥ 70% on the hand-labelled gold set.

---

## 6. Other completed workstreams (merged unless noted)
- Canonical company identity layer, company chips across the site, typed global search, company page hierarchy, directory, sitemap and routes.
- Canonical **asset registry** + resolver wired into the news robot, prices and globe; rich impact schema; event archive (production-verified).
- Globe lines v3 integrated with the registry; homepage globe shows only orange article → affected-asset lines; globe page green/red/orange with optional relationship and timeline layers; trade routes removed.
- Track-record pipeline audit; backtest pipeline; impact-v2 rules frozen + SEC anchoring; holdout Jun 26 – Aug 24 run with blind manual review; immutable versioned live implication format; event history rebuilt from git (Oct 21–30).
- Yahoo Finance licensing audit (`YAHOO-AUDIT.md`): Yahoo's free feed is not for commercial use, so prices must move to a licensed source before monetisation. Data licensing notes: `DATA-LICENSING.md`.
- BoJ/BoE permission request drafts (`PERMISSION-REQUESTS.md`, not sent).

## 7. In progress / backlog
| Item | State |
|---|---|
| SEC event harvester (8-K/6-K press releases 2021→2026) | in progress |
| impact-v3 rules to ≥ 95% precision on dev window, then validate on untouched 2024 window, then scale to 1,000 validated events | pending |
| 48-hour source test (PIB, Eurostat, ONS, StatCan), measurement only | in progress |
| P2 undrawable-article categories + honest coverage; P3–P4 affected-asset intelligence + article relationships (in progress); P5–P6 measured latency + price correctness; P7–P9 mobile globe gestures, regression audit, Track Record audit | pending |
| AGENTS.md to-dos: Google Auth branding confirmation, submit `sitemap.xml` in Search Console, forward `info@investedia.com` to the owner, delete five `+invtest` users (ask first), place oil/mining stocks at real sites, slogan decision | open |

---

## 8. Branches
| Branch | State | Content |
|---|---|---|
| `main` | production | Live site; robots commit here constantly. |
| `premium-preview` | pushed, not merged | Pro page, proposal, review, billing Worker code, migration, tests. |
| `pro-sandbox` | pushed | Same as `premium-preview`; pushing here deploys the sandbox Worker. |
| `engine-v6` | **local only** (10+ commits, not pushed) | V6/V7 research, V8 roadmap, Haiku pilot code. |
| `v7-shadow-job` | **local only** | Disabled prospective shadow job. |
| `v7-product` | **local only** | Market View card fields, Track Record engine panel. |
| many old `preview/*`, `footer-*`, `globe-*` branches | stale | Ask before deleting. |

The three local-only branches exist in the previous agent's cloud workspace; pushing them needs the owner's approval. If the workspace is gone, they must be recreated from the reports.

---

## 9. Accounts and where things live (no secrets here)
| Service | What | Who holds credentials |
|---|---|---|
| GitHub | `hellaynr1/Investedia` | owner |
| Cloudflare | Workers `investedia-live` (prod), `investedia-live-sandbox` (test), subdomain `adonaykabeya10.workers.dev` | owner |
| Supabase | project `lfjyoeusblhfpmgwbrhj` | owner (service key only in Cloudflare secrets) |
| Stripe | account "Guidify", use **Sandbox** | owner |
| Resend | email sending for `info@investedia.com` | owner (key in Supabase Vault `resend_api_key`) |
| Spaceship | DNS for investedia.com | owner |
| Google | OAuth for login, Search Console | owner |
| Gemini, Pixabay | news robot | GitHub secrets |

Troubleshooting: sign-up "Error sending confirmation email" → Supabase → Logs → Auth; `535` = wrong SMTP credentials (username `resend`, password = Resend key). Webhook 500 `event 401` = wrong Supabase key in the Worker (anon instead of service).

---

## 10. Recommended next steps (in order)
1. Finish sandbox tests with a Stripe **test clock**: renewal after day 7; failed payment → `past_due` → 3-day grace → loss of access.
2. Fix the post-checkout redirect; draft the Pro section of the Terms; change the statement descriptor.
3. Build **custom alerts** (Worker cron + KV) in the sandbox, then **calendar history** (event DB).
4. When VAT is decided: set `VAT_MODE`, run the `registered` scenario if applicable, update pricing copy.
5. Owner approvals, each separately: merge `premium-preview`; live Stripe setup; `PRO_ENABLED`/`PRO_LIVE` in prod.
6. Research track: add Anthropic key → run Haiku pilot (≤ $0.20) → if the gate passes, follow V8 Stage 1; activate the shadow job only after approval.
7. Before monetisation: move prices to a licensed data source.

### Owner decisions pending (noted 2026-11-06)
- **€5 Anthropic API credit:** recommended, with a €5 monthly limit in the Anthropic console. Uses: Haiku pilot (≤ $0.20), then filing digest and earnings briefs for Pro. It does **not** raise prediction accuracy by itself; accuracy can only be proven prospectively, with the V7 shadow job (free) running on future events. The key goes in through the environment's secure credential form when the owner says "add key"; shadow job activation needs "activate shadow".
- **Making the repo private:** pushing still works through the owner's GitHub app connection. Risks to check first: GitHub Pages on a private repo needs GitHub Pro, otherwise investedia.com goes down; private repos have limited Actions minutes (2,000/month on Free), which the robots would exceed. Options: GitHub Pro + spending limit, or serve the site from a separate public repo / Cloudflare Pages.

## 11. Key documents
`AGENTS.md` (rules, build, robots) · `WORKFLOW.md` (owner's weekly routine) · `design/PRO-PROPOSAL.md` · `design/PRO-PHASE1-REVIEW.md` · `design/CODEX-ACCEPTANCE-PROTOCOL.md` · `workers/live/README.md` · `NEWS-PIPELINE.md` · `DATA-LICENSING.md` · `YAHOO-AUDIT.md` · `LEGAL-TODO.md` · `LEGAL-REVIEW-PACK.md` · `RELEASE-CHECKLIST.md` · `research/` (engine reports; V7/V8 on `engine-v6`).
