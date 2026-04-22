"""Notification schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class NotificationTemplateBase(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=100)
    channel: str = Field(..., min_length=1, max_length=50) # EMAIL, SMS, IN_APP
    title_template: str | None = None
    body_template: str = Field(..., min_length=1)
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateResponse(NotificationTemplateBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


class NotificationBase(BaseModel):
    notification_type: str
    title: str
    body: str
    action_data: dict | None = None
    is_read: bool = False


class NotificationCreate(NotificationBase):
    user_id: UUID


class NotificationResponse(NotificationBase):
    id: UUID
    school_id: UUID
    user_id: UUID
    read_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
