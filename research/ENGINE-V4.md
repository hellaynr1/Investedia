# Prediction Engine v4: design and frozen rules

Status: **design frozen 2026-10-31, before any v4 prediction exists.** Changing a rule in §5–§8 after the first v4 call
requires a new engine version (v4.1, …) recorded on every call. Public name: *Investedia Prediction Model · Prediction Engine v4*
(internal id `pe-v4`). Engine v3 (ranked impact tiers, branch `asset-intel`) was never released; its tiering is folded into v4.

## 1. Audit of the current live engine (Prediction Engine v2, `impact-gemini-v2`)

| Step | What happens today |
|---|---|
| Article → event | Gemini, per robot run, merges candidate headlines of the same batch ("members"); `news_core.dedupe` drops near-identical titles. No stable cross-run event id yet (event-id work in review). |
| Assets | Gemini lists ≤6 "impacts" (company/asset/sector/country), primary/secondary role; tickers resolved by the registry; sector/country rows are never scored. |
| Direction | Gemini writes `up/down/mixed/unclear` per impact from the article text. Only `up/down` with a resolved asset becomes a call. |
| Magnitude | **None.** |
| Confidence | Gemini's own `high/medium/low` label. Never calibrated; 120 of 176 live calls are "high". |
| Event type | Gemini `event_type` (14 values). Stored on the story, **not used by any logic**, not frozen on the call. |
| Horizon | Fixed 24 h for everything. |
| Market context | **None**: the prompt sees headline + short description only; no prices, no index, no prior move. |
| Duplicates | Every article's impacts are frozen separately: one story covered by 10 articles = 10 calls (Binance hack: 25 articles). |
| Abstention | Only implicit: `mixed/unclear`, unresolved tickers, sector/country rows. No "no call" decision, no reasons. |
| Outcome | outcome-v3: entry = first traded price after the proven public time; end = first traded price ≥ 24 h later; ±0.3 % flat band; index benchmark stored. |
| Frozen at creation | article id, symbol, asset id, direction, confidence label, created/public/start, engine version, model, headline, category, article time. |
| Used by | Market Implications and Track Record read the same ledger (`news-ledger.json`); Early calls are a separate file. |

**Five biggest weaknesses limiting real edge**
1. **No expectations.** Direction comes from how the article *sounds*, not from actual vs expected. Markets price surprises.
2. **No market context.** The engine cannot know the asset already moved, the index moved more, or volatility is high; "Bitcoin falls after hack" is called *after* the fall.
3. **Forced calls.** Commentary, previews, price-move recaps and indirect relationships still become directional calls; nothing abstains on purpose.
4. **Correlated duplicates.** One event produces many "independent" calls, inflating both wins and losses and any accuracy figure.
5. **Uncalibrated, unused metadata.** Confidence is a label, event type and horizon are not used, magnitude does not exist, so there is nothing to tune *honestly* and nothing to calibrate.

Measured evidence: the first engine scored 52.7 % (v2 historical method, p = 0.44 vs a coin flip) and lost to "follow the index"
(51.9 % vs 62.5 %, p = 0.03). The live engine has 17 judged calls: too few to say anything yet.

## 2. Architecture of v4 (shadow first, then promotion)

```
article ─► [1 extract]  LLM → structured record (no direction decision):
                         event_type (15 classes), catalyst facts with numbers *as stated*, expectation fields
                         (actual / expected / previous, or "unavailable"), relationship directness per asset,
                         flags: commentary, preview, price-move recap, competing catalysts, already-priced language,
                         LLM stance per asset (+/−/0) with a one-line reason
         ─► [2 resolve]  registry ids; asset class; benchmark index + sector ETF
         ─► [3 identity] stable event id (event_ids.py); one decision per event × asset × horizon
         ─► [4 context]  code, from prices at publication: asset move since previous close and last 24 h, in σ units;
                         index and sector move; 5-day trend; 20-day volatility; session state (open / pre / after / closed)
         ─► [5 decide]   deterministic policy table per event type: direction = Long | Short | No call, with the
                         reason codes for every abstention; raw score from frozen feature weights
         ─► [6 confidence] raw score → probability through a calibration map fitted on VALIDATION only, then frozen
         ─► [7 magnitude] expected move range = event-type × asset-class base (in σ), scaled by catalyst strength
         ─► [8 freeze]   full prediction record (§9) → shadow ledger; published to the site only after promotion
```
The LLM never decides publication. Direction, abstention, confidence and horizon are code + frozen tables, so every call is reproducible.

## 3. Versions (kept separate on every record)
- `engine`: pe-v4 (and `prompt` hash, `model` name). Existing v1/v2 calls stay frozen, untouched.
- `outcome_rule`: outcome-v4 for v4 calls (variable horizon, class floors, relative moves). v2 calls keep outcome-v3.
- `policy`: hash of the frozen tables in `engine/policy.py`; `calibration`: id of the frozen calibration map.

## 4. Event taxonomy (15)
earnings · guidance · m&a · financing (debt/equity raise, buyback) · analyst (rating/target change) · product (launch, contract) ·
legal-regulatory · management · macro-data · central-bank · geopolitical · commodity-supply · trade-tariff · crypto · other.

## 5. Horizon table (frozen; from the entry price)
"S1" = close of the first full trading session after entry; "S2" = close of the second. 24/7 and near-24 h markets use hours.

| Event type | Equity | Index | FX | Commodity | Crypto |
|---|---|---|---|---|---|
| earnings, guidance, financing, management | S1 | S1 | — | — | — |
| m&a | S1 (target), S2 (acquirer) | — | — | — | — |
| analyst | S2 | — | — | — | — |
| product, legal-regulatory | S1 | — | — | — | 24 h |
| macro-data | S1 | S1 | 6 h | 6 h | 6 h |
| central-bank | S1 | S1 | 24 h | 24 h | 24 h |
| geopolitical, trade-tariff | S2 | S2 | 48 h | 48 h | 48 h |
| commodity-supply | S2 | S2 | 48 h | 48 h | — |
| crypto | — | — | — | — | 24 h |
| other | S1 | S1 | 24 h | 24 h | 24 h |
"—" = this combination does not produce calls in v4 (abstain: `unsupported-combination`).

## 6. Abstention rules (frozen; any one ⇒ No call, reason code stored)
`commentary` · `preview` · `price-move-recap` (story mainly reports a move, no new catalyst) · `indirect` (relationship not
subject/target/acquirer/direct counterparty/policy-rate/commodity-output) · `competing-catalysts` · `stance-neutral` ·
`no-expectations` (earnings, guidance, macro-data, central-bank without expected values) · `already-moved` (asset moved ≥ 1.5 σ
in the called direction between previous close and publication) · `unsupported-combination` · `duplicate-event` (event × asset ×
horizon already called) · `below-threshold` (calibrated confidence < frozen publish threshold, chosen on validation).

## 7. Direction policy (frozen)
- With expectations (earnings, guidance, macro-data, central-bank): direction = sign of the surprise when |surprise| ≥ the
  type's floor (EPS/revenue 2 %, guidance midpoint 1 %, macro 0.5 × the series' historical surprise σ when available, else any
  non-zero beyond rounding, rates 10 bp); conflicting surprises (e.g. EPS beat, revenue miss) ⇒ the guidance sign if stated,
  else `competing-catalysts`. Asset mapping: equities the company; macro/central-bank: currency (higher-than-expected
  inflation/rates ⇒ currency long), index (⇒ short), gold (⇒ short).
- Without expectations (m&a, financing, analyst, product, legal, management, geopolitical, commodity, trade, crypto, other):
  direction = LLM stance only if directness passes and no abstention rule fires; m&a targets of cash offers at a premium ⇒ long
  target; equity raise ⇒ short issuer; downgrade ⇒ short, upgrade ⇒ long.
- Context never flips a direction; it can only cause abstention (`already-moved`) or lower the score.

## 8. Score, confidence, magnitude (frozen form; numbers fitted on validation only)
- Raw score = sum of frozen points: expectations available (+2), |surprise| ≥ 2× floor (+1), direct subject (+1), single
  catalyst (+1), context agrees (asset not already moving the other way, +1), LLM stance agrees with surprise sign (+1).
- Confidence = calibration map(raw score, event-type group), isotonic, fitted on the validation set, then frozen.
- Publish threshold: the lowest confidence bucket whose validation accuracy beats both "always long" and "follow the index"
  with ≥ 30 calls; frozen before the holdout starts.
- Expected move: base |move| = m(event type, class) × σ_h (σ_h = 20-day daily σ × √(horizon/1 day)), m from the development set,
  × 1.5 when |surprise| ≥ 2× floor; reported as a range [0.5×, 1.5×] with the sign of the direction. Never used to judge
  direction.

## 9. Prediction record (frozen at creation; outcome fields appended, never overwritten)
prediction id · event id · article id · asset id/symbol · asset class · event type · created / public / start · engine, prompt,
policy, calibration ids · decision (long/short/none) + reason codes · confidence · expected move range · horizon code ·
benchmark index + sector ETF · catalyst fields (surprise %, premium %, size % of market cap, bp…) with explicit `null` = unavailable ·
expectations-available flag · context fields (pre-publication move σ, index/sector move, trend, vol, session) ·
then outcome-v4: entry, exit, asset move, index move, sector move, relative move, verdict, magnitude error.

## 10. Outcome rule outcome-v4 (for v4 calls)
Entry = first traded price at or after the proven public time. Exit per §5 (S1/S2 = session close; hours = first price at or after).
Verdict: |move| < max(class floor, 0.5 σ_h) ⇒ no clear move; else hit/miss by sign. Class floors: equity 0.3 %, index 0.2 %, FX 0.1 %,
commodity 0.3 %, crypto 0.5 %. Also stored: index move, sector move, relative move = asset − benchmark (second metric: event alpha).

## 11. Evaluation (no tuning on the holdout)
- **Development** (design only): early calls 21–30 Oct, live v2 calls, and a v4 *replay* of archived articles since 15 Oct
  (after the model's training data; still treated as development only).
- **Validation** (fit calibration, choose threshold, enable/disable event types): the first 300 judged forward v4 shadow calls.
- **Freeze** v4 policy + calibration + threshold (git tag `pe-v4-frozen`).
- **Holdout** (never used to tune): the next 400 judged forward v4 calls *after* the freeze.
- Metrics per version: calls, abstention rate (+ reasons), direction accuracy (hits / (hits + misses)), no-clear-move rate,
  Wilson 95 % interval, exact binomial vs 50 %, paired McNemar vs always-long, follow-the-index, follow-the-sector and v2 on the
  same events, calibration (bucket accuracy vs stated, ECE, n ≥ 30 per bucket), magnitude MAE / median AE vs a naive σ baseline,
  relative-move accuracy, by event type / class (n ≥ 30 to display).
- Power: detecting 55 % vs 50 % needs ≈ 780 independent calls (80 % power, α = 0.05); 57 % needs ≈ 400. Claims wait for that.

## 12. Data
Existing: articles + event archive, registry (identity, class), exchange bars (5-min ≤ 60 days; daily years), index and sector ETF
prices, macro calendar with consensus for 130/236 releases (ForexFactory), earnings calendar with EPS estimates (Nasdaq).
Needs new data: revenue/guidance consensus (only when the article states it, otherwise `unavailable`), macro surprise history
for σ, pre/post-market quotes (Yahoo `includePrePost`). Licensing caveats in YAHOO-AUDIT.md / DATA-LICENSING.md apply.

## 13. Known risks
LLM look-ahead: any backtest on events before the model's training cutoff is contaminated; only forward shadow results count as
evidence. Sample size: weeks of forward data before any claim. Article-stated expectations can be wrong: stored verbatim with source.
