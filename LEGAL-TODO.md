# Legal completion checklist

These documents must be reviewed by a Belgian lawyer before relying on them. No owner facts are inferred. Fill legal-config.json with verified plain text values; null keeps the highlighted preview marker. This configuration is public: enter display text only, never credentials, keys, contracts or private case records. Run `python3 tools/legal_check.py` for the remaining list.

## Owner facts and review decisions

- [ ] `legal-config.json.enterprise_number` — [OWNER: KBO/BCE number]
- [ ] `legal-config.json.vat_status` — [OWNER: VAT number or not applicable]
- [ ] `legal-config.json.accessibility_audit_plan` — [OWNER: commission an accessibility audit and publish a remediation plan]
- [ ] `legal-config.json.retention_events` — [OWNER: configure event retention]
- [ ] `legal-config.json.complaint_response_timeframe` — [OWNER: confirm a workable complaints-response process and timeframe]
- [ ] `legal-config.json.mailbox_monitoring` — [OWNER: confirm mailbox forwarding and monitoring]
- [ ] `legal-config.json.trading_name` — [OWNER: confirm registered trading name]
- [ ] `legal-config.json.minimum_age` — [OWNER: confirm the proposed minimum age of 16 before publication]
- [ ] `legal-config.json.commercial_relationships` — [OWNER: confirm there are no existing commercial relationships before publication]
- [ ] `legal-config.json.legal_bases_review` — [OWNER: confirm these bases, assess legitimate interests and document provider contracts before publication]
- [ ] `legal-config.json.registered_address` — [OWNER: full registered address]
- [ ] `legal-config.json.operator_name_and_form` — [OWNER: legal name and legal form]
- [ ] `legal-config.json.operator_name_trading_and_form` — [OWNER: legal name, trading name and legal form]
- [ ] `legal-config.json.operator_status_and_form` — [OWNER: legal name; natural person, sole trader or company; legal form]
- [ ] `legal-config.json.legal_name` — [OWNER: legal name]
- [ ] `legal-config.json.finfluencer_review` — [OWNER: obtain Belgian legal review of the service and finfluencer position]
- [ ] `legal-config.json.pro_terms_review` — [OWNER: prepare and obtain legal review of Pro terms before taking payments]
- [ ] `legal-config.json.registered_address` — [OWNER: registered address]
- [ ] `legal-config.json.retention_policy_review` — [OWNER: set and implement account-closure, backup, usage-event, correspondence, email and security-log retention periods; confirm each provider’s retention]
- [ ] `legal-config.json.hosting_details` — [OWNER: verify GitHub’s current legal address and service contact details]
- [ ] `legal-config.json.supabase_region` — [OWNER: verify Supabase project region]
- [ ] `legal-config.json.provider_contracts_locations` — [OWNER: verify contracting entities, countries and processing terms]
- [ ] `legal-config.json.feed_licences_review` — [OWNER: verify redistribution and commercial-use permissions for every feed, especially Yahoo Finance, before monetisation]
- [ ] `legal-config.json.international_transfers_review` — [OWNER: verify region settings, DPAs, SCCs, certification where relied on, and the transfer assessment]
- [ ] `legal-config.json.security_reporting_policy` — [OWNER: verify security mailbox and reporting policy before publication]
- [ ] `legal-config.json.legal_form` — [OWNER: legal form]
- [ ] `legal-config.json.operator_type` — [OWNER: operator type]
- [ ] `legal-config.json.contact_email` — [OWNER: contact email]
- [ ] `legal-config.json.privacy_email` — [OWNER: privacy email]
- [ ] `legal-config.json.security_email` — [OWNER: security email]
- [ ] `legal-config.json.retention_accounts` — [OWNER: retention accounts]
- [ ] `legal-config.json.retention_watchlists` — [OWNER: retention watchlists]
- [ ] `legal-config.json.retention_follows` — [OWNER: retention follows]
- [ ] `legal-config.json.retention_correspondence` — [OWNER: retention correspondence]
- [ ] `legal-config.json.retention_email_delivery` — [OWNER: retention email delivery]
- [ ] `legal-config.json.retention_security_logs` — [OWNER: retention security logs]
- [ ] `legal-config.json.retention_backups` — [OWNER: retention backups]
- [ ] `legal-config.json.hosting_location` — [OWNER: hosting location]
- [ ] `legal-config.json.resend_location` — [OWNER: resend location]
- [ ] `legal-config.json.gemini_location` — [OWNER: gemini location]
- [ ] `legal-config.json.brandfetch_location` — [OWNER: brandfetch location]
- [ ] `legal-config.json.pixabay_location` — [OWNER: pixabay location]
- [ ] `legal-config.json.google_location` — [OWNER: google location]
- [ ] `legal-config.json.coinbase_location` — [OWNER: coinbase location]
- [ ] `legal-config.json.last_review_date` — [OWNER: last review date]

## Completion order (about 30 minutes once records are available)
1. Copy registration details from official company records: legal_name, trading_name, legal_form, operator_type, operator_status_and_form, operator_name_and_form, operator_name_trading_and_form, registered_address, enterprise_number, vat_status. Compound display fields must match the individual fields.
2. Verify contact_email, privacy_email, security_email and actual forwarding/monitoring; fill mailbox_monitoring and security_reporting_policy.
3. Open GitHub/Supabase/Resend dashboards and contracts. Record hosting_details, hosting_location, supabase_region and every *_location field; verify provider_contracts_locations and international_transfers_review. Do not guess regions or certification.
4. Confirm minimum_age and update any account-age controls if necessary. Fill commercial_relationships and complaint_response_timeframe with achievable processes.
5. Review and implement each retention_* period. Suggested periods in LEGAL-REVIEW-PACK.md are not operational facts. Set retention_policy_review only after actual deletion/backup settings are verified.
6. Have the lawyer complete legal_bases_review, finfluencer_review, pro_terms_review, feed_licences_review and accessibility_audit_plan. Set last_review_date to the actual review date.
7. Run normal build, Python tests and browser suites. Never publish with `python3 build.py --release` failing. No payment/Pro functionality should be activated on the basis of draft terms.

## Code inventory
Storage keys: tests/fixtures/legal-storage.json and cookies.html. Actual browser calls are checked in tests/consent.spec.mjs. Templates in emails/ do not prove deployment; verify Supabase triggers and Resend configuration separately. No live account, email, payment or deletion operation was performed by the prelaunch checks.
