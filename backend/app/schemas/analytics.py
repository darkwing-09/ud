"""Analytics Schemas."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class KPICard(BaseModel):
    title: str
    value: int | float | str
    trend: str | None = None  # e.g., "+5.2% from last month"
    trend_type: str | None = None  # "positive", "negative", "neutral"


class AdminDashboardResponse(BaseModel):
    total_students: int
    total_staff: int
    fee_collected_this_month: float
    total_outstanding_fees: float
    kpis: list[KPICard] = []


class TrendDataPoint(BaseModel):
    label: str  # e.g., "Jan", "Feb" or "Week 1"
    value: float


class FeeCollectionTrendResponse(BaseModel):
    currency: str = "USD"
    trend: list[TrendDataPoint]


class DefaulterAgingBucket(BaseModel):
    bucket_name: str  # "0-30 Days", "31-60 Days", "61-90 Days", "90+ Days"
    count: int
    amount: float


class DefaulterAgingResponse(BaseModel):
    buckets: list[DefaulterAgingBucket]


class AttendanceSummaryResponse(BaseModel):
    total_expected: int
    present: int
    absent: int
    late: int
    overall_percentage: float


class SalaryExpenseTrendResponse(BaseModel):
    trend: list[TrendDataPoint]


class AcademicSummaryDataPoint(BaseModel):
    label: str
    average_score: float
    total_students: int


class AcademicSummaryResponse(BaseModel):
    exam_name: str
    subject_summaries: list[AcademicSummaryDataPoint]
