"""Master API router — mounts all module sub-routers."""

from fastapi import APIRouter, Depends, Request
from app.core.rate_limit import api_rate_limit

from app.api.v1.auth import router as auth_router
from app.api.v1.system import router as system_router

# Module routers (uncommented as each module is built)
from app.api.v1.school import router as school_router
from app.api.v1.academic_year import router as academic_year_router
from app.api.v1.departments import router as department_router
from app.api.v1.classes import router as class_router
from app.api.v1.subjects import router as subject_router
from app.api.v1.staff import router as staff_router
from app.api.v1.students import router as student_router
from app.api.v1.parents import router as parent_router
from app.api.v1.timetable import router as timetable_router
from app.api.v1.attendance import router as attendance_router
# from app.api.v1.staff_attendance import router as staff_attendance_router
from app.api.v1.exams import router as exam_router
# from app.api.v1.marks import router as marks_router
from app.api.v1.fees import router as fee_router
from app.api.v1.salary import router as salary_router
from app.api.v1.payroll import router as payroll_router
from app.api.v1.leaves import router as leave_router
from app.api.v1.holidays import router as holiday_router
from app.api.v1.notices import router as notice_router
from app.api.v1.messages import router as message_router
from app.api.v1.homework import router as homework_router
from app.api.v1.events import router as event_router
from app.api.v1.notifications import router as notification_router
from app.api.v1.documents import router as document_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.audit_logs import router as audit_router
from app.api.v1.roles import router as roles_router

async def rate_limit_dependency(request: Request):
    await api_rate_limit(request)

api_router = APIRouter(dependencies=[Depends(rate_limit_dependency)])

# ── Always-on modules ─────────────────────────────────────────
api_router.include_router(auth_router)
api_router.include_router(system_router)

# ── Activated as each module is built (uncomment progressively) ─
api_router.include_router(school_router)
api_router.include_router(academic_year_router)
api_router.include_router(department_router)
api_router.include_router(class_router)
api_router.include_router(subject_router)
api_router.include_router(staff_router)
api_router.include_router(student_router)
api_router.include_router(parent_router)
api_router.include_router(timetable_router)
api_router.include_router(attendance_router)
api_router.include_router(exam_router)
# api_router.include_router(marks_router)
api_router.include_router(fee_router)
api_router.include_router(salary_router)
api_router.include_router(payroll_router)
api_router.include_router(leave_router)
api_router.include_router(holiday_router)
api_router.include_router(notice_router)
api_router.include_router(message_router)
api_router.include_router(homework_router)
api_router.include_router(event_router)
api_router.include_router(notification_router)
api_router.include_router(document_router)
api_router.include_router(analytics_router)
api_router.include_router(audit_router)
api_router.include_router(roles_router)
