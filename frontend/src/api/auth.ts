import apiClient from './client'
import type { ApiResponse } from '@/types'

export interface VerifyResponse {
  success: boolean
  message: string
}

export const authApi = {
  /**
   * Verify API key
   */
  verify: async (): Promise<VerifyResponse> => {
    const response = await apiClient.get<VerifyResponse>('/api/auth/verify')
    return response.data
  }
}
