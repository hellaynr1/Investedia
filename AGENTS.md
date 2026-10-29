# Investedia: guide for AI agents (Codex, ChatGPT, Claude Code, OmniRoute)

Read this whole file before changing anything. The owner is not a developer: explain in plain words and show results.

## What this is
investedia.com: **investing media for everyone**. A news-first website: the world's financial and business news on one live globe, with what happened, where, and why it matters to your money. Slogan: **"Invest with clarity. / See the world move."** Static site on GitHub Pages. Information and education only, never investment advice.

**Direction (Oct 2026):** news first, not a trading/price site. Do not add live price tickers, screeners, gainers/losers or TradingView-style pages. Old market pages still exist but are out of the menu; ask before changing or deleting them.

## Owner's rules (always follow)
1. **Never put anything live without the owner's "push" / "go".** Work on a branch (`git checkout -b preview/<topic>`), push the branch, show screenshots (PC 1440px wide + phone 390px), then merge to `main` only when told.
2. If the owner mentions one device (PC or phone), change only that one; suggest the other and show it first.
3. Always check on phone width.
4. Real data only, no fake content. Keep "Not investment advice" visible.
5. Design: black, dark-first, minimal (Stripe-like, no "AI slop", little glow). Accent orange `#FF7A1A`; green/red only for up/down, no multicolour. Fonts: Inter (text), Geist Mono (numbers). **Apple-like feel (owner request):** generous whitespace, large clean type, soft glass and rounded corners, subtle motion, few elements per screen, nothing busy. **Up/down must be obvious:** show direction as a clear arrow only (↑ green, ↓ red, ↔ grey) in a round badge, never the words Up/Down (owner finds them childish). Wordmark "Investedia" with the font's own i-dot in orange.
6. **Secrets:** never commit `.env`, API keys, the Supabase service_role key, the Google client secret or the Resend key. Only the Supabase *publishable* key may be in the code (it is in `assets/ui.js`).
7. Never delete files, data, accounts or keys without asking.
8. **Label every option on the image itself.** Whenever you show design options, put a clear label (A, B, C or 1, 2, 3, plus a 2-3 word name) printed on each screenshot or mock-up image, big enough to read at a glance, and use the same labels in the message. The owner receives many screenshots and must be able to decide from the image alone. Also label before/after images ("Now" / "New") and PC / phone.
9. **A chosen design is finished only when every visible element of the chosen mockup exists in the build** (including numbers such as % changes). Follow `design/CODEX-ACCEPTANCE-PROTOCOL.md` for every task and PR: numbered acceptance criteria, a data map, one test per criterion, and a built-vs-mockup screenshot table. Missing data means stop and report, never ship a different design.

## How the site is built
- Pages live in `src/pages/*.html` (first line is JSON: title, desc, key, optional scripts). `python3 build.py` wraps them with the shared head and writes the root `*.html` files **and** mirrors everything to `docs/`. GitHub Pages serves `docs/`.
- **Always run `python3 build.py` after editing**, and commit both the source and the generated files.
- Shared UI: `assets/ui.js` (menu Home · Globe · News · Learn · Tools · About, login popup, footer, analytics) and `assets/app.css`.
- **Homepage** `src/pages/index.html` + `assets/home-news.js` + `assets/home-news.css` (classes prefixed `hn-` so they never clash with app.css): globe hero, top stories, why it moved, countries, markets open now, upcoming events + earnings, free-resources strip.
- **Globe News page** `assets/globe/news.html`, source in `tools/globe-news/` (`page.html`, `build.py`). Build: `python3 tools/globe-news/build.py && python3 build.py`. `?embed=1` gives the globe alone (used by the homepage).
- **Robots (GitHub Actions):**
  - `broad-news.yml` every 30 min: `update_globe_news.py` (GDELT + ECB/Fed/BoE feeds, Gemini picks and summarises, Pixabay topic photos) → `assets/globe/news-live.json`; `update_calendar.py` (ForexFactory events, Nasdaq earnings) → `assets/calendar-live.json`.
  - `update-economy.yml` weekly: `update_economy.py` (World Bank) → `assets/globe/economy.json`.
  - `update-market.yml`: old price data (still used by Tools pages).
  - Secrets in GitHub: `GEMINI_API_KEY`, `PIXABAY_KEY`. Brandfetch logo Client ID is public, in `tools/globe-news/page.html`.
- Robots commit to `main` often: **always `git pull --rebase origin main` before you push.**
- Preview locally: `cd docs && python3 -m http.server 8765` then open http://localhost:8765.
- News rules: never copy articles or photos; every story keeps source name, link and time; AI summaries are labelled "AI-assisted"; topic photos are labelled "Illustration". No Wikimedia images.

## Accounts, emails, analytics (Supabase project `lfjyoeusblhfpmgwbrhj`)
- Login popup: Google + email/password (Supabase Auth). Header account menu with Log out; `profile.html` saves to the account (user metadata).
- Tables (row-level security on): `watchlists` (one row per user), `events` (privacy-friendly analytics: no cookies, no IDs; only the owner's emails can read).
- Owner-only analytics dashboard: `admin.html` (owners listed in `OWNERS` in `assets/ui.js` and in the `events` select policy).
- Emails from `info@investedia.com` via Resend (DNS at Spaceship). Templates and setup SQL in `emails/`. "Confirm your email" = Supabase template; "Welcome" = database trigger `on_email_confirmed` reading the Resend key from Supabase Vault (`resend_api_key`).
- If sign-ups fail with "Error sending confirmation email": check Supabase → Logs → Auth. `535` = wrong SMTP username/password (username is `resend`, password = Resend API key).

## Open to-do list (as of 2026-10-17)
- Google Auth Platform → Branding: after 24 h, "J'ai corrigé les problèmes" (domain verified in Search Console).
- Search Console: submit `sitemap.xml`.
- Forward `info@investedia.com` to the owner's Gmail (Spaceship email forwarding or ImprovMX) so replies arrive.
- Delete the five `+invtest` test users (aliases of the owner's mailbox) in Supabase (ask first).
- Globe: place oil/mining stocks at their real mines and oil fields (only where relevant).
- Later: news on the globe (Pro feature); weekly analytics summary into the owner's Second Brain.
- Before making money from the site: move prices to a licensed data source (Yahoo's free feed is not for commercial use).
- Slogan decision: keep "Invest with clarity." or go back to "Understand every market move."

## Weekly workflow
The owner's weekly routine (research, content, small site tasks, review) and the prompts are in **WORKFLOW.md**.

## Working style
- Small, focused changes; one commit per change with a clear message.
- Show screenshots (Playwright works: `npx playwright screenshot`), not descriptions.
- Explain what the owner must do themselves (Supabase, Google, Resend, DNS) as numbered click-by-click steps.

**Voice and wording (owner rule):** the audience is professional and educated investors who will pay for the product. Say **article(s)**, never "story/stories" in visible text (URL parameters and code identifiers such as `story.html` and `?story=` stay as they are for compatibility). Use precise financial vocabulary (basis points, yield, spread, guidance, drawdown, volatility, positioning), a newsroom register like Reuters/Bloomberg, no "for beginners", no "explained simply", no cutesy copy. Keep "Not investment advice".
