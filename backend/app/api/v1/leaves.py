"""Leave Management API endpoints."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.leave import (
    LeaveTypeCreate, LeaveTypeResponse,
    LeaveApplicationCreate, LeaveApplicationResponse,
    StaffLeaveBalanceCreate, StaffLeaveBalanceResponse,
)
from app.services.leave import LeaveService

router = APIRouter(prefix="/leaves", tags=["Leave Management"])

def get_leave_service(db: DBSession) -> LeaveService:
    return LeaveService(db)


# ── Leave Types ──────────────────────────────────────────────

@router.post("/types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    school_id: SchoolScopedID,
    data: LeaveTypeCreate,
    auth: User = Depends(require_school_admin),
    service: LeaveService = Depends(get_leave_service),
) -> LeaveTypeResponse:
    """Define a new type of generic leave."""
    return await service.create_leave_type(school_id, data)

@router.get("/types", response_model=list[LeaveTypeResponse])
async def list_leave_types(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "HR"])),
    service: LeaveService = Depends(get_leave_service),
) -> list[LeaveTypeResponse]:
    """Get all available leave types for the school."""
    return await service.get_leave_types(school_id)


# ── Leave Balances ───────────────────────────────────────────

@router.post("/allocations", response_model=StaffLeaveBalanceResponse, status_code=status.HTTP_201_CREATED)
async def allocate_leaves(
    school_id: SchoolScopedID,
    data: StaffLeaveBalanceCreate,
    auth: User = Depends(require_school_admin),
    service: LeaveService = Depends(get_leave_service),
) -> StaffLeaveBalanceResponse:
    """Allocate a quota of leaves to a specific staff member for a given year."""
    return await service.allocate_leaves(school_id, data.staff_id, data.leave_type_id, data.year, data.allocated_days)

@router.get("/my-balances/{year}", response_model=list[StaffLeaveBalanceResponse])
async def list_my_balances(
    school_id: SchoolScopedID,
    year: int,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "HR"])),
    service: LeaveService = Depends(get_leave_service),
) -> list[StaffLeaveBalanceResponse]:
    """Staff API: See available leave balances for the year."""
    return await service.balance_repo.list_for_staff(auth.id, year)


# ── Applications ─────────────────────────────────────────────

@router.post("/apply", response_model=LeaveApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_leave(
    school_id: SchoolScopedID,
    data: LeaveApplicationCreate,
    auth: User = Depends(require_roles(["TEACHER", "ADMIN", "HR"])),
    service: LeaveService = Depends(get_leave_service),
) -> LeaveApplicationResponse:
    """Submit a leave application for approval."""
    if auth.role not in ["SUPER_ADMIN", "SCHOOL_ADMIN", "HR_MANAGER"]:
        if str(data.staff_id) != str(auth.id):
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("You can only apply leaves for yourself.")
    return await service.apply_leave(school_id, data)

@router.get("/my-applications", response_model=list[LeaveApplicationResponse])
async def my_applications(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["TEACHER", "ADMIN", "HR"])),
    service: LeaveService = Depends(get_leave_service),
) -> list[LeaveApplicationResponse]:
    """Staff API: view historical inbox of leaves."""
    return await service.leave_repo.list_for_staff(auth.id)


@router.get("/inbox", response_model=list[LeaveApplicationResponse])
async def admin_leave_inbox(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: LeaveService = Depends(get_leave_service),
) -> list[LeaveApplicationResponse]:
    """HR/Admin API: view all pending requests."""
    return await service.leave_repo.get_pending_inbox(school_id)


@router.put("/{app_id}/approve", response_model=LeaveApplicationResponse)
async def approve_leave(
    school_id: SchoolScopedID,
    app_id: UUID,
    auth: User = Depends(require_school_admin),
    service: LeaveService = Depends(get_leave_service),
) -> LeaveApplicationResponse:
    return await service.approve_leave(school_id, app_id, auth.id)


@router.put("/{app_id}/reject", response_model=LeaveApplicationResponse)
async def reject_leave(
    school_id: SchoolScopedID,
    app_id: UUID,
    reason: str,
    auth: User = Depends(require_school_admin),
    service: LeaveService = Depends(get_leave_service),
) -> LeaveApplicationResponse:
    return await service.reject_leave(school_id, app_id, reason, auth.id)
