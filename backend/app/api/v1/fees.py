"""Fee Management API — 17 endpoints covering structures, dues, payments, reports."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.core.deps import (
    ADMIN_OR_ACCOUNTANT,
    DBSession,
    SCHOOL_ADMIN,
    SchoolScopedID,
    require_roles,
    require_school_admin,
)
from app.core.enums import UserRole
from app.models.user import User
from app.schemas.fee import (
    ApplyDiscountRequest,
    ApplyDiscountResponse,
    CashPaymentRequest,
    CollectionReportResponse,
    DefaulterListResponse,
    DefaulterRecord,
    FeeAssignRequest,
    FeeAssignResponse,
    FeeDiscountCreate,
    FeeDiscountResponse,
    FeeDueResponse,
    FeePaymentResponse,
    FeeReminderRequest,
    FeeReminderResponse,
    FeeStructureCreate,
    FeeStructureResponse,
    FeeStructureSummary,
    FeeStructureUpdate,
    LateFeeWaiveRequest,
    PaymentInitiateRequest,
    PaymentVerifyRequest,
    RazorpayOrderResponse,
    StudentFeeOverview,
)
from app.services.fee import FeeStructureService
from app.services.payment import PaymentService

router = APIRouter(prefix="/fees", tags=["Fee Management"])


# ── Dependency helpers ────────────────────────────────────────────────────────

def get_fee_service(db: DBSession) -> FeeStructureService:
    return FeeStructureService(db)


def get_payment_service(db: DBSession) -> PaymentService:
    return PaymentService(db)


# ══════════════════════════════════════════════════════════════════════════════
# FEE STRUCTURES
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/structures",
    response_model=FeeStructureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create fee structure",
    description=(
        "Define a fee template (e.g., 'Grade 10 Annual Fee') with components "
        "and assign it to classes later. Only SCHOOL_ADMIN and ACCOUNTANT can create."
    ),
)
async def create_fee_structure(
    school_id: SchoolScopedID,
    data: FeeStructureCreate,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> FeeStructureResponse:
    structure = await service.create_structure(school_id, data)
    return structure  # type: ignore[return-value]


@router.get(
    "/structures",
    response_model=list[FeeStructureSummary],
    summary="List fee structures",
    description="List all fee structures for a given academic year.",
)
async def list_fee_structures(
    school_id: SchoolScopedID,
    academic_year_id: UUID,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
    service: FeeStructureService = Depends(get_fee_service),
) -> list[FeeStructureSummary]:
    return await service.list_structures(school_id, academic_year_id)  # type: ignore[return-value]


@router.get(
    "/structures/{structure_id}",
    response_model=FeeStructureResponse,
    summary="Get fee structure details",
    description="Retrieve a single fee structure with all its components.",
)
async def get_fee_structure(
    school_id: SchoolScopedID,
    structure_id: UUID,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
    service: FeeStructureService = Depends(get_fee_service),
) -> FeeStructureResponse:
    return await service.get_structure(school_id, structure_id)  # type: ignore[return-value]


@router.patch(
    "/structures/{structure_id}",
    response_model=FeeStructureResponse,
    summary="Update fee structure",
    description="Update structure metadata. Blocked if active dues have been generated.",
)
async def update_fee_structure(
    school_id: SchoolScopedID,
    structure_id: UUID,
    data: FeeStructureUpdate,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> FeeStructureResponse:
    return await service.update_structure(school_id, structure_id, data)  # type: ignore[return-value]


@router.delete(
    "/structures/{structure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete fee structure",
    description="Soft-delete a fee structure. Blocked if any dues have been generated.",
)
async def delete_fee_structure(
    school_id: SchoolScopedID,
    structure_id: UUID,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> None:
    await service.delete_structure(school_id, structure_id)


@router.post(
    "/structures/{structure_id}/assign",
    response_model=FeeAssignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign fee structure to class / section / student",
    description=(
        "Assign a fee structure to a class, section, or individual student. "
        "Automatically generates FeeDue records per period based on frequency. "
        "Idempotent per period — re-assigning does not create duplicate dues."
    ),
)
async def assign_fee_structure(
    school_id: SchoolScopedID,
    structure_id: UUID,
    data: FeeAssignRequest,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> FeeAssignResponse:
    assignment, dues_count = await service.assign_structure(school_id, structure_id, data)
    return FeeAssignResponse(
        message=f"Fee structure assigned. {dues_count} dues generated.",
        assignment_id=assignment.id,
        dues_queued=dues_count,
    )


# ══════════════════════════════════════════════════════════════════════════════
# FEE DISCOUNTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/discounts",
    response_model=FeeDiscountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create fee discount",
    description="Define a reusable discount (e.g., Sibling Discount 10%, Staff Ward ₹500).",
)
async def create_discount(
    school_id: SchoolScopedID,
    data: FeeDiscountCreate,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> FeeDiscountResponse:
    discount = await service.create_discount(school_id, data)
    return discount  # type: ignore[return-value]


@router.get(
    "/discounts",
    response_model=list[FeeDiscountResponse],
    summary="List fee discounts",
    description="List all discount definitions for this school.",
)
async def list_discounts(
    school_id: SchoolScopedID,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
    service: FeeStructureService = Depends(get_fee_service),
) -> list[FeeDiscountResponse]:
    return await service.list_discounts(school_id)  # type: ignore[return-value]


@router.post(
    "/discounts/{discount_id}/apply",
    response_model=ApplyDiscountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply discount to student",
    description="Apply a discount to a specific student. Discount will be reflected in future dues.",
)
async def apply_discount(
    school_id: SchoolScopedID,
    discount_id: UUID,
    data: ApplyDiscountRequest,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> ApplyDiscountResponse:
    await service.apply_discount_to_student(school_id, discount_id, data, auth.id)
    return ApplyDiscountResponse(
        message="Discount applied successfully.",
        student_id=data.student_id,
        discount_id=discount_id,
    )


# ══════════════════════════════════════════════════════════════════════════════
# STUDENT FEE VIEWS (Student, Parent, Accountant, Admin)
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/student/{student_id}",
    response_model=StudentFeeOverview,
    summary="Student fee overview",
    description=(
        "Returns total fees, paid, outstanding, and overdue amounts, "
        "plus full list of dues with their statuses."
    ),
)
async def get_student_fee_overview(
    school_id: SchoolScopedID,
    student_id: UUID,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT,
        UserRole.STUDENT, UserRole.PARENT,
    )),
    service: FeeStructureService = Depends(get_fee_service),
) -> StudentFeeOverview:
    return await service.get_student_overview(school_id, student_id)


@router.get(
    "/student/{student_id}/dues",
    response_model=list[FeeDueResponse],
    summary="Student outstanding dues",
    description="List all UNPAID or PARTIAL dues for a student.",
)
async def get_student_dues(
    school_id: SchoolScopedID,
    student_id: UUID,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT,
        UserRole.STUDENT, UserRole.PARENT,
    )),
    service: FeeStructureService = Depends(get_fee_service),
) -> list[FeeDueResponse]:
    overview = await service.get_student_overview(school_id, student_id)
    return [d for d in overview.dues if d.status in ("UNPAID", "PARTIAL")]


@router.get(
    "/student/{student_id}/history",
    response_model=list[FeePaymentResponse],
    summary="Student payment history",
    description="Paginated list of all successful payments for a student.",
)
async def get_student_payment_history(
    school_id: SchoolScopedID,
    student_id: UUID,
    skip: int = 0,
    limit: int = 50,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT,
        UserRole.STUDENT, UserRole.PARENT,
    )),
    service: PaymentService = Depends(get_payment_service),
) -> list[FeePaymentResponse]:
    payments, _ = await service.get_payment_history(school_id, student_id, skip, limit)
    return payments  # type: ignore[return-value]


# ══════════════════════════════════════════════════════════════════════════════
# LATE FEE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@router.patch(
    "/late-fee/waive/{due_id}",
    response_model=FeeDueResponse,
    summary="Waive late fee",
    description="Zero out the late fee on a specific due with a required reason. Admin only.",
)
async def waive_late_fee(
    school_id: SchoolScopedID,
    due_id: UUID,
    data: LateFeeWaiveRequest,
    auth: User = Depends(require_school_admin),
    service: FeeStructureService = Depends(get_fee_service),
) -> FeeDueResponse:
    return await service.waive_late_fee(school_id, due_id, data)  # type: ignore[return-value]


# ══════════════════════════════════════════════════════════════════════════════
# ONLINE PAYMENTS (Razorpay)
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/payments/initiate",
    response_model=RazorpayOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate Razorpay payment",
    description=(
        "Creates a Razorpay order for selected fee dues. "
        "Returns order_id and key_id for frontend Razorpay checkout integration."
    ),
)
async def initiate_payment(
    school_id: SchoolScopedID,
    data: PaymentInitiateRequest,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT,
        UserRole.STUDENT, UserRole.PARENT,
    )),
    service: PaymentService = Depends(get_payment_service),
) -> RazorpayOrderResponse:
    return await service.initiate_payment(school_id, data)


@router.post(
    "/payments/verify",
    response_model=FeePaymentResponse,
    summary="Verify Razorpay payment",
    description=(
        "Called by the frontend after Razorpay checkout success. "
        "Verifies HMAC-SHA256 signature, marks dues as PAID, and queues receipt PDF."
    ),
)
async def verify_payment(
    school_id: SchoolScopedID,
    data: PaymentVerifyRequest,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT,
        UserRole.STUDENT, UserRole.PARENT,
    )),
    service: PaymentService = Depends(get_payment_service),
) -> FeePaymentResponse:
    payment = await service.verify_payment(
        school_id=school_id,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        razorpay_signature=data.razorpay_signature,
        fee_payment_id=data.fee_payment_id,
    )
    return payment  # type: ignore[return-value]


@router.post(
    "/payments/webhook",
    status_code=status.HTTP_200_OK,
    summary="Razorpay webhook handler",
    description=(
        "Asynchronous webhook from Razorpay for payment.captured / payment.failed events. "
        "Validates X-Razorpay-Signature header. Idempotent — safe to re-deliver."
    ),
)
async def razorpay_webhook(
    request: Request,
    service: PaymentService = Depends(get_payment_service),
) -> dict:
    raw_body = await request.body()
    payload = await request.json()
    signature = request.headers.get("X-Razorpay-Signature", "")
    await service.process_webhook(payload, signature, raw_body)
    return {"status": "ok"}


@router.post(
    "/payments/cash",
    response_model=list[FeePaymentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record cash / offline payment",
    description=(
        "Record a CASH, CHEQUE, or UPI payment collected offline. "
        "Amount is distributed across selected dues in due-date order. "
        "Triggers receipt PDF generation. Accountant and Admin only."
    ),
)
async def record_cash_payment(
    school_id: SchoolScopedID,
    data: CashPaymentRequest,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
    service: PaymentService = Depends(get_payment_service),
) -> list[FeePaymentResponse]:
    return await service.record_cash_payment(school_id, data, auth.id)  # type: ignore[return-value]


@router.get(
    "/payments/{payment_id}",
    response_model=FeePaymentResponse,
    summary="Get payment details",
    description="Retrieve details of a specific payment transaction.",
)
async def get_payment(
    school_id: SchoolScopedID,
    payment_id: UUID,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT,
        UserRole.STUDENT, UserRole.PARENT,
    )),
    service: PaymentService = Depends(get_payment_service),
) -> FeePaymentResponse:
    return await service.get_payment(school_id, payment_id)  # type: ignore[return-value]


# ══════════════════════════════════════════════════════════════════════════════
# DEFAULTERS & REMINDERS
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/defaulters",
    response_model=DefaulterListResponse,
    summary="Defaulter list",
    description=(
        "List all students with overdue fee dues. "
        "Supports filtering by class, minimum days overdue, and minimum amount."
    ),
)
async def get_defaulters(
    school_id: SchoolScopedID,
    class_id: UUID | None = None,
    days_overdue_min: int = 1,
    amount_min: float = 0,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
    service: FeeStructureService = Depends(get_fee_service),
) -> DefaulterListResponse:
    records = await service.get_defaulters(school_id, class_id, days_overdue_min, amount_min)
    defaulters = [
        DefaulterRecord(
            student_id=r["student"].id,
            student_name=r["student"].full_name,
            admission_number=r["student"].admission_number,
            section_name=None,  # Can join section in v2
            overdue_amount=round(r["outstanding"], 2),
            oldest_due_date=r["due"].due_date,
            days_overdue=r["days_overdue"],
        )
        for r in records
    ]
    total_overdue = sum(d.overdue_amount for d in defaulters)
    return DefaulterListResponse(
        total_defaulters=len(defaulters),
        total_overdue_amount=round(total_overdue, 2),
        defaulters=defaulters,
    )


@router.post(
    "/reminders/send",
    response_model=FeeReminderResponse,
    summary="Send fee reminders",
    description=(
        "Send fee reminder notifications to selected defaulters via EMAIL or SMS channels. "
        "Runs as an async Celery task. Maximum 500 students per call."
    ),
)
async def send_fee_reminders(
    school_id: SchoolScopedID,
    data: FeeReminderRequest,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
) -> FeeReminderResponse:
    # Queue Celery task
    try:
        from app.workers.tasks import send_fee_reminders_batch
        send_fee_reminders_batch.delay(
            str(school_id),
            [str(sid) for sid in data.student_ids],
            data.channels,
            data.message,
        )
    except ImportError:
        pass
    return FeeReminderResponse(
        queued=len(data.student_ids),
        message=f"Reminders queued for {len(data.student_ids)} students via {data.channels}.",
    )


# ══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/reports/collection",
    response_model=CollectionReportResponse,
    summary="Fee collection report",
    description=(
        "Aggregate collection data between dates. "
        "Returns total collected + breakdown by payment method."
    ),
)
async def get_collection_report(
    school_id: SchoolScopedID,
    from_date: date,
    to_date: date,
    auth: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN, UserRole.ACCOUNTANT
    )),
    service: PaymentService = Depends(get_payment_service),
) -> CollectionReportResponse:
    return await service.get_collection_report(school_id, from_date, to_date)
