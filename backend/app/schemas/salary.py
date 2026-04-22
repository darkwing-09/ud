"""Salary structure schemas."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ── SalaryStructure ──────────────────────────────────────────────

class SalaryStructureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    
    basic_salary: float = Field(..., ge=0)
    hra: float = Field(..., ge=0)
    da: float = Field(..., ge=0)
    allowances: float = Field(..., ge=0)
    
    pf_percentage: float = Field(12.0, ge=0, le=100)
    esi_percentage: float = Field(0.0, ge=0, le=100)
    professional_tax: float = Field(..., ge=0)
    
    is_active: bool = True


class SalaryStructureCreate(SalaryStructureBase):
    pass


class SalaryStructureResponse(SalaryStructureBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── StaffSalaryAssignment ────────────────────────────────────────

class StaffSalaryAssignmentBase(BaseModel):
    structure_id: UUID
    effective_from: date
    effective_until: date | None = None


class StaffSalaryAssignmentCreate(StaffSalaryAssignmentBase):
    staff_id: UUID


class StaffSalaryAssignmentResponse(StaffSalaryAssignmentBase):
    id: UUID
    school_id: UUID
    staff_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── SalaryAdvance ────────────────────────────────────────────────

class SalaryAdvanceBase(BaseModel):
    amount: float = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=500)
    emi_amount: float = Field(..., gt=0)
    deduction_start_month: int = Field(..., ge=1, le=12)
    deduction_start_year: int = Field(..., gt=2000)


class SalaryAdvanceCreate(SalaryAdvanceBase):
    staff_id: UUID


class SalaryAdvanceResponse(SalaryAdvanceBase):
    id: UUID
    school_id: UUID
    staff_id: UUID
    status: str
    approved_by_id: UUID | None

    model_config = ConfigDict(from_attributes=True)
