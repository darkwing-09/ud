"""Middleware stack: request ID, tenant injection, security headers, logging."""
from __future__ import annotations

import time
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.exceptions import MaintenanceModeError

# Maintenance mode flag (set via /system/maintenance endpoints)
_MAINTENANCE_MODE = False


def set_maintenance_mode(enabled: bool) -> None:
    global _MAINTENANCE_MODE
    _MAINTENANCE_MODE = enabled


def is_maintenance_mode() -> bool:
    return _MAINTENANCE_MODE


# ── Request ID Middleware ─────────────────────────────────────
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Injects X-Request-ID header into every request/response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ── Tenant Middleware ─────────────────────────────────────────
class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts school_id from JWT and binds it to request state.
    All subsequent DB queries use request.state.school_id automatically.
    """

    BYPASS_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/verify-email",
        "/system/health",
        "/system/version",
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tenant injection for public paths
        if any(request.url.path.startswith(path) for path in self.BYPASS_PATHS):
            request.state.school_id = None
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            from app.core.security import decode_access_token
            try:
                token = auth_header.split(" ", 1)[1]
                payload = decode_access_token(token)
                school_id = payload.get("school_id")
                request.state.school_id = uuid.UUID(school_id) if school_id else None
                request.state.user_id = uuid.UUID(payload["sub"])
                request.state.user_role = payload.get("role")
                structlog.contextvars.bind_contextvars(
                    school_id=str(school_id) if school_id else None,
                    user_id=payload.get("sub"),
                    role=payload.get("role"),
                )
            except Exception:
                request.state.school_id = None
        else:
            request.state.school_id = None

        return await call_next(request)


# ── Maintenance Mode Middleware ────────────────────────────────
class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """Block all requests when maintenance mode is enabled (except SUPER_ADMIN)."""

    ALWAYS_ALLOW = {"/system/health", "/system/version"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if _MAINTENANCE_MODE and request.url.path not in self.ALWAYS_ALLOW:
            role = getattr(request.state, "user_role", None)
            if role != "SUPER_ADMIN":
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=503,
                    content={"detail": "System is under maintenance. Please try again later."},
                    headers={"Retry-After": "3600"},
                )
        return await call_next(request)


# ── Security Headers Middleware ───────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://checkout.razorpay.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://blob.educore.in https://fastapi.tiangolo.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https://sentry.io https://api.razorpay.com; "
            "frame-src 'self' https://api.razorpay.com; "
            "object-src 'none';"
        )
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        return response


# ── Request Logging Middleware ─────────────────────────────────
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing, status code, and request ID."""

    SKIP_PATHS = {"/system/health", "/system/version"}
    logger = structlog.get_logger("http.access")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        level = "info" if response.status_code < 400 else "warning" if response.status_code < 500 else "error"
        log_fn = getattr(self.logger, level)
        log_fn(
            "HTTP request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else "unknown",
        )
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response
