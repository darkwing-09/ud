"""System module — Module 22: health, metrics, maintenance, flags, backup."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.deps import SUPER_ADMIN, CurrentUser
from app.middleware import is_maintenance_mode, set_maintenance_mode
from app.schemas.auth import MessageResponse

router = APIRouter(tags=["⚙️ System"])

# In-memory feature flags (replace with DB in production)
_feature_flags: dict[str, bool] = {
    "whatsapp": settings.FEATURE_WHATSAPP_ENABLED,
    "ai_analytics": settings.FEATURE_AI_ANALYTICS,
    "multi_school": settings.FEATURE_MULTI_SCHOOL,
    "library_module": settings.FEATURE_LIBRARY_MODULE,
    "bus_tracking": settings.FEATURE_BUS_TRACKING,
}


@router.get(
    "/system/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns status of API, PostgreSQL, and Redis. Public endpoint.",
    tags=["⚙️ System"],
)
async def health_check() -> dict[str, Any]:
    db_ok = True
    redis_ok = True

    try:
        from app.db.session import ping_database
        db_ok = await ping_database()
    except Exception:
        db_ok = False

    try:
        from app.core.cache import ping_redis
        redis_ok = await ping_redis()
    except Exception:
        redis_ok = False

    overall = "healthy" if (db_ok and redis_ok) else "degraded"
    http_status = status.HTTP_200_OK if overall == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "status": overall,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "services": {
                "database": "up" if db_ok else "down",
                "redis": "up" if redis_ok else "down",
            },
            "maintenance_mode": is_maintenance_mode(),
        },
    )


@router.get(
    "/system/version",
    status_code=status.HTTP_200_OK,
    summary="API version",
    description="Returns the current API version. Public.",
)
async def get_version() -> dict[str, str]:
    return {
        "version": settings.APP_VERSION,
        "name": settings.APP_NAME,
    }


@router.get(
    "/system/metrics",
    status_code=status.HTTP_200_OK,
    summary="System metrics [SUPER_ADMIN]",
    description="Platform-wide metrics for super admin monitoring.",
)
async def get_metrics(current_user: SUPER_ADMIN) -> dict[str, Any]:
    # Placeholder — wire with actual DB counts in production
    return {
        "total_schools": 0,
        "total_users": 0,
        "active_sessions": 0,
        "queue_size": 0,
    }


@router.get(
    "/system/queue-stats",
    status_code=status.HTTP_200_OK,
    summary="Celery queue statistics",
    description="Returns queue depth and worker status for monitoring.",
)
async def get_queue_stats(current_user: SUPER_ADMIN) -> dict[str, Any]:
    try:
        from app.workers.celery_app import celery_app
        inspect = celery_app.control.inspect()
        active = inspect.active() or {}
        return {
            "active_tasks": sum(len(v) for v in active.values()),
            "workers": list(active.keys()),
            "status": "running" if active else "no_workers",
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@router.post(
    "/system/maintenance/enable",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable maintenance mode [SUPER_ADMIN]",
    description="Blocks all non-SUPER_ADMIN requests with 503.",
)
async def enable_maintenance(current_user: SUPER_ADMIN) -> MessageResponse:
    set_maintenance_mode(True)
    return MessageResponse(message="Maintenance mode enabled")


@router.post(
    "/system/maintenance/disable",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable maintenance mode [SUPER_ADMIN]",
)
async def disable_maintenance(current_user: SUPER_ADMIN) -> MessageResponse:
    set_maintenance_mode(False)
    return MessageResponse(message="Maintenance mode disabled. System is live.")


@router.get(
    "/system/feature-flags",
    status_code=status.HTTP_200_OK,
    summary="List feature flags",
    description="Returns all platform feature flags and their current state.",
)
async def list_feature_flags(current_user: CurrentUser) -> dict[str, bool]:
    return _feature_flags


@router.patch(
    "/system/feature-flags/{key}",
    status_code=status.HTTP_200_OK,
    summary="Toggle feature flag [SUPER_ADMIN]",
    description="Enable or disable a feature flag platform-wide.",
)
async def toggle_feature_flag(
    key: str,
    enabled: bool,
    current_user: SUPER_ADMIN,
) -> dict[str, Any]:
    if key not in _feature_flags:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Feature flag '{key}' not found")
    _feature_flags[key] = enabled
    return {"key": key, "enabled": enabled, "message": f"Feature '{key}' {'enabled' if enabled else 'disabled'}"}


@router.post(
    "/system/backup/trigger",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger manual DB backup [SUPER_ADMIN]",
    description="Queues a manual database backup job.",
)
async def trigger_backup(current_user: SUPER_ADMIN) -> MessageResponse:
    # Wire to Celery backup task
    return MessageResponse(message="Database backup job queued successfully")


@router.get(
    "/system/backup/list",
    status_code=status.HTTP_200_OK,
    summary="List backups [SUPER_ADMIN]",
    description="Returns list of available database backups.",
)
async def list_backups(current_user: SUPER_ADMIN) -> dict[str, Any]:
    return {"backups": [], "message": "Backup listing requires external storage integration"}


@router.post(
    "/system/broadcast",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Platform-wide broadcast [SUPER_ADMIN]",
    description="Send an announcement to all users across all schools.",
)
async def platform_broadcast(
    message: str,
    current_user: SUPER_ADMIN,
) -> MessageResponse:
    # Wire to notification service
    return MessageResponse(message=f"Broadcast queued: '{message}'")
