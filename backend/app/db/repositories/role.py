"""Role and Permission Repository."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.db.repositories.base import BaseRepository
from app.models.user import Role, Permission, RolePermission


class RoleRepository(BaseRepository[Role]):
    async def get_by_school_or_system(self, school_id: UUID) -> list[Role]:
        stmt = (
            select(Role)
            .where((Role.school_id == school_id) | (Role.school_id.is_(None)))
            .options(selectinload(Role.permissions))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, school_id: UUID, name: str) -> Role | None:
        stmt = select(Role).where(Role.school_id == school_id, Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_permissions(self, role_id: UUID) -> None:
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )


class PermissionRepository(BaseRepository[Permission]):
    async def get_all_permissions(self) -> list[Permission]:
        result = await self.db.execute(select(Permission))
        return list(result.scalars().all())
