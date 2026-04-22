import { useAuth } from '@/hooks/useAuth'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { 
  Users, CheckCircle2, ChevronRight, School, Wallet, AlertCircle, BookOpen
} from 'lucide-react'

export default function ParentDashboardPage() {
  const { user } = useAuth()

  // Mock data: A parent can have multiple children in the school
  const childrenData = [
    {
      id: 'st-01',
      name: 'Aarav Sharma',
      class: 'Class 10-A',
      attendance: 94.2,
      next_exam: 'Mathematics - 12 Oct',
      fee_due: 4500,
    },
    {
      id: 'st-02',
      name: 'Priya Sharma',
      class: 'Class 6-B',
      attendance: 98.1,
      next_exam: 'Science - 14 Oct',
      fee_due: 0,
    }
  ]

  const totalFeeDue = childrenData.reduce((acc, c) => acc + c.fee_due, 0)

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title={`Welcome, Mr. ${user?.full_name.split(' ').pop()} 👋`}
        description="Monitor your children's progress and stay updated"
      />

      {/* Global Alerts */}
      {totalFeeDue > 0 && (
        <div className="flex items-center justify-between p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
          <div className="flex items-center gap-3">
            <AlertCircle className="size-5" />
            <div>
              <p className="font-semibold text-sm">Action Required: Fee Payment</p>
              <p className="text-xs text-amber-500/80">You have a total outstanding balance of ₹{totalFeeDue}</p>
            </div>
          </div>
          <Button variant="outline" className="border-amber-500/50 hover:bg-amber-500/20 text-amber-500" size="sm" asChild>
            <Link to="/parent/fees">Pay All Dues</Link>
          </Button>
        </div>
      )}

      {/* Children Overview */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
          <Users className="size-4 text-primary" /> Your Wards
        </h3>
        
        <div className="grid gap-4 md:grid-cols-2">
          {childrenData.map(child => (
            <Card key={child.id} className="group hover:border-primary/50 transition-colors">
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <UserAvatar name={child.name} size="lg" className="border-2 border-background shadow-sm" />
                    <div>
                      <p className="font-semibold text-foreground">{child.name}</p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                        <School className="size-3" /> {child.class}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon-sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <ChevronRight className="size-4" />
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-2 pt-4 border-t border-border/50">
                  <div className="bg-muted/30 p-2.5 rounded-lg flex items-center gap-2">
                    <div className="bg-emerald-500/20 p-1.5 rounded-md text-emerald-500">
                      <CheckCircle2 className="size-3.5" />
                    </div>
                    <div>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Attendance</p>
                      <p className="text-sm font-medium text-foreground">{child.attendance}%</p>
                    </div>
                  </div>
                  <div className="bg-muted/30 p-2.5 rounded-lg flex items-center gap-2">
                    <div className="bg-blue-500/20 p-1.5 rounded-md text-blue-500">
                      <BookOpen className="size-3.5" />
                    </div>
                    <div>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Next Exam</p>
                      <p className="text-xs font-medium text-foreground line-clamp-1 truncate" title={child.next_exam}>{child.next_exam}</p>
                    </div>
                  </div>
                </div>

                {/* Sub-actions for each child */}
                <div className="flex items-center gap-2 mt-3">
                  <Button variant="secondary" size="sm" className="w-full text-xs" asChild>
                    <Link to={`/parent/marks`}>Report Card</Link>
                  </Button>
                  <Button variant="secondary" size="sm" className="w-full text-xs" asChild>
                    <Link to={`/parent/attendance`}>Leave Request</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Links for the Parent */}
      <h3 className="text-sm font-semibold text-foreground pt-4 flex items-center gap-2">
        <School className="size-4 text-primary" /> School Updates
      </h3>
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Notice Board</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
             {[
               { title: 'PTM Scheduled for next Saturday', date: '3 hours ago', tag: 'Important' },
               { title: 'School transport fee revision', date: '2 days ago', tag: 'Finance' },
               { title: 'Winter Vacation Dates', date: '1 week ago', tag: 'General' },
             ].map((n, i) => (
               <div key={i} className="flex gap-3 justify-between items-start border-b border-border/50 last:border-0 pb-3 last:pb-0">
                 <div>
                   <p className="text-sm font-medium text-foreground hover:text-primary cursor-pointer transition-colors">
                     {n.title}
                   </p>
                   <p className="text-xs text-muted-foreground mt-1">{n.date}</p>
                 </div>
                 <span className="text-[10px] bg-muted px-2 py-0.5 rounded text-muted-foreground font-medium">{n.tag}</span>
               </div>
             ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Fee Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-10 w-10 text-emerald-500 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                <Wallet className="size-5" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Total Dues</p>
                <p className="font-bold text-lg text-foreground">₹{totalFeeDue}</p>
              </div>
            </div>
            <Button className="w-full text-xs" asChild>
              <Link to="/parent/fees">View Fee Structure</Link>
            </Button>
            <Button variant="outline" className="w-full mt-2 text-xs" asChild>
              <Link to="/parent/fees/receipts">Download Receipts</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

    </div>
  )
}
