"""Events Calendar API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.communication import SchoolEventCreate, SchoolEventResponse
from app.services.communication import CommunicationService


router = APIRouter(prefix="/events", tags=["School Events"])

def get_comm_service(db: DBSession) -> CommunicationService:
    return CommunicationService(db)

@router.post("", response_model=SchoolEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    school_id: SchoolScopedID,
    data: SchoolEventCreate,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER"])),
    service: CommunicationService = Depends(get_comm_service),
) -> SchoolEventResponse:
    """Add an event to the school calendar."""
    return await service.create_event(school_id, data)

@router.get("", response_model=list[SchoolEventResponse])
async def get_upcoming_events(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: CommunicationService = Depends(get_comm_service),
) -> list[SchoolEventResponse]:
    """Get upcoming school events."""
    return await service.get_upcoming_events(school_id)
