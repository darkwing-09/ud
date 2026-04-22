"""Homework API endpoints."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_roles
from app.models.user import User
from app.schemas.communication import HomeworkCreate, HomeworkResponse
from app.services.communication import CommunicationService


router = APIRouter(prefix="/homework", tags=["Homework Assignments"])

def get_comm_service(db: DBSession) -> CommunicationService:
    return CommunicationService(db)

@router.post("", response_model=HomeworkResponse, status_code=status.HTTP_201_CREATED)
async def assign_homework(
    school_id: SchoolScopedID,
    data: HomeworkCreate,
    auth: User = Depends(require_roles(["TEACHER", "ADMIN"])),
    service: CommunicationService = Depends(get_comm_service),
) -> HomeworkResponse:
    """Assign homework to a specific section."""
    return await service.assign_homework(school_id, auth.id, data)

@router.get("/section/{section_id}", response_model=list[HomeworkResponse])
async def list_homework_for_section(
    school_id: SchoolScopedID,
    section_id: UUID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: CommunicationService = Depends(get_comm_service),
) -> list[HomeworkResponse]:
    """Get active homework assigned to a specific section."""
    return await service.list_homework(school_id, section_id)
