import { Menu, Bell,ChevronDown, User, LogOut } from 'lucide-react'
import { useUIStore } from '@/store/uiStore'
import { useAuth } from '@/hooks/useAuth'
import { useSchoolStore } from '@/store/schoolStore'
import { useAuthStore } from '@/store/authStore'
import { UserAvatar } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { Link } from 'react-router-dom'
import { ROLE_LABELS } from '@/lib/constants'

export function TopBar() {
  const { openMobileSidebar } = useUIStore()
  const { user } = useAuth()
  const { schoolName, activeAcademicYearName } = useSchoolStore()
  const logout = useAuthStore((s) => s.logout)

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-border bg-[hsl(var(--topbar-bg))]/80 backdrop-blur-md px-4 lg:px-6">
      {/* Mobile menu */}
      <Button
        variant="ghost"
        size="icon-sm"
        className="lg:hidden"
        onClick={openMobileSidebar}
        aria-label="Open menu"
      >
        <Menu className="size-5" />
      </Button>

      {/* Breadcrumb / school info */}
      <div className="flex-1 min-w-0">
        {activeAcademicYearName && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="font-medium text-foreground/70 truncate">{schoolName}</span>
            <span>·</span>
            <span className="truncate">{activeAcademicYearName}</span>
          </div>
        )}
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <Button variant="ghost" size="icon-sm" aria-label="Notifications" className="relative">
          <Bell className="size-4" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-primary animate-glow" />
        </Button>

        {/* User menu */}
        {user && (
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <button className="flex items-center gap-2 rounded-lg px-2 py-1 hover:bg-accent transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring">
                <UserAvatar name={user.full_name} src={user.avatar_url} size="sm" />
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium leading-none text-foreground">{user.full_name.split(' ')[0]}</p>
                  <p className="text-xs text-muted-foreground">
                    {ROLE_LABELS[user.role as keyof typeof ROLE_LABELS] ?? user.role}
                  </p>
                </div>
                <ChevronDown className="size-3 text-muted-foreground hidden sm:block" />
              </button>
            </DropdownMenu.Trigger>

            <DropdownMenu.Portal>
              <DropdownMenu.Content
                className="z-50 min-w-[180px] rounded-xl border border-border bg-popover p-1.5 shadow-xl animate-fade-in"
                sideOffset={8}
                align="end"
              >
                <div className="px-3 py-2 mb-1">
                  <p className="text-sm font-semibold text-foreground">{user.full_name}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
                <DropdownMenu.Separator className="my-1 h-px bg-border" />
                <DropdownMenu.Item asChild>
                  <Link
                    to="/profile"
                    className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-foreground hover:bg-accent cursor-pointer outline-none select-none"
                  >
                    <User className="size-4 text-muted-foreground" />
                    Profile Settings
                  </Link>
                </DropdownMenu.Item>
                <DropdownMenu.Separator className="my-1 h-px bg-border" />
                <DropdownMenu.Item
                  className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-rose-400 hover:bg-rose-500/10 cursor-pointer outline-none select-none"
                  onSelect={() => { logout(); window.location.href = '/login' }}
                >
                  <LogOut className="size-4" />
                  Sign Out
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        )}
      </div>
    </header>
  )
}
