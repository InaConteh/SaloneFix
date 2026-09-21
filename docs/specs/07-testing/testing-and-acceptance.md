# Testing and Acceptance Specification

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Test levels

1. Unit tests.
2. Integration tests.
3. API contract tests.
4. End-to-end workflow tests.
5. Security tests.
6. Accessibility tests.
7. User acceptance tests.
8. Human-only baseline evaluation.
9. Later hybrid AI evaluation.

## 2. Critical test cases

| ID | Scenario | Expected result |
|---|---|---|
| TC-001 | Valid report submission | Report created and reference returned |
| TC-002 | Missing description | Actionable validation error |
| TC-003 | Missing location | Fallback or configured rejection, clearly explained |
| TC-004 | Invalid media | Upload rejected without corrupting report |
| TC-005 | Moderator verifies report | Decision and audit event created |
| TC-006 | Moderator merges duplicate | Reports preserved and linked to one incident |
| TC-007 | Unauthorized status change | Request rejected and logged |
| TC-008 | Officer submits evidence | Evidence stored and review state created |
| TC-009 | Citizen disputes resolution | Incident enters disputed/review state |
| TC-010 | Reviewer reopens case | Valid transition and audit event |
| TC-011 | Audit read access | Only authorized users can view full history |
| TC-012 | AI disabled | Complete human workflow still succeeds |
| TC-013 | Future AI provider unavailable | Human-only fallback continues |
| TC-014 | Repeated submit request | Idempotency prevents duplicates |
| TC-015 | Public map access | Exact restricted location is not exposed |

## 3. Acceptance criteria for current launch

The Human-First Foundation is accepted when:

- A citizen can submit a report.
- A moderator can review it without AI.
- Multiple reports can be linked to one incident.
- An institution can manage an assignment.
- Resolution evidence and disputes work.
- Status transitions are permission-controlled.
- Material events are auditable.
- Critical security and privacy tests pass.
- The workflow works without AI and WhatsApp.

## 4. Defect severity

- Critical: data loss, unauthorized access, false success, broken audit history.
- High: blocked core workflow, incorrect permissions, incorrect lifecycle transition.
- Medium: important usability or reporting problem with workaround.
- Low: cosmetic or minor text issue.

Critical and high defects block release.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
