import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { editApi, createJobProgressSocket, type JobProgressWebSocket } from '@/api'
import type { EditParams, JobStatus, JobResult, StyleType, ProgressMessage } from '@/types'
import { ElMessage } from 'element-plus'

export interface ImageItem {
  file: File
  url: string
  id: string
}

export const useEditStore = defineStore('edit', () => {
  // State
  const currentImage = ref<File | null>(null)
  const currentImageUrl = ref<string | null>(null)
  
  // Multi-image state
  const images = ref<ImageItem[]>([])
  const maxImages = ref<number>(3)
  
  const resultImage = ref<string | null>(null)
  const jobId = ref<string | null>(null)
  const jobStatus = ref<JobStatus | null>(null)
  const progress = ref<number>(0)
  const isProcessing = ref<boolean>(false)
  const error = ref<string | null>(null)
  const sessionId = ref<string>(`session-${Date.now()}`)

  // Default edit params
  const params = ref<EditParams>({
    prompt: '',
    negative_prompt: '',
    num_inference_steps: 20,
    true_cfg_scale: 4.0,
    guidance_scale: 1.0,
    seed: -1,
    num_images_per_prompt: 1
  })

  // WebSocket connection
  let wsConnection: JobProgressWebSocket | null = null

  // Getters
  const hasImage = computed(() => images.value.length > 0)
  const canEdit = computed(() => hasImage.value && !!params.value.prompt && !isProcessing.value)
  const lastResult = computed(() => jobStatus.value?.result ?? null)
  
  // Multi-image mode detection
  const isMultiMode = computed(() => images.value.length > 1)
  const imageCount = computed(() => images.value.length)

  // Actions
  function setImage(file: File): void {
    // Clear existing images and add new one (single image mode compatibility)
    clearImage()
    addImages([file])
  }

  function clearImage(): void {
    // Revoke all URLs
    images.value.forEach(img => URL.revokeObjectURL(img.url))
    images.value = []
    
    // Legacy single image state
    if (currentImageUrl.value) {
      URL.revokeObjectURL(currentImageUrl.value)
    }
    currentImage.value = null
    currentImageUrl.value = null
    resultImage.value = null
    error.value = null
  }

  function addImages(files: File[]): void {
    const remaining = maxImages.value - images.value.length
    const toAdd = files.slice(0, remaining)
    
    toAdd.forEach(file => {
      const id = `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      images.value.push({
        file,
        url: URL.createObjectURL(file),
        id
      })
    })
    
    // Update legacy state for first image
    if (images.value.length > 0) {
      currentImage.value = images.value[0].file
      currentImageUrl.value = images.value[0].url
    }
    
    resultImage.value = null
    error.value = null
  }

  function removeImage(id: string): void {
    const index = images.value.findIndex(img => img.id === id)
    if (index !== -1) {
      URL.revokeObjectURL(images.value[index].url)
      images.value.splice(index, 1)
    }
    
    // Update legacy state
    if (images.value.length > 0) {
      currentImage.value = images.value[0].file
      currentImageUrl.value = images.value[0].url
    } else {
      currentImage.value = null
      currentImageUrl.value = null
    }
  }

  function updateParams(newParams: Partial<EditParams>): void {
    params.value = { ...params.value, ...newParams }
  }

  function resetParams(): void {
    params.value = {
      prompt: '',
      negative_prompt: '',
      num_inference_steps: 20,
      true_cfg_scale: 4.0,
      guidance_scale: 1.0,
      seed: -1,
      num_images_per_prompt: 1
    }
  }

  async function submitEdit(): Promise<boolean> {
    if (images.value.length === 0) {
      ElMessage.warning('이미지를 먼저 업로드해주세요.')
      return false
    }

    if (!params.value.prompt) {
      ElMessage.warning('프롬프트를 입력해주세요.')
      return false
    }

    isProcessing.value = true
    error.value = null
    progress.value = 0

    try {
      let response
      
      if (images.value.length === 1) {
        // Single image mode
        response = await editApi.editSingleUpload(
          images.value[0].file,
          params.value,
          {
            response_format: 'url',
            session_id: sessionId.value,
            save_to_gallery: true
          }
        )
      } else {
        // Multi image mode
        const files = images.value.map(img => img.file)
        response = await editApi.editMultiUpload(
          files,
          params.value,
          {
            response_format: 'url',
            session_id: sessionId.value,
            save_to_gallery: true
          }
        )
      }

      if (response.success) {
        jobId.value = response.job_id
        connectWebSocket(response.job_id)
        ElMessage.info(images.value.length > 1 ? 'Multi 모드로 편집 시작...' : 'Single 모드로 편집 시작...')
        return true
      }
      return false
    } catch (err) {
      error.value = '편집 요청 실패'
      isProcessing.value = false
      return false
    }
  }

  async function submitStyleTransfer(
    style: StyleType,
    intensity: number = 1.0,
    additionalPrompt?: string
  ): Promise<boolean> {
    if (!currentImage.value) {
      ElMessage.warning('이미지를 먼저 업로드해주세요.')
      return false
    }

    isProcessing.value = true
    error.value = null
    progress.value = 0

    try {
      const response = await editApi.styleTransferUpload(
        currentImage.value,
        style,
        {
          intensity,
          additional_prompt: additionalPrompt,
          response_format: 'url',
          session_id: sessionId.value,
          save_to_gallery: true
        }
      )

      if (response.success) {
        jobId.value = response.job_id
        connectWebSocket(response.job_id)
        return true
      }
      return false
    } catch (err) {
      error.value = '스타일 변환 요청 실패'
      isProcessing.value = false
      return false
    }
  }

  function connectWebSocket(jobIdValue: string): void {
    disconnectWebSocket()

    wsConnection = createJobProgressSocket(
      jobIdValue,
      (message: ProgressMessage) => {
        console.log('[EditStore] WebSocket message:', message)
        
        progress.value = message.progress
        
        // Determine status: use message.status if available, or infer from progress/result
        const inferredStatus = message.status || 
          (message.progress === 100 && message.result ? 'completed' : 
           message.error ? 'failed' : 'processing')
        
        jobStatus.value = {
          job_id: message.job_id,
          status: inferredStatus,
          progress: message.progress,
          result: message.result,
          error: message.error
        }

        // Check for completion: explicit status OR (progress 100% with result)
        const isCompleted = message.status === 'completed' || 
          (message.progress === 100 && message.result)
        
        if (isCompleted && message.result) {
          console.log('[EditStore] Completed! Result image:', message.result.image)
          resultImage.value = message.result.image
          isProcessing.value = false
          ElMessage.success('이미지 편집이 완료되었습니다.')
        } else if (message.status === 'failed' || message.error) {
          error.value = message.error || '편집 실패'
          isProcessing.value = false
          ElMessage.error(error.value)
        }
      },
      {
        onError: () => {
          console.warn('[EditStore] WebSocket error, falling back to polling')
          error.value = 'WebSocket 연결 오류'
          // Fallback to polling
          startPolling(jobIdValue)
        },
        onClose: () => {
          console.log('[EditStore] WebSocket closed, isProcessing:', isProcessing.value)
          wsConnection = null
          // If still processing when socket closes unexpectedly, try polling
          if (isProcessing.value && !error.value) {
            console.log('[EditStore] Socket closed while processing, starting polling fallback')
            startPolling(jobIdValue)
          }
        }
      }
    )
  }

  function disconnectWebSocket(): void {
    if (wsConnection) {
      wsConnection.close()
      wsConnection = null
    }
  }

  // Polling fallback
  let pollingInterval: number | null = null

  function startPolling(jobIdValue: string): void {
    stopPolling()
    console.log('[EditStore] Starting polling for job:', jobIdValue)
    
    pollingInterval = window.setInterval(async () => {
      try {
        const status = await editApi.getJobStatus(jobIdValue)
        console.log('[EditStore] Polling status:', status)
        
        progress.value = status.progress
        jobStatus.value = status

        // Check for completion: explicit status OR (progress 100% with result)
        const isCompleted = status.status === 'completed' || 
          (status.progress === 100 && status.result)

        if (isCompleted && status.result) {
          console.log('[EditStore] Polling completed! Result image:', status.result.image)
          resultImage.value = status.result.image
          isProcessing.value = false
          ElMessage.success('이미지 편집이 완료되었습니다.')
          stopPolling()
        } else if (status.status === 'failed' || status.error) {
          error.value = status.error || '편집 실패'
          isProcessing.value = false
          ElMessage.error(error.value)
          stopPolling()
        }
      } catch (err) {
        console.error('[EditStore] Polling error:', err)
      }
    }, 1000)
  }

  function stopPolling(): void {
    if (pollingInterval !== null) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  function reset(): void {
    disconnectWebSocket()
    stopPolling()
    clearImage()
    resetParams()
    jobId.value = null
    jobStatus.value = null
    progress.value = 0
    isProcessing.value = false
    error.value = null
  }

  return {
    // State
    currentImage,
    currentImageUrl,
    images,
    maxImages,
    resultImage,
    jobId,
    jobStatus,
    progress,
    isProcessing,
    error,
    sessionId,
    params,
    // Getters
    hasImage,
    canEdit,
    lastResult,
    isMultiMode,
    imageCount,
    // Actions
    setImage,
    clearImage,
    addImages,
    removeImage,
    updateParams,
    resetParams,
    submitEdit,
    submitStyleTransfer,
    reset
  }
})
