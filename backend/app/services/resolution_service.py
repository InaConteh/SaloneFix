from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.entities import Incident, ResolutionEvidence, Dispute, MediaAsset, ReportIncidentLink, Report, User
from app.models.enums import IncidentStatus, EvidenceReviewStatus, DisputeStatus, UserRole
from app.schemas.resolution import ResolutionEvidenceCreate, ResolutionReviewCreate, DisputeCreate, ReopenRequest
from app.schemas.report import MediaAssetOut
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError, StateConflictError
from app.services.audit_service import record_audit_event
from app.services.incident_service import require_officer_assigned_to_incident
from app.services.notification_service import notify_incident_reporters, notify_institution_officers, notify_roles


def submit_resolution_evidence(
    db: Session,
    incident_id: str,
    evidence_in: ResolutionEvidenceCreate,
    uploader: User,
    request_id: Optional[str] = None,
) -> ResolutionEvidence:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    if uploader.role == UserRole.OFFICER:
        require_officer_assigned_to_incident(db, incident, uploader)

    if incident.lifecycle_status not in [IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLUTION_UNDER_REVIEW]:
        raise StateConflictError(
            f"Resolution evidence can only be submitted for incidents in IN_PROGRESS or RESOLUTION_UNDER_REVIEW status."
        )

    evidence = ResolutionEvidence(
        incident_id=incident.id,
        uploader_id=uploader.id,
        description=evidence_in.description.strip(),
        review_status=EvidenceReviewStatus.PENDING,
    )
    db.add(evidence)
    db.flush()

    old_status = incident.lifecycle_status
    incident.lifecycle_status = IncidentStatus.RESOLUTION_UNDER_REVIEW

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="RESOLUTION_EVIDENCE_SUBMITTED",
        actor_id=uploader.id,
        previous_value={"status": old_status.value},
        new_value={"status": incident.lifecycle_status.value, "evidence_id": evidence.id},
        reason="Institutional officer submitted resolution evidence for verification",
        request_id=request_id,
    )
    notify_roles(
        db=db,
        roles=[UserRole.MODERATOR, UserRole.ADMIN],
        title="Resolution evidence submitted",
        message=f"Incident case {incident.title} is ready for human review.",
        entity_type="INCIDENT",
        entity_id=incident.id,
    )
    notify_incident_reporters(
        db=db,
        incident=incident,
        title="Resolution under review",
        message=f"Resolution evidence for incident case {incident.title} has been submitted for human review.",
    )

    db.commit()
    db.refresh(evidence)
    return evidence


def review_resolution_evidence(
    db: Session,
    incident_id: str,
    review_in: ResolutionReviewCreate,
    reviewer: User,
    request_id: Optional[str] = None,
) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    # Get latest pending evidence
    evidence = db.query(ResolutionEvidence).filter(
        ResolutionEvidence.incident_id == incident.id,
        ResolutionEvidence.review_status == EvidenceReviewStatus.PENDING,
    ).order_by(ResolutionEvidence.submitted_at.desc()).first()

    if not evidence:
        # Fallback to latest evidence
        evidence = db.query(ResolutionEvidence).filter(
            ResolutionEvidence.incident_id == incident.id
        ).order_by(ResolutionEvidence.submitted_at.desc()).first()
        if not evidence:
            raise ValidationError("No resolution evidence found for this incident.")

    if review_in.decision == EvidenceReviewStatus.APPROVED:
        requires_media = bool(incident.category and incident.category.requires_resolution_evidence)
        if requires_media and not evidence.media_assets:
            raise StateConflictError(
                "This category requires photo evidence before a resolution can be approved. "
                "Ask the assigned officer to attach at least one image to the evidence record.",
                details={"evidence_id": evidence.id, "category": incident.category.code},
            )

    evidence.review_status = review_in.decision
    evidence.reviewer_id = reviewer.id
    evidence.review_reason = review_in.reason
    evidence.reviewed_at = datetime.utcnow()

    old_status = incident.lifecycle_status
    if review_in.decision == EvidenceReviewStatus.APPROVED:
        incident.lifecycle_status = IncidentStatus.RESOLVED
    else:
        incident.lifecycle_status = IncidentStatus.IN_PROGRESS

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action=f"RESOLUTION_{review_in.decision.value}",
        actor_id=reviewer.id,
        previous_value={"status": old_status.value},
        new_value={"status": incident.lifecycle_status.value, "decision": review_in.decision.value},
        reason=review_in.reason,
        request_id=request_id,
    )
    if review_in.decision == EvidenceReviewStatus.APPROVED:
        notify_incident_reporters(
            db=db,
            incident=incident,
            title="Incident resolved",
            message=f"Incident case {incident.title} has been marked resolved after human evidence review.",
        )
    else:
        assignment = incident.assignments[-1] if incident.assignments else None
        if assignment:
            notify_institution_officers(
                db=db,
                institution_id=assignment.institution_id,
                officer_id=assignment.officer_id,
                title="Resolution evidence needs revision",
                message=f"Incident case {incident.title} needs more work before it can be resolved.",
                entity_type="INCIDENT",
                entity_id=incident.id,
            )

    db.commit()
    db.refresh(incident)
    return incident


def dispute_resolution(
    db: Session,
    incident_id: str,
    dispute_in: DisputeCreate,
    reporter: User,
    request_id: Optional[str] = None,
) -> Dispute:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    if incident.lifecycle_status != IncidentStatus.RESOLVED:
        raise StateConflictError("Disputes can only be filed against incidents in RESOLVED status.")

    # Check that reporter has a linked report or is citizen
    linked = db.query(ReportIncidentLink).join(Report).filter(
        ReportIncidentLink.incident_id == incident.id,
        Report.reporter_id == reporter.id,
    ).first()

    if reporter.role == UserRole.CITIZEN and not linked:
        # If citizen, ensure they submitted one of the reports
        raise ForbiddenError("You can only dispute resolutions for incidents linked to your reports.")

    dispute = Dispute(
        incident_id=incident.id,
        reporter_id=reporter.id,
        reason=dispute_in.reason.strip(),
        status=DisputeStatus.SUBMITTED,
    )
    db.add(dispute)

    old_status = incident.lifecycle_status
    incident.lifecycle_status = IncidentStatus.DISPUTED

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="RESOLUTION_DISPUTED",
        actor_id=reporter.id,
        previous_value={"status": old_status.value},
        new_value={"status": incident.lifecycle_status.value, "dispute_id": dispute.id},
        reason=dispute_in.reason,
        request_id=request_id,
    )
    notify_roles(
        db=db,
        roles=[UserRole.MODERATOR, UserRole.ADMIN],
        title="Resolution disputed",
        message=f"A citizen disputed incident case {incident.title}; independent review is required.",
        entity_type="INCIDENT",
        entity_id=incident.id,
    )

    db.commit()
    db.refresh(dispute)
    return dispute


def reopen_incident(
    db: Session,
    incident_id: str,
    reopen_in: ReopenRequest,
    reviewer: User,
    request_id: Optional[str] = None,
) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    if incident.lifecycle_status not in [IncidentStatus.DISPUTED, IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
        raise StateConflictError(f"Incident in {incident.lifecycle_status.value} status cannot be reopened.")

    old_status = incident.lifecycle_status
    incident.lifecycle_status = IncidentStatus.RESOLUTION_UNDER_REVIEW

    # Update active dispute status if present
    active_dispute = db.query(Dispute).filter(
        Dispute.incident_id == incident.id,
        Dispute.status == DisputeStatus.SUBMITTED,
    ).first()
    if active_dispute:
        active_dispute.status = DisputeStatus.ACCEPTED
        active_dispute.resolved_at = datetime.utcnow()

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="INCIDENT_REOPENED",
        actor_id=reviewer.id,
        previous_value={"status": old_status.value},
        new_value={"status": incident.lifecycle_status.value},
        reason=reopen_in.reason,
        request_id=request_id,
    )
    notify_incident_reporters(
        db=db,
        incident=incident,
        title="Incident reopened",
        message=f"Incident case {incident.title} has been reopened for further human review.",
    )

    db.commit()
    db.refresh(incident)
    return incident


def attach_evidence_media(
    db: Session,
    incident_id: str,
    evidence_id: str,
    uploader: User,
    sanitized_bytes: bytes,
    filename: str,
    mime_type: str,
    idempotency_key: Optional[str] = None,
    request_id: Optional[str] = None,
) -> MediaAsset:
    """Attach a sanitized image to a pending evidence record.

    Only the uploader of the evidence (or an admin) may add media, and only while
    the evidence is still PENDING — reviewed evidence is immutable.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")
    evidence = db.query(ResolutionEvidence).filter(
        ResolutionEvidence.id == evidence_id,
        ResolutionEvidence.incident_id == incident.id,
    ).first()
    if not evidence:
        raise NotFoundError("Resolution evidence")

    if uploader.role == UserRole.OFFICER:
        require_officer_assigned_to_incident(db, incident, uploader)
        if evidence.uploader_id != uploader.id:
            raise ForbiddenError("Only the officer who submitted this evidence can attach media to it.")

    if evidence.review_status != EvidenceReviewStatus.PENDING:
        raise StateConflictError("Media cannot be added to evidence that has already been reviewed.")

    if idempotency_key:
        existing = db.query(MediaAsset).filter(
            MediaAsset.evidence_id == evidence.id,
            MediaAsset.idempotency_key == idempotency_key,
        ).first()
        if existing:
            return existing

    from app.services.storage import save_media_file

    storage_key, sha256_hash, file_size = save_media_file(sanitized_bytes, filename)
    asset = MediaAsset(
        evidence_id=evidence.id,
        storage_key=storage_key,
        original_filename=filename,
        mime_type=mime_type,
        file_size=file_size,
        sha256_hash=sha256_hash,
        metadata_status="SANITIZED",
        idempotency_key=idempotency_key,
    )
    db.add(asset)
    db.flush()

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="RESOLUTION_EVIDENCE_MEDIA_ATTACHED",
        actor_id=uploader.id,
        previous_value=None,
        new_value={"evidence_id": evidence.id, "media_asset_id": asset.id, "sha256": sha256_hash},
        reason="Officer attached photo evidence to resolution record",
        request_id=request_id,
    )
    db.commit()
    db.refresh(asset)
    return asset
