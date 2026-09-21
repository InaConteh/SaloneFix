from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentLinkReport, IncidentStatusUpdate, IncidentPublicMapItem
from app.models.entities import User, Incident, Assignment, Report, ReportIncidentLink
from app.models.enums import UserRole, IncidentStatus
from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import PageParams, page_params, paginate
from app.services.incident_service import create_incident, link_report_to_incident, transition_incident_status, get_incident_detail

router = APIRouter()


@router.post("", response_model=IncidentOut)
def create_new_incident(
    incident_in: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    incident = create_incident(db, incident_in, current_user, request_id=request_id)
    return get_incident_detail(db, incident.id, current_user)


@router.get("/public/map", response_model=List[IncidentPublicMapItem])
def get_public_incidents_map(
    db: Session = Depends(get_db),
):
    """
    Public safe map view (TC-015):
    Coordinates are generalized to 2 decimal places (~1.1 km) to protect privacy.
    """
    incidents = db.query(Incident).filter(
        Incident.lifecycle_status != IncidentStatus.CLOSED
    ).limit(100).all()

    items = []
    for inc in incidents:
        approx_lat = round(inc.centroid_latitude, 2) if inc.centroid_latitude is not None else None
        approx_lon = round(inc.centroid_longitude, 2) if inc.centroid_longitude is not None else None
        items.append(
            IncidentPublicMapItem(
                id=inc.id,
                category_name=inc.category.name if inc.category else None,
                title=inc.title,
                lifecycle_status=inc.lifecycle_status,
                approx_latitude=approx_lat,
                approx_longitude=approx_lon,
                created_at=inc.created_at,
            )
        )
    return items


@router.get("", response_model=List[IncidentOut])
def list_incidents(
    response: Response,
    status: Optional[IncidentStatus] = None,
    page: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.lifecycle_status == status)

    if current_user.role == UserRole.OFFICER:
        # Officers see only incidents assigned to their institution (none if unaffiliated).
        query = query.join(Assignment).filter(Assignment.institution_id == current_user.institution_id).distinct()
    elif current_user.role == UserRole.CITIZEN:
        # Citizens see only incidents linked to a report they submitted.
        query = (
            query.join(ReportIncidentLink, ReportIncidentLink.incident_id == Incident.id)
            .join(Report, Report.id == ReportIncidentLink.report_id)
            .filter(Report.reporter_id == current_user.id)
            .distinct()
        )

    incidents = paginate(query.order_by(Incident.created_at.desc()), page, response)
    return [get_incident_detail(db, inc.id, current_user) for inc in incidents]


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_incident_detail(db, incident_id, current_user)


@router.post("/{incident_id}/reports", response_model=IncidentOut)
def link_report(
    incident_id: str,
    link_in: IncidentLinkReport,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    link_report_to_incident(db, incident_id, link_in.report_id, current_user, notes=link_in.notes, request_id=request_id)
    return get_incident_detail(db, incident_id, current_user)


@router.patch("/{incident_id}/status", response_model=IncidentOut)
def update_status(
    incident_id: str,
    status_in: IncidentStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.OFFICER, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    transition_incident_status(db, incident_id, status_in.status, status_in.reason, current_user, request_id=request_id)
    return get_incident_detail(db, incident_id, current_user)
