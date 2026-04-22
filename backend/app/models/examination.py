"""Examination and Grading models."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class GradeScale(SoftDeleteModel):
    """Defines the grading system for a school (e.g., A=90-100)."""
    __tablename__ = "grade_scales"
    __table_args__ = (
        UniqueConstraint("school_id", "grade", "name", name="uq_grade_scale_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)  # e.g., "Primary", "High School"
    
    grade: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., "A+", "B"
    min_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    max_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    point_value: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)  # for GPA (e.g., 4.0)
    
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Exam(SoftDeleteModel):
    """Specific exam or assessment event."""
    __tablename__ = "exams"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    term_id: Mapped[UUID | None] = mapped_column(ForeignKey("academic_terms.id", ondelete="SET NULL"), nullable=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # FORMATIVE, SUMMATIVE, FINAL
    
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relationships
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")


class ExamResult(SoftDeleteModel):
    """Marks obtained by a student in a specific exam and subject."""
    __tablename__ = "exam_results"
    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", "subject_id", name="uq_exam_result_entry"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    exam_id: Mapped[UUID] = mapped_column(ForeignKey("exams.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    
    marks_obtained: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    max_marks: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    
    grade_id: Mapped[UUID | None] = mapped_column(ForeignKey("grade_scales.id", ondelete="SET NULL"), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    published: Mapped[bool] = mapped_column(default=False)
    entered_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

    # Relationships
    exam = relationship("Exam", back_populates="results")
    student = relationship("StudentProfile", backref="exam_results")
    subject = relationship("Subject", backref="exam_results")
    grade = relationship("GradeScale")
