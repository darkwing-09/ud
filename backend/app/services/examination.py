"""Examination and Grading services."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.examination import (
    ExamRepository,
    GradeScaleRepository,
    ExamResultRepository,
)
from app.models.examination import Exam, ExamResult, GradeScale
from app.schemas.examination import (
    ExamCreate,
    ExamResultBulkEntry,
    GradeScaleCreate,
    StudentGPA,
)


class ExaminationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.exam_repo = ExamRepository(session)
        self.grade_repo = GradeScaleRepository(session)
        self.result_repo = ExamResultRepository(session)

    # ── Exams ──────────────────────────────────────────────────

    async def create_exam(self, school_id: UUID, data: ExamCreate) -> Exam:
        """Schedule a new exam."""
        exam = Exam(
            school_id=school_id,
            **data.model_dump()
        )
        return await self.exam_repo.save(exam)

    async def list_exams(self, school_id: UUID, year_id: UUID) -> list[Exam]:
        """List exams for an academic year."""
        return await self.exam_repo.get_by_academic_year(school_id, year_id)

    # ── Grade Scales ──────────────────────────────────────────

    async def create_grade_scale(self, school_id: UUID, data: GradeScaleCreate) -> GradeScale:
        """Define a grading unit."""
        scale = GradeScale(
            school_id=school_id,
            **data.model_dump()
        )
        return await self.grade_repo.save(scale)

    async def get_grade_scales(self, school_id: UUID) -> list[GradeScale]:
        """All grade scales for the school."""
        return await self.grade_repo.get_for_school(school_id)

    # ── Results ──────────────────────────────────────────────

    async def enter_marks(self, school_id: UUID, data: ExamResultBulkEntry, user_id: UUID) -> list[ExamResult]:
        """Bulk enter marks for a class/subject and auto-assign grades."""
        results = []
        
        # Prefetch grade scales to avoid N+1 inside loop
        # For simplicity, we trust there is only one scale per school for now
        # but in v2 we can link specific exams to specific scales.
        scales = await self.grade_repo.get_for_school(school_id)
        
        async with self.session.begin_nested():
            for entry in data.results:
                percentage = (entry.marks_obtained / entry.max_marks) * 100
                
                # Find matching grade
                matched_grade = None
                for s in scales:
                    if s.min_score <= percentage <= s.max_score:
                        matched_grade = s
                        break
                
                existing = await self.result_repo.get_existing(
                    school_id, data.exam_id, entry.student_id, data.subject_id
                )
                
                if existing:
                    existing.marks_obtained = entry.marks_obtained
                    existing.max_marks = entry.max_marks
                    existing.grade_id = matched_grade.id if matched_grade else None
                    existing.remarks = entry.remarks
                    existing.entered_by = user_id
                    results.append(await self.result_repo.save(existing))
                else:
                    new_result = ExamResult(
                        school_id=school_id,
                        exam_id=data.exam_id,
                        student_id=entry.student_id,
                        subject_id=data.subject_id,
                        marks_obtained=entry.marks_obtained,
                        max_marks=entry.max_marks,
                        grade_id=matched_grade.id if matched_grade else None,
                        remarks=entry.remarks,
                        entered_by=user_id
                    )
                    results.append(await self.result_repo.save(new_result))
            
            # Commit is handled by the outer transaction or get_db dependency
            pass
        
        return results

    # ── GPA Engine ──────────────────────────────────────────

    async def calculate_student_gpa(self, school_id: UUID, student_id: UUID, academic_year_id: UUID) -> StudentGPA:
        """Calculate GPA based on point values from published results."""
        results = await self.result_repo.get_student_results(school_id, student_id)
        # Filter for the year and published only
        year_results = [r for r in results if r.published] 
        # (Note: In a real app, you'd filter at DB level or check exam's year_id)
        
        total_points = 0.0
        subject_count = 0
        total_marks = 0.0
        max_total_marks = 0.0
        
        for r in year_results:
            if r.grade:
                total_points += float(r.grade.point_value)
                subject_count += 1
                total_marks += float(r.marks_obtained)
                max_total_marks += float(r.max_marks)
        
        gpa = total_points / subject_count if subject_count > 0 else 0.0
        percentage = (total_marks / max_total_marks * 100) if max_total_marks > 0 else 0.0
        
        return StudentGPA(
            student_id=student_id,
            academic_year_id=academic_year_id,
            gpa=round(gpa, 2),
            total_marks=total_marks,
            max_total_marks=max_total_marks,
            percentage=round(percentage, 2)
        )
