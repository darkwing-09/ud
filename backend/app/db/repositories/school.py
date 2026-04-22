"""School repository."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base import BaseRepository
from app.models.school import School


class SchoolRepository(BaseRepository[School]):
    """School repository."""

    model = School

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_code(self, code: str) -> School | None:
        """Get school by tenant code."""
        return await self.get_by_field("code", code)

    async def get_stats(self, school_id: UUID) -> dict[str, Any]:
        """Get raw stats for a school.
        In the future this will aggregate from students and staff tables.
        For now, returns dummy structure.
        """
        # TODO: Implement actual aggregations once Student and Staff models exist.
        return {
            "total_students": 0,
            "total_staff": 0,
            "active_academic_year_id": None,
            "storage_used_bytes": 0,
        }
