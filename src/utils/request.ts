import axios, {
  type InternalAxiosRequestConfig,
  type AxiosResponse,
  type AxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'
import { queueRequest } from './requestQueue'
import { clearAuthClientState, getStoredAccessToken, getStoredTokenType } from './auth'

// 定义API响应的标准接口
export interface ApiResponse<T = any> {
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

const redirectToLogin = () => {
  if (window.location.pathname === '/login') return

  const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`
  window.location.replace(`/login?redirect=${encodeURIComponent(redirect)}`)
}

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokenType = getStoredTokenType()
    const accessToken = getStoredAccessToken()

    // 调试：打印月度计划相关的请求参数
    // if (config.url?.includes('/scheduleInfo/page')) {
    //   console.log('月度计划API请求参数:', {
    //     url: config.url,
    //     params: config.params,
    //     data: config.data,
    //   })
    // }

    if (tokenType && accessToken) {
      if (config.headers) {
        config.headers.Authorization = `${tokenType} ${accessToken}`
      }
    }

    // 如果是 FormData，删除 Content-Type 让浏览器自动设置（包括 boundary）
    if (config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type']
      }
    }

    return config
  },
  (error) => {
    // 对请求错误做些什么
    console.error('Request Error:', error) // for debug
    return Promise.reject(error)
  },
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data as ApiResponse
    // 全局判断：如果 code 不为 0 或 200，弹出后端报错信息
    if (res && typeof res.code === 'number' && res.code !== 0 && res.code !== 200) {
      ElMessage.error(res.msg || '操作失败')
    }
    return response
  },
  (error) => {
    console.error('Response Error:', error.response || error.message) // for debug

    // 处理token过期或无效的情况
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      clearAuthClientState()
      redirectToLogin()
    }

    // 处理424状态码，需要退回登录界面
    if (error.response?.status === 424) {
      ElMessage.error('会话异常，请重新登录')
      clearAuthClientState()
      redirectToLogin()
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

// 内部请求方法（不使用队列）
const directRequest = {
  get: <T = any>(url: string, params?: any, config?: any): Promise<ApiResponse<T>> =>
    service.get<ApiResponse<T>>(url, { params, ...config }).then((res) => res.data),
  post: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    service.post<ApiResponse<T>>(url, data, config).then((res) => res.data),
  put: <T = any>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
    service.put<ApiResponse<T>>(url, data, config).then((res) => res.data),
  delete: <T = any>(url: string, params?: any, config?: any): Promise<ApiResponse<T>> =>
    service.delete<ApiResponse<T>>(url, { params, ...config }).then((res) => res.data),
}

// 封装请求方法（支持队列和优先级）
const request = {
  get: <T = any>(
    url: string,
    params?: any,
    config?: any & RequestOptions,
  ): Promise<ApiResponse<T>> => {
    const { priority = 'medium', useQueue = true, ...axiosConfig } = config || {}

    const makeRequest = () => directRequest.get<T>(url, params, axiosConfig)

    if (useQueue) {
      return queueRequest(makeRequest, priority)
    }
    return makeRequest()
  },

  post: <T = any>(
    url: string,
    data?: any,
    config?: any & RequestOptions,
  ): Promise<ApiResponse<T>> => {
    const { priority = 'high', useQueue = true, ...axiosConfig } = config || {}

    const makeRequest = () => directRequest.post<T>(url, data, axiosConfig)

    if (useQueue) {
      return queueRequest(makeRequest, priority)
    }
    return makeRequest()
  },

  put: <T = any>(
    url: string,
    data?: any,
    config?: any & RequestOptions,
  ): Promise<ApiResponse<T>> => {
    const { priority = 'high', useQueue = true, ...axiosConfig } = config || {}

    const makeRequest = () => directRequest.put<T>(url, data, axiosConfig)

    if (useQueue) {
      return queueRequest(makeRequest, priority)
    }
    return makeRequest()
  },

  delete: <T = any>(
    url: string,
    params?: any,
    config?: any & RequestOptions,
  ): Promise<ApiResponse<T>> => {
    const { priority = 'high', useQueue = true, ...axiosConfig } = config || {}

    const makeRequest = () => directRequest.delete<T>(url, params, axiosConfig)

    if (useQueue) {
      return queueRequest(makeRequest, priority)
    }
    return makeRequest()
  },

  // 原始 GET 请求（用于下载文件等非标准 ApiResponse 场景）
  rawGet: <T = any>(
    url: string,
    params?: any,
    config?: AxiosRequestConfig & RequestOptions,
  ): Promise<T> => {
    const { priority = 'medium', useQueue = true, ...axiosConfig } = config || {}
    const makeRequest = () => service.get<T>(url, { params, ...axiosConfig }).then((res) => res.data)

    if (useQueue) {
      return queueRequest(makeRequest, priority)
    }
    return makeRequest()
  },

  // 直接请求方法（绕过队列，用于关键操作）
  direct: directRequest,
}

export default request
