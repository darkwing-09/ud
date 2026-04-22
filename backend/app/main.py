"""FastAPI application — lifespan, middleware stack, router mount."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.exceptions import BaseAppError
from app.core.logging import configure_logging, get_logger
from app.middleware import (
    MaintenanceModeMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    TenantMiddleware,
)

logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    configure_logging()
    logger.info("EduCore API starting up", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Validate DB connection
    try:
        from app.db.session import ping_database
        await ping_database()
        logger.info("✅ PostgreSQL connected")
    except Exception as exc:
        logger.error("❌ PostgreSQL connection failed", error=str(exc))
        raise

    # Validate Redis connection
    try:
        from app.core.cache import ping_redis
        await ping_redis()
        logger.info("✅ Redis connected")
    except Exception as exc:
        logger.error("❌ Redis connection failed", error=str(exc))
        raise

    # Initialize Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=0.1,
            environment=settings.APP_ENV,
            release=settings.APP_VERSION,
        )
        logger.info("✅ Sentry initialized")

    logger.info("🚀 EduCore API ready to serve requests")
    yield

    # Shutdown
    from app.core.cache import close_cache
    await close_cache()
    logger.info("👋 EduCore API shut down gracefully")


# ── App Instance ──────────────────────────────────────────────
app = FastAPI(
    title="EduCore School Management Platform",
    description="""
## 🏫 EduCore API — Complete School Automation Platform

**Zero paperwork. 100% digital. Every role, every workflow.**

### Modules
- 🔐 Authentication & 2FA
- 🏫 School Management
- 📅 Academic Years & Terms
- 🏛️ Structures (Departments, Classes, Sections)
- 📚 Subjects & Assignments
- 👨🏫 Staff Management & HR
- 🎓 Student Management
- 👨‍👩‍👧 Parent Management
- 🗓️ Timetable Engine
- ✅ Attendance (Student + Staff)
- 📝 Examinations & Marks
- 💰 Fee Management & Payments
- 💼 Salary & Payroll
- 🏖️ Leave Management
- 📢 Communication & Notices
- 🔔 Notifications
- 📁 Document Management
- 📊 Analytics & Reports
- 🔍 Audit Logs
- ⚙️ System & RBAC

### Authentication
Use `POST /api/v1/auth/login` → copy `access_token` → click **Authorize** (🔒) above.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-School-ID"],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-Total-Count"],
)

# ── Custom Middleware (applied in reverse order) ───────────────
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MaintenanceModeMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(RequestIDMiddleware)


# ── Global Exception Handler ──────────────────────────────────
@app.exception_handler(BaseAppError)
async def app_error_handler(request: Request, exc: BaseAppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": type(exc).__name__,
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception", error=str(exc), path=request.url.path, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred", "error_code": "InternalServerError"},
    )


# ── Routers ───────────────────────────────────────────────────
from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix=settings.API_PREFIX)


# ── Root ──────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root() -> dict[str, Any]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/system/health",
    }
