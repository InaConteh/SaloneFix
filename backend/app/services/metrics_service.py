"""Human-only baseline metrics (docs/specs/09-research/evaluation-protocol.md section 4).

Phase 2 asks for a frozen human-only baseline that Phase 3 can be compared
against. This module derives that baseline from the existing domain tables.

Three properties are deliberate:

* **Read-only.** Nothing here writes to the database and nothing in a lifecycle
  transition calls it, so measuring the workflow cannot alter the workflow.
* **Honest about gaps.** Metrics that need adjudicated ground truth or a survey
  instrument are not computed. They are listed in ``unavailable_metrics`` with
  the reason, because inventing a number would break the protocol's
  interpretation rule (section 6).
* **Self-describing.** Every metric carries its definition, so a frozen snapshot
  stays readable years later without this source file.

Aggregation happens in Python rather than SQL: the per-report grouping below
(first decision per moderator per report) does not express cleanly in SQLite,
and prototype data volumes are small. Revisit if this is ever pointed at a
production-sized dataset.
"""
from datetime import datetime
from statistics import median
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import (
    Assignment,
    AuditEvent,
    Dispute,
    Incident,
    ModerationDecision,
    Report,
    ResolutionEvidence,
    User,
)
from app.models.enums import (
    AssignmentStatus,
    EvidenceReviewStatus,
    IncidentStatus,
    ModerationDecisionType,
    ReportStatus,
    UserRole,
)
from app.schemas.metrics import (
    BaselineMetricsOut,
    MetricValue,
    ModeratorWorkload,
    UnavailableMetric,
)

# A report has left the moderator's hands once it reaches one of these.
# NEEDS_CLARIFICATION is excluded on purpose: it is waiting on the citizen.
TERMINAL_REPORT_STATUSES = (
    ReportStatus.VERIFIED,
    ReportStatus.MERGED,
    ReportStatus.REJECTED,
    ReportStatus.ESCALATED,
)

# Incident states that mean a resolution outcome has been reached.
SETTLED_INCIDENT_STATUSES = (IncidentStatus.RESOLVED, IncidentStatus.CLOSED)

INTERPRETATION_NOTE = (
    "These figures describe what the humans using this system did within the selected "
    "window. They do not establish whether any individual decision was correct. Report "
    "them as evidence about precision, traceability, consistency and operational "
    "usefulness under the tested conditions only (evaluation-protocol.md section 6)."
)


def _window(query, column, start: Optional[datetime], end: Optional[datetime]):
    if start is not None:
        query = query.filter(column >= start)
    if end is not None:
        query = query.filter(column <= end)
    return query


def _ratio(key: str, label: str, numerator: int, denominator: int, definition: str) -> MetricValue:
    """A rate over an empty denominator is None, never 0.0 — absence is not zero."""
    value = round(numerator / denominator, 4) if denominator else None
    return MetricValue(
        key=key,
        label=label,
        value=value,
        unit="ratio",
        sample_size=denominator,
        definition=definition,
    )


def _median_seconds(key: str, label: str, deltas: List[float], definition: str) -> MetricValue:
    return MetricValue(
        key=key,
        label=label,
        value=round(median(deltas), 1) if deltas else None,
        unit="seconds",
        sample_size=len(deltas),
        definition=definition,
    )


def _count(key: str, label: str, total: int, population: int, definition: str) -> MetricValue:
    """A count reports the population it was drawn from, not itself: "3 overdue"
    means something different out of 4 than it does out of 400."""
    return MetricValue(
        key=key,
        label=label,
        value=float(total),
        unit="count",
        sample_size=population,
        definition=definition,
    )


def _first_decision_per_report(decisions: List[ModerationDecision]) -> Dict[str, ModerationDecision]:
    earliest: Dict[str, ModerationDecision] = {}
    for d in decisions:
        current = earliest.get(d.report_id)
        if current is None or d.created_at < current.created_at:
            earliest[d.report_id] = d
    return earliest


def _reviewer_agreement(decisions: List[ModerationDecision]) -> Tuple[int, int]:
    """(agreeing reports, double-reviewed reports).

    Only reports that two or more *distinct* moderators independently decided on
    count towards this. Each moderator contributes their earliest decision. The
    normal workflow produces one decision per report, so this sample is usually
    empty until a double-review exercise is run — which is why sample_size is
    reported alongside the value.
    """
    by_report: Dict[str, Dict[str, ModerationDecision]] = {}
    for d in decisions:
        per_moderator = by_report.setdefault(d.report_id, {})
        existing = per_moderator.get(d.moderator_id)
        if existing is None or d.created_at < existing.created_at:
            per_moderator[d.moderator_id] = d

    double_reviewed = 0
    agreeing = 0
    for per_moderator in by_report.values():
        if len(per_moderator) < 2:
            continue
        double_reviewed += 1
        if len({d.decision for d in per_moderator.values()}) == 1:
            agreeing += 1
    return agreeing, double_reviewed


def _audit_completeness(
    db: Session, start: Optional[datetime], end: Optional[datetime]
) -> Tuple[int, int]:
    """(covered material actions, total material actions).

    Each material action should have left exactly one audit event. Expectations
    are keyed by (entity_type, entity_id, action) and compared against the events
    actually present, capped per key so one event cannot cover two actions on the
    same entity.
    """
    expected: Dict[Tuple[str, str, str], int] = {}

    def expect(entity_type: str, entity_id: str, action: str) -> None:
        expected[(entity_type, entity_id, action)] = expected.get((entity_type, entity_id, action), 0) + 1

    for report in _window(db.query(Report), Report.submitted_at, start, end):
        expect("REPORT", report.id, "REPORT_SUBMITTED")

    for decision in _window(db.query(ModerationDecision), ModerationDecision.created_at, start, end):
        expect("REPORT", decision.report_id, f"MODERATION_{decision.decision.value}")

    for incident in _window(db.query(Incident), Incident.created_at, start, end):
        expect("INCIDENT", incident.id, "INCIDENT_CREATED")

    for assignment in _window(db.query(Assignment), Assignment.assigned_at, start, end):
        expect("INCIDENT", assignment.incident_id, "INCIDENT_ASSIGNED")

    for evidence in _window(db.query(ResolutionEvidence), ResolutionEvidence.submitted_at, start, end):
        expect("INCIDENT", evidence.incident_id, "RESOLUTION_EVIDENCE_SUBMITTED")

    reviewed = _window(
        db.query(ResolutionEvidence).filter(ResolutionEvidence.reviewed_at.isnot(None)),
        ResolutionEvidence.reviewed_at,
        start,
        end,
    )
    for evidence in reviewed:
        expect("INCIDENT", evidence.incident_id, f"RESOLUTION_{evidence.review_status.value}")

    for dispute in _window(db.query(Dispute), Dispute.created_at, start, end):
        expect("INCIDENT", dispute.incident_id, "RESOLUTION_DISPUTED")

    if not expected:
        return 0, 0

    observed: Dict[Tuple[str, str, str], int] = {}
    entity_ids = {entity_id for _, entity_id, _ in expected}
    for event in db.query(AuditEvent).filter(AuditEvent.entity_id.in_(entity_ids)):
        key = (event.entity_type, event.entity_id, event.action)
        observed[key] = observed.get(key, 0) + 1

    covered = sum(min(count, observed.get(key, 0)) for key, count in expected.items())
    return covered, sum(expected.values())


def _unavailable_metrics() -> List[UnavailableMetric]:
    """Protocol section 4 metrics that system data cannot supply.

    Returned explicitly rather than omitted, so a reader of a frozen baseline can
    tell the difference between "measured as zero" and "never measured".
    """
    return [
        UnavailableMetric(
            key="correct_category_rate",
            label="Correct category rate",
            reason=(
                "The database records the category a moderator chose, not the category that was "
                "correct. Scoring accuracy requires an adjudicated ground-truth label per case."
            ),
            how_to_collect=(
                "Have at least two reviewers label a sample of cases independently per "
                "evaluation-protocol.md section 3, adjudicate disagreements, and compare that "
                "label set against the recorded categories offline."
            ),
        ),
        UnavailableMetric(
            key="correct_routing_rate",
            label="Correct routing rate",
            reason=(
                "Which institution should have received a case is a judgement the system never "
                "records. Assignment decline rate is reported instead as an observed proxy; it "
                "detects routing an officer rejected, not routing that was wrong but accepted."
            ),
            how_to_collect=(
                "Label the correct responding institution per case during the same adjudication "
                "pass used for categories, then compare against the recorded assignments."
            ),
        ),
        UnavailableMetric(
            key="usability_score",
            label="Usability score",
            reason="A survey instrument result. It is not produced by using the application.",
            how_to_collect=(
                "Administer a standard usability questionnaire to each role cohort at the end of "
                "the UAT sessions and record the scores alongside this export."
            ),
        ),
    ]


def compute_baseline_metrics(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    now: Optional[datetime] = None,
) -> BaselineMetricsOut:
    """Aggregate the human-only baseline over the window [start, end] (both optional)."""
    now = now or datetime.utcnow()

    reports = _window(db.query(Report), Report.submitted_at, start, end).all()
    decisions = _window(db.query(ModerationDecision), ModerationDecision.created_at, start, end).all()
    incidents = _window(db.query(Incident), Incident.created_at, start, end).all()
    assignments = _window(db.query(Assignment), Assignment.assigned_at, start, end).all()
    evidences = _window(db.query(ResolutionEvidence), ResolutionEvidence.submitted_at, start, end).all()
    disputes = _window(db.query(Dispute), Dispute.created_at, start, end).all()

    metrics: List[MetricValue] = []

    # --- Report completion -------------------------------------------------
    completed = sum(1 for r in reports if r.current_status in TERMINAL_REPORT_STATUSES)
    metrics.append(
        _ratio(
            "report_completion_rate",
            "Report completion rate",
            completed,
            len(reports),
            "Reports submitted in the window that reached a terminal moderation outcome "
            "(VERIFIED, MERGED, REJECTED or ESCALATED), divided by all reports submitted in the "
            "window. NEEDS_CLARIFICATION counts as incomplete: it is waiting on the citizen.",
        )
    )

    # --- Moderator time ----------------------------------------------------
    submitted_at_by_report = {r.id: r.submitted_at for r in db.query(Report)}
    review_deltas: List[float] = []
    for decision in _first_decision_per_report(decisions).values():
        submitted_at = submitted_at_by_report.get(decision.report_id)
        if submitted_at is None:
            continue
        seconds = (decision.created_at - submitted_at).total_seconds()
        if seconds >= 0:
            review_deltas.append(seconds)
    metrics.append(
        _median_seconds(
            "median_review_seconds",
            "Median review time",
            review_deltas,
            "Median seconds from report submission to its first moderation decision, over "
            "decisions recorded in the window. This is queue wait plus handling time, not "
            "handling time alone: the system does not record when a moderator opened a case.",
        )
    )

    # --- Reviewer agreement ------------------------------------------------
    agreeing, double_reviewed = _reviewer_agreement(decisions)
    metrics.append(
        _ratio(
            "reviewer_agreement",
            "Reviewer agreement",
            agreeing,
            double_reviewed,
            "Of reports decided independently by two or more distinct moderators, the share where "
            "every moderator chose the same decision type. The normal workflow records one "
            "decision per report, so this is empty (sample_size 0) unless a deliberate "
            "double-review exercise was run.",
        )
    )

    # --- Moderation mix ----------------------------------------------------
    merges = sum(1 for d in decisions if d.decision == ModerationDecisionType.MERGE)
    clarifications = sum(1 for d in decisions if d.decision == ModerationDecisionType.NEEDS_CLARIFICATION)
    metrics.append(
        _ratio(
            "duplicate_identification_rate",
            "Duplicate identification rate",
            merges,
            len(decisions),
            "Share of moderation decisions in the window that merged a report into an existing "
            "incident. Measures how often moderators found duplicates, not how many existed.",
        )
    )
    metrics.append(
        _ratio(
            "clarification_rate",
            "Clarification rate",
            clarifications,
            len(decisions),
            "Share of moderation decisions in the window that sent a report back to the citizen "
            "for more detail. A proxy for how often submissions arrive unusable.",
        )
    )

    # --- Routing (proxy only) ----------------------------------------------
    answered = [a for a in assignments if a.status in (AssignmentStatus.ACCEPTED, AssignmentStatus.DECLINED)]
    declined = sum(1 for a in answered if a.status == AssignmentStatus.DECLINED)
    metrics.append(
        _ratio(
            "assignment_decline_rate",
            "Assignment decline rate (routing proxy)",
            declined,
            len(answered),
            "Share of answered assignments the receiving institution declined. An observed proxy "
            "for mis-routing: it cannot see a case routed to the wrong institution that was "
            "accepted anyway. This is not the protocol's correct routing rate.",
        )
    )

    # --- Resolution and disputes -------------------------------------------
    reviewed_evidence = [e for e in evidences if e.review_status != EvidenceReviewStatus.PENDING]
    approved = sum(1 for e in reviewed_evidence if e.review_status == EvidenceReviewStatus.APPROVED)
    metrics.append(
        _ratio(
            "resolution_evidence_agreement",
            "Resolution-evidence agreement",
            approved,
            len(reviewed_evidence),
            "Share of reviewed resolution evidence that the reviewing moderator approved, over "
            "evidence submitted in the window. Low values mean officers and reviewers disagree "
            "about what counts as proof of a fix.",
        )
    )

    incidents_with_evidence = {e.incident_id for e in evidences}
    disputed_incident_ids = {d.incident_id for d in db.query(Dispute)}
    metrics.append(
        _ratio(
            "dispute_rate",
            "Dispute rate",
            len(incidents_with_evidence & disputed_incident_ids),
            len(incidents_with_evidence),
            "Of incidents where a resolution was proposed in the window, the share a citizen "
            "disputed at any time.",
        )
    )

    # --- Audit completeness ------------------------------------------------
    covered, total_actions = _audit_completeness(db, start, end)
    metrics.append(
        _ratio(
            "audit_completeness",
            "Audit completeness",
            covered,
            total_actions,
            "Share of material actions in the window (report submission, moderation decision, "
            "incident creation, assignment, evidence submission, evidence review, dispute) that "
            "have a matching audit event. Anything below 1.0 is a defect in the audit trail.",
        )
    )

    # --- Operational context ------------------------------------------------
    created_at_by_incident = {i.id: i.created_at for i in db.query(Incident)}
    first_assignment: Dict[str, Assignment] = {}
    for assignment in assignments:
        current = first_assignment.get(assignment.incident_id)
        if current is None or assignment.assigned_at < current.assigned_at:
            first_assignment[assignment.incident_id] = assignment
    assignment_deltas: List[float] = []
    for assignment in first_assignment.values():
        created_at = created_at_by_incident.get(assignment.incident_id)
        if created_at is None:
            continue
        seconds = (assignment.assigned_at - created_at).total_seconds()
        if seconds >= 0:
            assignment_deltas.append(seconds)
    metrics.append(
        _median_seconds(
            "median_seconds_to_assignment",
            "Median time to assignment",
            assignment_deltas,
            "Median seconds from incident creation to its first assignment, over assignments made "
            "in the window.",
        )
    )

    closed = _window(db.query(Incident).filter(Incident.closed_at.isnot(None)), Incident.closed_at, start, end).all()
    closure_deltas = [
        (i.closed_at - i.created_at).total_seconds()
        for i in closed
        if (i.closed_at - i.created_at).total_seconds() >= 0
    ]
    metrics.append(
        _median_seconds(
            "median_seconds_to_closure",
            "Median time to closure",
            closure_deltas,
            "Median seconds from incident creation to closure, over incidents closed in the window.",
        )
    )

    overdue = sum(
        1
        for a in assignments
        if a.due_at is not None
        and a.due_at < now
        and a.status != AssignmentStatus.DECLINED
        and a.incident is not None
        and a.incident.lifecycle_status not in SETTLED_INCIDENT_STATUSES
    )
    metrics.append(
        _count(
            "overdue_assignments",
            "Overdue assignments",
            overdue,
            len(assignments),
            "Assignments made in the window whose due date has passed while the incident is "
            "neither resolved nor closed, and which were not declined. Nothing in the system "
            "notifies on these yet.",
        )
    )

    # --- Per-moderator workload ---------------------------------------------
    staff = {
        u.id: u
        for u in db.query(User).filter(User.role.in_([UserRole.MODERATOR, UserRole.ADMIN]))
    }
    counts: Dict[str, int] = {}
    seconds_by_moderator: Dict[str, List[float]] = {}
    for decision in decisions:
        counts[decision.moderator_id] = counts.get(decision.moderator_id, 0) + 1
        submitted_at = submitted_at_by_report.get(decision.report_id)
        if submitted_at is None:
            continue
        seconds = (decision.created_at - submitted_at).total_seconds()
        if seconds >= 0:
            seconds_by_moderator.setdefault(decision.moderator_id, []).append(seconds)

    workload: List[ModeratorWorkload] = []
    for moderator_id, decision_count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        user = staff.get(moderator_id)
        deltas = seconds_by_moderator.get(moderator_id, [])
        workload.append(
            ModeratorWorkload(
                moderator_id=moderator_id,
                name_or_alias=user.name_or_alias if user else "(account no longer a moderator)",
                decisions=decision_count,
                median_review_seconds=round(median(deltas), 1) if deltas else None,
            )
        )

    return BaselineMetricsOut(
        generated_at=now,
        window_start=start,
        window_end=end,
        phase=settings.PHASE_NAME,
        ai_enabled=settings.AI_ENABLED,
        whatsapp_enabled=settings.WHATSAPP_ENABLED,
        volumes={
            "reports_submitted": len(reports),
            "moderation_decisions": len(decisions),
            "incidents_created": len(incidents),
            "assignments_made": len(assignments),
            "resolution_evidence_submitted": len(evidences),
            "disputes_filed": len(disputes),
        },
        metrics=metrics,
        unavailable_metrics=_unavailable_metrics(),
        moderator_workload=workload,
        interpretation_note=INTERPRETATION_NOTE,
    )
