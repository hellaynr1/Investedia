# News pipeline

One canonical dataset feeds Home, Globe, News, asset pages, country panels and Search:
`assets/globe/news-live.json` (7 days, 160 articles) and `news-archive.json` (30 days, 600). Schema `investedia.globe.news/v1`;
new fields are additive only (`score`, `content_hash`) so older readers keep working.

## Two tiers
| | Priority (`priority-news.yml`) | Broad (`broad-news.yml`) |
|---|---|---|
| Cron | `*/10 * * * *` | `7,37 * * * *` |
| Sources | official feeds (central banks, SEC, BEA, EIA…) + 6 fast business feeds | everything: official, publishers, GDELT, regional feeds |
| Article pages fetched | never (feed text only) | yes, for the short description |
| Max new articles / run | 10 | 45 |
| Writes | `news-live.json` only, and only if articles were added | live + archive + photos + impacts backfill |
| Gemini | only if there are unseen candidates | same, plus impact backfill |

Both use `concurrency: news-data` (never two writers; a pending run replaces older pending runs). Neither triggers the other.
**Honest limits:** GitHub cron is best effort. Runs may start 5–15 minutes late or be skipped under load, and every commit queues a
GitHub Pages build (often 1–5 min, sometimes 10+). Expect priority news on the site ~10–25 minutes after publication, not seconds.
That is why the UI says "Updated 12m ago" and never "LIVE" for news. Crypto prices alone are live (Coinbase relay).

## Stages
1. **Fetch** (per-source timeout, one retry, failures listed in `news-status.json › tiers › <tier> › sources_failed`).
2. **Deterministic filter** (`NOISE`, canonical URL, already-online, **seen cache**: `news-seen.json`, 3 days, keyed by canonical URL + content hash — rejected or kept candidates are never sent to Gemini again while their text is unchanged; not saved when Gemini fails).
3. **Dedupe** (`news_core.dedupe`): canonical URL, title similarity, shared entities/numbers within 12 h; the most authoritative source wins (official > publisher > aggregator), then earliest.
4. **Score** (`news_core.score`, 0–100, stored as `score`, never shown): authority 26, recency 20, relevance 16, macro significance 14, asset exposure 10, event severity 8, geography 6, minus 6 per extra duplicate. Candidates are ordered by it so caps drop the weakest, not the newest. Home "Why it moved" and Top ranking use it after `importance`.
5. **Gemini enrichment** only on survivors: neutral headline, our own summary, "why it matters", category, location, impacts. Output validated (`validate_analysis`).
6. **Atomic validated write** (`news_core.atomic_write`): temp file → re-read → validate (non-empty, unique ids, required fields, valid dates) → `os.replace`. Failure keeps the previous file; an empty feed is never published.
7. **Status** `news-status.json` (v2): per-tier `last_run`, `last_success`, counts, failed sources; `newest_article`, `oldest_article`, `live_articles`.

## What we store and show (legal posture, see DATA-LICENSING.md)
Headline (rewritten), source name, publication time, link to the original, **our own** AI summary and "why it matters". No full text, no
paywall bypass, no hotlinked publisher images (topic photos are Pixabay, downloaded once; fallback is logos/flags/category visuals).
`ai_summary: true` marks AI-assisted text; `source`/`sources` is the original publisher.

## Operate
- **Trigger a refresh:** GitHub → Actions → "Priority news" or "Broad news" → Run workflow. Locally: `NEWS_TIER=priority python3 update_globe_news.py` (needs `GEMINI_API_KEY`; without it nothing is written).
- **Add a source:** official → `FEEDS`, publisher → `NEWS_FEEDS` (add its name to `PRIORITY_NEWS` to include it in the fast tier), regional → `REGION_FEEDS`. Test the feed returns items first.
- **Debug stale news:** (1) `assets/globe/news-status.json` — is `tiers.priority.last_success` recent? (2) Actions tab — failing/queued runs? (3) `failed_sources`? (4) `gemini_ok` false → quota/key. (5) Pages build queued? (6) Browser: hard refresh; `sw.js` serves `assets/globe/*.json` network-first.
- **Tests:** `python3 -m unittest discover -s tests -p 'test_news_*.py'`.

## Delivery layer decision
Now: GitHub Pages JSON (free, no new accounts). Bottleneck: Pages deploy latency per commit. **Option, not built (needs your approval):**
Cloudflare Worker + KV `news:live` (the existing `investedia-live` Worker/KV could host `/news`), with the priority workflow POSTing the JSON using a
`NEWS_INGEST_TOKEN` secret you create, and the front end falling back to the static file. Free-tier fits (≈150 writes/day). I did not add it to avoid
credentials and a second source of truth before you decide.
