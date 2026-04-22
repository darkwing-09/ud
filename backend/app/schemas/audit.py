"""Audit schemas."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    action: str
    module: str
    entity_id: str | None = None
    before_state: dict | None = None
    after_state: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class AuditLogCreate(AuditLogBase):
    school_id: UUID | None = None
    user_id: UUID | None = None


class AuditLogResponse(AuditLogBase):
    id: UUID
    school_id: UUID | None
    user_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
