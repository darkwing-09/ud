"""Salary and payroll structure models."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class SalaryStructure(SoftDeleteModel):
    """A salary structure/template that can be assigned to multiple staff members."""
    __tablename__ = "salary_structures"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_salary_structure_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Senior Teacher Level 1"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    basic_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    hra: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)  # House Rent Allowance
    da: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)  # Dearness Allowance
    allowances: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)  # Other explicit allowances
    
    # Statutory Deductions
    pf_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=12.0)  # Usually 12% of basic
    esi_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    professional_tax: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StaffSalaryAssignment(SoftDeleteModel):
    """Maps a staff member to a salary structure with an effective date."""
    __tablename__ = "staff_salary_assignments"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    structure_id: Mapped[UUID] = mapped_column(ForeignKey("salary_structures.id", ondelete="CASCADE"))
    
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_until: Mapped[date | None] = mapped_column(Date, nullable=True)  # Null means currently active
    
    # Relationships
    staff = relationship("StaffProfile", backref="salary_assignments")
    structure = relationship("SalaryStructure")


class SalaryAdvance(SoftDeleteModel):
    """Tracks salary advance requests and EMI plans."""
    __tablename__ = "salary_advances"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    emi_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    deduction_start_month: Mapped[int] = mapped_column(nullable=False)
    deduction_start_year: Mapped[int] = mapped_column(nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED, COMPLETED
    
    approved_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    staff = relationship("StaffProfile", backref="salary_advances")
    approved_by = relationship("User")
