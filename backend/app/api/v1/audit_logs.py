"""Audit Log Endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from app.services.audit import AuditService

router = APIRouter(tags=["Audit Logs"], prefix="/audit-logs")

def get_audit_service(db: DBSession) -> AuditService:
    return AuditService(db)

@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    school_id: SchoolScopedID,
    limit: int = 100,
    offset: int = 0,
    auth: User = Depends(require_school_admin),
    service: AuditService = Depends(get_audit_service),
) -> list[AuditLogResponse]:
    """Fetch audit logs for the current school."""
    return await service.get_logs(school_id, limit, offset)
