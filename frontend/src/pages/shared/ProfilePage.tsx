import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { User, Lock, Mail, Phone, MapPin, Camera, Save, KeyRound } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { UserAvatar } from '@/components/ui/avatar'
import { ROLE_LABELS } from '@/lib/constants'
import { toast } from 'sonner'
import { useAuthStore } from '@/store/authStore'

const updateProfileSchema = z.object({
  phone_number: z.string().optional(),
  address: z.string().optional(),
})

const changePasswordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'New password must be at least 8 characters'),
  confirm_password: z.string().min(8, 'Please confirm your password'),
}).refine(data => data.new_password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

export default function ProfilePage() {
  const { user } = useAuth()
  const updateUser = useAuthStore(s => s.updateUser)
  const [isUpdating, setIsUpdating] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  const profileForm = useForm({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: {
      phone_number: user?.phone_number ?? '+91 9876543210',
      address: user?.address ?? '123, Education Hub, New Delhi, India',
    }
  })

  const passwordForm = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    }
  })

  const onUpdateProfile = (data: any) => {
    setIsUpdating(true)
    setTimeout(() => {
      // Mock API call
      toast.success('Profile updated successfully')
      if (user) {
        updateUser({ ...user, ...data })
      }
      setIsUpdating(false)
    }, 1000)
  }

  const onChangePassword = (data: any) => {
    setIsChangingPassword(true)
    setTimeout(() => {
      // Mock API call
      toast.success('Password changed successfully')
      passwordForm.reset()
      setIsChangingPassword(false)
    }, 1000)
  }

  if (!user) return null

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      <PageHeader
        title="My Profile"
        description="Manage your account settings and preferences"
      />

      <div className="grid gap-6 md:grid-cols-3">
        {/* Left Column: Avatar & Basic Info */}
        <Card className="md:col-span-1 h-fit">
          <CardContent className="p-6 flex flex-col items-center text-center">
            <div className="relative mb-4 group">
              <UserAvatar name={user.full_name} src={user.avatar_url} size="xl" className="ring-4 ring-background shadow-xl w-32 h-32 text-4xl" />
              <button className="absolute bottom-0 right-0 p-2 bg-primary text-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity hover:scale-105 active:scale-95">
                <Camera className="size-4" />
              </button>
            </div>
            
            <h2 className="text-xl font-bold text-foreground">{user.full_name}</h2>
            <p className="text-sm font-medium text-primary mt-1">
              {ROLE_LABELS[user.role as keyof typeof ROLE_LABELS] ?? user.role}
            </p>
            
            <div className="w-full mt-6 space-y-3">
              <div className="flex items-center gap-3 text-sm text-muted-foreground p-3 bg-muted/20 rounded-lg">
                <Mail className="size-4 text-emerald-500" />
                <span className="truncate">{user.email}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground p-3 bg-muted/20 rounded-lg">
                <User className="size-4 text-blue-500" />
                <span className="truncate">@{user.username}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right Column: Forms */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Personal Information</CardTitle>
              <CardDescription>Update your contact details and address</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={profileForm.handleSubmit(onUpdateProfile)} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Full Name</label>
                    <Input value={user.full_name} disabled leftIcon={<User />} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Username</label>
                    <Input value={user.username} disabled leftIcon={<User />} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Phone Number</label>
                    <Input 
                      placeholder="+91 xxxxx xxxxx" 
                      leftIcon={<Phone />} 
                      {...profileForm.register('phone_number')}
                      error={!!profileForm.formState.errors.phone_number}
                    />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <label className="text-xs font-medium text-muted-foreground">Address</label>
                    <Input 
                      placeholder="Your full address" 
                      leftIcon={<MapPin />} 
                      {...profileForm.register('address')}
                      error={!!profileForm.formState.errors.address}
                    />
                  </div>
                </div>
                <div className="flex justify-end pt-2">
                  <Button type="submit" loading={isUpdating} className="gap-2">
                    <Save className="size-4" /> Save Changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <KeyRound className="size-4 text-primary" /> Change Password
              </CardTitle>
              <CardDescription>Ensure your account is using a long, random password to stay secure.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={passwordForm.handleSubmit(onChangePassword)} className="space-y-4">
                <div className="space-y-2 max-w-sm">
                  <label className="text-xs font-medium text-muted-foreground">Current Password</label>
                  <Input 
                    type="password" 
                    placeholder="••••••••" 
                    leftIcon={<Lock />} 
                    {...passwordForm.register('current_password')}
                    error={passwordForm.formState.errors.current_password?.message?.toString()}
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">New Password</label>
                    <Input 
                      type="password" 
                      placeholder="••••••••" 
                      leftIcon={<Lock />} 
                      {...passwordForm.register('new_password')}
                      error={passwordForm.formState.errors.new_password?.message?.toString()}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-muted-foreground">Confirm New Password</label>
                    <Input 
                      type="password" 
                      placeholder="••••••••" 
                      leftIcon={<Lock />} 
                      {...passwordForm.register('confirm_password')}
                      error={passwordForm.formState.errors.confirm_password?.message?.toString()}
                    />
                  </div>
                </div>
                <div className="flex justify-end pt-2">
                  <Button type="submit" variant="secondary" loading={isChangingPassword}>
                    Update Password
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
