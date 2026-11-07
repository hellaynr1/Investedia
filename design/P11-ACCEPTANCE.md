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
