from typing import Optional
from pydantic import BaseModel, ConfigDict


class InstitutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    service_area: str
    contact_channel: Optional[str] = None
    is_active: bool


class ServiceCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str] = None
    requires_resolution_evidence: bool
    is_active: bool
