import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { PageTransition, MotionTiltCard } from '@/components/ui/motion'
import { post } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Lock } from 'lucide-react'

const schema = z.object({
  otp: z.string().min(6, 'Must be exactly 6 characters').max(6, 'Must be exactly 6 characters'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
})

type FormValues = z.infer<typeof schema>

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormValues) => {
    if (!token) {
      toast.error('Invalid reset link')
      return
    }

    try {
      await post('/auth/reset-password', {
        token,
        otp: data.otp,
        new_password: data.new_password
      })
      toast.success('Password reset successfully')
      navigate('/login')
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to reset password')
    }
  }

  return (
    <PageTransition 
      className="min-h-screen flex items-center justify-center p-4 bg-[length:100vw_100vh] bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070&auto=format&fit=crop')" }}
    >
      <div className="absolute inset-0 bg-background/80 backdrop-blur-[4px]" />

      <MotionTiltCard className="w-full max-w-md relative z-10 glass-card p-8 rounded-2xl shadow-2xl shadow-black/20 border-border/50 border">
        <div className="text-center space-y-6">
          <div className="space-y-2">
            <h1 className="text-2xl font-bold">Set New Password</h1>
            <p className="text-muted-foreground text-sm">Update your password to regain access</p>
          </div>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 text-left">
            <div className="space-y-2">
              <label htmlFor="otp" className="block text-sm font-medium text-foreground">
                6-Digit Reset Code
              </label>
              <Input
                id="otp"
                type="text"
                placeholder="123456"
                error={errors.otp?.message}
                {...register('otp')}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="new_password" className="block text-sm font-medium text-foreground">
                New Password
              </label>
              <Input
                id="new_password"
                type="password"
                placeholder="••••••••"
                leftIcon={<Lock />}
                error={errors.new_password?.message}
                {...register('new_password')}
              />
            </div>

            <Button type="submit" className="w-full mt-2" loading={isSubmitting}>
              Reset Password
            </Button>
          </form>

          <div className="text-sm">
            <Link to="/login" className="text-primary hover:underline font-medium">
              Back to login
            </Link>
          </div>
        </div>
      </MotionTiltCard>
    </PageTransition>
  )
}
