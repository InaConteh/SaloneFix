from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import ModerationDecisionType, ReportStatus
from app.schemas.report import ReportOut


class ModerationDecisionCreate(BaseModel):
    decision: ModerationDecisionType
    reason: str = Field(..., min_length=3, max_length=1000, description="Explicit human reason required")
    target_incident_id: Optional[str] = None  # for MERGE


class ModerationDecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_id: str
    moderator_id: str
    decision: ModerationDecisionType
    reason: str
    created_at: datetime


class ModerationQueueItem(BaseModel):
    report: ReportOut
    nearby_reports: List[ReportOut] = []
