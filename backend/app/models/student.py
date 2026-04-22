"""Student Profile model."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel
from app.utils.encryption import encrypt_pii, decrypt_pii


class StudentProfile(SoftDeleteModel):
    __tablename__ = "student_profiles"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    
    admission_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    religion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    caste_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    current_section_id: Mapped[UUID | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year_id: Mapped[UUID] = mapped_column(ForeignKey("academic_years.id", ondelete="CASCADE"), index=True)
    
    roll_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    previous_school: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Encrypted PII
    aadhaar_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE | INACTIVE | ALUMNI | TRANSFERRED

    # Relationships
    school = relationship("School", backref="student_profiles")
    user = relationship("User", backref="student_profile")
    section = relationship("Section", backref="students")
    parent_links = relationship("StudentParentLink", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_aadhaar(self, value: str):
        self.aadhaar_encrypted = encrypt_pii(value)

    @property
    def aadhaar(self) -> str | None:
        return decrypt_pii(self.aadhaar_encrypted)
