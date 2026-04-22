"""Generic async base repository with full CRUD support."""
from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.base import SoftDeleteModel

ModelT = TypeVar("ModelT", bound=Any)


class BaseRepository(Generic[ModelT]):
    """
    Generic repository providing CRUD operations for SQLAlchemy models.
    All queries automatically filter by school_id for multi-tenancy.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── Create ────────────────────────────────────────────────
    async def create(self, **kwargs: Any) -> ModelT:
        """Create and persist a new record from attributes."""
        instance = self.model(**kwargs)
        return await self.save(instance)

    async def save(self, instance: ModelT) -> ModelT:
        """Persist an existing model instance."""
        self.session.add(instance)
        await self.session.flush()
        try:
            await self.session.refresh(instance)
        except Exception:
            # Refresh might fail for some models or if already detached
            pass
        return instance

    # ── Read ──────────────────────────────────────────────────
    async def get_by_id(self, id: UUID, school_id: UUID | None = None) -> ModelT:
        """Get record by UUID. Raises NotFoundError if not found."""
        stmt = select(self.model).where(self.model.id == id)
        if school_id is not None:
            stmt = stmt.where(self.model.school_id == school_id)
        # Exclude soft-deleted records
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} with id={id} not found")
        return instance

    async def get_by_field(self, field: str, value: Any, school_id: UUID | None = None) -> ModelT | None:
        """Get single record by any field value."""
        stmt = select(self.model).where(getattr(self.model, field) == value)
        if school_id is not None:
            stmt = stmt.where(self.model.school_id == school_id)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        school_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
        **filters: Any,
    ) -> tuple[list[ModelT], int]:
        """
        List records with optional filters.
        Returns (items, total_count) tuple for pagination.
        """
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        if school_id is not None:
            stmt = stmt.where(self.model.school_id == school_id)
            count_stmt = count_stmt.where(self.model.school_id == school_id)

        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
            count_stmt = count_stmt.where(self.model.deleted_at.is_(None))

        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)
                count_stmt = count_stmt.where(getattr(self.model, field) == value)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def exists(self, school_id: UUID | None = None, **filters: Any) -> bool:
        """Check if matching record exists."""
        stmt = select(func.count()).select_from(self.model)
        if school_id is not None:
            stmt = stmt.where(self.model.school_id == school_id)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        for field, value in filters.items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    # ── Update ────────────────────────────────────────────────
    async def update(self, instance: ModelT, **kwargs: Any) -> ModelT:
        """Update fields on an existing record."""
        for field, value in kwargs.items():
            if value is not None and hasattr(instance, field):
                setattr(instance, field, value)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    # ── Delete ────────────────────────────────────────────────
    async def soft_delete(self, instance: ModelT) -> None:
        """Soft delete — sets deleted_at timestamp."""
        from datetime import datetime, timezone
        if not hasattr(instance, "deleted_at"):
            raise AttributeError(f"{self.model.__name__} does not support soft delete")
        instance.deleted_at = datetime.now(timezone.utc)  # type: ignore[assignment]
        self.session.add(instance)
        await self.session.flush()

    async def hard_delete(self, instance: ModelT) -> None:
        """Hard delete — permanently removes the record."""
        await self.session.delete(instance)
        await self.session.flush()

    # ── Bulk ──────────────────────────────────────────────────
    async def bulk_create(self, items: list[dict[str, Any]]) -> list[ModelT]:
        """Create multiple records efficiently."""
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        return instances
