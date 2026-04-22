import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { Outlet } from 'react-router-dom'
import { Toaster } from 'sonner'

export function AppShell() {
  return (
    <div 
      className="flex h-screen overflow-hidden bg-[length:100vw_100vh] bg-center bg-no-repeat relative"
      style={{ backgroundImage: "url('https://images.unsplash.com/photo-1541339907198-e08756dedf3f?q=80&w=2070&auto=format&fit=crop')" }}
    >
      {/* Universal Dark Overlay: Restricts image to very low intensity */}
      <div className="absolute inset-0 bg-background/80 backdrop-blur-[4px] z-0" />

      {/* Sidebar is z-10 so it sits above the background overlay */}
      <div className="z-10 bg-sidebar/80 backdrop-blur-xl border-r border-border shrink-0">
        <Sidebar />
      </div>

      <div className="flex flex-1 flex-col min-w-0 overflow-hidden relative z-10">
        <div className="bg-background/40 backdrop-blur-sm border-b border-border">
          <TopBar />
        </div>
        
        <main
          id="main-content"
          className="flex-1 overflow-y-auto px-4 py-6 lg:px-6 lg:py-8"
        >
          <Outlet />
        </main>
      </div>
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          classNames: {
            toast: 'bg-card border border-border text-foreground shadow-xl',
            title: 'text-foreground font-semibold text-sm',
            description: 'text-muted-foreground text-xs',
            success: 'border-emerald-500/30',
            error: 'border-rose-500/30',
            warning: 'border-amber-500/30',
          },
        }}
      />
    </div>
  )
}
