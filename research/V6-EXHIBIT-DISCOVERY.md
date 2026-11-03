# Exhibit 99 discovery repair

2026-11-03, engine-v6 only. Informational research; not investment advice.

The original EFTS index contains primary 8-K documents but no Exhibit 99 entries.
The old extractor therefore has no eligible filings. This change adds an
independent cached filing-index lookup instead of rewriting the original index.

## Acceptance criteria / data map

1. Verified attachment types and filenames come from the SEC accession's document
   table, never guesses from an exhibit number. `tools/v6/exhibits.py:parse_index`
   requires the expected accession, an 8-K primary row and acceptance timestamp.
2. `research/v6/exhibits/YYYY-MM.jsonl` stores acceptance times, exhibit docs,
   source URL, SHA256 and retrieval time. Compressed index HTML is retained in
   `exhibits/source/`. `filings()` merges these with the untouched raw index.
3. Completed filings (including a verified absence of Exhibit 99) are not fetched
   twice. Access-denied/invalid pages remain retryable failures, not empty results.
   A denial/rate limit stops a run; all requests are limited to two per second.
4. Legacy acceptance timestamps are reused with source-row hashes. Truncated text
   and missing filenames are never promoted to verified attachments/full releases.
5. Claude candidates read the merged index, choose a readable Exhibit 99, and
   prefer press releases over presentations. One filing is emitted once.
6. Discovery makes zero model API requests. `claude_extract.py --fetch-only`
   caches SEC text without importing Anthropic, collecting batches, or submitting
   requests. Existing paid extraction is not executed during this task.
7. Evaluation inventory includes discovered exhibits and recovered timestamps.

Tests: `tests/test_v6_exhibits.py`, plus existing Track D suite. No website design
changes; mockups and screenshots are inapplicable.

## Commands

```
python3 -m tools.v6.exhibits --import-legacy --minutes 10 --max-filings 500
python3 tools/v6/claude_extract.py --fetch-only
```

Discovery prioritizes historical earnings filings, then other relevant items,
within 2022-01-01–2026-10-20. `--from` / `--to` permit bounded chronological runs.
The default text-fetch limit remains V6_FETCH_MAX (6000); discovery does not fetch
release bodies. PDF exhibits remain indexed but are not fed to the HTML/text
extractor. SEC acceptance is not automatically the earliest company-public time.
The existing extractor still uses a single selected exhibit per filing; ambiguous
or multi-release filings need further research review before model evaluation.

Optional manual workflow `v6-exhibits.yml` runs discovery for up to 35 minutes
and uploads a seven-day artifact. It has no API secrets, schedules, repository
write permissions, paid infrastructure, or deployment step. It does not merge
artifact data back into the branch automatically. Neither workflow nor branch
push has been executed during this task.

## Actual local result / not done

- Reused 22,198 SEC acceptance timestamps from the existing archive, normalized
  from SEC Eastern time to UTC and linked to source-row hashes.
- Found 9,110 existing truncated exhibit excerpts among those matched filings;
  these are counted as excerpts only, not verified exhibit entries.
- New verified Exhibit 99 entries downloaded: **0**.
- SEC HTTPS request returned a proxy CONNECT 403 because www.sec.gov is outside
  the environment's allowed hosts. No alternate route or access bypass was used.
- To populate entries here, www.sec.gov must be added to this cloud environment's
  allowed network hosts. Then the discovery command resumes from the cache.
- No Anthropic calls, API credit use, live-site changes, deployment or merge.

Verification: all 8 new discovery tests and all 25 existing Track D tests pass.
Full Python suite: 157/158 pass; the only failure remains the unchanged
`test_footer_links_and_signup_destinations` mailto-path assertion. Site build
passes; its 92 generated file changes were restored so no website files changed.

## Update: GitHub research runner succeeded

Local SEC requests remain policy-blocked, but the repository's GitHub Actions
research runner successfully collected and verified the first 20 indexes / 20
Exhibit 99 documents in 17 filings. See V6-GITHUB-DISCOVERY.md and
V6-EXHIBIT-RESULTS.md for run links and real examples. The current workflow can
persist cache data only to engine-v6 and cache text in explicit --fetch-only mode.
This supersedes the initial manual-only/read-only workflow description above.
