"""Payment Service — Razorpay integration, cash recording, receipt generation."""
from __future__ import annotations

import hashlib
import hmac
from datetime import date
from uuid import UUID

# razorpay imported lazily in the razorpay_client property below
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.repositories.fee import FeeDueRepository, FeePaymentRepository
from app.models.fee import FeeDue
from app.models.payment import FeePayment
from app.schemas.fee import (
    CashPaymentRequest,
    CollectionBreakdown,
    CollectionReportResponse,
    FeePaymentResponse,
    OutstandingReportResponse,
    PaymentInitiateRequest,
    RazorpayOrderResponse,
)


class PaymentService:
    """Handles Razorpay online payments, cash recording, and collection reports."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repo = FeePaymentRepository(session)
        self.due_repo = FeeDueRepository(session)
        self._razorpay: object | None = None

    @property
    def razorpay_client(self) -> "razorpay.Client":  # type: ignore[name-defined]
        """Lazily instantiate Razorpay client from config."""
        if self._razorpay is None:
            try:
                import razorpay  # noqa: PLC0415
            except ModuleNotFoundError as exc:
                raise ImportError(
                    "razorpay package not available. Ensure it is installed."
                ) from exc
            self._razorpay = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
        return self._razorpay

    # ── Razorpay Payment Flow ─────────────────────────────────────────────

    async def initiate_payment(
        self, school_id: UUID, data: PaymentInitiateRequest
    ) -> RazorpayOrderResponse:
        """
        Validate selected dues, compute total (incl. late fees),
        create Razorpay order, and return order details for frontend checkout.
        """
        dues = await self._resolve_and_validate_dues(school_id, data.fee_due_ids)

        total_paise = int(sum(
            max(0.0, float(d.net_amount) + float(d.late_fee_amount) - float(d.paid_amount))
            for d in dues
        ) * 100)

        if total_paise <= 0:
            raise ValidationError("All selected dues are already fully paid.")

        # Razorpay order creation
        order = self.razorpay_client.order.create({
            "amount": total_paise,
            "currency": "INR",
            "receipt": f"school-{str(school_id)[:8]}-{str(data.student_id)[:8]}",
            "notes": {
                "school_id": str(school_id),
                "student_id": str(data.student_id),
            },
        })

        # Create a PENDING payment record for the first due (split across dues in webhook)
        async with self.session.begin():
            payment = FeePayment(
                school_id=school_id,
                student_id=data.student_id,
                fee_due_id=dues[0].id,  # Primary due; webhook handles multi-due
                amount=total_paise / 100,
                payment_method="ONLINE",
                status="PENDING",
                gateway_order_id=order["id"],
            )
            self.session.add(payment)
            await self.session.flush()
            await self.session.refresh(payment)

        return RazorpayOrderResponse(
            razorpay_order_id=order["id"],
            amount=total_paise,
            currency="INR",
            key_id=settings.RAZORPAY_KEY_ID,
            fee_payment_id=payment.id,
        )

    async def verify_payment(
        self,
        school_id: UUID,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        fee_payment_id: UUID,
    ) -> FeePayment:
        """
        1. Verify HMAC-SHA256 signature.
        2. Idempotency: skip if already processed.
        3. Update payment + mark dues PAID.
        """
        # Idempotency guard — never process the same payment twice
        existing = await self.payment_repo.get_by_gateway_payment_id(school_id, razorpay_payment_id)
        if existing and existing.status == "SUCCESS":
            return existing

        # Verify Razorpay signature (HMAC-SHA256)
        self._verify_razorpay_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        )

        # Fetch PENDING payment
        payment = await self.payment_repo.get_by_id(fee_payment_id, school_id)
        if payment.status != "PENDING":
            raise ConflictError(f"Payment {fee_payment_id} is not in PENDING state.")

        due = await self.due_repo.get_by_id(payment.fee_due_id, school_id)
        receipt_number = await self.payment_repo.get_next_receipt_number(school_id)

        async with self.session.begin():
            payment.status = "SUCCESS"
            payment.gateway_payment_id = razorpay_payment_id
            payment.gateway_signature = razorpay_signature
            payment.receipt_number = receipt_number
            self.session.add(payment)

            # Mark due as paid
            new_paid = float(due.paid_amount) + float(payment.amount)
            due.paid_amount = new_paid
            outstanding = float(due.net_amount) + float(due.late_fee_amount) - new_paid
            due.status = "PAID" if outstanding <= 0.01 else "PARTIAL"
            self.session.add(due)

        # Queue receipt PDF (non-blocking)
        self._queue_receipt_pdf(payment.id)

        return payment

    def _verify_razorpay_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> None:
        """Raise ValidationError if Razorpay signature verification fails."""
        body = f"{order_id}|{payment_id}"
        expected = hmac.new(
            key=settings.RAZORPAY_KEY_SECRET.encode("utf-8"),
            msg=body.encode("utf-8"),
            digestmod="sha256",
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise ValidationError("Razorpay signature verification failed.")

    # ── Webhook Handler ───────────────────────────────────────────────────

    async def process_webhook(
        self, payload: dict, webhook_signature: str, raw_body: bytes
    ) -> None:
        """
        Razorpay webhook — idempotent. Validates signature then processes event.
        Supported events: payment.captured, payment.failed
        """
        self._verify_webhook_signature(raw_body, webhook_signature)
        event = payload.get("event", "")

        if event == "payment.captured":
            payment_entity = payload["payload"]["payment"]["entity"]
            razorpay_payment_id = payment_entity["id"]
            razorpay_order_id = payment_entity["order_id"]

            # Extract school_id from notes if possible, else we can't scope it easily
            # However, get_by_gateway_order_id now requires school_id.
            # We should pass it to the repo if we can find it.
            notes = payment_entity.get("notes", {})
            school_id_str = notes.get("school_id")
            if not school_id_str:
                return # Can't process without school context
            
            school_id = UUID(school_id_str)

            # Idempotency
            if await self.payment_repo.get_by_gateway_payment_id(school_id, razorpay_payment_id):
                return  # Already processed

            # Find PENDING payment by order_id
            pending = await self.payment_repo.get_by_gateway_order_id(school_id, razorpay_order_id)
            if not pending:
                return  # Unknown order — ignore

            due = await self.due_repo.get_by_id(pending.fee_due_id, pending.school_id)
            receipt_number = await self.payment_repo.get_next_receipt_number(pending.school_id)

            async with self.session.begin():
                pending.status = "SUCCESS"
                pending.gateway_payment_id = razorpay_payment_id
                pending.receipt_number = receipt_number
                self.session.add(pending)

                new_paid = float(due.paid_amount) + float(pending.amount)
                due.paid_amount = new_paid
                outstanding = float(due.net_amount) + float(due.late_fee_amount) - new_paid
                due.status = "PAID" if outstanding <= 0.01 else "PARTIAL"
                self.session.add(due)

            self._queue_receipt_pdf(pending.id)

        elif event == "payment.failed":
            payment_entity = payload["payload"]["payment"]["entity"]
            razorpay_order_id = payment_entity["order_id"]
            notes = payment_entity.get("notes", {})
            school_id_str = notes.get("school_id")
            if school_id_str:
                school_id = UUID(school_id_str)
                pending = await self.payment_repo.get_by_gateway_order_id(school_id, razorpay_order_id)
                if pending:
                    async with self.session.begin():
                        pending.status = "FAILED"
                        self.session.add(pending)

    def _verify_webhook_signature(self, raw_body: bytes, signature: str) -> None:
        """Verify webhook using Razorpay-Webhook-Secret."""
        expected = hmac.new(
            key=settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
            msg=raw_body,
            digestmod="sha256",
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise ValidationError("Invalid Razorpay webhook signature.")

    def _queue_receipt_pdf(self, payment_id: UUID) -> None:
        """Queue async receipt PDF generation (Celery task)."""
        try:
            from app.workers.tasks import generate_fee_receipt_pdf
            generate_fee_receipt_pdf.delay(str(payment_id))
        except ImportError:
            pass  # Celery not configured in this environment

    # ── Cash / Offline Payment ────────────────────────────────────────────

    async def record_cash_payment(
        self,
        school_id: UUID,
        data: CashPaymentRequest,
        recorded_by_id: UUID,
    ) -> list[FeePayment]:
        """
        Record offline cash/cheque/UPI payment for one or more dues.
        Distributes `amount` across selected dues in due_date order.
        """
        dues = await self._resolve_and_validate_dues(school_id, data.fee_due_ids)
        remaining = data.amount
        payments: list[FeePayment] = []

        async with self.session.begin():
            for due in dues:
                if remaining <= 0:
                    break
                outstanding = max(
                    0.0,
                    float(due.net_amount) + float(due.late_fee_amount) - float(due.paid_amount)
                )
                if outstanding <= 0:
                    continue

                pay_amount = min(remaining, outstanding)
                receipt_number = await self.payment_repo.get_next_receipt_number(school_id)

                payment = FeePayment(
                    school_id=school_id,
                    student_id=data.student_id,
                    fee_due_id=due.id,
                    amount=pay_amount,
                    payment_method=data.payment_method,
                    status="SUCCESS",
                    receipt_number=receipt_number,
                    remarks=data.remarks,
                    recorded_by_id=recorded_by_id,
                )
                self.session.add(payment)
                await self.session.flush()
                await self.session.refresh(payment)
                payments.append(payment)

                # Update due
                new_paid = float(due.paid_amount) + pay_amount
                due.paid_amount = new_paid
                new_out = float(due.net_amount) + float(due.late_fee_amount) - new_paid
                due.status = "PAID" if new_out <= 0.01 else "PARTIAL"
                self.session.add(due)

                remaining -= pay_amount

        for p in payments:
            self._queue_receipt_pdf(p.id)

        return payments

    # ── Payment History ───────────────────────────────────────────────────

    async def get_payment_history(
        self, school_id: UUID, student_id: UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[FeePayment], int]:
        """Paginated payment history for a student."""
        return await self.payment_repo.get_student_payments(
            school_id, student_id, skip, limit
        )

    async def get_payment(self, school_id: UUID, payment_id: UUID) -> FeePayment:
        """Get a specific payment record."""
        return await self.payment_repo.get_by_id(payment_id, school_id)

    # ── Collection Report ─────────────────────────────────────────────────

    async def get_collection_report(
        self, school_id: UUID, from_date: date, to_date: date
    ) -> CollectionReportResponse:
        """Aggregate fee collection by method and class."""
        payments = await self.payment_repo.get_collection_summary(
            school_id, from_date, to_date
        )

        total = sum(float(p.amount) for p in payments)

        # Group by method
        method_totals: dict[str, tuple[float, int]] = {}
        for p in payments:
            m = p.payment_method
            prev = method_totals.get(m, (0.0, 0))
            method_totals[m] = (prev[0] + float(p.amount), prev[1] + 1)

        breakdown_by_method = [
            CollectionBreakdown(label=k, amount=round(v, 2), count=c)
            for k, (v, c) in method_totals.items()
        ]

        return CollectionReportResponse(
            total_collected=round(total, 2),
            from_date=from_date,
            to_date=to_date,
            breakdown_by_method=breakdown_by_method,
            breakdown_by_class=[],  # Requires join to student→section→class, handled in v2
        )

    # ── Internal Helpers ──────────────────────────────────────────────────

    async def _resolve_and_validate_dues(
        self, school_id: UUID, due_ids: list[UUID]
    ) -> list[FeeDue]:
        """Fetch and validate dues belong to the school and are payable."""
        dues: list[FeeDue] = []
        for due_id in due_ids:
            due = await self.due_repo.get_by_id(due_id, school_id)
            if due.status in ("PAID", "WAIVED"):
                raise ValidationError(
                    f"Due {due_id} (period: {due.period_label}) is already {due.status}."
                )
            dues.append(due)
        return sorted(dues, key=lambda d: d.due_date)
