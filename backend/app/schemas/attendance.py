"""Attendance schemas."""
from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentAttendanceBase(BaseModel):
    date: date
    status: str = Field(..., pattern="^(PRESENT|ABSENT|LATE|EXCUSED)$")
    remarks: str | None = None


class StudentAttendanceCreate(StudentAttendanceBase):
    student_id: UUID
    academic_year_id: UUID
    section_id: UUID


class StudentAttendanceBulkCreate(BaseModel):
    date: date
    section_id: UUID
    academic_year_id: UUID
    records: list[dict]  # list of {student_id, status, remarks}


class StudentAttendanceResponse(StudentAttendanceBase):
    id: UUID
    school_id: UUID
    student_id: UUID
    academic_year_id: UUID
    section_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StaffAttendanceBase(BaseModel):
    date: date
    status: str = Field(..., pattern="^(PRESENT|ABSENT|LATE|ON_LEAVE)$")
    check_in: time | None = None
    check_out: time | None = None
    remarks: str | None = None


class StaffAttendanceCreate(StaffAttendanceBase):
    staff_id: UUID


class StaffAttendanceResponse(StaffAttendanceBase):
    id: UUID
    school_id: UUID
    staff_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
