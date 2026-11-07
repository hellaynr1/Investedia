# Keep the repo private for ~€5–10/month: site on Cloudflare Pages, robots on a small server

## Why
The repo is private, so GitHub Actions minutes are billed. The robots use ~3,500 min/day (~100,000/month,
measured 2026-11-06); GitHub Pro includes 3,000/month, so ~$800/month extra. They currently fail on billing.

## Target
| Piece | Where | Cost (est.) |
|---|---|---|
| Code | GitHub, private (Free plan) | €0 |
| Website (`docs/`) | Cloudflare Pages, deployed from the private repo on every push to `main` | €0 |
| Robots: broad news, priority news, engine V5, prices/market, registry, calendar, economy | Small Linux server (e.g. Hetzner CX22), cron | ~€4–6/month |
| Cloudflare Worker `investedia-live` | unchanged | €0 |
| Claude PR reviews (optional) | GitHub Actions, ~1 min per PR (fits the free 2,000 min) | €0 + API ($5 cap) |

## Steps
1. **Owner:** Cloudflare → Workers & Pages → Create → Pages → connect GitHub → `hellaynr1/Investedia`;
   build command: none; output directory: `docs`; production branch: `main`.
2. Check the `*.pages.dev` preview: every page, globe, news, prices (screenshots PC + phone).
3. **Owner:** create the server (Ubuntu, smallest size, EU), add an SSH key; send me nothing secret.
4. Server setup script (run once): Python 3, git, a deploy key with **write** access to the repo only,
   environment file `/etc/investedia.env` holding `GEMINI_API_KEY`, `PIXABAY_KEY`, Worker ingest tokens
   (owner types them in on the server; never in chat or code).
5. `robots.sh` per job = the same commands as the workflow files (pull --rebase, run script, commit, push), with a lock
   file so runs never overlap. Cron: priority every 10 min, broad every 30 min, engine V5 every 15 min, registry hourly,
   market/prices as now, calendar/economy daily/weekly.
6. Run server robots and GitHub workflows side by side for 1 day **without** pushing from the server (dry run, logs only).
7. Switch: server pushes; GitHub workflows disabled (files kept, `on: workflow_dispatch` only, as fallback).
8. **Owner:** Cloudflare Pages → Custom domains → `investedia.com`; DNS at Spaceship → point to Pages (CNAME). Turn
   GitHub Pages off only after the domain works on Cloudflare.
9. Monitor 48 h: news freshness, V5 calls, error logs, server CPU/disk; report.

## Rollback
Re-enable the GitHub workflows (or make the repo public) and point DNS back to GitHub Pages. Nothing is deleted.

## Not changed
News rules, Track Record, frozen calls, V5 logic, the Worker, site design.

## Time
About 1 day of work plus the 1-day side-by-side run. Owner actions: steps 1, 3, 4 (keys), 8.
