# Codex task P1: Global Markets: country markets panel (A) and continent explorer (B)

Read `AGENTS.md` and `design/CODEX-ACCEPTANCE-PROTOCOL.md` first. Start **after P0 is merged**. Branch `codex/p1-global-markets`,
open a pull request, **do not merge**.

Mockups (real data, approved layouts A + B; phone C + D):
`design/global-markets/M-A.png` (country panel, PC), `M-B.png` (continent explorer, PC), `M-C.png` (country sheet, phone),
`M-D.png` (continent list, phone). Build what they show. Every visible element must exist with real data, or be clearly marked
as missing data ("no data yet"); never fake values.

## No new pages
Everything lives in the existing Globe page side panel (PC) and bottom sheet (phone), source `tools/globe-news/page.html`.
- **A (country)** extends the existing country view `openCountry()` (around line 1446).
- **B (continent)** appears when a region is chosen in the existing Region control (`F.region`, `REGIONS`), above the article
  list, without removing the article list.

## Data (all already in the repo; reuse, do not duplicate)
| Need | Source |
|---|---|
| Benchmark index, currency, country ETF, price, % move | `assets/globe/markets.json` (`k` = country name, `g` = 'Index', `t` = 'fx' / 'stocks') |
| Listed companies per exchange | `data/registry.json` → `assets` with `class: 'equity'`; exchange = MIC in the id (`EQ:XJSE:...`) |
| Company pages / logos | `data/companies.json`, existing company links (`company.html?...`), existing logo helpers |
| Macro (GDP, inflation, unemployment, population) | `assets/globe/economy.json` (World Bank) |
| Country news | articles already loaded on the globe (and P0 day files for 7D/30D), filtered by `location.country` |
| Article counts per country | same loaded articles, current time window |

### New small data file (only addition allowed)
`data/exchanges.json`: about 60 exchanges keyed by ISO 10383 MIC: `{ "XJSE": { "name": "Johannesburg Stock Exchange",
"short": "JSE", "city": "Johannesburg", "country": "ZA", "currency": "ZAR", "central_bank": "South African Reserve Bank" } }`.
Use only public, verifiable facts (ISO 10383 list, exchange and central-bank websites). Cover at least every MIC present in
`data/registry.json`, plus NGX (XNSA), Nairobi (XNAI), EGX (XCAI), Casablanca (XCAS), Ghana (XGHA), Tadawul (XSAU),
ADX (XADS), DFM (XDFM), Qatar (DSMD), Boursa Kuwait (XKUW), Bahrain (XBAH), IDX (XIDX), HOSE (XSTC), SET (XBKK), PSE (XPHS).

## Panel A: country (PC side panel, phone bottom sheet)
Header: continent · "Country", flag, name; line "<exchange short> · <currency> · <central bank short>".
Tabs: Overview / News (count) / Companies (count) / Markets.
Overview: 3 KPI tiles (benchmark index level and % move, currency vs USD and % move, inflation and unemployment with year);
"Latest market developments" (3 newest important articles, link "All N →" opens the News tab); "Listed companies · <exchange>"
(4 rows, largest moves first, link "N →" opens Companies tab); "Also listed abroad" chips (same company listed on another
exchange, from registry listings).
Companies tab: all registry equities for the country's exchanges, with move and link to the company/asset page.
Markets tab: index, currency, country ETF(s), all with price, day and 7-day move. Missing → "no data yet".
Up/down: arrow only, green/red (AGENTS.md rule 5). "Prices delayed. Not investment advice." at the bottom.

## Panel B: continent (when a region is selected)
Title = continent; line "<n> countries · <n> exchanges with data · <window>".
Region tabs (Americas, Europe, Africa, Middle East, Asia, Oceania) = same as the existing region control.
"Countries by news activity (<window>)": rows flag · name · exchange short · currency · article count; tap → panel A.
"Exchanges & benchmarks": index rows with move; missing index → country ETF row marked "ETF".
"Currencies vs USD": chips with move.
"Underserved: few articles, worth a look": countries in this continent with 1–9 articles in the window.

## Do not change
Frozen predictions, Track Record, `v5-*`, news robot, registry contents (except reading), homepage, globe position/size/
animations, connection logic, colours/fonts. No new pages, no new dependencies, no secrets, no fake data.

## Acceptance criteria
1. PC: clicking South Africa shows panel A with JSE All Share level/move equal to `markets.json`, USD/ZAR, inflation 3.2% (2025),
   and 23 JSE companies in the Companies tab.
2. Phone: same content as a bottom sheet (layout C); fits 390 px without horizontal scroll.
3. PC: choosing Africa shows panel B (layout B) with countries ordered by article count, equal to the counts on the globe.
4. Phone: layout D.
5. Every number shown comes from the listed files (test compares panel values to the files for 5 countries:
   ZA, NG, SA, IN, BR).
6. Missing data shows "no data yet"; no placeholder numbers anywhere (test scans the panel text for "NaN", "undefined", "null").
7. `data/exchanges.json` covers every MIC in the registry; test fails on any missing MIC.
8. Article list, filters, time window, connections and the P0 timeline still work (existing checks pass).
9. No console errors; PC 1440 px and phone 390 px screenshots.
10. `python3 tools/globe-news/build.py && python3 build.py` run clean; tests in `tests/` that pass on `main` still pass.

## PR must include
Built-vs-mockup screenshot table (A, B, C, D next to M-A…M-D), labelled PC/phone, the data map (element → file → field), test
results, files changed.
