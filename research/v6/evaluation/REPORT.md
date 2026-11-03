# v6 Track D evaluation

As of 2026-11-03T18:33:37Z. Informational research; not investment advice.

Status: OFFLINE. No trained/frozen v6 model; OOS locked. No claim of improvement.

## Cache inventory

- sec_filings: 330824
- filings_with_acceptance_timestamp: 22198
- filing_indexes_discovered: 0
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
rule comparisons using independent research labels; they cannot establish the value of a trained v6 model.

## Limitations and remaining gates

- No provenance-complete historical calls or collected Claude facts in the audited branch.
- SEC filing dates lack acceptance timestamps; Nasdaq retrospective consensus has no vintage proof.
- Verified Exhibit 99 filings in this checkout: 0; discovery requires SEC access.
- Daily next-open proxies cannot prove first intraday trade; sector mapping still required.
- Split adjustments, ticker reuse, delistings, exceptional closures and incomplete free prices require review.
- Calibration is descriptive score bucketing, not probability calibration. No Brier/log loss claim.
- Fit two-stage model on TRAIN, select/calibrate on 2024, commit freeze, then unlock OOS in a separate change.
- Market/sector-follow and v5 baselines need pre-call context not currently supplied; unavailable.
- Seeded event-cluster intervals and training-versus-validation warning flags require a populated cohort.
- Keep v6 offline. The tiny live v5 sample is not v6 evidence. No API calls made by this tool.

## Calibration and baselines

| Score bucket | Judged | Confirmed | Other way | No clear move |
|---|---:|---:|---:|---:|
| 50–55 | 0 | 0 | 0 | 0 |
| 55–60 | 0 | 0 | 0 | 0 |
| 60–65 | 0 | 0 | 0 | 0 |
| 65–70 | 0 | 0 | 0 | 0 |
| 70+ | 0 | 0 | 0 | 0 |

Baseline counts and rates are in metrics.json for the identical evaluated cohort.
Missing model/cohort means performance is unavailable; empty groups must not be read as 0% accuracy.
Run python -m tools.v6.train after building a provenance-complete cohort for two-stage logistic
training, validation Platt calibration, coverage-constrained threshold selection and refitted ablations.
Training writes a candidate only; no policy freeze, OOS unlock or live integration.

## Verification at implementation

25 Track D tests pass. Full Python suite: 149/150 pass; the pre-existing footer test
treats mailto:jobs@investedia.com as a local path. Worker tests: 3/3 pass.
Site build succeeds; generated output restored to keep website files unchanged.
No API credit used, deployment, merge or live-site change.