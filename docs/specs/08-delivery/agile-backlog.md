# Agile Backlog and Delivery Plan

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## Phase 1: Human-First Foundation

### Epic HF-01: Scope and governance

- Confirm scope and roles.
- Approve categories.
- Approve status lifecycle.
- Approve privacy and ethics process.

### Epic HF-02: Authentication and RBAC

- Create user model.
- Implement login/session.
- Implement server-side role checks.
- Add object-level access tests.

### Epic HF-03: Citizen reporting

- Build report form.
- Validate fields.
- Add location fallback.
- Add media upload.
- Generate tracking reference.
- Add status view.

### Epic HF-04: Moderator review

- Build queue.
- Build review workspace.
- Add verify/clarify/reject/escalate decisions.
- Add manual merge.
- Require reasons.

### Epic HF-05: Incident and assignment

- Create incident.
- Link reports.
- Assign institution/officer.
- Accept/decline assignment.
- Track due date.

### Epic HF-06: Resolution and disputes

- Add progress updates.
- Add resolution evidence.
- Add review decision.
- Add citizen dispute.
- Add reopen and close.

### Epic HF-07: Audit and notifications

- Add audit events.
- Add audit viewer.
- Add material-event notifications.
- Log delivery failures.

## Phase 2: Human-Only MVP

- Run realistic test scenarios.
- Conduct UAT.
- Measure moderator time.
- Measure reviewer agreement.
- Measure routing and duplicate decisions.
- Analyze defects and revise workflow.
- Freeze human-only baseline.

## Phase 3: Hybrid AI

- Add AI adapter interface.
- Add category recommendation.
- Add recommendation display.
- Add human override.
- Log AI and human decisions.
- Evaluate against human-only baseline.

## Sprint rule

Every story needs acceptance criteria, test evidence, owner, and a decision about whether it is in the current phase. Future AI stories cannot block Phase 1 or Phase 2 completion.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
