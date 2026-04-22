"""Leave management schemas."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


# ── LeaveType ──────────────────────────────────────────────────

class LeaveTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_paid: bool = True
    requires_attachment: bool = False
    default_days_per_year: float = Field(0.0, ge=0)


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeResponse(LeaveTypeBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── StaffLeaveBalance ──────────────────────────────────────────

class StaffLeaveBalanceBase(BaseModel):
    year: int = Field(..., gt=2000)
    allocated_days: float = Field(0.0, ge=0)


class StaffLeaveBalanceCreate(StaffLeaveBalanceBase):
    staff_id: UUID
    leave_type_id: UUID


class StaffLeaveBalanceResponse(StaffLeaveBalanceBase):
    id: UUID
    school_id: UUID
    staff_id: UUID
    leave_type_id: UUID
    used_days: float

    model_config = ConfigDict(from_attributes=True)


# ── LeaveApplication ───────────────────────────────────────────

class LeaveApplicationBase(BaseModel):
    from_date: date
    to_date: date
    is_half_day: bool = False
    reason: str = Field(..., min_length=5, max_length=1000)
    attachment_url: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> LeaveApplicationBase:
        if self.to_date < self.from_date:
            raise ValueError("to_date cannot be earlier than from_date")
        if self.is_half_day and self.from_date != self.to_date:
            raise ValueError("is_half_day can only be true for single-day leaves")
        return self


class LeaveApplicationCreate(LeaveApplicationBase):
    staff_id: UUID
    leave_type_id: UUID


class LeaveApplicationResponse(LeaveApplicationBase):
    id: UUID
    school_id: UUID
    staff_id: UUID
    leave_type_id: UUID
    actual_leave_days: float
    status: str
    reviewed_by_id: UUID | None
    reviewer_comments: str | None

    model_config = ConfigDict(from_attributes=True)


# ── Holiday ────────────────────────────────────────────────────

class HolidayBase(BaseModel):
    date: date
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)
