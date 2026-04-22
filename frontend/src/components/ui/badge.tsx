import { cn, statusVariant } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium border transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary/15 text-primary border-primary/20',
        success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20',
        warning: 'bg-amber-500/15 text-amber-400 border-amber-500/20',
        error: 'bg-rose-500/15 text-rose-400 border-rose-500/20',
        info: 'bg-blue-500/15 text-blue-400 border-blue-500/20',
        muted: 'bg-muted text-muted-foreground border-border',
        violet: 'bg-violet-500/15 text-violet-400 border-violet-500/20',
      },
    },
    defaultVariants: { variant: 'default' },
  }
)

interface BadgeProps extends VariantProps<typeof badgeVariants> {
  className?: string
  children: React.ReactNode
  dot?: boolean
}

function Badge({ className, variant, dot, children }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)}>
      {dot && (
        <span className={cn(
          'size-1.5 rounded-full',
          variant === 'success' && 'bg-emerald-400',
          variant === 'warning' && 'bg-amber-400',
          variant === 'error' && 'bg-rose-400',
          variant === 'info' && 'bg-blue-400',
          variant === 'muted' && 'bg-muted-foreground',
          (!variant || variant === 'default') && 'bg-primary',
        )} />
      )}
      {children}
    </span>
  )
}

// Auto-variant badge from a raw status string
function StatusBadge({ status, className }: { status: string; className?: string }) {
  const variant = statusVariant(status)
  return (
    <Badge variant={variant} dot className={className}>
      {status.charAt(0) + status.slice(1).toLowerCase().replace(/_/g, ' ')}
    </Badge>
  )
}

export { Badge, StatusBadge, badgeVariants }
