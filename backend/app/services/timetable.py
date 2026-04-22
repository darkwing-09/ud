"""Timetable services."""
from __future__ import annotations

from uuid import UUID

from app.db.repositories.timetable import TimetableSlotRepository, TimetableEntryRepository
from app.models.timetable import TimetableSlot, TimetableEntry
from app.schemas.timetable import TimetableSlotCreate, TimetableEntryCreate
from sqlalchemy.ext.asyncio import AsyncSession


class TimetableService:
    def __init__(self, db: AsyncSession):
        self.slot_repo = TimetableSlotRepository(db)
        self.entry_repo = TimetableEntryRepository(db)
        self.db = db

    async def create_slot(self, school_id: UUID, data: TimetableSlotCreate) -> TimetableSlot:
        """Create a new timetable slot for a school."""
        slot = TimetableSlot(
            school_id=school_id,
            **data.model_dump()
        )
        return await self.slot_repo.save(slot)

    async def list_slots(self, school_id: UUID) -> list[TimetableSlot]:
        """List all slots for a school."""
        return await self.slot_repo.list_by_school(school_id)

    async def create_entry(self, school_id: UUID, data: TimetableEntryCreate) -> TimetableEntry:
        """Create a new timetable entry."""
        entry = TimetableEntry(
            school_id=school_id,
            **data.model_dump()
        )
        return await self.entry_repo.save(entry)

    async def get_section_timetable(self, school_id: UUID, section_id: UUID, academic_year_id: UUID) -> list[TimetableEntry]:
        """Get the full timetable for a section."""
        return await self.entry_repo.list_by_section(school_id, section_id, academic_year_id)

    async def get_teacher_timetable(self, school_id: UUID, teacher_id: UUID, academic_year_id: UUID) -> list[TimetableEntry]:
        """Get the full timetable for a teacher."""
        return await self.entry_repo.list_by_teacher(school_id, teacher_id, academic_year_id)
