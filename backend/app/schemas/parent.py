"""Parent schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class ParentProfileBase(BaseModel):
    first_name: str
    last_name: str
    relationship_type: str | None = "FATHER"  # FATHER | MOTHER | GUARDIAN
    phone: str | None = None
    email: EmailStr | None = None

class ParentProfileCreate(ParentProfileBase):
    user_id: UUID
    occupation: str | None = None
    annual_income: float | None = None

class ParentProfileResponse(ParentProfileBase):
    id: UUID
    school_id: UUID
    user_id: UUID
    full_name: str
    occupation: str | None
    annual_income: float | None
    created_at: datetime

    class Config:
        from_attributes = True

class StudentParentLinkCreate(BaseModel):
    student_id: UUID
    parent_id: UUID
    is_primary: bool = False

class StudentParentLinkResponse(BaseModel):
    student_id: UUID
    parent_id: UUID
    is_primary: bool
    parent: ParentProfileResponse

    class Config:
        from_attributes = True
