# Actual v6 validation run

Cutoff: 2026-11-03T18:33:37Z. Status: **BLOCKED — not a completed backtest**.

| Check | Actual result |
|---|---|
| SEC download | 1 attempted; 403 proxy error; 0 new exhibit entries |
| Frozen dataset | 0 rows |
| TRAIN judged | 0 |
| 2024 VALIDATION judged | 0 |
| Model fit | BLOCKED: insufficient cohort |
| Historical OOS | LOCKED |
| Holdout success rate | Unavailable, 0 judged holdout calls |
| Python tests | 159/160 pass; unchanged mailto footer test fails |
| Claude spending this run | $0 |
| Deployment / live changes | None |

No outcome performance claim is supported. The downloader, evaluator, training
cohort guard and test suite were actually executed; a synthetic test fixture is
not counted as a historical call. The environment still omits www.sec.gov from
its enforced allowlist. That runtime access must be fixed before exhibit data
can populate the research dataset. No approval was bypassed.
