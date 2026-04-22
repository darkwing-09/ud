"""Document API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status, Response

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.document import DocumentService

router = APIRouter(prefix="/documents", tags=["Document Management"])

def get_document_service(db: DBSession) -> DocumentService:
    return DocumentService(db)

@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register document"
)
async def create_document(
    school_id: SchoolScopedID,
    data: DocumentCreate,
    auth: User = Depends(require_school_admin),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Register a new document record."""
    return await service.create_document(school_id, data)

@router.get(
    "/owner/{owner_type}/{owner_id}",
    response_model=list[DocumentResponse],
    summary="List owner documents"
)
async def list_documents(
    owner_id: UUID,
    owner_type: str,
    auth: User = Depends(require_school_admin),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentResponse]:
    """List all documents for an owner."""
    return await service.list_owner_documents(owner_id, owner_type)

@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete document"
)
async def delete_document(
    doc_id: UUID,
    auth: User = Depends(require_school_admin),
    service: DocumentService = Depends(get_document_service),
) -> Response:
    """Soft delete a document record."""
    await service.soft_delete_document(doc_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
