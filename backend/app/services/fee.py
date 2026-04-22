"""Fee Management Service — structure lifecycle, due generation, discount engine."""
from __future__ import annotations

import calendar
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.repositories.fee import (
    FeeAssignmentRepository,
    FeeDiscountRepository,
    FeeDueRepository,
    FeeStructureRepository,
)
from app.db.repositories.student import StudentRepository
from app.models.fee import FeeAssignment, FeeComponent, FeeDue, FeeStructure
from app.models.student import StudentProfile
from app.schemas.fee import (
    ApplyDiscountRequest,
    FeeAssignRequest,
    FeeDiscountCreate,
    FeeStructureCreate,
    FeeStructureUpdate,
    LateFeeWaiveRequest,
    StudentFeeOverview,
)


class FeeStructureService:
    """Handles FeeStructure CRUD, assignment, and discount management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = FeeStructureRepository(session)
        self.assignment_repo = FeeAssignmentRepository(session)
        self.discount_repo = FeeDiscountRepository(session)
        self.student_repo = StudentRepository(session)
        self.due_repo = FeeDueRepository(session)

    # ── FeeStructure CRUD ──────────────────────────────────────────────────

    async def create_structure(
        self, school_id: UUID, data: FeeStructureCreate
    ) -> FeeStructure:
        """Create a fee structure with its components in a single transaction."""
        async with self.session.begin():
            structure = FeeStructure(
                school_id=school_id,
                academic_year_id=data.academic_year_id,
                name=data.name,
                frequency=data.frequency,
                due_day=data.due_day,
                late_fee_per_day=data.late_fee_per_day,
                max_late_fee=data.max_late_fee,
            )
            self.session.add(structure)
            await self.session.flush()

            for comp in data.components:
                component = FeeComponent(
                    school_id=school_id,
                    fee_structure_id=structure.id,
                    name=comp.name,
                    amount=comp.amount,
                    is_mandatory=comp.is_mandatory,
                )
                self.session.add(component)

            await self.session.flush()
            await self.session.refresh(structure)
        return structure

    async def list_structures(
        self, school_id: UUID, academic_year_id: UUID
    ) -> list[FeeStructure]:
        """List all fee structures for an academic year."""
        return await self.repo.get_by_academic_year(school_id, academic_year_id)

    async def get_structure(self, school_id: UUID, structure_id: UUID) -> FeeStructure:
        """Get a single fee structure with components."""
        return await self.repo.get_by_id(structure_id, school_id)

    async def update_structure(
        self, school_id: UUID, structure_id: UUID, data: FeeStructureUpdate
    ) -> FeeStructure:
        """Update fee structure metadata. Block if active dues exist."""
        structure = await self.repo.get_by_id(structure_id, school_id)
        if await self.repo.has_active_dues(school_id, structure_id):
            raise ConflictError(
                "Cannot edit fee structure: active dues already generated. "
                "Create a new structure instead."
            )
        update_data = data.model_dump(exclude_none=True)
        async with self.session.begin():
            return await self.repo.update(structure, **update_data)

    async def delete_structure(self, school_id: UUID, structure_id: UUID) -> None:
        """Soft-delete structure. Block if dues exist."""
        structure = await self.repo.get_by_id(structure_id, school_id)
        if await self.repo.has_active_dues(school_id, structure_id):
            raise ConflictError(
                "Cannot delete fee structure: dues have been generated. "
                "Soft-delete is blocked to preserve financial integrity."
            )
        async with self.session.begin():
            await self.repo.soft_delete(structure)

    # ── Assignment + Due Generation ────────────────────────────────────────

    async def assign_structure(
        self,
        school_id: UUID,
        structure_id: UUID,
        data: FeeAssignRequest,
    ) -> tuple[FeeAssignment, int]:
        """
        Assign a fee structure to a class/section/student and generate dues.
        Returns (assignment, dues_generated_count).
        """
        structure = await self.repo.get_by_id(structure_id, school_id)

        # Duplicate check
        if await self.assignment_repo.duplicate_exists(
            school_id, structure_id, data.class_id, data.section_id, data.student_id
        ):
            raise ConflictError("This fee structure has already been assigned to this target.")

        async with self.session.begin():
            assignment = FeeAssignment(
                school_id=school_id,
                fee_structure_id=structure_id,
                class_id=data.class_id,
                section_id=data.section_id,
                student_id=data.student_id,
            )
            self.session.add(assignment)
            await self.session.flush()

            # Resolve target students
            students = await self._resolve_students(school_id, data)

            dues_count = 0
            for student in students:
                count = await self._generate_dues_for_student(
                    school_id, structure, student
                )
                dues_count += count

        return assignment, dues_count

    async def _resolve_students(
        self, school_id: UUID, data: FeeAssignRequest
    ) -> list[StudentProfile]:
        """Resolve the set of students to generate dues for."""
        if data.student_id:
            student = await self.student_repo.get_by_id(data.student_id, school_id)
            return [student]

        if data.section_id:
            return await self.student_repo.list_by_section(school_id, data.section_id)

        if data.class_id:
            # Get all sections for this class, then all students
            from sqlalchemy import select as sa_select
            from app.models.section import Section
            stmt = sa_select(Section).where(
                Section.class_id == data.class_id,
                Section.deleted_at.is_(None),
            )
            result = await self.session.execute(stmt)
            sections = result.scalars().all()
            students: list[StudentProfile] = []
            for section in sections:
                section_students = await self.student_repo.list_by_section(school_id, section.id)
                students.extend(section_students)
            return students

        return []

    async def _generate_dues_for_student(
        self,
        school_id: UUID,
        structure: FeeStructure,
        student: StudentProfile,
    ) -> int:
        """
        Generate period-wise FeeDue records for a student based on frequency.
        Returns number of dues created.
        """
        base_amount = sum(
            float(c.amount) for c in structure.components if c.is_mandatory
        )

        # Apply student discounts
        discount_amount = await self._compute_discount(school_id, student.id, base_amount)
        net_amount = max(0.0, base_amount - discount_amount)

        periods = self._compute_periods(structure)
        created = 0
        for period_label, due_date in periods:
            # Idempotency: skip if already exists
            if await self.due_repo.exists_for_period(
                school_id, student.id, structure.id, period_label
            ):
                continue

            due = FeeDue(
                school_id=school_id,
                student_id=student.id,
                fee_structure_id=structure.id,
                period_label=period_label,
                due_date=due_date,
                base_amount=base_amount,
                discount_amount=discount_amount,
                late_fee_amount=0.0,
                net_amount=net_amount,
                paid_amount=0.0,
                status="UNPAID",
            )
            self.session.add(due)
            created += 1

        return created

    def _compute_periods(
        self, structure: FeeStructure
    ) -> list[tuple[str, date]]:
        """
        Compute (period_label, due_date) pairs for the academic year
        based on frequency. Uses current calendar year as approximation.
        """
        today = date.today()
        year = today.year
        due_day = structure.due_day or 1
        freq = structure.frequency

        if freq == "ONE_TIME":
            label = f"One-Time {year}"
            d = date(year, today.month, min(due_day, 28))
            return [(label, d)]

        if freq == "MONTHLY":
            months = [
                "April", "May", "June", "July", "August", "September",
                "October", "November", "December", "January", "February", "March",
            ]
            # Academic year: Apr–Mar
            result = []
            for i, month_name in enumerate(months):
                m = (i + 4) % 12 or 12  # Apr=4, ..., Mar=3
                y = year if m >= 4 else year + 1
                last_day = calendar.monthrange(y, m)[1]
                d = date(y, m, min(due_day, last_day))
                result.append((f"{month_name} {y}", d))
            return result

        if freq == "QUARTERLY":
            quarters = [
                ("Q1 Apr–Jun", 4, year),
                ("Q2 Jul–Sep", 7, year),
                ("Q3 Oct–Dec", 10, year),
                ("Q4 Jan–Mar", 1, year + 1),
            ]
            result = []
            for label, month, y in quarters:
                last_day = calendar.monthrange(y, month)[1]
                d = date(y, month, min(due_day, last_day))
                result.append((label, d))
            return result

        if freq == "ANNUAL":
            d = date(year, 4, min(due_day, 30))  # April (start of academic year)
            label = f"Annual {year}-{str(year + 1)[-2:]}"
            return [(label, d)]

        return []

    async def _compute_discount(
        self, school_id: UUID, student_id: UUID, base_amount: float
    ) -> float:
        """Sum all applicable discounts for a student."""
        student_discounts = await self.discount_repo.get_student_discounts(
            school_id, student_id
        )
        total_discount = 0.0
        for sd in student_discounts:
            disc = sd.discount
            if disc.discount_type == "PERCENTAGE":
                total_discount += base_amount * (float(disc.value) / 100)
            elif disc.discount_type == "FIXED":
                total_discount += float(disc.value)
        return min(total_discount, base_amount)

    # ── Discounts ──────────────────────────────────────────────────────────

    async def create_discount(
        self, school_id: UUID, data: FeeDiscountCreate
    ) -> "FeeDiscount":  # type: ignore[name-defined]
        from app.models.fee import FeeDiscount
        async with self.session.begin():
            discount = FeeDiscount(school_id=school_id, **data.model_dump())
            self.session.add(discount)
            await self.session.flush()
            await self.session.refresh(discount)
        return discount

    async def list_discounts(self, school_id: UUID) -> list["FeeDiscount"]:  # type: ignore[name-defined]
        from app.models.fee import FeeDiscount
        from sqlalchemy import select
        stmt = select(FeeDiscount).where(
            FeeDiscount.school_id == school_id,
            FeeDiscount.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def apply_discount_to_student(
        self,
        school_id: UUID,
        discount_id: UUID,
        data: ApplyDiscountRequest,
        approved_by_id: UUID,
    ) -> None:
        """Apply a discount to a student."""
        from app.models.fee import FeeDiscount, StudentFeeDiscount
        # Validate discount exists
        discount = await self.discount_repo.get_by_id(discount_id, school_id)
        # Validate student exists
        await self.student_repo.get_by_id(data.student_id, school_id)

        async with self.session.begin():
            link = StudentFeeDiscount(
                school_id=school_id,
                student_id=data.student_id,
                discount_id=discount_id,
                reason=data.reason,
                approved_by_id=approved_by_id,
            )
            self.session.add(link)

    # ── Student Fee Overview ────────────────────────────────────────────────

    async def get_student_overview(
        self, school_id: UUID, student_id: UUID
    ) -> StudentFeeOverview:
        """Aggregate fee summary for one student."""
        await self.student_repo.get_by_id(student_id, school_id)
        dues = await self.due_repo.get_student_dues(school_id, student_id)

        today = date.today()
        total_fees = sum(float(d.net_amount) + float(d.late_fee_amount) for d in dues)
        paid_amount = sum(float(d.paid_amount) for d in dues)
        outstanding = sum(
            max(0.0, float(d.net_amount) + float(d.late_fee_amount) - float(d.paid_amount))
            for d in dues
        )
        overdue = sum(
            max(0.0, float(d.net_amount) + float(d.late_fee_amount) - float(d.paid_amount))
            for d in dues
            if d.due_date < today and d.status not in ("PAID", "WAIVED")
        )

        return StudentFeeOverview(
            student_id=student_id,
            total_fees=round(total_fees, 2),
            paid_amount=round(paid_amount, 2),
            outstanding=round(outstanding, 2),
            overdue=round(overdue, 2),
            dues=dues,  # type: ignore[arg-type]
        )

    # ── Late Fee Computation ────────────────────────────────────────────────

    async def compute_and_apply_late_fee(
        self, school_id: UUID, due_id: UUID
    ) -> FeeDue:
        """Recompute late fee for a due based on days_overdue and structure config."""
        due = await self.due_repo.get_by_id(due_id, school_id)
        if due.status in ("PAID", "WAIVED"):
            return due

        structure = await self.repo.get_by_id(due.fee_structure_id, school_id)
        today = date.today()

        if today <= due.due_date:
            return due  # Not yet overdue

        days_overdue = (today - due.due_date).days
        raw_late_fee = days_overdue * float(structure.late_fee_per_day)
        max_late = float(structure.max_late_fee)
        late_fee = min(raw_late_fee, max_late) if max_late > 0 else raw_late_fee

        async with self.session.begin():
            due.late_fee_amount = late_fee
            self.session.add(due)
        return due

    async def waive_late_fee(
        self, school_id: UUID, due_id: UUID, data: LateFeeWaiveRequest
    ) -> FeeDue:
        """Zero out the late fee for a specific due (admin action)."""
        due = await self.due_repo.get_by_id(due_id, school_id)
        async with self.session.begin():
            due.late_fee_amount = 0.0
            self.session.add(due)
        return due

    # ── Defaulter Report ────────────────────────────────────────────────────

    async def get_defaulters(
        self,
        school_id: UUID,
        class_id: UUID | None = None,
        days_overdue_min: int = 1,
        amount_min: float = 0,
    ) -> list[dict]:
        """Return defaulter records with student and aging data."""
        return await self.due_repo.get_defaulters(
            school_id, class_id, days_overdue_min, amount_min
        )
