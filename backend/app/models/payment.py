"""FeePayment model — immutable financial transaction record."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.fee import FeeDue
    from app.models.student import StudentProfile
    from app.models.user import User


class FeePayment(Base, UUIDMixin):
    """
    Immutable payment record. Once status=SUCCESS, no fields may be updated.
    No deleted_at — financials are never soft-deleted.
    No updated_at — immutable after creation.
    """
    __tablename__ = "fee_payments"

    school_id: Mapped[UUID] = mapped_column(
        ForeignKey("schools.id", ondelete="CASCADE"), index=True, nullable=False
    )
    student_id: Mapped[UUID] = mapped_column(
        ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    fee_due_id: Mapped[UUID] = mapped_column(
        ForeignKey("fee_dues.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    # ONLINE | CASH | CHEQUE | UPI
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    # PENDING | SUCCESS | FAILED | REFUNDED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", index=True)

    # Razorpay fields
    gateway_order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gateway_payment_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    gateway_signature: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Receipt
    receipt_number: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # For cash/cheque — who recorded it
    recorded_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Immutable audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    fee_due: Mapped["FeeDue"] = relationship("FeeDue", back_populates="payments")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", backref="fee_payments")
    recorded_by: Mapped["User"] = relationship("User", foreign_keys=[recorded_by_id])
