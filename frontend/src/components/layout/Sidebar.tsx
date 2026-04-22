import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/store/uiStore'
import { useAuth } from '@/hooks/useAuth'
import { useSchoolStore } from '@/store/schoolStore'
import {
  LayoutDashboard, Users, GraduationCap, BookOpen, Clock, Calendar,
  ClipboardList, DollarSign, CreditCard, UserCog, FileText,
  Bell, Settings, ShieldCheck, BarChart3, Building2, X,
  ChevronLeft, ChevronRight, School, UserSquare, BookMarked,
  Calculator, Banknote, Briefcase, MessageSquare, FolderOpen,
  LogOut, ReceiptText, Trophy, UserX
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { ROLE_LABELS } from '@/lib/constants'

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: number
}

interface NavGroup {
  title: string
  items: NavItem[]
}

function getNavGroups(role: string): NavGroup[] {
  switch (role) {
    case 'SUPER_ADMIN':
      return [
        {
          title: 'Platform',
          items: [
            { label: 'Dashboard', href: '/superadmin', icon: LayoutDashboard },
            { label: 'Schools', href: '/superadmin/schools', icon: School },
            { label: 'Analytics', href: '/superadmin/analytics', icon: BarChart3 },
            { label: 'System', href: '/superadmin/system', icon: Settings },
          ],
        },
      ]

    case 'SCHOOL_ADMIN':
      return [
        {
          title: 'Overview',
          items: [
            { label: 'Dashboard', href: '/admin', icon: LayoutDashboard },
            { label: 'Analytics', href: '/admin/analytics', icon: BarChart3 },
          ],
        },
        {
          title: 'Academic',
          items: [
            { label: 'Academic Years', href: '/admin/academic-years', icon: Calendar },
            { label: 'Departments', href: '/admin/departments', icon: Building2 },
            { label: 'Classes & Sections', href: '/admin/classes', icon: BookOpen },
            { label: 'Subjects', href: '/admin/subjects', icon: BookMarked },
            { label: 'Timetable', href: '/admin/timetable', icon: Clock },
          ],
        },
        {
          title: 'People',
          items: [
            { label: 'Staff', href: '/admin/staff', icon: UserCog },
            { label: 'Students', href: '/admin/students', icon: GraduationCap },
            { label: 'Parents', href: '/admin/parents', icon: Users },
          ],
        },
        {
          title: 'Attendance',
          items: [
            { label: 'Overview', href: '/admin/attendance', icon: ClipboardList },
            { label: 'Defaulters', href: '/admin/attendance/defaulters', icon: UserX },
            { label: 'Reports', href: '/admin/attendance/reports', icon: FileText },
            { label: 'Staff Attendance', href: '/admin/staff-attendance', icon: UserSquare },
          ],
        },
        {
          title: 'Academics',
          items: [
            { label: 'Examinations', href: '/admin/exams', icon: BookOpen },
            { label: 'Marks & Results', href: '/admin/marks', icon: Trophy },
            { label: 'Grade Schemes', href: '/admin/grade-schemes', icon: Calculator },
          ],
        },
        {
          title: 'Finance',
          items: [
            { label: 'Fee Structures', href: '/admin/fees', icon: CreditCard },
            { label: 'Collect Fees', href: '/admin/fees/collect', icon: DollarSign },
            { label: 'Defaulters', href: '/admin/fees/defaulters', icon: UserX },
            { label: 'Fee Reports', href: '/admin/fees/reports', icon: ReceiptText },
            { label: 'Fee Analytics', href: '/admin/fees/analytics', icon: BarChart3 },
          ],
        },
        {
          title: 'HR & Payroll',
          items: [
            { label: 'Salary Structures', href: '/admin/salary', icon: Banknote },
            { label: 'Payroll', href: '/admin/payroll', icon: Calculator },
            { label: 'Leaves', href: '/admin/leaves', icon: Calendar },
            { label: 'Holidays', href: '/admin/holidays', icon: Calendar },
          ],
        },
        {
          title: 'Communication',
          items: [
            { label: 'Notices', href: '/admin/notices', icon: Bell },
            { label: 'Broadcast', href: '/admin/broadcast', icon: MessageSquare },
            { label: 'Messages', href: '/admin/messages', icon: MessageSquare },
          ],
        },
        {
          title: 'System',
          items: [
            { label: 'School Profile', href: '/admin/school', icon: School },
            { label: 'Role Builder', href: '/admin/roles', icon: ShieldCheck },
            { label: 'Audit Logs', href: '/admin/audit', icon: FileText },
            { label: 'Documents', href: '/admin/documents', icon: FolderOpen },
          ],
        },
      ]

    case 'CLASS_TEACHER':
    case 'SUBJECT_TEACHER':
      return [
        {
          title: 'Overview',
          items: [
            { label: 'Dashboard', href: '/teacher', icon: LayoutDashboard },
            { label: 'My Students', href: '/teacher/students', icon: GraduationCap },
            { label: 'Timetable', href: '/teacher/timetable', icon: Clock },
          ],
        },
        {
          title: 'Attendance',
          items: [
            { label: 'Mark Attendance', href: '/teacher/attendance', icon: ClipboardList },
            { label: 'History', href: '/teacher/attendance/history', icon: Calendar },
          ],
        },
        {
          title: 'Academics',
          items: [
            { label: 'Enter Marks', href: '/teacher/marks', icon: BookOpen },
          ],
        },
        {
          title: 'Other',
          items: [
            { label: 'Notices', href: '/teacher/notices', icon: Bell },
            { label: 'My Leaves', href: '/teacher/leaves', icon: Briefcase },
          ],
        },
      ]

    case 'STUDENT':
      return [
        {
          title: 'My Dashboard',
          items: [
            { label: 'Home', href: '/student', icon: LayoutDashboard },
            { label: 'Attendance', href: '/student/attendance', icon: ClipboardList },
            { label: 'Marks', href: '/student/marks', icon: BookOpen },
            { label: 'Report Card', href: '/student/report-card', icon: FileText },
            { label: 'Timetable', href: '/student/timetable', icon: Clock },
          ],
        },
        {
          title: 'Finance',
          items: [
            { label: 'My Fees', href: '/student/fees', icon: CreditCard },
            { label: 'Receipts', href: '/student/fees/receipts', icon: ReceiptText },
          ],
        },
        {
          title: 'Resources',
          items: [
            { label: 'Notices', href: '/student/notices', icon: Bell },
            { label: 'Documents', href: '/student/documents', icon: FolderOpen },
          ],
        },
      ]

    case 'PARENT':
      return [
        {
          title: 'My Dashboard',
          items: [
            { label: 'Home', href: '/parent', icon: LayoutDashboard },
            { label: 'Attendance', href: '/parent/attendance', icon: ClipboardList },
            { label: 'Marks', href: '/parent/marks', icon: BookOpen },
            { label: 'Fees', href: '/parent/fees', icon: CreditCard },
            { label: 'Timetable', href: '/parent/timetable', icon: Clock },
          ],
        },
        {
          title: 'Communication',
          items: [
            { label: 'Notices', href: '/parent/notices', icon: Bell },
            { label: 'Messages', href: '/parent/messages', icon: MessageSquare },
          ],
        },
      ]

    default:
      return []
  }
}

export function Sidebar() {
  const location = useLocation()
  const { sidebarCollapsed, mobileSidebarOpen, toggleSidebar, closeMobileSidebar } = useUIStore()
  const { user } = useAuth()
  const { schoolName } = useSchoolStore()
  const logout = useAuthStore((s) => s.logout)

  const navGroups = getNavGroups(user?.role ?? '')

  const isActive = (href: string) => {
    if (href === '/admin' || href === '/teacher' || href === '/student' || href === '/parent' || href === '/superadmin') {
      return location.pathname === href
    }
    return location.pathname.startsWith(href)
  }

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className={cn(
        'flex items-center gap-3 px-4 py-4 border-b border-sidebar-border',
        sidebarCollapsed && 'px-3 justify-center'
      )}>
        <div className="flex-shrink-0 h-8 w-8 rounded-lg bg-primary flex items-center justify-center shadow-sm shadow-primary/30">
          <GraduationCap className="h-5 w-5 text-white" />
        </div>
        {!sidebarCollapsed && (
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-foreground truncate">
              {schoolName ?? 'EduCore'}
            </p>
            <p className="text-xs text-muted-foreground">
              {user ? ROLE_LABELS[user.role as keyof typeof ROLE_LABELS] ?? user.role : ''}
            </p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {navGroups.map((group) => (
          <div key={group.title}>
            {!sidebarCollapsed && (
              <p className="px-3 mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60">
                {group.title}
              </p>
            )}
            <ul className="space-y-0.5">
              {group.items.map((item) => (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    onClick={closeMobileSidebar}
                    className={cn(
                      'sidebar-item',
                      isActive(item.href) && 'active',
                      sidebarCollapsed && 'justify-center px-2'
                    )}
                    title={sidebarCollapsed ? item.label : undefined}
                  >
                    <item.icon className="size-4 shrink-0" />
                    {!sidebarCollapsed && (
                      <span className="flex-1 truncate">{item.label}</span>
                    )}
                    {!sidebarCollapsed && item.badge ? (
                      <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary/20 px-1 text-[10px] font-bold text-primary">
                        {item.badge}
                      </span>
                    ) : null}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {/* User footer */}
      <div className={cn('border-t border-sidebar-border p-3 space-y-1', sidebarCollapsed && 'px-2')}>
        <Link
          to="/profile"
          className={cn('sidebar-item', sidebarCollapsed && 'justify-center px-2')}
          title={sidebarCollapsed ? 'Profile' : undefined}
        >
          <Settings className="size-4 shrink-0" />
          {!sidebarCollapsed && <span>Settings</span>}
        </Link>
        <button
          onClick={() => { logout(); window.location.href = '/login' }}
          className={cn('sidebar-item w-full text-left hover:text-rose-400', sidebarCollapsed && 'justify-center px-2')}
          title={sidebarCollapsed ? 'Logout' : undefined}
        >
          <LogOut className="size-4 shrink-0" />
          {!sidebarCollapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'hidden lg:flex flex-col h-screen sticky top-0 bg-[hsl(var(--sidebar-bg))] border-r border-[hsl(var(--sidebar-border))] transition-all duration-200 ease-out',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
      >
        {sidebarContent}
        {/* Collapse toggle */}
        <button
          onClick={toggleSidebar}
          className="absolute -right-3 top-20 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-background text-muted-foreground hover:text-foreground shadow-sm transition-colors z-10"
        >
          {sidebarCollapsed ? <ChevronRight className="size-3" /> : <ChevronLeft className="size-3" />}
        </button>
      </aside>

      {/* Mobile overlay */}
      {mobileSidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={closeMobileSidebar}
          />
          <aside className="relative z-50 flex w-72 flex-col bg-[hsl(var(--sidebar-bg))] border-r border-[hsl(var(--sidebar-border))] animate-slide-in-right">
            <button
              onClick={closeMobileSidebar}
              className="absolute right-3 top-3 flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:text-foreground"
            >
              <X className="size-4" />
            </button>
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  )
}
