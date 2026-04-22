"""Role and Permission management service."""
from __future__ import annotations

from uuid import UUID
from app.core.deps import DBSession
from app.core.exceptions import NotFoundError, ConflictError
from app.db.repositories.role import RoleRepository, PermissionRepository
from app.models.user import Role, Permission, RolePermission, User
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, session: DBSession):
        self.session = session
        self.role_repo = RoleRepository(session)
        self.perm_repo = PermissionRepository(session)

    async def list_roles(self, school_id: UUID | None = None) -> list[Role]:
        return await self.role_repo.get_by_school_or_system(school_id)

    async def create_role(self, school_id: UUID, data: RoleCreate) -> Role:
        # Check if exists
        existing = await self.role_repo.get_by_name(school_id, data.name)
        if existing:
            raise ConflictError("Role with this name already exists in this school.")

        role = await self.role_repo.create(
            school_id=school_id,
            name=data.name,
            description=data.description,
            is_system=False
        )
        await self.session.flush()

        if data.permission_ids:
            for p_id in data.permission_ids:
                rp = RolePermission(role_id=role.id, permission_id=p_id)
                self.session.add(rp)

        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def update_role(self, role_id: UUID, school_id: UUID, data: RoleUpdate) -> Role:
        role = await self.role_repo.get_by_id(role_id)
        if not role or role.school_id != school_id:
            raise NotFoundError("Role not found.")
        
        if role.is_system:
            raise ConflictError("Cannot modify system roles.")

        update_data = data.model_dump(exclude={"permission_ids"}, exclude_unset=True)
        if update_data:
            role = await self.role_repo.update(role, **update_data)
            
        if data.permission_ids is not None:
            # Sync permissions
            await self.role_repo.clear_permissions(role_id)
            for p_id in data.permission_ids:
                rp = RolePermission(role_id=role_id, permission_id=p_id)
                self.session.add(rp)

        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def list_permissions(self) -> list[Permission]:
        return await self.perm_repo.get_all_permissions()

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID, school_id: UUID):
        # Implementation for multi-role assignment if needed
        # For MVP, user has one role in core User model, but we can extend this
        user = await self.session.get(User, user_id)
        if not user or user.school_id != school_id:
            raise NotFoundError("User not found.")
            
        role = await self.session.get(Role, role_id)
        if not role or (role.school_id and role.school_id != school_id):
            raise NotFoundError("Role not found.")
            
        user.role = role.name # Simplified for MVP string-based roles
        await self.session.commit()
        return user
