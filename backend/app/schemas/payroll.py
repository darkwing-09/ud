"""Payroll generation schemas."""
from __future__ import annotations

from datetime import date
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ── PayrollRecord ──────────────────────────────────────────────

class PayrollRecordBase(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., gt=2000)
    
    total_working_days: int = Field(..., ge=1, le=31)
    lop_days: float = Field(..., ge=0)
    
    basic_salary: float = Field(..., ge=0)
    hra: float = Field(..., ge=0)
    da: float = Field(..., ge=0)
    allowances: float = Field(..., ge=0)
    gross_earnings: float = Field(..., ge=0)
    
    lop_amount: float = Field(..., ge=0)
    pf_deduction: float = Field(..., ge=0)
    esi_deduction: float = Field(..., ge=0)
    tax_deduction: float = Field(..., ge=0)
    advance_emi: float = Field(..., ge=0)
    total_deductions: float = Field(..., ge=0)
    
    net_salary: float = Field(..., ge=0)
    
    status: str
    disbursed_at: date | None = None
    remarks: str | None = None


class PayrollGenerateRequest(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., gt=2000)


class PayrollRecordResponse(PayrollRecordBase):
    id: UUID
    school_id: UUID
    staff_id: UUID
    assignment_id: UUID

    model_config = ConfigDict(from_attributes=True)
