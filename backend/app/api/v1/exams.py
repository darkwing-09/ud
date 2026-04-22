"""Examination and Results API endpoints."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.examination import (
    ExamCreate,
    ExamResponse,
    ExamResultBulkEntry,
    ExamResultResponse,
    GradeScaleCreate,
    GradeScaleResponse,
    StudentGPA,
)
from app.services.examination import ExaminationService

router = APIRouter(prefix="/exams", tags=["Examinations"])


def get_exam_service(db: DBSession) -> ExaminationService:
    return ExaminationService(db)


# ── Exam Management ──────────────────────────────────────────

@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def schedule_exam(
    school_id: SchoolScopedID,
    data: ExamCreate,
    auth: User = Depends(require_school_admin),
    service: ExaminationService = Depends(get_exam_service),
) -> ExamResponse:
    """Schedule a new school-wide exam."""
    return await service.create_exam(school_id, data)


@router.get("", response_model=list[ExamResponse])
async def list_exams(
    school_id: SchoolScopedID,
    academic_year_id: UUID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: ExaminationService = Depends(get_exam_service),
) -> list[ExamResponse]:
    """List exams for an academic year."""
    return await service.list_exams(school_id, academic_year_id)


# ── Grade Scale ──────────────────────────────────────────────

@router.post("/grade-scales", response_model=GradeScaleResponse, status_code=status.HTTP_201_CREATED)
async def create_grade_scale(
    school_id: SchoolScopedID,
    data: GradeScaleCreate,
    auth: User = Depends(require_school_admin),
    service: ExaminationService = Depends(get_exam_service),
) -> GradeScaleResponse:
    """Define a grading unit."""
    return await service.create_grade_scale(school_id, data)


@router.get("/grade-scales", response_model=list[GradeScaleResponse])
async def list_grade_scales(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER"])),
    service: ExaminationService = Depends(get_exam_service),
) -> list[GradeScaleResponse]:
    """Get all grading units."""
    return await service.get_grade_scales(school_id)


# ── Marks Entry ──────────────────────────────────────────────

@router.post("/{exam_id}/marks", response_model=list[ExamResultResponse])
async def enter_marks(
    school_id: SchoolScopedID,
    exam_id: UUID,
    data: ExamResultBulkEntry,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER"])),
    service: ExaminationService = Depends(get_exam_service),
) -> list[ExamResultResponse]:
    """Bulk mark entry for students in a subject."""
    # Safety check: exam_id in URL must match data
    data.exam_id = exam_id
    return await service.enter_marks(school_id, data, auth.id)


# ── Results & GPA ────────────────────────────────────────────

@router.get("/students/{student_id}/gpa", response_model=StudentGPA)
async def get_student_gpa(
    school_id: SchoolScopedID,
    student_id: UUID,
    academic_year_id: UUID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: ExaminationService = Depends(get_exam_service),
) -> StudentGPA:
    """Calculate and return student's GPA for the academic year."""
    return await service.calculate_student_gpa(school_id, student_id, academic_year_id)
