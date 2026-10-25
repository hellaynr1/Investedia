# Acceptance record: calendar A, Why it moved C, globe hover B (2026-10-25)

Mockups: `preview/design-options-4` (design/options-4/*.png). Built-vs-mockup images: `design/options-4/built-vs-mockup-*.png`.
Tests: `tests/redesign.spec.mjs` (30 checks at 1440 and 390 px, results in `tests/redesign-results.json`). Regression: all other suites pass.

| ID | Criterion (what the owner chose) | Test | Status |
|---|---|---|---|
| C1 | Header line "Next high impact: <event> · in x d y h" (prefers US/EU/UK events) | C1 | done |
| C2 | Compact filter bar: Today, Tomorrow, This week, Next week, 30 days, Custom, High impact only, Earnings, Region menu, search | C2 | done |
| C3 | Agenda grouped by day with a "n high-impact" count; rows with time, flag, event, impact bars, forecast, previous (and actual once released) | C3 | done |
| C4 | A row is preselected; detail panel with Forecast, Previous, Actual | C4 | done |
| C5 | "Watch these markets" chips with real % moves from markets.json; "Latest related article" only when a region-matching article exists | C5 | done |
| C6 | Phone: tapping a row opens a bottom sheet with Close | C6 | done |
| W1 | Why it moved: no 01 / 02 / 03 numbers | W1 | done |
| W2 | Featured article shows the asset's real % today and 7-day change | W2 | done |
| W3 | Price chart with an "article published" marker | W3 | done |
| W4/W5 | Side cards and featured card show the asset, a % pill and "Article implies ↑/↓" next to the real move | W4, W5 | done |
| G1 | Globe: pill with asset name and real % in the middle of the line | G1 | done |
| G2 | Hover card: name, ticker, price, % today, 7-day %, "Article implies / price today", sparkline, why | G2 | done |
| G3 | Hover card does not cover the pill | G3 | done |
| G4 | Article panel's Affected assets list shows the % too | G4 | done |

## Not done / differs from the mockup (read this)
- Pills and hover cards exist only for impacts whose ticker is found in `assets/globe/markets.json` (47 of 106 saved impacts). Sector-only or country-only impacts have no price, so they show no %. Nothing is invented.
- Pills appear for the selected or hovered article's lines (calm globe by default), as chosen for batch 2.
- The "since publication" % from globe option C was not chosen and is not built (it would need intraday prices for non-US stocks).
- The Why it moved featured card is the highest-ranked article that has a real price (today Brent crude), not the example article in the mockup. The article marker on the chart is placed by calendar days, not intraday.
- The calendar's default view hides earnings and low/medium impact (toggle "High impact only" and "Earnings"). On weekends "This week" shows the coming week.
- On phones there is no hover: tapping a line opens the article, whose Affected assets list shows the %.
- Real data can disagree with an article: e.g. the Volkswagen article implies "up" while the share is down 0.40% today. The UI shows both on purpose.
