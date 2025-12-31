import apiClient from './client'
import type { ApiResponse, AppSettings, AutoUnloadSettings, AutoLoadSettings } from '@/types'

export const settingsApi = {
  /**
   * Get all settings
   */
  getAll: async (): Promise<ApiResponse<AppSettings>> => {
    const response = await apiClient.get<ApiResponse<AppSettings>>('/api/settings')
    return response.data
  },

  /**
   * Update all settings
   */
  updateAll: async (settings: Partial<AppSettings>): Promise<ApiResponse<AppSettings>> => {
    const response = await apiClient.put<ApiResponse<AppSettings>>('/api/settings', settings)
    return response.data
  },

  /**
   * Get auto-unload settings
   */
  getAutoUnload: async (): Promise<ApiResponse<AutoUnloadSettings> & { idle_minutes: number }> => {
    const response = await apiClient.get('/api/settings/auto-unload')
    return response.data
  },

  /**
   * Update auto-unload settings
   */
  updateAutoUnload: async (settings: AutoUnloadSettings): Promise<ApiResponse> => {
    const response = await apiClient.put<ApiResponse>('/api/settings/auto-unload', settings)
    return response.data
  },

  /**
   * Get auto-load settings
   */
  getAutoLoad: async (): Promise<ApiResponse<AutoLoadSettings>> => {
    const response = await apiClient.get<ApiResponse<AutoLoadSettings>>('/api/settings/auto-load')
    return response.data
  },

  /**
   * Update auto-load settings
   */
  updateAutoLoad: async (settings: AutoLoadSettings): Promise<ApiResponse> => {
    const response = await apiClient.put<ApiResponse>('/api/settings/auto-load', settings)
    return response.data
  },

  /**
   * Reset settings to default
   */
  reset: async (): Promise<ApiResponse<AppSettings>> => {
    const response = await apiClient.post<ApiResponse<AppSettings>>('/api/settings/reset')
    return response.data
  }
}
