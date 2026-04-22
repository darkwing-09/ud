"""School service layer."""
from __future__ import annotations

from uuid import UUID

from fastapi import UploadFile

from app.core.exceptions import BadRequestError, ConflictError
from app.db.repositories.school import SchoolRepository
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolSettingsUpdate
from app.services.storage import StorageService


class SchoolService:
    """Service for managing core school entities."""

    def __init__(self, school_repo: SchoolRepository, storage_service: StorageService | None = None) -> None:
        self.school_repo = school_repo
        self.storage_service = storage_service

    async def create_school(self, data: SchoolCreate) -> School:
        """Create a new tenant school."""
        existing = await self.school_repo.get_by_code(data.code)
        if existing:
            raise ConflictError(f"School with code '{data.code}' already exists")

        # Create school using repo
        school_data = data.model_dump(exclude={"settings"})
        school_data["settings"] = data.settings.model_dump()
        school = await self.school_repo.create(**school_data)
        await self.school_repo.session.commit()
        await self.school_repo.session.refresh(school)
        # from app.workers.tasks.tenant import provision_tenant_resources
        # provision_tenant_resources.delay(str(school.id))

        return school

    async def update_school(self, school_id: UUID, data: SchoolUpdate) -> School:
        """Update basic school details."""
        school = await self.school_repo.get_by_id(id=school_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = await self.school_repo.update(school, **update_data)
        await self.school_repo.session.commit()
        return updated

    async def update_settings(self, school_id: UUID, data: SchoolSettingsUpdate) -> School:
        """Update configurable settings."""
        school = await self.school_repo.get_by_id(id=school_id)
        # Merge existing settings with new
        current_settings = school.settings or {}
        new_settings = data.settings.model_dump()
        merged = {**current_settings, **new_settings}
        
        return await self.school_repo.update(school, settings=merged)

    async def toggle_activation(self, school_id: UUID, is_active: bool) -> School:
        """Suspend or activate a school (Super Admin feature)."""
        school = await self.school_repo.get_by_id(id=school_id)
        if school.is_active == is_active:
            raise BadRequestError(f"School is already {'active' if is_active else 'suspended'}")
        return await self.school_repo.update(school, is_active=is_active)

    async def upload_logo(self, school_id: UUID, file: UploadFile) -> School:
        """Upload and process a school logo."""
        if not self.storage_service:
            raise RuntimeError("StorageService not configured")
        
        school = await self.school_repo.get_by_id(id=school_id)
        
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise BadRequestError("File must be an image")
            
        file_bytes = await file.read()
        file_ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "png"
        path = f"schools/{school.id}/logo.{file_ext}"
        
        # Upload using storage service
        url = await self.storage_service.upload_file(
            file_bytes=file_bytes,
            filename=path,
            content_type=file.content_type
        )
        
        # Note: Celery worker resizing will be handled async if needed
        # from app.workers.tasks.image import resize_logo
        # resize_logo.delay(str(school.id), path)
        
        updated = await self.school_repo.update(school, logo_url=url)
        await self.school_repo.session.commit()
        return updated

    async def get_stats(self, school_id: UUID) -> dict:
        """Aggregate stats."""
        # Verifies existence implicitly
        await self.school_repo.get_by_id(school_id)
        return await self.school_repo.get_stats(school_id)
