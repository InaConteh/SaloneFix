# AI Strategy and Build Rules

**Project:** SaloneFix  
**Current phase:** Human-First Foundation Launch  
**Next phase:** Human-Only Operational MVP and Baseline  
**Future phase:** Hybrid Human + AI Assistance  
**Scope:** Freetown public-service reporting prototype

## 1. AI is not part of the current launch dependency

The current Human-First Foundation and the Human-Only MVP must run with the AI adapter disabled. Do not add AI calls to required database transitions.

## 2. When AI may be introduced

Begin AI implementation only after:

- The human workflow passes acceptance testing.
- The human-only baseline is measured.
- The dataset and ground-truth procedure are documented.
- Privacy approval for AI data processing is available.
- The product owner defines a specific AI value hypothesis.

## 3. Hybrid AI capabilities

Introduce one capability at a time:

1. Category recommendation.
2. Text-image consistency recommendation.
3. Similar-report suggestion.
4. Evidence prioritization.
5. Resolution-evidence assistance.

## 4. AI adapter contract

```json
{
  "report_id": "uuid",
  "task": "CATEGORY_SUGGESTION",
  "model_version": "provider-model-v1",
  "result": {
    "category": "ROAD_POTHOLE",
    "confidence": 0.86,
    "signals": ["visible_road_damage"],
    "requires_human_review": true
  },
  "failure": null,
  "created_at": "timestamp"
}
```

The adapter returns a recommendation record. It does not mutate status, assignment, incident links, or resolution state.

## 5. Prompt and input rules

Treat citizen text and images as untrusted data. Do not allow report content to change system instructions. Minimize identity and exact location sent to an external provider. Record provider/model version, configuration version, time, and failure.

## 6. AI output rules

- Never write “the citizen is lying.”
- Never write “fraud detected” as an automatic outcome.
- Use “requires review” or “evidence inconsistency detected.”
- Show original evidence beside the recommendation.
- Allow the moderator to accept, correct, or ignore it.
- Log both recommendation and human decision.

## 7. Evaluation

Compare the human-only baseline against human plus AI recommendations. Measure quality, time, workload, false positives, fairness, privacy, cost, and latency. If AI does not create measurable value, do not keep it in the product.

## References

[1]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines 2.2"
[2]: https://owasp.org/www-project-application-security-verification-standard/ "OWASP Application Security Verification Standard"
[3]: https://doi.org/10.6028/NIST.AI.100-1 "NIST Artificial Intelligence Risk Management Framework"
