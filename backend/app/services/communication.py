"""Communication business logic services."""
from __future__ import annotations

from typing import cast
from uuid import UUID

from app.core.deps import DBSession
from app.core.exceptions import NotFoundError
from app.db.repositories.communication import (
    EventRepository,
    HomeworkRepository,
    MessageRepository,
    NoticeRepository,
)
from app.db.repositories.school import SchoolRepository
from app.db.repositories.auth import UserRepository

from app.models.event import SchoolEvent
from app.models.homework import HomeworkAssignment
from app.models.message import Message
from app.models.notice import Notice

from app.schemas.communication import (
    SchoolEventCreate,
    HomeworkCreate,
    MessageCreate,
    NoticeCreate,
)


class CommunicationService:
    def __init__(self, session: DBSession):
        self.session = session
        self.notice_repo = NoticeRepository(session)
        self.message_repo = MessageRepository(session)
        self.homework_repo = HomeworkRepository(session)
        self.event_repo = EventRepository(session)
        self.user_repo = UserRepository(session)

    # ── Notices ──────────────────────────────────────────────────
    async def create_notice(self, school_id: UUID, author_id: UUID, data: NoticeCreate) -> Notice:
        notice = Notice(
            school_id=school_id,
            author_id=author_id,
            title=data.title,
            content=data.content,
            audience_roles=data.audience_roles,
            audience_section_ids=data.audience_section_ids,
            attachments=data.attachments,
            is_pinned=data.is_pinned,
            expires_at=data.expires_at,
        )
        self.notice_repo.add(notice)
        await self.session.commit()
        await self.session.refresh(notice)
        # TODO: Celery task push_notice_notifications.delay(notice.id)
        return notice

    async def get_notices_for_user(self, school_id: UUID, role: str) -> list[Notice]:
        """Fetch notices the current user's role is allowed to see."""
        return await self.notice_repo.get_active_notices(school_id, role)

    # ── Messages ─────────────────────────────────────────────────
    async def send_message(self, school_id: UUID, sender_id: UUID, data: MessageCreate) -> Message:
        receiver = await self.user_repo.get_by_id(data.receiver_id)
        if not receiver or receiver.school_id != school_id:
            raise NotFoundError("Recipient not found.")

        msg = Message(
            school_id=school_id,
            sender_id=sender_id,
            receiver_id=data.receiver_id,
            content=data.content,
            attachments=data.attachments,
        )
        self.message_repo.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        # TODO: Route to websocket or push notification if active
        return msg

    async def get_inbox(self, school_id: UUID, user_id: UUID) -> list[Message]:
        return await self.message_repo.get_inbox(school_id, user_id)

    # ── Homework ─────────────────────────────────────────────────
    async def assign_homework(self, school_id: UUID, teacher_id: UUID, data: HomeworkCreate) -> HomeworkAssignment:
        hw = HomeworkAssignment(
            school_id=school_id,
            section_id=data.section_id,
            subject_id=data.subject_id,
            teacher_id=teacher_id,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            attachments=data.attachments,
        )
        self.homework_repo.add(hw)
        await self.session.commit()
        await self.session.refresh(hw)
        return hw

    async def list_homework(self, school_id: UUID, section_id: UUID) -> list[HomeworkAssignment]:
        return await self.homework_repo.get_for_section(school_id, section_id)

    # ── Events ───────────────────────────────────────────────────
    async def create_event(self, school_id: UUID, data: SchoolEventCreate) -> SchoolEvent:
        event = SchoolEvent(
            school_id=school_id,
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            location=data.location,
            event_type=data.event_type,
        )
        self.event_repo.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_upcoming_events(self, school_id: UUID) -> list[SchoolEvent]:
        return await self.event_repo.get_upcoming(school_id)
