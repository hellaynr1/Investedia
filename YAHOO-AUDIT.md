# Yahoo Finance dependency and licensing audit (2026-10-30, audit only: nothing replaced)

Not legal advice. Sources: Yahoo Terms of Service (https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html, read 2026-10-30) and this repository.

## 1. Where Yahoo is used (exact)

All of the endpoints below are undocumented: `query1.finance.yahoo.com/v8/finance/chart/<SYM>` and, in two places, `/v8/finance/spark`.
No API key and no Yahoo agreement is involved.

| # | Code | What it fetches | What we store / publish | Runs | Cached? |
|---|---|---|---|---|---|
| 1 | `update_market.py` (`yahoo()`, `from_yahoo()`, `history()`) | prices, day/week/month changes, intraday, full price history for ~260 site symbols (stocks, indices, crypto, FX, commodities; US10Y/US30Y via `^TNX/^TYX`) | `assets/quotes.js`, `assets/intraday.json`, `assets/hist/*.json` (260 files, 6.5 MB of price history), all committed and **published** in `docs/` | `update-market.yml`: every 15 min on weekdays (06–21 UTC), plus nights and weekends | **Yes**: prices and history are downloaded, stored in git and served publicly |
| 2 | `update_globe.py` | 1-month daily closes and currency for the 928 Globe assets | `assets/globe/markets.json` + inline in `assets/globe/index.html`, **published** | same workflow | Yes (prices + 22-day sparkline) |
| 3 | `update_news_prices.py` | 1-month closes for assets the news mentions that markets.json lacks, sector ETFs, 12 major coins, ^NDX/^RUT/^VIX | `assets/globe/news-prices.json`, **published** | same workflow | Yes |
| 4 | `update_prices.py` | monthly adjusted closes since 2000 for 14 tickers (calculator) | `assets/data.js`, **published** | `update-prices.yml`, weekdays | Yes |
| 5 | `workers/live/providers/yahoo.js` (`/v8/finance/spark`) | live/delayed quotes, up to 20 symbols per call | served by the Cloudflare Worker `/v1/prices` to site visitors | on request | Worker cache (short) |
| 6 | `tools/registry/sources.py` → `build_registry.py` | **metadata only**: official security name, exchange code, instrument type, currency (no prices) for ~830 non-US symbols | raw replies cached in `tools/registry/cache/yahoo/` (gitignored, not published). Derived facts (official name, exchange → MIC, currency) are stored in `data/registry.json` (committed; mirrored to `docs/data/`) | `registry.yml` daily (new branch, not merged) | Metadata cached |
| 7 | `tools/add-companies.py`, `tools/gen-worker-symbols.py` | one-off developer tools (check that symbols return data) | nothing published directly | manual | no |
| 8 | Indirect: `update_news_track.py` (Live Track Record) | none itself | scores implications on prices from #2/#3 (Yahoo-derived) | every price run | uses the Yahoo-derived files |
| 9 | Research (`research/track-record/`, local branch only) | daily closes for the Historical Prediction Track Record | local cache | manual | yes, local only |

Not Yahoo, despite the docs:
- `update_news.py`'s docstring still says "Yahoo Finance RSS", but the code only calls Google News RSS, CoinDesk and Cointelegraph. That's a
  stale comment; Google News RSS has its own licensing question (already listed in DATA-LICENSING.md).
- The news robot's prompt asks Gemini for "Yahoo Finance symbols". That's only a ticker *format*; no Yahoo data is fetched there.

Visible attribution today:
- footer tooltip "Data: Yahoo Finance, FRED, Coinbase" (`assets/ui.js`);
- the Globe sparkline caption "Yahoo Finance" (`tools/globe-news/page.html`);
- `sources.html` ("Yahoo Finance: public market-data feeds… not a licensed execution feed").

## 2. Is the current use permitted for a commercial Investedia?

**No, not under Yahoo's published terms.** From the Yahoo Terms of Service:
- **§2(e) Use of Services:** "you may not access or reuse the Services, or any portion thereof, for any commercial purpose."
- **§2(d)(9):** no accessing or collecting data "using any automated means, devices, programs, algorithms or methodologies" (robots,
  spiders, scrapers, data-mining tools) without express prior permission. All nine uses above are automated.
- **§2(d)(10):** no using material or data to create a competing database, data feed or service, or a "material substitute". Our committed
  price files (`quotes.js`, `hist/`, `markets.json`, `news-prices.json`) are a public data feed built from Yahoo data.
- **§2(h) Ownership and Reuse:** no reproducing, distributing or transmitting content (including APIs) without explicit written permission.
- Yahoo has **no public market-data API or licence** to sign up for; the endpoints we call are undocumented and can change or block without notice.
- Underneath Yahoo, quotes and index values are licensed from exchanges and index providers (S&P DJI, FTSE Russell, STOXX…). Redistributing
  them commercially needs those licences regardless of where the numbers come from.

Even today (no revenue), §2(d)(9) automated collection and §2(h) redistribution are not permitted. The "non-commercial" status lowers the
practical risk; it does not make the use licensed. DATA-LICENSING.md already lists Yahoo as "not licensed for commercial use"; this audit
confirms that and adds the automated-access and redistribution clauses.

**Attribution:** the only attribution clause in Yahoo's terms is §2(o) **RSS feeds** (display without modification, attribute and link). We
do not use Yahoo RSS. Attribution does not create a licence for the price endpoints.

**Redistribution:** prohibited without written permission (§2(h), §2(d)(10)). Our published price files and history are redistribution.

**Registry metadata (#6):** this is the lightest use: identity facts (a security's official name and exchange), not prices. Facts themselves
are generally not copyrightable, but the automated collection still falls under §2(d)(9). The registry can be rebuilt without Yahoo (see below).

## 3. What breaks if Yahoo becomes unavailable

| Area | Effect |
|---|---|
| Globe | `markets.json` freezes at the last values (update_globe keeps old prices if >50% fail). % pills and sparklines go stale; lines still draw (places don't depend on Yahoo). |
| News price pills, implications cards | `news-prices.json` freezes; new assets get no price. |
| **Live Track Record** | new calls can't get a baseline or outcome → stay "pending" / unresolved. This is the most important break. |
| Old market pages / tools / calculator | `quotes.js`, `intraday.json`, `hist/`, `data.js` freeze. |
| Worker `/v1/prices` | errors → front end falls back to static files. |
| Asset registry | existing entries are kept (committed). New non-US tickers can't be verified → stay unresolved (no wrong lines; coverage just stops growing). US tickers are unaffected (SEC). |
| Historical Prediction Track Record (research) | no outcome prices. |

## 4. Realistic replacements per dependency (free or low-cost; terms must be confirmed before switching)

| Dependency | Free / official replacement | Low-cost licensed option | Notes |
|---|---|---|---|
| Security identity (registry #6) | **GLEIF LEI golden copy** (CC0: legal name, HQ address, country for every LEI issuer) + **GLEIF ISIN↔LEI mapping**; **OpenFIGI** (free API by Bloomberg: ticker + exchange → FIGI, name, security type; 25 req/6 s with a free key; commercial terms to confirm); official exchange listing files (NSE, JPX, HKEX, LSE, ASX, TSX, B3, Euronext) | n/a | Best path: SEC (US) + OpenFIGI (non-US identity) + GLEIF (company and HQ). This removes Yahoo from the registry completely. |
| FX (#1/#2) | **ECB euro reference rates** (daily, free reuse with source), FRED H.10 | vendor bundle | Daily, not intraday. |
| Rates (#1) | **FRED** (already used for US02Y etc.), **US Treasury** daily par yields (public domain), ECB/Bundesbank (ESCB reuse policy), BoE Database (OGL) | — | Replaces `^TNX/^TYX/^FVX/^IRX` fully. |
| Commodities (#1/#2) | **EIA** daily spot WTI/Brent/Henry Hub (public domain); FRED; World Bank Pink Sheet (monthly) | vendor futures data | Gold/silver: LBMA prices are licensed. Futures settlement data (CME/ICE) is licensed. |
| Crypto (#1/#3/#5) | **Coinbase Exchange public API** (already used for live crypto), Kraken public API | CoinGecko paid plans (the free Demo plan forbids redistribution and requires attribution) | Confirm exchange API terms for display. |
| Equities + indices prices (#1–#5, Track Record) | **None that is both free and licensed for commercial display.** Free tiers (Alpha Vantage, Twelve Data, Tiingo, EODHD) are personal/non-commercial. | Tiingo commercial (~$50/month reported), EODHD commercial (custom quote; standard plans ~$20–100/month are personal), Twelve Data business (internal use; external display needs approval), Polygon/Massive starter plans | Exchange display rules are the binding constraint. **Index values** need index-provider display rights; ETFs (SPY, QQQ…) are a common licensed proxy. Ask each vendor in writing for "display on a public website, delayed/EOD, non-professional users". |
| Track Record outcomes | same as equities; daily closes are enough | EOD plan from the vendor above | The cheapest licensed need: end-of-day closes only. |

## 5. Recommendation (no change made)

1. Keep Yahoo for now (no revenue). Don't add new Yahoo dependencies. Don't publish more Yahoo-derived history than needed (`assets/hist`,
   6.5 MB, is the largest redistribution).
2. Before any revenue: (a) move the registry's non-US identity to OpenFIGI + GLEIF (free); (b) move FX, rates and energy commodities to
   ECB/FRED/Treasury/EIA (free); (c) license one EOD equities/indices vendor with written public-display rights, which also feeds the Track Record.
3. Fix the stale `update_news.py` docstring (says Yahoo RSS; uses Google News).
