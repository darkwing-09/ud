"""Role and Permission schemas."""
from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    module: str
    action: str
    scope: str | None = None
    description: str | None = None


class PermissionResponse(PermissionBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class RoleCreate(RoleBase):
    permission_ids: list[UUID] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permission_ids: list[UUID] | None = None


class RoleResponse(RoleBase):
    id: UUID
    school_id: UUID | None
    is_system: bool
    permissions: list[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class UserRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
