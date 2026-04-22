"""Communication schemas (Notices, Messages, Homework, Events)."""
from __future__ import annotations

from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ── Notice ──────────────────────────────────────────────────────

class NoticeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    audience_roles: list[str] = Field(default_factory=list)
    audience_section_ids: list[str] = Field(default_factory=list)
    attachments: list[dict] = Field(default_factory=list)
    is_pinned: bool = False
    expires_at: datetime | None = None


class NoticeCreate(NoticeBase):
    pass


class NoticeResponse(NoticeBase):
    id: UUID
    school_id: UUID
    author_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Message ─────────────────────────────────────────────────────

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    attachments: list[dict] = Field(default_factory=list)


class MessageCreate(MessageBase):
    receiver_id: UUID


class MessageResponse(MessageBase):
    id: UUID
    school_id: UUID
    sender_id: UUID
    receiver_id: UUID
    is_read: bool
    read_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Homework Assignment ─────────────────────────────────────────

class HomeworkBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    attachments: list[dict] = Field(default_factory=list)
    due_date: date


class HomeworkCreate(HomeworkBase):
    section_id: UUID
    subject_id: UUID


class HomeworkResponse(HomeworkBase):
    id: UUID
    school_id: UUID
    section_id: UUID
    subject_id: UUID
    teacher_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── School Event ────────────────────────────────────────────────

class SchoolEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = None
    event_type: str = Field(..., min_length=1)


class SchoolEventCreate(SchoolEventBase):
    pass


class SchoolEventResponse(SchoolEventBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)
