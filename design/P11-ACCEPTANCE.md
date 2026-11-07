# P11 acceptance and data map

Spec: CODEX-TASK-P11-ui-polish.md. Final phone navigation section wins. Handoff decisions: HANDOFF-2026-11-07.md.

1. A1: desktop switch height 34px, 12px/600 text, 2px padding beside CTA; no phone switch or explanatory caption. Test: slim desktop switch / no caption / no phone switch.
2. A2: Momentum chips use 8px gap and 7px 13px padding. Test: momentum gap at each width.
3. A3: panels use grey translucent surface rgba(18,18,22,.62), blur 26px. Committed axe colour-contrast assertions: News/dock, Countries and Markets at both widths have zero violations. This is a contrast scan, not a full accessibility audit.
4. A4: close, Escape, drag and empty-globe dismissal; reopening preserves selected country/tab. Country clicks must still open country panels. Test: desktop country click while panel open, close, Escape, upward/downward handle, preserved News/market tabs, no closed-market lines, restored minimized headline.
5. A5: phone first tab tap selects globe mode, repeat tap opens/closes sheet, handle opens sheet; Globe restores the headline card. Tests: first/second News tap, Markets mode/sheet, handle, Globe.
6. A6: Markets sheet content Overview/Indices/FX/Commodities and exact NAV-mkt match: NOT DONE here, queued P10.

Data map: article counts/headlines/source/country come from news-live.json, news-48h.json and loaded events day files via shown/normalize; company identity is data/registry.json; exchange labels are data/exchanges.json; prices are assets/globe/markets.json; macro is economy.json; links are market-links.json. This UI task adds no numerical data. Missing source values retain existing missing-data text.

Screenshots live under tests/screens/p11-ui (four PNG evidence files, no design/evidence folder). Built/mockup URLs and measured results are in the PR.

## Review validation additions
A2 tests every `.chips`, `.regions`, `.panel-tabs`, `.gm-tabs`, `.gm-regions` and `.market-tabs` row at both widths. Time-window button groups are not chip rows.
A3 tests the exact panel background and blur for News, Countries and Markets; list-card background/radius and axe contrast at 390/1440px are executable in the committed test.
A4 tests actual downward pointer movement to minimise the headline and tapping to restore, plus country and article close controls at both widths.
A5 phone dock/handle gestures are N/A at 1440px because desktop uses the switch and close/Escape controls instead. Those desktop controls are tested at 1440px. A6 remains NOT DONE until P10.
Mockups are attached under tests/mockups/p11-ui; screenshots under tests/screens/p11-ui. No remote task branch is needed to view the comparisons.

## Overlay scope and exceptions
- Implemented/tested: News/Countries/article/country sheets and market panel close buttons; phone sheet drag; peek downward minimise + restore; desktop country click while panel is open.
- Transient map hover/hotspot detail has a dynamically added “Close map detail” button. Layers has a close button. Filter sheet has its existing close button. These additional controls are implemented but not all are in the interaction matrix: full dismissal coverage is NOT DONE and belongs in P9's overlay audit.
- Search results and Region/Watchlist dropdowns currently dismiss by their toggle, outside click and Escape, rather than a separate ✕: exceptions to “every popover” remain NOT DONE. Peek has swipe-down minimisation and tap restoration; it does not have a separate ✕. The future P10 carousel is not claimed complete here.
- Controls and hairline colour assertions are now executable. The old `.panel` background has `!important`, and the later P11 override also has `!important` with rgba(18,18,22,.62), so computed colour tests at both widths confirm it wins. There is one #panel instance; every view reuses it.
- Every test now passes its A1–A5 criterion explicitly to check(); no fallback regex maps assertions.
- P4's phone regression path now uses the full globe's dock, checking first tap selects Markets and second tap opens the sheet; desktop retains homepage embedded-mode coverage.

Fourth review: opening a sheet from Globe activates News in go(); a real phone country tap checks active dock, visible handle and dismissal. Escape yields to active InvPeek, Layers, search and dropdown handlers before dismissing the underlying panel. Desktop country/article/Layers/search Escape checks pass. Country brief popovers stack above the peek so their tap remains reachable. Final focused suite: 57 assertions passed.
