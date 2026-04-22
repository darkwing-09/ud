"""Payroll generation models."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class PayrollRecord(SoftDeleteModel):
    """Monthly payroll generation record for a staff member."""
    __tablename__ = "payroll_records"
    __table_args__ = (
        UniqueConstraint("staff_id", "month", "year", name="uq_payroll_staff_month"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    assignment_id: Mapped[UUID] = mapped_column(ForeignKey("staff_salary_assignments.id", ondelete="RESTRICT"))
    
    month: Mapped[int] = mapped_column(nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(nullable=False)
    
    # Working days & Attendance
    total_working_days: Mapped[int] = mapped_column(nullable=False)
    lop_days: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False, default=0.0)  # Loss of Pay days
    
    # Earnings snapshot
    basic_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    hra: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    da: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    allowances: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    gross_earnings: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Deductions snapshot
    lop_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    pf_deduction: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    esi_deduction: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    tax_deduction: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)  # TDS / PT
    advance_emi: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    total_deductions: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    net_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Config snapshot (just in case we need arbitrary breakdowns historically)
    breakdown_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", index=True)  # DRAFT, APPROVED, DISBURSED
    
    disbursed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    staff = relationship("StaffProfile", backref="payroll_records")
    assignment = relationship("StaffSalaryAssignment")
