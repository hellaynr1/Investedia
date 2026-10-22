# Prelaunch checks

Run from the repository root. Python: `python3 -m unittest discover -s tests -p 'test_*.py'`.
Normal build: `python3 tools/globe-news/build.py && python3 build.py`.
Release gate: `python3 build.py --release` (expected to fail while owner facts remain null).

Use an installed Playwright package as a development tool (`PLAYWRIGHT_MODULE` can point to it). Linux browser images can use `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`. This Mac uses installed Google Chrome; `PLAYWRIGHT_CHROMIUM_EXECUTABLE` overrides it. `tests/browser-support.mjs` resolves these settings. Pinned axe-core is vendored under tests/vendor; nothing is added to production runtime.

Serve `docs/` with `python3 -m http.server 8769 --bind 127.0.0.1 --directory docs`, then run:

```sh
TEST_BASE_URL=http://127.0.0.1:8769 node tests/consent.spec.mjs
TEST_BASE_URL=http://127.0.0.1:8769 node tests/consent-media.spec.mjs
TEST_BASE_URL=http://127.0.0.1:8769 node tests/alert-consent.spec.mjs
TEST_BASE_URL=http://127.0.0.1:8769 node tests/a11y.spec.mjs
TEST_BASE_URL=http://127.0.0.1:8769 node tests/keyboard.spec.mjs
TEST_BASE_URL=http://127.0.0.1:8769 node tests/redirects.spec.mjs
TEST_BASE_URL=http://127.0.0.1:8769 node tests/screenshots.spec.mjs
python3 tests/contrast-check.py
```

Network fixtures record optional requests then substitute deterministic font/logo/rate/event responses. They prevent test analytics from being submitted and isolate provider outages; they do not prove provider uptime or validate provider accounts. Real saved article/data files are used. Authenticated account actions, genuine outgoing email, live infrastructure/region/RLS/retention settings and manual assistive-technology testing require the owner/provider review described in the release checklist. Service workers are blocked in functional suites to isolate the currently built code; their source cache policy and CORE inventory are reviewed separately. A deployed worker upgrade still needs an installation/update smoke test.
