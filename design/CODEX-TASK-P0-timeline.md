# Codex task P0: make the Globe timeline show real history (7D, 30D, Play)

Read `AGENTS.md` and `design/CODEX-ACCEPTANCE-PROTOCOL.md` first. Work on a new branch `codex/p0-timeline`, open a pull request,
**do not merge**. Owner review happens on the PR.

## Problem (measured on investedia.com, 6 Nov 2026)
On the Globe page (`assets/globe/news.html`, source `tools/globe-news/page.html`) the time buttons 24H / 48H / 7D / 30D and the
Play button (7-day replay) all show the same ~600 articles, because the page only loads `news-live.json` (newest 360) and
`news-48h.json` (the rest of the last 48 hours). Older articles exist but are never loaded:
- `assets/globe/events/YYYY-MM-DD.json`: one file per day since 2026-10-15, about 6,600 events. Fields per event:
  `id, at, title, src, url, n_src, cluster, cat, fam, imp, mm, loc{place,country,lat,lon,region}, cos, assets`.

## What to build
1. When the user selects **7D** or **30D**, or presses **Play**, load the needed day files from `assets/globe/events/` (only the
   days in the window, loaded in parallel, cached in memory) and add them to the globe as articles.
   - Map each event to the page's article shape used by `normalize()` (headline = `title`, source name = `src`, link = `url`,
     published time = `at`, importance = `imp`, category = `cat`, location = `loc`, market moving = `mm`).
   - Skip any event whose `id` is already loaded (live / 48 h data wins).
   - Missing day files (404) are skipped silently.
2. A historical event opens like any article: headline, source, time and the **original source link**. Events have no AI summary;
   show the existing "no summary" state, never invent one.
3. Markers: keep the place-grouping (`buildSites`) so rendering cost depends on places, not articles.
4. Lines for older days: events carry `assets` (registry ids). Do **not** compute new connections in the browser. Only show lines
   for articles that have entries in `assets/globe/connections.json`. Older days simply show dots. (A later task will add
   per-day connection files.)
5. The article count in the time bar must show the real number in the window (e.g. "3,412 articles · 7D").
6. 24H and 48H must behave exactly as today (no day files loaded for them).
7. The homepage globe (`?embed=1`) must not load day files at all.

## Do not change
Frozen predictions, `v5-*`, `news-track.json`, Track Record files, the news robot, event files themselves, homepage layout,
globe position/size/animations, connection logic, colours. No new dependencies. No secrets.

## Acceptance criteria (one test or measured check each)
1. Globe page, 7D: article count > 2,000 and the oldest article is 6–7 days old (Playwright check on a local server).
2. Globe page, 30D: oldest article is from 2026-10-15 (first day file) and count > 5,000.
3. 24H and 48H counts are identical to `main` (same data, same numbers).
4. Play replays 7 days: the replay's earliest frame shows articles older than 48 h.
5. Homepage globe (`?embed=1`): no request to `/events/` (check network log).
6. No duplicate articles: ids unique after merging.
7. Opening a historical article shows its headline, source and working original link, and no invented summary.
8. Phone (iPhone 13 emulation, 4x CPU slowdown): median frame time on 30D no more than 15% worse than on 48H.
9. No console errors on PC (1440 px) and phone (390 px).
10. `python3 tools/globe-news/build.py && python3 build.py` run clean; all tests in `tests/` that pass on `main` still pass.

## PR must include
Screenshots (labelled "Now" / "New", PC and phone) of 48H vs 7D vs 30D, the measured numbers for every criterion above, and the
list of files changed.
