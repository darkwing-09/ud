import fs from 'fs'
import path from 'path'

const pages = [
  'src/pages/auth/ForgotPasswordPage.tsx',
  'src/pages/auth/ResetPasswordPage.tsx',
  'src/pages/admin/students/StudentEnrollPage.tsx',
  'src/pages/admin/students/StudentProfilePage.tsx',
  'src/pages/admin/staff/StaffDirectoryPage.tsx',
  'src/pages/admin/staff/StaffNewPage.tsx',
  'src/pages/admin/staff/StaffProfilePage.tsx',
  'src/pages/admin/parents/ParentsPage.tsx',
  'src/pages/admin/academic/DepartmentsPage.tsx',
  'src/pages/admin/academic/ClassesPage.tsx',
  'src/pages/admin/academic/SubjectsPage.tsx',
  'src/pages/admin/academic/AcademicYearsPage.tsx',
  'src/pages/admin/timetable/TimetablePage.tsx',
  'src/pages/admin/attendance/AttendanceOverviewPage.tsx',
  'src/pages/admin/attendance/AttendanceDefaultersPage.tsx',
  'src/pages/admin/exams/ExamsListPage.tsx',
  'src/pages/admin/exams/ExamCreatePage.tsx',
  'src/pages/admin/marks/MarksReviewPage.tsx',
  'src/pages/admin/fees/FeeStructuresPage.tsx',
  'src/pages/admin/fees/FeeCollectPage.tsx',
  'src/pages/admin/fees/FeeDefaultersPage.tsx',
  'src/pages/admin/fees/FeeAnalyticsPage.tsx',
  'src/pages/admin/hr/SalaryStructuresPage.tsx',
  'src/pages/admin/hr/PayrollDashboardPage.tsx',
  'src/pages/admin/hr/LeaveApplicationsPage.tsx',
  'src/pages/admin/communication/NoticesPage.tsx',
  'src/pages/admin/communication/NoticeCreatePage.tsx',
  'src/pages/admin/system/AnalyticsPage.tsx',
  'src/pages/admin/system/AuditLogsPage.tsx',
  'src/pages/admin/school/SchoolProfilePage.tsx',
  'src/pages/admin/system/RoleBuilderPage.tsx',
  'src/pages/teacher/TeacherDashboardPage.tsx',
  'src/pages/teacher/AttendanceMarkPage.tsx',
  'src/pages/teacher/MarksEntryPage.tsx',
  'src/pages/student/StudentDashboardPage.tsx',
  'src/pages/student/AttendancePage.tsx',
  'src/pages/student/MarksPage.tsx',
  'src/pages/student/FeesPage.tsx',
  'src/pages/parent/ParentDashboardPage.tsx',
  'src/pages/superadmin/SuperAdminDashboardPage.tsx',
  'src/pages/shared/ProfilePage.tsx',
]

const componentTemplate = (name) => `import { PageHeader } from '@/components/common/PageHeader'
import { EmptyState } from '@/components/common/EmptyState'

export default function ${name}() {
  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader 
        title="${name.replace(/Page$/, '')}" 
        description="This page is under construction." 
      />
      <EmptyState 
        title="Coming Soon" 
        description="The features for this module are currently being developed." 
      />
    </div>
  )
}
`

const baseDir = '/home/darkwing/Videos/udca/school-platform/frontend'

pages.forEach(p => {
  const fullPath = path.join(baseDir, p)
  const dir = path.dirname(fullPath)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }
  if (!fs.existsSync(fullPath)) {
    const filename = path.basename(fullPath, '.tsx')
    fs.writeFileSync(fullPath, componentTemplate(filename))
    console.log('Created:', p)
  }
})
