"""Staff service."""
from __future__ import annotations

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.staff import StaffRepository
from app.models.staff import StaffProfile
from app.schemas.staff import StaffProfileCreate, StaffProfileUpdate
from app.core.exceptions import BaseAppError

class StaffService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StaffRepository(db)

    async def create_staff_profile(self, school_id: UUID, data: StaffProfileCreate) -> StaffProfile:
        """Create a new staff profile."""
        # Check if code already exists
        if data.employee_code:
            existing = await self.repo.get_by_employee_code(school_id, data.employee_code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Staff with code {data.employee_code} already exists"
                )

        # Map data to model
        staff = StaffProfile(
            school_id=school_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            employee_code=data.employee_code,
            designation=data.designation,
            department_id=data.department_id,
            employment_type=data.employment_type,
            official_email=data.official_email,
            phone_primary=data.phone_primary,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_group=data.blood_group,
            personal_email=data.personal_email,
            phone_secondary=data.phone_secondary,
            address=data.address,
            city=data.city,
            state=data.state,
            join_date=data.join_date,
            qualification=data.qualification,
            experience_years=data.experience_years,
            ifsc_code=data.ifsc_code
        )
        
        # Set encrypted fields
        if data.aadhaar:
            staff.set_aadhaar(data.aadhaar)
        if data.pan:
            staff.set_pan(data.pan)
        if data.bank_account:
            staff.set_bank_account(data.bank_account)

        return await self.repo.save(staff)

    async def get_staff_profile(self, staff_id: UUID, school_id: UUID) -> StaffProfile:
        """Get staff profile by ID."""
        staff = await self.repo.get_by_id(staff_id, school_id)
        return staff

    async def list_staff(self, school_id: UUID) -> list[StaffProfile]:
        """List all staff for a school."""
        return await self.repo.list_by_school(school_id)

    async def update_staff_profile(self, staff_id: UUID, school_id: UUID, data: StaffProfileUpdate) -> StaffProfile:
        """Update staff profile."""
        staff = await self.get_staff_profile(staff_id, school_id)
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle PII fields separately
        if "aadhaar" in update_data:
            staff.set_aadhaar(update_data.pop("aadhaar"))
        if "pan" in update_data:
            staff.set_pan(update_data.pop("pan"))
        if "bank_account" in update_data:
            staff.set_bank_account(update_data.pop("bank_account"))
            
        return await self.repo.update(staff, **update_data)
