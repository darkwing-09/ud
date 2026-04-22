"""Salary Management API."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.salary import (
    SalaryStructureCreate,
    SalaryStructureResponse,
    StaffSalaryAssignmentCreate,
    StaffSalaryAssignmentResponse,
    SalaryAdvanceCreate,
    SalaryAdvanceResponse,
)
from app.services.salary import SalaryService

router = APIRouter(prefix="/salary", tags=["Salary & Compensation"])


def get_salary_service(db: DBSession) -> SalaryService:
    return SalaryService(db)


@router.post("/structures", response_model=SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_structure(
    school_id: SchoolScopedID,
    data: SalaryStructureCreate,
    auth: User = Depends(require_school_admin),
    service: SalaryService = Depends(get_salary_service),
) -> SalaryStructureResponse:
    """Create a new salary structure."""
    return await service.create_structure(school_id, data)


@router.get("/structures", response_model=list[SalaryStructureResponse])
async def list_structures(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: SalaryService = Depends(get_salary_service),
) -> list[SalaryStructureResponse]:
    """Get all salary structures in the school."""
    return await service.get_structures(school_id)


@router.post("/assignments", response_model=StaffSalaryAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_salary(
    school_id: SchoolScopedID,
    data: StaffSalaryAssignmentCreate,
    auth: User = Depends(require_school_admin),
    service: SalaryService = Depends(get_salary_service),
) -> StaffSalaryAssignmentResponse:
    """Assign a salary structure to a staff member."""
    return await service.assign_staff(school_id, data)


@router.post("/advances", response_model=SalaryAdvanceResponse, status_code=status.HTTP_201_CREATED)
async def request_advance(
    school_id: SchoolScopedID,
    data: SalaryAdvanceCreate,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "HR"])),
    service: SalaryService = Depends(get_salary_service),
) -> SalaryAdvanceResponse:
    """Submit a request for a salary advance."""
    # Ensure they can only request for themselves unless they are admin/HR
    if auth.role not in ["SUPER_ADMIN", "SCHOOL_ADMIN", "HR_MANAGER"]:
        if str(data.staff_id) != str(auth.id):
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Can only request advance for own account.")
    return await service.request_advance(school_id, data)


@router.put("/advances/{advance_id}/review", response_model=SalaryAdvanceResponse)
async def review_advance(
    school_id: SchoolScopedID,
    advance_id: UUID,
    approved: bool,
    auth: User = Depends(require_school_admin),
    service: SalaryService = Depends(get_salary_service),
) -> SalaryAdvanceResponse:
    """Approve or reject a salary advance request."""
    return await service.review_advance(school_id, advance_id, approved, auth.id)
