# Track D audit and contract

Audit of branch 78c568a752876066ae6bebecbdd972def52d78cd, 2026-11-02.
Tracks A/B/C exist: SEC EFTS index, Yahoo/Tiingo daily prices, Nasdaq and Finnhub
caches, and budgeted Claude batch extraction code. No Track D implementation,
training code, frozen v6 policy, frozen v6 calls, or collected Claude facts exists
in this checkout. ENGINE-V6-AUDIT.md is a proposal, not a completion log.
Its referenced tools/eval/forward_report.py does not exist. SEC rows contain a
filing date, not a proven acceptance timestamp. Daily price caches cannot prove
first intraday trade. Today's ticker identity and free delisted coverage remain
limitations; EFTS display names alone do not prove a complete historical universe.

No UI, live ledger, v3/v4/v5 policy or deployment is changed by Track D.
Informational research only; not investment advice.

## Acceptance criteria and data map

1. Frozen timestamps determine entry; missing data remains Pending/unresolved.
2. Feature allowlist and availability/source checks reject leakage.
3. TRAIN 2022–23, VALIDATION 2024, OOS 2025–2026-10-20; purge crossing
   horizons and embargo first five observed SPY sessions of each split.
4. Report denominator counts, No View, pending, groups, thresholds, baselines.
5. Ablation reruns inference from features, never changes a frozen public call.
6. Repeatable local command, input hashes, no network/API requests.

Tests: tests/test_v6_track_d.py. No mockup or screenshot applies: this is a
research pipeline, and there are no website changes.

`python3 -m tools.v6.evaluate --as-of 2026-11-02T00:00:00Z`
reads `research/v6/frozen-calls.jsonl` when available, uses cached prices only,
and writes dataset.jsonl, rejected.jsonl, metrics.json and REPORT.md under
research/v6/evaluation. Missing call file means zero calls, never synthetic calls.

Each input line requires event_id, cluster_id, asset, event_type, tier,
direction (long/short/none), horizon (S1/S2), information_public_at,
prediction_generated_at, public_call_at, publication_proof, frozen_at,
policy_id, features. All timestamps have explicit zones. Each feature is
`{value, available_at, source_kind, source_published_at, source_updated_at}`.
Source kind is original-release, as-filed, or market-bar. Historical extraction
can be executed later, but its document version and facts must be proven available
at the call cutoff. Updated/retrospective text is rejected. one_line and arbitrary
text are never model inputs. Frozen predictions are evaluated as supplied; the
fact-rule candidate is a separate, untrained comparator, not a replacement call.

Daily fallback: next available session open strictly after cutoff (same-day
open only before it), then close of S1/S2 full session AFTER entry session, matching
v4 horizon semantics. This is explicitly a next-open proxy, not proof of the first
trade. Unadjusted series spanning a split are unresolved rather than silently
mislabelled. Missing intervening sessions invalidate the label. Exact timestamped
trades can use calculate_trades; the daily adapter is intentionally conservative.
Primary proposed v6 sector-relative labels require sector ETF + 20 prior paired
returns. Missing sector data does not fall back to the market. Raw outcome-v4
labels remain separate. No confidence is called a probability.

No trained model or thresholds are frozen by this work. OOS is locked until a
separate development/validation freeze exists; no OOS candidate selection occurs.
Historical sample building still needs timestamp/document provenance and a
point-in-time sector mapping. Cache counts are inventory, not evaluated calls.

## Training candidate

`python3 -m tools.v6.train` fits regularized two-stage logistic models using
TRAIN-only feature vocabulary/scales, Platt calibration on 2024, and a validation
coverage-versus-quality grid. Threshold selection maximizes signed abnormal
return subject to at least 20% coverage and 30 accepted validation calls. These
are declared engineering safeguards, not validated product thresholds. Individual
and group ablations refit the models; training-positive/validation-negative
comparisons are flagged. Validation selection is optimistic and is never called
OOS evidence. A minimum 100/50 train/validation cohort, class counts and cluster
counts block meaningless fitting. No model is frozen or published by this command.
Inference is JSON coefficients + standard-library deterministic math; training
requires scikit-learn/numpy (already available here). No paid infrastructure.

Extraction audit: the index contains **zero Exhibit 99 document entries**. EFTS
root-form filtering appears to retain only primary 8-K documents, while Track C
requires EX-99 candidates. Exhibit discovery and acceptance-time provenance must
be repaired upstream before historical extraction can populate this pipeline.
No Anthropic request was issued during this work.

## Verification and completion status

The offline tooling is implemented; the end-to-end historical research is **not
complete**. Zero provenance-complete calls means no fitted model, no empirical
ablation result, no validated threshold, and no holdout superiority claim. Remaining
work is real dataset construction after Exhibit 99/timestamp repair, validated
point-in-time sector assignment, then development/calibration/freeze and OOS.
Market/sector-follow and v5 baselines still need pre-call contextual inputs.
LightGBM comparison is deferred until the logistic baseline has real data.
The existing extractor's quoted rates and budget accounting were not validated
against Anthropic billing; no manifest means actual spending/failures are unknown.

Validation: the new Track D tests cover outcomes, sessions/DST/early closes,
missing data, split breaks, No View research targets, chronological splits,
leakage, cohort guards, deterministic inference and bootstrap, and a synthetic
train/validation coefficient roundtrip (test data only, not research evidence).
The broader Python suite has one unchanged failure in
`test_legal_pages.LegalPages.test_footer_links_and_signup_destinations`:
it treats `mailto:jobs@investedia.com` as a file path. The test and footer file
are byte-identical to audited HEAD. Existing Worker tests pass. Site build passes;
generated changes were restored because the task has no UI changes.

An optional, manual-only `v6-evaluate.yml` runs offline checks and uploads a
seven-day research artifact. It has read-only repository permissions, an engine-v6
ref guard, no API secrets, no schedule, and no deployment or repository pushes.
