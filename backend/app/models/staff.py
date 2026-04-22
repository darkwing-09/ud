"""Staff Profile model with encrypted PII fields."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel
from app.utils.encryption import encrypt_pii, decrypt_pii


class StaffProfile(SoftDeleteModel):
    __tablename__ = "staff_profiles"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    employee_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    
    personal_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    official_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_primary: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_secondary: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    department_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # PERMANENT | CONTRACT | PART_TIME
    join_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    qualification: Mapped[str | None] = mapped_column(String(500), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Encrypted PII
    aadhaar_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    pan_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_account_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    school = relationship("School", backref="staff_profiles")
    user = relationship("User", backref="staff_profile")
    department = relationship("Department", backref="staff")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    # Helpers for PII
    def set_aadhaar(self, value: str):
        self.aadhaar_encrypted = encrypt_pii(value)

    @property
    def aadhaar(self) -> str | None:
        return decrypt_pii(self.aadhaar_encrypted)

    def set_pan(self, value: str):
        self.pan_encrypted = encrypt_pii(value)

    @property
    def pan(self) -> str | None:
        return decrypt_pii(self.pan_encrypted)

    def set_bank_account(self, value: str):
        self.bank_account_encrypted = encrypt_pii(value)

    @property
    def bank_account(self) -> str | None:
        return decrypt_pii(self.bank_account_encrypted)
