# P0b acceptance and data map

Original task: CODEX-TASK-P0b-history-connections.md. Inputs are read-only library article files, per-day event IDs, markets.json, iso.json and the canonical registry. Historical connections reuse the live `_rules` engine. The mode does not run the live writer or any news robot.

1. A1 deterministic generation: `CONN_HISTORY=1 python3 tools/globe-news/connections.py`. Sorted files/articles/benchmark symbols and stable output ordering, no current-time field. Tests rerun with a different PYTHONHASHSEED and compare all committed bytes.
2. A2 live file integrity: byte comparison before/after generation. Current live connections count is 298, not the old task snapshot's 148. No generated live connection changes are committed.
3. A3 browser history: 30D loads 1,498 raw records; normal source/event filtering and existing geographic duplicate merging produce 294 historical connections in the network. The unchanged display budgets (22 PC/14 phone, per-country limits) render a subset, 17 PC/11 phone in the recorded view. Both snapped endpoints of every rendered historical line are visible; no historical line references an unloaded event. Tests independently derive eligible deduplicated counts from the loaded source records. The raw sum is not claimed to equal the capped display count.
4. A4 live windows: 24H has 96 events, 48H 116, identical to main's renderer served the same real input data. After 7D/30D, returning to either restores those counts with zero historical lines.
5. A5 replay: 7D loads historical connections before playback; network events follow the replay time cursor. PC1440/phone390 no page exceptions; console summary in tests/results/p0b-history.json.
6. A6 performance: run existing tests/p0-timeline-performance.spec.mjs (iPhone13, CPU4, ABBA, 200 measured frames/window); results in tests/results/p0b-performance.json and PR. No frame-scheduler or clustering changes.
7. A7 provenance: every generated connection event id exists in its events/day file, minimum100km, confidence>=.25, sectors rejected. Python test validates all records and both copies.

Screenshots in tests/screens/p0b-history are labelled Now/New + width + window. Main screenshots use baseline HTML c8e3f58a4 with the same real JSON inputs as the candidate, to isolate renderer changes from continuously updating news data. Data map: connection origin/destination/evidence/tier/confidence/explanation are emitted from `_rules`; dates and source ids come from library/event files; baseline and final counts are measured, not invented.

## Not done
The literal raw-file sum = visible-line count reading of A3 is not met: the existing geographic duplicate merge and line-density budgets intentionally reduce the raw records. The PR must report raw, eligible and drawn counts separately; this document does not assert all 1,498 source records are displayed at once. The existing capped design and phone performance gate are retained.

Final refreshed-data validation: 42 browser assertions and the provenance/reproduction test pass. CPU4 benchmark was captured before the routine main-data refresh, as recorded in the performance artifact; +5.6% frame interval / +13.8% draw duration.
