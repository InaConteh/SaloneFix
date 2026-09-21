from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import AssignmentStatus, IncidentStatus, IncidentPriority
from app.schemas.report import ReportOut
from app.schemas.resolution import ResolutionEvidenceOut, DisputeOut


class IncidentCreate(BaseModel):
    category_id: str
    title: str = Field(..., min_length=5, max_length=200)
    summary: str = Field(..., min_length=10, max_length=2000)
    priority: IncidentPriority = IncidentPriority.MEDIUM
    report_id: Optional[str] = None  # optionally seed with first verified report


class IncidentLinkReport(BaseModel):
    report_id: str
    notes: Optional[str] = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus
    reason: str = Field(..., min_length=3, max_length=1000)


class LinkedReportOut(BaseModel):
    link_id: str
    report: ReportOut
    linked_at: datetime
    notes: Optional[str] = None


class ActiveAssignmentOut(BaseModel):
    id: str
    institution_id: str
    institution_name: Optional[str] = None
    officer_id: Optional[str] = None
    officer_name: Optional[str] = None
    status: AssignmentStatus
    due_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    is_overdue: bool = False


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category_id: str
    category_name: Optional[str] = None
    title: str
    summary: str
    priority: IncidentPriority
    lifecycle_status: IncidentStatus
    centroid_latitude: Optional[float] = None
    centroid_longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    linked_reports_count: int = 0
    linked_reports: List[LinkedReportOut] = []
    assigned_institution_name: Optional[str] = None
    active_assignment: Optional[ActiveAssignmentOut] = None
    requires_resolution_evidence: bool = True
    resolution_evidence: List[ResolutionEvidenceOut] = []
    disputes: List[DisputeOut] = []


class IncidentPublicMapItem(BaseModel):
    id: str
    category_name: Optional[str] = None
    title: str
    lifecycle_status: IncidentStatus
    approx_latitude: Optional[float] = None
    approx_longitude: Optional[float] = None
    created_at: datetime
