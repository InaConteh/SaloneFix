"""Build client-facing media descriptors.

Media is never served as static files. Every URL handed to a client carries a
short-lived signed token so ``<img>`` tags (which cannot send a bearer header)
can load it, while anyone without the token — or after it expires — is refused.
"""
from app.core.security import generate_signed_media_token
from app.models.entities import MediaAsset
from app.schemas.report import MediaAssetOut

MEDIA_TOKEN_TTL_SECONDS = 3600


def media_asset_out(asset: MediaAsset) -> MediaAssetOut:
    token = generate_signed_media_token(asset.id, expires_in_seconds=MEDIA_TOKEN_TTL_SECONDS)
    return MediaAssetOut(
        id=asset.id,
        original_filename=asset.original_filename,
        mime_type=asset.mime_type,
        file_size=asset.file_size,
        created_at=asset.created_at,
        url=f"/api/v1/media/{asset.id}?token={token}",
    )
