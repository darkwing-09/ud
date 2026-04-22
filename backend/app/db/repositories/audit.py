"""Audit Log Repository."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.repositories.base import BaseRepository
from app.models.audit import AuditLog


class AuditRepository(BaseRepository[AuditLog]):
    async def get_by_school(
        self, school_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.school_id == school_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(AuditLog.user))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
