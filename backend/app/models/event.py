"""School event models."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import SoftDeleteModel


class SchoolEvent(SoftDeleteModel):
    """Events in the school calendar."""
    __tablename__ = "school_events"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # E.g., EXAM, SPORTS, HOLIDAY, MEETING
    event_type: Mapped[str] = mapped_column(String(50), default="GENERAL")
