"""Analytics Service."""
from __future__ import annotations

from typing import cast
from uuid import UUID
from datetime import date, timedelta
from calendar import monthrange
from sqlalchemy import select, func

from app.core.exceptions import NotFoundError
from app.core.deps import DBSession
from app.models.student import StudentProfile
from app.models.staff import StaffProfile
from app.models.fee import FeeDue
from app.models.payment import FeePayment
from app.models.attendance import StudentAttendance
from app.models.examination import Exam, ExamResult
from app.models.payroll import PayrollRecord
from app.models.subject import Subject
from app.schemas.analytics import (
    AdminDashboardResponse,
    KPICard,
    FeeCollectionTrendResponse,
    TrendDataPoint,
    DefaulterAgingResponse,
    DefaulterAgingBucket,
    AttendanceSummaryResponse,
    SalaryExpenseTrendResponse,
    AcademicSummaryResponse,
    AcademicSummaryDataPoint,
)


class AnalyticsService:
    def __init__(self, session: DBSession):
        self.session = session

    async def get_admin_dashboard(self, school_id: UUID) -> AdminDashboardResponse:
        total_students = await self.session.scalar(
            select(func.count(StudentProfile.id)).where(
                StudentProfile.school_id == school_id,
                StudentProfile.status == "ACTIVE"
            )
        ) or 0

        total_staff = await self.session.scalar(
            select(func.count(StaffProfile.id)).where(
                StaffProfile.school_id == school_id,
                StaffProfile.status == "ACTIVE"
            )
        ) or 0

        # Current month boundary
        today = date.today()
        first_day = today.replace(day=1)

        fee_collected = await self.session.scalar(
            select(func.sum(FeePayment.amount)).where(
                FeePayment.school_id == school_id,
                FeePayment.status == "SUCCESS",
                func.date(FeePayment.created_at) >= first_day
            )
        ) or 0.0

        outstanding = await self.session.scalar(
            select(func.sum(FeeDue.net_amount - FeeDue.paid_amount)).where(
                FeeDue.school_id == school_id,
                FeeDue.status.in_(["UNPAID", "PARTIAL"]),
                FeeDue.deleted_at.is_(None)
            )
        ) or 0.0

        return AdminDashboardResponse(
            total_students=total_students,
            total_staff=total_staff,
            fee_collected_this_month=float(fee_collected),
            total_outstanding_fees=float(outstanding),
            kpis=[
                KPICard(title="Total Students", value=total_students, trend="+2%", trend_type="positive"),
                KPICard(title="Total Staff", value=total_staff, trend="+0%", trend_type="neutral"),
            ]
        )

    async def get_fee_collection_trend(self, school_id: UUID, months: int = 6) -> FeeCollectionTrendResponse:
        # PostgreSQL specific date truncation grouped by month
        trend_pts = []
        today = date.today()

        for m in reversed(range(months)):
            d = today.replace(day=1) - timedelta(days=m * 28) # approx
            check_date = d.replace(day=1)
            next_month = (check_date.replace(day=28) + timedelta(days=4)).replace(day=1)

            val = await self.session.scalar(
                select(func.sum(FeePayment.amount)).where(
                    FeePayment.school_id == school_id,
                    FeePayment.status == "SUCCESS",
                    func.date(FeePayment.created_at) >= check_date,
                    func.date(FeePayment.created_at) < next_month
                )
            ) or 0.0
            
            trend_pts.append(
                TrendDataPoint(label=check_date.strftime("%b %Y"), value=float(val))
            )

        return FeeCollectionTrendResponse(trend=trend_pts)

    async def get_defaulter_aging(self, school_id: UUID) -> DefaulterAgingResponse:
        today = date.today()
        
        # 0-30
        thirty_days_ago = today - timedelta(days=30)
        sixty_days_ago = today - timedelta(days=60)
        ninety_days_ago = today - timedelta(days=90)

        async def get_bucket(from_date: date | None, to_date: date, name: str) -> DefaulterAgingBucket:
            query = select(
                func.count(FeeDue.id),
                func.sum(FeeDue.net_amount - FeeDue.paid_amount)
            ).where(
                FeeDue.school_id == school_id,
                FeeDue.status.in_(["UNPAID", "PARTIAL"]),
                FeeDue.due_date < today,
                FeeDue.deleted_at.is_(None)
            )
            
            if to_date:
                query = query.where(FeeDue.due_date >= to_date)
            if from_date:
                query = query.where(FeeDue.due_date <= from_date)

            res = (await self.session.execute(query)).first()
            count = res[0] if res and res[0] else 0
            amount = float(res[1]) if res and res[1] else 0.0
            return DefaulterAgingBucket(bucket_name=name, count=count, amount=amount)

        # today to 30 days ago
        b1 = await get_bucket(today, thirty_days_ago, "0-30 Days")
        # 30 to 60 days
        b2 = await get_bucket(thirty_days_ago, sixty_days_ago, "31-60 Days")
        # 60 to 90
        b3 = await get_bucket(sixty_days_ago, ninety_days_ago, "61-90 Days")
        # 90+
        b4 = await get_bucket(ninety_days_ago, date(1970, 1, 1), "90+ Days")

        return DefaulterAgingResponse(buckets=[b1, b2, b3, b4])

    async def get_attendance_summary(self, school_id: UUID, section_id: UUID | None = None, date_: date | None = None) -> AttendanceSummaryResponse:
        target_date = date_ or date.today()
        
        query = select(
            func.count(StudentAttendance.id),
            func.count(StudentAttendance.id).filter(StudentAttendance.status == "PRESENT"),
            func.count(StudentAttendance.id).filter(StudentAttendance.status == "ABSENT"),
            func.count(StudentAttendance.id).filter(StudentAttendance.status == "LATE")
        ).where(
            StudentAttendance.school_id == school_id,
            StudentAttendance.date == target_date
        )
        
        if section_id:
            query = query.where(StudentAttendance.section_id == section_id)
            
        res = (await self.session.execute(query)).first()
        total = res[0] if res and res[0] else 0
        present = res[1] if res and res[1] else 0
        absent = res[2] if res and res[2] else 0
        late = res[3] if res and res[3] else 0
        
        percentage = (present / total * 100) if total > 0 else 0.0
        
        return AttendanceSummaryResponse(
            total_expected=total,
            present=present,
            absent=absent,
            late=late,
            overall_percentage=percentage
        )

    async def get_academic_summary(self, school_id: UUID, exam_id: UUID) -> AcademicSummaryResponse:
        exam = await self.session.scalar(
            select(Exam).where(
                Exam.id == exam_id,
                Exam.school_id == school_id,
                Exam.deleted_at.is_(None)
            )
        )
        if not exam:
            raise NotFoundError("Exam not found")
            
        # Group by subject
        query = select(
            Subject.name,
            func.avg(ExamResult.marks_obtained / ExamResult.max_marks * 100),
            func.count(ExamResult.id)
        ).join(Subject, ExamResult.subject_id == Subject.id).where(
            ExamResult.school_id == school_id,
            ExamResult.exam_id == exam_id,
            ExamResult.published == True,
            ExamResult.deleted_at.is_(None)
        ).group_by(Subject.name)
        
        results = await self.session.execute(query)
        summaries = []
        for name, avg, count in results:
            summaries.append(AcademicSummaryDataPoint(
                label=name,
                average_score=float(avg or 0),
                total_students=count
            ))
            
        return AcademicSummaryResponse(
            exam_name=exam.name,
            subject_summaries=summaries
        )

    async def get_salary_expense_trend(self, school_id: UUID, months: int = 6) -> SalaryExpenseTrendResponse:
        trend_pts = []
        today = date.today()

        for m in reversed(range(months)):
            # This is simplified. In a real DB, we'd query by year/month in PayrollRecord
            target_month = (today.month - m - 1) % 12 + 1
            target_year = today.year + (today.month - m - 1) // 12
            
            val = await self.session.scalar(
                select(func.sum(PayrollRecord.net_salary)).where(
                    PayrollRecord.school_id == school_id,
                    PayrollRecord.status == "DISBURSED",
                    PayrollRecord.month == target_month,
                    PayrollRecord.year == target_year
                )
            ) or 0.0
            
            label = date(target_year, target_month, 1).strftime("%b %Y")
            trend_pts.append(TrendDataPoint(label=label, value=float(val)))

        return SalaryExpenseTrendResponse(trend=trend_pts)
