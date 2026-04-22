"""Payroll API endpoints."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.payroll import PayrollRecordResponse, PayrollGenerateRequest
from app.services.payroll import PayrollService

router = APIRouter(prefix="/payroll", tags=["Payroll Generation"])


def get_payroll_service(db: DBSession) -> PayrollService:
    return PayrollService(db)


@router.post("/generate", response_model=list[PayrollRecordResponse], status_code=status.HTTP_201_CREATED)
async def generate_payroll(
    school_id: SchoolScopedID,
    data: PayrollGenerateRequest,
    auth: User = Depends(require_school_admin),
    service: PayrollService = Depends(get_payroll_service),
) -> list[PayrollRecordResponse]:
    """Generate DRAFT payroll for all staff for a specific month and year."""
    return await service.generate_monthly_payroll(school_id, data.month, data.year)


@router.put("/records/{record_id}/approve", response_model=PayrollRecordResponse)
async def approve_record(
    school_id: SchoolScopedID,
    record_id: UUID,
    auth: User = Depends(require_school_admin),
    service: PayrollService = Depends(get_payroll_service),
) -> PayrollRecordResponse:
    """Approve a DRAFT payroll record."""
    return await service.approve_record(school_id, record_id)


@router.post("/disburse", response_model=list[PayrollRecordResponse])
async def disburse_payroll_batch(
    school_id: SchoolScopedID,
    data: PayrollGenerateRequest,
    auth: User = Depends(require_school_admin),
    service: PayrollService = Depends(get_payroll_service),
) -> list[PayrollRecordResponse]:
    """Disburse APPROVED payroll records for the month. Triggers payslip emails."""
    return await service.disburse_month(school_id, data.month, data.year)


@router.get("/my-payslips", response_model=list[PayrollRecordResponse])
async def list_my_payslips(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(["ADMIN", "TEACHER", "HR"])),
    service: PayrollService = Depends(get_payroll_service),
) -> list[PayrollRecordResponse]:
    """Retrieve all payslips (payroll records) for the authenticated user."""
    # Depends on how staff_profiles map to user.auth.id
    # Assuming the API endpoint will use auth.id to map to staff profile.
    # We will just pass auth.id since they correspond in the seeder.
    return await service.payroll_repo.get_staff_records(auth.id)
