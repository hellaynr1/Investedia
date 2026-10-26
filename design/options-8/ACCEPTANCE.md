# Phone globe, option A "Dock + peek card" (2026-10-26)

Chosen by the owner: **A**. Reference: `opt-A.png`. Built screens: `built/A-*.png`. Tests: `tests/globe-phone.spec.mjs` (390 px, plus one desktop check), results in `tests/globe-phone-results.json`.

## What changed (phone only, 760 px and narrower; desktop unchanged)
- Top bar: logo, Privacy, Search button, Filters button (badge shows how many filters are on). The topic chips, region chips, time bar, search box and the live/demo badge moved into the Filters sheet.
- Filters sheet: Topic (with counts), Region, Time and "Replay 7 days", Reset, Close, and a "Show N articles" button. It is a dialog: focus moves in, Tab stays inside, Escape closes and focus returns to the Filters button.
- Peek card above the dock: the top story of the current filters with its time, source and the real % move of the asset it names. Tapping opens the story.
- Bottom dock: Globe / News / Markets. News opens the story list ("160 articles · 24H · Global", rows with time, source and % pill); Markets opens the exchange list.
- Exchange labels on the globe are hidden on phones except in the Markets view, so they no longer cover pins.
- Zoom buttons are 44 px and sit in the empty bottom-right corner of the globe area; pins and the globe stay clear of the top bar, peek card and zoom buttons.
- Text is at least 14 px in all new phone UI; dim grey raised to #a1a1aa; every control is at least 44 px.

## Criteria and tests
| # | Criterion | Test |
|---|---|---|
| P1 | Top bar has only logo, Search, Filters (and Privacy); chips, regions, time bar, search box, badge are off the globe screen | P1 |
| P2 | All controls on the globe screen at least 44 px | P2 |
| P3 | Text on the globe screen at least 14 px | P3 |
| P4 | Peek card shows the top story with the real asset move and opens the story | P4 (checked against `markets.json`) |
| P5 | Filters is a proper dialog with 44 px controls, focus handling and Escape | P5 |
| P6 | Filters work: badge count, "Show N articles" is the real count, peek follows, Reset undoes | P6 |
| P7 | Dock switches Globe / News / Markets and marks the current one | P7 |
| P8 | News rows show time, source and the real % pill; tabs 44 px; text 14 px | P8 |
| P9 | Globe and pins clear of top bar, peek card and zoom buttons | P9 |
| P10 | No overflow, no script errors | P10 |
| D1 | Desktop unchanged | D1 |
Axe (a11y suite) also passes on the phone globe page, including the target-size rule.

## Built vs mockup
| Item | Mockup A | Built | Why |
|---|---|---|---|
| Top bar | logo, search, Filters | same, plus a small Privacy link | Cookie settings must stay reachable on every page. |
| Filters | not drawn for A (B had it) | sheet with Topic, Region, Time, Reset, "Show N articles" | Needed to hold the moved controls. |
| News tab | list without tabs | same list, with the Top / Movers / Latest / Countries / Markets tabs kept under the header at 44 px | Keeps existing views; say if you want them removed on phone. |
| Live / demo badge | not drawn | in the Filters sheet footer | Still visible to anyone who opens Filters. |
| Globe | no exchange labels | same on phone (labels only in Markets view) | – |
