# Investedia: guide for AI agents (Codex, ChatGPT, Claude Code, OmniRoute)

Read this whole file before changing anything. The owner is not a developer: explain in plain words and show results.

## What this is
investedia.com: a free investing-information website (markets, news, tools, a live world globe), built as a **static site** on GitHub Pages. Prices are real (Yahoo Finance, FRED), refreshed by GitHub Actions. Information and education only, never investment advice.

## Owner's rules (always follow)
1. **Never put anything live without the owner's "push" / "go".** Work on a branch (`git checkout -b preview/<topic>`), push the branch, show screenshots (PC 1440px wide + phone 390px), then merge to `main` only when told.
2. If the owner mentions one device (PC or phone), change only that one; suggest the other and show it first.
3. Always check on phone width.
4. Real data only, no fake content. Keep "Not investment advice" visible.
5. Design: black, dark-first, minimal (Stripe-like, no "AI slop", little glow). Accent orange `#FF7A1A`; green/red only for up/down, no multicolour. Fonts: Inter (text), Geist Mono (numbers). Wordmark "Investedia" with the font's own i-dot in orange.
6. **Secrets:** never commit `.env`, API keys, the Supabase service_role key, the Google client secret or the Resend key. Only the Supabase *publishable* key may be in the code (it is in `assets/ui.js`).
7. Never delete files, data, accounts or keys without asking.

## How the site is built
- Pages live in `src/pages/*.html` (first line is JSON: title, desc, key). `python3 build.py` wraps them with the shared head/header/footer and writes the root `*.html` files **and** mirrors everything to `docs/`. GitHub Pages serves `docs/`.
- **Always run `python3 build.py` after editing**, and commit both the source and the generated files.
- Shared UI: `assets/ui.js` (header, menus, search, login popup, watchlist, analytics tracking) and `assets/app.css`.
- Market data for most pages: `assets/mock.js` + `assets/quotes.js` (refreshed by `update_market.py`).
- World globe: source in `tools/globe/` (`head.html` = CSS/layout, `script.js` = behaviour). Build with `python3 tools/globe/build.py && python3 build.py`. Its prices refresh via `update_globe.py`. It is embedded on the homepage (hero, `?mode=hero`) and on `globe.html`.
- GitHub Actions (`.github/workflows/update-market.yml`) commit fresh prices/news every ~10 minutes. **Always `git pull --rebase origin main` before you push**, or the push is rejected.
- Preview locally: `cd docs && python3 -m http.server 8765` then open http://localhost:8765.

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
- Delete the test users `adonaykabeya10+invtest1…5@gmail.com` in Supabase (ask first).
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
