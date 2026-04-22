"""Department model for grouping classes and staff."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class Department(SoftDeleteModel):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_department_name"),
    )

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # head_staff_id will be added in Phase 1.3 or 1.4 after StaffProfile is implemented
    head_staff_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)

    # Relationships
    school = relationship("School", back_populates="departments")
    classes = relationship("Class", back_populates="department")
