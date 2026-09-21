from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import EvidenceReviewStatus, DisputeStatus
from app.schemas.report import MediaAssetOut


class ResolutionEvidenceCreate(BaseModel):
    description: str = Field(..., min_length=10, max_length=2000)
    media_asset_id: Optional[str] = None


class ResolutionEvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    uploader_id: str
    uploader_name: Optional[str] = None
    description: str
    submitted_at: datetime
    review_status: EvidenceReviewStatus
    reviewer_id: Optional[str] = None
    review_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    media_assets: List[MediaAssetOut] = []


class ResolutionReviewCreate(BaseModel):
    decision: EvidenceReviewStatus  # APPROVED or REJECTED
    reason: str = Field(..., min_length=3, max_length=1000)


class DisputeCreate(BaseModel):
    reason: str = Field(..., min_length=5, max_length=2000)


class DisputeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    reporter_id: str
    reason: str
    status: DisputeStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None


class ReopenRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)
