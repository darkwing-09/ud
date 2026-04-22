"""All models for Alembic discovery."""
from app.models.school import School
from app.models.academic_year import AcademicYear
from app.models.department import Department
from app.models.class_ import Class
from app.models.section import Section
from app.models.subject import Subject, ClassSubjectAssignment
from app.models.user import User
from app.models.staff import StaffProfile
from app.models.student import StudentProfile
from app.models.parent import ParentProfile
from app.models.attendance import StudentAttendance, StaffAttendance
from app.models.timetable import TimetableSlot, TimetableEntry
from app.models.examination import Exam, GradeScale, ExamResult
from app.models.document import Document
from app.models.fee import (
    FeeStructure, FeeComponent, FeeAssignment,
    FeeDiscount, StudentFeeDiscount, FeeDue,
)
from app.models.payment import FeePayment
from app.models.salary import SalaryStructure, StaffSalaryAssignment, SalaryAdvance
from app.models.payroll import PayrollRecord
from app.models.leave import LeaveType, StaffLeaveBalance, LeaveApplication, Holiday
from app.models.notice import Notice
from app.models.message import Message
from app.models.homework import HomeworkAssignment
from app.models.event import SchoolEvent
from app.models.notification import Notification, NotificationTemplate
from app.models.audit import AuditLog
