"""Academic Year and Term API endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.deps import DBSession, SchoolScopedID, require_school_admin
from app.models.user import User
from app.schemas.academic_year import (
    AcademicYearCreate,
    AcademicYearResponse,
    TermCreate,
    TermResponse,
)
from app.services.academic_year import AcademicYearService

router = APIRouter(prefix="/academic-years", tags=["Academic Calendar"])


def get_academic_service(db: DBSession) -> AcademicYearService:
    return AcademicYearService(db)


@router.post(
    "",
    response_model=AcademicYearResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_academic_year(
    school_id: SchoolScopedID,
    data: AcademicYearCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicYearService = Depends(get_academic_service),
) -> AcademicYearResponse:
    """Create a new academic year for the school."""
    return await service.create_year(school_id, data)


@router.get(
    "",
    response_model=list[AcademicYearResponse],
)
async def list_academic_years(
    school_id: SchoolScopedID,
    auth: User = Depends(require_school_admin),
    service: AcademicYearService = Depends(get_academic_service),
) -> list[AcademicYearResponse]:
    """List all academic years for the school."""
    return await service.list_years(school_id)


@router.get(
    "/{year_id}",
    response_model=AcademicYearResponse,
)
async def get_academic_year(
    school_id: SchoolScopedID,
    year_id: UUID,
    auth: User = Depends(require_school_admin),
    service: AcademicYearService = Depends(get_academic_service),
) -> AcademicYearResponse:
    """Get details of a specific academic year."""
    return await service.get_year(school_id, year_id)


@router.post(
    "/{year_id}/activate",
    response_model=AcademicYearResponse,
)
async def activate_academic_year(
    school_id: SchoolScopedID,
    year_id: UUID,
    auth: User = Depends(require_school_admin),
    service: AcademicYearService = Depends(get_academic_service),
) -> AcademicYearResponse:
    """Set an academic year as the active one for the school."""
    return await service.activate_year(school_id, year_id)


@router.post(
    "/{year_id}/terms",
    response_model=TermResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_academic_term(
    school_id: SchoolScopedID,
    year_id: UUID,
    data: TermCreate,
    auth: User = Depends(require_school_admin),
    service: AcademicYearService = Depends(get_academic_service),
) -> TermResponse:
    """Create a new term within an academic year."""
    return await service.create_term(school_id, year_id, data)


@router.get(
    "/{year_id}/terms",
    response_model=list[TermResponse],
)
async def list_academic_terms(
    school_id: SchoolScopedID,
    year_id: UUID,
    auth: User = Depends(require_school_admin),
    service: AcademicYearService = Depends(get_academic_service),
) -> list[TermResponse]:
    """List all terms for an academic year."""
    return await service.list_terms(school_id, year_id)
