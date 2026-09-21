from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import UserRole


class StaffUserCreate(BaseModel):
    """Administrator-provisioned account. Public registration cannot set a role."""
    name_or_alias: str = Field(..., min_length=2, max_length=120)
    contact: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole
    institution_id: Optional[str] = None


class UserAdminUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    institution_id: Optional[str] = None
    reason: str = Field(..., min_length=3, max_length=500)


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    service_area: str = Field("Freetown", min_length=2, max_length=150)
    contact_channel: Optional[str] = Field(None, max_length=100)


class InstitutionUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=2000)
    service_area: Optional[str] = Field(None, min_length=2, max_length=150)
    contact_channel: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
