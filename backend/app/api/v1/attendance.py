"""Attendance API endpoints."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.core.enums import UserRole
from app.models.user import User
from app.schemas.attendance import (
    StudentAttendanceCreate, 
    StudentAttendanceBulkCreate, 
    StudentAttendanceResponse,
    StaffAttendanceCreate,
    StaffAttendanceResponse
)
from app.services.attendance import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance Management"])

def get_attendance_service(db: DBSession) -> AttendanceService:
    return AttendanceService(db)

@router.post(
    "/students",
    response_model=StudentAttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark student attendance"
)
async def mark_student_attendance(
    school_id: SchoolScopedID,
    data: StudentAttendanceCreate,
    auth: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.CLASS_TEACHER)),
    service: AttendanceService = Depends(get_attendance_service),
) -> StudentAttendanceResponse:
    """Mark attendance for a specific student."""
    return await service.mark_student_attendance(school_id, data)

@router.post(
    "/students/bulk",
    response_model=list[StudentAttendanceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk mark student attendance"
)
async def bulk_mark_student_attendance(
    school_id: SchoolScopedID,
    data: StudentAttendanceBulkCreate,
    auth: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.CLASS_TEACHER)),
    service: AttendanceService = Depends(get_attendance_service),
) -> list[StudentAttendanceResponse]:
    """Bulk mark attendance for a section."""
    return await service.bulk_mark_student_attendance(school_id, data)

@router.get(
    "/students/section/{section_id}",
    response_model=list[StudentAttendanceResponse],
    summary="Get section attendance"
)
async def get_section_attendance(
    school_id: SchoolScopedID,
    section_id: UUID,
    date: date,
    auth: User = Depends(require_school_admin),
    service: AttendanceService = Depends(get_attendance_service),
) -> list[StudentAttendanceResponse]:
    """Get attendance records for a section on a date."""
    return await service.get_section_attendance(school_id, section_id, date)

@router.post(
    "/staff",
    response_model=StaffAttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark staff attendance"
)
async def mark_staff_attendance(
    school_id: SchoolScopedID,
    data: StaffAttendanceCreate,
    auth: User = Depends(require_school_admin),
    service: AttendanceService = Depends(get_attendance_service),
) -> StaffAttendanceResponse:
    """Mark attendance for a staff member."""
    return await service.mark_staff_attendance(school_id, data)
