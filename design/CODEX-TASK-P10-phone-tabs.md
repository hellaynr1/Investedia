# Codex task P10: phone tabs (Globe, News, Countries, Markets) — owner request 2026-11-07
> Note: the bottom nav is changed by P11 ("no double News/Markets on phone"); follow P11 for navigation.

Read `AGENTS.md` and `design/CODEX-ACCEPTANCE-PROTOCOL.md`. Branch `codex/p10-phone-tabs` from `main` (after P4). PR, **do not merge.**
Mockups (real data): `design/phone-tabs/T2-globe.png`, `T2-news.png`, `T2-countries.png`, `T2-markets.png`. Source: `tools/globe-news/page.html`
(phone layout ≤ 760 px) and the bottom navigation Globe / News / Markets.

## 1. Globe tab: swipe through articles
Today one article card shows. Make it a horizontal, snap-scrolling carousel of the articles in the current window (newest/top first):
card = category (orange, small caps) · source · country, headline (max 3 lines). Page dots (max 5, the active one long) and a
"1 / N" counter. Swiping a card flies the globe to that article's place and highlights its dot; tapping opens the article.
Lazy-render: only the visible card ± 2 exist in the DOM. Works with touch, mouse drag and keyboard arrows.

## 2. News tab: Apple-like, professional typography
Font stack `-apple-system, "SF Pro Text", Inter, system-ui` for this tab; title 32 px/700, -0.02em; headlines 15.5 px/600;
meta 12.5 px #8e8e93; 0.5 px separators #2c2c2e; thumbnails 62 px rounded 10 px. Segmented control Top / Latest / Countries.
**AI notices only where due:** do not show "AI-assisted" labels in the list or cards. Show the notice once, small, inside the article
view next to the Investedia summary only ("Summary written with AI from the source's headline and description"). Keep the site-wide
AI disclosure page. Never remove "Not investment advice" from article pages.

## 3. News › Countries: a real directory
Search field (filters as you type), region chips (All, Americas, Europe, Africa, Asia, Middle East, Oceania), "Most active" section
(top 10 by articles in the window), then **every country with news A–Z** with an index rail on the right. Row: flag, name, article
count, chevron; tap opens the country panel from P1. Today only 3 countries show: show all of them.

## 4. Markets tab: a real markets view, not a filter
Replace the filter behaviour with a page: title "Markets", "Delayed prices · tap any row for its page", segmented Overview / Indices /
FX / Commodities. Overview = Indices (4), Currencies (2), Commodities (2), Biggest moves today (stocks, by absolute % move).
Each row: name, sub-label (country or symbol), price (tabular figures), move (↑ green / ↓ red, the site rule). Tap → the existing
asset page. Data: `assets/globe/markets.json` only; respect the currency setting from P4 (label converted values). Pull-to-refresh
re-reads the file. Empty / loading / error states designed (skeleton rows, "Prices unavailable, try again").

## Acceptance
1. Built-vs-mockup screenshots at 390 px for all four screens. 2. Carousel: swipe changes the globe focus; 60 articles scroll without
dropping frames below today's 48H baseline by more than 15%. 3. Countries list count equals the countries in the window.
4. No "AI-assisted" text in lists/cards (test). 5. Markets rows link to asset pages; prices match `markets.json`.
6. No console errors; PC layout unchanged; tests from `main` pass.

## Change (owner): Countries list, no A–Z index
Remove the A–Z letter strip on the right side. Keep search, region chips and the full list grouped by letter headers.
Style: professional finance app (Bloomberg / Yahoo Finance / Reuters), not a full iOS contacts copy: Inter, glass rows, flag · name · article count.
