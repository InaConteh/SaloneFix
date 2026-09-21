from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.resolution import (
    ResolutionEvidenceCreate,
    ResolutionEvidenceOut,
    ResolutionReviewCreate,
    DisputeCreate,
    DisputeOut,
    ReopenRequest,
)
from app.schemas.incident import IncidentOut
from app.schemas.report import MediaAssetOut
from app.models.entities import User
from app.models.enums import UserRole
from app.core.dependencies import get_current_user, require_roles
from app.services.resolution_service import (
    submit_resolution_evidence,
    review_resolution_evidence,
    dispute_resolution,
    reopen_incident,
    attach_evidence_media,
)
from app.services.incident_service import get_incident_detail, evidence_to_out
from app.services.media_processor import validate_and_sanitize_image
from app.services.media_links import media_asset_out

router = APIRouter()


@router.post("/incidents/{incident_id}/resolution-evidence", response_model=ResolutionEvidenceOut)
def submit_evidence(
    incident_id: str,
    evidence_in: ResolutionEvidenceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.OFFICER, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    evidence = submit_resolution_evidence(db, incident_id, evidence_in, current_user, request_id=request_id)
    return evidence_to_out(evidence)


@router.post("/incidents/{incident_id}/resolution-evidence/{evidence_id}/media", response_model=MediaAssetOut)
async def upload_evidence_media(
    incident_id: str,
    evidence_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.OFFICER, UserRole.ADMIN])),
):
    raw_bytes = await file.read()
    sanitized_bytes, output_mime, filename = validate_and_sanitize_image(
        file_bytes=raw_bytes,
        filename=file.filename or "evidence.jpg",
        mime_type=file.content_type or "image/jpeg",
    )
    asset = attach_evidence_media(
        db,
        incident_id,
        evidence_id,
        current_user,
        sanitized_bytes=sanitized_bytes,
        filename=filename,
        mime_type=output_mime,
        idempotency_key=request.headers.get("Idempotency-Key"),
        request_id=request.headers.get("X-Request-ID"),
    )
    return media_asset_out(asset)


@router.post("/incidents/{incident_id}/resolution-review", response_model=IncidentOut)
def review_evidence(
    incident_id: str,
    review_in: ResolutionReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    review_resolution_evidence(db, incident_id, review_in, current_user, request_id=request_id)
    return get_incident_detail(db, incident_id, current_user)


@router.post("/incidents/{incident_id}/disputes", response_model=DisputeOut)
def dispute(
    incident_id: str,
    dispute_in: DisputeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request_id = request.headers.get("X-Request-ID")
    disp = dispute_resolution(db, incident_id, dispute_in, current_user, request_id=request_id)
    return DisputeOut(
        id=disp.id,
        incident_id=disp.incident_id,
        reporter_id=disp.reporter_id,
        reason=disp.reason,
        status=disp.status,
        created_at=disp.created_at,
        resolved_at=disp.resolved_at,
    )


@router.post("/incidents/{incident_id}/reopen", response_model=IncidentOut)
def reopen(
    incident_id: str,
    reopen_in: ReopenRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MODERATOR, UserRole.ADMIN])),
):
    request_id = request.headers.get("X-Request-ID")
    reopen_incident(db, incident_id, reopen_in, current_user, request_id=request_id)
    return get_incident_detail(db, incident_id, current_user)
