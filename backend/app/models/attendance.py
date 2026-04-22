"""Attendance models for students and staff."""
from __future__ import annotations

from datetime import date, time
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class StudentAttendance(SoftDeleteModel):
    """Daily attendance record for students."""
    __tablename__ = "student_attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_attendance_date"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True)
    
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # PRESENT | ABSENT | LATE | EXCUSED
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    student = relationship("StudentProfile", backref="attendance_records")
    section = relationship("Section", backref="attendance_records")


class StaffAttendance(SoftDeleteModel):
    """Daily attendance record for staff members."""
    __tablename__ = "staff_attendance"
    __table_args__ = (
        UniqueConstraint("staff_id", "date", name="uq_staff_attendance_date"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    staff_id: Mapped[UUID] = mapped_column(ForeignKey("staff_profiles.id", ondelete="CASCADE"), index=True)
    
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # PRESENT | ABSENT | LATE | ON_LEAVE
    
    check_in: Mapped[time | None] = mapped_column(Time, nullable=True)
    check_out: Mapped[time | None] = mapped_column(Time, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    staff = relationship("StaffProfile", backref="attendance_records")
