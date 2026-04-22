"""Timetable schemas."""
from __future__ import annotations

from datetime import time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimetableSlotBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    is_break: bool = False
    order: int = 0


class TimetableSlotCreate(TimetableSlotBase):
    pass


class TimetableSlotResponse(TimetableSlotBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TimetableEntryBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    room_number: str | None = None


class TimetableEntryCreate(TimetableEntryBase):
    academic_year_id: UUID
    section_id: UUID
    subject_id: UUID
    teacher_id: UUID
    slot_id: UUID


class TimetableEntryResponse(TimetableEntryBase):
    id: UUID
    school_id: UUID
    academic_year_id: UUID
    section_id: UUID
    subject_id: UUID
    teacher_id: UUID
    slot_id: UUID
    
    # Optional nested data for response
    subject_name: str | None = None
    teacher_name: str | None = None
    slot_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
