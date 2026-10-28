# Data sources and licensing (honest status, not legal advice)

| Source | Used for | Status |
|---|---|---|
| ECB, Federal Reserve, BoE, BoJ, BoC, RBA, Riksbank, BoK, SEC, BEA, EIA RSS | headline + link (+ our summary) | Public-sector press feeds; generally reusable with attribution. **Check each site's terms before any commercial launch.** |
| BBC, Guardian, NYT, MarketWatch, SCMP, Straits Times, ABC AU, CoinDesk, OilPrice, Investing.com RSS | headline + link + our own short summary | Publisher RSS is for personal/non-commercial syndication of headlines and links. **Uncertain for a commercial product** (MarketWatch/Dow Jones and NYT terms restrict commercial use; Investing.com is stricter). Needs licences or removal before monetising. |
| Regional publisher feeds (Africa, LatAm, Middle East) | same | Same caveat; terms vary per site. |
| GDELT DOC API | discovery of headlines/links | GDELT data is open; the **linked publisher text is not** — we use only titles/links. |
| Google News / Yahoo Finance RSS (`update_news.py`) | headlines | **Uncertain** — Google/Yahoo terms do not allow general redistribution; candidate for removal. |
| Yahoo Finance prices | delayed quotes | **Not licensed for commercial use.** Needs a licensed provider before revenue. |
| Coinbase public WebSocket/ticker | live crypto | Public market data; keep attribution. |
| faireconomy / ForexFactory calendar | economic calendar | **Uncertain**; FRED + official calendars preferred. |
| Pixabay | topic photos | Pixabay Content License (OK for commercial use, no hotlinking required; we self-host). |
| Brandfetch logos | company logos | Check Brandfetch terms; fallback to initials. |
| Gemini | AI summaries | Our output is generated from headline + description only; keep "AI-assisted" labelling. |

Rules we follow: no full-text republishing, no paywall bypass, no publisher image hotlinking, always link to the original. Provider adapters are
isolated per source so a licensed feed can replace a risky one without touching the rest.
