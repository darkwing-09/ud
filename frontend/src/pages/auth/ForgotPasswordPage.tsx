import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { Link } from 'react-router-dom'
import { PageTransition, MotionTiltCard } from '@/components/ui/motion'
import { post } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Mail } from 'lucide-react'

const schema = z.object({
  email: z.string().email('Invalid email address'),
})

type FormValues = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormValues) => {
    try {
      await post('/auth/forgot-password', data)
      toast.success('Reset link sent if account exists')
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? 'Failed to send reset link')
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
            <h1 className="text-2xl font-bold">Forgot Password</h1>
            <p className="text-muted-foreground text-sm">Enter your email to receive a reset link</p>
          </div>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 text-left">
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-foreground">
                Email address
              </label>
              <Input
                id="email"
                type="email"
                placeholder="admin@school.edu"
                leftIcon={<Mail />}
                error={errors.email?.message}
                {...register('email')}
              />
            </div>

            <Button type="submit" className="w-full" loading={isSubmitting}>
              Send Reset Link
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
