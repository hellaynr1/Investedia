# Acceptance record: indices region switch and commodities (owner picks, 2026-10-25)

Picks: indices C (region button) on wide screens + A (tabs) on phones; commodities C (scoreboard) on wide screens + A (grouped list with chips) on phones.
Mockups: `design/options-5/*.png`. Built-vs-mockup: `design/options-5/built-vs-mockup-*.png`. Tests: `tests/indices-commodities.spec.mjs` (19 checks at 1440 and 390 px).

| ID | Criterion | Status |
|---|---|---|
| I1 | Only the chosen region's table is shown, not every continent stacked | done |
| I2 | Wide: "Region: Europe ▾" button, ‹ › arrows, "n indices · average x%" | done |
| I3 | Wide: menu lists each region with its average move and "All regions"; Escape closes | done |
| I4 | Wide: choosing a region or stepping with ‹ › changes the table and wraps; All shows all regions | done |
| I2p/I3p | Phone: tabs Americas, Europe, Asia, All (44 px targets); no wide button | done |
| I5 | `?region=Asia` opens that region | done |
| C1 | Wide: three group cards (Energy, Metals, Agriculture) with the group's average move | done |
| C2 | Wide: each card highlights the real biggest mover (checked against markets.json) | done |
| C3 | Wide: other markets as small rows with sparkline and %; clicking a row opens the asset pop-up | done |
| C1p-C3p | Phone: chips All, Energy, Metals, Agri; list rows with price, sparkline, % pill | done |
| X1 | No horizontal overflow | done |

## Not done / differs from the mockup
- The default region is Americas (the mockups showed Europe selected).
- The region menu shows each region's average for the selected window (Today, Week or Month), not only today.
- The scoreboard has no "Week/Month heat" colouring; the sparkline colour follows the selected window.
- Palladium and aluminium are not in the commodity list (they were not on the old page either).
- Also fixed on the way: faint table header text and a red pill in the menu failed WCAG AA contrast; both lightened.
