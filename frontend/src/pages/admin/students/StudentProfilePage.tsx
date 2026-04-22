import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { UserAvatar } from '@/components/ui/avatar'
import { StatusBadge } from '@/components/ui/badge'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Pencil, User, MapPin, Phone, Mail, FileText, Activity, Wallet } from 'lucide-react'

export default function StudentProfilePage() {
  const { id } = useParams()

  // Mock data fetching based on id
  const student = {
    id: id || 'STU-2026-90',
    full_name: 'Aditi Verma',
    class: 'Class 10',
    section: 'A',
    roll_no: '02',
    date_of_birth: '12 May 2011',
    gender: 'FEMALE',
    status: 'ACTIVE',
    parent_name: 'Suresh Verma',
    contact_number: '+91 98765 43210',
    email: 'suresh.verma@example.com',
    address: '42, Oakwood View, Phase 2, New Delhi',
    attendance: '96.4%',
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      <PageHeader
        title="Student Profile"
        description="Detailed view of academic and personal records"
        breadcrumbs={[
          { label: 'Admin' },
          { label: 'Students', href: '/admin/students' },
          { label: student.full_name }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link to="/admin/students"><ArrowLeft className="size-4 mr-2" /> Directory</Link>
            </Button>
            <Button size="sm" asChild>
              <Link to={`/admin/students/${student.id}/edit`}><Pencil className="size-4 mr-2" /> Edit</Link>
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 md:grid-cols-3">
        {/* Left Col: Identity Card */}
        <div className="md:col-span-1 space-y-6">
          <Card className="overflow-hidden">
            <div className="h-24 bg-gradient-to-br from-primary/60 to-violet-500/40 relative">
              <div className="absolute top-3 right-3">
                <StatusBadge status={student.status} />
              </div>
            </div>
            <CardContent className="p-6 pt-0 text-center relative">
              <UserAvatar 
                name={student.full_name} 
                size="xl" 
                className="w-24 h-24 text-2xl mx-auto -mt-12 mb-4 ring-4 ring-background border border-border shadow-xl"
              />
              <h2 className="text-xl font-bold text-foreground">{student.full_name}</h2>
              <p className="text-sm font-medium text-primary mt-1">{student.class} - {student.section}</p>
              
              <div className="flex items-center justify-center gap-4 mt-6 text-sm">
                <div className="text-center">
                  <p className="text-muted-foreground mb-1 text-xs uppercase tracking-widest font-semibold">Roll No</p>
                  <p className="font-mono font-medium">{student.roll_no}</p>
                </div>
                <div className="w-px h-8 bg-border" />
                <div className="text-center">
                  <p className="text-muted-foreground mb-1 text-xs uppercase tracking-widest font-semibold">Adm No</p>
                  <p className="font-mono font-medium">{student.id}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-sm font-semibold flex items-center gap-2"><User className="size-4 text-emerald-500" /> Guardian Info</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div className="flex items-start gap-3">
                <User className="size-4 text-muted-foreground mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-foreground">{student.parent_name}</p>
                  <p className="text-xs text-muted-foreground">Father</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Phone className="size-4 text-muted-foreground mt-0.5" />
                <p className="text-sm text-foreground">{student.contact_number}</p>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="size-4 text-muted-foreground mt-0.5" />
                <p className="text-sm text-foreground truncate">{student.email}</p>
              </div>
              <div className="flex items-start gap-3">
                <MapPin className="size-4 text-muted-foreground mt-0.5 shrink-0" />
                <p className="text-sm text-foreground leading-relaxed">{student.address}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Col: Details Tabs */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader className="pb-3 border-b border-border flex flex-row items-center gap-6 overflow-x-auto whitespace-nowrap hide-scrollbar">
              <div className="text-sm font-bold text-primary border-b-2 border-primary pb-3 -mb-[13px] cursor-pointer">Overview</div>
              <div className="text-sm font-medium text-muted-foreground hover:text-foreground pb-3 -mb-[13px] cursor-pointer transition-colors">Academics</div>
              <div className="text-sm font-medium text-muted-foreground hover:text-foreground pb-3 -mb-[13px] cursor-pointer transition-colors">Attendance</div>
              <div className="text-sm font-medium text-muted-foreground hover:text-foreground pb-3 -mb-[13px] cursor-pointer transition-colors">Fees</div>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              
              {/* Basic Info Section */}
              <div>
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">Personal Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground mb-1">Date of Birth</p>
                    <p className="text-sm font-medium text-foreground">{student.date_of_birth}</p>
                  </div>
                  <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground mb-1">Gender</p>
                    <p className="text-sm font-medium text-foreground capitalize">{student.gender.toLowerCase()}</p>
                  </div>
                  <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground mb-1">Blood Group</p>
                    <p className="text-sm font-medium text-foreground">O+</p>
                  </div>
                  <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                    <p className="text-xs text-muted-foreground mb-1">Admission Date</p>
                    <p className="text-sm font-medium text-foreground">01 Apr 2021</p>
                  </div>
                </div>
              </div>

              {/* Quick Metrics */}
              <div>
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">Year to Date Metrics</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="flex flex-col items-center justify-center bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl">
                    <Activity className="size-5 text-blue-500 mb-2" />
                    <p className="text-2xl font-bold text-foreground">{student.attendance}</p>
                    <p className="text-xs text-muted-foreground mt-1 text-center">Attendance</p>
                  </div>
                  <div className="flex flex-col items-center justify-center bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl">
                    <FileText className="size-5 text-emerald-500 mb-2" />
                    <p className="text-2xl font-bold text-foreground">A</p>
                    <p className="text-xs text-muted-foreground mt-1 text-center">Average Grade</p>
                  </div>
                  <div className="flex flex-col items-center justify-center bg-rose-500/10 border border-rose-500/20 p-4 rounded-xl">
                    <Wallet className="size-5 text-rose-500 mb-2" />
                    <p className="text-xl font-bold text-foreground mt-1">₹0</p>
                    <p className="text-xs text-muted-foreground mt-1 text-center">Pending Dues</p>
                  </div>
                </div>
              </div>

            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
