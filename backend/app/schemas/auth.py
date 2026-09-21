from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    contact: str
    password: str


class RegisterRequest(BaseModel):
    name_or_alias: str = Field(..., min_length=2, max_length=120)
    contact: str = Field(..., min_length=3, max_length=120)
    password: str = Field(..., min_length=8, max_length=128)
    consent_status: bool = True


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: UserRole
    name_or_alias: str
    contact: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
