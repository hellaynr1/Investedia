# Real market data preview — handover for Claude and owner

Branch: `preview/home-real-data`. Do not merge or publish without the owner’s approval.

## Result
- Shared quotes: 243/244 feed symbols refreshed; 237/238 main asset-list entries have quotes. NGSE remains unavailable; no sample price or generated price chart is shown for it.
- Globe: all 836 entries have source timestamps. Shared listings use the same quote data as the main site. Fixed home-exchange mapping and pence/cents conversion.
- Homepage: CoinGecko crypto totals/dominance, Alternative.me Fear & Greed, Yahoo sector ETF proxies, TradingView economic calendar, Nasdaq expected earnings dates. Each snapshot has its own attribution and time.
- Yahoo prices remain delayed snapshots. FRED foreign yields are explicitly monthly averages. Only supported crypto pairs stream from Coinbase; universal live exchange prices require additional provider access.
- Missing fundamentals, financial statements, ratings, bid/ask spreads, fund flows, holdings and contract metadata are unavailable instead of being estimated from sample values. Analysis pages remain explicitly labelled design examples; this is not a claim to have verified every educational/editorial paragraph.
- CSS, navigation, fonts, colours and homepage section order remain unchanged.

## Validation
- `python3 -m unittest discover -s tests -v`: 4 tests pass (currency conversion, percentage vs basis-point changes, provenance, feed failure).
- All 33 built pages checked in headless Chromium with no JavaScript page errors.
- Phone 390px: no horizontal page overflow or NaN/undefined/Infinity in homepage text.
- Desktop 1440px and phone 390px screenshots are in this folder.

## Review for Claude
1. Read AGENTS.md, then review the diff against main. Do not make overlapping changes on main.
2. Confirm exchange mappings and units in update_market.py and update_globe.py, especially the foreign home listings.
3. Check desktop/phone screenshots and the missing-data states. Source annotations and truthful ranking labels are intentional.
4. Verify scheduled refreshes write both assets/ and docs/assets/. Keep source timestamps on failed refreshes.
5. Licensed real-time coverage, unsupported NGSE, complete fundamentals and editorial verification remain separate work. Do not label those complete or buy a data plan without the owner.

## Refresh
`python3 update_market.py --quotes-only`
`python3 update_home.py`
`python3 update_globe.py`
`python3 tools/globe/build.py`
`python3 build.py`
