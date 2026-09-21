from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import AssignmentStatus


class AssignmentCreate(BaseModel):
    institution_id: str
    officer_id: Optional[str] = None
    due_at: Optional[datetime] = None


class AssignmentStatusUpdate(BaseModel):
    status: AssignmentStatus  # ACCEPTED or DECLINED
    decline_reason: Optional[str] = None


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    institution_id: str
    institution_name: Optional[str] = None
    officer_id: Optional[str] = None
    officer_name: Optional[str] = None
    assigned_by: str
    assigned_at: datetime
    due_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    decline_reason: Optional[str] = None
    status: AssignmentStatus
