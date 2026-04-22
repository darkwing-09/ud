"""Parent repository."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.models.parent import ParentProfile, StudentParentLink

class ParentRepository(BaseRepository[ParentProfile]):
    @property
    def model(self) -> type[ParentProfile]:
        return ParentProfile

    async def get_by_user_id(self, user_id: UUID) -> ParentProfile | None:
        """Get parent profile by user ID."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_school(self, school_id: UUID) -> list[ParentProfile]:
        """List all parents for a school."""
        stmt = select(self.model).where(self.model.school_id == school_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_student_parent_links(self, student_id: UUID) -> list[StudentParentLink]:
        """Get all parent links for a student."""
        stmt = select(StudentParentLink).where(StudentParentLink.student_id == student_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def link_parent_to_student(self, school_id: UUID, student_id: UUID, parent_id: UUID, is_primary: bool = False) -> StudentParentLink:
        """Link a parent to a student."""
        link = StudentParentLink(
            school_id=school_id,
            student_id=student_id,
            parent_id=parent_id,
            is_primary=is_primary
        )
        self.session.add(link)
        await self.session.flush()
        return link
