"""Audit logging model."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class AuditLog(Base, UUIDMixin):
    """
    Tracks every write operation in the system.
    Immutable record.
    """
    __tablename__ = "audit_logs"

    school_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # login, create_student, update_fee, delete_staff etc.
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # student, fee_due, attendance etc.
    module: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # ID of the entity being modified
    entity_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    
    # Payload before and after changes
    before_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    school = relationship("School", foreign_keys=[school_id])
