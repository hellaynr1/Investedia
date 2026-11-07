# Codex task P11: switch, spacing, glass lists, dismissible overlays (owner 2026-11-07)

Applies to P4 and P10 (build into them if not merged yet, otherwise a follow-up PR `codex/p11-ui-polish`). **Do not merge.**
Mockups: `design/markets-globe/D-desktop-slim-switch.png`, `D-phone-slim-switch.png`, `design/phone-tabs/T3-*.png`.

1. **News / Markets switch:** slim segmented control, height 34 px desktop / 32 px phone, text 12 px 600, 2 px inner padding, active
   segment white with black text. Desktop: left of the "Open globe" button, vertically centred with it. Phone: top-left over the globe.
   **No caption/explanation line under the switch** (remove it on both).
2. **Spacing:** Market Momentum tabs (Performers / Attention / Sectors) 8 px gap, 7×13 px padding; apply the same 8 px chip gap
   everywhere chips sit in a row.
3. **Glass, not black:** lists and full-screen sheets on phone (News, Countries, Markets) use a translucent grey surface
   (`rgba(18,18,22,.62)` + `backdrop-filter: blur(26px)`), list groups as rounded 14 px grey cards (`rgba(44,44,50,.55)`) with
   hairline separators (`rgba(255,255,255,.08)`). Segmented controls, search fields and chips: `rgba(60,60,67,.45)`. Text contrast
   must stay WCAG AA (check).
4. **Everything on top of the globe can be moved away:** every panel, sheet, card or popover that covers the globe has a close (✕)
   button; phone sheets also drag down to dismiss (and up to expand), with a handle; the article carousel can be swiped down to
   minimise to a one-line bar; Esc closes on desktop; tapping empty globe space closes the open panel. State is not lost (re-open
   restores the same country / tab).
5. Test: open and dismiss each overlay by ✕, drag, Esc and outside tap on 1440 px and 390 px; screenshot table vs mockups.

## Phone: News/Markets switch under the globe (owner approved)
- On phone the slim switch (176×32 px, glass background) sits centred just under the globe, not pinned at the top.
- It does not always show: hide it while a sheet, article or the Countries list is open; show it again when the globe is visible.
- Tapping a side slides the white pill over to it (0.25 s ease) and switches mode. No caption under it.
- Mockups: design/phone-tabs/SWP-news.png, SWP-markets.png.

## Phone navigation (owner, final; replaces the switch-under-globe and "no double" sections above)
Bottom bar keeps three tabs: Globe · News · Markets. No News/Markets switch on phone.
- **Globe**: the plain globe with the swipeable headline cards (P10). Nothing else.
- **News**: the globe in News mode (news dots, counts, connection lines). Tap News again, or swipe up the handle, and a sheet slides up with the News widget (Top / Latest / Countries). Swipe down or tap the tab again to close it and return to the News globe.
- **Markets**: the same system. First tap = globe in Markets mode (exchanges, trade lines). Second tap or swipe up = Markets sheet (Overview / Indices / FX / Commodities).
- Sheets: glass style, 0.25 s slide, a small grab handle always visible above the bar so people know they can pull it up.
- Mockups: design/phone-tabs/NAV-closed.png, NAV-open.png.
- PC keeps the slim switch beside "Open globe" (placement 3).
