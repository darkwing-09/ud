"""Attendance repositories."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.attendance import StudentAttendance, StaffAttendance


class StudentAttendanceRepository(BaseRepository[StudentAttendance]):
    @property
    def model(self) -> type[StudentAttendance]:
        return StudentAttendance

    async def get_by_student_and_date(self, school_id: UUID, student_id: UUID, date: date) -> StudentAttendance | None:
        """Get attendance record for a student on a specific date."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.student_id == student_id,
            self.model.date == date
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_section_and_date(self, school_id: UUID, section_id: UUID, date: date) -> list[StudentAttendance]:
        """List all attendance records for a section on a specific date."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.section_id == section_id,
            self.model.date == date
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StaffAttendanceRepository(BaseRepository[StaffAttendance]):
    @property
    def model(self) -> type[StaffAttendance]:
        return StaffAttendance

    async def get_by_staff_and_date(self, school_id: UUID, staff_id: UUID, date: date) -> StaffAttendance | None:
        """Get attendance record for a staff member on a specific date."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.staff_id == staff_id,
            self.model.date == date
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
