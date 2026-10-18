# Frozen baselines

Snapshots of the **human-only baseline** that Phase 3 (Hybrid Human + AI) is
measured against, per [`../specs/09-research/evaluation-protocol.md`](../specs/09-research/evaluation-protocol.md)
Stage B.

Produce one with:

```bash
cd backend && .venv/Scripts/python.exe ../scripts/freeze_baseline.py --label uat-round-1
```

Each run writes a pair of files:

| File | Purpose |
|---|---|
| `baseline-<label>.json` | Canonical machine-readable snapshot. Phase 3 compares against this. |
| `baseline-<label>.md` | Human-readable summary for the written report. |

## Rules

- **Commit the snapshots.** A frozen baseline is evidence; it is never
  recomputed later, because the data it was computed from keeps changing.
- **Never edit a snapshot by hand.** If it is wrong, fix the computation in
  `backend/app/services/metrics_service.py`, re-run, and freeze under a new label.
- The script refuses to run while `AI_ENABLED` or `WHATSAPP_ENABLED` is true. A
  baseline collected with assistance switched on is not a human-only baseline
  and would invalidate every comparison built on it.
- Three protocol metrics (correct category rate, correct routing rate, usability
  score) cannot come from system data. Every snapshot lists them under
  `unavailable_metrics` with collection instructions; record the offline results
  alongside the snapshot rather than editing them in.
