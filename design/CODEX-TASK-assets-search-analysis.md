# TASK: Many more assets per sector, a search bar inside every sector pop-up, a richer asset pop-up, and 7-day / 30-day articles and analysis for every asset

Read `AGENTS.md` first and obey it, especially: work on a branch `preview/assets-search-analysis`, never push to `main`, show screenshots (PC 1440 and phone 390) and wait for the owner's "push"; **rule 8: whenever you show options, print the option label (A, B, C or 1, 2, 3) on the image itself** (`python3 tools/label-image.py in.png out.png "A" "Short name" "PC"`); say "article(s)" never "story"; arrows only for direction; real data only; no secrets in the repo; never delete files or data without asking; keep "Not investment advice".

Already on `main` and to build on (read these first): `assets/peek.js` (`InvPeek.open(sym)` asset pop-up, `InvPeek.panel(html, hash)` sector pop-up, search overlay), `assets/markets-heat.js` (`SGRP` sector rules, `sectorMovers`, `sectorHtml`, shared `tbl()`), `assets/asset-page.js` + `asset-page.css` (asset page, also shown inside the pop-up with `?embed=1`), `assets/asset-icons.js`, `assets/prefs.js` (`InvPrefs.fmt`, per-asset currency via the `cur` field), `assets/globe/markets.json` (asset universe, fields `s n k c la lo r m t g site cc cur p d w sp`), `update_globe.py` (refreshes the universe from Yahoo and writes `cur`), `tools/add-companies.py` (adds companies after validating them on Yahoo; extend it, do not duplicate it), `tools/gen-worker-symbols.py` (price Worker symbol list), `update_asset_analysis.py` + `assets/globe/analysis.json` (move analysis today), `update_globe_news.py` + `assets/globe/news-live.json` / `news-archive.json` (news pipeline), `.github/workflows/*.yml` (robots). After editing run `python3 build.py && git checkout -- docs/assets/data.js`. Run robots' scripts locally to fill data, but pull `main` first because robots commit often (`git pull --rebase origin <branch>`).

## 1. Many more assets in every sector (target: 40 to 150 companies per sector, 600 to 1,500 in total)
- Extend `tools/add-companies.py` (data lists in the script, one row per company: symbol, name, group, country, city, lat, lon, region, cc). Validate every symbol on Yahoo before adding; skip and report the ones that fail. Use real headquarters cities and coordinates.
- Coverage per sector (the sector tiles are defined in `assets/sectors.js`, selection rules in `SGRP` in `assets/markets-heat.js`): Technology, Semiconductors, Energy, Banks & Finance, Healthcare, Consumer & Retail, Autos, Industrials, Aerospace & Defence, Materials & Mining, Utilities, Real estate, Insurance, Communication, Crypto. Include large caps first (S&P 500, Nasdaq-100, Euro Stoxx 50, FTSE 100, Nikkei 225, Hang Seng, major EM names via their US ADR tickers), then mid caps. Prefer US-listed tickers and ADRs because the price pipeline uses the Yahoo symbol directly; for other exchanges use the Yahoo suffix (`SAP.DE`, `7203.T`) and make sure `update_globe.py`, `ysym()` and the `known()` filter in `markets-heat.js` (which currently hides symbols containing digits or dots) handle them: relax `known()` to hide only assets with missing prices or absurd moves, and check each non-USD listing shows the right currency through the `cur` field.
- ETFs: add 60 to 100 sector and thematic ETFs and mark them `g: 'ETF'` (SPY, QQQ, IWM, VTI, VOO, XL* sector funds, SMH, SOXX, ARKK, GLD, SLV, USO, TLT, EEM, VWO, IEMG, EWJ, FXI, and the main UCITS ETFs available in Belgium: IWDA.AS, VWCE.DE, SXR8.DE, EUNL.DE). ETFs are searchable but excluded from "companies" counts.
- Each new asset needs: a row in the universe, a logo or a centred initial tile (see `asset-icons.js`; no Wikimedia images; follow licences), an entry in `tools/gen-worker-symbols.py` output (tier A for the top 150 by market importance, tier B for the rest), and for the top 500: daily history in `assets/hist/<SYM>.json` with `hi52`/`lo52` (extend `update_market.py`, keep run time under 10 minutes by batching).
- Performance: `markets.json` must stay under about 2.5 MB gzipped. If it grows past that, split it into `markets-core.json` (indices, commodities, FX, crypto, top 300 companies) and `markets-all.json` loaded lazily by the sector pop-up and the search overlay. Keep first paint of Markets unchanged.
- Never invent data: market cap, P/E and dividend yield stay out until a legitimate free source is wired (see section 6).

## 2. Search inside every sector pop-up
- In the sector pop-up (`sectorHtml` in `markets-heat.js`, shown by `InvPeek.panel`) add a search field at the top: "Search 72 companies in Semiconductors". It filters all companies of the sector by name, ticker and country as you type (fuzzy, accent-insensitive, same ranking as the main search).
- Under the field: sort control (Largest move · Name · Price · Market cap when available), a country/region filter (chips: All, North America, Europe, Asia, Other), and a counter "Showing 24 of 72".
- The table must handle 150 rows smoothly: render the first 25 rows, then "Show more" (or windowed rendering with fixed row height), keep keyboard access (↑ ↓ Enter), `aria-live` for the counter, and no layout shift. Row click opens the asset pop-up and Back returns to the sector pop-up with the search text preserved.
- Same behaviour on phone (bottom sheet, 44 px touch targets).
- Reuse the shared `tbl()` and the Aurora look (`assets/skin.css`).

## 3. Asset pop-up: calmer and richer (first fix, then add)
- Bug already fixed on `main`: commodity tiles filled the whole header; keep the icon small and left of the name (36 px in the pop-up, 48 px on the full page).
- Layout (owner approved "Option A" compact card): small logo next to name and ticker, price 32 px, chart about 130 px, key figures grid, "Full chart" and "Watch" buttons, move analysis, articles. Keep all of that and add:
  - A time-window switch for the chart and the figures: 1D · 1W · 1M · 3M · 1Y (use `assets/hist/<SYM>.json` daily series for 3M and 1Y).
  - Performance strip: 1D, 1W, 1M, 3M, YTD, 1Y changes with arrows.
  - For stocks: sector, industry, country, exchange, currency of listing (from the `cur` field), and "Part of: <sector pop-up link>".
  - For commodities and FX: unit and quote convention (per troy ounce, per barrel, per bushel, EUR per USD ...), contract month for futures.
  - For crypto: 24 h range, 24 h volume (relay), rank by volume.
  - "Compare with" selector (same sector top peers) that overlays a second line in the chart, normalised to 100 at the start of the window.
  - "Related assets" row (same sector peers, correlated assets) as small chips that open their own pop-up.
- Everything priced goes through `InvPrefs.fmt`; every number uses the Apple numeral font (`--num` in `skin.css`).

## 3b. News pins on the chart: "why did it move" (owner priority, repeated several times)
First version is already on `main` (`pins()` in `assets/asset-page.js`, styles at the end of `asset-page.css`): numbered round pins sit on the price line at the publication time of each article that names the asset; green = the article's analysis says up, red = down, grey = neutral; hover/tap opens a card with time, source, headline and the "why it matters" line; a second tap jumps to the article in the list below (same number). Improve and extend it for **every asset**:
- Importance tiers decide the density: top assets (indices, gold, oil, bitcoin, ethereum, the 50 largest companies) up to 12 pins; mid-importance up to 6; the rest up to 3. Define the tiers in one place (`data/asset-importance.json`) and reuse them for robot frequency in sections 1, 4 and 5.
- Feed the pins from the per-asset news files of section 4 (30 days), not only from `news-archive.json`, so 7-day and 30-day charts have real content.
- On the 1D chart also mark scheduled events (earnings, central-bank decisions, data releases from `assets/calendar-live.json`) with a small diamond marker.
- Add a "Why it moved" summary directly under the chart: 2 to 4 short bullet points with the measured move around each pin (for example "Gold fell 1.4 % in the 6 hours after article 3"), computed from our own price series between the pin time and the next pin; wording rule: "followed", "coincided with", never "caused".
- Clustering: when pins overlap, merge them into one pin with a count that expands on tap; keep touch targets at 44 px on phone (the pin can stay 22 px visually with a larger invisible hit area).
- Make the same pin layer reusable for the sector pop-up chart (sector fund) and for the Markets board mini-charts of the top assets (without tooltips there, just dots).
- Accessibility: pins are real buttons with `aria-label`, reachable by keyboard (Tab), tooltip opens on focus, Esc closes it.

## 4. A lot more articles per asset (last 7 and 30 days)
Today `asset-page.js` shows only the few articles of `news-archive.json` that name the asset. Build a per-asset news layer:
- New robot script `update_asset_news.py` (GitHub Action `update-asset-news.yml`, tier A every 2 hours, tier B once a day, `concurrency: market-data`) that, for each asset, finds articles of the last 30 days using free sources only (GDELT DOC API by company name/ticker, official RSS feeds already used in `update_globe_news.py`, ECB/Fed/BoE). Save compact JSON per asset `assets/news/<SYM>.json`: `{asof, items:[{id, headline, source, url, published_at, direction?, why?}]}` capped at 60 items. Store only headline, source, link and time (never copy article text or photos).
- Match precisely: use the company's legal name plus ticker and aliases, avoid false matches (the word "Apple" the fruit, "Gold" the metal vs the company, "Meta" prefix). Keep a small alias table in `data/asset-aliases.json` and exclusion words per asset.
- Front end: the asset pop-up and page show "Articles naming <asset>" with a 7 days / 30 days switch, grouped by day, up to 10 visible with "Show more", each with source, time, direction arrow when the existing analysis marks one, and the "why it matters" line when present. Link out to the original source in a new tab and to our own article page when we have one.
- Respect free-tier limits: log counts, back off on HTTP 429, never fail the whole run for one asset, keep each run under 20 minutes.

## 5. Much more analysis per asset (7-day and 30-day)
Extend `update_asset_analysis.py` and `analysis.json` (or split to `assets/analysis/<SYM>.json` if the file gets large):
- For every asset with price history, write three blocks: "Today", "Last 7 days" and "Last 30 days". Each block has a headline sentence, 3 to 5 bullet points with measured facts (move vs the asset's own 21-day volatility, rank within its sector, relation to the index or sector fund, volume vs average, distance from the 52-week high/low, biggest day) and, when articles exist, a sentence naming the catalysts with links to the supporting articles. Every number must be computed from our data; wording is generated by the model only from those facts and the headlines (the existing code path already labels AI-assisted text: keep the label "Written with AI from the price data and the linked articles").
- Never claim causation: use "coincided with", "followed", "articles name". Keep "Not investment advice".
- Cost control (free Gemini quota): compute all numbers deterministically in Python; call the model only for the wording of assets that moved more than 1.3x their normal daily move in the window, plus a rotating 10 % of the rest each day; cache by a hash of the inputs so unchanged assets are not regenerated; log tokens per run; abort gracefully when the quota is exhausted and keep the previous text.
- Front end: the "Move analysis" card in the pop-up and page gets tabs Today · 7 days · 30 days, a "Key facts" list under the text, and the date of the last update.

## 6. Data we cannot get free (do not fake)
Market cap, P/E, dividend yield, analyst ratings, earnings dates. Options to research and report to the owner in the PR (do not wire a paid or licence-restricted source without asking): Finnhub free tier (60 calls per minute, key in GitHub secret `FINNHUB_KEY`, fetched by a robot, never from the browser), Nasdaq earnings calendar (already used by `update_calendar.py`), SEC EDGAR for US fundamentals. Show a cell only when real data exists.

## 7. Tests, checks, screenshots
- Playwright (Chromium at `/opt/pw-browsers/chromium`; do not run `playwright install`): at 1440 and 390 widths open each sector pop-up, assert at least 40 companies are searchable, typing a name filters within 150 ms, "Show more" works, Back returns with the search kept; open the pop-up for a stock, a crypto, a commodity (gold) and assert header icon width ≤ 48 px, price font-size ≤ 36 px, no horizontal page scroll; assert the articles list shows the 7 day / 30 day switch and at least 1 item for the top 50 assets.
- Data checks: script `tools/check-universe.py` fails if a symbol has no price, a stock has no `cur`, two assets share a name inside one sector, or an asset has coordinates outside its country.
- Existing tests in `tests/` must pass. Screenshots in the PR with the option labels printed on the images.

## 8. Order of work and checkpoints (open one PR per checkpoint, owner approves each)
1. Universe: 40+ companies per sector, ETFs, currency fields, performance split if needed. Checkpoint screenshot: every sector pop-up with its count.
2. Sector search + sorting + filters.
3. Asset pop-up additions (windows, performance strip, compare, related).
4. Per-asset news robot and the 7/30-day articles UI.
5. Per-asset analysis (Today · 7 days · 30 days) and the tabs.

## 9. Done means
Every sector lists at least 40 real companies with correct prices and currencies; every sector pop-up has a working search, sort and filters; every asset pop-up is compact, shows the extra details above, 7-day and 30-day articles and three analysis windows; robots run inside free limits; PRs opened (not merged) with labelled screenshots and a list of anything that could not be sourced legitimately.
