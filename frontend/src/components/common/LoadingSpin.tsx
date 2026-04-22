import { Loader2 } from 'lucide-react'

export function LoadingSpin({ size = 24, className = '' }: { size?: number, className?: string }) {
  return (
    <div className={`flex items-center justify-center w-full h-full min-h-[50vh] ${className}`}>
      <Loader2 size={size} className="animate-spin text-primary" />
    </div>
  )
}
