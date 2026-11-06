# Codex task P0c: readable numbers on the globe (layout options first, owner picks)

Read `AGENTS.md`, `design/CODEX-ACCEPTANCE-PROTOCOL.md` and `design/CODEX-TASK-P0b-history-connections.md`. Branch
`codex/p0c-cluster-labels` from `main` (after P0b is merged, or from its branch if P0b is not merged yet and the owner agrees).
Open a pull request. **Do not merge.**

## Problem (owner, 6 Nov 2026)
On 7D and 30D there are too many count badges. The globe looks messy. The owner asked for a better system for showing numbers.

## Step 1: layout examples only (no change to the live page)
Build three options on a preview page, not in the live Globe. Each option is shown on the real globe with 30D data, on PC (1440 px)
and phone (390 px). Label each image on the image itself with "A · <name>", "B · <name>", "C · <name>", and the same labels in the PR.
Make each one visibly different. Suggested directions (use these or better, state which):
- **A · Zoom levels:** country totals when zoomed out, place counts only when zoomed in.
- **B · Top markers only:** only the top N markers get a number, the rest are plain dots, with a "+N more" line.
- **C · Count in the card:** dots have no number; tapping or hovering shows the count in the card.
Also state the rule used for "top N" and for zoom levels.

## Step 2: wait for the owner to pick one (do not implement the others)

## Step 3 (after the owner picks): implement the chosen option on the Globe page only
Use the existing clustering (`buildSites`, `drawn`). Do not change coordinates, colours, animations, the homepage or the timeline logic.

## Acceptance criteria
1. Three labelled options, PC and phone, each visibly different at normal size (PR table).
2. Each option states its rule in numbers (e.g. the N, the zoom thresholds).
3. Step 3 only after the owner's choice is written in the PR.
4. After Step 3: no number text overlaps another number text on a 390 px screen in the 30D view (measured by bounding boxes, state
   the count of overlaps before and after).
5. Phone median frame time on 30D within 15% of 48H.
6. No page errors on PC or phone; build clean; tests that pass on `main` still pass.

## PR must include
The labelled options, the overlap counts, the rule for each option, and files changed.
