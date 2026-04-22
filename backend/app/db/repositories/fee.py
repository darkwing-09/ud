"""Fee repositories — FeeStructure, FeeDue, FeePayment, FeeDiscount."""
from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select

from app.db.repositories.base import BaseRepository
from app.models.fee import (
    FeeAssignment,
    FeeComponent,
    FeeDiscount,
    FeeDue,
    FeeStructure,
    StudentFeeDiscount,
)
from app.models.payment import FeePayment
from app.models.student import StudentProfile


class FeeStructureRepository(BaseRepository[FeeStructure]):
    """Repository for FeeStructure operations."""
    model = FeeStructure

    async def get_by_academic_year(
        self, school_id: UUID, academic_year_id: UUID
    ) -> list[FeeStructure]:
        """List all fee structures for a given academic year."""
        stmt = (
            select(self.model)
            .where(
                self.model.school_id == school_id,
                self.model.academic_year_id == academic_year_id,
                self.model.deleted_at.is_(None),
            )
            .order_by(self.model.name.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def has_active_dues(self, school_id: UUID, structure_id: UUID) -> bool:
        """Check if any fee dues exist for this structure (prevent deletion)."""
        stmt = select(func.count()).select_from(FeeDue).where(
            FeeDue.school_id == school_id,
            FeeDue.fee_structure_id == structure_id,
            FeeDue.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0


class FeeAssignmentRepository(BaseRepository[FeeAssignment]):
    """Repository for FeeAssignment (structure → class/section/student links)."""
    model = FeeAssignment

    async def get_for_class(self, school_id: UUID, class_id: UUID) -> list[FeeAssignment]:
        """Get all assignments for a class."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.class_id == class_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_student(self, school_id: UUID, student_id: UUID) -> list[FeeAssignment]:
        """Get direct student-level assignments."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def duplicate_exists(
        self,
        school_id: UUID,
        fee_structure_id: UUID,
        class_id: UUID | None,
        section_id: UUID | None,
        student_id: UUID | None,
    ) -> bool:
        """Check if an identical assignment already exists."""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.school_id == school_id,
            self.model.fee_structure_id == fee_structure_id,
            self.model.class_id == class_id,
            self.model.section_id == section_id,
            self.model.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0


class FeeDiscountRepository(BaseRepository[FeeDiscount]):
    """Repository for FeeDiscount definitions."""
    model = FeeDiscount

    async def get_student_discounts(
        self, school_id: UUID, student_id: UUID
    ) -> list[StudentFeeDiscount]:
        """Get all active discounts applied to a student."""
        stmt = (
            select(StudentFeeDiscount)
            .where(
                StudentFeeDiscount.school_id == school_id,
                StudentFeeDiscount.student_id == student_id,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class FeeDueRepository(BaseRepository[FeeDue]):
    """Repository for FeeDue (individual payment obligations)."""
    model = FeeDue

    async def get_student_dues(
        self,
        school_id: UUID,
        student_id: UUID,
        status: str | None = None,
    ) -> list[FeeDue]:
        """Get all dues for a student, optionally filtered by status."""
        stmt = (
            select(self.model)
            .where(
                self.model.school_id == school_id,
                self.model.student_id == student_id,
                self.model.deleted_at.is_(None),
            )
            .order_by(self.model.due_date.asc())
        )
        if status:
            stmt = stmt.where(self.model.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_overdue_dues(self, school_id: UUID) -> list[FeeDue]:
        """Get all unpaid dues past their due_date."""
        today = date.today()
        stmt = (
            select(self.model)
            .where(
                self.model.school_id == school_id,
                self.model.status.in_(["UNPAID", "PARTIAL"]),
                self.model.due_date < today,
                self.model.deleted_at.is_(None),
            )
            .order_by(self.model.due_date.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists_for_period(
        self, school_id: UUID, student_id: UUID, fee_structure_id: UUID, period_label: str
    ) -> bool:
        """Prevent duplicate due generation for the same period."""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.school_id == school_id,
            self.model.student_id == student_id,
            self.model.fee_structure_id == fee_structure_id,
            self.model.period_label == period_label,
            self.model.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def get_defaulters(
        self,
        school_id: UUID,
        class_id: UUID | None = None,
        days_overdue_min: int = 1,
        amount_min: float = 0,
    ) -> list[dict]:
        """
        Return defaulter records with student info and aging.
        Returns a list of dicts: { due, student }
        """
        today = date.today()
        cutoff = today - timedelta(days=days_overdue_min)

        stmt = (
            select(self.model, StudentProfile)
            .join(StudentProfile, StudentProfile.id == self.model.student_id)
            .where(
                self.model.school_id == school_id,
                self.model.status.in_(["UNPAID", "PARTIAL"]),
                self.model.due_date <= cutoff,
                self.model.deleted_at.is_(None),
                StudentProfile.deleted_at.is_(None),
            )
        )
        if class_id:
            from app.models.section import Section
            from app.models.class_ import Class
            stmt = stmt.join(
                Section, Section.id == StudentProfile.current_section_id
            ).where(Section.class_id == class_id)

        result = await self.session.execute(stmt)
        rows = result.all()

        defaulters = []
        for due, student in rows:
            outstanding = max(0.0, float(due.net_amount) + float(due.late_fee_amount) - float(due.paid_amount))
            if outstanding < amount_min:
                continue
            days_late = (today - due.due_date).days
            defaulters.append({
                "due": due,
                "student": student,
                "outstanding": outstanding,
                "days_overdue": days_late,
            })
        return defaulters


class FeePaymentRepository(BaseRepository[FeePayment]):
    """Repository for FeePayment records — immutable after SUCCESS."""
    model = FeePayment

    async def get_by_gateway_payment_id(
        self, school_id: UUID, gateway_payment_id: str
    ) -> FeePayment | None:
        """Find payment by Razorpay payment_id for idempotency checks."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.gateway_payment_id == gateway_payment_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_gateway_order_id(
        self, school_id: UUID, gateway_order_id: str
    ) -> FeePayment | None:
        """Find a PENDING payment by Razorpay order_id for webhook matching."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.gateway_order_id == gateway_order_id,
            self.model.status == "PENDING",
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_student_payments(
        self, school_id: UUID, student_id: UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[FeePayment], int]:
        """Paginated payment history for a student."""
        base_where = and_(
            self.model.school_id == school_id,
            self.model.student_id == student_id,
            self.model.status == "SUCCESS",
        )
        count_stmt = select(func.count()).select_from(self.model).where(base_where)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(self.model)
            .where(base_where)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def get_next_receipt_number(self, school_id: UUID) -> str:
        """Generate a sequential, school-scoped receipt number."""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.school_id == school_id,
            self.model.status == "SUCCESS",
        )
        result = await self.session.execute(stmt)
        count = (result.scalar_one() or 0) + 1
        school_prefix = str(school_id)[:8].upper()
        return f"RCP-{school_prefix}-{count:06d}"

    async def get_collection_summary(
        self,
        school_id: UUID,
        from_date: date,
        to_date: date,
    ) -> list[FeePayment]:
        """Get all successful payments in a date range for reports."""
        stmt = (
            select(self.model)
            .where(
                self.model.school_id == school_id,
                self.model.status == "SUCCESS",
                func.date(self.model.created_at) >= from_date,
                func.date(self.model.created_at) <= to_date,
            )
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
