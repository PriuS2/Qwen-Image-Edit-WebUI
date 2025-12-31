import apiClient from './client'
import type { 
  ApiResponse, 
  ModelStatus, 
  AvailableModel, 
  DownloadStatus,
  OptimizationSettings 
} from '@/types'

export interface ModelStatusResponse extends ApiResponse<ModelStatus> {}

export interface AvailableModelsResponse {
  success: boolean
  models: AvailableModel[]
}

export interface DownloadRequest {
  model_name?: string
  force_download?: boolean
}

export interface LoadRequest {
  model_name?: string
  optimization?: Partial<OptimizationSettings>
  force_reload?: boolean
}

export interface OptimizationUpdateRequest {
  optimization: Partial<OptimizationSettings>
  apply_immediately?: boolean
}

export const modelApi = {
  /**
   * Get current model status
   */
  getStatus: async (): Promise<ModelStatusResponse> => {
    const response = await apiClient.get<ModelStatusResponse>('/api/model/status')
    return response.data
  },

  /**
   * Get available models
   */
  getAvailable: async (): Promise<AvailableModelsResponse> => {
    const response = await apiClient.get<AvailableModelsResponse>('/api/model/available')
    return response.data
  },

  /**
   * Start model download
   */
  download: async (request: DownloadRequest = {}): Promise<ApiResponse<DownloadStatus>> => {
    const response = await apiClient.post<ApiResponse<DownloadStatus>>('/api/model/download', request)
    return response.data
  },

  /**
   * Get download status
   */
  getDownloadStatus: async (): Promise<ApiResponse<DownloadStatus>> => {
    const response = await apiClient.get<ApiResponse<DownloadStatus>>('/api/model/download/status')
    return response.data
  },

  /**
   * Cancel download
   */
  cancelDownload: async (): Promise<ApiResponse<DownloadStatus>> => {
    const response = await apiClient.post<ApiResponse<DownloadStatus>>('/api/model/download/cancel')
    return response.data
  },

  /**
   * Check if model is downloaded
   */
  checkDownload: async (modelName: string): Promise<{ success: boolean; model_name: string; is_downloaded: boolean }> => {
    const response = await apiClient.get(`/api/model/download/check/${encodeURIComponent(modelName)}`)
    return response.data
  },

  /**
   * Load model
   */
  load: async (request: LoadRequest = {}): Promise<ModelStatusResponse> => {
    const response = await apiClient.post<ModelStatusResponse>('/api/model/load', request)
    return response.data
  },

  /**
   * Unload model
   */
  unload: async (): Promise<ApiResponse & { vram_freed_gb: number }> => {
    const response = await apiClient.post('/api/model/unload')
    return response.data
  },

  /**
   * Get optimization settings
   */
  getOptimization: async (): Promise<ApiResponse<{
    saved_settings: OptimizationSettings
    applied_settings: OptimizationSettings | null
    is_model_loaded: boolean
  }>> => {
    const response = await apiClient.get('/api/model/optimization')
    return response.data
  },

  /**
   * Update optimization settings
   */
  updateOptimization: async (request: OptimizationUpdateRequest): Promise<ApiResponse> => {
    const response = await apiClient.put('/api/model/optimization', request)
    return response.data
  }
}
