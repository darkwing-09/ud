"""Alembic env.py — async SQLAlchemy migrations."""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from app.core.config import settings
from app.db.base import Base

# Import ALL models here so Alembic picks them up for autogenerate
from app.models.user import User, RefreshToken, Role, Permission, RolePermission, UserRole
from app.models.school import School
# Add remaining models as modules are built:
from app.models.academic_year import AcademicYear, Term
from app.models.department import Department
from app.models.class_ import Class
from app.models.section import Section
from app.models.subject import Subject, ClassSubjectAssignment
from app.models.staff import StaffProfile
from app.models.student import StudentProfile
from app.models.parent import ParentProfile, StudentParentLink
# from app.models.timetable import TimetableEntry, SubstituteEntry
# from app.models.attendance import AttendanceSession, AttendanceRecord, LeaveRequest
# from app.models.staff_attendance import StaffAttendanceRecord
# from app.models.exam import ExamType, Exam, ExamSchedule, ExamHall
# from app.models.marks import GradeScheme, MarkEntry, Result
# from app.models.fee import FeeCategory, FeeStructure, FeeInvoice, Payment
# from app.models.salary import SalaryStructure, SalaryAssignment
# from app.models.payroll import PayrollBatch, PayrollRecord
# from app.models.leave import LeaveType, LeaveAllocation, LeaveRequest
# from app.models.holiday import Holiday
# from app.models.notice import Notice, Message, Broadcast, Event, Homework
# from app.models.notification import Notification, NotificationPreference
from app.models.document import Document
# from app.models.audit_log import AuditLog

config = context.config
target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override URL from settings (includes pool config)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
