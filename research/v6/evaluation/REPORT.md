# v6 Track D evaluation

As of 2026-11-02T00:00:00Z. Informational research; not investment advice.

Status: OFFLINE. No trained/frozen v6 model; OOS locked. No claim of improvement.

## Cache inventory

- sec_filings: 330824
- filings_with_exhibit99: 0
- claude_unique_extractions: 0
- duplicate_fact_rows: 0
- claude_tracked_cost_usd: unknown / not recorded
- extraction_failures: unknown / not recorded
- uncollected_batches: 0
- price_files: 6385

Frozen research rows accepted: 0; rejected: 0.

Cache counts are not evaluated calls. Claude failures/cost are unknown when no manifest exists.

## Development and validation

| Split | Judged | Confirmed | Other way | No clear move | Pending | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| TRAIN | 0 | 0/0 (N/A) | 0/0 (N/A) | 0/0 (N/A) | 0 | 0 |
| VALIDATION | 0 | 0/0 (N/A) | 0/0 (N/A) | 0/0 (N/A) | 0 | 0 |

## Coverage versus quality

| Split | Minimum score | Accepted / eligible | Judged | Confirmed / judged |
|---|---:|---:|---:|---:|
| TRAIN | None | 0/0 | 0 | 0/0 |
| TRAIN | 50 | 0/0 | 0 | 0/0 |
| TRAIN | 55 | 0/0 | 0 | 0/0 |
| TRAIN | 60 | 0/0 | 0 | 0/0 |
| TRAIN | 65 | 0/0 | 0 | 0/0 |
| TRAIN | 70 | 0/0 | 0 | 0/0 |
| VALIDATION | None | 0/0 | 0 | 0/0 |
| VALIDATION | 50 | 0/0 | 0 | 0/0 |
| VALIDATION | 55 | 0/0 | 0 | 0/0 |
| VALIDATION | 60 | 0/0 | 0 | 0/0 |
| VALIDATION | 65 | 0/0 | 0 | 0/0 |
| VALIDATION | 70 | 0/0 | 0 | 0/0 |

## Detailed measurements

metrics.json contains direction, tier, event type, horizon, calibration, same-event long/short baselines,
individual/group fact-rule ablations, raw and sector-relative labels, and threshold coverage.
Empty groups mean no observations, not zero predictive performance. Candidate ablations are untrained
rule comparisons on directional calls only; they cannot establish the value of a trained v6 model.

## Limitations and remaining gates

- No provenance-complete historical calls or collected Claude facts in the audited branch.
- SEC filing dates lack acceptance timestamps; Nasdaq retrospective consensus has no vintage proof.
- Index has no EX-99 document entries: the current Claude candidate selector has zero eligible documents.
- Daily next-open proxies cannot prove first intraday trade; sector mapping still required.
- Split adjustments, ticker reuse, delistings, early closes and incomplete free prices require review.
- Calibration is descriptive score bucketing, not probability calibration. No Brier/log loss claim.
- Fit two-stage model on TRAIN, select/calibrate on 2024, commit freeze, then unlock OOS in a separate change.
- Market/sector-follow and v5 baselines need pre-call context not currently supplied; unavailable.
- Cluster bootstrap and training-versus-holdout failure flags require a populated evaluation cohort.
- Keep v6 offline. The tiny live v5 sample is not v6 evidence. No API calls made by this tool.
