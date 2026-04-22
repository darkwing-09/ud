"""Attendance services."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from app.db.repositories.attendance import StudentAttendanceRepository, StaffAttendanceRepository
from app.models.attendance import StudentAttendance, StaffAttendance
from app.schemas.attendance import StudentAttendanceCreate, StudentAttendanceBulkCreate, StaffAttendanceCreate
from sqlalchemy.ext.asyncio import AsyncSession


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.student_repo = StudentAttendanceRepository(db)
        self.staff_repo = StaffAttendanceRepository(db)
        self.db = db

    async def mark_student_attendance(self, school_id: UUID, data: StudentAttendanceCreate) -> StudentAttendance:
        """Mark or update student attendance for a specific date."""
        existing = await self.student_repo.get_by_student_and_date(school_id, data.student_id, data.date)
        if existing:
            existing.status = data.status
            existing.remarks = data.remarks
            return await self.student_repo.save(existing)
        
        attendance = StudentAttendance(
            school_id=school_id,
            **data.model_dump()
        )
        return await self.student_repo.save(attendance)

    async def bulk_mark_student_attendance(self, school_id: UUID, data: StudentAttendanceBulkCreate) -> list[StudentAttendance]:
        """Mark attendance for multiple students at once."""
        results = []
        for record in data.records:
            create_data = StudentAttendanceCreate(
                date=data.date,
                section_id=data.section_id,
                academic_year_id=data.academic_year_id,
                student_id=record["student_id"],
                status=record["status"],
                remarks=record.get("remarks")
            )
            # Use mark_student_attendance to handle existing records
            results.append(await self.mark_student_attendance(school_id, create_data))
        return results

    async def get_section_attendance(self, school_id: UUID, section_id: UUID, date: date) -> list[StudentAttendance]:
        """Get attendance records for a section on a given date."""
        return await self.student_repo.list_by_section_and_date(school_id, section_id, date)

    async def mark_staff_attendance(self, school_id: UUID, data: StaffAttendanceCreate) -> StaffAttendance:
        """Mark or update staff attendance for a specific date."""
        existing = await self.staff_repo.get_by_staff_and_date(school_id, data.staff_id, data.date)
        if existing:
            existing.status = data.status
            existing.check_in = data.check_in
            existing.check_out = data.check_out
            existing.remarks = data.remarks
            return await self.staff_repo.save(existing)
        
        attendance = StaffAttendance(
            school_id=school_id,
            **data.model_dump()
        )
        return await self.staff_repo.save(attendance)
