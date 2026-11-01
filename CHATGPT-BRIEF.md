You are reviewing the prediction system of my website, Investedia (investedia.com): a financial news site with a live 3D news globe. For every important news story it makes a short-term "call" on an affected asset (Long or Short), freezes it, and later judges it against the real price. I want your honest, critical second opinion: what we did right, what is weak, and how to make the predictions genuinely more accurate. Do not just praise it.

## How calls are judged (fixed rules, never changed after the fact)
- A call starts at the moment it is made (not when the article appeared), so no price move before the call is credited.
- Entry = first traded price at/after the call; exit = first traded price after the horizon (next session close or 24–48 h) in the asset's own market session.
- Flat if the move is below a noise floor (about 0.5× the asset's daily volatility); else hit or miss.
- Every call is frozen and timestamped in git; calls can never be edited or deleted.

## What happened so far
1. **Old engine (v1–v3)**: an LLM (Gemini) read each story and guessed direction. Real results: early calls 52.7% (129/245, p=0.44 — a coin flip); live 8 hits / 4 misses / 5 flat. No edge.
2. **Engine v4**: rebuilt as a structured pipeline. The LLM only extracts facts (event type, actual vs expected numbers, catalyst size, which assets, stance); deterministic frozen rules decide; abstains on weak cases ("No View": commentary, previews, price recaps, indirect assets, competing catalysts, unresolved assets); two tiers (Market View, Priority Insight); context at publication (pre-move in σ units, 5-day trend, index/sector move).
   - Re-run on all 3,336 stories since Oct 21 (rules frozen first): 746 Market Views covering 71% of eligible events; 317 judged: **55.8%** (177/140). Same calls "always long": 55.5%; "follow the index": 58.8%. Only 5 Priority Insights in 10 days. **No edge over trivial baselines.**
3. **Diagnosis on Oct 21–27 (design window, 252 judged)**: calls in the direction the price had *already* moved before publication hit 43%; calls where it had not hit 65%. Earnings calls 48%, shorts 45%.
4. **Engine v5** = v4 + one rule: publish only if the price has not already moved in the call's direction (direction × pre-move σ ≤ 0). Design window: 64.9% on 114 calls — but "always long" scored 65.8% on the same calls, so it may mostly capture mean reversion, not news. Rule frozen in git **before** the held-out test (Oct 28–31), which is judged Monday Nov 2 after the US close. v5 is live on the site now; its past-news calls are shown labelled "Backtest".

## What we are building now: v6
- **Data**: SEC 8-K filings 2022→2026 for ~460 US companies (exact acceptance time, items, press-release text); prices after each event vs its sector ETF; Finnhub earnings surprises and analyst rating changes; market mood (VIX, index trend). Later (v6.1): insider buying (Form 4), short interest, macro surprises (FRED + calendar), GDELT historical headlines, crypto on-chain.
- **Method**: train 2022–2023, validate/select features on 2024 (any source that doesn't help is dropped), then score v5 and v6 **once** on a sealed test period Jul 2025 – Oct 2026 against "always long" and "follow the index", with confidence intervals. The winner goes live; the 16-month test record is shown labelled Backtest; new calls go live from the switch.
- **Infrastructure**: static site on GitHub Pages; robots on GitHub Actions; a Cloudflare Worker serves prices and acts as an alarm clock that starts the news robot every 5 min and the engine every 10 min; Gemini (free tier) for extraction.

## Constraints
- Free tools only (student budget). No paid data feeds.
- Real data only; never backfill or cherry-pick; informational wording only (no personal advice); "Not investment advice".
- Realistic target: ~60–65% sustained, clearly above "always long".

## Questions for you
1. Is the methodology sound? Any leakage or bias we missed (look-ahead, survivorship, event-time alignment, overlapping calls)?
2. Which features/signals have the strongest documented evidence for 1–2 day moves after news (e.g. earnings surprise, PEAD, analyst revisions, insider buying)? What is a realistic accuracy ceiling?
3. Better targets? (raw direction vs move relative to sector vs "big move vs no move")
4. Which model would you use for v6 (gradient boosting, logistic regression, LLM-scored features) and how should confidence/abstention thresholds be set without overfitting?
5. Any free data sources we're missing?
6. How should results be presented on the site so they are credible and honest, and look trustworthy to a potential paying user?
