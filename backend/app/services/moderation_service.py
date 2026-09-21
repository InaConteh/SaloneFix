import math
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import Report, Incident, ModerationDecision, ReportIncidentLink, User, ServiceCategory
from app.models.enums import ReportStatus, ModerationDecisionType, IncidentStatus, IncidentPriority, UserRole
from app.schemas.moderation import ModerationDecisionCreate, ModerationQueueItem
from app.schemas.report import ReportOut, MediaAssetOut
from app.core.exceptions import NotFoundError, ValidationError, StateConflictError
from app.services.audit_service import record_audit_event
from app.services.notification_service import notify_reporter
from app.services.media_links import media_asset_out


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula to compute distance between two coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def moderation_queue_query(db: Session, category_code: Optional[str] = None):
    """Base query for reports awaiting human review (oldest first)."""
    query = db.query(Report).filter(
        Report.current_status.in_([ReportStatus.SUBMITTED, ReportStatus.NEEDS_CLARIFICATION, ReportStatus.UNDER_REVIEW])
    )
    if category_code:
        query = query.join(ServiceCategory).filter(ServiceCategory.code == category_code)
    return query.order_by(Report.submitted_at.asc())


def get_moderation_queue(
    db: Session,
    category_code: Optional[str] = None,
    reports: Optional[List[Report]] = None,
) -> List[ModerationQueueItem]:
    """Build queue items (with nearby contextual reports) for the given page of reports."""
    if reports is None:
        reports = moderation_queue_query(db, category_code).all()
    queue_items = []

    for r in reports:
        # Find nearby reports if location exists
        nearby: List[Report] = []
        if r.latitude and r.longitude:
            all_with_coords = db.query(Report).filter(
                Report.id != r.id,
                Report.latitude.isnot(None),
                Report.longitude.isnot(None)
            ).all()
            for other in all_with_coords:
                dist = calculate_distance_km(r.latitude, r.longitude, other.latitude, other.longitude)
                if dist <= 2.0:  # within 2 km radius
                    nearby.append(other)

        def to_out(item: Report) -> ReportOut:
            return ReportOut(
                id=item.id,
                tracking_reference=item.tracking_reference,
                reporter_id=item.reporter_id,
                category_id=item.category_id,
                category_code=item.category.code if item.category else None,
                category_name=item.category.name if item.category else None,
                description=item.description,
                latitude=item.latitude,
                longitude=item.longitude,
                location_precision=item.location_precision,
                submitted_at=item.submitted_at,
                current_status=item.current_status,
                source_channel=item.source_channel,
                clarification_notes=item.clarification_notes,
                media_assets=[
                    media_asset_out(m)
                    for m in item.media_assets
                ],
            )

        queue_items.append(
            ModerationQueueItem(
                report=to_out(r),
                nearby_reports=[to_out(n) for n in nearby[:5]],
            )
        )

    return queue_items


def process_moderation_decision(
    db: Session,
    report_id: str,
    decision_in: ModerationDecisionCreate,
    moderator: User,
    request_id: Optional[str] = None,
) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise NotFoundError("Report")

    old_status = report.current_status
    target_incident_id = None

    if decision_in.decision == ModerationDecisionType.VERIFY:
        report.current_status = ReportStatus.VERIFIED
        notification_title = "Report verified"
        notification_message = f"Your report {report.tracking_reference} has been verified and is ready for incident assignment."
    elif decision_in.decision == ModerationDecisionType.NEEDS_CLARIFICATION:
        report.current_status = ReportStatus.NEEDS_CLARIFICATION
        report.clarification_notes = decision_in.reason
        notification_title = "Clarification requested"
        notification_message = f"A moderator needs more detail for report {report.tracking_reference}."
    elif decision_in.decision == ModerationDecisionType.REJECT:
        report.current_status = ReportStatus.REJECTED
        notification_title = "Report reviewed"
        notification_message = f"Your report {report.tracking_reference} has been reviewed and closed by a moderator."
    elif decision_in.decision == ModerationDecisionType.ESCALATE:
        report.current_status = ReportStatus.ESCALATED
        notification_title = "Report escalated"
        notification_message = f"Your report {report.tracking_reference} has been escalated for senior human review."
    elif decision_in.decision == ModerationDecisionType.MERGE:
        if not decision_in.target_incident_id:
            raise ValidationError("target_incident_id is required when merging a report.")
        incident = db.query(Incident).filter(Incident.id == decision_in.target_incident_id).first()
        if not incident:
            raise NotFoundError("Target incident")
        target_incident_id = incident.id
        report.current_status = ReportStatus.MERGED

        # Create link
        existing_link = db.query(ReportIncidentLink).filter(
            ReportIncidentLink.report_id == report.id,
            ReportIncidentLink.incident_id == incident.id,
        ).first()
        if not existing_link:
            link = ReportIncidentLink(
                report_id=report.id,
                incident_id=incident.id,
                linked_by=moderator.id,
                notes=decision_in.reason,
            )
            db.add(link)
        notification_title = "Report linked to case"
        notification_message = f"Your report {report.tracking_reference} has been linked to an existing incident case."

    # Record decision object
    dec = ModerationDecision(
        report_id=report.id,
        incident_id=target_incident_id,
        moderator_id=moderator.id,
        decision=decision_in.decision,
        reason=decision_in.reason,
    )
    db.add(dec)

    # Record audit event
    record_audit_event(
        db=db,
        entity_type="REPORT",
        entity_id=report.id,
        action=f"MODERATION_{decision_in.decision.value}",
        actor_id=moderator.id,
        previous_value={"status": old_status.value},
        new_value={"status": report.current_status.value, "decision": decision_in.decision.value},
        reason=decision_in.reason,
        request_id=request_id,
    )
    notify_reporter(db, report, notification_title, notification_message)

    db.commit()
    db.refresh(report)
    return report
