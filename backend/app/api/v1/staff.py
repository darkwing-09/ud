"""Staff API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.staff import StaffProfileCreate, StaffProfileResponse, StaffProfileUpdate
from app.services.staff import StaffService

router = APIRouter(prefix="/staff", tags=["Staff Management"])

def get_staff_service(db: DBSession) -> StaffService:
    return StaffService(db)

@router.post(
    "",
    response_model=StaffProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create staff profile"
)
async def create_staff(
    school_id: SchoolScopedID,
    data: StaffProfileCreate,
    auth: User = Depends(require_school_admin),
    service: StaffService = Depends(get_staff_service),
) -> StaffProfileResponse:
    """Create a new staff profile for the school."""
    return await service.create_staff_profile(school_id, data)

@router.get(
    "",
    response_model=list[StaffProfileResponse],
    summary="List all staff"
)
async def list_staff(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: StaffService = Depends(get_staff_service),
) -> list[StaffProfileResponse]:
    """List all staff profiles in the school."""
    return await service.list_staff(school_id)

@router.get(
    "/{staff_id}",
    response_model=StaffProfileResponse,
    summary="Get staff profile"
)
async def get_staff(
    school_id: SchoolScopedID,
    staff_id: UUID,
    auth: User = Depends(require_school_admin),
    service: StaffService = Depends(get_staff_service),
) -> StaffProfileResponse:
    """Get detailed staff profile."""
    staff = await service.get_staff_profile(staff_id, school_id)
    return staff

@router.patch(
    "/{staff_id}",
    response_model=StaffProfileResponse,
    summary="Update staff profile"
)
async def update_staff(
    school_id: SchoolScopedID,
    staff_id: UUID,
    data: StaffProfileUpdate,
    auth: User = Depends(require_school_admin),
    service: StaffService = Depends(get_staff_service),
) -> StaffProfileResponse:
    """Update staff profile information."""
    updated = await service.update_staff_profile(staff_id, school_id, data)
    return updated
