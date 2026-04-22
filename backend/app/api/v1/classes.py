"""Class and Section API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.academic_structure import (
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    SectionCreate,
    SectionResponse,
    SectionUpdate,
)
from app.services.academic_structure import AcademicStructureService

router = APIRouter(prefix="/classes", tags=["Academic Structure"])


def get_structure_service(db: DBSession) -> AcademicStructureService:
    return AcademicStructureService(db)


@router.post(
    "",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_class(
    school_id: SchoolScopedID,
    data: ClassCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> ClassResponse:
    """Create a new class for the active academic year."""
    return await service.create_class(school_id, data)


@router.get(
    "",
    response_model=list[ClassResponse],
)
async def list_classes(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> list[ClassResponse]:
    """List all classes for the active academic year."""
    return await service.list_classes(school_id)


@router.post(
    "/{class_id}/sections",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_section(
    school_id: SchoolScopedID,
    class_id: UUID,
    data: SectionCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> SectionResponse:
    """Create a section within a class."""
    return await service.create_section(school_id, class_id, data)


@router.get(
    "/{class_id}/sections",
    response_model=list[SectionResponse],
)
async def list_sections(
    school_id: SchoolScopedID,
    class_id: UUID,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> list[SectionResponse]:
    """List all sections for a class."""
    return await service.list_sections(school_id, class_id)
