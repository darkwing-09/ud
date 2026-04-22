"""Leave and Holiday business logic."""
from __future__ import annotations

from datetime import date, timedelta
from typing import cast
from uuid import UUID

from app.core.deps import DBSession
from app.core.exceptions import NotFoundError, ValidationError
from app.db.repositories.leave import (
    LeaveApplicationRepository,
    LeaveTypeRepository,
    StaffLeaveBalanceRepository,
    HolidayRepository,
)
from app.db.repositories.staff import StaffRepository
from app.models.leave import LeaveApplication, LeaveType, StaffLeaveBalance, Holiday
from app.schemas.leave import LeaveApplicationCreate, LeaveTypeCreate, HolidayCreate


class HolidayService:
    def __init__(self, session: DBSession):
        self.session = session
        self.repo = HolidayRepository(session)

    async def create_holiday(self, school_id: UUID, data: HolidayCreate) -> Holiday:
        existing = await self.repo.list_holidays(school_id, data.date, data.date)
        if existing:
            raise ValidationError("A holiday is already defined for this date.")
        holiday = Holiday(school_id=school_id, date=data.date, name=data.name, description=data.description)
        self.repo.add(holiday)
        await self.session.commit()
        await self.session.refresh(holiday)
        return holiday

    async def list_holidays(self, school_id: UUID, start_date: date, end_date: date) -> list[Holiday]:
        return await self.repo.list_holidays(school_id, start_date, end_date)


class LeaveService:
    def __init__(self, session: DBSession):
        self.session = session
        self.leave_repo = LeaveApplicationRepository(session)
        self.type_repo = LeaveTypeRepository(session)
        self.balance_repo = StaffLeaveBalanceRepository(session)
        self.holiday_repo = HolidayRepository(session)
        self.staff_repo = StaffRepository(session)

    async def get_leave_types(self, school_id: UUID) -> list[LeaveType]:
        return await self.type_repo.get_all_for_school(school_id)

    async def create_leave_type(self, school_id: UUID, data: LeaveTypeCreate) -> LeaveType:
        l_type = LeaveType(
            school_id=school_id,
            name=data.name,
            description=data.description,
            is_paid=data.is_paid,
            requires_attachment=data.requires_attachment,
            default_days_per_year=data.default_days_per_year,
        )
        self.type_repo.add(l_type)
        await self.session.commit()
        await self.session.refresh(l_type)
        return l_type

    async def allocate_leaves(self, school_id: UUID, staff_id: UUID, leave_type_id: UUID, year: int, days: float) -> StaffLeaveBalance:
        """Assign an allocation of leave days to a user for a specific year."""
        staff = await self.staff_repo.get_by_id(staff_id)
        if not staff or getattr(staff, "school_id", None) != school_id:
            raise NotFoundError("Staff not found")

        l_type = await self.type_repo.get_by_id(leave_type_id)
        if not l_type or l_type.school_id != school_id:
            raise NotFoundError("Leave type not found")

        balance = await self.balance_repo.get_balance(staff_id, leave_type_id, year)
        if balance:
            balance.allocated_days += days
        else:
            balance = StaffLeaveBalance(
                school_id=school_id,
                staff_id=staff_id,
                leave_type_id=leave_type_id,
                year=year,
                allocated_days=days
            )
            self.balance_repo.add(balance)

        await self.session.commit()
        await self.session.refresh(balance)
        return balance

    async def compute_leave_days(self, school_id: UUID, from_date: date, to_date: date, is_half_day: bool = False) -> float:
        """Calculate the actual number of days taken out of balance, ignoring weekends and holidays."""
        if is_half_day:
            return 0.5
        
        holidays = await self.holiday_repo.list_holidays(school_id, from_date, to_date)
        holiday_dates = {h.date for h in holidays}
        
        days_taken = 0.0
        current = from_date
        while current <= to_date:
            if current.weekday() < 5 and current not in holiday_dates:  # Weekend is 5 (Sat), 6 (Sun)
                days_taken += 1.0
            current += timedelta(days=1)
            
        return float(days_taken)

    async def apply_leave(self, school_id: UUID, data: LeaveApplicationCreate) -> LeaveApplication:
        """Staff submission of a leave application."""
        # 1. Ownership & Overlap
        staff = await self.staff_repo.get_by_id(data.staff_id)
        if not staff or getattr(staff, "school_id", None) != school_id:
            raise NotFoundError("Staff not found in this school.")

        if await self.leave_repo.check_overlap(data.staff_id, data.from_date, data.to_date):
            raise ValidationError("You already have a pending or approved leave during this requested period.")

        l_type = await self.type_repo.get_by_id(data.leave_type_id)
        if not l_type:
            raise NotFoundError("Leave type not found.")

        # 2. Days calculation
        computed_days = await self.compute_leave_days(school_id, data.from_date, data.to_date, data.is_half_day)
        if computed_days <= 0:
            raise ValidationError("Requested timeframe contains no workable days (entirely weekends or holidays).")

        # 3. Balance verification
        year = data.from_date.year
        balance = await self.balance_repo.get_balance(data.staff_id, data.leave_type_id, year)
        
        available = (balance.allocated_days - balance.used_days) if balance else 0.0
        if available < computed_days:
            raise ValidationError(f"Insufficient balance. Tried applying for {computed_days} days, but only {available} available in {l_type.name}.")

        if l_type.requires_attachment and not data.attachment_url:
            raise ValidationError("An attachment (like a medical certificate) is mandatory for this leave type.")

        # 4. Record application
        application = LeaveApplication(
            school_id=school_id,
            staff_id=data.staff_id,
            leave_type_id=data.leave_type_id,
            from_date=data.from_date,
            to_date=data.to_date,
            is_half_day=data.is_half_day,
            actual_leave_days=computed_days,
            reason=data.reason,
            attachment_url=data.attachment_url,
            status="PENDING",
        )
        self.leave_repo.add(application)
        await self.session.commit()
        await self.session.refresh(application)
        return application

    async def approve_leave(self, school_id: UUID, app_id: UUID, user_id: UUID) -> LeaveApplication:
        app = await self.leave_repo.get_by_id(app_id)
        if not app or app.school_id != school_id:
            raise NotFoundError("Leave application not found.")
        
        if app.status != "PENDING":
            raise ValidationError(f"Application already {app.status}")
            
        # Update balance
        balance = await self.balance_repo.get_balance(app.staff_id, app.leave_type_id, app.from_date.year)
        if not balance or (balance.allocated_days - balance.used_days) < float(app.actual_leave_days):
             raise ValidationError("Insufficient balance detected at approval time.")
             
        balance.used_days = float(balance.used_days) + float(app.actual_leave_days)
        
        app.status = "APPROVED"
        app.reviewed_by_id = user_id
        await self.session.commit()
        await self.session.refresh(app)
        
        # In a real setup, dispatch Celery task `notify_leave_approved.delay(app_id)`
        return app

    async def reject_leave(self, school_id: UUID, app_id: UUID, reason: str, user_id: UUID) -> LeaveApplication:
        app = await self.leave_repo.get_by_id(app_id)
        if not app or app.school_id != school_id:
            raise NotFoundError("Leave application not found.")
        
        if app.status != "PENDING":
            raise ValidationError(f"Application already {app.status}")

        app.status = "REJECTED"
        app.reviewer_comments = reason
        app.reviewed_by_id = user_id
        
        await self.session.commit()
        await self.session.refresh(app)
        
        # Celery dispatch `notify_leave_rejected.delay(app_id)`
        return app
