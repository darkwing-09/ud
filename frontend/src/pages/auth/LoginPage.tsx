import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Eye, EyeOff, GraduationCap, Lock, Mail, Building2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { post } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useSchoolStore } from '@/store/schoolStore'
import { ROLE_HOME } from '@/lib/constants'
import type { AuthUser } from '@/store/authStore'

const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(6, 'Password too short'),
  school_code: z.string().optional(),
})

type LoginForm = z.infer<typeof loginSchema>

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

import { PageTransition, MotionTiltCard } from '@/components/ui/motion'

export default function LoginPage() {
  const navigate = useNavigate()
  const [showPw, setShowPw] = useState(false)
  const login = useAuthStore((s) => s.login)
  const setTokens = useAuthStore((s) => s.setTokens)
  // School context will be loaded via a separate /school/me endpoint later

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  // Phase 7 Integration: Two step login (OAuth2 standard)
  const { mutate, isPending } = useMutation({
    mutationFn: async (credentials: LoginForm) => {
      // 1. Get tokens
      const tokenData = await post<TokenResponse>('/auth/login', credentials)
      
      // Temporary manual token set for the subsequent request if Zustand hasn't triggered rerender
      setTokens(tokenData.access_token, tokenData.refresh_token)

      // 2. Get User Profile using the new token
      const { get } = await import('@/lib/api')
      const userProfile = await get<AuthUser>('/auth/me')

      return { tokens: tokenData, user: userProfile }
    },
    onSuccess: (data) => {
      login(data.user, data.tokens.access_token, data.tokens.refresh_token)
      toast.success(`Welcome back, ${data.user.full_name.split(' ')[0]}!`)
      navigate(ROLE_HOME[data.user.role] ?? '/')
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail ?? 'Invalid credentials'
      toast.error(msg)
    },
  })

  return (
    <PageTransition 
      className="min-h-screen flex overflow-hidden relative bg-[length:100vw_100vh] bg-center bg-no-repeat"
      style={{ backgroundImage: "url('https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070&auto=format&fit=crop')" }}
    >
      {/* Global Dark glass overlay for contrast (very low intensity background) */}
      <div className="absolute inset-0 bg-background/80 md:bg-background/80 backdrop-blur-[4px] z-0" />

      {/* Left: Brand panel */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-12 z-10 border-r border-white/10 bg-black/20 backdrop-blur-md">
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <MotionTiltCard className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary shadow-2xl shadow-primary/40">
              <GraduationCap className="h-7 w-7 text-white" />
            </MotionTiltCard>
            <span className="text-2xl font-bold text-white tracking-tight">EduCore</span>
          </div>
        </div>

        <div className="relative z-10 space-y-6">
          <MotionTiltCard>
            <h1 className="text-5xl font-bold text-white leading-tight">
              Smarter School<br />Management.
            </h1>
            <p className="mt-4 text-gray-200 text-lg leading-relaxed max-w-sm font-medium">
              One platform for admissions, attendance, examinations, fees, payroll, and more.
            </p>
          </MotionTiltCard>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-2 pt-4">
            {['Multi-tenant', 'Role-based access', 'Smart Analytics', 'PDF reports'].map((f) => (
              <span key={f} className="px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-sm font-semibold text-white shadow-lg">
                {f}
              </span>
            ))}
          </div>
        </div>

        <p className="relative z-10 text-sm font-medium text-gray-300">
          © {new Date().getFullYear()} EduCore System. All rights reserved.
        </p>
      </div>

      {/* Right: Login form */}
      <div className="flex flex-1 items-center justify-center px-6 py-12 relative overflow-hidden">
        {/* Top right gradient ambient */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        
        <MotionTiltCard className="w-full max-w-md relative z-10">
          <div className="glass-card p-8 rounded-2xl shadow-2xl shadow-black/5 border border-border/50">
            {/* Mobile logo */}
            <div className="flex flex-col items-center lg:hidden space-y-3 mb-8">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg shadow-primary/30">
                <GraduationCap className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-foreground">EduCore</h1>
            </div>

            {/* Header */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-foreground">Sign in to your account</h2>
              <p className="mt-2 text-sm text-muted-foreground font-medium">
                Enter your credentials to access the platform
              </p>
            </div>

          {/* Form */}
          <form onSubmit={handleSubmit((data) => mutate(data))} className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-foreground">
                Email address <span className="text-destructive">*</span>
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

            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-foreground">
                Password <span className="text-destructive">*</span>
              </label>
              <Input
                id="password"
                type={showPw ? 'text' : 'password'}
                placeholder="Your password"
                leftIcon={<Lock />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPw((v) => !v)}
                    className="text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
                    aria-label={showPw ? 'Hide password' : 'Show password'}
                  >
                    {showPw ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                }
                error={errors.password?.message}
                {...register('password')}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="school_code" className="block text-sm font-medium text-foreground">
                School code <span className="text-muted-foreground text-xs">(optional for admins)</span>
              </label>
              <Input
                id="school_code"
                type="text"
                placeholder="e.g. DELHI-PS-001"
                leftIcon={<Building2 />}
                {...register('school_code')}
              />
            </div>

            <div className="flex items-center justify-end">
              <a href="/forgot-password" className="text-xs text-primary hover:text-primary/80 font-medium transition-colors">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full shadow-lg shadow-primary/20"
              loading={isPending}
            >
              Sign in
            </Button>
          </form>

          {/* Demo credentials note */}
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 mt-8">
            <p className="text-xs text-amber-400 font-semibold mb-1">Demo credentials</p>
            <p className="text-xs text-muted-foreground">
              Email: <code className="text-amber-400">admin@educore.demo</code><br />
              Password: <code className="text-amber-400">Demo@1234</code>
            </p>
          </div>
          </div>
        </MotionTiltCard>
      </div>
    </PageTransition>
  )
}
