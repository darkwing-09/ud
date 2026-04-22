"""Database base classes: DeclarativeBase, AuditMixin, SoftDeleteMixin."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class UUIDMixin:
    """UUID primary key mixin."""
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        sort_order=-100,
    )


class AuditMixin:
    """Audit timestamp fields — must be on every model."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        sort_order=100,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        sort_order=101,
    )


class SoftDeleteMixin:
    """Soft-delete support — deleted_at instead of hard DELETE."""
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        sort_order=102,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class BaseModel(Base, UUIDMixin, AuditMixin):
    """Base model with UUID PK + audit fields. No soft delete."""
    __abstract__ = True


class SoftDeleteModel(Base, UUIDMixin, AuditMixin, SoftDeleteMixin):
    """Base model with UUID PK + audit fields + soft delete."""
    __abstract__ = True
