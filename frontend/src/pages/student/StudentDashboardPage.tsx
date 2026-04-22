import { useAuth } from '@/hooks/useAuth'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { 
  Calendar, Clock, BookOpen, AlertCircle, 
  CheckCircle2, FileText, ArrowRight, Download 
} from 'lucide-react'

export default function StudentDashboardPage() {
  const { user } = useAuth()

  const stats = {
    attendance_pct: 94.2,
    present_days: 142,
    total_days: 151,
    fee_due: 4500,
    next_exam: 'Mid Term - Mathematics',
    next_exam_date: '12 Oct',
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title={`Hello, ${user?.full_name.split(' ')[0]} 👋`}
        description="Welcome to your student portal"
      />

      {/* Top Banner indicating Fees/Important Alerts */}
      {stats.fee_due > 0 && (
        <div className="flex items-center justify-between p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          <div className="flex items-center gap-3">
            <AlertCircle className="size-5" />
            <div>
              <p className="font-semibold text-sm">Fee Payment Due</p>
              <p className="text-xs text-rose-400/80">You have an outstanding balance of ₹{stats.fee_due}</p>
            </div>
          </div>
          <Button variant="destructive" size="sm" asChild>
            <Link to="/student/fees">Pay Now</Link>
          </Button>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column: Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Stats Row */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="stat-card">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Attendance</p>
                  <p className="kpi-number mt-1.5">{stats.attendance_pct}%</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{stats.present_days} / {stats.total_days} days present</p>
                </div>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20">
                  <CheckCircle2 className="size-5 text-emerald-500" />
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-border flex items-center justify-between text-xs">
                <span className="text-emerald-400 font-medium">Excellent attendance!</span>
                <Link to="/student/attendance" className="text-muted-foreground hover:text-foreground flex items-center gap-1">Details <ArrowRight className="size-3" /></Link>
              </div>
            </div>

            <div className="stat-card">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Next Exam</p>
                  <p className="kpi-number mt-1.5 text-xl line-clamp-1">{stats.next_exam}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{stats.next_exam_date}</p>
                </div>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/20">
                  <BookOpen className="size-5 text-blue-500" />
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-border flex items-center justify-between text-xs">
                <span className="text-blue-400 font-medium">In 4 days</span>
                <Link to="/student/marks" className="text-muted-foreground hover:text-foreground flex items-center gap-1">Syllabus <ArrowRight className="size-3" /></Link>
              </div>
            </div>
          </div>

          {/* Timetable Card */}
          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Clock className="size-4 text-primary" /> Today's Timetable
                </CardTitle>
                <Link to="/student/timetable" className="text-xs text-muted-foreground hover:text-primary">View Full Week</Link>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-0 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
                {[
                  { time: '08:00 AM', subject: 'Mathematics', teacher: 'Mr. Sharma', room: 'Room 102', status: 'past' },
                  { time: '09:00 AM', subject: 'Physics', teacher: 'Mrs. Gupta', room: 'Lab 1', status: 'current' },
                  { time: '10:00 AM', subject: 'Break', isBreak: true, status: 'upcoming' },
                  { time: '10:30 AM', subject: 'English Literature', teacher: 'Miss. Jane', room: 'Room 102', status: 'upcoming' },
                ].map((item, i) => (
                  <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className={`flex items-center justify-center w-10 h-10 rounded-full border-4 border-background shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm ${item.status === 'current' ? 'bg-primary' : 'bg-muted'}`}>
                      {item.isBreak ? <Calendar className="size-4 text-muted-foreground" /> : <BookOpen className={`size-4 ${item.status === 'current' ? 'text-primary-foreground' : 'text-muted-foreground'}`} />}
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl glass-card border border-border">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono text-muted-foreground">{item.time}</span>
                        {item.status === 'current' && <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse"></span>}
                      </div>
                      <p className={`font-semibold ${item.status === 'current' ? 'text-primary' : 'text-foreground'}`}>{item.subject}</p>
                      {!item.isBreak && (
                        <p className="text-xs text-muted-foreground mt-1">{item.teacher} • {item.room}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Quick Links */}
          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-sm font-semibold">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-2">
              <Button variant="outline" className="w-full justify-between group" asChild>
                <Link to="/student/report-card">
                  <span className="flex items-center gap-2"><FileText className="size-4 text-violet-400" /> Download Report Card</span>
                  <Download className="size-4 text-muted-foreground group-hover:text-foreground" />
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-between group" asChild>
                <Link to="/student/fees/receipts">
                  <span className="flex items-center gap-2"><FileText className="size-4 text-emerald-400" /> Fee Receipts</span>
                  <ArrowRight className="size-4 text-muted-foreground group-hover:text-foreground" />
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-between group" asChild>
                <Link to="/student/attendance">
                  <span className="flex items-center gap-2"><Calendar className="size-4 text-blue-400" /> Apply for Leave</span>
                  <ArrowRight className="size-4 text-muted-foreground group-hover:text-foreground" />
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Recent Notices */}
          <Card>
            <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold text-foreground">Notice Board</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {[
                { title: 'Annual Sports Day Postponed', date: '2 days ago', unread: true },
                { title: 'Science Fair Requirements', date: '5 days ago', unread: false },
                { title: 'Mid-Term Exam Schedule Released', date: '1 week ago', unread: false },
              ].map((n, i) => (
                <div key={i} className="flex gap-3 items-start group cursor-pointer">
                  <div className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${n.unread ? 'bg-primary' : 'bg-muted'}`} />
                  <div>
                    <p className={`text-sm ${n.unread ? 'font-medium text-foreground' : 'text-muted-foreground'} group-hover:text-primary transition-colors line-clamp-2`}>
                      {n.title}
                    </p>
                    <p className="text-xs text-muted-foreground/70 mt-1">{n.date}</p>
                  </div>
                </div>
              ))}
              <Button variant="link" className="w-full h-auto text-xs py-2 px-0 text-primary" asChild>
                <Link to="/student/notices">View all notices</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
