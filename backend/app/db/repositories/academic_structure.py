"""Academic Structure repositories."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.department import Department
from app.models.class_ import Class
from app.models.section import Section
from app.models.subject import Subject, ClassSubjectAssignment


class DepartmentRepository(BaseRepository[Department]):
    model = Department

    async def get_by_school(self, school_id: UUID) -> list[Department]:
        """Get all departments for a school."""
        stmt = select(self.model).where(self.model.school_id == school_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ClassRepository(BaseRepository[Class]):
    model = Class

    async def get_by_school_year(self, school_id: UUID, academic_year_id: UUID) -> list[Class]:
        """Get all classes for a school in a specific academic year."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.academic_year_id == academic_year_id
        ).order_by(self.model.numeric_level)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SectionRepository(BaseRepository[Section]):
    model = Section

    async def get_by_class(self, school_id: UUID, class_id: UUID) -> list[Section]:
        """Get all sections for a class."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.class_id == class_id
        ).order_by(self.model.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SubjectRepository(BaseRepository[Subject]):
    model = Subject

    async def get_by_school(self, school_id: UUID) -> list[Subject]:
        """Get all subjects for a school."""
        stmt = select(self.model).where(self.model.school_id == school_id).order_by(self.model.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ClassSubjectAssignmentRepository(BaseRepository[ClassSubjectAssignment]):
    model = ClassSubjectAssignment

    async def get_by_class_or_section(
        self, 
        school_id: UUID,
        class_id: UUID, 
        section_id: UUID | None = None
    ) -> list[ClassSubjectAssignment]:
        """Get subject assignments for a class or a specific section."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.class_id == class_id
        )
        if section_id:
            stmt = stmt.where(self.model.section_id == section_id)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
