"""Academic Year and Term repositories."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, select, update

from app.db.repositories.base import BaseRepository
from app.models.academic_year import AcademicYear, Term


class AcademicYearRepository(BaseRepository[AcademicYear]):
    model = AcademicYear

    async def get_active_year(self, school_id: UUID) -> AcademicYear | None:
        """Get the currently active academic year for a school."""
        stmt = select(AcademicYear).where(
            and_(
                AcademicYear.school_id == school_id,
                AcademicYear.is_active.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_all_years(self, school_id: UUID) -> None:
        """Deactivate all academic years for a school."""
        stmt = (
            update(AcademicYear)
            .where(AcademicYear.school_id == school_id)
            .values(is_active=False)
        )
        await self.session.execute(stmt)


class TermRepository(BaseRepository[Term]):
    model = Term

    async def get_by_year(self, school_id: UUID, academic_year_id: UUID) -> list[Term]:
        """Get all terms for a specific academic year."""
        stmt = (
            select(Term)
            .where(
                Term.school_id == school_id,
                Term.academic_year_id == academic_year_id
            )
            .order_by(Term.start_date)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
