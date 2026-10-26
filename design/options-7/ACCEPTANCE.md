# Globe ideas 1.A, 2.A, 3.A: acceptance (2026-10-26)

Chosen by the owner: **1.A Topic lenses**, **2.A Country briefing (hover card)**, **3.A Markets open (night shade)**.
Reference images: `lens-A.png`, `brief-A.png`, `night-A.png`, `phones-lenses.png`, `phones-country-briefing.png`, `phones-markets-open.png`.
Built screenshots and side-by-sides (mockup left, built right): `built/compare-*.png`.
Tests: `tests/globe-ideas.spec.mjs` (1440 and 390 px), results in `tests/globe-ideas-results.json`.

## Data map (every number on screen and where it comes from)

| On screen | Source |
|---|---|
| Lens chip counts, lens header "N articles · M countries", lens list | `assets/globe/news-live.json`: a story is in a lens when the lens words appear in its own headline or summary (`LENSES` in `tools/globe-news/page.html`). Counts use the current time window and region. |
| % pill next to a lens article | `assets/globe/markets.json` `d` of the first asset named in that story's `impacts` that has a price. No pill when none is priced. |
| Briefing: flag, name, article count, 3 headlines | `news-live.json` stories of that country that match the current filters; duplicate headlines are shown once. |
| Briefing: main index move | `markets.json`, first `g:"Index"` asset of that country flagged `m` (S&P 500 for the US). Row left out when the country has none. |
| Briefing: "Next: … in …" | `assets/calendar-live.json`, earliest future event of that country with impact 3 (high). Row left out when none. |
| Markets now list and globe dots | Regular trading hours per exchange and time zone (`EXCH`), computed in the browser from the real clock. Public holidays are not included (said on the panel). |
| Night shade | Sun position from the real UTC time and date (`sunPoint`, `nightPath`); not a picture. |
| Click on an exchange | Opens the asset viewer for its main index (`^AXJO`, `^N225`, `^HSI`, `^FTSE`, `^GSPC`). |

## Criteria and tests

| # | Criterion | Test |
|---|---|---|
| L1 | Bar is All, Energy, Central banks, Trade & tariffs, Earnings, each with its article count | globe-ideas L1 (counts recomputed from the data file) |
| L2 | Choosing a lens marks the chip, shows "<Lens> lens", the same count as the chip, only that lens's stories | L2 |
| L3 | Each row shows the real % move of the named asset, or nothing | L3 (checked against `markets.json`) |
| L4 | Lens stories are pins; every other story in the window stays as a dimmed dot | L4 |
| L5 | All restores the normal panel; `?lens=energy` opens with the lens set | L5 |
| L6 | Crypto label still exists (`CAT.crypto`), fixing the bug from the earlier chip removal | L6 |
| B1 | Briefing has flag, name, count, up to 3 headlines, index move, next high-impact release | B1 |
| B2 | Missing index or release leaves the row out; never "undefined" or "NaN" | B2 |
| B3 | Hover (PC) or tap (phone) shows the card; click or tap on it opens the full country panel | B3 |
| M1 | Open and closed follow each exchange's hours and time zone | M1 (25 Oct 2026 23:22 UTC) |
| M2 | Weekends are closed | M2 |
| M3 | Sun position is right (noon UTC at about 0°, declination about −12° on 25 Oct) | M3 |
| M4 | Night side is darker than the day side on the canvas | M4 (same land, only the sun moves) |
| M5 | Markets tab lists the five exchanges with the mockup wording and index links | M5 |
| M6 | Clicking a row or a dot on the globe asks the asset viewer for that index | M6 |
| X1 | No script errors, no horizontal overflow, no "undefined"/"NaN" | X1 |

## Built vs mockup (differences you should know about)

| Item | Mockup | Built | Why |
|---|---|---|---|
| Lens counts | 21 / 12 / 13 / 17 | 18 / 15 / 9 / 10 (24H window; changes with window and region) | Mockup numbers were illustrative; built numbers are real. |
| "All" count | 160 (all stories) | Stories in the current window | Matches the number of pins and the "articles" counter. |
| Old category chips (Markets, Companies, Economy, Technology, Commodities, Geopolitics) | not shown | removed, as the mockup replaces the category bar | Say if you want any of them back as extra lenses. |
| Markets-now list | replaces the panel | fifth panel tab "Markets" beside Top, Movers, Latest, Countries | Keeps the news panel one tap away. |
| London opening | "Opens in 7 h 38 min" | "8 h 38 min" | UK clocks went back on 25 Oct 2026, so London opens at 08:00 UTC. New York is still on summer time until 1 Nov. |
| Night shade | drawn as an illustration with the dark side on the left | real sun position, moves with the clock and the slow rotation | Honest data; at some hours most of the visible side is night. |
| Briefing card (PC) | hover card, 340 px | same | – |
| Briefing card (phone) | bottom card with 2 headlines | bottom card with up to 3 headlines, tap opens the full country | – |
| Lens panel (phone) | bottom sheet with first article | same; scrolls through up to 20 | – |
| Chip counts on phone | row of chips | same row, scrolls sideways | – |

Not part of this build (listed for the next round): guided tour, cause-and-effect chains, event pins, My-watchlist toggle, net-impact tint, list view, session clock.
