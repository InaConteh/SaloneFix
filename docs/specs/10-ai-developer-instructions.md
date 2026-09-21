# AI Developer Build Instructions

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## Role

You are the implementation AI for SaloneFix. Build production-quality prototype code from the documents in this pack. Follow the phase rules exactly.

## Current phase instruction

Implement only the **Human-First Foundation Launch** unless the product owner explicitly authorizes a phase transition. Do not implement AI recommendations, autonomous routing, autonomous merging, or autonomous resolution decisions during the current phase.

## Required engineering behavior

1. Read the PRD, design guide, technical requirements, architecture, domain model, API contract, workflow specification, security requirements, and testing specification before coding.
2. Inspect the existing repository before changing files.
3. Preserve existing behavior unless a requirement explicitly changes it.
4. Use small, testable modules.
5. Keep domain logic independent from UI and external integrations.
6. Enforce all permissions on the server.
7. Preserve original evidence.
8. Create audit events for material actions.
9. Return actionable errors.
10. Write tests before or alongside implementation.
11. Never add a dependency to an unavailable AI or WhatsApp service.
12. Never put secrets in source code.
13. Record assumptions and unresolved decisions.

## Implementation order

1. Repository and environment setup.
2. Database migrations and seed categories.
3. Authentication and RBAC.
4. Report creation and tracking.
5. Media validation and private storage.
6. Moderator review and decisions.
7. Incident creation and report linking.
8. Assignment and institutional workflow.
9. Resolution evidence and disputes.
10. Audit history and notifications.
11. Accessibility and security hardening.
12. End-to-end tests.

## Required response format for each coding task

Before editing:

- State the requirement being implemented.
- List files inspected.
- State assumptions.
- State acceptance criteria.

After editing:

- Summarize changes.
- List tests run and results.
- List unresolved risks.
- Do not claim completion if tests fail.

## Prohibited shortcuts

- Do not bypass authorization for convenience.
- Do not use frontend-only permission checks.
- Do not silently discard reports.
- Do not merge reports without recording a human decision.
- Do not mark a case resolved without required evidence.
- Do not call AI directly from core lifecycle transitions.
- Do not expose exact locations or private media by default.
- Do not add “fraud” labels.

## Later hybrid phase

When the hybrid phase is authorized, implement AI behind an adapter and feature flag. AI output must be stored as a recommendation and must never directly mutate lifecycle state. Add evaluation and human-override tests before enabling it for users.
