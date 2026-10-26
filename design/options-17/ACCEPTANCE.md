# Since the news: card, option B (2026-10-26)

Chosen by the owner: **B, before and after** (grey line before the article, red or green after). Mockup: `design/options-15/1-before-after-options.png`. Built screens here: `ok-pc.png`, `ok-phone.png`, `na-pc.png`.

## What is built in this change
- **Recorder** `update_news_track.py`: after each price run it appends one price point for every asset that a story from the last 72 hours names, to `assets/globe/news-track.json`. It uses the prices the price robot has just written (no new network calls), adds a point only when those prices have a new time, keeps 72 hours, drops assets no recent story names, and keeps the previous file on any failure. Added to `.github/workflows/update-market.yml` (every 15 minutes while markets are open, every 3 hours otherwise).
- **Card** `assets/since-news.js` + `.css`: shown in the globe's story panel for the first affected asset that has a price.

## Data map
| On the card | Source |
|---|---|
| Big number, after text, line after the article | `news-track.json`: first recorded price at or after publication is the start; the last is "now" |
| "Before the article" text and grey line | recorded points in the 3 hours before publication (only when at least 2 exist) |
| Publish time, source | the story's `published_at` |
| "the article said down ✓/✗" | the story's own `impacts[].direction` against the move; under 0.3% is "barely moved" |
| Today's move (fallback) | `markets.json` / `news-prices.json` |

## Honest states (no invented chart)
| Situation | What the card says |
|---|---|
| No recorded price after the article | "We started recording this article's price after it was published, so the since-the-news chart is not available. Showing today's move instead." |
| One recorded price | "Tracking started at HH:MM UTC. The chart appears after the next price update (about 15 minutes)." |
| First price more than 90 min after the article and nothing before | same as "no recorded price" |
| First price 15–90 min late | chart shown; note says "The first price was recorded N minutes after the article, so the change is measured from HH:MM UTC." |
| No points before the article | "Before the article: no price data (market closed or not yet recorded)." and no grey line |

## Tests
`tests/since-news.spec.mjs` (SN1–SN9 at 1440 and 390: numbers recomputed from the fixture, wrong call, flat move, missing file, single point, late first price, pure calculation, layout and text size) and `tests/test_news_track.py` (6 unit tests for the recorder).

## Built vs mockup
| Item | Mockup | Built |
|---|---|---|
| Layout | big number, before/after text, split chart, axis, legend | same |
| Verdict chip | not in mockup B | added ("✓ the article said down · it went down"), same wording as the earlier cards |
| Chart curves | examples | real recorded prices only |
| Where it shows | homepage, globe panel, article pages | **globe story panel only in this change**; homepage card and the article page come next |
| First days | n/a | until the recorder has run for a few hours the card shows the "not available" or "tracking started" message |
