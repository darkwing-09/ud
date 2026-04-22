"""Subject and Class-Subject Assignment models."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class Subject(SoftDeleteModel):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_subject_school_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="THEORY", nullable=False)  # THEORY | PRACTICAL | ELECTIVE

    # Relationships
    school = relationship("School", back_populates="subjects")
    assignments = relationship("ClassSubjectAssignment", back_populates="subject", cascade="all, delete-orphan")


class ClassSubjectAssignment(SoftDeleteModel):
    """Links subjects to classes/sections with teacher assignment."""
    __tablename__ = "class_subject_assignments"
    __table_args__ = (
        UniqueConstraint("class_id", "section_id", "subject_id", "academic_year_id", name="uq_class_subject_assign"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    class_id: Mapped[UUID] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"), index=True)
    section_id: Mapped[UUID | None] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    
    # teacher_id will be added after StaffProfile is implemented
    teacher_id: Mapped[UUID | None] = mapped_column(ForeignKey("staff_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    
    weekly_periods: Mapped[int] = mapped_column(Integer, default=4, nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="assignments")
    target_class = relationship("Class", back_populates="subject_assignments")
    section = relationship("Section", back_populates="subject_assignments")
