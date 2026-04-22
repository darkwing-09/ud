"""Domain exceptions with HTTP code mappings."""
from __future__ import annotations

from fastapi import HTTPException, status


class BaseAppError(Exception):
    """Base exception for all application errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(status_code=self.status_code, detail=self.detail)


class APIError(BaseAppError):
    """Generic API error."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"


# ── 400 Bad Request ───────────────────────────────────────────
class ValidationError(BaseAppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation failed"


class BadRequestError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"


class InvalidCredentialsError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"


class InvalidTokenError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token is invalid or expired"


class TokenBlacklistedError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has been revoked"


class InvalidOTPError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "OTP is invalid or expired"


class WeakPasswordError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Password does not meet security requirements"


class SamePasswordError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "New password must be different from current password"


class InvalidFileTypeError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "File type is not allowed"


class FileTooLargeError(BaseAppError):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    detail = "File size exceeds maximum allowed limit"


class BulkImportError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bulk import failed"


class PaymentAlreadyProcessedError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Payment has already been processed"


class MarksAlreadyPublishedError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Marks have been published and cannot be modified"


class AttendanceAlreadyMarkedError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Attendance has already been marked for this session"


class InsufficientLeaveBalanceError(BaseAppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Insufficient leave balance"


class LeaveConflictError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Leave request conflicts with existing approved leave"


class TimetableConflictError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Timetable conflict: teacher or section already assigned at this time"


# ── 401 Unauthorized ──────────────────────────────────────────
class AuthenticationError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication required"


class AccountLockedError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Account is locked due to too many failed login attempts"


class AccountInactiveError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Account is inactive. Contact your administrator"


class EmailNotVerifiedError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Email address is not verified"


class TwoFactorRequiredError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Two-factor authentication is required"


# ── 403 Forbidden ─────────────────────────────────────────────
class ForbiddenError(BaseAppError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You do not have permission to perform this action"


class CrossTenantAccessError(BaseAppError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access to another school's data is not allowed"


class SystemRoleModificationError(BaseAppError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "System roles cannot be modified or deleted"


# ── 404 Not Found ─────────────────────────────────────────────
class NotFoundError(BaseAppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class UserNotFoundError(NotFoundError):
    detail = "User not found"


class SchoolNotFoundError(NotFoundError):
    detail = "School not found"


class StudentNotFoundError(NotFoundError):
    detail = "Student not found"


class StaffNotFoundError(NotFoundError):
    detail = "Staff member not found"


class ClassNotFoundError(NotFoundError):
    detail = "Class not found"


class SectionNotFoundError(NotFoundError):
    detail = "Section not found"


class SubjectNotFoundError(NotFoundError):
    detail = "Subject not found"


class ExamNotFoundError(NotFoundError):
    detail = "Exam not found"


class FeeStructureNotFoundError(NotFoundError):
    detail = "Fee structure not found"


class InvoiceNotFoundError(NotFoundError):
    detail = "Fee invoice not found"


class PaymentNotFoundError(NotFoundError):
    detail = "Payment not found"


class DocumentNotFoundError(NotFoundError):
    detail = "Document not found"


class NoticeNotFoundError(NotFoundError):
    detail = "Notice not found"


class LeaveRequestNotFoundError(NotFoundError):
    detail = "Leave request not found"


class AcademicYearNotFoundError(NotFoundError):
    detail = "Academic year not found"


class PayrollNotFoundError(NotFoundError):
    detail = "Payroll record not found"


# ── 409 Conflict ──────────────────────────────────────────────
class ConflictError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource already exists"


class EmailAlreadyExistsError(ConflictError):
    detail = "An account with this email already exists"


class AdmissionNumberExistsError(ConflictError):
    detail = "Admission number already exists in this school"


class AcademicYearAlreadyActiveError(ConflictError):
    detail = "Another academic year is already active"


# ── 503 External Service ──────────────────────────────────────
class PaymentGatewayError(BaseAppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Payment gateway error. Please try again"


class SMSDeliveryError(BaseAppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "SMS delivery failed"


class StorageError(BaseAppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "File storage service error"


# ── Maintenance ───────────────────────────────────────────────
class MaintenanceModeError(BaseAppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "System is under maintenance. Please try again later"


# Exception → HTTP mapping for exception handler middleware
EXCEPTION_HTTP_MAP: dict[type[BaseAppError], int] = {
    exc_class: exc_class.status_code
    for exc_class in BaseAppError.__subclasses__()
}
