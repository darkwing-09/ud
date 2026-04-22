"""Document repository."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.models.document import Document

class DocumentRepository(BaseRepository[Document]):
    @property
    def model(self) -> type[Document]:
        return Document

    async def list_by_owner(self, owner_id: UUID, owner_type: str) -> list[Document]:
        """List documents for a specific owner."""
        stmt = select(self.model).where(
            self.model.owner_id == owner_id,
            self.model.owner_type == owner_type
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_file_key(self, file_key: str) -> Document | None:
        """Get document by its R2 file key."""
        stmt = select(self.model).where(self.model.file_key == file_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
