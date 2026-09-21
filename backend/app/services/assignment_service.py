from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.entities import Assignment, Incident, Institution, User
from app.models.enums import AssignmentStatus, IncidentStatus, UserRole
from app.schemas.assignment import AssignmentCreate, AssignmentOut, AssignmentStatusUpdate
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError, StateConflictError
from app.services.audit_service import record_audit_event
from app.services.notification_service import notify_incident_reporters, notify_institution_officers, notify_roles


def assign_incident(
    db: Session,
    incident_id: str,
    assign_in: AssignmentCreate,
    assigner: User,
    request_id: Optional[str] = None,
) -> Assignment:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise NotFoundError("Incident")

    institution = db.query(Institution).filter(Institution.id == assign_in.institution_id).first()
    if not institution:
        raise NotFoundError("Institution")

    officer = None
    if assign_in.officer_id:
        officer = db.query(User).filter(User.id == assign_in.officer_id).first()
        if not officer:
            raise NotFoundError("Officer")
        if officer.institution_id != institution.id:
            raise ValidationError("Assigned officer does not belong to the designated institution.")

    assignment = Assignment(
        incident_id=incident.id,
        institution_id=institution.id,
        officer_id=officer.id if officer else None,
        assigned_by=assigner.id,
        due_at=assign_in.due_at,
        status=AssignmentStatus.ASSIGNED,
    )
    db.add(assignment)

    # Automatically transition incident to ASSIGNED if currently VERIFIED
    old_status = incident.lifecycle_status
    # VERIFIED -> ASSIGNED on first assignment; ESCALATED -> ASSIGNED on reassignment
    # (both allowed by workflow-specification §3). Other states keep their status.
    if incident.lifecycle_status in (IncidentStatus.VERIFIED, IncidentStatus.ESCALATED):
        incident.lifecycle_status = IncidentStatus.ASSIGNED

    record_audit_event(
        db=db,
        entity_type="INCIDENT",
        entity_id=incident.id,
        action="INCIDENT_ASSIGNED",
        actor_id=assigner.id,
        previous_value={"status": old_status.value},
        new_value={"status": incident.lifecycle_status.value, "institution": institution.name, "officer_id": officer.id if officer else None},
        reason=f"Assigned to {institution.name}",
        request_id=request_id,
    )
    notify_institution_officers(
        db=db,
        institution_id=institution.id,
        officer_id=officer.id if officer else None,
        title="New incident assignment",
        message=f"Incident case {incident.title} has been assigned to {institution.name}.",
        entity_type="INCIDENT",
        entity_id=incident.id,
    )
    notify_incident_reporters(
        db=db,
        incident=incident,
        title="Incident assigned",
        message=f"Incident case {incident.title} has been assigned to {institution.name}.",
    )

    db.commit()
    db.refresh(assignment)
    return assignment


def update_assignment_status(
    db: Session,
    assignment_id: str,
    status_update: AssignmentStatusUpdate,
    officer: User,
    request_id: Optional[str] = None,
) -> Assignment:
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise NotFoundError("Assignment")

    if status_update.status == AssignmentStatus.ASSIGNED:
        raise ValidationError("Assignment response must be ACCEPTED or DECLINED.")

    if officer.role == UserRole.OFFICER:
        if not officer.institution_id or assignment.institution_id != officer.institution_id:
            raise ForbiddenError("You can only respond to assignments for your institution.")
        if assignment.officer_id and assignment.officer_id != officer.id:
            raise ForbiddenError("This assignment is reserved for another officer.")

    if assignment.status != AssignmentStatus.ASSIGNED:
        raise StateConflictError(f"Assignment has already been {assignment.status.value}.")

    old_assignment_status = assignment.status
    old_incident_status = assignment.incident.lifecycle_status
    if status_update.status == AssignmentStatus.ACCEPTED:
        assignment.status = AssignmentStatus.ACCEPTED
        assignment.accepted_at = datetime.utcnow()
        # Advance incident to IN_PROGRESS
        if assignment.incident.lifecycle_status == IncidentStatus.ASSIGNED:
            assignment.incident.lifecycle_status = IncidentStatus.IN_PROGRESS
    elif status_update.status == AssignmentStatus.DECLINED:
        if not status_update.decline_reason:
            raise ValidationError("Decline reason is mandatory when declining an assignment.")
        assignment.status = AssignmentStatus.DECLINED
        assignment.declined_at = datetime.utcnow()
        assignment.decline_reason = status_update.decline_reason

    record_audit_event(
        db=db,
        entity_type="ASSIGNMENT",
        entity_id=assignment.id,
        action=f"ASSIGNMENT_{status_update.status.value}",
        actor_id=officer.id,
        previous_value={"status": old_assignment_status.value},
        new_value={"status": status_update.status.value, "reason": status_update.decline_reason},
        reason=status_update.decline_reason or f"Assignment {status_update.status.value}",
        request_id=request_id,
    )
    if old_incident_status != assignment.incident.lifecycle_status:
        record_audit_event(
            db=db,
            entity_type="INCIDENT",
            entity_id=assignment.incident.id,
            action=f"INCIDENT_STATUS_{assignment.incident.lifecycle_status.value}",
            actor_id=officer.id,
            previous_value={"status": old_incident_status.value},
            new_value={"status": assignment.incident.lifecycle_status.value},
            reason=f"Assignment {status_update.status.value.lower()} by institution officer",
            request_id=request_id,
        )

    if status_update.status == AssignmentStatus.ACCEPTED:
        notify_incident_reporters(
            db=db,
            incident=assignment.incident,
            title="Repair work started",
            message=f"{assignment.institution.name} accepted incident case {assignment.incident.title} and work is in progress.",
        )
    else:
        notify_roles(
            db=db,
            roles=[UserRole.MODERATOR, UserRole.ADMIN],
            title="Assignment declined",
            message=f"{assignment.institution.name} declined incident case {assignment.incident.title}.",
            entity_type="INCIDENT",
            entity_id=assignment.incident.id,
        )

    db.commit()
    db.refresh(assignment)
    return assignment
