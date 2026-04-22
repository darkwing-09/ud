"""Subject and Assignment API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.academic_structure import (
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
    ClassSubjectAssignmentCreate,
    ClassSubjectAssignmentResponse,
)
from app.services.academic_structure import AcademicStructureService

router = APIRouter(prefix="/subjects", tags=["Academic Structure"])


def get_structure_service(db: DBSession) -> AcademicStructureService:
    return AcademicStructureService(db)


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_subject(
    school_id: SchoolScopedID,
    data: SubjectCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> SubjectResponse:
    """Create a new subject."""
    return await service.create_subject(school_id, data)


@router.get(
    "",
    response_model=list[SubjectResponse],
)
async def list_subjects(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> list[SubjectResponse]:
    """List all subjects for the school."""
    return await service.list_subjects(school_id)


@router.post(
    "/assignments/{class_id}",
    response_model=ClassSubjectAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_subject(
    school_id: SchoolScopedID,
    class_id: UUID,
    data: ClassSubjectAssignmentCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> ClassSubjectAssignmentResponse:
    """Assign a subject to a class or specific section."""
    return await service.assign_subject(school_id, class_id, data)
