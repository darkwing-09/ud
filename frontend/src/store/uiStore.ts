import { create } from 'zustand'

interface UIStore {
  sidebarCollapsed: boolean
  mobileSidebarOpen: boolean
  activeModal: string | null

  toggleSidebar: () => void
  setSidebarCollapsed: (v: boolean) => void
  openMobileSidebar: () => void
  closeMobileSidebar: () => void
  openModal: (id: string) => void
  closeModal: () => void
}

export const useUIStore = create<UIStore>()((set) => ({
  sidebarCollapsed: false,
  mobileSidebarOpen: false,
  activeModal: null,

  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
  openMobileSidebar: () => set({ mobileSidebarOpen: true }),
  closeMobileSidebar: () => set({ mobileSidebarOpen: false }),
  openModal: (id) => set({ activeModal: id }),
  closeModal: () => set({ activeModal: null }),
}))
