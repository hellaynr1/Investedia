# News pipeline: how Investedia's news gets from sources to the site

Plain-language guide for the owner. Last updated 2026-10-28.

## The short version

Investedia runs **two robots** that collect financial news and write it into files the website reads:

| Tier | What it covers | How often (target) | Workflow file |
|---|---|---|---|
| **Priority** | Central banks, statistics offices, US Securities and Exchange Commission (SEC) and Energy Information Administration (EIA), plus MarketWatch headlines | about every **10 minutes** | `.github/workflows/priority-news.yml` |
| **Broad** | Everything: GDELT (global news index), publisher business feeds, regional feeds, the 30-day archive, photos | about every **30 minutes** | `.github/workflows/update-globe-news.yml` |

Both robots run the same script, `update_globe_news.py`, with a setting called `TIER` that decides which mode it runs in.

> **Honest timing.** GitHub's scheduler is best-effort. A "every 10 minutes" job can start 5 to 15 minutes late, and occasionally skip a slot. Target: important official news appears within about 10 to 20 minutes of publication, not guaranteed. Nothing on the site says "live" for this feed; it says "Latest news · updated HH:MM".

## The flow

```
Sources (free feeds, GDELT)
  ↓
Raw ingestion            (RSS/XML parsing, GDELT JSON, timeouts, one failure never stops the run)
  ↓
Basic normalisation      (dates converted to UTC, HTML entities removed, future dates clamped to now, items older than 3 days dropped)
  ↓
URL and title dedupe     (tracking parameters removed; near-identical headlines collapsed; official source kept over copies)
  ↓
Seen-ledger              (items already sent to the editor in the last 3 days are skipped: nothing is paid for twice)
  ↓
Relevance gate           (priority tier: keyword score 0-8, only 3+ continues; junk words such as "stock to buy" removed)
  ↓
AI enrichment            (Gemini: summary, "why it matters", category, place, companies, direction; capped at 12 items per priority run, 140 per broad run)
  ↓
Canonical feed           assets/globe/news-live.json   (newest 160 stories from the last 7 days)
  ↓
Archive                  assets/globe/news-archive.json (up to 600 stories from the last 30 days; rebuilt by the broad tier only)
  ↓
Frontend                 Home, Globe, News page, asset pages, search, notifications: all read the same files
```

## Files

| File | What it holds | Who writes it |
|---|---|---|
| `assets/globe/news-live.json` | The live feed (160 newest stories, 7 days). Read by Home, Globe, notifications, Movers. | Both tiers (only when the stories changed) |
| `assets/globe/news-archive.json` | Up to 600 stories over 30 days. Read by the News page. | Broad tier only |
| `assets/globe/news-seen.json` | Items already sent to the editor (3-day memory). Internal. | Both tiers |
| `assets/globe/news-status.json` | Health summary: last successful runs, article count, newest and oldest article, failed sources. Contains no keys or private data. | Every run (committed by the broad tier) |
| `assets/globe/news-ledger.json`, `news-track.json`, `news-prices.json` | Track record and price checks for articles | Other scripts (`update_news_track.py`, `update_track_backfill.py`, `update_news_prices.py`), run from `update-market.yml` |
| `assets/globe/photos/` and `photos/index.json` | Downloaded topic photos with credits | Broad tier, once per topic |
| `docs/assets/globe/...` | Identical copies for GitHub Pages | Written automatically with every file above |

A `.tmp` file is written first and then swapped in, so readers never see a half-written file. A feed with **zero stories is never written**: the last working file stays online.

## Schedules and workflows

| Workflow | Schedule (UTC) | Concurrency group | Notes |
|---|---|---|---|
| `priority-news.yml` | minutes 4, 14, 24, 34, 44, 54 of every hour | `market-data` | Commits only the live feed and seen-ledger; quiet runs create no commit |
| `update-globe-news.yml` | minutes 7 and 37 of every hour | `market-data` | Also draws share cards and updates the economic calendar |
| `update-market.yml` | every 15 min on weekdays while markets are open, less often otherwise | `market-data` | Prices and the asset-level headlines (`update_news.py`) |
| `update-calendar.yml` | every 15 min on weekdays | `calendar-refresh` | Economic calendar |
| `update-economy.yml` | Mondays | `market-data` | World Bank country data |

**Why one shared group?** All of these write to the same JSON files. The `market-data` group makes them queue instead of racing. The cost: a long broad run can delay a priority run by a few minutes. Typical broad run: 1 to 4 minutes.

**Commit noise.** Each commit adds to the repository's history. The feed is only committed when its stories changed. Watch the repository size monthly (see "Costs" below).

## Environment variables and secrets

| Name | Where it lives | Used for | If missing |
|---|---|---|---|
| `TIER` | Set inside each workflow file (`priority` or `broad`) | Chooses the mode | Defaults to `broad` |
| `GEMINI_API_KEY` | GitHub → Settings → Secrets → Actions | AI selection and summaries | News is still collected, but no new stories are written (old ones stay online) |
| `PIXABAY_KEY` | GitHub Actions secret | Topic photos | Existing photos are reused; no new ones |
| `FRED_API_KEY` | GitHub Actions secret | Economic calendar | Calendar keeps its last data |

Never paste keys into code, chat or files. Keys are read from the environment only.

## Cloudflare

The news pipeline **does not depend on Cloudflare**. The Cloudflare Worker in `workers/live/` is only the live crypto relay for prices. The news files are served directly by GitHub Pages. (A Cloudflare cache in front of the news files was considered and deferred: it needs a deployment with your account, so it is not done without your approval. See the report at the end of the session.)

## Failure behaviour

| What fails | What happens | What you see |
|---|---|---|
| One feed times out or returns junk | Logged in `news-status.json` under `errors`; the others continue | `failedSources` count goes up |
| GDELT returns HTTP 429 (rate limit) | The GDELT step stops for this run; feeds continue | GDELT error in `errors` |
| Gemini quota reached on one model | Next model in the list is tried immediately | Gemini errors only if all models fail |
| Gemini fails completely | New candidates are **not** marked as seen, so they are retried next run; existing news stays | `priorityNewsLastSuccessfulRun` stops moving forward |
| Script crashes | The `fatal:` error is logged, the previous files stay, the workflow exits cleanly | `errors` in `news-status.json` |
| Two robots run at once | Impossible within the shared group; they queue | Nothing |

## How to run a refresh by hand

1. Open the repository on GitHub, go to **Actions**.
2. Choose **Priority market news (every ~10 min)** or **Update globe news**.
3. Click **Run workflow**, pick the `main` branch, click the green button.
4. Wait 1 to 4 minutes, then open `assets/globe/news-status.json` on GitHub to check `ran_at`, `errors` and `priorityNewsLastSuccessfulRun`.

For a broad run that also fills the past days, set `backfill_days` (0 to 7) in the broad workflow's form. It is slow and uses Gemini, so do it rarely.

## How to add a new source

1. Decide the tier:
   - **Official** (central bank, statistics office, regulator): add a line to `FEEDS` in `update_globe_news.py`. It joins both tiers.
   - **Business publisher**: add it to `NEWS_FEEDS`. Broad tier only. Only add it to the priority tier if it is a market-wide headline feed (like MarketWatch, which is in `PRIORITY_NEWS`).
   - **Regional**: add it to `REGION_FEEDS` with its region code (`af`, `latam`, `me`).
2. Check the licence first and add a row to `DATA-LICENSING.md`. Do not add a source whose terms forbid this use.
3. Run the tests: `python3 -m unittest discover -s tests -p "test_*.py"`.
4. Run the robot once by hand (see above) and read `errors` in `news-status.json`.

## How to debug stale news

Work through these in order:

1. **Open `assets/globe/news-status.json`** on GitHub (or the live site: `https://investedia.com/assets/globe/news-status.json`).
   - `priorityNewsLastSuccessfulRun` older than 30 minutes → the priority robot is failing or late.
   - `errors` mentions `Gemini` → quota or key problem. Check Google AI Studio usage, and the `GEMINI_API_KEY` secret.
   - `errors` mentions `GDELT ... 429` → normal, GDELT limits the rate; the broad tier just uses the feeds.
2. **Open Actions** and check the last two priority runs. A red X shows the failing step.
3. **Check `newestPublishedAt`**. If it is recent but the site looks old, the problem is the browser or service worker: hard-refresh once. After this session's fix, the news files bypass the offline cache.
4. **Check `news-seen.json`**. If many candidates are being skipped, they were already sent to Gemini in the last 3 days.
5. If nothing helps, run the workflow by hand and read the log.

## Testing

```
python3 -m unittest discover -s tests -p "test_*.py"
```

`tests/test_news_pipeline.py` covers: URL cleaning, duplicate detection, date and timezone parsing, future and stale items, the relevance gate, the seen-ledger, atomic saves, empty-feed protection, failed and malformed sources, Gemini failure handling, and bounded impact analysis. No test touches the network.

## Known limits (honest list)

- Timing is best-effort (GitHub scheduler). Not real-time.
- Gemini's free tier has per-model daily quotas. Heavy days can leave the priority tier without AI for a few hours.
- The asset-level headlines (`update_news.py`, used by asset pages) still come from Google News and Yahoo RSS on their own schedule. They are not yet part of this two-tier design. See `DATA-LICENSING.md` before relying on them commercially.
- The priority tier currently covers official feeds and MarketWatch only. Company announcements, earnings and M&A need a decision on a lawful source first (see `DATA-LICENSING.md`).

## Costs

| Item | Cost | Note |
|---|---|---|
| GitHub Actions | €0 on the current plan | The repository is public, so standard runners are free. Check the Actions usage page if this changes. |
| GDELT, official feeds, publisher feeds | €0 | Free. Terms differ by source: see `DATA-LICENSING.md` |
| Gemini API | €0 on the free tier | Per-model daily limits. Upgrading would need your approval |
| Pixabay | €0 | Free licence, credit stored with each photo |
| Repository size | grows with commits | The feed is committed only when it changes. Check the repository size every few months |

