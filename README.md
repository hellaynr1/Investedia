# Investedia — UI preview

A complete, clickable visual frontend for Investedia. **UI only**: every price, chart, article and AI answer is illustrative sample data. There is no backend, API, database or login.

## Run it

Open `index.html` in a browser, or serve the folder:

```
python3 -m http.server 8000     # then open http://localhost:8000
```

To publish a preview: drag the folder onto https://app.netlify.com/drop.

## Edit it

Pages live in `src/pages/`. Each file starts with one line of JSON (title, description, nav key, optional extra scripts) followed by the page markup and its small page script. After editing, rebuild:

```
python3 build.py
```

This wraps every page in the shared `<head>` and writes the `.html` files at the project root.

| File | What it holds |
|---|---|
| `assets/app.css` | Design system: colour tokens, type, layout, cards, tables, tabs, charts, mega-menu |
| `assets/ui.js` | Shared components: header + mega-menu, mobile drawer, ⌘K search, ticker, footer, charts (area, sparkline, heatmap), tables, newsletter, deep-link tabs |
| `assets/mock.js` | Sample market data (120 assets), news, analysis, calendar, earnings |
| `assets/profiles.js` | Sample profiles and AI analysis for the showcase asset pages |
| `assets/data.js` | Real monthly price history used by the POV calculator (`update_prices.py` refreshes it) |

## Pages

- **Home** `index.html`
- **Markets** hub `markets.html` and seven category pages: `stocks.html`, `indices.html`, `crypto.html`, `currencies.html`, `commodities.html`, `bonds.html`, `funds.html`
- **Asset template** `asset.html?s=SYMBOL`. It adapts to the asset class. Showcase examples: AAPL, NVDA, TSLA, MSFT, SPX, NDX, BTC, ETH, EURUSD, XAU, US10Y, SPY
- **News** `news.html`, article `article.html`
- **Analysis** `analysis.html`, analysis article `analysis-article.html`
- **AI Insights** `ai-insights.html`
- **Tools**: `screener.html`, `calendar.html` (economic + `#earnings`), `compare.html`, `calculator.html` (POV, compound, returns, dividends), `converter.html`
- **Real Estate** (coming soon) `real-estate.html`
- **Watchlist** (demo account) `watchlist.html`, **About** `about.html`

## Plugging in real data later

Every page renders from `window.MOCK`. Replace `assets/mock.js` with calls to your data provider (keeping the same object shapes) and the UI keeps working.
