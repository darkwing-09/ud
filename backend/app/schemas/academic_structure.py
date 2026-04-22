"""Academic Structure schemas (Department, Class, Section, Subject)."""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ── Department ──────────────────────────────────────────────────
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    head_staff_id: UUID | None = None


class DepartmentResponse(DepartmentBase):
    id: UUID
    school_id: UUID
    head_staff_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


# ── Class ──────────────────────────────────────────────────
class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    numeric_level: int = Field(..., ge=0, le=15)


class ClassCreate(ClassBase):
    department_id: UUID | None = None


class ClassUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    numeric_level: int | None = Field(None, ge=0, le=15)
    department_id: UUID | None = None


class ClassResponse(ClassBase):
    id: UUID
    school_id: UUID
    academic_year_id: UUID
    department_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


# ── Section ──────────────────────────────────────────────────
class SectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=10)
    max_strength: int = Field(40, ge=1, le=200)


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=10)
    max_strength: int | None = Field(None, ge=1, le=200)
    class_teacher_id: UUID | None = None


class SectionResponse(SectionBase):
    id: UUID
    school_id: UUID
    class_id: UUID
    class_teacher_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


# ── Subject ──────────────────────────────────────────────────
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str | None = Field(None, max_length=50)
    type: str = Field("THEORY", pattern="^(THEORY|PRACTICAL|ELECTIVE)$")


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    code: str | None = Field(None, max_length=50)
    type: str | None = Field(None, pattern="^(THEORY|PRACTICAL|ELECTIVE)$")


class SubjectResponse(SubjectBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── ClassSubjectAssignment ────────────────────────────────────
class ClassSubjectAssignmentBase(BaseModel):
    weekly_periods: int = Field(4, ge=1, le=20)


class ClassSubjectAssignmentCreate(ClassSubjectAssignmentBase):
    subject_id: UUID
    section_id: UUID | None = None  # NULL = all sections of the class


class ClassSubjectAssignmentUpdate(BaseModel):
    weekly_periods: int | None = Field(None, ge=1, le=20)
    teacher_id: UUID | None = None


class ClassSubjectAssignmentResponse(ClassSubjectAssignmentBase):
    id: UUID
    school_id: UUID
    academic_year_id: UUID
    class_id: UUID
    section_id: UUID | None
    subject_id: UUID
    teacher_id: UUID | None

    model_config = ConfigDict(from_attributes=True)
