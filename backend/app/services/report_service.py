import hashlib
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.entities import Report, ServiceCategory, User, Incident, ReportIncidentLink, Assignment, Institution, ResolutionEvidence
from app.models.enums import ReportStatus, UserRole, IncidentStatus
from app.schemas.report import ReportCreate, ReportOut, ReportPublicStatus, ReportCreateResponse, MediaAssetOut
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.services.audit_service import record_audit_event
from app.services.notification_service import create_notification
from app.services.media_links import media_asset_out


def generate_tracking_reference(db: Session) -> str:
    """Generate a unique tracking reference: SF-YYYY-NNNNNN."""
    current_year = datetime.utcnow().year
    prefix = f"SF-{current_year}-"
    # Count existing reports for the current year
    count = db.query(func.count(Report.id)).filter(Report.tracking_reference.like(f"{prefix}%")).scalar() or 0
    ref_number = count + 1
    return f"{prefix}{ref_number:06d}"


def create_report(
    db: Session,
    report_in: ReportCreate,
    reporter: User,
    request_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> ReportCreateResponse:
    # 0. Idempotency Check (TC-014)
    if idempotency_key:
        existing = db.query(Report).filter(
            Report.reporter_id == reporter.id,
            Report.idempotency_key == idempotency_key,
        ).first()
        if existing:
            return ReportCreateResponse(
                id=existing.id,
                tracking_reference=existing.tracking_reference,
                status=existing.current_status,
                created_at=existing.submitted_at,
                next_step="A moderator will review the report.",
            )

    # 1. Validate category
    category = db.query(ServiceCategory).filter(
        ServiceCategory.code == report_in.category_code,
        ServiceCategory.is_active == True,
    ).first()
    if not category:
        raise ValidationError(f"Invalid or inactive category code: {report_in.category_code}")

    # 2. Canonical payload hash for audit integrity & rapid duplicate protection
    payload_dict = report_in.model_dump()
    payload_str = json.dumps(payload_dict, sort_keys=True)
    payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    # If no idempotency key was supplied, prevent rapid double-clicks (< 5s with same payload hash)
    if not idempotency_key:
        recent_duplicate = db.query(Report).filter(
            Report.reporter_id == reporter.id,
            Report.original_payload_hash == payload_hash,
        ).order_by(Report.submitted_at.desc()).first()
        if recent_duplicate and (datetime.utcnow() - recent_duplicate.submitted_at).total_seconds() < 5:
            return ReportCreateResponse(
                id=recent_duplicate.id,
                tracking_reference=recent_duplicate.tracking_reference,
                status=recent_duplicate.current_status,
                created_at=recent_duplicate.submitted_at,
                next_step="A moderator will review the report.",
            )

    # 3. Generate unique tracking reference
    tracking_ref = generate_tracking_reference(db)

    report = Report(
        tracking_reference=tracking_ref,
        reporter_id=reporter.id,
        category_id=category.id,
        description=report_in.description.strip(),
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        location_precision=report_in.location_precision,
        current_status=ReportStatus.SUBMITTED,
        source_channel=report_in.source_channel,
        idempotency_key=idempotency_key,
        original_payload_hash=payload_hash,
    )
    db.add(report)
    db.flush()

    # 4. Record audit event
    record_audit_event(
        db=db,
        entity_type="REPORT",
        entity_id=report.id,
        action="REPORT_SUBMITTED",
        actor_id=reporter.id,
        previous_value=None,
        new_value={"status": ReportStatus.SUBMITTED.value, "tracking_reference": tracking_ref},
        reason="Citizen report submitted",
        request_id=request_id,
    )
    create_notification(
        db=db,
        user_id=reporter.id,
        title="Report received",
        message=f"Your report {tracking_ref} has been received and queued for human review.",
        entity_type="REPORT",
        entity_id=report.id,
    )
    db.commit()
    db.refresh(report)

    return ReportCreateResponse(
        id=report.id,
        tracking_reference=report.tracking_reference,
        status=report.current_status,
        created_at=report.submitted_at,
        next_step="A moderator will review the report.",
    )


def get_report_detail(
    db: Session,
    report_id: str,
    current_user: User,
) -> ReportOut:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise NotFoundError("Report")

    # Object-level authorization: owner or staff roles
    if current_user.role == UserRole.CITIZEN and report.reporter_id != current_user.id:
        raise ForbiddenError("You are not authorized to view this report.")

    # Find linked incident if any
    incident_link = db.query(ReportIncidentLink).filter(ReportIncidentLink.report_id == report.id).first()
    incident_id = incident_link.incident_id if incident_link else None

    # Format media assets
    media_out = [
        media_asset_out(m)
        for m in report.media_assets
    ]

    return ReportOut(
        id=report.id,
        tracking_reference=report.tracking_reference,
        reporter_id=report.reporter_id,
        category_id=report.category_id,
        category_code=report.category.code if report.category else None,
        category_name=report.category.name if report.category else None,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        location_precision=report.location_precision,
        submitted_at=report.submitted_at,
        current_status=report.current_status,
        source_channel=report.source_channel,
        clarification_notes=report.clarification_notes,
        media_assets=media_out,
        incident_id=incident_id,
    )


def get_public_report_status(
    db: Session,
    reference_or_id: str,
) -> ReportPublicStatus:
    report = db.query(Report).filter(
        (Report.tracking_reference == reference_or_id) | (Report.id == reference_or_id)
    ).first()
    if not report:
        raise NotFoundError("Report")

    # Determine responsible institution and resolution details if linked to an incident
    assigned_inst_name = None
    incident_id = None
    can_dispute = False
    resolution_desc = None

    incident_link = db.query(ReportIncidentLink).filter(ReportIncidentLink.report_id == report.id).first()
    if incident_link:
        incident = db.query(Incident).filter(Incident.id == incident_link.incident_id).first()
        if incident:
            incident_id = incident.id
            # Check assignment
            assignment = db.query(Assignment).filter(Assignment.incident_id == incident.id).order_by(Assignment.assigned_at.desc()).first()
            if assignment and assignment.institution:
                assigned_inst_name = assignment.institution.name

            # Can dispute if incident is RESOLVED
            if incident.lifecycle_status == IncidentStatus.RESOLVED:
                can_dispute = True
                ev = db.query(ResolutionEvidence).filter(ResolutionEvidence.incident_id == incident.id).order_by(ResolutionEvidence.submitted_at.desc()).first()
                if ev:
                    resolution_desc = ev.description

    # Derive next step message based on current status
    next_step_map = {
        ReportStatus.SUBMITTED: "A moderator will review your report shortly.",
        ReportStatus.UNDER_REVIEW: "A moderator is currently assessing the report and verifying local details.",
        ReportStatus.NEEDS_CLARIFICATION: f"Clarification requested: {report.clarification_notes or 'Please provide additional details.'}",
        ReportStatus.VERIFIED: "Verified. An incident case is being assigned to the responsible institution.",
        ReportStatus.MERGED: "Linked to an existing public incident case. Updates will be tracked through the case.",
        ReportStatus.REJECTED: "Report reviewed and closed by moderator.",
        ReportStatus.ESCALATED: "Escalated for senior supervisor review.",
    }
    next_step = next_step_map.get(report.current_status, "In progress.")

    return ReportPublicStatus(
        tracking_reference=report.tracking_reference,
        current_status=report.current_status,
        category_name=report.category.name if report.category else "Public Service",
        description=report.description,
        submitted_at=report.submitted_at,
        last_update=report.submitted_at,
        next_step=next_step,
        responsible_institution=assigned_inst_name,
        can_dispute=can_dispute,
        incident_id=incident_id,
        resolution_description=resolution_desc,
    )
