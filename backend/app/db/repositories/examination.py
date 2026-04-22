"""Examination and Grading repositories."""
from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.models.examination import Exam, GradeScale, ExamResult


class ExamRepository(BaseRepository[Exam]):
    """Repository for Exam operations."""
    model = Exam

    async def get_by_academic_year(self, school_id: UUID, year_id: UUID) -> list[Exam]:
        """Get exams for a specific academic year."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.academic_year_id == year_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.start_date.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class GradeScaleRepository(BaseRepository[GradeScale]):
    """Repository for GradeScale operations."""
    model = GradeScale

    async def get_for_school(self, school_id: UUID) -> list[GradeScale]:
        """Get all grade scales for a school."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.deleted_at.is_(None)
        ).order_by(self.model.min_score.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_grade(self, school_id: UUID, score_percentage: float) -> GradeScale | None:
        """Find the matching grade for a percentage score."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.min_score <= score_percentage,
            self.model.max_score >= score_percentage,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ExamResultRepository(BaseRepository[ExamResult]):
    """Repository for ExamResult operations."""
    model = ExamResult

    async def get_by_exam_and_subject(self, school_id: UUID, exam_id: UUID, subject_id: UUID) -> list[ExamResult]:
        """Get results for a specific exam and subject."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.exam_id == exam_id,
            self.model.subject_id == subject_id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_student_results(self, school_id: UUID, student_id: UUID, exam_id: UUID | None = None) -> list[ExamResult]:
        """Get all results for a student, optionally filtered by exam."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.student_id == student_id,
            self.model.deleted_at.is_(None)
        )
        if exam_id:
            stmt = stmt.where(self.model.exam_id == exam_id)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_existing(self, school_id: UUID, exam_id: UUID, student_id: UUID, subject_id: UUID) -> ExamResult | None:
        """Get a specific result entry if it exists."""
        stmt = select(self.model).where(
            self.model.school_id == school_id,
            self.model.exam_id == exam_id,
            self.model.student_id == student_id,
            self.model.subject_id == subject_id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
