import { useQuery } from '@tanstack/react-query'
import {
  Users, GraduationCap, TrendingUp, DollarSign, ClipboardCheck,
  BookOpen, AlertCircle, UserCheck, ArrowUpRight, ArrowDownRight
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatsSkeleton } from '@/components/ui/skeleton'
import { PageHeader } from '@/components/common/PageHeader'
import { formatCurrency, formatNumber } from '@/lib/utils'
import { get } from '@/lib/api'
import type { DashboardStats } from '@/types/models'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { useAuth } from '@/hooks/useAuth'

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6']

// Mock data for charts until API is ready
const attendanceTrend = [
  { day: 'Mon', pct: 91 }, { day: 'Tue', pct: 88 }, { day: 'Wed', pct: 93 },
  { day: 'Thu', pct: 87 }, { day: 'Fri', pct: 95 }, { day: 'Sat', pct: 70 },
]

const feeCollection = [
  { month: 'Oct', collected: 4200000, pending: 800000 },
  { month: 'Nov', collected: 5100000, pending: 600000 },
  { month: 'Dec', collected: 3800000, pending: 1200000 },
  { month: 'Jan', collected: 5600000, pending: 400000 },
  { month: 'Feb', collected: 4900000, pending: 700000 },
  { month: 'Mar', collected: 6100000, pending: 300000 },
]

const gradeDistribution = [
  { grade: 'A+', count: 120 }, { grade: 'A', count: 280 },
  { grade: 'B+', count: 340 }, { grade: 'B', count: 180 },
  { grade: 'C', count: 80 },
]

interface StatCardProps {
  title: string
  value: string
  change?: string
  changeType?: 'up' | 'down'
  icon: React.ElementType
  accent: string
  sub?: string
}

function StatCard({ title, value, change, changeType, icon: Icon, accent, sub }: StatCardProps) {
  return (
    <div className="stat-card group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{title}</p>
          <p className="kpi-number mt-1.5">{value}</p>
          {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
        </div>
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${accent} group-hover:scale-105 transition-transform duration-200`}>
          <Icon className="size-5 text-white" />
        </div>
      </div>
      {change && (
        <div className="flex items-center gap-1">
          {changeType === 'up' ? (
            <ArrowUpRight className="size-3 text-emerald-400" />
          ) : (
            <ArrowDownRight className="size-3 text-rose-400" />
          )}
          <span className={`text-xs font-medium ${changeType === 'up' ? 'text-emerald-400' : 'text-rose-400'}`}>
            {change}
          </span>
          <span className="text-xs text-muted-foreground">vs last month</span>
        </div>
      )}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-3 py-2 text-xs">
      <p className="font-medium text-foreground mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  )
}

export default function AdminDashboardPage() {
  const { user } = useAuth()

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: () => get<DashboardStats>('/analytics/dashboard'),
    staleTime: 5 * 60 * 1000,
  })

  // Fallback stats while API loads
  const s: DashboardStats = stats ?? {
    total_students: 1248,
    total_staff: 87,
    attendance_today_pct: 91.4,
    fee_collected_month: 52_40_000,
    fee_due_month: 8_60_000,
    active_exams: 3,
    pending_leaves: 12,
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title={`Welcome back, ${user?.full_name.split(' ')[0]} 👋`}
        description="Here's what's happening at your school today"
      />

      {/* KPI Stats */}
      {isLoading ? (
        <StatsSkeleton count={7} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            title="Total Students"
            value={formatNumber(s.total_students)}
            change="+24 this month"
            changeType="up"
            icon={GraduationCap}
            accent="bg-blue-500"
          />
          <StatCard
            title="Total Staff"
            value={formatNumber(s.total_staff)}
            change="+2 this month"
            changeType="up"
            icon={UserCheck}
            accent="bg-violet-500"
          />
          <StatCard
            title="Today's Attendance"
            value={`${s.attendance_today_pct.toFixed(1)}%`}
            change="+1.2%"
            changeType="up"
            icon={ClipboardCheck}
            accent="bg-emerald-500"
          />
          <StatCard
            title="Fee Collected"
            value={formatCurrency(s.fee_collected_month)}
            sub="This month"
            change="+18%"
            changeType="up"
            icon={DollarSign}
            accent="bg-amber-500"
          />
          <StatCard
            title="Fee Pending"
            value={formatCurrency(s.fee_due_month)}
            sub="Overdue dues"
            change="-5%"
            changeType="down"
            icon={AlertCircle}
            accent="bg-rose-500"
          />
          <StatCard
            title="Active Exams"
            value={String(s.active_exams)}
            sub="2 scheduled this week"
            icon={BookOpen}
            accent="bg-cyan-500"
          />
          <StatCard
            title="Pending Leaves"
            value={String(s.pending_leaves)}
            sub="Awaiting approval"
            change="-3"
            changeType="down"
            icon={Users}
            accent="bg-orange-500"
          />
        </div>
      )}

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Attendance trend */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Attendance This Week</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={attendanceTrend} margin={{ top: 5, right: 10, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="attGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={[60, 100]} unit="%" />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="pct"
                  name="Attendance %"
                  stroke="#3B82F6"
                  strokeWidth={2.5}
                  fill="url(#attGrad)"
                  dot={{ fill: '#3B82F6', strokeWidth: 0, r: 3 }}
                  activeDot={{ r: 5, strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Fee collection */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Fee Collection Trend (6 months)</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={feeCollection} margin={{ top: 5, right: 10, bottom: 0, left: -20 }} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false}
                  tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="collected" name="Collected" fill="#10B981" radius={[4, 4, 0, 0]} maxBarSize={28} />
                <Bar dataKey="pending" name="Pending" fill="#F43F5E" opacity={0.7} radius={[4, 4, 0, 0]} maxBarSize={28} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Bottom row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Grade distribution */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Grade Distribution</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={gradeDistribution} margin={{ top: 5, right: 10, bottom: 0, left: -25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="grade" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Students">
                  {gradeDistribution.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} radius={[4, 4, 0, 0] as any} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Quick actions */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Enroll Student', href: '/admin/students/new', color: 'text-blue-400', bg: 'bg-blue-500/10 hover:bg-blue-500/20', icon: GraduationCap },
                { label: 'Add Staff', href: '/admin/staff/new', color: 'text-violet-400', bg: 'bg-violet-500/10 hover:bg-violet-500/20', icon: UserCheck },
                { label: 'Collect Fee', href: '/admin/fees/collect', color: 'text-amber-400', bg: 'bg-amber-500/10 hover:bg-amber-500/20', icon: DollarSign },
                { label: 'Mark Attendance', href: '/admin/attendance', color: 'text-emerald-400', bg: 'bg-emerald-500/10 hover:bg-emerald-500/20', icon: ClipboardCheck },
                { label: 'Create Exam', href: '/admin/exams/new', color: 'text-cyan-400', bg: 'bg-cyan-500/10 hover:bg-cyan-500/20', icon: BookOpen },
                { label: 'Run Payroll', href: '/admin/payroll', color: 'text-rose-400', bg: 'bg-rose-500/10 hover:bg-rose-500/20', icon: TrendingUp },
              ].map((a) => (
                <a
                  key={a.label}
                  href={a.href}
                  className={`flex items-center gap-3 rounded-xl p-3.5 transition-colors duration-150 cursor-pointer border border-transparent hover:border-border/50 ${a.bg}`}
                >
                  <a.icon className={`size-5 ${a.color}`} />
                  <span className="text-sm font-medium text-foreground">{a.label}</span>
                </a>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
