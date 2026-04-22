"""Homework assignment models."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class HomeworkAssignment(SoftDeleteModel):
    """Homework assigned by teachers to specific sections."""
    __tablename__ = "homework_assignments"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[list[dict]] = mapped_column(JSONB, default=list)

    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    section = relationship("Section")
    subject = relationship("Subject")
    teacher = relationship("StaffProfile")
