# Codex task queue after P4 (owner decisions 2026-11-07)

Run in this order, one pull request each, from `main`. Read `AGENTS.md` and `design/CODEX-ACCEPTANCE-PROTOCOL.md` first.
Every PR: no evidence folders, list files changed, test results; the automatic Claude review comments on it. **Do not merge.**

## Owner decisions that apply to P4 and later
- Phone Markets: floating bottom sheet above the bottom navigation (rounded 20 px, 8 px side margins, max 54% height), mockups
  `design/markets-globe/D-phone-performers.png`, `-attention.png`, `-sectors.png`.
- **Performers** = 12-month total return from licensed historical prices only, period and "as of" date always shown; prices older
  than 3 trading days are hidden; if no licensed prices: show "Performance data not available for <exchange>" and keep Attention.
- **Trade/investment lines:** clean: at most 5 lines on phone and 8 on PC for the selected country (largest partners first);
  no lines before a country is selected.
- **Currency setting:** converted values are labelled with their currency code (e.g. "€1.23", "NGN 1,346"); never silent.
- **Backfill quality gate:** 90% relevant, 95% correct country (as in P3).

## P5 · Connections for underserved markets (after P2)
New companies from P2 can now be connection destinations. Extend `tools/globe-news/connections.py` so that articles about
Nigeria, Kenya, Egypt, Morocco, the Gulf, Vietnam, the Philippines, Peru and Colombia resolve to those companies and indices by the
same rules (exact registry match, verified place, no sector lines). Add the country index / ETF proxy as a "market" destination.
Report before/after: connections per region, share of underserved-market articles with at least one line. Gate: no rejected-reason
category grows by more than 10% (no forced matches).

## P6 · Market links data (trade and investment)
Build `assets/globe/market-links.json` used by P4: UN Comtrade (latest full year) top bilateral trade partners per country and
IMF CPIS portfolio investment holdings. Each link: from, to, type (trade|investment), value, unit, year, source URL.
Script `tools/build-market-links.py`, run monthly by a workflow with a manual trigger only (no new cron until the owner agrees).

## P7 · Country pages depth
Each country page (from P1) gets: exchange info, benchmark/ETF proxy chart (delayed, labelled), listed companies table
(sortable), news list with filters, macro block (World Bank), and the Market Momentum module. Missing data stays "no data yet".

## P8 · Globe "fuller" look (owner picks the option first)
Implement the option the owner chooses from `design/globe-options/` (G1 recent-news pulse, G2 market rings + more lines,
G3 atmosphere rim). Keep phone frame time within 15% of today.

## P9 · Quality and safety pass
Accessibility (keyboard, labels, contrast) on the new panels; error states for every fetch; a smoke test that loads the homepage,
Globe page (News + Markets), a country page and an asset page on PC and phone with no console errors.
