"""Timetable repositories."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.timetable import TimetableSlot, TimetableEntry


class TimetableSlotRepository(BaseRepository[TimetableSlot]):
    @property
    def model(self) -> type[TimetableSlot]:
        return TimetableSlot

    async def list_by_school(self, school_id: UUID) -> list[TimetableSlot]:
        """List all slots for a school ordered by their set order."""
        stmt = select(self.model).where(
            self.model.school_id == school_id
        ).order_by(self.model.order, self.model.start_time)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class TimetableEntryRepository(BaseRepository[TimetableEntry]):
    @property
    def model(self) -> type[TimetableEntry]:
        return TimetableEntry

    async def list_by_section(self, school_id: UUID, section_id: UUID, academic_year_id: UUID) -> list[TimetableEntry]:
        """List all timetable entries for a section in a specific year."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.section_id == section_id,
            self.model.academic_year_id == academic_year_id
        ).order_by(self.model.day_of_week, self.model.slot_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_teacher(self, school_id: UUID, teacher_id: UUID, academic_year_id: UUID) -> list[TimetableEntry]:
        """List all timetable entries for a teacher."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.teacher_id == teacher_id,
            self.model.academic_year_id == academic_year_id
        ).order_by(self.model.day_of_week, self.model.slot_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
