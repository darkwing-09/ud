"""Staff schemas."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class StaffProfileBase(BaseModel):
    first_name: str
    last_name: str
    employee_code: str | None = None
    designation: str | None = None
    department_id: UUID | None = None
    employment_type: str | None = "PERMANENT"
    official_email: EmailStr | None = None
    phone_primary: str | None = None

class StaffProfileCreate(StaffProfileBase):
    user_id: UUID
    date_of_birth: date | None = None
    gender: str | None = None
    blood_group: str | None = None
    personal_email: EmailStr | None = None
    phone_secondary: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    join_date: date | None = None
    qualification: str | None = None
    experience_years: int = 0
    
    # PII fields (plain text here, encrypted in service)
    aadhaar: str | None = None
    pan: str | None = None
    bank_account: str | None = None
    ifsc_code: str | None = None

class StaffProfileResponse(StaffProfileBase):
    id: UUID
    school_id: UUID
    user_id: UUID
    full_name: str
    join_date: date | None
    profile_photo_url: str | None
    created_at: datetime
    
    # PII (decrypted and returned only to authorized roles)
    aadhaar: str | None = None
    pan: str | None = None
    bank_account: str | None = None
    ifsc_code: str | None = None

    model_config = ConfigDict(from_attributes=True)

class StaffProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    designation: str | None = None
    department_id: UUID | None = None
    employment_type: str | None = None
    official_email: EmailStr | None = None
    phone_primary: str | None = None
    phone_secondary: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    qualification: str | None = None
    experience_years: int | None = None
    aadhaar: str | None = None
    pan: str | None = None
    bank_account: str | None = None
    ifsc_code: str | None = None
