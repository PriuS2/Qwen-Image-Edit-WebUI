import apiClient from './client'
import type { 
  ApiResponse, 
  EditParams, 
  EditRequest, 
  StyleTransferRequest,
  JobStatus,
  StyleType
} from '@/types'

export interface SubmitResponse {
  success: boolean
  job_id: string
  message: string
}

export const editApi = {
  /**
   * Submit single image edit (JSON)
   */
  editSingle: async (request: EditRequest): Promise<SubmitResponse> => {
    const response = await apiClient.post<SubmitResponse>('/api/edit/single', request)
    return response.data
  },

  /**
   * Submit single image edit (file upload)
   */
  editSingleUpload: async (
    image: File,
    params: EditParams,
    options: {
      response_format?: 'url' | 'base64'
      session_id?: string
      save_to_gallery?: boolean
    } = {}
  ): Promise<SubmitResponse> => {
    const formData = new FormData()
    formData.append('image', image)
    formData.append('prompt', params.prompt)
    
    if (params.negative_prompt) formData.append('negative_prompt', params.negative_prompt)
    if (params.num_inference_steps) formData.append('num_inference_steps', String(params.num_inference_steps))
    if (params.true_cfg_scale) formData.append('true_cfg_scale', String(params.true_cfg_scale))
    if (params.guidance_scale) formData.append('guidance_scale', String(params.guidance_scale))
    if (params.seed !== undefined) formData.append('seed', String(params.seed))
    if (params.num_images_per_prompt) formData.append('num_images_per_prompt', String(params.num_images_per_prompt))
    
    if (options.response_format) formData.append('response_format', options.response_format)
    if (options.session_id) formData.append('session_id', options.session_id)
    if (options.save_to_gallery !== undefined) formData.append('save_to_gallery', String(options.save_to_gallery))

    const response = await apiClient.post<SubmitResponse>('/api/edit/upload/single', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  /**
   * Submit multi image edit (JSON)
   */
  editMulti: async (request: {
    images: string[]
    params: EditParams
    response_format?: 'url' | 'base64'
    session_id?: string
    save_to_gallery?: boolean
  }): Promise<SubmitResponse> => {
    const response = await apiClient.post<SubmitResponse>('/api/edit/multi', request)
    return response.data
  },

  /**
   * Submit multi image edit (file upload)
   */
  editMultiUpload: async (
    images: File[],
    params: EditParams,
    options: {
      response_format?: 'url' | 'base64'
      session_id?: string
      save_to_gallery?: boolean
    } = {}
  ): Promise<SubmitResponse> => {
    const formData = new FormData()
    images.forEach(image => formData.append('images', image))
    formData.append('prompt', params.prompt)
    
    if (params.negative_prompt) formData.append('negative_prompt', params.negative_prompt)
    if (params.num_inference_steps) formData.append('num_inference_steps', String(params.num_inference_steps))
    if (params.true_cfg_scale) formData.append('true_cfg_scale', String(params.true_cfg_scale))
    if (params.guidance_scale) formData.append('guidance_scale', String(params.guidance_scale))
    if (params.seed !== undefined) formData.append('seed', String(params.seed))
    
    if (options.response_format) formData.append('response_format', options.response_format)
    if (options.session_id) formData.append('session_id', options.session_id)
    if (options.save_to_gallery !== undefined) formData.append('save_to_gallery', String(options.save_to_gallery))

    const response = await apiClient.post<SubmitResponse>('/api/edit/upload/multi', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  /**
   * Submit style transfer (JSON)
   */
  styleTransfer: async (request: StyleTransferRequest): Promise<SubmitResponse> => {
    const response = await apiClient.post<SubmitResponse>('/api/edit/style-transfer', request)
    return response.data
  },

  /**
   * Submit style transfer (file upload)
   */
  styleTransferUpload: async (
    image: File,
    style: StyleType,
    options: {
      intensity?: number
      additional_prompt?: string
      response_format?: 'url' | 'base64'
      session_id?: string
      save_to_gallery?: boolean
    } = {}
  ): Promise<SubmitResponse> => {
    const formData = new FormData()
    formData.append('image', image)
    formData.append('style', style)
    
    if (options.intensity) formData.append('intensity', String(options.intensity))
    if (options.additional_prompt) formData.append('additional_prompt', options.additional_prompt)
    if (options.response_format) formData.append('response_format', options.response_format)
    if (options.session_id) formData.append('session_id', options.session_id)
    if (options.save_to_gallery !== undefined) formData.append('save_to_gallery', String(options.save_to_gallery))

    const response = await apiClient.post<SubmitResponse>('/api/edit/upload/style-transfer', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  /**
   * Get job status
   */
  getJobStatus: async (jobId: string): Promise<JobStatus> => {
    const response = await apiClient.get<JobStatus>(`/api/edit/job/${jobId}`)
    return response.data
  }
}
