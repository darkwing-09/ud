"""Timetable API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.timetable import (
    TimetableSlotCreate, 
    TimetableSlotResponse,
    TimetableEntryCreate,
    TimetableEntryResponse
)
from app.services.timetable import TimetableService

router = APIRouter(prefix="/timetable", tags=["Timetable Management"])

def get_timetable_service(db: DBSession) -> TimetableService:
    return TimetableService(db)

@router.post(
    "/slots",
    response_model=TimetableSlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create timetable slot"
)
async def create_slot(
    school_id: SchoolScopedID,
    data: TimetableSlotCreate,
    auth: User = Depends(require_school_admin),
    service: TimetableService = Depends(get_timetable_service),
) -> TimetableSlotResponse:
    """Create a new period/slot for the school."""
    return await service.create_slot(school_id, data)

@router.get(
    "/slots",
    response_model=list[TimetableSlotResponse],
    summary="List timetable slots"
)
async def list_slots(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: TimetableService = Depends(get_timetable_service),
) -> list[TimetableSlotResponse]:
    """List all slots defined for the school."""
    return await service.list_slots(school_id)

@router.post(
    "/entries",
    response_model=TimetableEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create timetable entry"
)
async def create_entry(
    school_id: SchoolScopedID,
    data: TimetableEntryCreate,
    auth: User = Depends(require_school_admin),
    service: TimetableService = Depends(get_timetable_service),
) -> TimetableEntryResponse:
    """Assign a subject, teacher, and slot to a section's timetable."""
    return await service.create_entry(school_id, data)

@router.get(
    "/section/{section_id}",
    response_model=list[TimetableEntryResponse],
    summary="Get section timetable"
)
async def get_section_timetable(
    school_id: SchoolScopedID,
    section_id: UUID,
    academic_year_id: UUID,
    auth: User = Depends(require_school_admin),
    service: TimetableService = Depends(get_timetable_service),
) -> list[TimetableEntryResponse]:
    """Get the full timetable for a specific section."""
    return await service.get_section_timetable(school_id, section_id, academic_year_id)

@router.get(
    "/teacher/{teacher_id}",
    response_model=list[TimetableEntryResponse],
    summary="Get teacher timetable"
)
async def get_teacher_timetable(
    school_id: SchoolScopedID,
    teacher_id: UUID,
    academic_year_id: UUID,
    auth: User = Depends(require_school_admin),
    service: TimetableService = Depends(get_timetable_service),
) -> list[TimetableEntryResponse]:
    """Get the full schedule for a specific teacher."""
    return await service.get_teacher_timetable(school_id, teacher_id, academic_year_id)
