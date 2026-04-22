import { useAuthStore } from '@/store/authStore'
import { ADMIN_ROLES, TEACHER_ROLES, type Role } from '@/lib/constants'

export function useAuth() {
  const { user, isAuthenticated, accessToken, login, logout, updateUser } = useAuthStore()

  const role = user?.role as Role | undefined
  const isAdmin = isAuthenticated && role !== undefined && ADMIN_ROLES.includes(role as never)
  const isTeacher = isAuthenticated && role !== undefined && TEACHER_ROLES.includes(role as never)
  const isStudent = role === 'STUDENT'
  const isParent = role === 'PARENT'
  const isSuperAdmin = role === 'SUPER_ADMIN'

  const hasRole = (...roles: Role[]) => !!role && roles.includes(role)

  return {
    user,
    role,
    isAuthenticated,
    accessToken,
    isAdmin,
    isTeacher,
    isStudent,
    isParent,
    isSuperAdmin,
    hasRole,
    login,
    logout,
    updateUser,
  }
}
