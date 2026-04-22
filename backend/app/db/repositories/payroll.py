"""Payroll repositories."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.payroll import PayrollRecord


class PayrollRecordRepository(BaseRepository[PayrollRecord]):
    """Repository for managing generated payroll records."""
    model = PayrollRecord

    async def get_by_month(self, school_id: UUID, month: int, year: int) -> list[PayrollRecord]:
        """Get all payroll records for a school in a specific month."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.month == month,
            self.model.year == year,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_staff_records(self, school_id: UUID, staff_id: UUID) -> list[PayrollRecord]:
        """Get all payroll records for a specific staff member."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.staff_id == staff_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.year.desc(), self.model.month.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_record(self, school_id: UUID, staff_id: UUID, month: int, year: int) -> PayrollRecord | None:
        """Get a specific payroll record for a staff member."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.staff_id == staff_id,
            self.model.month == month,
            self.model.year == year,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
