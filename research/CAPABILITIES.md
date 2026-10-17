# Capabilities (verified 2026-10-17, cloud Claude Code session)

| Capability | Status | Notes |
|---|---|---|
| Network egress | Open | Proxy allows all hosts tested (no relay failures). Not a network-policy issue |
| Web search | Works | WebSearch tool, US-only |
| Direct fetch (curl with browser User-Agent) | Works | finviz, tradingview, koyfin, youtube, tiktok, x return 200. Default curl UA gets 403 on some sites |
| investopedia.com | Blocked by site | Cloudflare returns 402 (bot protection, operator People Inc). Use search snippets, Wayback, or a scraping service |
| Reddit HTML | Works with browser UA | `.json` endpoint returns 403; use official OAuth API |
| Instagram | Login wall | Profile URL redirects to login. Needs official API (own account only) or a scraping service |
| TikTok / X | 200 but unverified content | Pages are JS-rendered; likely need a headless browser (Playwright/Chromium is installed) or an API |
| WebFetch tool | Partial | Refused investopedia.com |
| Commit to GitHub | Works | Push access to this repo |
| Nightly runs | **Not active yet** | Needs workflow + `ANTHROPIC_API_KEY` secret (below) |

## To enable nightly research
1. Repo → Settings → Secrets and variables → Actions → add `ANTHROPIC_API_KEY`.
2. Install the Claude GitHub app on the repo (https://github.com/apps/claude).
3. Merge the workflow; run it once via "Run workflow" to confirm.
