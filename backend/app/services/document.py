"""Document service."""
from __future__ import annotations

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.document import DocumentRepository
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentRepository(db)

    async def create_document(self, school_id: UUID, data: DocumentCreate) -> Document:
        """Register a new document in the database."""
        doc = Document(
            school_id=school_id,
            owner_id=data.owner_id,
            owner_type=data.owner_type,
            name=data.name,
            file_key=data.file_key,
            file_type=data.file_type,
            file_size=data.file_size,
            category=data.category,
            metadata_json=data.metadata_json,
            is_public=data.is_public
        )
        return await self.repo.create(doc)

    async def get_document(self, doc_id: UUID) -> Document:
        """Get document details."""
        doc = await self.repo.get(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    async def list_owner_documents(self, owner_id: UUID, owner_type: str) -> list[Document]:
        """List all documents for an owner."""
        return await self.repo.list_by_owner(owner_id, owner_type)

    async def soft_delete_document(self, doc_id: UUID):
        """Soft delete a document (doesn't remove from R2)."""
        doc = await self.get_document(doc_id)
        # We use soft delete from SoftDeleteModel (if implemented in repo.delete)
        await self.repo.delete(doc_id)
