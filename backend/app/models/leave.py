"""Leave management and Holiday models."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class LeaveType(SoftDeleteModel):
    """Types of leaves available in the school (e.g., Casual, Sick, Maternity)."""
    __tablename__ = "leave_types"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_leave_type_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Defaults for annual allocation logic
    default_days_per_year: Mapped[float] = mapped_column(Numeric(4, 1), default=0.0)


class StaffLeaveBalance(SoftDeleteModel):
    """Tracks available and used leave balances for a staff member per year."""
    __tablename__ = "staff_leave_balances"
    __table_args__ = (
        UniqueConstraint("staff_id", "leave_type_id", "year", name="uq_staff_leave_balance"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    leave_type_id: Mapped[UUID] = mapped_column(ForeignKey("leave_types.id", ondelete="CASCADE"))
    
    year: Mapped[int] = mapped_column(nullable=False)
    
    allocated_days: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False, default=0.0)
    used_days: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False, default=0.0)
    
    # Relationships
    staff = relationship("StaffProfile", backref="leave_balances")
    leave_type = relationship("LeaveType")


class LeaveApplication(SoftDeleteModel):
    """Staff leave request workflow."""
    __tablename__ = "leave_applications"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    leave_type_id: Mapped[UUID] = mapped_column(ForeignKey("leave_types.id", ondelete="RESTRICT"))
    
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # In case from_date == to_date and it's a half day
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False)
    
    actual_leave_days: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)  # Computed excluding holidays
    
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED
    
    reviewed_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewer_comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    staff = relationship("StaffProfile", backref="leave_applications")
    leave_type = relationship("LeaveType")
    reviewed_by = relationship("User")


class Holiday(SoftDeleteModel):
    """School-wide holidays that don't count towards leave consumption."""
    __tablename__ = "holidays"
    __table_args__ = (
        UniqueConstraint("school_id", "date", name="uq_school_holiday_date"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
