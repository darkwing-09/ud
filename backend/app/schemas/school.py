"""School Pydantic schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SchoolSettings(BaseModel):
    min_attendance_percentage: int = Field(default=75)
    late_fee_per_day: float = Field(default=10.0)
    grading_system: str = Field(default="CBSE")
    currency: str = Field(default="INR")
    timezone: str = Field(default="Asia/Kolkata")
    academic_year_start_month: int = Field(default=4, ge=1, le=12)


class SchoolBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50, description="Tenant subdomain/identifier")
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=10)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=255)
    principal_name: str | None = Field(default=None, max_length=255)
    affiliation: str | None = Field(default=None, max_length=255)
    affiliation_number: str | None = Field(default=None, max_length=100)
    subscription_plan: str = Field(default="BASIC", max_length=50)


class SchoolCreate(SchoolBase):
    """Schema for creating a new school (Super Admin only)."""
    settings: SchoolSettings = Field(default_factory=SchoolSettings)


class SchoolUpdate(BaseModel):
    """Schema for updating school details."""
    name: str | None = Field(default=None, max_length=255)
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=10)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=255)
    principal_name: str | None = Field(default=None, max_length=255)
    affiliation: str | None = Field(default=None, max_length=255)
    affiliation_number: str | None = Field(default=None, max_length=100)


class SchoolSettingsUpdate(BaseModel):
    """Schema for updating flexible school settings."""
    settings: SchoolSettings


class SchoolResponse(SchoolBase):
    """Schema for school responses."""
    id: UUID
    logo_url: str | None = None
    is_active: bool
    settings: SchoolSettings
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SchoolStatsResponse(BaseModel):
    """Schema for school statistics."""
    total_students: int
    total_staff: int
    active_academic_year_id: UUID | None = None
    storage_used_bytes: int = 0
