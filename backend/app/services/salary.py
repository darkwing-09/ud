"""Salary business logic service."""
from __future__ import annotations

from typing import cast
from uuid import UUID
from datetime import date

from app.core.deps import DBSession
from app.core.exceptions import NotFoundError, ValidationError
from app.db.repositories.salary import (
    SalaryAdvanceRepository,
    SalaryStructureRepository,
    StaffSalaryAssignmentRepository,
)
from app.db.repositories.staff import StaffRepository
from app.schemas.salary import SalaryAdvanceCreate, SalaryStructureCreate, StaffSalaryAssignmentCreate
from app.models.salary import SalaryAdvance, SalaryStructure, StaffSalaryAssignment


class SalaryService:
    def __init__(self, session: DBSession):
        self.session = session
        self.structure_repo = SalaryStructureRepository(session)
        self.assignment_repo = StaffSalaryAssignmentRepository(session)
        self.advance_repo = SalaryAdvanceRepository(session)
        self.staff_repo = StaffRepository(session)

    async def create_structure(self, school_id: UUID, data: SalaryStructureCreate) -> SalaryStructure:
        """Create a new template for salary structure."""
        new_structure = SalaryStructure(
            school_id=school_id,
            name=data.name,
            description=data.description,
            basic_salary=data.basic_salary,
            hra=data.hra,
            da=data.da,
            allowances=data.allowances,
            pf_percentage=data.pf_percentage,
            esi_percentage=data.esi_percentage,
            professional_tax=data.professional_tax,
            is_active=data.is_active,
        )
        self.structure_repo.add(new_structure)
        await self.session.commit()
        await self.session.refresh(new_structure)
        return new_structure

    async def get_structures(self, school_id: UUID) -> list[SalaryStructure]:
        """List all structures for the school."""
        return await self.structure_repo.get_by_school(school_id)

    async def assign_staff(self, school_id: UUID, data: StaffSalaryAssignmentCreate) -> StaffSalaryAssignment:
        """Map staff member to a salary structure."""
        staff = await self.staff_repo.get_by_id(data.staff_id)
        if not staff or getattr(staff, "school_id", None) != school_id:
            raise NotFoundError("Staff member not found in this school.")

        struct = await self.structure_repo.get_by_id(data.structure_id)
        if not struct or struct.school_id != school_id:
            raise NotFoundError("Salary structure not found in this school.")

        # Close existing assignment if overlapping
        existing = await self.assignment_repo.get_active_for_staff(data.staff_id, data.effective_from)
        if existing:
            existing.effective_until = data.effective_from

        assignment = StaffSalaryAssignment(
            school_id=school_id,
            staff_id=data.staff_id,
            structure_id=data.structure_id,
            effective_from=data.effective_from,
            effective_until=data.effective_until,
        )
        self.assignment_repo.add(assignment)
        await self.session.commit()
        await self.session.refresh(assignment)
        return assignment

    async def request_advance(self, school_id: UUID, data: SalaryAdvanceCreate) -> SalaryAdvance:
        """Staff request for an advance."""
        advance = SalaryAdvance(
            school_id=school_id,
            staff_id=data.staff_id,
            amount=data.amount,
            reason=data.reason,
            emi_amount=data.emi_amount,
            deduction_start_month=data.deduction_start_month,
            deduction_start_year=data.deduction_start_year,
            status="PENDING",
        )
        self.advance_repo.add(advance)
        await self.session.commit()
        await self.session.refresh(advance)
        return advance

    async def review_advance(self, school_id: UUID, advance_id: UUID, approved: bool, user_id: UUID) -> SalaryAdvance:
        """HR/Admin review of salary advance."""
        advance = await self.advance_repo.get_by_id(advance_id)
        if not advance or advance.school_id != school_id:
            raise NotFoundError("Salary advance request not found.")
        
        if advance.status != "PENDING":
            raise ValidationError(f"Cannot review advance that is already {advance.status}.")
            
        advance.status = "APPROVED" if approved else "REJECTED"
        advance.approved_by_id = user_id
        
        await self.session.commit()
        await self.session.refresh(advance)
        return advance
