"""School router for creating and managing physical schools/tenants."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, File

from app.core.deps import get_current_user, require_school_admin, require_super_admin, get_db
from app.db.repositories.school import SchoolRepository
from app.models.user import User
from app.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolSettingsUpdate,
    SchoolStatsResponse,
    SchoolUpdate,
)
from app.services.school import SchoolService
from app.services.storage import StorageService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/schools", tags=["School Management"])


def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    repo = SchoolRepository(db)
    storage = StorageService()
    return SchoolService(school_repo=repo, storage_service=storage)


@router.get("", response_model=list[SchoolResponse])
async def list_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(require_super_admin),
) -> list[SchoolResponse]:
    """List all schools (Platform Super Admin only)."""
    schools, _ = await service.school_repo.list(skip=skip, limit=limit)
    return schools


@router.post("", response_model=SchoolResponse, status_code=201)
async def create_school(
    data: SchoolCreate,
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(require_super_admin),
) -> SchoolResponse:
    """Register a new SaaS tenant/school (Platform Super Admin only)."""
    return await service.create_school(data)


@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: UUID,
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(get_current_user),
) -> SchoolResponse:
    """Get details of a school."""
    # If not super admin, ensure they belong to this school
    if not await current_user.is_super_admin() and current_user.school_id != school_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Not authorized to access this school's details")
        
    return await service.school_repo.get_by_id(school_id)


@router.patch("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: UUID,
    data: SchoolUpdate,
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(get_current_user),
) -> SchoolResponse:
    """Update general school details (Super Admin or School Admin)."""
    if not await current_user.is_super_admin():
        if current_user.school_id != school_id or not await current_user.has_permission("school.update", school_id):
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Not authorized to update this school")
            
    return await service.update_school(school_id, data)


@router.patch("/{school_id}/settings", response_model=SchoolResponse)
async def update_school_settings(
    school_id: UUID,
    data: SchoolSettingsUpdate,
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(require_school_admin),
) -> SchoolResponse:
    """Update school configurations (School Admin)."""
    if not await current_user.is_super_admin() and current_user.school_id != school_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Not authorized to update this school's settings")
        
    return await service.update_settings(school_id, data)


@router.post("/{school_id}/activation", response_model=SchoolResponse)
async def toggle_school_activation(
    school_id: UUID,
    is_active: bool = Query(..., description="Set to true to activate, false to suspend"),
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(require_super_admin),
) -> SchoolResponse:
    """Activate or suspend a school (Super Admin only)."""
    return await service.toggle_activation(school_id, is_active)


@router.post("/{school_id}/logo", response_model=SchoolResponse)
async def upload_school_logo(
    school_id: UUID,
    file: UploadFile = File(...),
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(get_current_user),
) -> SchoolResponse:
    """Upload a new logo for the school."""
    if not await current_user.is_super_admin():
        if current_user.school_id != school_id or not await current_user.has_permission("school.update", school_id):
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Not authorized to update this school")
            
    return await service.upload_logo(school_id, file)


@router.get("/{school_id}/stats", response_model=SchoolStatsResponse)
async def get_school_stats(
    school_id: UUID,
    service: SchoolService = Depends(get_school_service),
    current_user: User = Depends(get_current_user),
) -> SchoolStatsResponse:
    """Get high-level statistics for the dashboard."""
    if not await current_user.is_super_admin() and current_user.school_id != school_id:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Not authorized to access this school's stats")
        
    stats = await service.get_stats(school_id)
    return SchoolStatsResponse(**stats)
