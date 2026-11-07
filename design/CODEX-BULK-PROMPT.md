# Codex bulk prompt (paste once)

Work through the Investedia task queue in bulk, without waiting for me between tasks.

Queue (in order): P4 → P11 → P0b → P10 → P2 → P3 → P5 → P6 → P7 → P8 → P9.
Task files: P4 on branch codex/tasks-p4-markets; P0b on codex/tasks-p0b-p0c (skip P0c); all others on codex/tasks-p2-p3
(CODEX-TASK-P11, P10, P2, P3, and CODEX-TASKS-NEXT.md for P5–P9). Also read design/HANDOFF-2026-11-07.md: its decisions win.

For each task:
1. Branch `codex/<task>` from the latest main. If it needs code from an earlier unmerged task, branch from that task's branch and say so in the PR.
2. Build it, run `python3 tools/globe-news/build.py && python3 build.py` and the tests, open a PR. Do not merge.
3. Immediately start the next task. Do not wait for review or merge.
4. Whenever the review bot comments "CHANGES NEEDED" on any open PR, fix ALL its comments in ONE push, then continue where you were.
5. After a PR is merged, rebase any open branches that were built on it.

Always: never commit keys or secrets; never touch frozen predictions, Track Record, v5 files or news robots; no fake data;
keep "Not investment advice". If a task is blocked (missing key, unclear data), write the blocker in its PR and move on.
