"""Communication module repositories."""
from __future__ import annotations

from datetime import datetime, date
from uuid import UUID

from sqlalchemy import select, and_, or_

from app.db.repositories.base import BaseRepository
from app.models.notice import Notice
from app.models.message import Message
from app.models.homework import HomeworkAssignment
from app.models.event import SchoolEvent


class NoticeRepository(BaseRepository[Notice]):
    model = Notice

    async def get_active_notices(self, school_id: UUID, role: str) -> list[Notice]:
        """Fetch notices applicable to a user role or global."""
        now = datetime.utcnow()
        # Find global notices (empty array) OR role-specific notices
        # In SQLite/Postgres JSON, checking `contains` can be tricky without right dialect, 
        # but we can filter simply in Python if traffic is low, or use cast.
        # We will use basic filtering for school_id and expires_at, then filter roles via Python or dialect-specific if needed.
        # For this setup, we'll return all active and let the service filter audience to be safe across DB engines.
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            or_(
                self.model.expires_at.is_(None),
                self.model.expires_at >= now
            ),
            self.model.deleted_at.is_(None)
        ).order_by(self.model.is_pinned.desc(), self.model.created_at.desc())
        
        result = await self.session.execute(stmt)
        all_notices = result.scalars().all()
        
        filtered = []
        for n in all_notices:
             if not n.audience_roles or role in n.audience_roles:
                 filtered.append(n)
        return filtered


class MessageRepository(BaseRepository[Message]):
    model = Message

    async def get_inbox(self, school_id: UUID, receiver_id: UUID) -> list[Message]:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.receiver_id == receiver_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_sent(self, school_id: UUID, sender_id: UUID) -> list[Message]:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.sender_id == sender_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class HomeworkRepository(BaseRepository[HomeworkAssignment]):
    model = HomeworkAssignment

    async def get_for_section(self, school_id: UUID, section_id: UUID) -> list[HomeworkAssignment]:
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.section_id == section_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.due_date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class EventRepository(BaseRepository[SchoolEvent]):
    model = SchoolEvent

    async def get_upcoming(self, school_id: UUID) -> list[SchoolEvent]:
        now = datetime.utcnow()
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.end_time >= now,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.start_time.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
