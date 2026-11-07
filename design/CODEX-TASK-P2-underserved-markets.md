# Codex task P2: underserved markets: companies, indices, ETFs, exchanges

Read `AGENTS.md`, `design/CODEX-ACCEPTANCE-PROTOCOL.md` and `design/CODEX-TASK-P1-global-markets.md`.
Branch `codex/p2-underserved-markets` from `main` (after P1 and P4 are merged). Open a pull request. **Do not merge.**

## Why
P1 showed the gaps. In the registry, 1,665 listed companies cover 53 exchanges, but some exchanges have very few or none:
Nigeria (XNSA) 0, Kenya (XNAI) 0, Egypt (XCAI) 0, Morocco (XCAS) 0, Abu Dhabi (XADS) 0, Bahrain (XBAH) 0, Philippines (XPHS) 0,
Lima (XLIM) 0, Bolsa Valores Colombia (XBVC) 0, Saudi (XSAU) 9, Qatar (DSMD) 0. Several markets have no index in `markets.json`
(about 49 index/ETF rows cover the rest). Users who open Nigeria or Kenya currently see "no data yet" for most things.

## Scope (in this order)
1. **Exchanges missing from `data/exchanges.json`:** add XLIM, XBVC, DSMD, and any other MIC used by a registry company but absent
   from the file. Facts only: ISO 10383 MIC, name, city, currency, central bank, official exchange website URL.
2. **Companies:** for each underserved exchange, add the 10–15 largest listed companies by market value (from the exchange's own
   published list of listed companies or the official index constituents). Each entry needs: legal name, trading name, ticker
   (exchange symbol and Yahoo-style symbol, e.g. `DANGCEM.LG`), exchange MIC, currency, country, sector (ICB), official source URL
   and the date the list was taken. Do not add a company you cannot cite.
3. **Indices and ETFs:** for each market without an index, add the national benchmark **only** if a free, licensed feed exists;
   otherwise add the closest US/EU-listed country ETF and mark it `"type": "etf-proxy"` so the panel says "ETF proxy", never
   "benchmark". Markets to check: Nigeria (NGX ASI), Kenya (NSE 20), Egypt (EGX30), Morocco (MASI), Saudi (TASI), Qatar, UAE, Kuwait,
   Bahrain, Philippines, Vietnam, Peru, Colombia, Chile.
4. **Verification script** `tools/check-underserved.py` (new, deterministic, no AI): every new ticker resolves in the registry
   listing table; MIC is in `exchanges.json`; currency matches the exchange; every entry has a source URL that returns HTTP 200
   (store the check results in `design/evidence/p2-underserved/` only as a small summary, not raw pages).
5. **Registry rebuild:** run the existing registry build (see `registry.yml` and `registry.py`); do not hand-edit generated files.

## Do not change
Frozen predictions, Track Record, `v5-*`, news robots, historical archives, existing company pages' data (add only), colours,
fonts, homepage layout. No secrets. No scraping of pages that forbid it (check robots.txt; record the result).

## Acceptance criteria
1. Every underserved exchange listed in "Why" has at least 10 companies or an explicit note "source does not publish a list".
2. `check-underserved.py` passes with 0 failures (report the counts).
3. Every new company has a source URL and a list date; no duplicates by ticker across exchanges unless it is a real dual listing (flag it).
4. Country panel (P1) for Nigeria, Kenya, Egypt, Morocco, Saudi shows real company rows instead of "no data yet" for companies.
5. No new price data is invented: prices stay "delayed" or "no data yet" where no licensed feed exists; state the count of companies
   with and without prices.
6. Build clean; tests from `main` still pass; registry rebuild diff is limited to the new entries.

## PR must include
Table: exchange → companies added → sources → prices available (yes/no). Check-script output. Files changed. No evidence folders
beyond the small summary.
