"""Document model for tracking file uploads in Cloudflare R2."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import SoftDeleteModel


class Document(SoftDeleteModel):
    __tablename__ = "documents"

    school_id: Mapped[UUID] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), index=True)
    
    # Polymorphic linking (owner)
    owner_id: Mapped[UUID] = mapped_column(index=True)
    owner_type: Mapped[str] = mapped_column(String(50), index=True)  # STAFF | STUDENT | SCHOOL | SYSTEM
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)  # R2 path
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)  # MIME type
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Bytes
    
    # Metadata for specific document types (e.g. Aadhaar card, Marks sheet)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    school = relationship("School", backref="documents")

    def __repr__(self) -> str:
        return f"<Document {self.name} owner={self.owner_type}:{self.owner_id}>"
