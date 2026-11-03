# Research runner plan: SEC discovery without a mobile settings change

Only engine-v6 is pushed. No main update, merge, Pages deployment or Worker deployment.
The task's local environment denies SEC HTTPS. This job uses the repository's
existing GitHub Actions research environment, with its own network access; local
proxy settings and security controls are not modified.

Paid Claude extraction in v6-features.yml now requires an explicit manual
workflow_dispatch with run_claude=true. Its default is false. Pushes and schedules
cannot invoke that paid step. Existing extraction code and budget guard remain.

Upload the research checkpoint with [skip ci], then enable the SEC job's narrowly
scoped push trigger in a separate commit touching only v6-exhibits.yml. The upload
must not automatically start the long historical-index/price jobs. The isolated
sample is bounded to 20 filing indexes and three minutes; it has read-only repo
permissions, no API secrets and a seven-day output artifact. Its Actions summary
shows actual indexes, exhibit entries, errors and zero model API spending.

SEC can also deny GitHub runner IPs. A workflow completion alone is not proof of
successful downloads: inspect the result counters and any error before expanding.
No model performance claim follows from downloaded exhibit entries.

## Executed results

The bootstrap push and bounded research run succeeded. GitHub Actions run
41696800244 downloaded 20 filing indexes and found 20 Exhibit 99 documents,
with zero errors and no model API calls. These belong to 17 filings; three
verified indexes had no Exhibit 99. There are 17 readable filing candidates.

Run 41697937604 reused that artifact, verified every source hash and parsed
metadata record, and committed the cache only to engine-v6. It did not refetch
SEC. All 20 source pages were independently verified again after pulling locally.

The workflow now has narrowly scoped contents:write and actions:read permission
so it can persist research/v6/exhibits and research/v6/text to engine-v6 with a
[skip ci] bot commit. It cannot run on main, uses no model API secrets, and has
no deployment step. Sparse checkout avoids loading the unrelated site/prices.

Run 41698672765 is the next bounded collection: at most 500 fresh indexes / ten
minutes, followed by up to 500 readable text fetches in --fetch-only mode.
Previously completed filings and cached text are reused. Paid extraction remains
manual opt-in only. Model training remains blocked on the unpopulated frozen-call
cohort; data collection is not an accuracy result.

Local checks: 39 v6 tests pass; full Python suite 163/164 pass. The only failure
is the unchanged footer mailto-path assertion. No production merge or deployment.

The larger run completed: 173 attempted / 170 verified indexes / 196 additional
Exhibit 99 documents / three discovery errors. It cached 176 filing excerpts
without Anthropic. Cumulative results and limitations are in V6-EXHIBIT-RESULTS.md.
No collection job is claimed to be still running after this completed batch.
