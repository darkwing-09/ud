import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// --- Request interceptor: attach access token ---
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- Response interceptor: auto-refresh on 401 ---
let refreshing = false
let refreshQueue: Array<(token: string) => void> = []

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true

      if (refreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((token) => {
            original.headers.Authorization = `Bearer ${token}`
            resolve(api(original))
          })
        })
      }

      refreshing = true

      try {
        const { refreshToken, setTokens, logout } = useAuthStore.getState()
        if (!refreshToken) { logout(); throw error }

        const res = await axios.post(`${BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const { access_token, refresh_token } = res.data.data
        setTokens(access_token, refresh_token)

        refreshQueue.forEach((cb) => cb(access_token))
        refreshQueue = []

        original.headers.Authorization = `Bearer ${access_token}`
        return api(original)
      } catch (e) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(e)
      } finally {
        refreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api

// --- Typed helper wrappers ---
export async function get<T>(url: string, params?: object): Promise<T> {
  const r = await api.get<{ success: boolean; data: T }>(url, { params })
  return r.data.data
}

export async function post<T>(url: string, data?: unknown): Promise<T> {
  const r = await api.post<{ success: boolean; data: T }>(url, data)
  return r.data.data
}

export async function put<T>(url: string, data?: unknown): Promise<T> {
  const r = await api.put<{ success: boolean; data: T }>(url, data)
  return r.data.data
}

export async function patch<T>(url: string, data?: unknown): Promise<T> {
  const r = await api.patch<{ success: boolean; data: T }>(url, data)
  return r.data.data
}

export async function del<T>(url: string): Promise<T> {
  const r = await api.delete<{ success: boolean; data: T }>(url)
  return r.data.data
}

export function uploadFile<T>(url: string, file: File, extra?: Record<string, string>): Promise<T> {
  const form = new FormData()
  form.append('file', file)
  if (extra) Object.entries(extra).forEach(([k, v]) => form.append(k, v))
  return api
    .post<{ success: boolean; data: T }>(url, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data.data)
}
