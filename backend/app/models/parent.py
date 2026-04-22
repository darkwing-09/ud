"""Parent Profile and Student-Parent Link models."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class ParentProfile(BaseModel):
    __tablename__ = "parent_profiles"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    relationship_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # FATHER | MOTHER | GUARDIAN
    occupation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    annual_income: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    school = relationship("School", backref="parent_profiles")
    user = relationship("User", backref="parent_profile")
    student_links = relationship("StudentParentLink", back_populates="parent", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class StudentParentLink(BaseModel):
    __tablename__ = "student_parent_links"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[UUID] = mapped_column(ForeignKey("parent_profiles.id", ondelete="CASCADE"), index=True)
    
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="parent_links")
    parent = relationship("ParentProfile", back_populates="student_links")
