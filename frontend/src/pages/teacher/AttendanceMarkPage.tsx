import { useState } from 'react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { UserAvatar } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { CheckCircle2, UserX, Clock, CalendarIcon, Save } from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'LEAVE'
type StudentStatus = { id: string; name: string; roll_no: string; status: AttendanceStatus }

const MOCK_DATE = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })
const MOCK_STUDENTS: StudentStatus[] = [
  { id: '1', name: 'Aarav Sharma', roll_no: '01', status: 'PRESENT' },
  { id: '2', name: 'Aditi Verma', roll_no: '02', status: 'PRESENT' },
  { id: '3', name: 'Aryan Gupta', roll_no: '03', status: 'PRESENT' },
  { id: '4', name: 'Diya Patel', roll_no: '04', status: 'PRESENT' },
  { id: '5', name: 'Ishaan Singh', roll_no: '05', status: 'PRESENT' },
  { id: '6', name: 'Kavya Joshi', roll_no: '06', status: 'PRESENT' },
  { id: '7', name: 'Krishna Kumar', roll_no: '07', status: 'PRESENT' },
  { id: '8', name: 'Neha Reddy', roll_no: '08', status: 'PRESENT' },
]

export default function AttendanceMarkPage() {
  const [students, setStudents] = useState<StudentStatus[]>(MOCK_STUDENTS)
  const [isSaving, setIsSaving] = useState(false)

  const handleStatusChange = (id: string, newStatus: AttendanceStatus) => {
    setStudents(prev => prev.map(s => s.id === id ? { ...s, status: newStatus } : s))
  }

  const handleMarkAll = (status: AttendanceStatus) => {
    setStudents(prev => prev.map(s => ({ ...s, status })))
  }

  const handleSubmit = () => {
    setIsSaving(true)
    setTimeout(() => {
      toast.success('Attendance submitted successfully')
      setIsSaving(false)
    }, 1200)
  }

  const stats = {
    present: students.filter(s => s.status === 'PRESENT').length,
    absent: students.filter(s => s.status === 'ABSENT').length,
    leave: students.filter(s => s.status === 'LEAVE' || s.status === 'HALF_DAY').length,
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      <PageHeader
        title="Mark Attendance"
        description={<span className="flex items-center gap-2"><CalendarIcon className="size-4" /> {MOCK_DATE}</span>}
      />

      <div className="grid gap-6 md:grid-cols-4">
        {/* Quick Stats sidebar */}
        <div className="space-y-6 md:col-span-1">
          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-sm font-semibold">Today's Summary</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div>
                <div className="flex justify-between text-xs text-muted-foreground font-medium mb-1.5 uppercase">
                  <span>Class Strength</span>
                  <span>{students.length}</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="flex items-center gap-2 text-emerald-500 font-medium"><CheckCircle2 className="size-4" /> Present</span>
                  <span className="font-semibold">{stats.present}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="flex items-center gap-2 text-rose-500 font-medium"><UserX className="size-4" /> Absent</span>
                  <span className="font-semibold">{stats.absent}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="flex items-center gap-2 text-amber-500 font-medium"><Clock className="size-4" /> Leave/Half</span>
                  <span className="font-semibold">{stats.leave}</span>
                </div>
              </div>
              
              <div className="pt-4 border-t border-border">
                <Button className="w-full gap-2 shadow-primary/20 shadow-md" onClick={handleSubmit} loading={isSaving}>
                  <Save className="size-4" /> Submit Register
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main interactive list */}
        <div className="md:col-span-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between border-b border-border pb-4 bg-muted/20">
              <CardTitle className="text-sm font-semibold">Class 10-A Roll Call</CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => handleMarkAll('PRESENT')} className="text-emerald-500 hover:text-emerald-400 hover:bg-emerald-500/10 border-emerald-500/20">
                  <CheckCircle2 className="mr-2 size-3.5" /> Mark All Present
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-border">
                {students.map((student) => (
                  <div key={student.id} className="flex flex-wrap items-center justify-between gap-4 p-4 hover:bg-muted/10 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-8 text-center text-xs font-mono text-muted-foreground mr-2">
                        {student.roll_no}
                      </div>
                      <UserAvatar name={student.name} size="sm" className="hidden sm:flex" />
                      <p className="font-medium text-sm text-foreground">{student.name}</p>
                    </div>

                    {/* Status Toggles */}
                    <div className="flex p-1 bg-input/50 rounded-lg border border-border">
                      <button
                        onClick={() => handleStatusChange(student.id, 'PRESENT')}
                        className={cn(
                          'px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200',
                          student.status === 'PRESENT' ? 'bg-emerald-500 text-white shadow-sm' : 'text-muted-foreground hover:text-emerald-400 hover:bg-emerald-500/10'
                        )}
                      >
                        P
                      </button>
                      <button
                        onClick={() => handleStatusChange(student.id, 'ABSENT')}
                        className={cn(
                          'px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200',
                          student.status === 'ABSENT' ? 'bg-rose-500 text-white shadow-sm' : 'text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10'
                        )}
                      >
                        A
                      </button>
                      <button
                        onClick={() => handleStatusChange(student.id, 'HALF_DAY')}
                        className={cn(
                          'px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200',
                          student.status === 'HALF_DAY' ? 'bg-blue-500 text-white shadow-sm' : 'text-muted-foreground hover:text-blue-400 hover:bg-blue-500/10'
                        )}
                        title="Half Day"
                      >
                        H
                      </button>
                      <button
                        onClick={() => handleStatusChange(student.id, 'LEAVE')}
                        className={cn(
                          'px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200',
                          student.status === 'LEAVE' ? 'bg-amber-500 text-white shadow-sm' : 'text-muted-foreground hover:text-amber-400 hover:bg-amber-500/10'
                        )}
                        title="On Leave"
                      >
                        L
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
