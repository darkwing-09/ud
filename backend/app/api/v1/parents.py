"""Parent API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.parent import ParentProfileCreate, ParentProfileResponse, StudentParentLinkCreate, StudentParentLinkResponse
from app.services.parent import ParentService

router = APIRouter(prefix="/parents", tags=["Parent Management"])

def get_parent_service(db: DBSession) -> ParentService:
    return ParentService(db)

@router.post(
    "",
    response_model=ParentProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create parent profile"
)
async def create_parent(
    school_id: SchoolScopedID,
    data: ParentProfileCreate,
    auth: User = Depends(require_school_admin),
    service: ParentService = Depends(get_parent_service),
) -> ParentProfileResponse:
    """Create a new parent profile."""
    return await service.create_parent_profile(school_id, data)

@router.post(
    "/link",
    response_model=StudentParentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link parent to student"
)
async def link_parent_student(
    school_id: SchoolScopedID,
    data: StudentParentLinkCreate,
    auth: User = Depends(require_school_admin),
    service: ParentService = Depends(get_parent_service),
) -> StudentParentLinkResponse:
    """Link a parent to a student."""
    link = await service.link_student_parent(school_id, data)
    return StudentParentLinkResponse.from_orm(link)

@router.get(
    "/student/{student_id}",
    response_model=list[StudentParentLinkResponse],
    summary="List student parents"
)
async def list_student_parents(
    student_id: UUID,
    auth: User = Depends(require_school_admin),
    service: ParentService = Depends(get_parent_service),
) -> list[StudentParentLinkResponse]:
    """List all parents linked to a student."""
    return await service.list_student_parents(student_id)
