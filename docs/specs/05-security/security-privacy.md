# Security, Privacy, and Governance Requirements

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Threat priorities

Protect against spam, fake accounts, unauthorized report access, media leakage, location exposure, unauthorized status changes, evidence deletion, account compromise, API abuse, provider failure, and future prompt injection.

## 2. Security requirements

- Server-side RBAC and object-level authorization.
- Secure password hashing or approved external identity provider.
- Short-lived sessions/tokens and secure cookies.
- CSRF protection where applicable.
- Rate limits on authentication, report creation, media upload, and tracking.
- File signature, MIME, size, and dimension validation.
- Private object storage and short-lived signed URLs.
- TLS in deployed environments.
- Secrets only in environment or secret-manager configuration.
- Append-only audit events.
- Backups and restoration tests.
- Logs that exclude secrets and unnecessary personal data.

## 3. Privacy rules

Collect only data required to submit, manage, communicate, evaluate, and audit an incident. Do not make exact identity, exact coordinates, device metadata, or original media public by default.

## 4. Location policy

The operational system may store exact coordinates when necessary for routing, but public maps should generalize locations. Explain why location is requested. A user may continue without location when allowed, with reduced operational usefulness recorded.

## 5. Media policy

Images are private by default. Remove unnecessary metadata from public derivatives. Retain original files only for a justified period. Do not treat missing or altered EXIF as proof of dishonesty.

## 6. Audit policy

Never silently delete or rewrite material decisions. Corrections create a new event referencing the corrected value. Audit access is restricted and itself logged.

## 7. AI governance for later phase

AI must not make legal findings, accusations, autonomous closure decisions, or irreversible access decisions. AI output is a recommendation. Human review is mandatory for uncertainty, conflicts, high-impact cases, and model failure [3].

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
