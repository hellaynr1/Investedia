# TASK: Sector pop-ups, a smaller and richer asset pop-up, and more companies per sector

Read `AGENTS.md` first and obey it: work on a branch `preview/popups-sectors`, never push to `main`, show screenshots (PC 1440 wide and phone 390 wide) and wait for the owner's "push". Wording: "article(s)", never "story". Direction is shown with arrows only (↑ ↓ ↔), never the words Up/Down. Keep "Not investment advice". Real data only: if a figure has no real source, leave it out rather than inventing it. No secrets in the repo.

Design references (open in a browser from the repo root, served over `python3 -m http.server`): `design/popup-options.html` shows five mock-ups: asset pop-up A, B, C and sector pop-up 1, 2. The owner picks one asset option and one sector option in the pull-request thread. **Until the owner answers, implement asset option A and sector option 1** and structure the code so switching is a CSS/markup change, not a rewrite.

Current state you build on (already on `main`): `assets/peek.js` (blurred pop-up layer `InvPeek.open(symbol)` that shows `asset.html?s=…&embed=1` in an iframe, plus the search overlay), `assets/markets-heat.js` + `markets-heat.css` (Markets board, shared `tbl()` table, sector tiles and the inline `#mh-panel` that opens under the grid), `assets/asset-page.js` + `asset-page.css` (asset page), `assets/asset-icons.js` (logos and commodity icons), `assets/skin.css` (Aurora look: frosted glass, Apple system numerals), `assets/sectors.js` (`InvSectors.list`), `workers/live` (Cloudflare Worker), `build.py` (builds `src/pages/*.html` into root and `docs/`). After editing run `python3 build.py` and then `git checkout -- docs/assets/data.js`.

## 1. Sector pop-up (replaces the panel that opens under the sector grid)
- Clicking any sector tile on Markets (Technology, Semiconductors, Energy, Banks & Finance, Healthcare, Consumer & Retail, Autos, Industrials, Aerospace & Defence, Materials & Mining, Utilities, Real estate, Insurance, Communication and the Crypto tile) must immediately open a blurred pop-up layer, exactly like the asset pop-up (same backdrop blur, same close button, Esc to close, click outside to close, browser Back closes it, focus is trapped and returned, `prefers-reduced-motion` respected). Remove the old inline `#mh-panel` section and its scroll behaviour.
- Implementation: add `src/pages/sector.html` + `assets/sector-page.js` + `assets/sector-page.css`, opened by `InvPeek.openSector(slug)` in an iframe with `?embed=1`, same pattern as `asset.html`. URL hash `#s=<slug>`; deep links `sector.html?s=<slug>` work as a normal page too. Add `data-search` entries so the search overlay also finds sectors and opens this pop-up (search already lists sectors; make the click open the pop-up instead of navigating).
- Content (sector option 1 by default): header with sector icon, name, sector fund (ETF) and number of tracked companies; Today / Week / Month change chips; a small chart of the sector fund; "Largest movers" table using the shared `tbl()` styling (logo, name + ticker, price in the visitor's currency via `InvPrefs.fmt`, change with arrow, 1-month range, small chart); every row opens the asset pop-up (use `InvPeek.open`); a line "See articles on the News page" linking `news.html?sector=<slug>`; footer buttons "Articles on this sector" and "Follow sector" (reuse the existing follow logic in `assets/globe/news.html` if present, otherwise omit the button).
- Option 2 (heat map): a CSS-grid treemap of the sector's companies, size by market cap if available else by trading volume, colour by the selected window's move. Do not fabricate sizes: fall back to equal squares if neither number exists.

## 2. Asset pop-up: smaller, calmer, with more detail
Problem reported by the owner: the price and the chart are far too big and the pop-up looks empty. Fix in `assets/asset-page.js`, `assets/asset-page.css` and the `html.embed` rules in `assets/peek.js` (the pop-up is the same page in an iframe):
- Pop-up sheet width 560 px (option A) instead of about 1080 px; on phone full width with a bottom-sheet look.
- Price font 32 px (not 52–76 px), change pill small (12.5 px, already styled in `skin.css`), chart about 120 px high (not 240 px), range switch 1D · 1W · 1M · 1Y.
- Header: logo tile 40 px with the real logo or a centred initial (see section 4), name, `TICKER · exchange · sector · industry`.
- Key figures grid (3 columns on PC, 2 on phone): day range with position marker, 52-week range with marker, volume, market cap, P/E, dividend yield. **Only show a cell when you have real data.** Sources: day range and volume come from the price Worker snapshot (`/prices`, fields h, l, v) once it is switched on, otherwise from `assets/intraday.json`; 52-week range from the daily history in `assets/hist/` or `update_market.py` (add a `52w` field there if missing). Market cap, P/E and dividend yield are not in the data today: add them only from a source that is free to use and credited (for example Finnhub's free tier with a key stored as a GitHub secret named `FINNHUB_KEY`, fetched by a robot, never in the browser). If you cannot get them legitimately, leave those three cells out and tell the owner.
- "Move analysis" paragraph (already generated by `update_asset_analysis.py`), "Latest articles" (three, linking the story), and a footer with: "Full chart" (see section 5), "Watch" (star, uses the existing watchlist storage), "Open full page".
- Option B (side sheet) and C (wide dashboard) are alternatives; do not build them unless the owner asks.
- All numbers keep the Apple system numeral font (`--num` in `skin.css`) and tabular figures. All prices go through `InvPrefs.fmt` so currency conversion keeps working.

## 3. More companies in thin sectors
The sector tables are nearly empty for Real estate (1 company), Utilities (5), Insurance, Autos, Aerospace & Defence, Industrials (4). Add real, liquid companies to the asset universe so each sector has at least 10 names:
- Real estate: PLD, AMT, EQIX, WELL, SPG, PSA, O, DLR, CCI, VICI, VNQ (fund). Europe: VNA.DE, LAND.L, URW.AS.
- Utilities: NEE, DUK, SO, D, AEP, EXC, SRE, XEL, ED, NGG, IBE.MC, ENEL.MI, EDF.PA is not listed so skip, RWE.DE, EOAN.DE, ENGI.PA, ORSTED.CO.
- Insurance: BRK-B, CB, PGR, AIG, MET, PRU, ALL, TRV, AFL, ALV.DE, CS.PA (AXA), MUV2.DE, ZURN.SW, G.MI, ADM.L.
- Autos: GM, F, STLA, RACE, TM, HMC, 7203.T (Toyota), VOW3.DE, BMW.DE, MBG.DE, P911.DE, RNO.PA, BYDDY.
- Aerospace & Defence: LMT, RTX, NOC, GD, BA, LHX, AIR.PA, RHM.DE, BA.L (BAE), HO.PA (Thales), SAF.PA (Safran), LDO.MI, SAAB-B.ST.
- Industrials: CAT, DE, HON, GE, UPS, MMM, UNP, ETN, SIE.DE, SU.PA (Schneider), ABBN.SW.
- Also check Technology, Semiconductors, Energy, Healthcare, Materials and Communication reach at least 10 names each.
How: the asset universe lives inline in `assets/globe/index.html` between `/*MK*/` markers and is rewritten by `update_globe.py` into `assets/globe/markets.json` (fields `s, n, k (country), c (city), la, lo, r (region), m (rank), t (stocks|fx|cmd|crypto), g (group), site, cc`). Add each company as a new entry with its real headquarters city and coordinates, set `g` to one of the existing group names (Finance, Technology, Consumer, Healthcare, Communication, Energy, Materials, Utilities, Industrials, Real Estate) and extend the `SGRP` rules in `assets/markets-heat.js` so Autos, Insurance, Aerospace & Defence and Real estate select by group plus name pattern. Run `python3 update_globe.py` locally to fill prices and sparklines, check that Yahoo returns data for each symbol and drop symbols that fail. Then run `python3 tools/gen-worker-symbols.py` so the price Worker includes them. Add logos: download only where the licence allows (company brand assets or the existing Brandfetch route that `assets/asset-icons.js` already uses), otherwise the centred-initial fallback is used. Do not use Wikimedia images.

## 4. Logo tiles and fallback initials must fit
The owner reported that in the sector table the company logo and the fallback letter ("C") sit jammed in the corner of an oversized grey tile. Fix in `assets/asset-icons.js`, `assets/markets-heat.css`, `assets/skin.css`:
- Logo tiles are 28 px in tables and 40 px in the pop-up header, 24 px on phone; the `<img>` uses `object-fit: contain` with about 14 % padding on a white or dark tile that matches the logo; fallback initials are centred (both axes) and about 45 % of the tile height.
- The tile must always fill its holder (the commodity tiles already do: `.ai-c { width:100%; height:100% }`). Check `.ai-t`, `.ai-i`, `.mh-ic2` and `.ic` together so no rule gives a tile a fixed size that differs from its holder.
- Verify with a company that has no logo file (for example a new symbol you add) at 1440 and 390 px.

## 5. "Full chart" button (TradingView) in the pop-up
Add a "Full chart" button to the asset pop-up and asset page. Pressing it replaces the small chart with TradingView's free advanced-chart widget **only after the click** (consent and privacy: the page text must say TradingView receives the visitor's IP address; reuse the wording used for "Load live charts" on Markets and `consent.js`). Map site symbols to TradingView symbols (examples: `BTC-USD` → `BITSTAMP:BTCUSD`, `^GSPC` → `FOREXCOM:SPXUSD`, `GC=F` → `OANDA:XAUUSD`, `EURUSD` → `FX:EURUSD`, US stocks → `NASDAQ:` or `NYSE:` + ticker). If an asset has no valid mapping, hide the button instead of showing a broken chart. Show TradingView's credit link and a note when data is delayed.

## 6. Tests and checks
- Playwright (Chromium is at `/opt/pw-browsers/chromium`, do not run `playwright install`): at 1440 and 390 widths open Markets, click every sector tile and assert a `.pk` layer with the sector iframe appears, the page behind is blurred, Esc closes it, Back closes it; click a company row and assert the asset pop-up opens with price font-size ≤ 36 px and chart height ≤ 160 px; assert no horizontal page scroll; assert each sector lists ≥ 10 companies.
- Unit-check `tools/gen-worker-symbols.py` output includes the new symbols; run existing tests (`tests/`), nothing may regress.
- Screenshots to attach to the PR: sector pop-up (Technology, Insurance, Crypto), asset pop-up (a stock, a crypto, a commodity, an index) on PC and phone.

## 7. Done means
1. Every sector tile opens a blurred pop-up with that sector's companies; the old panel under the grid is gone.
2. The asset pop-up is compact (≈560 px wide, price 32 px, chart ≈120 px) and shows more real details; nothing invented.
3. Every sector has at least 10 companies with working prices and sensible logos or centred initials.
4. Logo tiles and initials fit and are centred at 1440 and 390.
5. "Full chart" works for mapped assets and is hidden otherwise.
6. PR opened (not merged) with screenshots and a list of any figures you could not source.
