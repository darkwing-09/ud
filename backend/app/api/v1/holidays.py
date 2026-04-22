"""Holiday API endpoints."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.leave import HolidayCreate, HolidayResponse
from app.services.leave import HolidayService

router = APIRouter(prefix="/holidays", tags=["Holidays"])

def get_holiday_service(db: DBSession) -> HolidayService:
    return HolidayService(db)

@router.post("", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    school_id: SchoolScopedID,
    data: HolidayCreate,
    auth: User = Depends(require_school_admin),
    service: HolidayService = Depends(get_holiday_service),
) -> HolidayResponse:
    """Declare a new school-wide holiday."""
    return await service.create_holiday(school_id, data)

@router.get("", response_model=list[HolidayResponse])
async def list_holidays(
    school_id: SchoolScopedID,
    start_date: date,
    end_date: date,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "STUDENT", "PARENT"])),
    service: HolidayService = Depends(get_holiday_service),
) -> list[HolidayResponse]:
    """Retrieve holidays within a specific date range."""
    return await service.list_holidays(school_id, start_date, end_date)
