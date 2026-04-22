import {
  Users, CheckCircle2, Clock, BookOpen,
  StickyNote, Award, AlertCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { formatDate } from '@/lib/utils'
import { Link } from 'react-router-dom'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts'
import { PageTransition, MotionTiltCard, StaggerContainer, StaggerItem } from '@/components/ui/motion'

export default function TeacherDashboardPage() {
  const { user } = useAuth()

  // Mapped mock data for demonstration
  const stats = {
    my_students: 42,
    attendance_today: 38,
    pending_tasks: 3,
    upcoming_classes: 4,
  }

  const attendanceData = [
    { name: 'Present', value: 38 },
    { name: 'Absent', value: 3 },
    { name: 'Leave', value: 1 },
  ]
  const COLORS = ['#10B981', '#F43F5E', '#F59E0B']

  return (
    <PageTransition className="space-y-8">
      <PageHeader
        title={`Welcome, ${user?.full_name.split(' ')[0]} 👋`}
        description="Here is your schedule and tasks for today"
      />

      <StaggerContainer className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Stat Cards */}
        <StaggerItem>
          <MotionTiltCard className="stat-card group h-full">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">My Class</p>
                <p className="kpi-number mt-1.5">{stats.my_students}</p>
                <p className="text-xs text-muted-foreground mt-0.5">Total students</p>
              </div>
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/20 group-hover:scale-105 transition-transform duration-200">
                <Users className="size-5 text-blue-500" />
              </div>
            </div>
          </MotionTiltCard>
        </StaggerItem>

        <StaggerItem>
          <MotionTiltCard className="stat-card group h-full">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Attendance</p>
                <p className="kpi-number mt-1.5">{stats.attendance_today}/{stats.my_students}</p>
                <p className="text-xs text-muted-foreground mt-0.5">Present today</p>
              </div>
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 group-hover:scale-105 transition-transform duration-200">
                <CheckCircle2 className="size-5 text-emerald-500" />
              </div>
            </div>
          </MotionTiltCard>
        </StaggerItem>

        <StaggerItem>
          <MotionTiltCard className="stat-card group h-full">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Pending Tasks</p>
                <p className="kpi-number mt-1.5 text-amber-500">{stats.pending_tasks}</p>
                <p className="text-xs text-muted-foreground mt-0.5">Marks entry open</p>
              </div>
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/20 group-hover:scale-105 transition-transform duration-200">
                <AlertCircle className="size-5 text-amber-500" />
              </div>
            </div>
          </MotionTiltCard>
        </StaggerItem>

        <StaggerItem>
          <MotionTiltCard className="stat-card group h-full">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Classes Today</p>
                <p className="kpi-number mt-1.5">{stats.upcoming_classes}</p>
                <p className="text-xs text-muted-foreground mt-0.5">Next in 45m</p>
              </div>
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-500/20 group-hover:scale-105 transition-transform duration-200">
                <Clock className="size-5 text-violet-500" />
              </div>
            </div>
          </MotionTiltCard>
        </StaggerItem>
      </StaggerContainer>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Today's Schedule */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center justify-between">
              <span>Today's Schedule</span>
              <span className="text-xs text-muted-foreground font-normal">{formatDate(new Date())}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { time: '08:30 AM', subject: 'Mathematics', class: 'Class 10-A', status: 'completed' },
              { time: '10:00 AM', subject: 'Physics', class: 'Class 9-B', status: 'ongoing' },
              { time: '11:45 AM', subject: 'Mathematics', class: 'Class 10-C', status: 'upcoming' },
              { time: '01:30 PM', subject: 'Science Lab', class: 'Class 9-A', status: 'upcoming' },
            ].map((s, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-border/50 hover:bg-muted/10 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-20 text-xs font-medium text-muted-foreground text-right">{s.time}</div>
                  <div className="w-1 h-8 rounded-full bg-border" />
                  <div>
                    <p className="font-semibold text-foreground text-sm">{s.subject}</p>
                    <p className="text-xs text-muted-foreground">{s.class}</p>
                  </div>
                </div>
                <div>
                  {s.status === 'completed' && <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 rounded text-xs font-medium flex items-center gap-1"><CheckCircle2 className="size-3" /> Done</span>}
                  {s.status === 'ongoing' && <span className="px-2 py-1 bg-blue-500/10 text-blue-500 rounded text-xs font-medium animate-pulse">Right Now</span>}
                  {s.status === 'upcoming' && <span className="px-2 py-1 bg-muted text-muted-foreground rounded text-xs font-medium">Upcoming</span>}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Quick Actions & Overview */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Today's Class Attendance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[140px] mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={attendanceData} innerRadius={40} outerRadius={60} paddingAngle={2} dataKey="value">
                      {attendanceData.map(( _entry , index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-2 text-xs">
                {attendanceData.map((d, i) => (
                 <div key={d.name} className="flex items-center gap-1.5 text-muted-foreground">
                   <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                   {d.name} ({d.value})
                 </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-2">
                <Button variant="outline" className="justify-start gap-3 w-full" asChild>
                  <Link to="/teacher/attendance"><CheckCircle2 className="size-4 text-emerald-400" /> Mark Attendance</Link>
                </Button>
                <Button variant="outline" className="justify-start gap-3 w-full" asChild>
                  <Link to="/teacher/marks"><Award className="size-4 text-amber-400" /> Enter Marks</Link>
                </Button>
                <Button variant="outline" className="justify-start gap-3 w-full" asChild>
                  <Link to="/teacher/notices"><StickyNote className="size-4 text-primary" /> Send Notice</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageTransition>
  )
}
