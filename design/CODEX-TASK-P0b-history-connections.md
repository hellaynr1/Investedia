# Codex task P0b: connection lines for historical days (7D, 30D, replay)

Read `AGENTS.md` and `design/CODEX-ACCEPTANCE-PROTOCOL.md` first. Branch `codex/p0b-history-connections` from `main`.
Open a pull request. **Do not merge.**

## Problem (owner, 6 Nov 2026)
Going back to 7D or 30D shows history dots but almost no connection lines. Lines exist only for the last 48 hours.

## Starting point (already on branch `preview/history-connections`, not verified in a browser)
- `tools/globe-news/connections.py` has a `CONN_HISTORY=1` mode. It runs the same rules as the live connections on every
  article in `assets/globe/library/` and writes one file per day to `assets/globe/connections-history/YYYY-MM-DD.json`.
  Measured: 21 day files, 1,347 connections, about 1 MB. The live output is unchanged (148 connections).
- `tools/globe-news/page.html`: `loadHistory()` fetches `connections-history/<day>.json` for the days it loads and merges them
  into `CONN_HIST`; `updateNetwork()` draws them alongside `CONN`. Known risk: a duplicate `const days` was just renamed to
  `histDays`. Check that the page loads with no errors.
- Copy the files to `docs/assets/globe/connections-history/` as well (the build does not do this yet).

Start from the branch if it helps, but verify everything. Do not trust the measurements above without rerunning them.

## Rules (must stay the same)
Only evidence-backed relations (impacts the article itself states), no sector lines, no lines under 100 km, confidence and tier
as in `connections.py`, no browser-side inference, no changes to frozen predictions, Track Record or the news robot.

## What to build
1. Confirm the generator output and commit the per-day files (both copies).
2. On 7D and 30D, historical lines appear, each with the same card content as live lines (relationship, tier, confidence, explanation).
3. Lines only join dots that are on screen (same clustering as today), and a line never points at an article that is not loaded.
4. Changing the window back to 24H/48H hides history lines again. Live lines are unchanged.
5. Replay (Play) shows history lines as the replay passes each day, or it is documented why not.

## Acceptance criteria
1. Generator reproduces the committed files byte for byte when rerun (state the command).
2. Live `connections.json` is unchanged (148 connections) and `build.py` output is clean.
3. 30D: history connections drawn > 0 and equal to the sum of the connections of the loaded days that have an article on screen (report both numbers).
4. 48H and 24H line counts identical to `main`.
5. No page errors on PC (1440 px) or phone (390 px), checked with a browser run; attach the console log.
6. Phone median frame time on 30D within 15% of 48H (same method as P0).
7. Every drawn history line has a source event id that exists in its day file.

## PR must include
Counts for each criterion, the browser console logs, before/after screenshots (labelled "Now" / "New", PC and phone) for 48H and 30D,
and the list of files changed.
