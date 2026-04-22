"""Academic Structure management service."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError
from app.db.repositories.academic_structure import (
    DepartmentRepository,
    ClassRepository,
    SectionRepository,
    SubjectRepository,
    ClassSubjectAssignmentRepository,
)
from app.db.repositories.academic_year import AcademicYearRepository
from app.models.department import Department
from app.models.class_ import Class
from app.models.section import Section
from app.models.subject import Subject, ClassSubjectAssignment
from app.schemas.academic_structure import (
    DepartmentCreate,
    DepartmentUpdate,
    ClassCreate,
    ClassUpdate,
    SectionCreate,
    SectionUpdate,
    SubjectCreate,
    SubjectUpdate,
    ClassSubjectAssignmentCreate,
    ClassSubjectAssignmentUpdate,
)


class AcademicStructureService:
    """Business logic for organizational units, classes, and subjects."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.dept_repo = DepartmentRepository(db)
        self.class_repo = ClassRepository(db)
        self.section_repo = SectionRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.assign_repo = ClassSubjectAssignmentRepository(db)
        self.year_repo = AcademicYearRepository(db)

    # ── Departments ──────────────────────────────────────────────
    async def create_department(self, school_id: UUID, data: DepartmentCreate) -> Department:
        dept = await self.dept_repo.create(school_id=school_id, **data.model_dump())
        await self.db.commit()
        await self.db.refresh(dept)
        return dept

    async def list_departments(self, school_id: UUID) -> list[Department]:
        return await self.dept_repo.get_by_school(school_id)

    # ── Classes ──────────────────────────────────────────────────
    async def create_class(self, school_id: UUID, data: ClassCreate) -> Class:
        # Get active academic year
        active_year = await self.year_repo.get_active_year(school_id)
        if not active_year:
            raise BadRequestError("No active academic year found. Create and activate a year first.")

        # Check department if provided
        if data.department_id:
            dept = await self.dept_repo.get_by_id(data.department_id, school_id)
            if not dept:
                raise BadRequestError("Department not found or belongs to another school")

        new_class = await self.class_repo.create(
            school_id=school_id,
            academic_year_id=active_year.id,
            **data.model_dump()
        )
        await self.db.commit()
        await self.db.refresh(new_class)
        return new_class

    async def list_classes(self, school_id: UUID) -> list[Class]:
        active_year = await self.year_repo.get_active_year(school_id)
        if not active_year:
            return []
        return await self.class_repo.get_by_school_year(school_id, active_year.id)

    # ── Sections ──────────────────────────────────────────────────
    async def create_section(self, school_id: UUID, class_id: UUID, data: SectionCreate) -> Section:
        parent_class = await self.class_repo.get_by_id(class_id, school_id)
        if not parent_class:
            raise BadRequestError("Class not found or belongs to another school")

        section = await self.section_repo.create(
            school_id=school_id,
            class_id=class_id,
            **data.model_dump()
        )
        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def list_sections(self, school_id: UUID, class_id: UUID) -> list[Section]:
        return await self.section_repo.get_by_class(school_id, class_id)

    # ── Subjects ──────────────────────────────────────────────────
    async def create_subject(self, school_id: UUID, data: SubjectCreate) -> Subject:
        subject = await self.subject_repo.create(school_id=school_id, **data.model_dump())
        await self.db.commit()
        await self.db.refresh(subject)
        return subject

    async def list_subjects(self, school_id: UUID) -> list[Subject]:
        return await self.subject_repo.get_by_school(school_id)

    # ── Assignment ───────────────────────────────────────────────
    async def assign_subject(
        self, 
        school_id: UUID, 
        class_id: UUID, 
        data: ClassSubjectAssignmentCreate
    ) -> ClassSubjectAssignment:
        # Validate class
        parent_class = await self.class_repo.get_by_id(class_id, school_id)
        if not parent_class:
            raise BadRequestError("Class not found")

        # Validate section if provided
        if data.section_id:
            section = await self.section_repo.get_by_id(data.section_id, school_id)
            if not section or section.class_id != class_id:
                raise BadRequestError("Section not found or does not belong to the class")

        # Validate subject
        subject = await self.subject_repo.get_by_id(data.subject_id, school_id)
        if not subject:
            raise BadRequestError("Subject not found")

        assignment = await self.assign_repo.create(
            school_id=school_id,
            academic_year_id=parent_class.academic_year_id,
            class_id=class_id,
            **data.model_dump()
        )
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment
