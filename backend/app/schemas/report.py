from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import LocationPrecision, ReportStatus


class ReportCreate(BaseModel):
    category_code: str
    description: str = Field(..., min_length=10, max_length=2000)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_precision: LocationPrecision = LocationPrecision.APPROXIMATE
    source_channel: str = "WEB"


class MediaAssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    mime_type: str
    file_size: int
    created_at: datetime
    url: Optional[str] = None


class ReportCreateResponse(BaseModel):
    id: str
    tracking_reference: str
    status: ReportStatus
    created_at: datetime
    next_step: str


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tracking_reference: str
    reporter_id: str
    category_id: str
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_precision: LocationPrecision
    submitted_at: datetime
    current_status: ReportStatus
    source_channel: str
    clarification_notes: Optional[str] = None
    media_assets: List[MediaAssetOut] = []
    incident_id: Optional[str] = None


class ReportPublicStatus(BaseModel):
    tracking_reference: str
    current_status: ReportStatus
    category_name: str
    description: str
    submitted_at: datetime
    last_update: datetime
    next_step: str
    responsible_institution: Optional[str] = None
    can_dispute: bool = False
    incident_id: Optional[str] = None
    resolution_description: Optional[str] = None
