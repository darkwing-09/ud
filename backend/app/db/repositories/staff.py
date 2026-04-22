"""Staff repository."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.models.staff import StaffProfile

class StaffRepository(BaseRepository[StaffProfile]):
    @property
    def model(self) -> type[StaffProfile]:
        return StaffProfile

    async def get_by_user_id(self, user_id: UUID) -> StaffProfile | None:
        """Get staff profile by user ID."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_code(self, school_id: UUID, code: str) -> StaffProfile | None:
        """Get staff profile by employee code within a school."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.employee_code == code
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_school(self, school_id: UUID) -> list[StaffProfile]:
        """List all staff for a school."""
        stmt = select(self.model).where(self.model.school_id == school_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
