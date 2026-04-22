"""Parent service."""
from __future__ import annotations

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.parent import ParentRepository
from app.models.parent import ParentProfile, StudentParentLink
from app.schemas.parent import ParentProfileCreate, StudentParentLinkCreate

class ParentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ParentRepository(db)

    async def create_parent_profile(self, school_id: UUID, data: ParentProfileCreate) -> ParentProfile:
        """Create a new parent profile."""
        parent = ParentProfile(
            school_id=school_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            relationship_type=data.relationship_type,
            occupation=data.occupation,
            annual_income=data.annual_income,
            phone=data.phone,
            email=data.email
        )
        return await self.repo.create(parent)

    async def get_parent_profile(self, parent_id: UUID) -> ParentProfile:
        """Get parent profile by ID."""
        parent = await self.repo.get(parent_id)
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found")
        return parent

    async def link_student_parent(self, school_id: UUID, data: StudentParentLinkCreate) -> StudentParentLink:
        """Link a student to a parent."""
        return await self.repo.link_parent_to_student(
            school_id=school_id,
            student_id=data.student_id,
            parent_id=data.parent_id,
            is_primary=data.is_primary
        )

    async def list_student_parents(self, student_id: UUID) -> list[StudentParentLink]:
        """List all parents linked to a student."""
        return await self.repo.get_student_parent_links(student_id)
