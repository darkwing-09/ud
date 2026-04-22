// --- User Roles ---
export const ROLES = {
  SUPER_ADMIN: 'SUPER_ADMIN',
  SCHOOL_ADMIN: 'SCHOOL_ADMIN',
  ACCOUNTANT: 'ACCOUNTANT',
  HR_MANAGER: 'HR_MANAGER',
  CLASS_TEACHER: 'CLASS_TEACHER',
  SUBJECT_TEACHER: 'SUBJECT_TEACHER',
  STUDENT: 'STUDENT',
  PARENT: 'PARENT',
} as const

export type Role = (typeof ROLES)[keyof typeof ROLES]

export const ROLE_LABELS: Record<Role, string> = {
  SUPER_ADMIN: 'Super Admin',
  SCHOOL_ADMIN: 'School Admin',
  ACCOUNTANT: 'Accountant',
  HR_MANAGER: 'HR Manager',
  CLASS_TEACHER: 'Class Teacher',
  SUBJECT_TEACHER: 'Subject Teacher',
  STUDENT: 'Student',
  PARENT: 'Parent',
}

// --- Admin-level roles ---
export const ADMIN_ROLES: Role[] = ['SUPER_ADMIN', 'SCHOOL_ADMIN', 'ACCOUNTANT', 'HR_MANAGER']
export const TEACHER_ROLES: Role[] = ['CLASS_TEACHER', 'SUBJECT_TEACHER']
export const STAFF_ROLES: Role[] = [...ADMIN_ROLES, ...TEACHER_ROLES]

// --- Default dashboard route per role ---
export const ROLE_HOME: Record<Role, string> = {
  SUPER_ADMIN: '/superadmin',
  SCHOOL_ADMIN: '/admin',
  ACCOUNTANT: '/admin/fees',
  HR_MANAGER: '/admin/hr',
  CLASS_TEACHER: '/teacher',
  SUBJECT_TEACHER: '/teacher',
  STUDENT: '/student',
  PARENT: '/parent',
}

// --- Pagination defaults ---
export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// --- API endpoints ---
export const API = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    VERIFY_EMAIL: '/auth/verify-email',
    ME: '/auth/me',
  },
  SCHOOLS: {
    BASE: '/schools',
    BY_ID: (id: string) => `/schools/${id}`,
    SETTINGS: (id: string) => `/schools/${id}/settings`,
  },
  ACADEMIC_YEARS: {
    BASE: '/academic-years',
    BY_ID: (id: string) => `/academic-years/${id}`,
    ACTIVATE: (id: string) => `/academic-years/${id}/activate`,
  },
  DEPARTMENTS: '/departments',
  CLASSES: '/classes',
  SECTIONS: '/sections',
  SUBJECTS: '/subjects',
  STAFF: {
    BASE: '/staff',
    BY_ID: (id: string) => `/staff/${id}`,
    BULK_IMPORT: '/staff/bulk-import',
  },
  STUDENTS: {
    BASE: '/students',
    BY_ID: (id: string) => `/students/${id}`,
    BULK_IMPORT: '/students/bulk-import',
    PROMOTE: '/students/promote',
  },
  PARENTS: '/parents',
  TIMETABLE: '/timetable',
  ATTENDANCE: {
    BASE: '/attendance',
    SESSIONS: '/attendance/sessions',
    SUMMARY: (studentId: string) => `/attendance/students/${studentId}/summary`,
    DEFAULTERS: '/attendance/defaulters',
    STAFF: '/staff-attendance',
  },
  EXAMS: '/exams',
  MARKS: '/marks',
  RESULTS: '/results',
  FEES: {
    STRUCTURES: '/fees/structures',
    DUES: '/fees/dues',
    PAYMENTS: '/fees/payments',
    DEFAULTERS: '/fees/defaulters',
    ANALYTICS: '/fees/analytics',
  },
  SALARY: '/salary',
  PAYROLL: '/payroll',
  LEAVES: '/leaves',
  HOLIDAYS: '/holidays',
  NOTICES: '/notices',
  MESSAGES: '/messages',
  NOTIFICATIONS: '/notifications',
  DOCUMENTS: '/documents',
  ANALYTICS: '/analytics',
  AUDIT: '/audit-logs',
  SYSTEM: {
    HEALTH: '/system/health',
    ROLES: '/roles',
  },
} as const

// --- Date formats ---
export const DATE_FORMAT = 'dd MMM yyyy'
export const DATE_TIME_FORMAT = 'dd MMM yyyy, h:mm a'
export const MONTH_FORMAT = 'MMMM yyyy'

// --- File limits ---
export const MAX_FILE_SIZE_MB = 10
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
export const ALLOWED_DOC_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
export const ALLOWED_CSV_TYPES = ['text/csv', 'application/vnd.ms-excel']

// --- Status enums ---
export const FEE_STATUS = { PENDING: 'PENDING', PAID: 'PAID', PARTIAL: 'PARTIAL', OVERDUE: 'OVERDUE', WAIVED: 'WAIVED' } as const
export const LEAVE_STATUS = { PENDING: 'PENDING', APPROVED: 'APPROVED', REJECTED: 'REJECTED', CANCELLED: 'CANCELLED' } as const
export const PAYROLL_STATUS = { DRAFT: 'DRAFT', GENERATED: 'GENERATED', APPROVED: 'APPROVED', DISBURSED: 'DISBURSED' } as const
export const EXAM_STATUS = { DRAFT: 'DRAFT', PUBLISHED: 'PUBLISHED', ONGOING: 'ONGOING', COMPLETED: 'COMPLETED' } as const
export const ATTENDANCE_STATUS = { PRESENT: 'PRESENT', ABSENT: 'ABSENT', LATE: 'LATE', LEAVE: 'LEAVE' } as const
