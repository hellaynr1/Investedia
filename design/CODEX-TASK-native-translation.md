# Native Investedia translation

Requested design: the owner's screenshot shows Google's banner and widget. Replace those with Investedia's existing dark footer language selector; no external widget, toolbar or branding. Native screenshots are captured at 1440px and 390px. No new visual mockup was selected.

## Acceptance criteria and data map

A1. The footer's existing seven-language selector switches visible text using `/assets/locales/<language>.json`; `html.lang` matches. There are no Google translator scripts, iframes, toolbar or redirects. `assets/locale.js` consumes the pack's `strings` object keyed by normalized original English text.

A2. Dynamically inserted articles use their cached translations; buttons retain handlers; input values, prices, code and the Investedia wordmark remain unchanged. Sources: rendered public site text plus the saved public article files under `assets/globe/`.

A3. `inv-lang` remembers the requested language for 12 months; loading a second page and same-origin globe frames preserves the language. English reverses translated text without navigating or losing page state.

A4. Repeated switches and live text updates preserve the original English source; native layout must fit desktop and phone. Homepage `fitTitle` runs after the language changes.

A5. All six non-English packs cover the published source catalogue. `tools/check-locales.py` flags missing strings, altered numbers and storage identifiers. Gemini runs only in the existing secured GitHub Actions environment; visitors load first-party cached data and no translation credentials.

A6. A missing/broken pack preserves the current language and page and provides a retry message. Unknown new text remains the original English until generated, rather than showing a fabricated translation.

One assertion group per criterion: `tests/native-translation.spec.mjs`. Unit-level dynamic DOM checks: `tests/native-locale-engine.spec.mjs`. Real pack generation: `.github/workflows/native-locales.yml`; it runs incrementally after successful news workflows once merged. UI changes should refresh the catalogue with `tools/collect-locale-text.mjs`.

## Not done / verification

Generation and validation of all six actual packs is required before this replacement is ready to merge. Old Google widget tests are superseded by the native suites. No changes from this branch are deployed to the public site yet.
