"""Notification logic service."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.core.deps import DBSession
from app.core.exceptions import NotFoundError
from app.db.repositories.notification import NotificationRepository, NotificationTemplateRepository
from app.models.notification import Notification, NotificationTemplate
from app.schemas.notification import NotificationCreate, NotificationTemplateCreate


class NotificationService:
    def __init__(self, session: DBSession):
        self.session = session
        self.notif_repo = NotificationRepository(session)
        self.template_repo = NotificationTemplateRepository(session)

    # ── Templates ───────────────────────────────────────────────
    async def create_template(self, school_id: UUID, data: NotificationTemplateCreate) -> NotificationTemplate:
        template = NotificationTemplate(
            school_id=school_id,
            event_type=data.event_type,
            channel=data.channel,
            title_template=data.title_template,
            body_template=data.body_template,
            is_active=data.is_active,
        )
        self.template_repo.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    # ── Dispatch Engine ─────────────────────────────────────────
    async def dispatch(self, school_id: UUID, user_id: UUID, event_type: str, context: dict) -> Notification | None:
        """Central hub for formatting and sending a notification."""
        # Check if an IN_APP template exists for this event
        template = await self.template_repo.get_by_event(school_id, event_type, "IN_APP")
        
        # If no template exists, we can optionally skip or send a default one. Let's skip.
        if not template:
            return None
            
        try:
            # Quick string interpolation mapping context vars safely
            rendered_title = template.title_template.format(**context) if template.title_template else "Notification"
            rendered_body = template.body_template.format(**context)
        except KeyError:
            # Fallback if context is missing variables
            rendered_title = template.title_template or "System Notice"
            rendered_body = template.body_template
            
        return await self.create_notification(school_id, user_id, event_type, rendered_title, rendered_body, context)

    # ── Notifications CRUD ──────────────────────────────────────
    async def create_notification(self, school_id: UUID, user_id: UUID, type_: str, title: str, body: str, data: dict | None = None) -> Notification:
        notif = Notification(
            school_id=school_id,
            user_id=user_id,
            notification_type=type_,
            title=title,
            body=body,
            action_data=data,
        )
        self.notif_repo.add(notif)
        await self.session.commit()
        await self.session.refresh(notif)
        
        # Optionally pushing to Redis PubSub for realtime websocket dispatch
        # redis_client.publish(f"user:{user_id}:notifications", notif.json())
        return notif

    async def get_my_notifications(self, user_id: UUID) -> list[Notification]:
        return await self.notif_repo.get_for_user(user_id)

    async def get_unread_count(self, user_id: UUID) -> int:
        return await self.notif_repo.get_unread_count(user_id)

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notif = await self.notif_repo.mark_read(notification_id, user_id)
        if not notif:
            raise NotFoundError("Notification not found.")
            
        notif.is_read = True
        notif.read_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(notif)
        return notif

    async def mark_all_read(self, user_id: UUID) -> int:
        count = await self.notif_repo.mark_all_read(user_id)
        await self.session.commit()
        return count
