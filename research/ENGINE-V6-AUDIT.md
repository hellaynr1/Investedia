# Engine v6: audit and proposed architecture (before implementation)

Status 2026-11-01. Nothing below has been implemented except the raw SEC 8-K download (research/sec/, branch engine-v6), which is
kept as raw input only. The rushed "v6-lite" build was cancelled. Live v5 keeps running unchanged until v6 is frozen and approved.

## 1. Current architecture

| Part | Where | What it does | Status |
|---|---|---|---|
| News robots | `update_globe_news.py`; workflows `priority-news.yml` (~10 min, now woken every 5 min by the Worker), `broad-news.yml` | RSS/official feeds (+ Eurostat, PR Newswire) → Gemini summaries → `news-live.json`, `news-archive.json` (last 600 stories), `events/YYYY-MM-DD.json` (event archive with `cluster`) | live |
| Event IDs | `events.py` | story id = hash; `cluster` field groups duplicate stories; stricter grouping rule still unapplied (branch `event-eval`, awaiting owner review) | partial |
| Engines v1–v3 | `update_news_track.py` | LLM direction per story → `news-ledger.json` (179 calls; frozen; outcome-v3 since 31 Oct, earlier verdicts kept in `prev_v2`) | archived, intact |
| Early record | `research/early-*.json`, branch `early-track-record` | 650 pre-live calls, scoring v1/v2 | archived; publication task 4 Nov |
| Engine v4 | `engine/` (policy, extract, context, magnitude, outcome, run, shadow) | Gemini extracts facts; frozen policy decides; tiers; outcome-v4 judging | code reused by v5 |
| Engine v5 | `engine/live_v5.py`, `engine-v5.yml` | v4 + "not already priced in" rule; records `v5-records.json` (append-only), calls `v5-ledger.json`; judged once | **live** since 31 Oct 17:30 UTC |
| v5 backtest | `assets/globe/v5-backtest.json` | v5 rule on Oct 21–31 news | shown on site as one figure "67% BACKTEST" |
| Worker | `workers/live` (Cloudflare) | prices every 2 min (KV), news ingest endpoint, alarm clock (dispatch) every 5 min | live |
| Site | `assets/calls-ui.js`, `implications.html`, `track-record.html`, `call.html` | reads ledgers; Backtest tag; live "Building X of 50" | live |

## 2. Leakage and bias issues found

1. **"Sealed test" Jul 2025–Oct 2026 is not sealed.** The v5 rule was designed on Oct 21–27 2026 outcomes and Oct 28–31 is its declared test.
   Any v6/v5 evaluation window must end **before 2026-10-21**. Fixed below.
2. **The v5 "67% BACKTEST" figure on the site mixes the design window (Oct 21–27, used to choose the rule) with its test window.**
   It is a TRAIN-type number shown as a backtest. Recommendation: show it labelled DESIGN/TRAIN with its baselines, or remove the
   headline figure; the underlying frozen records stay untouched either way. (Owner decision; display only.)
3. **Survivorship bias in the SEC download:** the universe is today's registry tickers mapped through today's SEC ticker file. Delisted,
   acquired, renamed companies are missing. Must be replaced by a point-in-time universe (§4).
4. **Event time:** SEC acceptance time is used as the event time. For earnings, the press release usually goes out on a wire minutes to
   hours earlier, and for after-close releases the 8-K can be filed later still. Must store several timestamps and enter conservatively (§3).
5. **Price data:** Yahoo has no prices for most delisted tickers, and its split-adjusted daily data rewrites history. Free delisted prices are
   limited; this is a real constraint (see risks), measured rather than hidden.
6. **Independence:** v4/v5 stats treat every call as independent (Wilson CI). Several calls on one event or one macro day are correlated.
7. **Target:** v4/v5 judge raw direction; much of the "edge" seen (always-long 55–66%) is market drift, not news.
8. **Owner-visible decisions after seeing results** (e.g. choosing v5's rule from the Oct 21–27 diagnosis) are a form of selection.
   v6 will freeze every threshold on validation data before any OOS number is computed, and record the freeze in git.

## 3. Proposed v6 architecture

**Evaluation periods (time-based, purged):**
| Label | Period | Use |
|---|---|---|
| TRAIN | 2022-01-01 → 2023-12-31 | fit models |
| VALIDATION | 2024-01-01 → 2024-12-31 | feature selection, calibration, thresholds; then **freeze** |
| HISTORICAL OOS | 2025-01-01 → 2026-10-20 | scored once after the freeze; nothing tuned on it |
| LIVE / PROSPECTIVE | from the frozen v6 switch onward | the real evidence |
Events whose horizon window crosses a boundary are purged (plus a 5-trading-day embargo).
2021 is kept only as warm-up for rolling features. Oct 21–31 2026 belongs to v5 design/test and is excluded from v6 numbers.

**Timestamps per event:** `information_public_at` (earliest of: company press release time from the wire/IR or 8-K exhibit date line, SEC
acceptance), `filing_accepted_at`, `investedia_first_seen_at` (live only), `prediction_generated_at`, `entry_timestamp` (first trade
strictly after `max(information_public_at, prediction_generated_at)`; for historical runs, the next session open if public outside hours, else
the next 5-minute bar where available, else the next open: conservative), `exit_timestamp`.

**Events and clustering:** `event_id` (one underlying corporate event), `story_id` (each source document: 8-K, press release, news
article), `cluster_id` (same company + same event type within ±1 trading day, or the existing news cluster), `asset_id`, `event_type`.
One prediction per event × asset × horizon. Statistics use **cluster bootstrap** (resample event clusters / trading days).

**Event universe (v6.0):** earnings surprises; guidance raise/cut; analyst up/downgrades; M&A/takeover; major regulatory decisions;
major litigation; CEO/CFO departures; buyback/dividend/financing. Everything else = No View.

**Features:** only those available at `prediction_generated_at` (listed in the spec: event, earnings surprise/guidance, price context in σ
units over 30 min/1 d/5 d, gap, volatility, volume z-score, SPY/QQQ/sector/VIX, analyst). Gemini extracts facts only.

**Targets:** primary = sector-relative abnormal return over the horizon (stock − sector ETF), classified LONG/SHORT/FLAT by a noise
threshold (0.5 × the stock's 20-day σ of excess returns). Raw return always stored and shown.

**Two-stage model:** A = P(material abnormal move) → below threshold = No View; B = P(positive abnormal move | material).
Models: regularized logistic regression (baseline) and LightGBM; prefer logistic unless LightGBM is clearly better on validation.
Calibration: Platt on validation (isotonic only with enough data). Buckets 50–55/55–60/60–65/65–70/70+. Market View and Priority Insight
thresholds chosen on validation, frozen in `research/ENGINE-V6-FROZEN.json` (git commit = proof), then OOS is scored once.

**Baselines on the same events:** always Long; follow market; follow sector; logistic regression; v5 rule.
**Metrics:** calls/hits/misses/flats, accuracy, 95% cluster-bootstrap CI, coverage, Brier, log loss, calibration, mean/median abnormal
return, by event type, tier, Long/Short, regime (VIX bands).

## 4. Datasets needed (all free)
1. SEC EDGAR full-index 8-K list 2021→2026 (all filers, not just today's tickers), submission headers (acceptance time, items), Exhibit 99.x text.
2. **Point-in-time universe:** SEC `submissions/CIK*.json` (former names, ticker history where present) + historical S&P 500/400/600 membership
   (Wikipedia change tables) to define who was in the universe on each date, including removed/delisted companies.
3. Daily prices (Yahoo; unadjusted + split events) for stocks, SPY, QQQ, sector ETFs (XLK…XLC), VIX (CBOE free history).
4. Finnhub: earnings calendar with EPS/revenue estimate and actual; recommendation trends/upgrades-downgrades (dates); company profile (sector).
5. SEC XBRL company facts (reported revenue/EPS as filed, point-in-time by filing date).
6. Later: FINRA short interest and daily short volume, Form 4, 13D/13G, FRED/ALFRED vintages.

## 5. Reusable
`engine/extract.py` (fact extraction pattern, PROMPT_ID hashing), `engine/context.py` (σ-unit pre-move features), `engine/outcome.py`
(session-aware exits), `engine/shadow.py` (append-only freeze + judge once), `tools/eval/forward_report.py` (coverage-first reporting),
`tools/sec/harvest.py` (fetching/rate limiting; universe logic must change), Worker + workflows, `calls-ui.js` (rendering).

## 6. Must change
Universe (point-in-time), event-time model (multi-timestamp), target (sector-relative), statistics (cluster bootstrap), engine decision
(two-stage calibrated model instead of hand rules), track-record data model (stage labels TRAIN/VALIDATION/HISTORICAL OOS/LIVE per
result set; never one combined headline).

## 7. Implementation order (each stage: tests + measurements + report, no claims without held-out data)
1. Point-in-time universe + event table (8-K → events, clusters, timestamps). Measure: events per year, % with prices, delisted share.
2. Price/label builder (raw + sector-relative, noise threshold, purging). Measure: label balance, coverage, split audit.
3. Feature builder (earnings/analyst from Finnhub, price/market context, XBRL), with an availability-time check per feature.
4. Baselines on train/validation (always long, market, sector, v5 rule, logistic).
5. LightGBM two-stage + calibration + thresholds on validation → **freeze** (commit).
6. Score HISTORICAL OOS once; report vs baselines with cluster CIs.
7. If v6 beats baselines on OOS: live v6 in shadow, then on site with stage-labelled Track Record; archive section for v1–v5.

## 8. Files to create / change
New: `tools/v6/universe.py`, `tools/v6/events.py`, `tools/v6/prices.py`, `tools/v6/labels.py`, `tools/v6/features.py`, `tools/v6/train.py`,
`tools/v6/evaluate.py`, `tools/v6/stats.py` (cluster bootstrap), `engine/v6/model.py` (inference), `research/ENGINE-V6.md`,
`research/ENGINE-V6-FROZEN.json`, workflows `v6-data.yml`, `v6-train.yml`, tests `tests/test_v6_*.py`.
Change later (stage 7 only): `engine/live_v6.py`, `assets/calls-ui.js`, `src/pages/track-record.html`, `src/pages/implications.html`.

## 9. Risks
- Free delisted-stock prices are incomplete → residual survivorship bias; we will measure and publish how many events lack prices.
- Exact press-release times are not always recoverable for 2022–2024; conservative entry (next open) may understate tradable edge.
- Finnhub free-tier history depth/rate limits may cap feature coverage; measured per year.
- Honest outcome may be "no edge over baselines". That result will be reported, not tuned away.
- Gemini free-tier quota limits fact extraction on large historical sets; structured sources (XBRL, Finnhub) are preferred where possible.

## 10. Intentionally NOT changed
All frozen calls and ledgers (v1–v3 `news-ledger.json`, early records, `v5-records.json`, `v5-ledger.json`, `v5-backtest.json`); v5 stays the
live engine until v6 is frozen, tested and approved; outcome rules already published; Worker and news robots; the scheduled v5 held-out
test (Mon 2 Nov) and the early-record publication (4 Nov).
