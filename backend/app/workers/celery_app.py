"""Celery application configuration with named queues."""
from __future__ import annotations

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "educore",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.email_tasks",
        "app.workers.tasks.sms_tasks",
        "app.workers.tasks.pdf_tasks",
        "app.workers.tasks.import_tasks",
        "app.workers.tasks.fee_tasks",
        "app.workers.tasks.payroll_tasks",
        "app.workers.tasks.notification_tasks",
        "app.workers.tasks.analytics_tasks",
        "app.workers.tasks.school",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # One task at a time for long-running jobs
    result_expires=3600,  # Results expire in 1 hour
    task_soft_time_limit=300,   # 5 minutes soft limit
    task_time_limit=600,        # 10 minutes hard limit

    # ── Named Queues ─────────────────────────────────────────
    task_queues={
        "high": {"exchange": "high", "routing_key": "high"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_default_queue="default",
    task_routes={
        # HIGH priority — parent notifications (< 60s SLA)
        "app.workers.tasks.sms_tasks.*": {"queue": "high"},
        "app.workers.tasks.notification_tasks.send_absence_notification": {"queue": "high"},
        "app.workers.tasks.fee_tasks.send_payment_confirmation": {"queue": "high"},

        # DEFAULT priority
        "app.workers.tasks.email_tasks.*": {"queue": "default"},
        "app.workers.tasks.fee_tasks.*": {"queue": "default"},
        "app.workers.tasks.payroll_tasks.*": {"queue": "default"},

        # LOW priority — bulk jobs, reports
        "app.workers.tasks.import_tasks.*": {"queue": "low"},
        "app.workers.tasks.pdf_tasks.*": {"queue": "low"},
        "app.workers.tasks.analytics_tasks.*": {"queue": "low"},
    },

    # ── Celery Beat Schedule (cron jobs) ─────────────────────
    beat_schedule={
        "daily-attendance-summary": {
            "task": "app.workers.tasks.notification_tasks.send_daily_attendance_summary",
            "schedule": {"hour": 16, "minute": 0},  # 4:00 PM IST daily
        },
        "fee-reminder-campaign": {
            "task": "app.workers.tasks.fee_tasks.run_fee_reminder_campaign",
            "schedule": {"hour": 9, "minute": 0},  # 9:00 AM IST daily
        },
        "pre-compute-analytics": {
            "task": "app.workers.tasks.analytics_tasks.precompute_analytics_snapshots",
            "schedule": {"hour": 0, "minute": 30},  # 12:30 AM IST nightly
        },
        "late-fee-calculation": {
            "task": "app.workers.tasks.fee_tasks.calculate_daily_late_fees",
            "schedule": {"hour": 0, "minute": 1},  # 12:01 AM IST daily
        },
    },
)
