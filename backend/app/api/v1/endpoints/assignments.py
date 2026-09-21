from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.assignment import AssignmentCreate, AssignmentOut, AssignmentStatusUpdate
from app.models.entities import User, Assignment
from app.models.enums import UserRole
from app.core.dependencies import require_roles
from app.services.assignment_service import assign_incident, update_assignment_status

router = APIRouter()


@router.post("/incidents/{incident_id}/assignments", response_model=AssignmentOut)
def create_assignment(
    incident_id: str,
    assign_in: AssignmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    assignment = assign_incident(db, incident_id, assign_in, current_user, request_id=request_id)
    return AssignmentOut(
        id=assignment.id,
        incident_id=assignment.incident_id,
        institution_id=assignment.institution_id,
        institution_name=assignment.institution.name if assignment.institution else None,
        officer_id=assignment.officer_id,
        officer_name=assignment.officer.name_or_alias if assignment.officer else None,
        assigned_by=assignment.assigned_by,
        assigned_at=assignment.assigned_at,
        due_at=assignment.due_at,
        accepted_at=assignment.accepted_at,
        declined_at=assignment.declined_at,
        decline_reason=assignment.decline_reason,
        status=assignment.status,
    )


@router.patch("/assignments/{assignment_id}/status", response_model=AssignmentOut)
def respond_to_assignment(
    assignment_id: str,
    status_update: AssignmentStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.OFFICER, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    assignment = update_assignment_status(db, assignment_id, status_update, current_user, request_id=request_id)
    return AssignmentOut(
        id=assignment.id,
        incident_id=assignment.incident_id,
        institution_id=assignment.institution_id,
        institution_name=assignment.institution.name if assignment.institution else None,
        officer_id=assignment.officer_id,
        officer_name=assignment.officer.name_or_alias if assignment.officer else None,
        assigned_by=assignment.assigned_by,
        assigned_at=assignment.assigned_at,
        due_at=assignment.due_at,
        accepted_at=assignment.accepted_at,
        declined_at=assignment.declined_at,
        decline_reason=assignment.decline_reason,
        status=assignment.status,
    )
