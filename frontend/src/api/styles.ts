import apiClient from './client'
import type { ApiResponse, StylePreset, StylePresetCreate, StylePresetUpdate } from '@/types'

export const stylesApi = {
  /**
   * Get all style presets
   */
  getAll: async (enabledOnly: boolean = false): Promise<ApiResponse<StylePreset[]>> => {
    const response = await apiClient.get<ApiResponse<StylePreset[]>>(
      `/api/styles?enabled_only=${enabledOnly}`
    )
    return response.data
  },

  /**
   * Get a specific style preset by ID or name
   */
  getOne: async (styleId: string): Promise<ApiResponse<StylePreset>> => {
    const response = await apiClient.get<ApiResponse<StylePreset>>(`/api/styles/${styleId}`)
    return response.data
  },

  /**
   * Create a new style preset
   */
  create: async (data: StylePresetCreate): Promise<ApiResponse<StylePreset>> => {
    const response = await apiClient.post<ApiResponse<StylePreset>>('/api/styles', data)
    return response.data
  },

  /**
   * Update an existing style preset
   */
  update: async (styleId: string, data: StylePresetUpdate): Promise<ApiResponse<StylePreset>> => {
    const response = await apiClient.put<ApiResponse<StylePreset>>(`/api/styles/${styleId}`, data)
    return response.data
  },

  /**
   * Delete a style preset
   */
  delete: async (styleId: string): Promise<ApiResponse> => {
    const response = await apiClient.delete<ApiResponse>(`/api/styles/${styleId}`)
    return response.data
  },

  /**
   * Reset all styles to default
   */
  reset: async (): Promise<ApiResponse<StylePreset[]>> => {
    const response = await apiClient.post<ApiResponse<StylePreset[]>>('/api/styles/reset')
    return response.data
  }
}
