/// <reference types="vite/client" />
import axios, { type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 定义API响应的标准接口
interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

// 定义请求选项接口
interface RequestOptions {
  priority?: 'high' | 'medium' | 'low'
  useQueue?: boolean
  timeout?: number
}

// 获取API基础路径
const getApiBaseUrl = () => {
  // 在构建时通过define注入的环境变量
  if (typeof __VITE_API_BASE_URL__ !== 'undefined') {
    return __VITE_API_BASE_URL__
  }
  // 回退到import.meta.env
  return import.meta.env.MODE === 'production'
    ? import.meta.env.VITE_PROD_API_BASE_URL || ''
    : import.meta.env.VITE_API_BASE_URL || '/api'
}

// 创建 axios 实例
const service = axios.create({
  baseURL: getApiBaseUrl(), // 动态获取API基础路径
  timeout: 300000, // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从主应用获取用户认证信息
    const tokenType = localStorage.getItem('tokenType')
    const accessToken = localStorage.getItem('accessToken')

    if (tokenType && accessToken) {
      if (config.headers) {
        config.headers.Authorization = `${tokenType} ${accessToken}`
      }
    }
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    console.error('Response Error:', error.response || error.message)

    // 处理token过期或无效的情况
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')

      // 清除本地存储
      localStorage.removeItem('tokenType')
      localStorage.removeItem('accessToken')

      // 重定向到登录页（如果当前不在登录页）
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // 处理424状态码，需要退回登录界面
    if (error.response?.status === 424) {
      ElMessage.error('会话异常，请重新登录')

      // 清除本地存储
      localStorage.removeItem('tokenType')
      localStorage.removeItem('accessToken')

      // 重定向到登录页（如果当前不在登录页）
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)

// 创建请求方法的类型
export type RequestMethod = <T = any>(
  url: string,
  data?: any,
  config?: any,
) => Promise<ApiResponse<T>>

// 封装请求方法
const request = {
  get: <T = any>(url: string, params?: any, config?: any): Promise<ApiResponse<T>> =>
    service.get<ApiResponse<T>>(url, { params, ...config }).then((res) => res.data),
  post: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    service.post<ApiResponse<T>>(url, data, config).then((res) => res.data),
  put: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    service.put<ApiResponse<T>>(url, data, config).then((res) => res.data),
  delete: <T = any>(url: string, params?: any, config?: any): Promise<ApiResponse<T>> =>
    service.delete<ApiResponse<T>>(url, { params, ...config }).then((res) => res.data),
}

export default request