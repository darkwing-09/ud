"""Direct messaging API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.communication import MessageCreate, MessageResponse
from app.services.communication import CommunicationService


router = APIRouter(prefix="/messages", tags=["Direct Messaging"])

def get_comm_service(db: DBSession) -> CommunicationService:
    return CommunicationService(db)

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    school_id: SchoolScopedID,
    data: MessageCreate,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: CommunicationService = Depends(get_comm_service),
) -> MessageResponse:
    """Send a direct message to another user in the school."""
    return await service.send_message(school_id, auth.id, data)

@router.get("/inbox", response_model=list[MessageResponse])
async def get_my_inbox(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: CommunicationService = Depends(get_comm_service),
) -> list[MessageResponse]:
    """Get the user's inbox."""
    return await service.get_inbox(school_id, auth.id)
