from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.audit import AuditEventOut
from app.models.entities import Assignment, AuditEvent, User, Incident, ReportIncidentLink
from app.models.enums import UserRole
from app.core.dependencies import require_roles
from app.core.pagination import PageParams, page_params, paginate
from app.services.audit_service import record_audit_event

router = APIRouter()


@router.get("/incidents/{incident_id}/audit", response_model=List[AuditEventOut])
def get_incident_audit(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.AUDITOR, UserRole.ADMIN, UserRole.MODERATOR])),
    request: Request = None,
):
    request_id = request.headers.get("X-Request-ID") if request is not None else None
    # Log the audit access event (Section 6: Audit access is restricted and itself logged)
    record_audit_event(
        db=db,
        entity_type="AUDIT",
        entity_id=incident_id,
        action="AUDIT_ACCESSED",
        actor_id=current_user.id,
        previous_value=None,
        new_value={"incident_id": incident_id, "role": current_user.role.value},
        reason="Incident audit trail inspected by authorized user",
        request_id=request_id,
    )
    db.commit()
    # Find all linked reports to gather their IDs as well
    linked_report_ids = [
        link.report_id
        for link in db.query(ReportIncidentLink).filter(ReportIncidentLink.incident_id == incident_id).all()
    ]
    assignment_ids = [
        assignment.id
        for assignment in db.query(Assignment).filter(Assignment.incident_id == incident_id).all()
    ]

    events = db.query(AuditEvent).filter(
        (
            (AuditEvent.entity_type == "INCIDENT") & (AuditEvent.entity_id == incident_id)
        ) | (
            (AuditEvent.entity_type == "REPORT") & (AuditEvent.entity_id.in_(linked_report_ids))
        ) | (
            (AuditEvent.entity_type == "ASSIGNMENT") & (AuditEvent.entity_id.in_(assignment_ids))
        )
    ).order_by(AuditEvent.created_at.asc()).all()

    results = []
    for ev in events:
        actor = db.query(User).filter(User.id == ev.actor_id).first() if ev.actor_id else None
        results.append(
            AuditEventOut(
                id=ev.id,
                actor_id=ev.actor_id,
                actor_name=actor.name_or_alias if actor else "System",
                actor_role=actor.role.value if actor else None,
                entity_type=ev.entity_type,
                entity_id=ev.entity_id,
                action=ev.action,
                previous_value=ev.previous_value,
                new_value=ev.new_value,
                reason=ev.reason,
                request_id=ev.request_id,
                created_at=ev.created_at,
            )
        )
    return results


@router.get("/events", response_model=List[AuditEventOut])
def get_all_audit_events(
    response: Response,
    page: PageParams = Depends(page_params),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.AUDITOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID") if request else None
    record_audit_event(
        db=db,
        entity_type="AUDIT",
        entity_id="ALL",
        action="AUDIT_ACCESSED",
        actor_id=current_user.id,
        previous_value=None,
        new_value={"limit": page.limit, "offset": page.offset, "role": current_user.role.value},
        reason="System auditor inspected global audit trail",
        request_id=request_id,
    )
    db.commit()
    query = db.query(AuditEvent)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type.upper())
    if action:
        query = query.filter(AuditEvent.action == action.upper())
    events = paginate(query.order_by(AuditEvent.created_at.desc()), page, response)
    results = []
    for ev in events:
        actor = db.query(User).filter(User.id == ev.actor_id).first() if ev.actor_id else None
        results.append(
            AuditEventOut(
                id=ev.id,
                actor_id=ev.actor_id,
                actor_name=actor.name_or_alias if actor else "System",
                actor_role=actor.role.value if actor else None,
                entity_type=ev.entity_type,
                entity_id=ev.entity_id,
                action=ev.action,
                previous_value=ev.previous_value,
                new_value=ev.new_value,
                reason=ev.reason,
                request_id=ev.request_id,
                created_at=ev.created_at,
            )
        )
    return results
