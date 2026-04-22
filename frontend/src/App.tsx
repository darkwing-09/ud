import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { useAuth } from '@/hooks/useAuth'
import { ROLE_HOME } from '@/lib/constants'
import { LoadingSpin } from '@/components/common/LoadingSpin'
import { AnimatePresence } from 'framer-motion'

// Lazy-load all pages for code splitting
// Auth
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'))
const ForgotPasswordPage = lazy(() => import('@/pages/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('@/pages/auth/ResetPasswordPage'))

// Admin
const AdminDashboard = lazy(() => import('@/pages/admin/DashboardPage'))
const StudentDirectory = lazy(() => import('@/pages/admin/students/StudentDirectoryPage'))
const StudentEnroll = lazy(() => import('@/pages/admin/students/StudentEnrollPage'))
const StudentProfile = lazy(() => import('@/pages/admin/students/StudentProfilePage'))
const StaffDirectory = lazy(() => import('@/pages/admin/staff/StaffDirectoryPage'))
const StaffNew = lazy(() => import('@/pages/admin/staff/StaffNewPage'))
const StaffProfile = lazy(() => import('@/pages/admin/staff/StaffProfilePage'))
const ParentsPage = lazy(() => import('@/pages/admin/parents/ParentsPage'))
const DepartmentsPage = lazy(() => import('@/pages/admin/academic/DepartmentsPage'))
const ClassesPage = lazy(() => import('@/pages/admin/academic/ClassesPage'))
const SubjectsPage = lazy(() => import('@/pages/admin/academic/SubjectsPage'))
const AcademicYearsPage = lazy(() => import('@/pages/admin/academic/AcademicYearsPage'))
const TimetablePage = lazy(() => import('@/pages/admin/timetable/TimetablePage'))
const AttendanceOverviewPage = lazy(() => import('@/pages/admin/attendance/AttendanceOverviewPage'))
const AttendanceDefaultersPage = lazy(() => import('@/pages/admin/attendance/AttendanceDefaultersPage'))
const ExamsListPage = lazy(() => import('@/pages/admin/exams/ExamsListPage'))
const ExamCreatePage = lazy(() => import('@/pages/admin/exams/ExamCreatePage'))
const MarksReviewPage = lazy(() => import('@/pages/admin/marks/MarksReviewPage'))
const FeeStructuresPage = lazy(() => import('@/pages/admin/fees/FeeStructuresPage'))
const FeeCollectPage = lazy(() => import('@/pages/admin/fees/FeeCollectPage'))
const FeeDefaultersPage = lazy(() => import('@/pages/admin/fees/FeeDefaultersPage'))
const FeeAnalyticsPage = lazy(() => import('@/pages/admin/fees/FeeAnalyticsPage'))
const SalaryPage = lazy(() => import('@/pages/admin/hr/SalaryStructuresPage'))
const PayrollDashboard = lazy(() => import('@/pages/admin/hr/PayrollDashboardPage'))
const LeaveApplicationsPage = lazy(() => import('@/pages/admin/hr/LeaveApplicationsPage'))
const NoticesPage = lazy(() => import('@/pages/admin/communication/NoticesPage'))
const NoticeCreatePage = lazy(() => import('@/pages/admin/communication/NoticeCreatePage'))
const AnalyticsPage = lazy(() => import('@/pages/admin/system/AnalyticsPage'))
const AuditLogsPage = lazy(() => import('@/pages/admin/system/AuditLogsPage'))
const SchoolProfilePage = lazy(() => import('@/pages/admin/school/SchoolProfilePage'))
const RoleBuilderPage = lazy(() => import('@/pages/admin/system/RoleBuilderPage'))

// Teacher
const TeacherDashboard = lazy(() => import('@/pages/teacher/TeacherDashboardPage'))
const AttendanceMarkPage = lazy(() => import('@/pages/teacher/AttendanceMarkPage'))
const MarksEntryPage = lazy(() => import('@/pages/teacher/MarksEntryPage'))

// Student
const StudentDashboard = lazy(() => import('@/pages/student/StudentDashboardPage'))
const StudentAttendancePage = lazy(() => import('@/pages/student/AttendancePage'))
const StudentMarksPage = lazy(() => import('@/pages/student/MarksPage'))
const StudentFeesPage = lazy(() => import('@/pages/student/FeesPage'))

// Parent
const ParentDashboard = lazy(() => import('@/pages/parent/ParentDashboardPage'))

// Super Admin
const SuperAdminDashboard = lazy(() => import('@/pages/superadmin/SuperAdminDashboardPage'))

// Shared
const ProfilePage = lazy(() => import('@/pages/shared/ProfilePage'))
const NotFoundPage = lazy(() => import('@/pages/shared/NotFoundPage'))
const UnauthorizedPage = lazy(() => import('@/pages/shared/UnauthorizedPage'))

// --- Guards ---
function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RoleGuard({ roles, children }: { roles: string[]; children: React.ReactNode }) {
  const { user } = useAuth()
  if (!user || !roles.includes(user.role)) return <Navigate to="/unauthorized" replace />
  return <>{children}</>
}

function PublicOnly({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuth()
  if (isAuthenticated && user) return <Navigate to={ROLE_HOME[user.role] ?? '/'} replace />
  return <>{children}</>
}

const ADMIN_ROLES = ['SUPER_ADMIN', 'SCHOOL_ADMIN', 'ACCOUNTANT', 'HR_MANAGER']
const TEACHER_ROLES = ['CLASS_TEACHER', 'SUBJECT_TEACHER']

export default function App() {
  const location = useLocation()
  
  return (
    <Suspense fallback={<LoadingSpin />}>
      <AnimatePresence mode="wait">
        <Routes key={location.pathname}>
          {/* Public routes */}
          <Route path="/login" element={<PublicOnly><LoginPage /></PublicOnly>} />
          <Route path="/forgot-password" element={<PublicOnly><ForgotPasswordPage /></PublicOnly>} />
          <Route path="/reset-password" element={<PublicOnly><ResetPasswordPage /></PublicOnly>} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />

          {/* Protected shell */}
          <Route element={<AuthGuard><AppShell /></AuthGuard>}>

            {/* Root redirect */}
            <Route index element={<RootRedirect />} />

            {/* Shared */}
            <Route path="/profile" element={<ProfilePage />} />

            {/* Super Admin */}
            <Route path="/superadmin" element={<RoleGuard roles={['SUPER_ADMIN']}><SuperAdminDashboard /></RoleGuard>} />
            <Route path="/superadmin/schools" element={<RoleGuard roles={['SUPER_ADMIN']}><SuperAdminDashboard /></RoleGuard>} />

            {/* Admin routes */}
            <Route path="/admin" element={<RoleGuard roles={ADMIN_ROLES}><AdminDashboard /></RoleGuard>} />

            {/* Academic */}
            <Route path="/admin/academic-years" element={<RoleGuard roles={ADMIN_ROLES}><AcademicYearsPage /></RoleGuard>} />
            <Route path="/admin/departments" element={<RoleGuard roles={ADMIN_ROLES}><DepartmentsPage /></RoleGuard>} />
            <Route path="/admin/classes" element={<RoleGuard roles={ADMIN_ROLES}><ClassesPage /></RoleGuard>} />
            <Route path="/admin/subjects" element={<RoleGuard roles={ADMIN_ROLES}><SubjectsPage /></RoleGuard>} />

            {/* Staff */}
            <Route path="/admin/staff" element={<RoleGuard roles={ADMIN_ROLES}><StaffDirectory /></RoleGuard>} />
            <Route path="/admin/staff/new" element={<RoleGuard roles={ADMIN_ROLES}><StaffNew /></RoleGuard>} />
            <Route path="/admin/staff/:id" element={<RoleGuard roles={ADMIN_ROLES}><StaffProfile /></RoleGuard>} />

            {/* Students */}
            <Route path="/admin/students" element={<RoleGuard roles={ADMIN_ROLES}><StudentDirectory /></RoleGuard>} />
            <Route path="/admin/students/new" element={<RoleGuard roles={ADMIN_ROLES}><StudentEnroll /></RoleGuard>} />
            <Route path="/admin/students/:id" element={<RoleGuard roles={ADMIN_ROLES}><StudentProfile /></RoleGuard>} />

            {/* Parents */}
            <Route path="/admin/parents" element={<RoleGuard roles={ADMIN_ROLES}><ParentsPage /></RoleGuard>} />

            {/* Timetable */}
            <Route path="/admin/timetable" element={<RoleGuard roles={ADMIN_ROLES}><TimetablePage /></RoleGuard>} />

            {/* Attendance */}
            <Route path="/admin/attendance" element={<RoleGuard roles={ADMIN_ROLES}><AttendanceOverviewPage /></RoleGuard>} />
            <Route path="/admin/attendance/defaulters" element={<RoleGuard roles={ADMIN_ROLES}><AttendanceDefaultersPage /></RoleGuard>} />

            {/* Exams */}
            <Route path="/admin/exams" element={<RoleGuard roles={ADMIN_ROLES}><ExamsListPage /></RoleGuard>} />
            <Route path="/admin/exams/new" element={<RoleGuard roles={ADMIN_ROLES}><ExamCreatePage /></RoleGuard>} />

            {/* Marks */}
            <Route path="/admin/marks" element={<RoleGuard roles={ADMIN_ROLES}><MarksReviewPage /></RoleGuard>} />

            {/* Fees */}
            <Route path="/admin/fees" element={<RoleGuard roles={['SCHOOL_ADMIN', 'ACCOUNTANT']}><FeeStructuresPage /></RoleGuard>} />
            <Route path="/admin/fees/collect" element={<RoleGuard roles={['SCHOOL_ADMIN', 'ACCOUNTANT']}><FeeCollectPage /></RoleGuard>} />
            <Route path="/admin/fees/defaulters" element={<RoleGuard roles={['SCHOOL_ADMIN', 'ACCOUNTANT']}><FeeDefaultersPage /></RoleGuard>} />
            <Route path="/admin/fees/analytics" element={<RoleGuard roles={['SCHOOL_ADMIN', 'ACCOUNTANT']}><FeeAnalyticsPage /></RoleGuard>} />

            {/* HR */}
            <Route path="/admin/salary" element={<RoleGuard roles={['SCHOOL_ADMIN', 'HR_MANAGER']}><SalaryPage /></RoleGuard>} />
            <Route path="/admin/payroll" element={<RoleGuard roles={['SCHOOL_ADMIN', 'HR_MANAGER']}><PayrollDashboard /></RoleGuard>} />
            <Route path="/admin/leaves" element={<RoleGuard roles={['SCHOOL_ADMIN', 'HR_MANAGER']}><LeaveApplicationsPage /></RoleGuard>} />

            {/* Communication */}
            <Route path="/admin/notices" element={<RoleGuard roles={ADMIN_ROLES}><NoticesPage /></RoleGuard>} />
            <Route path="/admin/notices/new" element={<RoleGuard roles={ADMIN_ROLES}><NoticeCreatePage /></RoleGuard>} />

            {/* System */}
            <Route path="/admin/school" element={<RoleGuard roles={['SCHOOL_ADMIN']}><SchoolProfilePage /></RoleGuard>} />
            <Route path="/admin/analytics" element={<RoleGuard roles={ADMIN_ROLES}><AnalyticsPage /></RoleGuard>} />
            <Route path="/admin/audit" element={<RoleGuard roles={['SCHOOL_ADMIN']}><AuditLogsPage /></RoleGuard>} />
            <Route path="/admin/roles" element={<RoleGuard roles={['SCHOOL_ADMIN']}><RoleBuilderPage /></RoleGuard>} />

            {/* Teacher routes */}
            <Route path="/teacher" element={<RoleGuard roles={TEACHER_ROLES}><TeacherDashboard /></RoleGuard>} />
            <Route path="/teacher/attendance" element={<RoleGuard roles={TEACHER_ROLES}><AttendanceMarkPage /></RoleGuard>} />
            <Route path="/teacher/marks" element={<RoleGuard roles={TEACHER_ROLES}><MarksEntryPage /></RoleGuard>} />

            {/* Student routes */}
            <Route path="/student" element={<RoleGuard roles={['STUDENT']}><StudentDashboard /></RoleGuard>} />
            <Route path="/student/attendance" element={<RoleGuard roles={['STUDENT']}><StudentAttendancePage /></RoleGuard>} />
            <Route path="/student/marks" element={<RoleGuard roles={['STUDENT']}><StudentMarksPage /></RoleGuard>} />
            <Route path="/student/fees" element={<RoleGuard roles={['STUDENT']}><StudentFeesPage /></RoleGuard>} />

            {/* Parent routes */}
            <Route path="/parent" element={<RoleGuard roles={['PARENT']}><ParentDashboard /></RoleGuard>} />
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AnimatePresence>
    </Suspense>
  )
}

function RootRedirect() {
  const { user, isAuthenticated } = useAuth()
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />
  return <Navigate to={ROLE_HOME[user.role] ?? '/admin'} replace />
}
