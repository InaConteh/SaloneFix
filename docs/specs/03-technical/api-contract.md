# API Contract

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. API conventions

Base path: `/api/v1`. Use JSON for structured data and multipart upload for media. Every response includes a request ID. Collections are paginated. All non-public operations require authentication and object-level authorization.

## 2. Endpoints

| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| POST | `/auth/login` | Public | Authenticate |
| POST | `/reports` | Citizen | Create report |
| GET | `/reports/{id}` | Owner/moderator/authorized officer | Read report |
| POST | `/reports/{id}/media` | Owner | Upload media |
| GET | `/reports/{id}/status` | Owner | Safe tracking view |
| GET | `/moderation/queue` | Moderator | Review queue |
| POST | `/reports/{id}/moderation-decision` | Moderator | Record decision |
| POST | `/incidents` | Moderator | Create incident |
| POST | `/incidents/{id}/reports` | Moderator | Link report |
| POST | `/incidents/{id}/assignments` | Admin/authorized officer | Assign |
| PATCH | `/incidents/{id}/status` | Authorized actor | Transition status |
| POST | `/incidents/{id}/resolution-evidence` | Assigned officer | Submit evidence |
| POST | `/incidents/{id}/resolution-review` | Reviewer | Review evidence |
| POST | `/incidents/{id}/disputes` | Citizen | Dispute resolution |
| POST | `/incidents/{id}/reopen` | Reviewer/admin | Reopen case |
| GET | `/incidents/{id}/audit` | Authorized auditor | Read history |
| GET | `/institutions` | Authorized | List institutions |
| GET | `/categories` | Public/authorized | List active categories |

## 3. Example report request

```json
{
  "category_code": "ROAD_POTHOLE",
  "description": "Large pothole near the junction beside the market.",
  "latitude": 8.4657,
  "longitude": -13.2317,
  "location_precision": "APPROXIMATE"
}
```

## 4. Example report response

```json
{
  "id": "uuid",
  "tracking_reference": "SF-2026-000001",
  "status": "SUBMITTED",
  "created_at": "2026-09-13T10:00:00Z",
  "next_step": "A moderator will review the report."
}
```

## 5. Errors

Use stable error codes: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `STATE_CONFLICT`, `MEDIA_INVALID`, `MEDIA_TOO_LARGE`, `RATE_LIMITED`, `DEPENDENCY_UNAVAILABLE`, and `INTERNAL_ERROR`.

## 6. Authorization rules

The server must check both role and object ownership. A citizen must not retrieve another citizen’s report by changing an ID. An institution officer must see only incidents assigned to the relevant institution. Audit access is restricted.

## 7. Idempotency

Report creation and media upload should support an idempotency key. Repeating a request must not create duplicate reports or duplicate audit events.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
