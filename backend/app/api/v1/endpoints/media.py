from typing import Optional
from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import MediaAsset, User
from app.models.enums import UserRole
from app.core.exceptions import NotFoundError, ForbiddenError
from app.core.dependencies import get_optional_current_user
from app.core.security import verify_signed_media_token
from app.services.storage import get_media_bytes

router = APIRouter()


@router.get("/{asset_id}")
def stream_media(
    asset_id: str,
    token: Optional[str] = Query(None, description="Signed media access token"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if not asset:
        raise NotFoundError("Media asset")

    # Authorization: authenticated staff/owner, or a valid signed token issued
    # by the API in a MediaAssetOut.url. Anonymous access is refused — media is
    # private evidence and must never be exposed by default.
    authorized = False
    if current_user:
        if current_user.role in (UserRole.MODERATOR, UserRole.OFFICER, UserRole.ADMIN, UserRole.AUDITOR):
            authorized = True
        elif asset.report and asset.report.reporter_id == current_user.id:
            authorized = True

    if not authorized and token and verify_signed_media_token(asset.id, token):
        authorized = True

    if not authorized:
        raise ForbiddenError("A valid signed media token or authorized session is required.")

    try:
        content = get_media_bytes(asset.storage_key)
    except FileNotFoundError:
        raise NotFoundError("Stored media file")

    return Response(
        content=content,
        media_type=asset.mime_type,
        headers={"Content-Disposition": f'inline; filename="{asset.original_filename}"'},
    )
