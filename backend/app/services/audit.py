"""Audit logging service."""
from __future__ import annotations

from uuid import UUID
from app.core.deps import DBSession
from app.db.repositories.audit import AuditRepository
from app.models.audit import AuditLog


class AuditService:
    def __init__(self, session: DBSession):
        self.session = session
        self.repo = AuditRepository(session)

    async def log(
        self,
        action: str,
        module: str,
        school_id: UUID | None = None,
        user_id: UUID | None = None,
        entity_id: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        ip: str | None = None,
        ua: str | None = None,
    ) -> AuditLog:
        """Create a new audit log entry."""
        log_entry = await self.repo.create(
            school_id=school_id,
            user_id=user_id,
            action=action,
            module=module,
            entity_id=entity_id,
            before_state=before,
            after_state=after,
            ip_address=ip,
            user_agent=ua,
        )
        await self.session.commit()
        await self.session.refresh(log_entry)
        return log_entry

    async def get_logs(self, school_id: UUID, limit: int = 100, offset: int = 0):
        return await self.repo.get_by_school(school_id, limit, offset)
