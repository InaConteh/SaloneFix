# Workflow and State Specification

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Citizen report flow

```text
START → CATEGORY → DESCRIPTION → LOCATION → MEDIA → CONFIRMATION → SUBMITTED
```

The image is optional. Location may use a manual fallback, but the system records that the location was user-entered or unavailable.

## 2. Moderator flow

```text
SUBMITTED → UNDER_REVIEW
UNDER_REVIEW → VERIFIED
UNDER_REVIEW → NEEDS_CLARIFICATION
UNDER_REVIEW → MERGED
UNDER_REVIEW → REJECTED
UNDER_REVIEW → ESCALATED
```

A moderator decision requires a reason for rejection, merge, escalation, or clarification.

## 3. Incident flow

```text
VERIFIED → ASSIGNED → IN_PROGRESS → RESOLUTION_UNDER_REVIEW → RESOLVED → CLOSED
```

Alternative paths:

```text
RESOLUTION_UNDER_REVIEW → NEEDS_CLARIFICATION
RESOLVED → DISPUTED → RESOLUTION_UNDER_REVIEW
IN_PROGRESS → ESCALATED
```

## 4. Transition authorization

| Transition | Allowed actor |
|---|---|
| Submit report | Citizen/system |
| Begin review | Moderator |
| Verify | Moderator |
| Merge | Moderator |
| Reject | Moderator |
| Assign | Administrator/authorized moderator |
| Accept assignment | Institutional officer |
| Update progress | Assigned officer |
| Submit resolution evidence | Assigned officer |
| Approve resolution evidence | Moderator/reviewer |
| Dispute | Citizen |
| Reopen | Reviewer/administrator |
| Close | Authorized reviewer |

## 5. Human decision requirements

For every material decision, store actor, timestamp, reason, related evidence, previous state, and new state. A system validation can block an invalid transition, but it must not silently make a substantive decision.

## 6. Notification rules

Notify the citizen after report creation, clarification request, verification/rejection, assignment, progress update, resolution review, resolution, dispute, and closure. Do not send private moderator notes or exact internal data.

## 7. Failure behavior

If persistence fails, show failure and preserve a retryable draft where safe. If notifications fail, keep the case state and log delivery failure. If a future AI service fails, continue with the human-only path.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
