# Footer translation control repair

No new design mockup was selected: this repairs the existing footer language control. Keep the existing globe, language names, dark appearance, and Google Translate destinations.

## Acceptance criteria and data map

1. A1: Clicking/tapping the globe, current language, or arrow opens a visible list of all seven existing languages, within the viewport, at 1440px and 390px. Labels: `assets/ui.js` `languages` mapping (English, Français, Nederlands, Deutsch, Español, Italiano, Português).
2. A2: Enter opens the control; Tab reaches the language links; Escape closes it and returns focus; clicking outside closes it. State: native `details.open`.
3. A3: Language links preserve `location.pathname`, non-translation query parameters, and the anchor. English uses investedia.com; other languages use investedia-com.translate.goog with the existing Google translation parameters.
4. A4: Menu text passes 4.5:1 contrast in both themes; language targets are at least 44px high. Colors: `assets/app.css` theme variables `--fg` and `--bg-2`.
5. A5: A translated page displays its current `_x_tr_tl` language; returning to English removes all `_x_tr_*` parameters. Unsupported language labels fall back to English.

`tests/footer-translation.spec.mjs` contains an assertion group for each criterion and runs both widths. Translation destinations are served local application files during the test; this tests menu behavior and navigation, not Google's translation service.

## Built review

| Criteria | Result | Built PC | Built phone | Mockup |
|---|---|---|---|---|
| A1–A5 | Passed at both widths | `/workspace/.investedia-tools/translation-screens/translation-1440.png` | `/workspace/.investedia-tools/translation-screens/translation-390.png` | Not applicable: bug repair |

Screenshots have visible “New / PC” and “New / Phone” labels. Reviewed both: all seven options are readable and the menu is not clipped by the footer card.

## Not done

Live Google Translate availability is unverified: this environment's network policy blocks the external translation host. Nothing has been pushed or published.
