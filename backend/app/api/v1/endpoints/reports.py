from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Request, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.report import ReportCreate, ReportCreateResponse, ReportOut, ReportPublicStatus, MediaAssetOut
from app.models.entities import User, Report, MediaAsset
from app.models.enums import UserRole, ReportStatus
from app.core.dependencies import get_current_user, get_optional_current_user, rate_limiter
from app.core.pagination import PageParams, page_params, paginate
from app.core.exceptions import ForbiddenError, NotFoundError
from app.services.report_service import create_report, get_report_detail, get_public_report_status
from app.services.media_processor import validate_and_sanitize_image
from app.services.storage import save_media_file
from app.services.media_links import media_asset_out

router = APIRouter()


@router.post("", response_model=ReportCreateResponse)
def submit_report(
    report_in: ReportCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: bool = Depends(rate_limiter(max_requests=30, window_seconds=60)),
):
    request_id = request.headers.get("X-Request-ID")
    idempotency_key = request.headers.get("Idempotency-Key")
    return create_report(
        db,
        report_in,
        current_user,
        request_id=request_id,
        idempotency_key=idempotency_key,
    )


@router.get("", response_model=List[ReportOut])
def list_reports(
    response: Response,
    status: Optional[ReportStatus] = None,
    page: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Report)
    if current_user.role == UserRole.CITIZEN:
        query = query.filter(Report.reporter_id == current_user.id)
    if status:
        query = query.filter(Report.current_status == status)
    reports = paginate(query.order_by(Report.submitted_at.desc()), page, response)

    return [
        ReportOut(
            id=r.id,
            tracking_reference=r.tracking_reference,
            reporter_id=r.reporter_id,
            category_id=r.category_id,
            category_code=r.category.code if r.category else None,
            category_name=r.category.name if r.category else None,
            description=r.description,
            latitude=r.latitude,
            longitude=r.longitude,
            location_precision=r.location_precision,
            submitted_at=r.submitted_at,
            current_status=r.current_status,
            source_channel=r.source_channel,
            clarification_notes=r.clarification_notes,
            media_assets=[
                media_asset_out(m)
                for m in r.media_assets
            ],
        )
        for r in reports
    ]


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_report_detail(db, report_id, current_user)


@router.post("/{report_id}/media", response_model=MediaAssetOut)
async def upload_report_media(
    report_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: bool = Depends(rate_limiter(max_requests=30, window_seconds=60)),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise NotFoundError("Report")

    # Only owner or moderator can attach media
    if current_user.role == UserRole.CITIZEN and report.reporter_id != current_user.id:
        raise ForbiddenError("You can only upload media to your own report.")

    # Idempotent retry: same key on the same report returns the original asset
    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        existing = db.query(MediaAsset).filter(
            MediaAsset.report_id == report.id,
            MediaAsset.idempotency_key == idempotency_key,
        ).first()
        if existing:
            return media_asset_out(existing)

    raw_bytes = await file.read()
    sanitized_bytes, output_mime, filename = validate_and_sanitize_image(
        file_bytes=raw_bytes,
        filename=file.filename or "upload.jpg",
        mime_type=file.content_type or "image/jpeg",
    )

    storage_key, sha256_hash, file_size = save_media_file(sanitized_bytes, filename)

    asset = MediaAsset(
        report_id=report.id,
        storage_key=storage_key,
        original_filename=filename,
        mime_type=output_mime,
        file_size=file_size,
        sha256_hash=sha256_hash,
        metadata_status="SANITIZED",
        idempotency_key=idempotency_key,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return media_asset_out(asset)


@router.get("/{reference_or_id}/status", response_model=ReportPublicStatus)
def get_report_status_public(
    reference_or_id: str,
    db: Session = Depends(get_db),
):
    """Public safe tracking view with no sensitive private citizen details."""
    return get_public_report_status(db, reference_or_id)
