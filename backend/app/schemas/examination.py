"""Examination and Grading schemas."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ── GradeScale ──────────────────────────────────────────────────

class GradeScaleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    grade: str = Field(..., min_length=1, max_length=10)
    min_score: float = Field(..., ge=0, le=100)
    max_score: float = Field(..., ge=0, le=100)
    point_value: float = Field(..., ge=0, le=10)
    description: str | None = Field(None, max_length=500)


class GradeScaleCreate(GradeScaleBase):
    pass


class GradeScaleResponse(GradeScaleBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── Exam ──────────────────────────────────────────────────────

class ExamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field("SUMMATIVE", pattern="^(FORMATIVE|SUMMATIVE|FINAL)$")
    start_date: date
    end_date: date
    term_id: UUID | None = None


class ExamCreate(ExamBase):
    academic_year_id: UUID


class ExamResponse(ExamBase):
    id: UUID
    school_id: UUID
    academic_year_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── ExamResult ──────────────────────────────────────────────────

class ExamResultBase(BaseModel):
    marks_obtained: float = Field(..., ge=0)
    max_marks: float = Field(..., gt=0)
    remarks: str | None = Field(None, max_length=500)


class ExamResultCreate(ExamResultBase):
    exam_id: UUID
    student_id: UUID
    subject_id: UUID


class ExamResultBulkEntry(BaseModel):
    exam_id: UUID
    subject_id: UUID
    results: list[ExamResultCreate]


class ExamResultResponse(ExamResultBase):
    id: UUID
    school_id: UUID
    exam_id: UUID
    student_id: UUID
    subject_id: UUID
    grade_id: UUID | None
    published: bool

    model_config = ConfigDict(from_attributes=True)


# ── GPA & Performance ──────────────────────────────────────────

class StudentGPA(BaseModel):
    student_id: UUID
    academic_year_id: UUID
    gpa: float
    total_marks: float
    max_total_marks: float
    percentage: float
