"""Notice board and announcements models."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class Notice(SoftDeleteModel):
    """System-wide or targeted announcements."""
    __tablename__ = "notices"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Target audience filtering (empty = global)
    # roles: e.g. ["TEACHER", "STUDENT"]
    # sections: list of section UUIDs if targeted to specific classes
    audience_roles: Mapped[list[str]] = mapped_column(JSONB, default=list)
    audience_section_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    
    attachments: Mapped[list[dict]] = mapped_column(JSONB, default=list)  # List of {name, url}
    
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User")
