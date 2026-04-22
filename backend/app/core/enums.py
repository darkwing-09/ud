"""All application-wide Enum definitions."""
from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SCHOOL_ADMIN = "SCHOOL_ADMIN"
    ACCOUNTANT = "ACCOUNTANT"
    HR_MANAGER = "HR_MANAGER"
    CLASS_TEACHER = "CLASS_TEACHER"
    SUBJECT_TEACHER = "SUBJECT_TEACHER"
    STUDENT = "STUDENT"
    PARENT = "PARENT"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class SchoolStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"


class SubscriptionPlan(str, Enum):
    BASIC = "BASIC"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class BloodGroup(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class GuardianRelation(str, Enum):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    GUARDIAN = "GUARDIAN"
    SIBLING = "SIBLING"
    GRANDPARENT = "GRANDPARENT"
    OTHER = "OTHER"


class StudentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ALUMNI = "ALUMNI"
    TRANSFERRED = "TRANSFERRED"
    DROPPED = "DROPPED"
    SUSPENDED = "SUSPENDED"


class StaffStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"
    RESIGNED = "RESIGNED"


class StaffType(str, Enum):
    TEACHING = "TEACHING"
    NON_TEACHING = "NON_TEACHING"
    ADMINISTRATIVE = "ADMINISTRATIVE"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"
    HOLIDAY = "HOLIDAY"
    HALF_DAY = "HALF_DAY"


class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    WITHDRAWN = "WITHDRAWN"


class LeaveType(str, Enum):
    SICK = "SICK"
    CASUAL = "CASUAL"
    EARNED = "EARNED"
    MATERNITY = "MATERNITY"
    PATERNITY = "PATERNITY"
    UNPAID = "UNPAID"
    COMPENSATORY = "COMPENSATORY"
    OTHER = "OTHER"


class ExamType(str, Enum):
    UNIT_TEST = "UNIT_TEST"
    MID_TERM = "MID_TERM"
    FINAL = "FINAL"
    HALF_YEARLY = "HALF_YEARLY"
    ANNUAL = "ANNUAL"
    INTERNAL = "INTERNAL"
    PRACTICAL = "PRACTICAL"


class ExamStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MarksStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PUBLISHED = "PUBLISHED"
    LOCKED = "LOCKED"


class SubjectType(str, Enum):
    THEORY = "THEORY"
    PRACTICAL = "PRACTICAL"
    ELECTIVE = "ELECTIVE"
    LANGUAGE = "LANGUAGE"
    CO_CURRICULAR = "CO_CURRICULAR"


class FeeStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"
    CANCELLED = "CANCELLED"


class PaymentGateway(str, Enum):
    RAZORPAY = "RAZORPAY"
    PAYU = "PAYU"
    CASH = "CASH"
    NEFT = "NEFT"
    CHEQUE = "CHEQUE"
    DD = "DD"
    WAIVER = "WAIVER"
    OTHER = "OTHER"


class PaymentStatus(str, Enum):
    INITIATED = "INITIATED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class SalaryComponentType(str, Enum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"


class PayrollStatus(str, Enum):
    DRAFT = "DRAFT"
    COMPUTED = "COMPUTED"
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    CANCELLED = "CANCELLED"


class NoticeAudience(str, Enum):
    ALL = "ALL"
    TEACHERS = "TEACHERS"
    STUDENTS = "STUDENTS"
    PARENTS = "PARENTS"
    STAFF = "STAFF"
    CLASS = "CLASS"
    SECTION = "SECTION"


class NoticeStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    SCHEDULED = "SCHEDULED"
    ARCHIVED = "ARCHIVED"


class NotificationChannel(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    WHATSAPP = "WHATSAPP"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    READ = "READ"


class DocumentType(str, Enum):
    PHOTO = "PHOTO"
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
    AADHAR_CARD = "AADHAR_CARD"
    MARKSHEET = "MARKSHEET"
    TRANSFER_CERTIFICATE = "TRANSFER_CERTIFICATE"
    MIGRATION_CERTIFICATE = "MIGRATION_CERTIFICATE"
    BONAFIDE_CERTIFICATE = "BONAFIDE_CERTIFICATE"
    CHARACTER_CERTIFICATE = "CHARACTER_CERTIFICATE"
    ID_PROOF = "ID_PROOF"
    SALARY_SLIP = "SALARY_SLIP"
    APPOINTMENT_LETTER = "APPOINTMENT_LETTER"
    CONTRACT = "CONTRACT"
    FEE_RECEIPT = "FEE_RECEIPT"
    REPORT_CARD = "REPORT_CARD"
    OTHER = "OTHER"


class CertificateType(str, Enum):
    BONAFIDE = "BONAFIDE"
    CHARACTER = "CHARACTER"
    SPORTS = "SPORTS"
    ACHIEVEMENT = "ACHIEVEMENT"
    PARTICIPATION = "PARTICIPATION"
    TRANSFER = "TRANSFER"


class ImportJobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class AdvanceStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RECOVERING = "RECOVERING"
    SETTLED = "SETTLED"


class AuditAction(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT_DATA = "IMPORT_DATA"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PUBLISH = "PUBLISH"
    PAYMENT = "PAYMENT"
