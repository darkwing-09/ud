"""Document schemas."""
from __future__ import annotations

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentBase(BaseModel):
    name: str
    category: str | None = None
    is_public: bool = False

class DocumentCreate(DocumentBase):
    owner_id: UUID
    owner_type: str  # STAFF | STUDENT | SCHOOL | SYSTEM
    file_key: str
    file_type: str
    file_size: int
    metadata_json: dict = {}

class DocumentResponse(DocumentBase):
    id: UUID
    school_id: UUID
    owner_id: UUID
    owner_type: str
    file_key: str
    file_type: str
    file_size: int
    metadata_json: dict
    created_at: datetime
    
    # Virtual field for signed URL
    url: str | None = None

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    is_public: bool | None = None
    metadata_json: dict | None = None
