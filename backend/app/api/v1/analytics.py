"""Analytics API Routing."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from uuid import UUID

from app.core.deps import DBSession, SchoolScopedID, require_school_admin, require_roles
from app.models.user import User
from app.schemas.analytics import (
    AdminDashboardResponse,
    FeeCollectionTrendResponse,
    DefaulterAgingResponse,
    AttendanceSummaryResponse,
    AcademicSummaryResponse,
    SalaryExpenseTrendResponse,
)
from app.services.analytics import AnalyticsService
from datetime import date

router = APIRouter(tags=["Analytics"], prefix="/analytics")

def get_analytics_service(db: DBSession) -> AnalyticsService:
    return AnalyticsService(db)

@router.get("/admin/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AdminDashboardResponse:
    """Fetch high-level KPIs for administrative dashboard."""
    return await service.get_admin_dashboard(school_id)

@router.get("/fees/trend", response_model=FeeCollectionTrendResponse)
async def get_fee_collection_trend(
    school_id: SchoolScopedID,
    months: int = 6,
    auth: User = Depends(require_school_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> FeeCollectionTrendResponse:
    """Fetch a monthly trend line for fee collections."""
    return await service.get_fee_collection_trend(school_id, months)

@router.get("/fees/defaulter-aging", response_model=DefaulterAgingResponse)
async def get_defaulter_aging(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> DefaulterAgingResponse:
    """Fetch aging buckets for outstanding fees."""
    return await service.get_defaulter_aging(school_id)

@router.get("/attendance/summary", response_model=AttendanceSummaryResponse)
async def get_attendance_summary(
    school_id: SchoolScopedID,
    section_id: UUID | None = None,
    target_date: date | None = None,
    auth: User = Depends(require_school_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AttendanceSummaryResponse:
    """Fetch daily attendance aggregate stats."""
    return await service.get_attendance_summary(school_id, section_id, target_date)

@router.get("/academic/summary/{exam_id}", response_model=AcademicSummaryResponse)
async def get_academic_summary(
    school_id: SchoolScopedID,
    exam_id: UUID,
    auth: User = Depends(require_school_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AcademicSummaryResponse:
    """Fetch class/subject performance for a specific exam."""
    return await service.get_academic_summary(school_id, exam_id)

@router.get("/salary/trend", response_model=SalaryExpenseTrendResponse)
async def get_salary_expense_trend(
    school_id: SchoolScopedID,
    months: int = 6,
    auth: User = Depends(require_school_admin),
    service: AnalyticsService = Depends(get_analytics_service),
) -> SalaryExpenseTrendResponse:
    """Fetch monthly trend of school salary expenses."""
    return await service.get_salary_expense_trend(school_id, months)
