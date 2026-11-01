I'm improving the design of my website **Investedia** (investedia.com) and want your help as a senior product/UI designer. Below is the full current design system and page structure. Give concrete, implementable suggestions (exact CSS values, spacing, components), keeping the existing identity. The site is plain HTML/CSS/JS (no framework), static on GitHub Pages, so suggestions must work as plain CSS + small vanilla JS.

## Product
Financial news and market intelligence. Hero = a live 3D **news globe** (canvas) showing where market-moving news happens, with lines from a story's location to affected countries/assets. Each important story can carry a short-term "call" on an asset (Long/Short) that is later judged against the real price (Market Implications + Track Record pages). Audience: retail investors who want clarity, not noise. Tone: calm, precise, "terminal-grade", trustworthy. Informational only, never "buy/sell now"; footer always says "Not investment advice".

## Brand
- Name: Investedia. Logo: a small orange line-chart mark on a black rounded square (28×28, radius 7). In the wordmark, the dot of the "i" is orange.
- One accent colour: orange **#FF7A1A** (hover #FF9147). Everything else is neutral.
- Personality: dark, dense, data-first, hairline borders, one warm accent.

## Design tokens (CSS variables)
Dark (default):
```
--bg:#0A0A0B; --bg-2:#111113; --card:#171719; --card-hi:#1d1d20;
--line:#29292D; --line-soft:#1f1f23;
--fg:#FFFFFF; --fg-2:#A1A1AA; --fg-3:#a1a1aa;
--accent:#FF7A1A; --accent-hi:#FF9147; --accent-soft: accent at 12%;
--up:#22C55E; --down:#ff7373; --up-soft:rgba(34,197,94,.12); --down-soft:rgba(240,68,68,.12);
--r:10px; --r-sm:6px; --head:64px (header height)
```
Light theme ([data-theme="light"]):
```
--bg:#F7F7F8; --bg-2:#FFFFFF; --card:#FFFFFF; --card-hi:#F3F3F5; --line:#E4E4E7; --line-soft:#EEEEF0;
--fg:#0A0A0B; --fg-2:#52525B; --fg-3:#8A8A93; --up:#15803D; --down:#DC2626
```
Homepage overrides: --card:#121214, --bg-2:#0B0B0D (dark); light resets them to white.

## Typography
- UI: **Inter** (fallback Geist, system-ui). Body 14px / 1.5, antialiased.
- Numbers: Apple system numerals (-apple-system / SF Pro) with tabular-nums; code/labels: **Geist Mono**.
- Hero title: 2 lines, white line + grey line, 56px (auto-shrinks to fit), weight 600, letter-spacing -0.04em, line-height 1.04.
- Section eyebrows: small uppercase labels in orange/grey; section titles ~26px.

## "Aurora" skin (dark mode only)
- Soft colour glow behind the top of pages: radial gradients of orange (rgba(255,122,26,.4)) top-left and violet (rgba(120,80,255,.3)) top-right.
- Frosted-glass cards: background rgba(255,255,255,.045) + backdrop-filter blur(30px), hairline borders.
- Big page titles use a white→grey vertical gradient text; highlighted words use an orange gradient (#ff7a1a→#ffb347).
- Change pills glow softly green/red.

## Layout
- Content width max 1360px, side padding 24px (16px on phones, safe-area aware).
- Sticky header (64px), translucent dark with blur, bottom hairline. Nav: Home, Globe, News ▾, Markets, Learn, Tools ▾, About; active item has a 2px orange underline.
- Header tools: currency symbol button ($/€/£ round), notifications bell, Log in (ghost), Sign up (orange), light/dark button. On phones: bell, light/dark, menu; currency moves into the menu.
- Phone menu: full-screen drawer with large rows, hairline separators, account buttons pinned at the bottom.

## Homepage
1. **Hero**: full-width globe canvas (height ~min(820px, 100vh-64px)); text column on the left over a dark-to-transparent gradient: orange "Updated Xm ago" live pill, 2-line title "Invest with clarity. / See the world move.", lead paragraph (18px, grey), search bar (52px tall, radius 14, translucent), "Popular searches" chips with asset logos (Nvidia, Apple, Microsoft, Tesla, Bitcoin). "Open globe" pill bottom-right. On phones the globe sits below the text and continues behind the search bar.
2. Light/dark switch: the new theme spreads in a circle from the pressed button (View Transitions, 0.65 s); the globe changes from night to day (palette blend + a moving day/night terminator line) in 0.8 s.
3. Resource strip ("Learn alongside the best free resources": Morningstar, Yahoo Finance, Khan Academy, FRED, CoinMarketCap…).
4. "What matters right now": 1 large + 4 small article cards with photos, flags, category labels, source and time.
5. "Articles the market confirmed".
6. "Explore by country": horizontal country chips with flags and article counts.
7. Two boxes: Upcoming economic events (time, flag, event, impact bars in orange) and Upcoming earnings (logo circle, company, EPS estimate).
8. Sign-up band, disclaimer, footer (5 link columns + legal row).

## Globe (canvas)
Dark: black space with a faint galaxy and stars, dotted land, orange glowing city markers with numbered circles, orange arcs between locations, a thin orange rim. Day mode: pale blue sky, light globe, grey land dots, dark labels. Lines are attached to the globe (rotate with it) and the far side is hidden.

## Market Implications / Track Record / call pages
- Time filters as segmented control (24H / 7D / 30D / All).
- Summary row: Confirmed (green), Went the other way (red), No clear move, Pending (orange).
- Filter chips (All, Confirmed, Other way, No clear move, Pending).
- Call cards: asset logo + ticker + name, Long/Short label, headline, article time, signed result (+5.15% green / −3.83% red), small price chart with markers.
- Track Record: big number boxes ("Building — X of 50 judged calls" until 50 calls), KPI tiles, groups (Direction, Tier, Event type), full list of every call.
- Pages refresh by themselves every ~45 s when new calls arrive (no reload).

## Constraints
- Mobile performance matters (iPhone): avoid heavy blur stacks, keep animations GPU-friendly, respect prefers-reduced-motion.
- Accessibility: AA contrast in both themes, visible focus (2px orange outline), 44px touch targets.
- No new paid fonts/assets; images from free sources; keep "Not investment advice".

## What I want from you
1. Critique: what feels dated, cluttered or inconsistent?
2. A refined token set (colours, spacing scale, radius scale, shadow/glow scale) for dark and light.
3. Typography scale (sizes, weights, line-heights) for hero, section titles, cards, data.
4. Component upgrades: header, hero, search bar, chips, cards, call cards, KPI tiles, segmented controls, buttons.
5. Micro-interactions that feel premium but cheap to run on phones.
6. Any layout changes for the homepage order and the phone layout.
Give answers as CSS I can paste, grouped by component.
