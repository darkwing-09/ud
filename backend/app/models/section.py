"""Section model for dividing classes into smaller groups."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class Section(SoftDeleteModel):
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("class_id", "name", name="uq_section_class_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    class_id: Mapped[UUID] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String(10), nullable=False)  # "A", "B", "C"
    max_strength: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
    
    # class_teacher_id will be added after StaffProfile is implemented
    class_teacher_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)

    # Relationships
    parent_class = relationship("Class", back_populates="sections")
    subject_assignments = relationship("ClassSubjectAssignment", back_populates="section", cascade="all, delete-orphan")
