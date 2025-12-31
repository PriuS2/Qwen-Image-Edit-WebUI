import apiClient from './client'
import type { ApiResponse, GalleryItem, GalleryCompareData } from '@/types'

export interface GalleryListResponse {
  success: boolean
  data: GalleryItem[]
  total: number
  limit: number
  offset: number
}

export const galleryApi = {
  /**
   * Get gallery list
   */
  list: async (options: {
    limit?: number
    offset?: number
    favorites_only?: boolean
  } = {}): Promise<GalleryListResponse> => {
    const params = new URLSearchParams()
    if (options.limit) params.append('limit', String(options.limit))
    if (options.offset) params.append('offset', String(options.offset))
    if (options.favorites_only) params.append('favorites_only', 'true')
    
    const response = await apiClient.get<GalleryListResponse>(`/api/gallery?${params}`)
    return response.data
  },

  /**
   * Get gallery item
   */
  get: async (galleryId: string): Promise<ApiResponse<GalleryItem>> => {
    const response = await apiClient.get<ApiResponse<GalleryItem>>(`/api/gallery/${galleryId}`)
    return response.data
  },

  /**
   * Get compare data
   */
  compare: async (galleryId: string): Promise<ApiResponse<GalleryCompareData>> => {
    const response = await apiClient.get<ApiResponse<GalleryCompareData>>(`/api/gallery/${galleryId}/compare`)
    return response.data
  },

  /**
   * Get download URL
   */
  getDownloadUrl: (galleryId: string): string => {
    return `/api/gallery/${galleryId}/download`
  },

  /**
   * Update gallery item
   */
  update: async (
    galleryId: string,
    updates: { title?: string; description?: string; is_favorite?: boolean }
  ): Promise<ApiResponse> => {
    const params = new URLSearchParams()
    if (updates.title) params.append('title', updates.title)
    if (updates.description) params.append('description', updates.description)
    if (updates.is_favorite !== undefined) params.append('is_favorite', String(updates.is_favorite))
    
    const response = await apiClient.patch<ApiResponse>(`/api/gallery/${galleryId}?${params}`)
    return response.data
  },

  /**
   * Delete gallery item
   */
  delete: async (galleryId: string, deleteFiles: boolean = true): Promise<ApiResponse> => {
    const params = new URLSearchParams()
    params.append('delete_files', String(deleteFiles))
    
    const response = await apiClient.delete<ApiResponse>(`/api/gallery/${galleryId}?${params}`)
    return response.data
  }
}
