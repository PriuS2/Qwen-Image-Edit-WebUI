import axios from 'axios'
import type { AxiosInstance, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const DEFAULT_API_KEY = 'qwen-image-edit-default-key'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Get API key from localStorage or use default
const getApiKey = (): string => {
  return localStorage.getItem('api_key') || DEFAULT_API_KEY
}

// Set API key
export const setApiKey = (key: string): void => {
  localStorage.setItem('api_key', key)
}

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const apiKey = getApiKey()
    config.headers['X-API-Key'] = apiKey
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError) => {
    const status = error.response?.status
    const data = error.response?.data as { detail?: string }

    let message = '오류가 발생했습니다.'

    if (status === 401) {
      message = 'API 키가 유효하지 않습니다.'
    } else if (status === 403) {
      message = '접근이 거부되었습니다.'
    } else if (status === 404) {
      message = '리소스를 찾을 수 없습니다.'
    } else if (status === 409) {
      message = '작업이 진행 중입니다.'
    } else if (status === 503) {
      message = '모델이 로드되지 않았습니다. 먼저 모델을 로드해주세요.'
    } else if (data?.detail) {
      message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default apiClient
