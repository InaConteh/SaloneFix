# Deployment and Configuration Guide

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Environments

| Environment | Data | Purpose |
|---|---|---|
| Development | Synthetic/local | Engineering |
| Staging | Controlled test data | Integration and UAT |
| Demonstration | Approved demo data | Presentation and evaluation |

## 2. Configuration

```text
APP_ENV
DATABASE_URL
STORAGE_ENDPOINT
STORAGE_BUCKET
STORAGE_ACCESS_KEY
STORAGE_SECRET
SESSION_SECRET
JWT_SECRET
EMAIL_PROVIDER_URL
WHATSAPP_TOKEN              # future/optional
WHATSAPP_WEBHOOK_SECRET     # future/optional
AI_API_KEY                  # future/optional
AI_BASE_URL                 # future/optional
```

Do not commit real values. Provide `.env.example` with placeholder names only.

## 3. Deployment requirements

- TLS in staging/demo.
- Database migrations run before application release.
- Private storage bucket.
- Health endpoint.
- Structured logs.
- Error monitoring.
- Backup procedure.
- Restoration test.
- Rollback procedure.

## 4. Human-first deployment rule

The application must start and operate when `AI_API_KEY` is absent. The application must start and operate when WhatsApp variables are absent. Disabled integrations must expose a clear status, not create hidden failures.

## 5. Release process

1. Run unit and integration tests.
2. Run security checks.
3. Apply migration in staging.
4. Run end-to-end acceptance tests.
5. Review logs and error rates.
6. Obtain release approval.
7. Deploy demonstration environment.
8. Record version and deployment decision.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
