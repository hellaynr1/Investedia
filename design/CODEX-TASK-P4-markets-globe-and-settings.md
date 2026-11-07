# Codex task P4: Markets mode on the homepage globe (design D) + header Settings (currency, language)

Read `AGENTS.md` and `design/CODEX-ACCEPTANCE-PROTOCOL.md` first. Branch `codex/p4-markets-globe` from `main` (after P1 is merged).
Open a pull request. **Do not merge.** Approved mockup: `design/markets-globe/D-desktop-markets-nigeria.png`.

## Part 1. News / Markets globe on the homepage (approved design D)
Source: `tools/globe-news/page.html` (globe, also embedded on the homepage with `?embed=1`) and `src/pages/index.html` (homepage).
Rebuild with `python3 tools/globe-news/build.py && python3 build.py`.

1. **Switch.** A segmented `News | Markets` control **next to the bottom-right "Open globe" button** (left of it, same height),
   as in the mockup. News is the default. The choice is kept in the URL (`?mode=markets`) and sent to the globe iframe.
2. **Caption.** One short line under the switch's row (or in the globe's top area) that says what the globe shows:
   News: "Live news map · last 48 h · each light = where news happened · lines = markets it affects".
   Markets: "World markets · each ring = a stock exchange · lines = trade (orange) and investment (white)".
3. **Search + CTA follow the mode.** Markets: placeholder "Search countries, exchanges, indices & companies", CTA "Explore markets"
   (links to the Globe page in Markets mode). News: unchanged ("Open globe").
4. **Markets layer on the same renderer** (same camera, rotation, lighting; no new library):
   - One marker per stock exchange / benchmark (from `assets/globe/markets.json` `g === 'Index'`, plus exchanges in
     `data/exchanges.json` from P1). Thin white ring; selected = brighter ring + soft orange glow.
   - Atlas labels (exchange short name + country, small caps, Inter 9.5 px) only for the selected market and the markets connected
     to it; skip any label that would overlap another label or sit behind the panel.
   - Lines only when a country is selected: **trade = orange solid**, **investment = white, lower opacity**. Data must be real:
     add a small generated file `assets/globe/market-links.json` from public sources (UN Comtrade top bilateral trade partners;
     IMF CPIS portfolio investment), with source + year per link. No file → no lines (never random arcs).
   - News mode is unchanged.
5. **Country panel (desktop, right side, rounded 16 px, max height ends above the Open globe button):**
   region · "Market" eyebrow; flag + country name in **Inter** (not serif); "Exchange (short) · city · currency";
   3 KPI tiles: benchmark index, currency vs USD, inflation (year · World Bank) — numbers in **Inter, tabular figures**, 15 px 600;
   missing data shows "—" and "no data yet" (never invented numbers);
   "Notable developments" (2 newest important articles for that country, max 2 lines each, link "N →" to the country's news);
   **Market Momentum** with three one-line tabs **Performers / Attention / Sectors** (30 days):
   Attention = companies with the most verified article mentions (count shown); Sectors = article counts per sector;
   Performers = only when licensed historical prices exist (state period and date), otherwise an explanation, no numbers;
   footnote "Not a recommendation."; button "Explore <country> →" (country page from P1); legend Trade / Investment.
6. **Phone (390 px):** switch above the globe; the panel is a bottom sheet (max 55% height, drag handle); globe stays usable;
   at most 5 lines at once.
7. Selecting: click/tap a market ring or a country; Esc / tap outside closes the panel.

## Part 2. Header Settings (replace the "$" currency button)
Source: `assets/ui.js` (header, footer, currency picker around the "live prices" helpers), `assets/app.css`.

1. Replace the header's currency button with a **settings (gear) icon button** (same size/style as the other header icons; on
   phones keep it in the header too). It opens a small popover with two rows:
   - **Currency:** USD, EUR, GBP, JPY, CHF, CAD, AUD, plus local currencies where we have rates (at least NGN, ZAR, INR, BRL).
   - **Language:** the same languages as the footer language selector (it uses `assets/locale.js` + `assets/locales/<lang>.json`,
     first-party, no third-party script). Move the control to this popover; the footer may keep a link "Language" that opens it.
2. **Make the currency setting actually work:** when a currency is chosen, every displayed price and market value that is in USD is
   converted using the rates the site already fetches (the free exchange-rate feed in `ui.js`, refreshed every 30 s), formatted with
   the right symbol and decimals; percentages are not converted; assets quoted in their own currency (e.g. a JSE share in ZAR) keep
   their currency unless the user chose to convert all (keep it simple: convert USD-quoted values only, and label converted values
   with the currency code). The choice is saved (localStorage) and applied on every page.
   No conversion data → show original values, never wrong numbers.
3. Accessibility: button has a label, popover is keyboard reachable, Esc closes it.

## Do not change
Frozen predictions, Track Record, `v5-*`, the news robots, event/archive data, globe camera/position/size/animations, News mode,
colours (black, orange `#FF7A1A`), fonts (Inter, Geist Mono for prices elsewhere). No new pages, no new dependencies, no secrets.

## Acceptance criteria
1. Homepage: News is default; switching to Markets shows rings, no lines until a country is selected; Nigeria selected shows the
   panel exactly as in the mockup (content from real files; screenshot side by side with the mockup).
2. Every line in Markets mode comes from `market-links.json` with a source and year (test reads the file and the drawn lines).
3. Panel never covers the Open globe button or the switch on 1440 px; bottom sheet on 390 px leaves the globe visible.
4. No text overlap between atlas labels (bounding-box test, 0 overlaps).
5. Settings: gear icon replaces "$"; currency change converts a USD price on the homepage and on an asset page, persists after reload.
6. Language in Settings switches the page language the same way the footer selector did.
7. Phone frame time (iPhone 13 emulation, 4x CPU) in Markets mode within 15% of News mode.
8. No console errors on PC and phone; `build.py` clean; tests that pass on `main` still pass.

## PR must include
Built-vs-mockup screenshots (PC 1440 + phone 390, News and Markets, Nigeria selected, Settings open), the data sources for
`market-links.json`, test results and the list of files changed.
