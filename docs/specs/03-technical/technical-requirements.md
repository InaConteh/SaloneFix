# Technical Requirements Document

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Technology baseline

| Layer | Required choice |
|---|---|
| Frontend | React with TypeScript |
| Backend | Python FastAPI |
| Database | PostgreSQL with PostGIS |
| Media | Private S3-compatible object storage or protected local equivalent |
| Image processing | Pillow plus a maintained metadata library |
| Authentication | Secure session or short-lived token mechanism |
| Testing | Pytest plus frontend/API tests |
| Version control | Git |

## 2. Functional requirements

| ID | Requirement | Priority |
|---|---|---:|
| FR-001 | Create a citizen report with category, description, location, and optional image | Must |
| FR-002 | Validate required fields and media | Must |
| FR-003 | Preserve original report content | Must |
| FR-004 | Generate a unique tracking reference | Must |
| FR-005 | Allow a citizen to view safe report status | Must |
| FR-006 | Allow moderators to review reports | Must |
| FR-007 | Allow moderators to create or link incidents | Must |
| FR-008 | Preserve all original reports after merging | Must |
| FR-009 | Assign incidents to institutions and officers | Must |
| FR-010 | Enforce allowed lifecycle transitions | Must |
| FR-011 | Require resolution evidence before resolution | Must |
| FR-012 | Allow citizens to dispute a resolution | Must |
| FR-013 | Allow authorized users to reopen disputed cases | Must |
| FR-014 | Record append-only audit events | Must |
| FR-015 | Provide role-specific dashboards | Must |
| FR-016 | Provide search, filtering, and map/list views | Should |
| FR-017 | Provide notifications for material events | Should |
| FR-018 | Extract metadata for reviewer visibility | Should |
| FR-019 | Provide a WhatsApp adapter | Later |
| FR-020 | Provide AI recommendations | Later |

## 3. Non-functional requirements

### Security

Enforce server-side RBAC, object-level authorization, secure cookies/tokens, rate limits, file validation, private media storage, short-lived signed URLs, audit events, and secret management [2].

### Privacy

Minimize identity, location, device, and image data. Generalize public map locations. Restrict exact coordinates, original images, identity, and internal notes.

### Reliability

The system must not claim a report was created until persistence succeeds. External failures must produce a recoverable error state. AI and WhatsApp outages must not stop the human workflow.

### Performance

For prototype expectations, common form and dashboard operations should return a visible result within 2 seconds under the expected test load, excluding external provider latency. Upload and analysis operations may be asynchronous.

### Accessibility

Target WCAG 2.2 AA practices [1].

### Maintainability

Separate domain services from channel adapters, use migrations, typed schemas, documented configuration, testable business rules, and structured logs.

## 4. Technical constraints

- Freetown-focused prototype.
- Limited student-project budget.
- Small controlled evaluation dataset.
- Variable connectivity and GPS quality.
- Institutional access may be limited.
- AI and WhatsApp access may be unavailable.

## 5. Definition of technical readiness

The human-only application is technically ready when a complete report lifecycle passes automated tests and a manual demonstration without AI or WhatsApp.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
