"""Timetable and Scheduling models."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class TimetableSlot(SoftDeleteModel):
    """Defines a period or time slot in the school day."""
    __tablename__ = "timetable_slots"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_slot_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., Period 1, Lunch Break
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    is_break: Mapped[bool] = mapped_column(default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    school = relationship("School", backref="timetable_slots")


class TimetableEntry(SoftDeleteModel):
    """A specific entry in the timetable linking subject, teacher, and slot."""
    __tablename__ = "timetable_entries"
    __table_args__ = (
        UniqueConstraint("section_id", "slot_id", "day_of_week", "academic_year_id", name="uq_timetable_slot_day"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), index=True)
    
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    slot_id: Mapped[UUID] = mapped_column(ForeignKey("timetable_slots.id", ondelete="CASCADE"), index=True)
    
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    room_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    section = relationship("Section", backref="timetable")
    subject = relationship("Subject", backref="timetable_entries")
    teacher = relationship("StaffProfile", backref="timetable_entries")
    slot = relationship("TimetableSlot", backref="entries")
