"""Department API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.academic_structure import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.academic_structure import AcademicStructureService

router = APIRouter(prefix="/departments", tags=["Academic Structure"])


def get_structure_service(db: DBSession) -> AcademicStructureService:
    return AcademicStructureService(db)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    school_id: SchoolScopedID,
    data: DepartmentCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> DepartmentResponse:
    """Create a new department."""
    return await service.create_department(school_id, data)


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
async def list_departments(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: AcademicStructureService = Depends(get_structure_service),
) -> list[DepartmentResponse]:
    """List all departments for the school."""
    return await service.list_departments(school_id)
