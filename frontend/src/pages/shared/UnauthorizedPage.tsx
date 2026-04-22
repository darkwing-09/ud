import { AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function UnauthorizedPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-center px-4">
      <div className="bg-rose-500/10 border border-rose-500/20 p-6 rounded-3xl mb-6">
        <AlertTriangle className="w-16 h-16 text-rose-500" />
      </div>
      <h1 className="text-4xl font-bold text-foreground mb-3 tracking-tight">Access Denied</h1>
      <p className="text-muted-foreground mb-8 max-w-md">
        You do not have the required permissions to view this page. If you believe this is a mistake, contact your administrator.
      </p>
      <Button variant="default" size="lg" asChild>
        <Link to="/">Return to Dashboard</Link>
      </Button>
    </div>
  )
}
