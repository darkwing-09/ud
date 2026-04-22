"""School model — tenant root entity."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class School(SoftDeleteModel):
    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)  # Tenant identifier / subdomain

    # Contact Info
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Leadership
    principal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Academic
    affiliation: Mapped[str | None] = mapped_column(String(255), nullable=True)  # CBSE, ICSE, etc.
    affiliation_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Platform status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    subscription_plan: Mapped[str] = mapped_column(String(50), default="BASIC", nullable=False)

    # Flexible settings: attendance threshold, late fee rules, grading type, etc.
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    users = relationship("User", backref="school", cascade="all, delete-orphan")
    academic_years = relationship("AcademicYear", back_populates="school", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="school", cascade="all, delete-orphan")
    classes = relationship("Class", back_populates="school", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="school", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<School id={self.id} code={self.code} name={self.name}>"

    @property
    def attendance_threshold(self) -> int:
        return self.settings.get("min_attendance_percentage", 75)

    @property
    def late_fee_per_day(self) -> float:
        return self.settings.get("late_fee_per_day", 10.0)
