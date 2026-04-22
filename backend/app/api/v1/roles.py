"""RBAC Endpoints."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.role import (
    RoleResponse,
    RoleCreate,
    RoleUpdate,
    PermissionResponse,
)
from app.services.role import RoleService

router = APIRouter(tags=["RBAC"], prefix="/rbac")

def get_role_service(db: DBSession) -> RoleService:
    return RoleService(db)

@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: RoleService = Depends(get_role_service),
) -> list[RoleResponse]:
    """List all available roles (system + customized)."""
    return await service.list_roles(school_id)

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    school_id: SchoolScopedID,
    data: RoleCreate,
    auth: User = Depends(require_school_admin),
    service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    """Create a customized school role."""
    return await service.create_role(school_id, data)

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    school_id: SchoolScopedID,
    role_id: UUID,
    data: RoleUpdate,
    auth: User = Depends(require_school_admin),
    service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    """Update a custom role and its permissions."""
    return await service.update_role(role_id, school_id, data)

@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: RoleService = Depends(get_role_service),
) -> list[PermissionResponse]:
    """List all available system permissions."""
    return await service.list_permissions()
