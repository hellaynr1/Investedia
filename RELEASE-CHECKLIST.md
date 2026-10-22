# Prelaunch release checklist — 22 October 2026

**Status: preview prepared; release BLOCKED by 44 unresolved owner/review fields. No merge or publication to main is authorised or performed by this task.** A successful technical build is not legal sign-off. All facts in legal-config.json remain null rather than invented.

## Five-minute review

1. Open [desktop and phone screenshots](tests/screens/index.html), especially first-visit/settings consent cards, News/article photos and the footer.
2. Read [consent matrix](tests/consent-matrix.md), [accessibility report](tests/a11y-report.md) and the remaining verification limits below.
3. Complete [legal-config.json](legal-config.json) using [LEGAL-TODO.md](LEGAL-TODO.md), then send [LEGAL-REVIEW-PACK.md](LEGAL-REVIEW-PACK.md) to Belgian counsel for review. This is public display configuration; never paste private contracts, credentials or keys into it.
4. Re-run the release gate and checks after changes. Approve main publication separately only after the gate passes and the operational/legal questions are resolved.

## Validation evidence

| Check | Result | Evidence |
|---|---|---|
| Normal globe + site build | PASS, 47 source pages (including 8 redirect stubs) | build.py; tools/globe-news/build.py |
| Release build | Expected FAIL: 44 unresolved facts only; no unmapped placeholders | `python3 build.py --release`; list below |
| Python unit tests | PASS: 21 tests | tests/test_legal_pages.py, test_legal_release.py, test_news_impacts.py, test_news_photos.py; local duplicate test copies are excluded from commits |
| Consent | PASS: 41 URLs × 2 widths, first visit, essential, all, withdrawal, expiry/version | tests/consent-matrix.md; tests/consent-results.json |
| Optional logo/font gates | PASS: 5 representative routes × 2 widths, including direct legacy globe | tests/consent-media-results.json |
| Open headline popup | PASS: homepage, News and globe at both widths; consent, keyboard dismissal, no axe violations | tests/alert-consent-results.json |
| Axe-core 4.10.3 | PASS: 40 pages × 2 widths; zero automated WCAG rule violations and runtime errors | tests/a11y-report.md; tests/a11y-results.json |
| Keyboard scenarios | PASS: 7 checks × 2 widths | tests/keyboard-results.json |
| Contrast calculations | PASS for used pairs; white on orange deliberately rejected (2.61:1), dark text on orange 7.23:1 | tests/contrast-results.json |
| Visible viewport phone targets | No remaining measured target below 44×44 in audited initial states | tests/a11y-results.json |
| Reflow sample | No horizontal overflow in audited initial states or 200% root-font-size sample | tests/a11y-results.json |
| Retired URLs | PASS: 8 URLs × 2 widths; no loops/runtime errors | tests/redirect-results.json; tests/retired-url-map.md |
| Screenshot console errors | None | tests/screens/validation.json |

The full suite was followed by targeted reruns of the changed pages. Reports retain the full matrix; they are not fabricated from untested assumptions. Read tests/README.md for exact commands and environment.

## What changed

- Public owner configuration drives visible legal placeholders, contact mailboxes, review dates and the footer. Null markers remain highlighted in preview. Release mode fails before publishing output if any required fact or provider/retention review field is unresolved.
- Consent stays non-blocking with two equally prominent orange actions. Preferences are cleared in both local/session storage on withdrawal and expiry; optional media/fonts/rates/events are gated. Optional remote responses are not cached by the site service worker; old cross-origin cache entries are removed on withdrawal. Requested auth loads only when requested or when restoring an existing session.
- Public data-flow descriptions match the inspected code: public RSS/GDELT → Gemini → locally saved news/photos; watchlists in Supabase; follows on the device; an in-page popup polls a local feed, with no claim of active follow-email delivery.
- Shared focus, skip link, scroll-region labelling, menu/dialog/sheet keyboard handling, contrast, motion and mobile target sizes improved. Topic photos retain Illustration labels; photo labels missing in newer main layouts were restored. Reduced-motion headline text no longer overlaps.
- Eight unused legacy pages became redirect stubs. Current tool/account/email destinations remain for the dependencies documented in the URL map. No source/data files were deleted.

## Owner fields still unresolved

Fill the exact keys below with verified facts or counsel-approved review statements. Suggested retention periods are in LEGAL-REVIEW-PACK.md, marked **to confirm**; they are not implemented facts.

- `accessibility_audit_plan`
- `brandfetch_location`
- `coinbase_location`
- `commercial_relationships`
- `complaint_response_timeframe`
- `contact_email`
- `enterprise_number`
- `feed_licences_review`
- `finfluencer_review`
- `gemini_location`
- `google_location`
- `hosting_details`
- `hosting_location`
- `international_transfers_review`
- `last_review_date`
- `legal_bases_review`
- `legal_form`
- `legal_name`
- `mailbox_monitoring`
- `minimum_age`
- `operator_name_and_form`
- `operator_name_trading_and_form`
- `operator_status_and_form`
- `operator_type`
- `pixabay_location`
- `privacy_email`
- `pro_terms_review`
- `provider_contracts_locations`
- `registered_address`
- `resend_location`
- `retention_accounts`
- `retention_backups`
- `retention_correspondence`
- `retention_email_delivery`
- `retention_events`
- `retention_follows`
- `retention_policy_review`
- `retention_security_logs`
- `retention_watchlists`
- `security_email`
- `security_reporting_policy`
- `supabase_region`
- `trading_name`
- `vat_status`

## Lawyer and operational review still required

- Controller/operator identity, KBO/BCE/VAT and monitored mailbox/forwarding details.
- Actual Supabase region, hosting/mail providers, contracting roles, locations, DPAs and international transfers. No dashboard or server configuration was inspected or altered.
- Appropriate legal bases, consent-purpose grouping, account age/eligibility, implemented retention/deletion, complaints and rights handling. No live account/email/payment/destructive operation was performed.
- FSMA/finfluencer/investment-recommendation position and disclosures; commercial relationships; Pro consumer/payment terms before charging.
- Rights for every publisher RSS/headline/summary, Yahoo, FRED series, Coinbase, Brandfetch, Pixabay and other inputs. Attribution does not prove permission; current product contracts and licences need owner/counsel review.

## Verification limits / known accessibility work

- Automated checks do not certify WCAG conformity. Genuine screen-reader testing, real browser zoom to 200%, and authenticated/third-party interfaces remain for human review. The 200% root-font test does not prove that all fixed-pixel typography scales correctly.
- Canvas globe/chart details do not fully expose geography and individual prices to screen readers; article lists and News provide text alternatives. Dense chart pins/links and all expanded/authenticated states still need a full manual spacing/target audit. Initial viewport target sizes passed; a ≥8px gap between every interactive pair was not exhaustively established.
- Optional font/logo/rate/event requests were recorded and fulfilled with deterministic network fixtures. This isolates gate behaviour, avoids sending test analytics and does not prove provider uptime or external service correctness. No real Google sign-in, email delivery, account deletion, provider RLS or retention automation was tested.
- Functional browser suites block service workers to test the current build. CORE paths and cross-origin cache policy were inspected; installation/update/withdrawal on an already-installed home-screen app still needs a real-device smoke test.
- The legacy direct market globe remains for compatibility with its price-update interface; optional fonts are now gated there too. The main globe wrapper now uses the news globe. Full canvas usability and legacy-map accessibility remain limitations.

## Screenshot set

Desktop 1440×900 and phone 390×844; full-height desktop footer plus phone top/bottom viewport captures. Real saved articles and local assets, essential services selected. Open tests/screens/index.html.

- [tests/screens/article-1440.png](tests/screens/article-1440.png)
- [tests/screens/article-390.png](tests/screens/article-390.png)
- [tests/screens/consent-first-1440.png](tests/screens/consent-first-1440.png)
- [tests/screens/consent-first-390.png](tests/screens/consent-first-390.png)
- [tests/screens/consent-settings-1440.png](tests/screens/consent-settings-1440.png)
- [tests/screens/consent-settings-390.png](tests/screens/consent-settings-390.png)
- [tests/screens/cookies-1440.png](tests/screens/cookies-1440.png)
- [tests/screens/cookies-390.png](tests/screens/cookies-390.png)
- [tests/screens/footer-1440.png](tests/screens/footer-1440.png)
- [tests/screens/footer-390.png](tests/screens/footer-390.png)
- [tests/screens/footer-top-390.png](tests/screens/footer-top-390.png)
- [tests/screens/globe-1440.png](tests/screens/globe-1440.png)
- [tests/screens/globe-390.png](tests/screens/globe-390.png)
- [tests/screens/homepage-1440.png](tests/screens/homepage-1440.png)
- [tests/screens/homepage-390.png](tests/screens/homepage-390.png)
- [tests/screens/legal-1440.png](tests/screens/legal-1440.png)
- [tests/screens/legal-390.png](tests/screens/legal-390.png)
- [tests/screens/markets-1440.png](tests/screens/markets-1440.png)
- [tests/screens/markets-390.png](tests/screens/markets-390.png)
- [tests/screens/news-1440.png](tests/screens/news-1440.png)
- [tests/screens/news-390.png](tests/screens/news-390.png)

## Owner-only merge and publication commands — DO NOT RUN until approved

These commands are provided for the owner after all legal facts, reviews, real-device checks and release-gate failures are resolved. This task does not run them. If main changed, merge it into the preview, rebuild and repeat validation/review first; do not blindly resolve a conflict or bypass a failing gate.

```sh
git fetch origin
git switch preview/legal
git merge origin/main
python3 tools/globe-news/build.py
python3 build.py --release
python3 -m unittest discover -s tests -p 'test_*.py'
# Serve docs/ and run the browser checks listed in tests/README.md.
# If rebuilding changed files: review and commit only the intended source/generated files.
git push origin preview/legal
# STOP: owner reviews and explicitly approves the final preview.
git switch main
git pull --ff-only origin main
git merge --no-ff origin/preview/legal
python3 build.py --release
git push origin main
```

## Release risks to check after owner-approved publication

- GitHub Pages/CDN/browser caches may show mixed versions briefly. Verify the live consent script/style version and the footer on a fresh session and an existing installed app.
- Service-worker cache upgrade needs real-device confirmation; inspect existing cached optional responses after withdrawing consent.
- Client-side static redirects are not server HTTP 301s. Re-submit sitemap/check canonical destinations in Search Console; re-indexing is not immediate.
- News robots update main frequently. Preserve their fresh data during the eventual approved merge and repeat the build/tests against the final combined tree.
- Public operator configuration, source licences and mailbox promises must reflect actual operation. Passing scripts cannot confirm them or approve a regulated/consumer-law position.
