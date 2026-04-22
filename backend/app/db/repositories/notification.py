"""Notification repositories."""
from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import select, func, update

from app.db.repositories.base import BaseRepository
from app.models.notification import Notification, NotificationTemplate


class NotificationTemplateRepository(BaseRepository[NotificationTemplate]):
    model = NotificationTemplate

    async def get_by_event(self, school_id: UUID, event_type: str, channel: str) -> NotificationTemplate | None:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.event_type == event_type,
            self.model.channel == channel,
            self.model.is_active == True,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    async def get_for_user(self, user_id: UUID, limit: int = 50) -> list[Notification]:
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: UUID) -> int:
        stmt = select(func.count(self.model.id)).where(
            self.model.user_id == user_id,
            self.model.is_read == False,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        val = result.scalar()
        return cast(int, val) if val is not None else 0

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        stmt = select(self.model).where(
            self.model.id == notification_id,
            self.model.user_id == user_id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        notif = result.scalar_one_or_none()
        return notif

    async def mark_all_read(self, user_id: UUID) -> int:
        from datetime import datetime
        stmt = (
            update(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.is_read == False,
                self.model.deleted_at.is_(None)
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        return cast(int, result.rowcount)
