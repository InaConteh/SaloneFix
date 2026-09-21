# SaloneFix Design Guide

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. Design objective

Design for clarity, trust, accessibility, and accountable human action. SaloneFix should feel like a dependable public-service workflow, not an AI experiment.

## 2. Design principles

- **Clarity:** One primary action per screen.
- **Human accountability:** Show who is responsible for each decision.
- **Evidence neutrality:** Use “requires review” instead of accusatory language.
- **Low friction:** Ask only for information needed at that step.
- **Recoverability:** Users can go back, cancel, correct, or dispute.
- **Accessibility:** Support keyboard use, mobile screens, readable text, and non-color status cues [1].
- **Privacy:** Avoid public exposure of exact identity and unnecessary location precision.

## 3. Information architecture

```text
Citizen
 ├── New report
 ├── My reports
 ├── Report detail
 └── Dispute resolution

Moderator
 ├── Review queue
 ├── Incident workspace
 ├── Assignment review
 └── Audit history

Institution officer
 ├── Assigned incidents
 ├── Incident detail
 ├── Progress update
 └── Resolution evidence

Administrator
 ├── Users and roles
 ├── Institutions
 ├── Categories
 └── Configuration and audit
```

## 4. Visual language

Use a restrained civic-service visual system:

| Token | Value | Use |
|---|---|---|
| Primary blue | `#0B5FFF` | Primary action and links |
| Text | `#1D2939` | Body text |
| Muted text | `#667085` | Supporting information |
| Surface | `#F8FAFC` | Page background |
| Success | `#18794E` | Verified/resolved, always with text/icon |
| Warning | `#A15C00` | Needs review |
| Danger | `#B42318` | Rejected/destructive actions |
| Border | `#D0D5DD` | Dividers and inputs |

Use a readable sans-serif font. Use a 4px spacing base. Use a minimum 44px touch target. Use an 8px card radius. Do not use decorative gradients or animation that distracts from decisions.

## 5. Status design

Every status includes text, icon, and color. Examples:

- Submitted — clock icon
- Under review — search icon
- Verified — check icon
- Assigned — arrow icon
- In progress — activity icon
- Resolution under review — document/search icon
- Resolved — check icon
- Disputed — alert icon
- Closed — lock/check icon

## 6. Citizen screens

### Report screen

Show category, description, location, image, privacy note, and submit action. Clearly mark optional fields.

### Tracking screen

Show reference number, current status, last update, next expected step, responsible institution where appropriate, and dispute action.

### Dispute screen

Ask for a reason and optional supporting evidence. Explain that the dispute sends the case to human review.

## 7. Moderator workspace

Use three columns on desktop:

1. Original evidence and report details.
2. Nearby reports, history, and operational context.
3. Decision controls and required reason.

On mobile, stack these sections in the same order. Never hide the original report behind an AI summary.

## 8. Institution workspace

Show assigned incident, location, reports linked to the incident, due date, current status, progress history, evidence requirements, and dispute state.

## 9. Content rules

Use plain language. Prefer “More information is needed” over “Invalid user.” Prefer “Evidence inconsistency detected” over “Fraud detected.” State when a decision was made by a human reviewer.

## 10. Accessibility acceptance

The interface must support keyboard navigation, visible focus, accessible labels, adequate contrast, readable error messages, screen-reader-friendly status text, and a list alternative to map-only information.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
