# Economic calendar: sources and how to add one

`update_calendar.py` builds `assets/calendar-live.json` (mirrored to `docs/assets/`) from these sources, in this order. Each source is isolated: if one fails, the others still run and the previous data stays.

| Source | File | Gives | Key needed |
|---|---|---|---|
| ForexFactory weekly feed | `update_calendar.py` | this and next week, all regions, forecast and actual | no (terms unclear for commercial use) |
| BLS, BEA, Federal Reserve | `calendar_official.py` | US release dates and times months ahead (CPI, jobs, GDP, PCE, FOMC) | no (public domain) |
| FRED (St. Louis Fed) | `calendar_fred.py` | Actual and Previous after BLS/BEA releases; date-only US releases | `FRED_API_KEY` (optional) |
| Nasdaq | `update_calendar.py` | earnings | no |

## FRED key (optional)
1. Request a free key: https://fredaccount.stlouisfed.org/apikeys (docs: https://fred.stlouisfed.org/docs/api/api_key.html).
2. Add it as a repository secret named `FRED_API_KEY`: https://github.com/hellaynr1/Investedia/settings/secrets/actions/new
3. Both workflows that run `update_calendar.py` pass it in (`update-calendar.yml`, `broad-news.yml`). Without the secret the module does nothing.
4. Never paste the key into a chat, a file or a commit. The module reads it from the environment and strips it from every error message.
5. First run: Actions, "Refresh economic releases", Run workflow. Check the log for the line `FRED: n releases added, n actuals filled`.

## Add a source module (checklist)
1. **One file per source**, e.g. `calendar_<name>.py`, with a module docstring that says what it gives, its terms, and whether it needs a key.
2. **Return plain events** in the existing shape: `t` title, `c` currency, `at` ISO UTC time, `imp` 1-3, `type: 'economic'`, `country`, `actual`, `fc`, `prev`, plus `src` (source name). Date-only rows use `dateOnly: True`, `when: 'Time not published'` and `at` at 12:00 UTC.
3. **Never invent values.** Leave `actual`, `fc` and `prev` empty when the source has none.
4. **Isolate failures.** Raise a small error with a status code only (no URLs, no keys) and catch it per call. A failing source must not stop the others.
5. **Avoid duplicates.** Skip a release when another source already lists it on the same day (see `covered()` in `calendar_fred.py` and the `ff` keys in `calendar_official.py`).
6. **Hook it up** in `update_calendar.py` next to the other sources; add its secret (if any) to the `env:` of the workflows that run the script.
7. **Test it** in `tests/test_<name>.py` with fake responses: no key means no calls; parses a sample payload; respects the dedupe; one failing call does not block others; errors never contain a key. Run `python3 -m unittest discover -s tests -p "test_*.py"`.
8. **Run it once for real** (manual workflow run on a branch) and compare a few values with the source's own website before merging.
9. **Say what is not covered** in the PR description.
