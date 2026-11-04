# Footer translation navigation repair

The owner clarified that the language list opens; selecting a language produces an error or blank page. No design mockup was selected. Preserve the existing desktop popover and phone sheet. The earlier unrelated dropdown redesign has been removed from the final branch.

The original selection handler successfully navigates, as reproduced at 1440px and 390px, but constructs `investedia-com.translate.goog` directly. The correction uses Google's standard `https://translate.google.com/translate` entry point with `sl`, `tl`, `hl`, and the complete public original URL in `u`. This is a candidate correction; external translation output has not been verified.

## Acceptance criteria and data map

1. A1: Selecting each of Français, Nederlands, Deutsch, Español, Italiano, and Português navigates to Google's normal translation entry point with the requested language and the original public page, query, and anchor. Language codes: existing `select` option values in `assets/ui.js`. Original: `location.pathname`, `location.search`, and `location.hash`, with origin `https://investedia.com`.
2. A2: On a translated page, `_x_tr_tl` sets the current supported language. Choosing a different language translates the public original, never nests another proxy, and removes `_x_tr_*` parameters from the original URL.
3. A3: Choosing English on a translated copy returns directly to investedia.com, preserving unrelated query parameters and the anchor.
4. A4: Keep the existing seven-language desktop popover and phone sheet. Enter opens them; Escape closes them and restores focus.

`tests/footer-translation.spec.mjs` exercises each criterion at 1440px and 390px, including actual clicks/taps on the existing dropdown options. External navigation is fulfilled by clearly identified test fixtures; these do not translate any text and are not evidence of Google's service working.

## Built review

| Criteria | Result | Built PC | Built phone | Mockup |
|---|---|---|---|---|
| A1–A4 | Passed with navigation fixtures at both widths | `/workspace/.investedia-tools/translation-handoff-screens/translation-1440.png` | `/workspace/.investedia-tools/translation-handoff-screens/translation-390.png` | Not applicable: navigation repair |

## Not done

Live Google Translate output and the owner's external error remain unverified. Both the old proxy destination and the normal translation entry point are denied by the running environment's restricted network policy (CONNECT 403); no response from Google was obtained. Saved environment settings specify unrestricted networking, but the current machine still reports restricted networking. A current runtime with Google Translate access is needed for end-to-end verification. No code has been pushed or published.
