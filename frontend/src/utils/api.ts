import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import router from '../router'
import { buildBasicAuthHeader, clearAdminCredentials, getAdminCredentials } from './adminAuth'

type ApiClient = Omit<AxiosInstance, 'get' | 'post' | 'put' | 'patch' | 'delete'> & {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
}

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
}) as ApiClient

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    if (config.url?.startsWith('/admin/')) {
      const credentials = getAdminCredentials()
      if (credentials) {
        config.headers = config.headers ?? {}
        config.headers.Authorization = buildBasicAuthHeader(credentials)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.data) {
      const data = error.response.data
      if (!data.detail && data.error?.message) {
        data.detail = data.error.message
      }
    }
    if (error.response?.status === 401 && error.config?.url?.startsWith('/admin/')) {
      clearAdminCredentials()
      if (router.currentRoute.value.name !== 'Login') {
        void router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } })
      }
    }
    return Promise.reject(error)
  }
)

export default api
