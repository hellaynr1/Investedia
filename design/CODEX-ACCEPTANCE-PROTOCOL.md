# How every Codex task is written and checked (owner request, 2026-10-25)

Why this exists: batch 2 shipped globe arcs without the % changes that option C showed, and the PR text said "move data depends on available fields". Nobody compared the build with the chosen mockup before it was merged. Not again.

## A task file must contain
1. **Chosen mockup**: the exact image path(s) in `design/options-*/` for PC and phone. The built page must match them, element by element.
2. **Numbered acceptance criteria**, each one visible and testable, with the exact strings and fields. Example: "A1. Hovering a Volkswagen line shows a pill `↓ 0.40%` (today's change from `assets/globe/markets.json` field `d` of the asset whose `s` or `site` equals the impact's `ticker`)."
3. **Data map**: for every number or label on the mockup, the file and field it comes from. If a field does not exist, the task says what to do (usually: add it to the updater script), never "skip".
4. **Stop rule**: if a criterion cannot be met with real data, stop and say so in the PR under "Not done". Never ship a different design and call it done. Never invent numbers.
5. **One Playwright assertion per criterion** in `tests/`, run at 1440 and 390 px.

## The PR must contain
- A table: criterion, status (done / not done), and a screenshot of the built page next to the mockup, both labelled (Mockup / Built, PC / Phone).
- A "Not done" section, even if empty.

## Before Claude tells the owner it is good
Claude opens the PR, puts each built screenshot beside its mockup, ticks every criterion, and reports every gap in plain words. Claude does not say "looks good" from the PR description or from passing tests alone.
