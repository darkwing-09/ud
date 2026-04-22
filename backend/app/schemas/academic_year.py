"""Academic Year and Term schemas."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


# ── Term ──────────────────────────────────────────────────
class TermBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    is_active: bool = True


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class TermResponse(TermBase):
    id: UUID
    academic_year_id: UUID

    class Config:
        from_attributes = True


# ── Academic Year ──────────────────────────────────────────
class AcademicYearBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    start_date: date
    end_date: date
    is_active: bool = False


class AcademicYearCreate(AcademicYearBase):
    pass


class AcademicYearUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class AcademicYearResponse(AcademicYearBase):
    id: UUID
    school_id: UUID
    terms: list[TermResponse] = []

    class Config:
        from_attributes = True
