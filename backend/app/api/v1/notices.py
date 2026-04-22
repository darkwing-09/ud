"""Notice API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.communication import NoticeCreate, NoticeResponse
from app.services.communication import CommunicationService


router = APIRouter(prefix="/notices", tags=["Notices & Announcements"])

def get_comm_service(db: DBSession) -> CommunicationService:
    return CommunicationService(db)

@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_notice(
    school_id: SchoolScopedID,
    data: NoticeCreate,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "HR"])),
    service: CommunicationService = Depends(get_comm_service),
) -> NoticeResponse:
    """Create a new notice or announcement."""
    return await service.create_notice(school_id, auth.id, data)

@router.get("", response_model=list[NoticeResponse])
async def list_notices(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: CommunicationService = Depends(get_comm_service),
) -> list[NoticeResponse]:
    """Get active notices tailored to the user's role."""
    return await service.get_notices_for_user(school_id, auth.role)
