"""Notifications endpoints."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationTemplateCreate,
    NotificationTemplateResponse,
)
from app.services.notification import NotificationService


router = APIRouter(tags=["Notifications"])

def get_notif_service(db: DBSession) -> NotificationService:
    return NotificationService(db)

# ── Templates (Admin Only) ──────────────────────────────────────────────

@router.post("/notification-templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    school_id: SchoolScopedID,
    data: NotificationTemplateCreate,
    auth: User = Depends(require_school_admin),
    service: NotificationService = Depends(get_notif_service),
) -> NotificationTemplateResponse:
    """Create a new notification template (e.g. for fee payments)."""
    return await service.create_template(school_id, data)

# ── Notifications (User Inbox) ──────────────────────────────────────────

@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: NotificationService = Depends(get_notif_service),
) -> list[NotificationResponse]:
    """Get inbox notifications for current user."""
    return await service.get_my_notifications(auth.id)

@router.get("/notifications/unread-count")
async def get_unread_count(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: NotificationService = Depends(get_notif_service),
) -> dict[str, int]:
    """Realtime poll endpoint to get unread badge count."""
    count = await service.get_unread_count(auth.id)
    return {"unread": count}

@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    school_id: SchoolScopedID,
    notification_id: UUID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: NotificationService = Depends(get_notif_service),
) -> NotificationResponse:
    """Mark a specific notification as read."""
    return await service.mark_read(notification_id, auth.id)

@router.put("/notifications/mark-all-read")
async def mark_all_read(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: NotificationService = Depends(get_notif_service),
) -> dict[str, str]:
    """Mark all inbox notifications as read."""
    count = await service.mark_all_read(auth.id)
    return {"message": f"Marked {count} notifications as read."}
