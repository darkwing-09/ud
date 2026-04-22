"""Student schemas."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import BaseRequest

class StudentProfileBase(BaseRequest):
    first_name: str
    last_name: str
    admission_number: str
    roll_number: str | None = None
    current_section_id: UUID | None = None
    academic_year_id: UUID

class StudentProfileCreate(StudentProfileBase):
    user_id: UUID | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    religion: str | None = None
    caste_category: str | None = None
    admission_date: date | None = None
    previous_school: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    aadhaar: str | None = None

class StudentProfileResponse(StudentProfileBase):
    id: UUID
    school_id: UUID
    user_id: UUID | None
    full_name: str
    status: str
    profile_photo_url: str | None
    created_at: datetime
    
    # PII (decrypted)
    aadhaar: str | None = None

    model_config = ConfigDict(from_attributes=True)

class StudentProfileUpdate(BaseRequest):
    first_name: str | None = None
    last_name: str | None = None
    roll_number: str | None = None
    current_section_id: UUID | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    aadhaar: str | None = None
    status: str | None = None
