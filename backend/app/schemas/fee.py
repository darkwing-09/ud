"""Fee Management Pydantic v2 schemas — structures, discounts, dues, payments."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ── FeeComponent ─────────────────────────────────────────────────────────────

class FeeComponentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    is_mandatory: bool = True


class FeeComponentResponse(FeeComponentCreate):
    id: UUID
    fee_structure_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── FeeStructure ─────────────────────────────────────────────────────────────

class FeeStructureCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    academic_year_id: UUID
    frequency: str = Field("MONTHLY", pattern="^(MONTHLY|QUARTERLY|ANNUAL|ONE_TIME)$")
    due_day: int | None = Field(None, ge=1, le=28, description="Day of month payment is due")
    late_fee_per_day: float = Field(0, ge=0)
    max_late_fee: float = Field(0, ge=0)
    components: list[FeeComponentCreate] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_due_day(self) -> "FeeStructureCreate":
        if self.frequency != "ONE_TIME" and self.due_day is None:
            raise ValueError("due_day is required for non-ONE_TIME fee structures")
        return self


class FeeStructureUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    due_day: int | None = Field(None, ge=1, le=28)
    late_fee_per_day: float | None = Field(None, ge=0)
    max_late_fee: float | None = Field(None, ge=0)


class FeeStructureResponse(BaseModel):
    id: UUID
    school_id: UUID
    academic_year_id: UUID
    name: str
    frequency: str
    due_day: int | None
    late_fee_per_day: float
    max_late_fee: float
    components: list[FeeComponentResponse]

    model_config = ConfigDict(from_attributes=True)


class FeeStructureSummary(BaseModel):
    """Lightweight structure response (no components) for list views."""
    id: UUID
    name: str
    frequency: str
    due_day: int | None
    academic_year_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ── FeeAssignment ─────────────────────────────────────────────────────────────

class FeeAssignRequest(BaseModel):
    """Assign a FeeStructure to a class, section, or individual student."""
    class_id: UUID | None = None
    section_id: UUID | None = None
    student_id: UUID | None = None

    @model_validator(mode="after")
    def exactly_one_target(self) -> "FeeAssignRequest":
        targets = [x for x in [self.class_id, self.section_id, self.student_id] if x is not None]
        if len(targets) != 1:
            raise ValueError("Exactly one of class_id, section_id, or student_id must be provided.")
        return self


class FeeAssignResponse(BaseModel):
    message: str
    assignment_id: UUID
    dues_queued: int


# ── FeeDiscount ───────────────────────────────────────────────────────────────

class FeeDiscountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    discount_type: str = Field(..., pattern="^(PERCENTAGE|FIXED)$")
    value: float = Field(..., gt=0)
    applicable_on: str = Field("TOTAL", pattern="^(TOTAL|COMPONENT)$")
    description: str | None = Field(None, max_length=1000)

    @model_validator(mode="after")
    def validate_percentage(self) -> "FeeDiscountCreate":
        if self.discount_type == "PERCENTAGE" and self.value > 100:
            raise ValueError("Percentage discount cannot exceed 100%")
        return self


class FeeDiscountResponse(FeeDiscountCreate):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ApplyDiscountRequest(BaseModel):
    student_id: UUID
    reason: str | None = Field(None, max_length=1000)


class ApplyDiscountResponse(BaseModel):
    message: str
    student_id: UUID
    discount_id: UUID


# ── FeeDue ───────────────────────────────────────────────────────────────────

class FeeDueResponse(BaseModel):
    id: UUID
    school_id: UUID
    student_id: UUID
    fee_structure_id: UUID
    period_label: str
    due_date: date
    base_amount: float
    discount_amount: float
    late_fee_amount: float
    net_amount: float
    paid_amount: float
    status: str  # UNPAID | PARTIAL | PAID | WAIVED

    @property
    def outstanding(self) -> float:
        return max(0.0, self.net_amount + self.late_fee_amount - self.paid_amount)

    model_config = ConfigDict(from_attributes=True)


class LateFeeWaiveRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


# ── Student Fee Overview ──────────────────────────────────────────────────────

class StudentFeeOverview(BaseModel):
    student_id: UUID
    total_fees: float
    paid_amount: float
    outstanding: float
    overdue: float
    dues: list[FeeDueResponse]


# ── FeePayment ────────────────────────────────────────────────────────────────

class PaymentInitiateRequest(BaseModel):
    student_id: UUID
    fee_due_ids: list[UUID] = Field(..., min_length=1)


class RazorpayOrderResponse(BaseModel):
    razorpay_order_id: str
    amount: int  # in paise
    currency: str
    key_id: str
    fee_payment_id: UUID


class PaymentVerifyRequest(BaseModel):
    """Verify Razorpay payment after checkout completion."""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    fee_payment_id: UUID


class CashPaymentRequest(BaseModel):
    student_id: UUID
    fee_due_ids: list[UUID] = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    payment_method: str = Field("CASH", pattern="^(CASH|CHEQUE|UPI)$")
    remarks: str | None = Field(None, max_length=500)


class FeePaymentResponse(BaseModel):
    id: UUID
    school_id: UUID
    student_id: UUID
    fee_due_id: UUID
    amount: float
    payment_method: str
    status: str
    gateway_order_id: str | None
    gateway_payment_id: str | None
    receipt_number: str | None
    receipt_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Defaulter Report ──────────────────────────────────────────────────────────

class DefaulterRecord(BaseModel):
    student_id: UUID
    student_name: str
    admission_number: str
    section_name: str | None
    overdue_amount: float
    oldest_due_date: date
    days_overdue: int


class DefaulterListResponse(BaseModel):
    total_defaulters: int
    total_overdue_amount: float
    defaulters: list[DefaulterRecord]


# ── Fee Reminder ──────────────────────────────────────────────────────────────

class FeeReminderRequest(BaseModel):
    student_ids: list[UUID] = Field(..., min_length=1)
    channels: list[str] = Field(..., description="EMAIL | SMS")
    message: str | None = Field(None, max_length=1000)


class FeeReminderResponse(BaseModel):
    queued: int
    message: str


# ── Collection Report ─────────────────────────────────────────────────────────

class CollectionBreakdown(BaseModel):
    label: str
    amount: float
    count: int


class CollectionReportResponse(BaseModel):
    total_collected: float
    from_date: date
    to_date: date
    breakdown_by_method: list[CollectionBreakdown]
    breakdown_by_class: list[CollectionBreakdown]


class OutstandingReportResponse(BaseModel):
    total_outstanding: float
    academic_year_id: UUID
    student_count: int
    class_wise: list[CollectionBreakdown]
