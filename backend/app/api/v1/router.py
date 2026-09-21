from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    reports,
    moderation,
    incidents,
    assignments,
    resolution,
    audit,
    institutions,
    categories,
    media,
    notifications,
    admin,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(moderation.router, prefix="/moderation", tags=["moderation"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(assignments.router, tags=["assignments"])
api_router.include_router(resolution.router, tags=["resolution"])
api_router.include_router(audit.router, tags=["audit"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
