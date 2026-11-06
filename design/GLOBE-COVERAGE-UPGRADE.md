# Globe coverage and connections upgrade (preview, 2026-11-06)

Branch `preview/globe-connections` (local, not pushed). Nothing changes predictions, archives, event IDs or the Track Record.

## Audit (measured, 7 days of git history: 60 archive snapshots, 872 robot runs)
- 3,236 unique articles, 119 countries, 115 sources, 100% geolocated (the location is set by Gemini).
- By region: North America 32%, Latin America 25%, Africa 16%, Europe 14%, Asia 9%, Middle East 2%, Oceania 2%.
- Africa: 6% market-moving, 7% drawable. Thin: Hong Kong, Switzerland, Nordics, Gulf, Israel, New Zealand, Morocco.
- Funnel: 413,684 fetched → 269,683 already seen → 12,537 duplicates → 12,790 sent to Gemini → 4,052 published.
- Feed failures: Federal Reserve 15 runs, Bank of Korea 10, Daily Sabah 7, Premium Times 6, Central Bank of Kenya 4.
- Lines: 1,110 articles drawable (34%); **89% of those lines start and end in the same country** (stubs); 8% of impacts cross a border.

## Changes in this preview
1. **Connection engine** `tools/globe-news/connections.py` → `assets/globe/connections.json` (deterministic, no AI).
   Each line: event id, origin, destination, relationship type, tier (direct / secondary), confidence, evidence (impact,
   stated reason, source, headline) and an explanation. Rejected candidates are counted by reason.
   - Country impacts are anchored to that country's priced market (main index, or currency for currency effects).
   - Sector impacts never draw a line (no "same broad sector" lines). Crypto has no place → no line.
   - Only same-city pairs (under 100 km) are skipped; the event dot already shows them.
   - Confidence below 0.55 is drawn only as a lower-opacity secondary line; below 0.25 not at all.
2. **Globe rendering**: same orange family; direct = solid, secondary = solid at lower opacity. Overlapping arcs between the
   same two ~6° cells merge. Budgets raised to 22 PC / 14 phone lines, 4 per country (frame time on an emulated phone at 4x CPU slowdown: old 250 ms p95, new 233 ms p95 - no worse; absolute numbers are software rendering, not a real phone). `?lines=v3` shows the old logic.
3. **Connection card**: adds the relationship type, direct/secondary, confidence and the plain-language explanation.
4. **Top articles**: within the same importance level, regions take turns (nothing hidden, coordinates unchanged).
5. **Sources** (update_globe_news.py): 17 feeds added after checking each feed's own published history; the editor reserve
   now covers all regions (56 of 140 slots, at most 10 per region); one source can fill at most 25 slots; one retry after 3 s;
   Gemini told not to place events at a company's registration country, a commodity's exchange, or the US by default.
6. **Diagnostics**: `connections.json → diag` (articles per region/country, geolocation rate, events with connections,
   connections per event, cross-border share, by type, rejection reasons, failed feeds, last run funnel). Updated every run.

## Measured before / after (same 24 h of articles, same browser)
| | Before (v3) | After |
|---|---|---|
| Connections built | 25 | 18 |
| … of which real lines ≥ 400 km | 12 | 18 (+50%) |
| Same-area stubs | 13 | 0 |
| Every line has type, evidence, confidence, explanation | no | yes |
Archive (600 articles): 101 connections on 97 events; types: direct 44, market 29, commodity 17, acquisition 5, partnership 3,
central bank 1, currency 1, named competitor 1. Rejected: same place 230, sector 61, company without location 59, crypto 7.

## Feed check (each feed's own history, fetched 2026-11-06; 403 = refused this checker, may differ from GitHub's runners)
Added: The Japan Times (16/day), The Business Times SG (12), CNA Business (54), Mint companies (32), The National UAE,
Globes Israel (6), Euronews Business (6), The Irish Times Business (14), ECB press (1.3), Swiss National Bank (1.1), RNZ (14),
NZ Herald Business (14), Reserve Bank of NZ, Business Daily Africa (5), Diario Financiero Chile (164, Spanish), The Globe and Mail (25),
Bank of Canada. All dated 100%, newest item < 30 h, headlines mostly business.
Rejected: Doha News and The Local Sweden (mostly non-business), The Conversation (opinion, 1/day), Economic Times markets (mostly
US-market recaps already covered), Nikkei Asia (no dates). Refused or gone: Korea Herald, Yonhap, JoongAng, The Standard HK,
Business Standard, Caixin, China Daily, Taipei Times, Arab News, Gulf Business, Zawya, Times of Israel, Saudi Gazette, Argaam,
swissinfo, Yle, Norges Bank, BusinessLIVE, Medias24, Morocco World News, Ahram, Banxico, El Economista, BNamericas, Financial Post.

## Estimated cost (not measured until it runs in GitHub Actions)
Gemini: 0 extra calls (still 140 candidates per run). Actions: +~1 min per broad run for 17 more feeds. Cloudflare: none.
Connection engine: < 1 s per run. Globe: same line budgets, so frame cost is unchanged.

## Final QA (2026-11-06, before push)
- Company locations: 51 unlocated company impacts in the archive; 8 resolve by exact name to a listed company with a verified
  place in data/registry.json (OCBC, Nubank, AngloGold Ashanti, FTAI Infrastructure, Guardian Real Estate...). Added. The rest are
  private or unlisted (OpenAI, Anthropic, ByteDance, Pemex, ADNOC, MTN Nigeria...) and stay unlocated: no verified place exists.
- Asia/Oceania: 57 articles, 11 with lines. Of the 46 without: 18 have no impacts at all (upstream extraction), 13 are same-place
  (country or asset in the same city), 7 sector-only, 6 company without a place. No legitimate line was rejected by the new rules.
- Selection: regional reserve now requires a score at or above the median candidate; the "one pick in six" hint was removed
  (Gemini is told never to prefer a regional story over a more important event); the per-source cap trims only the lowest-scored
  surplus (candidates are sorted by score first).
- Touch: the first tap on a line pins its connection card with an "Open article" button; a second tap or the button opens it.
  Tap radius 20 px on touch (10 px mouse). Mouse click still opens the article directly.
- Fallback: with connections.json missing the globe draws the previous lines (25 events, no errors).
- Deploy: connections.json is written in the same step and the same commit as the news files (atomic temp-file rename). If the
  connection step fails, the news still publishes and the globe keeps the previous file; stale entries for removed articles are skipped.
- Phone frame time (iPhone 13 emulation, 4x CPU slowdown, software rendering): median 200 ms in both; p95 233-250 ms vs 233 ms.

## Global news expansion (2026-11-07, preview)
Bottlenecks found (measured):
- The globe's 24 h view showed only the newest 160 articles (~7 h); 576 articles were actually published in the last 24 h.
- Per broad run the editor saw on average ~32 fresh candidates and published ~9 (12,790 -> 4,052 over 7 days, 32%).
  Gemini's individual rejections were never logged; per-run region/source diagnostics are now recorded in news-status.json.
- Candidate scoring was English-only and US-weighted (Nasdaq/S&P/Dow and US mega-caps; a geography boost for 8 large
  economies), so non-English and local-market items sank below the cut.
Changes:
- 35 more feeds (55 of 116 extra candidates were reachable; chosen for dated, fresh, business-relevant output).
- Scoring: local benchmarks, currencies and central banks count like US ones; finance words in Spanish, Portuguese, French,
  Turkish, Polish and the Nordic languages are recognised; regional publishers get a geography weight.
- Editor input 140 -> 200 candidates: up to 80 best-scored core/global items first, then up to 16 per region (only items at or
  above the median score), then the rest by score; max 25 per source. Max picks per run 45 -> 60.
- Editor instructions: local market events qualify without a US link; for market-wide moves record the local index or
  currency (new articles only; frozen implications are never rewritten).
- Connection engine: benchmarks named in a headline become a secondary "market" link with the headline as evidence.
- Retention: live file 160 -> 360 articles; archive 600 -> 1,500.
Estimates (not measured until it runs with Gemini): +1,500-1,900 published per week; Gemini input ~+45% per broad run,
same number of calls; Actions ~+1 min per broad run; live file ~340 KB -> ~760 KB, archive ~1.2 MB -> ~3 MB.
Phone frame time (emulated, 4x CPU slowdown): 160 dots median 183 ms; 360 dots median 200-217 ms.
