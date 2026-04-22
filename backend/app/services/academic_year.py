"""Academic Year and Term management service."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError
from app.db.repositories.academic_year import AcademicYearRepository, TermRepository
from app.models.academic_year import AcademicYear, Term
from app.schemas.academic_year import (
    AcademicYearCreate,
    AcademicYearUpdate,
    TermCreate,
    TermUpdate,
)


class AcademicYearService:
    """Business logic for Academic Year and Term management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.year_repo = AcademicYearRepository(db)
        self.term_repo = TermRepository(db)

    async def create_year(self, school_id: UUID, data: AcademicYearCreate) -> AcademicYear:
        """Create a new academic year."""
        # Check if year name already exists for this school
        # (This is also enforced by DB constraint, but better to check here)
        
        # Validate dates
        if data.start_date >= data.end_date:
            raise BadRequestError("Start date must be before end date")

        # Create year
        year = await self.year_repo.create(
            school_id=school_id,
            **data.model_dump()
        )
        
        if data.is_active:
            await self.activate_year(school_id, year.id)
        else:
            await self.db.commit()
            await self.db.refresh(year)
            
        return year

    async def activate_year(self, school_id: UUID, year_id: UUID) -> AcademicYear:
        """Set a specific academic year as active for the school."""
        year = await self.year_repo.get_by_id(id=year_id)
        if year.school_id != school_id:
             raise BadRequestError("Year does not belong to this school")

        # Deactivate all and activate this one
        await self.year_repo.deactivate_all_years(school_id)
        year.is_active = True
        self.db.add(year)
        await self.db.commit()
        await self.db.refresh(year)
        return year

    async def list_years(self, school_id: UUID) -> list[AcademicYear]:
        """List all academic years for a school."""
        from sqlalchemy import select
        stmt = (
            select(AcademicYear)
            .where(AcademicYear.school_id == school_id)
            .order_by(AcademicYear.start_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_year(self, school_id: UUID, year_id: UUID) -> AcademicYear:
        """Get details of a specific year."""
        year = await self.year_repo.get_by_id(id=year_id)
        if year.school_id != school_id:
             raise BadRequestError("Year does not belong to this school")
        return year

    async def create_term(self, school_id: UUID, year_id: UUID, data: TermCreate) -> Term:
        """Create a term within an academic year."""
        year = await self.get_year(school_id, year_id)

        # Validate dates are within year boundaries
        if data.start_date < year.start_date or data.end_date > year.end_date:
            raise BadRequestError(
                f"Term dates must be within academic year range ({year.start_date} to {year.end_date})"
            )
        
        if data.start_date >= data.end_date:
            raise BadRequestError("Start date must be before end date")

        term = await self.term_repo.create(
            academic_year_id=year_id,
            **data.model_dump()
        )
        await self.db.commit()
        await self.db.refresh(term)
        return term

    async def list_terms(self, school_id: UUID, year_id: UUID) -> list[Term]:
        """List all terms for an academic year."""
        await self.get_year(school_id, year_id)  # Validate year belongs to school
        return await self.term_repo.get_by_year(year_id)
