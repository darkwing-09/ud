"""Common shared schemas: pagination, errors, generic responses."""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class BaseRequest(BaseModel):
    """Base for all input schemas. Rejects unknown fields."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PaginationParams(BaseRequest):

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=200, description="Items per page")

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit


class PagedResponse(BaseModel, Generic[DataT]):
    model_config = ConfigDict(from_attributes=True)

    items: list[DataT]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def build(cls, items: list, total: int, page: int, limit: int) -> "PagedResponse[DataT]":
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return cls(items=items, total=total, page=page, limit=limit, pages=pages)


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    detail: str
    error_code: str | None = None


class ImportJobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED, PARTIAL
    total_rows: int
    processed_rows: int
    failed_rows: int
    errors: list[dict] = []
    completed_at: str | None = None


class BulkActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    message: str
    estimated_completion: str | None = None


class IDResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    message: str = "Created successfully"


class SignedURLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    expires_in_seconds: int
