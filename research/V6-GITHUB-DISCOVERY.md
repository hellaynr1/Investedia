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
