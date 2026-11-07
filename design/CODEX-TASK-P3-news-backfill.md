# Codex task P3: back-fill 30 and 90 days of news history

Read `AGENTS.md`, `design/CODEX-ACCEPTANCE-PROTOCOL.md` and `design/CODEX-TASK-P0-timeline.md`.
Branch `codex/p3-news-backfill` from `main`. Open a pull request. **Do not merge.** Run the backfill only after the owner says "run backfill".

## Why
The Globe page can show history for 7D/30D (P0), but the archive starts 15 Oct 2026 (about 22 days). The owner wants 30 days now and
90 days later. Live RSS feeds keep only about 0.3–8 days of items, so history needs a different source.

## Facts already measured (2026-11-06/07)
- RSS: unusable for history (items span 0.3–8 days per feed).
- GDELT DOC 2.0: free, metadata only (headline, link, date, domain, country, language), roughly 3 months of depth, rate-limited
  (about 280 HTTP 429 errors per week in the live robot).
- Official archives (central banks, regulators, exchanges) publish dated press releases; check each one's archive page and robots.txt.
- Current archive: 6,490 full articles and 6,635 events, 15 Oct to 6 Nov.

## Scope
1. **Source list (`data/backfill-sources.json`):** each source with: name, URL pattern, date range it covers, type (gdelt / official /
   publisher archive), licence/terms URL, robots.txt result, rate limit used. Only sources whose terms allow storing a headline,
   link and our own summary.
2. **Backfill script `tools/backfill_history.py`** (new, deterministic except the AI summary step):
   - fetch by day (oldest first), resumable (a day file is written atomically once complete);
   - rate limit: one GDELT request per 6 s (their stated limit), exponential backoff on 429, stop after 20 consecutive failures;
   - de-duplicate against the existing archive by normalised URL, then content fingerprint, then headline similarity (same rule as
     `news_core.dedupe`); keep distinct developments even when syndicated (keep the first source, record the others);
   - event location from the article text, validated against the existing location rules (no publisher-country defaults);
   - write `assets/globe/events/YYYY-MM-DD.json` in the same shape as current day files; mark every backfilled item `"backfill": true`;
   - **never** write to the news robot's live files, the frozen prediction files, or the Track Record.
3. **AI cost control:** backfilled items get the cheap deterministic summary (headline + source + location) by default. Gemini
   summaries only if the owner approves a budget. Write the estimate before running: items per day, tokens, calls, cost (see
   `update_globe_news.py` for the prompt size used today).
4. **Quality gate:** a random sample of 100 backfilled items is checked by hand (owner or Codex with a written checklist) for
   relevance (financial/economic), correct country, no duplicates. Report precision. Gate: 90% relevant, 95% correct country.
5. **Labelling:** the globe shows backfilled items with the same card as live ones, plus a small "Backfilled" tag in the card.
6. **Days 30 then 90:** run 30 days first; only after the gate passes and the owner says so, run 90.

## Do not change
Frozen predictions, Track Record, `v5-*`, live robot schedule, `news-live.json` / `news-archive.json` contents, globe design,
homepage. No secrets in code (keys from the environment). No paid API calls without owner approval.

## Acceptance criteria
1. `backfill_history.py --dry-run` prints per-day estimates (articles found, duplicates removed, calls, cost) for 30 and 90 days.
2. A 3-day trial run writes valid day files and passes the schema check; re-running it writes nothing new (idempotent).
3. Duplicate rate reported; no duplicate URLs in the output.
4. Every backfilled item has source name, original link, date, `backfill: true`; no AI-written text presented as article text.
5. Quality gate sample: precision and country accuracy reported with the sample size and method.
6. Globe 30D shows the backfilled days (count matches the files); live and 48H counts unchanged.
7. Build clean; tests from `main` still pass.

## PR must include
Source table, dry-run estimates, trial-run counts, duplicate rate, quality sample results, cost actually spent (should be 0 until
the owner approves), files changed.

## Addition (owner, 7 Nov): connections for back-filled news, both globes
- Every back-filled day must get connection lines exactly like live news: run the same connection engine (globe-lines-v3 + registry) over the history, not a separate one.
- Do this for **News mode** (story links between countries) and **Markets mode** (links between markets/exchanges when one story moves several markets, e.g. "One story, multiple markets: a financial event connecting Japan and the United States").
- **As few doubles as possible:** group the same story from different sources into one cluster before drawing (same event + same countries + within 48 h = one line). Test: no two lines with the same pair of countries for the same cluster.
- **Look for more useful sources** for the history (official statistics, central banks, exchanges, reputable wires with an allowed feed). List each new source with its licence/terms in the PR. No scraping where the terms forbid it.
- **Gemini allowed as a helper** to decide which countries/markets a story connects. Rules: key only as GitHub secret `GEMINI_API_KEY` (owner adds it, never in code); every link Gemini suggests must be backed by a country or company actually named in the article text, otherwise drop it; store the reason text with each link; report the cost per 1,000 articles in the PR.
- Acceptance: 30D view shows lines on back-filled days in both modes; double-line test passes; a sample of 50 random links checked by hand in the PR (≥ 95 % correct).
