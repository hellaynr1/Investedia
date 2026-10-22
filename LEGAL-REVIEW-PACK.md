# Investedia — Belgian prelaunch review brief

Prepared 22 October 2026 for counsel. This pack records observed code and questions, not legal approval. The operator's identity, provider contracts, deployment settings and actual retention remain unverified. Fill `legal-config.json`; null values deliberately block release.

## Service and current implementation

Investedia is a static financial-news and education site hosted through GitHub Pages (`docs/`). Public pages show publisher-linked summaries, market context, a globe, saved market/economic datasets and locally hosted topic photographs. Accounts use Supabase Auth (email/password or requested Google sign-in); the `watchlists` table stores requested account lists. Local `inv-follow`, `inv-follow-topics` and `inv-follow-items` store follows. No separate follow-email backend/table was found in this branch. The headline popup polls a saved first-party feed; it is not an email alert service. Email templates/SQL configure Supabase confirmation and Resend welcome delivery; actual deployment is not proven by repository files. No payment integration or operative Pro subscription contract was found.

The robot on GitHub Actions fetches GDELT and public publisher/official RSS, sends headline/description candidates to Google Gemini for selection/summary, downloads Pixabay topic images and saves JSON/JPEGs. Visitor account data is not included in those model requests in the inspected code. Repository workflows and runtime credentials were not executed as part of this review.

## Data flows for counsel

All bases below are **proposed for review**. All suggested periods are **to confirm and implement**, not assertions of existing deletion jobs. Locations are **to confirm** from contracts, dashboard regions and subprocessors.

| Data | Purpose | Legal basis proposed | Provider | Location | Retention proposed — to confirm |
|---|---|---|---|---|---|
| Email, auth ID, password-auth/session metadata, requested Google profile | Requested account and sign-in | Contract; assess necessary security interests | Supabase Auth; Google only when requested; jsDelivr SDK delivery | Supabase project region, auth/support locations; Google/CDN infrastructure to confirm | Active account; remove within 30 days of verified closure, subject to lawful holds; provider logs separately |
| Account watchlists (`watchlists`) | Requested saved lists across devices | Contract | Supabase database | Selected project region to confirm | Account lifetime; remove with closure within 30 days |
| Country/topic/article follows and guest lists | Requested following/list features | Necessity of requested feature; confirm local-storage treatment | Device localStorage; first-party code | Visitor device | Until visitor clears/changes them; no coded expiry |
| Consent version/date and three category flags | Respect and evidence choices | Consent-management necessity / legal obligation to assess | Device localStorage (`inv-consent`) | Visitor device | 12 months, or invalidated by changed policy version |
| Theme, palette, studio, progress, legacy profile, notification-read count | Optional personalisation | Consent | Device storage | Visitor device | Until withdrawal or clearing; no independent timed expiry |
| Page path, referring hostname, device category, timezone, language, member flag, limited event detail; request IP/logs at infrastructure layer | Optional first-party usage measurement | Consent for events; assess infrastructure/security basis separately | Supabase `events`; GitHub hosting | Region and logging locations to confirm | Raw optional events 90 days, aggregate non-identifying counts 12 months; implement purge first |
| IP, user agent, permitted referrer in optional logo/font/rate requests | Logo/font delivery and rates | Consent proposed; assess each purpose | Brandfetch, Google Fonts, Coinbase | Contract/infrastructure locations to confirm | No optional browser cache through site worker; each provider's server retention to confirm |
| Correspondence, complaints, rights/content/security notices | Respond, resolve disputes and prevent abuse | Legitimate interests / legal obligations to assess | Monitored mailbox and forwarding provider (owner to identify) | Mail provider/forwarding destinations to confirm | Routine correspondence 12 months after resolution; disputes/legal holds reviewed case by case |
| Recipient address, confirmation/welcome message and delivery/security records | Transactional account email | Contract and necessary security interests | Supabase Auth, Resend | Contract, processing and subprocessors to confirm | Delivery records 30 days if configurable; necessary security logs 90 days; verify provider limits |
| Provider backups/security logs | Recovery, integrity and incident handling | Proportionate legitimate interests / legal obligation to assess | GitHub, Supabase, mail providers | To confirm | Rolling backups up to 30 days; security logs 90 days, exception for documented incident/hold |
| Public headlines/descriptions, source URLs/times and country/company context | Discovery and AI-assisted editorial summaries | Assess copyright/database rights and any personal-data basis for public reporting | GDELT, listed publishers/central banks, Google Gemini, GitHub Actions | Provider/model/project settings to confirm | Public feed/archive lifecycle in code; review historical archive and model-provider retention separately |
| Topic photos, creator/source/licence credit | Illustrative editorial images, served locally | Licence/rightsholder review, not assumed GDPR consent | Pixabay API → GitHub-hosted JPEG | Provider and repository infrastructure to confirm | While licensed content is used; preserve licence evidence and handle takedowns |

## Questions requiring answers

1. Who is the controller/operator: natural person, sole trader or company? Verify legal/trading name, form, registered Belgian address, KBO/BCE and VAT status. Which mailbox is monitored for privacy/security complaints and which forwarding provider receives messages?
2. Are the proposed bases, optional-service grouping and two equally prominent consent actions appropriate? Is retaining consent evidence only on the visitor device sufficient for the intended operation? Identify a legitimate-interest assessment and provider-contract record where needed.
3. Which Supabase region is actually selected? Verify every processor/controller role, DPA, subprocessors and international-transfer basis. A selected region alone is not a compliance determination. Do not infer EU residency or DPF participation.
4. Which retention periods are proportionate and technically supported? Assign actual purge/closure/backup ownership. Do not put suggested periods into public pages until implemented.
5. Does personalised context, impact/direction labelling, watchlists, alerts or paid access create investment-recommendation, marketing or regulated-service duties under Belgian/EU rules? Assess FSMA/finfluencer guidance, MAR conflict/disclosure obligations and whether disclaimers/placement need changes. “Not investment advice” is not offered as a legal exemption.
6. Review AI Act applicability/transparency and responsibility for generated summaries. The public AI page and small contextual disclosures describe assistance; topic photographs remain labelled Illustration. Confirm whether additional labels or editorial review are required. Automated validation is not human fact checking.
7. Confirm applicable age and consumer-law terms. Review liability, complaints, rights requests, corrections/takedown and DSA applicability without assuming intermediary status. Set a practical response process rather than an unsupported guaranteed deadline.
8. Review a separate Pro contract before payments: price/tax, renewal, trial, cancellation, statutory withdrawal/digital-content exceptions, service availability and refunds. The current draft is a placeholder, not approval to sell subscriptions.
9. Audit redistribution, caching, derivative summary, trademark and commercial-use permissions for **each** feed and asset. Public accessibility and attribution do not establish permission. Review Yahoo Finance, FRED series owners, Coinbase rates, Brandfetch logo/CDN terms, Pixabay (including recognisable people/brands and contextual use), GDELT and each publisher RSS licence. Preserve evidence with retrieval date; obtain licences or replace feeds where necessary.
10. Review accessibility scope and the outstanding report, including keyboard/text equivalents for canvas charts/globe, resize, low-contrast/tap-target exceptions and authenticated flows. No WCAG conformance certification is claimed.

## Source and deployment evidence

- Browser/storage: `assets/consent.js`, `assets/ui.js`, `tests/fixtures/legal-storage.json`, `tests/consent-matrix.md`.
- Public news/AI/photo pipeline: `update_globe_news.py`, `news_rules.py`, `.github/workflows/update-globe-news.yml`, `assets/globe/photos/index.json`.
- Account lists: `assets/ui.js` (`watchlists`); usage: REST `/rest/v1/events`; templates: `emails/`.
- Local checks cannot establish Supabase RLS deployment, email-trigger installation, provider region/retention, ownership facts or commercial contracts.

## Primary reference starting points (checked 22 October 2026)

These are review resources, not statements that all current terms have been met.

- [Supabase regions](https://supabase.com/docs/guides/platform/regions): verify the actual project setting; location selection is not proof of regulatory compliance.
- [Pixabay licence summary](https://pixabay.com/service/license-summary/) and linked full terms: restrictions and third-party rights still need contextual review.
- [FRED API terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html): check rights attached to individual data series as well as API conditions.
- [GDPR official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj) and [FSMA](https://www.fsma.be/): counsel to retrieve current applicable texts/guidance; automated access to the attempted GDPR/finfluencer pages was unavailable during this pass.
- [Resend legal hub](https://resend.com/legal), [GitHub privacy](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement), [Brandfetch terms](https://brandfetch.com/terms), [Coinbase legal](https://www.coinbase.com/legal), [Google terms](https://policies.google.com/terms), [Yahoo terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html): owner/counsel to verify the applicable product terms, contracting entity and region rather than relying on this link list.
