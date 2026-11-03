# v6 data decision — 2026-11-03

Engine-v6 remains offline research. A filing, document, or price history is not a
judged prediction. The current zero-call evaluation cannot support an accuracy
percentage or deployment decision.

## What is already present

* Official SEC 8-K index: 330,824 accession records. Verified Exhibit 99 and
  acceptance-time sidecars are growing separately from the raw index.
* Daily research price histories: 5,985 Yahoo and 400 Tiingo files. The price
  manifest also lists 893 missing symbols, 813 marked by the Tiingo monthly cap.
* Nasdaq earnings history and the existing Claude factual extractor. The new
  Exhibit 99 excerpts have not been sent to Claude; collection cost is $0.

## Collection and validation order

1. Complete bounded SEC attachment discovery. Cache original accession pages,
   hashes, acceptance clocks, and readable release text; review rejected links
   before expanding their parser. Keep one verified event identity per accession.
2. Audit price coverage *for those events*, including delisted symbols, corporate
   actions, and the first trade after the earliest proven publication time.
   Daily next-open labels remain explicitly marked proxies where intraday data
   cannot be sourced. Missing prices stay unresolved, never losses.
3. Build historical examples using the original as-filed release and only facts
   available by each replay cutoff. Separate historical replay from actual frozen
   public calls. The latter must never be rewritten by a backtest.
4. Compare fixed factual rules and simple always-long/always-short baselines
   against a trained candidate, with 2022–23 development, 2024 validation and
   later years locked until policy freeze. Report sample size, coverage,
   confirmed/other-way/flat rates, and each missing-data reason.
5. Trial a new news source only after a small timestamp/document-version and
   licensing audit. Accept it only if later-period ablations improve a useful
   metric without collapsing coverage. Retrospective sentiment is not an
   original-time fact.

## Source decisions

* Alpha Vantage NEWS_SENTIMENT: potential secondary news coverage; no v6
  integration or verified historical article-version provenance exists yet.
  Free quota/retention/licensing must be checked against the actual account.
* Stooq: possible independent price cross-check, not a publication-time source.
* Polygon/Massive: potentially useful for timestamped trade bars and delisted
  coverage, but neither is connected. Check exact historical access and display
  rights before committing to a plan; no paid infrastructure is assumed.
* Kaggle news corpora: optional language research only until original publish
  time, revisions, ticker identity, duplication, and license are auditable.
* Postal codes: entity/location metadata only. Do not treat a headquarters ZIP
  as predictive evidence without a specific, validated geographic exposure.

GitHub Actions is the bounded historical collector and evaluator. The existing
Cloudflare worker can serve prompt live capture, but moving a historical backtest
there would not improve label quality. Neither host should silently publish v6
direction calls while holdout validation is absent.
