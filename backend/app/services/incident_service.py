from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.entities import Incident, Report, ReportIncidentLink, User, ServiceCategory, Assignment, Institution
from app.models.enums import IncidentStatus, IncidentPriority, ReportStatus, UserRole
from app.schemas.incident import ActiveAssignmentOut, IncidentCreate, IncidentOut, LinkedReportOut
from app.schemas.report import ReportOut, MediaAssetOut
from app.core.exceptions import NotFoundError, ValidationError, StateConflictError, ForbiddenError
from app.services.audit_service import record_audit_event
from app.services.notification_service import notify_incident_reporters
from app.services.media_links import media_asset_out
from app.schemas.resolution import ResolutionEvidenceOut, DisputeOut


def evidence_to_out(ev) -> ResolutionEvidenceOut:
    return ResolutionEvidenceOut(
        id=ev.id,
        incident_id=ev.incident_id,
        uploader_id=ev.uploader_id,
        uploader_name=ev.uploader.name_or_alias if ev.uploader else None,
        description=ev.description,
        submitted_at=ev.submitted_at,
        review_status=ev.review_status,
        reviewer_id=ev.reviewer_id,
        review_reason=ev.review_reason,
        reviewed_at=ev.reviewed_at,
        media_assets=[media_asset_out(m) for m in ev.media_assets],
    )


def recalculate_incident_centroid(db: Session, incident: Incident) -> None:
    """Recalculate centroid latitude and longitude from all linked reports with coordinates."""
    links = db.query(ReportIncidentLink).filter(ReportIncidentLink.incident_id == incident.id).all()
    coords = []
    for link in links:
        if link.report and link.report.latitude and link.report.longitude:
            coords.append((link.report.latitude, link.report.longitude))

    if coords:
        incident.centroid_latitude = sum(c[0] for c in coords) / len(coords)
        incident.centroid_longitude = sum(c[1] for c in coords) / len(coords)
    else:
        incident.centroid_latitude = None
        incident.centroid_longitude = None


def require_officer_assigned_to_incident(db: Session, incident: Incident, officer: User) -> Assignment:
    if not officer.institution_id:
        raise ForbiddenError("Officer account is not attached to an institution.")

    assignment = db.query(Assignment).filter(
        Assignment.incident_id == incident.id,
        Assignment.institution_id == officer.institution_id,
    ).order_by(Assignment.assigned_at.desc()).first()
    if not assignment:
        raise ForbiddenError("You can only act on incidents assigned to your institution.")
    if assignment.officer_id and assignment.officer_id != officer.id:
        raise ForbiddenError("This assignment is reserved for another officer.")
    return assignment


def create_incident(
    db: Session,
    incident_in: IncidentCreate,
    creator: User,
    request_id: Optional[str] = None,
) -> Incident:
    category = db.query(ServiceCategory).filter(ServiceCategory.id == incident_in.category_id).first()
    if not category:
        raise NotFoundError("Service category")

    incident = Incident(
        category_id=category.id,
        title=incident_in.title.strip(),
        summary=incident_in.summary.strip(),
        priority=incident_in.priority,
        lifecycle_status=IncidentStatus.VERIFIED,
    )
    db.add(incident)
    db.flush()

    # Link initial report if provided
    if incident_in.report_id:
        report = db.query(Report).filter(Report.id == incident_in.report_id).first()
        if report:
            link = ReportIncidentLink(
                report_id=report.id,
                incident_id=incident.id,
                linked_by=creator.id,
                notes="Initial report linked upon incident creation",
            )
            db.add(link)
            if report.latitude and report.longitude:
                incident.centroid_latitude = report.latitude
                incident.centroid_longitude = report.longitude

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="INCIDENT_CREATED",
        actor_id=creator.id,
        previous_value=None,
        new_value={"title": incident.title, "priority": incident.priority.value, "status": incident.lifecycle_status.value},
        reason="Incident case created by moderator/admin",
        request_id=request_id,
    )
    notify_incident_reporters(
        db=db,
        incident=incident,
        title="Incident case created",
        message=f"Your report has been linked to incident case {incident.title}.",
    )
    db.commit()
    db.refresh(incident)
    return incident


def link_report_to_incident(
    db: Session,
    incident_id: str,
    report_id: str,
    actor: User,
    notes: Optional[str] = None,
    request_id: Optional[str] = None,
) -> ReportIncidentLink:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise NotFoundError("Report")

    existing_link = db.query(ReportIncidentLink).filter(
        ReportIncidentLink.report_id == report.id,
        ReportIncidentLink.incident_id == incident.id,
    ).first()
    if existing_link:
        raise StateConflictError("Report is already linked to this incident.")

    link = ReportIncidentLink(
        report_id=report.id,
        incident_id=incident.id,
        linked_by=actor.id,
        notes=notes,
    )
    db.add(link)

    # If report was submitted/under_review, mark it as merged/linked
    old_report_status = report.current_status
    if report.current_status != ReportStatus.VERIFIED:
        report.current_status = ReportStatus.MERGED

    recalculate_incident_centroid(db, incident)

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="REPORT_LINKED",
        actor_id=actor.id,
        previous_value=None,
        new_value={"report_id": report.id, "tracking_reference": report.tracking_reference},
        reason=notes or "Report linked/merged to incident case",
        request_id=request_id,
    )
    notify_incident_reporters(
        db=db,
        incident=incident,
        title="Report linked to incident",
        message=f"Another citizen report has been linked to incident case {incident.title}.",
    )

    db.commit()
    return link


def transition_incident_status(
    db: Session,
    incident_id: str,
    new_status: IncidentStatus,
    reason: str,
    actor: User,
    request_id: Optional[str] = None,
) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    old_status = incident.lifecycle_status
    if actor.role == UserRole.OFFICER:
        require_officer_assigned_to_incident(db, incident, actor)

    # Enforce allowed transitions
    allowed_transitions = {
        IncidentStatus.VERIFIED: [IncidentStatus.ASSIGNED, IncidentStatus.IN_PROGRESS, IncidentStatus.CLOSED],
        IncidentStatus.ASSIGNED: [IncidentStatus.IN_PROGRESS, IncidentStatus.ESCALATED],
        IncidentStatus.IN_PROGRESS: [IncidentStatus.RESOLUTION_UNDER_REVIEW, IncidentStatus.ESCALATED],
        IncidentStatus.RESOLUTION_UNDER_REVIEW: [IncidentStatus.RESOLVED, IncidentStatus.IN_PROGRESS],
        IncidentStatus.RESOLVED: [IncidentStatus.DISPUTED, IncidentStatus.CLOSED],
        IncidentStatus.DISPUTED: [IncidentStatus.RESOLUTION_UNDER_REVIEW, IncidentStatus.IN_PROGRESS],
        IncidentStatus.ESCALATED: [IncidentStatus.ASSIGNED, IncidentStatus.IN_PROGRESS],
        IncidentStatus.CLOSED: [IncidentStatus.RESOLUTION_UNDER_REVIEW],
    }

    if new_status not in allowed_transitions.get(old_status, []):
        raise StateConflictError(
            f"Cannot transition incident from {old_status.value} to {new_status.value}. "
            f"Allowed next states: {[s.value for s in allowed_transitions.get(old_status, [])]}"
        )

    incident.lifecycle_status = new_status
    if new_status == IncidentStatus.CLOSED:
        incident.closed_at = datetime.utcnow()

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action=f"INCIDENT_STATUS_{new_status.value}",
        actor_id=actor.id,
        previous_value={"status": old_status.value},
        new_value={"status": new_status.value},
        reason=reason,
        request_id=request_id,
    )
    if new_status in [IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLVED, IncidentStatus.CLOSED, IncidentStatus.ESCALATED]:
        notify_incident_reporters(
            db=db,
            incident=incident,
            title=f"Incident {new_status.value.replace('_', ' ').title()}",
            message=f"Incident case {incident.title} is now {new_status.value.replace('_', ' ').lower()}.",
        )

    db.commit()
    db.refresh(incident)
    return incident


def citizen_linked_report_ids(db: Session, incident: Incident, citizen: User) -> set[str]:
    """IDs of the citizen's own reports that are linked to this incident."""
    rows = (
        db.query(ReportIncidentLink.report_id)
        .join(Report, Report.id == ReportIncidentLink.report_id)
        .filter(ReportIncidentLink.incident_id == incident.id, Report.reporter_id == citizen.id)
        .all()
    )
    return {r[0] for r in rows}


def get_incident_detail(db: Session, incident_id: str, current_user: User) -> IncidentOut:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    # Object-level authorization. Officers: only their institution's cases.
    # Citizens: only cases linked to a report they submitted, and even then the
    # view is redacted below (other reporters' reports, disputes and exact
    # coordinates are never exposed to another citizen).
    own_report_ids: Optional[set[str]] = None
    if current_user.role == UserRole.OFFICER:
        require_officer_assigned_to_incident(db, incident, current_user)
    elif current_user.role == UserRole.CITIZEN:
        own_report_ids = citizen_linked_report_ids(db, incident, current_user)
        if not own_report_ids:
            raise ForbiddenError("You can only view incidents linked to your own reports.")
    is_citizen = own_report_ids is not None

    # Fetch linked reports
    links = db.query(ReportIncidentLink).filter(ReportIncidentLink.incident_id == incident.id).all()
    linked_reports = []
    for link in links:
        rep = link.report
        if is_citizen and rep.id not in own_report_ids:
            continue  # another citizen's report: not visible
        linked_reports.append(
            LinkedReportOut(
                link_id=link.id,
                linked_at=link.linked_at,
                notes=link.notes,
                report=ReportOut(
                    id=rep.id,
                    tracking_reference=rep.tracking_reference,
                    reporter_id=rep.reporter_id,
                    category_id=rep.category_id,
                    category_code=rep.category.code if rep.category else None,
                    category_name=rep.category.name if rep.category else None,
                    description=rep.description,
                    latitude=rep.latitude,
                    longitude=rep.longitude,
                    location_precision=rep.location_precision,
                    submitted_at=rep.submitted_at,
                    current_status=rep.current_status,
                    source_channel=rep.source_channel,
                    clarification_notes=rep.clarification_notes,
                    media_assets=[
                        media_asset_out(m)
                        for m in rep.media_assets
                    ],
                ),
            )
        )

    # Find active assignment institution
    assigned_name = None
    assignment = db.query(Assignment).filter(Assignment.incident_id == incident.id).order_by(Assignment.assigned_at.desc()).first()
    if assignment and assignment.institution:
        assigned_name = assignment.institution.name
        active_assignment = ActiveAssignmentOut(
            id=assignment.id,
            institution_id=assignment.institution_id,
            institution_name=assignment.institution.name,
            officer_id=assignment.officer_id,
            officer_name=assignment.officer.name_or_alias if assignment.officer else None,
            status=assignment.status,
            due_at=assignment.due_at,
            accepted_at=assignment.accepted_at,
            declined_at=assignment.declined_at,
            is_overdue=bool(
                assignment.due_at
                and assignment.due_at < datetime.utcnow()
                and incident.lifecycle_status in (IncidentStatus.ASSIGNED, IncidentStatus.IN_PROGRESS)
            ),
        )
    else:
        active_assignment = None

    evidence_out = [evidence_to_out(ev) for ev in incident.resolution_evidences]
    disputes_out = [
        DisputeOut.model_validate(d)
        for d in incident.disputes
        if not is_citizen or d.reporter_id == current_user.id
    ]
    # Citizens get the same coarse location as the public map (~1 km).
    centroid_lat = incident.centroid_latitude
    centroid_lon = incident.centroid_longitude
    if is_citizen:
        centroid_lat = round(centroid_lat, 2) if centroid_lat is not None else None
        centroid_lon = round(centroid_lon, 2) if centroid_lon is not None else None

    return IncidentOut(
        id=incident.id,
        category_id=incident.category_id,
        category_name=incident.category.name if incident.category else None,
        title=incident.title,
        summary=incident.summary,
        priority=incident.priority,
        lifecycle_status=incident.lifecycle_status,
        centroid_latitude=centroid_lat,
        centroid_longitude=centroid_lon,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        closed_at=incident.closed_at,
        linked_reports_count=len(links),  # true total; the list itself may be redacted for citizens
        linked_reports=linked_reports,
        requires_resolution_evidence=bool(incident.category.requires_resolution_evidence) if incident.category else True,
        resolution_evidence=evidence_out,
        disputes=disputes_out,
        assigned_institution_name=assigned_name,
        active_assignment=active_assignment,
    )
