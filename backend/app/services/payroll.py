"""Payroll generation business logic service."""
from __future__ import annotations

import calendar
from datetime import date
from uuid import UUID

from sqlalchemy import select, and_

from app.core.deps import DBSession
from app.core.exceptions import NotFoundError, ValidationError
from app.db.repositories.payroll import PayrollRecordRepository
from app.db.repositories.salary import StaffSalaryAssignmentRepository, SalaryAdvanceRepository
from app.models.attendance import StaffAttendance
from app.models.payroll import PayrollRecord
from app.models.salary import SalaryStructure


class PayrollService:
    def __init__(self, session: DBSession):
        self.session = session
        self.payroll_repo = PayrollRecordRepository(session)
        self.assignment_repo = StaffSalaryAssignmentRepository(session)
        self.advance_repo = SalaryAdvanceRepository(session)

    async def _get_lop_days(self, school_id: UUID, staff_id: UUID, month: int, year: int) -> float:
        """Calculate total LOP (absent) days in the specified month."""
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        stmt = select(StaffAttendance).where(
            StaffAttendance.school_id == school_id,
            StaffAttendance.staff_id == staff_id,
            StaffAttendance.date >= start_date,
            StaffAttendance.date <= end_date,
            StaffAttendance.status == "ABSENT",
            StaffAttendance.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        absences = result.scalars().all()
        # Half day could be 0.5, but for now we assume 1.0 per absent record. Let's sum them up.
        lop_days = 0.0
        for entry in absences:
            # Check remarks/reason if it's half day, default to 1.
            if entry.remarks and "half" in entry.remarks.lower():
                lop_days += 0.5
            else:
                lop_days += 1.0
        return lop_days

    async def generate_monthly_payroll(self, school_id: UUID, month: int, year: int) -> list[PayrollRecord]:
        """Compute payroll for all active staff in a given month. Algorithmic heavy lifting."""
        # 1. Get all active staff assignments
        end_of_month = date(year, month, calendar.monthrange(year, month)[1])
        assignments = await self.assignment_repo.get_active_in_school(school_id, end_of_month)
        
        records_generated = []
        
        for assignment in assignments:
            # Check if record already generated
            existing_record = await self.payroll_repo.get_record(school_id, assignment.staff_id, month, year)
            if existing_record and existing_record.status != "DRAFT":
                continue  # Skip if already approved or disbursed
            if existing_record:
                # Evolve the existing draft
                record = existing_record
            else:
                record = PayrollRecord(
                    school_id=school_id,
                    staff_id=assignment.staff_id,
                    assignment_id=assignment.id,
                    month=month,
                    year=year
                )
                self.session.add(record)
            
            # Retrieve components
            # Mypy cannot guarantee relationship loading without selectinload, so let's query it
            stmt = select(SalaryStructure).where(
                SalaryStructure.id == assignment.structure_id,
                SalaryStructure.school_id == school_id
            )
            res = await self.session.execute(stmt)
            struct = res.scalar_one()

            total_working_days = end_of_month.day
            record.total_working_days = total_working_days
            
            # 2. Compute LOP Days
            lop_days = await self._get_lop_days(school_id, assignment.staff_id, month, year)
            record.lop_days = lop_days

            # 3. Base Earnings (Full month assumed initially)
            record.basic_salary = float(struct.basic_salary)
            record.hra = float(struct.hra)
            record.da = float(struct.da)
            record.allowances = float(struct.allowances)
            
            gross = record.basic_salary + record.hra + record.da + record.allowances
            record.gross_earnings = gross
            
            # 4. LOP Amount Deduction (Prorated off Gross)
            lop_amount = (gross / total_working_days) * lop_days
            record.lop_amount = round(lop_amount, 2)
            
            # 5. Statutory Deductions
            pf_deduction = (record.basic_salary * float(struct.pf_percentage)) / 100
            esi_deduction = ((gross - lop_amount) * float(struct.esi_percentage)) / 100
            record.pf_deduction = round(pf_deduction, 2)
            record.esi_deduction = round(esi_deduction, 2)
            record.tax_deduction = float(struct.professional_tax)
            
            # 6. Advances EMI
            advances = await self.advance_repo.get_active_advances_for_staff(school_id, assignment.staff_id)
            total_emi = 0.0
            for adv in advances:
                # Fast check if it falls in the correct timeline (ignoring total paid check for scaffolding simplicity)
                if adv.deduction_start_year < year or (adv.deduction_start_year == year and adv.deduction_start_month <= month):
                    total_emi += float(adv.emi_amount)
            
            record.advance_emi = total_emi
            
            # 7. Final Calculation
            total_ded = record.lop_amount + record.pf_deduction + record.esi_deduction + record.tax_deduction + record.advance_emi
            record.total_deductions = total_ded
            record.net_salary = max(0.0, record.gross_earnings - record.total_deductions)
            record.status = "DRAFT"
            
            # Snapshotting config
            record.breakdown_snapshot = {
                "structure_name": struct.name,
                "pf_percentage": float(struct.pf_percentage)
            }
            
            records_generated.append(record)

        await self.session.commit()
        return records_generated

    async def approve_record(self, school_id: UUID, record_id: UUID) -> PayrollRecord:
        record = await self.payroll_repo.get_by_id(record_id, school_id)
        if not record:
            raise NotFoundError("Payroll record not found")
            
        if record.status != "DRAFT":
            raise ValidationError("Only DRAFT records can be approved.")
            
        record.status = "APPROVED"
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def disburse_month(self, school_id: UUID, month: int, year: int) -> list[PayrollRecord]:
        records = await self.payroll_repo.get_by_month(school_id, month, year)
        disbursed = []
        today = date.today()
        
        for r in records:
            if r.status == "APPROVED":
                r.status = "DISBURSED"
                r.disbursed_at = today
                disbursed.append(r)
                
        await self.session.commit()
        # Side effect: Celery dispatches payslip PDFs here
        return disbursed
