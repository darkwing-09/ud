"""Fee Management models — structures, assignments, discounts, dues."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, SoftDeleteModel

if TYPE_CHECKING:
    from app.models.payment import FeePayment
    from app.models.student import StudentProfile


class FeeStructure(SoftDeleteModel):
    """Template defining a fee collection plan for a class/academic year."""
    __tablename__ = "fee_structures"

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        ForeignKey("academic_years.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # MONTHLY | QUARTERLY | ANNUAL | ONE_TIME
    frequency: Mapped[str] = mapped_column(String(50), nullable=False, default="MONTHLY")
    # Day of month the payment is due (1-28), NULL for ONE_TIME
    due_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    late_fee_per_day: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    max_late_fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    # Relationships
    components: Mapped[list["FeeComponent"]] = relationship(
        "FeeComponent", back_populates="structure", cascade="all, delete-orphan",
        lazy="selectin"
    )
    assignments: Mapped[list["FeeAssignment"]] = relationship(
        "FeeAssignment", back_populates="structure", cascade="all, delete-orphan"
    )
    dues: Mapped[list["FeeDue"]] = relationship(
        "FeeDue", back_populates="structure"
    )


class FeeComponent(BaseModel):
    """Individual line-item in a fee structure (e.g., Tuition, Transport)."""
    __tablename__ = "fee_components"

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    fee_structure_id: Mapped[UUID] = mapped_column(
        ForeignKey("fee_structures.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    structure: Mapped["FeeStructure"] = relationship("FeeStructure", back_populates="components")


class FeeAssignment(BaseModel):
    """Links a FeeStructure to a class, section, or individual student."""
    __tablename__ = "fee_assignments"
    __table_args__ = (
        UniqueConstraint(
            "fee_structure_id", "class_id", "section_id", "student_id",
            name="uq_fee_assignment"
        ),
    )

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    fee_structure_id: Mapped[UUID] = mapped_column(
        ForeignKey("fee_structures.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Exactly one of these should be non-null (enforced in service layer)
    class_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("classes.id", ondelete="CASCADE"), index=True, nullable=True
    )
    section_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("sections.id", ondelete="CASCADE"), index=True, nullable=True
    )
    student_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=True
    )

    # Relationships
    structure: Mapped["FeeStructure"] = relationship("FeeStructure", back_populates="assignments")


class FeeDiscount(SoftDeleteModel):
    """Reusable discount definitions (e.g., Sibling Discount, Staff Ward)."""
    __tablename__ = "fee_discounts"

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # PERCENTAGE | FIXED
    discount_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # TOTAL | COMPONENT
    applicable_on: Mapped[str] = mapped_column(String(50), default="TOTAL", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    student_discounts: Mapped[list["StudentFeeDiscount"]] = relationship(
        "StudentFeeDiscount", back_populates="discount"
    )


class StudentFeeDiscount(BaseModel):
    """Applied discount for a specific student."""
    __tablename__ = "student_fee_discounts"

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    discount_id: Mapped[UUID] = mapped_column(
        ForeignKey("fee_discounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    discount: Mapped["FeeDiscount"] = relationship("FeeDiscount", back_populates="student_discounts")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", backref="fee_discounts")


class FeeDue(SoftDeleteModel):
    """A specific payment obligation for a student in a given period."""
    __tablename__ = "fee_dues"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "fee_structure_id", "period_label",
            name="uq_fee_due_period"
        ),
    )

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    fee_structure_id: Mapped[UUID] = mapped_column(
        ForeignKey("fee_structures.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # e.g., "April 2025", "Q1 2025-26", "Annual 2025-26"
    period_label: Mapped[str] = mapped_column(String(100), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    base_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    late_fee_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    net_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    # UNPAID | PARTIAL | PAID | WAIVED
    status: Mapped[str] = mapped_column(
        String(50), default="UNPAID", nullable=False, index=True
    )

    # Relationships
    structure: Mapped["FeeStructure"] = relationship("FeeStructure", back_populates="dues")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", backref="fee_dues")
    payments: Mapped[list["FeePayment"]] = relationship(
        "FeePayment", back_populates="fee_due"
    )
