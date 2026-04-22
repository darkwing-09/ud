"""Leave management repositories."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select, and_, or_

from app.db.repositories.base import BaseRepository
from app.models.leave import LeaveType, StaffLeaveBalance, LeaveApplication, Holiday


class LeaveTypeRepository(BaseRepository[LeaveType]):
    """Repository for Leave Types."""
    model = LeaveType

    async def get_all_for_school(self, school_id: UUID) -> list[LeaveType]:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.name.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StaffLeaveBalanceRepository(BaseRepository[StaffLeaveBalance]):
    """Repository for Staff Leave Balances."""
    model = StaffLeaveBalance

    async def get_balance(self, staff_id: UUID, leave_type_id: UUID, year: int) -> StaffLeaveBalance | None:
        stmt = select(self.model).where(
            self.model.staff_id == staff_id,
            self.model.leave_type_id == leave_type_id,
            self.model.year == year,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_staff(self, staff_id: UUID, year: int) -> list[StaffLeaveBalance]:
        stmt = select(self.model).where(
            self.model.staff_id == staff_id,
            self.model.year == year,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class LeaveApplicationRepository(BaseRepository[LeaveApplication]):
    """Repository for Leave Applications."""
    model = LeaveApplication

    async def check_overlap(self, staff_id: UUID, from_date: date, to_date: date) -> bool:
        """Check if any APPROVED or PENDING leave overlaps with the specified timeframe."""
        stmt = select(self.model).where(
            self.model.staff_id == staff_id,
            self.model.status.in_(["PENDING", "APPROVED"]),
            self.model.deleted_at.is_(None),
            self.model.from_date <= to_date,
            self.model.to_date >= from_date
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_for_staff(self, staff_id: UUID) -> list[LeaveApplication]:
        stmt = select(self.model).where(
            self.model.staff_id == staff_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.from_date.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_inbox(self, school_id: UUID) -> list[LeaveApplication]:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.status == "PENDING",
            self.model.deleted_at.is_(None)
        ).order_by(self.model.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class HolidayRepository(BaseRepository[Holiday]):
    """Repository for Holidays."""
    model = Holiday

    async def list_holidays(self, school_id: UUID, start_date: date, end_date: date) -> list[Holiday]:
        """List holidays inside a date range."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.date >= start_date,
            self.model.date <= end_date,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
