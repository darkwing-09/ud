import { Link } from 'react-router-dom'
import { GraduationCap, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PageTransition, MotionTiltCard } from '@/components/ui/motion'

export default function NotFoundPage() {
  return (
    <PageTransition className="min-h-screen flex items-center justify-center relative bg-[length:100vw_100vh] bg-no-repeat bg-center" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070&auto=format&fit=crop')" }}>
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-background/80 backdrop-blur-[4px]" />

      <MotionTiltCard className="text-center relative z-10 p-12 max-w-lg glass-card rounded-3xl shadow-2xl shadow-black/20">
        <div className="inline-flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/20 shadow-inner shadow-primary/30 mb-8 blur-[0.5px]">
          <GraduationCap className="h-10 w-10 text-primary" />
        </div>
        <h1 className="text-9xl font-black text-foreground tracking-tighter mix-blend-overlay">404</h1>
        <h2 className="mt-4 text-2xl font-bold text-foreground">Page Not Found</h2>
        <p className="mt-4 text-muted-foreground text-lg leading-relaxed">
          The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
        </p>
        <Button asChild size="lg" className="mt-10 shadow-lg shadow-primary/20 rounded-full px-8">
          <Link to="/">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
          </Link>
        </Button>
      </MotionTiltCard>
    </PageTransition>
  )
}
