"""Student API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.student import StudentProfileCreate, StudentProfileResponse, StudentProfileUpdate
from app.services.student import StudentService

router = APIRouter(prefix="/students", tags=["Student Management"])

def get_student_service(db: DBSession) -> StudentService:
    return StudentService(db)

@router.post(
    "",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll student"
)
async def create_student(
    school_id: SchoolScopedID,
    data: StudentProfileCreate,
    auth: User = Depends(require_school_admin),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    """Enroll a new student in the school."""
    return await service.create_student_profile(school_id, data)

@router.get(
    "",
    response_model=list[StudentProfileResponse],
    summary="List students"
)
async def list_students(
    school_id: SchoolScopedID,
    section_id: UUID | None = None,
    auth: User = Depends(require_school_admin),
    service: StudentService = Depends(get_student_service),
) -> list[StudentProfileResponse]:
    """List students in the school or a specific section."""
    return await service.list_students(school_id, section_id)

@router.get(
    "/{student_id}",
    response_model=StudentProfileResponse,
    summary="Get student profile"
)
async def get_student(
    school_id: SchoolScopedID,
    student_id: UUID,
    auth: User = Depends(require_school_admin),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    """Get detailed student profile."""
    student = await service.get_student_profile(student_id, school_id)
    return student

@router.patch(
    "/{student_id}",
    response_model=StudentProfileResponse,
    summary="Update student profile"
)
async def update_student(
    school_id: SchoolScopedID,
    student_id: UUID,
    data: StudentProfileUpdate,
    auth: User = Depends(require_school_admin),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    """Update student profile information."""
    updated = await service.update_student_profile(student_id, school_id, data)
    return updated
