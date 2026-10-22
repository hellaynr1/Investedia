# Retired URL inspection — 22 October 2026

Source stubs use the JSON `redirect` field; build.py writes noindex, canonical, visible notice, immediate meta refresh and location.replace. No source files or knowledge history were deleted. Archived content remains in Git history. Retired paths are absent from sitemap and active internal navigation links; none was in the service-worker CORE list. Account CORE pages remain.

| Retired URL | Successor |
|---|---|
| real-estate.html | markets.html |
| indices.html | markets.html |
| currencies.html | markets.html |
| commodities.html | markets.html |
| crypto.html | markets.html |
| bonds.html | markets.html |
| funds.html | markets.html |
| home-v2.html | index.html |

| Inspected and kept | Current dependency / reason |
|---|---|
| calculator.html | Tools menu/footer: POV, compound interest, investment returns, dividend calculations; education links |
| converter.html | Tools menu/footer: Currency Converter |
| compare.html | Tools menu/footer: Stock Comparison |
| screener.html | Tools menu/footer: Stock Screener |
| stocks.html | Tools menu/footer: Market Heatmaps |
| asset.html | Shared asset links/search results, saved watchlists and the retained tools open detailed asset pages; retiring it would break those requested features |
| dashboard.html | Welcome email template links here; About page also links here; service-worker CORE retains the account destination |
| ai-insights.html | Retained dashboard links to its brief; the analysis news navigation also exposes it; retained as a reachable legacy page rather than silently breaking that chain |
| watchlist.html | Account menu, welcome email and service-worker CORE |
| profile.html | Account menu, requested sign-in/settings and welcome-email unsubscribe/settings URL |

`globe.html` remains a compatibility wrapper but now embeds the consent-aware news globe. The old direct `assets/globe/index.html` map is not in the live primary menu; its fonts are now consent-gated too, and it has Privacy choices. This preserves its data/robot interface without a consent bypass.

Browser redirect results at both widths: `redirect-results.json`. These are client-side compatibility redirects appropriate for static hosting, not HTTP 301 responses; search engines may take time to update.
