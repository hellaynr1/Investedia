# Free headline updates and exposure explanations

Headlines are collected from GDELT and official central-bank RSS feeds every five minutes on standard GitHub Actions runners in this public repository. Schedules and sources may be delayed; this is not a seconds-fast newswire. Readers poll the saved public feed every 30 seconds while the tab is visible. Browser traffic never calls Gemini or a news provider.

New headlines trigger a dismissible in-page alert, after the initial feed has loaded. Alerts show one leading headline and the count of new stories; no notification permission, sound or focus interruption. Home, News and Globe also refresh their content. Temporary fetch failures preserve the previous feed.

Offline editorial rules cover rates, inflation/jobs/GDP, major earnings, large market moves, oil/shipping/supply disruption and market-relevant politics: elections, budgets, taxes, regulation, tariffs, sanctions, export restrictions, trade agreements and conflict. Politics must have an economic connection. Keywords flag candidates, not verified importance or forecasts.

Every story displays potential exposure or “Impact unclear.” Direct company names and topic rules can identify multiple assets/sectors. Rule-based directions remain unclear. Unknown locations are explicitly unconfirmed and never receive invented globe coordinates. Existing country connections can be tapped on the globe, or opened with keyboard-accessible exposure buttons. Explanations show the reporting, possible mechanism, uncertainty and source. Editorial story-to-story links are not presented as proven causation. No buy/sell recommendations.

## Optional major-story summaries

Headline collection and asset tagging work without any API key. Existing summaries are retained. New summaries remain disabled by default because a request ceiling alone cannot guarantee zero charges on a billed Gemini project.

Before enabling, the owner must verify that the GitHub `GEMINI_API_KEY` belongs to a project with no paid billing and an available free-tier text model. Then set these repository Actions variables:

- `NEWS_FREE_TIER_CONFIRMED`: `true`, only after the free-tier-only project is verified.
- `NEWS_FREE_MODEL`: the exact currently available free-tier model identifier.

The collector makes at most one request per 30 minutes and eight attempts per UTC day, summarizing at most four major stories per batch. A persisted `news-ai-usage.json` ledger reserves an attempt before sending. Failed requests count, and there are no model fallbacks/retries. Confirmed limits are ceilings, not a promise of provider quota availability. Repeated stories retain their summaries; unrelated smaller stories remain headline-only. A 429 or model error never prevents headline publication.

## Review

Run `python3 -m unittest discover -s tests -v`, then `python3 tools/globe-news/build.py` and `python3 build.py`. Review News and Globe at 1440px and 390px, including no-summary stories, new-headline arrival, offline refresh, modal keyboard dismissal and line hit detection. This branch must be reviewed and approved before merging to `main`, per `AGENTS.md`.
