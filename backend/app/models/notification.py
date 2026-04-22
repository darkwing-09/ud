"""Notification models."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class NotificationTemplate(SoftDeleteModel):
    """Jinja2 templates for emails, SMS, and in-app notifications."""
    __tablename__ = "notification_templates"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    
    # Event that triggers this template e.g., "fee.payment.success", "attendance.absent"
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    
    # "EMAIL", "SMS", "IN_APP"
    channel: Mapped[str] = mapped_column(String(50))
    
    title_template: Mapped[str] = mapped_column(String(200), nullable=True) # Used for email subject or in-app title
    body_template: Mapped[str] = mapped_column(Text)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Notification(SoftDeleteModel):
    """In-app notifications sent to specific users."""
    __tablename__ = "notifications"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Reference to original event type
    notification_type: Mapped[str] = mapped_column(String(100))
    
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    
    # Optional metadata (e.g., {"fee_id": "...", "amount": 500})
    action_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User")
