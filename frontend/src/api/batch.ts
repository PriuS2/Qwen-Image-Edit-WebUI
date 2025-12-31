import apiClient from './client'
import type { ApiResponse, BatchItem, BatchJob } from '@/types'

export interface BatchSubmitRequest {
  items: BatchItem[]
  response_format?: 'url' | 'base64'
  session_id?: string
  save_to_gallery?: boolean
}

export interface BatchSubmitResponse {
  success: boolean
  job_id: string
  total_items: number
  message: string
}

export interface BatchListResponse {
  success: boolean
  data: BatchJob[]
  total: number
}

export const batchApi = {
  /**
   * Submit batch job
   */
  submit: async (request: BatchSubmitRequest): Promise<BatchSubmitResponse> => {
    const response = await apiClient.post<BatchSubmitResponse>('/api/batch/submit', request)
    return response.data
  },

  /**
   * Get batch job status
   */
  getStatus: async (jobId: string): Promise<ApiResponse<BatchJob>> => {
    const response = await apiClient.get<ApiResponse<BatchJob>>(`/api/batch/${jobId}`)
    return response.data
  },

  /**
   * Cancel batch job
   */
  cancel: async (jobId: string): Promise<ApiResponse> => {
    const response = await apiClient.delete<ApiResponse>(`/api/batch/${jobId}`)
    return response.data
  },

  /**
   * List batch jobs
   */
  list: async (options: { session_id?: string; limit?: number } = {}): Promise<BatchListResponse> => {
    const params = new URLSearchParams()
    if (options.session_id) params.append('session_id', options.session_id)
    if (options.limit) params.append('limit', String(options.limit))
    
    const response = await apiClient.get<BatchListResponse>(`/api/batch/list?${params}`)
    return response.data
  }
}
