"""Student service."""
from __future__ import annotations

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.student import StudentRepository
from app.models.student import StudentProfile
from app.schemas.student import StudentProfileCreate, StudentProfileUpdate

class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StudentRepository(db)

    async def create_student_profile(self, school_id: UUID, data: StudentProfileCreate) -> StudentProfile:
        """Create a new student profile."""
        # Check if admission number exists
        existing = await self.repo.get_by_admission_number(school_id, data.admission_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with admission number {data.admission_number} already exists"
            )

        student = StudentProfile(
            school_id=school_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            admission_number=data.admission_number,
            roll_number=data.roll_number,
            current_section_id=data.current_section_id,
            academic_year_id=data.academic_year_id,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_group=data.blood_group,
            religion=data.religion,
            caste_category=data.caste_category,
            admission_date=data.admission_date,
            previous_school=data.previous_school,
            address=data.address,
            city=data.city,
            state=data.state
        )
        
        if data.aadhaar:
            student.set_aadhaar(data.aadhaar)

        return await self.repo.save(student)

    async def get_student_profile(self, student_id: UUID, school_id: UUID) -> StudentProfile:
        """Get student profile by ID."""
        student = await self.repo.get_by_id(student_id, school_id)
        return student

    async def list_students(self, school_id: UUID, section_id: UUID | None = None) -> list[StudentProfile]:
        """List students by school or section."""
        if section_id:
            return await self.repo.list_by_section(school_id, section_id)
        return await self.repo.list_by_school(school_id)

    async def update_student_profile(self, student_id: UUID, school_id: UUID, data: StudentProfileUpdate) -> StudentProfile:
        """Update student profile."""
        student = await self.get_student_profile(student_id, school_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if "aadhaar" in update_data:
            student.set_aadhaar(update_data.pop("aadhaar"))
            
        return await self.repo.update(student, **update_data)
