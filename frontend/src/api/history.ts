import apiClient from './client'
import type { ApiResponse, HistoryItem, UndoRedoResult } from '@/types'

export interface HistoryListResponse {
  success: boolean
  data: HistoryItem[]
  total: number
}

export const historyApi = {
  /**
   * Get history list
   */
  list: async (options: { 
    session_id?: string
    limit?: number
    offset?: number 
  } = {}): Promise<HistoryListResponse> => {
    const params = new URLSearchParams()
    if (options.session_id) params.append('session_id', options.session_id)
    if (options.limit) params.append('limit', String(options.limit))
    if (options.offset) params.append('offset', String(options.offset))
    
    const response = await apiClient.get<HistoryListResponse>(`/api/history?${params}`)
    return response.data
  },

  /**
   * Get history item
   */
  get: async (historyId: string): Promise<ApiResponse<HistoryItem>> => {
    const response = await apiClient.get<ApiResponse<HistoryItem>>(`/api/history/${historyId}`)
    return response.data
  },

  /**
   * Undo
   */
  undo: async (historyId: string): Promise<UndoRedoResult> => {
    const response = await apiClient.post<UndoRedoResult>(`/api/history/${historyId}/undo`)
    return response.data
  },

  /**
   * Redo
   */
  redo: async (historyId: string): Promise<UndoRedoResult> => {
    const response = await apiClient.post<UndoRedoResult>(`/api/history/${historyId}/redo`)
    return response.data
  },

  /**
   * Delete history item
   */
  delete: async (historyId: string): Promise<ApiResponse> => {
    const response = await apiClient.delete<ApiResponse>(`/api/history/${historyId}`)
    return response.data
  }
}
