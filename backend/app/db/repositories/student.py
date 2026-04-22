"""Student repository."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.models.student import StudentProfile

class StudentRepository(BaseRepository[StudentProfile]):
    @property
    def model(self) -> type[StudentProfile]:
        return StudentProfile

    async def get_by_user_id(self, user_id: UUID) -> StudentProfile | None:
        """Get student profile by user ID."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_admission_number(self, school_id: UUID, admission_number: str) -> StudentProfile | None:
        """Get student profile by admission number within a school."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.admission_number == admission_number
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_section(self, school_id: UUID, section_id: UUID) -> list[StudentProfile]:
        """List all students in a section."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.current_section_id == section_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_school(self, school_id: UUID) -> list[StudentProfile]:
        """List all students for a school."""
        stmt = select(self.model).where(self.model.school_id == school_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
