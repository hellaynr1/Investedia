# Capabilities (verified 2026-10-17, cloud Claude Code session)

| Capability | Status | Notes |
|---|---|---|
| Web search | Works | WebSearch tool, US-only, returns links/snippets |
| Fetch pages | Partial | finviz.com worked; investopedia.com refused; direct `curl` returns 402/403 via proxy |
| Instagram / TikTok / X / YouTube | Not verified | Logged-out pages usually blocked. Needs official APIs (YouTube Data API key is free) or a connected scraper service. Not attempted yet |
| Reddit | Blocked via curl (403) | Try official API with OAuth app credentials |
| Commit to GitHub | Works | Session has push access to this repo |
| Background / nightly runs | **Not active yet** | Needs `.github/workflows/competitor-research.yml` + `ANTHROPIC_API_KEY` repo secret (see below) |
| Claude Code in-session scheduling | Session-only | Dies when session ends; not reliable for nights |

## To enable nightly research
1. Repo → Settings → Secrets and variables → Actions → add `ANTHROPIC_API_KEY`.
2. Install the Claude GitHub app on the repo (https://github.com/apps/claude).
3. Merge the workflow; run it once via "Run workflow" to confirm.
