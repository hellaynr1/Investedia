# Verified Exhibit 99 sample — actual results

SEC discovery run: https://github.com/hellaynr1/Investedia/actions/runs/41696800244
Verified cache import: https://github.com/hellaynr1/Investedia/actions/runs/41697937604

20 filing indexes checked; 20 Exhibit 99 documents in 17 filings; 0 errors; $0 model API spend.
17 readable filing candidates. Source HTML, hashes and acceptance timestamps retained.
All 20 source hashes and parsed metadata were independently verified after pulling the cache locally.

| Asset | Filing date | Exhibit | Verified SEC document |
|---|---|---|---|
| TSLA | 2022-01-03 | EX-99.1 | [tsla-ex991_6.htm](https://www.sec.gov/Archives/edgar/data/1318605/000156459022000009/tsla-ex991_6.htm) |
| MRNA | 2022-01-04 | EX-99.1 | [exhibit991lettertosharehol.htm](https://www.sec.gov/Archives/edgar/data/1682852/000168285222000004/exhibit991lettertosharehol.htm) |
| WEX | 2022-01-04 | EX-99.1 | [a52557193ex99_1.htm](https://www.sec.gov/Archives/edgar/data/1309108/000115752322000007/a52557193ex99_1.htm) |
| T | 2022-01-05 | EX-99.1 | [exhibit991pressreleaseofat.htm](https://www.sec.gov/Archives/edgar/data/732717/000073271722000004/exhibit991pressreleaseofat.htm) |

This is a data-collection result, not prediction accuracy. Zero frozen v6 calls have been evaluated.
A second batch is configured for at most 500 new filing indexes / 10 minutes, with free text caching.
Claude extraction requires explicit manual opt-in and is not invoked. Only engine-v6 is updated; no deployment.

## Larger batch actual result

Run 41698672765 completed and saved its data to engine-v6. It attempted 173
filing indexes, verified 170, and found 196 additional Exhibit 99 documents.
It stopped after three discovery errors rather than completing the 500 cap.
The latest error was an attachment URL outside the expected accession path;
failed filings remain retryable and are not marked complete.

Cumulative cache: **190 verified filing indexes, 216 Exhibit 99 documents in
176 filings, 176 readable release text excerpts cached**. Excerpts are limited
to 6,000 characters as configured by Track C, with provenance and SHA256 proof.
All 190 filing-index hashes / parsed metadata and all 176 excerpt hashes were
independently verified locally. There were no model API requests.

Before scaling collection, inspect the rejected attachment-link variants.
The current collector conservatively stops at three errors. Fact extraction,
provenance-complete frozen historical calls, training, calibration/freeze and
OOS validation remain unfinished. No success percentage is supported yet.

## Diagnostic collection, 2026-11-03 19:21 UTC

Run [41701905302](https://github.com/hellaynr1/Investedia/actions/runs/41701905302)
added 262 verified indexes, 343 Exhibit 99 documents and 244 readable excerpts
at $0 model API cost. Cumulative cache: **452 verified indexes, 559 Exhibit 99
documents in 421 filings, and 420 cached excerpts**. One eligible exhibit text
was temporarily unavailable and remains retryable. All 452 accession-page hashes,
acceptance clocks and extracted document lists were independently rechecked.

The three rejected links exposed an official SEC cross-filer pattern: the
attachment is under a different numeric CIK directory but the exact same
accession. The discovery/parser fix requires the SEC host, numeric CIK and exact
accession; the text fetcher uses that attachment CIK. It never follows a different
accession or external host. The three failed filings have not yet been retried
with this fix; no result from that retry is included in these totals.
