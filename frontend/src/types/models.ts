// --- Common API wrapper ---
export interface ApiResponse<T> {
  success: boolean
  data: T
  meta?: {
    request_id: string
    timestamp: string
  }
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, string[]>
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  sort_by?: string
  sort_dir?: 'asc' | 'desc'
}

// --- Core User ---
export interface User {
  id: string
  email: string
  full_name: string
  phone?: string
  avatar_url?: string
  role: string
  is_active: boolean
  is_verified: boolean
  last_login_at?: string
  created_at: string
}

// --- School ---
export interface School {
  id: string
  name: string
  code: string
  address?: string
  city?: string
  state?: string
  pincode?: string
  phone?: string
  email?: string
  website?: string
  logo_url?: string
  principal_name?: string
  affiliation?: string
  affiliation_number?: string
  is_active: boolean
  subscription_plan: string
  settings: Record<string, unknown>
  created_at: string
}

// --- Academic Year ---
export interface AcademicYear {
  id: string
  school_id: string
  name: string
  start_date: string
  end_date: string
  is_active: boolean
  created_at: string
}

export interface Term {
  id: string
  academic_year_id: string
  name: string
  start_date: string
  end_date: string
  is_active: boolean
}

// --- Org Structure ---
export interface Department {
  id: string
  name: string
  description?: string
  head_staff_id?: string
}

export interface Class {
  id: string
  name: string
  numeric_level: number
  academic_year_id: string
  sections_count?: number
}

export interface Section {
  id: string
  class_id: string
  class_name?: string
  name: string
  class_teacher_id?: string
  class_teacher_name?: string
  max_strength: number
  current_strength?: number
}

export interface Subject {
  id: string
  name: string
  code?: string
  type: 'THEORY' | 'PRACTICAL' | 'ELECTIVE'
}

// --- Staff ---
export interface StaffProfile {
  id: string
  user_id: string
  employee_code: string
  full_name: string
  email: string
  phone?: string
  gender?: string
  date_of_birth?: string
  date_of_joining?: string
  department_id?: string
  department_name?: string
  designation?: string
  employment_type?: string
  is_active: boolean
  avatar_url?: string
}

// --- Student ---
export interface StudentProfile {
  id: string
  user_id: string
  admission_number: string
  full_name: string
  email?: string
  phone?: string
  gender?: string
  date_of_birth?: string
  date_of_admission?: string
  section_id?: string
  section_name?: string
  class_id?: string
  class_name?: string
  roll_number?: string
  is_active: boolean
  avatar_url?: string
}

// --- Parent ---
export interface ParentProfile {
  id: string
  user_id: string
  full_name: string
  email: string
  phone?: string
  relationship?: string
  children: Array<{ id: string; name: string; class: string }>
}

// --- Attendance ---
export interface AttendanceSession {
  id: string
  section_id: string
  subject_id?: string
  date: string
  session_type: string
  status: 'OPEN' | 'CLOSED'
  created_by_name: string
}

export interface AttendanceRecord {
  student_id: string
  student_name: string
  roll_number?: string
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'LEAVE'
  remark?: string
}

export interface AttendanceSummary {
  student_id: string
  total_days: number
  present: number
  absent: number
  late: number
  leave: number
  percentage: number
}

// --- Exams ---
export interface Exam {
  id: string
  name: string
  exam_type: string
  academic_year_id: string
  start_date: string
  end_date: string
  status: string
  schedule_count?: number
}

export interface ExamSchedule {
  id: string
  exam_id: string
  subject_id: string
  subject_name: string
  class_id: string
  section_id?: string
  date: string
  start_time: string
  end_time: string
  max_marks: number
  passing_marks: number
}

// --- Marks ---
export interface StudentMarks {
  id: string
  student_id: string
  student_name: string
  roll_number?: string
  exam_schedule_id: string
  marks_obtained: number
  max_marks: number
  grade?: string
  is_absent: boolean
  is_locked: boolean
}

// --- Fees ---
export interface FeeStructure {
  id: string
  name: string
  academic_year_id: string
  frequency: string
  components: FeeComponent[]
  total_amount: number
}

export interface FeeComponent {
  id: string
  name: string
  amount: number
  is_optional: boolean
}

export interface FeeDue {
  id: string
  student_id: string
  student_name: string
  fee_structure_id: string
  fee_structure_name: string
  amount: number
  paid_amount: number
  balance: number
  due_date: string
  status: string
  period_label: string
}

export interface FeePayment {
  id: string
  fee_due_id: string
  amount: number
  payment_method: string
  transaction_id?: string
  status: string
  receipt_number: string
  created_at: string
}

// --- Leave ---
export interface LeaveApplication {
  id: string
  staff_id: string
  staff_name: string
  leave_type: string
  from_date: string
  to_date: string
  days: number
  reason: string
  status: string
  applied_at: string
}

// --- Payroll ---
export interface PayrollRecord {
  id: string
  staff_id: string
  staff_name: string
  month: number
  year: number
  gross_salary: number
  total_deductions: number
  net_salary: number
  lop_days: number
  status: string
}

// --- Notice ---
export interface Notice {
  id: string
  title: string
  content: string
  target_roles: string[]
  is_pinned: boolean
  published_at?: string
  created_by_name: string
  created_at: string
}

// --- Analytics ---
export interface DashboardStats {
  total_students: number
  total_staff: number
  attendance_today_pct: number
  fee_collected_month: number
  fee_due_month: number
  active_exams: number
  pending_leaves: number
}
