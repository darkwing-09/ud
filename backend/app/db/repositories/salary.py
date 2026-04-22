"""Salary repositories."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from sqlalchemy import select, and_, or_

from app.db.repositories.base import BaseRepository
from app.models.salary import SalaryStructure, StaffSalaryAssignment, SalaryAdvance


class SalaryStructureRepository(BaseRepository[SalaryStructure]):
    model = SalaryStructure

    async def get_by_school(self, school_id: UUID) -> list[SalaryStructure]:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StaffSalaryAssignmentRepository(BaseRepository[StaffSalaryAssignment]):
    model = StaffSalaryAssignment

    async def get_active_for_staff(self, school_id: UUID, staff_id: UUID, current_date: date) -> StaffSalaryAssignment | None:
        """Get the active salary assignment for a staff member on a specific date."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.staff_id == staff_id,
            self.model.effective_from <= current_date,
            or_(
                self.model.effective_until.is_(None),
                self.model.effective_until >= current_date
            ),
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_in_school(self, school_id: UUID, current_date: date) -> list[StaffSalaryAssignment]:
        """Get all active salary assignments in the school for a given date."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.effective_from <= current_date,
            or_(
                self.model.effective_until.is_(None),
                self.model.effective_until >= current_date
            ),
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SalaryAdvanceRepository(BaseRepository[SalaryAdvance]):
    model = SalaryAdvance

    async def get_active_advances_for_staff(self, school_id: UUID, staff_id: UUID) -> list[SalaryAdvance]:
        """Get approved advances that are not yet fully recovered."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.staff_id == staff_id,
            self.model.status == "APPROVED",
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
