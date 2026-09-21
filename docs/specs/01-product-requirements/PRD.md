# Product Requirements Document

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Product decision

Build SaloneFix as a human-accountable public-service incident-management platform. Citizens submit reports. Moderators review and organize them. Institutions receive assigned incidents and report progress. Human reviewers assess resolution evidence. The platform preserves the lifecycle for accountability.

## 2. Problem

Public-service complaints may be incomplete, duplicated, poorly located, difficult to route, and difficult to track through resolution. Citizens may not know what happened after reporting. Institutions may lack structured information and a reliable history of decisions.

## 3. Product vision

Turn citizen-submitted public-service complaints into structured, traceable incidents that can be reviewed, assigned, acted on, disputed, and closed through accountable human decisions.

## 4. Target users

| User | Goal | Main pain |
|---|---|---|
| Citizen | Report and track a problem | Unclear channel and lack of feedback |
| Moderator | Make consistent review decisions | Incomplete evidence and duplicate reports |
| Institutional officer | Act on assigned incidents | Poorly structured incoming information |
| Administrator | Control platform configuration | Permission and governance risk |
| Auditor/supervisor | Inspect lifecycle history | Changes may be difficult to reconstruct |

## 5. MVP categories

Start with four categories: roads/potholes, drainage/flooding, waste, and public facilities. The category list must be configurable by an administrator.

## 6. Current phase: Human-First Foundation

The current release must include the human workflow foundation and must not depend on AI or WhatsApp. It must support report capture, manual moderation, incident fusion, assignment, status changes, resolution evidence, disputes, notifications, role permissions, and audit events.

## 7. Human-Only phase

After the foundation passes acceptance testing, operate the full workflow without AI and measure review time, reviewer agreement, routing quality, duplicate identification, resolution decisions, usability, and audit completeness.

## 8. Hybrid phase

Only after the human-only baseline is stable may the team add AI recommendations. AI can suggest category, similarity, conflict, or priority. Humans retain decision authority.

## 9. Goals

- Improve the completeness and structure of citizen reports.
- Reduce duplicated institutional work through human-approved incident fusion.
- Make assignment and status visible.
- Require and review resolution evidence.
- Preserve an auditable history.
- Establish a measurable human-only baseline.

## 10. Non-goals

- Determining whether a person is truthful.
- Automatically accusing people or institutions.
- Replacing emergency services or public authorities.
- Nationwide production deployment.
- Autonomous AI routing or closure.
- Blockchain-based proof.

## 11. Success metrics

| Metric | Initial target |
|---|---:|
| Valid report completion in usability tests | ≥90% |
| Unauthorized status changes rejected | 100% of test attempts |
| Material status changes with audit events | 100% |
| Human moderator workflow completion | 100% of supported scenarios |
| Resolution dispute can reopen an incident | 100% of test cases |
| AI-independent workflow completion | 100% when AI is disabled |

## 12. Product principles

1. The original report is preserved.
2. Reports and incidents are different objects.
3. Human decisions are explicit and auditable.
4. Missing evidence is not proof of dishonesty.
5. AI is a later recommendation layer, not a dependency.
6. The system must fail safely and clearly.

## 13. Primary demonstration

Demonstrate a complete lifecycle: citizen submits a pothole report, moderator reviews it, a second report is linked, an institution is assigned, progress is updated, resolution evidence is submitted, the citizen disputes the resolution, and the audit history shows the full chain.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
