import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface SchoolStore {
  schoolId: string | null
  schoolName: string | null
  activeAcademicYearId: string | null
  activeAcademicYearName: string | null
  logoUrl: string | null

  setSchool: (id: string, name: string, logo?: string | null) => void
  setActiveYear: (id: string, name: string) => void
  clearSchool: () => void
}

export const useSchoolStore = create<SchoolStore>()(
  persist(
    (set) => ({
      schoolId: null,
      schoolName: null,
      activeAcademicYearId: null,
      activeAcademicYearName: null,
      logoUrl: null,

      setSchool: (id, name, logo = null) => set({ schoolId: id, schoolName: name, logoUrl: logo }),
      setActiveYear: (id, name) => set({ activeAcademicYearId: id, activeAcademicYearName: name }),
      clearSchool: () => set({ schoolId: null, schoolName: null, activeAcademicYearId: null, activeAcademicYearName: null, logoUrl: null }),
    }),
    {
      name: 'educore-school',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
