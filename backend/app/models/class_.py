"""Class model representing a grade level or vertical group."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class Class(SoftDeleteModel):
    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint("school_id", "academic_year_id", "name", name="uq_class_school_year_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    department_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Grade 10"
    numeric_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12 for sorting
    
    # Relationships
    school = relationship("School", back_populates="classes")
    department = relationship("Department", back_populates="classes")
    sections = relationship("Section", back_populates="parent_class", cascade="all, delete-orphan")
    subject_assignments = relationship("ClassSubjectAssignment", back_populates="target_class", cascade="all, delete-orphan")
