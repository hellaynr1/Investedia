# Engine v6 — earnings-reaction engine: audit, data, models, results

Research only, on `engine-v6`. Nothing here is published, deployed or merged. V5 stays the production engine. Not investment advice.

## 1. Audit (what existed, what was wrong)

- **V5 (production):** news-driven calls; live ledger today 153 calls: 19 hits, 18 misses, 4 flat, 112 pending. Its own held-out replay test failed (51.4%, 55/107, CI 42–61). The earlier 55.8% (177/317) figure was not reproduced and is treated as history only.
- **V6 tracks A–C:** SEC 8-K index, 22,198 recovered acceptance timestamps, verified Exhibit 99 cache, 6,386 daily price histories (2021-10 → 2026-10-30), Nasdaq earnings calendar 2022-01 → 2026-10, Finnhub cache. Track D (training/eval) had code but **zero provenance-complete events**, so no model had ever been fit.
- **Weaknesses found:** (a) SEC rows carry filing dates, not proven first-public times, and Exhibit 99 coverage is still partial; (b) the earnings calendar almost never says before-open/after-close (99.4% `time-not-supplied`); (c) SPY-adjusted labels are biased: the median stock lags the cap-weighted index (on random non-earnings days liquid stocks finish below SPY 51.8% of the time in 2025–26), so 'always short vs SPY' looks like an edge; (d) daily bars cannot prove the first trade after a call.
- **Fixes in this work:** the timing problem is removed by entering at the open of the first session strictly *after* the report day (after any pre-market or after-hours release); the bias is removed by labelling against the **median liquid stock** that session (`tools/v6/universe_median.py`); one event per ticker per 20 sessions; split-unadjusted series spanning a split are dropped; a point-in-time unit test proves features ignore every bar from the entry close onward.

## 2. Historical data coverage

- Earnings events with EPS + consensus + prices: 53,691; kept 53,232 (3,437 tickers). By entry year: 2022 10,624, 2023 10,955, 2024 11,246, 2025 11,708, 2026 8,699.
- Labels vs median stock: up 22,245, down 23,513, flat (|move| < 0.25σ) 7,474. Sector-ETF label available for 5,219 (sector map covers only ~380 tickers).
- Rejected: outside-price-window 407, duplicate-within-20-sessions 24, no-price-history 28.
- Not yet usable as training events: SEC 8-K/EX-99 news events (provenance gaps), free historical news with original timestamps. Claude Haiku extraction was **not** run (no spend).

## 3. Pipeline

`python3 -m tools.v6.universe_median && python3 -m tools.v6.earnings_dataset && python3 -m tools.v6.earnings_model && python3 -m tools.v6.earnings_final` — offline, deterministic, no network, no API calls. Tests: `python3 -m unittest tests.test_v6_earnings`.
Splits fixed in advance (Track D contract): TRAIN 2022–23, VALIDATION 2024, TEST 2025-01 → 2026-10 (never used for any choice), 5-session embargo at each boundary. Call = open of the session after the report day; exit = next open (~24 h). Features (19): surprise size/sign, prior surprise, analyst count, report-day and overnight reaction (σ-scaled), 5/20/60-day relative momentum, volatility, dollar volume, report-day volume ratio, SPY trend/vol, VIX. CIs: bootstrap over trading days.

## 4. Baselines vs candidates (decisive outcomes only; flat reported separately)

| Model | Validation 2024 (100%) | TEST 2025–26 (100%) |
|---|---|---|
| always long | 48.0% (4650/9681) [46.5–49.7] · -25 bp | 48.3% (8449/17504) [47.2–49.4] · -30 bp |
| always short | 52.0% (5031/9681) [50.3–53.5] · +25 bp | 51.7% (9055/17504) [50.6–52.8] · +30 bp |
| random 50 50 | 50.3% (4873/9681) [49.4–51.3] · +6 bp | 50.1% (8762/17504) [49.3–50.7] · -5 bp |
| surprise sign | 50.4% (4539/9010) [49.4–51.3] · +16 bp | 50.1% (8218/16412) [49.2–50.9] · +4 bp |
| follow reaction | 50.3% (4865/9681) [48.9–51.6] · +18 bp | 49.5% (8666/17504) [48.6–50.4] · +8 bp |
| fade reaction | 49.7% (4816/9681) [48.4–51.1] · -18 bp | 50.5% (8838/17504) [49.6–51.4] · -8 bp |
| sector market momentum | 49.3% (4777/9681) [47.8–51.2] · -0 bp | 49.6% (8681/17504) [48.5–50.6] · -6 bp |
| logistic (all calls) | 51.4% (4972/9681) [49.7–52.7] · +19 bp | 50.7% (8871/17504) [49.7–51.6] · +14 bp |
| lightgbm (all calls) | 53.2% (5152/9681) [52.0–54.3] · +40 bp | 51.2% (8964/17504) [50.4–51.9] · +14 bp |
| ensemble (all calls) | 52.4% (5071/9681) [50.9–53.7] · +33 bp | 51.0% (8930/17504) [50.1–51.8] · +15 bp |

Brier (TEST, decisive): logistic 0.2506, lightgbm 0.2513, ensemble 0.2505 vs 0.2500 for a constant 50%. Isotonic calibration on 2024 did not improve TEST Brier (it slightly worsened it), i.e. probabilities carry almost no information.

## 5. Win rate vs coverage (validation-picked model = LightGBM; thresholds set on 2024)

| Coverage | Validation 2024 | TEST — trained 2022–23 | TEST — walk-forward, trained 2022–24 | 'always short' on the same TEST calls | paired p (walk-forward vs always-short) |
|---|---|---|---|---|---|
| 10% | 61.3% (593/968) [57.6–64.3] · +135 bp | 53.9% (881/1636) [51.4–56.5] · +59 bp | 57.1% (770/1349) [54.2–59.9] · +101 bp | 54.7% | 0.12 |
| 20% | 59.7% (1162/1945) [57.0–62.6] · +113 bp | 52.4% (1891/3606) [50.8–54.3] · +27 bp | 55.0% (1678/3053) [52.9–57.0] · +64 bp | 54.2% | 0.47 |
| 30% | 57.5% (1672/2906) [54.8–60.1] · +80 bp | 52.2% (2850/5461) [50.8–53.4] · +31 bp | 53.1% (2531/4768) [51.5–54.7] · +41 bp | 52.6% | 0.62 |
| 50% | 55.2% (2681/4853) [53.3–57.1] · +61 bp | 51.5% (4683/9100) [50.5–52.6] · +19 bp | 52.1% (4331/8310) [50.6–53.5] · +30 bp | 52.5% | 0.63 |
| 75% | 54.4% (3954/7267) [53.0–56.0] · +51 bp | 51.3% (6888/13422) [50.3–52.2] · +15 bp | 51.9% (6613/12738) [51.0–53.1] · +23 bp | 51.9% | 1.00 |
| 100% | 53.2% (5152/9681) [52.0–54.3] · +40 bp | 51.2% (8964/17504) [50.4–51.9] · +14 bp | 51.7% (9049/17504) [50.8–52.5] · +20 bp | 51.7% | 0.95 |

Large validation→test decay (e.g. 61% → 54% at 10% coverage) shows the validation numbers are optimistic. The ablation (`results.json`) shows no feature group whose removal clearly hurts validation Brier; the model mostly learns the short bias plus market regime (SPY trend, VIX).

## 6. Verdict

**The v6 earnings engine does not outperform simple baselines out of sample.** Its best TEST result (walk-forward, top 10%: 57.1%, 1,349 decisive calls, CI 54.2–59.9) is not statistically better than shorting the same events (54.7%, paired p = 0.12). At 100% coverage it equals always-short (51.7%). Compared with V5 (held-out 51.4%, n = 107) it is not demonstrably better either, and it covers a different event set (earnings only). **V5 stays the production engine.** No Priority Insight tier can be justified from these results: a tier must be a statistically stronger subset, and none is.

## 7. Shadow mode

`python3 -m tools.v6.shadow_earnings` (after the US open) freezes one record per earnings event of the previous session into `research/v6/shadow/earnings-calls.jsonl` (append-only, `frozen_at`, p_up, tier priority/view/none, all features); `--resolve` scores them later from the first open after the freeze (stricter than the backtest). Nothing is published. First run: 245 events from 2026-11-03 frozen (4 priority, 40 view, 201 no view). `.github/workflows/v6-shadow.yml` runs it on `engine-v6` (manual dispatch; GitHub only runs schedules from the default branch, so automatic daily runs need the workflow file on main — that needs your approval).

## 8. Limitations and next steps

1. Exact release timing (before open / after close) would let the call be made at the first open after the release instead of a day later; the reaction-day information is mostly priced in by our entry. Sources: SEC 8-K Item 2.02 acceptance timestamps (already 22k cached) joined to the earnings calendar.
2. Guidance, revenue surprise and management tone are absent; these need EX-99 text + Claude Haiku fact extraction (estimated a few dollars for ~5k releases; needs your approval).
3. Longer horizons (5–20 sessions, post-earnings drift) and sector-relative labels need a point-in-time sector map beyond ~380 tickers.
4. Daily bars only: intraday entry cannot be proven; the shadow ledger is the honest forward test.
5. Re-run this report after 3+ months of shadow data before any production decision.
