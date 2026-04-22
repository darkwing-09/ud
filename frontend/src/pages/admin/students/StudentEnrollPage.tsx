import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowLeft, Save, User, Calendar, Phone, Mail, Home, MapPin } from 'lucide-react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import { MOCK_CLASSES } from '@/lib/constants'

// Very basic Zod schema for student enrollment
const enrollSchema = z.object({
  first_name: z.string().min(2, 'First name is required'),
  last_name: z.string().min(2, 'Last name is required'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['MALE', 'FEMALE', 'OTHER']),
  class_id: z.string().min(1, 'Class selection is required'),
  section_id: z.string().min(1, 'Section selection is required'), // In real app, derived from class
  parent_name: z.string().min(2, 'Parent name is required'),
  contact_number: z.string().min(10, 'Valid phone number is required'),
  email: z.string().email('Valid email is required'),
  address: z.string().min(5, 'Address is required'),
})

type EnrollForm = z.infer<typeof enrollSchema>

export default function StudentEnrollPage() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<EnrollForm>({
    resolver: zodResolver(enrollSchema),
    defaultValues: {
      gender: 'MALE',
      class_id: '',
      section_id: 'sec-a',
    }
  })

  const onSubmit = (data: EnrollForm) => {
    setIsSubmitting(true)
    console.log(data)
    setTimeout(() => {
      toast.success('Student enrolled successfully!')
      setIsSubmitting(false)
      navigate('/admin/students')
    }, 1500)
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <PageHeader
        title="Enroll New Student"
        description="Enter the student and guardian details for admission"
        breadcrumbs={[
          { label: 'Admin' },
          { label: 'Students', href: '/admin/students' },
          { label: 'Enroll' }
        ]}
        actions={
          <Button variant="outline" size="sm" asChild>
            <Link to="/admin/students"><ArrowLeft className="size-4 mr-2" /> Back</Link>
          </Button>
        }
      />

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        
        {/* Personal Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <User className="size-4 text-primary" /> Personal Information
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">First Name *</label>
              <Input placeholder="John" {...register('first_name')} error={errors.first_name?.message} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Last Name *</label>
              <Input placeholder="Doe" {...register('last_name')} error={errors.last_name?.message} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Date of Birth *</label>
              <Input type="date" leftIcon={<Calendar />} {...register('date_of_birth')} error={errors.date_of_birth?.message} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Gender *</label>
              <select 
                {...register('gender')} 
                className="flex h-9 w-full rounded-md border border-input bg-input px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring text-foreground"
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
              {errors.gender && <p className="text-xs text-destructive">{errors.gender.message}</p>}
            </div>
          </CardContent>
        </Card>

        {/* Academic Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Home className="size-4 text-blue-500" /> Academic Placement
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Class Admission *</label>
              <select 
                {...register('class_id')} 
                className="flex h-9 w-full rounded-md border border-input bg-input px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring text-foreground"
              >
                <option value="" disabled>Select a class</option>
                <option value="cls-1">Class 1</option>
                <option value="cls-2">Class 2</option>
                <option value="cls-9">Class 9</option>
                <option value="cls-10">Class 10</option>
              </select>
              {errors.class_id && <p className="text-xs text-destructive">{errors.class_id.message}</p>}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Section *</label>
              <select 
                {...register('section_id')} 
                className="flex h-9 w-full rounded-md border border-input bg-input px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring text-foreground"
              >
                <option value="sec-a">Section A</option>
                <option value="sec-b">Section B</option>
                <option value="sec-c">Section C</option>
              </select>
              {errors.section_id && <p className="text-xs text-destructive">{errors.section_id.message}</p>}
            </div>
          </CardContent>
        </Card>

        {/* Guardian / Contact Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Phone className="size-4 text-emerald-500" /> Guardian & Contact Details
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Guardian Name *</label>
              <Input placeholder="Parent / Guardian Name" leftIcon={<User />} {...register('parent_name')} error={errors.parent_name?.message} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Contact Number *</label>
              <Input placeholder="+91 9999999999" leftIcon={<Phone />} {...register('contact_number')} error={errors.contact_number?.message} />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <label className="text-sm font-medium text-foreground">Email Address *</label>
              <Input placeholder="parent@example.com" type="email" leftIcon={<Mail />} {...register('email')} error={errors.email?.message} />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <label className="text-sm font-medium text-foreground">Residential Address *</label>
              <Input placeholder="Full residential address" leftIcon={<MapPin />} {...register('address')} error={errors.address?.message} />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3 pt-4 border-t border-border mt-6">
          <Button type="button" variant="ghost" asChild>
            <Link to="/admin/students">Cancel</Link>
          </Button>
          <Button type="submit" loading={isSubmitting} className="min-w-[120px]">
            <Save className="mr-2 size-4" /> Enroll Student
          </Button>
        </div>
      </form>
    </div>
  )
}
