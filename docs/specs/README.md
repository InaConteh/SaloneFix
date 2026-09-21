# SaloneFix AI Build Specification Pack

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## Purpose

This pack is the implementation source of truth for an AI developer or engineering team building SaloneFix. It translates the product idea and Agile phase plan into a coherent set of product, design, technical, data, security, testing, and delivery instructions.

## Non-negotiable phase rule

Do not start by building AI automation. Build the human-accountable foundation first, then operate and measure the human-only workflow, then introduce AI recommendations as a hybrid layer.

```text
Human-First Foundation → Human-Only MVP and Baseline → Hybrid Human + AI Assistance
```

The codebase must remain fully usable when AI is disabled.

## Document order for an AI developer

1. `01-product-requirements/PRD.md`
2. `02-design/design-guide.md`
3. `03-technical/technical-requirements.md`
4. `03-technical/architecture.md`
5. `03-technical/domain-data-model.md`
6. `03-technical/api-contract.md`
7. `04-workflows/workflow-specification.md`
8. `05-security/security-privacy.md`
9. `06-ai/ai-strategy-and-build-rules.md`
10. `07-testing/testing-and-acceptance.md`
11. `08-delivery/agile-backlog.md`
12. `08-delivery/deployment-and-configuration.md`
13. `09-research/evaluation-protocol.md`

## Implementation instruction

When requirements conflict, prioritize in this order:

1. Safety, privacy, and authorization.
2. Human accountability and auditability.
3. Current Agile phase scope.
4. Core user workflow.
5. Performance and convenience.
6. Future automation.

Do not invent missing institutional policies. Record assumptions and ask the product owner when a decision would affect permissions, privacy, lifecycle state, or scope.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
