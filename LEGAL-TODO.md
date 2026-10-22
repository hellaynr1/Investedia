# Legal review checklist

These documents are a strong draft and **must be reviewed by a Belgian lawyer before relying on them**, especially liability limits, GDPR legal bases, retention, and the FSMA/finfluencer position. Do not publish with unverified owner details.

## Owner facts to complete

- [ ] [OWNER: KBO/BCE number]
- [ ] [OWNER: VAT number or not applicable]
- [ ] [OWNER: commission an accessibility audit and publish a remediation plan]
- [ ] [OWNER: configure event retention]
- [ ] [OWNER: confirm a workable complaints-response process and timeframe]
- [ ] [OWNER: confirm mailbox forwarding and monitoring]
- [ ] [OWNER: confirm registered trading name]
- [ ] [OWNER: confirm the proposed minimum age of 16 before publication]
- [ ] [OWNER: confirm there are no existing commercial relationships before publication]
- [ ] [OWNER: confirm these bases, assess legitimate interests and document provider contracts before publication]
- [ ] [OWNER: full registered address]
- [ ] [OWNER: legal name and legal form]
- [ ] [OWNER: legal name, trading name and legal form]
- [ ] [OWNER: legal name; natural person, sole trader or company; legal form]
- [ ] [OWNER: obtain Belgian legal review of the service and finfluencer position]
- [ ] [OWNER: prepare and obtain legal review of Pro terms before taking payments]
- [ ] [OWNER: registered address]
- [ ] [OWNER: set and implement account-closure, backup, usage-event, correspondence, email and security-log retention periods; confirm each provider’s retention]
- [ ] [OWNER: verify GitHub’s current legal address and service contact details]
- [ ] [OWNER: verify Supabase project region]
- [ ] [OWNER: verify contracting entities, countries and processing terms]
- [ ] [OWNER: verify redistribution and commercial-use permissions for every feed, especially Yahoo Finance, before monetisation]
- [ ] [OWNER: verify region settings, DPAs, SCCs, certification where relied on, and the transfer assessment]

- [ ] [OWNER: verify security mailbox and reporting policy before publication]

## Operational checks before publication

- [ ] Confirm info@investedia.com forwarding and monitoring for privacy, security and legal notices.
- [ ] Confirm the proposed account eligibility of 16+ and whether sign-up needs an age attestation.
- [ ] Confirm the date format: 22 October 2026 (day, month in English, year).
- [ ] Record controller contact, enterprise/KBO/BCE and VAT status as required by Belgian law.
- [ ] Verify GitHub, Inc. hosting address/service details; Supabase region; all provider DPAs, subprocessors and international-transfer mechanisms. Do not assume DPF certification.
- [ ] Configure and document actual retention/deletion for account closure, watchlists, Supabase events, messages, provider logs, email delivery records and backups. No fixed deletion SLA is asserted by these drafts.
- [ ] Review the pre-existing Supabase events feature: it is now gated by Analytics consent. The category is disclosed because the code already contains analytics; no new analytics provider was introduced. The owner requested the two actions Accept all and Accept essential; review the grouping of optional purposes before publication.
- [ ] Third-party images & services is the safer opt-in option implemented for Brandfetch, Google Fonts and Coinbase. Verify other deployments do not inject trackers or remote media outside this repository.
- [ ] Increment the consent policy VERSION in assets/consent.js when consent purposes or categories materially change.
- [ ] Verify authentication and provider-managed session storage settings and update the cookie inventory if they change.
- [ ] Check all content/data licences, especially Yahoo Finance permissions before monetisation. FRED notice retained in Sources.
- [ ] Confirm no advertising, affiliate or sponsorship relationships currently exist; disclose any exceptions before publication.
- [ ] Establish a genuine correction, complaint and takedown handling process, with human responsibility and achievable response targets.
- [ ] Confirm legal scope under the DSA and EU AI Act; these pages make no compliance-certification claim.
- [ ] Commission accessibility review against WCAG 2.2 AA; globe/chart accessibility remains a known limitation.
- [ ] Prepare separate legally reviewed Pro payment/cancellation/withdrawal terms before taking payments.
- [ ] Review /.well-known/security.txt and renew its expiry before 22 October 2027; decide who handles reports.
- [ ] Verify account, newsletter and deletion flows against actual deployed behaviour; a local newsletter acknowledgement does not send or subscribe an email by itself.

## Primary references checked for this draft

- GDPR: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- EDPB cookie banner report: https://www.edpb.europa.eu/system/files/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf
- Belgian DPA complaints: https://www.autoriteprotectiondonnees.be/citoyen/agir/introduire-une-plainte
- Supabase transfers: https://supabase.com/legal/privacy-resources/data-residency-and-transfers-faq
- Resend legal hub: https://resend.com/legal
- GitHub privacy: https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement
- FSMA investor warning: https://www.fsma.be/en/warnings/be-wary-investment-offers-made-through-social-media

## Code inventory

Cookie rows are recorded in tests/fixtures/legal-storage.json and rendered in src/pages/cookies.html. The legal-page tests cross-check literal storage keys. Account/session keys are necessary when the user requests authentication; optional appearance/progress keys are blocked before consent. Browser storage is not claimed to be encrypted or anonymous.
